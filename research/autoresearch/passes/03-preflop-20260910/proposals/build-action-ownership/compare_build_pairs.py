"""Strict comparator for frozen build/load harness. No solver execution."""
import json, math, statistics
from pathlib import Path
IDENTITY = ["mode", "input", "typed_config_hash", "typed_profile_hash", "typed_hash_algorithm", "native_arenas", "iteration", "frozen", "hero", "point_lock_hash", "point_lock_count", "hero_backup_meta", "pre_hero_frozen", "model", "roundtrip_bytes", "equity_cache", "equity_cache_hash", "equity_samples", "fit_cache", "fit_cache_hash", "fresh_mode_note"]
TOPOLOGY = ["topology_hash", "nodes", "action_nodes", "edges", "action_string_len_bytes"]
CAPACITY = ["action_vec_capacity_bytes", "action_string_capacity_bytes", "action_retained_bytes"]
def require(ok, message):
    if not ok: raise ValueError(message)
def same_existing_file(left, right):
    """OS file identity, including Windows extended paths; missing files fail closed."""
    try:
        return Path(left).samefile(Path(right))
    except (OSError, ValueError, TypeError):
        return False

def verified(log):
    rows = [json.loads(line[len("BUILD_BENCH "):]) for line in Path(log).read_text(encoding="utf-8").splitlines() if line.startswith("BUILD_BENCH ")]
    require(len(rows)==2 and [r.get("phase") for r in rows]==["timed", "verified"], "missing, duplicated or out-of-order build verification")
    timed, row = rows
    require(row.get("operation_ms")==timed.get("operation_ms") and row.get("mode")==timed.get("mode"), "timed/verified mismatch")
    value=row.get("operation_ms")
    require(isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>0, "invalid timing")
    for key in IDENTITY: require(key in row, "missing identity: "+key)
    for key in TOPOLOGY+CAPACITY: require(key in row.get("topology",{}), "missing topology: "+key)
    require(isinstance(row["native_arenas"],dict) and isinstance(row["native_arenas"].get("arrays"),list) and len(row["native_arenas"]["arrays"]) in [2,4], "malformed native arenas")
    for a in row["native_arenas"]["arrays"]:
        for k in ["index","elements","hash","nonzero_bytes"]: require(k in a,"missing arena field "+k)
    return row

def compare_rows(a,b):
    for key in IDENTITY: require(a[key]==b[key],"identity mismatch: "+key)
    for key in TOPOLOGY: require(a["topology"][key]==b["topology"][key],"topology mismatch: "+key)
    return {"exact":True,"baseline_ms":a["operation_ms"],"candidate_ms":b["operation_ms"],"reduction_percent":100*(1-b["operation_ms"]/a["operation_ms"]),"capacity_bytes":{k:{"baseline":a["topology"][k],"candidate":b["topology"][k],"delta":b["topology"][k]-a["topology"][k]} for k in CAPACITY}}

def compare_plan(plan):
    groups={}
    for pair in plan["pairs"]:
        rows={};memory={}
        for side in ["baseline","candidate"]:
            run=pair[side]; record=json.loads(Path(run["guard_record"]).read_text(encoding="utf-8"))
            require(record.get("id")==run["id"] and record.get("returncode")==0 and record.get("reason") is None,"guard failed "+run["id"])
            require(record.get("executable_sha256")==plan["executables"][side]["sha256"],"executable mismatch")
            require(record.get("diagnostic_env",{}).get("PREFLOP_MEASURE_MEMORY")=="1","memory monitoring absent")
            require(bool(record.get("memory_peak_bytes")),"missing memory observations")
            rows[side]=verified(run["log"]);memory[side]=record["memory_peak_bytes"]
            require(rows[side]["mode"]==pair["mode"],"wrong mode")
            require(same_existing_file(rows[side]["input"], pair["input"]),"wrong input")
            require(same_existing_file(rows[side]["roundtrip_path"], run["output"]),"wrong output")
        result=compare_rows(rows["baseline"],rows["candidate"])
        result.update(pair=pair["pair"],order=pair["order"],memory_peak_bytes=memory)
        groups.setdefault(pair["case"],[]).append(result)
    summary={}
    for case,rows in groups.items():
        values=[r["reduction_percent"] for r in rows]
        summary[case]={"pairs":len(rows),"median_paired_reduction_percent":statistics.median(values),"min_paired_reduction_percent":min(values),"max_paired_reduction_percent":max(values),"baseline_median_ms":statistics.median(r["baseline_ms"] for r in rows),"candidate_median_ms":statistics.median(r["candidate_ms"] for r in rows),"results":rows}
    return {"retention_decision":"Manual review required: fixed2% threshold plus retained capacity/RSS tradeoffs; identity pass is not speed acceptance.","all_identity_gates_passed":True,"groups":summary,"memory_scope":"Whole-process sampled/OS peak includes untimed save/hash verification, not isolated build/load RSS.","timing_scope":"Only operation_ms; verification and process launch excluded."}
if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument("plan");parser.add_argument("output");args=parser.parse_args()
    result=compare_plan(json.loads(Path(args.plan).read_text(encoding="utf-8")))
    with Path(args.output).open("x",encoding="utf-8") as f:json.dump(result,f,indent=2)
