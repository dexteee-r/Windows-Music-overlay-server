@echo off
title Installation - Music Overlay Server
color 0B

echo.
echo ============================================================
echo     INSTALLATION - MUSIC OVERLAY SERVER
echo ============================================================
echo.

REM Vérifier si Python est installé
echo Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo ERREUR : Python n'est pas installe ou pas dans le PATH
    echo ========================================================
    echo.
    echo Veuillez installer Python 3.13+ depuis :
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT : Cochez "Add python.exe to PATH" pendant l'installation
    echo.
    echo Consultez INSTALL.md pour un guide detaille.
    echo.
    pause
    exit /b 1
)

REM Afficher la version de Python
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python detecte : %PYTHON_VERSION%
echo.

REM Créer le dossier config s'il n'existe pas
if not exist "config" (
    echo Creation du dossier config/...
    mkdir config
    echo Dossier config/ cree!
) else (
    echo Dossier config/ deja present
)
echo.

REM Installation des dépendances
echo ============================================================
echo Installation des dependances Python...
echo ============================================================
echo.
echo Mise a jour de pip...
python -m pip install --upgrade pip --quiet

echo Installation des packages...
echo - Flask
echo - Flask-CORS
echo - winrt (Windows Runtime)
echo.

py -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo ERREUR lors de l'installation des dependances
    echo ========================================================
    echo.
    echo Essayez de relancer install.bat en mode administrateur:
    echo   Clic droit sur install.bat ^> Executer en tant qu'administrateur
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Installation terminee avec succes!
echo ============================================================
echo.
echo Prochaines etapes :
echo   1. Double-cliquez sur start.bat pour lancer le serveur
echo   2. Visitez http://127.0.0.1:48952 dans votre navigateur
echo   3. Lancez Apple Music et jouez une musique
echo.
echo Configuration :
echo   - config/settings.json       : Port, host, parametres
echo   - config/media_filter.json   : Applications autorisees/bloquees
echo.
echo Documentation :
echo   - README.md   : Documentation complete
echo   - INSTALL.md  : Guide d'installation detaille
echo.
pause
