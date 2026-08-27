"""Point d'entrée de l'application (interface graphique).

L'extension ``.pyw`` évite l'ouverture d'une console Windows. Ce nom de fichier
est aussi la cible du raccourci de démarrage automatique : le conserver garde
les raccourcis existants fonctionnels.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from music_overlay.gui import main

if __name__ == "__main__":
    raise SystemExit(main())
