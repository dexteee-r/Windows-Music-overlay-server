"""Découverte des skins, cache, skin actif et garde-fous de sécurité."""

from __future__ import annotations

from pathlib import Path

import pytest

from music_overlay.skins import (
    DEFAULT_SKIN_ID,
    Skin,
    SkinNotFoundError,
    SkinRepository,
    is_valid_skin_id,
)


class TestDecouverte:
    def test_liste_les_skins_valides(self, repository: SkinRepository):
        assert {skin.id for skin in repository.list_skins()} == {
            "zen_minimalist",
            "neon_cyberpunk",
        }

    def test_dossier_sans_skin_html_ignore(self, skins_dir: Path, repository: SkinRepository):
        (skins_dir / "vide").mkdir()
        assert not any(skin.id == "vide" for skin in repository.list_skins(force_refresh=True))

    def test_metadonnees_lues_depuis_info_json(self, repository: SkinRepository):
        assert repository.get("zen_minimalist").name == "Zen Minimalist"

    def test_nom_par_defaut_sans_info_json(
        self, skins_dir: Path, repository: SkinRepository, write_skin
    ):
        write_skin(skins_dir, "retro_cassette")
        repository.invalidate()
        assert repository.get("retro_cassette").name == "Retro Cassette"

    def test_info_json_corrompu_tolere(
        self, skins_dir: Path, repository: SkinRepository, write_skin
    ):
        write_skin(skins_dir, "casse")
        (skins_dir / "casse" / "info.json").write_text("{{{", encoding="utf-8")
        repository.invalidate()
        assert repository.get("casse").name == "Casse"

    def test_priorite_au_premier_repertoire(
        self, tmp_path: Path, skins_dir: Path, config_dir: Path, write_skin
    ):
        user_dir = tmp_path / "skins_utilisateur"
        user_dir.mkdir()
        write_skin(user_dir, "zen_minimalist", name="Version utilisateur")

        repository = SkinRepository([user_dir, skins_dir], config_dir=config_dir)
        assert repository.get("zen_minimalist").name == "Version utilisateur"


class TestSecurite:
    @pytest.mark.parametrize(
        "skin_id",
        ["../config", "..\\config", "a/b", "", None, "skin;rm", "." * 5],
    )
    def test_identifiants_refuses(self, skin_id):
        assert not is_valid_skin_id(skin_id)

    def test_remontee_d_arborescence_refusee(self, repository: SkinRepository):
        with pytest.raises(SkinNotFoundError):
            repository.get("../../etc")


class TestSkinActif:
    def test_defaut_quand_rien_n_est_configure(self, repository: SkinRepository):
        assert repository.active_id == DEFAULT_SKIN_ID

    def test_set_active_persiste(self, repository: SkinRepository, config_dir: Path):
        repository.set_active("neon_cyberpunk")
        assert repository.active_id == "neon_cyberpunk"
        assert (config_dir / "active_skin.json").exists()

    def test_set_active_inconnu_leve(self, repository: SkinRepository):
        with pytest.raises(SkinNotFoundError):
            repository.set_active("inexistant")

    def test_skin_actif_supprime_bascule_sur_un_autre(
        self, repository: SkinRepository, skins_dir: Path
    ):
        repository.set_active("neon_cyberpunk")
        for file in (skins_dir / "neon_cyberpunk").iterdir():
            file.unlink()
        (skins_dir / "neon_cyberpunk").rmdir()
        repository.invalidate()

        assert repository.active_id == DEFAULT_SKIN_ID

    def test_html_du_skin_actif(self, repository: SkinRepository):
        assert "zen_minimalist" in repository.active_html()


class TestCache:
    def test_modification_du_html_prise_en_compte(
        self, repository: SkinRepository, skins_dir: Path
    ):
        assert "zen_minimalist" in repository.read_html("zen_minimalist")

        html_file = skins_dir / "zen_minimalist" / "skin.html"
        html_file.write_text("<html>nouvelle version</html>", encoding="utf-8")
        import os

        stat = html_file.stat()
        os.utime(html_file, (stat.st_atime, stat.st_mtime + 10))

        assert "nouvelle version" in repository.read_html("zen_minimalist")

    def test_nouveau_skin_visible_apres_invalidation(
        self, repository: SkinRepository, skins_dir: Path, write_skin
    ):
        assert len(repository.list_skins()) == 2
        write_skin(skins_dir, "nouveau")
        repository.invalidate()
        assert len(repository.list_skins()) == 3


class TestSkin:
    def test_to_dict_expose_has_preview(self, repository: SkinRepository, skins_dir: Path):
        skin: Skin = repository.get("zen_minimalist")
        assert skin.to_dict()["has_preview"] is False

        (skins_dir / "zen_minimalist" / "preview.png").write_bytes(b"png")
        assert repository.get("zen_minimalist").to_dict()["has_preview"] is True
