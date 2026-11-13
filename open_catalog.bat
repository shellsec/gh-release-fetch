@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

call "%~dp0lookup_app.bat" --serve-catalog %*
exit /b %ERRORLEVEL%
