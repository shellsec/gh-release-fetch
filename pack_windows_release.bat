@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "tools\pack_windows_release.ps1" %*
exit /b %ERRORLEVEL%
