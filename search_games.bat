@echo off
call "%~dp0lookup_app.bat" --search-games %*
exit /b %ERRORLEVEL%
