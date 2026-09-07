@echo off
cd /d "%~dp0..\.."
call GTOpen.cmd -NoBrowser
if errorlevel 1 exit /b 1
python -u tools\phh\overnight_reports.py %*
exit /b %ERRORLEVEL%
