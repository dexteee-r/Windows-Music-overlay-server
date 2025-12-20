@echo off
title Music Overlay Server
color 0A

echo.
echo ============================================================
echo     MUSIC OVERLAY SERVER - APPLE MUSIC
echo ============================================================
echo.
echo Demarrage du serveur...
echo.

REM Change to src directory and run the server
cd src
python music_overlay_server.py

pause