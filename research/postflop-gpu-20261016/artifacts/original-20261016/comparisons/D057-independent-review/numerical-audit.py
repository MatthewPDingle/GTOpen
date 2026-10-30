from pathlib import Path
import json, hashlib, math, struct, statistics, re, datetime
ROOT=Path(r"S:\GTOpen-research\postflop-gpu-20261016")
HERE=Path(__file__).resolve().parent
OUTPUT=HERE/"numerical-validation.json"
assert not OUTPUT.exists(), "Preserve previous numerical audit"
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
def read(rel, expected=None):
    p=ROOT/rel
    digest=sha(p)
    if expected is not None: assert digest==expected,rel
    inputs[str(p)]=digest
    return p.read_text(encoding="utf-8")
def js(rel, expected=None): return json.loads(read(rel,expected))
assessed=js("comparisons/D057-evaluation-envelope-diagnostic/report.json","ac6f63332bb3d0c512a7096cb3c1c8fee8de138e6a0c5129c9e90e9c241be350")
anchors=js("runs/D057-evaluation-envelope-plan/anchors.json","b63e5855c82d5418769967aafcaf35e5e3a9b5a5b15dade08e0c6cc599317145")
source=read("runs/D057-evaluation-envelope-diagnostic/source/r2/candidate-evaluation_device_events.rs","09e35e16097b6b68ad85df4b26855bbdc66bc82ceb56db0ea13d69f040056fdb")
source_manifest=js("runs/D057-evaluation-envelope-diagnostic/source/r2/source-manifest.json","2b761d68451d7e7d92f06fb06034466201f7554549420553f785511bf0eab5cd")
schema=js("runs/D057-evaluation-envelope-diagnostic/source/r2/output-schema.json")
assert inputs[str(ROOT/"runs/D057-evaluation-envelope-diagnostic/source/r2/output-schema.json")]==source_manifest["artifact_sha256"]["output-schema.json"]
assert read("runs/D057-build/candidate-evaluation_device_events.rs")==source
native=js("runs/D057R1/report.json")
raw=read("runs/D057R1/stdout.log",native["stdout_sha256"])
assert native["returncode"]==0 and native["test_pass_count"]==1
assert native["binary_sha256"]==assessed["binary_sha256"]=="608d6436ef39596a10ca2c2e1f2eaa51809f25ec2472bfab82026351ce8eac77"
assert re.search(r"test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; 88 filtered out;",raw)
markers=[json.loads(line.split("D057_EVAL_DIAGNOSTIC ",1)[1]) for line in raw.splitlines() if "D057_EVAL_DIAGNOSTIC " in line]
assert len(markers)==22 and [x["stage"] for x in markers]==schema["expected_stage_order"]
by=lambda stage:[x for x in markers if x["stage"]==stage]
expected_bits={x["iteration"]:x["exploit_bits"] for x in anchors["convergence_anchors"]}
assert sorted(expected_bits)==list(range(20,201,20))
assert json.loads(re.search(r'const ANCHOR_JSON: &str = r#"(.*)"#;',source).group(1))==anchors
assert json.loads(re.search(r'const CONVERGENCE_JSON: &str = r#"(.*)"#;',source).group(1))==anchors["convergence_anchors"]
originals=[]
for run in ["B038","E015C1","E020C1"]:
    report=js(f"runs/{run}/report.json")
    row=next(x for x in report["results"] if x["fixture_id"]=="two-tone")
    assert row["config"]==anchors["config"]
    assert row["state_fingerprint"]==anchors["final_state_fingerprint"]
    text=read(f"runs/{run}/stdout.log",report["stdout_sha256"])
    records=[json.loads(line.split("AUTORESEARCH_STAGE ",1)[1]) for line in text.splitlines() if "AUTORESEARCH_STAGE " in line]
    points=[x for x in records if x.get("fixture_id")=="two-tone" and x.get("stage")=="convergence_check"]
    assert len(points)==10 and {x["iteration"]:x["exploit_bits"] for x in points}==expected_bits
    originals.append(run)
for x in by("warm_check"):
    t=x["iteration"];assert x["exploit_bits"]==expected_bits[t]
    assert x["normal_production_method_both_arms"] and x["ordinary_eval_warmed"] and x["instrumented_eval_warmed"]
    assert x["ordinary_eval_graph_present"]==x["instrumented_eval_graph_present"]==(t>=40)
assert [x["iteration"] for x in by("warm_check")]==list(range(20,141,20))
adm=by("admission")[0]
assert adm==assessed["admission"]
assert adm["dual_device_required_with_reserve"]==2*adm["device_per_arm_payload_bytes"]+adm["device_reserve_bytes"]
assert adm["host_additional_required"]==2*adm["cpu_arena_bytes_per_arm"]+2*adm["pinned_bytes_per_arm"]+adm["raw_compare_max_bytes"]+adm["host_reserve_bytes"]
assert adm["device_free_bytes"]>=adm["dual_device_required_with_reserve"] and adm["host_free_after_spot_and_plan"]>=adm["host_additional_required"]
assert adm["device_arena_elements"]==[93381294,110745280]
float32=lambda x:struct.unpack("<f",struct.pack("<f",x))[0]
floatbits=lambda x:struct.unpack("<I",struct.pack("<f",x))[0]
raw_count=root_count=0
raw_rows=[]
for row in by("raw_exact"):
    t=row["iteration"];assert row["pass"] and row["post_evaluation"] and not row["before_exploitability"] and not row["cfv_scratch_compared"]
    assert row["chunk_floats"]==1048576 and row["peak_pairwise_snapshot_bytes"]==8388608
    arrays=row["arrays"];assert len(arrays)==12
    identities=[(x["array"],x["player"],x.get("mode")) for x in arrays]
    assert identities==[(a,p,None) for p in [0,1] for a in ["regrets","strategy","reach","weights"]]+[("evaluation_root",p,m) for p in [0,1] for m in [0,1]]
    for x in arrays:
        assert isinstance(x["entries"],int) and x["entries"]>0 and re.fullmatch("[0-9a-f]{16}",x["hash"])
        p=x["player"]
        if x["array"] in ["regrets","strategy"]:assert x["entries"]==adm["device_arena_elements"][p]
        if x["array"] in ["weights","evaluation_root"]:assert x["entries"]==anchors["hands"][p]
        if x["array"]=="reach":assert x["entries"]==[117863172,141110400][p] and x["entries"]%anchors["hands"][p]==0
        raw_count+=x["entries"]
        if x["array"]=="evaluation_root":root_count+=x["entries"]
    ta=float(t)**1.5
    discounts=[floatbits(ta/(ta+1.0)),floatbits(0.5),floatbits((float(t)/(t+1.0))**2)]
    assert row["discount_bits"]==discounts
    raw_rows.append({"iteration":t,"pairwise_f32_locations":sum(x["entries"] for x in arrays),"discount_bits":discounts})
assert [x["iteration"] for x in by("raw_exact")]==[140,160,180,200]
assert raw_count==assessed["raw_f32_words_compared"]==2668913816
assert root_count==assessed["logical_root_words_compared"]==4624
for x in by("checkpoint_exact"):
    assert x["post_evaluation"] and x["raw_and_compressed_pass"] and x["exploit_bits"]==expected_bits[x["iteration"]]
assert [x["iteration"] for x in by("checkpoint_exact")]==[140,160,180,200]
final=by("final_anchor_exact")[0]["state_fingerprint"]
assert final==anchors["final_state_fingerprint"]==assessed["final_state_fingerprint"]
assert final["hash"]=="9dd12ac305ce542f" and final["exploit_bits"]==expected_bits[200]
assert final["iteration"]==200 and final["iteration_le_bytes"]==[200,0,0,0]
assert len(final["root_strategy_bits"])==2*anchors["hands"][0]
assert sum(a["bytes"] for a in final["arenas"])==adm["cpu_arena_bytes_per_arm"]==1391071288
for a in final["arenas"]:
    assert a["entries"]==[156627930,185752640][a["player"]]
    assert a["scale_entries"]==1346813
    assert a["bytes"]==a["entries"]*2+a["scale_entries"]*4
    assert a["kind"]==("i16" if a["arena"]=="regrets" else "u16")
rows=[]
for i,x in enumerate(by("batch")):
    t=[160,180,200][i];assert x["checkpoint"]==t and x["iterations"]==20
    assert x["arm_order"]==[["ordinary","instrumented"],["instrumented","ordinary"],["ordinary","instrumented"]][i]
    assert x["event_record_counts"]==[i+1,i+1] and x["post_both_arm_completion"]
    assert x["ordinary_exploit_bits"]==x["instrumented_exploit_bits"]==expected_bits[t]
    a,b=x["ordinary_host_batch_ms"],x["instrumented_host_batch_ms"]
    assert math.isfinite(a) and math.isfinite(b) and a>0 and b>0
    change=(b/a-1.0)*100.0
    assert change==x["host_batch_change_pct"] and abs(change)==x["abs_host_batch_change_pct"]
    assert x["within_10pct"]==(abs(change)<=10.0)
    ms=x["instrumented_evaluation_device_envelope_ms"]
    assert math.isfinite(ms) and ms>=0 and float32(ms)==ms
    assert x["near_resolution"]==(ms<=float32(0.0005))
    ar=assessed["outer_batches"][i]
    for key1,key2 in [("ordinary_host_batch_ms","ordinary_host_batch_ms"),("instrumented_host_batch_ms","instrumented_host_batch_ms"),("host_batch_change_pct","host_change_pct"),("abs_host_batch_change_pct","abs_host_change_pct"),("instrumented_evaluation_device_envelope_ms","instrumented_evaluation_device_envelope_ms")]:assert x[key1]==ar[key2]
    rows.append({"iteration":t,"ordinary_host_batch_ms":a,"instrumented_host_batch_ms":b,"recomputed_change_pct":change,"abs_change_lte_10pct":abs(change)<=10.0,"evaluation_device_envelope_ms":ms})
vals=[x["evaluation_device_envelope_ms"] for x in rows]
assert assessed["evaluation_device_envelope_ms"]=={"samples":vals,"median":statistics.median(vals),"min":min(vals),"max":max(vals)}
assert all(x["abs_change_lte_10pct"] for x in rows) and assessed["usefulness_pass"]
graph=by("graph_metadata")[0]
assert graph["ordinary"]==graph["instrumented"] and graph["iteration"]==140 and not graph["raw_pointer_or_argument_comparison"]
meta=graph["ordinary"];assert sum(meta["node_kinds"].values())==meta["node_count"]
assert len(meta["kernel_descriptors_sorted"])==meta["node_kinds"]["CU_GRAPH_NODE_TYPE_KERNEL"]
complete=by("complete")[0]
assert complete["checked_cleanup"] and complete["event_handles"]==2 and complete["event_record_counts"]==[3,3] and complete["evaluation_intervals"]==3
assert not complete["accepted_performance_claim"] and not complete["candidate_accepted"]
assert assessed["exactness_pass"] and not assessed["accepted_performance_claim"] and not assessed["candidate_accepted"] and not assessed["deployment_changed"]
# Bind numerical source meaning without claiming retained raw snapshots.
for text in ['if x.to_bits()!=y.to_bits()', 'x.as_slice()==y.as_slice()', 'xs.as_slice().iter().zip(ys.as_slice()).all(|(x,y)|x.to_bits()==y.to_bits())', 'compare_post_raw(native,instrumented,iteration)?;', 'compare_cpu(host_a,host_b)?;', 'first!=anchor["final_state_fingerprint"] || second!=first']:
    assert text in source,text
assert source.index('compare_cpu(host_a,host_b)?;')<source.index('"stage":"checkpoint_exact"')
inputs[str(Path(__file__).resolve())]=sha(Path(__file__))
result={"id":"D057-numerical-audit","created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"verdict":"PASS_SCOPED_NUMERICAL_MARKERS_AND_ARITHMETIC","findings":[],"marker_count":22,"all10_anchor_bits_both_arms_exact":True,"anchor_source_runs":originals,"matched_post_evaluation_checkpoints":[140,160,180,200],"pairwise_raw_f32_locations_compared_by_native_assertions":raw_count,"logical_root_locations_included":root_count,"discount_words_per_arm_per_checkpoint":3,"raw_checkpoint_arithmetic":raw_rows,"full_cpu_q_scale_direct_equality_enforced_before_each_checkpoint_marker":True,"full_cpu_bytes_per_arm":1391071288,"gpu_compact_arena_entries":adm["device_arena_elements"],"cpu_full_arena_entries":[156627930,185752640],"full_final_state_object_equals_all_immutable_anchors":True,"final_hash":final["hash"],"final_root_strategy_bit_words":len(final["root_strategy_bits"]),"recomputed_samples":rows,"all_three_host_usefulness_guards_pass":True,"evaluation_device_envelope_ms":{"samples":vals,"median":statistics.median(vals),"min":min(vals),"max":max(vals)},"graph_metadata_counts":meta["node_kinds"],"admission_arithmetic_checked":True,"native_exit0_and_one_filtered_test_pass":True,"binary_sha256_bound":native["binary_sha256"],"checked_input_sha256":inputs,"scope_limits":["Audit recomputes JSON/count/statistical arithmetic and compares complete anchor objects; it does not rerun CUDA.","Billions of raw device values and full CPU stores were compared directly inside the source-pinned successful native test; those large arrays are not retained for independent byte replay. Logged FNV summaries alone are not treated as proof of raw equality.","Raw reach/root state is post-evaluation. Unknown CFV scratch is excluded. Compact GPU lengths and full CPU lengths remain distinct.","Device envelope is event-perturbed evaluation only, not host/check wall time, family/kernel attribution, native full-solve fraction, removable headroom or speedup. The<=10%whole-batch host guard does not bound event-interval bias.","Full build/provenance/custody/restoration audit belongs to the separate reviewer."],"compiler_native_gpu_executed_by_auditor":False,"performance_acceptance":False,"candidate_accepted":False,"source_or_status_modified":False}
OUTPUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"verdict":result["verdict"],"report_sha256":sha(OUTPUT),"script_sha256":sha(Path(__file__)),"raw_locations":raw_count,"median_envelope_ms":statistics.median(vals),"host_change_pct":[x["recomputed_change_pct"] for x in rows]}))
