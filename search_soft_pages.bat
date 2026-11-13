@echo off
call "%~dp0lookup_app.bat" --search-soft-pages %*
exit /b %ERRORLEVEL%
