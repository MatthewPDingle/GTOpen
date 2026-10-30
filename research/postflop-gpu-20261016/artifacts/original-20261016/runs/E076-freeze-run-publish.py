"""Freeze and own one fixed three-pair complete-solve screen of CFV row sharing."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not (R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
build=R/'runs/E076-final-build/complete.json';built=old.read(build);assert built['all_compilers_terminal']and built['native_executions']==0
for p,h in built['evidence_sha256'].items():old.pin(p,h)
receipt=old.read(R/'runs/E076-build-manager/build.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
d=R/'runs/E076-kernel-control/complete.json';control=old.read(d)
assert control['status']=='pass_scoped_full_in_place_CFV_raw_equivalence'and control['cases']==819 and control['alias_cases']==138 and control['application_kernel_launches']==1638 and control['all_owned_children_terminal']and control['source_main_live_PTX_custody_pass']
H=R/'runs/E076-primary-plan';assert not H.exists();H.mkdir()
for name in ['native.py','assess.py','root-check.py','run.py']:
 code=(R/'runs/E075-primary-plan'/name).read_text(encoding='utf-8').replace('E075','E076').replace('e075','e076').replace('pass_scoped_full_up_action_raw_equivalence','pass_scoped_full_in_place_CFV_raw_equivalence')
 compile(code,str(H/name),'exec');(H/name).write_text(code,encoding='utf-8',newline='\n')
source=old.read(R/'runs/E076-source/manifest.json');P=old.read(R/'runs/E075-primary-plan/protocol.json')
P.update(id='E076-primary',at=old.now(),candidate_owned_sha256=source['candidate_owned_sha256'],build_protocol_sha256=old.sha(R/'runs/E076-build-plan/build-protocol.json'),ordinary_unit_id='V076-unit',control_ids=['V076-unit'],pairs=[{'baseline':'B241','candidate':'E076R1'},{'baseline':'B242','candidate':'E076R2'},{'baseline':'B243','candidate':'E076R3'}],measurement_order=['B241','E076R1','E076R2','B242','B243','E076R3'],direct_control_report={'path':str(d),'sha256':old.sha(d)},source_scope=source['source_scope']+' All12 compiled CFV maps match independently frozen D122, other51 fields/capacities/structs exact.819 direct GPU pairs include138 in-place cases: full logical outputs and expected physical images/inputs/guards exact. Complete clocks include CPU plan allocation/coloring/temporary work, NVRTC/JIT, all setup/readback. No whole-solve/broad/material result yet.')
paths=[Path(__file__),build,d,R/'comparisons/E076-kernel-control-root-check/report.json',R/'runs/D122-cfv-lifetimes/protocol.json',R/'runs/D122-cfv-lifetimes/report.json',R/'runs/E076-plan-control/report.json',R/'runs/E076-plan-control/protocol-r2.json',R/'runs/E076-kernel-control/protocol.json',R/'runs/E076-build-plan/build-protocol.json',R/'runs/E076-source/manifest.json',R/'runs/E076-source/candidate-plan.rs',Path(P['baseline']['path']),Path(P['baseline_binary']['path']),Path(P['baseline_binary']['manifest']),C/'common_e051_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[H/n for n in ['native.py','assess.py','root-check.py','run.py']]]
for stem in ['E076-feature-solver','E076-solver','E076-postflop_autoresearch']:
 exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp);old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'];paths.extend([exe,mp])
st=old.read(old.ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:assert not (R/'runs'/identity).exists()and not any(x['id']==identity for x in st['experiments'])
for name in ['E076-native-execution','E076-primary-wrapper','E076-primary-manager']:assert not (R/'runs'/name).exists()
for name in ['E076-three-pair-comparison','E076-root-crosscheck']:assert not (R/'comparisons'/name).exists()
P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'protocol.json',P)
def publish(src,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes(),key
 else:shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(src)}
pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()];old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'native_primary_executions':0,'all_compilers_terminal':True,'HTTP_byte_verified_artifacts':pub})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E076');e.update(stage='Ordinary tests then three complete-solve pairs',reason='Both isolated builds are terminal and accepted source restored.12 metadata cases and819 raw GPU pairs passed. Fixed BC/CB/BC complete-solve clocks include CPU layout/coloring costs, GPU/NVRTC/JIT setup and full readback. No speed claim yet.');e['evidence'].append({'label':'Frozen complete-solve screen with1% cutoff','url':'evidence/E076-primary-plan/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E076',stage='E076 complete-solve comparison',activity='Run84 ordinary tests, then exactly B241/E076R1, E076R2/B242, B243/E076R3. Same quality, unrounded1% cutoff and strict fixture guard. All CPU layout costs included. Accepted/live E051 unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
O=R/'runs/E076-primary-manager';O.mkdir();print('E076 primary protocol',old.sha(H/'protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'run.py'),old.sha(H/'protocol.json')],O,'primary',old.env(),2400)
qpath=R/'comparisons/E076-three-pair-comparison/report.json';rootpath=R/'comparisons/E076-root-crosscheck/report.json';q=old.read(qpath);root=old.read(rootpath);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']and root['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}and q['excluded_samples']==[]and q['extension_runs']==0 and q['historical_timing_samples_used']==0
old.custody();assert not (R/'gpu-run.lock').exists();out=R/'runs/E076-initial-closure';out.mkdir()
reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All18 full non-timing results,138 checkpoints,84 ordinary tests,12 CPU metadata cases and819 direct GPU pairs passed. "
if passed:reason+='Initial gate passed; separately frozen fresh16, broad compatibility, actual CPU/host+GPU peak/resources/capacity, holdout and cumulative checks remain. Not accepted.'
else:
 why=[]
 if perf['observed_gain_pct']<1:why.append('below the unrounded1% cutoff')
 guards=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']]
 if guards:why.append('repeatable fixture slowdown: '+', '.join(guards))
 reason+='Rejected: '+'; '.join(why)+'. No extra samples, layout/source/placement variants or rescue.'
decision={'id':'E076','at':old.now(),'decision':q['decision'],'performance':perf,'ordinary_units_passed':84,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,'CPU_metadata_cases':12,'direct_control_report_sha256':old.sha(d),'direct_GPU_cases':819,'direct_GPU_alias_cases':138,'direct_GPU_launches':1638,'direct_raw_report_sha256':old.sha(R/'comparisons/E076-kernel-control-root-check/report.json'),'assessment_sha256':old.sha(qpath),'root_replay_sha256':old.sha(rootpath),'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,'source_adopted':False,'accepted_and_live_source':'E051','fresh16_broad_material_holdout_cumulative_run':False,'no_exclusions_extensions_pooling':True,'reason':reason};old.save(out/'decision.json',decision)
published=[]
for folder in [H,R/'runs/E076-build-plan',R/'runs/E076-primary-wrapper',R/'runs/E076-native-execution',out,qpath.parent,rootpath.parent]:
 for p in folder.iterdir():
  if p.is_file()and p.suffix in ['.json','.py','.rs','.patch','.log']:published.append(publish(p,folder.name+'/'+p.name))
for phase in ['feature','primary']:
 for p in (R/'runs/E076-final-build'/phase).iterdir():
  if p.is_file()and p.suffix in ['.json','.log']:published.append(publish(p,'E076-final-build-'+phase+'/'+p.name))
for stem in ['E076-feature-solver','E076-solver','E076-postflop_autoresearch']:published.append(publish(R/'binaries'/(stem+'.manifest.json'),'E076-binary-manifests/'+stem+'.manifest.json'))
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E076');e.update(status='measured'if passed else'rejected',correctness='pass',stage='Initial pass; confirmation and broader qualification pending'if passed else'Closed: initial performance gate failed',reason=reason,observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now(),accepted=False);e['evidence'].extend([{'label':'Fixed complete-solve assessment','url':'evidence/E076-three-pair-comparison/report.json'},{'label':'Raw-record arithmetic replay','url':'evidence/E076-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E076-initial-closure/decision.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E076'if passed else None,stage='E076 fresh confirmation preparation'if passed else'Investigating the next GPU optimization',activity=reason+' Accepted/live E051 remain unchanged:12.44% cumulative improvement on the registered benchmark suite.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(out/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':published,'accepted_and_live_source_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E076 CFV lifetime-sharing complete-solve screen'not in raw
entry=f'''

### E076 CFV lifetime-sharing complete-solve screen

The sole D122-admitted original-schedule Rust allocator, source SHA {P['candidate_owned_sha256']['crates/solver/src/gpu/plan.rs']}, remains unchanged from12 compiled metadata controls and819 direct GPU pairs/1638 launches. Every CFV map matches the separately frozen lifetime model and all51 other fields/capacities/struct sizes match accepted plans.138 numerical cases exercise one-action parent/child in-place rows. All12,375,858 full output words,5,199,114 actual immutable words and10,240,828 guards match the explicitly expected per-arm physical layout; logical parent outputs and full regret/strategy arrays exact. CUDA source/PTX, float operations, worklists, graph/level schedule, launch geometry, reach metadata, ABI and solve/save behavior unchanged. CPU temporary flags/buckets/coloring/scans remain inside complete-cycle clocks; modeled payload savings alone establish no speed/material conclusion.

Two fresh isolated feature/primary builds terminal0; accepted E051 restored after each. V076-unit84 passed/4 ignored. Fixed B241/E076R1,E076R2/B242,B243/E076R3; all18 full non-timing payloads and138 quality records exact. Sum fixture median complete cycle {perf['baseline_full_cycle_ms']:.10f} to {perf['candidate_full_cycle_ms']:.10f}ms; unrounded gain {perf['observed_gain_pct']:.10f}%. Strict fixture guards {json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Root {root['checks']} raw/arithmetic checks; assessment SHA {old.sha(qpath)}. {reason}

No exclusions, extensions, historical timing pooling or adoption. Fresh16, broad F32/state/menu/save/resume/continuation, actual CPU/host+GPU peak/capacity/responsiveness, holdout and cumulative not run for E076. Primary full arena fingerprints exact; primary full raw arena bytes not independently compared. All{len(published)} published files HTTP byte verified. All owned children terminal; accepted162/main163/live/protected2PTX exact. E051 accepted/deployed cumulative12.4372274192% unchanged. Last primary B243; goal active.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: screen original-schedule CFV row sharing','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'report_sha256':old.sha(qpath),'published_files':len(published),'accepted_and_live_source':'E051'}),flush=True)
