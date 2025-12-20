@echo off
title Installation - Music Overlay
color 0B

echo.
echo ============================================================
echo     INSTALLATION - MUSIC OVERLAY
echo ============================================================
echo.

REM Create directory structure
echo Creation de la structure du projet...
if not exist "config" mkdir config
if not exist "src" mkdir src
echo Structure du projet creee!
echo.

REM Create default config files if they don't exist
if not exist "config\settings.json" (
    echo Creation du fichier de configuration settings.json...
    (
        echo {
        echo   "server": {
        echo     "host": "127.0.0.1",
        echo     "port": 48952
        echo   },
        echo   "update_interval": 0.5
        echo }
    ) > "config\settings.json"
)

if not exist "config\media_filter.json" (
    echo Creation du fichier de filtre media_filter.json...
    (
        echo {
        echo   "mode": "whitelist",
        echo   "allowed_apps": [
        echo     "Music.UI.exe",
        echo     "AppleMusic.exe"
        echo   ],
        echo   "blocked_apps": [],
        echo   "default_message": {
        echo     "title": "No track playing",
        echo     "artist": "Unknown",
        echo     "album": ""
        echo   }
        echo }
    ) > "config\media_filter.json"
)

echo.
echo Installation des dependances Python...
echo.

python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ============================================================
echo Installation terminee!
echo ============================================================
echo.
echo Structure du projet:
echo   - config/settings.json        (Configuration serveur)
echo   - config/media_filter.json    (Filtre applications media)
echo   - src/music_overlay_server.py (Serveur principal)
echo   - src/media_filter.py         (Module de filtrage)
echo.
echo Vous pouvez maintenant lancer le serveur avec:
echo    start_server.bat
echo.
echo Pour modifier la configuration, editez les fichiers dans config/
echo.
pause