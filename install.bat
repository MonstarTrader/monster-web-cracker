@echo off
REM monster web cracker -- windows installer
REM author: MR HAXOR
setlocal

echo :: monster web cracker - installer
echo :: author: MR HAXOR
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PY=python
    ) else (
        echo !! python not found. install from https://python.org
        exit /b 1
    )
)

echo -^> using: %PY%
%PY% --version

echo -^> installing pip deps
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt

echo.
echo :: done.  run:  run.bat   or   %PY% mwc.py
endlocal
