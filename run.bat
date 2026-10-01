@echo off
REM monster web cracker -- windows launcher
REM author: MR HAXOR
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py monster-web-cracker.py %*
) else (
    python monster-web-cracker.py %*
)
