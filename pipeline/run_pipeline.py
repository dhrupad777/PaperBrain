import json
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch

from models.infer_autoencoder import anomaly_score
from models.infer_bilstm_crf import load_bilstm_extractor
from pipeline.ocr_gcp import ocr_tokens_gcp
from pipeline.ocr import ocr_tokens  # keep Tesseract fallback

# CNN preprocessing (optional - for future CNN classifier integration)
# from pipeline.preprocess_cnn import load_image_tensor

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

    # ---- OCR (GCP primary, Tesseract fallback) ----
    # Pass original image path directly to GCP - no preprocessing before OCR
    # GCP Vision handles its own image enhancement
    try:
        text, tokens = ocr_tokens_gcp(str(png_path))
        print("✅ GCP Vision OCR used")
    except Exception as e:
        print("⚠️ GCP OCR failed, fallback to Tesseract:", e)
        text, tokens = ocr_tokens(str(png_path))

    # 2) BiLSTM-CRF extraction
    model, vocab, id2tag, max_len = load_bilstm_extractor()
    fields, tags = extract_with_bilstm(tokens, model, vocab, id2tag, max_len)

    # 2.5) Fallback extraction if ANN returns empty
    if not fields:
        from pipeline.extract import fallback_extract
        fields = fallback_extract(text)

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

    # 4) Forecast (mocked for prototype)
    forecast_next_total = 1250.00  # Mock value or implement simple logic

    return {
        "ocr_text": text,
        "ocr_tokens_preview": tokens[:200],
        "tokens": tokens,
        "tags": tags,
        "extracted_fields": fields,
        "anomaly": anomaly,
        "forecast_next_total": forecast_next_total
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
