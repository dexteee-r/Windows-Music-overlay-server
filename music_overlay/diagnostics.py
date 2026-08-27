"""Auto-diagnostic de l'installation.

Un seul endroit décrit ce dont l'application a besoin pour fonctionner ; le
bouton « Diagnostic » de la GUI, ``scripts/diagnostic.bat`` et le message
d'erreur affiché au démarrage utilisent tous ce module.

Utilisation en ligne de commande ::

    python -m music_overlay.diagnostics
"""

from __future__ import annotations

import importlib
import platform
import sys
from dataclasses import dataclass

from . import __app_name__, __version__, paths
from .config import ConfigStore
from .server import is_port_available
from .skins import SkinRepository

MINIMUM_PYTHON = (3, 10)

# (module importable, nom affiché, indispensable ?, ce qu'on perd sans lui)
DEPENDENCIES = (
    ("flask", "Flask", True, "le serveur web"),
    ("flask_cors", "Flask-CORS", True, "l'acces API depuis d'autres pages"),
    ("winrt.windows.media.control", "winrt", True, "la detection de la musique"),
    ("requests", "requests", False, "les verifications reseau"),
    ("tkinter", "tkinter", False, "l'interface graphique"),
    ("PIL", "Pillow", False, "les apercus de skins et l'icone"),
    ("pystray", "pystray", False, "l'icone dans la barre des taches"),
    ("win32com.client", "pywin32", False, "le demarrage automatique"),
)


@dataclass(frozen=True)
class CheckResult:
    """Résultat d'une vérification unitaire."""

    name: str
    ok: bool
    detail: str = ""
    hint: str = ""
    critical: bool = True

    @property
    def status(self) -> str:
        if self.ok:
            return "OK"
        return "ECHEC" if self.critical else "ATTENTION"

    def format(self) -> str:
        line = f"[{self.status}] {self.name}"
        if self.detail:
            line += f" : {self.detail}"
        if not self.ok and self.hint:
            line += f"\n         -> {self.hint}"
        return line


def _check_python() -> CheckResult:
    version = platform.python_version()
    ok = sys.version_info >= MINIMUM_PYTHON
    return CheckResult(
        name="Version de Python",
        ok=ok,
        detail=version,
        hint=(
            f"Installez Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}+ depuis python.org "
            "en cochant « Add python.exe to PATH »."
        ),
    )


def _check_dependency(module: str, label: str, critical: bool, purpose: str) -> CheckResult:
    try:
        importlib.import_module(module)
    except Exception as exc:
        return CheckResult(
            name=f"Dependance {label}",
            ok=False,
            detail=str(exc),
            hint=f"Relancez scripts\\install.bat (necessaire pour {purpose}).",
            critical=critical,
        )
    return CheckResult(name=f"Dependance {label}", ok=True, critical=critical)


def _check_config() -> CheckResult:
    store = ConfigStore()
    try:
        store.ensure_defaults()
    except OSError as exc:
        return CheckResult(
            name="Dossier de configuration",
            ok=False,
            detail=str(exc),
            hint=(
                f"Verifiez les droits d'ecriture sur {store.directory} "
                "ou deplacez l'application hors d'un dossier protege."
            ),
        )
    return CheckResult(name="Dossier de configuration", ok=True, detail=str(store.directory))


def _check_skins() -> CheckResult:
    repository = SkinRepository()
    skins = repository.list_skins()
    return CheckResult(
        name="Skins installes",
        ok=bool(skins),
        detail=f"{len(skins)} skin(s)",
        hint=(
            "Le dossier skins/ est vide : reinstallez l'application ou "
            "restaurez au moins un dossier de skin."
        ),
    )


def _check_port() -> CheckResult:
    settings = ConfigStore().settings
    available = is_port_available(settings.host, settings.port)
    return CheckResult(
        name="Port du serveur",
        ok=available,
        detail=f"{settings.host}:{settings.port}",
        hint=(
            "Le port est occupe. L'application basculera automatiquement sur le "
            "port libre suivant, ou changez-le dans l'onglet Parametres."
        ),
        critical=False,
    )


def run_checks() -> list[CheckResult]:
    """Exécute toutes les vérifications, de la plus fondamentale à la plus fine."""
    results = [_check_python()]
    results += [
        _check_dependency(module, label, critical, purpose)
        for module, label, critical, purpose in DEPENDENCIES
    ]
    results.append(_check_config())
    results.append(_check_skins())
    results.append(_check_port())
    return results


def format_report(results: list[CheckResult] | None = None) -> str:
    """Rapport texte lisible, réutilisé par la GUI et la ligne de commande."""
    results = results if results is not None else run_checks()
    failures = [result for result in results if not result.ok and result.critical]
    warnings = [result for result in results if not result.ok and not result.critical]

    lines = [
        f"{__app_name__} v{__version__} - diagnostic",
        f"Systeme    : {platform.system()} {platform.release()}",
        f"Executable : {sys.executable}",
        f"Dossier    : {paths.app_dir()}",
        "",
    ]
    lines += [result.format() for result in results]
    lines.append("")

    if failures:
        lines.append(f"{len(failures)} probleme(s) bloquant(s) a corriger.")
    elif warnings:
        lines.append("Installation fonctionnelle, avec des avertissements sans gravite.")
    else:
        lines.append("Tout est OK : l'application peut demarrer.")
    return "\n".join(lines)


def main() -> int:
    """Point d'entrée console : code de retour 1 si un test critique échoue."""
    results = run_checks()
    print(format_report(results))
    return 1 if any(not result.ok and result.critical for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
