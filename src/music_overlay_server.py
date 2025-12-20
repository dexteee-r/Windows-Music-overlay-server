"""
Music Overlay Server for Windows
Displays currently playing music from Windows Media API with application filtering
"""

import asyncio
import json
import os
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import threading
from typing import Optional, Dict
import sys
import base64
import time
from pathlib import Path

# Import media filter module
from media_filter import MediaFilter

# For Windows Media Control using winrt (precompiled wheels)
try:
    from winrt.windows.media.control import \
        GlobalSystemMediaTransportControlsSessionManager as MediaManager
    from winrt.windows.storage.streams import \
        DataReader, Buffer, InputStreamOptions
except ImportError:
    print("Error: winrt packages not installed.")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)

# Load configuration
def load_config():
    """Load server configuration from settings.json"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"

    default_config = {
        "server": {
            "host": "127.0.0.1",
            "port": 48952
        },
        "update_interval": 0.5
    }

    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"✅ Configuration loaded from {config_path}")
                return config
        else:
            print(f"⚠️ Config file not found, using defaults")
            return default_config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return default_config

# Load configuration
CONFIG = load_config()
SERVER_HOST = CONFIG.get("server", {}).get("host", "127.0.0.1")
SERVER_PORT = CONFIG.get("server", {}).get("port", 48952)
UPDATE_INTERVAL = CONFIG.get("update_interval", 0.5)

app = Flask(__name__)
CORS(app)

# Initialize media filter
media_filter = MediaFilter()

# Global variable to store current track info
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

async def get_media_info() -> Optional[Dict]:
    """Get current playing media info from Windows Media API"""
    try:
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()

        if current_session:
            info = await current_session.try_get_media_properties_async()

            # Get source app ID
            source_app_id = current_session.source_app_user_model_id

            # Get playback info
            playback_info = current_session.get_playback_info()
            timeline_props = current_session.get_timeline_properties()

            # Get thumbnail
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
                    print(f"Error getting thumbnail: {e}")

            # In winrt 3.x, position and end_time are timedelta objects
            position_seconds = int(timeline_props.position.total_seconds()) if timeline_props.position else 0
            duration_seconds = int(timeline_props.end_time.total_seconds()) if timeline_props.end_time else 0

            media_data = {
                "title": info.title or "Unknown Title",
                "artist": info.artist or "Unknown Artist",
                "album": info.album_title or "",
                "thumbnail": thumbnail_base64,
                "is_playing": playback_info.playback_status == 4,  # 4 = Playing
                "position": position_seconds,
                "duration": duration_seconds
            }

            # Apply media filter
            return media_filter.filter_media_info(media_data, source_app_id)

    except Exception as e:
        print(f"Error getting media info: {e}")

    return None

def update_track_info():
    """Background thread to continuously update track info"""
    global current_track_info
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            info = loop.run_until_complete(get_media_info())
            if info:
                current_track_info = info
        except Exception as e:
            print(f"Error in update loop: {e}")

        time.sleep(UPDATE_INTERVAL)

# HTML Template for the overlay
OVERLAY_HTML = """
<!DOCTYPE html>
<html lang="en">
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

        .no-music {
            display: none;
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.6);
            font-size: 18px;
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
                console.error('Error fetching track info:', error);
            }
        }

        // Update every 500ms
        setInterval(updateTrackInfo, 500);
        updateTrackInfo();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the overlay HTML"""
    return render_template_string(OVERLAY_HTML)

@app.route('/api/current-track')
def get_current_track():
    """API endpoint to get current track info"""
    return jsonify(current_track_info)

@app.route('/api/filter-config')
def get_filter_config():
    """API endpoint to get current filter configuration"""
    return jsonify(media_filter.get_config_info())

@app.route('/api/reload-config', methods=['POST'])
def reload_config():
    """API endpoint to reload filter configuration"""
    success = media_filter.reload_config()
    return jsonify({
        "success": success,
        "message": "Configuration reloaded" if success else "Failed to reload configuration"
    })

if __name__ == '__main__':
    # Start background thread to update track info
    update_thread = threading.Thread(target=update_track_info, daemon=True)
    update_thread.start()

    print("\n" + "="*70)
    print("🎵 Music Overlay Server Started!")
    print("="*70)
    print(f"\n📺 Overlay URL: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"📊 API URL: http://{SERVER_HOST}:{SERVER_PORT}/api/current-track")
    print(f"⚙️  Filter Config: http://{SERVER_HOST}:{SERVER_PORT}/api/filter-config")
    print(f"\n🔒 Server: {SERVER_HOST}:{SERVER_PORT} (LOCAL only)")
    print(f"🎯 Filter Mode: {media_filter.mode}")
    print("ℹ️  Open the overlay URL in OBS Browser Source")
    print("="*70 + "\n")

    # Run Flask server
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, threaded=True)
