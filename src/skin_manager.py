"""
Gestionnaire des skins
Sépare la logique métier de l'interface graphique
"""

import json
import requests
from pathlib import Path


class SkinManager:
    """Gère le chargement, la sauvegarde et le changement de skins"""

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.skins_dir = self.base_dir / "skins"
        self.config_dir = self.base_dir / "config"
        self.active_skin_file = self.config_dir / "active_skin.json"

    def load_skins_from_api(self, server_url):
        """
        Charge la liste des skins depuis l'API Flask

        Args:
            server_url: URL du serveur (ex: http://127.0.0.1:48952)

        Returns:
            dict: {"skins": [...], "active_skin": "..."}
            None si erreur
        """
        try:
            response = requests.get(f"{server_url}/api/list-skins", timeout=2)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return None

    def load_skins_from_files(self):
        """
        Charge la liste des skins directement depuis les fichiers (fallback)

        Returns:
            dict: {"skins": [...], "active_skin": "..."}
        """
        skins = []

        if not self.skins_dir.exists():
            return {"skins": [], "active_skin": ""}

        for skin_folder in self.skins_dir.iterdir():
            if skin_folder.is_dir() and (skin_folder / "skin.html").exists():
                info_file = skin_folder / "info.json"
                skin_id = skin_folder.name

                skin_info = {
                    "id": skin_id,
                    "name": skin_id.replace('_', ' ').title(),
                    "description": "Skin personnalisé",
                    "author": "Unknown",
                    "version": "1.0"
                }

                if info_file.exists():
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            info = json.load(f)
                        skin_info.update({
                            "name": info.get('name', skin_info["name"]),
                            "description": info.get('description', skin_info["description"]),
                            "author": info.get('author', skin_info["author"]),
                            "version": info.get('version', skin_info["version"])
                        })
                    except:
                        pass

                skins.append(skin_info)

        # Charger le skin actif
        active_skin = self.get_active_skin_id()

        return {
            "skins": skins,
            "active_skin": active_skin,
            "count": len(skins)
        }

    def get_active_skin_id(self):
        """
        Lit le skin actif depuis le fichier de configuration

        Returns:
            str: ID du skin actif
        """
        try:
            if self.active_skin_file.exists():
                with open(self.active_skin_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('active_skin', 'zen_minimalist')
        except:
            pass
        return 'zen_minimalist'

    def set_active_skin_file(self, skin_id):
        """
        Sauvegarde le skin actif dans le fichier de configuration

        Args:
            skin_id: ID du skin à activer

        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Vérifier que le skin existe
            skin_path = self.skins_dir / skin_id / "skin.html"
            if not skin_path.exists():
                return False

            config = {
                "_commentaire": "Définit le skin actif affiché par l'overlay",
                "active_skin": skin_id
            }

            self.config_dir.mkdir(exist_ok=True)

            with open(self.active_skin_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True
        except:
            return False

    def set_active_skin_api(self, server_url, skin_id):
        """
        Change le skin actif via l'API Flask

        Args:
            server_url: URL du serveur
            skin_id: ID du skin à activer

        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            response = requests.get(f"{server_url}/api/set-skin/{skin_id}", timeout=2)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": "Erreur serveur"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Erreur de connexion: {e}"}
