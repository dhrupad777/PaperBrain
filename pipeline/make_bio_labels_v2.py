import json
import re
import random
import os
from pathlib import Path
from typing import List, Tuple, Dict
import pytesseract
from PIL import Image
from difflib import SequenceMatcher

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
PNG_DIR  = Path("data/raw/synthetic/png")
BIO_DIR  = Path("data/raw/synthetic/bio")
BIO_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_PATH = BIO_DIR / "train.txt"
VAL_PATH   = BIO_DIR / "val.txt"

random.seed(42)

def ocr_text(png_path: Path) -> str:
    return pytesseract.image_to_string(Image.open(png_path).convert("RGB"))

def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9₹.,/%\-]+", text)

def norm(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("₹", "").replace("rs.", "").replace("rs", "")
    s = re.sub(r"[,]", "", s)           # remove commas in numbers
    s = re.sub(r"[^a-z0-9.\- ]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def fuzzy_equal(a: str, b: str, thr=0.85) -> bool:
    return SequenceMatcher(None, a, b).ratio() >= thr

def find_spans(tokens: List[str], field_value: str) -> List[Tuple[int,int]]:
    if not field_value:
        return []
    fv = norm(field_value)

    # direct n-gram match up to 8 tokens
    for n in range(8, 0, -1):
        for i in range(len(tokens)-n+1):
            chunk = norm(" ".join(tokens[i:i+n]))
            if chunk == fv:
                return [(i, i+n)]

    # fuzzy match for long fields (vendor)
    fv_tokens = fv.split()
    if len(fv_tokens) >= 2:
        for n in range(min(6, len(fv_tokens)), 1, -1):
            for i in range(len(tokens)-n+1):
                chunk = norm(" ".join(tokens[i:i+n]))
                if fuzzy_equal(chunk, fv, thr=0.82):
                    return [(i, i+n)]

    return []

def tag_tokens(tokens: List[str], spans: Dict[str, List[Tuple[int,int]]]) -> List[str]:
    tags = ["O"] * len(tokens)
    for label, ranges in spans.items():
        for s, e in ranges:
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
    subtotal = str(round(totals.get("subtotal", 0), 2))

    # add alt date formats
    try:
        d = re.sub(r"(\d{2})-([A-Za-z]{3})-(\d{2})", r"\1 \2 \3", date)
    except:
        d = date

    return {
        "VENDOR": vendor,
        "DATE": date,
        "DATE_ALT": d,
        "INVOICE_NO": inv_no,
        "TOTAL": total,
        "SUBTOTAL": subtotal,
    }

def build_bio_for_one(json_path: Path):
    base = json_path.stem
    png_path = PNG_DIR / f"{base}.png"
    if not png_path.exists():
        return []

    gt = json.loads(json_path.read_text(encoding="utf-8"))
    fields = extract_fields(gt)

    text = ocr_text(png_path)
    tokens = tokenize(text)

    spans = {}
    spans["VENDOR"] = find_spans(tokens, fields["VENDOR"])
    spans["INVOICE_NO"] = find_spans(tokens, fields["INVOICE_NO"])
    spans["TOTAL"] = find_spans(tokens, fields["TOTAL"]) or find_spans(tokens, fields["SUBTOTAL"])
    spans["DATE"] = find_spans(tokens, fields["DATE"]) or find_spans(tokens, fields["DATE_ALT"])

    tags = tag_tokens(tokens, spans)
    return list(zip(tokens, tags))

def write_split(samples, out_path):
    with out_path.open("w", encoding="utf-8") as f:
        for jp in samples:
            pairs = build_bio_for_one(jp)
            if not pairs:
                continue
            for tok, tag in pairs:
                f.write(f"{tok}\t{tag}\n")
            f.write("\n")

def main(val_ratio=0.2):
    all_json = sorted(JSON_DIR.glob("inv_*.json"))
    random.shuffle(all_json)

    cut = int(len(all_json) * (1 - val_ratio))
    train, val = all_json[:cut], all_json[cut:]

    write_split(train, TRAIN_PATH)
    write_split(val, VAL_PATH)

    print(f"BIO v2 done. train={len(train)} val={len(val)}")

if __name__ == "__main__":
    main()

