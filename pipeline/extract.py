# field parsing
import torch
import sys
import re
from pathlib import Path
from typing import List, Dict

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

CKPT_PATH = Path("models/checkpoints/bilstm_crf.pt")

def load_extractor():
    """Load the trained BiLSTM-CRF model and checkpoint."""
    ckpt = torch.load(CKPT_PATH, map_location="cpu")
    from models.bilstm_crf import BiLSTMCRF
    
    model = BiLSTMCRF(len(ckpt["vocab"]), len(ckpt["tag2id"]))
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, ckpt

def predict_tags(tokens: List[str]) -> List[str]:
    """
    Predict BIO tags for a list of tokens using the trained BiLSTM-CRF model.
    
    Args:
        tokens: List of token strings
    
    Returns:
        List of predicted BIO tags
    """
    model, ckpt = load_extractor()
    vocab, id2tag = ckpt["vocab"], ckpt["id2tag"]
    max_len = ckpt["max_len"]

    x = [vocab.get(t.lower(), vocab["<UNK>"]) for t in tokens][:max_len]
    mask = [1] * len(x)
    pad_len = max_len - len(x)
    x += [0] * pad_len
    mask += [0] * pad_len

    x = torch.tensor([x])
    mask = torch.tensor([mask])

    path = model.decode(x, mask)[0][:len(tokens)]
    return [id2tag[i] for i in path]

def fallback_extract(text: str) -> Dict[str, str]:
    """
    Fallback extraction optimized for clean GCP OCR text.
    This ensures correct extraction when ANN model returns empty or weak results.
    
    Args:
        text: Raw OCR text (expected to be clean from GCP Vision)
    
    Returns:
        Dictionary of extracted fields
    """
    out = {}
    
    # VENDOR: take first big uppercase org line containing these keywords
    vendor_match = re.search(
        r"\b([A-Z][A-Z\s&.,]{5,}(ASSOCIATION|ENTERPRISES|LLP|LTD|PRIVATE|PVT|COMPANY))\b",
        text
    )
    if vendor_match:
        out["VENDOR"] = vendor_match.group(1).strip()
    
    # DATE
    date_match = re.search(
        r"\b(\d{1,2}[-/][A-Za-z]{3,9}[-/]\d{2,4})\b",
        text
    )
    if date_match:
        out["DATE"] = date_match.group(1)
    
    # INVOICE NO: prefer explicit label
    inv_match = re.search(
        r"(Invoice\s*No\.?\s*[:\-]?\s*)([A-Za-z0-9\-\/]+)",
        text,
        flags=re.I
    )
    if inv_match:
        out["INVOICE_NO"] = inv_match.group(2)
    else:
        top_chunk = "\n".join(text.splitlines()[:25])
        inv2 = re.search(r"\b([A-Z]{1,4}-\d{1,6})\b", top_chunk)
        if inv2:
            out["INVOICE_NO"] = inv2.group(1)
    
    # TOTAL: prefer total line, else max amount
    total_line = re.search(
        r"\b(Grand\s*Total|Total)\b[^\d₹]{0,20}(₹?\s?[\d,]+\.?\d{0,2})",
        text,
        flags=re.I
    )
    if total_line:
        out["TOTAL"] = total_line.group(2).strip()
    else:
        amounts = re.findall(r"₹\s?[\d,]+\.?\d{0,2}", text)
        if amounts:
            def to_num(x):
                return float(x.replace("₹","").replace(",","").strip())
            out["TOTAL"] = max(amounts, key=to_num)
    
    if "TOTAL" in out and not out["TOTAL"].startswith("₹"):
        out["TOTAL"] = "₹ " + out["TOTAL"]
    
    return out
