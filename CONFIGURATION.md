# Guide de Configuration - Music Overlay Server

## 📋 Table des Matières

1. [Configuration Rapide](#configuration-rapide)
2. [Configuration du Serveur](#configuration-du-serveur)
3. [Configuration du Filtre Média](#configuration-du-filtre-média)
4. [API Endpoints](#api-endpoints)
5. [Exemples Pratiques](#exemples-pratiques)

---

## Configuration Rapide

### Démarrage en 3 étapes

1. **Installation** : Double-cliquez sur `install.bat`
2. **Configuration** (optionnel) : Éditez les fichiers dans `config/`
3. **Démarrage** : Double-cliquez sur `start_server.bat`

📺 URL de l'overlay : `http://127.0.0.1:48952`

---

## Configuration du Serveur

**Fichier** : `config/settings.json`

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 48952
  },
  "update_interval": 0.5
}
```

### Paramètres disponibles :

| Paramètre | Type | Description | Valeur par défaut |
|-----------|------|-------------|-------------------|
| `server.host` | string | Adresse IP du serveur | `"127.0.0.1"` |
| `server.port` | number | Port d'écoute | `48952` |
| `update_interval` | number | Intervalle de mise à jour (secondes) | `0.5` |

### Exemples de configuration :

#### Serveur local uniquement
```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 48952
  }
}
```

#### Accessible sur le réseau local
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 48952
  }
}
```

#### Port personnalisé
```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 50000
  }
}
```

---

## Configuration du Filtre Média

**Fichier** : `config/media_filter.json`

```json
{
  "mode": "whitelist",
  "allowed_apps": [
    "Music.UI.exe",
    "AppleMusic.exe"
  ],
  "blocked_apps": [],
  "default_message": {
    "title": "No track playing",
    "artist": "Unknown",
    "album": ""
  }
}
```

### Modes de filtrage

#### 1. Mode Whitelist (Liste Blanche)
✅ **Recommandé** - Seules les applications autorisées sont affichées

```json
{
  "mode": "whitelist",
  "allowed_apps": [
    "Music.UI.exe",
    "AppleMusic.exe"
  ]
}
```

**Cas d'usage** :
- Vous voulez afficher uniquement Apple Music
- Vous voulez bloquer YouTube, Spotify, etc.
- Contrôle strict des sources média

#### 2. Mode Blacklist (Liste Noire)
🚫 Toutes les applications sont autorisées sauf celles bloquées

```json
{
  "mode": "blacklist",
  "blocked_apps": [
    "chrome.exe",
    "firefox.exe",
    "spotify.exe"
  ]
}
```

**Cas d'usage** :
- Vous voulez bloquer quelques applications spécifiques
- Vous voulez autoriser la plupart des applications média

#### 3. Mode Allow All (Tout Autoriser)
🌐 Aucun filtrage - toutes les applications sont autorisées

```json
{
  "mode": "allow_all",
  "allowed_apps": [],
  "blocked_apps": []
}
```

**Cas d'usage** :
- Test et développement
- Identifier les noms d'applications
- Afficher n'importe quelle source média

### Identifier les noms d'applications

**Méthode 1 : Via l'API**
1. Configurez le mode `"allow_all"`
2. Lancez une musique depuis l'application
3. Visitez : `http://127.0.0.1:48952/api/current-track`
4. Regardez le champ `"source_app"`

**Méthode 2 : Noms courants**
- Apple Music (Windows 11) : `Music.UI.exe` ou `Apple Music.exe`
- Spotify : `Spotify.exe`
- YouTube (Chrome) : `chrome.exe`
- YouTube (Firefox) : `firefox.exe`
- VLC : `vlc.exe`
- Windows Media Player : `wmplayer.exe`

### Message par défaut

Personnalisez le message affiché quand une application est bloquée :

```json
{
  "default_message": {
    "title": "🎵 Musique non autorisée",
    "artist": "Source bloquée",
    "album": "Utilisez Apple Music"
  }
}
```

---

## API Endpoints

### 1. Obtenir la piste actuelle
```http
GET http://127.0.0.1:48952/api/current-track
```

**Réponse** :
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

### 2. Obtenir la configuration du filtre
```http
GET http://127.0.0.1:48952/api/filter-config
```

**Réponse** :
```json
{
  "mode": "whitelist",
  "allowed_apps": ["music.ui.exe", "applemusic.exe"],
  "blocked_apps": [],
  "config_path": "C:\\...\\config\\media_filter.json"
}
```

### 3. Recharger la configuration
```http
POST http://127.0.0.1:48952/api/reload-config
```

**Réponse** :
```json
{
  "success": true,
  "message": "Configuration reloaded"
}
```

**Usage avec curl** :
```bash
curl -X POST http://127.0.0.1:48952/api/reload-config
```

---

## Exemples Pratiques

### Exemple 1 : Apple Music uniquement (strict)

`config/media_filter.json` :
```json
{
  "mode": "whitelist",
  "allowed_apps": ["Music.UI.exe", "Apple Music.exe"],
  "blocked_apps": [],
  "default_message": {
    "title": "No track playing",
    "artist": "Unknown",
    "album": ""
  }
}
```

**Résultat** :
- ✅ Apple Music → Affiche les infos
- ❌ YouTube → "No track playing"
- ❌ Spotify → "No track playing"

---

### Exemple 2 : Bloquer les navigateurs

`config/media_filter.json` :
```json
{
  "mode": "blacklist",
  "allowed_apps": [],
  "blocked_apps": ["chrome.exe", "firefox.exe", "msedge.exe"],
  "default_message": {
    "title": "🚫 Navigateur bloqué",
    "artist": "Utilisez une application musicale",
    "album": ""
  }
}
```

**Résultat** :
- ✅ Apple Music → Affiche les infos
- ✅ Spotify → Affiche les infos
- ❌ YouTube (Chrome/Firefox/Edge) → "🚫 Navigateur bloqué"

---

### Exemple 3 : Tout autoriser (mode découverte)

`config/media_filter.json` :
```json
{
  "mode": "allow_all",
  "allowed_apps": [],
  "blocked_apps": []
}
```

**Résultat** :
- ✅ Toutes les applications → Affiche les infos
- Utile pour tester et identifier les noms d'applications

---

### Exemple 4 : Port personnalisé + Réseau local

`config/settings.json` :
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 50000
  },
  "update_interval": 0.5
}
```

**Résultat** :
- 🌐 Accessible depuis n'importe quel appareil sur le réseau
- 📺 URL : `http://[IP-de-votre-PC]:50000`

---

## 🔄 Workflow de Configuration

### Scénario : "Je veux autoriser uniquement Apple Music"

1. **Ouvrir** `config/media_filter.json`

2. **Configurer** :
   ```json
   {
     "mode": "whitelist",
     "allowed_apps": ["Music.UI.exe", "Apple Music.exe"]
   }
   ```

3. **Recharger** (2 options) :
   - Option A : Redémarrer le serveur
   - Option B : `curl -X POST http://127.0.0.1:48952/api/reload-config`

4. **Vérifier** :
   - Visiter : `http://127.0.0.1:48952/api/filter-config`
   - Confirmer que `mode: "whitelist"`

5. **Tester** :
   - Lancer Apple Music → ✅ Infos affichées
   - Lancer YouTube → ❌ "No track playing"

---

## 🛠️ Commandes Utiles

### Vérifier la configuration actuelle
```bash
curl http://127.0.0.1:48952/api/filter-config
```

### Voir la piste en cours
```bash
curl http://127.0.0.1:48952/api/current-track
```

### Recharger la configuration
```bash
curl -X POST http://127.0.0.1:48952/api/reload-config
```

### Vérifier si le serveur est actif
```bash
curl http://127.0.0.1:48952/
```

---

## ❓ FAQ

**Q : Comment changer le port ?**
> Éditez `config/settings.json` et modifiez `"port": 48952` vers votre port souhaité.

**Q : Le filtre ne fonctionne pas**
> 1. Vérifiez la syntaxe JSON (virgules, guillemets)
> 2. Rechargez : `POST /api/reload-config`
> 3. Vérifiez le nom exact de l'app via `GET /api/current-track`

**Q : Comment identifier le nom d'une application ?**
> Mettez `"mode": "allow_all"`, lancez la musique, consultez `"source_app"` dans l'API.

**Q : Puis-je modifier la config en direct ?**
> Oui ! Modifiez le fichier puis rechargez via `POST /api/reload-config`.

---

## 📚 Ressources

- [README.md](README.md) - Documentation complète
- [LICENSE](LICENSE) - Licence du projet
- GitHub Issues - Support et bugs

---

**Version** : 2.0.0
**Dernière mise à jour** : 2025-12-20
