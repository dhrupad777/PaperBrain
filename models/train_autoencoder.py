import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.preprocess_num import load_feature_matrix
from models.autoencoder import AutoEncoder

SAVE_DIR = Path("models/checkpoints")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

def main():
    X, _ = load_feature_matrix()

    # normalize features
    mean = X.mean(axis=0)
    std = X.std(axis=0) + 1e-6
    Xn = (X - mean) / std

    ds = TensorDataset(torch.tensor(Xn))
    dl = DataLoader(ds, batch_size=16, shuffle=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoEncoder(in_dim=X.shape[1]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = torch.nn.MSELoss()

    epochs = 40
    for ep in range(1, epochs+1):
        model.train()
        total_loss = 0
        for (xb,) in dl:
            xb = xb.to(device)
            recon = model(xb)
            loss = loss_fn(recon, xb)

            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item()

        if ep % 5 == 0:
            print(f"Epoch {ep}/{epochs} | loss={total_loss/len(dl):.6f}")

    # reconstruction errors on full set
    model.eval()
    with torch.no_grad():
        xb = torch.tensor(Xn).to(device)
        recon = model(xb)
        errs = ((recon - xb)**2).mean(dim=1).cpu().numpy()

    # threshold = 95th percentile of normal errors
    threshold = float(np.percentile(errs, 95))

    ckpt = {
        "model_state": model.state_dict(),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "threshold": threshold,
        "in_dim": X.shape[1],
    }
    torch.save(ckpt, SAVE_DIR / "autoencoder.pt")
    print("Saved -> models/checkpoints/autoencoder.pt")
    print("Threshold:", threshold)

if __name__ == "__main__":
    main()

