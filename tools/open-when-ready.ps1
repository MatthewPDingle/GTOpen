param([int]$Port = 3737, [int]$TimeoutSec = 120)
. "$PSScriptRoot\server-status.ps1"
$deadline = (Get-Date).AddSeconds($TimeoutSec)
do {
    if ((Get-GTOpenServerState $Port) -eq 'Ready') {
        Start-Process "http://127.0.0.1:$Port"
        exit 0
    }
    Start-Sleep -Milliseconds 300
} while ((Get-Date) -lt $deadline)
Write-Error "GTOpen did not become ready on port $Port."
exit 1
