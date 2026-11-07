#!/usr/bin/env python3
"""Render the pooled data generation progress graph (SVG) and a contributors table.

    python tools/datagen/progress_chart.py --progress progress.json --out site/
    python tools/datagen/progress_chart.py --out site/   # fetch from the dataset

Writes progress.svg (cumulative validated examples over time, with the
go/no-go and goal marks) and contributors.md. Standard library only, so the
GitHub Action needs no installs. A missing progress.json renders an empty
"not started" chart.
"""

import argparse
import datetime
import json
import sys
import os
import urllib.request
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 820, 340
L, R, T, B = 64, 128, 64, 44  # plot margins (right margin holds the mark labels)


def load_config():
    with open(os.path.join(HERE, "config.json")) as f:
        return json.load(f)


def fetch_progress(repo):
    url = f"https://huggingface.co/datasets/{repo}/resolve/main/progress.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except Exception:
        return None


def fmt_k(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1000:
        return f"{n / 1000:.0f}k"
    return str(int(n))


def nice_ceiling(x):
    for step in (10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000):
        if x <= step * 6:
            return step * int(-(-x // step)), step
    return x, x / 6


def series(progress):
    """[(date, cumulative examples)] by day."""
    per_day = {}
    for e in progress.get("events", []):
        per_day[e["date"]] = per_day.get(e["date"], 0) + int(e["examples"])
    out, total = [], 0
    for d in sorted(per_day):
        total += per_day[d]
        out.append((datetime.date.fromisoformat(d), total))
    return out


def render_svg(progress, cfg):
    goal = int(progress.get("goal_examples", cfg["goal_examples"]))
    gate = int(progress.get("go_no_go_examples", cfg["go_no_go_examples"]))
    pts = series(progress)
    total = pts[-1][1] if pts else 0
    n_contrib = len({e["contributor"] for e in progress.get("events", [])})
    ymax, ystep = nice_ceiling(max(goal, total) * 1.05)
    today = datetime.date.today()
    if pts:
        x0 = pts[0][0] - datetime.timedelta(days=1)
        x1 = max(today, pts[-1][0])
    else:
        x0, x1 = today - datetime.timedelta(days=7), today
    span = max((x1 - x0).days, 1)
    pw, ph = W - L - R, H - T - B

    def X(d):
        return L + pw * (d - x0).days / span

    def Y(v):
        return T + ph * (1 - v / ymax)

    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             f'role="img" aria-labelledby="t d">')
    pct = 100 * total / goal if goal else 0
    title = f"{total:,} training examples from {n_contrib} contributor{'s' if n_contrib != 1 else ''}"
    o.append(f'<title id="t">GTOpen value-net training data: {escape(title)}</title>')
    o.append(f'<desc id="d">Cumulative validated examples over time. Go/no-go check at {gate:,}, '
             f'goal {goal:,}. {pct:.1f}% of goal.</desc>')
    o.append("""<style>
  .bg{fill:#fcfcfb}.t1{fill:#0b0b0b}.t2{fill:#52514e}.grid{stroke:#e4e3df}.axis{stroke:#b9b8b2}
  .mark{stroke:#8a8983;stroke-dasharray:5 4}.line{stroke:#2a78d6;fill:none}.area{fill:#2a78d6;fill-opacity:.12}
  .dot{fill:#2a78d6;stroke:#fcfcfb}
  text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
  @media (prefers-color-scheme: dark){
    .bg{fill:#1a1a19}.t1{fill:#f0efec}.t2{fill:#c3c2b7}.grid{stroke:#33332f}.axis{stroke:#5a5953}
    .mark{stroke:#8f8e87}.line{stroke:#3987e5}.area{fill:#3987e5;fill-opacity:.18}.dot{fill:#3987e5;stroke:#1a1a19}
  }
</style>""")
    o.append(f'<rect class="bg" width="{W}" height="{H}" rx="8"/>')
    o.append(f'<text class="t1" x="{L}" y="28" font-size="17" font-weight="600">{escape(title)}</text>')
    sub = (f"{pct:.1f}% of the {fmt_k(goal)} goal · updated {progress.get('updated', 'never')[:10]}"
           if pts else "Pilot starting: no validated examples yet")
    o.append(f'<text class="t2" x="{L}" y="48" font-size="12.5">{escape(sub)}</text>')
    # grid + y labels
    v = 0
    while v <= ymax + 1:
        y = Y(v)
        o.append(f'<line class="grid" x1="{L}" x2="{L + pw}" y1="{y:.1f}" y2="{y:.1f}" stroke-width="1"/>')
        o.append(f'<text class="t2" x="{L - 8}" y="{y + 4:.1f}" font-size="11" text-anchor="end">{fmt_k(v)}</text>')
        v += ystep
    o.append(f'<line class="axis" x1="{L}" x2="{L + pw}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke-width="1"/>')
    # x labels: first, middle, last date
    for d in sorted({x0, x0 + datetime.timedelta(days=span // 2), x1}):
        o.append(f'<text class="t2" x="{X(d):.1f}" y="{T + ph + 18}" font-size="11" text-anchor="middle">'
                 f'{d.strftime("%b %-d") if os.name != "nt" else d.strftime("%b %d")}</text>')
    # go/no-go and goal marks
    for val, label in ((gate, f"Go/no-go check {fmt_k(gate)}"), (goal, f"Goal {fmt_k(goal)}")):
        y = Y(val)
        o.append(f'<line class="mark" x1="{L}" x2="{L + pw}" y1="{y:.1f}" y2="{y:.1f}" stroke-width="1.5"/>')
        o.append(f'<text class="t2" x="{L + pw + 8}" y="{y + 4:.1f}" font-size="11.5">{escape(label)}</text>')
    # series (steps: the total holds until the next validated batch)
    if pts:
        path = [(X(x0), Y(0))]
        for d, c in pts:
            path.append((X(d), path[-1][1]))
            path.append((X(d), Y(c)))
        path.append((X(x1), Y(total)))
        line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(path))
        area = line + f" L{X(x1):.1f},{Y(0):.1f} Z"
        o.append(f'<path class="area" d="{area}"/>')
        o.append(f'<path class="line" d="{line}" stroke-width="2" stroke-linejoin="round"/>')
        o.append(f'<circle class="dot" cx="{X(x1):.1f}" cy="{Y(total):.1f}" r="4.5" stroke-width="2"/>')
        o.append(f'<text class="t1" x="{X(x1) - 8:.1f}" y="{Y(total) - 10:.1f}" font-size="12.5" '
                 f'font-weight="600" text-anchor="end">{total:,}</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


def render_table(progress):
    contrib = {}
    for e in progress.get("events", []):
        c = contrib.setdefault(e["contributor"], [0, 0, e["date"]])
        c[0] += int(e["examples"])
        c[1] += int(e["jobs"])
        c[2] = max(c[2], e["date"])
    lines = ["# Contributors", "",
             "Validated examples per contributor (updated automatically).", "",
             "| Contributor | Examples | Jobs | Last upload |", "| --- | ---: | ---: | --- |"]
    for login, (ex, jobs, last) in sorted(contrib.items(), key=lambda kv: -kv[1][0]):
        lines.append(f"| [{login}](https://github.com/{login}) | {ex:,} | {jobs:,} | {last} |")
    if not contrib:
        lines.append("| (none yet) | | | |")
    return "\n".join(lines) + "\n"


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--progress", help="progress.json path (default: fetch from the dataset)")
    ap.add_argument("--repo", default=cfg["hf_repo"])
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    if args.progress:
        with open(args.progress) as f:
            progress = json.load(f)
    else:
        progress = fetch_progress(args.repo)
        if progress is None:
            # Don't replace a good graph with an empty one on a network blip.
            sys.exit(f"could not fetch progress.json from {args.repo}; graph left unchanged")
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "progress.svg"), "w") as f:
        f.write(render_svg(progress, cfg))
    with open(os.path.join(args.out, "contributors.md"), "w") as f:
        f.write(render_table(progress))
    with open(os.path.join(args.out, "progress.json"), "w") as f:
        json.dump(progress, f, indent=1)
    print(f"wrote {args.out}/progress.svg, contributors.md, progress.json")


if __name__ == "__main__":
    main()
