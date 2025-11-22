# field parsing
import torch
import sys
from pathlib import Path
from typing import List

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
