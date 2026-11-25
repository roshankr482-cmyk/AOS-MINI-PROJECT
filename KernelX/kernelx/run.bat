@echo off
REM KernelX launcher for Windows.
REM Usage: run.bat [-p PORT] [--host 0.0.0.0] [--no-browser]   |   run.bat cli [args]
setlocal
cd /d "%~dp0"

set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY (
  python --version >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo.
  echo Python not found. Install from https://www.python.org/downloads/
  echo ^(tick "Add python.exe to PATH"^) and run this again.
  echo If you only get a Microsoft Store popup, install Python from python.org instead.
  pause
  exit /b 1
)

echo [1/3] Building C engine ^(optional^)...
call "%~dp0build.bat"
cd /d "%~dp0"

if exist "%~dp0backend\test_algorithms.exe" (
  echo [2/3] Running self-test...
  "%~dp0backend\test_algorithms.exe" | findstr /c:"PASSED" /c:"FAILED"
) else (
  echo [2/3] Self-test skipped ^(no C compiler - using Python engine^)
)

if /i "%~1"=="cli" (
  if not exist "%~dp0backend\kernelx_cli.exe" (
    echo CLI needs gcc ^(MinGW-w64^). See README.
    pause
    exit /b 1
  )
  shift
  "%~dp0backend\kernelx_cli.exe" %1 %2 %3 %4 %5 %6 %7 %8 %9
  exit /b %errorlevel%
)

echo [3/3] Starting web server...
%PY% "%~dp0server.py" %*
if errorlevel 1 (
  echo.
  echo Server exited with an error - see message above.
  pause
)
