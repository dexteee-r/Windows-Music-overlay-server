"""Point d'entrée de l'exécutable compilé (PyInstaller).

Un fichier ``.py`` distinct est nécessaire : PyInstaller n'accepte pas le
``.pyw`` comme script d'entrée.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from music_overlay.gui import main

if __name__ == "__main__":
    sys.exit(main())
