#!/usr/bin/env python3
"""Trainer for the bomb pot net.

    python tools/bombpot/train.py --data "work/mem/*.adv.bps" --out adv.bin
        [--kind adv|strat] [--hidden 256] [--layers 3] [--steps 4000]
        [--batch 8192] [--lr 1e-3] [--init prev.bin] [--device cuda|cpu]
        [--check path/to/bombpot]

Reads the example files `bombpot gen` writes (crates/solver/src/bombpot/
deepcfr.rs), fits a net to them and writes it in the format the engine reads
(crates/solver/src/bombpot/net.rs). Two kinds of net:

- adv: what each action is worth compared with the mix played, per unit of
  pot. The next run of self-play plays in proportion to the positive ones.
- strat: the mix played, averaged over every run. This is the net to play.

Later runs count for more (an example of run k weighs k times one of run 1),
as in the table solver. Every batch shows each example with its four suits
renamed at random: the same hand in other suits must play the same way.

`--check` runs the engine's `netcheck` on the first examples and fails if
its outputs differ from this file's.
"""
import argparse
import glob
import json
import struct
import subprocess
import sys
import time

import numpy as np
import torch
from torch import nn

PUB, HAND, MENU = 57, 16, 6
DENSE = PUB + HAND
EMB_ROWS = 52 + 2 * 156
KINDS = {"adv": 0, "strat": 1}
REC = np.dtype([
    ("cards", "u1", 12), ("mask", "u1"), ("street", "u1"), ("player", "u1"), ("pad", "u1"),
    ("weight", "<f4"), ("pub", "<u4"), ("hand", "<f4", HAND), ("target", "<f4", MENU),
])
HEAD = struct.Struct("<4sIIIQQIIII")
NET_HEAD = struct.Struct("<4s8I")


def read_examples(path):
    """One file: (kind, run number, rows of betting inputs, examples)."""
    with open(path, "rb") as f:
        magic, version, kind, it, n, n_pub, pub, hand, menu, rec = HEAD.unpack(f.read(HEAD.size))
        if magic != b"BPS1" or version != 1 or (pub, hand, menu, rec) != (PUB, HAND, MENU, REC.itemsize):
            raise ValueError(f"{path}: not an examples file this trainer reads")
        rows = np.fromfile(f, dtype="<f4", count=n_pub * PUB).reshape(n_pub, PUB)
        recs = np.fromfile(f, dtype=REC, count=n)
    if len(recs) != n:
        raise ValueError(f"{path}: cut short")
    return kind, it, rows, recs


class Memory:
    """Examples of every run so far. Past the cap it holds a uniform random
    sample of everything seen (reservoir sampling)."""

    FIELDS = ("cards", "mask", "street", "weight", "pub", "hand", "target")

    def __init__(self, cap, seed=0):
        self.cap = cap
        self.rng = np.random.default_rng(seed)
        self.rows = np.zeros((0, PUB), np.float32)
        self.cards = np.zeros((0, 12), np.uint8)
        self.mask = np.zeros(0, np.uint8)
        self.street = np.zeros(0, np.uint8)
        self.weight = np.zeros(0, np.float32)
        self.pub = np.zeros(0, np.int64)
        self.hand = np.zeros((0, HAND), np.float32)
        self.target = np.zeros((0, MENU), np.float32)
        self.kind = None
        self.seen = 0

    def add(self, path, power=1.0):
        """Add one file. An example of round t counts t^power times."""
        kind, it, rows, recs = read_examples(path)
        if self.kind not in (None, kind):
            raise ValueError(f"{path}: mixes advantage and strategy examples")
        self.kind = kind
        self.seen += len(recs)
        room = self.cap - len(self.weight)
        if len(recs) > room:
            # Full: every example ever seen stays with the same chance
            # (cap / seen). New ones pass that draw, then push out old ones
            # picked at random.
            stay = self.rng.random(len(recs)) < self.cap / self.seen
            stay[:room] |= True
            recs = recs[stay]
            out = max(0, len(recs) - room)
            if out:
                keep = np.ones(len(self.weight), bool)
                keep[self.rng.choice(len(self.weight), out, replace=False)] = False
                for name in self.FIELDS:
                    setattr(self, name, getattr(self, name)[keep])
        shift = len(self.rows)
        self.rows = np.concatenate([self.rows, rows])
        self.cards = np.concatenate([self.cards, recs["cards"]])
        self.mask = np.concatenate([self.mask, recs["mask"]])
        self.street = np.concatenate([self.street, recs["street"]])
        self.weight = np.concatenate([self.weight, recs["weight"] * float(it) ** power])
        self.pub = np.concatenate([self.pub, recs["pub"].astype(np.int64) + shift])
        self.hand = np.concatenate([self.hand, recs["hand"]])
        self.target = np.concatenate([self.target, recs["target"]])
        if len(self.rows) > 2 * len(self.weight) + 100_000:
            # Drop rows of betting inputs no example names any more.
            used, inverse = np.unique(self.pub, return_inverse=True)
            self.rows, self.pub = self.rows[used], inverse.astype(np.int64)

    def __len__(self):
        return len(self.weight)


class Net(nn.Module):
    def __init__(self, hidden=256, layers=3, residual=True):
        super().__init__()
        self.h, self.residual = hidden, residual
        self.emb = nn.Embedding(EMB_ROWS + 1, hidden, padding_idx=EMB_ROWS)
        nn.init.normal_(self.emb.weight, std=0.3)
        with torch.no_grad():
            self.emb.weight[EMB_ROWS].zero_()
        self.dense = nn.Linear(DENSE, hidden)
        self.hidden = nn.ModuleList(nn.Linear(hidden, hidden) for _ in range(layers))
        self.out = nn.Linear(hidden, MENU)

    def forward(self, idx, dense):
        x = torch.relu(self.emb(idx).sum(1) + self.dense(dense))
        for layer in self.hidden:
            y = torch.relu(layer(x))
            x = x + y if self.residual else y
        return self.out(x)


class Two(nn.Module):
    """A two-sided net. The hand side reads the hand on its board (cards and
    strength) and returns `d` numbers. The situation side reads the board and
    the betting and returns, per menu slot, `d` weights and an offset. A
    slot's output is the weighted sum plus the offset. In the engine the hand
    side runs once per board and the situation side once per decision, for
    all hands, so play costs far less than one net per hand."""

    def __init__(self, hidden=256, layers=3, d=128, spot_hidden=0, spot_layers=0):
        super().__init__()
        # The situation side runs once per decision in the engine, so it can
        # be much larger than the hand side at almost no cost in play.
        sh, sl = spot_hidden or hidden, spot_layers or layers
        self.h, self.d, self.sh, self.residual = hidden, d, sh, True
        self.hand_emb = nn.Embedding(EMB_ROWS + 1, hidden, padding_idx=EMB_ROWS)
        self.spot_emb = nn.Embedding(EMB_ROWS + 1, sh, padding_idx=EMB_ROWS)
        for emb in (self.hand_emb, self.spot_emb):
            nn.init.normal_(emb.weight, std=0.3)
            with torch.no_grad():
                emb.weight[EMB_ROWS].zero_()
        self.hand_dense, self.spot_dense = nn.Linear(HAND, hidden), nn.Linear(PUB, sh)
        self.hand_hidden = nn.ModuleList(nn.Linear(hidden, hidden) for _ in range(layers))
        self.spot_hidden = nn.ModuleList(nn.Linear(sh, sh) for _ in range(sl))
        self.hand_out, self.spot_out = nn.Linear(hidden, d), nn.Linear(sh, MENU * (d + 1))

    def forward(self, idx, dense):
        x = torch.relu(self.hand_emb(idx).sum(1) + self.hand_dense(dense[:, PUB:]))
        for layer in self.hand_hidden:
            x = x + torch.relu(layer(x))
        side = self.hand_out(x)
        board = idx.clone()
        board[:, :2] = EMB_ROWS  # the situation side does not see the hole cards
        y = torch.relu(self.spot_emb(board).sum(1) + self.spot_dense(dense[:, :PUB]))
        for layer in self.spot_hidden:
            y = y + torch.relu(layer(y))
        spot = self.spot_out(y).view(-1, MENU, self.d + 1)
        return (spot[:, :, :self.d] * side[:, None, :]).sum(2) / self.d ** 0.5 + spot[:, :, self.d]

    def sides(self):
        return ((self.hand_emb, self.hand_dense, self.hand_hidden, self.hand_out),
                (self.spot_emb, self.spot_dense, self.spot_hidden, self.spot_out))


TWO_HEAD = struct.Struct("<4s9I")   # version 1: both sides the same size
TWO_HEAD2 = struct.Struct("<4s11I")


# Card-table row of each of an example's 12 cards: hole cards share one
# table; each board has one for its flop, one for the turn, one for the river.
_OFFSET = np.array([0, 0] + [52 + b * 156 + s * 52 for b in range(2) for s in (0, 0, 0, 1, 2)], np.int64)
_PERMS = np.array([[a, b, c, 6 - a - b - c] for a in range(4) for b in range(4) for c in range(4)
                   if len({a, b, c}) == 3], np.int64)


def card_rows(cards, offset, perms=None):
    """(n, 12) cards as card-table rows, 255 as the empty row. With `perms`
    (n, 4), suits are renamed per example."""
    c = cards.long()
    absent = c == 255
    if perms is not None:
        c = (c & ~3) | torch.gather(perms, 1, (c & 3))
    return torch.where(absent, torch.full_like(c, EMB_ROWS), c + offset)


def save_net(net, path, kind):
    if isinstance(net, Two):
        with open(path, "wb") as f:
            f.write(TWO_HEAD2.pack(b"BPN2", 2, net.h, len(net.hand_hidden), net.sh, len(net.spot_hidden), net.d,
                                   PUB, HAND, EMB_ROWS, MENU, kind))
            for emb, dense, hidden, out in net.sides():
                parts = [emb.weight[:EMB_ROWS], dense.weight, dense.bias]
                for layer in hidden:
                    parts += [layer.weight, layer.bias]
                parts += [out.weight, out.bias]
                for p in parts:
                    f.write(p.detach().cpu().numpy().astype("<f4").tobytes())
        return
    layers = len(net.hidden)
    with open(path, "wb") as f:
        f.write(NET_HEAD.pack(b"BPN1", 1, net.h, layers, DENSE, EMB_ROWS, MENU, int(net.residual), kind))
        parts = [net.emb.weight[:EMB_ROWS], net.dense.weight, net.dense.bias]
        for layer in net.hidden:
            parts += [layer.weight, layer.bias]
        parts += [net.out.weight, net.out.bias]
        for p in parts:
            f.write(p.detach().cpu().numpy().astype("<f4").tobytes())


def load_net(path):
    with open(path, "rb") as f:
        if f.read(4) == b"BPN2":
            f.seek(0)
            if struct.unpack("<I", f.read(8)[4:])[0] == 1:
                f.seek(0)
                _, _, h, layers, d, n_pub, n_hand, emb_rows, menu, kind = TWO_HEAD.unpack(f.read(TWO_HEAD.size))
                sh, sl = h, layers
            else:
                f.seek(0)
                _, version, h, layers, sh, sl, d, n_pub, n_hand, emb_rows, menu, kind = TWO_HEAD2.unpack(f.read(TWO_HEAD2.size))
                if version != 2:
                    raise ValueError(f"{path}: not a net this trainer reads")
            if (n_pub, n_hand, emb_rows, menu) != (PUB, HAND, EMB_ROWS, MENU):
                raise ValueError(f"{path}: not a net this trainer reads")
            net = Two(h, layers, d, sh, sl)
            take = lambda *shape: torch.from_numpy(np.fromfile(f, "<f4", int(np.prod(shape))).reshape(shape).copy())
            with torch.no_grad():
                for emb, dense, hidden, out in net.sides():
                    w = dense.weight.shape[0]
                    emb.weight[:EMB_ROWS] = take(EMB_ROWS, w)
                    dense.weight.copy_(take(*dense.weight.shape))
                    dense.bias.copy_(take(w))
                    for layer in hidden:
                        layer.weight.copy_(take(w, w))
                        layer.bias.copy_(take(w))
                    out.weight.copy_(take(*out.weight.shape))
                    out.bias.copy_(take(out.bias.shape[0]))
            return net, kind
        f.seek(0)
        magic, version, h, layers, dense, emb, menu, residual, kind = NET_HEAD.unpack(f.read(NET_HEAD.size))
        if magic != b"BPN1" or (version, dense, emb, menu) != (1, DENSE, EMB_ROWS, MENU):
            raise ValueError(f"{path}: not a net this trainer reads")
        net = Net(h, layers, bool(residual))
        take = lambda *shape: torch.from_numpy(np.fromfile(f, "<f4", int(np.prod(shape))).reshape(shape).copy())
        with torch.no_grad():
            net.emb.weight[:EMB_ROWS] = take(EMB_ROWS, h)
            net.dense.weight.copy_(take(h, DENSE))
            net.dense.bias.copy_(take(h))
            for layer in net.hidden:
                layer.weight.copy_(take(h, h))
                layer.bias.copy_(take(h))
            net.out.weight.copy_(take(MENU, h))
            net.out.bias.copy_(take(MENU))
    return net, kind


def loss_of(kind, pred, target, legal, weight):
    if kind == KINDS["adv"]:
        per = ((pred - target) ** 2 * legal).sum(1)
    else:
        logp = torch.log_softmax(pred.masked_fill(~legal, -1e9), 1)
        per = -(target * logp.masked_fill(~legal, 0.0)).sum(1)
    return (per * weight).sum() / weight.sum()


def train(mem, out, hidden=256, layers=3, residual=True, steps=4000, batch=8192, lr=1e-3, init=None,
          device="cpu", seed=0, log=None, shuffle=True, width=0, spot=(0, 0), in_ram=False):
    """Fit a net to the memory and write it to `out`. Returns a summary.
    With `width` above 0 the net is two-sided (`Two`) with that many numbers
    between the sides, and `spot` (hidden, layers) sizes its situation side
    (0: as the hand side). `in_ram` keeps the examples in main memory and
    sends each batch to the device: a little slower per step, and the device
    then holds the net and one batch only (about 1 GB on a GPU, whatever the
    number of examples)."""
    torch.manual_seed(seed)
    dev = torch.device(device)
    store = torch.device("cpu") if in_ram else dev
    kind = mem.kind
    n = len(mem)
    t0 = time.time()
    rows = torch.from_numpy(mem.rows).to(dev)
    cards = torch.from_numpy(mem.cards).to(store)
    pub = torch.from_numpy(mem.pub.astype(np.int32)).to(store)
    hand = torch.from_numpy(mem.hand).to(store)
    target = torch.from_numpy(mem.target).to(store)
    weight = torch.from_numpy(mem.weight / mem.weight.mean()).to(store)
    legal_all = torch.from_numpy((mem.mask[:, None] >> np.arange(MENU, dtype=np.uint8)) & 1 > 0).to(store)
    street = torch.from_numpy(mem.street).to(store)
    offset = torch.from_numpy(_OFFSET).to(dev)
    perms = torch.from_numpy(_PERMS).to(dev)
    # One example in twenty is held back to read the fit.
    g = torch.Generator(device="cpu").manual_seed(seed)
    order = torch.randperm(n, generator=g).to(store)

    def take(idx):
        """One batch of examples on the device: cards, betting row, hand
        numbers, target, legal actions, weight, street."""
        return tuple(t[idx].to(dev, non_blocking=True)
                     for t in (cards, pub, hand, target, legal_all, weight, street))
    n_val = max(1, n // 20)
    val, fit = order[:n_val], order[n_val:]
    if init:
        net, _ = load_net(init)
        net = net.to(dev)
    else:
        net = (Two(hidden, layers, width, *spot) if width else Net(hidden, layers, residual)).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=steps, pct_start=0.05)

    def batch_loss(idx, shuffle_suits):
        c, pb, h, tg, lg, w, _ = take(idx)
        p = perms[torch.randint(0, 24, (len(idx),), device=dev)] if shuffle_suits else None
        x = torch.cat([rows[pb.long()], h], 1)
        pred = net(card_rows(c, offset, p), x)
        return loss_of(kind, pred, tg, lg, w)

    running = 0.0
    for step in range(steps):
        idx = fit[torch.randint(0, len(fit), (batch,), device=store)]
        loss = batch_loss(idx, shuffle)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step()
        sched.step()
        running = loss.item() if step == 0 else 0.98 * running + 0.02 * loss.item()
        if log and (step + 1) % max(1, steps // 5) == 0:
            log(f"  step {step + 1}/{steps} loss {running:.5f}")
    net.eval()
    with torch.no_grad():
        val_loss = sum(batch_loss(val[i:i + 65536], False).item() * len(val[i:i + 65536])
                       for i in range(0, n_val, 65536)) / n_val
        # Advantage nets: the share of the held-back targets' spread the net
        # explains, per street (1 is a perfect fit, 0 is no better than zero).
        fit_by_street = None
        if kind == KINDS["adv"]:
            err, tot = torch.zeros(3, device=dev), torch.zeros(3, device=dev)
            for i in range(0, n_val, 65536):
                c, pb, h, tg, lg, w, st = take(val[i:i + 65536])
                x = torch.cat([rows[pb.long()], h], 1)
                pred = net(card_rows(c, offset), x)
                st = st.long()
                err.index_add_(0, st, w * ((pred - tg) ** 2 * lg).sum(1))
                tot.index_add_(0, st, w * (tg ** 2 * lg).sum(1))
            fit_by_street = [round(float(1 - e / t), 4) if t > 0 else None for e, t in zip(err, tot)]
    save_net(net, out, kind)
    # Hand the GPU memory back between trainings: PyTorch would otherwise
    # keep every earlier, smaller copy of the examples cached.
    del rows, cards, pub, hand, target, weight, legal_all, street, order, val, fit, net, opt, sched
    if dev.type == "cuda":
        torch.cuda.empty_cache()
    return {"kind": kind, "examples": n, "steps": steps, "train_loss": running, "val_loss": val_loss,
            "fit_by_street": fit_by_street, "train_s": time.time() - t0}


def check(net_path, examples, exe, rows=64):
    """Compare this file's outputs with the engine's on the first examples."""
    net, _ = load_net(net_path)
    _, _, table, recs = read_examples(examples)
    recs = recs[:rows]
    x = torch.from_numpy(np.concatenate([table[recs["pub"]], recs["hand"]], 1))
    with torch.no_grad():
        mine = net(card_rows(torch.from_numpy(recs["cards"].copy()), torch.from_numpy(_OFFSET)), x).numpy()
    text = subprocess.run([exe, "netcheck", examples, "--net", net_path, "--rows", str(rows)],
                          check=True, capture_output=True, text=True).stdout
    theirs = np.array(json.loads(text), np.float32)
    worst = float(np.abs(mine - theirs).max())
    scale = float(np.abs(mine).max())
    if worst > 1e-3 * max(1.0, scale):
        raise SystemExit(f"engine and trainer disagree: largest difference {worst:.5f} (outputs up to {scale:.3f})")
    return worst


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="glob of example files")
    ap.add_argument("--out", required=True)
    ap.add_argument("--hidden", type=int, default=256)
    ap.add_argument("--layers", type=int, default=3)
    ap.add_argument("--plain", action="store_true", help="no skip connections")
    ap.add_argument("--width", type=int, default=0, help="above 0: a two-sided net with this many numbers between the sides")
    ap.add_argument("--spot-hidden", type=int, default=0, help="two-sided nets: size of the situation side (0: as --hidden)")
    ap.add_argument("--spot-layers", type=int, default=0)
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--batch", type=int, default=8192)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--init")
    ap.add_argument("--cap", type=int, default=40_000_000, help="most examples held")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fixed-suits", action="store_true", help="do not rename suits at random (for one fixed flop)")
    ap.add_argument("--in-ram", action="store_true",
                    help="keep the examples in main memory, not on the GPU (the GPU then holds about 1 GB)")
    ap.add_argument("--power", type=float, default=1.0, help="an example of round t counts t^power times")
    ap.add_argument("--check", help="path to the bombpot tool, to compare outputs")
    a = ap.parse_args()
    files = sorted(glob.glob(a.data))
    if not files:
        sys.exit(f"no files match {a.data}")
    mem = Memory(a.cap, a.seed)
    for f in files:
        mem.add(f, a.power)
    res = train(mem, a.out, a.hidden, a.layers, not a.plain, a.steps, a.batch, a.lr, a.init, a.device, a.seed,
                log=lambda s: print(s, file=sys.stderr), shuffle=not a.fixed_suits, width=a.width,
                spot=(a.spot_hidden, a.spot_layers), in_ram=a.in_ram)
    if a.check:
        res["engine_difference"] = check(a.out, files[0], a.check)
    print(json.dumps(res))


if __name__ == "__main__":
    main()
