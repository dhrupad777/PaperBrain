import torch
import torch.nn as nn


class CRF(nn.Module):
    """
    A minimal linear-chain CRF layer.
    """
    def __init__(self, num_tags: int):
        super().__init__()
        self.num_tags = num_tags
        self.start_tag = num_tags
        self.end_tag = num_tags + 1

        # transition scores: from_tag -> to_tag
        self.transitions = nn.Parameter(torch.randn(num_tags + 2, num_tags + 2))

        # disallow transitions into START and out of END
        self.transitions.data[:, self.start_tag] = -1e4
        self.transitions.data[self.end_tag, :] = -1e4

    def forward(self, emissions, tags, mask):
        # negative log likelihood
        log_numerator = self.score_sentence(emissions, tags, mask)
        log_denominator = self.compute_log_partition(emissions, mask)
        return torch.mean(log_denominator - log_numerator)

    def score_sentence(self, emissions, tags, mask):
        batch_size, seq_len, num_tags = emissions.size()

        # add START, END
        score = torch.zeros(batch_size, device=emissions.device)
        tags = torch.cat(
            [torch.full((batch_size, 1), self.start_tag, dtype=torch.long, device=emissions.device), tags],
            dim=1,
        )

        for t in range(seq_len):
            cur_tag = tags[:, t + 1]
            prev_tag = tags[:, t]

            # Use gather for proper indexing
            emit_score = emissions[:, t, :].gather(1, cur_tag.unsqueeze(1)).squeeze(1)
            trans_score = self.transitions[prev_tag, cur_tag]

            score += (emit_score + trans_score) * mask[:, t]

        # transition to END
        last_tag_indices = mask.sum(1).long()
        last_tags = tags.gather(1, last_tag_indices.unsqueeze(1)).squeeze(1)
        score += self.transitions[last_tags, self.end_tag]

        return score

    def compute_log_partition(self, emissions, mask):
        batch_size, seq_len, num_tags = emissions.size()

        alpha = torch.full((batch_size, num_tags + 2), -1e4, device=emissions.device)
        alpha[:, self.start_tag] = 0.0

        for t in range(seq_len):
            emit_t = emissions[:, t]  # (B, num_tags)

            alpha_t = []
            for next_tag in range(num_tags):
                emit_score = emit_t[:, next_tag].unsqueeze(1)
                trans_score = self.transitions[:, next_tag].unsqueeze(0)
                scores = alpha + trans_score + emit_score
                alpha_t.append(torch.logsumexp(scores, dim=1))

            alpha_t = torch.stack(alpha_t, dim=1)
            mask_t = mask[:, t].unsqueeze(1)
            alpha = alpha_t * mask_t + alpha[:, :num_tags] * (1 - mask_t)

            # pad back to num_tags+2
            pad = torch.full((batch_size, 2), -1e4, device=emissions.device)
            alpha = torch.cat([alpha, pad], dim=1)

        alpha = alpha[:, :num_tags]
        alpha = alpha + self.transitions[:num_tags, self.end_tag].unsqueeze(0)
        return torch.logsumexp(alpha, dim=1)

    def decode(self, emissions, mask):
        batch_size, seq_len, num_tags = emissions.size()

        # INIT from START -> tag transition + first emission
        alpha = self.transitions[self.start_tag, :num_tags].unsqueeze(0) + emissions[:, 0]
        backpointers = []

        for t in range(1, seq_len):
            emit_t = emissions[:, t]  # (B, num_tags)

            # (B, prev_tag, next_tag)
            scores = alpha.unsqueeze(2) + self.transitions[:num_tags, :num_tags].unsqueeze(0)
            best_scores, best_tags = scores.max(dim=1)  # max over prev_tag

            alpha = best_scores + emit_t
            backpointers.append(best_tags)

            # apply mask
            mask_t = mask[:, t].unsqueeze(1)
            alpha = alpha * mask_t + alpha * (1 - mask_t)

        # END transition
        alpha = alpha + self.transitions[:num_tags, self.end_tag].unsqueeze(0)
        best_scores, best_last_tags = alpha.max(dim=1)

        # BACKTRACE
        best_paths = []
        for b in range(batch_size):
            seq_end = int(mask[b].sum().item()) - 1
            last_tag = best_last_tags[b].item()
            path = [last_tag]

            for bp_t in reversed(backpointers[:seq_end]):
                last_tag = bp_t[b, last_tag].item()
                path.append(last_tag)

            path.reverse()
            best_paths.append(path)

        return best_paths


class BiLSTMCRF(nn.Module):
    def __init__(self, vocab_size, tagset_size, emb_dim=128, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.bilstm = nn.LSTM(
            emb_dim, hidden_dim // 2,
            num_layers=1, batch_first=True, bidirectional=True
        )
        self.fc = nn.Linear(hidden_dim, tagset_size)
        self.crf = CRF(tagset_size)

    def forward(self, x, tags=None, mask=None):
        emb = self.embedding(x)
        lstm_out, _ = self.bilstm(emb)
        emissions = self.fc(lstm_out)

        if tags is not None:
            loss = self.crf(emissions, tags, mask)
            return loss
        return emissions

    def decode(self, x, mask):
        emissions = self.forward(x)
        return self.crf.decode(emissions, mask)

