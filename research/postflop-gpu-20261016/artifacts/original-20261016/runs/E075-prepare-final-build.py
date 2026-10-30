"""Freeze isolated builds of the exact numerically controlled LDU source."""
from pathlib import Path
import json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
D=R/'runs/E075-kernel-control';done=old.read(D/'complete.json');assert done['status']=='pass_scoped_full_up_action_raw_equivalence'and done['cases']==819 and done['application_kernel_launches']==1638 and done['all_owned_children_terminal']and done['source_main_live_PTX_custody_pass']
for label in ['direct','audit']:
 e=old.read(R/'runs/E075-direct-manager'/(label+'.exit.json'));assert e['returncode']==0 and e['error']is e['cleanup']is None
q=old.read(R/'runs/E075-resource/report.json');assert q['status']=='pass_compiled_uniform_load_prerequisites'and all(q['gates'].values())and len(q['driver_capture'])==2
S=R/'runs/E075-source';source=old.read(S/'manifest.json');H=R/'runs/E075-build-plan';assert not H.exists();H.mkdir()
code=(R/'runs/E072-build-plan/build.py').read_text(encoding='utf-8').replace('E072','E075').replace('e072','e075');compile(code,str(H/'build.py'),'exec')
with(H/'build.py').open('x',encoding='utf-8',newline='\n')as f:f.write(code)
n='crates/solver/src/gpu/kernels.cu';old.pin(S/'baseline.cu',old.BASE[n]);old.pin(S/'candidate.cu',source['candidate_owned_sha256'][n]);P=old.read(R/'runs/E069-build-plan/build-protocol.json');P.update(id='E075-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(C/'protected-main.json'),owned={n:{'base':str(S/'baseline.cu'),'base_sha256':old.BASE[n],'candidate':str(S/'candidate.cu'),'candidate_sha256':source['candidate_owned_sha256'][n]}})
for phase in P['phases']:
 phase['target']=str(R/('build-e075-final-'+phase['id']));phase['outputs']={k:v.replace('E069','E075')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
paths=[Path(__file__),H/'build.py',D/'complete.json',D/'protocol.json',R/'comparisons/E075-kernel-control-root-check/report.json',R/'runs/E075-resource/protocol.json',R/'runs/E075-resource/report.json',R/'runs/D121-uniform-node-reads/protocol.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for p in S.iterdir()if p.is_file()]]
P['input_sha256']={str(p):old.sha(p)for p in paths};P['direct_GPU_controls_exact_cases']=819;P['source_scope']='Only immutable CTAuniform node reads use typedldu with explicitglobaladdressconversion. Float source body/order and all host/ABI/buffers/layout/launch/graph/quality/save behavior exact. ActualdriverSASSloadencoding changed; registers62to56/local64same/128threadoccupancy8to9, no warning. All819direct fullraw pairs exact. No solver speed or broad/material qualification yet.';old.save(H/'build-protocol.json',P)
pub=[]
for p in H.iterdir():
 key=H.name+'/'+p.name;dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'pre-build-publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'integrated_builds_or_solver_executions':0,'protocol_sha256':old.sha(H/'build-protocol.json')})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E075');e.update(stage='Isolated feature and primary builds',reason='819full raw GPU pairs passed. Build exact singleCUDAfile in fresh targets and restore accepted source after each phase. No complete-solve speed result.');e['evidence'].append({'label':'Frozen isolated build protocol','url':'evidence/E075-build-plan/build-protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E075',stage='Building the E075 solver trial',activity='All819direct GPU pairs exact. Fresh isolated feature/primary builds of immutable nodeLDUsource; accepted source restored after each phase. No E075performance result. E051accepted/live benchmark gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
M=R/'runs/E075-build-manager';M.mkdir();print('E075 build protocol',old.sha(H/'build-protocol.json'),flush=True);old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'build-protocol.json')],M,'build',old.env(),3900)
old.custody();print('E075 both builds terminal; no solver native tests yet.',flush=True)
