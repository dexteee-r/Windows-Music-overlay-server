# Changelog

Toutes les modifications notables du projet seront documentées dans ce fichier.

## [3.0.0] - 2025-12-23

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

### 📋 Migration depuis v2.0.0

1. **Sauvegarder** vos fichiers `config/*.json` actuels
2. **Supprimer** anciens fichiers obsolètes (voir section Supprimés)
3. **Copier** nouveaux fichiers de structure depuis v3.0.0
4. **Restaurer** votre configuration personnalisée dans nouveaux JSON
5. **Lancer** `launcher.pyw` pour tester
6. **Reconfigurer** démarrage auto si nécessaire (checkbox dans Paramètres)

---

## [2.0.0] - 2025-12-20

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

### Types de changements

- **Nouveautés** pour les nouvelles fonctionnalités
- **Améliorations** pour les changements dans les fonctionnalités existantes
- **Obsolète** pour les fonctionnalités bientôt supprimées
- **Supprimés** pour les fonctionnalités supprimées
- **Corrections** pour les corrections de bugs
- **Sécurité** en cas de vulnérabilités
