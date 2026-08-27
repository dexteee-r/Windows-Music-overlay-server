"""Fenêtres secondaires de l'interface."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Sequence
from tkinter import ttk

from ..media import MediaSource


class SourcePickerDialog(tk.Toplevel):
    """Sélection des applications média détectées.

    Remplace la procédure manuelle « ouvrez /api/current-track et recopiez le
    champ source_app » : l'utilisateur coche ce qu'il veut autoriser.
    """

    def __init__(self, parent: tk.Misc, sources: Sequence[MediaSource]):
        super().__init__(parent)
        self.title("Applications media detectees")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.selected: list[str] = []
        self._vars: list[tuple[tk.BooleanVar, str]] = []

        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        if not sources:
            ttk.Label(
                container,
                text=(
                    "Aucune application media detectee.\n\n"
                    "Lancez votre lecteur (Spotify, Apple Music...), mettez une\n"
                    "musique en lecture, puis relancez la detection.\n\n"
                    "Si rien n'apparait malgre tout, l'application n'alimente pas les\n"
                    "controles media de Windows : ajoutez son identifiant a la main\n"
                    "en suivant la procedure affichee sous le bouton de detection."
                ),
                justify="left",
            ).pack(anchor="w")
        else:
            ttk.Label(
                container,
                text="Cochez les applications a autoriser :",
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", pady=(0, 10))

            for source in sources:
                variable = tk.BooleanVar(value=not source.allowed)
                row = ttk.Frame(container)
                row.pack(fill="x", pady=3)

                label = source.app_id
                if source.title:
                    label += f"  —  {source.title}"
                    if source.artist:
                        label += f" ({source.artist})"

                ttk.Checkbutton(row, variable=variable).pack(side="left")
                ttk.Label(
                    row, text=label, font=("Consolas", 8), wraplength=520, justify="left"
                ).pack(side="left", padx=(4, 0))

                state = []
                if source.is_playing:
                    state.append("en lecture")
                if source.allowed:
                    state.append("deja autorisee")
                if state:
                    ttk.Label(
                        container,
                        text="      " + ", ".join(state),
                        font=("Segoe UI", 8, "italic"),
                        foreground="gray",
                    ).pack(anchor="w")

                self._vars.append((variable, source.app_id))

        buttons = ttk.Frame(container)
        buttons.pack(fill="x", pady=(15, 0))
        ttk.Button(buttons, text="Annuler", command=self._cancel).pack(side="right")
        ttk.Button(buttons, text="Ajouter la selection", command=self._confirm).pack(
            side="right", padx=5
        )

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda _event: self._cancel())

    def _confirm(self) -> None:
        self.selected = [app_id for variable, app_id in self._vars if variable.get()]
        self.destroy()

    def _cancel(self) -> None:
        self.selected = []
        self.destroy()


def ask_sources(parent: tk.Misc, sources: Sequence[MediaSource]) -> list[str]:
    """Affiche le sélecteur et retourne les identifiants cochés."""
    dialog = SourcePickerDialog(parent, sources)
    parent.wait_window(dialog)
    return dialog.selected


class ReportDialog(tk.Toplevel):
    """Fenêtre de texte défilant (rapport de diagnostic)."""

    def __init__(self, parent: tk.Misc, title: str, report: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("720x520")
        self.transient(parent)

        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        text = tk.Text(frame, wrap="word", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

        text.insert("1.0", report)
        text.configure(state="disabled")

        ttk.Button(self, text="Fermer", command=self.destroy).pack(pady=(0, 10))
        self.bind("<Escape>", lambda _event: self.destroy())
