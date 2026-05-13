@echo off
:: ╔══════════════════════════════════════════════════════════════╗
:: ║  skill-blast — Windows Double-Click Installer               ║
:: ║  Just download and double-click this file!                  ║
:: ╚══════════════════════════════════════════════════════════════╝

title skill-blast Installer
color 0B

echo.
echo  ================================================
echo   skill-blast -- 50 AI Agent Skills Installer
echo  ================================================
echo.

:: ── Python check ───────────────────────────────────────────────
echo  Checking for Python...

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
    echo  [OK] Found: %PYVER%
    set PYTHON=python
) else (
    py --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        for /f "tokens=*" %%i in ('py --version 2^>^&1') do set PYVER=%%i
        echo  [OK] Found: %PYVER%
        set PYTHON=py
    ) else (
        echo.
        echo  [ERROR] Python not found!
        echo.
        echo  Please install Python 3.9+ from:
        echo    https://www.python.org/downloads/windows/
        echo.
        echo  IMPORTANT: During install, check "Add Python to PATH"
        echo.
        echo  Opening download page...
        start https://www.python.org/downloads/windows/
        echo.
        echo  After installing Python, run this file again.
        pause
        exit /b 1
    )
)

:: ── git check ──────────────────────────────────────────────────
echo  Checking for git...
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] git not found!
    echo.
    echo  Please install git from:
    echo    https://git-scm.com/download/win
    echo.
    echo  Opening download page...
    start https://git-scm.com/download/win
    echo.
    echo  After installing git, run this file again.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('git --version') do echo  [OK] %%i

:: ── Install ──────────────────────────────────────────────────────
echo.
echo  Installing skill-blast...

:: Prefer uv if available
uv --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Found uv, using it for installation...
    uv pip install --upgrade skill-blast
    if %ERRORLEVEL% EQU 0 (
        echo  [OK] skill-blast installed via uv!
        goto :installed
    )
    echo  [WARN] uv install failed, falling back to pip...
)

%PYTHON% -m pip install --quiet --upgrade skill-blast
if %ERRORLEVEL% NEQ 0 (
    echo  Trying user install...
    %PYTHON% -m pip install --quiet --upgrade skill-blast --user
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo  [ERROR] Install failed. Please run this command manually:
        echo    pip install skill-blast
        pause
        exit /b 1
    )
)
echo  [OK] skill-blast installed via pip!

:installed

:: ── Run ────────────────────────────────────────────────────────
echo.
echo  ================================================
echo   Launching skill-blast...
echo  ================================================
echo.
timeout /t 2 /nobreak >nul

skill-blast >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    %PYTHON% -m skill_blast
)

pause
