@echo off
setlocal
REM ==========================================================================
REM  UPWARDS Drone Project - one-time setup for Windows.
REM  Double-click this file, or run it from a terminal in this folder.
REM  It builds a Python environment, installs everything, and checks it.
REM  Uses Python 3.11 or 3.12 (3.10 to 3.13 also work).
REM ==========================================================================
cd /d "%~dp0"
echo.
echo Setting up the drone project environment...
echo.

REM Find a real Python. Prefer the "py" launcher: the Microsoft Store alias does not shadow it.
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY (
  python --version >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo.
  echo Python was not found on this laptop.
  echo   1. Install Python 3.12 from https://www.python.org/downloads/
  echo   2. On the FIRST screen of the installer, check "Add python.exe to PATH".
  echo   3. Close this window, then double-click setup_windows.bat again.
  echo.
  echo Note: do NOT install "Python" from the Microsoft Store; it does not work here.
  echo.
  pause & exit /b 1
)
echo Using this Python:
%PY% --version
echo.

echo Creating the virtual environment (.venv)...
%PY% -m venv .venv
set "VPY=.venv\Scripts\python.exe"
if not exist "%VPY%" (
  echo.
  echo The environment could not be created.
  echo If typing "python" opened the Microsoft Store, install Python from python.org
  echo instead ^(the Store version does not work here^), then run this again.
  echo If a broken .venv folder exists, delete it and re-run.
  echo.
  pause & exit /b 1
)

echo Upgrading pip...
"%VPY%" -m pip install --upgrade pip

echo.
echo Installing OpenCV, matplotlib, av, and pillow...
"%VPY%" -m pip install opencv-contrib-python matplotlib av pillow
if errorlevel 1 (echo Install failed. Check your internet connection and try again. & pause & exit /b 1)

echo.
echo Installing djitellopy (with --no-deps so it does not fight OpenCV)...
"%VPY%" -m pip install --no-deps djitellopy
if errorlevel 1 (echo Install failed. & pause & exit /b 1)

echo.
echo Checking the install...
"%VPY%" check_setup.py

echo.
echo ==========================================================================
echo  Setup finished. From now on, open a terminal here and run:
echo      .venv\Scripts\activate
echo  Then read DRONE_HANDBOOK.pdf and run:  python example_mission.py
echo ==========================================================================
pause
