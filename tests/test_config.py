"""Validation, persistance et filtrage média."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from music_overlay.config import (
    DEFAULT_PORT,
    ConfigError,
    ConfigStore,
    MediaFilter,
    ServerSettings,
)


class TestServerSettings:
    def test_valeurs_par_defaut(self):
        settings = ServerSettings()
        assert settings.port == DEFAULT_PORT
        assert settings.host == "127.0.0.1"

    @pytest.mark.parametrize("port", ["49450", 49450, " 49450 "])
    def test_port_accepte_les_chaines(self, port):
        assert ServerSettings.validated("127.0.0.1", port, 0.5).port == 49450

    @pytest.mark.parametrize("port", [80, 0, 70000, "abc", None])
    def test_port_invalide(self, port):
        with pytest.raises(ConfigError):
            ServerSettings.validated("127.0.0.1", port, 0.5)

    @pytest.mark.parametrize("interval", [0.05, 42, "x"])
    def test_intervalle_invalide(self, interval):
        with pytest.raises(ConfigError):
            ServerSettings.validated("127.0.0.1", 49450, interval)

    def test_virgule_decimale_acceptee(self):
        assert ServerSettings.validated("127.0.0.1", 49450, "0,5").refresh_interval == 0.5

    def test_host_vide_refuse(self):
        with pytest.raises(ConfigError):
            ServerSettings.validated("   ", 49450, 0.5)

    def test_url_remplace_l_adresse_d_ecoute_globale(self):
        assert ServerSettings(host="0.0.0.0", port=49450).url == "http://127.0.0.1:49450"

    def test_json_invalide_retombe_sur_les_defauts(self):
        assert ServerSettings.from_dict({"port": "n'importe quoi"}) == ServerSettings()


class TestMediaFilter:
    def test_mode_all_accepte_tout_sauf_bloque(self):
        media_filter = MediaFilter(mode="all", allowed_apps=(), blocked_apps=("chrome.exe",))
        assert media_filter.allows("Spotify.exe")
        assert not media_filter.allows("chrome.exe")

    def test_whitelist_n_accepte_que_les_apps_listees(self):
        media_filter = MediaFilter(mode="whitelist", allowed_apps=("Spotify.exe",))
        assert media_filter.allows("Spotify.exe")
        assert not media_filter.allows("chrome.exe")

    def test_blacklist_accepte_tout_sauf_les_apps_listees(self):
        media_filter = MediaFilter(mode="blacklist", blocked_apps=("chrome.exe",))
        assert media_filter.allows("Spotify.exe")
        assert not media_filter.allows("chrome.exe")

    def test_comparaison_insensible_a_la_casse(self):
        media_filter = MediaFilter(mode="whitelist", allowed_apps=("SPOTIFY.exe",))
        assert media_filter.allows("spotify.exe")

    def test_app_vide_toujours_refusee(self):
        assert not MediaFilter(mode="all").allows("")
        assert not MediaFilter(mode="all").allows(None)

    def test_mode_invalide(self):
        with pytest.raises(ConfigError):
            MediaFilter.validated("nawak", (), ())

    def test_doublons_et_vides_nettoyes(self):
        media_filter = MediaFilter.validated("all", ["a", " a ", "", "b"], None)
        assert media_filter.allowed_apps == ("a", "b")

    def test_with_allowed_ajoute_sans_doublon(self):
        media_filter = MediaFilter(mode="whitelist", allowed_apps=("a",))
        assert media_filter.with_allowed("b").allowed_apps == ("a", "b")
        assert media_filter.with_allowed("a").allowed_apps == ("a",)


class TestConfigStore:
    def test_ensure_defaults_cree_les_fichiers(self, config_dir: Path):
        store = ConfigStore(config_dir)
        store.ensure_defaults()
        assert store.settings_file.exists()
        assert store.filter_file.exists()

    def test_relecture_apres_sauvegarde(self, config_dir: Path):
        ConfigStore(config_dir).save_settings("127.0.0.1", 50000, 1.5)
        assert ConfigStore(config_dir).settings.port == 50000

    def test_sauvegarde_invalide_n_ecrit_rien(self, config_dir: Path):
        store = ConfigStore(config_dir)
        store.ensure_defaults()
        original = store.settings_file.read_text(encoding="utf-8")
        with pytest.raises(ConfigError):
            store.save_settings("127.0.0.1", 42, 0.5)
        assert store.settings_file.read_text(encoding="utf-8") == original

    def test_fichier_corrompu_ne_fait_pas_planter(self, config_dir: Path):
        (config_dir / "settings.json").write_text("{ pas du json", encoding="utf-8")
        assert ConfigStore(config_dir).settings == ServerSettings()

    def test_reload_relit_les_modifications_externes(self, config_dir: Path):
        store = ConfigStore(config_dir)
        store.ensure_defaults()
        assert store.settings.port == DEFAULT_PORT

        payload = json.loads(store.settings_file.read_text(encoding="utf-8"))
        payload["port"] = 51000
        store.settings_file.write_text(json.dumps(payload), encoding="utf-8")

        assert store.settings.port == DEFAULT_PORT  # cache encore chaud
        store.reload()
        assert store.settings.port == 51000

    def test_filtre_persiste(self, config_dir: Path):
        store = ConfigStore(config_dir)
        store.save_media_filter("blacklist", [], ["chrome.exe"])
        assert ConfigStore(config_dir).media_filter.blocked_apps == ("chrome.exe",)
