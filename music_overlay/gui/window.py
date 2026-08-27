"""Fenêtre principale de configuration et de contrôle."""

from __future__ import annotations

import contextlib
import logging
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, scrolledtext, ttk

from PIL import Image, ImageTk

from .. import __app_name__, __version__, paths
from ..config import ConfigError, ConfigStore
from ..diagnostics import format_report
from ..logging_setup import CallbackHandler
from ..media import MediaUnavailableError, list_sources
from ..server import ServerAlreadyRunningError, ServerRuntime
from ..skins import Skin, SkinNotFoundError
from ..startup import StartupManager
from . import assets
from .dialogs import ReportDialog, ask_sources

logger = logging.getLogger(__name__)

WINDOW_SIZE = "760x820"
PREVIEW_MAX_SIZE = (480, 290)
MAX_LOG_LINES = 500

try:  # pragma: no cover - dépend de l'environnement graphique
    import pystray

    PYSTRAY_AVAILABLE = True
except ImportError:  # pragma: no cover
    pystray = None  # type: ignore[assignment]
    PYSTRAY_AVAILABLE = False


class MusicOverlayWindow:
    """Interface graphique : vue et orchestration, aucune logique métier.

    Toute la logique vit dans ``music_overlay`` (config, skins, serveur) ; la
    fenêtre ne fait que l'appeler et afficher les résultats.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{__app_name__} v{__version__}")
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(680, 620)

        self.config = ConfigStore()
        self.runtime = ServerRuntime.create(self.config)
        self.skins = self.runtime.skins
        self.startup = StartupManager()

        self._skins_by_label: dict[str, Skin] = {}
        self._preview_cache: dict[str, ImageTk.PhotoImage] = {}
        self._placeholder: ImageTk.PhotoImage | None = None
        self._current_preview: ImageTk.PhotoImage | None = None
        self.tray_icon = None

        self._build_ui()
        self._attach_log_handler()
        self._setup_tray()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(200, self.refresh_skins)

    # ==================================================================
    # Construction de l'interface
    # ==================================================================
    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_skins = ttk.Frame(notebook)
        self.tab_settings = ttk.Frame(notebook)
        self.tab_control = ttk.Frame(notebook)
        self.tab_about = ttk.Frame(notebook)

        notebook.add(self.tab_control, text="  Controle  ")
        notebook.add(self.tab_skins, text="  Skins  ")
        notebook.add(self.tab_settings, text="  Parametres  ")
        notebook.add(self.tab_about, text="  A propos  ")

        self._build_control_tab()
        self._build_skins_tab()
        self._build_settings_tab()
        self._build_about_tab()

        self._load_settings_into_form()
        self._update_server_state(False)

    # ------------------------------------------------------------------
    def _build_control_tab(self) -> None:
        frame = ttk.Frame(self.tab_control, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Controle du serveur", font=("Segoe UI", 14, "bold")).pack(
            pady=(0, 12)
        )

        actions = ttk.LabelFrame(frame, text="Actions", padding=10)
        actions.pack(fill="x")

        row = ttk.Frame(actions)
        row.pack(fill="x")
        self.start_button = ttk.Button(row, text="Demarrer", width=16, command=self.start_server)
        self.start_button.pack(side="left", padx=3)
        self.stop_button = ttk.Button(row, text="Arreter", width=16, command=self.stop_server)
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
            status, text="Serveur arrete", font=("Segoe UI", 10, "bold"), foreground="#c0392b"
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
    def _build_skins_tab(self) -> None:
        frame = ttk.Frame(self.tab_skins, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Selection du skin", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        paned = ttk.PanedWindow(frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        list_frame = ttk.LabelFrame(left, text="Skins installes", padding=8)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.skins_listbox = tk.Listbox(
            list_frame,
            height=12,
            font=("Segoe UI", 10),
            yscrollcommand=scrollbar.set,
            exportselection=False,
        )
        self.skins_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.skins_listbox.yview)
        self.skins_listbox.bind("<<ListboxSelect>>", self._on_skin_selected)
        self.skins_listbox.bind("<Double-Button-1>", lambda _event: self.apply_selected_skin())

        buttons = ttk.Frame(left)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Appliquer", command=self.apply_selected_skin).pack(
            fill="x", pady=2
        )
        ttk.Button(buttons, text="Rafraichir la liste", command=self.refresh_skins).pack(
            fill="x", pady=2
        )

        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        preview = ttk.LabelFrame(right, text="Apercu", padding=10)
        preview.pack(fill="both", expand=True)

        self.preview_label = ttk.Label(preview)
        self.preview_label.pack(pady=(0, 10))

        self.preview_name = ttk.Label(preview, text="", font=("Segoe UI", 12, "bold"))
        self.preview_name.pack(anchor="w")
        self.preview_description = ttk.Label(
            preview, text="", font=("Segoe UI", 9), wraplength=420, justify="left"
        )
        self.preview_description.pack(anchor="w", pady=(4, 0))
        self.preview_meta = ttk.Label(
            preview, text="", font=("Segoe UI", 8), foreground="gray", justify="left"
        )
        self.preview_meta.pack(anchor="w", pady=(8, 0))

        self.active_skin_label = ttk.Label(
            frame, text="Skin actif : ...", font=("Segoe UI", 9, "italic")
        )
        self.active_skin_label.pack(pady=(8, 0))

        self._show_placeholder()

    # ------------------------------------------------------------------
    def _build_settings_tab(self) -> None:
        frame = ttk.Frame(self.tab_settings, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Parametres", font=("Segoe UI", 14, "bold")).pack(pady=(0, 12))

        server = ttk.LabelFrame(frame, text="Serveur", padding=10)
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
        ttk.Label(
            host_row,
            text="127.0.0.1 = ce PC uniquement",
            font=("Segoe UI", 8),
        ).pack(side="left", padx=5)

        refresh_row = ttk.Frame(server)
        refresh_row.pack(fill="x", pady=4)
        ttk.Label(refresh_row, text="Intervalle de mise a jour :", width=24).pack(side="left")
        self.refresh_entry = ttk.Entry(refresh_row, width=8)
        self.refresh_entry.pack(side="left")
        ttk.Label(refresh_row, text="secondes (0.1 - 10)", font=("Segoe UI", 8)).pack(
            side="left", padx=5
        )

        media = ttk.LabelFrame(frame, text="Filtre des applications", padding=10)
        media.pack(fill="x", pady=(10, 0))

        self.filter_mode = tk.StringVar(value="whitelist")
        ttk.Radiobutton(media, text="Tout accepter", variable=self.filter_mode, value="all").pack(
            anchor="w"
        )
        ttk.Radiobutton(
            media,
            text="Whitelist : uniquement les applications autorisees",
            variable=self.filter_mode,
            value="whitelist",
        ).pack(anchor="w")
        ttk.Radiobutton(
            media,
            text="Blacklist : tout sauf les applications bloquees",
            variable=self.filter_mode,
            value="blacklist",
        ).pack(anchor="w")

        detect_row = ttk.Frame(media)
        detect_row.pack(fill="x", pady=(8, 4))
        self.detect_button = ttk.Button(
            detect_row, text="Detecter les applications en cours", command=self.detect_sources
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
            manual,
            text=(
                "Si la detection ne trouve rien, ajoutez l'identifiant a la main :\n"
                "   1. passez en mode « Tout accepter » et enregistrez\n"
                "   2. lancez votre musique, puis ouvrez la page ci-dessous\n"
                "   3. copiez la valeur de « source_app » dans la liste voulue"
            ),
            font=("Segoe UI", 8),
            foreground="gray",
            justify="left",
        ).pack(anchor="w")
        ttk.Button(
            manual,
            text="Ouvrir la page source_app",
            command=self.open_current_track_api,
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

        startup = ttk.LabelFrame(frame, text="Demarrage", padding=10)
        startup.pack(fill="x", pady=(10, 0))
        self.autostart_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            startup,
            text="Lancer automatiquement au demarrage de Windows",
            variable=self.autostart_var,
        ).pack(anchor="w")

        ttk.Button(frame, text="Enregistrer", command=self.save_settings).pack(pady=14)
        ttk.Label(
            frame,
            text="Les filtres et le skin s'appliquent immediatement, sans redemarrer.",
            font=("Segoe UI", 8, "italic"),
            foreground="gray",
        ).pack()

    # ------------------------------------------------------------------
    def _build_about_tab(self) -> None:
        frame = ttk.Frame(self.tab_about, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=__app_name__, font=("Segoe UI", 18, "bold")).pack(pady=(10, 2))
        ttk.Label(frame, text=f"Version {__version__}", font=("Segoe UI", 10)).pack(pady=(0, 16))

        self.about_details = ttk.Label(frame, text="", font=("Segoe UI", 9), justify="left")
        self.about_details.pack(anchor="w")

        ttk.Label(
            frame,
            text=f"Dossier de l'application : {paths.app_dir()}",
            font=("Segoe UI", 8),
            foreground="gray",
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(16, 0))

    def _refresh_about(self) -> None:
        count = len(self.skins.list_skins())
        settings = self.config.settings
        self.about_details.config(
            text=(
                "Overlay web de la musique en cours de lecture sur Windows,\n"
                "pour OBS, Streamlabs et tout logiciel acceptant une source navigateur.\n\n"
                f"  Skins installes  : {count}\n"
                f"  Port configure   : {settings.port}\n"
                f"  API              : /api/current-track, /api/skins, /api/sources\n"
                f"  Journal          : {paths.logs_dir()}\n"
            )
        )

    # ==================================================================
    # Journal
    # ==================================================================
    def _attach_log_handler(self) -> None:
        handler = CallbackHandler(self._log_from_any_thread)
        logging.getLogger().addHandler(handler)
        self._log_handler = handler
        logger.info("%s v%s pret", __app_name__, __version__)

    def _log_from_any_thread(self, message: str) -> None:
        # Tkinter n'est pilotable que depuis le thread principal ; la fenetre
        # peut aussi avoir deja ete detruite quand un thread loggue encore.
        with contextlib.suppress(RuntimeError, tk.TclError):
            self.root.after(0, self._append_log, message)

    def _append_log(self, message: str) -> None:
        self.logs_text.config(state="normal")
        self.logs_text.insert(tk.END, message + "\n")

        excess = int(self.logs_text.index("end-1c").split(".")[0]) - MAX_LOG_LINES
        if excess > 0:
            self.logs_text.delete("1.0", f"{excess}.0")

        self.logs_text.see(tk.END)
        self.logs_text.config(state="disabled")

    # ==================================================================
    # Serveur
    # ==================================================================
    def start_server(self) -> None:
        """Démarre le serveur, en signalant un éventuel changement de port."""
        wanted_port = self.config.settings.port
        try:
            settings = self.runtime.start()
        except ServerAlreadyRunningError:
            self._update_server_state(True)
            return
        except OSError as exc:
            logger.error("Demarrage impossible : %s", exc)
            messagebox.showerror("Demarrage impossible", str(exc))
            return

        self._update_server_state(True)
        if settings.port != wanted_port:
            messagebox.showinfo(
                "Port occupe",
                f"Le port {wanted_port} etait deja utilise.\n\n"
                f"Le serveur ecoute sur {settings.url}.\n"
                "Pensez a mettre a jour l'URL dans OBS, ou enregistrez ce port "
                "dans l'onglet Parametres.",
            )

    def stop_server(self) -> None:
        self.runtime.stop()
        self._update_server_state(False)

    def _update_server_state(self, running: bool) -> None:
        if running:
            self.status_label.config(text="Serveur actif", foreground="#1e8449")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.status_label.config(text="Serveur arrete", foreground="#c0392b")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

        self.url_value.config(text=self.runtime.settings.url)
        self._refresh_about()

    def copy_url(self) -> None:
        url = self.runtime.settings.url
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        logger.info("URL copiee : %s", url)

    def open_in_browser(self) -> None:
        if not self.runtime.running:
            if not messagebox.askyesno(
                "Serveur arrete", "Le serveur n'est pas demarre. Le lancer maintenant ?"
            ):
                return
            self.start_server()
            if not self.runtime.running:
                return
        webbrowser.open(self.runtime.settings.url)

    def open_current_track_api(self) -> None:
        """Ouvre ``/api/current-track`` : repli manuel pour relever ``source_app``.

        Utile quand la détection automatique ne voit pas le lecteur : la page
        affiche l'identifiant exact de l'application en cours de lecture.
        """
        if not self.runtime.running:
            if not messagebox.askyesno(
                "Serveur arrete",
                "Le serveur doit tourner pour afficher cette page.\n\nLe demarrer maintenant ?",
            ):
                return
            self.start_server()
            if not self.runtime.running:
                return
        webbrowser.open(f"{self.runtime.settings.url}/api/current-track")

    def show_diagnostic(self) -> None:
        """Affiche le rapport d'auto-diagnostic (dépendances, port, skins)."""
        ReportDialog(self.root, "Diagnostic", format_report())

    # ==================================================================
    # Skins
    # ==================================================================
    def refresh_skins(self) -> None:
        self.skins.invalidate()
        skins = self.skins.list_skins()

        self.skins_listbox.delete(0, tk.END)
        self._skins_by_label = {}

        try:
            active_id = self.skins.active_id
        except SkinNotFoundError:
            active_id = ""

        for index, skin in enumerate(skins):
            # Deux skins peuvent porter le meme nom : on desambigue par l'id.
            label = skin.name
            if label in self._skins_by_label:
                label = f"{skin.name} ({skin.id})"
            self._skins_by_label[label] = skin
            self.skins_listbox.insert(tk.END, label)
            if skin.id == active_id:
                self.skins_listbox.selection_clear(0, tk.END)
                self.skins_listbox.selection_set(index)
                self.skins_listbox.see(index)
                self._show_skin(skin)

        active = next((skin for skin in skins if skin.id == active_id), None)
        self.active_skin_label.config(text=f"Skin actif : {active.name if active else 'aucun'}")
        logger.info("%d skin(s) disponibles", len(skins))
        self._refresh_about()

    def _selected_skin(self) -> Skin | None:
        selection = self.skins_listbox.curselection()
        if not selection:
            return None
        return self._skins_by_label.get(self.skins_listbox.get(selection[0]))

    def _on_skin_selected(self, _event: object) -> None:
        skin = self._selected_skin()
        if skin is not None:
            self._show_skin(skin)

    def apply_selected_skin(self) -> None:
        """Active le skin sélectionné (effet immédiat, serveur démarré ou non)."""
        skin = self._selected_skin()
        if skin is None:
            messagebox.showwarning("Aucune selection", "Selectionnez un skin dans la liste.")
            return

        try:
            self.skins.set_active(skin.id)
        except SkinNotFoundError as exc:
            messagebox.showerror("Erreur", str(exc))
            return

        self.active_skin_label.config(text=f"Skin actif : {skin.name}")
        logger.info("Skin applique : %s", skin.name)
        messagebox.showinfo(
            "Skin applique",
            f"Skin actif : {skin.name}\n\nRafraichissez la source navigateur dans OBS.",
        )

    def _show_skin(self, skin: Skin) -> None:
        self.preview_name.config(text=skin.name)
        self.preview_description.config(text=skin.description)
        self.preview_meta.config(text=f"Auteur : {skin.author}\nVersion : {skin.version}")

        cached = self._preview_cache.get(skin.id)
        if cached is not None:
            self._set_preview(cached)
            return

        preview_file = skin.preview_file
        if preview_file is None:
            self._show_placeholder()
            return

        try:
            image = Image.open(preview_file)
            image.thumbnail(PREVIEW_MAX_SIZE, Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        except (OSError, ValueError) as exc:
            logger.debug("Apercu illisible pour %s : %s", skin.id, exc)
            self._show_placeholder()
            return

        self._preview_cache[skin.id] = photo
        self._set_preview(photo)

    def _show_placeholder(self) -> None:
        if self._placeholder is None:
            self._placeholder = ImageTk.PhotoImage(assets.create_placeholder_image())
        self._set_preview(self._placeholder)

    def _set_preview(self, photo: ImageTk.PhotoImage) -> None:
        # Référence conservée : sans cela Tk libère l'image et affiche du vide.
        self._current_preview = photo
        self.preview_label.config(image=photo)

    # ==================================================================
    # Paramètres
    # ==================================================================
    def _load_settings_into_form(self) -> None:
        settings = self.config.settings
        media_filter = self.config.media_filter

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
        self.autostart_var.set(self.startup.is_enabled())

    @staticmethod
    def _lines(widget: tk.Text) -> list[str]:
        return [line.strip() for line in widget.get("1.0", tk.END).splitlines() if line.strip()]

    def save_settings(self) -> None:
        """Valide et enregistre ; propose de redémarrer si le réseau change."""
        previous = self.config.settings
        try:
            settings = self.config.save_settings(
                self.host_entry.get(), self.port_entry.get(), self.refresh_entry.get()
            )
            self.config.save_media_filter(
                self.filter_mode.get(),
                self._lines(self.allowed_text),
                self._lines(self.blocked_text),
            )
        except ConfigError as exc:
            messagebox.showerror("Valeur invalide", str(exc))
            return
        except OSError as exc:
            messagebox.showerror("Enregistrement impossible", str(exc))
            return

        ok, message = self.startup.toggle(self.autostart_var.get())
        if not ok:
            messagebox.showwarning("Demarrage automatique", message)

        network_changed = (settings.host, settings.port) != (previous.host, previous.port)
        if self.runtime.running and network_changed:
            if messagebox.askyesno(
                "Redemarrer le serveur ?",
                "L'adresse ou le port a change.\n\nRedemarrer le serveur maintenant ?",
            ):
                self.runtime.stop()
                self.start_server()
        else:
            logger.info("Parametres appliques immediatement")
            messagebox.showinfo("Enregistre", "Parametres enregistres et appliques.")

        self._update_server_state(self.runtime.running)

    def detect_sources(self) -> None:
        """Liste les applications média actives dans un thread de fond."""
        self.detect_button.config(state="disabled", text="Detection en cours...")
        media_filter = self.config.media_filter

        def worker() -> None:
            try:
                sources = list_sources(media_filter)
                error: str | None = None
            except MediaUnavailableError as exc:
                sources, error = [], str(exc)
            except Exception as exc:
                sources, error = [], f"Detection impossible : {exc}"
            self.root.after(0, self._show_detected_sources, sources, error)

        threading.Thread(target=worker, name="detect-sources", daemon=True).start()

    def _show_detected_sources(self, sources: list, error: str | None) -> None:
        self.detect_button.config(state="normal", text="Detecter les applications en cours")

        if error:
            messagebox.showerror(
                "Detection impossible",
                f"{error}\n\n"
                "Vous pouvez ajouter l'application a la main : suivez la procedure "
                "indiquee sous le bouton de detection.",
            )
            return

        chosen = ask_sources(self.root, sources)
        if not chosen:
            return

        existing = self._lines(self.allowed_text)
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

    # ==================================================================
    # Barre des tâches
    # ==================================================================
    def _setup_tray(self) -> None:
        if not PYSTRAY_AVAILABLE:
            logger.info("pystray absent : pas d'icone dans la barre des taches")
            return

        menu = pystray.Menu(
            pystray.MenuItem("Afficher", self._tray_show, default=True),
            pystray.MenuItem("Masquer", self._tray_hide),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Demarrer le serveur", self._tray_start),
            pystray.MenuItem("Arreter le serveur", self._tray_stop),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quitter", self._tray_quit),
        )
        self.tray_icon = pystray.Icon(
            "music_overlay", assets.create_tray_image(), __app_name__, menu
        )
        threading.Thread(target=self.tray_icon.run, name="tray", daemon=True).start()

    def _tray_show(self, *_args: object) -> None:
        self.root.after(0, self._show_window)

    def _tray_hide(self, *_args: object) -> None:
        self.root.after(0, self.root.withdraw)

    def _tray_start(self, *_args: object) -> None:
        self.root.after(0, self.start_server)

    def _tray_stop(self, *_args: object) -> None:
        self.root.after(0, self.stop_server)

    def _tray_quit(self, *_args: object) -> None:
        self.root.after(0, self.quit)

    def _show_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    # ==================================================================
    # Fermeture
    # ==================================================================
    def _on_close(self) -> None:
        """La croix réduit dans la barre des tâches, sauf si elle est absente."""
        if self.tray_icon is not None:
            self.root.withdraw()
            logger.info("Fenetre masquee (icone dans la barre des taches)")
            return
        self.quit()

    def quit(self) -> None:
        logger.info("Fermeture de l'application")
        logging.getLogger().removeHandler(self._log_handler)

        if self.tray_icon is not None:
            self.tray_icon.stop()
        self.runtime.stop()
        self.root.quit()
        self.root.destroy()
