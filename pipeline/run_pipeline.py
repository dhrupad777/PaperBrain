import json
from pathlib import Path
import sys
import re

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytesseract
from PIL import Image
import torch

from models.infer_autoencoder import anomaly_score
from models.bilstm_crf import BiLSTMCRF

# CNN preprocessing (optional - for future CNN classifier integration)
# from pipeline.preprocess_cnn import load_image_tensor

BILSTM_CKPT = Path("models/checkpoints/bilstm_crf.pt")

# Try to set Tesseract path for Windows
import os
if os.name == 'nt':  # Windows
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

def load_bilstm_extractor():
    ckpt = torch.load(BILSTM_CKPT, map_location="cpu")
    vocab, tag2id, id2tag = ckpt["vocab"], ckpt["tag2id"], ckpt["id2tag"]
    max_len = ckpt["max_len"]

    model = BiLSTMCRF(len(vocab), len(tag2id))
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, vocab, id2tag, max_len

def ocr_tokens(png_path):
    text = pytesseract.image_to_string(Image.open(png_path).convert("RGB"))
    return re.findall(r"[A-Za-z0-9₹.,/%\-]+", text)

def extract_with_bilstm(tokens, model, vocab, id2tag, max_len):
    x = [vocab.get(t.lower(), vocab["<UNK>"]) for t in tokens][:max_len]
    mask = [1]*len(x)
    pad = max_len-len(x)
    x += [0]*pad
    mask += [0]*pad

    x = torch.tensor([x])
    mask = torch.tensor([mask])
    path = model.decode(x, mask)[0][:len(tokens)]
    tags = [id2tag[i] for i in path]

    fields = {}
    cur_label, cur_words = None, []
    for tok, tag in zip(tokens, tags):
        if tag.startswith("B-"):
            if cur_label:
                fields[cur_label] = " ".join(cur_words)
            cur_label = tag[2:]
            cur_words = [tok]
        elif tag.startswith("I-") and cur_label == tag[2:]:
            cur_words.append(tok)
        else:
            if cur_label:
                fields[cur_label] = " ".join(cur_words)
            cur_label, cur_words = None, []

    if cur_label:
        fields[cur_label] = " ".join(cur_words)

    return fields, tags

def run_pipeline(png_path: str, json_gt_path: str=None):
    png_path = Path(png_path)

    # 1) OCR
    tokens = ocr_tokens(png_path)

    # 2) BiLSTM-CRF extraction
    model, vocab, id2tag, max_len = load_bilstm_extractor()
    fields, tags = extract_with_bilstm(tokens, model, vocab, id2tag, max_len)

    # 3) Anomaly score (if GT json provided)
    anomaly = None
    if json_gt_path:
        gt = json.loads(Path(json_gt_path).read_text(encoding="utf-8"))
        score, is_anom, err, thr = anomaly_score(gt)
        anomaly = {
            "score": score,
            "is_anomaly": is_anom,
            "recon_error": err,
            "threshold": thr
        }

    return {
        "tokens": tokens,
        "tags": tags,
        "extracted_fields": fields,
        "anomaly": anomaly
    }

# Alias for server.py compatibility
def run_on_invoice(json_path, png_path):
    """Wrapper for server.py - accepts Path objects or strings"""
    json_str = str(json_path) if json_path else None
    png_str = str(png_path)
    return run_pipeline(png_str, json_str)

if __name__ == "__main__":
    # quick test on one file
    sample_png = "data/raw/synthetic/png/inv_00001.png"
    sample_json = "data/raw/synthetic/json/inv_00001.json"
    out = run_pipeline(sample_png, sample_json)
    print(json.dumps(out, indent=2))
