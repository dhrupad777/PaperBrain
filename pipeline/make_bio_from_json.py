import json
import re
import random
from pathlib import Path

JSON_DIR = Path("data/raw/synthetic/json")
BIO_DIR = Path("data/raw/synthetic/bio")
BIO_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_PATH = BIO_DIR / "train.txt"
VAL_PATH = BIO_DIR / "val.txt"

random.seed(42)

def tokenize(text):
    return re.findall(r"[A-Za-z0-9₹.,/%\-]+", text)

def make_sentence_and_tags(gt):
    """
    Build a synthetic sentence with perfect ordering so BIO labels are clean.
    """
    fields = {}

    seller = gt["seller"]
    inv = gt["invoice"]
    totals = gt["totals"]

    fields["VENDOR"] = seller["name"]
    fields["DATE"] = inv["date"]
    fields["INVOICE_NO"] = inv["no"]
    fields["TOTAL"] = str(round(totals["subtotal"] + totals["tax_total"], 2))

    sentence = f"{seller['name']} invoice {inv['no']} dated {inv['date']} total {fields['TOTAL']}"
    tokens = tokenize(sentence)

    tags = ["O"] * len(tokens)

    for label, value in fields.items():
        v_tokens = tokenize(value)
        for i in range(len(tokens)):
            if tokens[i:i+len(v_tokens)] == v_tokens:
                tags[i] = f"B-{label}"
                for j in range(1, len(v_tokens)):
                    tags[i+j] = f"I-{label}"

    return list(zip(tokens, tags))

def write_bio(samples, out_path):
    with out_path.open("w", encoding="utf-8") as f:
        for jp in samples:
            gt = json.loads(jp.read_text())
            pairs = make_sentence_and_tags(gt)
            for t, tg in pairs:
                f.write(f"{t}\t{tg}\n")
            f.write("\n")

def main():
    all_json = sorted(JSON_DIR.glob("inv_*.json"))
    random.shuffle(all_json)

    split = int(0.8 * len(all_json))
    train, val = all_json[:split], all_json[split:]

    write_bio(train, TRAIN_PATH)
    write_bio(val, VAL_PATH)

    print("BIO from JSON created successfully!")

if __name__ == "__main__":
    main()
