#!/usr/bin/env python3
"""Convert a go/no-go net (datagen_gonogo/net.npz) to the leaf_net.bin format
that solve-cli and the Preflop Lab load.

    python tools/datagen/export_net.py                       # datagen_gonogo/net.npz -> datagen_gonogo/leaf_net.bin
    python tools/datagen/export_net.py NET.npz OUT.bin

gonogo.py now writes leaf_net.bin itself; this is for nets trained before it did.
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import leafnet_io  # noqa: E402


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "datagen_gonogo", "net.npz")
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(src), "leaf_net.bin")
    z = np.load(src)
    arrays = [z[f"arr_{i}"] for i in range(len([k for k in z.files if k.startswith("arr_")]))]
    layers = len(arrays) // 2
    weights, biases = arrays[:layers], arrays[layers:]
    extra = {}
    report = os.path.join(os.path.dirname(src), "report.json")
    if os.path.exists(report):
        with open(report, encoding="utf-8") as f:
            r = json.load(f)
        extra = {"dataset_examples": r["examples"], "trained": r["when"],
                 "held_out": {"class_error": r["class_error"], "range_error": r["range_error"]}}
    leafnet_io.write(dst, weights, biases, z["mu"], z["sd"], extra=extra)
    print(f"wrote {dst} ({os.path.getsize(dst) / 1e6:.1f} MB, layers {[w.shape for w in weights]})")


if __name__ == "__main__":
    main()
