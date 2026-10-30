"""Prospective source/runner seal for accepted E051 application qualification."""
import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
H=R/'runs/E051-server-final-plan';target=R/'build-server-e051-final';assert not target.exists() and not(H/'protocol.json').exists()
reference=R/'runs/E020-server-implementation';inventory=old.read(reference/'unit-inventory.json')
for rel,h in inventory['server_source_sha256'].items():old.pin(old.REPO/rel,h);old.pin(Path(r'X:\Dev\GTOpen')/rel,h)
for name in ['unit-inventory.json','spot-request.json','solve-request.json']:shutil.copyfile(reference/name,H/name)
code=(reference/'smoke.py').read_text(encoding='utf-8').replace('E020','E051').replace('E051-server-smoke','E051-server-final-smoke').replace('V020-server-unit','V051-server-unit')
assert "runs/V051-server-unit/report.json" in code
with(H/'smoke.py').open('x',encoding='utf-8',newline='\n') as f:f.write(code)
for name in ['common.py','build.py','smoke.py']:compile((H/name).read_text(encoding='utf-8'),str(H/name),'exec')
code="$ls=@(Get-NetTCPConnection -LocalPort 43735 -State Listen -ErrorAction Stop); $p=Get-CimInstance Win32_Process -Filter 'ProcessId=37268'; @{listeners=@($ls|Select-Object -ExpandProperty OwningProcess -Unique);pid=$p.ProcessId;path=$p.ExecutablePath;created=$p.CreationDate.ToUniversalTime().ToString('o')} | ConvertTo-Json -Compress"
native=subprocess.run(['powershell.exe','-NoProfile','-Command',code],capture_output=True,text=True,encoding='utf-8',check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
live=json.loads(native.stdout);protected=old.read(R/'runs/accepted-E051/protected-main.json');assert live['pid']==37268 and live['listeners']==[37268] and Path(live['path'])==Path(protected['live_path']);old.pin(live['path'],protected['live_sha256'])
accept=R/'comparisons/E051-qualification-r2/report.json';a=old.read(accept);assert a['candidate']=='E051' and a['status']=='accepted_source_integrated'
inputs=[Path(__file__),accept,reference/'smoke.py',reference/'E020-kernels.cu',R/'runs/accepted-E051/baseline.json',R/'runs/accepted-E051/protected-main.json',*[H/n for n in ['common.py','build.py','smoke.py','unit-inventory.json','spot-request.json','solve-request.json']]]
P={'id':'E051-final-server-qualification','at':old.now(),'status':'FROZEN_PRE_COMPILATION','candidate':'E051','source_sha256':old.BASE|inventory['server_source_sha256'],'server_source_sha256':inventory['server_source_sha256'],'acceptance':{'path':str(accept),'sha256':old.sha(accept)},'target':str(target),'target_previously_absent':True,'research_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip(),'live_identity':live,'live_sha256':protected['live_sha256'],'input_sha256':{str(p):old.sha(p) for p in inputs},'expected_unit_names':inventory['expected_test_names'],'minimum_free_S_bytes':66*1024**3,'peak_output_reservation_bytes':8*1024**3,'rule':'Two compile-only phases; exact embedded E051 CUDA and typed artifact proof; exact21test inventory,20passed/1ignored; then separately sealed original tiny river100iteration GPU API smoke on owned43736. No new speed observation. No live source/executable/session changes during qualification. Fresh E051 server binary must pass before any separately frozen maintenance deployment.','native_execution_authority':'Human requested full access and approval-free continuation; current danger-full-access/never verified operational. Routine builds/restarts authorized by current AGENTS. No policy override or security settings mutation.'}
old.save(H/'protocol.json',P)
pub=[]
for src in H.iterdir():
 if not src.is_file():continue
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 pub.append({'url':'evidence/'+key,'sha256':old.sha(src)})
old.save(H/'pre-build-publication.json',{'at':old.now(),'files_http_byte_verified':pub,'protocol_sha256':old.sha(H/'protocol.json'),'native_build_or_unit_or_API_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E051-server',stage='E051 isolated server qualification',activity='Native goal resumed. Prior turn completed and rejected E070 at0.855187%. Qualified E051 source is integrated but live still original; preparing fresh isolated server build/unit/GPU API verification before routine maintenance deployment. Current sessions and reports idle and empty.');s['evidence'].append({'label':'Frozen E051 application qualification','url':'evidence/'+H.name+'/protocol.json'});old.ar.atomic_json(old.ar.STATUS,s)
manager=R/'runs/E051-server-final-manager';assert not manager.exists();manager.mkdir()
print('E051 final server protocol',old.sha(H/'protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'build.py'),old.sha(H/'protocol.json')],manager,'build-unit',old.env(),4200)
print('E051 build manager complete',flush=True)
