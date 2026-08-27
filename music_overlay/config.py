"""Chargement, validation et sauvegarde de la configuration.

Unique implémentation partagée par le serveur et la GUI (avant la v3 le code
existait en double, avec des valeurs par défaut divergentes).
"""

from __future__ import annotations

import json
import logging
import os
import threading
from collections.abc import Iterable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from . import paths

logger = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 49450
DEFAULT_REFRESH_INTERVAL = 0.5

MIN_PORT = 1024
MAX_PORT = 65535
MIN_REFRESH_INTERVAL = 0.1
MAX_REFRESH_INTERVAL = 10.0

FILTER_MODES = ("all", "whitelist", "blacklist")
DEFAULT_ALLOWED_APPS = (
    "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
    "AppleInc.AppleMusicWin_nzyj5cx40ttqa!App",
)

SETTINGS_FILE_NAME = "settings.json"
FILTER_FILE_NAME = "media_filter.json"

SETTINGS_COMMENT = (
    "Configuration du serveur - modifiable depuis l'onglet Parametres de l'application"
)
FILTER_COMMENT = "Filtre des applications media - controle quelles apps peuvent s'afficher"
FILTER_MODES_COMMENT = {
    "all": "Accepter toutes les applications sauf blocked_apps",
    "whitelist": "Accepter uniquement les apps listees dans allowed_apps",
    "blacklist": "Accepter toutes les apps sauf celles de blocked_apps",
}


class ConfigError(ValueError):
    """Configuration invalide fournie par l'utilisateur."""


def _clean_app_list(apps: Iterable[str] | None) -> tuple[str, ...]:
    """Normalise une liste d'identifiants d'application (sans doublon ni vide)."""
    if not apps:
        return ()
    cleaned: list[str] = []
    for app in apps:
        value = str(app).strip()
        if value and value not in cleaned:
            cleaned.append(value)
    return tuple(cleaned)


@dataclass(frozen=True)
class ServerSettings:
    """Paramètres réseau du serveur."""

    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    refresh_interval: float = DEFAULT_REFRESH_INTERVAL

    @classmethod
    def validated(cls, host: Any, port: Any, refresh_interval: Any) -> ServerSettings:
        """Construit des paramètres valides ou lève ``ConfigError``.

        Les messages d'erreur sont affichés tels quels à l'utilisateur : ils
        doivent rester explicites.
        """
        host_value = str(host).strip()
        if not host_value:
            raise ConfigError("L'adresse (host) ne peut pas etre vide.")

        try:
            port_value = int(str(port).strip())
        except (TypeError, ValueError):
            raise ConfigError(f"Le port doit etre un nombre entier (recu : {port!r}).") from None
        if not MIN_PORT <= port_value <= MAX_PORT:
            raise ConfigError(f"Le port doit etre compris entre {MIN_PORT} et {MAX_PORT}.")

        try:
            interval_value = float(str(refresh_interval).strip().replace(",", "."))
        except (TypeError, ValueError):
            raise ConfigError(
                f"L'intervalle doit etre un nombre (recu : {refresh_interval!r})."
            ) from None
        if not MIN_REFRESH_INTERVAL <= interval_value <= MAX_REFRESH_INTERVAL:
            raise ConfigError(
                f"L'intervalle doit etre compris entre {MIN_REFRESH_INTERVAL} "
                f"et {MAX_REFRESH_INTERVAL} secondes."
            )

        return cls(host=host_value, port=port_value, refresh_interval=interval_value)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ServerSettings:
        """Lit des paramètres depuis un JSON, en retombant sur les défauts."""
        try:
            return cls.validated(
                data.get("host", DEFAULT_HOST),
                data.get("port", DEFAULT_PORT),
                data.get("refresh_interval", DEFAULT_REFRESH_INTERVAL),
            )
        except ConfigError as exc:
            logger.warning("settings.json invalide (%s), valeurs par defaut utilisees", exc)
            return cls()

    def to_dict(self) -> dict[str, Any]:
        return {
            "_commentaire": SETTINGS_COMMENT,
            "host": self.host,
            "port": self.port,
            "refresh_interval": self.refresh_interval,
        }

    @property
    def url(self) -> str:
        """URL d'accès à l'overlay (``0.0.0.0`` n'étant pas navigable)."""
        host = "127.0.0.1" if self.host in ("0.0.0.0", "::") else self.host
        return f"http://{host}:{self.port}"


@dataclass(frozen=True)
class MediaFilter:
    """Règles décidant quelles applications média peuvent s'afficher."""

    mode: str = "whitelist"
    allowed_apps: tuple[str, ...] = DEFAULT_ALLOWED_APPS
    blocked_apps: tuple[str, ...] = ()

    @classmethod
    def validated(
        cls,
        mode: Any,
        allowed_apps: Iterable[str] | None,
        blocked_apps: Iterable[str] | None,
    ) -> MediaFilter:
        mode_value = str(mode).strip().lower()
        if mode_value not in FILTER_MODES:
            raise ConfigError(
                f"Mode de filtre invalide : {mode!r}. "
                f"Valeurs possibles : {', '.join(FILTER_MODES)}."
            )
        return cls(
            mode=mode_value,
            allowed_apps=_clean_app_list(allowed_apps),
            blocked_apps=_clean_app_list(blocked_apps),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MediaFilter:
        try:
            return cls.validated(
                data.get("mode", "whitelist"),
                data.get("allowed_apps", ()),
                data.get("blocked_apps", ()),
            )
        except ConfigError as exc:
            logger.warning("media_filter.json invalide (%s), mode 'all' utilise", exc)
            return cls(mode="all", allowed_apps=(), blocked_apps=())

    def to_dict(self) -> dict[str, Any]:
        return {
            "_commentaire": FILTER_COMMENT,
            "_modes": dict(FILTER_MODES_COMMENT),
            "mode": self.mode,
            "allowed_apps": list(self.allowed_apps),
            "blocked_apps": list(self.blocked_apps),
        }

    def allows(self, app_id: str | None) -> bool:
        """Indique si l'application ``app_id`` a le droit de s'afficher.

        La comparaison est insensible à la casse : les identifiants Windows
        (``SpotifyAB.SpotifyMusic_...``) sont souvent recopiés à la main.
        """
        if not app_id:
            return False

        app = app_id.strip().lower()
        blocked = {value.lower() for value in self.blocked_apps}

        if self.mode == "whitelist":
            allowed = {value.lower() for value in self.allowed_apps}
            return app in allowed
        return app not in blocked  # modes "all" et "blacklist"

    def with_allowed(self, app_id: str) -> MediaFilter:
        """Retourne un filtre incluant ``app_id`` dans la liste autorisée."""
        return replace(self, allowed_apps=_clean_app_list((*self.allowed_apps, app_id)))


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    """Écrit un JSON sans jamais laisser un fichier à moitié écrit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    os.replace(temporary, path)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return data
        logger.warning("%s ne contient pas un objet JSON, ignore", path.name)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning(
            "Lecture de %s impossible (%s), valeurs par defaut utilisees", path.name, exc
        )
    return None


class ConfigStore:
    """Accès thread-safe aux fichiers de configuration, avec cache mémoire.

    Le serveur et la GUI partagent la même instance : une sauvegarde depuis
    l'interface est donc visible immédiatement par le serveur, sans redémarrage.
    """

    def __init__(self, directory: Path | None = None):
        self.directory = Path(directory) if directory is not None else paths.config_dir()
        self.settings_file = self.directory / SETTINGS_FILE_NAME
        self.filter_file = self.directory / FILTER_FILE_NAME
        self._lock = threading.RLock()
        self._settings: ServerSettings | None = None
        self._filter: MediaFilter | None = None

    # ------------------------------------------------------------------
    # Lecture
    # ------------------------------------------------------------------
    @property
    def settings(self) -> ServerSettings:
        with self._lock:
            if self._settings is None:
                data = _read_json(self.settings_file)
                self._settings = ServerSettings.from_dict(data) if data else ServerSettings()
            return self._settings

    @property
    def media_filter(self) -> MediaFilter:
        with self._lock:
            if self._filter is None:
                data = _read_json(self.filter_file)
                self._filter = MediaFilter.from_dict(data) if data else MediaFilter()
            return self._filter

    def reload(self) -> None:
        """Force la relecture des fichiers au prochain accès."""
        with self._lock:
            self._settings = None
            self._filter = None
        logger.info("Configuration rechargee depuis %s", self.directory)

    # ------------------------------------------------------------------
    # Écriture
    # ------------------------------------------------------------------
    def save_settings(self, host: Any, port: Any, refresh_interval: Any) -> ServerSettings:
        """Valide puis enregistre les paramètres serveur.

        Raises:
            ConfigError: si une valeur est invalide (rien n'est écrit).
        """
        settings = ServerSettings.validated(host, port, refresh_interval)
        with self._lock:
            _write_json_atomic(self.settings_file, settings.to_dict())
            self._settings = settings
        logger.info("Parametres enregistres : %s:%s", settings.host, settings.port)
        return settings

    def save_media_filter(
        self,
        mode: Any,
        allowed_apps: Iterable[str] | None,
        blocked_apps: Iterable[str] | None,
    ) -> MediaFilter:
        """Valide puis enregistre le filtre média.

        Raises:
            ConfigError: si le mode est invalide (rien n'est écrit).
        """
        media_filter = MediaFilter.validated(mode, allowed_apps, blocked_apps)
        with self._lock:
            _write_json_atomic(self.filter_file, media_filter.to_dict())
            self._filter = media_filter
        logger.info("Filtre media enregistre : mode=%s", media_filter.mode)
        return media_filter

    def ensure_defaults(self) -> None:
        """Crée les fichiers de configuration manquants (premier lancement)."""
        if not self.settings_file.exists():
            _write_json_atomic(self.settings_file, ServerSettings().to_dict())
            logger.info("%s cree avec les valeurs par defaut", SETTINGS_FILE_NAME)
        if not self.filter_file.exists():
            _write_json_atomic(self.filter_file, MediaFilter().to_dict())
            logger.info("%s cree avec les valeurs par defaut", FILTER_FILE_NAME)
