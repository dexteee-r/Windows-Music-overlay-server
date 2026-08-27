"""Lecture de la session média Windows (API ``GlobalSystemMediaTransportControls``).

Le module s'importe même sans les paquets ``winrt`` : ``WINRT_AVAILABLE`` passe
simplement à ``False``. Cela permet de lancer les tests, la GUI et le
diagnostic sur une installation incomplète et d'afficher un message utile au
lieu d'un ``ImportError`` brut.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import threading
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

from .config import ConfigStore, MediaFilter

logger = logging.getLogger(__name__)

try:  # pragma: no cover - dépend de l'environnement Windows
    from winrt.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    )
    from winrt.windows.storage.streams import Buffer, DataReader, InputStreamOptions

    WINRT_AVAILABLE = True
    WINRT_ERROR: str | None = None
except ImportError as exc:  # pragma: no cover - dépend de l'environnement Windows
    MediaManager = None  # type: ignore[assignment]
    Buffer = DataReader = InputStreamOptions = None  # type: ignore[assignment]
    WINRT_AVAILABLE = False
    WINRT_ERROR = str(exc)

PLAYBACK_STATUS_PLAYING = 4


@dataclass(frozen=True)
class Track:
    """Instantané de la piste en cours."""

    title: str = "No track playing"
    artist: str = "Unknown"
    album: str = ""
    thumbnail: str = ""
    is_playing: bool = False
    position: int = 0
    duration: int = 0
    source_app: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def key(self) -> tuple[str, str, str]:
        """Identité de la piste, utilisée pour le cache de pochette."""
        return (self.title, self.artist, self.album)


NO_TRACK = Track()


@dataclass
class MediaSource:
    """Application média détectée, qu'elle soit filtrée ou non."""

    app_id: str
    title: str = ""
    artist: str = ""
    is_playing: bool = False
    allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MediaUnavailableError(RuntimeError):
    """Les API média Windows ne sont pas utilisables."""


def _require_winrt() -> None:
    if not WINRT_AVAILABLE:
        raise MediaUnavailableError(
            "Les paquets winrt ne sont pas installes. "
            "Relancez scripts\\install.bat pour reparer l'installation."
        )


async def _read_thumbnail(properties: Any) -> str:
    """Encode la pochette en data-URI base64, ou chaîne vide si indisponible."""
    reference = getattr(properties, "thumbnail", None)
    if reference is None:
        return ""
    try:
        stream = await reference.open_read_async()
        buffer = Buffer(stream.size)
        await stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
        reader = DataReader.from_buffer(buffer)
        payload = bytearray(buffer.length)
        reader.read_bytes(payload)
    except Exception as exc:
        logger.debug("Pochette illisible : %s", exc)
        return ""
    return "data:image/jpeg;base64," + base64.b64encode(payload).decode("ascii")


def _seconds(value: Any) -> int:
    try:
        return int(value.total_seconds()) if value else 0
    except (AttributeError, TypeError, ValueError):
        return 0


class MediaWatcher:
    """Interroge Windows en boucle et publie la piste courante.

    Le thread est démarré/arrêté avec le serveur. ``current`` reste lisible à
    tout moment depuis n'importe quel thread.
    """

    def __init__(self, config: ConfigStore, on_error: Callable[[Exception], None] | None = None):
        self._config = config
        self._on_error = on_error
        self._lock = threading.Lock()
        self._track: Track = NO_TRACK
        self._thumbnail_cache: tuple[tuple[str, str, str] | None, str] = (None, "")
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_error: str | None = None

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------
    @property
    def current(self) -> Track:
        with self._lock:
            return self._track

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def last_error(self) -> str | None:
        with self._lock:
            return self._last_error

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Démarre le thread de rafraîchissement (sans effet s'il tourne déjà)."""
        if self.running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="media-watcher", daemon=True)
        self._thread.start()
        logger.info("Surveillance media demarree")

    def stop(self, timeout: float = 3.0) -> None:
        """Demande l'arrêt du thread et attend sa fin."""
        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=timeout)
        self._thread = None
        with self._lock:
            self._track = NO_TRACK
        logger.info("Surveillance media arretee")

    # ------------------------------------------------------------------
    # Boucle interne
    # ------------------------------------------------------------------
    def _run(self) -> None:
        if not WINRT_AVAILABLE:
            message = "winrt indisponible : la piste en cours ne sera pas detectee"
            logger.error(message)
            with self._lock:
                self._last_error = message
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            while not self._stop_event.is_set():
                try:
                    track = loop.run_until_complete(self._poll_once())
                    with self._lock:
                        self._track = track or NO_TRACK
                        self._last_error = None
                except Exception as exc:
                    with self._lock:
                        self._last_error = str(exc)
                    logger.debug("Lecture media echouee : %s", exc)
                    if self._on_error is not None:
                        self._on_error(exc)

                self._stop_event.wait(self._config.settings.refresh_interval)
        finally:
            loop.close()

    async def _poll_once(self) -> Track | None:
        manager = await MediaManager.request_async()
        session = manager.get_current_session()
        if session is None:
            return None

        app_id = session.source_app_user_model_id or ""
        media_filter: MediaFilter = self._config.media_filter
        if not media_filter.allows(app_id):
            logger.debug("Application filtree : %s", app_id)
            return None

        properties = await session.try_get_media_properties_async()
        playback = session.get_playback_info()
        timeline = session.get_timeline_properties()

        title = getattr(properties, "title", "") or "Unknown Title"
        artist = getattr(properties, "artist", "") or "Unknown Artist"
        album = getattr(properties, "album_title", "") or ""
        key = (title, artist, album)

        cached_key, cached_thumbnail = self._thumbnail_cache
        if cached_key == key:
            thumbnail = cached_thumbnail
        else:
            thumbnail = await _read_thumbnail(properties)
            self._thumbnail_cache = (key, thumbnail)

        return Track(
            title=title,
            artist=artist,
            album=album,
            thumbnail=thumbnail,
            is_playing=getattr(playback, "playback_status", 0) == PLAYBACK_STATUS_PLAYING,
            position=_seconds(getattr(timeline, "position", None)),
            duration=_seconds(getattr(timeline, "end_time", None)),
            source_app=app_id,
        )


def _all_sessions(manager: Any) -> list[Any]:
    """Toutes les sessions média, avec repli sur la session courante.

    ``get_sessions()`` a besoin du paquet ``winrt-Windows.Foundation.Collections``
    (il retourne une collection WinRT). S'il manque, on se rabat sur la seule
    session active plutôt que d'échouer : l'utilisateur voit au moins
    l'application qu'il est en train d'écouter.
    """
    try:
        return list(manager.get_sessions())
    except (ModuleNotFoundError, AttributeError, OSError) as exc:
        logger.warning(
            "Enumeration des sessions indisponible (%s), repli sur la session active", exc
        )
        session = manager.get_current_session()
        return [session] if session is not None else []


async def _collect_sources(media_filter: MediaFilter) -> list[MediaSource]:
    manager = await MediaManager.request_async()
    sources: list[MediaSource] = []
    seen: set[str] = set()

    for session in _all_sessions(manager):
        app_id = session.source_app_user_model_id or ""
        if not app_id or app_id in seen:
            continue
        seen.add(app_id)

        title = artist = ""
        try:
            properties = await session.try_get_media_properties_async()
            title = getattr(properties, "title", "") or ""
            artist = getattr(properties, "artist", "") or ""
        except Exception as exc:
            logger.debug("Metadonnees indisponibles pour %s : %s", app_id, exc)

        playing = False
        try:
            playing = session.get_playback_info().playback_status == PLAYBACK_STATUS_PLAYING
        except Exception as exc:
            logger.debug("Statut de lecture indisponible pour %s : %s", app_id, exc)

        sources.append(
            MediaSource(
                app_id=app_id,
                title=title,
                artist=artist,
                is_playing=playing,
                allowed=media_filter.allows(app_id),
            )
        )

    sources.sort(key=lambda source: (not source.is_playing, source.app_id.lower()))
    return sources


def list_sources(media_filter: MediaFilter) -> list[MediaSource]:
    """Liste toutes les applications média actives, filtre ignoré.

    C'est ce qui alimente le bouton « Détecter les applications » de la GUI :
    l'utilisateur n'a plus à aller lire un JSON pour trouver l'identifiant
    exact de Spotify ou d'Apple Music.

    Raises:
        MediaUnavailableError: si les paquets ``winrt`` manquent.
    """
    _require_winrt()
    return asyncio.run(_collect_sources(media_filter))
