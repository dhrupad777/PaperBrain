import json
import numpy as np
from pathlib import Path

JSON_DIR = Path("data/raw/synthetic/json")

def invoice_to_features(gt: dict):
    totals = gt.get("totals", {})
    items = gt.get("items", [])

    subtotal = float(totals.get("subtotal", 0))
    tax_total = float(totals.get("tax_total", 0))
    grand_total = subtotal + tax_total

    n_items = len(items)
    qty_sum = sum(float(it.get("qty", 0)) for it in items)
    rate_avg = np.mean([float(it.get("rate", 0)) for it in items]) if items else 0
    item_total_sum = sum(float(it.get("total", 0)) for it in items)

    # ratios help detect mismatch/anomaly
    tax_ratio = tax_total / subtotal if subtotal > 0 else 0
    total_ratio = grand_total / (item_total_sum + 1e-6)

    return np.array([
        subtotal,
        tax_total,
        grand_total,
        n_items,
        qty_sum,
        rate_avg,
        item_total_sum,
        tax_ratio,
        total_ratio
    ], dtype=np.float32)

def load_feature_matrix():
    feats = []
    files = sorted(JSON_DIR.glob("inv_*.json"))
    for fp in files:
        gt = json.loads(fp.read_text(encoding="utf-8"))
        feats.append(invoice_to_features(gt))
    return np.stack(feats), files

