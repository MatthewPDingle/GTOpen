"""Corrections files for the solver's PREFLOP_LEAF_FIX research setting.

The solver adds the file's numbers to the leaf net's output at heads-up flop leaves
(crates/solver/src/preflop/leaf_fix.rs has the layout and the rules). This writes and checks such files.

    python tools/leafnet/leaf_fix.py known --pairs -0.0045 --totals srp=-0.0040,3bet=-0.0045,4bet=-0.0052 --out fix.json
    python tools/leafnet/leaf_fix.py field --table diff.json --per-hand 0.01 --out fix.json
    python tools/leafnet/leaf_fix.py check fix.json

`known` writes changes of a known size: `--pairs` adds a number to every pair from 22 to 99 for both players at
every leaf, and `--totals` moves a pot type's total (both players together) by a number, half on each player's
every class. `field` scales a table of per-line values (for example the difference between two nets at one
solve's ranges) to a given mean size per hand. All numbers are fractions of the pot: 0.01 is 1% of the pot.

No GPU or torch.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "datagen"))

import numpy as np  # noqa: E402

import leafnet_io  # noqa: E402

FORMAT, VERSION = "gtopen-leaf-fix", 1
NC = 169
POT_TYPES = ("limped", "srp", "3bet", "4bet")
MAX_FIX = 0.5  # the solver refuses more: the numbers are fractions of the pot
SMALL_PAIRS = tuple(r * 14 for r in range(8))  # 22 to 99 in the solver's class order (rank 0 is the deuce)


def side(value):
    """One side of an entry: a number for every class, or 169 numbers."""
    a = np.asarray(value, np.float64)
    if a.shape == ():
        return float(a)
    if a.shape != (NC,):
        raise ValueError(f"a side is one number or {NC} numbers, not shape {a.shape}")
    return [float(x) for x in a]


def entry(oop=None, ip=None, line=None, pot_type=None):
    """One entry: for the leaf `line` ends at, for every leaf of `pot_type`, or (neither) for every leaf."""
    e = {}
    if line is not None:
        e["line"] = line
    if pot_type is not None:
        e["pot_type"] = pot_type
    if oop is not None:
        e["oop"] = side(oop)
    if ip is not None:
        e["ip"] = side(ip)
    return e


def document(entries, note=""):
    doc = {"format": FORMAT, "version": VERSION, "note": note, "entries": list(entries)}
    check(doc)
    return doc


def check(doc):
    """Raise ValueError for a file the solver would refuse. Returns (entries for every leaf, pot types, lines)."""
    if not isinstance(doc, dict) or doc.get("format") != FORMAT or doc.get("version") != VERSION:
        raise ValueError(f'must say "format": "{FORMAT}", "version": {VERSION}')
    extra = set(doc) - {"format", "version", "note", "entries"}
    if extra:
        raise ValueError(f"unknown key {sorted(extra)[0]!r}")
    if not isinstance(doc.get("entries"), list):
        raise ValueError('"entries" must be a list')
    seen_all, seen_types, seen_lines = 0, set(), set()
    for i, e in enumerate(doc["entries"], 1):
        if not isinstance(e, dict):
            raise ValueError(f"entry {i}: must be an object")
        extra = set(e) - {"line", "pot_type", "oop", "ip"}
        if extra:
            raise ValueError(f"entry {i}: unknown key {sorted(extra)[0]!r}")
        for key in ("oop", "ip"):
            if key not in e:
                continue
            v = e[key]
            numbers = [v] if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            if not isinstance(numbers, list) or (numbers is v and len(v) != NC) or any(
                    isinstance(x, bool) or not isinstance(x, (int, float)) for x in numbers):
                raise ValueError(f'entry {i}: "{key}" must be one number or {NC} numbers')
            bad = [x for x in numbers if not np.isfinite(x) or abs(x) > MAX_FIX]
            if bad:
                raise ValueError(f"entry {i}: {bad[0]} is not a correction: the numbers are fractions of the pot "
                                 f"(0.01 is 1% of the pot), at most {MAX_FIX} either way")
        line, pot_type = e.get("line"), e.get("pot_type")
        if line is not None and pot_type is not None:
            raise ValueError(f'entry {i}: give "line" or "pot_type", not both')
        if line is not None:
            if not isinstance(line, str) or not line.strip():
                raise ValueError(f"entry {i}: an empty line")
            if line in seen_lines:
                raise ValueError(f"entry {i}: a second entry for line {line!r}")
            seen_lines.add(line)
        elif pot_type is not None:
            if pot_type not in POT_TYPES:
                raise ValueError(f'entry {i}: "pot_type" must be one of {", ".join(POT_TYPES)}, not {pot_type!r}')
            if pot_type in seen_types:
                raise ValueError(f"entry {i}: a second entry for pot type {pot_type}")
            seen_types.add(pot_type)
        else:
            if seen_all:
                raise ValueError(f"entry {i}: a second entry for every leaf")
            seen_all = 1
    return seen_all, sorted(seen_types, key=POT_TYPES.index), sorted(seen_lines)


def write(path, entries, note=""):
    doc = document(entries, note)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f)
        f.write("\n")
    return doc


def known(pairs=0.0, totals=None):
    """Entries for changes of a known size. `pairs`: added to every pair from 22 to 99, both players, at every
    leaf. `totals`: {pot type: change of the two players' total}; each player's every class takes half of it,
    which moves the leaf's dealt sum by exactly that much and leaves the split between the players alone."""
    entries = []
    if pairs:
        v = np.zeros(NC)
        v[list(SMALL_PAIRS)] = pairs
        entries.append(entry(oop=v, ip=v))
    for pot_type, change in (totals or {}).items():
        if change:
            entries.append(entry(oop=change / 2.0, ip=change / 2.0, pot_type=pot_type))
    return entries


def mean_per_hand(rows):
    """Mean absolute value per hand of a table of per-line values: a line counts by its `weight` (how often
    it comes up) and a class by its share of its player's range among hands that can be dealt against the
    other range (leafnet_io.dealt_weights), the two players counting the same."""
    num = den = 0.0
    for r in rows:
        w_oop, w_ip, _ = leafnet_io.dealt_weights(r["oop_range"], r["ip_range"])
        here = 0.5 * (float(w_oop @ np.abs(np.asarray(r["oop"], np.float64))) + float(w_ip @ np.abs(np.asarray(r["ip"], np.float64))))
        num += r["weight"] * here
        den += r["weight"]
    if not den > 0.0:
        raise ValueError("the table's weights add up to nothing")
    return num / den


def field(rows, per_hand):
    """Entries, one per line, holding the table's values scaled so that their mean absolute size per hand
    (`mean_per_hand`) is `per_hand`. `rows`: [{"line", "weight", "oop": 169, "ip": 169, "oop_range": 169,
    "ip_range": 169}]. Returns (entries, the factor the values were multiplied by)."""
    for r in rows:
        for key in ("oop", "ip", "oop_range", "ip_range"):
            if np.asarray(r[key]).shape != (NC,):
                raise ValueError(f'line {r.get("line")!r}: "{key}" must be {NC} numbers')
    now = mean_per_hand(rows)
    if not now > 0.0:
        raise ValueError("the table's values are all zero")
    factor = per_hand / now
    return [entry(oop=factor * np.asarray(r["oop"], np.float64), ip=factor * np.asarray(r["ip"], np.float64), line=r["line"])
            for r in rows], factor


def parse_totals(text):
    out = {}
    for part in filter(None, (p.strip() for p in (text or "").split(","))):
        name, _, value = part.partition("=")
        if name not in POT_TYPES or not value:
            raise ValueError(f"--totals takes pot_type=change pairs with pot types {', '.join(POT_TYPES)}, not {part!r}")
        out[name] = float(value)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("known", help="changes of a known size")
    k.add_argument("--pairs", type=float, default=0.0, help="added to every pair from 22 to 99, both players, every leaf")
    k.add_argument("--totals", default="", help="pot_type=change of the total, comma separated (srp=-0.004,4bet=-0.005)")
    k.add_argument("--note", default="")
    k.add_argument("--out", required=True)
    f = sub.add_parser("field", help="a table of per-line values scaled to a mean size per hand")
    f.add_argument("--table", required=True, help='JSON: {"lines": [{"line", "weight", "oop", "ip", "oop_range", "ip_range"}]}')
    f.add_argument("--per-hand", type=float, required=True, help="mean absolute value per hand after scaling (0.01 is 1% of the pot)")
    f.add_argument("--note", default="")
    f.add_argument("--out", required=True)
    c = sub.add_parser("check", help="check a file as the solver would")
    c.add_argument("file")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "known":
            entries = known(args.pairs, parse_totals(args.totals))
            if not entries:
                raise ValueError("nothing to write: give --pairs or --totals")
            write(args.out, entries, args.note or f"known changes: pairs {args.pairs}, totals {args.totals or 'none'}")
            print(f"{args.out}: {len(entries)} entries")
        elif args.cmd == "field":
            with open(args.table, encoding="utf-8") as fh:
                rows = json.load(fh)["lines"]
            before = mean_per_hand(rows)
            entries, factor = field(rows, args.per_hand)
            write(args.out, entries, args.note or f"{os.path.basename(args.table)} times {factor:.4g}: {args.per_hand} per hand")
            print(f"{args.out}: {len(entries)} lines, mean per hand {before:.5f} -> {args.per_hand:.5f} (times {factor:.4g})")
        else:
            with open(args.file, encoding="utf-8") as fh:
                every, types, lines = check(json.load(fh))
            print(f"{args.file}: ok ({'every leaf; ' if every else ''}pot types {', '.join(types) or 'none'}; {len(lines)} lines)")
    except (ValueError, KeyError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
