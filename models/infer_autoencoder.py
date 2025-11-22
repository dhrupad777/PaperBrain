import torch
import numpy as np
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.autoencoder import AutoEncoder
from pipeline.preprocess_num import invoice_to_features

CKPT_PATH = Path("models/checkpoints/autoencoder.pt")

def load_autoencoder():
    ckpt = torch.load(CKPT_PATH, map_location="cpu")
    model = AutoEncoder(in_dim=ckpt["in_dim"])
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, ckpt

def anomaly_score(gt: dict):
    model, ckpt = load_autoencoder()
    mean = np.array(ckpt["mean"], dtype=np.float32)
    std = np.array(ckpt["std"], dtype=np.float32)

    x = invoice_to_features(gt)
    xn = (x - mean) / std
    xb = torch.tensor(xn).unsqueeze(0)

    with torch.no_grad():
        recon = model(xb).squeeze(0).numpy()
    err = float(((recon - xn) ** 2).mean())

    # scale to (0–1) using threshold
    threshold = ckpt["threshold"]
    score = min(err / (threshold + 1e-6), 3.0) / 3.0
    is_anomaly = err > threshold
    return score, is_anomaly, err, threshold

