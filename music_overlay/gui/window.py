"""Fenêtre principale : assemble les onglets, le serveur et la barre des tâches.

Chaque onglet vit dans son propre module (``tab_*.py``) et reçoit cette fenêtre
en paramètre : elle est le point d'accès unique aux services partagés
(configuration, skins, serveur) et le seul endroit qui coordonne les onglets
entre eux.
"""

from __future__ import annotations

import contextlib
import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .. import __app_name__, __version__
from ..config import ConfigStore
from ..logging_setup import CallbackHandler
from ..server import ServerAlreadyRunningError, ServerRuntime
from ..startup import StartupManager
from . import assets
from .tab_about import AboutTab
from .tab_control import ControlTab
from .tab_settings import SettingsTab
from .tab_skins import SkinsTab

logger = logging.getLogger(__name__)

WINDOW_SIZE = "760x820"
MIN_SIZE = (680, 620)

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
        self.root.minsize(*MIN_SIZE)

        self.config = ConfigStore()
        self.runtime = ServerRuntime.create(self.config)
        self.skins = self.runtime.skins
        self.startup = StartupManager()
        self.tray_icon = None

        self._build_ui()
        self._attach_log_handler()
        self._setup_tray()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(200, self.skins_tab.refresh)

    # ==================================================================
    # Construction
    # ==================================================================
    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # L'onglet A propos est construit en premier : les autres l'actualisent.
        self.about_tab = AboutTab(notebook, self)
        self.control_tab = ControlTab(notebook, self)
        self.skins_tab = SkinsTab(notebook, self)
        self.settings_tab = SettingsTab(notebook, self)

        notebook.add(self.control_tab, text="  Controle  ")
        notebook.add(self.skins_tab, text="  Skins  ")
        notebook.add(self.settings_tab, text="  Parametres  ")
        notebook.add(self.about_tab, text="  A propos  ")

        self.refresh_server_state()

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
            self.root.after(0, self.control_tab.append_log, message)

    # ==================================================================
    # Serveur
    # ==================================================================
    def start_server(self) -> None:
        """Démarre le serveur, en signalant un éventuel changement de port."""
        wanted_port = self.config.settings.port
        try:
            settings = self.runtime.start()
        except ServerAlreadyRunningError:
            self.refresh_server_state()
            return
        except OSError as exc:
            logger.error("Demarrage impossible : %s", exc)
            messagebox.showerror("Demarrage impossible", str(exc))
            return

        self.refresh_server_state()
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
        self.refresh_server_state()

    def refresh_server_state(self) -> None:
        """Propage l'état du serveur aux onglets concernés."""
        self.control_tab.set_server_state(self.runtime.running, self.runtime.settings.url)
        self.about_tab.refresh()

    def ensure_server_running(self, raison: str) -> bool:
        """Garantit que le serveur tourne, en proposant de le démarrer.

        Returns:
            ``True`` si le serveur tourne à la sortie.
        """
        if self.runtime.running:
            return True
        if not messagebox.askyesno("Serveur arrete", f"{raison}\n\nLe demarrer maintenant ?"):
            return False
        self.start_server()
        return self.runtime.running

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
