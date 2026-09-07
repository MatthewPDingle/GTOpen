param([string]$Directory = (Join-Path (Split-Path $PSScriptRoot -Parent) 'saves\scenarios'))
$ErrorActionPreference = 'Stop'
# Older builds allowed ':' in filenames, which creates an NTFS alternate stream.
# Recover its JSON without removing the original or replacing newer normal saves.
if (-not (Test-Path -LiteralPath $Directory)) { exit 0 }
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Read-ScenarioStream([string]$Path) {
    # .NET Framework and Windows PowerShell 5 reject some ADS paths (notably
    # streams beginning with a space); open through Win32, then read as UTF-8.
    if (-not ('GTOpenScenarioFile' -as [type])) {
        Add-Type @'
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class GTOpenScenarioFile {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern SafeFileHandle CreateFileW(string path, uint access,
        uint share, System.IntPtr security, uint disposition, uint flags, System.IntPtr template);
}
'@
    }
    $handle = [GTOpenScenarioFile]::CreateFileW($Path, 2147483648, 7, [IntPtr]::Zero, 3, 0, [IntPtr]::Zero)
    if ($handle.IsInvalid) { $handle.Dispose(); throw "Cannot read scenario stream: $Path" }
    $file = New-Object System.IO.FileStream($handle, [System.IO.FileAccess]::Read)
    $reader = New-Object System.IO.StreamReader($file, [System.Text.Encoding]::UTF8)
    try { return $reader.ReadToEnd() } finally { $reader.Dispose() }
}
foreach ($entry in Get-ChildItem -LiteralPath $Directory -File) {
    foreach ($stream in Get-Item -LiteralPath $entry.FullName -Stream *) {
        if (-not $stream.Stream.EndsWith('.json')) { continue }
        $raw = Read-ScenarioStream ($entry.FullName + ":" + $stream.Stream)
        try { $scenario = $raw | ConvertFrom-Json } catch { continue }
        if (-not $scenario.name -or -not $scenario.players) { continue }
        $clean = ($scenario.name -replace '[/\\:]', '-') -replace '[^\p{L}\p{N} _.,%$+()\-]', ''
        if (-not $clean.Trim()) { continue }
        $destination = Join-Path $Directory ($clean.Trim() + '.json')
        if ((Test-Path -LiteralPath $destination) -and
            (Get-Item -LiteralPath $destination).LastWriteTimeUtc -ge $entry.LastWriteTimeUtc) { continue }
        [System.IO.File]::WriteAllText($destination, $raw, $utf8)
        Write-Host "Recovered scenario: $($scenario.name)"
    }
}
