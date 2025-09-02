# database.py
import sqlite3
import time
from pathlib import Path

DB_FILE = "pickleball.db"
DB_PATH = Path(__file__).parent / DB_FILE

def get_db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if DB_PATH.exists():
        return
    print("[INFO] Creating new database...", flush=True)
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE courts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE cameras (
            id TEXT,
            court_id TEXT,
            name TEXT NOT NULL,
            position TEXT,
            status TEXT DEFAULT 'offline',
            last_seen REAL,
            created_at REAL NOT NULL,
            PRIMARY KEY (id, court_id),
            FOREIGN KEY (court_id) REFERENCES courts (id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

def dict_from_row(row):
    return dict(row) if row else None

def get_courts():
    conn = get_db_conn()
    courts_cursor = conn.cursor()
    courts_cursor.execute("SELECT * FROM courts")
    courts_list = [dict_from_row(r) for r in courts_cursor.fetchall()]
    
    courts_dict = {}
    for court in courts_list:
        cameras_cursor = conn.cursor()
        cameras_cursor.execute("SELECT * FROM cameras WHERE court_id = ?", (court['id'],))
        court['cameras'] = {str(cam['id']): dict_from_row(cam) for cam in cameras_cursor.fetchall()}
        courts_dict[court['id']] = court
        
    conn.close()
    return courts_dict

def get_court_by_id(court_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courts WHERE id = ?", (court_id,))
    court = dict_from_row(cursor.fetchone())
    conn.close()
    return court
    
def delete_court(court_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    # Due to "ON DELETE CASCADE" in the table definition,
    # deleting a court will automatically delete its associated cameras.
    cursor.execute("DELETE FROM courts WHERE id = ?", (court_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count > 0
def create_court(court_id, court_name):
    conn = get_db_conn()
    try:
        conn.execute("INSERT INTO courts (id, name, created_at) VALUES (?, ?, ?)", (court_id, court_name, time.time()))
        conn.commit()
        conn.close()
        return {"id": court_id, "name": court_name, "cameras": {}, "created_at": time.time()}
    except sqlite3.IntegrityError:
        conn.close()
        return None

def add_camera(court_id, cam_id, cam_name, position):
    conn = get_db_conn()
    try:
        conn.execute(
            "INSERT INTO cameras (id, court_id, name, position, created_at) VALUES (?, ?, ?, ?, ?)",
            (cam_id, court_id, cam_name, position, time.time())
        )
        conn.commit()
        conn.close()
        return {"id": cam_id, "name": cam_name, "position": position, "status": "offline", "created_at": time.time()}
    except sqlite3.IntegrityError:
        conn.close()
        return None

def remove_camera(court_id, cam_id):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cameras WHERE court_id = ? AND id = ?", (court_id, cam_id))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count > 0

def update_camera_status(court_id, cam_id, status):
    conn = get_db_conn()
    conn.execute(
        "UPDATE cameras SET status = ?, last_seen = ? WHERE court_id = ? AND id = ?",
        (status, time.time(), court_id, cam_id)
    )
    conn.commit()
    conn.close()