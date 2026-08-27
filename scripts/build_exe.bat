@echo off
REM ===========================================================
REM  Compile un executable autonome dans dist\
REM  L'utilisateur final n'a alors plus besoin de Python.
REM ===========================================================
title Build - Music Overlay Server
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    call "%~dp0install.bat" --silencieux || exit /b 1
)

echo Installation des outils de build...
".venv\Scripts\python.exe" -m pip install --quiet "pyinstaller>=6.6"
if errorlevel 1 (
    echo [ECHEC] Impossible d'installer PyInstaller.
    pause
    exit /b 1
)

echo.
echo Compilation en cours ^(quelques minutes^)...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean packaging\MusicOverlayServer.spec
if errorlevel 1 (
    echo.
    echo [ECHEC] La compilation a echoue.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo     EXECUTABLE PRET
echo ============================================================
echo.
echo   dist\MusicOverlayServer\MusicOverlayServer.exe
echo.
echo   Distribuez tout le dossier dist\MusicOverlayServer\.
echo.
pause
