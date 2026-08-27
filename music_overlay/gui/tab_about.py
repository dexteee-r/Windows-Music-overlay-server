"""Onglet À propos : version, état de l'installation et emplacements."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from .. import __app_name__, __version__, paths

if TYPE_CHECKING:
    from .window import MusicOverlayWindow

DESCRIPTION = (
    "Overlay web de la musique en cours de lecture sur Windows,\n"
    "pour OBS, Streamlabs et tout logiciel acceptant une source navigateur."
)


class AboutTab(ttk.Frame):
    """Informations sur l'application et son installation."""

    def __init__(self, parent: tk.Misc, app: MusicOverlayWindow):
        super().__init__(parent)
        self.app = app
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=__app_name__, font=("Segoe UI", 18, "bold")).pack(pady=(10, 2))
        ttk.Label(frame, text=f"Version {__version__}", font=("Segoe UI", 10)).pack(pady=(0, 16))

        self.details = ttk.Label(frame, text="", font=("Segoe UI", 9), justify="left")
        self.details.pack(anchor="w")

        ttk.Label(
            frame,
            text=f"Dossier de l'application : {paths.app_dir()}",
            font=("Segoe UI", 8),
            foreground="gray",
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(16, 0))

    def refresh(self) -> None:
        """Recalcule les informations qui dépendent de l'état courant."""
        count = len(self.app.skins.list_skins())
        settings = self.app.config.settings
        self.details.config(
            text=(
                f"{DESCRIPTION}\n\n"
                f"  Skins installes  : {count}\n"
                f"  Port configure   : {settings.port}\n"
                f"  API              : /api/current-track, /api/skins, /api/sources\n"
                f"  Journal          : {paths.logs_dir()}\n"
            )
        )
