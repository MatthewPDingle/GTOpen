"""Read and write GTOpen leaf-value net files (the format solve-cli loads).

Layout, little endian:
    b"GTOLEAF1"
    u32 header length, then a UTF-8 JSON header
    f32 input mean [inputs], f32 input scale [inputs]
    for each layer: f32 weights [rows x cols] (row-major, input-major as in
    numpy x @ W), f32 bias [cols]

The header records the layer sizes and the feature layout. Inputs are
features() below; the output is the solved value minus the balanced model's
value, out of position 169 classes then in position 169 classes, as a
fraction of the pot.

An ensemble file holds several nets: its header has "ensemble", the list of
every member's layer sizes ("sizes" repeats the first member's), and each
member's mean, scale and layers follow back to back. Its output is the mean
of the members' outputs (write_ensemble, read_members, forward_members).

A header can carry "total_rule": a fitted rule for what the two players'
values add up to at a raked leaf whose rake is below its cap (the solver's
PREFLOP_LEAF_PIN=rule uses it; crates/solver/src/preflop/leaf_total.rs reads
the same layout and must give the same numbers as leaf_total() here):

    {"form": "linear" or "share",
     "coef": {"limped": [c0, c1, c2, c3], "srp": [...], "3bet": [...], "4bet": [...]},
     "valid": {"rake_frac": [lo, hi], "cap_over_pot": [lo, hi], "pot_bb": [lo, hi], "stack_over_pot": [lo, hi]}}

With k = rake cap / pot, the pot and the effective stack behind in bb and the
rake as a fraction, the total as a fraction of the pot is
    linear: c0 + c1 k + c2 ln(pot) + c3 ln(stack / pot)
    share:  1 - rake - (k - rake) clip(c0 + c1 ln(k / rake) + c2 ln(stack / pot) + c3 ln(pot), 0, 1)
held to its bounds. "valid" is the range of each input in the rows the rule
was fitted on; outside it the rule is not used.
"""

import json
import struct

import numpy as np

MAGIC = b"GTOLEAF1"
POT_TYPES = ["limped", "srp", "3bet", "4bet"]
FEATURES = ("range oop 169 (largest weight 1), range ip 169, balanced value oop 169, balanced value ip 169, "
            "ln pot_bb, ln stack_bb, ln(stack/pot), 10 x rake fraction, rake cap bb / pot, raked (0/1), "
            "pot type one-hot (limped, srp, 3bet, 4bet)")


def meta_features(pot_bb, stack_bb, rake_frac, rake_cap_bb, pot_type):
    return [float(np.log(pot_bb)), float(np.log(stack_bb)), float(np.log(stack_bb / pot_bb)), 10 * rake_frac,
            rake_cap_bb / pot_bb, 1.0 if rake_frac > 0 else 0.0] + [1.0 if pot_type == t else 0.0 for t in POT_TYPES]


TOTAL_RULE_FORMS = ("linear", "share")
TOTAL_RULE_VALID = ("rake_frac", "cap_over_pot", "pot_bb", "stack_over_pot")


def check_total_rule(rule):
    """Raise ValueError unless `rule` is a total rule the solver can read (see the module text)."""
    def numbers(v, n, what):
        ok = (isinstance(v, (list, tuple)) and len(v) == n
              and all(isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x) for x in v))
        if not ok:
            raise ValueError(f"total_rule {what} must be {n} numbers")
    if not isinstance(rule, dict) or rule.get("form") not in TOTAL_RULE_FORMS:
        raise ValueError(f"total_rule form must be one of {TOTAL_RULE_FORMS}")
    for t in POT_TYPES:
        numbers((rule.get("coef") or {}).get(t), 4, f"coef.{t}")
    for key in TOTAL_RULE_VALID:
        v = (rule.get("valid") or {}).get(key)
        numbers(v, 2, f"valid.{key}")
        if v[0] > v[1]:
            raise ValueError(f"total_rule valid.{key} must be [lowest, highest]")


def leaf_total(rule, pot_bb, stack_bb, rake_frac, rake_cap_bb, pot_type):
    """What a heads-up flop leaf's two values add up to, as a fraction of the pot: ("exact", total)
    with no rake or when the rake on the pot as it stands is at its cap; ("rule", total) below the cap
    where `rule` (a header's "total_rule", or None) covers the leaf; (None, None) otherwise.
    `pot_type` is a POT_TYPES name or index; rake_cap_bb = 0 means no cap."""
    if not rake_frac > 0:
        return "exact", 1.0
    if not (rake_cap_bb > 0 and pot_bb > 0):
        return None, None
    k = rake_cap_bb / pot_bb
    if rake_frac >= k:
        return "exact", 1.0 - k
    if rule is None:
        return None, None
    spr = stack_bb / pot_bb
    for key, v in zip(TOTAL_RULE_VALID, (rake_frac, k, pot_bb, spr)):
        lo, hi = rule["valid"][key]
        if v < lo - 1e-9 or v > hi + 1e-9:
            return None, None
    c = rule["coef"][pot_type if isinstance(pot_type, str) else POT_TYPES[min(int(pot_type), 3)]]
    if rule["form"] == "linear":
        t = c[0] + c[1] * k + c[2] * np.log(pot_bb) + c[3] * np.log(spr)
    else:
        share = c[0] + c[1] * np.log(k / rake_frac) + c[2] * np.log(spr) + c[3] * np.log(pot_bb)
        t = 1.0 - rake_frac - (k - rake_frac) * min(max(share, 0.0), 1.0)
    if not np.isfinite(t):
        return None, None
    most = min(k, rake_frac * (1.0 + 2.0 * spr))
    return "rule", float(min(max(t, 1.0 - most), 1.0 - rake_frac))


def class_parts(idx):
    """(high rank, low rank, suited) of a class index, ranks 0 (deuce) to 12 (ace): the solver's order."""
    r, c = divmod(idx, 13)
    return (r, c, False) if r == c else (r, c, True) if r > c else (c, r, False)


_DISJOINT = None


def disjoint_share():
    """169 x 169: for every pair of classes, the share of their combo pairs that share no card."""
    global _DISJOINT
    if _DISJOINT is None:
        combos = []
        for idx in range(169):
            hi, lo, suited = class_parts(idx)
            keep = (lambda a, b: a < b) if hi == lo else (lambda a, b: a == b) if suited else (lambda a, b: a != b)
            combos.append([(1 << (hi * 4 + a)) | (1 << (lo * 4 + b)) for a in range(4) for b in range(4) if keep(a, b)])
        t = np.zeros((169, 169))
        for h in range(169):
            for g in range(h, 169):
                free = sum(1 for a in combos[h] for b in combos[g] if a & b == 0)
                t[h, g] = t[g, h] = free / (len(combos[h]) * len(combos[g]))
        _DISJOINT = t
    return _DISJOINT


def dealt_weights(oop, ip):
    """The weights under which a leaf's values add up to the pot minus the rake taken: each class by its
    share of its range (`oop`, `ip`: per-class masses on any scale, shape [..., 169]) times the share of the
    other range it does not block. Returns (w_oop, w_ip, together): each side's weights add up to 1, and
    `together` is how often the two ranges are dealt together relative to ranges from separate decks."""
    oop, ip = np.asarray(oop, np.float64), np.asarray(ip, np.float64)
    oop, ip = oop / oop.sum(-1, keepdims=True), ip / ip.sum(-1, keepdims=True)
    t = disjoint_share()
    w_oop, w_ip = oop * (ip @ t), ip * (oop @ t)
    mean = w_oop.sum(-1, keepdims=True)
    return w_oop / mean, w_ip / mean, mean[..., 0] * 1326.0 / 1225.0


def layer_sizes(weights):
    return [int(weights[0].shape[0])] + [int(W.shape[1]) for W in weights]


def _write(path, header, members):
    blob = json.dumps(header).encode()
    with open(path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<I", len(blob)))
        f.write(blob)
        for weights, biases, mu, sd in members:
            for a in [mu, sd] + [x for pair in zip(weights, biases) for x in pair]:
                f.write(np.ascontiguousarray(a, dtype="<f4").tobytes())


def write(path, weights, biases, mu, sd, extra=None):
    header = {"format": "gtopen-leaf-net", "version": 1, "sizes": layer_sizes(weights), "activation": "relu",
              "features": FEATURES, "output": "solved minus balanced value, oop 169 then ip 169, fraction of pot"}
    header.update(extra or {})
    if header.get("total_rule") is not None:
        check_total_rule(header["total_rule"])
    _write(path, header, [(weights, biases, mu, sd)])


def write_ensemble(path, members, extra=None):
    """Several nets in one file: `members` is a list of (weights, biases, mu, sd). The loader's output
    is the mean of the members' outputs."""
    if len(members) < 2:
        raise ValueError("an ensemble needs at least two members")
    sizes = [layer_sizes(m[0]) for m in members]
    header = {"format": "gtopen-leaf-net", "version": 2, "sizes": sizes[0], "ensemble": sizes, "activation": "relu",
              "features": FEATURES,
              "output": "mean over the members of solved minus balanced value, oop 169 then ip 169, fraction of pot"}
    header.update(extra or {})
    if header.get("total_rule") is not None:
        check_total_rule(header["total_rule"])
    _write(path, header, members)


def read_members(path):
    """(header, [(weights, biases, mu, sd), ...]): one member for a plain net, several for an ensemble."""
    with open(path, "rb") as f:
        if f.read(8) != MAGIC:
            raise ValueError(f"{path} is not a GTOpen leaf net")
        (n,) = struct.unpack("<I", f.read(4))
        header = json.loads(f.read(n))
        data = np.frombuffer(f.read(), dtype="<f4")
    pos = 0

    def take(count, shape=None):
        nonlocal pos
        a = data[pos:pos + count]
        if len(a) != count:
            raise ValueError(f"{path}: the data is truncated")
        pos += count
        return a.reshape(shape) if shape else a

    members = []
    for sizes in header.get("ensemble") or [header["sizes"]]:
        mu, sd = take(sizes[0]), take(sizes[0])
        weights, biases = [], []
        for a, b in zip(sizes, sizes[1:]):
            weights.append(take(a * b, (a, b)))
            biases.append(take(b))
        members.append((weights, biases, mu, sd))
    if pos != len(data):
        raise ValueError(f"{path}: {len(data) - pos} unexpected trailing values")
    return header, members


def read(path):
    """(header, weights, biases, mu, sd) of a plain net (an ensemble has several: read_members)."""
    header, members = read_members(path)
    if len(members) != 1:
        raise ValueError(f"{path} is an ensemble of {len(members)} nets: use read_members")
    return (header,) + members[0]


def forward(weights, biases, mu, sd, x):
    x = (np.asarray(x, np.float32) - mu) / sd
    for i, (W, b) in enumerate(zip(weights, biases)):
        x = x @ W + b
        if i < len(weights) - 1:
            x = np.maximum(x, 0)
    return x


def forward_members(members, x, batch=4096):
    """The net's output for raw inputs x: the mean over `members` (from read_members)."""
    x = np.asarray(x, np.float32)
    out = []
    for i in range(0, len(x), batch):
        out.append(np.mean([forward(*m, x[i:i + batch]) for m in members], axis=0))
    return np.concatenate(out) if out else np.zeros((0, len(members[0][1][-1])), np.float32)
