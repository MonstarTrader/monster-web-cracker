@echo off
REM monster web cracker -- windows launcher
REM author: MR HAXOR
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py mwc.py %*
) else (
    python mwc.py %*
)
