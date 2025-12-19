@echo off
title Installation - Music Overlay
color 0B

echo.
echo ============================================================
echo     INSTALLATION - MUSIC OVERLAY
echo ============================================================
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
echo Vous pouvez maintenant lancer le serveur avec:
echo    start_server.bat
echo.
echo ou directement avec:
echo    python music_overlay_server.py
echo.
pause