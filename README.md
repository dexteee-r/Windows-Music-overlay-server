# 🎵 Overlay Musical Apple Music pour Windows 11

Un overlay musical en temps réel qui affiche ce que vous écoutez sur Apple Music, accessible via HTTP pour une intégration dans OBS ou autres logiciels de streaming.

## ✨ Fonctionnalités

- 🎨 Design moderne et élégant avec animations
- 🖼️ Affichage de la pochette d'album
- 📊 Barre de progression en temps réel
- ⏱️ Temps écoulé et durée totale
- 🎚️ Equalizer animé
- 🔄 Mise à jour automatique toutes les 500ms
- 🌐 Accessible via HTTP (parfait pour OBS)
- 🎯 **Système de filtrage des applications média** (whitelist/blacklist)
- ⚙️ **Configuration flexible** via fichiers JSON
- 🔒 **Port personnalisable** (par défaut: 48952)

## 📋 Prérequis

- Windows 11
- Python 3.8 ou supérieur
- Apple Music installé et en cours d'exécution
- Connexion Internet (pour l'installation des dépendances)

## 📁 Structure du Projet

```
music-overlay-server/
├── config/
│   ├── settings.json          # Configuration du serveur (port, host)
│   └── media_filter.json      # Filtre des applications média
├── src/
│   ├── music_overlay_server.py # Serveur principal
│   └── media_filter.py         # Module de filtrage
├── requirements.txt
├── README.md
├── LICENSE
├── install.bat                 # Script d'installation automatique
└── start_server.bat           # Script de démarrage
```

## 🚀 Installation

### Méthode 1 : Installation Automatique (Recommandé)

1. Double-cliquez sur `install.bat`
2. Le script va automatiquement :
   - Créer la structure des dossiers
   - Générer les fichiers de configuration
   - Installer toutes les dépendances Python

### Méthode 2 : Installation Manuelle

#### Étape 1 : Installer Python

Si Python n'est pas déjà installé :
1. Téléchargez Python depuis https://www.python.org/downloads/
2. Cochez "Add Python to PATH" lors de l'installation
3. Installez Python

#### Étape 2 : Installer les dépendances

Ouvrez PowerShell ou l'Invite de commandes dans le dossier du projet et exécutez :

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 🎮 Utilisation

### Démarrer le serveur

#### Méthode 1 : Avec le script (Recommandé)
Double-cliquez sur `start_server.bat`

#### Méthode 2 : Manuellement
```bash
cd src
python music_overlay_server.py
```

Le serveur va démarrer et afficher :
```
======================================================================
🎵 Music Overlay Server Started!
======================================================================

📺 Overlay URL: http://127.0.0.1:48952
📊 API URL: http://127.0.0.1:48952/api/current-track
⚙️  Filter Config: http://127.0.0.1:48952/api/filter-config

🔒 Server: 127.0.0.1:48952 (LOCAL only)
🎯 Filter Mode: whitelist
ℹ️  Open the overlay URL in OBS Browser Source
======================================================================
```

### Accéder à l'overlay

#### Dans un navigateur web
- Ouvrez : `http://127.0.0.1:48952`

#### Dans OBS Studio
1. Ajoutez une source "Navigateur"
2. URL : `http://127.0.0.1:48952`
3. Largeur : 600
4. Hauteur : 150
5. Cochez "Rafraîchir le navigateur lorsque la scène devient active"

### Accéder aux données JSON (API)

Pour intégrer dans vos propres applications, plusieurs endpoints sont disponibles :

#### 1. Informations de la piste actuelle
- URL : `http://127.0.0.1:48952/api/current-track`
- Méthode : GET
- Format : JSON

Exemple de réponse :
```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "thumbnail": "data:image/jpeg;base64,...",
  "is_playing": true,
  "position": 45,
  "duration": 180,
  "source_app": "Music.UI.exe"
}
```

#### 2. Configuration du filtre média
- URL : `http://127.0.0.1:48952/api/filter-config`
- Méthode : GET
- Format : JSON

Exemple de réponse :
```json
{
  "mode": "whitelist",
  "allowed_apps": ["Music.UI.exe", "AppleMusic.exe"],
  "blocked_apps": [],
  "config_path": "C:\\...\\config\\media_filter.json"
}
```

#### 3. Recharger la configuration
- URL : `http://127.0.0.1:48952/api/reload-config`
- Méthode : POST
- Format : JSON

Permet de recharger les fichiers de configuration sans redémarrer le serveur.

## ⚙️ Configuration

Le serveur est maintenant entièrement configurable via des fichiers JSON.

### 1. Configuration du Serveur (`config/settings.json`)

```json
{
  "server": {
    "host": "127.0.0.1",    // Adresse du serveur (127.0.0.1 = local uniquement)
    "port": 48952            // Port du serveur (48952 par défaut)
  },
  "update_interval": 0.5     // Intervalle de mise à jour en secondes
}
```

**Changer le port :**
1. Ouvrez `config/settings.json`
2. Modifiez la valeur de `port`
3. Redémarrez le serveur

### 2. Filtrage des Applications Média (`config/media_filter.json`)

Le système de filtrage permet de contrôler quelles applications peuvent afficher leurs informations dans l'overlay.

```json
{
  "mode": "whitelist",           // Mode de filtrage: "whitelist", "blacklist", ou "allow_all"
  "allowed_apps": [              // Applications autorisées (mode whitelist)
    "Music.UI.exe",
    "AppleMusic.exe"
  ],
  "blocked_apps": [],            // Applications bloquées (mode blacklist)
  "default_message": {           // Message affiché si l'application est bloquée
    "title": "No track playing",
    "artist": "Unknown",
    "album": ""
  }
}
```

#### Modes de filtrage disponibles :

1. **`whitelist`** (recommandé) : Seules les applications listées dans `allowed_apps` sont autorisées
   - Utilisez ce mode pour autoriser uniquement Apple Music
   - Exemple : `["Music.UI.exe", "AppleMusic.exe"]`

2. **`blacklist`** : Toutes les applications sont autorisées sauf celles dans `blocked_apps`
   - Utilisez ce mode pour bloquer des applications spécifiques (YouTube, Spotify, etc.)
   - Exemple : `["chrome.exe", "firefox.exe", "spotify.exe"]`

3. **`allow_all`** : Toutes les applications sont autorisées
   - Pas de filtrage, toutes les sources média sont affichées

#### Identifier le nom d'une application :

Pour trouver le nom exact d'une application :
1. Lancez le serveur en mode `allow_all`
2. Ouvrez l'URL : `http://127.0.0.1:48952/api/current-track`
3. Regardez le champ `source_app` dans la réponse JSON
4. Ajoutez ce nom dans `allowed_apps` ou `blocked_apps`

#### Recharger la configuration sans redémarrer :

```bash
curl -X POST http://127.0.0.1:48952/api/reload-config
```

Ou visitez cette URL dans votre navigateur (configurez un raccourci).

### 3. Personnalisation Visuelle

Vous pouvez modifier l'apparence de l'overlay en éditant le code HTML/CSS dans [src/music_overlay_server.py](src/music_overlay_server.py) :

- **Couleurs** : Modifiez les valeurs dans les `linear-gradient`
- **Taille** : Ajustez `max-width` de `.music-widget`
- **Animations** : Modifiez les `@keyframes`
- **Police** : Changez `font-family`

## 🔧 Dépannage

### Le serveur ne démarre pas
- Vérifiez que le port 48952 n'est pas déjà utilisé par un autre programme
- Changez le port dans `config/settings.json` si nécessaire
- Vérifiez que Python est correctement installé : `python --version`

### Aucune information n'apparaît
- Vérifiez qu'Apple Music est bien ouvert
- Lancez une musique dans Apple Music
- Vérifiez le mode de filtrage dans `config/media_filter.json`
- Si vous utilisez le mode `whitelist`, assurez-vous que `Music.UI.exe` est dans `allowed_apps`
- Consultez l'API pour voir l'application source : `http://127.0.0.1:48952/api/current-track`

### Le filtre ne fonctionne pas
1. Vérifiez la syntaxe JSON dans `config/media_filter.json`
2. Les noms d'applications sont sensibles à la casse mais convertis en minuscules
3. Rechargez la configuration : `POST http://127.0.0.1:48952/api/reload-config`
4. Consultez la configuration actuelle : `GET http://127.0.0.1:48952/api/filter-config`

### Identifier l'application qui joue de la musique
1. Mettez le mode sur `"allow_all"` dans `config/media_filter.json`
2. Lancez une musique
3. Visitez : `http://127.0.0.1:48952/api/current-track`
4. Regardez le champ `"source_app"` pour voir le nom exact de l'application
5. Ajoutez ce nom dans la whitelist ou blacklist selon vos besoins

### Erreur lors de l'installation des dépendances
Si vous avez des erreurs avec les anciens packages (comme winsdk), utilisez :
```bash
pip uninstall winsdk -y
pip install -r requirements.txt
```

Les nouveaux packages `winrt-*` sont précompilés et ne nécessitent **PAS** Visual Studio.

### L'image de la pochette ne s'affiche pas
- C'est normal si Apple Music ne fournit pas la pochette
- Une icône par défaut sera affichée

### Conflits de port
Le port par défaut (48952) est choisi dans la plage des ports dynamiques/privés (49152-65535) pour minimiser les conflits. Si vous rencontrez quand même un conflit :
1. Ouvrez `config/settings.json`
2. Changez `"port"` vers un autre numéro (ex: 49500, 50000, etc.)
3. Redémarrez le serveur
4. Mettez à jour l'URL dans OBS avec le nouveau port

## 🔒 Sécurité

Le serveur est configuré pour être **strictement local** par défaut :
- ✅ Accessible uniquement depuis votre PC (127.0.0.1)
- ✅ NON accessible depuis Internet
- ✅ NON accessible depuis d'autres appareils sur votre réseau local
- ✅ Données privées et sécurisées
- ✅ Filtrage des applications média pour contrôler les sources autorisées

### Accès réseau local (optionnel)

Si vous souhaitez accéder au serveur depuis un autre appareil sur votre réseau (tablette, téléphone, autre PC) :
1. Ouvrez `config/settings.json`
2. Modifiez `"host": "127.0.0.1"` en `"host": "0.0.0.0"`
3. Redémarrez le serveur
4. Accédez depuis un autre appareil avec : `http://[IP-de-votre-PC]:48952`

⚠️ **Attention** : Cela rendra le serveur accessible à tous les appareils sur votre réseau local.

## 📝 Notes

- Le serveur doit rester actif pour que l'overlay fonctionne
- L'overlay se met à jour automatiquement (configurable via `update_interval`)
- Compatible avec tous les logiciels supportant les sources web (OBS, Streamlabs, etc.)
- Les fichiers de configuration peuvent être modifiés à chaud et rechargés via l'API
- Le port 48952 est dans la plage des ports privés/dynamiques pour éviter les conflits

## 🎯 Exemples d'utilisation du filtre

### Cas 1 : Autoriser uniquement Apple Music
```json
{
  "mode": "whitelist",
  "allowed_apps": ["Music.UI.exe", "Apple Music.exe"],
  "blocked_apps": []
}
```

### Cas 2 : Bloquer YouTube et Spotify
```json
{
  "mode": "blacklist",
  "allowed_apps": [],
  "blocked_apps": ["chrome.exe", "firefox.exe", "spotify.exe"]
}
```

### Cas 3 : Tout autoriser
```json
{
  "mode": "allow_all",
  "allowed_apps": [],
  "blocked_apps": []
}
```

## 🐛 Problèmes connus

- Parfois, au démarrage d'Apple Music, il peut falloir quelques secondes pour que les informations apparaissent
- La rotation de la pochette d'album ne fonctionne que lorsque la musique est en lecture
- Certaines applications média peuvent avoir des noms différents selon la version de Windows

## 📄 Licence

Projet open source - Libre d'utilisation et de modification

## 🤝 Support

Si vous rencontrez des problèmes, vérifiez :
1. Que Python est correctement installé
2. Que toutes les dépendances sont installées
3. Qu'Apple Music est ouvert et en cours de lecture
4. Que le pare-feu Windows autorise le serveur