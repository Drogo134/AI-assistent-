@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   SWIFTWHISPER ASSISTANT START
echo ========================================
echo.

if not exist .venv (
  echo [INFO] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
  )
)

set PYEXE=.\.venv\Scripts\python.exe
if not exist %PYEXE% (
  echo [ERROR] Python in venv not found: %PYEXE%
  pause
  exit /b 1
)

echo [STEP] Upgrading pip...
"%PYEXE%" -m pip install --upgrade pip

echo [STEP] Installing requirements...
"%PYEXE%" -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install requirements
  pause
  exit /b 1
)

echo [STEP] Starting assistant...
"%PYEXE%" -X utf8 -u swift_assistant.py
set ERR=%ERRORLEVEL%
echo Exit code: %ERR%
pause
exit /b %ERR%


