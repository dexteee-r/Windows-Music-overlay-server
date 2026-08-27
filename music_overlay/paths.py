"""Résolution des chemins de l'application.

Toutes les lectures/écritures de fichiers passent par ce module afin que
l'application fonctionne de façon identique dans les trois contextes :

- exécution depuis les sources (``python launcher.pyw``) ;
- exécution depuis un exécutable PyInstaller (``MusicOverlayServer.exe``) ;
- exécution depuis n'importe quel répertoire courant.

C'est ce qui permet de supprimer tout ``os.chdir()`` : aucun chemin relatif
n'est utilisé ailleurs dans le code.
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR_NAME = "config"
SKINS_DIR_NAME = "skins"
LOGS_DIR_NAME = "logs"


def is_frozen() -> bool:
    """Indique si l'application tourne depuis un exécutable PyInstaller."""
    return bool(getattr(sys, "frozen", False))


def bundle_dir() -> Path:
    """Répertoire des ressources embarquées, en lecture seule.

    En mode « gelé », PyInstaller extrait les données dans ``sys._MEIPASS``.
    Depuis les sources, il s'agit simplement de la racine du dépôt.
    """
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def app_dir() -> Path:
    """Répertoire inscriptible : configuration utilisateur, logs, skins perso.

    À côté de l'exécutable en mode gelé (application portable), à la racine du
    dépôt en développement.
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def config_dir() -> Path:
    """Répertoire de configuration (créé à la demande par ``ConfigStore``)."""
    return app_dir() / APP_DIR_NAME


def logs_dir() -> Path:
    """Répertoire des fichiers de log."""
    return app_dir() / LOGS_DIR_NAME


def user_skins_dir() -> Path:
    """Skins ajoutés par l'utilisateur, à côté de l'exécutable ou du dépôt."""
    return app_dir() / SKINS_DIR_NAME


def bundled_skins_dir() -> Path:
    """Skins fournis avec l'application."""
    return bundle_dir() / SKINS_DIR_NAME


def skins_dirs() -> list[Path]:
    """Répertoires de skins par ordre de priorité (l'utilisateur gagne).

    En développement les deux chemins sont identiques ; le doublon est retiré.
    """
    directories = [user_skins_dir(), bundled_skins_dir()]
    unique: list[Path] = []
    for directory in directories:
        if directory not in unique:
            unique.append(directory)
    return unique
