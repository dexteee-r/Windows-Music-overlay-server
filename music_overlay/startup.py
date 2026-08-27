"""Démarrage automatique avec Windows (raccourci dans le dossier Démarrage)."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from . import __app_name__, paths

logger = logging.getLogger(__name__)

SHORTCUT_NAME = f"{__app_name__}.lnk"
SHORTCUT_DESCRIPTION = "Music Overlay Server - affiche la musique en cours"


class StartupManager:
    """Ajoute ou retire le raccourci de démarrage automatique.

    Fonctionne aussi bien depuis les sources (cible ``launcher.pyw``) que
    depuis l'exécutable compilé (cible l'``.exe`` lui-même).
    """

    def __init__(self, startup_folder: Path | None = None):
        if startup_folder is not None:
            self.startup_folder = Path(startup_folder)
        else:
            appdata = os.environ.get("APPDATA", "")
            self.startup_folder = (
                Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            )
        self.shortcut_path = self.startup_folder / SHORTCUT_NAME

    @property
    def target(self) -> Path:
        """Fichier lancé au démarrage de Windows."""
        if paths.is_frozen():
            return Path(sys.executable).resolve()
        return paths.app_dir() / "launcher.pyw"

    def is_enabled(self) -> bool:
        return self.shortcut_path.exists()

    def enable(self) -> tuple[bool, str]:
        """Crée le raccourci. Retourne ``(succès, message affichable)``."""
        target = self.target
        if not target.exists():
            return False, f"Fichier de lancement introuvable : {target}"

        try:
            from win32com.client import Dispatch
        except ImportError:
            return False, "Le paquet pywin32 est manquant : relancez scripts\\install.bat."

        try:
            self.startup_folder.mkdir(parents=True, exist_ok=True)
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(self.shortcut_path))
            shortcut.TargetPath = str(target)
            shortcut.WorkingDirectory = str(paths.app_dir())
            shortcut.Description = SHORTCUT_DESCRIPTION
            shortcut.IconLocation = str(target)
            shortcut.save()
        except Exception as exc:
            logger.warning("Activation du demarrage automatique impossible : %s", exc)
            return False, f"Erreur lors de l'activation : {exc}"

        logger.info("Demarrage automatique active (%s)", self.shortcut_path)
        return True, "Demarrage automatique active"

    def disable(self) -> tuple[bool, str]:
        """Supprime le raccourci s'il existe."""
        try:
            self.shortcut_path.unlink(missing_ok=True)
        except OSError as exc:
            logger.warning("Desactivation du demarrage automatique impossible : %s", exc)
            return False, f"Erreur lors de la desactivation : {exc}"

        logger.info("Demarrage automatique desactive")
        return True, "Demarrage automatique desactive"

    def toggle(self, enable: bool) -> tuple[bool, str]:
        return self.enable() if enable else self.disable()
