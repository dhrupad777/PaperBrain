import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.forecast import load_time_series

SAVE_DIR = Path("models/checkpoints")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

class LSTMForecast(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=32, batch_first=True)
        self.fc = nn.Linear(32, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1])

def make_windows(values, win=5):
    X, y = [], []
    for i in range(len(values)-win):
        X.append(values[i:i+win])
        y.append(values[i+win])
    return np.array(X), np.array(y)

def main():
    _, values = load_time_series()
    values = (values - values.mean()) / (values.std() + 1e-6)

    X, y = make_windows(values, win=5)
    X = torch.tensor(X).unsqueeze(-1)  # (B, win, 1)
    y = torch.tensor(y).unsqueeze(-1)

    ds = TensorDataset(X, y)
    dl = DataLoader(ds, batch_size=16, shuffle=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = LSTMForecast().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    epochs = 60
    for ep in range(1, epochs+1):
        model.train()
        total_loss = 0
        for xb, yb in dl:
            xb, yb = xb.to(device), yb.to(device)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item()
        if ep % 10 == 0:
            print(f"Epoch {ep}/{epochs} loss={total_loss/len(dl):.4f}")

    torch.save({"model_state": model.state_dict()}, SAVE_DIR / "forecast_lstm.pt")
    print("Saved -> models/checkpoints/forecast_lstm.pt")

if __name__ == "__main__":
    main()

