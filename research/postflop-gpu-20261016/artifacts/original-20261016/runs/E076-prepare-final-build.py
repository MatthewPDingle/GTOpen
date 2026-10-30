"""Freeze two isolated integrated builds of the numerically controlled layout."""
from pathlib import Path
import json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not (R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
D=R/'runs/E076-kernel-control';done=old.read(D/'complete.json');assert done['status']=='pass_scoped_full_in_place_CFV_raw_equivalence'and done['cases']==819 and done['alias_cases']==138 and done['application_kernel_launches']==1638 and done['all_owned_children_terminal']and done['source_main_live_PTX_custody_pass']
for label in ['direct','audit']:
 e=old.read(R/'runs/E076-direct-manager'/(label+'.exit.json'));assert e['returncode']==0 and e['error']is e['cleanup']is None
S=R/'runs/E076-source';source=old.read(S/'manifest.json');H=R/'runs/E076-build-plan';assert not H.exists();H.mkdir()
code=(R/'runs/E072-build-plan/build.py').read_text(encoding='utf-8').replace('E072','E076').replace('e072','e076').replace('>=54*1024**3','>=66*1024**3');compile(code,str(H/'build.py'),'exec');(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
n='crates/solver/src/gpu/plan.rs';old.pin(S/'baseline-plan.rs',old.BASE[n]);old.pin(S/'candidate-plan.rs',source['candidate_owned_sha256'][n])
P=old.read(R/'runs/E075-build-plan/build-protocol.json');P.update(id='E076-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(C/'protected-main.json'),owned={n:{'base':str(S/'baseline-plan.rs'),'base_sha256':old.BASE[n],'candidate':str(S/'candidate-plan.rs'),'candidate_sha256':source['candidate_owned_sha256'][n]}})
for phase in P['phases']:
 phase['target']=str(R/('build-e076-final-'+phase['id']));phase['outputs']={k:v.replace('E075','E076')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
paths=[Path(__file__),H/'build.py',D/'complete.json',D/'protocol.json',R/'comparisons/E076-kernel-control-root-check/report.json',R/'runs/E076-plan-control/protocol-r2.json',R/'runs/E076-plan-control/report.json',R/'runs/D122-cfv-lifetimes/protocol.json',R/'runs/D122-cfv-lifetimes/report.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for p in S.iterdir()if p.is_file()]]
P['input_sha256']={str(p):old.sha(p)for p in paths};P['direct_GPU_controls_exact_cases']=819;P['source_scope']=source['source_scope'];old.save(H/'build-protocol.json',P)
pub=[]
for p in H.iterdir():
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'pre-build-publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'integrated_builds_or_solver_executions':0,'protocol_sha256':old.sha(H/'build-protocol.json')})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E076');e.update(stage='Isolated feature and primary builds',reason='All12 CPU layouts and819 full GPU raw pairs passed. Build the exact single Rust plan change in fresh targets and restore accepted source after each phase. No whole-solve speed result.');e['evidence'].append({'label':'Frozen isolated build protocol','url':'evidence/E076-build-plan/build-protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E076',stage='Building the E076 solver trial',activity='The original-schedule CFV row-sharing prototype passed CPU metadata and GPU alias controls. Fresh isolated feature/primary builds; restore accepted source after each. No E076 performance result; E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
M=R/'runs/E076-build-manager';M.mkdir();print('E076 build protocol',old.sha(H/'build-protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'build-protocol.json')],M,'build',old.env(),3900)
old.custody();print('E076 both integrated builds terminal; no whole-solver native tests yet.',flush=True)
