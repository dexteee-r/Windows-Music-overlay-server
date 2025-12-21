"""
Launcher pour le serveur uniquement
Lance le serveur Flask sans afficher de fenêtre de commande
L'extension .pyw est utilisée pour cacher la console Windows

ATTENTION : Avec .pyw, vous ne verrez aucun message de log.
Pour déboguer, utilisez server.py au lieu de run_server.pyw
"""

import sys
from pathlib import Path

# S'assurer qu'on est dans le bon répertoire
import os
os.chdir(Path(__file__).parent)

# Importer et lancer le serveur
import server

if __name__ == "__main__":
    # Le serveur démarre automatiquement grâce au code dans server.py
    pass
