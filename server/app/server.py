# server.py

import os, io, cv2, base64, threading, time, json, hashlib
import numpy as np
import redis
import database
from pathlib import Path
from flask import Flask, request, send_file, jsonify, session
from flask_socketio import SocketIO, emit, disconnect, join_room
from shapely.geometry import Polygon
from config import *
from inference import CourtState, load_models, predict_bounce, in_out_on_bounce
from dataset_writer import ensure_dirs, write_frame_for_annotation, zip_dataset

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
app.config["SECRET_KEY"] = "pickleball_ai_secret_key_2024"
app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
app.config.setdefault("SESSION_COOKIE_SECURE", False)

ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:8081",
    "http://192.168.1.15:8080",
    "http://192.168.1.15:8081",
    "http://192.168.1.15:8000",
    "https://0nex2fx18j42ro-8000.proxy.runpod.net"# CHANGE THIS
]

from flask_cors import CORS
CORS(app, origins="*", supports_credentials=True)

def _select_async_mode():
    for mode in ("eventlet", "gevent", "threading"):
        try:
            if mode == "eventlet": import eventlet
            elif mode == "gevent": import gevent
            return mode
        except Exception: continue
    return "threading"

ASYNC_MODE = _select_async_mode()
socketio = SocketIO(app, cors_allowed_origins="*")

try:
    redis_client = redis.from_url("redis://default:bRKOb61oUhjqZ8IzEBM52SoQLm18bTQx@redis-12374.c330.asia-south1-1.gce.redns.redis-cloud.com:12374")
    redis_client.ping()
    print("[INFO] Connected to Redis.", flush=True)
except redis.exceptions.ConnectionError as e:
    print("[ERROR] Could not connect to Redis. Please ensure it is running via docker-compose.", flush=True)
    exit(1)

database.init_db()
yolo_model, gru_model, DEVICE = load_models(BALL_MODEL_PATH, BOUNCE_MODEL_PATH, YOLO_CONF)
ensure_dirs()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

streams = {}
clients = {}

def decode_jpeg(b64):
    arr = np.frombuffer(base64.b64decode(b64), np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def is_admin_authenticated():
    session_id = session.get('admin_id')
    if not session_id:
        return False
    return redis_client.exists(f"session:{session_id}")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
        session_id = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()
        redis_client.set(f"session:{session_id}", username, ex=86400)
        session['admin_id'] = session_id
        return {"ok": True, "session_id": session_id}
    return {"ok": False, "error": "Invalid credentials"}, 401

@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session_id = session.get('admin_id')
    if session_id:
        redis_client.delete(f"session:{session_id}")
        session.pop('admin_id', None)
    return {"ok": True}

@app.route("/admin/courts", methods=["GET"])
def get_courts():
    if not is_admin_authenticated():
        return {"ok": False, "error": "Not authenticated"}, 401
    return {"ok": True, "courts": database.get_courts()}

@app.route("/admin/courts", methods=["POST"])
def create_court():
    if not is_admin_authenticated():
        return {"ok": False, "error": "Not authenticated"}, 401
    
    data = request.get_json()
    court_id = data.get("court_id")
    court_name = data.get("court_name")
    
    if database.get_court_by_id(court_id):
        return {"ok": False, "error": "Court already exists"}, 400
    
    new_court = database.create_court(court_id, court_name)
    return {"ok": True, "court": new_court}

@app.route("/admin/cameras", methods=["POST"])
def add_camera():
    if not is_admin_authenticated():
        return {"ok": False, "error": "Not authenticated"}, 401
    
    data = request.get_json()
    court_id = data.get("court_id")
    cam_id = str(data.get("cam_id"))
    cam_name = data.get("cam_name")
    cam_position = data.get("position", "unknown")
    
    if not database.get_court_by_id(court_id):
        return {"ok": False, "error": "Court not found"}, 404
    
    new_camera = database.add_camera(court_id, cam_id, cam_name, cam_position)
    if new_camera:
        return {"ok": True, "camera": new_camera}
    return {"ok": False, "error": "Camera already exists or failed to create"}, 400

@app.route("/admin/cameras/<court_id>/<cam_id>", methods=["DELETE"])
def remove_camera(court_id, cam_id):
    if not is_admin_authenticated():
        return {"ok": False, "error": "Not authenticated"}, 401
    
    if database.remove_camera(court_id, cam_id):
        stream_key = (court_id, cam_id)
        if stream_key in streams: del streams[stream_key]
        return {"ok": True}
    return {"ok": False, "error": "Camera not found"}, 404

@app.route("/health")
def health():
    return {"ok": True, "device": DEVICE, "courts": len(database.get_courts())}, 200

@app.route("/status")
def status():
    courts_data = database.get_courts()
    active_streams = len([s for s in streams.values() if s.get("last_frame")])
    total_cameras = sum(len(c["cameras"]) for c in courts_data.values())
    return {
        "ok": True,
        "courts": len(courts_data),
        "active_streams": active_streams,
        "total_cameras": total_cameras,
    }

@app.route("/dataset/<court_id>/download")
def dataset_download(court_id):
    z = zip_dataset(court_id)
    return send_file(z, as_attachment=True)

@socketio.on("connect", namespace="/camera")
def on_camera_connect():
    print(f"[DEBUG] Camera connected: {request.sid}", flush=True)
    emit("server_ack", {"msg": "camera connected"}, namespace="/camera")

@socketio.on("register_stream", namespace = "/camera")
def on_register(data):
    court_id = data["court_id"]
    cam_id = str(data["cam_id"])
    client_type = data.get("client_type", "camera")
    
    courts_data = database.get_courts()
    if court_id not in courts_data or cam_id not in courts_data[court_id]['cameras']:
        print(f"[WARN] Unrecognized camera tried to register: Court {court_id}, Cam {cam_id}", flush=True)
        # You might want to disconnect here for security
        # disconnect() 
        return

    stream_key = (court_id, cam_id)
    streams[stream_key] = {
        "state": CourtState(),
        "fps": int(data.get("fps", 30)),
        "keep_frames": [],
        "last_frame": None,
        "last_decision": None
    }
    
    clients[request.sid] = (court_id, cam_id, client_type)
    database.update_camera_status(court_id, cam_id, "online")
    emit("registered", {"ok": True, "court_id": court_id, "cam_id": cam_id}, namespace = "/camera")

@socketio.on("set_polygons" )
def on_set_polygons(data):
    court_id = data["court_id"]
    cam_id = str(data["cam_id"])
    stream_key = (court_id, cam_id)
    
    s = streams.get(stream_key)
    if not s:
        emit("error", {"msg": "Stream not found"})
        return
    
    left = Polygon(data["left"]) if data.get("left") else None
    right = Polygon(data["right"]) if data.get("right") else None
    s["state"].polygons = {"left": left, "right": right}
    emit("polygons_ok", {"ok": True})

@socketio.on("frame", namespace = "/camera")
def on_frame(data):
    job = {
        "court_id": data["court_id"],
        "cam_id": str(data["cam_id"]),
        "frame_b64": data["jpg_b64"],
        "timestamp": time.time()
    }
    redis_client.rpush("inference_queue", json.dumps(job))
    socketio.emit(
        "live_frame",
        {"cam_id": str(data["cam_id"]), "frame": data["jpg_b64"]},
        namespace="/webapp",
        to=str(data["cam_id"])
    )
@app.route("/admin/courts/<court_id>", methods=["DELETE"])
def delete_court(court_id):
    if not is_admin_authenticated():
        return {"ok": False, "error": "Not authenticated"}, 401
    
    if database.delete_court(court_id):
        return {"ok": True}
    return {"ok": False, "error": "Court not found"}, 404
@socketio.on("join_camera_feed", namespace="/webapp")
def join_camera_feed(data):
    cam_id = str(data["cam_id"])
    # The join_room function subscribes the client to a specific broadcast channel.
    join_room(cam_id)
    print(f"[DEBUG] Webapp client {request.sid} is now viewing camera {cam_id}")

def listen_for_results():
    """
    Runs in a background thread to listen for results from the AI worker.
    """
    pubsub = redis_client.pubsub()
    pubsub.subscribe("results_channel")
    print("[SERVER] Listening for results from worker...", flush=True)
    for message in pubsub.listen():
        if message['type'] == 'message':
            result = json.loads(message['data'])
            # We use socketio.emit to send from the background thread
            socketio.emit("decision", result, namespace="/webapp")


@socketio.on("request_replay", namespace = "/webapp")
def on_request_replay(data):
    court_id = data["court_id"]
    cam_id = str(data["cam_id"])
    duration = int(data.get("duration", 5))
    stream_key = (court_id, cam_id)
    
    s = streams.get(stream_key)
    if not s:
        emit("error", {"msg": "Stream not found"})
        return
    
    fps = s["fps"]
    frames = s["keep_frames"]
    if not frames:
        emit("error", {"msg": "No frames available"})
        return
    
    tail = int(duration * fps)
    clip = frames[-tail:] if len(frames) >= tail else frames
    
    payload = []
    for f in clip:
        _, enc = cv2.imencode(".jpg", f)
        payload.append(base64.b64encode(enc.tobytes()).decode("ascii"))
    
    emit("replay_clip", {
        "court_id": court_id,
        "cam_id": cam_id,
        "fps": fps, 
        "frames": payload,
        "duration": duration
    })

@socketio.on("save_full_game", namespace = "/webapp")
def on_save_full_game(data):
    emit("save_ack", {"ok": True})

@socketio.on("disconnect", namespace="/camera")
def on_camera_disconnect():
    client_info = clients.pop(request.sid, None)
    if client_info:
        court_id, cam_id, client_type = client_info
        if client_type == "camera":
            stream_key = (court_id, str(cam_id))
            if stream_key in streams:
                del streams[stream_key]
            database.update_camera_status(court_id, str(cam_id), "offline")
    print(f"[DEBUG] Camera disconnected: {request.sid}", flush=True)

@socketio.on("connect", namespace="/webapp")
def on_webapp_connect():
    print(f"[DEBUG] Webapp connected: {request.sid}", flush=True)
    emit("server_ack", {"msg": "webapp connected"}, namespace="/webapp")

@socketio.on("get_status", namespace="/webapp")
def on_webapp_status():
    courts_data = database.get_courts()
    active_streams = len([s for s in streams.values() if s.get("last_frame")])
    total_cameras = sum(len(c["cameras"]) for c in courts_data.values())
    emit("status", {
        "ok": True,
        "courts": len(courts_data),
        "active_streams": active_streams,
        "total_cameras": total_cameras
    }, namespace="/webapp")

if __name__ == "__main__":
    print("[DEBUG] Starting server on 0.0.0.0:8000", flush=True)
    print(f"[DEBUG] Using device: {DEVICE}", flush=True)
    
    # Start the results listener in a background thread
    listener_thread = threading.Thread(target=listen_for_results, daemon=True)
    listener_thread.start()
    
    socketio.run(app, host="0.0.0.0", port=8000)