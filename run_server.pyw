"""Lance le serveur seul, sans console ni interface graphique.

Aucun message n'est visible : consultez ``logs/music-overlay.log`` en cas de
problème, ou utilisez ``python server.py`` pour voir les messages en direct.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from music_overlay.application import build_runtime
from music_overlay.logging_setup import setup_logging


def main() -> int:
    setup_logging(console=False)
    runtime = build_runtime()
    try:
        runtime.start()
        runtime.wait()
    except (OSError, KeyboardInterrupt):
        return 1
    finally:
        runtime.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
