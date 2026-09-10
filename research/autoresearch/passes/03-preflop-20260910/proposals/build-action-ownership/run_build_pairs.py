"""Frozen build ownership protocol runner. Calls only run_guarded, serially."""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
from compare_build_pairs import compare_plan, require
HERE=Path(__file__).resolve().parents[2]
ROOT=HERE.parents[3]
LAB=ROOT/"target/autoresearch/preflop-20260910"
HARNESS_SHA="71d629ae17f951a4d270b773a5260861c2a502228679109df9cab879e209ccb9"
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def write_new(path,obj):
    with Path(path).open("x",encoding="utf-8") as f:json.dump(obj,f,indent=2)
def main():
    p=argparse.ArgumentParser();p.add_argument("--candidate",required=True);p.add_argument("--candidate-source",required=True);p.add_argument("--id",required=True)
    p.add_argument("--small-only",action="store_true");p.add_argument("--rounds",type=int,default=5);p.add_argument("--modes",nargs="+",choices=["fresh-from-config","load"],default=["fresh-from-config","load"]);p.add_argument("--small-sanity",action="store_true");p.add_argument("--stop-before-utc",default="2026-09-10T21:34:18Z");p.add_argument("--baseline",default=str(LAB/"target/research-binaries/build-control-5cc6b3f.exe"));args=p.parse_args()
    require(1<=args.rounds<=5,"rounds must be1..5")
    require(bool(re.fullmatch(r"[A-Za-z0-9_-]+",args.id)),"unsafe run id")
    harness=LAB/"crates/solver/examples/preflop_build_research_bench.rs"
    require(sha(harness)==HARNESS_SHA,"frozen harness changed")
    manifest=json.loads((HERE/"build-binaries.json").read_text(encoding="utf-8"))
    exes={}
    for side,path in [("baseline",args.baseline),("candidate",args.candidate)]:
        path=Path(path).resolve();require(path.is_file() and path.suffix.lower()==".exe","missing executable")
        digest=sha(path);matches=[x for x in manifest if x["sha256"]==digest]
        require(len(matches)==1,"executable needs exactly one build-binaries manifest entry")
        require(matches[0].get("harness_sha256")==HARNESS_SHA,"compiled frozen harness not attested")
        if side=="candidate":require(matches[0]["source_commit"].startswith(args.candidate_source),"candidate source mismatch")
        exes[side]={"path":str(path),"sha256":digest,"source_commit":matches[0]["source_commit"]}
    large=ROOT/"saves/preflop/Before preflop autoresearch 20260910 2104.gtop";small=HERE/"fixtures/three.json"
    eq=LAB/"cache/preflop_eq169.bin";fit=LAB/"cache/realization_fit.json"
    inputs={str(x):sha(x) for x in [large,small,eq,fit]}
    target=(LAB/"target/research-build").resolve();target.mkdir(parents=True,exist_ok=True)
    output=(target/args.id).resolve();require(output.parent==target and not output.exists(),"output must be new research child")
    require(shutil.disk_usage(target).free>large.stat().st_size*(2*args.rounds*len(args.modes)+2)+1024**3,"insufficient space for retained native outputs")
    output.mkdir();pairs=[]
    cases=[] if args.small_only else [("eight-fresh" if mode=="fresh-from-config" else "eight-load",mode,large,args.rounds) for mode in args.modes]
    if args.small_sanity or args.small_only: cases.append(("three-fresh","fresh-from-config",small,args.rounds if args.small_only else 1))
    for case,mode,fixture,count in cases:
        for pair in range(1,count+1):
            order=["baseline","candidate"] if pair%2 else ["candidate","baseline"]
            row={"case":case,"mode":mode,"input":str(fixture),"pair":pair,"order":order}
            for side in order:
                runid=f"{args.id}-{case}-{pair}-{side}"
                log=HERE/"raw"/(runid+".log");require(not log.exists(),"run ID already exists")
                row[side]={"id":runid,"log":str(log),"guard_record":str(output/(runid+".guard.json")),"output":str(output/(runid+".gtop"))}
            pairs.append(row)
    plan={"version":1,"frozen_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"executables":exes,"inputs_sha256":inputs,"harness_sha256":HARNESS_SHA,"pairs":pairs,"memory_scope":"Whole process including untimed verification", "threads":16}
    planpath=output/"protocol.json";write_new(planpath,plan)
    env=os.environ.copy();env.update(PREFLOP_MEASURE_MEMORY="1",PREFLOP_VALIDATION_TIMEOUT="600",REALIZATION_FIT=str(fit),PREFLOP_TEST_CWD=str(LAB))
    deadline=datetime.datetime.fromisoformat(args.stop_before_utc.replace("Z","+00:00"))
    for pair in pairs:
        for side in pair["order"]:
            require(datetime.datetime.now(datetime.timezone.utc)<deadline,"experiment deadline reached before next run")
            env["PREFLOP_VALIDATION_TIMEOUT"]=str(max(1,min(600,int((deadline-datetime.datetime.now(datetime.timezone.utc)).total_seconds()))))
            run=pair[side];require(sha(exes[side]["path"])==exes[side]["sha256"],"binary changed")
            command=[sys.executable,str(HERE/"run_guarded.py"),run["id"],exes[side]["path"],pair["input"],pair["mode"],str(eq),str(fit),str(output),run["output"]]
            finished=subprocess.run(command,cwd=ROOT,env=env,text=True,capture_output=True)
            records=[json.loads(line) for line in finished.stdout.splitlines() if line.startswith("{")]
            require(len(records)==1,"guard did not produce one record: "+finished.stderr[-1000:])
            write_new(run["guard_record"],records[0]);require(finished.returncode==0 and records[0].get("reason") is None,"guard refused/failed run")
        # Fail closed immediately after every complete pair, before more work.
        partial={**plan,"pairs":[pair]};compare_plan(partial)
    require(all(sha(path)==digest for path,digest in inputs.items()),"input/cache changed")
    write_new(output/"comparison.json",compare_plan(plan));print(str(output/"comparison.json"))
if __name__=="__main__":main()
