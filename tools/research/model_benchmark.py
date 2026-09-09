"""Public, aggregate-only contextual preflop regression/performance benchmark.

Run from any directory: python tools/research/model_benchmark.py
Uses a standalone Rust process, never the user's running server or saved games.
Prediction quality is imported frozen RETROSPECTIVE evidence, not recomputed on
the artifact that was subsequently fitted to all available data.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("RAYON_NUM_THREADS", "4")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/ignition-reraise"
OUT = ROOT / "research/preflop-evolution/benchmarks"


def config(players=6, stack=100, sb=.5, ante=0):
    positions = {3:["BTN","SB","BB"], 4:["CO","BTN","SB","BB"],
        5:["HJ","CO","BTN","SB","BB"], 6:["UTG","HJ","CO","BTN","SB","BB"],
        8:["UTG","UTG1","MP","HJ","CO","BTN","SB","BB"]}[players]
    return dict(positions=positions, stack=stack, posts=[0.]*(players-2)+[sb,1.],
        ante=ante, limp=False, open_raises=[2.5], raise_mults=[3.], max_raises=3,
        add_allin=False, allin_threshold=.85, rake_pct=5., rake_cap=3.,
        no_flop_no_drop=True, realization="raw", call_only_seats=[])


def role(cfg, seat):
    n=len(cfg["positions"])
    return -2 if seat==n-1 else -1 if seat==n-2 else n-3-seat


def load_training_module():
    spec=importlib.util.spec_from_file_location("contextual_training", ROOT / "tools/ignition/contextual_reraise.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def policy(p):
    return dict(call=p[:,1].tolist(), raise_sizes=[], raise_size="max",
        **{"raise":p[:,2].tolist(), "jam":[0.]*169})


def fixtures(model, module):
    models={bucket:{(row["players"],row["role"]):np.array(row["probabilities"])
        for row in rows} for bucket,rows in model["baseline"].items()}
    traces=[]
    # Whole-range fixtures, not a selection of visually pleasing hands.
    for players in [3,4,5,6]:
        cfg=config(players)
        cfg["limp"]=True
        for entry in ["cold","called","raised"]:
            for raises,to in [(2,7.5),(3,22.5)]:
                if players==3 and entry=="cold" and raises==3:continue
                if entry=="cold": seat=players-1;invested=1.;pot=11. if raises==2 else 33.5
                elif entry=="raised": seat=0;invested=2.5;pot=11. if raises==2 else 32.5
                elif players==3: seat=0;invested=1. if raises==2 else 7.5;pot=11. if raises==2 else 37.5
                else: seat=players-3;invested=2.5;pot=13.5 if raises==2 else 35.
                inp=dict(entry=entry,raises=raises,to_call=to,pot=pot,invested=invested)
                traces.append(dict(name=f"{players}p {entry} vs {raises+1}-bet",cfg=cfg,seat=seat,input=inp,supported=True))
    # A large multiway pot, blind credits, and a short remaining stack.
    traces += [
        dict(name="6p raised low price",cfg=config(),seat=1,input=dict(entry="raised",raises=2,to_call=7.5,pot=30.,invested=2.5),supported=True),
        dict(name="6p BB cold",cfg=config(),seat=5,input=dict(entry="cold",raises=2,to_call=7.5,pot=11.5,invested=1.),supported=True),
        dict(name="6p short remaining",cfg=config(stack=30),seat=1,input=dict(entry="raised",raises=3,to_call=30.,pot=75.,invested=25.),supported=True),
    ]
    for name,cfg in [("8p 2/2 guard",config(8,150,1.)),("8p 2/5 guard",config(8,200,.4)),
        ("6p equal blinds guard",config(sb=1.)),("6p ante guard",config(ante=.1))]:
        traces.append(dict(name=name,cfg=cfg,seat=1,input=dict(entry="raised",raises=2,to_call=7.5,pot=14.,invested=2.5),supported=False))
    for t in traces:
        n=len(t["cfg"]["positions"]);r=role(t["cfg"],t["seat"])
        bucket="cold_reraise" if t["input"]["entry"]=="cold" else "reraise"
        base=models[bucket][module.sm.closest(models[bucket],(n,r))]
        t["baseline"]=policy(base)
    p=policy(models["reraise"][(6,2)])
    games=[dict(name="6p compact source",cfg=config(),policy=p),
        dict(name="8p compact 2/2",cfg=config(8,150,1.),policy=p),
        dict(name="8p compact 2/5",cfg=config(8,200,.4),policy=p)]
    return traces,games,models


def expected(t, models, artifact, module):
    cfg=t["cfg"];inp=t["input"]
    paid=min(inp["to_call"]-inp["invested"],cfg["stack"]-inp["invested"])
    price=paid/(inp["pot"]+paid)
    entry=["cold","called","raised"].index(inp["entry"])
    rows=np.array([[len(cfg["positions"]),role(cfg,t["seat"]),entry,int(inp["raises"]>=3),
        price,inp["invested"],cfg["stack"]-inp["invested"],h] for h in range(169)])
    x,names=module.features(rows,artifact["selected"]["family"])
    assert names==artifact["features"]
    return module.predict(x,module.base_probs(models,rows),np.array(artifact["weights"])),price


def compare(native,traces,models,artifact,module):
    results=[]
    for t,result in zip(traces,native["traces"],strict=True):
        assert t["name"]==result["name"]
        if not t["supported"]:
            assert result["probabilities"] is None, f"{t['name']}: unsupported context used model"
            results.append(dict(name=t["name"],fallback=True))
            continue
        py,price=expected(t,models,artifact,module)
        rust=np.array(result["probabilities"])
        error=float(np.max(np.abs(py-rust)))
        assert error<2e-6, f"{t['name']}: Python/Rust probability error {error}"
        assert abs(price-result["nominal_price"])<1e-12
        assert np.all(np.isfinite(rust)) and np.min(rust)>-1e-6
        assert np.max(np.abs(rust.sum(1)-1))<2e-6
        results.append(dict(name=t["name"],fallback=False,max_absolute_error=error,hands=169))
    for name in dict.fromkeys(x["name"] for x in native["games"]):
        pair=[x for x in native["games"] if x["name"]==name]
        assert len(pair)==2 and pair[0]["queried_nodes"]==pair[1]["queried_nodes"]==24
        assert pair[0]["nodes"]==pair[1]["nodes"] and pair[0]["arena_mb"]==pair[1]["arena_mb"]
        equal=pair[0]["strategy_fingerprint"]==pair[1]["strategy_fingerprint"]
        assert equal==name.startswith("8p"), f"{name}: supported change / unsupported fallback mismatch"
    return results


def graph_pair(path,title,ylabel,labels,baseline,candidate,log=False,legend=("Existing fixed policy","Contextual candidate")):
    fig,ax=plt.subplots(figsize=(max(7,len(labels)*1.25),3.6),layout="constrained")
    x=np.arange(len(labels));ax.bar(x-.18,baseline,.36,label=legend[0],color="#86909a")
    ax.bar(x+.18,candidate,.36,label=legend[1],color="#54ae76")
    ax.set_xticks(x,labels,rotation=15,ha="right");ax.set_ylabel(ylabel);ax.set_title(title)
    if log:ax.set_yscale("log")
    ax.legend(frameon=False);ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
    fig.savefig(path,dpi=150);plt.close(fig)


def charts(out,result):
    evidence=result["retrospective"]["metrics"]
    groups=["all","cold","after_entry","called/3bet","raised/3bet","raised/4betplus"]
    graph_pair(out/"prediction-loss.png","Prediction loss: frozen retrospective evaluation (lower is better)","Mean negative log probability",
        groups,[evidence[k]["baseline_loss"] for k in groups],[evidence[k]["candidate_loss"] for k in groups])
    traces=[x for x in result["native"]["traces"] if x["probabilities"] is not None]
    selected=[x for x in traces if x["name"].startswith("6p")]
    graph_pair(out/"compiled-inference.png","Same frozen model: paired dense vs compiled inference","Microseconds / 169-hand range",
        [x["name"] for x in selected],[x["dense_reference_us"]["median"] for x in selected],
        [x["contextual_predict_us"]["median"] for x in selected],legend=("Original dense inference","Compiled inference"))
    memory=result["native"]["model_memory"]
    graph_pair(out/"compiled-model-memory.png","Frozen model resident numeric payload","KiB (excludes headers/allocator overhead)",
        ["Model arrays"],[memory["baseline_numeric_bytes"]/1024],[memory["compiled_numeric_bytes"]/1024],
        legend=("Original dense inference","Compiled inference"))
    starts=result["cold_start"]
    graph_pair(out/"model-cold-start.png","First prediction in a fresh process (includes parse/compile)","Microseconds",
        ["One-time initialization + first range"],[np.median(starts["dense"])],[np.median(starts["compiled"])],
        legend=("Original dense inference","Compiled inference"))
    graph_pair(out/"inference-latency.png","Materialize all 169 hands: fixed clone vs contextual inference","Microseconds / range (log scale)",
        [x["name"] for x in selected],[x["fixed_policy_clone_us"]["median"] for x in selected],
        [x["contextual_predict_us"]["median"] for x in selected],log=True)
    games=result["native"]["games"];names=list(dict.fromkeys(x["name"] for x in games))
    for key,title,label in [("build_us","Compact tree construction","Milliseconds"),
        ("install_profiles_us","Install complete table profiles","Milliseconds"),
        ("first_query_batch_us","First 24 re-raise-node queries","Milliseconds / batch"),
        ("cached_query_batch_us","Repeat 24 re-raise-node queries","Milliseconds / batch"),
        ("materialize_all_policies_us","Materialize every policy in compact tree (after 24 query warmup)","Milliseconds / pass"),
        ("cached_all_policies_us","Repeat every policy in compact tree","Milliseconds / pass")]:
        graph_pair(out/f"{key}.png",title,label,names,
            [next(x[key]["median"]/1000 for x in games if x["name"]==name and not x["contextual"]) for name in names],
            [next(x[key]["median"]/1000 for x in games if x["name"]==name and x["contextual"]) for name in names])
    graph_pair(out/"arena-memory.png","Solver arena allocation (excludes node/profile/cache overhead)","Decimal MB",names,
        [next(x["arena_mb"] for x in games if x["name"]==name and not x["contextual"]) for name in names],
        [next(x["arena_mb"] for x in games if x["name"]==name and x["contextual"]) for name in names])
    graph_pair(out/"context-cache-memory.png","Context cache: vector payload after whole compact-tree pass","KiB (excludes allocation/map overhead)",names,
        [next(x["contextual_cache_vector_bytes"]/1024 for x in games if x["name"]==name and not x["contextual"]) for name in names],
        [next(x["contextual_cache_vector_bytes"]/1024 for x in games if x["name"]==name and x["contextual"]) for name in names])
    fig,ax=plt.subplots(figsize=(9,3.1),layout="constrained")
    parity=[x for x in result["parity"] if not x["fallback"]]
    ax.plot(range(1,len(parity)+1),[x["max_absolute_error"] for x in parity],"o",color="#54ae76")
    ax.axhline(2e-6,color="#b45561",ls="--",label="Acceptance tolerance")
    ax.set(title="Python / Rust parity across full 169-hand ranges",xlabel="Fixture number",ylabel="Maximum absolute probability error")
    ax.legend(frameon=False);fig.savefig(out/"parity.png",dpi=150);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(__doc__);parser.add_argument("--out",type=Path,default=OUT)
    parser.add_argument("--repeats",type=int,default=200);parser.add_argument("--no-build",action="store_true")
    parser.add_argument("--target-dir",type=Path,default=ROOT/"target")
    args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    artifact=json.loads((SOURCE/"candidate.json").read_text());evidence=json.loads((SOURCE/"experiment.json").read_text())
    module=load_training_module();traces,games,models=fixtures(artifact,module)
    request=dict(traces=traces,games=games,repeats=args.repeats)
    if not args.no_build:
        subprocess.run(["cargo","build","--release","-p","solver","--example","contextual_benchmark","--target-dir",str(args.target_dir)],cwd=ROOT,check=True)
    binary=args.target_dir/"release/examples"/("contextual_benchmark.exe" if os.name=="nt" else "contextual_benchmark")
    start=time.perf_counter()
    run=subprocess.run([str(binary)],input=json.dumps(request),text=True,capture_output=True,cwd=ROOT,check=True)
    native=json.loads(run.stdout)
    cold_start={"dense":[],"compiled":[]}
    for repeat in range(5):
        for method in (["dense","compiled"] if repeat%2==0 else ["compiled","dense"]):
            cold=subprocess.run([str(binary)],input=json.dumps(dict(request,cold_start_only=method)),text=True,capture_output=True,cwd=ROOT,check=True)
            cold_start[method].append(json.loads(cold.stdout)["first_prediction_us"])
    result=dict(schema=1,created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        working_tree_changes=bool(subprocess.check_output(["git","diff","--name-only"],cwd=ROOT,text=True).strip()),
        source_sha256={str(p.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__),ROOT/"crates/solver/examples/contextual_benchmark.rs",
                ROOT/"crates/solver/src/preflop/contextual.rs",ROOT/"crates/solver/src/preflop/mod.rs",
                ROOT/"tools/ignition/contextual_reraise.py"]},
        executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),reused_binary=args.no_build,
        model_sha256=hashlib.sha256((SOURCE/"candidate.json").read_bytes()).hexdigest(),
        model_file_bytes=(SOURCE/"candidate.json").stat().st_size,
        machine=dict(os=platform.platform(),processor=platform.processor(),rayon_threads=os.environ["RAYON_NUM_THREADS"]),
        duration_seconds=time.perf_counter()-start,cold_start=cold_start,retrospective=dict(source="research/ignition-reraise/experiment.json",
            note="Imported frozen chronological experiment; all periods previously inspected. Artifact was subsequently refit on all data. No fresh validation or EV claim.",
            metrics=evidence["metrics"]),native=native,parity=compare(native,traces,models,artifact,module))
    (out/"fixtures.json").write_text(json.dumps(request,indent=2)+"\n",encoding="utf-8",newline="\n")
    (out/"latest.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    history_path=out/"history.json"
    history=json.loads(history_path.read_text()) if history_path.exists() else []
    summary={k:v for k,v in result.items() if k not in ["native","retrospective"]}
    summary["native"]={"games":native["games"],"model_memory":native["model_memory"],"traces":[{k:v for k,v in x.items() if k!="probabilities"} for x in native["traces"]]}
    history.append(summary);history_path.write_text(json.dumps(history,indent=2)+"\n",encoding="utf-8",newline="\n")
    charts(out,result)
    imgs=["compiled-inference.png","compiled-model-memory.png","model-cold-start.png","prediction-loss.png","inference-latency.png","build_us.png","install_profiles_us.png","first_query_batch_us.png","cached_query_batch_us.png","materialize_all_policies_us.png","cached_all_policies_us.png","arena-memory.png","context-cache-memory.png","parity.png"]
    (out/"index.html").write_text('<!doctype html><meta charset="utf-8"><title>GTOpen model benchmarks</title><style>body{font:15px system-ui;max-width:1150px;margin:30px auto;background:#181b1f;color:#eceef0}img{width:100%;background:white;border-radius:8px;margin:10px 0 22px}p{line-height:1.5}a{color:#74c291}</style><h1>Contextual preflop model benchmarks</h1><p>First baseline/candidate measurements. These charts compare two implementations; they do not invent a historical improvement trend. Each run is retained in history.json.</p><p>Prediction quality is retrospective, previously inspected data. Timing fixtures use compact menus and synthetic aggregate profiles; they are not full saved scenarios or solving-speed/EV claims. Unsupported blind/table conditions retain the existing policy. Model bytes: '+str(result["model_file_bytes"])+'.</p>'+''.join('<img src="'+x+'" alt="'+x+'">' for x in imgs),encoding="utf-8")
    print(json.dumps(dict(output=str(out),parity_ranges=sum(not x["fallback"] for x in result["parity"]),fallback_guards=sum(x["fallback"] for x in result["parity"]),duration_seconds=result["duration_seconds"]),indent=2))


if __name__=="__main__":main()
