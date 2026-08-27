"""Assemblage des composants de l'application.

Point unique où config, skins, surveillance média et serveur sont câblés
ensemble : la GUI, le mode console et les tests partent tous d'ici.
"""

from __future__ import annotations

import logging

from . import __app_name__, __version__
from .config import ConfigStore
from .diagnostics import format_report, run_checks
from .logging_setup import setup_logging
from .media import MediaWatcher
from .server.runtime import ServerRuntime
from .skins import SkinRepository

logger = logging.getLogger(__name__)


def build_runtime(config: ConfigStore | None = None) -> ServerRuntime:
    """Construit un ``ServerRuntime`` prêt à démarrer.

    Les fichiers de configuration manquants sont créés au passage : un premier
    lancement ne peut donc pas échouer faute de ``config/``.
    """
    store = config if config is not None else ConfigStore()
    try:
        store.ensure_defaults()
    except OSError as exc:
        logger.warning("Configuration par defaut non ecrite (%s), valeurs memoire utilisees", exc)

    skins = SkinRepository(config_dir=store.directory)
    watcher = MediaWatcher(store)
    return ServerRuntime(store, skins=skins, watcher=watcher)


def run_console() -> int:
    """Lance le serveur en mode console (``server.py``), jusqu'à ``Ctrl+C``."""
    setup_logging()
    logger.info("%s v%s", __app_name__, __version__)

    failures = [check for check in run_checks() if not check.ok and check.critical]
    if failures:
        print(format_report())
        return 1

    runtime = build_runtime()
    try:
        settings = runtime.start()
    except OSError as exc:
        logger.error("Demarrage impossible : %s", exc)
        return 1

    print("")
    print("=" * 68)
    print(f"  {__app_name__} v{__version__}")
    print("=" * 68)
    print(f"  Overlay (a coller dans OBS) : {settings.url}")
    print(f"  API JSON                    : {settings.url}/api/current-track")
    print(f"  Filtre media                : mode {runtime.config.media_filter.mode}")
    print(f"  Skin actif                  : {runtime.skins.active_id}")
    print("")
    print("  Ctrl+C pour arreter.")
    print("=" * 68)
    print("")

    try:
        runtime.wait()
    except KeyboardInterrupt:
        print("\nArret en cours...")
    finally:
        runtime.stop()
    return 0
