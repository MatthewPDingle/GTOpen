"""Freeze one fixed E073 complete-solve screen after isolated builds are terminal."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
build=R/'runs/E073-final-build/complete.json';built=old.read(build);assert built['all_compilers_terminal']and built['native_executions']==0
for p,h in built['evidence_sha256'].items():old.pin(p,h)
receipt=old.read(R/'runs/E073-build-manager/build.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
d=R/'runs/E073-kernel-control-r3/complete.json';control=old.read(d);assert control['status']=='pass_scoped_full_show_raw_equivalence' and control['cases']==364 and control['application_kernel_launches']==728 and control['all_owned_children_terminal'] and control['source_main_live_PTX_custody_pass']
H=R/'runs/E073-primary-plan';H.mkdir()
previous="control['status']=='pass_cpu_metadata_and_concrete_ownership' and len(control['cases'])==12 and control['concrete_same_level_ownership_pass'] and control['nonorder_fields_exact']"
current="control['status']=='pass_scoped_full_show_raw_equivalence' and control['cases']==364 and control['application_kernel_launches']==728 and control['all_owned_children_terminal'] and control['source_main_live_PTX_custody_pass']"
for name in ['native.py','assess.py','root-check.py','run.py']:
 code=(R/'runs/E069-primary-plan'/name).read_text(encoding='utf-8').replace('E069','E073').replace('e069','e073').replace("HERE.parent/'accepted-E051'","HERE.parent/'accepted-E051-live-20261018'").replace("ROOT/'runs/accepted-E051'","ROOT/'runs/accepted-E051-live-20261018'").replace('import common_e051 as old','import common_e051_live as old').replace('cpu_control_report','direct_control_report')
 if name in ['native.py','assess.py']:assert code.count(previous)==1;code=code.replace(previous,current)
 compile(code,str(H/name),'exec')
 with(H/name).open('x',encoding='utf-8',newline='\n')as out:out.write(code)
source=old.read(R/'runs/E073-source-host-r2/manifest.json');P=old.read(R/'runs/E069-primary-plan/protocol.json')
P.pop('cpu_control_report',None)
P.update(id='E073-primary',at=old.now(),candidate_owned_sha256=source['candidate_owned_sha256'],build_protocol_sha256=old.sha(R/'runs/E073-build-plan/build-protocol.json'),ordinary_unit_id='V073-unit',control_ids=['V073-unit'],pairs=[{'baseline':'B235','candidate':'E073R1'},{'baseline':'B236','candidate':'E073R2'},{'baseline':'B237','candidate':'E073R3'}],measurement_order=['B235','E073R1','E073R2','B236','B237','E073R3'],direct_control_report={'path':str(d),'sha256':old.sha(d)},source_scope='Only privateGPUriver lower/upper boundary buffers narrowu32to u16, preserving complete logical values and original float body/order. Public CPUplan and all other GPUbuffers/launch/graph/save/quality unchanged. Added checked host packing4temporary allocations/4synchronizations inside complete clocks. Prebuild host accounting completion makes planned/observed continuation bytes exact, with CUDA/upload code unchanged from364direct pairs/728launches. Original resource pointer-decoder failure and D119cvta-only correction retained; same criterion/resources/PTX, no hardware rerun. Complete clocks include all NVRTC/JIT/setup/readback. No complete-solve/broad/material/holdout/cumulative result yet.')
paths=[Path(__file__),build,d,R/'runs/E073-kernel-control-r3/report.json',R/'runs/D119-boundary-load-audit/report.json',R/'runs/E073-resource/report.json',R/'runs/E073-kernel-control-r3/execution-plan.json',R/'runs/E073-build-plan/build-protocol.json',R/'runs/E073-source-host-r2/source-review.json',R/'runs/E073-source-host-r2/manifest.json',Path(P['baseline']['path']),Path(P['baseline_binary']['path']),Path(P['baseline_binary']['manifest']),C/'common_e051_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[H/n for n in ['native.py','assess.py','root-check.py','run.py']]]
for stem in ['E073-feature-solver','E073-solver','E073-postflop_autoresearch']:
 exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp);old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'];paths.extend([exe,mp])
st=old.read(old.ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:assert not(R/'runs'/identity).exists()and not any(x['id']==identity for x in st['experiments'])
for name in ['E073-native-execution','E073-primary-wrapper','E073-primary-manager']:assert not(R/'runs'/name).exists()
for name in ['E073-three-pair-comparison','E073-root-crosscheck']:assert not(R/'comparisons'/name).exists()
P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'protocol.json',P)
def publish(src,key):
 dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,dest)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(src)}
pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()];old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'native_primary_executions':0,'all_compilers_terminal':True,'http_byte_verified_artifacts':pub})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E073');e.update(stage='Ordinary tests then three complete-solve pairs',reason='Both isolated builds finished and accepted source is restored. All 364 direct GPU case pairs passed. The fixed BC/CB/BC screen includes all runtime compilation, setup and readback costs; no speed claim yet.');e['evidence'].append({'label':'Frozen complete-solve screen with 1% cutoff','url':'evidence/'+H.name+'/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E073',stage='E073 complete-solve comparison',activity='Running 84 ordinary tests, then exactly B235/E073R1, E073R2/B236, B237/E073R3. Same quality, unrounded 1% cutoff and strict fixture guard. The live E051 app remains unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
O=R/'runs/E073-primary-manager';O.mkdir();print('E073 primary protocol',old.sha(H/'protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'run.py'),old.sha(H/'protocol.json')],O,'primary',old.env(),2400)
qpath=R/'comparisons/E073-three-pair-comparison/report.json';rootpath=R/'comparisons/E073-root-crosscheck/report.json';q=old.read(qpath);root=old.read(rootpath);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']and root['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}and q['excluded_samples']==[]and q['extension_runs']==0 and q['historical_timing_samples_used']==0
old.custody();assert not(R/'gpu-run.lock').exists();out=R/'runs/E073-initial-closure';out.mkdir()
reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All 18 full non-timing results, 138 checkpoints, 84 ordinary tests and 364 direct GPU case pairs passed. "
if passed:reason+='Initial gate passed; fresh 16-pair confirmation, broad compatibility, actual CPU/host peak/resources/capacity, holdout and cumulative checks remain. Not accepted.'
else:
 why=[]
 if perf['observed_gain_pct']<1:why.append('below the unrounded 1% cutoff')
 guards=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']]
 if guards:why.append('repeatable fixture slowdown: '+', '.join(guards))
 reason+='Rejected: '+'; '.join(why)+'. No extra samples, width/packing/helper/source-scope variants or rescue.'
decision={'id':'E073','at':old.now(),'decision':q['decision'],'performance':perf,'ordinary_units_passed':84,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,'direct_control_report_sha256':old.sha(d),'direct_GPU_cases':364,'direct_GPU_launches':728,'direct_raw_report_sha256':old.sha(R/'runs/E073-kernel-control-r3/report.json'),'assessment_sha256':old.sha(qpath),'root_replay_sha256':old.sha(rootpath),'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,'source_adopted':False,'accepted_and_live_source':'E051','fresh16_broad_material_holdout_cumulative_run':False,'no_exclusions_extensions_pooling':True,'reason':reason};old.save(out/'decision.json',decision)
published=[]
for folder in [H,R/'runs/E073-build-plan',R/'runs/E073-primary-wrapper',R/'runs/E073-native-execution',out,R/'comparisons/E073-three-pair-comparison',R/'comparisons/E073-root-crosscheck']:
 for p in folder.iterdir():
  if p.is_file()and p.suffix in ['.json','.py','.rs','.patch','.log']:published.append(publish(p,folder.name+'/'+p.name))
for phase in ['feature','primary']:
 for p in(R/'runs/E073-final-build'/phase).iterdir():
  if p.is_file()and p.suffix in ['.json','.log']:published.append(publish(p,'E073-final-build-'+phase+'/'+p.name))
for stem in ['E073-feature-solver','E073-solver','E073-postflop_autoresearch']:published.append(publish(R/'binaries'/(stem+'.manifest.json'),'E073-binary-manifests/'+stem+'.manifest.json'))
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E073');e.update(status='measured'if passed else'rejected',correctness='pass',stage='Initial pass; confirmation and broader qualification pending'if passed else'Closed: initial performance gate failed',reason=reason,observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now(),accepted=False);e['evidence'].extend([{'label':'Fixed complete-solve assessment','url':'evidence/E073-three-pair-comparison/report.json'},{'label':'Raw-record and arithmetic replay','url':'evidence/E073-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E073-initial-closure/decision.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E073'if passed else None,stage='E073 fresh confirmation preparation'if passed else'Investigating the next GPU optimization',activity=reason+' Accepted and live E051 remain unchanged, with 12.44% cumulative improvement on the registered benchmark suite.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(out/'publication.json',{'at':old.now(),'http_byte_verified_artifacts':published,'accepted_and_live_source_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E073 private river boundary complete-solve screen'not in raw
entry=f'''

### E073 private river boundary complete-solve screen

D118source/legal-domain proof and D119cvta-only decoder correction retained. CandidateCUDA{P['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu']} unchanged from the sole resource probe and364direct GPUcase pairs/728launches. All full output/input/guard bytes exact, including physical32bit/16bit boundary images; public CPUplan and19other inputs unchanged. The original parser/resource and pre-native runner failures remain preserved. No resource/NVRTC rerun, completed-case repetition or source/width/packing variant. Shared/dynamic/local reservations and queried occupancy/register38unchanged. Three-file final source completes exact continuation planned/observed payload accounting before first integrated build; CUDA/upload code unchanged. Added checked packing4temporary allocations/4explicit synchronizations remain inside clocks. No launch/graph/quality/save change.

Two fresh isolated builds; source restored toE051after each. V073unit84passed/4ignored. Fixed B235/E073R1,E073R2/B236,B237/E073R3; all18full non-timing payloads and138quality records exact. Sum fixture median complete-cycle{perf['baseline_full_cycle_ms']:.10f}to{perf['candidate_full_cycle_ms']:.10f}ms, unrounded gain{perf['observed_gain_pct']:.10f}%. Strict fixture guards{json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Root{root['checks']}raw/arithmetic checks; assessmentSHA{old.sha(qpath)}. {reason}

No exclusions,extensions,historical timing pooling or adoption. Fresh16,broadF32/state/menu/save/resume/continuation,actual material CPU/host+GPUpeak/capacity,holdout/cumulative not yet run forE073. Primary arena fingerprints exact; primary full raw arenas not independently byte-compared. All{len(published)}published files HTTP-byteverified; ownedchildren terminal, accepted source/main/live/protectedPTX unchanged. E051accepted and deployed gain12.4372274192%unchanged. LastprimaryB237; goalactive.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
old.custody();subprocess.run(['git','commit','--only','-m','research: screen private river boundary storage','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody()
print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'report_sha256':old.sha(qpath),'published_files':len(published),'accepted_and_live_source':'E051'}),flush=True)
