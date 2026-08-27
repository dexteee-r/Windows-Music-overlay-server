"""Onglet Contrôle : démarrage du serveur, URL pour OBS et journal."""

from __future__ import annotations

import logging
import tkinter as tk
import webbrowser
from tkinter import scrolledtext, ttk
from typing import TYPE_CHECKING

from ..diagnostics import format_report
from .dialogs import ReportDialog

if TYPE_CHECKING:
    from .window import MusicOverlayWindow

logger = logging.getLogger(__name__)

MAX_LOG_LINES = 500
COULEUR_ACTIF = "#1e8449"
COULEUR_ARRETE = "#c0392b"


class ControlTab(ttk.Frame):
    """Tableau de bord : allumer le serveur, récupérer l'URL, lire le journal."""

    def __init__(self, parent: tk.Misc, app: MusicOverlayWindow):
        super().__init__(parent)
        self.app = app
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Controle du serveur", font=("Segoe UI", 14, "bold")).pack(
            pady=(0, 12)
        )

        actions = ttk.LabelFrame(frame, text="Actions", padding=10)
        actions.pack(fill="x")

        row = ttk.Frame(actions)
        row.pack(fill="x")
        self.start_button = ttk.Button(
            row, text="Demarrer", width=16, command=self.app.start_server
        )
        self.start_button.pack(side="left", padx=3)
        self.stop_button = ttk.Button(row, text="Arreter", width=16, command=self.app.stop_server)
        self.stop_button.pack(side="left", padx=3)
        ttk.Button(row, text="Ouvrir l'overlay", width=18, command=self.open_in_browser).pack(
            side="left", padx=3
        )
        ttk.Button(row, text="Diagnostic", width=14, command=self.show_diagnostic).pack(
            side="left", padx=3
        )

        status = ttk.LabelFrame(frame, text="Etat", padding=10)
        status.pack(fill="x", pady=(10, 0))

        self.status_label = ttk.Label(
            status, text="Serveur arrete", font=("Segoe UI", 10, "bold"), foreground=COULEUR_ARRETE
        )
        self.status_label.pack(anchor="w")

        url_row = ttk.Frame(status)
        url_row.pack(fill="x", pady=(6, 0))
        ttk.Label(url_row, text="URL pour OBS :").pack(side="left")
        self.url_value = ttk.Label(url_row, text="", font=("Consolas", 9), foreground="#2c3e50")
        self.url_value.pack(side="left", padx=(4, 8))
        ttk.Button(url_row, text="Copier", width=9, command=self.copy_url).pack(side="left")

        ttk.Label(
            status,
            text="Dans OBS : source « Navigateur », collez cette URL, 650 x 180 px.",
            font=("Segoe UI", 8, "italic"),
            foreground="gray",
        ).pack(anchor="w", pady=(6, 0))

        logs = ttk.LabelFrame(frame, text="Journal", padding=10)
        logs.pack(fill="both", expand=True, pady=(10, 0))

        self.logs_text = scrolledtext.ScrolledText(
            logs, height=12, font=("Consolas", 9), state="disabled", bg="#f5f5f5"
        )
        self.logs_text.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Mises à jour venant de la fenêtre
    # ------------------------------------------------------------------
    def set_server_state(self, running: bool, url: str) -> None:
        """Reflète l'état du serveur (appelé par la fenêtre principale)."""
        if running:
            self.status_label.config(text="Serveur actif", foreground=COULEUR_ACTIF)
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.status_label.config(text="Serveur arrete", foreground=COULEUR_ARRETE)
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
        self.url_value.config(text=url)

    def append_log(self, message: str) -> None:
        """Ajoute une ligne au journal, en limitant la taille affichée."""
        self.logs_text.config(state="normal")
        self.logs_text.insert(tk.END, message + "\n")

        excess = int(self.logs_text.index("end-1c").split(".")[0]) - MAX_LOG_LINES
        if excess > 0:
            self.logs_text.delete("1.0", f"{excess}.0")

        self.logs_text.see(tk.END)
        self.logs_text.config(state="disabled")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def copy_url(self) -> None:
        url = self.app.runtime.settings.url
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(url)
        logger.info("URL copiee : %s", url)

    def open_in_browser(self) -> None:
        if not self.app.ensure_server_running("Le serveur n'est pas demarre."):
            return
        webbrowser.open(self.app.runtime.settings.url)

    def show_diagnostic(self) -> None:
        """Affiche le rapport d'auto-diagnostic (dépendances, port, skins)."""
        ReportDialog(self.app.root, "Diagnostic", format_report())
