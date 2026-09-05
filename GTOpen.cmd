@echo off
title GTOpen server - close this window to stop
cd /d "%~dp0"

set "CARGO=%USERPROFILE%\.cargo\bin"
if exist "%CARGO%\cargo.exe" set "PATH=%PATH%;%CARGO%"
if not defined PORT set "PORT=3737"

rem nvrtc (CUDA runtime compiler) from the nvidia-cuda-nvrtc-cu12 pip wheel:
rem   pip install --target .cuda-nvrtc nvidia-cuda-nvrtc-cu12
rem Without nvrtc64_120_0.dll on PATH the server silently falls back to CPU.
set "NVRTC=%~dp0.cuda-nvrtc\nvidia\cuda_nvrtc\bin"
if exist "%NVRTC%\nvrtc64_120_0.dll" set "PATH=%NVRTC%;%PATH%"
if defined CUDA_PATH if exist "%CUDA_PATH%\bin" set "PATH=%CUDA_PATH%\bin;%PATH%"

rem Build the CUDA engine only when an NVIDIA driver is present (SOLVER_GPU=0
rem forces CPU-only). Cargo is incremental, so this is a fast no-op once built.
set "FEATURES=--features gpu"
if "%SOLVER_GPU%"=="0" set "FEATURES="
where nvidia-smi >nul 2>&1 || set "FEATURES="
if not defined FEATURES echo no NVIDIA CUDA runtime found - building CPU-only

where cargo >nul 2>&1
if %ERRORLEVEL%==0 (
  echo Building ^(release %FEATURES%^)...
  cargo build --release -p server %FEATURES%
  if errorlevel 1 (
    echo.
    echo Build failed. Press any key to close.
    pause >nul
    exit /b 1
  )
) else (
  if not exist "target\release\gto-server.exe" (
    echo Cargo not found and target\release\gto-server.exe is missing.
    pause >nul
    exit /b 1
  )
)

start "" /min powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0tools\open-when-ready.ps1" -Port %PORT%
echo.
echo GTOpen running at http://127.0.0.1:%PORT%
echo Close this window to stop the server.
echo.
"target\release\gto-server.exe" %*
