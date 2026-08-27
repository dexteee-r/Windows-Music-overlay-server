# -*- mode: python ; coding: utf-8 -*-
"""Recette PyInstaller : dossier autonome dans ``dist/MusicOverlayServer``.

Format « onedir » et non « onefile » : les skins et la configuration restent
des fichiers visibles et modifiables a cote de l'executable, ce qui permet a
l'utilisateur d'ajouter ses propres skins sans recompiler.
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

PROJECT_DIR = Path(SPECPATH).parent

datas = [
    (str(PROJECT_DIR / "skins"), "skins"),
    (str(PROJECT_DIR / "README.md"), "."),
    (str(PROJECT_DIR / "LICENSE"), "."),
    (str(PROJECT_DIR / "docs"), "docs"),
]

hiddenimports = [
    *collect_submodules("winrt"),
    "pystray._win32",
    "PIL._tkinter_finder",
    "win32com.client",
]

analysis = Analysis(
    [str(PROJECT_DIR / "packaging" / "main.py")],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "ruff", "tests"],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="MusicOverlayServer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # application graphique : pas de fenetre console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

collect = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MusicOverlayServer",
)
