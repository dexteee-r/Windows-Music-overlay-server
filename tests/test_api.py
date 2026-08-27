"""Contrat de l'API HTTP (les skins et les intégrations en dépendent)."""

from __future__ import annotations

from pathlib import Path

import pytest

from music_overlay.config import ConfigStore
from music_overlay.media import MediaSource, MediaUnavailableError
from music_overlay.skins import SkinRepository


class TestOverlay:
    def test_page_racine_sert_le_skin_actif(self, client, repository: SkinRepository):
        repository.set_active("neon_cyberpunk")
        response = client.get("/")
        assert response.status_code == 200
        assert b"neon_cyberpunk" in response.data

    def test_page_racine_sans_skin(self, tmp_path: Path, store: ConfigStore):
        from music_overlay.media import MediaWatcher
        from music_overlay.server import create_app

        vide = tmp_path / "aucun_skin"
        vide.mkdir()
        app = create_app(
            store, SkinRepository([vide], config_dir=store.directory), MediaWatcher(store)
        )
        response = app.test_client().get("/")
        assert response.status_code == 503
        assert "Aucun skin" in response.get_data(as_text=True)

    def test_health(self, client):
        payload = client.get("/health").get_json()
        assert payload["status"] == "ok"
        assert payload["version"]


class TestCurrentTrack:
    def test_structure_de_la_reponse(self, client):
        payload = client.get("/api/current-track").get_json()
        assert set(payload) == {
            "title",
            "artist",
            "album",
            "thumbnail",
            "is_playing",
            "position",
            "duration",
            "source_app",
        }

    def test_valeurs_par_defaut_sans_lecture(self, client):
        payload = client.get("/api/current-track").get_json()
        assert payload["is_playing"] is False
        assert payload["title"] == "No track playing"


class TestSkinsApi:
    @pytest.mark.parametrize("route", ["/api/skins", "/api/list-skins"])
    def test_les_deux_routes_documentees_repondent(self, client, route):
        payload = client.get(route).get_json()
        assert payload["count"] == 2
        assert payload["active_skin"]

    def test_set_skin_par_url(self, client):
        payload = client.post("/api/set-skin/neon_cyberpunk").get_json()
        assert payload["success"] is True
        assert client.get("/api/skins").get_json()["active_skin"] == "neon_cyberpunk"

    def test_set_skin_par_corps_json(self, client):
        payload = client.post("/api/set-skin", json={"skin_id": "neon_cyberpunk"}).get_json()
        assert payload["success"] is True

    def test_set_skin_sans_parametre(self, client):
        response = client.post("/api/set-skin", json={})
        assert response.status_code == 400

    def test_set_skin_inconnu(self, client):
        response = client.post("/api/set-skin/inexistant")
        assert response.status_code == 404
        assert response.get_json()["success"] is False

    def test_set_skin_refuse_la_remontee_d_arborescence(self, client):
        assert client.post("/api/set-skin/..%2F..%2Fconfig").status_code in (307, 404)


class TestSourcesApi:
    def test_liste_les_applications_detectees(self, client, monkeypatch):
        monkeypatch.setattr(
            "music_overlay.server.list_sources",
            lambda _filter: [MediaSource(app_id="Spotify.exe", title="Song", is_playing=True)],
        )
        payload = client.get("/api/sources").get_json()
        assert payload["count"] == 1
        assert payload["sources"][0]["app_id"] == "Spotify.exe"

    def test_message_clair_si_winrt_absent(self, client, monkeypatch):
        def boom(_filter):
            raise MediaUnavailableError("winrt manquant")

        monkeypatch.setattr("music_overlay.server.list_sources", boom)
        response = client.get("/api/sources")
        assert response.status_code == 503
        assert "winrt" in response.get_json()["message"]


class TestReloadConfig:
    def test_recharge_la_configuration(self, client, store: ConfigStore):
        store.save_media_filter("blacklist", [], ["chrome.exe"])
        payload = client.get("/api/reload-config").get_json()
        assert payload["success"] is True
        assert payload["filter_mode"] == "blacklist"
