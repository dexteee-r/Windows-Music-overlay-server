# ⚙️ Configuration

Tout est réglable depuis l'onglet **Paramètres**. Ce document décrit les
fichiers sous-jacents, pour ceux qui préfèrent les éditer à la main.

Les fichiers sont dans `config/`, à côté de l'application. Ils sont créés
automatiquement au premier lancement.

> Après une modification manuelle, cliquez sur **Diagnostic** ou appelez
> `POST /api/reload-config` — sinon la valeur en mémoire reste utilisée.
> Un JSON invalide n'empêche jamais le démarrage : les valeurs par défaut
> prennent le relais et un avertissement part dans le journal.

---

## `config/settings.json`

```json
{
  "_commentaire": "Configuration du serveur",
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
suivant (jusqu'à 20 tentatives) et l'indique dans le journal.

---

## `config/media_filter.json`

```json
{
  "mode": "whitelist",
  "allowed_apps": [
    "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
    "AppleInc.AppleMusicWin_nzyj5cx40ttqa!App"
  ],
  "blocked_apps": ["chrome.exe"]
}
```

| Clé | Type | Défaut | Valeurs |
|-----|------|--------|---------|
| `mode` | chaîne | `whitelist` | `all`, `whitelist`, `blacklist` |
| `allowed_apps` | liste | Spotify + Apple Music | Identifiants d'application |
| `blocked_apps` | liste | `[]` | Identifiants d'application |

La comparaison ignore la casse ; les doublons et lignes vides sont nettoyés à
l'enregistrement.

**Trouver un identifiant** : bouton **« Détecter les applications en cours »**,
ou `GET /api/sources`.

---

## `config/active_skin.json`

```json
{
  "active_skin": "zen_minimalist"
}
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

## Ligne de commande

| Commande | Effet |
|----------|-------|
| `python -m music_overlay` | Interface graphique |
| `python -m music_overlay --console` | Serveur seul, en console |
| `python -m music_overlay --diagnostic` | Rapport d'installation (code de retour 1 si problème) |
| `python -m music_overlay --version` | Version installée |

---

## Emplacement des fichiers

| Dossier | Contenu |
|---------|---------|
| `config/` | Vos réglages |
| `skins/` | Les skins (un dossier chacun) |
| `logs/` | `music-overlay.log` et ses rotations |

Avec l'exécutable, ces dossiers sont créés **à côté du `.exe`**. Vous pouvez y
déposer vos propres skins : ils sont détectés au prochain
**Rafraîchir la liste** et ont priorité sur les skins fournis en cas de nom identique.
