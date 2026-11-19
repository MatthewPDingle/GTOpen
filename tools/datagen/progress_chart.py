#!/usr/bin/env python3
"""Render the pooled data generation progress graph (SVG) and a contributors table.

    python tools/datagen/progress_chart.py --progress progress.json --out site/
    python tools/datagen/progress_chart.py --out site/   # fetch from the dataset

Writes progress.svg (cumulative validated examples over time, split by
contributor, with the go/no-go and goal marks) and contributors.md. Standard library only, so the
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

W = 820
L, R, B = 64, 128, 44  # plot margins (right margin holds the mark labels)
PLOT_H = 232
# One colour per contributor (light, dark), given in the order they first
# contributed so a colour stays with its contributor as the pool grows.
SERIES = [("#2a78d6", "#3987e5"), ("#eb6834", "#d95926"), ("#1baf7a", "#199e70"), ("#eda100", "#c98500"),
          ("#e87ba4", "#d55181"), ("#008300", "#0ca30c"), ("#6250d6", "#9085e9")]
OTHERS = ("#8a8983", "#8f8e87")


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


UTC = datetime.timezone.utc


def event_time(e):
    """When an entry was merged (UTC). Older entries carry only a date: noon that day."""
    if e.get("time"):
        t = datetime.datetime.fromisoformat(e["time"].replace("Z", "+00:00"))
        return t.replace(tzinfo=UTC) if t.tzinfo is None else t.astimezone(UTC)
    d = datetime.date.fromisoformat(e["date"])
    return datetime.datetime(d.year, d.month, d.day, 12, tzinfo=UTC)


def series(progress):
    """[(merge time, cumulative examples)], one point per merge."""
    per_time = {}
    for e in progress.get("events", []):
        t = event_time(e)
        per_time[t] = per_time.get(t, 0) + int(e["examples"])
    out, total = [], 0
    for t in sorted(per_time):
        total += per_time[t]
        out.append((t, total))
    return out


def contributor_bands(progress):
    """([(name, examples, colour index or None)], {contributor: band}), bottom band first.

    Contributors come in the order they first contributed, each with its own
    colour. When there are more than the palette holds, the largest keep a
    band of their own and the rest share one grey "others" band on top."""
    totals, first = {}, {}
    for e in progress.get("events", []):
        name, t = e["contributor"], event_time(e)
        totals[name] = totals.get(name, 0) + int(e["examples"])
        first[name] = min(first.get(name, t), t)
    names = sorted(totals, key=lambda n: (first[n], n))
    own = names
    if len(names) > len(SERIES):
        biggest = set(sorted(names, key=lambda n: (-totals[n], first[n], n))[:len(SERIES)])
        own = [n for n in names if n in biggest]
    bands = [(n, totals[n], i) for i, n in enumerate(own)]
    band_of = {n: i for i, n in enumerate(own)}
    rest = [n for n in names if n not in band_of]
    if rest:
        for n in rest:
            band_of[n] = len(bands)
        bands.append((f"{len(rest)} others", sum(totals[n] for n in rest), None))
    return bands, band_of


def stacked_series(progress, n_bands, band_of):
    """[(merge time, [running total through band 0, through band 1, ...])]."""
    per_time = {}
    for e in progress.get("events", []):
        row = per_time.setdefault(event_time(e), [0] * n_bands)
        row[band_of[e["contributor"]]] += int(e["examples"])
    out, run = [], [0] * n_bands
    for t in sorted(per_time):
        run = [a + b for a, b in zip(run, per_time[t])]
        tops, acc = [], 0
        for v in run:
            acc += v
            tops.append(acc)
        out.append((t, tops))
    return out


def time_label(t, span_s):
    if span_s <= 2 * 86400:
        return t.strftime("%b %d %H:%M UTC").replace(" 0", " ")
    return t.strftime("%b %d").replace(" 0", " ")


def legend_rows(bands, width):
    """Lay the legend out in rows that fit the width: [[(x, name, examples, colour index)]]."""
    rows, x = [[]], 0
    for name, ex, colour in bands:
        w = 18 + 6.6 * len(f"{name} {ex:,}") + 18  # swatch, text, gap
        if rows[-1] and x + w > width:
            rows.append([])
            x = 0
        rows[-1].append((x, name, ex, colour))
        x += w
    return rows


def render_svg(progress, cfg):
    goal = int(progress.get("goal_examples", cfg["goal_examples"]))
    gate = int(progress.get("go_no_go_examples", cfg["go_no_go_examples"]))
    bands, band_of = contributor_bands(progress)
    pts = stacked_series(progress, len(bands), band_of)
    total = pts[-1][1][-1] if pts else 0
    n_contrib = len(band_of)
    ymax, ystep = nice_ceiling(max(goal, total) * 1.05)
    now = datetime.datetime.now(UTC)
    if pts:
        x1 = max(now, pts[-1][0])
        # lead-in before the first merge: a tenth of the span, at least an hour
        x0 = pts[0][0] - max((x1 - pts[0][0]) / 10, datetime.timedelta(hours=1))
    else:
        x0, x1 = now - datetime.timedelta(days=7), now
    span = max((x1 - x0).total_seconds(), 1)
    pw, ph = W - L - R, PLOT_H
    # A legend only when there is more than one contributor to tell apart.
    legend = legend_rows(bands, W - L - 16) if len(bands) > 1 else []
    T = 64 + 20 * len(legend) + (6 if legend else 0)
    H = T + ph + B

    def X(t):
        return L + pw * (t - x0).total_seconds() / span

    def Y(v):
        return T + ph * (1 - v / ymax)

    def css(colour):
        return "so" if colour is None else f"s{colour}"

    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
             f'role="img" aria-labelledby="t d">')
    pct = 100 * total / goal if goal else 0
    title = f"{total:,} training examples from {n_contrib} contributor{'s' if n_contrib != 1 else ''}"
    o.append(f'<title id="t">GTOpen value-net training data: {escape(title)}</title>')
    split = "; ".join(f"{name} {ex:,}" for name, ex, _ in bands)
    o.append(f'<desc id="d">Cumulative validated examples over time, split by contributor'
             f'{": " + escape(split) if split else ""}. Go/no-go check at {gate:,}, '
             f'goal {goal:,}. {pct:.1f}% of goal.</desc>')
    light = "".join(f".s{i}{{fill:{c[0]}}}" for i, c in enumerate(SERIES)) + f".so{{fill:{OTHERS[0]}}}"
    dark = "".join(f".s{i}{{fill:{c[1]}}}" for i, c in enumerate(SERIES)) + f".so{{fill:{OTHERS[1]}}}"
    o.append(f"""<style>
  .bg{{fill:#fcfcfb}}.t1{{fill:#0b0b0b}}.t2{{fill:#52514e}}.grid{{stroke:#e4e3df}}.axis{{stroke:#b9b8b2}}
  .mark{{stroke:#8a8983;stroke-dasharray:5 4}}.band{{stroke:#fcfcfb}}.top{{stroke:#0b0b0b;fill:none}}
  .dot{{fill:#0b0b0b;stroke:#fcfcfb}}
  {light}
  text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
  @media (prefers-color-scheme: dark){{
    .bg{{fill:#1a1a19}}.t1{{fill:#f0efec}}.t2{{fill:#c3c2b7}}.grid{{stroke:#33332f}}.axis{{stroke:#5a5953}}
    .mark{{stroke:#8f8e87}}.band{{stroke:#1a1a19}}.top{{stroke:#f0efec}}.dot{{fill:#f0efec;stroke:#1a1a19}}
    {dark}
  }}
</style>""")
    o.append(f'<rect class="bg" width="{W}" height="{H}" rx="8"/>')
    o.append(f'<text class="t1" x="{L}" y="28" font-size="17" font-weight="600">{escape(title)}</text>')
    updated = progress.get("updated", "never")[:16].replace("T", " ")
    sub = (f"{pct:.1f}% of the {fmt_k(goal)} goal · updated {updated}{' UTC' if updated != 'never' else ''}"
           if pts else "Pilot starting: no validated examples yet")
    o.append(f'<text class="t2" x="{L}" y="48" font-size="12.5">{escape(sub)}</text>')
    # legend: one entry per band, name in text colour beside its swatch
    for r, row in enumerate(legend):
        y = 70 + 20 * r
        for x, name, ex, colour in row:
            o.append(f'<rect class="{css(colour)}" x="{L + x:.1f}" y="{y - 9}" width="11" height="11" rx="2.5"/>')
            o.append(f'<text class="t2" x="{L + x + 17:.1f}" y="{y + 1}" font-size="12">'
                     f'<tspan class="t1" font-weight="600">{escape(name)}</tspan> {ex:,}</text>')
    # grid + y labels
    v = 0
    while v <= ymax + 1:
        y = Y(v)
        o.append(f'<line class="grid" x1="{L}" x2="{L + pw}" y1="{y:.1f}" y2="{y:.1f}" stroke-width="1"/>')
        o.append(f'<text class="t2" x="{L - 8}" y="{y + 4:.1f}" font-size="11" text-anchor="end">{fmt_k(v)}</text>')
        v += ystep
    # x labels: start, middle, now
    for t, anchor in ((x0, "start"), (x0 + datetime.timedelta(seconds=span / 2), "middle"), (x1, "end")):
        o.append(f'<text class="t2" x="{X(t):.1f}" y="{T + ph + 18}" font-size="11" text-anchor="{anchor}">'
                 f'{time_label(t, span)}</text>')
    # go/no-go and goal marks
    for val, label in ((gate, f"Go/no-go check {fmt_k(gate)}"), (goal, f"Goal {fmt_k(goal)}")):
        y = Y(val)
        o.append(f'<line class="mark" x1="{L}" x2="{L + pw}" y1="{y:.1f}" y2="{y:.1f}" stroke-width="1.5"/>')
        o.append(f'<text class="t2" x="{L + pw + 8}" y="{y + 4:.1f}" font-size="11.5">{escape(label)}</text>')
    # one filled band per contributor, stacked (steps: a total holds until the next merge)
    if pts:
        def steps(b):
            """The step line along the top of band b (b = -1: the baseline)."""
            path = [(X(x0), Y(0))]
            for t, tops in pts:
                path.append((X(t), path[-1][1]))
                path.append((X(t), Y(tops[b] if b >= 0 else 0)))
            path.append((X(x1), path[-1][1]))
            return path

        def d(path, start="M"):
            return " ".join(f"{start if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(path))

        for b in range(len(bands) - 1, -1, -1):  # top band first, so each band's edge shows over the one above
            name, ex, colour = bands[b]
            o.append(f'<path class="{css(colour)} band" stroke-width="1" stroke-linejoin="round" '
                     f'd="{d(steps(b))} {d(steps(b - 1)[::-1], "L")} Z"><title>{escape(name)}: {ex:,} examples</title></path>')
        o.append(f'<path class="top" d="{d(steps(len(bands) - 1))}" stroke-width="1.5" stroke-linejoin="round"/>')
        o.append(f'<circle class="dot" cx="{X(x1):.1f}" cy="{Y(total):.1f}" r="4" stroke-width="2"/>')
        o.append(f'<text class="t1" x="{X(x1) - 8:.1f}" y="{Y(total) - 10:.1f}" font-size="12.5" '
                 f'font-weight="600" text-anchor="end">{total:,}</text>')
    o.append(f'<line class="axis" x1="{L}" x2="{L + pw}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke-width="1"/>')
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
    with open(os.path.join(args.out, "progress.svg"), "w", encoding="utf-8") as f:
        f.write(render_svg(progress, cfg))
    with open(os.path.join(args.out, "contributors.md"), "w", encoding="utf-8") as f:
        f.write(render_table(progress))
    with open(os.path.join(args.out, "progress.json"), "w") as f:
        json.dump(progress, f, indent=1)
    print(f"wrote {args.out}/progress.svg, contributors.md, progress.json")


if __name__ == "__main__":
    main()
