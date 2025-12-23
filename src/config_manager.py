"""
Gestionnaire de configuration
Sépare la logique métier de l'interface graphique
"""

import json
from pathlib import Path


class ConfigManager:
    """Gère le chargement et la sauvegarde des configurations"""

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.config_dir = self.base_dir / "config"
        self.settings_file = self.config_dir / "settings.json"
        self.filter_file = self.config_dir / "media_filter.json"

    def load_settings(self):
        """
        Charge les paramètres depuis settings.json

        Returns:
            dict: {"port": int, "host": str, "refresh_interval": float}
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {
                    "port": config.get("port", 48952),
                    "host": config.get("host", "127.0.0.1"),
                    "refresh_interval": config.get("refresh_interval", 0.5)
                }
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement de settings.json : {e}")

        # Valeurs par défaut
        return {
            "port": 48952,
            "host": "127.0.0.1",
            "refresh_interval": 0.5
        }

    def save_settings(self, port, host, refresh_interval):
        """
        Sauvegarde les paramètres dans settings.json

        Args:
            port: Port du serveur (int)
            host: Adresse IP du serveur (str)
            refresh_interval: Intervalle de rafraîchissement en secondes (float)

        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Validation des entrées
            port = int(port)
            if port < 1024 or port > 65535:
                raise ValueError("Le port doit être entre 1024 et 65535")

            refresh_interval = float(refresh_interval)
            if refresh_interval < 0.1 or refresh_interval > 10:
                raise ValueError("L'intervalle doit être entre 0.1 et 10 secondes")

            config = {
                "_commentaire": "Configuration du serveur - Modifiez ces valeurs selon vos besoins",
                "port": port,
                "host": host,
                "refresh_interval": refresh_interval
            }

            # Créer le dossier config s'il n'existe pas
            self.config_dir.mkdir(exist_ok=True)

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True

        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Erreur lors de la sauvegarde : {e}")

    def load_filter_config(self):
        """
        Charge la configuration du filtre média

        Returns:
            dict: {"mode": str, "allowed_apps": [str], "blocked_apps": [str]}
        """
        try:
            if self.filter_file.exists():
                with open(self.filter_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {
                    "mode": config.get("mode", "whitelist"),
                    "allowed_apps": config.get("allowed_apps", []),
                    "blocked_apps": config.get("blocked_apps", [])
                }
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement de media_filter.json : {e}")

        # Valeurs par défaut
        return {
            "mode": "whitelist",
            "allowed_apps": ["AppleInc.AppleMusicWin_nzyj5cx40ttqa!App"],
            "blocked_apps": []
        }

    def save_filter_config(self, mode, allowed_apps, blocked_apps):
        """
        Sauvegarde la configuration du filtre média

        Args:
            mode: Mode de filtrage ("all", "whitelist", "blacklist")
            allowed_apps: Liste des apps autorisées (whitelist)
            blocked_apps: Liste des apps bloquées (blacklist)

        Returns:
            bool: True si succès, False sinon
        """
        try:
            if mode not in ["all", "whitelist", "blacklist"]:
                raise ValueError("Mode invalide")

            config = {
                "_commentaire": "Filtre des applications média - Contrôlez quelles apps peuvent afficher leurs infos",
                "_modes": {
                    "all": "Accepter toutes les applications",
                    "whitelist": "Accepter uniquement les apps dans allowed_apps",
                    "blacklist": "Accepter toutes sauf celles dans blocked_apps"
                },
                "mode": mode,
                "allowed_apps": allowed_apps if isinstance(allowed_apps, list) else [],
                "blocked_apps": blocked_apps if isinstance(blocked_apps, list) else []
            }

            # Créer le dossier config s'il n'existe pas
            self.config_dir.mkdir(exist_ok=True)

            with open(self.filter_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True

        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Erreur lors de la sauvegarde : {e}")
