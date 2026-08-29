# Contribuer à Music Overlay Server

Merci de votre intérêt ! Bugs, skins et améliorations sont les bienvenus.

---

## 🐛 Signaler un bug

Ouvrez une [issue](https://github.com/dexteee-r/Windows-Music-overlay-server/issues)
en joignant :

1. la sortie de `scripts\diagnostic.bat` ;
2. le contenu de `logs\music-overlay.log` ;
3. les étapes pour reproduire, le comportement attendu et celui observé ;
4. votre version de Windows et le lecteur audio concerné.

---

## 💻 Mettre en place l'environnement

```bash
git clone https://github.com/dexteee-r/Windows-Music-overlay-server.git
cd Windows-Music-overlay-server
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

| Commande | Rôle |
|----------|------|
| `python -m music_overlay` | Lance l'interface graphique |
| `python -m music_overlay --console` | Lance le serveur seul |
| `python -m music_overlay --diagnostic` | Vérifie l'installation |
| `pytest` | Tests |
| `ruff check . && ruff format .` | Lint et formatage |
| `scripts\build_exe.bat` | Compile l'exécutable |

Le lint et les tests doivent passer avant toute pull request : la CI les rejoue
sur Python 3.10 et 3.13.

---

## 🗺️ Organisation du code

```
music_overlay/
├── paths.py          Résolution des chemins (sources / exécutable compilé)
├── logging_setup.py  Journalisation
├── config.py         Réglages et filtre média
├── skins.py          Découverte et sélection des skins
├── media.py          Session média Windows (WinRT)
├── diagnostics.py    Auto-diagnostic
├── startup.py        Démarrage automatique Windows
├── server.py         Routes Flask, démarrage, arrêt et choix du port
└── gui/
    ├── window.py       Fenêtre, onglets, serveur, barre des tâches
    ├── tab_control.py  Onglet Contrôle
    ├── tab_skins.py    Onglet Skins
    ├── tab_settings.py Onglet Paramètres
    ├── tab_about.py    Onglet À propos
    ├── dialogs.py      Fenêtres secondaires
    └── assets.py       Images générées (icône, aperçu par défaut)
```

**Quatre règles à respecter :**

1. **Aucune logique métier dans `gui/`.** L'interface appelle le cœur et affiche
   le résultat ; tout ce qui est testable vit ailleurs.
2. **Aucun chemin relatif.** Passez par `music_overlay.paths` : l'application
   doit fonctionner quel que soit le répertoire de lancement, et une fois compilée.
3. **Un onglet ne parle pas à un autre onglet.** Chaque `tab_*.py` reçoit la
   fenêtre (`app`) et passe par elle : c'est le seul endroit qui coordonne.
4. **`logging`, jamais `print()`** (sauf dans la banniere console volontaire de
   `__main__.run_console`).

---

## 🎨 Créer un skin

Un skin est un dossier de `skins/`, avec au minimum un `skin.html`.

```
skins/mon_skin/
├── skin.html      obligatoire
├── info.json      recommandé
└── preview.png    recommandé (500 × 300 environ)
```

**`info.json`**

```json
{
  "name": "Mon Skin",
  "description": "Une phrase de description",
  "author": "VotrePseudo",
  "version": "1.0"
}
```

**Contrat côté HTML** : interrogez `/api/current-track` et mettez la page à jour.

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <style>
    /* Fond transparent obligatoire : l'overlay se superpose a la scene OBS */
    body { background: transparent; margin: 0; font-family: 'Segoe UI', sans-serif; }
    #carte { display: flex; align-items: center; gap: 12px; padding: 12px; }
    #pochette { width: 64px; height: 64px; border-radius: 8px; }
  </style>
</head>
<body>
  <div id="carte">
    <img id="pochette" alt="">
    <div>
      <div id="titre"></div>
      <div id="artiste"></div>
    </div>
  </div>

  <script>
    function majUI(piste) {
      document.getElementById('titre').textContent = piste.title;
      document.getElementById('artiste').textContent = piste.artist;
      document.getElementById('pochette').src = piste.thumbnail || '';
      // piste.is_playing, piste.position, piste.duration, piste.album
      // sont egalement disponibles.
    }

    setInterval(() => {
      fetch('/api/current-track')
        .then(r => r.json())
        .then(majUI)
        .catch(() => {});
    }, 1000);
  </script>
</body>
</html>
```

**Bonnes pratiques**

- Fond **transparent**, sans marge extérieure.
- Prévoir une taille de 650 × 180 par défaut ; rester lisible si le texte est long.
- Gérer l'absence de pochette (`thumbnail` vide).
- Tout inclure dans le fichier : ni CDN, ni police distante (l'overlay doit
  fonctionner hors ligne).
- Tester avec **« Ouvrir l'overlay »**, puis dans OBS.

Le skin apparaît dans l'application après **Rafraîchir la liste**.

---

## 📤 Proposer une modification

```bash
git checkout -b feat/ma-fonctionnalite
# ... modifications ...
ruff check . && ruff format . && pytest
git commit -m "[ADD] description courte"
git push origin feat/ma-fonctionnalite
```

**Préfixes de commit utilisés dans le projet** : `[ADD]`, `[FIX]`, `[UPDATE]`,
`[PERF]`, `[DOC]`, `[REFACTOR]`, `[DELETE]`.

Dans la pull request, décrivez le problème résolu, la manière dont vous l'avez
testé, et joignez une capture pour toute modification visuelle.

---

## 🧪 Écrire des tests

Les tests vivent dans `tests/` et n'ont besoin ni d'un vrai serveur, ni de
Windows Media : `create_app()` reçoit ses dépendances en paramètre, et les
fixtures de `conftest.py` fournissent une arborescence temporaire.

```python
def test_whitelist_bloque_les_autres_apps():
    media_filter = MediaFilter(mode="whitelist", allowed_apps=("Spotify.exe",))
    assert media_filter.allows("Spotify.exe")
    assert not media_filter.allows("chrome.exe")
```

Toute correction de bug mérite un test qui échoue avant le correctif.

---

## ❓ Questions

Ouvrez une [issue](https://github.com/dexteee-r/Windows-Music-overlay-server/issues)
avec le label `question`.

Soyez respectueux et constructif : les contributions viennent de personnes aux
niveaux d'expérience très variés.
