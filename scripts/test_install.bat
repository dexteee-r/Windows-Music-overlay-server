@echo off
title Test Installation - Music Overlay Server
color 0E

REM Se placer dans le dossier parent (racine du projet)
cd /d "%~dp0\.."

echo.
echo ============================================================
echo     TEST INSTALLATION - DIAGNOSTIC
echo ============================================================
echo.

REM Test 1: Python
echo [TEST 1] Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ECHEC] Python n'est pas installe ou pas dans le PATH
    echo.
    echo Solution:
    echo 1. Installez Python 3.13+ depuis https://www.python.org/downloads/
    echo 2. IMPORTANT: Cochez "Add python.exe to PATH" pendant l'installation
    echo.
    goto :error
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] %PYTHON_VERSION%
)
echo.

REM Test 2: Fichiers critiques
echo [TEST 2] Verification des fichiers critiques...
if exist "launcher.pyw" (
    echo [OK] launcher.pyw existe
) else (
    echo [ECHEC] launcher.pyw manquant
    goto :error
)

if exist "server.py" (
    echo [OK] server.py existe
) else (
    echo [ECHEC] server.py manquant
    goto :error
)

if exist "requirements.txt" (
    echo [OK] requirements.txt existe
) else (
    echo [ECHEC] requirements.txt manquant
    goto :error
)

if exist "src\gui.py" (
    echo [OK] src\gui.py existe
) else (
    echo [ECHEC] src\gui.py manquant
    goto :error
)
echo.

REM Test 3: Dépendances Python
echo [TEST 3] Verification des dependances Python...
echo Teste Flask...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ECHEC] Flask non installe
    echo Solution: Lancez scripts\install.bat
    goto :error
) else (
    echo [OK] Flask installe
)

echo Teste requests...
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ECHEC] requests non installe
    echo Solution: Lancez scripts\install.bat
    goto :error
) else (
    echo [OK] requests installe
)

echo Teste tkinter...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ECHEC] tkinter non installe
    echo Solution: Reinstallez Python en cochant "tcl/tk and IDLE"
    goto :error
) else (
    echo [OK] tkinter installe
)

echo Teste pystray...
python -c "import pystray" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ATTENTION] pystray non installe (optionnel pour system tray)
) else (
    echo [OK] pystray installe
)

echo Teste Pillow...
python -c "from PIL import Image" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ATTENTION] Pillow non installe (optionnel pour system tray)
) else (
    echo [OK] Pillow installe
)

echo Teste pywin32...
python -c "import win32com.client" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ATTENTION] pywin32 non installe (optionnel pour auto-startup)
) else (
    echo [OK] pywin32 installe
)

echo Teste winrt...
python -c "from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ECHEC] winrt non installe
    echo Solution: Lancez scripts\install.bat
    goto :error
) else (
    echo [OK] winrt installe
)
echo.

REM Test 4: Test de lancement de la GUI
echo [TEST 4] Test de lancement de la GUI...
echo Teste l'import de gui.py...
python -c "import sys; sys.path.insert(0, 'src'); from gui import main; print('[OK] GUI peut etre importee')" 2>&1
if %errorlevel% neq 0 (
    echo [ECHEC] Impossible d'importer la GUI
    echo Erreur ci-dessus
    goto :error
)
echo.

REM Succès
echo ============================================================
echo     TOUS LES TESTS SONT PASSES !
echo ============================================================
echo.
echo Votre installation est correcte.
echo.
echo Pour lancer l'application:
echo   1. Double-cliquez sur launcher.pyw
echo   OU
echo   2. Lancez: python launcher.pyw
echo.
pause
exit /b 0

:error
echo.
echo ============================================================
echo     ERREUR DETECTEE
echo ============================================================
echo.
echo Corrigez les erreurs ci-dessus puis relancez ce test.
echo.
echo Si le probleme persiste, envoyez une capture de cette fenetre.
echo.
pause
exit /b 1
