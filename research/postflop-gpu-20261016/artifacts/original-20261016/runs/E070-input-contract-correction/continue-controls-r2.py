"""Run only the unexecuted E070 controls after the sealed fixture correction."""
from pathlib import Path
import json
import shutil
import sys

ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
HERE = Path(__file__).resolve().parent
ORIGINAL = ROOT/"runs/E070-direct-kernel-controls"
sys.path.insert(0, str(ROOT/"runs/accepted-E051"))
import common_e051 as old


def main():
    assert len(sys.argv) == 2
    old.pin(HERE/"protocol-r2.json", sys.argv[1]); protocol = old.read(HERE/"protocol-r2.json")
    for path, digest in protocol["input_sha256"].items():
        old.pin(path, digest)
    old.custody(); old.ar.refuse_active(old.ar.live_status())
    assert shutil.disk_usage(ROOT).free >= 66*1024**3
    assert not (HERE/"execution-started-r2.json").exists()
    env = old.env()
    with old.ar.exclusive_lock(ROOT/"gpu-run.lock"):
        old.custody(); old.ar.refuse_active(old.ar.live_status())
        old.save(HERE/"execution-started-r2.json", {"at": old.now(), "protocol_sha256": sys.argv[1], "new_application_kernel_launches_before_seal": 0})
        pre = HERE/"down-remaining"
        results = [{"component":"down-remaining","cases":24,"kernel_launches":48,"report_sha256":old.sha(pre/"report.json"),"raw_files":{p.name:{"sha256":old.sha(p),"bytes":p.stat().st_size} for p in (pre/"execution/raw").iterdir()}}]
        try:
            components = [
                ("up-action-eval", ORIGINAL/"inputs/up-action-eval", "E070_EVAL_KERNEL_CONTROL_DIR", 1638, "up-action-eval"),
                ("up-fold", ORIGINAL/"inputs/up-fold", "E070_FOLD_KERNEL_CONTROL_DIR", 180, "up-fold"),
                ("continuation-raw", ORIGINAL/"inputs/continuation-raw", "E070_HELPER_RAW_DIR", 2120, "continuation-raw"),
            ]
            for name, source, variable, cases, family in components:
                component = HERE/name; component.mkdir(exist_ok=True)
                run = component/"execution"; run.mkdir()
                for path, digest in protocol["input_sha256"].items():
                    old.pin(path, digest)
                old.custody(); old.ar.refuse_active(old.ar.live_status())
                assert shutil.disk_usage(ROOT).free >= 58*1024**3
                old.save(component/"before.json", {"at": old.now(), "cases": cases, "planned_kernel_launches": 2*cases,
                         "protocol_sha256": sys.argv[1], "binary_sha256": old.sha(source/"probe.exe")})
                with old.ar.exclusive_lock(old.ar.STATUS.with_suffix(".lock"), timeout=3):
                    data = old.read(old.ar.STATUS)
                    data.update(updated_at=old.now(), state="running", goal_status="active", active_experiment="E070",
                                stage="E070 remaining exact controls: "+name,
                                activity="Full access operational. Input-contract correction preserves prior raw evidence; executing only unexecuted case pairs, no speed samples or candidate code changes.")
                    old.ar.atomic_json(old.ar.STATUS, data)
                native_env = env.copy(); native_env[variable] = str(run/"raw")
                if family == "continuation-raw":
                    native_env["E070_HELPER_PTX_DIR"] = str(ORIGINAL/"helper-resource/execution/ptx")
                old.child([str(source/"probe.exe")], run, "probe", native_env, 1800)
                old.custody()
                if name == "down-remaining":
                    command = [sys.executable, "-B", str(HERE/"audit-remaining.py"), "down-action", str(source), str(run/"raw"), str(component/"report.json")]
                elif family == "continuation-raw":
                    command = [sys.executable, "-B", str(ORIGINAL/"scripts/helper_raw_audit.py"), str(source), str(run/"raw"), str(run/"probe.stdout.log"),
                               str(component/"report.json"), str(HERE/"numerical-admission.json"), old.sha(HERE/"numerical-admission.json")]
                else:
                    command = [sys.executable, "-B", str(ORIGINAL/"scripts/audit_raw.py"), family, str(source), str(run/"raw"), str(component/"report.json")]
                old.child(command, run, "root-audit", env, 1800)
                report = old.read(component/"report.json")
                assert report["status"].startswith("pass_scoped_") and report["cases"] == cases and report["kernel_launches"] == 2*cases
                results.append({"component": name, "cases": cases, "kernel_launches": 2*cases, "report_sha256": old.sha(component/"report.json"),
                                "raw_files": {p.name: {"sha256": old.sha(p), "bytes": p.stat().st_size} for p in (run/"raw").iterdir()}})
            old.custody()
            for path, digest in protocol["input_sha256"].items():
                old.pin(path, digest)
            assert sum(x["cases"] for x in results)+1172+819 == 5953
            old.save(HERE/"complete.json", {"id": "E070-seven-entry-partitioned-control-closure", "at": old.now(),
                     "status": "pass_scoped_seven_entry_exact_controls_with_recorded_fixture_correction",
                     "protocol_sha256": sys.argv[1], "original_execution_plan_sha256": old.sha(ORIGINAL/"execution-plan.json"),
                     "original_up_report_sha256": old.sha(ORIGINAL/"up-action/report.json"), "original_down_prefix_report_sha256": old.sha(HERE/"prefix-report.json"),
                     "corrected_remaining_components": results, "cases": 5953, "application_kernel_launches": 11906,
                     "native_numerical_processes": 6, "case_coverage": "Up819; down original IDs0..1171 plus corrected/unexecuted IDs1172..1195; eval1638; fold180; helpers2120. Each retained ID has one baseline/candidate GPU pair; no completed pair repeated or case excluded.",
                     "fixture_normalization": "Exactly12unexecuted signed actor=-1 cases use source-valid byte255 in both arms; all other dimensions/float factories/PTX/widths/locks/IDs retained.",
                     "source_main_live_PTX_custody_pass": True, "all_owned_child_handles_terminal": True,
                     "solver_activation": False, "solver_executions": 0, "performance_measurements": 0, "candidate_accepted": False})
            print("E070_ALL5953_CASE_PAIRS_EXACT; SOURCE_CANDIDATE_UNCHANGED; NO_SPEED_RESULT", flush=True)
        except BaseException as error:
            old.save(HERE/"continuation-failure-r2.json", {"at": old.now(), "error": repr(error), "completed_components": results,
                     "candidate_source_changed": False, "speed_samples": 0, "automatic_retry": False})
            raise


if __name__ == "__main__":
    main()
