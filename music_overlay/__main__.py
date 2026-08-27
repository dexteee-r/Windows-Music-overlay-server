"""Exécution du paquet : ``python -m music_overlay [--console|--diagnostic]``."""

from __future__ import annotations

import argparse
import sys

from . import __app_name__, __version__


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
        from .application import run_console

        return run_console()

    from .gui import main as gui_main

    return gui_main()


if __name__ == "__main__":
    sys.exit(main())
