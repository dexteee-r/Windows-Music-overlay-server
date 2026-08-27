"""Découverte, lecture et sélection des skins de l'overlay.

Un skin est un dossier contenant :

- ``skin.html`` (obligatoire) : la page affichée par OBS ;
- ``info.json`` (optionnel) : nom, description, auteur, version ;
- ``preview.png`` (optionnel) : capture affichée dans la GUI.
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import paths

logger = logging.getLogger(__name__)

DEFAULT_SKIN_ID = "zen_minimalist"
ACTIVE_SKIN_FILE_NAME = "active_skin.json"
ACTIVE_SKIN_COMMENT = "Definit le skin actif affiche par l'overlay"
SKIN_HTML_NAME = "skin.html"
SKIN_INFO_NAME = "info.json"
SKIN_PREVIEW_NAME = "preview.png"
CACHE_TTL_SECONDS = 30.0

# Un identifiant de skin provient de l'URL (``/api/set-skin/<id>``) : il sert à
# construire un chemin, donc il est strictement validé pour empêcher toute
# remontée d'arborescence.
SKIN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


class SkinNotFoundError(LookupError):
    """Le skin demandé n'existe pas ou ne contient pas de ``skin.html``."""


def is_valid_skin_id(skin_id: str | None) -> bool:
    """Valide un identifiant de skin (lettres, chiffres, ``_`` et ``-``)."""
    return bool(skin_id) and bool(SKIN_ID_PATTERN.match(str(skin_id)))


@dataclass(frozen=True)
class Skin:
    """Métadonnées d'un skin installé."""

    id: str
    name: str
    description: str
    author: str
    version: str
    directory: Path

    @property
    def html_file(self) -> Path:
        return self.directory / SKIN_HTML_NAME

    @property
    def preview_file(self) -> Path | None:
        preview = self.directory / SKIN_PREVIEW_NAME
        return preview if preview.exists() else None

    @property
    def has_preview(self) -> bool:
        return self.preview_file is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "has_preview": self.has_preview,
        }

    @classmethod
    def from_directory(cls, directory: Path) -> Skin | None:
        """Construit un ``Skin`` depuis un dossier, ou ``None`` s'il est invalide."""
        if not (directory / SKIN_HTML_NAME).exists():
            return None

        skin_id = directory.name
        if not is_valid_skin_id(skin_id):
            logger.warning("Dossier de skin ignore (nom invalide) : %s", skin_id)
            return None

        info: dict[str, Any] = {}
        info_file = directory / SKIN_INFO_NAME
        if info_file.exists():
            try:
                with open(info_file, encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    info = loaded
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("%s illisible (%s), metadonnees par defaut", info_file.name, exc)

        return cls(
            id=skin_id,
            name=str(info.get("name") or skin_id.replace("_", " ").title()),
            description=str(info.get("description") or "Skin personnalise"),
            author=str(info.get("author") or "Inconnu"),
            version=str(info.get("version") or "1.0"),
            directory=directory,
        )


class SkinRepository:
    """Accès thread-safe aux skins, avec cache de la liste et du HTML.

    Plusieurs répertoires peuvent être scrutés : les skins ajoutés par
    l'utilisateur (à côté de l'exécutable) ont priorité sur ceux fournis avec
    l'application.
    """

    def __init__(
        self,
        directories: Iterable[Path] | None = None,
        config_dir: Path | None = None,
        cache_ttl: float = CACHE_TTL_SECONDS,
    ):
        self.directories = [Path(d) for d in (directories or paths.skins_dirs())]
        self.config_dir = Path(config_dir) if config_dir is not None else paths.config_dir()
        self.active_skin_file = self.config_dir / ACTIVE_SKIN_FILE_NAME
        self.cache_ttl = cache_ttl

        self._lock = threading.RLock()
        self._skins: dict[str, Skin] | None = None
        self._skins_time = 0.0
        self._html_cache: dict[str, tuple[float, str]] = {}
        self._active_id: str | None = None

    # ------------------------------------------------------------------
    # Liste des skins
    # ------------------------------------------------------------------
    def _scan(self) -> dict[str, Skin]:
        found: dict[str, Skin] = {}
        for directory in self.directories:
            if not directory.is_dir():
                continue
            for entry in sorted(directory.iterdir()):
                if not entry.is_dir() or entry.name in found:
                    continue
                skin = Skin.from_directory(entry)
                if skin is not None:
                    found[skin.id] = skin
        return found

    def _cached_skins(self, force_refresh: bool = False) -> dict[str, Skin]:
        with self._lock:
            expired = (time.monotonic() - self._skins_time) >= self.cache_ttl
            if force_refresh or self._skins is None or expired:
                self._skins = self._scan()
                self._skins_time = time.monotonic()
            return self._skins

    def list_skins(self, force_refresh: bool = False) -> list[Skin]:
        """Retourne les skins disponibles, triés par nom affiché."""
        skins = self._cached_skins(force_refresh)
        return sorted(skins.values(), key=lambda skin: skin.name.lower())

    def get(self, skin_id: str) -> Skin:
        """Retourne un skin par identifiant.

        Raises:
            SkinNotFoundError: si l'identifiant est invalide ou introuvable.
        """
        if not is_valid_skin_id(skin_id):
            raise SkinNotFoundError(f"Identifiant de skin invalide : {skin_id!r}")

        skins = self._cached_skins()
        skin = skins.get(skin_id)
        if skin is None:
            skin = self._cached_skins(force_refresh=True).get(skin_id)
        if skin is None:
            raise SkinNotFoundError(f"Le skin '{skin_id}' n'existe pas")
        return skin

    def exists(self, skin_id: str) -> bool:
        try:
            self.get(skin_id)
        except SkinNotFoundError:
            return False
        return True

    def invalidate(self) -> None:
        """Vide les caches (nouveau skin déposé, fichier modifié à la main)."""
        with self._lock:
            self._skins = None
            self._skins_time = 0.0
            self._html_cache.clear()
            self._active_id = None

    # ------------------------------------------------------------------
    # Contenu HTML
    # ------------------------------------------------------------------
    def read_html(self, skin_id: str) -> str:
        """Lit le HTML d'un skin, avec cache invalidé par la date du fichier.

        Éditer un ``skin.html`` pendant que le serveur tourne suffit donc à voir
        le changement au rafraîchissement suivant.

        Raises:
            SkinNotFoundError: si le skin est introuvable ou illisible.
        """
        skin = self.get(skin_id)
        try:
            mtime = skin.html_file.stat().st_mtime
        except OSError as exc:
            raise SkinNotFoundError(f"Le skin '{skin_id}' est illisible : {exc}") from exc

        with self._lock:
            cached = self._html_cache.get(skin_id)
            if cached is not None and cached[0] == mtime:
                return cached[1]

        try:
            html = skin.html_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise SkinNotFoundError(f"Le skin '{skin_id}' est illisible : {exc}") from exc

        with self._lock:
            self._html_cache[skin_id] = (mtime, html)
        return html

    # ------------------------------------------------------------------
    # Skin actif
    # ------------------------------------------------------------------
    def _read_active_id(self) -> str:
        try:
            with open(self.active_skin_file, encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                value = str(data.get("active_skin", "")).strip()
                if value:
                    return value
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("%s illisible (%s)", ACTIVE_SKIN_FILE_NAME, exc)
        return DEFAULT_SKIN_ID

    @property
    def active_id(self) -> str:
        """Identifiant du skin actif, garanti installé.

        Si le skin configuré a disparu, on retombe sur le skin par défaut puis,
        à défaut, sur le premier skin trouvé — l'overlay affiche donc toujours
        quelque chose.
        """
        with self._lock:
            if self._active_id is not None:
                return self._active_id

        wanted = self._read_active_id()
        resolved = wanted
        if not self.exists(wanted):
            available = self.list_skins()
            fallback = DEFAULT_SKIN_ID if self.exists(DEFAULT_SKIN_ID) else None
            if fallback is None and available:
                fallback = available[0].id
            if fallback is None:
                raise SkinNotFoundError("Aucun skin installe")
            logger.warning("Skin actif '%s' introuvable, bascule sur '%s'", wanted, fallback)
            resolved = fallback

        with self._lock:
            self._active_id = resolved
        return resolved

    def set_active(self, skin_id: str) -> Skin:
        """Change le skin actif et l'enregistre.

        Raises:
            SkinNotFoundError: si le skin n'existe pas (rien n'est écrit).
        """
        skin = self.get(skin_id)
        payload = {"_commentaire": ACTIVE_SKIN_COMMENT, "active_skin": skin.id}

        self.config_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.active_skin_file.with_name(self.active_skin_file.name + ".tmp")
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        temporary.replace(self.active_skin_file)

        with self._lock:
            self._active_id = skin.id
        logger.info("Skin actif : %s", skin.id)
        return skin

    def active_html(self) -> str:
        """HTML du skin actif, prêt à être servi."""
        return self.read_html(self.active_id)
