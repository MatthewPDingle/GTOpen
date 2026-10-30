"""Freeze E072 integrated builds after exact direct fold GPU controls."""
from pathlib import Path
import shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as c
c.custody();assert not(R/'gpu-run.lock').exists();c.ar.refuse_active(c.ar.live_status())
D=R/'runs/E072-direct-fold';done=c.read(D/'complete.json');assert done['status']=='pass_scoped_full_fold_raw_equivalence'and done['cases']==360 and done['application_kernel_launches']==720 and done['all_owned_children_terminal']and done['source_main_live_PTX_custody_pass']
manager=c.read(R/'runs/E072-direct-manager/direct.exit.json');assert manager['returncode']==0 and manager['error']is manager['cleanup']is None
amend=c.read(R/'runs/D117-fold-PTX-audit/report.json');assert amend['source_candidate_unchanged']and all(amend['amended_prerequisite_gates'].values())
S=R/'runs/E072-source';H=R/'runs/E072-build-plan';H.mkdir();source=c.read(S/'manifest.json')
code=(R/'runs/E071-build-plan/build.py').read_text(encoding='utf-8').replace('E071','E072').replace('e071','e072');compile(code,str(H/'build.py'),'exec')
with(H/'build.py').open('x',encoding='utf-8',newline='\n')as out:out.write(code)
P=c.read(R/'runs/E069-build-plan/build-protocol.json');P.update(id='E072-final-build',at=c.now(),accepted_source_sha256=c.BASE,protected_main=str(C/'protected-main.json'),owned={'crates/solver/src/gpu/kernels.cu':{'base':str(S/'baseline.cu'),'base_sha256':c.BASE['crates/solver/src/gpu/kernels.cu'],'candidate':str(S/'candidate.cu'),'candidate_sha256':source['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu']}})
for phase in P['phases']:
 phase['target']=str(R/('build-e072-final-'+phase['id']));phase['outputs']={k:v.replace('E069','E072')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
inputs=[Path(__file__),H/'build.py',D/'complete.json',D/'report.json',D/'protocol.json',R/'runs/E072-resource/report.json',R/'runs/E072-resource/protocol.json',R/'runs/D117-fold-PTX-audit/report.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',c.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[x for x in S.iterdir()if x.is_file()]]
P['input_sha256']={str(p):c.sha(p)for p in inputs};P['direct_GPU_controls_exact_cases']=360;P['preserved_original_static_count_failure']=True;P['resource_assessment_amendment']='D117explains static addsite counts via16versus8unrolling; original report/source/execution unchanged, full raw GPU controls passed. No numerical/performance gate loosened.';c.save(H/'build-protocol.json',P)
pub=[]
for p in H.iterdir():
 key=H.name+'/'+p.name;dst=c.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(c.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 pub.append({'url':'evidence/'+key,'sha256':c.sha(p)})
c.save(H/'pre-build-publication.json',{'at':c.now(),'all_files_http_byte_verified':pub,'integrated_builds_or_solver_executions':0,'protocol_sha256':c.sha(H/'build-protocol.json')})
with c.ar.exclusive_lock(c.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=c.read(c.ar.STATUS);s.update(updated_at=c.now(),state='running',goal_status='active',active_experiment='E072',stage='Building the E072 solver trial',activity='All 360 direct fold GPU cases passed full output/input/guard byte equality. Building isolated solver binaries from the frozen CUDA source. Each phase restores accepted E051 source before native tests; the live E051 app remains protected. No E072 speed result yet.');c.ar.atomic_json(c.ar.STATUS,s)
O=R/'runs/E072-build-manager';O.mkdir();print('E072 build protocol',c.sha(H/'build-protocol.json'),flush=True)
c.child([sys.executable,'-B',str(H/'build.py'),c.sha(H/'build-protocol.json')],O,'build',c.env(),3900)
c.custody();print('E072 both builds terminal; no solver native tests ran yet.',flush=True)
