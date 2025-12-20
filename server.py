"""
Music Overlay Server pour Apple Music
Affiche en temps réel ce que vous écoutez sur Apple Music
Compatible avec OBS et autres logiciels de streaming
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import json
import os
from pathlib import Path
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import threading
from typing import Optional, Dict
import sys
import base64
import time

# Configurer l'encodage UTF-8 pour la console Windows
if sys.platform == "win32":
    try:
        import locale
        import codecs
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout.detach())
        sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr.detach())
    except:
        pass

# API Windows pour récupérer les informations média
try:
    from winrt.windows.media.control import \
        GlobalSystemMediaTransportControlsSessionManager as MediaManager
    from winrt.windows.storage.streams import \
        DataReader, Buffer, InputStreamOptions
except ImportError:
    print("❌ Erreur : Les packages winrt ne sont pas installés")
    print("   Lancez install.bat pour installer les dépendances")
    input("\nAppuyez sur Entrée pour quitter...")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

def create_default_config():
    """Crée les fichiers de configuration par défaut si nécessaire"""
    config_dir = Path("config")

    # Créer le dossier config s'il n'existe pas
    if not config_dir.exists():
        config_dir.mkdir()
        print("[OK] Dossier config/ cree automatiquement")

    # Créer settings.json si absent
    settings_file = config_dir / "settings.json"
    if not settings_file.exists():
        default_settings = {
            "_commentaire": "Configuration du serveur - Modifiez ces valeurs selon vos besoins",
            "port": 48952,
            "host": "127.0.0.1",
            "refresh_interval": 0.5
        }
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=2, ensure_ascii=False)
        print("[OK] settings.json cree avec les valeurs par defaut")

    # Créer media_filter.json si absent
    filter_file = config_dir / "media_filter.json"
    if not filter_file.exists():
        default_filter = {
            "_commentaire": "Filtre des applications média - Contrôlez quelles apps peuvent afficher leurs infos",
            "_modes": {
                "all": "Accepter toutes les applications",
                "whitelist": "Accepter uniquement les apps dans allowed_apps",
                "blacklist": "Accepter toutes sauf celles dans blocked_apps"
            },
            "mode": "whitelist",
            "allowed_apps": [
                "AppleInc.AppleMusicWin_nzyj5cx40ttqa!App"
            ],
            "blocked_apps": []
        }
        with open(filter_file, 'w', encoding='utf-8') as f:
            json.dump(default_filter, f, indent=2, ensure_ascii=False)
        print("[OK] media_filter.json cree en mode whitelist (Apple Music uniquement)")


def load_config():
    """Charge la configuration depuis config/settings.json"""
    create_default_config()

    config_file = Path("config") / "settings.json"
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"[OK] Configuration chargee depuis {config_file}")
        return config
    except Exception as e:
        print(f"[WARN] Erreur lors du chargement de la config : {e}")
        print("       Utilisation des valeurs par defaut")
        return {
            "port": 48952,
            "host": "127.0.0.1",
            "refresh_interval": 0.5
        }


def load_filter_config():
    """Charge la configuration du filtre média"""
    filter_file = Path("config") / "media_filter.json"
    try:
        with open(filter_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Convertir en minuscules pour comparaison
        mode = config.get("mode", "all").lower()
        allowed = [app.lower() for app in config.get("allowed_apps", [])]
        blocked = [app.lower() for app in config.get("blocked_apps", [])]

        print(f"[OK] Filtre charge : mode={mode}")
        if mode == "whitelist" and allowed:
            print(f"     Applications autorisees : {len(allowed)}")
        if blocked:
            print(f"     Applications bloquees : {len(blocked)}")

        return {
            "mode": mode,
            "allowed_apps": allowed,
            "blocked_apps": blocked
        }
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement du filtre : {e}")
        return {
            "mode": "all",
            "allowed_apps": [],
            "blocked_apps": []
        }


# Charger la configuration
CONFIG = load_config()
FILTER_CONFIG = load_filter_config()

SERVER_HOST = CONFIG.get("host", "127.0.0.1")
SERVER_PORT = CONFIG.get("port", 48952)
REFRESH_INTERVAL = CONFIG.get("refresh_interval", 0.5)

# ============================================================================
# FLASK APP
# ============================================================================
app = Flask(__name__)
CORS(app)

# Variable globale pour stocker les informations de la piste
current_track_info = {
    "title": "No track playing",
    "artist": "Unknown",
    "album": "",
    "thumbnail": "",
    "is_playing": False,
    "position": 0,
    "duration": 0,
    "source_app": ""
}

# ============================================================================
# FILTRE MÉDIA
# ============================================================================

def is_app_allowed(app_id: str) -> bool:
    """
    Vérifie si une application est autorisée selon les règles du filtre

    Args:
        app_id: ID de l'application (ex: "AppleInc.AppleMusicWin_...")

    Returns:
        True si l'application est autorisée, False sinon
    """
    if not app_id:
        return False

    app_id_lower = app_id.lower()
    mode = FILTER_CONFIG["mode"]

    # Mode "all" : tout accepter sauf les apps bloquées
    if mode == "all":
        if app_id_lower in FILTER_CONFIG["blocked_apps"]:
            return False
        return True

    # Mode "whitelist" : accepter uniquement les apps autorisées
    elif mode == "whitelist":
        return app_id_lower in FILTER_CONFIG["allowed_apps"]

    # Mode "blacklist" : accepter tout sauf les apps bloquées
    elif mode == "blacklist":
        return app_id_lower not in FILTER_CONFIG["blocked_apps"]

    # Par défaut : tout accepter
    return True

# ============================================================================
# RÉCUPÉRATION DES DONNÉES MÉDIA
# ============================================================================

async def get_media_info() -> Optional[Dict]:
    """Récupère les informations de la piste en cours depuis Windows Media API"""
    try:
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()

        if current_session:
            info = await current_session.try_get_media_properties_async()

            # Récupérer l'ID de l'application source
            source_app_id = current_session.source_app_user_model_id

            # Vérifier si l'application est autorisée
            if not is_app_allowed(source_app_id):
                print(f"[BLOCK] Application bloquee : {source_app_id}")
                return None

            # Récupérer les infos de lecture
            playback_info = current_session.get_playback_info()
            timeline_props = current_session.get_timeline_properties()

            # Récupérer la pochette d'album
            thumbnail_base64 = ""
            if info.thumbnail:
                try:
                    thumb_stream_ref = info.thumbnail
                    thumb_read_buffer = await thumb_stream_ref.open_read_async()

                    buffer = Buffer(thumb_read_buffer.size)
                    await thumb_read_buffer.read_async(
                        buffer,
                        buffer.capacity,
                        InputStreamOptions.READ_AHEAD
                    )

                    reader = DataReader.from_buffer(buffer)
                    byte_array = bytearray(buffer.length)
                    reader.read_bytes(byte_array)

                    thumbnail_base64 = "data:image/jpeg;base64," + base64.b64encode(byte_array).decode('utf-8')
                except Exception as e:
                    # Pas grave si la pochette n'est pas disponible
                    pass

            # Convertir les temps (timedelta) en secondes
            position_seconds = int(timeline_props.position.total_seconds()) if timeline_props.position else 0
            duration_seconds = int(timeline_props.end_time.total_seconds()) if timeline_props.end_time else 0

            return {
                "title": info.title or "Unknown Title",
                "artist": info.artist or "Unknown Artist",
                "album": info.album_title or "",
                "thumbnail": thumbnail_base64,
                "is_playing": playback_info.playback_status == 4,  # 4 = Playing
                "position": position_seconds,
                "duration": duration_seconds,
                "source_app": source_app_id
            }

    except Exception as e:
        # Pas de musique en cours ou erreur
        return None

    return None


def update_track_info():
    """Thread de mise à jour continue des informations de piste"""
    global current_track_info
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            info = loop.run_until_complete(get_media_info())
            if info:
                current_track_info = info
            else:
                # Aucune info ou app bloquée
                current_track_info = {
                    "title": "No track playing",
                    "artist": "Unknown",
                    "album": "",
                    "thumbnail": "",
                    "is_playing": False,
                    "position": 0,
                    "duration": 0,
                    "source_app": ""
                }
        except Exception as e:
            # En cas d'erreur, ne rien faire (garder les dernières infos)
            pass

        time.sleep(REFRESH_INTERVAL)

# ============================================================================
# TEMPLATE HTML
# ============================================================================

OVERLAY_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Music Overlay</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: transparent;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
        }

        .music-widget {
            display: flex;
            align-items: center;
            background: linear-gradient(135deg, rgba(20, 20, 30, 0.95), rgba(30, 30, 50, 0.95));
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 600px;
            margin: 20px;
            animation: slideIn 0.5s ease-out;
        }

        @keyframes slideIn {
            from {
                transform: translateX(-100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        .album-art {
            width: 100px;
            height: 100px;
            border-radius: 15px;
            object-fit: cover;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
            margin-right: 20px;
            animation: rotate 20s linear infinite;
            animation-play-state: paused;
        }

        .album-art.playing {
            animation-play-state: running;
        }

        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .track-info {
            flex: 1;
            color: white;
            min-width: 0;
        }

        .track-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        .track-artist {
            font-size: 18px;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 12px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .progress-container {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 10px;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px;
            transition: width 0.3s ease;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        }

        .time-info {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
        }

        .equalizer {
            display: flex;
            align-items: flex-end;
            height: 30px;
            gap: 3px;
            margin-left: 15px;
        }

        .equalizer-bar {
            width: 4px;
            background: linear-gradient(to top, #667eea, #764ba2);
            border-radius: 2px;
            animation: equalize 1s ease-in-out infinite;
        }

        .equalizer-bar:nth-child(1) { animation-delay: 0s; }
        .equalizer-bar:nth-child(2) { animation-delay: 0.1s; }
        .equalizer-bar:nth-child(3) { animation-delay: 0.2s; }
        .equalizer-bar:nth-child(4) { animation-delay: 0.3s; }
        .equalizer-bar:nth-child(5) { animation-delay: 0.4s; }

        @keyframes equalize {
            0%, 100% { height: 10px; }
            50% { height: 30px; }
        }

        .equalizer.paused .equalizer-bar {
            animation: none;
            height: 10px;
        }
    </style>
</head>
<body>
    <div class="music-widget" id="musicWidget">
        <img id="albumArt" class="album-art" src="" alt="Album Art">
        <div class="track-info">
            <div class="track-title" id="trackTitle">No track playing</div>
            <div class="track-artist" id="trackArtist">Unknown Artist</div>
            <div class="progress-container">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div class="time-info">
                <span id="currentTime">0:00</span>
                <span id="totalTime">0:00</span>
            </div>
        </div>
        <div class="equalizer" id="equalizer">
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
            <div class="equalizer-bar"></div>
        </div>
    </div>

    <script>
        const defaultAlbumArt = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzMzMzM0NCIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjQwIiBmaWxsPSIjNjY2Njc3IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+4pmqPC90ZXh0Pjwvc3ZnPg==';

        function formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }

        async function updateTrackInfo() {
            try {
                const response = await fetch('/api/current-track');
                const data = await response.json();

                document.getElementById('trackTitle').textContent = data.title;
                document.getElementById('trackArtist').textContent = data.artist;

                const albumArt = document.getElementById('albumArt');
                albumArt.src = data.thumbnail || defaultAlbumArt;

                if (data.is_playing) {
                    albumArt.classList.add('playing');
                    document.getElementById('equalizer').classList.remove('paused');
                } else {
                    albumArt.classList.remove('playing');
                    document.getElementById('equalizer').classList.add('paused');
                }

                const progress = data.duration > 0 ? (data.position / data.duration) * 100 : 0;
                document.getElementById('progressBar').style.width = `${progress}%`;

                document.getElementById('currentTime').textContent = formatTime(data.position);
                document.getElementById('totalTime').textContent = formatTime(data.duration);

            } catch (error) {
                console.error('Erreur lors de la récupération des infos:', error);
            }
        }

        // Mise à jour toutes les 500ms
        setInterval(updateTrackInfo, 500);
        updateTrackInfo();
    </script>
</body>
</html>
"""

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil avec l'overlay"""
    return render_template_string(OVERLAY_HTML)


@app.route('/api/current-track')
def get_current_track():
    """API: Informations de la piste en cours"""
    return jsonify(current_track_info)


@app.route('/api/reload-config', methods=['POST', 'GET'])
def reload_config():
    """API: Recharger la configuration"""
    global FILTER_CONFIG
    FILTER_CONFIG = load_filter_config()
    return jsonify({
        "success": True,
        "message": "Configuration rechargée avec succès"
    })

# ============================================================================
# DÉMARRAGE DU SERVEUR
# ============================================================================

if __name__ == '__main__':
    # Démarrer le thread de mise à jour
    update_thread = threading.Thread(target=update_track_info, daemon=True)
    update_thread.start()

    # Affichage de bienvenue
    print("\n" + "="*70)
    print("    MUSIC OVERLAY SERVER - APPLE MUSIC")
    print("="*70)
    print(f"\n[URL] Overlay : http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"[API] JSON    : http://{SERVER_HOST}:{SERVER_PORT}/api/current-track")
    print(f"\n[INFO] Serveur local uniquement ({SERVER_HOST}:{SERVER_PORT})")
    print(f"[INFO] Mode de filtrage : {FILTER_CONFIG['mode']}")
    print("\n[OBS] Pour utiliser dans OBS :")
    print(f"      1. Ajoutez une source 'Navigateur'")
    print(f"      2. URL : http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"      3. Dimensions : 600 x 150")
    print("\n[CONFIG] config/settings.json et config/media_filter.json")
    print("="*70 + "\n")

    # Lancer le serveur Flask
    try:
        app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, threaded=True)
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"\n[ERROR] Le port {SERVER_PORT} est deja utilise")
            print(f"        Solution : Modifiez le port dans config/settings.json")
            print(f"        Suggestions : 49152, 49500, 50000")
        else:
            print(f"\n[ERROR] {e}")
        input("\nAppuyez sur Entree pour quitter...")
    except KeyboardInterrupt:
        print("\n\n[INFO] Arret du serveur...")
