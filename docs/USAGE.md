# 📖 Guide d'utilisation

Tour complet de l'application. Pour aller vite : [démarrage rapide](QUICKSTART.md).

---

## L'interface

Quatre onglets.

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

**Serveur**

| Champ | Valeur par défaut | Remarque |
|-------|-------------------|----------|
| Port | `49450` | Entre 1024 et 65535. En cas de conflit, l'application choisit le suivant. |
| Adresse | `127.0.0.1` | `127.0.0.1` = ce PC uniquement. `0.0.0.0` expose l'overlay au réseau local. |
| Intervalle | `0.5` s | Entre 0.1 et 10. Plus bas = plus réactif, plus de CPU. |

Un changement de port ou d'adresse propose de redémarrer le serveur ; le reste
s'applique immédiatement.

**Filtre des applications** — voir la section suivante.

**Démarrage** — la case crée (ou retire) un raccourci dans le dossier Démarrage
de Windows.

### ℹ️ À propos

Version, nombre de skins installés, port configuré, routes de l'API et
emplacement des journaux.

---

## Choisir ce qui s'affiche

Sans filtre, l'overlay afficherait aussi la vidéo YouTube ouverte dans un onglet.

**Trois modes :**

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
application.

Pour le relever :

1. Mode **Tout accepter** → **Enregistrer**.
2. Lancez votre musique.
3. Cliquez sur **« Ouvrir la page source_app »** (sous le bouton de détection) :
   la page `/api/current-track` s'ouvre dans votre navigateur.
4. Copiez la valeur du champ `source_app` dans la liste voulue, puis
   remettez le mode souhaité et **Enregistrer**.

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

Les skins ont un fond transparent : ils se superposent à votre scène.
Certains, comme *Modern Vinyl*, sont plus à l'aise avec une hauteur plus grande
(220 px) — ajustez en regardant l'aperçu.

---

## Sans interface graphique

Pour un usage « serveur seul » :

| Commande | Effet |
|----------|-------|
| `scripts\start.bat` | Serveur en console, messages visibles |
| `run_server.pyw` | Serveur sans aucune fenêtre |
| `python -m music_overlay --console` | Idem, depuis un terminal |

Le skin actif et les filtres restent ceux configurés dans l'application.

---

## Les journaux

Tout est écrit dans `logs/music-overlay.log` (rotation automatique, 3 fichiers
de 512 Ko maximum). C'est le fichier à joindre à une demande d'aide.

---

## Aller plus loin

- [Toutes les options de configuration](CONFIGURATION.md)
- [Créer son propre skin](../CONTRIBUTING.md)
- [Dépannage](TROUBLESHOOTING.md)
