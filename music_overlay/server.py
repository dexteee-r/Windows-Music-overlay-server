"""Serveur de l'overlay : routes HTTP et cycle de vie.

Deux moitiés complémentaires :

- ``create_app`` construit l'application Flask. C'est une fabrique : elle reçoit
  ses dépendances en paramètre, ce qui rend l'API testable sans Windows ni
  serveur réel (voir ``tests/test_api.py``).
- ``ServerRuntime`` démarre, arrête et redémarre ce serveur. Flask ``app.run()``
  n'étant pas arrêtable proprement, on passe par ``werkzeug.make_server``, qui
  expose un vrai ``shutdown()``.
"""

from __future__ import annotations

import logging
import socket
import threading
from collections.abc import Callable
from typing import Any

from flask import Blueprint, Flask, current_app, jsonify, request
from flask_cors import CORS
from werkzeug.serving import BaseWSGIServer, make_server

from . import __version__
from .config import ConfigError, ConfigStore, ServerSettings
from .media import MediaUnavailableError, MediaWatcher, list_sources
from .skins import SkinNotFoundError, SkinRepository

logger = logging.getLogger(__name__)

EXTENSION_KEY = "music_overlay"
PORT_SEARCH_ATTEMPTS = 20
PORT_SEARCH_STEP = 1

NO_SKIN_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Music Overlay</title></head>
<body style="background:#1a1a2e;color:#fff;font-family:'Segoe UI',sans-serif;padding:2rem">
  <h1>Aucun skin disponible</h1>
  <p>Le dossier <code>skins/</code> est vide ou illisible.</p>
  <p>Reinstallez l'application ou restaurez un dossier de skin, puis rechargez cette page.</p>
</body>
</html>
"""


class ServerAlreadyRunningError(RuntimeError):
    """Le serveur tourne déjà."""


# ======================================================================
# Application Flask
# ======================================================================


class OverlayServices:
    """Dépendances partagées par les routes."""

    def __init__(self, config: ConfigStore, skins: SkinRepository, watcher: MediaWatcher):
        self.config = config
        self.skins = skins
        self.watcher = watcher


def _services() -> OverlayServices:
    return current_app.extensions[EXTENSION_KEY]


def _safe_active_skin(skins: SkinRepository) -> str:
    try:
        return skins.active_id
    except SkinNotFoundError:
        return ""


api = Blueprint("api", __name__, url_prefix="/api")
overlay = Blueprint("overlay", __name__)


@overlay.route("/")
def index() -> Any:
    """Sert le HTML du skin actif (c'est l'URL à mettre dans OBS)."""
    services = _services()
    try:
        return services.skins.active_html()
    except SkinNotFoundError as exc:
        logger.error("Aucun skin servable : %s", exc)
        return NO_SKIN_PAGE, 503


@overlay.route("/health")
def health() -> Any:
    """Sonde légère utilisée par la GUI pour confirmer que le serveur répond."""
    services = _services()
    return jsonify(
        {
            "status": "ok",
            "version": __version__,
            "media_available": services.watcher.running,
            "active_skin": _safe_active_skin(services.skins),
        }
    )


@api.route("/current-track")
def current_track() -> Any:
    """Piste en cours, au format attendu par les skins."""
    return jsonify(_services().watcher.current.to_dict())


@api.route("/skins")
@api.route("/list-skins")
def list_skins() -> Any:
    """Liste des skins installés et identifiant du skin actif."""
    services = _services()
    skins = services.skins.list_skins()
    return jsonify(
        {
            "skins": [skin.to_dict() for skin in skins],
            "active_skin": _safe_active_skin(services.skins),
            "count": len(skins),
        }
    )


@api.route("/set-skin", methods=["POST"])
@api.route("/set-skin/<skin_id>", methods=["GET", "POST"])
def set_skin(skin_id: str | None = None) -> Any:
    """Change le skin actif.

    Accepte ``/api/set-skin/<id>`` et ``POST /api/set-skin`` avec un corps
    ``{"skin_id": "..."}`` — les deux formes étaient documentées.
    """
    services = _services()

    if skin_id is None:
        payload = request.get_json(silent=True) or {}
        skin_id = payload.get("skin_id") or request.form.get("skin_id")

    if not skin_id:
        return jsonify({"success": False, "message": "Parametre 'skin_id' manquant"}), 400

    try:
        skin = services.skins.set_active(skin_id)
    except SkinNotFoundError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "active_skin": _safe_active_skin(services.skins),
            }
        ), 404

    return jsonify(
        {"success": True, "message": f"Skin change pour : {skin.name}", "active_skin": skin.id}
    )


@api.route("/sources")
def sources() -> Any:
    """Applications média détectées, filtre ignoré.

    Alimente le bouton « Détecter les applications » de la GUI.
    """
    services = _services()
    try:
        detected = list_sources(services.config.media_filter)
    except MediaUnavailableError as exc:
        return jsonify({"success": False, "message": str(exc), "sources": []}), 503

    return jsonify(
        {
            "success": True,
            "sources": [source.to_dict() for source in detected],
            "count": len(detected),
        }
    )


@api.route("/reload-config", methods=["GET", "POST"])
def reload_config() -> Any:
    """Relit la configuration et les skins depuis le disque."""
    services = _services()
    services.config.reload()
    services.skins.invalidate()
    return jsonify(
        {
            "success": True,
            "message": "Configuration rechargee",
            "filter_mode": services.config.media_filter.mode,
        }
    )


@api.errorhandler(ConfigError)
def _handle_config_error(exc: ConfigError) -> Any:
    return jsonify({"success": False, "message": str(exc)}), 400


def create_app(config: ConfigStore, skins: SkinRepository, watcher: MediaWatcher) -> Flask:
    """Construit l'application Flask servant l'overlay."""
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.extensions[EXTENSION_KEY] = OverlayServices(config, skins, watcher)

    # L'overlay lui-même est servi par ce serveur ; CORS ne sert qu'aux
    # intégrations tierces qui interrogent l'API JSON.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(overlay)
    app.register_blueprint(api)
    return app


# ======================================================================
# Choix du port
# ======================================================================


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


def os_assigned_port(host: str) -> int:
    """Demande un port libre au système (dernier recours).

    Raises:
        OSError: si le système ne peut attribuer aucun port.
    """
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as probe:
        probe.bind((host, 0))
        return int(probe.getsockname()[1])


def find_available_port(host: str, preferred: int, attempts: int = PORT_SEARCH_ATTEMPTS) -> int:
    """Retourne ``preferred`` s'il est libre, sinon le premier port libre suivant.

    Évite l'échec au démarrage quand OBS, un autre logiciel — ou une instance
    précédente mal fermée — occupe déjà le port.

    Si toute la plage explorée est indisponible, on laisse le système choisir :
    Windows réserve parfois des blocs entiers de ports (Hyper-V, WSL, plages
    exclues), ce qui condamnerait sinon le démarrage.

    Raises:
        OSError: si même le système ne peut attribuer aucun port.
    """
    for offset in range(attempts):
        candidate = preferred + offset * PORT_SEARCH_STEP
        if candidate > 65535:
            break
        if is_port_available(host, candidate):
            return candidate

    logger.warning(
        "Aucun port libre entre %s et %s, attribution laissee au systeme",
        preferred,
        preferred + attempts - 1,
    )
    try:
        return os_assigned_port(host)
    except OSError as exc:
        raise OSError(
            f"Aucun port disponible sur {host} (essais a partir de {preferred}). "
            "Fermez les applications qui occupent ces ports ou changez le port."
        ) from exc


# ======================================================================
# Cycle de vie
# ======================================================================


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

    @classmethod
    def create(cls, config: ConfigStore | None = None) -> ServerRuntime:
        """Assemble un serveur prêt à démarrer, avec ses dépendances.

        Les fichiers de configuration manquants sont créés au passage : un
        premier lancement ne peut donc pas échouer faute de ``config/``.
        """
        store = config if config is not None else ConfigStore()
        try:
            store.ensure_defaults()
        except OSError as exc:
            logger.warning(
                "Configuration par defaut non ecrite (%s), valeurs memoire utilisees", exc
            )
        return cls(
            store,
            skins=SkinRepository(config_dir=store.directory),
            watcher=MediaWatcher(store),
        )

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
