@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0autostart.ps1" %*
exit /b %ERRORLEVEL%
