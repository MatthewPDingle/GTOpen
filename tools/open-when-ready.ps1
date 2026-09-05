# Waits for the GTOpen server to accept connections, then opens the UI.
param([int]$Port = 3737, [int]$TimeoutSeconds = 120)

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $client.Connect('127.0.0.1', $Port)
        $client.Close()
        Start-Process "http://127.0.0.1:$Port"
        exit 0
    } catch {
        Start-Sleep -Milliseconds 400
    } finally {
        $client.Dispose()
    }
}
exit 1
