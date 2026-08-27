"""Démarrage, arrêt et redémarrage réels du serveur."""

from __future__ import annotations

import socket
import urllib.request

import pytest

from music_overlay.config import ConfigStore
from music_overlay.media import MediaWatcher
from music_overlay.server.runtime import (
    ServerAlreadyRunningError,
    ServerRuntime,
    find_available_port,
    is_port_available,
)
from music_overlay.skins import SkinRepository


@pytest.fixture
def runtime(store: ConfigStore, repository: SkinRepository):
    store.save_settings("127.0.0.1", find_available_port("127.0.0.1", 49700), 0.5)
    runtime = ServerRuntime(store, skins=repository, watcher=MediaWatcher(store))
    yield runtime
    runtime.stop()


class TestPorts:
    def test_port_libre_detecte(self):
        assert is_port_available("127.0.0.1", find_available_port("127.0.0.1", 49800))

    def test_port_occupe_detecte(self):
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen(1)
            port = occupied.getsockname()[1]
            assert not is_port_available("127.0.0.1", port)

    def test_bascule_sur_le_port_suivant(self):
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen(1)
            port = occupied.getsockname()[1]
            assert find_available_port("127.0.0.1", port) > port


class TestCycleDeVie:
    def test_demarrage_et_arret(self, runtime: ServerRuntime):
        settings = runtime.start()
        assert runtime.running

        with urllib.request.urlopen(f"{settings.url}/health", timeout=5) as response:
            assert response.status == 200

        runtime.stop()
        assert not runtime.running
        assert is_port_available(settings.host, settings.port), "le port doit etre libere"

    def test_redemarrage_possible(self, runtime: ServerRuntime):
        """Le bug historique : après un stop, le serveur ne repartait jamais."""
        first = runtime.start()
        runtime.stop()
        second = runtime.start()

        assert runtime.running
        assert second.port == first.port
        with urllib.request.urlopen(f"{second.url}/health", timeout=5) as response:
            assert response.status == 200

    def test_double_demarrage_refuse(self, runtime: ServerRuntime):
        runtime.start()
        with pytest.raises(ServerAlreadyRunningError):
            runtime.start()

    def test_arret_sans_demarrage_sans_effet(self, runtime: ServerRuntime):
        runtime.stop()
        assert not runtime.running

    def test_bascule_automatique_si_port_occupe(self, runtime: ServerRuntime):
        wanted = runtime.config.settings.port
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", wanted))
            occupied.listen(1)
            settings = runtime.start()
        assert settings.port != wanted
