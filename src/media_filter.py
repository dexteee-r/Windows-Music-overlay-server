"""
Media Filter Module
Manages whitelist/blacklist filtering for media applications
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path


class MediaFilter:
    """Handles filtering of media applications based on configuration"""

    def __init__(self, config_path: str = None):
        """
        Initialize the MediaFilter

        Args:
            config_path: Path to the media_filter.json config file
        """
        if config_path is None:
            # Default to config/media_filter.json relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "media_filter.json"

        self.config_path = config_path
        self.mode = "allow_all"
        self.allowed_apps = []
        self.blocked_apps = []
        self.default_message = {
            "title": "No track playing",
            "artist": "Unknown",
            "album": ""
        }

        self.load_config()

    def load_config(self) -> bool:
        """
        Load configuration from JSON file

        Returns:
            bool: True if config loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.config_path):
                print(f"⚠️ Warning: Config file not found at {self.config_path}")
                print("   Using default 'allow_all' mode")
                return False

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.mode = config.get("mode", "allow_all").lower()
            self.allowed_apps = [app.lower() for app in config.get("allowed_apps", [])]
            self.blocked_apps = [app.lower() for app in config.get("blocked_apps", [])]
            self.default_message = config.get("default_message", self.default_message)

            print(f"✅ Media filter loaded: mode={self.mode}")
            if self.mode == "whitelist" and self.allowed_apps:
                print(f"   Allowed apps: {', '.join(self.allowed_apps)}")
            if self.blocked_apps:
                print(f"   Blocked apps: {', '.join(self.blocked_apps)}")

            return True

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False

    def is_app_allowed(self, app_name: str) -> bool:
        """
        Check if an application is allowed based on filter rules

        Args:
            app_name: Name of the application (e.g., "Music.UI.exe")

        Returns:
            bool: True if app is allowed, False otherwise
        """
        if not app_name:
            return False

        app_name_lower = app_name.lower()

        # Mode: allow_all - allow everything except explicitly blocked
        if self.mode == "allow_all":
            return app_name_lower not in self.blocked_apps

        # Mode: whitelist - only allow explicitly listed apps
        elif self.mode == "whitelist":
            return app_name_lower in self.allowed_apps

        # Mode: blacklist - block only explicitly listed apps
        elif self.mode == "blacklist":
            return app_name_lower not in self.blocked_apps

        # Default: allow all
        return True

    def filter_media_info(self, media_info: Optional[Dict], app_name: str = "") -> Dict:
        """
        Filter media information based on app whitelist/blacklist

        Args:
            media_info: Dictionary containing media information
            app_name: Name of the source application

        Returns:
            Dict: Filtered media info or default message if blocked
        """
        # If no media info, return default
        if not media_info:
            return {
                "title": self.default_message["title"],
                "artist": self.default_message["artist"],
                "album": self.default_message.get("album", ""),
                "thumbnail": "",
                "is_playing": False,
                "position": 0,
                "duration": 0,
                "source_app": ""
            }

        # Check if app is allowed
        if not self.is_app_allowed(app_name):
            print(f"🚫 Blocked app: {app_name}")
            return {
                "title": self.default_message["title"],
                "artist": self.default_message["artist"],
                "album": self.default_message.get("album", ""),
                "thumbnail": "",
                "is_playing": False,
                "position": 0,
                "duration": 0,
                "source_app": app_name
            }

        # App is allowed, return the media info with source app
        media_info["source_app"] = app_name
        return media_info

    def reload_config(self) -> bool:
        """
        Reload configuration from file

        Returns:
            bool: True if reload successful
        """
        print("🔄 Reloading media filter configuration...")
        return self.load_config()

    def get_config_info(self) -> Dict:
        """
        Get current filter configuration

        Returns:
            Dict: Current configuration settings
        """
        return {
            "mode": self.mode,
            "allowed_apps": self.allowed_apps,
            "blocked_apps": self.blocked_apps,
            "config_path": str(self.config_path)
        }
