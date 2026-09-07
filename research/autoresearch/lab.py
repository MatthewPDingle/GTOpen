"""Record bounded experiments and regenerate progress charts.

The coding agent proposes/edits/tests/accepts implementations. This script
owns measurement evidence, not autonomous code generation or approval.
"""
import argparse
import csv
import datetime as dt
import hashlib
import fnmatch
import html
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import psutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
from workspace import LAB, ensure_workspace
PATHS = json.loads((HERE / "paths.json").read_text())
COLORS = {"baseline":"#64748b", "candidate":"#d97706", "keep":"#0284c7", "discard":"#dc2626", "crash":"#7c3aed", "inconclusive":"#d97706"}
SCORES = {
    "postflop_cuda":["postflop.*"],
    "preflop_cuda":["preflop.*.iteration_ms", "preflop.*.check_ms"],
    "cpu_solving":["cpu.*"],
    "memory_transfers":["*sync_ms", "*vram_mb", "*init_ms", "*arena_mb"],
    "reports_profiles":["*report*", "*profile*"],
    "build_save_load":["*build_ms", "*load_ms", "*save_ms", "*save_mb"],
}

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(["git", "-C", str(LAB), *args], text=True, encoding="utf-8").strip()

def append(event):
    with (HERE / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def rows():
    found = {}
    attribution = {}
    path = HERE / "events.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines() if path.exists() else []:
        event = json.loads(line)
        if event["event"] == "run":
            found[event["id"]] = event
        elif event["event"] == "invalidate_measurements":
            row = found[event["id"]]
            row["invalid_metrics"] = row["metrics"]
            row["metrics"] = {}
            row["measurement_invalid_reason"] = event["reason"]
        elif event["event"] == "decision":
            found[event["id"]].update(status=event["status"], reason=event["reason"], decided=event["utc"])
        elif event["event"] == "source_attribution":
            attribution[event["id"]] = event
    for run_id, event in attribution.items():
        if run_id in found:
            found[run_id].update(commit=event["commit"], source_attribution_note=event["reason"])
    return list(found.values())

def parse_metrics(log):
    metrics, checks = {}, []
    for line in log.splitlines():
        # Rust's single-threaded test runner can prefix a test's first print.
        if "METRIC_JSON " in line:
            line = "METRIC_JSON " + line.split("METRIC_JSON ", 1)[1]
        if line.startswith("METRIC_JSON "):
            data = json.loads(line[12:])
            metrics.update(data.pop("metrics", {}))
            checks.append(data)
        elif line.startswith("PERF seats="):
            seat = re.search(r"seats=(\d+)", line)[1]
            for key in ["iteration_ms", "check_ms", "sync_ms"]:
                metrics[f"preflop.{seat}.{key}"] = float(re.search(key+r"=([\d.]+)", line)[1])
            checks.append({"preflop": line})
        elif line.startswith("POSTFLOP board="):
            board = re.search(r"board=(\w+)", line)[1]
            for key in ["init_ms", "iteration_ms", "check_ms"]:
                metrics[f"postflop.{board}.{key}"] = float(re.search(key+r"=([\d.]+)", line)[1])
            checks.append({"postflop": line})
        elif line.startswith("POSTFLOP_TARGET "):
            board = re.search(r"board=(\w+)", line)[1]
            metrics[f"postflop.{board}.target_seconds"] = float(re.search(r"seconds=([\d.]+)", line)[1])
            checks.append({"convergence": line})
        elif line.startswith("REPORT_ADAPT "):
            metrics["reports.adaptation_seconds"] = float(re.search(r"seconds=([\d.]+)", line)[1])
            checks.append({"report": line})
    return metrics, checks

def chart(ax, data, metric, title=None):
    selected = [(i+1, r) for i, r in enumerate(data) if metric in r["metrics"]]
    if not selected:
        ax.text(.5, .5, "Baseline pending", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(title or metric, loc="left", fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        return
    best, bx, by = None, [], []
    for x, r in selected:
        value = r["metrics"][metric]
        scored = any(fnmatch.fnmatch(metric, pattern) for pattern in
                     (r.get("score_patterns") or SCORES.get(r["path"], ["*"])))
        if r["status"] == "baseline" or (r["status"] == "keep" and scored):
            best = value if best is None else min(best, value)
        if best is not None:
            bx.append(x); by.append(best)
        color = COLORS.get(r["status"], "#64748b") if scored else "#94a3b8"
        ax.scatter(x, value, s=32, color=color, zorder=3,
                   marker="x" if r["status"] in ["discard", "crash"] else "o")
    if bx:
        ax.step(bx, by, where="post", color="#16a34a", linewidth=1.7, label="Best retained")
    ax.set_title((title + "\n" + metric) if title else metric, loc="left", fontsize=10, fontweight="bold")
    ax.set_xlabel("Run sequence (see ledger)")
    unit = "ms" if metric.endswith("_ms") else "s" if metric.endswith("seconds") else "MB" if metric.endswith("_mb") else "value"
    ax.set_ylabel(unit + " · lower is better")
    ax.grid(axis="y", alpha=.18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(.5, max(1, len(data)) + .5)
    if len(data) <= 15:
        ax.set_xticks(range(1, len(data) + 1))
    else:
        ax.xaxis.get_major_locator().set_params(integer=True)
    ax.margins(x=.08, y=.18)

def render():
    data = rows()
    (HERE / "results.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    with (HERE / "results.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["experiment", "path", "commit", "status", "metric", "value", "hypothesis", "utc"])
        for r in data:
            for metric, value in r["metrics"].items():
                w.writerow([r["id"], r["path"], r["commit"], r["status"], metric, value, r["hypothesis"], r["utc"]])
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":9, "axes.edgecolor":"#cbd5e1"})
    fig, axes = plt.subplots(3, 2, figsize=(13, 10), constrained_layout=True)
    for p, ax in zip(PATHS, axes.flat):
        chart(ax, data, p["primary"], p["name"])
    fig.suptitle("GTOpen autoresearch · progress by research path", fontsize=17, fontweight="bold")
    from matplotlib.lines import Line2D
    fig.legend(handles=[
        Line2D([], [], color="#64748b", marker="o", linestyle="None", label="Baseline / control"),
        Line2D([], [], color="#0284c7", marker="o", linestyle="None", label="Retained"),
        Line2D([], [], color="#d97706", marker="o", linestyle="None", label="Candidate"),
        Line2D([], [], color="#dc2626", marker="x", linestyle="None", label="Rejected"),
        Line2D([], [], color="#16a34a", label="Best observed retained")
    ], loc="lower center", bbox_to_anchor=(.5, -.055), ncol=5, frameon=False)
    fig.savefig(HERE / "progress.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    config = json.loads((HERE / "run.json").read_text(encoding="utf-8"))
    pass_metrics = [
        ("preflop.6.iteration_ms", "Preflop CUDA - six seats"),
        ("preflop.8.iteration_ms", "Preflop CUDA - eight seats"),
        ("postflop.Ks7h2d.iteration_ms", "Postflop CUDA - rainbow flop"),
        ("postflop.Ks7s2d.iteration_ms", "Postflop CUDA - two-tone flop"),
        ("postflop.memory.cold.compressed.allocated_vram_mb", "Default compressed solve - GPU memory"),
        ("postflop.memory.warm.compressed.sync_ms", "Default compressed resume - full download"),
        ("preflop.6.allocated_vram_mb", "Preflop six seats - GPU memory"),
        ("preflop.8.allocated_vram_mb", "Preflop eight seats - GPU memory"),
    ]
    first = next((i + 1 for i, row in enumerate(data)
                  if row["utc"] >= config.get("pass_started_utc", config["started_utc"])), 1)
    fig, axes = plt.subplots(4, 2, figsize=(13, 13), constrained_layout=True)
    for ax, (metric, title) in zip(axes.flat, pass_metrics):
        chart(ax, data, metric, title)
        ax.set_xlim(first - .5, max(first, len(data)) + .5)
        visible = [row["metrics"][metric] for row in data[first - 1:] if metric in row["metrics"]]
        eligible = [row["metrics"][metric] for row in data if metric in row["metrics"]
                    and (row["status"] == "baseline" or (row["status"] == "keep" and any(
                        fnmatch.fnmatch(metric, pattern) for pattern in
                        (row.get("score_patterns") or SCORES.get(row["path"], ["*"])))))]
        if visible:
            low = min(visible + ([min(eligible)] if eligible else []))
            high = max(visible)
            pad = max((high - low) * .12, abs(high) * .015, .001)
            ax.set_ylim(max(0, low - pad), high + pad)
    fig.suptitle("GTOpen GPU research pass 2 - measured progress", fontsize=17, fontweight="bold")
    fig.legend(handles=[
        Line2D([], [], color="#64748b", marker="o", linestyle="None", label="Control / other target"),
        Line2D([], [], color="#0284c7", marker="o", linestyle="None", label="Retained target"),
        Line2D([], [], color="#d97706", marker="o", linestyle="None", label="Candidate / inconclusive"),
        Line2D([], [], color="#dc2626", marker="x", linestyle="None", label="Rejected"),
        Line2D([], [], color="#16a34a", label="Best eligible observation")
    ], loc="lower center", bbox_to_anchor=(.5, -.055), ncol=3, frameon=False)
    fig.savefig(HERE / "gpu-pass-progress.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    graph_dir = HERE / "graphs"
    graph_dir.mkdir(exist_ok=True)
    metrics = sorted({m for r in data for m in r["metrics"]})
    for metric in metrics:
        fig, ax = plt.subplots(figsize=(6.6, 3.4), constrained_layout=True)
        chart(ax, data, metric)
        fig.savefig(graph_dir / (metric + ".svg"))
        plt.close(fig)
    cards = []
    for p in PATHS:
        relevant = [r for r in data if r["path"] == p["id"] or r["path"] == "baseline"]
        ms = sorted({m for r in relevant for m in r["metrics"] if not m.startswith("monitor.")})
        if p["id"] == "postflop_cuda": ms = [m for m in ms if m.startswith("postflop.")]
        if p["id"] == "preflop_cuda": ms = [m for m in ms if m.startswith("preflop.") and not m.endswith("sync_ms")]
        if p["id"] == "cpu_solving": ms = [m for m in ms if m.startswith("cpu.")]
        if p["id"] == "memory_transfers": ms = [m for m in ms if m.endswith("sync_ms") or "memory" in m or "arena_mb" in m or "vram_mb" in m]
        if p["id"] == "reports_profiles": ms = [m for m in ms if "report" in m or "profile" in m or "raking" in m]
        if p["id"] == "build_save_load": ms = [m for m in ms if any(s in m for s in ["build_ms", "save_ms", "load_ms", "save_mb"])]
        metric_cards = []
        for m in ms:
            measurements = []
            for sequence, r in enumerate(data, 1):
                if m not in r["metrics"]:
                    continue
                targeted = any(fnmatch.fnmatch(m, pattern) for pattern in
                               (r.get("score_patterns") or SCORES.get(r["path"], ["*"])))
                role = "baseline / control" if r["status"] == "baseline" else "targeted" if targeted else "measured alongside another target"
                measurements.append(f'<tr><td>{sequence}</td><td>{r["id"]}</td><td>{r["metrics"][m]:.6g}</td><td>{r["status"]}</td><td>{role}</td></tr>')
            metric_cards.append(f'<div><img loading="lazy" src="graphs/{m}.svg" alt="{html.escape(m)}">'
                                f'<details><summary>Identify the {len(measurements)} measurements</summary><table><tr><th>Run</th><th>ID</th><th>Value</th><th>Decision</th><th>Role</th></tr>'
                                + ''.join(measurements) + '</table></details></div>')
        imgs = ''.join(metric_cards)
        cards.append(f'<section id="{p["id"]}"><h2>{html.escape(p["name"])}</h2><div class="plots">{imgs or "Baseline pending"}</div></section>')
    table = "".join(f'<tr><td>{i+1}</td><td>{r["id"]}</td><td>{r["path"]}</td><td>{r["status"]}</td><td>{html.escape(r["hypothesis"])}</td><td>{html.escape(r.get("reason", ""))}</td><td><a href="raw/{r["id"]}.log">log</a></td></tr>' for i, r in enumerate(data))
    (HERE / "index.html").write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GTOpen autoresearch</title><style>body{font:15px system-ui,sans-serif;color:#172033;background:#f5f7fb;margin:0 auto;max-width:1350px;padding:28px}h1{font-size:30px}h2{font-size:22px}section{background:white;padding:20px;margin:22px 0;border-radius:10px}.plots{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:10px}img{width:100%}a{color:#0369a1}table{width:100%;border-collapse:collapse;background:white}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}nav a{margin-right:16px}@media(max-width:600px){.plots{grid-template-columns:1fr}body{padding:12px}}</style><h1>GTOpen autoresearch</h1><p>Each dot is a measured experiment. Blue: retained. Red cross: rejected. Amber: candidate or inconclusive. Green line: best retained value. Accuracy checks are mandatory.</p>'''
        + '<section><h2>How to read the charts</h2><p><span style="color:#64748b">● Gray</span>: baseline or control measurement. <span style="color:#d97706">● Amber</span>: candidate being evaluated or inconclusive. <span style="color:#0284c7">● Blue</span>: retained change targeting this metric. <span style="color:#dc2626">× Red</span>: rejected trial. <span style="color:#7c3aed">× Purple</span>: failed run, if it produced a measurement. <span style="color:#16a34a">━ Green</span>: best observed baseline or retained improvement.</p><p>The horizontal axis is one global run sequence across all research paths, including baselines and repeats. A chart gets a point only when that run measured its metric; gaps are expected. Failed runs without measurements appear only in the ledger. The ledger maps each sequence number to its experiment ID. Lower values are better; timing noise means a small movement alone is not evidence of an improvement.</p><p><strong>Why several gray dots?</strong> Controls and baselines are repeated to check timing drift; a broader workload can also collect a metric that the current experiment is not targeting. Controls may use the original code or the retained code immediately before a new trial; their purpose is recorded in the ledger. <strong>Why a blue dot above green?</strong> Blue means retained code, not necessarily a new record in that metric. A repeat may be slower through normal noise, or a change may be kept for a larger benefit elsewhere. Green shows the best observed value so far, not an average or a guaranteed typical speed.</p></section>'
        + '<nav>' + ''.join(f'<a href="#{p["id"]}">{p["name"]}</a>' for p in PATHS) + '</nav>'
        + f'<p>Updated {now()} · Pass status: {html.escape(config.get("status", "active"))} · <a href="gpu-pass.md">GPU pass 2</a> · <a href="report.md">Pass 1 report</a> · <a href="results.tsv">Results TSV</a> · <a href="program.md">Research protocol</a></p>'
        + '<section><h2>GPU research pass 2</h2><p>Zoomed to this pass, retaining the global ledger sequence numbers. Every metric still has its full history below.</p><img src="gpu-pass-progress.png" alt="GPU research pass progress"></section>'
        + ''.join(cards) + '<h2>Experiment ledger</h2><table><tr><th>Sequence</th><th>ID</th><th>Path</th><th>Decision</th><th>Hypothesis</th><th>Reason</th><th>Evidence</th></tr>' + table + '</table></html>', encoding="utf-8")

def refresh_build_inputs():
    # A copied proposal or restored source can have an mtime older than the
    # last rustc invocation. Cargo's mtime fast path can then reuse stale code.
    # Track contents and refresh only changed compiler inputs before cargo.
    receipt = LAB / "target/autoresearch-input-hashes.json"
    previous = json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() else {}
    inputs = [LAB / "Cargo.toml", LAB / "Cargo.lock", LAB / "bench_spot.json"]
    for crate in (LAB / "crates").iterdir():
        if not crate.is_dir():
            continue
        inputs.append(crate / "Cargo.toml")
        for sub in ["src", "tests", "examples"]:
            folder = crate / sub
            if folder.exists():
                inputs.extend(p for p in folder.rglob("*") if p.is_file() and p.suffix in [".rs", ".cu"])
    current, touched = {}, []
    for path in inputs:
        if not path.exists():
            continue
        name = path.relative_to(LAB).as_posix()
        current[name] = sha(path)
        if previous.get(name) != current[name]:
            path.touch()
            touched.append(name)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(current, indent=2), encoding="utf-8")
    if touched:
        append(dict(event="refresh_compiler_inputs", utc=now(), files=touched,
                    reason="Content changes must invalidate Cargo even after copies preserving old mtimes"))

def run(args):
    config = json.loads((HERE / "run.json").read_text())
    for name, expected in config["harness"].items():
        if sha(LAB / name) != expected:
            raise SystemExit(f"Frozen harness changed: {name}")
    if args.id in {r["id"] for r in rows()}:
        raise SystemExit("Experiment id already recorded")
    if any(Path(part).name.lower() in ["cargo", "cargo.exe"] for part in args.command[:2]):
        refresh_build_inputs()
    env = os.environ.copy()
    env["PATH"] = str(ROOT / ".cuda-nvrtc/nvidia/cuda_nvrtc/bin") + os.pathsep + env["PATH"]
    threads = str(min(16, psutil.cpu_count(logical=False) or os.cpu_count() or 1))
    env.setdefault("RAYON_NUM_THREADS", threads)
    env.setdefault("SOLVER_THREADS", threads)
    for assignment in args.env:
        k, v = assignment.split("=", 1); env[k] = v
    for sub in ["raw", "patches"]: (HERE / sub).mkdir(exist_ok=True)
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if command and not Path(command[0]).is_absolute() and (LAB / command[0]).is_file():
        command[0] = str((LAB / command[0]).resolve())
    log_path = HERE / "raw" / (args.id + ".log")
    commit = git("rev-parse", "HEAD")
    (HERE / "patches" / (args.id + ".patch")).write_text(
        git("show", "--format=fuller", "--binary", "HEAD"), encoding="utf-8")
    started = time.monotonic()
    peak_rss = 0
    with log_path.open("w", encoding="utf-8") as out:
        try:
            proc = subprocess.Popen(command, cwd=LAB, env=env, stdout=out, stderr=subprocess.STDOUT)
        except OSError as exc:
            out.write(f"Failed to launch benchmark: {exc}\n")
            proc = None
        while proc is not None and proc.poll() is None:
            try:
                parent = psutil.Process(proc.pid)
                infos = [p.memory_info() for p in [parent, *parent.children(recursive=True)] if p.is_running()]
                rss = sum(getattr(info, "peak_wset", info.rss) if args.rss_metric else info.rss for info in infos)
                peak_rss = max(peak_rss, rss)
            except (psutil.NoSuchProcess, psutil.AccessDenied): pass
            if time.monotonic() - started > args.timeout:
                try:
                    for child in psutil.Process(proc.pid).children(recursive=True): child.kill()
                except psutil.NoSuchProcess: pass
                proc.kill(); proc.wait()
                break
            time.sleep(.05 if args.rss_metric else .25)
    log = log_path.read_text(encoding="utf-8", errors="replace")
    returncode = proc.returncode if proc is not None else 127
    metrics, checks = parse_metrics(log)
    # Compiler-inclusive RSS is diagnostic only; not an optimization score.
    event = dict(event="run", id=args.id, path=args.path, hypothesis=args.hypothesis,
                 status="crash" if returncode else args.status, utc=now(), commit=commit,
                 seconds=round(time.monotonic()-started,3), diagnostic_peak_process_mb=round(peak_rss/1e6,3),
                 returncode=returncode, command=command, env=args.env, metrics=metrics, checks=checks)
    event["score_patterns"] = args.score
    if args.rss_metric and not returncode and peak_rss:
        if command[0].lower().endswith(("cargo", "cargo.exe")):
            raise SystemExit("RSS scoring requires a prebuilt benchmark executable, not cargo")
        event["metrics"][args.rss_metric] = round(peak_rss/1e6, 3)
    append(event); render()
    print(json.dumps(event, ensure_ascii=False))
    if returncode: print("\n".join(log.splitlines()[-35:]))

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("run")
    p.add_argument("--id", required=True); p.add_argument("--path", required=True)
    p.add_argument("--hypothesis", required=True); p.add_argument("--status", default="candidate")
    p.add_argument("--timeout", type=int, default=600); p.add_argument("--env", action="append", default=[])
    p.add_argument("--score", action="append", default=[])
    p.add_argument("--rss-metric")
    p.add_argument("command", nargs=argparse.REMAINDER)
    p = sub.add_parser("decide")
    p.add_argument("id"); p.add_argument("status", choices=["keep","discard","inconclusive","crash"])
    p.add_argument("reason")
    p.add_argument("--also", action="append", default=[])
    p = sub.add_parser("promote")
    p.add_argument("files", nargs="+")
    sub.add_parser("render")
    args = parser.parse_args()
    if args.action == "run": run(args)
    elif args.action == "decide":
        ids = [args.id, *args.also]
        if not set(ids).issubset({r["id"] for r in rows()}): raise SystemExit("Unknown experiment")
        for experiment_id in ids:
            append(dict(event="decision", id=experiment_id, status=args.status, reason=args.reason, utc=now()))
        render()
    elif args.action == "promote":
        config = json.loads((HERE / "run.json").read_text())
        for name in args.files:
            if name not in config["main_source_hashes"]:
                raise SystemExit(f"Unregistered promotion target: {name}")
            current = sha(ROOT / name) if (ROOT / name).exists() else None
            if current != config["main_source_hashes"][name]:
                raise SystemExit(f"Main checkout changed externally: {name}")
        for name in args.files:
            (ROOT / name).write_bytes((LAB / name).read_bytes())
            config["main_source_hashes"][name] = sha(ROOT / name)
        (HERE / "run.json").write_text(json.dumps(config, indent=2))
        append(dict(event="promote", files=args.files, commit=git("rev-parse", "HEAD"), utc=now()))
        print("Promoted validated files: " + ", ".join(args.files))
    else: render()

if __name__ == "__main__":
    ensure_workspace()
    main()
