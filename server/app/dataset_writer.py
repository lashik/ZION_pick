import os, cv2, json, time, zipfile
from pathlib import Path
from config import INCOMING_DIR, DATASETS_DIR, ZIP_DATASET_NAME

def ensure_dirs():
    Path(INCOMING_DIR).mkdir(parents=True, exist_ok=True)
    Path(DATASETS_DIR).mkdir(parents=True, exist_ok=True)

def write_frame_for_annotation(match_id, cam_id, frame_bgr, meta):
    dst = Path(DATASETS_DIR)/match_id/f"cam{cam_id:02d}"/"images"
    dst.mkdir(parents=True, exist_ok=True)
    ts = int(time.time()*1000)
    img_path = dst/f"frame_{ts}.jpg"
    cv2.imwrite(str(img_path), frame_bgr)
    with open(dst.parent/"meta.jsonl","a") as f:
        f.write(json.dumps(meta)+"\n")
    return str(img_path)

def zip_dataset(match_id):
    root = Path(DATASETS_DIR)/match_id
    zip_path = Path(DATASETS_DIR)/ZIP_DATASET_NAME
    if zip_path.exists(): zip_path.unlink()
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
        for p in root.rglob("*"):
            zf.write(p, p.relative_to(DATASETS_DIR))
    return str(zip_path)
