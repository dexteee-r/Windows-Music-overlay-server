"""Lance le serveur d'overlay en mode console (sans interface graphique).

Utile pour le streaming « sans fenêtre » et pour déboguer : les messages
s'affichent dans le terminal et dans ``logs/music-overlay.log``.

    python server.py

Toute la logique vit dans le paquet ``music_overlay`` ; ce fichier n'est qu'un
point d'entrée conservé pour compatibilité avec ``scripts/start.bat``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from music_overlay.application import run_console

if __name__ == "__main__":
    raise SystemExit(run_console())
