"""
Launcher pour l'interface graphique
Lance la GUI sans afficher de fenêtre de commande
L'extension .pyw est utilisée pour cacher la console Windows
"""

import sys
from pathlib import Path

# Ajouter le dossier src au path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Importer et lancer la GUI
from gui import main

if __name__ == "__main__":
    main()
