"""Onglet Paramètres : serveur, filtre des applications et démarrage automatique."""

from __future__ import annotations

import logging
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

from ..config import ConfigError
from ..media import MediaSource, MediaUnavailableError, list_sources
from .dialogs import ask_sources

if TYPE_CHECKING:
    from .window import MusicOverlayWindow

logger = logging.getLogger(__name__)

AIDE_MANUELLE = (
    "Si la detection ne trouve rien, ajoutez l'identifiant a la main :\n"
    "   1. passez en mode « Tout accepter » et enregistrez\n"
    "   2. lancez votre musique, puis ouvrez la page ci-dessous\n"
    "   3. copiez la valeur de « source_app » dans la liste voulue"
)
LIBELLE_DETECTION = "Detecter les applications en cours"


def lignes(widget: tk.Text) -> list[str]:
    """Contenu d'une zone de texte, une entrée par ligne, sans vide ni espace."""
    return [line.strip() for line in widget.get("1.0", tk.END).splitlines() if line.strip()]


class SettingsTab(ttk.Frame):
    """Formulaire de configuration, appliqué à chaud."""

    def __init__(self, parent: tk.Misc, app: MusicOverlayWindow):
        super().__init__(parent)
        self.app = app
        self._build()
        self.load()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Parametres", font=("Segoe UI", 14, "bold")).pack(pady=(0, 12))

        self._build_server_section(frame)
        self._build_filter_section(frame)

        startup = ttk.LabelFrame(frame, text="Demarrage", padding=10)
        startup.pack(fill="x", pady=(10, 0))
        self.autostart_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            startup,
            text="Lancer automatiquement au demarrage de Windows",
            variable=self.autostart_var,
        ).pack(anchor="w")

        ttk.Button(frame, text="Enregistrer", command=self.save).pack(pady=14)
        ttk.Label(
            frame,
            text="Les filtres et le skin s'appliquent immediatement, sans redemarrer.",
            font=("Segoe UI", 8, "italic"),
            foreground="gray",
        ).pack()

    def _build_server_section(self, parent: tk.Misc) -> None:
        server = ttk.LabelFrame(parent, text="Serveur", padding=10)
        server.pack(fill="x")

        port_row = ttk.Frame(server)
        port_row.pack(fill="x", pady=4)
        ttk.Label(port_row, text="Port :", width=24).pack(side="left")
        self.port_entry = ttk.Entry(port_row, width=12)
        self.port_entry.pack(side="left")
        ttk.Label(port_row, text="(1024-65535)", font=("Segoe UI", 8)).pack(side="left", padx=5)

        host_row = ttk.Frame(server)
        host_row.pack(fill="x", pady=4)
        ttk.Label(host_row, text="Adresse :", width=24).pack(side="left")
        self.host_entry = ttk.Entry(host_row, width=20)
        self.host_entry.pack(side="left")
        ttk.Label(host_row, text="127.0.0.1 = ce PC uniquement", font=("Segoe UI", 8)).pack(
            side="left", padx=5
        )

        refresh_row = ttk.Frame(server)
        refresh_row.pack(fill="x", pady=4)
        ttk.Label(refresh_row, text="Intervalle de mise a jour :", width=24).pack(side="left")
        self.refresh_entry = ttk.Entry(refresh_row, width=8)
        self.refresh_entry.pack(side="left")
        ttk.Label(refresh_row, text="secondes (0.1 - 10)", font=("Segoe UI", 8)).pack(
            side="left", padx=5
        )

    def _build_filter_section(self, parent: tk.Misc) -> None:
        media = ttk.LabelFrame(parent, text="Filtre des applications", padding=10)
        media.pack(fill="x", pady=(10, 0))

        self.filter_mode = tk.StringVar(value="whitelist")
        for texte, valeur in (
            ("Tout accepter", "all"),
            ("Whitelist : uniquement les applications autorisees", "whitelist"),
            ("Blacklist : tout sauf les applications bloquees", "blacklist"),
        ):
            ttk.Radiobutton(media, text=texte, variable=self.filter_mode, value=valeur).pack(
                anchor="w"
            )

        detect_row = ttk.Frame(media)
        detect_row.pack(fill="x", pady=(8, 4))
        self.detect_button = ttk.Button(
            detect_row, text=LIBELLE_DETECTION, command=self.detect_sources
        )
        self.detect_button.pack(side="left")
        ttk.Label(
            detect_row,
            text="Lancez votre musique, puis cliquez ici.",
            font=("Segoe UI", 8, "italic"),
            foreground="gray",
        ).pack(side="left", padx=8)

        # Repli manuel : la detection ne voit que les applications qui alimentent
        # les controles media de Windows. Pour les autres, l'utilisateur doit
        # pouvoir coller l'identifiant lui-meme.
        manual = ttk.Frame(media)
        manual.pack(fill="x", pady=(2, 6))
        ttk.Label(
            manual, text=AIDE_MANUELLE, font=("Segoe UI", 8), foreground="gray", justify="left"
        ).pack(anchor="w")
        ttk.Button(
            manual, text="Ouvrir la page source_app", command=self.open_current_track_api
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(media, text="Applications autorisees (une par ligne) :").pack(
            anchor="w", pady=(6, 2)
        )
        self.allowed_text = tk.Text(media, height=3, font=("Consolas", 8))
        self.allowed_text.pack(fill="x")

        ttk.Label(media, text="Applications bloquees (une par ligne) :").pack(
            anchor="w", pady=(8, 2)
        )
        self.blocked_text = tk.Text(media, height=3, font=("Consolas", 8))
        self.blocked_text.pack(fill="x")

    # ------------------------------------------------------------------
    # Lecture / écriture
    # ------------------------------------------------------------------
    def load(self) -> None:
        """Remplit le formulaire depuis la configuration enregistrée."""
        settings = self.app.config.settings
        media_filter = self.app.config.media_filter

        for entry, value in (
            (self.port_entry, settings.port),
            (self.host_entry, settings.host),
            (self.refresh_entry, settings.refresh_interval),
        ):
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

        self.filter_mode.set(media_filter.mode)
        self.allowed_text.delete("1.0", tk.END)
        self.allowed_text.insert("1.0", "\n".join(media_filter.allowed_apps))
        self.blocked_text.delete("1.0", tk.END)
        self.blocked_text.insert("1.0", "\n".join(media_filter.blocked_apps))
        self.autostart_var.set(self.app.startup.is_enabled())

    def save(self) -> None:
        """Valide et enregistre ; propose de redémarrer si le réseau change."""
        previous = self.app.config.settings
        try:
            settings = self.app.config.save_settings(
                self.host_entry.get(), self.port_entry.get(), self.refresh_entry.get()
            )
            self.app.config.save_media_filter(
                self.filter_mode.get(),
                lignes(self.allowed_text),
                lignes(self.blocked_text),
            )
        except ConfigError as exc:
            messagebox.showerror("Valeur invalide", str(exc))
            return
        except OSError as exc:
            messagebox.showerror("Enregistrement impossible", str(exc))
            return

        ok, message = self.app.startup.toggle(self.autostart_var.get())
        if not ok:
            messagebox.showwarning("Demarrage automatique", message)

        network_changed = (settings.host, settings.port) != (previous.host, previous.port)
        if self.app.runtime.running and network_changed:
            if messagebox.askyesno(
                "Redemarrer le serveur ?",
                "L'adresse ou le port a change.\n\nRedemarrer le serveur maintenant ?",
            ):
                self.app.stop_server()
                self.app.start_server()
        else:
            logger.info("Parametres appliques immediatement")
            messagebox.showinfo("Enregistre", "Parametres enregistres et appliques.")

        self.app.refresh_server_state()

    # ------------------------------------------------------------------
    # Détection des applications
    # ------------------------------------------------------------------
    def detect_sources(self) -> None:
        """Liste les applications média actives dans un thread de fond."""
        self.detect_button.config(state="disabled", text="Detection en cours...")
        media_filter = self.app.config.media_filter

        def worker() -> None:
            try:
                sources = list_sources(media_filter)
                error: str | None = None
            except MediaUnavailableError as exc:
                sources, error = [], str(exc)
            except Exception as exc:
                sources, error = [], f"Detection impossible : {exc}"
            self.app.root.after(0, self._show_detected, sources, error)

        threading.Thread(target=worker, name="detect-sources", daemon=True).start()

    def _show_detected(self, sources: list[MediaSource], error: str | None) -> None:
        self.detect_button.config(state="normal", text=LIBELLE_DETECTION)

        if error:
            messagebox.showerror(
                "Detection impossible",
                f"{error}\n\n"
                "Vous pouvez ajouter l'application a la main : suivez la procedure "
                "indiquee sous le bouton de detection.",
            )
            return

        chosen = ask_sources(self.app.root, sources)
        if not chosen:
            return

        existing = lignes(self.allowed_text)
        for app_id in chosen:
            if app_id not in existing:
                existing.append(app_id)

        self.allowed_text.delete("1.0", tk.END)
        self.allowed_text.insert("1.0", "\n".join(existing))

        if self.filter_mode.get() == "all":
            self.filter_mode.set("whitelist")

        logger.info("%d application(s) ajoutee(s) a la liste autorisee", len(chosen))
        messagebox.showinfo(
            "Applications ajoutees",
            "Cliquez sur « Enregistrer » pour appliquer le nouveau filtre.",
        )

    def open_current_track_api(self) -> None:
        """Ouvre ``/api/current-track`` : repli manuel pour relever ``source_app``.

        Utile quand la détection automatique ne voit pas le lecteur : la page
        affiche l'identifiant exact de l'application en cours de lecture.
        """
        if not self.app.ensure_server_running("Le serveur doit tourner pour afficher cette page."):
            return
        webbrowser.open(f"{self.app.runtime.settings.url}/api/current-track")
