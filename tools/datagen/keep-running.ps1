# Keep the GTOpen data generator running on a machine nobody is watching (Windows).
#   tools\datagen\keep-running.cmd YOUR_GITHUB_LOGIN [datagen run options]
# Starts tools\datagen\contribute.cmd with the same arguments and starts it again
# whenever it ends (a crash, a driver update) or when no solve has been written
# for a long time (a stuck solve). Jobs carry on from where they stopped.
# Only one copy runs at a time; a second one ends at once.
# To stop it for good: create the file datagen_out\STOP (or run
# tools\datagen\autostart.cmd remove if it was set up to start at sign-in),
# then close this window.
# GTOPEN_STALL_MINUTES: minutes without a written solve before a restart (default 180).
# See docs/contribute-compute.md, "Running unattended".
$ErrorActionPreference = 'Continue'
$repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location -LiteralPath $repo
if ($args.Count -lt 1) {
    Write-Host 'usage: tools\datagen\keep-running.cmd YOUR_GITHUB_LOGIN [datagen run options]'
    exit 1
}
$login = $args[0]
$runArgs = @($args)
$out = Join-Path $repo 'datagen_out'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$log = Join-Path $out 'keep-running.log'
$stopFile = Join-Path $out 'STOP'
$stall = 180
if ($env:GTOPEN_STALL_MINUTES -match '^\d+$' -and [int]$env:GTOPEN_STALL_MINUTES -ge 10) { $stall = [int]$env:GTOPEN_STALL_MINUTES }

function Note([string]$text) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $text"
    Write-Host $line
    Add-Content -LiteralPath $log -Value $line -ErrorAction SilentlyContinue
}

# one copy per machine
$mutex = New-Object System.Threading.Mutex($false, 'GTOpenKeepRunning')
$mine = $false
try { $mine = $mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $mine = $true }
if (-not $mine) {
    Write-Host 'keep-running is already running on this machine: nothing to do.'
    exit 0
}

function Last-Write {
    # when the generator last wrote a solve or a finished job
    $dir = Join-Path $out $login
    if (-not (Test-Path -LiteralPath $dir)) { return $null }
    $newest = Get-ChildItem -LiteralPath $dir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notlike '*.uploaded' } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($newest) { return $newest.LastWriteTime }
    return $null
}

function Stop-Generator {
    # only the generator itself: a validator's solve-cli (datagen verify) is left alone
    Get-CimInstance Win32_Process -Filter "Name='solve-cli.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match 'datagen\s+run' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}

try {
    Note "keep-running started for $login (restart after $stall minutes without a written solve)"
    while ($true) {
        if (Test-Path -LiteralPath $stopFile) {
            Note 'datagen_out\STOP is there: not starting the generator. Delete that file to let it run again.'
            break
        }
        Note 'starting the generator'
        $line = "/c `"`"$(Join-Path $PSScriptRoot 'contribute.cmd')`" $($runArgs -join ' ')`""
        $p = Start-Process -FilePath 'cmd.exe' -ArgumentList $line -NoNewWindow -PassThru
        $null = $p.Handle
        $started = Get-Date
        $stuck = $false
        while (-not $p.HasExited) {
            Start-Sleep -Seconds 60
            if (Test-Path -LiteralPath $stopFile) {
                Note 'datagen_out\STOP is there: stopping the generator'
                Stop-Generator
                break
            }
            $last = Last-Write
            if (-not $last -or $last -lt $started) { $last = $started }
            if (((Get-Date) - $last).TotalMinutes -gt $stall) {
                Note "no solve written for $stall minutes: stopping the generator so it starts again"
                $stuck = $true
                Stop-Generator
                break
            }
        }
        # the script behind it uploads what is finished before it ends
        if (-not $p.WaitForExit(300000)) {
            Note 'the generator did not end by itself: ending its window'
            & taskkill.exe /T /F /PID $p.Id | Out-Null
        }
        Note "the generator ended$(if ($stuck) { ' (it was stuck)' })"
        if (Test-Path -LiteralPath $stopFile) { break }
        Start-Sleep -Seconds 60
    }
} finally {
    $mutex.ReleaseMutex()
}
