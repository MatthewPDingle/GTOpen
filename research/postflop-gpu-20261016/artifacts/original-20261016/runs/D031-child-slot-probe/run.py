"""D031 standalone compiler/resource probe. Run only in the parent's serialized slot."""
from pathlib import Path
import argparse
from collections import Counter
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
REPO = Path(r"X:\Dev\GTOpen-gpu-research-20261016")
DEPS = ROOT / "build/release/deps"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, value):
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def write_bytes(name, data):
    with (HERE / name).open("xb") as f:
        f.write(data)


def entry(source, name):
    match = re.search(r"\.visible\s+\.entry\s+" + re.escape(name) + r"\(", source)
    assert match, name
    begin = source.index("{", match.start())
    depth, end = 1, begin + 1
    while depth:
        if source[end] == "{": depth += 1
        elif source[end] == "}": depth -= 1
        end += 1
    return source[match.start():end]


def instruction_summary(source):
    # Static PTX text counts, not executed instructions, SASS or ordering proof.
    ops = []
    for line in source.splitlines():
        line = line.split("//", 1)[0]
        match = re.match(r"\s*(?:@!?%\w+\s+)?([a-z]\w*(?:\.\w+)+)\s", line)
        if match: ops.append(match.group(1))
    counts = Counter(ops)
    return {"lines": len(source.splitlines()), "bytes_utf8": len(source.encode()),
            "opcode_histogram": dict(sorted(counts.items())),
            "global_load_instructions": sum(v for k,v in counts.items() if k.startswith("ld.global.")),
            "local_load_instructions": sum(v for k,v in counts.items() if k.startswith("ld.local.")),
            "local_store_instructions": sum(v for k,v in counts.items() if k.startswith("st.local.")),
            "floating_opcode_sequence_textual_only": [op for op in ops if any(t in op.split(".") for t in ("f16","f32","f64"))]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True,
                        help="explicitly compile and query CUDA only after parent releases serialized slot")
    parser.parse_args()
    prepared = json.loads((HERE / "prepared-manifest.json").read_text(encoding="utf-8"))
    for name, expected in prepared["artifact_sha256"].items():
        assert sha(HERE/name) == expected, ("Prepared input changed", name)
    for name, info in prepared["dependency_rlibs"].items():
        assert sha(info["path"]) == info["sha256"], ("Dependency changed", name)
    # Exclusive create makes a failed attempt permanent evidence; do not retry in this directory.
    save("execution-started.json", {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "prepared_manifest_sha256": sha(HERE/"prepared-manifest.json"),
         "prepared_only_status_in_original_manifest_is_historical": True,
         "operator_obligation": "No concurrent build, benchmark or GPU work; lock also checked below"})
    spec = importlib.util.spec_from_file_location("d031_runner", HERE/"runner-primitives-source.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.REPO = REPO
    deps = prepared["dependency_rlibs"]
    command = ["rustc", "probe.rs", "--edition=2021", "-C", "opt-level=3", "-C", "codegen-units=1", "-C", "lto=thin",
               "-L", "dependency="+str(DEPS), "--extern", "cudarc="+deps["cudarc"]["path"],
               "--extern", "serde_json="+deps["serde_json"]["path"], "-o", "probe.exe"]
    commands = []

    def execute(args, name, env=None):
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        before = time.perf_counter()
        child = subprocess.Popen(args, cwd=HERE, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        try:
            out, err = child.communicate(timeout=120)
        except BaseException:
            child.kill()
            out, err = child.communicate()
            write_bytes(name+".stdout.log", out)
            write_bytes(name+".stderr.log", err)
            save(name+".command.json", {"args": args, "cwd": str(HERE), "started_at": started,
                "elapsed_seconds": time.perf_counter()-before, "returncode": child.returncode,
                "interrupted_or_timeout": True})
            raise
        write_bytes(name+".stdout.log",out)
        write_bytes(name+".stderr.log",err)
        record = {"args": args, "cwd": str(HERE), "started_at": started,
                  "elapsed_seconds": time.perf_counter()-before, "returncode": child.returncode}
        save(name+".command.json", record)
        commands.append(record)
        if child.returncode: raise RuntimeError(name+" failed; evidence retained, do not overwrite/retry")
        return out.decode("utf-8")

    try:
        with runner.exclusive_lock(ROOT/"gpu-run.lock"):
            live = runner.live_status()
            runner.refuse_active(live)
            save("preflight.json", {"live_status":live,"telemetry":runner.telemetry(),"lock":str(ROOT/"gpu-run.lock")})
            save("execution-manifest.json", {"id":"D031", "prepared_manifest_sha256":sha(HERE/"prepared-manifest.json"),
                 "input_sha256_before": {name:sha(HERE/name) for name in prepared["artifact_sha256"]},
                 "rustc":runner.read_command(["rustc","-Vv"]), "compile_command":command,
                 "nvrtc_directory":str(runner.NVRTC),
                 "nvrtc_dll_sha256":{p.name:sha(p) for p in sorted(Path(runner.NVRTC).glob("*.dll"))},
                 "source_identity":"Only sealed local baseline/candidate are compiled; current checkout source not used.",
                 "gpu_device_ordinal":0,"expected_device":"NVIDIA GeForce RTX 5090","expected_architecture":"compute_120",
                 "kernel_launches":0,"solver_executions":0,"performance_measurement":False})
            assert not (HERE/"probe.exe").exists(), "Refusing existing executable"
            execute(command,"rustc")
            env = os.environ.copy()
            env["PATH"] = str(runner.NVRTC)+os.pathsep+env.get("PATH","")
            env["RAYON_NUM_THREADS"] = "16"
            live = runner.live_status()
            runner.refuse_active(live)
            save("launch-preflight.json",live)
            output = execute([str(HERE/"probe.exe")],"probe",env)
            telemetry_after = runner.telemetry()
        rows = [json.loads(line.removeprefix("METRIC_JSON ")) for line in output.splitlines() if line.startswith("METRIC_JSON ")]
        assert [(r["source_variant"],r["kernel"]) for r in rows] == [("baseline","up_action"),("candidate","up_action")]
        for row in rows:
            expected = prepared["source_variants"][row["source_variant"]]
            assert row["source_fnv1a64"] == expected["fnv1a64"] and row["source_bytes"] == expected["bytes"]
            assert row["kernel_launches"] == 0 and row["solver_executions"] == 0
        ptx = {v:(HERE/(v+".ptx")).read_text(encoding="utf-8") for v in ("baseline","candidate")}
        up = {v:entry(text,"up_action") for v,text in ptx.items()}
        for variant,text in up.items(): write_bytes(variant+"-up_action.ptx",(text+"\n").encode())
        names = {v:re.findall(r"\.visible\s+\.entry\s+(\w+)\(",text) for v,text in ptx.items()}
        assert names["baseline"] == names["candidate"], "Entrypoints unexpectedly changed"
        summaries = {v:instruction_summary(text) for v,text in up.items()}
        controls = {name:entry(ptx["baseline"],name)==entry(ptx["candidate"],name)
                    for name in names["baseline"] if name!="up_action"}
        after = {name:sha(HERE/name) for name in prepared["artifact_sha256"]}
        assert after == prepared["artifact_sha256"], "Prepared inputs changed during run"
        for info in deps.values(): assert sha(info["path"]) == info["sha256"]
        report = {"id":"D031","status":"completed_compiler_resource_diagnostic",
             "prepared_manifest_sha256":sha(HERE/"prepared-manifest.json"),"results":rows,"commands":commands,
             "telemetry_after":telemetry_after,"input_sha256_after":after,
             "up_action_ptx":summaries,"other_entry_ptx_byte_equality":controls,
             "float_opcode_sequence_equal_textual_only":summaries["baseline"]["floating_opcode_sequence_textual_only"]==summaries["candidate"]["floating_opcode_sequence_textual_only"],
             "resource_change":{k:{"baseline":rows[0][k],"candidate":rows[1][k]} for k in
                    ["registers","local_bytes_per_thread","static_shared_bytes","occupancy_blocks_per_sm_128"]},
             "kernel_launches":0,"solver_executions":0,"performance_measurement":False,"candidate_accepted":False,
             "numerical_validation":"not executed",
             "limits":["PTX is virtual ISA; register/shared/local/occupancy queried after driver module load.",
                       "Static PTX counts/opcode order are not dynamic work, SASS, timing, or bitwise proof.",
                       "Common arity child loads were already hoisted outside hand loops in baseline.",
                       "No host mapping, upload, allocation, admission, graph, or continuation integration is tested.",
                       "Removing integer addressing can affect compiler float scheduling; runtime exact-state qualification still required.",
                       "Compiler process durations are audit metadata, never solver performance measurements."],
             "artifact_sha256":{p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file()}}
        save("report.json",report)
        print(json.dumps({"id":"D031","results":rows,"resource_change":report["resource_change"],"performance_measurement":False},indent=2))
    except BaseException as error:
        save("failure.json", {"error":repr(error),"commands":commands,
             "at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "instruction":"Preserve this attempt. Investigate before using a new explicitly authorized directory."})
        raise


if __name__ == "__main__":
    main()
