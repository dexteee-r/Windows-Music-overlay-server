"""Point d'entrée en ligne de commande : ``python -m music_overlay``.

Sans option, lance l'interface graphique. ``--console`` lance le serveur seul,
``--diagnostic`` vérifie l'installation.
"""

from __future__ import annotations

import argparse
import logging
import sys

from . import __app_name__, __version__

logger = logging.getLogger(__name__)


def run_console() -> int:
    """Lance le serveur sans interface graphique, jusqu'à ``Ctrl+C``."""
    from .diagnostics import format_report, run_checks
    from .logging_setup import setup_logging
    from .server import ServerRuntime

    setup_logging()
    logger.info("%s v%s", __app_name__, __version__)

    if any(check for check in run_checks() if not check.ok and check.critical):
        print(format_report())
        return 1

    runtime = ServerRuntime.create()
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="music_overlay", description=f"{__app_name__} v{__version__}"
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="lancer le serveur sans interface graphique",
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="verifier l'installation et afficher un rapport",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    if args.diagnostic:
        from .diagnostics import main as diagnostic_main

        return diagnostic_main()

    if args.console:
        return run_console()

    from .gui import main as gui_main

    return gui_main()


if __name__ == "__main__":
    sys.exit(main())
