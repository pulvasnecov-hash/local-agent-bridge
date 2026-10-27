@echo off
setlocal
set "PYTHONUTF8=1"
where py >nul 2>nul
if errorlevel 1 goto python
py -3 "%~dp0bridge.py" %*
exit /b %errorlevel%
:python
python "%~dp0bridge.py" %*
exit /b %errorlevel%
