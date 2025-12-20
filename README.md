# 🎵 Music Overlay Server pour Apple Music

**Affiche en temps réel ce que vous écoutez sur Apple Music**
Overlay web compatible avec OBS, Streamlabs et autres logiciels de streaming.

![Windows 11](https://img.shields.io/badge/Windows-11-blue)
![Python](https://img.shields.io/badge/Python-3.13+-green)
![License](https://img.shields.io/badge/License-Open%20Source-orange)

---

## 📖 Qu'est-ce que c'est ?

Music Overlay Server crée un serveur web local qui affiche en direct les informations de la musique que vous écoutez sur Apple Music. Parfait pour les streamers qui veulent partager leurs morceaux préférés avec leur audience !

**Fonctionnalités :**
- 🎨 Interface moderne et élégante
- 🖼️ Pochette d'album animée
- 📊 Barre de progression en temps réel
- 🎚️ Equalizer animé
- 🎯 Filtre personnalisable (bloquer certaines apps)
- ⚙️ Configuration simple (fichiers JSON)
- 🔒 Serveur local sécurisé

---

## 🚀 Installation rapide

### 3 étapes simples :

1. **Installez Python 3.13+**
   👉 [Guide d'installation détaillé](INSTALL.md)

2. **Double-cliquez sur `install.bat`**
   Installe toutes les dépendances automatiquement

3. **Double-cliquez sur `start.bat`**
   Lance le serveur !

📺 **Visitez** : `http://127.0.0.1:48952`

Pour un guide complet pas à pas avec captures, consultez [INSTALL.md](INSTALL.md).

---

## 📁 Structure du projet

```
music-overlay-server/
├── config/
│   ├── settings.json         # Port, host, intervalle de rafraîchissement
│   └── media_filter.json     # Applications autorisées/bloquées
├── server.py                 # Fichier principal (tout-en-un)
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
├── INSTALL.md                # Guide d'installation détaillé
├── install.bat               # Installation automatique
└── start.bat                 # Démarrage du serveur
```

---

## 🎮 Utilisation

### Démarrage

Double-cliquez sur **`start.bat`**

Le serveur affiche :
```
======================================================================
🎵 MUSIC OVERLAY SERVER - APPLE MUSIC
======================================================================

📺 URL de l'overlay : http://127.0.0.1:48952
📊 API JSON         : http://127.0.0.1:48952/api/current-track
```

**Laissez cette fenêtre ouverte** pendant que vous streamez.

### Dans OBS Studio

1. **Ajoutez une source** → Navigateur
2. **URL** : `http://127.0.0.1:48952`
3. **Dimensions** : 600 x 150
4. ✅ Cochez "Rafraîchir le navigateur lorsque la scène devient active"

---

## ⚙️ Configuration

Tous les paramètres sont dans le dossier `config/`.

### 1. Configuration du serveur (`config/settings.json`)

```json
{
  "port": 48952,
  "host": "127.0.0.1",
  "refresh_interval": 0.5
}
```

**Paramètres :**
- `port` : Port du serveur (49152-65535 recommandé)
- `host` : `127.0.0.1` = local uniquement | `0.0.0.0` = accessible réseau
- `refresh_interval` : Intervalle de mise à jour en secondes

### 2. Filtre des applications (`config/media_filter.json`)

```json
{
  "mode": "whitelist",
  "allowed_apps": [
    "AppleInc.AppleMusicWin_nzyj5cx40ttqa!App"
  ],
  "blocked_apps": [
    "brave.exe",
    "chrome.exe"
  ]
}
```

**Modes disponibles :**

| Mode | Description |
|------|-------------|
| `all` | Accepter toutes les apps (sauf celles dans `blocked_apps`) |
| `whitelist` | Accepter UNIQUEMENT les apps dans `allowed_apps` |
| `blacklist` | Accepter toutes SAUF celles dans `blocked_apps` |

### Comment trouver le nom d'une application ?

1. Mettez `"mode": "all"` dans `config/media_filter.json`
2. Lancez l'application (ex: Spotify)
3. Jouez une musique
4. Visitez : `http://127.0.0.1:48952/api/current-track`
5. Regardez le champ `"source_app"`
6. Copiez ce nom dans `allowed_apps` ou `blocked_apps`

### Recharger la configuration sans redémarrer

Visitez : `http://127.0.0.1:48952/api/reload-config`

---

## 📊 API JSON

### Endpoint : `/api/current-track`

**URL** : `http://127.0.0.1:48952/api/current-track`

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

Parfait pour créer vos propres intégrations !

---

## 🔧 Dépannage

### ❌ "Python n'est pas reconnu..."
**Solution** : Réinstallez Python en cochant **"Add python.exe to PATH"**

### ❌ "Le port 48952 est déjà utilisé"
**Solution** :
1. Ouvrez `config/settings.json`
2. Changez `"port": 48952` vers `"port": 49500`
3. Redémarrez le serveur

### ❌ "No track playing" même avec Apple Music ouvert
**Vérifiez que** :
- Apple Music est ouvert et joue une musique
- Le filtre autorise Apple Music (`config/media_filter.json`)
- L'ID de l'app dans `allowed_apps` correspond (voir "Comment trouver le nom d'une application")

### ❌ La pochette d'album ne s'affiche pas
C'est normal si Apple Music ne fournit pas la pochette. Une icône par défaut sera affichée.

### ❌ Le serveur ne démarre pas
**Vérifiez** :
1. Python est installé : `python --version` dans CMD
2. Dépendances installées : relancez `install.bat`
3. Aucun antivirus ne bloque `server.py`

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

*Créé par [@dexteee-r](https://github.com/dexteee-r) - Version 2.0.0*
