@echo off
title Music Overlay Server
color 0A

echo.
echo ======================================================================
echo     MUSIC OVERLAY SERVER - APPLE MUSIC
echo ======================================================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR : Python n'est pas installe!
    echo.
    echo Lancez install.bat pour installer Python et les dependances.
    echo.
    pause
    exit /b 1
)

REM Vérifier si les dépendances sont installées
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR : Les dependances ne sont pas installees!
    echo.
    echo Lancez install.bat pour installer les dependances.
    echo.
    pause
    exit /b 1
)

echo Demarrage du serveur...
echo.
echo ======================================================================
echo.

REM Lancer le serveur
python server.py

REM Si le serveur s'arrête, afficher un message
echo.
echo ======================================================================
echo Le serveur s'est arrete.
echo ======================================================================
echo.
pause
