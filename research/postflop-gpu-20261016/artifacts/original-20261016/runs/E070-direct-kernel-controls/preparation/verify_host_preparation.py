"""Parse staged Rust and execute only the exact host integer pack expression."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import time

HERE = Path(__file__).resolve().parent
STAGE = HERE / "host-integration-r2"
SOURCE = STAGE / "candidate/crates/solver/src/gpu"
OUT = STAGE / "syntax-and-integer-checks"
OUT.mkdir(exist_ok=False)
TMP = OUT / "compiler-tmp"
TMP.mkdir()
env = os.environ.copy()
env["TMP"] = env["TEMP"] = str(TMP)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def child(command, label):
    process = None
    error = None
    started = datetime.now(timezone.utc).isoformat()
    try:
        with (OUT / (label+".stdout.log")).open("xb") as stdout, (OUT / (label+".stderr.log")).open("xb") as stderr:
            process = subprocess.Popen(command, cwd=OUT, env=env, stdout=stdout, stderr=stderr,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                process.wait(timeout=120)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=30)
                raise
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        receipt = {"command": command, "started": started, "finished": datetime.now(timezone.utc).isoformat(),
                   "pid": process.pid if process else None, "returncode": process.returncode if process else None,
                   "error": error, "terminal": process is not None and process.poll() is not None,
                   "GPUexecutions": 0}
        with (OUT / (label+".receipt.json")).open("x", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)
    assert process.returncode == 0, (OUT / (label+".stderr.log")).read_text(encoding="utf-8", errors="replace")[-2500:]
    return receipt


manifest = json.loads((STAGE / "manifest.json").read_text(encoding="utf-8"))
for p, expected in manifest["candidate_source_sha256"].items():
    assert sha(STAGE / "candidate" / p) == expected
receipts = []
for filename in ["mod.rs", "continuation.rs", "continuation_storage.rs", "continuation_capacity.rs"]:
    receipts.append(child(["rustfmt", "--emit", "stdout", "--edition", "2021",
                           "--config", "skip_children=true", str(SOURCE/filename)], "parse-"+filename[:-3]))
tree = Path(r"X:\Dev\GTOpen-gpu-research-20261016/crates/solver/src/tree.rs").read_text(encoding="utf-8")
assert re.search(r"pub player:\s*u8", tree) and re.search(r"pub num_children:\s*u8", tree)
source = (SOURCE / "mod.rs").read_text(encoding="utf-8")
match = re.search(r"let node_attrs: Vec<u16> = solver\.spot\.tree\.nodes\.iter\(\)[\s\S]*?\.collect\(\);", source)
assert match
expression = match.group()
probe = '''struct Node {player:u8,num_children:u8}
struct Tree {nodes:Vec<Node>}
struct Spot {tree:Tree}
struct Solver {spot:Spot}
fn main(){
 let nodes:Vec<Node>=(0u16..=255).flat_map(|p|(0u16..=255).map(move |a|Node{player:p as u8,num_children:a as u8})).collect();
 let solver=Solver{spot:Spot{tree:Tree{nodes}}};
 '''+expression+'''
 assert_eq!(node_attrs.len(),65536);
 for (index,&packed) in node_attrs.iter().enumerate(){
  let original=&solver.spot.tree.nodes[index];
  assert_eq!(packed as usize,index);
  assert_eq!((packed>>8) as u8,original.player);
  assert_eq!((packed&255) as u8,original.num_children);
 }
 println!("E070_HOST_PACK_EXHAUSTIVE_PASS cases=65536 bytes={}",node_attrs.len()*std::mem::size_of::<u16>());
}
'''
(OUT / "host-pack.rs").write_text(probe, encoding="utf-8", newline="\n")
receipts.append(child(["rustc", str(OUT/"host-pack.rs"), "--edition=2021", "-C", "opt-level=3",
                       "-o", str(OUT/"host-pack.exe")], "host-pack-rustc"))
receipts.append(child([str(OUT/"host-pack.exe")], "host-pack-cpu"))
stdout = (OUT / "host-pack-cpu.stdout.log").read_text(encoding="utf-8").strip()
assert stdout == "E070_HOST_PACK_EXHAUSTIVE_PASS cases=65536 bytes=131072"
for p, expected in manifest["candidate_source_sha256"].items():
    assert sha(STAGE / "candidate" / p) == expected
report = {"id": "E070-host-syntax-and-integer-pack", "status": "pass_scoped_Rust_syntax_and_exhaustive_host_pack",
          "Rust_files_parsed": 4, "original_u8_pair_cases": 65536,
          "exact_candidate_pack_expression": expression,
          "candidate_mod_sha256": sha(SOURCE / "mod.rs"), "probe_sha256": sha(OUT / "host-pack.rs"),
          "probe_binary_sha256": sha(OUT / "host-pack.exe"), "stdout": stdout,
          "processes": receipts, "all_owned_handles_terminal": all(r["terminal"] for r in receipts),
          "integrated_typecheck": False, "NVRTC_processes": 0, "GPUexecutions": 0,
          "candidate_sources_unchanged": True, "candidate_accepted": False,
          "limits": "Syntax and integer representation checks only; no integrated Rust type/link check, GPU results, retained runtime allocation/host peak or speed evidence."}
with (STAGE / "syntax-and-integer-report.json").open("x", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps({"status": report["status"], "parsed_files": 4, "host_pack_cases": 65536,
                  "all_owned_handles_terminal": True, "GPUexecutions": 0}))
