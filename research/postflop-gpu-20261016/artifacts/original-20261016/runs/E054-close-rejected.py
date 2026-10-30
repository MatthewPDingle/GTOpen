"""Publish and close E054 only if its fixed initial screen rejects it."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
Q=ROOT/'comparisons/E054-three-pair-comparison';R=ROOT/'comparisons/E054-root-crosscheck';q=old.read(Q/'report.json');r=old.read(R/'report.json');P=old.read(ROOT/'runs/E054-primary-plan/protocol.json');perf=q['performance']
assert q['decision']=='rejected' and perf['primary_timing_pass'] is False and r['status']=='pass_rejected' and r['checks']==53 and r['aggregate_gain_pct']==perf['observed_gain_pct']
assert q['excluded_samples']==[] and q['extension_runs']==0 and q['historical_timing_samples_used']==0
O=ROOT/'runs/E054-closure';O.mkdir()
old.save(O/'decision.json',{'at':old.now(),'id':'E054','decision':'rejected','accepted_source':'E051','gain_pct':perf['observed_gain_pct'],'minimum_gain_pct':1.0,'strict_fixture_guards':perf['fixture_regression_guard'],'all18full_results_138checkpoints_exact':True,'ordinary_tests_passed':84,'raw_kernel_cases_passed':819,'raw_kernel_launches':1638,'all_parent_child_rows_disjoint':True,'source_restored_and_never_promoted':True,'confirmation_broader_holdout_cumulative_not_run':True,'no_variant_rescue_or_extra_samples':True,'resource_report_sha256':old.sha(ROOT/'runs/E054-resource/report.json'),'raw_root_report_sha256':old.sha(ROOT/'comparisons/E054-kernel-control-root-check/report.json'),'primary_report_sha256':old.sha(Q/'report.json'),'root_report_sha256':old.sha(R/'report.json'),'goal_active':True})
directories=[(ROOT/'runs/E054-source','E054-source'),(ROOT/'runs/E054-resource','E054-resource'),(ROOT/'comparisons/E054-resource-root-check','E054-resource-root-check'),(ROOT/'runs/E054-kernel-control','E054-kernel-control-native'),(ROOT/'comparisons/E054-kernel-control-root-check','E054-kernel-control-root-check'),(ROOT/'runs/E054-build-plan','E054-build-plan'),(ROOT/'runs/E054-final-build','E054-final-build'),(ROOT/'runs/E054-primary-plan','E054-primary-plan'),(ROOT/'runs/E054-native-execution','E054-native-execution'),(Q,Q.name),(R,R.name),(O,O.name)]+[(ROOT/'runs'/identity,identity) for identity in P['control_ids']+P['measurement_order']]
published={}
def put(src,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
 if dst.exists():assert dst.read_bytes()==data,key
 else:dst.write_bytes(data)
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
 published[key]=old.sha(src)
for directory,prefix in directories:
 for src in directory.rglob('*'):
  if src.is_file() and src.suffix not in ['.exe','.pdb'] and '__pycache__' not in src.parts:put(src,prefix+'/'+src.relative_to(directory).as_posix())
for src in (ROOT/'runs').glob('E054-*.py'):put(src,'E054-scripts/'+src.name)
old.save(O/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published,'no_production_changes':True})
failed=[g for g in perf['fixture_regression_guard'] if g['failed']]
reasons=[]
if perf['observed_gain_pct']<1:reasons.append('aggregate gain below1%')
for f in failed:reasons.append(f["fixture_id"]+' median slower with'+str(f['slower_pairs'])+'/3slower pairs')
reason='; '.join(reasons)
links=[{'label':label,'url':'evidence/'+key} for label,key in [('E054 complete fixed3pair result','E054-three-pair-comparison/report.json'),('E054 root raw/arithmetic replay','E054-root-crosscheck/report.json'),('E054 preserved rejection and scope','E054-closure/decision.json')]]
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert st['accepted_complete_run']['candidate_id']=='E051';e=next(x for x in st['experiments'] if x['id']=='E054');e.update(status='rejected',stage='Closed: '+reason,correctness='pass',accepted=False,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],reason='84units/819raw GPU cases/18full results/138checkpoints exact. '+reason+'. No confirmation, broader qualification, adoption or rescue.');e['evidence'] +=links;st['evidence'] +=links;st.update(updated_at=old.now(),state='running',stage='E054 closed; next hotspot investigation',activity='AcceptedE051 retains12.437227%cumulative suite gain. D085 validated activity profiling supplies measured direction for further research.',active_experiment=None);old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';data=ledger.read_bytes();assert b'### E054 early parent CFV store' not in data
fixture_text='; '.join(f"{f['fixture_id']} median {-f['observed_gain_pct']:.10f}% slowdown, {sum(x['fixture_gain_pct'][f['fixture_id']]<0 for x in q['pairs'])}/3slower pairs" for f in q['fixtures'])
text=f'''
### E054 early parent CFV store -- rejected

D086 uses D085's measured action-update ranking to test one unlocked-own-node store scheduling change: publish the completed out to the original parent CFV row immediately before the unchanged regret loop. E051 strategy scheduling, all float expressions/summation order, pointer qualifiers, locked/opponent paths, launch/layout/ABI/host/graphs/allocations/quality remain unchanged. Production GpuPlan::build has disjoint even/odd scratch pools and separately cached terminal rows; adjacent levels never alias. All819direct-case actual parent rows are disjoint from every actual child input row, including na>8reloads. Separate learning/CFV owned device buffers and stream dependencies remain unchanged.

Compute120 resource gate: up_action body changes with62registers,64local bytes,0static/dynamic shared,1024maxthreads and64/128/256occupancies16/8/4 unchanged. Full20parameterABI and eight other entries exact. Resource root {old.sha(ROOT/'comparisons/E054-resource-root-check/report.json')}. No SM75 or universal hardware claim.

Whole frozen819case/1638launch matrix passes:12,375,858full output words,5,199,114actual immutable device words and10,240,828guard checks exact. Native per-arm address witnesses and actual raw slot maps prove within-CFV parent/child nonaliasing as well as separate mutable buffers. Root decoder63,899checks {old.sha(ROOT/'comparisons/E054-kernel-control-root-check/report.json')}. Finite matrix and root source review only, not external independent audit.

Fresh feature/primary builds restore acceptedE051 after each phase.84ordinary units pass/4ignored. Fixed B177/E054R1,E054R2/B178,B179/E054R3 complete cycles give{perf['baseline_full_cycle_ms']:.10f}to{perf['candidate_full_cycle_ms']:.10f}ms, **{perf['observed_gain_pct']:.10f}%gain**. {fixture_text}. All18full non-timing payloads and138checkpoints exact. Decision: {reason}.

Assessment {old.sha(Q/'report.json')} and53check root raw/arithmetic replay {old.sha(R/'report.json')} preserve the complete result. No exclusion, historical timing pooling, extension, store-location/factor/launch-bound/cache variant rescue, confirmation, broader/capacity/holdout/cumulative qualification or adoption. All evidence HTTPbyteverified. AcceptedE051/main/live/PTX remain exact; accepted cumulative12.4372274192%unchanged. Last actual baselineB179; goal active.
'''
nl=b'\r\n' if b'\r\n' in data else b'\n';ledger.write_bytes(data+text.encode('utf-8').replace(b'\n',nl));old.custody()
old.save(O/'checkpoint.json',{'at':old.now(),'current_goal_turn':'progress: validated D085 low-overhead activity profiling; E054 source/resources/raw/native screen completed with preserved rejection','goal_active':True,'accepted_source':'E051','owned_children_active':False,'source_main_live_ptx_exact':True,'last_primary_baseline':'B179','accepted_cumulative_gain_pct':st['accepted_complete_run']['observed_gain_pct'],'closure_sha256':old.sha(O/'decision.json'),'publication_sha256':old.sha(O/'publication.json'),'next':'Choose genuinely new measured hotspot work. Do not revive closed early-parent-store, register-cap, cache-width, factor or alias-qualifier variants without new independent evidence.','live_deployment':'Prior automatic approval block remains; do not retry or ask duplicate permission.'});put(O/'checkpoint.json',O.name+'/checkpoint.json')
print(json.dumps({'status':'rejected_and_published','reason':reason,'gain_pct':perf['observed_gain_pct'],'http_verified_files':len(published),'accepted_source':'E051','accepted_cumulative_gain_pct':st['accepted_complete_run']['observed_gain_pct']}),flush=True)
