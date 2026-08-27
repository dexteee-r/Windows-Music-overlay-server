"""Application Flask : routes de l'overlay et API JSON.

``create_app`` est une fabrique : elle reçoit ses dépendances en paramètre
plutôt que de les construire. C'est ce qui rend l'API testable sans Windows ni
serveur réel (voir ``tests/test_api.py``).
"""

from __future__ import annotations

import logging
from typing import Any

from flask import Blueprint, Flask, current_app, jsonify, request
from flask_cors import CORS

from .. import __version__
from ..config import ConfigError, ConfigStore
from ..media import MediaUnavailableError, MediaWatcher, list_sources
from ..skins import SkinNotFoundError, SkinRepository

logger = logging.getLogger(__name__)

EXTENSION_KEY = "music_overlay"

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


class OverlayServices:
    """Dépendances partagées par les routes."""

    def __init__(self, config: ConfigStore, skins: SkinRepository, watcher: MediaWatcher):
        self.config = config
        self.skins = skins
        self.watcher = watcher


def _services() -> OverlayServices:
    return current_app.extensions[EXTENSION_KEY]


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


def _safe_active_skin(skins: SkinRepository) -> str:
    try:
        return skins.active_id
    except SkinNotFoundError:
        return ""


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


def create_app(
    config: ConfigStore,
    skins: SkinRepository,
    watcher: MediaWatcher,
) -> Flask:
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
