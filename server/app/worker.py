# worker.py
import time
import json
import base64
import cv2
import numpy as np
import redis
import torch

from inference import load_models, predict_bounce, in_out_on_bounce
from config import BALL_MODEL_PATH, BOUNCE_MODEL_PATH, YOLO_CONF

print("[WORKER] Starting AI Inference Worker...", flush=True)

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    print("[WORKER] Connected to Redis.", flush=True)
except redis.exceptions.ConnectionError as e:
    print("[WORKER] Could not connect to Redis.", flush=True)
    exit(1)

yolo_model, gru_model, DEVICE = load_models(BALL_MODEL_PATH, BOUNCE_MODEL_PATH, YOLO_CONF)
print(f"[WORKER] Models loaded on device: {DEVICE}", flush=True)

INFERENCE_QUEUE = "inference_queue"
RESULTS_CHANNEL = "results_channel"

def decode_jpeg(b64):
    arr = np.frombuffer(base64.b64decode(b64), np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def main():
    print("[WORKER] Waiting for inference jobs...", flush=True)
    while True:
        try:
            # blpop is a blocking command that waits for a job to appear
            job_packed = redis_client.blpop(INFERENCE_QUEUE, timeout=0)
            job_data = json.loads(job_packed[1])

            court_id = job_data["court_id"]
            cam_id = job_data["cam_id"]
            frame_b64 = job_data["frame_b64"]
            
            frame = decode_jpeg(frame_b64)

            res = yolo_model.predict(source=frame, conf=YOLO_CONF, verbose=False)[0]
            dets = res.boxes
            names = res.names

            ball_xy = None
            if dets is not None and dets.xyxy is not None:
                xyxy = dets.xyxy.cpu().numpy()
                cls  = dets.cls.cpu().numpy().astype(int)
                conf = dets.conf.cpu().numpy()
                best = -1; best_conf = 0.0
                for i in range(len(xyxy)):
                    if names[cls[i]] == "ball" and conf[i] > best_conf:
                        best_conf = conf[i]; best = i
                if best >= 0:
                    x1,y1,x2,y2 = xyxy[best]
                    ball_xy = (int((x1+x2)/2), int((y1+y2)/2))

            # Here you would add the bounce prediction logic if needed
            # For simplicity, this worker just finds the ball.
            # You can pass the xy_buffer in the job_data for bounce prediction.

            result = {
                "court_id": court_id,
                "cam_id": cam_id,
                "ball_xy": ball_xy,
                "decision": None, # Placeholder for bounce logic
                "timestamp": time.time()
            }
            
            redis_client.publish(RESULTS_CHANNEL, json.dumps(result))

        except Exception as e:
            print(f"[WORKER] Error processing job: {e}", flush=True)

if __name__ == "__main__":
    main()