# Resolve the same literal-only, loopback-default setting as the Rust server.
function Get-GTOpenEndpoint([int]$Port, [string]$BindHost = $env:GTOPEN_HOST) {
    $literal = if ([string]::IsNullOrWhiteSpace($BindHost)) { '127.0.0.1' } else { $BindHost.Trim() }
    # IPAddress.TryParse also accepts abbreviated/hex IPv4, brackets and scopes;
    # Rust's IpAddr does not. Reject those rather than silently changing the bind.
    $ipv4 = '(0|[1-9][0-9]{0,2})(\.(0|[1-9][0-9]{0,2})){3}'
    $validSyntax = $literal -notmatch '[\[\]%]' -and (
        ($literal.Contains(':') -and (
            -not $literal.Contains('.') -or $literal.Substring($literal.LastIndexOf(':') + 1) -match "^$ipv4$"
        )) -or $literal -match "^$ipv4$"
    )
    $address = $null
    if (-not $validSyntax -or -not [System.Net.IPAddress]::TryParse($literal, [ref]$address)) {
        throw "GTOPEN_HOST='$literal' is not an IP address (use an IPv4 or IPv6 literal)"
    }
    $connectAddress = $address
    if ($address.Equals([System.Net.IPAddress]::Any)) {
        $connectAddress = [System.Net.IPAddress]::Loopback
    } elseif ($address.Equals([System.Net.IPAddress]::IPv6Any)) {
        $connectAddress = [System.Net.IPAddress]::IPv6Loopback
    }
    $urlHost = $connectAddress.ToString()
    if ($connectAddress.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetworkV6) {
        $urlHost = "[$urlHost]"
    }
    [pscustomobject]@{
        BindHost = $literal
        Address = $connectAddress
        Url = "http://${urlHost}:$Port"
    }
}

# Shared identity check: an open TCP port alone is not a ready GTOpen server.
function Get-GTOpenServerState([int]$Port, $Endpoint = $null) {
    if ($null -eq $Endpoint) { $Endpoint = Get-GTOpenEndpoint $Port }
    $client = New-Object System.Net.Sockets.TcpClient -ArgumentList $Endpoint.Address.AddressFamily
    try {
        $pending = $client.BeginConnect($Endpoint.Address, $Port, $null, $null)
        if (-not $pending.AsyncWaitHandle.WaitOne(500)) { return 'Absent' }
        try { $client.EndConnect($pending) } catch { return 'Absent' }
    } finally { $client.Dispose() }
    $response = $null
    $reader = $null
    try {
        # This is our explicitly selected local listener, never an HTTP proxy.
        $request = [System.Net.WebRequest]::Create("$($Endpoint.Url)/api/status")
        $request.Proxy = $null
        $request.Timeout = 3000
        $request.ReadWriteTimeout = 3000
        $response = $request.GetResponse()
        $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
        $status = $reader.ReadToEnd() | ConvertFrom-Json
        $keys = $status.PSObject.Properties.Name
        foreach ($key in @('state', 'iteration', 'history', 'tree', 'spot_request')) {
            if ($key -notin $keys) { return 'Occupied' }
        }
        if ($status.state -notin @('idle', 'ready', 'running', 'done', 'error', 'stopped')) { return 'Occupied' }
        return 'Ready'
    } catch { return 'Occupied' }
    finally {
        if ($reader) { $reader.Dispose() }
        if ($response) { $response.Dispose() }
    }
}
