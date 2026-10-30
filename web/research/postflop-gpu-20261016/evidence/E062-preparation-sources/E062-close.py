"""Close original E057's first measured qualification; preserve every outcome."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
Q=ROOT/'comparisons/E062-three-pair-comparison';R=ROOT/'comparisons/E062-root-crosscheck'
q=old.read(Q/'report.json');r=old.read(R/'report.json');P=old.read(ROOT/'runs/E062-primary-plan/protocol.json');perf=q['performance']
assert q['decision']=='rejected' and r['status']=='pass_rejected' and r['checks']==53
assert perf['observed_gain_pct']==-0.9938628266406948
failed=[v for v in perf['fixture_regression_guard'] if v['failed']]
assert [x['fixture_id'] for x in failed]==['rainbow','river']
assert q['excluded_samples']==[] and q['extension_runs']==0 and q['historical_timing_samples_used']==0
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
assert old.read(ROOT/'runs/E062-primary-manager/complete.json')['all_owned_children_terminal']
for name in ['native','assess','root-check']:
 assert old.read(ROOT/f'runs/E062-primary-manager/{name}.exit.json')['returncode']==0
O=ROOT/'runs/E062-closure';O.mkdir()
old.save(O/'decision.json',{'id':'E062','at':old.now(),'original_source_form':'E057','decision':'rejected_first_fresh_source_form_speed_qualification','aggregate_gain_pct':perf['observed_gain_pct'],'minimum_gain_pct':1.0,'fixture_guards':perf['fixture_regression_guard'],'all18results_138checkpoints_exact':True,'ordinary_gpu_units_passed':84,'fresh_direct_kernel_pairs':364,'fresh_direct_kernel_launches':728,'fresh_resource_gate_passed':True,'source_restored_accepted_E051':True,'primary_report_sha256':old.sha(Q/'report.json'),'root_report_sha256':old.sha(R/'report.json'),'no_exclusions_pooling_extensions_or_source_variants':True,'fresh16_broader_material_holdout_cumulative_not_run':True,'historical_E057_decision_unchanged':True,'alias_now_has_known_speed_outcome':True,'not_eligible_for_future_never_timed_exception':True,'D101_fixed_docket_exhausted':True,'candidate_accepted':False,'goal_active':True,'limits':'Three-pair observed complete-cycle screen, no significance/universal slowdown or component-cause claim. Primary equality uses deterministic arena fingerprints and raw root/EV/stops/checkpoints, supplemented by full direct-kernel bytes.','comment_erratum':'The raw Rust wrapper first comment inherited an async-staging label. Pinned candidate CUDA b9c1b260895debf954def29b28804d3cd1cc0b431a668c698d72dda55693cec3 is exactly the E057 prefix mapping. This comment has no execution effect; sealed files unchanged.'})
old.save(O/'checkpoint.json',{'at':old.now(),'current_goal_turn':'E062 exact original E057 form: fresh resources,364raw pairs,2builds,84units,3fixed timing pairs, rejection and publication','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B194','all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'D101_fixed_docket_exhausted':True,'next':'Seek a distinct mechanism tied to measured complete-cycle work. First audit history and exact integer selector/capacity invariants for precomputed per-card correction cutoffs. No E057/E062 mapping/key/guard/width/block/schedule variants or resampling. All current1%/fixture/exactness/fresh16/broad/material/holdout/cumulative gates remain.','live_deployment':'Prior automatic approval block remains; no retry or duplicate approval request.'})
published={}
def put(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
folders=[ROOT/'runs/E062-source',ROOT/'runs/E062-resource',ROOT/'runs/E062-kernel-control',ROOT/'comparisons/E062-kernel-control-root-check',ROOT/'runs/E062-build-plan',ROOT/'runs/E062-final-build',ROOT/'runs/E062-primary-plan',ROOT/'runs/E062-native-execution',ROOT/'runs/E062-primary-manager',Q,R,O]+[ROOT/'runs'/x for x in P['control_ids']+P['measurement_order']]
for folder in folders:
 for p in folder.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.exe','.pdb','.dll','.obj','.lib','.exp','.bin']:put(p,folder.name+'/'+p.relative_to(folder).as_posix())
for p in (ROOT/'runs').glob('E062-*.py'):put(p,'E062-preparation-sources/'+p.name)
old.save(O/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
links=[{'label':'First fresh prefix-mapping complete-cycle result','url':'evidence/'+Q.name+'/report.json'},{'label':'Root timing and payload replay','url':'evidence/'+R.name+'/report.json'},{'label':'Preserved source-form failure','url':'evidence/E062-closure/decision.json'},{'label':'Docket closure and next audit','url':'evidence/E062-closure/checkpoint.json'}]
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert st['accepted_complete_run']['candidate_id']=='E051';e=next(e for e in st['experiments'] if e['id']=='E062')
 e.update(status='rejected',correctness='pass',accepted=False,stage='Closed: first speed screen0.993863%slower;rainbow and river guards fail',baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],reason='Resources,364raw pairs,84GPU units,18complete payloads and138checkpoints passed. Three fixed speed pairs:0.993863%slower aggregate;rainbow0.515039%slower2/3pairs and river7.896681%slower3/3pairs. Exact original E057form now has a measured failure. D101docket exhausted; no variants/extensions/adoption.')
 e['evidence'].extend(links);st['evidence'].extend(links);st.update(updated_at=old.now(),state='running',active_experiment=None,stage='Distinct mechanism audit',activity='E062rejected; D101fixed docket complete. Audit precomputed per-card correction boundaries as a distinct possibility. Accepted E05112.437227%cumulative gain unchanged.');old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E062 original prefix mapping' not in raw
note=f'''

### E062 original prefix mapping -- first fresh speed qualification rejected

Second and final D101fixed docket entry: exact original E057source, mechanically retained on byte-identical acceptedE051baseline. Candidate CUDA b9c1b260895debf954def29b28804d3cd1cc0b431a668c698d72dda55693cec3. Full32word tiles map k XOR((k>>5)&31), partial tiles identity, only power-of-two chunk>1; all five logical prefix accesses mapped. Same floating operations, buffers, launches and27parameterABI. CPU address proof retained with D093total-prefix-read broadcast correction. No tuning or composition. Original nominal-only rejection remains historical; this is attributed requalification.

Fresh resource protocol4c6e886bb48212300cc5317a8fcad7353adccb86729b6a95eb632cdf570b2896, report2a5e028953670147347429096b6c916436d09e9684e8b7e9a6f65dc216514a03. All10registered shapes pass unchanged D094filter: reported38to40registers, same1280perwarp/5120per128threadCTA; local0/static1040/dynamic bytes/maxthreads1024/occupancies unchanged. Other8entries exact; all four complete baseline/candidate PTX files for compute120/75 match retained originalE057files. No physical-counter or speed inference.

Fresh raw protocol9f233b2c3952c69037ca89ba0981610692794c6a25efe4a80d0c707b805b74e3:364pairs/728kernels,1,687,304full output words,3,065,944actual immutable input words,1,292,824guards exact. CPUrank/geometry/nonfinite/zero/tails/rounding controls retained; root649,014checks and resource/raw PTX byte equality. Raw digestddf7b1a237ff2291cbc2dd715463584b0a8336da63987cfe7af9bae692e398c5is expected identical to other exact controls because corpus/recorded values match; fresh outputs were executed. Native75665terminal0. Wrapper first comment inherited an async label; actual pinned full CUDA and all compiled files are prefix mapping; sealed files unchanged, erratum recorded.

Fresh feature and primary builds protocol0144b3b2ea4ae207e676fd009531ba6771d6c63d252898278b72f83f435fb4e0, session1304terminal0; acceptedE051restored in finally. Ordinary GPU-only84pass/4ignored. Primary protocolba7f6e072ec1852ca1ef3a5f0ad27796fcd47b86d76b5ef69bd5b3cc9ef070d4 freezes V062-unit,B192/E062R1,E062R2/B193,B194/E062R3. Manager14870terminal, every native/assess/root child exit0. All18non-timing payload/fingerprints and138convergence checkpoints exact. Primary arena equality is deterministic fingerprints plus raw root/EV/stops/checkpoints, not direct full arena bytes.

Sum per-fixture complete-cycle medians {perf['baseline_full_cycle_ms']:.10f}to{perf['candidate_full_cycle_ms']:.10f}ms, **{perf['observed_gain_pct']:.10f}%gain** (slower overall). Rainbow0.5150393073%slower with2/3slower pairs and river7.8966809390%slower with3/3fail strict fixture guards. Two-tone median1.5103680228%slower but1/3slower pairs, so its guard does not trigger. Assessment{old.sha(Q/'report.json')};root53checks{old.sha(R/'report.json')}. No significance/universal slowdown or component-cause attribution.

Reject with no exclusions, historical timing pooling, source variants or extension samples. Fresh16/broad/material/holdout/cumulative progression not run; no adoption. E057/E062alias has known timing failure and cannot use never-timed exception. D101fixed docket exhausted. All{len(published)}source/log/report/PTX files HTTP-byte verified; accepted162/main157/live/protectedPTX and accepted cumulative12.4372274192%unchanged. Next audit a distinct per-card cutoff precomputation mechanism before code/timing; preserve all failed forms. Goal active.
'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',nl));old.custody()
print(json.dumps({'status':'second_form_rejected_and_published','gain_pct':perf['observed_gain_pct'],'failed_fixtures':[x['fixture_id'] for x in failed],'published':len(published),'D101_docket_exhausted':True,'goal_active':True}),flush=True)
