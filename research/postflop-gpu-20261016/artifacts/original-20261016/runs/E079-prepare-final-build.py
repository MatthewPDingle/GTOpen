"""Freeze two isolated E079 builds after the exact admitted setup component."""
from pathlib import Path
import shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
D=R/'runs/D130-plan-context-overlap';q=old.read(D/'report.json');assert q['admit_one_integrated_trial']and q['fixed_six_fresh_processes_complete']and q['native_component_processes']==6 and len(q['full_metadata_raw_replays'])==18
receipt=old.read(R/'runs/D130-manager/component.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
S=R/'runs/E079-source';source=old.read(S/'manifest.json');H=R/'runs/E079-build-plan';assert not H.exists();H.mkdir();code=(R/'runs/E078-build-plan/build.py').read_text(encoding='utf-8').replace('E078','E079').replace('e078','e079').replace('final two-file build','final one-file build');compile(code,str(H/'build.py'),'exec');(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
owned={}
for n,files in source['owned'].items():
 base=Path(files['base']);candidate=Path(files['candidate']);old.pin(base,old.BASE[n]);old.pin(candidate,source['candidate_owned_sha256'][n]);owned[n]={'base':str(base),'base_sha256':old.BASE[n],'candidate':str(candidate),'candidate_sha256':source['candidate_owned_sha256'][n]}
assert set(owned)=={'crates/solver/src/gpu/mod.rs'};old.pin(old.REPO/'crates/solver/src/gpu/kernels.cu',old.BASE['crates/solver/src/gpu/kernels.cu'])
P=old.read(R/'runs/E078-build-plan/build-protocol.json');P.update(id='E079-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(C/'protected-main.json'),owned=owned)
for phase in P['phases']:
 phase['target']=str(R/('build-e079-final-'+phase['id']));phase['outputs']={k:v.replace('E078','E079')for k,v in phase['outputs'].items()};assert not Path(phase['target']).exists()
for k in list(P):
 if k.startswith('direct_GPU_'):del P[k]
paths=[Path(__file__),H/'build.py',D/'protocol.json',D/'execution-plan.json',D/'report.json',D/'probe.rs',D/'replay.py',D/'ability-report.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'crates/solver/src/gpu/kernels.cu',*[p for p in S.iterdir()if p.is_file()]]
P['input_sha256']={str(p):old.sha(p)for p in paths};P['component_full_metadata_snapshots']=18;P['component_error_cleanup_mock_cases']=18;P['CUDA_source_unchanged']=True;P['source_scope']=source['scope']+' All 18 full plan snapshots and 18 lifecycle mocks passed in the exact component form. The 31.3545 ms river component regression remains unresolved; no exception to the full-solve fixture guard. Fresh builds precede 86 ordinary tests and exactly three complete-solve pairs. No complete-solve or material qualification yet.';old.save(H/'build-protocol.json',P)
for p in H.iterdir():
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-build-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'build-protocol.json'),'all_prepared_artifacts_HTTP_byte_verified':True,'integrated_builds_or_solver_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E079');e.update(stage='Fresh feature and benchmark builds',reason='The exact D130 overlap is staged in one host file. Build both isolated variants and restore accepted source after each phase. CUDA source is unchanged. The river component slowdown remains unresolved; full-solve gates are unchanged.');e['evidence'].append({'label':'Frozen integrated build protocol','url':'evidence/E079-build-plan/build-protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E079',stage='Building E079 complete-solve trial',activity='Build the exact setup-overlap form, including the original serial river path. Error/cleanup controls and real worker-stream copies are in the ordinary unit suite. No full-solve gain claimed; accepted/live E051 remain unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
M=R/'runs/E079-build-manager';assert not M.exists();M.mkdir();print('E079 build protocol',old.sha(H/'build-protocol.json'),flush=True);old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'build-protocol.json')],M,'build',old.env(),3900);old.custody();print('E079 builds terminal; accepted source restored.',flush=True)
