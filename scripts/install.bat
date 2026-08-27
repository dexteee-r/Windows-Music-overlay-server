@echo off
REM ===========================================================
REM  Installation des dependances dans un environnement isole
REM  Usage : install.bat [--silencieux]
REM ===========================================================
title Installation - Music Overlay Server
cd /d "%~dp0.."

set "SILENCIEUX="
if /i "%~1"=="--silencieux" set "SILENCIEUX=1"

echo.
echo ============================================================
echo     INSTALLATION - MUSIC OVERLAY SERVER
echo ============================================================
echo.

REM --- Python present ? -------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo [ECHEC] Python n'est pas installe ou pas dans le PATH.
    echo.
    echo         1. Installez Python 3.10+ : https://www.python.org/downloads/
    echo         2. Cochez "Add python.exe to PATH"
    echo         3. Relancez ce script
    echo.
    if not defined SILENCIEUX pause
    exit /b 1
)

REM --- Version suffisante ? ---------------------------------
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    for /f "tokens=*" %%v in ('python --version') do echo [ECHEC] %%v est trop ancien, Python 3.10+ est requis.
    echo.
    if not defined SILENCIEUX pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version') do echo [OK] %%v
echo.

REM --- Environnement virtuel --------------------------------
if not exist ".venv\Scripts\python.exe" (
    echo Creation de l'environnement isole ^(.venv^)...
    python -m venv .venv
    if errorlevel 1 (
        echo [ECHEC] Creation de .venv impossible.
        echo         Verifiez que le dossier n'est pas en lecture seule.
        if not defined SILENCIEUX pause
        exit /b 1
    )
) else (
    echo [OK] Environnement .venv deja present
)

echo.
echo Installation des dependances...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo [ECHEC] Installation des dependances impossible.
    echo         Verifiez votre connexion internet, puis relancez ce script.
    echo.
    if not defined SILENCIEUX pause
    exit /b 1
)

echo.
echo ============================================================
echo     VERIFICATION
echo ============================================================
echo.
".venv\Scripts\python.exe" -m music_overlay --diagnostic
if errorlevel 1 (
    echo.
    echo [ECHEC] L'installation est incomplete ^(voir ci-dessus^).
    echo.
    if not defined SILENCIEUX pause
    exit /b 1
)

echo.
echo ============================================================
echo     INSTALLATION TERMINEE
echo ============================================================
echo.
echo   Double-cliquez sur DEMARRER.bat pour lancer l'application.
echo.
if not defined SILENCIEUX pause
exit /b 0
