"""Freeze two isolated integrated builds of the exact controlled three-file source."""
from pathlib import Path
import shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
D=R/'runs/E077-kernel-control';done=old.read(D/'complete.json');assert done['status']=='pass_scoped_full_selective_prefix_raw_equivalence'and done['cases']==1820 and done['application_kernel_launches']==3640 and done['all_owned_children_terminal']
for label in ['direct','audit']:
 e=old.read(R/'runs/E077-direct-manager'/(label+'.exit.json'));assert e['returncode']==0 and e['error']is e['cleanup']is None
S=R/'runs/E077-source';source=old.read(S/'manifest.json');H=R/'runs/E077-build-plan';assert not H.exists();H.mkdir()
code=(R/'runs/E076-build-plan/build.py').read_text(encoding='utf-8').replace('E076','E077').replace('e076','e077');compile(code,str(H/'build.py'),'exec');(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
owned={}
for n,files in source['owned'].items():
 base=Path(files['base']);candidate=Path(files['candidate']);old.pin(base,old.BASE[n]);old.pin(candidate,source['candidate_owned_sha256'][n]);owned[n]={'base':str(base),'base_sha256':old.BASE[n],'candidate':str(candidate),'candidate_sha256':source['candidate_owned_sha256'][n]}
P=old.read(R/'runs/E076-build-plan/build-protocol.json');P.update(id='E077-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(C/'protected-main.json'),owned=owned)
for phase in P['phases']:
 phase['target']=str(R/('build-e077-final-'+phase['id']));phase['outputs']={k:v.replace('E076','E077')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
paths=[Path(__file__),H/'build.py',D/'complete.json',D/'protocol.json',R/'comparisons/E077-kernel-control-root-check/report.json',R/'runs/E077-plan-control/protocol-r2.json',R/'runs/E077-plan-control/report.json',R/'runs/E077-resource/protocol.json',R/'runs/E077-resource/report.json',R/'runs/D124-prefix-liveness/protocol.json',R/'runs/D124-prefix-liveness/report.json',R/'runs/D125-index-address-audit/protocol.json',R/'runs/D125-index-address-audit/report.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for p in S.iterdir()if p.is_file()]]
P['input_sha256']={str(p):old.sha(p)for p in paths};P['direct_GPU_controls_exact_cases']=1820;P['source_scope']=source['source_scope'];old.save(H/'build-protocol.json',P)
for p in H.iterdir():
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-build-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'build-protocol.json'),'all_prepared_artifacts_HTTP_byte_verified':True,'integrated_builds_or_solver_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E077');e.update(stage='Fresh feature and primary solver builds',reason='12 compiled host maps/3 tests and1820 full raw GPU pairs passed. Build exact frozen3-file source in fresh targets, restore accepted files after each phase. No full-solve speed result.');e['evidence'].append({'label':'Frozen isolated integrated build protocol','url':'evidence/E077-build-plan/build-protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E077',stage='Building the E077 complete-solve trial',activity='Fresh integrated feature/primary builds after full host/GPU raw controls. Original accepted files restored after each phase. No E077 speed result; E051 live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
M=R/'runs/E077-build-manager';M.mkdir();print('E077 build protocol',old.sha(H/'build-protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'build-protocol.json')],M,'build',old.env(),3900)
old.custody();print('E077 integrated builds terminal; accepted source restored.',flush=True)
