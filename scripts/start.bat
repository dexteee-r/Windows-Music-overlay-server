@echo off
REM ===========================================================
REM  Serveur seul, en console (sans interface graphique)
REM ===========================================================
title Music Overlay Server - console
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo Environnement absent : lancement de l'installation...
    call "%~dp0install.bat" --silencieux || exit /b 1
)

".venv\Scripts\python.exe" server.py

echo.
echo Le serveur s'est arrete.
pause
