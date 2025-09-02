import torch, numpy as np
from ultralytics import YOLO
from shapely.geometry import Point, Polygon

class BounceGRU(torch.nn.Module):
    def __init__(self, input_size=2, hidden_size=32, num_layers=1):
        super().__init__()
        self.gru = torch.nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(hidden_size, 32), torch.nn.ReLU(),
            torch.nn.Linear(32, 1), torch.nn.Sigmoid()
        )
    def forward(self, x):
        out, _ = self.gru(x)
        return self.fc(out[:, -1, :]).squeeze()

class CourtState:
    def __init__(self):
        self.xy_buffer = []
        self.last_decision = "IN"
        self.polygons = {"left": None, "right": None}
        self.recent_track = []  # for replay

def load_models(ball_path, bounce_path, conf):
    yolo = YOLO(ball_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    class GRU(BounceGRU): pass
    gru = GRU().to(device)
    state = torch.load(bounce_path, map_location=device)
    gru.load_state_dict(state)
    gru.eval()
    return yolo, gru, device

def predict_bounce(gru, device, xy_buffer, window=8, thr=0.5):
    if len(xy_buffer) < window:
        return 0.0, False
    seq = np.array(xy_buffer[-window:], dtype=np.float32)
    seq = (seq - seq.min(axis=0)) / (seq.max(axis=0) - seq.min(axis=0) + 1e-6)
    tens = torch.tensor(seq, dtype=torch.float32, device=device).unsqueeze(0)
    with torch.no_grad():
        p = float(gru(tens).item())
    return p, p > thr

def in_out_on_bounce(ball_xy, polys):
    pt = Point(ball_xy)
    left, right = polys.get("left"), polys.get("right")
    if isinstance(left, Polygon) and left.contains(pt): return "IN"
    if isinstance(right, Polygon) and right.contains(pt): return "IN"
    return "OUT"
