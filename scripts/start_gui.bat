@echo off
REM ===========================================================
REM  Interface graphique AVEC la console visible (debogage)
REM  Usage normal : DEMARRER.bat a la racine du projet
REM ===========================================================
title Music Overlay Server - GUI (debogage)
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo Environnement absent : lancement de l'installation...
    call "%~dp0install.bat" --silencieux || exit /b 1
)

".venv\Scripts\python.exe" launcher.pyw

echo.
echo L'application s'est arretee.
echo En cas d'erreur ci-dessus, joignez logs\music-overlay.log a votre demande d'aide.
pause
