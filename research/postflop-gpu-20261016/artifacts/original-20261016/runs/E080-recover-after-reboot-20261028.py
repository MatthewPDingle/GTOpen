import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
H=R/'runs/E080-reboot-recovery-20261028';H.mkdir(exist_ok=False)
m=old.read(C/'protected-main.json');main=Path(m['root']);exe=Path(m['live_path']);old.pin(exe,m['live_sha256'])
inventory=lambda:[{'path':str(p.relative_to(main/'saves')),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns}for p in sorted((main/'saves').rglob('*'))if p.is_file()]
before=inventory();old.save(H/'saves-before.json',before)
code=r'''
$ErrorActionPreference='Stop'
$taskExe='X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'
$taskRoot='X:\Dev\GTOpen'
$taskOut='S:\GTOpen-research\postflop-gpu-20261016\runs\E080-reboot-recovery-20261028'
$taskExpected='__SHA__'
$taskServers=@(Get-CimInstance Win32_Process -Filter "Name = 'gto-server.exe'")
$taskListeners=@(Get-NetTCPConnection -LocalPort 43735 -State Listen -ErrorAction SilentlyContinue)
if($taskServers.Count -ne 0 -or $taskListeners.Count -ne 0){throw 'Server or listener reappeared; preserve it'}
$taskHasher=[Security.Cryptography.SHA256]::Create(); try{$taskHash=([BitConverter]::ToString($taskHasher.ComputeHash([IO.File]::ReadAllBytes($taskExe)))).Replace('-','').ToLowerInvariant()}finally{$taskHasher.Dispose()}; if($taskHash -ne $taskExpected){throw 'Verified binary changed'}
$taskBoot=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString('o')
@{at=[DateTime]::UtcNow.ToString('o');last_boot=$taskBoot;server_processes=0;listeners=0;sha256=$taskExpected} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'native-before.json') -Encoding UTF8
$env:PORT='43735'
$env:SOLVER_GPU='1'
$env:SOLVER_COMPRESS='1'
$env:RAYON_NUM_THREADS='16'
$env:PATH='X:\Dev\GTOpen\.cuda-nvrtc\nvidia\cuda_nvrtc\bin;'+$env:PATH
$taskOwned=Start-Process -FilePath $taskExe -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskOut 'server.stdout.log') -RedirectStandardError (Join-Path $taskOut 'server.stderr.log')
$taskReady=$false
$taskDeadline=(Get-Date).AddSeconds(60)
while((Get-Date) -lt $taskDeadline){
 if($taskOwned.HasExited){throw 'Verified server exited during startup'}
 $taskListeners=@(Get-NetTCPConnection -LocalPort 43735 -State Listen -ErrorAction SilentlyContinue)
 if($taskListeners.Count -gt 0){
  if(@($taskListeners | Select-Object -ExpandProperty OwningProcess -Unique).Count -ne 1 -or $taskListeners[0].OwningProcess -ne $taskOwned.Id){throw 'Unexpected listener ownership; preserve other process'}
  $taskNative=Get-CimInstance Win32_Process -Filter ('ProcessId='+$taskOwned.Id)
  if($taskNative.ExecutablePath -ne $taskExe){throw 'Owned server path differs'}
  try{
   $taskStatus=Invoke-RestMethod 'http://127.0.0.1:43735/api/status' -TimeoutSec 5
   if($null -ne $taskStatus.state){$taskReady=$true;break}
  }catch{}
 }
 Start-Sleep -Milliseconds 200
}
if(-not $taskReady){throw 'Verified server not ready within deadline; owned PID recorded in listener'}
@{at=[DateTime]::UtcNow.ToString('o');pid=$taskOwned.Id;created=$taskNative.CreationDate.ToUniversalTime().ToString('o');path=$taskNative.ExecutablePath;sha256=$taskExpected;last_boot=$taskBoot;port=43735;startup_ready=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'native-after.json') -Encoding UTF8
Write-Output ('Verified E080 server ready, PID '+$taskOwned.Id)
'''.replace('__SHA__',m['live_sha256'])
(H/'restart.ps1').write_bytes(code.encode())
old.save(H/'protocol.json',{'id':'E080-reboot-recovery-20261028','at':old.now(),'authority':'Existing user full-access and AGENTS routine restart/session restoration authorization. Confirm Windows reboot and no GTOpen process/listener; start exact deployed binary hidden. No rebuild, replacement, kill, data migration or automatic session load.','accepted_binary':str(exe),'accepted_sha256':m['live_sha256'],'restart_script_sha256':old.sha(H/'restart.ps1'),'saves_before_sha256':old.sha(H/'saves-before.json'),'last_verified_empty_session_checkpoint':str(R/'runs/E080-reboot-recovery-20261019/live-after.json'),'preparation_failure':'Read-only revalidation found no server/listener after the October28 Windows reboot. No E090 GPU control or timing process existed; the D141 model and E090 prepared source remain preserved.'})
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.custody();old.child(['powershell.exe','-NoProfile','-File',str(H/'restart.ps1')],H,'restart',old.env(),90)
 old.custody();after=inventory();assert after==before
 snap=old.ar.live_status();old.ar.refuse_active(snap)
 old.save(H/'live-after.json',snap);old.save(H/'saves-after.json',after)
 ui=old.read(R/'runs/E080-live-deployment/UI-after.json')
 for path,expected in ui.items():
  with urllib.request.urlopen(old.ar.LIVE+path,timeout=20)as z:assert z.status==expected['status']and z.read().decode('utf-8')==expected['body']
 native=json.loads((H/'native-after.json').read_text(encoding='utf-8-sig'))
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=20)
 assert gpu['returncode']==0 and'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee'in gpu['stdout']
 old.save(H/'report.json',{'at':old.now(),'status':'pass_verified_reboot_recovery','native':native,'saved_file_inventory_unchanged':True,'saved_files':len(before),'served_root_and_preflop_JS_exact':True,'accepted_source_main_live_PTX_custody_pass':True,'source_or_binary_replaced':False,'solver_performance_samples':0,'GPU_identity_after_reboot':gpu,'scope':'Restored exact previously qualified E080 app after verified OS reboot. No active process was stopped. Last verified sessions were empty; saved files remain available and no arbitrary save was loaded. Previous performance measurements remain historical observations; no new gain or cold-cache claim.'})
pub=[]
for p in H.iterdir():
 if not p.is_file()or p.suffix not in ['.json','.ps1','.log']:continue
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);s['deployment']['live_pid']=native['pid'];s['deployment']['last_recovered_at']=old.now()
 s['deployment']['summary']='Exact qualified E080 server restored after the Windows reboot. Saved-file inventory and served UI bytes are unchanged. Research continues on port 43735.'
 s['evidence'].append({'label':'Verified server recovery after reboot','url':'evidence/'+H.name+'/report.json'})
 s.update(updated_at=old.now(),state='running',goal_status='active',stage='Resume CFV row-width analysis after reboot recovery',activity='The Windows reboot stopped the app. The exact accepted E080 executable is serving the app and tracker again; no code or saved files changed. Resume the new CFV dependency analysis.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.save(H/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'intended_background_app_server_live':native['pid'],'restart_helper_terminal':True})
print(json.dumps({'status':'restored','pid':native['pid'],'saved_files_preserved':len(before),'new_performance_samples':0}),flush=True)
