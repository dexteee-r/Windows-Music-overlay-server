"""Interface graphique de Music Overlay Server."""

from __future__ import annotations

import logging
import sys
import traceback

from .. import __app_name__, __version__
from ..diagnostics import format_report, run_checks
from ..logging_setup import setup_logging

logger = logging.getLogger(__name__)


def _show_error(title: str, message: str) -> None:
    """Affiche une erreur, y compris quand aucune console n'est visible.

    L'application se lance via ``.pyw`` : sans cette boîte de dialogue, une
    erreur de démarrage serait totalement silencieuse pour l'utilisateur.
    """
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        print(f"{title}\n\n{message}", file=sys.stderr)


def main() -> int:
    """Point d'entrée de l'application graphique."""
    log_file = setup_logging()
    logger.info("Demarrage de %s v%s", __app_name__, __version__)

    blocking = [check for check in run_checks() if not check.ok and check.critical]
    if blocking:
        report = format_report()
        logger.error("Installation incomplete :\n%s", report)
        _show_error(
            "Installation incomplete",
            "L'application ne peut pas demarrer.\n\n"
            + "\n".join(check.format() for check in blocking)
            + "\n\nRelancez scripts\\install.bat, puis reessayez.",
        )
        return 1

    try:
        import tkinter as tk

        from .window import MusicOverlayWindow

        root = tk.Tk()
        MusicOverlayWindow(root)
        root.mainloop()
    except Exception as exc:
        logger.exception("Erreur fatale")
        details = f"{exc}\n\n{traceback.format_exc(limit=3)}"
        if log_file is not None:
            details += f"\nJournal complet : {log_file}"
        _show_error("Erreur inattendue", details)
        return 1
    return 0


__all__ = ["main"]
