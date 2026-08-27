"""Fixtures partagées : arborescence temporaire, config et application de test."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from music_overlay.config import ConfigStore
from music_overlay.media import MediaWatcher
from music_overlay.server.app import create_app
from music_overlay.skins import SkinRepository

SKIN_HTML = "<!DOCTYPE html><html><body>{name}</body></html>"


def write_skin(root: Path, skin_id: str, **info: object) -> Path:
    """Crée un dossier de skin minimal et retourne son chemin."""
    directory = root / skin_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "skin.html").write_text(SKIN_HTML.format(name=skin_id), encoding="utf-8")
    if info:
        (directory / "info.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    return directory


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "config"
    directory.mkdir()
    return directory


@pytest.fixture
def skins_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "skins"
    directory.mkdir()
    write_skin(directory, "zen_minimalist", name="Zen Minimalist", author="dexteee-r")
    write_skin(directory, "neon_cyberpunk", name="Neon Cyberpunk", version="2.0")
    return directory


@pytest.fixture
def store(config_dir: Path) -> ConfigStore:
    store = ConfigStore(config_dir)
    store.ensure_defaults()
    return store


@pytest.fixture
def repository(skins_dir: Path, config_dir: Path) -> SkinRepository:
    return SkinRepository([skins_dir], config_dir=config_dir)


@pytest.fixture
def client(store: ConfigStore, repository: SkinRepository):
    app = create_app(store, repository, MediaWatcher(store))
    app.config.update(TESTING=True)
    return app.test_client()
