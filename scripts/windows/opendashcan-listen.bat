@echo off
REM OpenDashCAN listen-only CLI (Windows)
REM Examples:
REM   opendashcan-listen.bat --virtual
REM   opendashcan-listen.bat --capture ..\..\captures\synthetic\idle_scenario.log

setlocal
where opendashcan >nul 2>&1
if %ERRORLEVEL%==0 (
  opendashcan listen %*
  exit /b %ERRORLEVEL%
)

python -m opendashcan.cli listen %*
exit /b %ERRORLEVEL%
