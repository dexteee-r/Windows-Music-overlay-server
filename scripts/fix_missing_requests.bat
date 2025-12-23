@echo off
title Fix Missing Requests Module
color 0C

REM Se placer dans le dossier parent (racine du projet)
cd /d "%~dp0\.."

echo.
echo ============================================================
echo     FIX: Installation du module 'requests' manquant
echo ============================================================
echo.

echo Le module 'requests' est necessaire pour la GUI.
echo Installation en cours...
echo.

python -m pip install requests>=2.31.0

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo ERREUR lors de l'installation
    echo ============================================================
    echo.
    echo Essayez de:
    echo 1. Relancer en mode administrateur
    echo 2. Verifier votre connexion internet
    echo 3. Relancer scripts\install.bat completement
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo     'requests' installe avec succes !
echo ============================================================
echo.
echo Vous pouvez maintenant lancer launcher.pyw
echo.
pause
