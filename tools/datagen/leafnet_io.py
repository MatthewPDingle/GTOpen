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


def write(path, weights, biases, mu, sd, extra=None):
    sizes = [int(weights[0].shape[0])] + [int(W.shape[1]) for W in weights]
    header = {"format": "gtopen-leaf-net", "version": 1, "sizes": sizes, "activation": "relu",
              "features": FEATURES, "output": "solved minus balanced value, oop 169 then ip 169, fraction of pot"}
    header.update(extra or {})
    blob = json.dumps(header).encode()
    with open(path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<I", len(blob)))
        f.write(blob)
        for a in [mu, sd] + [x for pair in zip(weights, biases) for x in pair]:
            f.write(np.ascontiguousarray(a, dtype="<f4").tobytes())


def read(path):
    with open(path, "rb") as f:
        if f.read(8) != MAGIC:
            raise ValueError(f"{path} is not a GTOpen leaf net")
        (n,) = struct.unpack("<I", f.read(4))
        header = json.loads(f.read(n))
        data = np.frombuffer(f.read(), dtype="<f4")
    sizes = header["sizes"]
    pos = 0

    def take(count, shape=None):
        nonlocal pos
        a = data[pos:pos + count]
        pos += count
        return a.reshape(shape) if shape else a

    mu, sd = take(sizes[0]), take(sizes[0])
    weights, biases = [], []
    for a, b in zip(sizes, sizes[1:]):
        weights.append(take(a * b, (a, b)))
        biases.append(take(b))
    if pos != len(data):
        raise ValueError(f"{path}: {len(data) - pos} unexpected trailing values")
    return header, weights, biases, mu, sd


def forward(weights, biases, mu, sd, x):
    x = (np.asarray(x, np.float32) - mu) / sd
    for i, (W, b) in enumerate(zip(weights, biases)):
        x = x @ W + b
        if i < len(weights) - 1:
            x = np.maximum(x, 0)
    return x
