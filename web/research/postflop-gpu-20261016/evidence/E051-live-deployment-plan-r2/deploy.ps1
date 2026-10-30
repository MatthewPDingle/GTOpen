param([Parameter(Mandatory=$true)][string]$Protocol,[Parameter(Mandatory=$true)][string]$ProtocolSha256)
$ErrorActionPreference = 'Stop'
function Get-TaskHash([string]$TaskPath) {
    $taskStream = [IO.File]::OpenRead($TaskPath)
    $taskHasher = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($taskHasher.ComputeHash($taskStream)).Replace('-','').ToLowerInvariant() }
    finally { $taskHasher.Dispose(); $taskStream.Dispose() }
}
if ((Get-TaskHash $Protocol) -ne $ProtocolSha256) { throw 'Protocol changed' }
$taskPlan = Get-Content -LiteralPath $Protocol -Raw | ConvertFrom-Json
$taskReleaseRoot = [IO.Path]::GetFullPath('X:\Dev\GTOpen\target\desktop-runtime\release')
$taskLivePath = [IO.Path]::GetFullPath([string]$taskPlan.live_path)
if ($taskLivePath -ne (Join-Path $taskReleaseRoot 'gto-server.exe')) { throw 'Unexpected live target' }
$taskBackupPath = [IO.Path]::GetFullPath([string]$taskPlan.backup_path)
if (-not $taskBackupPath.StartsWith('S:\GTOpen-research\postflop-gpu-20261016\runs\E051-live-deployment-r2\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Backup outside named evidence directory' }
$taskOutputPath = [IO.Path]::GetFullPath([string]$taskPlan.output_directory)
$taskOriginalExited = $false
$taskNewProcess = $null
$taskRestoredProcess = $null
$taskResult = [ordered]@{ started_at=[DateTime]::UtcNow.ToString('o'); passed=$false; old_pid=$taskPlan.old_identity.pid; original_backup_verified=$false; original_exited=$false; candidate_started=$false; rollback_attempted=$false }
function Get-TaskListeners { @(Get-NetTCPConnection -LocalPort 43735 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique) }
function Assert-TaskIdleEmpty {
    $taskPostflop = Invoke-RestMethod 'http://127.0.0.1:43735/api/status' -TimeoutSec 10
    $taskPreflop = Invoke-RestMethod 'http://127.0.0.1:43735/api/preflop/status' -TimeoutSec 10
    $taskReports = Invoke-RestMethod 'http://127.0.0.1:43735/api/reports/status' -TimeoutSec 10
    if ($taskPostflop.state -ne 'idle' -or $null -ne $taskPostflop.tree -or $null -ne $taskPostflop.spot_request -or $taskPostflop.iteration -ne 0) { throw 'Postflop session now exists or is active; preserve it' }
    if ($taskPreflop.state -ne '' -or $taskPreflop.iteration -ne 0 -or @($taskPreflop.evs).Count -ne 0 -or @($taskPreflop.gaps).Count -ne 0) { throw 'Preflop session now exists or is active; preserve it' }
    if ($taskReports.running) { throw 'Report active; preserve it' }
    return @{postflop=$taskPostflop;preflop=$taskPreflop;reports=$taskReports}
}
function Start-TaskServer([string]$TaskPrefix) {
    $env:PORT = '43735'
    $env:SOLVER_GPU = '1'
    $env:SOLVER_COMPRESS = '1'
    $env:RAYON_NUM_THREADS = '16'
    $env:PATH = 'X:\Dev\GTOpen\.cuda-nvrtc\nvidia\cuda_nvrtc\bin;' + $env:PATH
    return Start-Process -FilePath $taskLivePath -WorkingDirectory 'X:\Dev\GTOpen' -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskOutputPath ($TaskPrefix+'.stdout.log')) -RedirectStandardError (Join-Path $taskOutputPath ($TaskPrefix+'.stderr.log'))
}
function Wait-TaskReady($TaskProcess,[string]$TaskExpectedHash) {
    $taskDeadline = [DateTime]::UtcNow.AddSeconds(60)
    do {
        $TaskProcess.Refresh()
        if ($TaskProcess.HasExited) { throw 'Owned server exited before readiness' }
        $taskListeners = @(Get-TaskListeners)
        if ($taskListeners.Count -gt 0) {
            if ($taskListeners.Count -ne 1 -or $taskListeners[0] -ne $TaskProcess.Id) { throw 'Unexpected process owns live port' }
            $taskNative = Get-CimInstance Win32_Process -Filter ('ProcessId='+$TaskProcess.Id)
            if ([IO.Path]::GetFullPath($taskNative.ExecutablePath) -ne $taskLivePath -or (Get-TaskHash $taskLivePath) -ne $TaskExpectedHash) { throw 'Owned server path/hash mismatch' }
            try { $taskState = Assert-TaskIdleEmpty; return @{pid=$TaskProcess.Id;path=$taskNative.ExecutablePath;created=$taskNative.CreationDate.ToUniversalTime().ToString('o');state=$taskState} } catch { if ($_.Exception.Message -like '*session now exists*' -or $_.Exception.Message -like 'Report active*') { throw } }
        }
        Start-Sleep -Milliseconds 250
    } while ([DateTime]::UtcNow -lt $taskDeadline)
    throw 'Owned server readiness timed out'
}
try {
    if ((Get-TaskHash $taskLivePath) -ne $taskPlan.old_sha256 -or (Get-TaskHash $taskPlan.candidate_path) -ne $taskPlan.candidate_sha256) { throw 'Source executable hash mismatch' }
    if (Test-Path -LiteralPath $taskBackupPath) { throw 'Backup destination already exists' }
    $taskOriginal = Get-CimInstance Win32_Process -Filter ('ProcessId='+$taskPlan.old_identity.pid)
    if ($null -eq $taskOriginal -or $taskOriginal.ExecutablePath -ne $taskPlan.old_identity.path -or $taskOriginal.CreationDate.ToUniversalTime().ToString('o') -ne $taskPlan.old_identity.created) { throw 'Original process identity changed' }
    $taskListeners = @(Get-TaskListeners)
    if ($taskListeners.Count -ne 1 -or $taskListeners[0] -ne $taskPlan.old_identity.pid) { throw 'Original listener identity changed' }
    $taskResult.before = Assert-TaskIdleEmpty
    Copy-Item -LiteralPath $taskLivePath -Destination $taskBackupPath -ErrorAction Stop
    if ((Get-TaskHash $taskBackupPath) -ne $taskPlan.old_sha256) { throw 'Backup hash mismatch' }
    $taskResult.original_backup_verified = $true
    $taskExpectedProcess = Get-Process -Id $taskPlan.old_identity.pid -ErrorAction Stop
    if ($taskExpectedProcess.StartTime.ToUniversalTime().ToString('o').Substring(0,26) -ne $taskPlan.old_identity.created.Substring(0,26) -or $taskExpectedProcess.MainModule.FileName -ne $taskLivePath) { throw 'Original owned process handle identity changed' }
    $null = Assert-TaskIdleEmpty
    $taskExpectedProcess.Kill()
    if (-not $taskExpectedProcess.WaitForExit(10000)) { throw 'Original process did not exit' }
    $taskOriginalExited = $true; $taskResult.original_exited = $true
    if (@(Get-TaskListeners).Count -ne 0) { throw 'Port occupied after original process exited' }
    Copy-Item -LiteralPath $taskPlan.candidate_path -Destination $taskLivePath -Force -ErrorAction Stop
    if ((Get-TaskHash $taskLivePath) -ne $taskPlan.candidate_sha256) { throw 'Replacement hash mismatch' }
    $taskNewProcess = Start-TaskServer 'E051-server'
    $taskResult.candidate_started = $true; $taskResult.candidate_pid = $taskNewProcess.Id
    $taskResult.after = Wait-TaskReady $taskNewProcess $taskPlan.candidate_sha256
    $taskResult.passed = $true
} catch {
    $taskResult.error = $_.Exception.ToString()
    if ($taskOriginalExited) {
        $taskResult.rollback_attempted = $true
        try {
            if ($null -ne $taskNewProcess) {
                $taskNewProcess.Refresh()
                if (-not $taskNewProcess.HasExited) { $taskNewProcess.Kill(); if (-not $taskNewProcess.WaitForExit(10000)) { throw 'Owned candidate process did not exit during rollback' } }
            }
            if (@(Get-TaskListeners).Count -ne 0) { throw 'Port owned by another process; rollback refuses to stop it' }
            if ((Get-TaskHash $taskBackupPath) -ne $taskPlan.old_sha256) { throw 'Rollback backup changed' }
            Copy-Item -LiteralPath $taskBackupPath -Destination $taskLivePath -Force -ErrorAction Stop
            $taskRestoredProcess = Start-TaskServer 'rollback-original'
            $taskResult.rollback = Wait-TaskReady $taskRestoredProcess $taskPlan.old_sha256
            $taskResult.rollback_succeeded = $true
        } catch { $taskResult.rollback_error = $_.Exception.ToString() }
    }
} finally {
    $taskResult.finished_at = [DateTime]::UtcNow.ToString('o')
    $taskResult | ConvertTo-Json -Depth 25 | Set-Content -LiteralPath (Join-Path $taskOutputPath 'native-result.json') -Encoding UTF8
}
$taskResult | ConvertTo-Json -Depth 25 -Compress | Write-Output
if (-not $taskResult.passed) { exit 1 }
