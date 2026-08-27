"""Cycle de vie du serveur HTTP.

``app.run()`` de Flask n'est pas arrêtable proprement : c'est pourquoi la GUI
ne savait, avant la v3, que « marquer » le serveur comme arrêté sans jamais
libérer le port. On passe ici par ``werkzeug.serving.make_server``, qui expose
un vrai ``shutdown()`` — démarrer, arrêter et redémarrer devient possible dans
le même processus.
"""

from __future__ import annotations

import logging
import socket
import threading
from collections.abc import Callable

from werkzeug.serving import BaseWSGIServer, make_server

from ..config import ConfigStore, ServerSettings
from ..media import MediaWatcher
from ..skins import SkinRepository
from .app import create_app

logger = logging.getLogger(__name__)

PORT_SEARCH_ATTEMPTS = 20
PORT_SEARCH_STEP = 1


class ServerAlreadyRunningError(RuntimeError):
    """Le serveur tourne déjà."""


def is_port_available(host: str, port: int) -> bool:
    """Teste si ``host:port`` peut être écouté maintenant."""
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as probe:
        # Sous Windows, SO_REUSEADDR autoriserait deux écoutes simultanées :
        # on ne l'active pas, sinon le test répondrait toujours « libre ».
        try:
            probe.bind((host, port))
        except OSError:
            return False
    return True


def find_available_port(host: str, preferred: int, attempts: int = PORT_SEARCH_ATTEMPTS) -> int:
    """Retourne ``preferred`` s'il est libre, sinon le premier port libre suivant.

    Évite l'échec au démarrage quand OBS, un autre logiciel — ou une instance
    précédente mal fermée — occupe déjà le port.

    Raises:
        OSError: si aucun port libre n'a été trouvé.
    """
    for offset in range(attempts):
        candidate = preferred + offset * PORT_SEARCH_STEP
        if candidate > 65535:
            break
        if is_port_available(host, candidate):
            return candidate
    raise OSError(
        f"Aucun port libre trouve entre {preferred} et {preferred + attempts - 1}. "
        "Fermez les applications qui utilisent ces ports ou changez le port."
    )


class ServerRuntime:
    """Démarre, arrête et redémarre le serveur et sa surveillance média."""

    def __init__(
        self,
        config: ConfigStore,
        skins: SkinRepository | None = None,
        watcher: MediaWatcher | None = None,
        *,
        auto_port: bool = True,
    ):
        self.config = config
        self.skins = skins if skins is not None else SkinRepository(config_dir=config.directory)
        self.watcher = watcher if watcher is not None else MediaWatcher(config)
        self.auto_port = auto_port

        self._lock = threading.RLock()
        self._server: BaseWSGIServer | None = None
        self._thread: threading.Thread | None = None
        self._settings: ServerSettings | None = None

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------
    @property
    def running(self) -> bool:
        with self._lock:
            return self._server is not None

    @property
    def settings(self) -> ServerSettings:
        """Paramètres réellement utilisés (port éventuellement réajusté)."""
        with self._lock:
            return self._settings or self.config.settings

    @property
    def url(self) -> str:
        return self.settings.url

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------
    def start(self, on_error: Callable[[Exception], None] | None = None) -> ServerSettings:
        """Démarre le serveur et la surveillance média.

        Returns:
            Les paramètres effectifs, dont le port réellement écouté.

        Raises:
            ServerAlreadyRunningError: si le serveur tourne déjà.
            OSError: si aucun port n'est disponible.
        """
        with self._lock:
            if self._server is not None:
                raise ServerAlreadyRunningError("Le serveur est deja demarre")

            wanted = self.config.settings
            port = wanted.port
            if not is_port_available(wanted.host, port):
                if not self.auto_port:
                    raise OSError(f"Le port {port} est deja utilise")
                port = find_available_port(wanted.host, port)
                logger.warning("Port %s occupe, bascule automatique sur %s", wanted.port, port)

            settings = ServerSettings(
                host=wanted.host, port=port, refresh_interval=wanted.refresh_interval
            )
            app = create_app(self.config, self.skins, self.watcher)
            server = make_server(settings.host, settings.port, app, threaded=True)

            def _serve() -> None:
                try:
                    server.serve_forever()
                except Exception as exc:
                    logger.exception("Le serveur s'est arrete sur une erreur")
                    if on_error is not None:
                        on_error(exc)

            thread = threading.Thread(target=_serve, name="overlay-server", daemon=True)
            thread.start()

            self._server = server
            self._thread = thread
            self._settings = settings

        self.watcher.start()
        logger.info("Serveur demarre sur %s", settings.url)
        return settings

    def stop(self, timeout: float = 5.0) -> None:
        """Arrête le serveur et libère réellement le port."""
        with self._lock:
            server, thread = self._server, self._thread
            self._server = None
            self._thread = None

        self.watcher.stop()

        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None and thread.is_alive():
            thread.join(timeout=timeout)
        logger.info("Serveur arrete")

    def restart(self) -> ServerSettings:
        """Arrête puis redémarre (utilisé après un changement de port)."""
        if self.running:
            self.stop()
        return self.start()

    def wait(self) -> None:
        """Bloque tant que le serveur tourne (mode console).

        ``KeyboardInterrupt`` est laissé remonter : c'est à l'appelant de
        décider quoi afficher avant d'appeler ``stop()``.
        """
        while True:
            with self._lock:
                thread = self._thread
            if thread is None:
                return
            thread.join(timeout=0.5)
