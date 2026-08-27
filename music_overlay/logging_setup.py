"""Configuration centralisée des logs.

Remplace les ``print()`` disséminés dans le code : un seul point de réglage,
un fichier de log rotatif exploitable pour le support, et la possibilité de
brancher la zone de logs de la GUI via ``CallbackHandler``.
"""

from __future__ import annotations

import contextlib
import logging
import sys
from collections.abc import Callable
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import paths

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%H:%M:%S"
MAX_BYTES = 512 * 1024
BACKUP_COUNT = 2

_configured = False


def _force_utf8_console() -> None:
    """Évite les ``UnicodeEncodeError`` sur les consoles Windows en cp1252."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            with contextlib.suppress(ValueError, OSError):
                reconfigure(encoding="utf-8", errors="replace")


def setup_logging(
    level: int = logging.INFO,
    *,
    console: bool = True,
    log_file: Path | None = None,
) -> Path | None:
    """Configure les logs de l'application (idempotent).

    Args:
        level: niveau minimum des messages.
        console: ajouter un handler vers la sortie standard.
        log_file: chemin du fichier de log ; ``None`` utilise ``logs/``.

    Returns:
        Le chemin du fichier de log, ou ``None`` s'il n'a pas pu être créé.
    """
    global _configured

    root = logging.getLogger()
    if _configured:
        return getattr(root, "_music_overlay_log_file", None)

    root.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    if console:
        _force_utf8_console()
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)

    target = log_file
    if target is None:
        try:
            paths.logs_dir().mkdir(parents=True, exist_ok=True)
            target = paths.logs_dir() / "music-overlay.log"
        except OSError:
            target = None

    if target is not None:
        try:
            file_handler = RotatingFileHandler(
                target, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
        except OSError:
            target = None

    # Werkzeug loggue chaque requête HTTP : bruit inutile pour un overlay
    # interrogé deux fois par seconde.
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    root._music_overlay_log_file = target  # type: ignore[attr-defined]
    _configured = True
    return target


class CallbackHandler(logging.Handler):
    """Handler qui transmet chaque message formaté à une fonction.

    Utilisé par la GUI pour afficher les logs applicatifs dans son onglet
    Contrôle sans que le reste du code ait à connaître l'interface.
    """

    def __init__(self, callback: Callable[[str], None], level: int = logging.INFO):
        super().__init__(level=level)
        self._callback = callback
        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", DATE_FORMAT))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._callback(self.format(record))
        except Exception:
            self.handleError(record)
