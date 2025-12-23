# Contributing to Music Overlay Server

Merci de votre intérêt pour contribuer au Music Overlay Server ! 🎉

## 🤝 Comment Contribuer

### Signaler un Bug

1. Vérifiez que le bug n'a pas déjà été signalé dans [Issues](https://github.com/username/music-overlay-server/issues)
2. Créez une nouvelle issue avec le template "Bug Report"
3. Décrivez le problème en détail :
   - Version de Windows
   - Version de Python
   - Étapes pour reproduire
   - Comportement attendu vs actuel
   - Screenshots si applicable

### Proposer une Fonctionnalité

1. Ouvrez une issue avec le template "Feature Request"
2. Expliquez clairement :
   - Le problème que ça résout
   - Comment ça devrait fonctionner
   - Des exemples d'utilisation

### Soumettre du Code

#### 1. Fork & Clone

```bash
git clone https://github.com/VOTRE-USERNAME/music-overlay-server.git
cd music-overlay-server
```

#### 2. Créer une Branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/mon-bug-fix
```

#### 3. Développer

- Suivez le style de code existant
- Commentez les parties complexes
- Testez vos modifications

#### 4. Commit

```bash
git add .
git commit -m "[type] Description courte

Description plus détaillée si nécessaire
"
```

**Types de commit :**
- `[feat]` - Nouvelle fonctionnalité
- `[fix]` - Correction de bug
- `[docs]` - Documentation
- `[style]` - Formatage, point-virgules manquants, etc.
- `[refactor]` - Refactoring du code
- `[test]` - Ajout de tests
- `[chore]` - Mise à jour des dépendances, etc.

#### 5. Push & Pull Request

```bash
git push origin feature/ma-nouvelle-fonctionnalite
```

Puis créez une Pull Request sur GitHub.

---

## 📐 Standards de Code

### Python

- **PEP 8** pour le style
- **Docstrings** pour toutes les fonctions publiques
- **Type hints** quand c'est pertinent
- **Noms explicites** pour les variables

```python
def load_config_file(file_path: str) -> dict:
    """
    Charge un fichier de configuration JSON.

    Args:
        file_path: Chemin vers le fichier JSON

    Returns:
        dict: Configuration chargée

    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    # Implementation
```

### HTML/CSS (Skins)

- **Indentation** : 2 espaces
- **Noms de classes** : kebab-case (`music-widget`)
- **Commentaires** pour les sections importantes
- **Responsive** si possible

---

## 🎨 Créer un Nouveau Skin

1. Créez un dossier `skins/votre_skin/`

2. Créez `info.json` :
```json
{
  "name": "Votre Skin",
  "description": "Description du skin",
  "author": "Votre Nom",
  "version": "1.0"
}
```

3. Créez `skin.html` avec ce template :
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Music Overlay - Votre Skin</title>
    <style>
        /* Vos styles */
    </style>
</head>
<body>
    <div id="musicWidget">
        <div id="trackTitle">...</div>
        <div id="trackArtist">...</div>
    </div>

    <script>
        async function updateTrackInfo() {
            const response = await fetch('/api/current-track');
            const data = await response.json();

            document.getElementById('trackTitle').textContent = data.title;
            document.getElementById('trackArtist').textContent = data.artist;
        }

        setInterval(updateTrackInfo, 500);
        updateTrackInfo();
    </script>
</body>
</html>
```

4. Testez votre skin localement

5. Soumettez une PR avec :
   - Screenshot du skin
   - Description des features uniques

---

## 🧪 Tests

Avant de soumettre :

1. **Testez la GUI**
   ```bash
   python src/gui.py
   ```

2. **Testez le serveur**
   ```bash
   python server.py
   ```

3. **Vérifiez les imports**
   ```bash
   python launcher.pyw
   ```

4. **Testez le changement de skin**

---

## 📝 Documentation

Si vous modifiez une fonctionnalité :

1. Mettez à jour `README.md` si nécessaire
2. Mettez à jour `docs/USAGE.md` avec les nouvelles instructions
3. Ajoutez une entrée dans `CHANGELOG.md`

---

## ❓ Questions

Des questions ? N'hésitez pas à :
- Ouvrir une [Discussion](https://github.com/username/music-overlay-server/discussions)
- Demander dans une [Issue](https://github.com/username/music-overlay-server/issues)

---

## 📜 Code of Conduct

- Soyez respectueux et constructif
- Pas de spam ou de contenu inapproprié
- Concentrez-vous sur le code, pas sur les personnes

---

Merci d'aider à améliorer Music Overlay Server ! 🎵
