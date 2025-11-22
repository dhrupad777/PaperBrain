import json
import random
import sys
from pathlib import Path
from collections import Counter

import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.bilstm_crf import BiLSTMCRF

BIO_TRAIN = Path("data/raw/synthetic/bio/train.txt")
BIO_VAL   = Path("data/raw/synthetic/bio/val.txt")
SAVE_DIR  = Path("models/checkpoints")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)
torch.manual_seed(42)


# ----------------------------
# BIO Loader
# ----------------------------
def read_bio(path):
    sentences = []
    tags = []

    cur_words, cur_tags = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            if cur_words:
                sentences.append(cur_words)
                tags.append(cur_tags)
                cur_words, cur_tags = [], []
            continue
        w, t = line.split()
        cur_words.append(w)
        cur_tags.append(t)

    if cur_words:
        sentences.append(cur_words)
        tags.append(cur_tags)
    return sentences, tags


def downsample_O(sentences, tags, keep_o_prob=0.35):
    """
    Downsample O tokens to reduce class imbalance.
    Keeps all entity tokens, but only keeps O tokens with probability keep_o_prob.
    """
    new_s, new_t = [], []
    for s, t in zip(sentences, tags):
        s2, t2 = [], []
        for w, tag in zip(s, t):
            if tag == "O":
                if random.random() < keep_o_prob:
                    s2.append(w)
                    t2.append(tag)
            else:
                s2.append(w)
                t2.append(tag)
        # Keep only sentences that still have entities (at least one non-O tag)
        if any(x != "O" for x in t2):
            new_s.append(s2)
            new_t.append(t2)
    return new_s, new_t


def build_vocab(sentences, min_freq=1):
    counter = Counter(w.lower() for s in sentences for w in s)
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for w, c in counter.items():
        if c >= min_freq:
            vocab[w] = len(vocab)
    return vocab


def build_tag_map(tags):
    uniq = sorted({t for seq in tags for t in seq})
    tag2id = {t: i for i, t in enumerate(uniq)}
    id2tag = {i: t for t, i in tag2id.items()}
    return tag2id, id2tag


class BioDataset(Dataset):
    def __init__(self, sentences, tags, vocab, tag2id, max_len=256):
        self.sentences = sentences
        self.tags = tags
        self.vocab = vocab
        self.tag2id = tag2id
        self.max_len = max_len

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        words = self.sentences[idx]
        tags  = self.tags[idx]

        x = [self.vocab.get(w.lower(), self.vocab["<UNK>"]) for w in words][:self.max_len]
        # Handle missing tags gracefully (shouldn't happen if tag map built from all data)
        y = [self.tag2id.get(t, self.tag2id.get("O", 0)) for t in tags][:self.max_len]

        mask = [1] * len(x)

        # pad
        pad_len = self.max_len - len(x)
        x += [0] * pad_len
        y += [0] * pad_len
        mask += [0] * pad_len

        return torch.tensor(x), torch.tensor(y), torch.tensor(mask)


def evaluate(model, loader, id2tag, device):
    model.eval()
    all_true, all_pred = [], []

    with torch.no_grad():
        for x, y, mask in loader:
            x, y, mask = x.to(device), y.to(device), mask.to(device)
            paths = model.decode(x, mask)

            for i, path in enumerate(paths):
                seq_len = int(mask[i].sum().item())
                true_tags = y[i][:seq_len].tolist()
                pred_tags = path[:seq_len]

                all_true.extend(true_tags)
                all_pred.extend(pred_tags)

    true_labels = [id2tag[i] for i in all_true]
    pred_labels = [id2tag[i] for i in all_pred]

    print(classification_report(true_labels, pred_labels, digits=4))


def main():
    train_s, train_t = read_bio(BIO_TRAIN)
    val_s, val_t     = read_bio(BIO_VAL)

    # Downsample O tokens in training to reduce class imbalance
    train_s, train_t = downsample_O(train_s, train_t, keep_o_prob=0.35)
    
    vocab = build_vocab(train_s)
    # Build tag map from both train and val to ensure all tags are included
    all_tags = train_t + val_t
    tag2id, id2tag = build_tag_map(all_tags)

    train_ds = BioDataset(train_s, train_t, vocab, tag2id)
    val_ds   = BioDataset(val_s, val_t, vocab, tag2id)

    train_loader = DataLoader(train_ds, batch_size=8, shuffle=True)
    val_loader   = DataLoader(val_ds, batch_size=8, shuffle=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = BiLSTMCRF(vocab_size=len(vocab), tagset_size=len(tag2id)).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    epochs = 15
    for ep in range(1, epochs + 1):
        model.train()
        total_loss = 0

        for x, y, mask in train_loader:
            x, y, mask = x.to(device), y.to(device), mask.to(device)

            loss = model(x, tags=y, mask=mask)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"\nEpoch {ep}/{epochs} | loss={total_loss/len(train_loader):.4f}")
        evaluate(model, val_loader, id2tag, device)

    # save
    ckpt = {
        "model_state": model.state_dict(),
        "vocab": vocab,
        "tag2id": tag2id,
        "id2tag": id2tag,
        "max_len": 256
    }
    torch.save(ckpt, SAVE_DIR / "bilstm_crf.pt")
    print("\nSaved model -> models/checkpoints/bilstm_crf.pt")


if __name__ == "__main__":
    main()

