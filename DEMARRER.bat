@echo off
REM ===========================================================
REM  Music Overlay Server - lancement en un double-clic
REM  Installe ce qui manque, puis ouvre l'application.
REM ===========================================================
title Music Overlay Server
cd /d "%~dp0"

REM --- Python present ? -------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   Python n'est pas installe ^(ou pas dans le PATH^).
    echo.
    echo   1. Telechargez Python sur https://www.python.org/downloads/
    echo   2. IMPORTANT : cochez "Add python.exe to PATH" pendant l'installation
    echo   3. Relancez ce fichier
    echo.
    pause
    exit /b 1
)

REM --- Environnement installe ? -----------------------------
if not exist ".venv\Scripts\pythonw.exe" (
    echo.
    echo   Premiere utilisation : installation en cours...
    echo   ^(cela peut prendre 1 a 2 minutes^)
    echo.
    call "%~dp0scripts\install.bat" --silencieux
    if errorlevel 1 (
        echo.
        echo   L'installation a echoue. Lancez scripts\diagnostic.bat pour en savoir plus.
        echo.
        pause
        exit /b 1
    )
)

REM --- Lancement --------------------------------------------
start "" ".venv\Scripts\pythonw.exe" "launcher.pyw"
exit /b 0
