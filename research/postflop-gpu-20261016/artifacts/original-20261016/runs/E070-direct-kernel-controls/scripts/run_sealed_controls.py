"""Explicit native entry point for one frozen E070 correctness campaign.

Preparation/import starts nothing. --execute requires the exact prepublished
plan hash and actual runtime access to S: and localhost. No permission/config
changes, solver activation, server restart, timing, retries or extra samples.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import os
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
ARCHIVE = ROOT/"runs/E070-direct-kernel-controls"
GPU_UUID = "GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert len(sys.argv) == 3 and sys.argv[1] == "--execute", "--execute <frozen execution-plan SHA256> required"
    sys.path.insert(0, str(ROOT/"runs/accepted-E051"))
    import common_e051 as old
    plan_path = HERE/"native-execution-plan.json"
    old.pin(plan_path, sys.argv[2])
    plan = old.read(plan_path)
    assert plan["id"] == "E070-seven-entry-native-execution-plan"
    assert plan["candidate_cuda_sha256"] == "ffe6c46aa48fbae149ace1288ea512814da11b840c648e6a260759e427c54ec8"
    assert plan["declared_cases"] == 5953 and plan["planned_application_kernel_launches"] == 11906
    assert plan["native_archive"] == str(ARCHIVE) and not ARCHIVE.exists()
    for record in plan["archive_inputs"]:
        old.pin(record["source"], record["sha256"])
    for name, expected in plan["existing_scientific_inputs"].items():
        old.pin(name, expected)
    # A restricted runtime must not be worked around. This command is held until
    # the actual thread can perform these ordinary authorized native operations.
    old.custody()
    live = old.ar.live_status(); old.ar.refuse_active(live)
    assert shutil.disk_usage(ROOT).free >= plan["minimum_free_before_admission_bytes"]
    env = old.env()
    assert not {k: v for k, v in env.items() if k in {"RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC", "RUSTC_WRAPPER"} or k.startswith("CARGO_PROFILE_RELEASE_")}
    assert env.get("CUDA_VISIBLE_DEVICES") in {None, "", "0", GPU_UUID}
    phase = "not-admitted"
    numerical_started = 0
    with old.ar.exclusive_lock(ROOT/"gpu-run.lock"):
        old.custody(); old.ar.refuse_active(old.ar.live_status())
        assert not ARCHIVE.exists()
        ARCHIVE.mkdir()
        shutil.copyfile(plan_path, ARCHIVE/"execution-plan.json")
        old.pin(ARCHIVE/"execution-plan.json", sys.argv[2])

        def archived_inputs():
            for record in plan["archive_inputs"]:
                old.pin(ARCHIVE/record["archive_relative"], record["sha256"])
            old.pin(ARCHIVE/"execution-plan.json", sys.argv[2])
            for name, expected in plan["existing_scientific_inputs"].items():
                old.pin(name, expected)

        def fresh_state(label):
            archived_inputs(); old.custody()
            snapshots = old.ar.live_status(); old.ar.refuse_active(snapshots)
            assert shutil.disk_usage(ROOT).free >= plan["minimum_free_during_controls_bytes"]
            old.save(ARCHIVE/(label+"-preflight.json"), {"at": old.now(), "live": snapshots,
                     "S_free_bytes": shutil.disk_usage(ROOT).free, "file_and_Git_custody_pass": True})

        def status(stage, activity):
            with old.ar.exclusive_lock(old.ar.STATUS.with_suffix(".lock"), timeout=3):
                data = old.read(old.ar.STATUS)
                accepted = data["accepted_complete_run"].copy()
                assert accepted["candidate_id"] == "E051"
                data.update(updated_at=old.now(), state="running", goal_status="active", active_experiment="E070", stage=stage, activity=activity)
                assert data["accepted_complete_run"] == accepted
                old.ar.atomic_json(old.ar.STATUS, data)

        try:
            phase = "checksum archive"
            for record in plan["archive_inputs"]:
                target = ARCHIVE/record["archive_relative"]
                assert target.resolve().is_relative_to(ARCHIVE.resolve()) and not target.exists()
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(record["source"], target)
                old.pin(target, record["sha256"])
            archived_inputs()
            old.save(ARCHIVE/"input-archive.json", {"at": old.now(), "execution_plan_sha256": sys.argv[2],
                     "files": len(plan["archive_inputs"]), "all_originals_and_full_copies_SHA256_verified": True,
                     "application_kernel_launches_before_seal": 0, "live_before_admission": live})
            inventory = ARCHIVE/"inventory"; inventory.mkdir()
            old.child(["nvidia-smi", "--query-gpu=index,uuid,name", "--format=csv,noheader,nounits"], inventory, "gpu-inventory", env, 30)
            devices = list(csv.reader(io.StringIO((inventory/"gpu-inventory.stdout.log").read_text(encoding="utf-8"))))
            assert any([x.strip() for x in row] == ["0", GPU_UUID, "NVIDIA GeForce RTX 5090"] for row in devices), devices
            old.save(ARCHIVE/"device-admission.json", {"at": old.now(), "expected_physical_UUID": GPU_UUID,
                     "physical_index": 0, "inventory_sha256": old.sha(inventory/"gpu-inventory.stdout.log"),
                     "CUDA_VISIBLE_DEVICES": env.get("CUDA_VISIBLE_DEVICES")})
            status("E070 helper resource prerequisites", "Archived frozen inputs verified on S; one helper resource process, no application kernel launches or performance samples.")
            resource = ARCHIVE/"helper-resource"; resource.mkdir()
            execution = resource/"execution"; execution.mkdir()
            source = ARCHIVE/"inputs/continuation-resources"
            fresh_state("helper-resource")
            phase = "helper resource execution"
            resource_env = env.copy(); resource_env["E070_HELPER_RESOURCE_DIR"] = str(execution/"ptx")
            old.child([str(source/"probe.exe")], execution, "probe", resource_env, 180)
            old.custody(); archived_inputs()
            phase = "helper resource audit"
            old.child([sys.executable, "-B", str(ARCHIVE/"scripts/audit_helper_resources.py"),
                       str(source), str(execution/"ptx"), str(execution/"probe.stdout.log"), str(resource/"report.json")], execution, "root-audit", env, 180)
            resource_report = old.read(resource/"report.json")
            assert resource_report["status"] == "pass_helper_compiler_ABI_and_resource_prerequisites"
            pt_inputs = {name: digest for name, digest in resource_report["all_eight_PTX_sha256"].items() if name.endswith("compute_120.ptx")}
            assert len(pt_inputs) == 4
            phase = "prospective numerical admission"
            admission = {"id": "E070-seven-entry-numerical-admission", "at": old.now(),
                         "execution_plan_sha256": sys.argv[2], "helper_resource_report_sha256": old.sha(resource/"report.json"),
                         "helper_ptx_input_sha256": pt_inputs, "core_resource_report_sha256": plan["existing_scientific_inputs"][str(ROOT/"runs/E070-resource/report.json")],
                         "cases": 5953, "kernel_launches": 11906, "application_kernel_launches_before_seal": 0,
                         "fixed_sampling": "Five numerical processes, each case one baseline/candidate pair. No speed measurements, re-runs, additional/excluded cases or source variants."}
            old.save(ARCHIVE/"numerical-admission.json", admission)
            admission_sha = old.sha(ARCHIVE/"numerical-admission.json")
            results = []
            families = [
                ("up-action", "E070_UP_KERNEL_CONTROL_DIR", 819),
                ("down-action", "E070_DOWN_RAW_DIR", 1196),
                ("up-action-eval", "E070_EVAL_KERNEL_CONTROL_DIR", 1638),
                ("up-fold", "E070_FOLD_KERNEL_CONTROL_DIR", 180),
                ("continuation-raw", "E070_HELPER_RAW_DIR", 2120),
            ]
            for index, (name, variable, cases) in enumerate(families):
                phase = "numerical "+name
                component = ARCHIVE/name; component.mkdir()
                run = component/"execution"; run.mkdir()
                source = ARCHIVE/"inputs"/name
                fresh_state("numerical-"+name)
                for path, digest in pt_inputs.items():
                    old.pin(path, digest)
                old.pin(ARCHIVE/"numerical-admission.json", admission_sha)
                old.save(component/"before.json", {"at": old.now(), "cases": cases,
                         "planned_application_kernel_launches": 2*cases, "numerical_admission_sha256": admission_sha,
                         "binary_sha256": old.sha(source/"probe.exe"), "application_kernel_launches_in_this_process_before_seal": 0})
                status("E070 exact GPU controls: "+name, f"Executing declared{cases}case raw comparison ({index+1}/5processes); no solve-speed sample or accepted gain.")
                numerical_env = env.copy(); numerical_env[variable] = str(run/"raw")
                if name == "continuation-raw":
                    numerical_env["E070_HELPER_PTX_DIR"] = str(resource/"execution/ptx")
                numerical_started += 1
                old.child([str(source/"probe.exe")], run, "probe", numerical_env, plan["numerical_process_timeout_seconds"])
                archived_inputs(); old.custody()
                for path, digest in pt_inputs.items():
                    old.pin(path, digest)
                phase = "raw replay "+name
                if name == "continuation-raw":
                    command = [sys.executable, "-B", str(ARCHIVE/"scripts/helper_raw_audit.py"), str(source), str(run/"raw"),
                               str(run/"probe.stdout.log"), str(component/"report.json"), str(ARCHIVE/"numerical-admission.json"), admission_sha]
                else:
                    command = [sys.executable, "-B", str(ARCHIVE/"scripts/audit_raw.py"), name, str(source), str(run/"raw"), str(component/"report.json")]
                old.child(command, run, "root-audit", env, plan["root_replay_timeout_seconds"])
                report = old.read(component/"report.json")
                assert report["status"].startswith("pass_scoped_") and report["cases"] == cases and report["kernel_launches"] == 2*cases
                results.append({"family": name, "cases": cases, "kernel_launches": 2*cases, "report_sha256": old.sha(component/"report.json"),
                                "full_raw_files": {p.name: {"bytes": p.stat().st_size, "sha256": old.sha(p)} for p in (run/"raw").iterdir()}})
                assert len(results[-1]["full_raw_files"]) == 5
            phase = "closure"
            archived_inputs(); old.custody(); old.ar.refuse_active(old.ar.live_status())
            assert sum(r["cases"] for r in results) == 5953 and sum(r["kernel_launches"] for r in results) == 11906
            old.save(ARCHIVE/"complete.json", {"id": "E070-seven-entry-direct-controls", "at": old.now(),
                     "status": "pass_scoped_seven_entry_exact_controls", "execution_plan_sha256": sys.argv[2],
                     "numerical_admission_sha256": admission_sha, "components": results,
                     "cases": 5953, "application_kernel_launches": 11906, "native_numerical_processes": 5,
                     "all_owned_child_handles_terminal": True, "source_main_live_protected_PTX_custody_pass": True,
                     "solver_activation": False, "solver_executions": 0, "performance_measurement": False,
                     "candidate_accepted": False, "next": "Prepare source activation/build protocol for the full host/caller integration and ordinary/complete-solver/continuation exactness checks before registered timing."})
            evidence = old.ar.DASHBOARD/"evidence/E070-seven-entry-direct-controls"; evidence.mkdir()
            shutil.copyfile(ARCHIVE/"complete.json", evidence/"complete.json")
            shutil.copyfile(ARCHIVE/"execution-plan.json", evidence/"execution-plan.json")
            shutil.copyfile(ARCHIVE/"numerical-admission.json", evidence/"numerical-admission.json")
            shutil.copyfile(resource/"report.json", evidence/"helper-resource-report.json")
            for result in results:
                shutil.copyfile(ARCHIVE/result["family"]/"report.json", evidence/(result["family"]+"-report.json"))
            with old.ar.exclusive_lock(old.ar.STATUS.with_suffix(".lock"), timeout=3):
                data = old.read(old.ar.STATUS)
                accepted = data["accepted_complete_run"].copy()
                assert accepted["candidate_id"] == "E051"
                data.update(updated_at=old.now(), state="running", goal_status="active", stage="E070 direct controls pass; integrated build next",
                            activity="All5953declared raw GPUcase pairs across7entries pass scoped exactness/resource controls. No integrated solver or speed result yet; accepted E051 gain unchanged.")
                link = {"label": "Seven-entry full raw controls and root replays", "url": "evidence/E070-seven-entry-direct-controls/complete.json"}
                row = next(x for x in data["experiments"] if x["id"] == "E070")
                row.update(correctness="Direct5953case GPUcontrols pass; integrated solver untested", stage="Host/caller integrated build protocol next")
                row["evidence"].append(link); data["evidence"].append(link)
                assert data["accepted_complete_run"] == accepted
                old.ar.atomic_json(old.ar.STATUS, data)
            print("E070_SEVEN_ENTRY_DIRECT_CONTROLS_PASS; NO_SPEED_RESULT", flush=True)
        except BaseException as error:
            if not (ARCHIVE/"failure.json").exists():
                old.save(ARCHIVE/"failure.json", {"at": old.now(), "phase": phase, "error": repr(error),
                         "numerical_processes_started": numerical_started, "automatic_retry": False,
                         "source_activation": False, "speed_measurements": 0,
                         "disposition": "Stopped; preserve every source/result/receipt. Inspect the recorded failure before any further work. No candidate rescue or extra samples."})
            with old.ar.exclusive_lock(old.ar.STATUS.with_suffix(".lock"), timeout=3):
                data = old.read(old.ar.STATUS)
                data.update(updated_at=old.now(), state="waiting", goal_status="active", stage="E070 native controls stopped at "+phase,
                            activity="Frozen control run stopped; failure evidence preserved, no automatic retry, no new accepted gain. Source not activated.")
                old.ar.atomic_json(old.ar.STATUS, data)
            raise


if __name__ == "__main__":
    main()
