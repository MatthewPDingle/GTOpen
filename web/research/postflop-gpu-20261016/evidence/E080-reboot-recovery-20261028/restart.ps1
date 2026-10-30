
$ErrorActionPreference='Stop'
$taskExe='X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'
$taskRoot='X:\Dev\GTOpen'
$taskOut='S:\GTOpen-research\postflop-gpu-20261016\runs\E080-reboot-recovery-20261028'
$taskExpected='c3c88449297574df6eeb9cb3badf4a99b0802dc740fea0f9d8fee401c1c22a62'
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
