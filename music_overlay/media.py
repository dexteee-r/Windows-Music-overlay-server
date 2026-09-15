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
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
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
    """Publie la piste courante à partir des évènements WinRT de la session média.

    Le thread est démarré/arrêté avec le serveur et fait tourner une boucle
    asyncio dédiée. Au lieu de sonder Windows en continu, on s'abonne aux
    évènements de la session (``MediaPropertiesChanged``, etc.) : le coût
    WinRT/NPSMSvc n'est payé que quand quelque chose change réellement, plus
    jamais à un rythme fixe. ``refresh_interval`` ne sert plus que de filet de
    sécurité (certains lecteurs ne déclenchent pas ces évènements de façon
    fiable) et de base au recalcul de la position pendant la lecture.

    ``current`` reste lisible à tout moment depuis n'importe quel thread.
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

        # Etat interne au thread media-watcher uniquement (pas de verrou requis).
        self._loop: asyncio.AbstractEventLoop | None = None
        self._manager: Any = None
        self._session: Any = None
        self._session_tokens: list[Any] = []
        self._session_changed_token: Any = None
        self._background_tasks: set[asyncio.Task[None]] = set()

        # Anchre pour interpoler la position de lecture sans repoller WinRT :
        # position = _position_anchor + ecoule_depuis_anchor * _playback_rate.
        self._position_anchor = 0
        self._position_anchor_time = 0.0
        self._playback_rate = 0.0
        self._duration = 0

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------
    @property
    def current(self) -> Track:
        with self._lock:
            track = self._track
            if self._playback_rate == 0.0:
                return track
            elapsed = time.monotonic() - self._position_anchor_time
            position = int(self._position_anchor + elapsed * self._playback_rate)
            position = max(0, min(self._duration, position))
        if position == track.position:
            return track
        return replace(track, position=position)

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
        loop = self._loop
        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(loop.stop)
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=timeout)
        self._thread = None
        with self._lock:
            self._track = NO_TRACK
            self._playback_rate = 0.0
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
        self._loop = loop
        try:
            while not self._stop_event.is_set():
                try:
                    loop.run_until_complete(self._setup())
                    loop.run_forever()
                except Exception as exc:
                    with self._lock:
                        self._last_error = str(exc)
                    logger.debug("Surveillance media interrompue : %s", exc)
                    if self._on_error is not None:
                        self._on_error(exc)
                    self._detach_session()
                    # `_setup()` a echoue avant tout abonnement (WinRT
                    # temporairement indisponible) : on retente au lieu de
                    # laisser le thread mourir definitivement.
                    self._stop_event.wait(self._config.settings.refresh_interval)
        finally:
            self._detach_session()
            if self._manager is not None and self._session_changed_token is not None:
                try:
                    self._manager.remove_current_session_changed(self._session_changed_token)
                except Exception as exc:
                    logger.debug("Desabonnement manager echoue : %s", exc)
            self._manager = None
            self._session_changed_token = None
            self._loop = None
            loop.close()

    async def _setup(self) -> None:
        self._manager = await MediaManager.request_async()
        self._session_changed_token = self._manager.add_current_session_changed(
            self._on_current_session_changed
        )
        await self._attach_session(self._manager.get_current_session())
        self._schedule_safety_tick()

    def _spawn(self, coro: Any) -> None:
        """Lance une coroutine en tâche de fond sans perdre sa référence.

        ``asyncio`` ne garantit pas qu'une tâche créée sans réference reste en
        vie jusqu'à son terme (RUF006) : on la garde dans un set le temps
        qu'elle s'exécute.
        """
        task = self._loop.create_task(coro)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    # Multiplicateur appliqué a ``refresh_interval`` pour l'intervalle du
    # filet de securite. Les evenements WinRT font le travail reactif ; ce
    # tick ne sert qu'a rattraper un evenement manque ou un lecteur qui n'en
    # emet pas. Le decoupler ainsi de ``refresh_interval`` evite de retomber
    # dans un sondage continu au meme rythme que l'ancienne boucle.
    _SAFETY_TICK_FACTOR = 5.0
    _SAFETY_TICK_MIN = 2.0

    def _schedule_safety_tick(self) -> None:
        if self._stop_event.is_set() or self._loop is None:
            return
        delay = max(
            self._SAFETY_TICK_MIN, self._config.settings.refresh_interval * self._SAFETY_TICK_FACTOR
        )
        self._loop.call_later(delay, self._safety_tick)

    def _safety_tick(self) -> None:
        """Filet de sécurité : rattrape un évènement manqué ou un lecteur muet."""
        if self._stop_event.is_set() or self._loop is None:
            return
        self._spawn(self._recheck_current_session())
        self._schedule_safety_tick()

    async def _recheck_current_session(self) -> None:
        try:
            current = self._manager.get_current_session()
        except Exception as exc:
            logger.debug("Relecture de la session courante echouee : %s", exc)
            return

        current_app_id = getattr(current, "source_app_user_model_id", None)
        attached_app_id = getattr(self._session, "source_app_user_model_id", None)
        if current_app_id != attached_app_id:
            await self._attach_session(current)
        else:
            await self._refresh_current_session()

    # ------------------------------------------------------------------
    # Session courante : abonnement et lecture
    # ------------------------------------------------------------------
    def _on_current_session_changed(self, manager: Any, args: Any) -> None:
        loop = self._loop
        if loop is None:
            return
        loop.call_soon_threadsafe(
            lambda: self._spawn(self._attach_session(manager.get_current_session()))
        )

    def _on_media_properties_changed(self, sender: Any, args: Any) -> None:
        loop = self._loop
        if loop is None:
            return
        # `force_thumbnail=True` : cet evenement precis signifie que Windows a
        # rafraichi les proprietes (donc potentiellement la pochette). Sur
        # certaines apps, le titre/artiste se met a jour un instant avant que
        # la reference de pochette ne pointe vers la bonne image ; se fier a
        # l'egalite de la cle (titre, artiste, album) laisserait alors la
        # pochette du morceau precedent figee jusqu'au changement suivant.
        loop.call_soon_threadsafe(
            lambda: self._spawn(self._refresh_current_session(force_thumbnail=True))
        )

    def _on_session_event(self, sender: Any, args: Any) -> None:
        loop = self._loop
        if loop is None:
            return
        loop.call_soon_threadsafe(lambda: self._spawn(self._refresh_current_session()))

    def _detach_session(self) -> None:
        session = self._session
        if session is not None:
            removers = (
                (session.remove_media_properties_changed, self._session_tokens[0])
                if len(self._session_tokens) > 0
                else None,
                (session.remove_playback_info_changed, self._session_tokens[1])
                if len(self._session_tokens) > 1
                else None,
                (session.remove_timeline_properties_changed, self._session_tokens[2])
                if len(self._session_tokens) > 2
                else None,
            )
            for entry in removers:
                if entry is None:
                    continue
                remover, token = entry
                try:
                    remover(token)
                except Exception as exc:
                    logger.debug("Desabonnement session echoue : %s", exc)
        self._session = None
        self._session_tokens = []

    async def _attach_session(self, session: Any) -> None:
        self._detach_session()
        self._session = session
        if session is None:
            with self._lock:
                self._track = NO_TRACK
                self._playback_rate = 0.0
                self._last_error = None
            return

        self._session_tokens = [
            session.add_media_properties_changed(self._on_media_properties_changed),
            session.add_playback_info_changed(self._on_session_event),
            session.add_timeline_properties_changed(self._on_session_event),
        ]
        await self._refresh_current_session(force_thumbnail=True)

    async def _refresh_current_session(self, force_thumbnail: bool = False) -> None:
        session = self._session
        if session is None:
            return

        try:
            app_id = session.source_app_user_model_id or ""
            media_filter: MediaFilter = self._config.media_filter
            if not media_filter.allows(app_id):
                logger.debug("Application filtree : %s", app_id)
                with self._lock:
                    self._track = NO_TRACK
                    self._playback_rate = 0.0
                    self._last_error = None
                return

            properties = await session.try_get_media_properties_async()
            playback = session.get_playback_info()
            timeline = session.get_timeline_properties()

            title = getattr(properties, "title", "") or "Unknown Title"
            artist = getattr(properties, "artist", "") or "Unknown Artist"
            album = getattr(properties, "album_title", "") or ""
            key = (title, artist, album)

            cached_key, cached_thumbnail = self._thumbnail_cache
            if not force_thumbnail and cached_key == key:
                thumbnail = cached_thumbnail
            else:
                thumbnail = await _read_thumbnail(properties)
                self._thumbnail_cache = (key, thumbnail)

            is_playing = getattr(playback, "playback_status", 0) == PLAYBACK_STATUS_PLAYING
            position = _seconds(getattr(timeline, "position", None))
            duration = _seconds(getattr(timeline, "end_time", None))
            rate = getattr(playback, "playback_rate", None) or 1.0

            track = Track(
                title=title,
                artist=artist,
                album=album,
                thumbnail=thumbnail,
                is_playing=is_playing,
                position=position,
                duration=duration,
                source_app=app_id,
            )
            with self._lock:
                self._track = track
                self._duration = duration
                self._position_anchor = position
                self._position_anchor_time = time.monotonic()
                self._playback_rate = rate if is_playing else 0.0
                self._last_error = None
        except Exception as exc:
            with self._lock:
                self._last_error = str(exc)
            logger.debug("Lecture media echouee : %s", exc)
            if self._on_error is not None:
                self._on_error(exc)


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
