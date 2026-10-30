"""Close only a fully observed, rejected E066 screen; preserve every sample."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
Q=ROOT/'comparisons/E066-three-pair-comparison';R=ROOT/'comparisons/E066-root-crosscheck'
q=old.read(Q/'report.json');root=old.read(R/'report.json');P=old.read(ROOT/'runs/E066-primary-plan/protocol.json');perf=q['performance']
assert q['decision']=='rejected' and root['status']=='pass_rejected' and root['checks']==53
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
assert q['excluded_samples']==[] and q['historical_timing_samples_used']==q['extension_runs']==0
assert old.read(ROOT/'runs/E066-primary-manager/complete.json')['all_owned_children_terminal']
for label in ['native','assess','root-check']:
 x=old.read(ROOT/f'runs/E066-primary-manager/{label}.exit.json');assert x['returncode']==0 and x['error'] is x['cleanup'] is None
unit=old.read(ROOT/'runs/V066-unit/report.json');assert unit['test_pass_count']==84
failed=[f for f in perf['fixture_regression_guard'] if f['failed']]
O=ROOT/'runs/E066-closure';assert not O.exists();O.mkdir()
old.save(O/'decision.json',{'id':'E066','at':old.now(),'original_form':'E031','decision':'rejected_complete_cycle_screen','performance':perf,'all18payloads_138checkpoints_exact':True,'ordinary_gpu_units_passed':84,'direct_kernel_pairs':364,'direct_kernel_launches':728,'feasibility_passed':True,'known_resource_warnings':'Static shared1040to1248, nominal registers38to39,128thread theoretical residency12to11in2registered shapes. Fit/default/1326bound passed. These are disclosed risks, not measured materially-free proof.','primary_report_sha256':old.sha(Q/'report.json'),'root_report_sha256':old.sha(R/'report.json'),'fresh16_broad_material_holdout_cumulative_not_run':True,'no_exclusions_pooling_extensions_or_source_variants':True,'source_restored_E051':True,'main_live_protected_ptx_unchanged':True,'candidate_accepted':False,'goal_active':True,'limits':'Observed three-pair registered whole-cycle screen, not universal slowdown or component-cause attribution. Primary full-arena equivalence uses deterministic fingerprints plus raw root/EV/stops/checkpoints, not all arena bytes. Direct kernel controls compare full raw words. Original E031rejection remains frozen; E066is first fresh numerical/speed qualification, now closed including aliases.'})
old.save(O/'checkpoint.json',{'at':old.now(),'goal_turn_progress':'Prospective D108feasibility policy/inventory/helper boundary checks committed before requalification; original E031form exact transfer as E066, freshresource/364raw controls/rootreplay/feature-primarybuilds/84units/3paired solves and closure','goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B200','all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'next':'Next fixed D108docket form D049/E043 (same original source counted once), as E067. Verify original/current accepted baseline entry exact; mechanically transfer exact original candidate entry only, freeze fresh resources/mechanism/ABI before any raw numerical launch. No source variants/composition; no runtime failure retried. E059follows as E068only after E067terminal.','closed_family':'No E031/E066cache size/placement/table/shape/source variants or extra samples. Preserve complete failed outcome.','live_deployment':'Prior automatic approval block remains; no retry/bypass/duplicate permission request.'})
published={}
def put(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
folders=[ROOT/'runs/D108-resource-feasibility-audit',ROOT/'runs/E066-source',ROOT/'runs/E066-resource',ROOT/'comparisons/E066-resource-root-check',ROOT/'runs/E066-kernel-control',ROOT/'comparisons/E066-kernel-control-root-check',ROOT/'runs/E066-build-plan',ROOT/'runs/E066-final-build',ROOT/'runs/E066-primary-plan',ROOT/'runs/E066-native-execution',ROOT/'runs/E066-primary-manager',Q,R,O]+[ROOT/'runs'/identity for identity in P['control_ids']+P['measurement_order']]
for folder in folders:
 for p in folder.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.exe','.pdb','.dll','.obj','.lib','.exp','.bin']:put(p,folder.name+'/'+p.relative_to(folder).as_posix())
for pattern in ['E066-*.py','D108-*.py']:
 for p in (ROOT/'runs').glob(pattern):put(p,'E066-preparation-sources/'+p.name)
old.save(O/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
links=[{'label':'Original offset cache: first complete-solve screen','url':'evidence/'+Q.name+'/report.json'},{'label':'Timing/payload replay','url':'evidence/'+R.name+'/report.json'},{'label':'Preserved rejected qualification','url':'evidence/E066-closure/decision.json'},{'label':'Fixed next source form','url':'evidence/E066-closure/checkpoint.json'}]
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert st['accepted_complete_run']['candidate_id']=='E051';e=next(e for e in st['experiments'] if e['id']=='E066')
 e.update(status='rejected',correctness='pass',accepted=False,stage='Closed: initial complete-solve speed screen failed',baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],reason=f"Original E031shared-offset form: fresh feasibility,364raw pairs,84GPU units,18complete payloads/138checkpoints exact. Complete-cycle gain{perf['observed_gain_pct']:.8f}%, required1%; fixture guards failed:{[f['fixture_id'] for f in failed]}. No variants/resampling/adoption. Resource warnings retained; broad material qualification not run.");e['evidence'].extend(links);st['evidence'].extend(links);st.update(updated_at=old.now(),state='running',active_experiment=None,stage='Next fixed unmeasured source: original actor-map pointer',activity=f"E066original offset cache closed at{perf['observed_gain_pct']:.6f}%gain; exact results but speed screen failed. D108next is originalD049/E043asE067. Accepted E05112.44%cumulative gain unchanged.");old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E066 original offset cache' not in raw
fixture_text='; '.join(f"{f['fixture_id']}: median slowdown{f['median_slowdown_pct']:.10f}%, {f['slower_pairs']}/3paired slowdowns, guard_failed={f['failed']}" for f in perf['fixture_regression_guard'])
note=f"""

### E066 original offset cache: first exact numerical and speed qualification rejected

Under prospectively published/committed D108policy930fa211f6b63c3e28777247c5ed54f759cf4c3e, mechanically transferred exact original E031up_show entry onto E051; original/current baseline entries match exactly. Candidate CUDAc3a58840aab1f69ad5c7e730ae4394f858a88c231b14cccdbd1fec12afacfaa2. No size/placement/table/arithmetic/launch/host/global payload variants. Original E031resource-only rejection remains frozen; E066is attributed first numerical/timing qualification, not new mechanism or reversal of measured old speed.

Resource protocolbd7826e3258c9f48c51cd1df5efaa89f17601a885700bedf88e42dd959b167f6native/compile0; reportae81db1b7fc89d720f5f503db1d26f7ab638619a435b2b6919e4c1065d209ff1. All10registered shapes fit queried default shared/thread limits including1326handbound; monotone4*nh_o+16*m_o<=26520dynamic bytes plus1248static. Nominal38to39registers, staticshared1040to1248, theoretical128thread residency12to11in2shapes are disclosed warnings. Local0/dynamic/maxthreads unchanged;8other entries exact actual/compute75;27parameterABI exact;212Btable and5barriers emitted. Root resource replay is not external independent review or runtime memory/speed proof.

Raw protocol7e2b89d6ad5dcbd482e0d69339208b5f723114000aa875ee084e5796be4bb6e7terminal0:364pairs/728kernel launches,1,687,304full output words,3,065,944actual immutable device input words,1,292,824guards exact. Raw SHA ddf7b1a237ff2291cbc2dd715463584b0a8336da63987cfe7af9bae692e398c5. Root649,016checks and resource/raw PTX byte equality. No old numerical/timing result scored. Fresh integrated feature/primary build protocolc405f9b64dad8c920418c4edd9f772b95485a05259c02705a6a04b74813efbe6, allcompilers0 and acceptedE051restored in finally.

Primary protocola2671fb2c15cdb5cc81e009875eaab2c04ae203c6f24d1ee2f81ec35e986d1a6:84ordinary GPU units/4ignored, then exactlyB198/E066R1,E066R2/B199,B200/E066R3. Every native/assessment/root child terminal0. All18non-timing results/fingerprints and138convergence checkpoints exact. Primary whole-arena equivalence uses fingerprints plus raw root/EV/stops/checkpoints, not allarena bytes; direct kernels used fullraw.

Complete-solve sum fixture medians{perf['baseline_full_cycle_ms']:.10f}to{perf['candidate_full_cycle_ms']:.10f}ms, **{perf['observed_gain_pct']:.10f}%gain**, requiredunrounded1%. {fixture_text}. Report{old.sha(Q/'report.json')};root53checks{old.sha(R/'report.json')}. Reject without universal/cause attribution, exclusions, extensions, timing pooling, sourcevariants, fresh16/broad/material/holdout/cumulative progression or adoption. Resource/CPU/GPU peak/responsiveness no-material-cost requirement not discharged.

All{len(published)}code/log/report/PTX artifacts HTTPbyteverified. Accepted162/main157/live/protectedPTX unchanged; E051cumulative12.4372274192%on qualified suite unchanged. LastprimaryB200. Next fixed D108source D049/E043exact same actor-map form counted once, asE067; freshresource/mechanism/ABI then separately frozen numerical/speed stages, original source scope only. Goal remains active.
"""
nl=b'\r\n' if b'\r\n' in raw else b'\n'
with ledger.open('ab') as f:f.write(note.replace('\n',nl.decode()).encode())
old.custody();print(json.dumps({'status':'E066_rejected_published','gain_pct':perf['observed_gain_pct'],'published':len(published),'failed_fixtures':[x['fixture_id'] for x in failed],'accepted_source':'E051','goal_active':True}),flush=True)
