#!/usr/bin/env python3
"""Render the pooled data generation progress graph (SVG) and a contributors table.

    python tools/datagen/progress_chart.py --progress progress.json --out site/
    python tools/datagen/progress_chart.py --out site/   # fetch from the dataset

Writes progress.svg (cumulative validated examples over time, with the
go/no-go and goal marks) and contributors.md. Standard library only, so the
GitHub Action needs no installs. A missing progress.json renders an empty
"not started" chart.

Under the graph the SVG lists the stages of config.json's "stages": what the
pool was given to solve from when, and what that data is for. A stage is
marked on the graph by its number where it began. A stage with a "target"
({"list": NAME, "solves": N}) gets a bar: how many validated examples were
drawn from that published situation list so far (the events' "spots", which
validate.py counts as it merges).

A target can also say how many solves it needs of each pot type
("by_pot_type": {"limped": N, "srp": N, ...}, adding up to "solves"). The big
trees of a list fit only big cards, so small cards fill the small pot types
many times over; counted in one lump, the target would look met while the big
ones were still short. With "by_pot_type" the bar counts a pot type only up
to what it needs, and a row per pot type shows which ones are short (the
events' "spot_types"). Under the stages one line gives the pool's examples by
game size, for the examples that record it (the events' "sizes").
"""

import argparse
import datetime
import json
import sys
import os
import urllib.request
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 820, 340               # H is the graph's part; the list of stages comes under it
L, R, T, B = 64, 128, 64, 44  # plot margins (right margin holds the mark labels)
STAGE_H, BAR_H = 42, 24       # a stage's row under the graph, and the extra room its target bar takes
TYPE_H = 17                   # a pot type's row under a target bar
SIZES_H = 26                  # the line of game sizes under the stages
POT_TYPES = (("limped", "Limped pots"), ("srp", "Single-raised pots"), ("3bet", "3-bet pots"), ("4bet", "4-bet pots"))
SIZE_BANDS = (("0-6", "under 6 GB"), ("6-12", "6 to 12 GB"), ("12-19", "12 to 19 GB"), ("19+", "over 19 GB"))


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


def stage_time(stage):
    """When a stage began (UTC): its "since", a date or a full time."""
    since = stage["since"]
    if len(since) <= 10:
        d = datetime.date.fromisoformat(since)
        return datetime.datetime(d.year, d.month, d.day, tzinfo=UTC)
    t = datetime.datetime.fromisoformat(since.replace("Z", "+00:00"))
    return t.replace(tzinfo=UTC) if t.tzinfo is None else t.astimezone(UTC)


def spots(progress):
    """Validated examples drawn from each published situation list: {list: count}."""
    out = {}
    for e in progress.get("events", []):
        for name, n in (e.get("spots") or {}).items():
            out[name] = out.get(name, 0) + int(n)
    return out


def spot_types(progress):
    """Validated examples drawn from each published situation list by pot type: {list: {pot type: count}}."""
    out = {}
    for e in progress.get("events", []):
        for name, by in (e.get("spot_types") or {}).items():
            mine = out.setdefault(name, {})
            for pot_type, n in by.items():
                mine[pot_type] = mine.get(pot_type, 0) + int(n)
    return out


def sizes(progress):
    """Validated examples by size band, over the examples that record their tree size: {band: count}."""
    out = {}
    for e in progress.get("events", []):
        for band, n in (e.get("sizes") or {}).items():
            out[band] = out.get(band, 0) + int(n)
    return out


def target_rows(target, done, done_by_type):
    """A target's count and its rows by pot type: (have, want, [(label, have, want)]).

    With "by_pot_type" (and once any merge is counted by pot type) a pot type
    counts only up to what the target needs of it, so extra solves of a kind
    that is full do not stand in for a kind that is short. Otherwise the
    list's examples count in one lump, as before."""
    want, lump = int(target["solves"]), done.get(target["list"], 0)
    needs, by = target.get("by_pot_type"), done_by_type.get(target["list"])
    if not needs or not by:
        return lump, want, []
    rows = [(label, by.get(key, 0), int(needs[key])) for key, label in POT_TYPES if key in needs]
    return sum(min(have, need) for _, have, need in rows), want, rows


def time_label(t, span_s):
    if span_s <= 2 * 86400:
        return t.strftime("%b %d %H:%M UTC").replace(" 0", " ")
    return t.strftime("%b %d").replace(" 0", " ")


def render_svg(progress, cfg, now=None):
    goal = int(progress.get("goal_examples", cfg["goal_examples"]))
    gate = int(progress.get("go_no_go_examples", cfg["go_no_go_examples"]))
    pts = series(progress)
    total = pts[-1][1] if pts else 0
    n_contrib = len({e["contributor"] for e in progress.get("events", [])})
    ymax, ystep = nice_ceiling(max(goal, total) * 1.05)
    now = now or datetime.datetime.now(UTC)
    if pts:
        x1 = max(now, pts[-1][0])
        # lead-in before the first merge: a tenth of the span, at least an hour
        x0 = pts[0][0] - max((x1 - pts[0][0]) / 10, datetime.timedelta(hours=1))
    else:
        x0, x1 = now - datetime.timedelta(days=7), now
    span = max((x1 - x0).total_seconds(), 1)
    pw, ph = W - L - R, H - T - B

    def X(t):
        return L + pw * (t - x0).total_seconds() / span

    def Y(v):
        return T + ph * (1 - v / ymax)

    stages = sorted(cfg.get("stages", []), key=stage_time)
    done, done_by_type, by_size = spots(progress), spot_types(progress), sizes(progress)
    targets = {i: target_rows(s["target"], done, done_by_type) for i, s in enumerate(stages) if s.get("target")}
    full = H + (34 + sum(STAGE_H + (BAR_H + TYPE_H * len(targets[i][2]) + (6 if targets[i][2] else 0) if i in targets else 0)
                         for i, s in enumerate(stages)) + (SIZES_H if by_size else 0) + 8 if stages else 0)
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {full}" width="{W}" height="{full}" '
             f'role="img" aria-labelledby="t d">')
    pct = 100 * total / goal if goal else 0
    title = f"{total:,} training examples from {n_contrib} contributor{'s' if n_contrib != 1 else ''}"
    o.append(f'<title id="t">GTOpen value-net training data: {escape(title)}</title>')
    told = " ".join(f"Stage {i}, from {stage_time(s).strftime('%b %d').replace(' 0', ' ')}: {s['title']}. {s['for']}."
                    for i, s in enumerate(stages, 1))
    o.append(f'<desc id="d">Cumulative validated examples over time. Go/no-go check at {gate:,}, '
             f'goal {goal:,}. {pct:.1f}% of goal. {escape(told)}</desc>')
    o.append("""<style>
  .bg{fill:#fcfcfb}.t1{fill:#0b0b0b}.t2{fill:#52514e}.grid{stroke:#e4e3df}.axis{stroke:#b9b8b2}
  .mark{stroke:#8a8983;stroke-dasharray:5 4}.line{stroke:#2a78d6;fill:none}.area{fill:#2a78d6;fill-opacity:.12}
  .dot{fill:#2a78d6;stroke:#fcfcfb}.stage{stroke:#8a8983;stroke-dasharray:2 4}.num{fill:#52514e}.numt{fill:#fcfcfb}
  .rule{stroke:#e4e3df}.track{fill:#e4e3df}.fill{fill:#2a78d6}
  text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
  @media (prefers-color-scheme: dark){
    .bg{fill:#1a1a19}.t1{fill:#f0efec}.t2{fill:#c3c2b7}.grid{stroke:#33332f}.axis{stroke:#5a5953}
    .mark{stroke:#8f8e87}.line{stroke:#3987e5}.area{fill:#3987e5;fill-opacity:.18}.dot{fill:#3987e5;stroke:#1a1a19}
    .stage{stroke:#8f8e87}.num{fill:#c3c2b7}.numt{fill:#1a1a19}.rule{stroke:#33332f}.track{fill:#33332f}.fill{fill:#3987e5}
  }
</style>""")
    o.append(f'<rect class="bg" width="{W}" height="{full}" rx="8"/>')
    o.append(f'<text class="t1" x="{L}" y="28" font-size="17" font-weight="600">{escape(title)}</text>')
    updated = progress.get("updated", "never")[:16].replace("T", " ")
    reached = f"past the {fmt_k(goal)} goal" if total >= goal else f"{pct:.1f}% of the {fmt_k(goal)} goal"
    sub = (f"{reached} · updated {updated}{' UTC' if updated != 'never' else ''}"
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
    # x labels: start, middle, now
    for t, anchor in ((x0, "start"), (x0 + datetime.timedelta(seconds=span / 2), "middle"), (x1, "end")):
        o.append(f'<text class="t2" x="{X(t):.1f}" y="{T + ph + 18}" font-size="11" text-anchor="{anchor}">'
                 f'{time_label(t, span)}</text>')
    # go/no-go and goal marks
    for val, label in ((gate, f"Go/no-go check {fmt_k(gate)}"), (goal, f"Goal {fmt_k(goal)}")):
        y = Y(val)
        o.append(f'<line class="mark" x1="{L}" x2="{L + pw}" y1="{y:.1f}" y2="{y:.1f}" stroke-width="1.5"/>')
        o.append(f'<text class="t2" x="{L + pw + 8}" y="{y + 4:.1f}" font-size="11.5">{escape(label)}</text>')
    # where each stage began: a dotted line with the stage's number (a stage from before the graph's start sits at its left)
    def badge(x, y, i):
        return (f'<circle class="num" cx="{x:.1f}" cy="{y:.1f}" r="8"/>'
                f'<text class="numt" x="{x:.1f}" y="{y + 3.8:.1f}" font-size="10.5" font-weight="600" text-anchor="middle">{i}</text>')

    last_x = None
    for i, s in enumerate(stages, 1):
        t = stage_time(s)
        if t > x1:
            continue
        x = max(X(t), L)
        if last_x is not None and x - last_x < 18:
            x = last_x + 18  # two stages close together: numbers side by side
        last_x = x
        if x > L + 0.5:
            o.append(f'<line class="stage" x1="{x:.1f}" x2="{x:.1f}" y1="{T + 18}" y2="{T + ph}" stroke-width="1.5"/>')
        o.append(badge(x, T + 9, i))
    # series (steps: the total holds until the next merge)
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
    # the stages: what the pool was given to solve, and what that data is for
    if stages:
        y = H
        o.append(f'<line class="rule" x1="{L}" x2="{W - 24}" y1="{y}" y2="{y}" stroke-width="1"/>')
        o.append(f'<text class="t1" x="{L}" y="{y + 22}" font-size="13" font-weight="600">'
                 f'What the pool solves, and what it is for</text>')
        y += 34
        for i, s in enumerate(stages, 1):
            when = stage_time(s).strftime("%b %d").replace(" 0", " ")
            o.append(badge(L - 22, y + 10, i))
            o.append(f'<text class="t1" x="{L}" y="{y + 14}" font-size="12.5"><tspan font-weight="600">'
                     f'From {when}:</tspan> {escape(s["title"])}</text>')
            o.append(f'<text class="t2" x="{L}" y="{y + 31}" font-size="12">{escape(s["for"])}</text>')
            y += STAGE_H
            if i - 1 in targets:
                have, want, rows = targets[i - 1]
                bw = 300
                o.append(f'<rect class="track" x="{L}" y="{y}" width="{bw}" height="9" rx="4.5"/>')
                if have:
                    o.append(f'<rect class="fill" x="{L}" y="{y}" width="{max(bw * min(have / want, 1), 9):.1f}" '
                             f'height="9" rx="4.5"/>')
                o.append(f'<text class="t2" x="{L + bw + 10}" y="{y + 9}" font-size="12">'
                         f'<tspan class="t1" font-weight="600">{have:,}</tspan> of {want:,} of these spots solved'
                         f'{" · target reached" if have >= want else ""}</text>')
                y += BAR_H
                # by pot type: the big trees fit few cards, so this is where a shortage shows
                tw = 150
                for label, got, need in rows:
                    o.append(f'<text class="t2" x="{L}" y="{y + 7}" font-size="11.5">{escape(label)}</text>')
                    o.append(f'<rect class="track" x="{L + 150}" y="{y}" width="{tw}" height="7" rx="3.5"/>')
                    if got:
                        o.append(f'<rect class="fill" x="{L + 150}" y="{y}" width="{max(tw * min(got / need, 1), 7):.1f}" '
                                 f'height="7" rx="3.5"/>')
                    o.append(f'<text class="t2" x="{L + 150 + tw + 10}" y="{y + 7}" font-size="11.5">'
                             f'{got:,} of {need:,}{" · enough" if got >= need else ""}</text>')
                    y += TYPE_H
                if rows:
                    y += 6
        if by_size:
            n = sum(by_size.values())
            parts = " · ".join(f"{label} {100 * by_size.get(band, 0) / n:.0f}%" for band, label in SIZE_BANDS)
            o.append(f'<text class="t2" x="{L}" y="{y + 14}" font-size="12"><tspan class="t1" font-weight="600">'
                     f'Games by GPU memory needed:</tspan> {escape(parts)} (of {n:,} that record it)</text>')
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
