# Shared identity check: an open TCP port alone is not a ready GTOpen server.
function Get-GTOpenServerState([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $pending = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $pending.AsyncWaitHandle.WaitOne(500)) { return 'Absent' }
        try { $client.EndConnect($pending) } catch { return 'Absent' }
    } finally { $client.Dispose() }
    try {
        $status = Invoke-RestMethod "http://127.0.0.1:$Port/api/status" -TimeoutSec 3
        $keys = $status.PSObject.Properties.Name
        foreach ($key in @('state', 'iteration', 'history', 'tree', 'spot_request')) {
            if ($key -notin $keys) { return 'Occupied' }
        }
        if ($status.state -notin @('idle', 'ready', 'running', 'done', 'error', 'stopped')) { return 'Occupied' }
        return 'Ready'
    } catch { return 'Occupied' }
}
