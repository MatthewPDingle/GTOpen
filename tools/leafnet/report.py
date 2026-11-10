#!/usr/bin/env python3
"""Leaf-net dashboard: the loop's progress and the training data, as one
self-contained HTML page (inline SVG, no libraries).

    python tools/leafnet/report.py [--out WORK/dashboard.html]

Reads WORK/results.tsv, the snapshots' manifests and arrays, each snapshot's
runs/<snapshot>/state.json, and the dataset's progress.json from Hugging Face
(skipped when offline). Read-only: changes nothing the harness uses.

Run tables and hover text show how many training examples each run used (the
train split of its snapshot). Two optional files in WORK add context:
loop_summary.txt (first line a heading, then one paragraph per line; shown
under the tiles) and dashboard_labels.json (see load_labels: which loop or
session logged which runs; adds a Source column).
"""

import argparse
import csv
import datetime
import html
import json
import math
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "datagen"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from prepare import POT_TYPES, work_dir  # noqa: E402
from validate import load_config  # noqa: E402

E = html.escape


# ------------------------------------------------------------------ data ----

def read_results(work):
    path = os.path.join(work, "results.tsv")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def add_train_examples(work, runs, labels):
    """Sets r['train_n'] on every run: the train split size of the run's snapshot
    (scaled for the learning-curve runs, which say 'on F of the training examples'),
    and r['source'] (see load_labels)."""
    sizes = {}
    for r in runs:
        snap = r.get("snapshot") or ""
        if snap not in sizes:
            try:
                with open(os.path.join(work, "snapshots", snap, "manifest.json"), encoding="utf-8") as f:
                    sizes[snap] = int(json.load(f)["examples_by_split"]["train"])
            except (OSError, KeyError, ValueError):
                sizes[snap] = None
        n = sizes[snap]
        m = re.search(r"on ([0-9.]+) of the training examples", r.get("desc") or "")
        if n is not None and m:
            n = int(round(n * float(m.group(1))))
        r["train_n"] = n
        r["source"] = source_of(r, labels) if labels else ""
    return runs


def load_labels(work):
    """Optional WORK/dashboard_labels.json, to say which loop or session logged a run:
    {"prefix_labels": {"<description prefix>": "<source>"}, "loop_starts": [["<ISO time>", "<name>"], ...]}.
    Without the file the tables have no Source column."""
    path = os.path.join(work, "dashboard_labels.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def source_of(r, labels):
    desc = r.get("desc") or ""
    for prefix, name in (labels.get("prefix_labels") or {}).items():
        if desc.startswith(prefix):
            return name
    if desc.startswith("noise seed"):
        return "baseline"
    name = "loop 1"
    for start, loop in sorted(labels.get("loop_starts") or []):
        if (r.get("time") or "") >= start:
            name = loop
    return name


def fmt_n(n):
    return f"{n:,}" if n is not None else "–"


def github_repo():
    """owner/name of this checkout's origin remote on GitHub, or None."""
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True,
                             cwd=ROOT).stdout.strip()
    except OSError:
        return None
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    return m.group(1) if m else None


def progress_events(repo):
    """Per-merge events: the datagen-progress branch's copy first, the dataset's own second."""
    gh = github_repo()
    urls = [f"https://raw.githubusercontent.com/{gh}/datagen-progress/progress.json"] if gh else []
    for url in urls + [f"https://huggingface.co/datasets/{repo}/resolve/main/progress.json"]:
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return json.load(r)
        except Exception:
            continue
    return None


def snapshot_stats(work, name):
    d = os.path.join(work, "snapshots", name)
    with open(os.path.join(d, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    x = np.load(os.path.join(d, "x.npy"), mmap_mode="r")
    meta = np.asarray(x[:, -10:], dtype=np.float64)
    pt = np.load(os.path.join(d, "pot_type.npy"))
    gen = np.load(os.path.join(d, "generator.npy"))
    scale = np.load(os.path.join(d, "pot_scale.npy"))
    return {
        "manifest": m, "pot": np.exp(meta[:, 0]), "stack": np.exp(meta[:, 1]), "spr": np.exp(meta[:, 2]),
        "rake": meta[:, 3] / 10, "cap_bb": meta[:, 4] * np.exp(meta[:, 0]), "pot_type": pt, "generator": gen,
        "scaled": scale > 1.0001,
    }


# ------------------------------------------------------------------- svg ----

W, H, PADL, PADR, PADT, PADB = 720, 240, 64, 18, 14, 34
HW = 460  # drawing width of the half-width charts (keeps their text the same size as the full-width chart's)


def nice_ticks(lo, hi, n=5):
    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw), default=raw)
    start = math.ceil(lo / step) * step
    ticks, v = [], start
    while v <= hi + 1e-12:
        ticks.append(round(v, 10))
        v += step
    return ticks


def axes(xs_lo, xs_hi, ys_lo, ys_hi, yfmt, xlabels=None, ylabel="", w=None):
    w = w or W
    sx = lambda v: PADL + (v - xs_lo) / max(xs_hi - xs_lo, 1e-12) * (w - PADL - PADR)
    sy = lambda v: PADT + (1 - (v - ys_lo) / max(ys_hi - ys_lo, 1e-12)) * (H - PADT - PADB)
    out = []
    for t in nice_ticks(ys_lo, ys_hi):
        y = sy(t)
        out.append(f'<line x1="{PADL}" x2="{w - PADR}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
                   f'<text x="{PADL - 8}" y="{y + 4:.1f}" class="tick" text-anchor="end">{yfmt(t)}</text>')
    out.append(f'<line x1="{PADL}" x2="{w - PADR}" y1="{H - PADB}" y2="{H - PADB}" class="base"/>')
    for v, lab in (xlabels or []):
        out.append(f'<text x="{sx(v):.1f}" y="{H - PADB + 18}" class="tick" text-anchor="middle">{E(lab)}</text>')
    if ylabel:
        out.append(f'<text x="14" y="{PADT + (H - PADT - PADB) / 2:.0f}" class="tick" text-anchor="middle" '
                   f'transform="rotate(-90 14 {PADT + (H - PADT - PADB) / 2:.0f})">{E(ylabel)}</text>')
    return sx, sy, "".join(out)


def svg(body, label, w=None):
    return (f'<svg viewBox="0 0 {w or W} {H}" role="img" aria-label="{E(label)}" preserveAspectRatio="xMidYMid meet">'
            f'{body}</svg>')


def ref_line(sx, sy, x0, x1, y, cls, text):
    return (f'<line x1="{sx(x0):.1f}" x2="{sx(x1):.1f}" y1="{sy(y):.1f}" y2="{sy(y):.1f}" class="{cls}"/>'
            f'<text x="{sx(x1) - 4:.1f}" y="{sy(y) - 6:.1f}" class="reflabel" text-anchor="end">{E(text)}</text>')


def chart_progress(runs, ref_v1, ref_bal):
    """Every run's validation class error in order; the best-so-far as a step line."""
    pts = [(i, fnum(r["val_class"]), r) for i, r in enumerate(runs) if fnum(r.get("val_class")) is not None]
    if not pts:
        return "<p class='empty'>No runs yet.</p>"
    ys = [p[1] for p in pts]
    lo = min(ys + ([ref_v1] if ref_v1 else []))
    hi = min(max(ys), lo + 0.006)
    lo, hi = lo - 0.0003, hi + 0.0003
    n = len(pts)
    step = max(1, n // 6)
    sx, sy, ax = axes(0, max(n - 1, 1), lo, hi, lambda t: f"{t:.4f}",
                      [(i, f"#{i + 1}") for i in range(0, n, step)], "val class error")
    body = [ax]
    if ref_v1:
        body.append(ref_line(sx, sy, 0, max(n - 1, 1), ref_v1, "ref", f"v1 setup {ref_v1:.4f}"))
    best, line = None, []
    for i, y, r in pts:
        if r["verdict"] == "keep":
            best = y if best is None else min(best, y)
        if best is not None:
            line.append((i, best))
    if line:
        d = "M" + " L".join(f"{sx(a):.1f},{sy(b):.1f} {sx(a + 1 if k + 1 < len(line) else a):.1f},{sy(b):.1f}"
                             for k, (a, b) in enumerate(line))
        body.append(f'<path d="{d}" class="bestline"/>')
    for i, y, r in pts:
        yc = min(y, hi)
        tip = (f"#{i + 1} {r['time']}" + (f" ({r['source']})" if r.get("source") else "")
               + f"\n{r['desc']}\ntraining examples: {fmt_n(r.get('train_n'))}\n"
               f"val class {y:.6f}, range {r.get('val_range')}\n"
               f"verdict: {r['verdict']}" + (f" ({r['reason']})" if r.get("reason") else ""))
        # a near miss and its seed replicates are not kept on their own: draw them like discarded runs and
        # sweep trials (only "rejected" means not deployable)
        cls = {"keep": "dot keep", "discard": "dot discard", "near": "dot discard", "sweep": "dot sweep",
               "replicate": "dot sweep"}.get(r["verdict"], "dot reject")
        clip = " clipped" if y > hi else ""
        body.append(f'<circle cx="{sx(i):.1f}" cy="{sy(yc):.1f}" r="{5 if r["verdict"] == "keep" else 3.5}" '
                    f'class="{cls}{clip}"><title>{E(tip)}</title></circle>')
    note = f"Balanced (today's default) is at {ref_bal:.4f}, off the top of this scale." if ref_bal else ""
    return svg("".join(body), "Validation class error of every run") + (f"<p class='note'>{note} Runs above "
           f"{hi:.4f} sit on the top edge.</p>" if note else "")


def chart_leaves(runs, ref_bal, ref_v1):
    kept = [(r["time"], fnum(r["leaf_class"].split()[0]), r.get("train_n")) for r in runs
            if r["verdict"] == "keep" and r.get("leaf_class")]
    if not kept:
        return "<p class='empty'>No kept runs with real-leaf scores yet.</p>"
    ys = [k[1] for k in kept] + [v for v in (ref_bal, ref_v1) if v]
    lo, hi = min(ys) - 0.001, max(ys) + 0.001
    n = len(kept)
    sx, sy, ax = axes(0, max(n - 1, 1), lo, hi, lambda t: f"{t:.4f}",
                      [(i, f"keep {i + 1}") for i in range(0, n, max(1, n // 5))], "real-leaf class error", w=HW)
    body = [ax]
    if ref_bal:
        body.append(ref_line(sx, sy, 0, max(n - 1, 1), ref_bal, "ref2", f"balanced {ref_bal:.4f}"))
    if ref_v1:
        body.append(ref_line(sx, sy, 0, max(n - 1, 1), ref_v1, "ref", f"leaf net v1 {ref_v1:.4f}"))
    if n > 1:
        body.append('<path d="M' + " L".join(f"{sx(i):.1f},{sy(y):.1f}" for i, (_, y, _n) in enumerate(kept)) +
                    '" class="netline"/>')
    for i, (t, y, n_tr) in enumerate(kept):
        tip = f"kept run {i + 1} ({t}): real-leaf class error {y:.5f}\ntraining examples: {fmt_n(n_tr)}"
        body.append(f'<circle cx="{sx(i):.1f}" cy="{sy(y):.1f}" r="5" class="dot keep">'
                    f'<title>{E(tip)}</title></circle>')
    return svg("".join(body), "Real-leaf class error of kept runs", w=HW)


def chart_growth(prog, goal):
    if not prog or not prog.get("events"):
        return "<p class='empty'>Dataset progress unavailable (offline).</p>"
    ev = sorted(prog["events"], key=lambda e: e.get("time") or e["date"])
    t0 = datetime.datetime.fromisoformat((ev[0].get("time") or ev[0]["date"] + "T00:00:00+00:00"))
    pts, total = [], 0
    for e in ev:
        total += e["examples"]
        t = datetime.datetime.fromisoformat(e.get("time") or e["date"] + "T00:00:00+00:00")
        pts.append(((t - t0).total_seconds() / 86400, total))
    days = max(pts[-1][0], 1)
    sx, sy, ax = axes(0, days, 0, max(total, 1) * 1.08, lambda t: f"{t / 1000:.0f}k",
                      [(d, (t0 + datetime.timedelta(days=d)).strftime("%b %d")) for d in range(0, int(days) + 1, max(1, int(days) // 5))],
                      "validated examples", w=HW)
    d = "M" + " L".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in pts)
    area = d + f" L{sx(pts[-1][0]):.1f},{sy(0):.1f} L{sx(0):.1f},{sy(0):.1f} Z"
    body = [ax, f'<path d="{area}" class="area"/>', f'<path d="{d}" class="netline"/>',
            f'<circle cx="{sx(pts[-1][0]):.1f}" cy="{sy(total):.1f}" r="5" class="dot keep">'
            f'<title>{total:,} validated examples ({pts[-1][0]:.1f} days)</title></circle>',
            f'<text x="{sx(pts[-1][0]) - 8:.1f}" y="{sy(total) - 10:.1f}" class="reflabel" text-anchor="end">'
            f'{total:,} of {goal:,}</text>']
    return svg("".join(body), "Validated examples over time", w=HW)


def bars(items, label, fmt=lambda v: f"{v:,}"):
    """Horizontal bars: [(name, value, tooltip)]."""
    if not items:
        return ""
    vmax = max(v for _, v, _ in items) or 1
    rows = []
    for name, v, tip in items:
        rows.append(f'<div class="bar"><span class="bname">{E(name)}</span>'
                    f'<span class="btrack"><span class="bfill" style="width:{100 * v / vmax:.1f}%" title="{E(tip)}"></span></span>'
                    f'<span class="bval">{fmt(v)}</span></div>')
    return f'<div class="bars" role="list" aria-label="{E(label)}">{"".join(rows)}</div>'


def histogram(values, edges, label, unit):
    counts, _ = np.histogram(values, bins=edges)
    total = max(len(values), 1)
    items = []
    for i, c in enumerate(counts):
        name = f"{edges[i]:g}–{edges[i + 1]:g} {unit}"
        items.append((name, int(c), f"{c:,} examples ({100 * c / total:.1f}%)"))
    return bars(items, label)


# ------------------------------------------------------------------ page ----

CSS = """
:root{--bg:#f6f6f3;--panel:#fcfcfb;--ink:#141412;--ink2:#52514e;--muted:#898781;--grid:#e4e3dc;--base:#c3c2b7;
--net:#2a78d6;--bal:#eb6834;--chip-ok:#0ca30c;--line:rgba(11,11,11,.10);
--body:system-ui,-apple-system,"Segoe UI",sans-serif;--mono:ui-monospace,"Cascadia Mono",Consolas,monospace;}
/* layout: summary tiles, then the loop's charts, then the data, then tables */
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#111110;--panel:#1a1a19;
--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--base:#383835;--net:#3987e5;--bal:#d95926;--line:rgba(255,255,255,.10);}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#111110;--panel:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;
--grid:#2c2c2a;--base:#383835;--net:#3987e5;--bal:#d95926;--line:rgba(255,255,255,.10);}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 var(--body)}
main{max-width:1060px;margin:0 auto;padding:24px 20px 48px;display:grid;gap:22px}
h1{font-size:26px;margin:0;text-wrap:balance}h2{font-size:17px;margin:0 0 4px;text-wrap:balance}
.sub{color:var(--ink2);margin:2px 0 0}.note,.empty{color:var(--muted);font-size:13px;margin:6px 0 0}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.tile .k{color:var(--ink2);font-size:13px}.tile .v{font-size:24px;font-weight:600;font-variant-numeric:tabular-nums}
.tile .d{color:var(--muted);font-size:12.5px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 16px 12px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:22px}
svg{width:100%;height:auto;display:block}
svg .grid{stroke:var(--grid);stroke-width:1}svg .base{stroke:var(--base);stroke-width:1}
svg .tick{fill:var(--muted);font-size:11px;font-family:var(--body);font-variant-numeric:tabular-nums}
svg .reflabel{fill:var(--ink2);font-size:11.5px;font-family:var(--body)}
svg .ref{stroke:var(--muted);stroke-width:1.5;stroke-dasharray:5 4}svg .ref2{stroke:var(--bal);stroke-width:2;stroke-dasharray:6 4}
svg .bestline,svg .netline{fill:none;stroke:var(--net);stroke-width:2}svg .area{fill:var(--net);opacity:.12}
svg .dot{stroke:var(--panel);stroke-width:2}svg .keep{fill:var(--net)}svg .discard{fill:var(--muted);opacity:.75}
svg .sweep{fill:var(--base)}svg .reject{fill:var(--bal)}svg .clipped{opacity:.45}
.legend{display:flex;gap:16px;flex-wrap:wrap;color:var(--ink2);font-size:12.5px;margin:6px 0 2px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px}
.bars{display:grid;gap:6px;margin-top:6px}.bar{display:grid;grid-template-columns:150px 1fr 80px;gap:10px;align-items:center;font-size:13px}
.bname{color:var(--ink2)}.bval{text-align:right;font-variant-numeric:tabular-nums}
.btrack{background:var(--grid);border-radius:4px;height:12px;overflow:hidden}.bfill{display:block;height:100%;background:var(--net);border-radius:4px}
.tablewrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.chip{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;border:1px solid var(--line)}
.chip.keep{background:var(--net);color:#fff;border-color:transparent}.chip.reject{border-color:var(--bal);color:var(--bal)}
@media (max-width:520px){.bar{grid-template-columns:110px 1fr 64px}}
"""


def render(work, out, repo, goal):
    labels = load_labels(work)
    src_th = "<th>Source</th>" if labels else ""   # the Source column appears only with a labels file
    src_td = (lambda r: f"<td>{E(r.get('source') or '')}</td>") if labels else (lambda r: "")
    runs = add_train_examples(work, read_results(work), labels)
    snaps = sorted(os.listdir(os.path.join(work, "snapshots"))) if os.path.isdir(os.path.join(work, "snapshots")) else []
    cur = open(os.path.join(work, "CURRENT_SNAPSHOT"), encoding="utf-8").read().strip() if os.path.exists(
        os.path.join(work, "CURRENT_SNAPSHOT")) else (snaps[-1] if snaps else None)
    state = {}
    if cur and os.path.exists(os.path.join(work, "runs", cur, "state.json")):
        state = json.load(open(os.path.join(work, "runs", cur, "state.json"), encoding="utf-8"))
    spread = state.get("seed_spread", {})
    bal_val = spread.get("balanced_val_class")
    cur_runs = [r for r in runs if r["snapshot"] == cur]
    noise = [fnum(r["val_class"]) for r in cur_runs if r["desc"].startswith("noise seed")]
    v1_val = noise[0] if noise else None
    loop_runs = [r for r in cur_runs if not r["desc"].startswith("noise seed")]
    kept = [r for r in loop_runs if r["verdict"] == "keep"]
    best_run = state.get("best")
    best = next((r for r in reversed(cur_runs) if r["run"] == best_run), None)
    leaf_v1 = next((fnum(r["leaf_class"].split()[0]) for r in cur_runs
                    if r["desc"].startswith("noise seed 0") and r.get("leaf_class")), None)
    leaf_bal = None
    if cur:
        try:
            import harness
            es = harness.EvalSet(os.path.join(work, "snapshots", cur, "leaf", "datagen_leafcheck_v2"))
            leaf_bal = harness.totals(es.sums(es.base["balanced"]))[0]
        except Exception:
            leaf_bal = None
    prog = progress_events(repo)
    stats = snapshot_stats(work, cur) if cur else None
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def tile(k, v, d=""):
        return f'<div class="tile"><div class="k">{E(k)}</div><div class="v">{v}</div><div class="d">{d}</div></div>'

    best_v = fnum(best["val_class"]) if best else None
    gain = (bal_val - best_v) if (bal_val and best_v) else None
    gain_v1 = (v1_val - best_v) if (v1_val and best_v) else None
    tiles = [
        tile("Best validation class error", f"{best_v:.5f}" if best_v else "–",
             (f"balanced {bal_val:.5f}; the net removes {gain:.5f}" if gain else "")),
        tile("Gain over the v1 setup", f"{gain_v1:+.5f}" if gain_v1 is not None else "–",
             (f"{100 * gain_v1 / gain:.1f}% of the net's total gain; seed spread {spread.get('class', 0):.6f}"
              if gain_v1 is not None and gain else "")),
        tile("Real-leaf class error (best)", (best.get("leaf_class") or "–").split()[0] if best else "–",
             f"balanced {leaf_bal:.4f}, leaf net v1 {leaf_v1:.4f}" if leaf_bal and leaf_v1 else ""),
        tile("Loop runs", f"{len(loop_runs)}", f"{len(kept)} kept, "
             f"{sum(r['verdict'] == 'sweep' for r in loop_runs)} sweep trials, "
             f"{sum(r['verdict'] in ('discard', 'rejected') for r in loop_runs)} discarded or rejected"),
        tile("Training data", f"{stats['manifest']['examples']:,}" if stats else "–",
             (f"snapshot {cur}; dataset now {prog.get('total_examples', 0):,} of {goal:,}" if prog else f"snapshot {cur}")),
    ]

    legend = ('<div class="legend"><span><i style="background:var(--net)"></i>kept (best-so-far line)</span>'
              '<span><i style="background:var(--muted)"></i>discarded</span>'
              '<span><i style="background:var(--base)"></i>sweep trial</span>'
              '<span><i style="background:var(--bal)"></i>rejected (not deployable)</span></div>')
    parts = [f'<header><h1>Leaf net: training progress</h1><p class="sub">Autoresearch loop on the RTX 5090 and the '
             f'data behind it. Updated {now}. Lower error is better; errors are against exact single-flop solves, '
             f'so most of each number is flop-to-flop noise no flop-blind model can remove.</p></header>',
             f'<section class="tiles">{"".join(tiles)}</section>',
             f'<section class="panel"><h2>Every run on snapshot {E(cur or "")}</h2>'
             f'<p class="note">Validation class error, in run order. Hover a dot for the run.</p>{legend}'
             f'{chart_progress(loop_runs, v1_val, bal_val)}</section>',
             '<section class="grid2">'
             f'<div class="panel"><h2>Real Preflop Lab leaves</h2><p class="note">Class error on 640 exact solves of the '
             f'80 leaves a solved 6-max game reaches, for each kept run.</p>{chart_leaves(cur_runs and kept, leaf_bal, leaf_v1)}</div>'
             f'<div class="panel"><h2>Training data collected</h2><p class="note">Validated examples in the shared '
             f'dataset over time (goal {goal:,}).</p>{chart_growth(prog, goal)}</div></section>']
    summary_path = os.path.join(work, "loop_summary.txt")   # optional: first line is the heading, then one paragraph per line
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8-sig") as f:
            lines = [l.strip() for l in f if l.strip()]
        if lines:
            parts.insert(2, f'<section class="panel"><h2>{E(lines[0])}</h2>'
                            + "".join(f'<p class="sub" style="margin:8px 0 0">{E(l)}</p>' for l in lines[1:]) + '</section>')
    if stats:
        m = stats["manifest"]
        n = len(stats["pot_type"])
        pts = [(POT_TYPES[i], int((stats["pot_type"] == i).sum()), "") for i in range(4)]
        pts = [(a, b, f"{b:,} examples ({100 * b / n:.1f}%)") for a, b, _ in pts]
        gens = [(f"generator v{g}", int((stats["generator"] == g).sum()), "") for g in sorted(set(stats["generator"].tolist()))]
        gens = [(a, b, f"{b:,} examples") for a, b, _ in gens]
        split = [(k, v, f"{v:,} examples in {m['jobs_by_split'][k]} jobs") for k, v in m["examples_by_split"].items()]
        rk = stats["rake"]
        rakes = [("no rake", int((rk < 1e-6).sum()), ""), ("5%", int((np.abs(rk - 0.05) < 1e-6).sum()), ""),
                 ("10%", int((np.abs(rk - 0.10) < 1e-6).sum()), ""),
                 ("other", int(((rk > 1e-6) & (np.abs(rk - 0.05) > 1e-6) & (np.abs(rk - 0.10) > 1e-6)).sum()), "")]
        rakes = [(a, b, f"{b:,} examples ({100 * b / n:.1f}%)") for a, b, _ in rakes if b]
        parts.append(
            f'<section class="panel"><h2>What the current snapshot contains</h2>'
            f'<p class="note">{m["examples"]:,} examples from {m["files"]} job files, frozen {E(m["created"][:16])} UTC; '
            f'{int(stats["scaled"].sum()):,} with scaled-up pots (v3). Test jobs are never used by the loop.</p>'
            f'<div class="grid2"><div><h2>Pot type</h2>{bars(pts, "pot types")}<h2 style="margin-top:14px">Split</h2>'
            f'{bars(split, "split")}<h2 style="margin-top:14px">Generator</h2>{bars(gens, "generator versions")}'
            f'<h2 style="margin-top:14px">Rake</h2>{bars(rakes, "rake")}</div>'
            f'<div><h2>Pot at the flop</h2>{histogram(stats["pot"], [0, 3.5, 7.5, 15, 26, 40, 55, 100, 200], "pot sizes", "bb")}'
            f'<h2 style="margin-top:14px">Stack-to-pot ratio</h2>'
            f'{histogram(stats["spr"], [0, 1, 2, 4, 8, 16, 41], "stack to pot", "")}'
            f'<h2 style="margin-top:14px">Effective stack</h2>{histogram(stats["stack"], [0, 25, 50, 100, 150, 200, 400], "stacks", "bb")}'
            f'</div></div></section>')
    rows = []
    for r in kept:
        rows.append(f"<tr><td>{E(r['time'][5:16].replace('T', ' '))}</td>{src_td(r)}<td>{E(r['desc'])}</td>"
                    f"<td class='n'>{fmt_n(r.get('train_n'))}</td>"
                    f"<td class='n'>{E(r['val_class'])}</td><td class='n'>{E(r.get('gain_class') or '–')}</td>"
                    f"<td class='n'>{E(r['val_range'])}</td><td class='n'>{E((r.get('leaf_class') or '–').split()[0])}</td></tr>")
    parts.append('<section class="panel"><h2>Kept runs</h2><div class="tablewrap"><table><thead><tr><th>When</th>'
                 f'{src_th}<th>Change</th><th class="n">Training examples</th><th class="n">Val class</th><th class="n">Gain</th>'
                 '<th class="n">Val range</th>'
                 f'<th class="n">Real leaves</th></tr></thead><tbody>{"".join(rows) or "<tr><td colspan=8>None yet</td></tr>"}'
                 '</tbody></table></div></section>')
    recent = []
    for r in list(reversed(loop_runs))[:25]:
        chip = {"keep": "keep", "rejected": "reject"}.get(r["verdict"], "")
        recent.append(f"<tr><td>{E(r['time'][11:16])}</td>{src_td(r)}<td>{E(r['desc'])}</td><td class='n'>{fmt_n(r.get('train_n'))}</td>"
                      f"<td class='n'>{E(r.get('val_class') or '–')}</td>"
                      f"<td><span class='chip {chip}'>{E(r['verdict'])}</span></td><td>{E(r.get('reason') or '')}</td></tr>")
    parts.append('<section class="panel"><h2>Latest 25 runs</h2><div class="tablewrap"><table><thead><tr><th>Time</th>'
                 f'{src_th}<th>Change</th><th class="n">Training examples</th><th class="n">Val class</th><th>Verdict</th><th>Why</th></tr></thead><tbody>'
                 f'{"".join(recent)}</tbody></table></div></section>')
    page = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
            'content="width=device-width,initial-scale=1"><title>Leaf net progress</title>'
            f'<style>{CSS}</style></head><body><main>{"".join(parts)}</main></body></html>')
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    return out


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", default=work_dir())
    ap.add_argument("--out")
    args = ap.parse_args()
    out = args.out or os.path.join(args.work, "dashboard.html")
    print(render(args.work, out, cfg["hf_repo"], int(cfg.get("goal_examples", 300000))))


if __name__ == "__main__":
    main()
