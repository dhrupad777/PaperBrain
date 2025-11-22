import json
import numpy as np
from pathlib import Path
from datetime import datetime

JSON_DIR = Path("data/raw/synthetic/json")

def load_time_series():
    pts = []
    for fp in JSON_DIR.glob("inv_*.json"):
        gt = json.loads(fp.read_text(encoding="utf-8"))
        d = gt["invoice"]["date"]
        # synthetic format like 12-Aug-25
        dt = datetime.strptime(d, "%d-%b-%y")
        total = gt["totals"]["subtotal"] + gt["totals"]["tax_total"]
        pts.append((dt, float(total)))

    pts.sort(key=lambda x: x[0])
    dates = [p[0] for p in pts]
    values = np.array([p[1] for p in pts], dtype=np.float32)
    return dates, values
