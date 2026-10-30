"""Freeze one-file E071 integrated builds after the full CPU control replay."""
from pathlib import Path
import shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
control=R/'runs/D115-parallel-plan-control/report.json';q=old.read(control);assert q['status']=='pass_all53_CPU_fields_and_capacities' and len(q['cases'])==12 and q['all53_fields_exact']and q['all_capacities_exact']
manager=old.read(R/'runs/D115-manager/native.exit.json');assert manager['returncode']==0 and manager['error']is manager['cleanup']is None
root=old.read(R/'runs/D115-manager/root-replay.exit.json');assert root['returncode']==0 and root['error']is root['cleanup']is None
H=R/'runs/E071-build-plan';H.mkdir();S=R/'runs/E071-source';source=old.read(S/'manifest.json')
script=(R/'runs/E070-build-plan/build.py').read_text(encoding='utf-8').replace('E070','E071').replace('e070','e071').replace("HERE.parent/'accepted-E051'","HERE.parent/'accepted-E051-live-20261018'").replace('import common_e051 as old','import common_e051_live as old')
compile(script,str(H/'build.py'),'exec')
with(H/'build.py').open('x',encoding='utf-8',newline='\n')as out:out.write(script)
P=old.read(R/'runs/E069-build-plan/build-protocol.json');P.update(id='E071-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(C/'protected-main.json'),owned={'crates/solver/src/gpu/plan.rs':{'base':str(S/'baseline.rs'),'base_sha256':old.BASE['crates/solver/src/gpu/plan.rs'],'candidate':str(S/'candidate.rs'),'candidate_sha256':source['candidate_owned_sha256']['crates/solver/src/gpu/plan.rs']}})
for phase in P['phases']:
 phase['target']=str(R/('build-e071-final-'+phase['id']));phase['outputs']={k:v.replace('E069','E071')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
inputs=[Path(__file__),H/'build.py',control,R/'runs/D115-parallel-plan-control/protocol.json',R/'runs/D115-parallel-plan-control/native-report.json',R/'runs/D115-root-check.py',R/'runs/D115-manager/complete.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[x for x in S.iterdir()if x.is_file()]]
P['input_sha256']={str(p):old.sha(p)for p in inputs};P['CPU_controls_exact']=True;P['CUDA_unchanged']=True;P['resource_limits']='No CUDA/ABI/launch/buffer/device-payload changes. CPU task/queue/stack/temporary overlap and actual host peaks need material qualification before adoption.'
old.save(H/'build-protocol.json',P)
published=[]
for p in H.iterdir():
 key=H.name+'/'+p.name;dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 published.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'pre-build-publication.json',{'at':old.now(),'all_files_http_byte_verified':published,'integrated_builds_or_solver_executions':0,'protocol_sha256':old.sha(H/'build-protocol.json')})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E071',stage='Building the E071 solver trial',activity='All 53 CPU plan fields and capacities matched in 12 cases, including the retained accepted baseline. Building isolated feature and ordinary GPU test binaries. The live E051 app and accepted research source remain protected; each build restores accepted source before native tests. No complete-solve speed result yet.');old.ar.atomic_json(old.ar.STATUS,s)
O=R/'runs/E071-build-manager';O.mkdir();print('E071 build protocol',old.sha(H/'build-protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'build-protocol.json')],O,'build',old.env(),3900)
old.custody();print('E071 both builds terminal; integrated native tests not run yet.',flush=True)
