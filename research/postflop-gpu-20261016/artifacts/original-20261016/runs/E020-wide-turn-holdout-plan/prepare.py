"""Prepare source-only prospective holdout evidence; no native solver/build/GPU."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, itertools, json, math

HERE = Path(__file__).resolve().parent
RAW = HERE.parent.parent
REPO = Path(r"X:\Dev\GTOpen-gpu-research-20261016")
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name, value):
    with (HERE/name).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n')

# Explicit 169 classes, each weight one: no unsupported "random" shortcut.
ranks = '23456789TJQKA'
tokens = [r+r for r in ranks]
tokens += [ranks[h]+ranks[l]+s for h in range(13) for l in range(h) for s in ('s','o')]
assert len(tokens) == len(set(tokens)) == 169
full_range = ','.join(tokens)
sizing = {'bet':[{'PotPct':33.0},{'PotPct':75.0}], 'raise':[{'PotPct':75.0}], 'donk':[]}
config = {'board':'Ks7h2dQh','range_oop':full_range,'range_ip':full_range,
          'tree':{'starting_pot':10.0,'effective_stack':100.0,'rake_pct':0.05,'rake_cap':3.0,
                  'oop':[sizing.copy() for _ in range(3)],'ip':[sizing.copy() for _ in range(3)],
                  'allin_threshold':0.85,'add_allin':False,'max_raises':1,
                  'carry_aggressor_through_checks':False}}
save('fixture.json',config)

# A no-clamping/no-donk-omission upper bound, not a measured GpuPlan census.
nh = math.comb(48,2); mo = math.comb(47,2)
street_action_nodes=2+4+4
street_fold_nodes=4+4
street_show_endpoints=1+4+4
street_action_edges=2*3+4*3+4*2
chance_nodes=street_show_endpoints
river_copies=chance_nodes*48
nodes=street_action_nodes+street_fold_nodes+chance_nodes+river_copies*(street_action_nodes+street_fold_nodes+street_show_endpoints)
action_edges=street_action_edges*(1+river_copies)
reach_blocks_sum=2+action_edges+2*chance_nodes*48
staging=(reach_blocks_sum+nodes)*nh*4
arenas=action_edges*nh*8
bound={'method':'source-derived safe tree upper bound, not actual native build or GPU allocation',
       'root_hands_each':nh,'river_valid_hands_each':mo,'river_cards':48,
       'street_action_nodes_upper':street_action_nodes,'street_fold_nodes_upper':street_fold_nodes,
       'street_show_endpoints_upper':street_show_endpoints,'street_action_edges_upper':street_action_edges,
       'turn_tree_nodes_upper':nodes,'total_action_edges_upper':action_edges,
       'full_reach_blocks_both_upper':reach_blocks_sum,'full_staging_bytes_upper':staging,
       'full_f32_regret_and_strategy_bytes_upper':arenas,
       'public_vram_estimate_upper_bytes_including_512MiB_slack':staging+arenas+512*1024**2,
       'baseline_show_dynamic_bytes':8*mo+4*nh,'candidate_show_dynamic_bytes':16*mo+4*nh,
       'static_shared_bytes_from_D037':1040,
       'actual_holdout_occupancy_queried':False,
       'resource_warning':'5->3 occupancy is measured only at conservative1326 shape, not asserted for this1128/1081 shape',
       'native_assertions_required':['hands=[1128,1128]','tree nodes<=11691','every visited river count=1081',
                                     'both show_shared formulas match13160/21808 bytes','public estimate<=2GiB']}
assert nh==1128 and mo==1081 and nodes==11691
assert bound['public_vram_estimate_upper_bytes_including_512MiB_slack'] < 1024**3
save('source-derived-bounds.json',bound)

inputs = {
 'frozen-primary.rs':REPO/'crates/solver/tests/postflop_autoresearch.rs',
 'source-tree.rs':REPO/'crates/solver/src/tree.rs',
 'source-game.rs':REPO/'crates/solver/src/game.rs',
 'source-range.rs':REPO/'crates/solver/src/range.rs',
 'source-store.rs':REPO/'crates/solver/src/store.rs',
 'source-solve-cli.rs':REPO/'crates/solver/src/bin/solve_cli.rs',
 'E015-mod.rs':RAW/'runs/D037-showdown-cache-design/candidate/base/mod.rs',
 'E015-kernels.cu':RAW/'runs/D037-showdown-cache-design/candidate/base/kernels.cu',
 'E020-mod.rs':RAW/'runs/D037-showdown-cache-design/candidate/mod.rs',
 'E020-kernels.cu':RAW/'runs/D037-showdown-cache-design/candidate/kernels.cu',
 'D037-resource-report.json':RAW/'runs/D037-showdown-cache-resource/report.json',
 'D037-independent-manifest.json':RAW/'comparisons/D037-independent-review/manifest.json',
}
identities=[]
for name,path in inputs.items():
    data=path.read_bytes()
    with (HERE/name).open('xb') as f:f.write(data)
    identities.append({'source':str(path),'copy':name,'sha256':sha(HERE/name)})
assert sha(HERE/'frozen-primary.rs')=='f13d79410a22f140c05cb9a822fe9685c2180e5baeda4b625d52ae03feebd327'
save('reference-identities.json',identities)

protocol={
 'id':'E020-wide-turn-holdout-plan','at':datetime.now(timezone.utc).isoformat(),
 'status':'SOURCE_ONLY_PROSPECTIVE_CONDITIONAL_ON_PRIMARY_PASS','executed':False,
 'primary_results_inspected':False,'native_run_ids_reserved':False,
 'purpose':'Additional wide-range non-regression check for the increased up_show dynamic shared allocation; never changes the fixed primary metric or gates.',
 'entry_gate':'Only after E020 fixed primary three-pair qualification passes, exact state checks pass and independent raw audit passes. If primary fails, retain this protocol as terminally inapplicable, with zero holdout executions.',
 'fixture_id':'wide-turn-full169','fixture_file':'fixture.json','fixture_sha256':sha(HERE/'fixture.json'),
 'algorithm':'dcfr','storage':'compressed','use_isomorphism':True,'fresh_iteration':0,
 'target_pct':0.3,'check_every':20,'max_iterations':400,
 'stop_rule':'Exactly the original primary loop: first every20 check at or below0.3% of starting pot, otherwise stop at400 and fail quality. Same checks/discounts for both arms. No outcome-driven limit, target, storage, menu, range, cache policy or sample-count edits.',
 'candidate_base':'accepted E015; no E016/E017/E018/E019 code',
 'source_delta':'Only the exact D037 two-file cache candidate: kernels.cu07565169... and mod.rsce71fa3b...; full SHA identities copied alongside.',
 'harness_plan':{
  'kind':'one tiny independent fixed holdout integration-test/standalone evaluator, prepared and reviewed additively only if entry gate passes',
  'reuse':'Reuse frozen-primary.rs lifecycle boundaries, convergence loop and state_fingerprint/fingerprint_store/Fingerprint helper text unchanged. Replace only fixed fixture selection/config loading with fixture.json; add bounded admission and exact state artifact output after timing. Keep original checkout evaluator and all control workloads byte-identical.',
  'why_not_existing_cli':'solve-cli accepts JSON but GPU mode forces F32, synchronizes every iteration, uses check10 in single mode, lacks complete-cycle measurement and exact full-state output; existing postflop perf/state tests hardcode narrow inputs. Do not label those timings equivalent.',
  'minimum_new_code':'one fixed case, no parameter sweep, no profiler, no new kernel/lifecycle API, no numerical algorithm rewrite',
  'source_freeze':'Freeze identical evaluator/helper/config bytes for E015 and E020 before any holdout native run. Root seals concrete command/runID/binary/manifest/rlib bindings and independent review; this protocol does not authorize unreviewed execution.',
 },
 'timing':{
  'metric':'full_cycle_ms','start':'before Spot build and CPU arena allocation',
  'end':'after complete GPU readback and synchronization',
  'included':['tree/range/river-table construction','CPU storage allocation','admission checks inside evaluator','GPU initialization including runtime NVRTC/JIT','ordinary captured/eager iteration path','every20 exploitability checks','full readback','small flushed progress records'],
  'excluded':['Cargo/rustc compilation','post-timing fingerprints and exact state file output','process launch and destructor teardown'],
  'secondary':['build_ms','init_ms','solve_ms','readback_ms','external process wall_ms including teardown (also includes exact-state evidence; diagnostic only)'],
  'warm_cache_note':'Fresh process per run, existing persistent driver cache retained; no cache resets or selective warmup. This is not a cold-cache qualification.',
  'no_profile':True,
 },
 'holdout_resource_check':'If the entry gate passes, before six timings root performs one separately archived no-launch query using the exact D037 baseline/candidate CUDA and compilation options at this actual nh=1128/m_max=1081 shape: baseline dynamic13160 and candidate21808 bytes. Record actual registers/static shared/maxthreads/occupancy, without a conditional rescue or altered workload. Native GpuPlan counts independently bind the formula to the fixture; the prior1326 occupancy5->3 is only the motivation.',
 'order':['B1','C1','C2','B2','B3','C3'],
 'pairs':[['B1','C1'],['B2','C2'],['B3','C3']],
 'arms':{'B':'accepted E015 compiled against identical holdout evaluator','C':'exact E020 two-file candidate compiled against identical holdout evaluator'},
 'cohort_policy':'Exactly three fresh processes per binary, all retained. No trimming, retries, rescoring, cohort extension or favorable restart. Operational errors stop this protocol for independent review with evidence retained; failed numerical/quality/performance outcomes are not operational retries.',
 'exactness':{
  'checks':'All every20 exploit_bits, stopping iteration, target_met and all config/algorithm/storage/iso/count fields exact across all six runs; finite exploit and target reached in all.',
  'state':'After timed full readback, compare all four CPU stores including every I16/U16 q word and every f32 scale bit, all lengths/type tags, root_strategy_bits and full state_fingerprint object. Use primary helper fingerprints plus streaming framed raw store bytes to a new per-run state.bin, compared byte-for-byte with bounded host buffers; SHA256 is provenance, not a substitute for byte comparison.',
  'scope':'Exact full compressed CPU learning state and exploitability, not raw unsynchronized GPU float buffers. Existing broader F32/state/menu/resume controls remain mandatory separately.',
  'evidence_excluded_from_metric':True,
 },
 'gate':{
  'statistic':'100*(median(C.full_cycle_ms)/median(B.full_cycle_ms)-1)',
  'paired_statistic':'100*(C_i.full_cycle_ms/B_i.full_cycle_ms-1)',
  'reject':'Reject unconditional E020 adoption if median slowdown strictly>3% AND paired slowdown strictly>3% in at least2of3 pairs.',
  'correctness':'Any exactness mismatch or target failure prevents qualification regardless of timing.',
  'no_gain_requirement':True,'no_primary_score_merge':True,
  'ambiguity':'Retain all timing ranges and pair values. Passing this bounded guard does not prove equivalence or absence of all broad-range regressions; no statistical-significance claim.',
  'no_rescue':'No automatic threshold-based cache path, conditional kernel rescue, or hidden fixture-specific optimization. A future different candidate requires its own prospective evidence.',
 },
 'admission':{
  'serialization':'Root only, one build or GPU process at a time under existing gpu-run.lock; existing live-solve GET-only refusal before each run; no server mutation.',
  'device':'RTX5090, total>=30GiB and free>=4GiB before child; stop rather than downgrade engine/device/ranges.',
  'host_available_min_bytes':16*1024**3,'disk_free_reserve_bytes':50*1024**3,'output_reservation_bytes':2*1024**3,
  'tree_max_nodes':20000,'public_estimate_max_bytes':2*1024**3,'gpu_new_with_budget_bytes':2*1024**3,
  'checks':'Spot::new_with_limit(config,Some(20000)); assert hands[1128,1128], nodes<=11691 and public estimate<=2GiB before Solver allocation. Inspect existing Spot.river.get for all48 legal single-river Dealt values: assert each sorted player count1081 and record max1081 plus both show_shared formulas. Report tree_bytes and arena_bytes_for(Compressed). Keep these small admission checks inside timed construction; do not build a duplicate GpuPlan or context. GpuSolver::new_with_budget(&host,2GiB) performs its existing checked planned-buffer budget test before device allocation and must succeed. No CPU fallback, no second simultaneous solver. Unexpected shape is invalid.',
  'memory_note':'source-derived public estimate upper bound is below1GiB including existing512MiB slack, so2GiB budget and4GiB free gate are deliberately conservative on32GiB device. Native measured allocation still required; estimate is not measured residency.',
  'timeouts':'Root runner fixes build timeout1800s and each native process600s before execution, file stdout/stderr,10s heartbeat, explicit child cleanup inside lock. No GPU telemetry polling during native timing; pre/post only.',
 },
 'publication':'Separate holdout report/evidence; never alter original fixture medians or accepted gains from these timings. Acceptance remains root decision after all primary, broad controls and holdout gates. Deployment separate.',
 'limits':['One deliberately broad turn fixture, not all ranges/menus/hardware.','No actual holdout occupancy or performance measured during preparation.','No source/fixture result tuning after primary or holdout outcomes.']
}
save('protocol.json',protocol)
print(json.dumps({'prepared':str(HERE),'fixture_sha256':sha(HERE/'fixture.json'),'protocol_sha256':sha(HERE/'protocol.json'),'bounds':bound},indent=2))
