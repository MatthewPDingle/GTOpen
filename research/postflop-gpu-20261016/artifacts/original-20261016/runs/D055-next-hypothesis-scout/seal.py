from pathlib import Path
import hashlib,json,datetime
H=Path(__file__).resolve().parent;B=H.parents[1];R=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def save(n,d):
    with (H/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,indent=2,ensure_ascii=True);f.write('\n')
assert not (H/'manifest.json').exists()
src=B/'runs/E029-design/base'
pins=load(B/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
refs=[B/'binaries/E020-postflop_autoresearch.manifest.json',B/'runs/D037-showdown-cache-design/census.py',B/'runs/D033-oracle-anchors/anchors.json',B/'runs/E020C1/report.json',B/'comparisons/D033-descriptive-analysis/report.json',B/'runs/D033R1/stdout.log',B/'comparisons/D045-sparse-event-diagnostic/report.json',B/'comparisons/E019-three-pair-comparison/report.json']
for r in ['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/continuation_capacity.rs']:
    assert sha(src/r)==pins[r];refs.append(src/r)
# Preserve mutable source-history evidence rather than pinning a future ledger state.
(H/'references').mkdir(exist_ok=False)
history=R/'research/postflop-gpu-20261016/experiments.md'
(H/'references/experiments.md').write_bytes(history.read_bytes())
for r in ['crates/solver/src/tree.rs','crates/solver/src/range.rs','crates/solver/src/cards.rs']:
    assert sha(R/r)==pins[r]
    (H/'references'/Path(r).name).write_bytes((R/r).read_bytes())
proxy=load(H/'card-work-proxy.json')
dense=load(B/'comparisons/D033-descriptive-analysis/report.json')
report={'id':'D055','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'verdict':'SOURCE_FEASIBLE_SINGLE_INTEGER_SCHEDULING_HYPOTHESIS_UNMEASURED',
 'recommendation':'One bounded stable descending card-list-length scheduling experiment may be considered; no2% headroom or gain is established. No candidate prepared.',
 'accepted_base':'E020 archived bytes, independently of active E029 and its outcome',
 'source_sites':{'kernels.cu:163-169':'Independent card sums and unique s[card] writers','kernels.cu:170-189':'Original thread-index total reduction/barriers/output must remain unchanged','mod.rs:289-300':'Existing fold-card metadata construction','continuation_capacity.rs:37':'Planned53-offset payload would become105; observed actual lengths already general'},
 'representation':'Append52 verified card IDs to each existing53-u32 offset vector; original offset prefix and card-index lists unchanged; no new ABI or device allocation.',
 'added_immutable_device_bytes':416,'new_mutable_workspace_bytes':0,
 'work_proxy_rows':[{k:r[k] for k in ['fixture_id','opponent_player','hands','current_per_warp_max_loop_counts','descending_per_warp_max_loop_counts','current_sum_of_warp_maxima','descending_sum_of_warp_maxima','same_total_scalar_card_loop_additions','same_longest_single_card_loop']} for r in proxy['rows']],
 'timing_evidence':{'D033_paired_up_fold_ms':dense['last_replay_paired_graph_family_ms']['up_fold'],'D033_outer_device_perturbation_pct':dense['device_perturbation_pct'],'limits':'Dense perturbed final replay only, not native share. D045 does not select fold. No card-loop timing or complete-cycle headroom.'},
 'exactness_requirements':['Verified permutation of0..51','Unchanged each-card +0 initializer and ascending original hand-list additions','Unique unchanged s[card] destinations','Unchanged total partial distribution/reduction and all barriers','Correct opponent table at both training/eval sites','Exact actual-kernel outputs before native fullcycle qualification'],
 'performance_risks':['Same scalar additions and longest card loop','Changed shared-bank behavior and scheduling','Extra mapping load, host sorting and416B upload','Full-range proxy unchanged','E019 fold barrier candidate failed fullcycle2%gate'],
 'history_scope':'Current postflop ledger and bounded autoresearch Markdown search; no verified duplicate, not exhaustive. Inspected ledger archived.',
 'official_source':{'url':'https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-best-practices-guide/index.html#branching-and-divergence','use':'General warp control-flow motivation only, no quantitative hardware prediction'},
 'reference_sha256':{str(p):sha(p) for p in refs},'candidate_prepared':False,'compiler_native_gpu_executed':False,'performance_measurement':False,'candidate_accepted':False}
save('report.json',report)
save('manifest.json',{'id':'D055-next-hypothesis-scout','status':'SEALED_SOURCE_ONLY','artifact_sha256':{str(p.relative_to(H)).replace('\\','/'):sha(p) for p in sorted(H.rglob('*')) if p.is_file()},'reference_sha256':report['reference_sha256'],'candidate_prepared':False,'compiler_native_gpu_executed':False})
print(json.dumps({'report_sha256':sha(H/'report.json'),'manifest_sha256':sha(H/'manifest.json'),'proxy_sha256':sha(H/'card-work-proxy.json')}))
