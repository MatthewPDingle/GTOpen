param([int]$Port = 3737, [int]$TimeoutSec = 120)
. "$PSScriptRoot\server-status.ps1"
$endpoint = Get-GTOpenEndpoint $Port
$deadline = (Get-Date).AddSeconds($TimeoutSec)
do {
    if ((Get-GTOpenServerState $Port -Endpoint $endpoint) -eq 'Ready') {
        Start-Process $endpoint.Url
        exit 0
    }
    Start-Sleep -Milliseconds 300
} while ((Get-Date) -lt $deadline)
Write-Error "GTOpen did not become ready on port $Port."
exit 1
