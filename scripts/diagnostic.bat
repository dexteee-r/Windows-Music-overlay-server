@echo off
REM ===========================================================
REM  Verifie l'installation et affiche un rapport a joindre
REM  a une demande d'aide.
REM ===========================================================
title Diagnostic - Music Overlay Server
cd /d "%~dp0.."

if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    set "PY=python"
    echo [ATTENTION] Environnement .venv absent : diagnostic sur le Python systeme.
    echo             Lancez scripts\install.bat pour l'installer.
    echo.
)

"%PY%" -m music_overlay --diagnostic
set "CODE=%errorlevel%"

echo.
if exist "logs\music-overlay.log" echo Journal detaille : %cd%\logs\music-overlay.log
echo.
pause
exit /b %CODE%
