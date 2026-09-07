param(
    [ValidateRange(1, 65535)][int]$Port = $(if ($env:PORT) { [int]$env:PORT } else { 3737 }),
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\server-status.ps1"
$repo = Split-Path $PSScriptRoot -Parent
$url = "http://127.0.0.1:$Port"
$owned = $null
$locked = $false
$mutex = New-Object System.Threading.Mutex($false, "Local\GTOpen-launch-$Port")
function Open-GTOpen {
    Write-Host "GTOpen ready at $url"
    if (-not $NoBrowser) { Start-Process $url }
}
try {
    # Serialize build/start, including concurrent double-clicks of the shortcut.
    Write-Host 'Checking for GTOpen...'
    try { $locked = $mutex.WaitOne(600000) }
    catch [System.Threading.AbandonedMutexException] { $locked = $true }
    if (-not $locked) { throw 'Another GTOpen launch is still building. Try again shortly.' }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\recover-scenarios.ps1"
    if ($LASTEXITCODE -ne 0) { throw 'Scenario recovery failed; original files were preserved.' }
    $state = Get-GTOpenServerState $Port
    if ($state -eq 'Ready') {
        Write-Host 'Reusing the running app; your sessions are preserved.'
        Open-GTOpen
        exit 0
    }
    if ($state -eq 'Occupied') { throw "Port $Port is occupied or not responding as GTOpen. No process was stopped." }
    Set-Location -LiteralPath $repo
    $env:PORT = "$Port"
    $cargoBin = Join-Path $env:USERPROFILE '.cargo\bin'
    if (Test-Path "$cargoBin\cargo.exe") { $env:PATH = "$cargoBin;$env:PATH" }
    $nvrtc = Join-Path $repo '.cuda-nvrtc\nvidia\cuda_nvrtc\bin'
    if (Test-Path $nvrtc) { $env:PATH = "$nvrtc;$env:PATH" }
    if ($env:CUDA_PATH -and (Test-Path "$env:CUDA_PATH\bin")) { $env:PATH = "$env:CUDA_PATH\bin;$env:PATH" }
    $exe = Join-Path $repo 'target\release\gto-server.exe'
    if (Get-Command cargo -ErrorAction SilentlyContinue) {
        $buildArgs = @('build', '--release', '-p', 'server')
        if ($env:SOLVER_GPU -ne '0' -and (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
            $buildArgs += @('--features', 'gpu')
        }
        Write-Host "Building release: cargo $buildArgs"
        & cargo @buildArgs
        if ($LASTEXITCODE -ne 0) { throw 'Build failed; the server was not started.' }
    }
    if (-not (Test-Path $exe)) { throw 'No release executable found. Install Rust/Cargo and launch again.' }
    $state = Get-GTOpenServerState $Port
    if ($state -eq 'Ready') { Open-GTOpen; exit 0 }
    if ($state -ne 'Absent') { throw "Port $Port became occupied during the build." }
    $logs = Join-Path $repo 'target\launcher'
    New-Item -ItemType Directory -Force -Path $logs | Out-Null
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-ffff'
    $owned = Start-Process -FilePath $exe -WorkingDirectory $repo -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput "$logs\$stamp.stdout.log" -RedirectStandardError "$logs\$stamp.stderr.log"
    $deadline = (Get-Date).AddSeconds(120)
    do {
        if ($owned.HasExited) { throw "Server exited. See $logs\$stamp.stderr.log" }
        if ((Get-GTOpenServerState $Port) -eq 'Ready') {
            Write-Host "Server runs in the background (PID $($owned.Id)). Logs: $logs"
            $owned = $null
            Open-GTOpen
            exit 0
        }
        Start-Sleep -Milliseconds 300
    } while ((Get-Date) -lt $deadline)
    throw "Server did not become ready. See $logs\$stamp.stderr.log"
} catch {
    if ($owned -and -not $owned.HasExited) { $owned.Kill() }
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    if ($locked) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
