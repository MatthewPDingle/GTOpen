"""Publish the complete initial result without changing its scientific outcome."""
import json, shutil, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
Q=ROOT/'comparisons/E056-three-pair-comparison';R=ROOT/'comparisons/E056-root-crosscheck'
q=old.read(Q/'report.json');r=old.read(R/'report.json');perf=q['performance'];passed=perf['primary_timing_pass']
assert r['status']==('pass_initial_timing_only' if passed else 'pass_rejected') and r['aggregate_gain_pct']==perf['observed_gain_pct']
assert q['excluded_samples']==[] and q['historical_timing_samples_used']==0 and q['extension_runs']==0
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
P=old.read(ROOT/'runs/E056-primary-plan/protocol.json');D=old.read(ROOT/'runs/D092-action-arity-order/report.json')
W=old.read(ROOT/'runs/E056-primary-wrapper/complete.json');assert W['all_children_terminal'] and W['decision']==q['decision']
O=ROOT/'runs/E056-initial-closure';assert not O.exists();O.mkdir()
decision={'at':old.now(),'id':'E056','decision':q['decision'],'observed_gain_pct':perf['observed_gain_pct'],'minimum_gain_pct':1.0,'fixture_regression_guards':perf['fixture_regression_guard'],'ordinary_units_passed':84,'all18full_nontiming_result_payloads_138checkpoints_exact':True,'primary_whole_arena_fingerprints_match':True,'primary_raw_arena_bytes_compared':False,'cpu_metadata_cases':12,'all53fields_captured':True,'cpu_concrete_ownership_checks':D['root_checks'],'assessment_sha256':old.sha(Q/'report.json'),'root_sha256':old.sha(R/'report.json'),'source_restored':'E051','source_adopted':False,'fresh_confirmation_broader_material_holdout_cumulative_not_run':True,'no_exclusion_pooling_extension_rescue':True,'goal_active':True}
old.save(O/'decision.json',decision)
published=[]
def put(src,prefix):
    rel='evidence/'+prefix+'/'+src.name;dest=old.ar.DASHBOARD/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==src.read_bytes(),dest
    else:shutil.copyfile(src,dest)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+rel,timeout=15) as response:assert response.read()==src.read_bytes()
    published.append({'path':str(src),'url':rel,'sha256':old.sha(src)})
for dirname in ['D092-action-arity-order','E056-source','E056-build-plan','E056-primary-plan','E056-primary-wrapper','E056-native-execution','E056-initial-closure']:
    folder=ROOT/'runs'/dirname
    for src in folder.iterdir():
        if src.is_file() and src.suffix in ['.json','.py','.rs','.patch','.log']:put(src,dirname)
for phase in ['feature','primary']:
    for src in (ROOT/'runs/E056-final-build'/phase).iterdir():
        if src.is_file() and src.suffix in ['.json','.log']:put(src,'E056-final-build-'+phase)
for folder in [Q,R]:
    for src in folder.iterdir():
        if src.is_file():put(src,folder.name)
for stem in ['E056-feature-solver','E056-solver','E056-postflop_autoresearch']:put(ROOT/'binaries'/(stem+'.manifest.json'),'E056-binary-manifests')
reason=(f"Initial aggregate gain {perf['observed_gain_pct']:.6f}%. All18 full results,138 checkpoints,84 units and12 CPU metadata/ownership cases passed. ")
if passed:reason+='Initial performance gate passed; separate fresh16 and broader/resource/compatibility/holdout/cumulative checks remain. No adoption yet.'
else:
    why=[]
    if perf['observed_gain_pct']<1:why.append('below the unrounded1% cutoff')
    failed=[g['fixture_id'] for g in perf['fixture_regression_guard'] if g['failed']]
    if failed:why.append('repeatable fixture slowdown: '+', '.join(failed))
    reason+='Rejected: '+'; '.join(why)+'. No extra samples, ordering-key/arity/threshold variant rescue or adoption.'
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);assert st['research_policy']['minimum_aggregate_gain_pct']==1
    e=next(x for x in st['experiments'] if x['id']=='E056')
    e.update(status='measured' if passed else 'rejected',correctness='pass',stage='Initial pass; fresh confirmation and broader qualification pending' if passed else 'Closed: initial performance gate failed',reason=reason,observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now())
    e['evidence'].extend([{'label':'Fixed three-pair complete-cycle assessment','url':'evidence/E056-three-pair-comparison/report.json'},{'label':'Root raw-record and arithmetic replay','url':'evidence/E056-root-crosscheck/report.json'},{'label':'Initial decision; accepted source unchanged','url':'evidence/E056-initial-closure/decision.json'}])
    st.update(updated_at=old.now(),state='running',active_experiment='E056' if passed else None,stage='E056 fresh confirmation preparation' if passed else 'Next independent GPU hotspot investigation',activity=reason+' Accepted E051 research source and cumulative gain remain unchanged.')
    old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D092 and E056 ordering-only controls' not in raw
entry=f'''

### D092 and E056 ordering-only controls

User-directed current policy remains unrounded >=1% with exactness and no repeatable fixture slowdown/material tradeoff. E005/E014 already reordered shared lists as part of direct-kernel composites; this is the first isolated all-arity ordering intervention in the reviewed history, using unchanged existing kernels/dispatch/spans/launches and one in-place CPU sort per depth. It does not prove an instruction-cache bottleneck or reduce intra-CTA divergence. Sorting/locality costs count in the complete cycle.

D092 compiled exact accepted and candidate Plan modules plus an exact local game.rs copy off-tree for crate-private access. Twelve separate CPU processes cover three canonical configurations x iso off/on x compact/full arenas. All53 fields captured; all52 nonordering fields bitwise equal, actual capacities/struct sizes equal, per-level node multisets preserved, concrete down-reach/up-CFV/learning-interval independence passed {D['root_checks']:,} root checks. Raw metadata {sum(c['raw_bytes'] for c in D['cases']):,} bytes retained with SHA256 identities. CPU component timings are diagnostic only. Preparation's nested-quote parse failure was preserved and corrected before compilation or native output.

E056 candidate plan SHA256 {P['candidate_owned_sha256']['crates/solver/src/gpu/plan.rs']}. Only this source changed during isolated feature/primary builds, acceptedE051 restored in finally. CUDA source/ABI and host launch structure unchanged; actual graph/memory/broader compatibility qualification is still required before adoption. V056-unit:84passed/4ignored. Fixed B183/E056R1,E056R2/B184,B185/E056R3: all18 full non-timing results and138 checkpoints exact. Sum fixture medians {perf['baseline_full_cycle_ms']:.10f} -> {perf['candidate_full_cycle_ms']:.10f}ms; aggregate {perf['observed_gain_pct']:.10f}%. Decision {q['decision']}. Strict guards {json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Root {r['checks']} arithmetic/raw checks passed; no external independent review or significance claim. No excluded, historical pooled or extension samples. No adoption.

{reason} All{len(published)} source/result/log artifacts HTTP-byte verified. Fresh16 confirmation, broader/F32/save/resume/continuation/material/holdout/cumulative not run yet. Main/live/PTX and acceptedE051 source remain unchanged. Last primary baseline B185. Goal active.
'''
newline=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+entry.encode('utf-8').replace(b'\n',newline))
checkpoint={'at':old.now(),'goal_active':True,'current_goal_turn':'progress: complete12-case CPU metadata/ownership controls, ordering-only candidate builds, fixed initial screen and root replay','accepted_source':'E051','accepted_cumulative_gain_pct':st['accepted_complete_run']['observed_gain_pct'],'last_primary_baseline':'B185','all_owned_sessions_terminal':True,'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'next':'Freeze a separate fresh16 confirmation, then all broad/material/holdout/cumulative gates before adoption.' if passed else 'Investigate a distinct GPU mechanism. Do not rescue closed E056 with ordering-key/actor/arity/threshold/sort variants or extra timing. Prior closed hypotheses remain closed.','live_deployment':'Prior automatic approval review block remains; do not retry or ask duplicate permission.'}
old.save(O/'checkpoint.json',checkpoint);put(O/'checkpoint.json','E056-initial-closure')
old.save(O/'publication.json',{'at':old.now(),'http_bytes_verified':True,'published':published,'accepted_source_unchanged':True})
old.custody();print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'http_byte_verified_files':len(published),'accepted_source':'E051','goal_active':True}),flush=True)
