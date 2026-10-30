"""Freeze and own exactly three complete-solve pairs of the D130 host overlap."""
from pathlib import Path
import json,re,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
build=R/'runs/E079-final-build/complete.json';built=old.read(build);assert built['all_compilers_terminal']and built['native_executions']==0
for p,h in built['evidence_sha256'].items():old.pin(p,h)
receipt=old.read(R/'runs/E079-build-manager/build.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
d=R/'runs/D130-plan-context-overlap/report.json';control=old.read(d);assert control['admit_one_integrated_trial']and control['fixed_six_fresh_processes_complete']and len(control['full_metadata_raw_replays'])==18 and control['ability_mock_controls']==18 and control['all_owned_children_terminal']and control['source_main_live_PTX_custody_pass']
H=R/'runs/E079-primary-plan';assert not H.exists();H.mkdir()
for name in['native.py','assess.py','root-check.py','run.py']:
 code=(R/'runs/E078-primary-plan'/name).read_text(encoding='utf-8').replace('E078','E079').replace('e078','e079').replace('exact two-source scope','exact one-source scope')
 if name in['native.py','assess.py']:
  predicate="assert control['admit_one_integrated_trial'] and control['fixed_six_fresh_processes_complete'] and len(control['full_metadata_raw_replays'])==18 and control['ability_mock_controls']==18 and control['all_owned_children_terminal'] and control['source_main_live_PTX_custody_pass']"
  code,n=re.subn(r"assert control\['status'\][^\n]+",predicate,code);assert n==1
 if name=='native.py':code=re.sub(r'\b85\b','86',code)
 compile(code,str(H/name),'exec');(H/name).write_text(code,encoding='utf-8',newline='\n')
source=old.read(R/'runs/E079-source/manifest.json');P=old.read(R/'runs/E078-primary-plan/protocol.json')
P.update(id='E079-primary',at=old.now(),candidate_owned_sha256=source['candidate_owned_sha256'],build_protocol_sha256=old.sha(R/'runs/E079-build-plan/build-protocol.json'),ordinary_unit_id='V079-unit',control_ids=['V079-unit'],pairs=[{'baseline':'B250','candidate':'E079R1'},{'baseline':'B251','candidate':'E079R2'},{'baseline':'B252','candidate':'E079R3'}],measurement_order=['B250','E079R1','E079R2','B251','B252','E079R3'],direct_control_report={'path':str(d),'sha256':old.sha(d)},source_scope=source['scope']+' D130 passed 18 full plan snapshots and 18 cleanup/error mocks. The component saved145.855ms but its river setup regressed31.3545ms; this remains unresolved and receives no full-solve exception. All original CPU plan/budget, context/stream setup, NVRTC/JIT, quality solving and full readback remain within complete clocks. CUDA source/arithmetic/launches and payload sizes are unchanged. No full-solve gain or material-cost qualification yet.')
paths=[Path(__file__),build,d,R/'runs/D130-plan-context-overlap/protocol.json',R/'runs/D130-plan-context-overlap/execution-plan.json',R/'runs/D130-plan-context-overlap/ability-report.json',R/'runs/E079-build-plan/build-protocol.json',R/'runs/E079-source/manifest.json',R/'runs/E079-source/candidate-mod.rs',R/'runs/E079-source/source-review.json',Path(P['baseline']['path']),Path(P['baseline_binary']['path']),Path(P['baseline_binary']['manifest']),C/'common_e051_live.py',C/'protected-main.json',old.REPO/'crates/solver/src/gpu/kernels.cu',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[H/n for n in['native.py','assess.py','root-check.py','run.py']]]
for stem in['E079-feature-solver','E079-solver','E079-postflop_autoresearch']:
 exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp);old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'];paths.extend([exe,mp])
st=old.read(old.ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:assert not(R/'runs'/identity).exists()and not any(x['id']==identity for x in st['experiments'])
for name in['E079-native-execution','E079-primary-wrapper','E079-primary-manager']:assert not(R/'runs'/name).exists()
for name in['E079-three-pair-comparison','E079-root-crosscheck']:assert not(R/'comparisons'/name).exists()
P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'protocol.json',P)
def publish(src,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes(),key
 else:shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(src)}
pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()];old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'native_primary_executions':0,'all_compilers_terminal':True,'HTTP_byte_verified_artifacts':pub})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E079');e.update(stage='Ordinary tests, then three complete-solve pairs',reason='Both fresh builds are terminal and accepted source is restored. Run 86 ordinary tests before the fixed BC/CB/BC full-solve comparison. The river component regression is unresolved; no guard is waived. No full-solve speed claim yet.');e['evidence'].append({'label':'Frozen complete-solve screen with 1% cutoff','url':'evidence/E079-primary-plan/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E079',stage='E079 complete-solve comparison',activity='Run 86 ordinary tests, then exactly B250/E079R1, E079R2/B251, B252/E079R3. Same quality, unrounded 1% cutoff, strict fixture guards, and all setup costs. Accepted and live E051 remain unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
O=R/'runs/E079-primary-manager';O.mkdir();print('E079 primary protocol',old.sha(H/'protocol.json'),flush=True);old.child([sys.executable,'-B',str(H/'run.py'),old.sha(H/'protocol.json')],O,'primary',old.env(),2400)
qpath=R/'comparisons/E079-three-pair-comparison/report.json';rootpath=R/'comparisons/E079-root-crosscheck/report.json';q=old.read(qpath);root=old.read(rootpath);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']and root['status']==('pass_initial_timing_only'if passed else'pass_rejected');assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}and q['excluded_samples']==[]and q['extension_runs']==0 and q['historical_timing_samples_used']==0
old.custody();assert not(R/'gpu-run.lock').exists();out=R/'runs/E079-initial-closure';out.mkdir();reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All 18 full non-timing results, 138 checkpoints, and 86 ordinary tests passed. "
if passed:reason+='Initial gate passed; separately frozen fresh16 confirmation, broad compatibility, actual CPU and memory costs, capacity, holdout, and cumulative checks remain. Not accepted.'
else:
 why=[]
 if perf['observed_gain_pct']<1:why.append('below the unrounded 1% cutoff')
 guards=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']]
 if guards:why.append('repeatable fixture slowdown: '+', '.join(guards))
 reason+='Rejected: '+'; '.join(why)+'. No extra samples, threshold/thread/helper/scope/placement/eligibility variants, or rescue runs.'
decision={'id':'E079','at':old.now(),'decision':q['decision'],'performance':perf,'ordinary_units_passed':86,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,'component_full_plan_snapshots':18,'component_lifecycle_mocks':18,'component_control_report_sha256':old.sha(d),'CUDA_source_unchanged':True,'assessment_sha256':old.sha(qpath),'root_replay_sha256':old.sha(rootpath),'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,'source_adopted':False,'accepted_and_live_source':'E051','fresh16_broad_material_holdout_cumulative_run':False,'no_exclusions_extensions_pooling':True,'reason':reason};old.save(out/'decision.json',decision)
published=[]
for folder in[H,R/'runs/E079-build-plan',R/'runs/E079-primary-wrapper',R/'runs/E079-native-execution',out,qpath.parent,rootpath.parent]:
 for p in folder.iterdir():
  if p.is_file()and p.suffix in['.json','.py','.rs','.patch','.log']:published.append(publish(p,folder.name+'/'+p.name))
for phase in['feature','primary']:
 for p in(R/'runs/E079-final-build'/phase).iterdir():
  if p.is_file()and p.suffix in['.json','.log']:published.append(publish(p,'E079-final-build-'+phase+'/'+p.name))
for stem in['E079-feature-solver','E079-solver','E079-postflop_autoresearch']:published.append(publish(R/'binaries'/(stem+'.manifest.json'),'E079-binary-manifests/'+stem+'.manifest.json'))
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E079');e.update(status='measured'if passed else'rejected',correctness='pass',stage='Initial pass; confirmation and broader qualification pending'if passed else'Closed: initial performance gate failed',reason=reason,observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now(),accepted=False);e['evidence'].extend([{'label':'Fixed complete-solve assessment','url':'evidence/E079-three-pair-comparison/report.json'},{'label':'Raw-record arithmetic replay','url':'evidence/E079-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E079-initial-closure/decision.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E079'if passed else None,stage='E079 fresh confirmation preparation'if passed else'Investigating the next GPU optimization',activity=reason+' Accepted and live E051 remain unchanged: 12.44% cumulative improvement on the registered benchmarks.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(out/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':published,'accepted_and_live_source_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E079 plan/context overlap complete-solve screen'not in raw
entry=f'''

### E079 plan/context overlap complete-solve screen

Exact one-host-file source remains frozen {json.dumps(P['candidate_owned_sha256'],separators=(',',':'))}. CPU plan/fullF32/compressed budget work and primary-context/stream setup retain original bodies; one scoped worker overlaps them on original trees>=65536nodes, smaller trees serial. Join/error priority/panic cleanup/OSspawn fallback/root rebind match D130. No CUDA source, compiler flag, kernel/arithmetic, payload/layout/graph/quality/save change. D13018 full plan snapshots/18mocks pass; component145.855ms saving and31.3545ms river regression retained, no component timing pooled into full-solve score or river exemption. ServerMEM_CTX counterevidence and CPU/driverTLS/speculative budget-error resource costs remain material questions.

Two fresh isolated feature/primary builds terminal0, acceptedE051 restored after each. Frozen primary {old.sha(H/'protocol.json')}, V079-unit86passed/4ignored (includes added18mock lifecycle test and serial/scoped stream-copy test with active primary owner; CUDA-unavailable skip convention retained). Fixed B250/E079R1,E079R2/B251,B252/E079R3; all18full non-timing payloads/138quality checkpoints exact. Sum fixture-median complete cycle {perf['baseline_full_cycle_ms']:.10f} to {perf['candidate_full_cycle_ms']:.10f}ms, unrounded gain {perf['observed_gain_pct']:.10f}%. Strict fixture guards {json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Root {root['checks']}raw/arithmetic checks; assessment {old.sha(qpath)}. {reason}

No exclusions/extensions/historical pooling/adoption. Fresh16,broadF32/state/menu/save/resume/continuation,actual CPU/host+GPUpeak/capacity/responsiveness,holdout/cumulative not run for E079. Primary full arena fingerprints exact; primary raw arenas not independently byte-compared. All{len(published)}published files HTTPbyteverified; all owned children terminal, accepted162/main163/live/protected2PTX exact. E051accepted/deployed12.4372274192% unchanged. Last primaryB252,goalactive.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: screen exact plan-context overlap with complete-solve clocks','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'report_sha256':old.sha(qpath),'published_files':len(published),'accepted_and_live_source':'E051'}),flush=True)
