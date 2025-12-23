"""
Gestionnaire du serveur Flask
Sépare la logique métier de l'interface graphique
"""

import threading
import requests
from pathlib import Path


class ServerManager:
    """Gère le démarrage, l'arrêt et l'état du serveur Flask"""

    def __init__(self, host="127.0.0.1", port=48952):
        self.host = host
        self.port = port
        self.running = False
        self.thread = None

    def start(self, on_success=None, on_error=None):
        """
        Démarre le serveur Flask dans un thread séparé

        Args:
            on_success: Callback appelé si le serveur démarre (sans argument)
            on_error: Callback appelé en cas d'erreur (prend l'exception en argument)
        """
        if self.running:
            if on_error:
                on_error(Exception("Le serveur est déjà en cours d'exécution"))
            return

        def _run_server():
            try:
                import sys
                import os

                # Ajouter le dossier parent au path pour trouver server.py
                parent_dir = str(Path(__file__).parent.parent)
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)

                # IMPORTANT: Changer le répertoire de travail vers le dossier parent
                # pour que server.py trouve les dossiers skins/, config/, etc.
                os.chdir(parent_dir)

                import server

                # Démarrer le thread de mise à jour média AVANT Flask
                if not hasattr(server, '_update_thread_started'):
                    update_thread = threading.Thread(target=server.update_track_info, daemon=True)
                    update_thread.start()
                    # Marquer le thread comme démarré (attribut dynamique)
                    server._update_thread_started = True  # type: ignore[attr-defined]

                server.app.run(host=self.host, port=self.port,
                              debug=False, threaded=True, use_reloader=False)
            except Exception as e:
                if on_error:
                    on_error(e)

        self.thread = threading.Thread(target=_run_server, daemon=True)
        self.thread.start()

        # Vérifier que le serveur répond (après 1.5s)
        def _check_status():
            if self.is_responsive():
                self.running = True
                if on_success:
                    on_success()
            else:
                if on_error:
                    on_error(Exception("Le serveur ne répond pas"))

        # On ne peut pas utiliser root.after ici, donc on retourne le callback
        return _check_status

    def stop(self):
        """
        Arrête le serveur (note: Flask ne peut pas s'arrêter proprement depuis un thread)
        """
        self.running = False

    def is_responsive(self):
        """Vérifie si le serveur répond aux requêtes"""
        try:
            response = requests.get(f"http://{self.host}:{self.port}/api/current-track",
                                   timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_url(self):
        """Retourne l'URL du serveur"""
        return f"http://{self.host}:{self.port}"
