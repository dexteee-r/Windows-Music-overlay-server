# 📖 Guide complet

Tout ce que fait l'application, et comment la régler.
Pour l'installation et le premier lancement : [DEMARRAGE.md](DEMARRAGE.md).

---

## L'interface

### 🎛️ Contrôle

Le tableau de bord.

| Élément | Rôle |
|---------|------|
| **Démarrer / Arrêter** | Allume et éteint le serveur. Le port est réellement libéré à l'arrêt. |
| **Ouvrir l'overlay** | Ouvre l'overlay dans votre navigateur (pratique pour vérifier) |
| **Diagnostic** | Rapport complet sur l'installation |
| **Copier** | Copie l'URL de l'overlay pour la coller dans OBS |
| **Journal** | Ce que fait l'application en direct |

### 🎨 Skins

La liste à gauche, l'aperçu à droite (image, description, auteur, version).

- **Appliquer** (ou double-clic) active le skin, serveur démarré ou non.
- **Rafraîchir la liste** relit le dossier `skins/` : utile après y avoir déposé
  un nouveau skin.

Le changement est immédiat ; il suffit d'actualiser la source dans OBS.

### ⚙️ Paramètres

| Champ | Défaut | Remarque |
|-------|--------|----------|
| Port | `49450` | Entre 1024 et 65535. En cas de conflit, l'application choisit le suivant. |
| Adresse | `127.0.0.1` | `127.0.0.1` = ce PC uniquement. `0.0.0.0` expose l'overlay au réseau local. |
| Intervalle | `0.5` s | Entre 0.1 et 10. Plus bas = plus réactif, plus de CPU. |

Un changement de port ou d'adresse propose de redémarrer le serveur ; le reste
s'applique immédiatement.

La case **Démarrage** crée (ou retire) un raccourci dans le dossier Démarrage de
Windows.

### ℹ️ À propos

Version, nombre de skins installés, port configuré, routes de l'API et
emplacement des journaux.

---

## Choisir ce qui s'affiche

Sans filtre, l'overlay afficherait aussi la vidéo YouTube ouverte dans un onglet.

| Mode | Comportement |
|------|--------------|
| **Tout accepter** | Toutes les applications, sauf celles bloquées |
| **Whitelist** | Uniquement les applications autorisées *(recommandé)* |
| **Blacklist** | Toutes les applications, sauf celles bloquées |

**Remplir la liste sans rien recopier :**

1. Lancez la musique dans le lecteur voulu.
2. **« Détecter les applications en cours »**.
3. Cochez les applications, validez, puis **Enregistrer**.

Les identifiants ressemblent à `SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify`
pour les applications du Microsoft Store, ou à `chrome.exe` pour les programmes
classiques.

**Si la détection ne trouve pas votre lecteur**, les deux listes restent
librement modifiables : ajoutez l'identifiant à la main, une ligne par
application. Pour le relever :

1. Mode **Tout accepter** → **Enregistrer**.
2. Lancez votre musique.
3. Cliquez sur **« Ouvrir la page source_app »** (sous le bouton de détection) :
   la page `/api/current-track` s'ouvre dans votre navigateur.
4. Copiez la valeur du champ `source_app` dans la liste voulue, puis remettez le
   mode souhaité et **Enregistrer**.

```json
{ "title": "Song", "artist": "Artist", "source_app": "chrome.exe" }
```

**Exemples**

- *Uniquement Spotify* : mode Whitelist, Spotify dans les autorisées.
- *Tout sauf le navigateur* : mode Blacklist, `chrome.exe`, `msedge.exe`,
  `brave.exe`, `firefox.exe` dans les bloquées.

---

## Utilisation dans OBS

| Réglage | Valeur conseillée |
|---------|-------------------|
| Type de source | Navigateur |
| URL | Celle affichée dans l'onglet Contrôle |
| Largeur | 600 – 700 px |
| Hauteur | 150 – 200 px |
| Actualiser à l'activation de la scène | ✅ |

Les skins ont un fond transparent : ils se superposent à votre scène. Certains,
comme *Modern Vinyl*, sont plus à l'aise avec une hauteur plus grande (220 px) —
ajustez en regardant l'aperçu.

---

## Sans interface graphique

| Commande | Effet |
|----------|-------|
| `scripts\start.bat` | Serveur en console, messages visibles |
| `python -m music_overlay --console` | Idem, depuis un terminal |
| `python server.py` | Idem |

Le skin actif et les filtres restent ceux configurés dans l'application.

| Commande | Effet |
|----------|-------|
| `python -m music_overlay` | Interface graphique |
| `python -m music_overlay --diagnostic` | Rapport d'installation (code de retour 1 si problème) |
| `python -m music_overlay --version` | Version installée |

---

## Les fichiers de configuration

Tout se règle dans l'onglet **Paramètres**, mais les fichiers de `config/`
restent modifiables à la main. Ils sont créés automatiquement au premier
lancement, à côté de l'application.

> Après une modification manuelle, appelez `POST /api/reload-config` — sinon la
> valeur en mémoire reste utilisée. Un JSON invalide n'empêche jamais le
> démarrage : les valeurs par défaut prennent le relais et un avertissement part
> dans le journal.

### `config/settings.json`

```json
{
  "host": "127.0.0.1",
  "port": 49450,
  "refresh_interval": 0.5
}
```

| Clé | Type | Défaut | Contrainte |
|-----|------|--------|------------|
| `host` | chaîne | `127.0.0.1` | `127.0.0.1` (local) ou `0.0.0.0` (réseau local) |
| `port` | entier | `49450` | 1024 – 65535 |
| `refresh_interval` | nombre | `0.5` | 0.1 – 10 secondes |

Si le port est occupé au démarrage, l'application prend le premier port libre
suivant ; si toute la plage est réservée par Windows, elle laisse le système en
choisir un.

### `config/media_filter.json`

```json
{
  "mode": "whitelist",
  "allowed_apps": ["SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"],
  "blocked_apps": ["chrome.exe"]
}
```

| Clé | Défaut | Valeurs |
|-----|--------|---------|
| `mode` | `whitelist` | `all`, `whitelist`, `blacklist` |
| `allowed_apps` | Spotify + Apple Music | Identifiants d'application |
| `blocked_apps` | `[]` | Identifiants d'application |

La comparaison ignore la casse ; les doublons et lignes vides sont nettoyés à
l'enregistrement.

### `config/active_skin.json`

```json
{ "active_skin": "zen_minimalist" }
```

La valeur est le **nom du dossier** dans `skins/`. Si le skin n'existe plus,
l'application bascule sur `zen_minimalist`, puis sur le premier skin disponible.

---

## API HTTP

Base : `http://127.0.0.1:49450` (adapter au port réel).

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | L'overlay (skin actif) |
| `GET` | `/health` | `{"status", "version", "media_available", "active_skin"}` |
| `GET` | `/api/current-track` | Piste en cours |
| `GET` | `/api/skins` · `/api/list-skins` | Skins installés + skin actif |
| `GET`/`POST` | `/api/set-skin/<skin_id>` | Change le skin |
| `POST` | `/api/set-skin` | Idem, corps `{"skin_id": "..."}` |
| `GET` | `/api/sources` | Applications média détectées |
| `GET`/`POST` | `/api/reload-config` | Relit configuration et skins |

**`/api/current-track`**

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

Sans lecture en cours (ou si l'application est filtrée), `title` vaut
`"No track playing"` et `is_playing` est `false`.

**`/api/sources`**

```json
{
  "success": true,
  "count": 2,
  "sources": [
    { "app_id": "Spotify.exe", "title": "Song", "artist": "Artist",
      "is_playing": true, "allowed": true }
  ]
}
```

Répond `503` si les paquets `winrt` sont absents.

**Codes d'erreur** : `400` paramètre manquant · `404` skin inconnu ·
`503` skin ou API média indisponible.

Le CORS est ouvert sur `/api/*` : une page web tierce peut interroger l'API,
mais uniquement depuis votre machine.

---

## Emplacement des fichiers

| Dossier | Contenu |
|---------|---------|
| `config/` | Vos réglages |
| `skins/` | Les skins (un dossier chacun) |
| `logs/` | `music-overlay.log` et ses rotations (3 × 512 Ko) |

Avec l'exécutable, ces dossiers sont créés **à côté du `.exe`**. Vous pouvez y
déposer vos propres skins : ils sont détectés au prochain **Rafraîchir la
liste** et ont priorité sur les skins fournis en cas de nom identique.

Le journal est le fichier à joindre à une demande d'aide.

---

## Aller plus loin

- [Créer son propre skin](../CONTRIBUTING.md)
- [Dépannage](TROUBLESHOOTING.md)
