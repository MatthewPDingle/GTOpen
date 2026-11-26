@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0keep-running.ps1" %*
exit /b %ERRORLEVEL%
