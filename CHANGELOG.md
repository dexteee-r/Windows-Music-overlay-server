# Changelog

Toutes les modifications notables du projet seront documentées dans ce fichier.

## [3.1.0] - 2026-08-27

### 🧹 Simplification de l'arborescence

52 fichiers suivis (hors skins) → 39, et deux dossiers en moins.

- ❌ **`requirements.txt`** : les dépendances étaient listées deux fois.
  `pyproject.toml` est désormais l'unique source ; l'installation se fait par
  `pip install -e .`
- ❌ **`config/*.json` ne sont plus suivis** : l'application les recrée au
  premier lancement. Vos réglages personnels n'apparaissent plus comme des
  modifications à commiter
- ❌ **`packaging/`** : la recette PyInstaller rejoint `scripts/` et son script
  d'entrée intermédiaire disparaît (elle pointe directement sur `launcher.pyw`)
- ❌ **`run_server.pyw`** : redondant avec `server.py` et
  `python -m music_overlay --console`
- ❌ **`scripts/start_gui.bat`** : n'existait que parce qu'une erreur de
  démarrage était invisible — le journal et la boîte d'erreur le remplacent
- ❌ **`application.py`** : `ServerRuntime.create()` et `run_console()` en
  reprennent le contenu
- 📦 **Paquet `server/` aplati** en un module unique `music_overlay/server.py`
- 📚 **`docs/` passe de 5 à 3 fichiers** : `DEMARRAGE.md` (installation et
  premier lancement), `GUIDE.md` (interface, filtres, configuration, API) et
  `TROUBLESHOOTING.md`

### ✨ Nouveautés

- 🖼️ **Aperçus complets** : `clipping_mask`, `kinetic_typography` et
  `retro_cassette` ont enfin leur `preview.png`. Les 10 skins ont désormais un
  aperçu dans l'onglet Skins.

---

## [3.0.1] - 2026-08-27

### 🐛 Corrections

- 🔌 **Ports réservés par Windows** : la recherche de port abandonnait après
  20 candidats, ce qui pouvait empêcher le démarrage sur une machine où
  Hyper-V, WSL ou une plage exclue condamne tout un bloc de ports. Le système
  attribue désormais un port en dernier recours.
- ⚙️ **Workflow de release** : le lancement manuel demande le tag à publier ;
  il produisait sinon des archives mal nommées et échouait à créer la release.

---

## [3.0.0] - 2026-08-27

### 🏗️ Refonte de l'architecture

Réorganisation complète du code autour d'un paquet `music_overlay/`. Aucune
action n'est requise : la configuration, les skins et les points d'entrée
(`launcher.pyw`, `server.py`) sont inchangés côté utilisateur.

- 📦 **Paquet `music_overlay/`** : `config`, `skins`, `media`, `server/`, `gui/`,
  `diagnostics`, `startup`. Le dossier `src/` et ses managers disparaissent.
- ♻️ **Fin des doublons** : la configuration et la liste des skins avaient deux
  implémentations concurrentes (serveur et GUI) avec des valeurs par défaut
  différentes ; il n'en reste qu'une, partagée.
- 📁 **Chemins absolus** : plus aucun `os.chdir()` ni chemin relatif. L'application
  fonctionne quel que soit le répertoire de lancement.
- 🧾 **Journalisation** : `logging` et fichier rotatif `logs/music-overlay.log`
  à la place des `print()`.
- 🧪 **Tests automatisés** : 75 tests (configuration, filtres, skins, API HTTP,
  cycle de vie du serveur) + `ruff` + CI GitHub Actions sur chaque push.

### ✨ Nouveautés

- 🔍 **Détection des applications** : bouton « Détecter les applications en cours »
  et route `GET /api/sources`. La saisie manuelle reste possible pour les lecteurs
  qui échappent à la détection, avec un bouton « Ouvrir la page source_app » et la
  marche à suivre affichée directement dans l'onglet Paramètres.
- 🩺 **Diagnostic intégré** : bouton dans la GUI, `scripts/diagnostic.bat` et
  `python -m music_overlay --diagnostic`.
- 📦 **Exécutable autonome** : `scripts/build_exe.bat` et publication automatique
  d'un `.exe` à chaque tag — l'utilisateur final n'installe plus Python.
- 🖱️ **`DEMARRER.bat`** : un seul double-clic, qui installe ce qui manque.
- 📋 **Bouton « Copier »** de l'URL de l'overlay, et route `GET /health`.
- 🎛️ **`python -m music_overlay`** avec les options `--console` et `--diagnostic`.

### 🐛 Corrections

- 🔴 **Le serveur redémarre vraiment** : « Arrêter » ne faisait que marquer le
  serveur comme arrêté sans libérer le port, et « Démarrer » ne repartait jamais.
  Le serveur passe par `werkzeug.make_server`, avec un arrêt réel.
- 🔌 **Port occupé** : bascule automatique sur le port libre suivant au lieu d'un
  échec au démarrage.
- ⚡ **Filtres appliqués immédiatement** : fermer et relancer l'application n'est
  plus nécessaire après un changement de filtre ou de skin.
- 🛡️ **Identifiants de skin validés** : `/api/set-skin/<id>` ne peut plus servir à
  remonter l'arborescence du disque.
- 🧯 **Erreurs visibles** : une erreur au démarrage affiche une boîte de dialogue
  au lieu d'échouer en silence dans une console invisible (`.pyw`).
- 🎨 **Skin manquant** : bascule sur un skin valide au lieu d'une page vide.
- 🔤 **Console Windows** : plus d'échec d'encodage sur les caractères accentués.
- ✏️ Dossier `skins/kynetic_typography/` renommé en `kinetic_typography/`.

### 🔒 Sécurité

- `flask-cors` passe de 4.0.0 à `>=5.0` (vulnérabilités connues sur la 4.0.0)
  et le partage CORS est restreint aux routes `/api/*`.
- Les identifiants de skin issus des URL sont strictement validés.

### 📚 Documentation

- README, `docs/` et `CONTRIBUTING.md` réécrits et alignés sur le code
  (l'API documentée ne correspondait plus aux routes réelles).
- `RELEASE_NOTES.md` fusionné dans ce changelog.

### ⚠️ Pour les contributeurs

- `src/` n'existe plus : importez depuis `music_overlay`.
- `server.py` n'expose plus de variables globales (`CONFIG`, `FILTER_CONFIG`,
  `current_track_info`) ; utilisez `ConfigStore`, `SkinRepository`, `MediaWatcher`.
- Le port par défaut est `49450` partout (le code annonçait encore `48952`).

---

## [2.1.0] - 2026-02-01

### ✨ Nouveautés

- 🔒 **Thread safety** : verrous sur les données partagées et arrêt propre des
  threads via `threading.Event()`.
- 🖼️ **Aperçu des skins** dans la GUI (image `preview.png` + métadonnées).
- 🎨 **6 nouveaux skins** : Modern Vinyl, Modern Vinyl V2, Liquid Capsule,
  Kinetic Typography, Clipping Mask, Streetwear Hypebeast (RGB Gamer retiré).

### 🚀 Performances

- Cache de la pochette (réencodée uniquement au changement de piste), du skin
  actif, de la liste des skins (TTL 60 s) et des images d'aperçu de la GUI.

---

## [2.0.0] - 2025-12-23

### 🎉 Version Complète avec GUI et System Tray

Version majeure intégrant une interface graphique complète, gestion du system tray, et restructuration professionnelle du projet.

### ✨ Nouveautés Majeures

#### Interface Graphique (GUI)
- 🖥️ **Application tkinter complète** avec 4 onglets :
  - **Skins** : Sélection et aperçu des 5 skins disponibles
  - **Paramètres** : Configuration serveur et filtres média
  - **Contrôle** : Gestion serveur avec logs en temps réel
  - **À propos** : Informations sur l'application
- 📏 **Fenêtre 900x700** redimensionnable pour afficher tous les contrôles
- 💾 **Sauvegarde en temps réel** de tous les paramètres

#### System Tray Integration
- 🔔 **Icône système** générée dynamiquement (Pillow)
- 📋 **Menu contextuel** :
  - Afficher/Masquer la fenêtre
  - Démarrer/Arrêter le serveur
  - Quitter l'application
- 🎯 **Notification** de l'état du serveur dans le tray

#### Gestion des Skins
- 🎨 **5 skins professionnels** organisés dans `skins/*/` :
  - Zen Minimalist
  - Neon Cyberpunk
  - Retro Cassette
  - RGB Gamer
  - Glassmorphism Frosted
- 🔄 **Changement à chaud** via GUI ou API
- 📄 **Métadonnées** (`info.json`) pour chaque skin
- 🌐 **API** : `GET /api/skins` et `POST /api/set-skin`

#### Démarrage Automatique
- 🚀 **Lancement au démarrage Windows** via dossier Startup
- ✅ **Checkbox dans GUI** pour activer/désactiver
- 🔗 **Raccourci automatique** créé dans `shell:startup`
- 📝 **Logs détaillés** de l'état du démarrage auto

#### Filtrage Média Avancé
- 🎯 **Gestion GUI des filtres** avec champs de texte multilignes
- ✏️ **Modification en direct** des listes allowed_apps/blocked_apps
- ⚠️ **Messages clairs** : redémarrage requis pour appliquer les changements
- 🔍 **3 modes** : all, whitelist, blacklist

#### Architecture Modulaire
- 📦 **Managers pattern** :
  - `ServerManager` : Gestion serveur Flask en thread
  - `SkinManager` : Gestion skins et configuration
  - `ConfigManager` : Chargement/sauvegarde JSON
  - `StartupManager` : Gestion démarrage Windows (shell:startup)
- 🔌 **Séparation GUI/logique** pour maintenabilité

#### Structure Professionnelle GitHub
- 📁 **Nouvelle organisation** :
  ```
  /config/          - Fichiers de configuration JSON
  /skins/*/         - Skins avec info.json et skin.html
  /src/             - Code source Python
  /docs/            - Documentation utilisateur
  /scripts/         - Scripts batch
  /assets/          - Ressources (icons, screenshots)
  ```
- 🗑️ **Nettoyage complet** : suppression des doublons et fichiers obsolètes
- 📋 **Documentation standardisée** : README, CONTRIBUTING, USAGE, CHANGELOG

### 📁 Fichiers Ajoutés

**Code Source**
- `launcher.pyw` - Point d'entrée sans console
- `src/gui.py` - Interface graphique principale
- `src/managers/server_manager.py` - Gestion serveur
- `src/managers/skin_manager.py` - Gestion skins
- `src/managers/config_manager.py` - Gestion configuration
- `src/managers/startup_manager.py` - Gestion démarrage auto
- `config/active_skin.json` - Skin actif sauvegardé

**Skins Organisés**
- `skins/zen_minimalist/info.json` + `skin.html`
- `skins/neon_cyberpunk/info.json` + `skin.html`
- `skins/retro_cassette/info.json` + `skin.html`
- `skins/rgb_gamer/info.json` + `skin.html`
- `skins/glassmorphism_frosted/info.json` + `skin.html`

**Documentation**
- `docs/USAGE.md` - Guide utilisateur complet (200+ lignes)
- `docs/QUICKSTART.md` - Guide de démarrage rapide
- `CONTRIBUTING.md` - Guide de contribution avec standards
- `.gitignore` - Configuration Git complète

**Scripts**
- `scripts/install.bat` - Installation automatique
- `scripts/start.bat` - Démarrage rapide

### 🔧 Fichiers Modifiés

- `server.py` - Support API skins + chargement skin actif
- `README.md` - Mise à jour complète avec nouvelles fonctionnalités
- `config/settings.json` - Port par défaut 49450
- `config/media_filter.json` - Configuration filtre avec exemples

### 🗑️ Fichiers Supprimés

**Nettoyage Obsolètes**
- `__pycache__/` (root et src/)
- `music_overlay_server.py` - Version obsolète
- `src/music_overlay_server.py` - Doublon
- `src/media_filter.py` - Non utilisé
- `src/config/` - Doublon de /config/
- `skins/skin - *.html` - Anciennes versions standalone (5 fichiers)
- `PROJECT_STRUCTURE.md` - Documentation obsolète
- `SUMMARY.md` - Documentation obsolète

### 🚀 Améliorations

**Expérience Utilisateur**
- ⚡ **Lancement simplifié** : double-clic sur launcher.pyw
- 🎛️ **Contrôle total** depuis GUI sans ligne de commande
- 📊 **Logs en temps réel** dans l'onglet Contrôle
- 🔄 **État serveur visible** : indicateur vert/rouge + URL affichée
- 🌐 **Bouton "Ouvrir dans navigateur"** pour tester overlay

**Robustesse**
- 🔒 **Gestion erreurs** : validation des ports, gestion imports manquants
- 💾 **Sauvegarde atomique** : fichiers JSON avec gestion d'erreurs
- 🧵 **Threading propre** : serveur Flask en daemon thread
- ⚠️ **Messages explicites** : instructions de redémarrage après changements

**Performance**
- 🚄 **Chargement optimisé** : configuration chargée une fois au démarrage
- 📦 **Imports conditionnels** : pystray, PIL importés uniquement si disponibles
- 🔄 **Rafraîchissement 500ms** : équilibre performance/réactivité

### 🐛 Corrections

- ✅ **Fix window size** : 900x700 pour afficher bouton "Enregistrer"
- ✅ **Fix .gitignore** : suppression règle incorrecte `src/`
- ✅ **Fix server.py restauré** : récupération depuis Git après suppression accidentelle
- ✅ **Fix skin change** : rechargement correct via active_skin.json
- ✅ **Fix startup** : utilisation shell:startup au lieu du registre
- ✅ **Fix port changes** : sauvegarde et rechargement corrects

### 📚 Documentation

- ✅ **USAGE.md** : Guide complet avec OBS, dépannage, raccourcis
- ✅ **CONTRIBUTING.md** : Standards de code, création de skins, workflow Git
- ✅ **QUICKSTART.md** : 5 étapes pour démarrer
- ✅ **README.md** : Présentation professionnelle avec screenshots
- ✅ **Commentaires JSON** : Tous les fichiers config documentés

### 🔒 Sécurité

- 🔐 **Local uniquement** : 127.0.0.1 par défaut (pas d'exposition réseau)
- 🛡️ **Port non-standard** : 49450 (évite conflits)
- 🚫 **Validation entrées** : filtrage des chemins et ports

### ⚠️ Breaking Changes

- 🔄 **Structure changée** : fichiers déplacés de root vers `src/`, `docs/`, `scripts/`
- 📦 **Skins organisés** : migration de `skins/skin-*.html` vers `skins/*/skin.html`
- ⚙️ **Démarrage auto** : shell:startup au lieu du registre (nécessite reconfiguration)
- 🚪 **Point d'entrée** : `launcher.pyw` au lieu de `gui.py` ou `server.py`

### 📋 Migration depuis v1.x

1. **Sauvegarder** vos fichiers `config/*.json` actuels
2. **Supprimer** anciens fichiers obsolètes (voir section Supprimés)
3. **Copier** nouveaux fichiers de structure depuis v2.0.0
4. **Restaurer** votre configuration personnalisée dans nouveaux JSON
5. **Lancer** `launcher.pyw` pour tester
6. **Reconfigurer** démarrage auto si nécessaire (checkbox dans Paramètres)

---

## [1.0.1] - 2025-12-20

### 🎉 Nouveautés Majeures

#### Architecture Professionnelle
- ✨ **Nouvelle structure de projet** avec dossiers `config/` et `src/`
- 📦 **Module de filtrage** dédié (`media_filter.py`)
- ⚙️ **Système de configuration JSON** flexible et modifiable à chaud

#### Système de Filtrage des Applications
- 🎯 **3 modes de filtrage** :
  - `whitelist` : Autoriser uniquement certaines applications
  - `blacklist` : Bloquer certaines applications
  - `allow_all` : Tout autoriser (mode par défaut)
- 🔍 **Identification automatique** de l'application source
- 💬 **Messages personnalisables** pour les applications bloquées

#### Configuration Flexible
- 🔧 **Port personnalisable** (défaut: 48952 au lieu de 5000)
- 🌐 **Host configurable** (local ou réseau)
- ⏱️ **Intervalle de mise à jour** ajustable
- 🔄 **Rechargement à chaud** de la configuration sans redémarrage

#### Nouvelles API
- 📊 `GET /api/filter-config` - Consulter la configuration du filtre
- 🔄 `POST /api/reload-config` - Recharger la configuration
- 📝 Champ `source_app` ajouté à `/api/current-track`

### 📁 Fichiers et Dossiers

#### Ajoutés
- `config/settings.json` - Configuration du serveur
- `config/media_filter.json` - Configuration du filtre média
- `src/music_overlay_server.py` - Serveur principal (nouvelle version)
- `src/media_filter.py` - Module de filtrage
- `src/__init__.py` - Package Python
- `CONFIGURATION.md` - Guide de configuration détaillé
- `CHANGELOG.md` - Ce fichier
- `.gitignore` - Fichiers à ignorer par Git

#### Modifiés
- `README.md` - Documentation complète mise à jour
- `install.bat` - Création automatique de la structure + config
- `start_server.bat` - Lancement depuis le dossier `src/`

#### Conservés (rétrocompatibilité)
- `music_overlay_server.py` - Ancienne version (root)
- `requirements.txt` - Dépendances Python inchangées

### 🔒 Sécurité

- 🛡️ **Port par défaut changé** : 48952 (plage privée) au lieu de 5000
- 🔐 **Filtrage des applications** pour contrôler les sources média
- 🏠 **Mode local par défaut** (127.0.0.1)

### 🚀 Améliorations

- 📝 **Messages de démarrage** plus informatifs avec configuration affichée
- 🎨 **Code mieux structuré** et modulaire
- 📖 **Documentation enrichie** avec exemples pratiques
- 🔧 **Installation simplifiée** avec scripts automatiques

### 🐛 Corrections

- Aucune - Version majeure avec refonte complète

### 📚 Documentation

- ✅ Guide de configuration détaillé (CONFIGURATION.md)
- ✅ README mis à jour avec tous les nouveaux paramètres
- ✅ Exemples d'utilisation du filtre média
- ✅ Section dépannage améliorée

---

## [1.0.0] - 2025-12-20 (Version initiale)

### Fonctionnalités Initiales

- 🎵 Affichage en temps réel des informations de lecture
- 🖼️ Support des pochettes d'album
- 📊 Barre de progression
- 🎨 Interface moderne avec animations
- 🎚️ Equalizer animé
- 🌐 API REST pour intégrations tierces
- 🔄 Mise à jour automatique (500ms)

### Architecture Initiale

- Serveur Flask sur port 5000
- Utilisation de Windows Media API (winrt)
- Fichier unique `music_overlay_server.py`
- Installation via `requirements.txt`

---

## Format du Changelog

Ce changelog suit le format [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versionnement Sémantique](https://semver.org/lang/fr/).

### Note sur la numérotation

Les entrées antérieures à la v2.1.0 ont été renumérotées pour correspondre aux
tags git réellement publiés (`v1.0.0`, `v1.0.1`, `v2.0.0` → `v2.0.2`, `v2.1.0`) :
le changelog et les tags divergeaient d'une version majeure.

### Types de changements

- **Nouveautés** pour les nouvelles fonctionnalités
- **Améliorations** pour les changements dans les fonctionnalités existantes
- **Obsolète** pour les fonctionnalités bientôt supprimées
- **Supprimés** pour les fonctionnalités supprimées
- **Corrections** pour les corrections de bugs
- **Sécurité** en cas de vulnérabilités
