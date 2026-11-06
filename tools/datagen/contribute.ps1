# Contribute compute to the GTOpen value-net training data (Windows).
#   tools\datagen\contribute.cmd YOUR_GITHUB_LOGIN [datagen run options, e.g. --hours 8]
# Builds solve-cli (with CUDA when nvidia-smi is present), uploads finished
# jobs every 30 minutes in the background, and generates until stopped
# (Ctrl+C is safe: an unfinished job restarts next time).
# See docs/contribute-compute.md.
$ErrorActionPreference = 'Stop'
$repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location -LiteralPath $repo
if ($args.Count -lt 1) {
    Write-Host 'usage: tools\datagen\contribute.cmd YOUR_GITHUB_LOGIN [--hours H] [--jobs N]'
    exit 1
}
$login = $args[0]
$rest = @($args | Select-Object -Skip 1)

$cargoBin = Join-Path $env:USERPROFILE '.cargo\bin'
if (Test-Path "$cargoBin\cargo.exe") { $env:PATH = "$cargoBin;$env:PATH" }
$nvrtc = Join-Path $repo '.cuda-nvrtc\nvidia\cuda_nvrtc\bin'
if (Test-Path $nvrtc) { $env:PATH = "$nvrtc;$env:PATH" }
if ($env:CUDA_PATH -and (Test-Path "$env:CUDA_PATH\bin")) { $env:PATH = "$env:CUDA_PATH\bin;$env:PATH" }

$buildArgs = @('build', '--release', '-p', 'solver', '--bin', 'solve-cli')
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    $buildArgs += @('--features', 'gpu')
} else {
    Write-Host 'nvidia-smi not found: building CPU-only (much slower)'
}
& cargo @buildArgs
if ($LASTEXITCODE -ne 0) { throw 'cargo build failed' }

$py = (Get-Command python -ErrorAction SilentlyContinue)
$uploader = $null
if ($py) {
    $ErrorActionPreference = 'Continue'
    & $py.Source -c 'import huggingface_hub' 2>$null | Out-Null
    $hasHub = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = 'Stop'
    if ($hasHub) {
        $uploader = Start-Process -FilePath $py.Source -NoNewWindow -PassThru -ArgumentList @(
            'tools\datagen\upload.py', '--contributor', $login, '--watch', '30')
    }
}
if (-not $uploader) {
    Write-Host 'huggingface_hub is not installed: jobs will be saved but not uploaded.'
    Write-Host 'Install it (python -m pip install huggingface_hub), run huggingface-cli login, then'
    Write-Host "  python tools\datagen\upload.py --contributor $login"
}
try {
    & (Join-Path $repo 'target\release\solve-cli.exe') datagen run --contributor $login @rest
} finally {
    if ($uploader -and -not $uploader.HasExited) { Stop-Process -Id $uploader.Id -ErrorAction SilentlyContinue }
    if ($uploader) { & $py.Source tools\datagen\upload.py --contributor $login }
}
