import json
import re
import random
import os
from pathlib import Path
from typing import List, Tuple, Dict

import pytesseract
from PIL import Image

# Try to set Tesseract path for Windows (common installation location)
if os.name == 'nt':  # Windows
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

JSON_DIR = Path("data/raw/synthetic/json")
PNG_DIR  = Path("data/raw/synthetic/png")   # use clean images first
BIO_DIR  = Path("data/raw/synthetic/bio")
BIO_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_PATH = BIO_DIR / "train.txt"
VAL_PATH   = BIO_DIR / "val.txt"

random.seed(42)

# ----------------------------
# Helpers
# ----------------------------

def ocr_text(png_path: Path) -> str:
    try:
        img = Image.open(png_path).convert("RGB")
        text = pytesseract.image_to_string(img)
        return text
    except pytesseract.pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR is not installed or not in PATH.\n"
            "Please install Tesseract OCR:\n"
            "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "2. Install it (default location: C:\\Program Files\\Tesseract-OCR)\n"
            "3. Add to PATH or set: pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'"
        )

def tokenize(text: str) -> List[str]:
    # simple word tokenizer
    tokens = re.findall(r"[A-Za-z0-9₹.,/%\-]+", text)
    return tokens

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def find_spans(tokens: List[str], field_value: str) -> List[Tuple[int,int]]:
    """
    Find approximate spans where field_value appears in tokens.
    Returns list of (start, end) token indices.
    """
    if not field_value:
        return []
    fv = normalize(field_value)

    # try direct n-gram match up to 6 tokens
    for n in range(6, 0, -1):
        for i in range(len(tokens)-n+1):
            chunk = normalize(" ".join(tokens[i:i+n]))
            if chunk == fv:
                return [(i, i+n)]
    return []

def tag_tokens(tokens: List[str], spans: Dict[str, List[Tuple[int,int]]]) -> List[str]:
    tags = ["O"] * len(tokens)

    for label, ranges in spans.items():
        for (s, e) in ranges:
            if s < 0 or e > len(tokens): 
                continue
            tags[s] = f"B-{label}"
            for j in range(s+1, e):
                tags[j] = f"I-{label}"
    return tags

def extract_fields(gt: dict) -> Dict[str, str]:
    seller = gt.get("seller", {})
    inv = gt.get("invoice", {})
    totals = gt.get("totals", {})

    vendor = seller.get("name", "")
    date = inv.get("date", "")
    inv_no = inv.get("no", "")
    total = str(round(totals.get("subtotal", 0) + totals.get("tax_total", 0), 2))

    # also try matching subtotal alone if OCR misses tax line
    subtotal = str(round(totals.get("subtotal", 0), 2))

    return {
        "VENDOR": vendor,
        "DATE": date,
        "INVOICE_NO": inv_no,
        "TOTAL": total,
        "SUBTOTAL": subtotal,
    }

def build_bio_for_one(json_path: Path) -> List[Tuple[str,str]]:
    base = json_path.stem
    png_path = PNG_DIR / f"{base}.png"
    if not png_path.exists():
        return []

    gt = json.loads(json_path.read_text(encoding="utf-8"))
    fields = extract_fields(gt)

    text = ocr_text(png_path)
    tokens = tokenize(text)

    spans = {}
    for label in ["VENDOR", "DATE", "INVOICE_NO", "TOTAL", "SUBTOTAL"]:
        spans[label] = find_spans(tokens, fields[label])

    # if TOTAL not found, allow SUBTOTAL to tag TOTAL
    if not spans["TOTAL"] and spans["SUBTOTAL"]:
        spans["TOTAL"] = spans["SUBTOTAL"]

    # remove subtotal label (only used as fallback)
    spans.pop("SUBTOTAL", None)

    tags = tag_tokens(tokens, spans)

    return list(zip(tokens, tags))

def write_split(samples: List[Path], out_path: Path):
    with out_path.open("w", encoding="utf-8") as f:
        for jp in samples:
            bio_pairs = build_bio_for_one(jp)
            if not bio_pairs:
                continue
            for tok, tag in bio_pairs:
                f.write(f"{tok}\t{tag}\n")
            f.write("\n")

def main(val_ratio=0.2):
    all_json = sorted(JSON_DIR.glob("inv_*.json"))
    random.shuffle(all_json)

    cut = int(len(all_json) * (1 - val_ratio))
    train_set, val_set = all_json[:cut], all_json[cut:]

    write_split(train_set, TRAIN_PATH)
    write_split(val_set, VAL_PATH)

    print(f"BIO done. train={len(train_set)} val={len(val_set)}")
    print(f"train -> {TRAIN_PATH}")
    print(f"val   -> {VAL_PATH}")

if __name__ == "__main__":
    main()

