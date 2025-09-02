# Pickleball AI Server Configuration

# Model paths
BALL_MODEL_PATH = "C:/Users/Kafka/Desktop/Pickleball/True/server/models/best.pt"
BOUNCE_MODEL_PATH = "C:/Users/Kafka/Desktop/Pickleball/True/server/models/bounce_model.pt"

# Detection confidence
YOLO_CONF = 0.25
INCOMING_DIR = "/incoming"
DATASETS_DIR = "/datasets"
ZIP_DATASET_NAME = "dataset.zip"

# Event recording
EVENT_CLIP_SEC_BEFORE = 3
EVENT_CLIP_SEC_AFTER = 3

# Multi-court system
MAX_CAMERAS_PER_COURT = 4
MAX_COURTS = 10
REPLAY_DURATIONS = [5, 10]
CONNECTION_TIMEOUT = 30
FRAME_BUFFER_SIZE = 100

# GPU Optimization Settings
GPU_ENABLED = True
GPU_MEMORY_FRACTION = 0.9
CUDNN_BENCHMARK = True
GPU_DEVICE = "auto"  # "auto", "cuda:0", "cuda:1", "cpu"

# YOLO Model Settings
YOLO_DEVICE = "auto"  # Will use GPU if available
YOLO_BATCH_SIZE = 1
YOLO_HALF_PRECISION = True  # Use FP16 for faster inference

# GRU Model Settings
GRU_DEVICE = "auto"
GRU_SEQUENCE_LENGTH = 30
GRU_HIDDEN_SIZE = 128

# Performance Settings
INFERENCE_THREADS = 4
FRAME_PROCESSING_QUEUE_SIZE = 50
MAX_CONCURRENT_INFERENCES = 2

# Logging
LOG_LEVEL = "INFO"
LOG_GPU_USAGE = True
LOG_INFERENCE_TIME = True
