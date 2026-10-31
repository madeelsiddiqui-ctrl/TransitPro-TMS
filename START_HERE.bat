@echo off
setlocal
title Transport Management System - Muhammad Adeel Siddiqi
cd /d "%~dp0"
cls
echo.
echo  ==============================================================
echo     TRANSPORT MANAGEMENT SYSTEM
echo     Muhammad Adeel Siddiqi  -  PGD/DSAI/Apr-26/312564
echo     NED University of Engineering and Technology
echo  ==============================================================
echo.

REM ---------- 1. find Python ----------
set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python --version >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo  [X] Python is NOT installed on this computer.
  echo.
  echo      1. The Python download page will open now.
  echo      2. Download and run the installer.
  echo      3. VERY IMPORTANT: on the first screen tick the box
  echo         "Add python.exe to PATH", then click "Install Now".
  echo      4. When it finishes, double-click START_HERE again.
  echo.
  start "" https://www.python.org/downloads/
  pause
  exit /b
)
echo  [OK] Python found.

REM ---------- 2. install packages (Flask, PyMySQL) ----------
echo.
echo  [..] Preparing the app (first time only, needs internet, 1-2 minutes)...
%PY% -m pip install --disable-pip-version-check --no-warn-script-location -q -r requirements.txt
if errorlevel 1 %PY% -m pip install --user --disable-pip-version-check --no-warn-script-location -q -r requirements.txt
if errorlevel 1 (
  echo  [X] Could not install the packages. Check your internet and try again.
  pause
  exit /b
)
echo  [OK] App ready.

REM ---------- 3. MySQL password ----------
echo.
echo  --------------------------------------------------------------
echo   Type your MySQL ROOT PASSWORD and press ENTER.
echo   (the same password you use to open MySQL Workbench)
echo.
echo   No MySQL on this computer? Just press ENTER - the app will
echo   use its built-in database instead.
echo  --------------------------------------------------------------
set "MYSQL_PASSWORD="
set /p "MYSQL_PASSWORD=  MySQL password: "
if defined MYSQL_PASSWORD (set "DB_ENGINE=mysql") else (set "DB_ENGINE=sqlite")
cls
echo.
echo  ==============================================================
echo    STARTING...  your browser will open in a few seconds at
echo                 http://127.0.0.1:5000
echo.
echo    KEEP THIS WINDOW OPEN while you use the app.
echo    To stop the app, close this window.
echo  ==============================================================

REM ---------- 4. open browser + start server ----------
start "" cmd /c "timeout /t 5 >nul & start http://127.0.0.1:5000"
%PY% app.py
echo.
echo  The app has stopped.
pause
