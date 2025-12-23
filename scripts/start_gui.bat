@echo off
title Music Overlay Server - GUI
color 0B

REM Se placer dans le dossier parent (racine du projet)
cd /d "%~dp0\.."

echo.
echo ============================================================
echo     MUSIC OVERLAY SERVER - INTERFACE GRAPHIQUE
echo ============================================================
echo.

REM Vérifier si Python est installé
echo Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    echo.
    echo Lancez scripts\install.bat pour installer Python.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python detecte: %PYTHON_VERSION%
echo.

REM Vérifier que tkinter est disponible
echo Verification de tkinter...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERREUR: tkinter n'est pas installe
    echo.
    echo Reinstallez Python en cochant l'option "tcl/tk and IDLE"
    echo.
    pause
    exit /b 1
)
echo tkinter OK
echo.

REM Vérifier que les dépendances sont installées
echo Verification des dependances...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERREUR: Les dependances ne sont pas installees
    echo.
    echo Lancez scripts\install.bat pour installer les dependances.
    echo.
    pause
    exit /b 1
)
echo Dependances OK
echo.

echo Lancement de l'interface graphique...
echo.
echo Si une erreur apparait, envoyez une capture d'ecran.
echo.
echo ============================================================
echo.

REM Lancer la GUI avec affichage des erreurs
python launcher.pyw

REM Si le launcher s'arrête, afficher un message
echo.
echo ============================================================
echo L'application s'est arretee.
echo ============================================================
echo.
echo Si vous voyez une erreur ci-dessus, envoyez une capture.
echo.
pause
