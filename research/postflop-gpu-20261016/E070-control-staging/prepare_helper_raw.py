"""Freeze/compile the three helper raw comparisons without executing them."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
OUT = HERE / "continuation-raw"
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
assert not OUT.exists()
cases = []


def add(kind, hands, actions, threads, p, operation, count, value_mode, group):
    assert 0 <= actions <= 255 and p in [0, 1] and operation in [0, 1]
    cases.append({"id": len(cases), "kind": kind, "hands": hands, "actions": actions,
                  "threads": threads, "p": p, "operation": operation, "count": count,
                  "value_mode": value_mode, "group": group,
                  "descriptor": [kind, hands, actions, threads, p, operation, count, value_mode, 5, 13, 11]})


kinds = [(0, [0, 1]), (1, [0]), (2, [0, 1])]
for kind, operations in kinds:
    for nh in [0, 1, 2, 31, 32, 33, 127, 128, 129, 255, 256, 257, 511, 512, 513, 1326]:
        for na in [0, 1, 2, 3, 4, 8, 9, 17, 255]:
            for p in [0, 1]:
                for operation in operations:
                    add(kind, nh, na, 128, p, operation, 3, 0, "dimensions_and_byte_arity")
for kind, operations in kinds:
    for block in [1, 32, 64, 256]:
        for nh in [7, 129, 513]:
            for na in [1, 2, 9, 17]:
                for p in [0, 1]:
                    for operation in operations:
                        add(kind, nh, na, block, p, operation, 3, 0, "fallback_blocks_and_tails")
for kind, operations in kinds:
    for mode in [1, 2, 3, 4]:
        for na in [1, 2, 9, 17]:
            for p in [0, 1]:
                for operation in operations:
                    add(kind, 257, na, 128, p, operation, 3, mode, "signedzero_nonfinite_overflow_subnormal")
for kind, operations in kinds:
    for na in [0, 1, 9, 255]:
        for p in [0, 1]:
            for operation in operations:
                add(kind, 129, na, 128, p, operation, 0, 0, "uniform_zero_count")
assert len(cases) == 2120
raw_bound = 100
maximum_mutable_bytes = 0
for c in cases:
    nh, na = c["hands"], c["actions"]
    full = 13+4*(na*nh+7)+na*nh+17
    packed = 11+4*(na*nh+5)+na*nh+17
    immutable = 5*8+10*2+max(1, 2*nh)  # nodes,players,arity,attrs,masks,sources,source_pm =7x5; actual below
    immutable = 5+5+5+5+10+5+max(1, 2*nh)+5+5+10
    mutable = 2*full+2*packed
    raw_bound += 20+8+44+3*8*(10+4)+12*(immutable+mutable)
    maximum_mutable_bytes = max(maximum_mutable_bytes, mutable*4)
corpus = {
    "id": "E070-continuation-full-raw-unexecuted-blueprint", "case_count": len(cases),
    "planned_kernel_launches": 2*len(cases), "cases": cases,
    "kinds": {"0": "continuation_project, operation0reduce/1broadcast",
              "1": "continuation_transport, reverse hand permutation from immutable canonical nodes",
              "2": "continuation_storage_copy, operation0scatter/1gather"},
    "finite_symmetry_group": "Identity and reversal (order2), plus mask1 early-return nodes. Each operation starts from a fresh original seed; this does not replace end-to-end reduce/broadcast/sweep tests.",
    "CPU_oracle": "All owned copy/transport/broadcast words must match the original source bits, including nonfinite payloads. Finite projection reductions must match ordered double accumulation of identity/reversal images followed by division and f32 conversion. Nonfinite reductions require complete baseline/candidate bit equality, with no cross-platform CPU NaN-payload claim.",
    "immutable_schema": ["nodes:u32", "players:i32", "arity:i32", "attrs:u16 decoded as u32",
                         "full_offsets:u64 split words", "stabilizers:u32", "permutations:u32",
                         "canonical_sources:u32", "source_permutations:u32", "packed_offsets:u64 split words"],
    "mutable_schema": ["full_regrets:f32 bits", "full_sums:f32 bits", "packed_regrets:f32 bits", "packed_sums:f32 bits"],
    "guards": "Complete four mutable arrays, including unlaunched guards, opposite-player rows, canonical source rows and all nonowned orbit words. Every actual immutable device array is captured unchanged after both arms. Four actual mutable pointer extents must be disjoint.",
    "limits": "Declared synthetic layouts and an order2 group only. Full solver, actual deal-group continuation/storage, supported capacity, no-tradeoff and timing qualification remain required.",
}
OUT.mkdir()
(OUT/"corpus.json").write_text(json.dumps(corpus, indent=2), encoding="utf-8")
shutil.copyfile(HERE/"helper_raw_probe.rs", OUT/"probe.rs")
p = json.loads((ROOT/"runs/E070-resource/protocol.json").read_text(encoding="utf-8"))
resource = ROOT/"runs/E070-resource"
command = [str(OUT/"probe.rs") if x == str(resource/"probe.rs") else
           str(OUT/"probe.exe") if x == str(resource/"probe.exe") else x for x in p["rustc_command"]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


prep = {"id": "E070-three-continuation-helper-raw-preparation", "status": "unexecuted_correctness_controls",
        "cases": len(cases), "planned_kernel_launches": 2*len(cases),
        "rustc_command": command, "input_sha256": {x.name: sha(x) for x in OUT.iterdir() if x.is_file()},
        "conservative_full_raw_bytes": raw_bound, "maximum_mutable_GPU_payload_bytes": maximum_mutable_bytes,
        "storage_reservation": "Combined main+helper correctness raw outputs fit within the existing8GiB peak reservation; recheck66GiB free on S at native admission.",
        "PTX_dependency": "Read the four compute_120 PTX files from the separately sealed successful helper resource run. Parent must pin their SHA256 before and after the one numerical process, and retain that exact PTX manifest before any application kernel launch.",
        "candidate_sources": json.loads((HERE/"host-integration-r2/manifest.json").read_text(encoding="utf-8"))["candidate_source_sha256"],
        "no_rescue": "Fixed2120cases, one baseline/candidate launch each, no resampling/extra/excluded cases or candidate source/compiler-option rescue.",
        "native_admission_pending": True, "GPUexecutions": 0, "NVRTC_processes": 0,
        "limits": "Host compilation preparation only; no numerical result or speed measurement."}
assert raw_bound + 735936900 < 8*1024**3
with (OUT/"preparation.json").open("x", encoding="utf-8") as f:
    json.dump(prep, f, indent=2)
temporary = OUT/"compiler-tmp"
temporary.mkdir()
env = os.environ.copy()
env["TMP"] = env["TEMP"] = str(temporary)
process = None
error = None
started = datetime.now(timezone.utc).isoformat()
try:
    with (OUT/"rustc.stdout.log").open("xb") as stdout, (OUT/"rustc.stderr.log").open("xb") as stderr:
        process = subprocess.Popen(command, cwd=OUT, env=env, stdout=stdout, stderr=stderr,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=30); raise
except BaseException as exc:
    error = repr(exc)
    raise
finally:
    receipt = {"started": started, "finished": datetime.now(timezone.utc).isoformat(),
               "pid": process.pid if process else None, "returncode": process.returncode if process else None,
               "terminal": process is not None and process.poll() is not None,
               "error": error, "GPUexecutions": 0, "NVRTC_processes": 0,
               "preparation_sha256": sha(OUT/"preparation.json")}
    if (OUT/"probe.exe").exists():
        receipt["binary_sha256"] = sha(OUT/"probe.exe")
    with (OUT/"rustc-exit.json").open("x", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
assert process.returncode == 0, (OUT/"rustc.stderr.log").read_text(encoding="utf-8", errors="replace")[-3500:]
print(json.dumps({"compiled": "three helper raw controls", "cases": len(cases),
                  "binary_sha256": receipt["binary_sha256"], "conservative_raw_bytes": raw_bound,
                  "GPUexecutions": 0, "NVRTC_processes": 0}))
