@echo off
REM OpenDashCAN Desktop launcher (Windows)
REM After:  pip install -e ".[gui,hw]"
REM This script runs the console scripts if on PATH, else falls back to python -m.

setlocal
where opendashcan-gui >nul 2>&1
if %ERRORLEVEL%==0 (
  opendashcan-gui %*
  exit /b %ERRORLEVEL%
)

where opendashcan >nul 2>&1
if %ERRORLEVEL%==0 (
  opendashcan gui %*
  exit /b %ERRORLEVEL%
)

python -m opendashcan.gui %*
exit /b %ERRORLEVEL%
