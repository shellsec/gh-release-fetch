@echo off
setlocal
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set "GHRF_EXE=%~dp0GHReleaseFetch.exe"
if not exist "%GHRF_EXE%" set "GHRF_EXE=%~dp0dist\exe\GHReleaseFetch.exe"
if exist "%GHRF_EXE%" (
    "%GHRF_EXE%" --gui-lookup %*
    exit /b
)
echo [ERROR] GHReleaseFetch.exe was not found.
exit /b 1
