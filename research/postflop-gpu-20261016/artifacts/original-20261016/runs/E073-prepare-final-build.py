"""Freeze isolated integrated E073 builds after terminal full raw controls."""
from pathlib import Path
import json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
D=R/'runs/E073-kernel-control-r3';done=old.read(D/'complete.json');assert done['status']=='pass_scoped_full_show_raw_equivalence'and done['cases']==364 and done['application_kernel_launches']==728 and done['all_owned_children_terminal']and done['source_main_live_PTX_custody_pass']and done['both_boundary_physical_byte_images_exact']
manager=old.read(R/'runs/E073-direct-manager-r3/direct.exit.json');assert manager['returncode']==0 and manager['error']is manager['cleanup']is None
audit=old.read(R/'runs/D119-boundary-load-audit/report.json');assert audit['criterion_unchanged']and all(audit['gates'].values())
S=R/'runs/E073-source-host-r2';source=old.read(S/'manifest.json');review=old.read(S/'source-review.json');assert review['candidate_CUDA_unchanged']and review['candidate_upload_unchanged']
H=R/'runs/E073-build-plan';H.mkdir();code=(R/'runs/E072-build-plan/build.py').read_text(encoding='utf-8').replace('E072','E073').replace('e072','e073').replace('final one-file build','final three-file build');compile(code,str(H/'build.py'),'exec')
with(H/'build.py').open('x',encoding='utf-8',newline='\n')as f:f.write(code)
P=old.read(R/'runs/E069-build-plan/build-protocol.json');owned={}
for n,h in source['candidate_owned_sha256'].items():
 base=S/('baseline-'+Path(n).name);candidate=S/('candidate-'+Path(n).name);old.pin(base,old.BASE[n]);old.pin(candidate,h);owned[n]={'base':str(base),'base_sha256':old.BASE[n],'candidate':str(candidate),'candidate_sha256':h}
P.update(id='E073-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(C/'protected-main.json'),owned=owned)
for phase in P['phases']:
 phase['target']=str(R/('build-e073-final-'+phase['id']));phase['outputs']={k:v.replace('E069','E073')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
paths=[Path(__file__),R/'runs/E073-complete-host-accounting.py',H/'build.py',D/'complete.json',D/'report.json',D/'execution-plan.json',R/'runs/E073-resource/report.json',R/'runs/E073-resource/protocol.json',R/'runs/D119-boundary-load-audit/report.json',R/'runs/D118-river-boundaries/report.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for p in S.iterdir()if p.is_file()]]
P['input_sha256']={str(p):old.sha(p)for p in paths};P['direct_GPU_controls_exact_cases']=364;P['preserved_original_resource_parser_failure']=True;P['source_scope']='Privateu16river bounds only; original CPUplan/public save/quality and floatingrecurrences exact. Checked temporary uploads4allocations/4synchronizations inside clocks. Prebuild completion makes planned/observed continuation payload accounting exact; CUDA/uploadcode unchanged from direct controls. Full feature capacity, primary/broad/material/holdout/cumulative qualification still required.';old.save(H/'build-protocol.json',P)
pub=[]
for p in H.iterdir():
 key=H.name+'/'+p.name;dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(p,dest)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'pre-build-publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'integrated_builds_or_solver_executions':0,'protocol_sha256':old.sha(H/'build-protocol.json')})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E073');e.update(stage='Isolated feature and primary builds',reason='All364full raw GPU pairs passed. Prebuild integration completes exact continuation byte accounting; CUDA/upload code unchanged. Building isolated binaries, restoring accepted source after each phase. No complete-solve speed result.');e['evidence'].extend([{'label':'Completed three-file source and accounting review','url':'evidence/E073-source-host-r2/source-review.json'},{'label':'Frozen isolated build scope','url':'evidence/E073-build-plan/build-protocol.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E073',stage='Building the E073 solver trial',activity='All364direct GPU pairs exact. Fresh isolated feature/primary builds of private16bit river boundaries; accepted source restored after each phase. E051live/accepted benchmark gain12.44%unchanged, no E073performance result.');old.ar.atomic_json(old.ar.STATUS,s)
M=R/'runs/E073-build-manager';M.mkdir();print('E073 build protocol',old.sha(H/'build-protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'build-protocol.json')],M,'build',old.env(),3900)
old.custody();print('E073 both builds terminal; no solver native tests yet.',flush=True)
