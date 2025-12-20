# Changelog

Toutes les modifications notables du projet seront documentées dans ce fichier.

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
