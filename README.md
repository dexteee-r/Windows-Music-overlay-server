# 🎵 Music Overlay Server pour vos STREAM/LIVES/DIRECT

**Affiche en temps réel ce que vous écoutez sur votre machine**
Overlay web compatible avec OBS, Streamlabs et autres logiciels de streaming.

![Windows 11](https://img.shields.io/badge/Windows-11-blue)
![Python](https://img.shields.io/badge/Python-3.13+-green)
![License](https://img.shields.io/badge/License-Open%20Source-orange)

---

## 📖 Qu'est-ce que c'est ?

Music Overlay Server crée un serveur web local qui affiche en direct les informations de la musique que vous écoutez. Parfait pour les streamers qui veulent partager leurs morceaux préférés avec leur audience !

**Fonctionnalités :**
- 🖥️ **Interface graphique (GUI)** complète pour tout contrôler
- 🎨 **10 skins professionnels** avec preview intégrée
- 🖼️ Pochette d'album animée avec barre de progression
- 🎚️ Equalizer animé en temps réel
- 🎯 **Filtre média** : whitelist/blacklist d'applications
- 🔔 **System tray** : contrôle depuis la barre des tâches
- 🚀 **Démarrage automatique** au lancement de Windows
- ⚙️ Configuration simple via GUI (plus besoin d'éditer les fichiers)
- 🔒 Serveur local

---

## 🚀 Installation rapide

### 3 étapes simples :

1. **Installez Python 3.13+**
   👉 [Guide d'installation détaillé](docs/INSTALL.md)

2. **Double-cliquez sur `scripts/install.bat`**
   Installe toutes les dépendances automatiquement

3. **Double-cliquez sur `launcher.pyw`**
   Lance l'application avec interface graphique !

📺 **L'overlay sera accessible à** : `http://127.0.0.1:49450`

Pour un guide complet pas à pas avec captures, consultez [docs/INSTALL.md](docs/INSTALL.md) ou [docs/QUICKSTART.md](docs/QUICKSTART.md).

---

## 📁 Structure du projet

```
Windows-Music-overlay-server/
├── config/                   # Configuration JSON
│   ├── settings.json         # Port, host, intervalle
│   ├── media_filter.json     # Filtres média (whitelist/blacklist)
│   └── active_skin.json      # Skin actif
├── skins/                    # 10 skins professionnels
│   ├── zen_minimalist/
│   ├── neon_cyberpunk/
│   ├── retro_cassette/
│   ├── glassmorphism_frosted/
│   ├── modern_vinyl/
│   ├── modern_vinyl_v2/
│   ├── liquid_capsule/
│   ├── kinetic_typography/
│   ├── clipping_mask/
│   └── streetwear_hypebeast/
├── src/                      # Code source Python
│   ├── gui.py                # Interface graphique
│   ├── server_manager.py     # Gestion serveur
│   ├── skin_manager.py       # Gestion skins
│   ├── config_manager.py     # Gestion config
│   └── startup_manager.py    # Démarrage auto
├── scripts/                  # Scripts batch
│   ├── install.bat           # Installation automatique
│   └── start.bat             # Démarrage serveur seul
├── docs/                     # Documentation
│   ├── USAGE.md              # Guide utilisateur complet
│   ├── QUICKSTART.md         # Démarrage rapide
│   └── INSTALL.md            # Installation détaillée
├── launcher.pyw              # 🚀 Point d'entrée (GUI)
├── server.py                 # Serveur Flask
└── requirements.txt          # Dépendances Python
```

---

## 🎮 Utilisation

### Démarrage de l'Application

Double-cliquez sur **`launcher.pyw`** à la racine du projet.

**L'interface graphique s'ouvre avec 4 onglets :**

1. **🎨 Skins** - Sélectionnez parmi 5 skins professionnels
2. **⚙️ Paramètres** - Configurez le port, host, filtres média
3. **🎛️ Contrôle** - Démarrez/Arrêtez le serveur, consultez les logs
4. **ℹ️ À propos** - Informations sur l'application

### Démarrer le Serveur

1. Ouvrez l'onglet **Contrôle**
2. Cliquez sur **"Démarrer le serveur"**
3. Le statut passe au vert avec l'URL : `http://127.0.0.1:49450`

**Vous pouvez maintenant :**
- ✅ Minimiser la fenêtre (l'app reste dans le system tray)
- ✅ Configurer le démarrage automatique dans l'onglet Paramètres
- ✅ Changer de skin à chaud dans l'onglet Skins

### Dans OBS Studio

1. **Ajoutez une source** → Navigateur
2. **URL** : `http://127.0.0.1:49450` (ou l'URL affichée dans l'onglet Contrôle)
3. **Dimensions recommandées** :
   - Largeur : **600 - 650 px**
   - Hauteur : **150 - 180 px**
4. ✅ Cochez "Rafraîchir le navigateur lorsque la scène devient active"

💡 **Astuce** : Ajustez les dimensions selon le skin choisi pour un rendu optimal

### Menu System Tray

L'icône dans la barre des tâches permet de :
- 👁️ Afficher/Masquer la fenêtre
- ▶️ Démarrer le serveur
- ⏹️ Arrêter le serveur
- ❌ Quitter l'application

---

## ⚙️ Configuration

### Via l'Interface Graphique (Recommandé)

Ouvrez l'onglet **Paramètres** dans l'application pour configurer :

**Serveur :**
- 🔌 **Port** : Port du serveur (défaut: 49450)
- 🌐 **Host** : `127.0.0.1` = local uniquement
- ⏱️ **Intervalle de rafraîchissement** : Mise à jour en secondes

**Filtres Média :**
- 🎯 **Mode** : all / whitelist / blacklist
- ✅ **Applications autorisées** : Liste d'apps (une par ligne)
- ❌ **Applications bloquées** : Liste d'apps à ignorer

**Démarrage :**
- 🚀 **Démarrer automatiquement avec Windows** : Case à cocher

⚠️ **Important** : Après avoir modifié les filtres, il faut :
1. Arrêter le serveur
2. Fermer l'application
3. Relancer l'application

### Via les Fichiers JSON (Avancé)

Vous pouvez aussi éditer directement les fichiers dans `config/` :

**`config/settings.json`** - Configuration serveur
```json
{
  "port": 49450,
  "host": "127.0.0.1",
  "refresh_interval": 0.5
}
```

**`config/media_filter.json`** - Filtres média
```json
{
  "mode": "whitelist",
  "allowed_apps": [
    "AppleInc.AppleMusicWin_nzyj5cx40ttqa!App"
  ],
  "blocked_apps": []
}
```

**Modes disponibles :**
- `all` : Toutes les apps (sauf `blocked_apps`)
- `whitelist` : Uniquement les apps dans `allowed_apps`
- `blacklist` : Toutes sauf celles dans `blocked_apps`

### Trouver le nom d'une application

1. Changez le mode à `all` dans l'onglet Paramètres
2. Lancez l'application (ex: Spotify)
3. Jouez une musique
4. Cliquez sur **"Ouvrir dans navigateur"** dans l'onglet Contrôle
5. Allez sur `/api/current-track`
6. Regardez `"source_app"` dans le JSON
7. Ajoutez ce nom dans la liste appropriée

---

## 🎨 Skins Disponibles

L'application inclut **10 skins professionnels** que vous pouvez changer à la volée avec **preview intégrée** :

| Skin | Style | Description |
|------|-------|-------------|
| **Zen Minimalist** | Minimaliste | Design épuré, focus sur l'essentiel |
| **Neon Cyberpunk** | Futuriste | Néons roses/bleus, style cyberpunk |
| **Retro Cassette** | Vintage | Look cassette années 80-90 |
| **Glassmorphism Frosted** | Moderne | Effet verre dépoli (glassmorphism) |
| **Modern Vinyl** | Vinyle | Disque vinyle avec pochette rotative |
| **Modern Vinyl V2** | Vinyle | Version améliorée du vinyle |
| **Liquid Capsule** | Fluide | Design capsule avec effets liquides |
| **Kinetic Typography** | Typographie | Focus sur le texte animé |
| **Clipping Mask** | Artistique | Effet de masque d'écrêtage |
| **Streetwear Hypebeast** | Urbain | Style streetwear moderne |

**Pour changer de skin :**
1. Ouvrez l'onglet **Skins** dans l'application
2. Sélectionnez un skin pour voir l'**aperçu** (métadonnées + screenshot)
3. Cliquez sur **"Appliquer le skin sélectionné"**
4. Le skin change immédiatement (pas besoin de redémarrer)

**Pour créer votre propre skin :**
Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour le guide complet avec template HTML/CSS.

---

## 📊 API JSON

### Endpoint : `/api/current-track`

**URL** : `http://127.0.0.1:49450/api/current-track`

**Exemple de réponse :**
```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "thumbnail": "data:image/jpeg;base64,...",
  "is_playing": true,
  "position": 45,
  "duration": 180,
  "source_app": "AppleInc.AppleMusicWin_nzyj5cx40ttqa!App"
}
```

### Autres endpoints

- `GET /api/skins` - Liste des skins disponibles
- `POST /api/set-skin` - Changer de skin (body: `{"skin_id": "neon_cyberpunk"}`)
- `GET /api/list-skins` - Métadonnées complètes des skins

Parfait pour créer vos propres intégrations !

---

## 🔧 Dépannage

### ❌ "Python n'est pas reconnu..."
**Solution** : Réinstallez Python en cochant **"Add python.exe to PATH"**
👉 Consultez [docs/INSTALL.md](docs/INSTALL.md)

### ❌ L'application ne se lance pas (`launcher.pyw`)
**Vérifiez** :
1. Python 3.13+ est installé : `python --version` dans CMD
2. Dépendances installées : relancez `scripts/install.bat`
3. Vérifiez les logs dans l'onglet Contrôle

### ❌ "Le port est déjà utilisé"
**Solution via GUI** :
1. Ouvrez l'onglet **Paramètres**
2. Changez le **Port** (ex: 49500, 50000, etc.)
3. Cliquez sur **"Enregistrer les paramètres"**
4. Redémarrez le serveur

### ❌ "No track playing" même avec Apple Music ouvert
**Vérifiez dans l'onglet Paramètres** :
- Apple Music est ouvert et joue une musique
- Le **Mode de filtre** autorise Apple Music
- `AppleInc.AppleMusicWin_nzyj5cx40ttqa!App` est dans **Applications autorisées** (si mode whitelist)

### ❌ Les changements de configuration ne s'appliquent pas
**Solution** :
1. Arrêtez le serveur (bouton "Arrêter le serveur")
2. Fermez complètement l'application
3. Relancez `launcher.pyw`
4. Démarrez le serveur

### ❌ La pochette d'album ne s'affiche pas
C'est normal si Apple Music ne fournit pas la pochette. Une icône par défaut sera affichée.

### ❌ L'icône system tray n'apparaît pas
**Solution** :
1. Vérifiez que `pystray` et `Pillow` sont installés : relancez `scripts/install.bat`
2. Relancez l'application

### 📚 Plus d'aide
Consultez le guide complet : [docs/USAGE.md](docs/USAGE.md)

---

## 🛡️ Sécurité

Le serveur est configuré pour être **local uniquement** par défaut :
- ✅ Accessible uniquement depuis votre PC (127.0.0.1)
- ✅ NON accessible depuis Internet
- ✅ NON accessible depuis d'autres appareils
- ✅ Données privées et sécurisées

### Accès réseau local (optionnel)

Pour accéder depuis un autre appareil (tablette, téléphone, etc.) :

1. Ouvrez `config/settings.json`
2. Changez `"host": "127.0.0.1"` en `"host": "0.0.0.0"`
3. Redémarrez le serveur
4. Accédez via : `http://[IP-de-votre-PC]:48952`

⚠️ **Attention** : Cela rendra le serveur accessible à tous les appareils sur votre réseau local.

---

## 📝 FAQ

**Q : Est-ce que ça marche avec Spotify ?**
R : Oui ! Ajoutez l'ID de Spotify dans `allowed_apps`. Pour le trouver, voir la section "Comment trouver le nom d'une application".

**Q : Puis-je changer l'apparence de l'overlay ?**
R : Oui, éditez le template HTML dans `server.py` (section `OVERLAY_HTML`).

**Q : Le serveur doit rester actif pendant le stream ?**
R : Oui, laissez la fenêtre ouverte pendant toute la durée de votre stream.

**Q : Puis-je utiliser un autre port ?**
R : Oui, modifiez `"port"` dans `config/settings.json`. Utilisez un port entre 49152 et 65535.

**Q : Comment bloquer YouTube mais autoriser le reste ?**
R : Utilisez le mode `"blacklist"` et ajoutez `"chrome.exe"`, `"firefox.exe"` dans `blocked_apps`.

---

## 🎯 Exemples de configuration

### Cas 1 : Autoriser uniquement Apple Music

```json
{
  "mode": "whitelist",
  "allowed_apps": [
    "AppleInc.AppleMusicWin_nzyj5cx40ttqa!App"
  ],
  "blocked_apps": []
}
```

### Cas 2 : Bloquer les navigateurs (YouTube, etc.)

```json
{
  "mode": "blacklist",
  "allowed_apps": [],
  "blocked_apps": [
    "chrome.exe",
    "firefox.exe",
    "msedge.exe",
    "brave.exe"
  ]
}
```

### Cas 3 : Autoriser Apple Music et Spotify

```json
{
  "mode": "whitelist",
  "allowed_apps": [
    "AppleInc.AppleMusicWin_nzyj5cx40ttqa!App",
    "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"
  ],
  "blocked_apps": []
}
```

---

## 📄 Licence

Projet open source - Libre d'utilisation et de modification.

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Créer des pull requests

---

## 📞 Support

**Problème non résolu ?**
1. Consultez [INSTALL.md](INSTALL.md)
2. Relisez la section "Dépannage" ci-dessus
3. Ouvrez un Issue sur GitHub avec :
   - Version de Windows
   - Version de Python (`python --version`)
   - Message d'erreur complet

---

**Bon streaming !** 🎵🎬

---

## 🤖 Vibe Coding

Ce projet a été réalisé en **vibe coding** avec [Claude Code](https://claude.ai/claude-code) (Claude Opus 4.5).

Le vibe coding est une approche de développement collaborative où l'humain guide la direction créative et les décisions, tandis que l'IA assiste dans l'implémentation technique, la résolution de problèmes et l'optimisation du code.

---

*Créé par [@dexteee-r](https://github.com/dexteee-r) - Version 2.0.0*
