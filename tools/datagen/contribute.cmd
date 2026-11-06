@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0contribute.ps1" %*
exit /b %ERRORLEVEL%
