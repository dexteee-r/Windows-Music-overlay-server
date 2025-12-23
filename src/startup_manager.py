"""
Gestionnaire de démarrage automatique Windows
Gère l'ajout/suppression d'un raccourci dans le dossier Startup
"""

import os
from pathlib import Path
from win32com.client import Dispatch


class StartupManager:
    """Gère le démarrage automatique de l'application sur Windows"""

    def __init__(self):
        # Dossier de démarrage Windows
        self.startup_folder = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
        self.shortcut_name = "Music Overlay Server.lnk"
        self.shortcut_path = self.startup_folder / self.shortcut_name

        # Chemin vers le launcher.pyw
        self.base_dir = Path(__file__).parent.parent
        self.launcher_path = self.base_dir / "launcher.pyw"

    def is_enabled(self):
        """
        Vérifie si le démarrage automatique est activé

        Returns:
            bool: True si activé, False sinon
        """
        return self.shortcut_path.exists()

    def enable(self):
        """
        Active le démarrage automatique en créant un raccourci

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.launcher_path.exists():
                return False, f"Le fichier launcher.pyw est introuvable : {self.launcher_path}"

            # Créer le raccourci avec COM (Windows Script Host)
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(self.shortcut_path))
            shortcut.TargetPath = str(self.launcher_path)
            shortcut.WorkingDirectory = str(self.base_dir)
            shortcut.Description = "Music Overlay Server - Affiche la musique en cours"
            shortcut.IconLocation = str(self.launcher_path)
            shortcut.save()

            return True, "Démarrage automatique activé avec succès"

        except Exception as e:
            return False, f"Erreur lors de l'activation : {e}"

    def disable(self):
        """
        Désactive le démarrage automatique en supprimant le raccourci

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if self.shortcut_path.exists():
                self.shortcut_path.unlink()
                return True, "Démarrage automatique désactivé avec succès"
            else:
                return True, "Démarrage automatique déjà désactivé"

        except Exception as e:
            return False, f"Erreur lors de la désactivation : {e}"

    def toggle(self, enable):
        """
        Active ou désactive le démarrage automatique

        Args:
            enable (bool): True pour activer, False pour désactiver

        Returns:
            tuple: (success: bool, message: str)
        """
        if enable:
            return self.enable()
        else:
            return self.disable()
