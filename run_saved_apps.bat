@echo off
call "%~dp0lookup_app.bat" --run-saved-apps %*
exit /b %ERRORLEVEL%
