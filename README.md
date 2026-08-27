# 🎵 Music Overlay Server

**Affichez en direct la musique que vous écoutez, dans OBS.**
Serveur local Windows qui expose la lecture en cours sous forme d'overlay web,
avec 10 skins prêts à l'emploi et une interface de configuration.

![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![Licence](https://img.shields.io/badge/Licence-Open%20Source-orange)

---

## 🚀 Démarrage en 30 secondes

1. **Téléchargez** la dernière version depuis la
   [page des releases](https://github.com/dexteee-r/Windows-Music-overlay-server/releases)
   et décompressez le dossier.
2. **Lancez** l'application :
   - version `.exe` → double-cliquez sur **`MusicOverlayServer.exe`** (aucune installation) ;
   - version sources → double-cliquez sur **`DEMARRER.bat`** (installe tout seul ce qui manque).
3. **Cliquez sur « Démarrer »**, puis sur **« Copier »** pour récupérer l'URL de l'overlay.

Dans OBS : *Sources* → **+** → **Navigateur** → collez l'URL → largeur **650**, hauteur **180**.

> Besoin de détails ? [Installation pas à pas](docs/DEMARRAGE.md) ·
> [Guide d'utilisation](docs/GUIDE.md) · [Dépannage](docs/TROUBLESHOOTING.md)

---

## ✨ Fonctionnalités

| | |
|---|---|
| 🎨 **10 skins** | Aperçu intégré, changement à chaud sans redémarrer |
| 🖼️ **Pochette et progression** | Barre de lecture, equalizer animé, artiste et album |
| 🎯 **Filtre d'applications** | N'affichez que Spotify, ou tout sauf votre navigateur |
| 🔍 **Détection automatique** | Un bouton liste vos lecteurs : plus d'identifiant à recopier |
| 🔔 **Barre des tâches** | L'application se réduit dans le system tray |
| 🚀 **Démarrage avec Windows** | Une case à cocher |
| 🩺 **Diagnostic intégré** | Un bouton dit exactement ce qui manque |
| 🔒 **100 % local** | Rien ne sort de votre PC, aucun compte, aucune télémétrie |

---

## 🎨 Skins disponibles

| Skin | Style |
|------|-------|
| **Zen Minimalist** | Épuré, discret |
| **Neon Cyberpunk** | Néons roses et bleus |
| **Retro Cassette** | Cassette années 80-90 |
| **Glassmorphism Frosted** | Verre dépoli |
| **Modern Vinyl** / **Modern Vinyl V2** | Disque vinyle rotatif |
| **Liquid Capsule** | Capsule fluide |
| **Kinetic Typography** | Texte animé |
| **Clipping Mask** | Masque d'écrêtage |
| **Streetwear Hypebeast** | Urbain moderne |

Onglet **Skins** → sélectionnez → **Appliquer** → rafraîchissez la source dans OBS.
Pour créer le vôtre : [CONTRIBUTING.md](CONTRIBUTING.md).

---

## ⚙️ Configuration

Tout se règle dans l'onglet **Paramètres** ; les fichiers JSON de `config/` restent
modifiables à la main pour les habitués ([détail des options](docs/GUIDE.md)).

**Filtrer les applications** — trois modes :

| Mode | Effet |
|------|-------|
| `all` | Toutes les applications, sauf celles bloquées |
| `whitelist` | Uniquement les applications autorisées |
| `blacklist` | Toutes, sauf les applications bloquées |

Pour remplir la liste : cliquez sur **« Détecter les applications en cours »**,
cochez vos lecteurs, enregistrez. Le filtre s'applique immédiatement.

Si un lecteur échappe à la détection, les listes restent modifiables à la main :
le bouton **« Ouvrir la page source_app »** affiche l'identifiant exact à
recopier ([procédure détaillée](docs/GUIDE.md#choisir-ce-qui-saffiche)).

---

## 📊 API JSON

Toutes les routes sont locales (`http://127.0.0.1:49450` par défaut).

| Route | Description |
|-------|-------------|
| `GET /` | L'overlay lui-même (URL à mettre dans OBS) |
| `GET /health` | État du serveur et version |
| `GET /api/current-track` | Piste en cours |
| `GET /api/skins` (alias `/api/list-skins`) | Skins installés et skin actif |
| `POST /api/set-skin/<id>` | Change le skin (aussi `POST /api/set-skin` avec `{"skin_id": "..."}`) |
| `GET /api/sources` | Applications média détectées |
| `POST /api/reload-config` | Relit la configuration depuis le disque |

```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "thumbnail": "data:image/jpeg;base64,...",
  "is_playing": true,
  "position": 45,
  "duration": 180,
  "source_app": "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"
}
```

---

## 📁 Structure du projet

```
Windows-Music-overlay-server/
├── DEMARRER.bat            # Lancement en un double-clic
├── launcher.pyw            # Point d'entrée GUI
├── server.py               # Point d'entrée console
├── music_overlay/          # Code de l'application
│   ├── config.py           #   configuration et filtre média
│   ├── skins.py            #   découverte et sélection des skins
│   ├── media.py            #   lecture de la session média Windows
│   ├── diagnostics.py      #   auto-diagnostic
│   ├── server.py           #   routes Flask et cycle de vie
│   └── gui/                #   interface tkinter
├── skins/                  # 10 skins (un dossier chacun)
├── config/                 # Configuration utilisateur (JSON)
├── tests/                  # Tests automatisés
├── scripts/                # install.bat, diagnostic.bat, build_exe.bat, recette PyInstaller
└── docs/                   # Documentation détaillée
```

---

## 🛠️ Développement

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

| Commande | Rôle |
|----------|------|
| `python -m music_overlay` | Lance l'interface graphique |
| `python -m music_overlay --console` | Lance le serveur seul |
| `python -m music_overlay --diagnostic` | Vérifie l'installation |
| `pytest` | Exécute les tests |
| `ruff check . && ruff format .` | Lint et formatage |
| `scripts\build_exe.bat` | Compile l'exécutable dans `dist/` |

Les tests et le lint tournent aussi en CI sur chaque push
(voir [.github/workflows/ci.yml](.github/workflows/ci.yml)).

---

## 🔒 Sécurité et vie privée

- Le serveur écoute sur `127.0.0.1` : il n'est **pas** accessible depuis Internet
  ni depuis les autres appareils du réseau.
- Aucune donnée n'est envoyée à l'extérieur ; les seules écritures sont
  `config/` et `logs/`.
- Pour afficher l'overlay depuis un autre appareil du réseau local, passez `host`
  à `0.0.0.0` dans l'onglet Paramètres — en connaissance de cause.

---

## ❓ Questions fréquentes

**Ça marche avec Spotify ?** Oui, ainsi qu'Apple Music, les navigateurs, VLC et
toute application qui alimente les contrôles média de Windows.

**Le serveur doit-il rester ouvert pendant le stream ?** Oui, mais la fenêtre
peut être réduite dans la barre des tâches.

**Le port 49450 est occupé.** L'application bascule automatiquement sur le port
libre suivant et vous indique la nouvelle URL.

**Je peux modifier un skin en direct ?** Oui : éditez son `skin.html`, puis
rafraîchissez la source navigateur dans OBS.

Le reste est dans [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

## 🤝 Contribution

Bugs, idées et pull requests sont les bienvenus — voir [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Licence

Projet open source, libre d'utilisation et de modification. Voir [LICENSE](LICENSE).

---

## 🤖 Vibe coding

Ce projet est développé en **vibe coding** avec [Claude Code](https://claude.ai/claude-code) :
la direction et les décisions sont humaines, l'implémentation est assistée par l'IA.

*Créé par [@dexteee-r](https://github.com/dexteee-r)*
