import torch
from pathlib import Path
from models.bilstm_crf import BiLSTMCRF

CKPT_PATH = Path("models/checkpoints/bilstm_crf.pt")

def load_bilstm_extractor(device="cpu"):
    """
    Loads: model, vocab, id2tag, max_len
    from the saved checkpoint.
    """
    ckpt = torch.load(CKPT_PATH, map_location=device)
    
    vocab = ckpt["vocab"]
    id2tag = ckpt["id2tag"]
    max_len = ckpt.get("max_len", 256)
    
    model = BiLSTMCRF(
        vocab_size=len(vocab),
        tagset_size=len(id2tag),
        emb_dim=128,  # Default from BiLSTMCRF class
        hidden_dim=256,  # Default from BiLSTMCRF class
    )
    model.load_state_dict(ckpt["model_state"])
    model.to(device)
    model.eval()
    
    return model, vocab, id2tag, max_len

