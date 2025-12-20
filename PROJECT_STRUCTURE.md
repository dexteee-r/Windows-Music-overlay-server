# 📁 Structure du Projet - Music Overlay Server v2.0

## 🎯 Vue d'Ensemble

Music Overlay Server v2.0 a été entièrement réorganisé pour être **simple, accessible et professionnel**.

---

## 📂 Arborescence Complète

```
music-overlay-server/
│
├── 📁 config/                          # Configuration
│   ├── settings.json                   # Port, host, paramètres serveur
│   └── media_filter.json               # Applications autorisées/bloquées
│
├── 🐍 server.py                        # ⭐ FICHIER PRINCIPAL UNIQUE
│
├── 📜 install.bat                      # Installation automatique
├── 📜 start.bat                        # Démarrage du serveur
│
├── 📖 README.md                        # Documentation principale
├── 📖 INSTALL.md                       # Guide d'installation détaillé
├── 📖 SUMMARY.md                       # Résumé des changements v2.0
├── 📖 PROJECT_STRUCTURE.md             # Ce fichier
│
├── 📄 requirements.txt                 # Dépendances Python
├── 📄 LICENSE                          # Licence MIT
├── 📄 .gitignore                       # Fichiers ignorés par Git
├── 📄 .gitattributes                   # Configuration Git (fins de ligne)
│
└── 📁 [Anciens fichiers]               # À supprimer (optionnel)
    ├── src/                            # Ancien dossier (ne plus utilisé)
    ├── music_overlay_server.py         # Ancienne version
    ├── start_server.bat                # Ancien script
    ├── CONFIGURATION.md                # Documentation v1.x
    └── QUICKSTART.md                   # Guide v1.x
```

---

## 🎯 Fichiers Essentiels (Minimum Vital)

Pour que le projet fonctionne, vous avez besoin **au minimum** de :

```
music-overlay-server/
├── config/
│   ├── settings.json
│   └── media_filter.json
├── server.py                   ← LE FICHIER PRINCIPAL
├── requirements.txt
├── install.bat
└── start.bat
```

---

## 📋 Description des Fichiers

### 🔧 Fichiers de Configuration

| Fichier | Description | Modifiable |
|---------|-------------|------------|
| `config/settings.json` | Port, host, intervalle de mise à jour | ✅ Oui |
| `config/media_filter.json` | Whitelist/blacklist des applications | ✅ Oui |

### 🐍 Code Python

| Fichier | Description | Rôle |
|---------|-------------|------|
| `server.py` | Serveur Flask + Filtre + HTML | ⭐ Principal |
| `requirements.txt` | Dépendances (Flask, winrt, etc.) | Installation |

### 📜 Scripts Windows

| Fichier | Description | Usage |
|---------|-------------|-------|
| `install.bat` | Installation des dépendances | Une seule fois |
| `start.bat` | Démarrage du serveur | À chaque utilisation |

### 📖 Documentation

| Fichier | Public Cible | Contenu |
|---------|--------------|---------|
| `README.md` | Tous les utilisateurs | Vue d'ensemble, configuration, FAQ |
| `INSTALL.md` | Débutants | Guide pas à pas avec explications |
| `SUMMARY.md` | Utilisateurs v1.x | Changements et migration |
| `PROJECT_STRUCTURE.md` | Développeurs | Structure du projet |

### 📄 Fichiers Git

| Fichier | Description |
|---------|-------------|
| `.gitignore` | Fichiers à ne pas versionner |
| `.gitattributes` | Normalisation des fins de ligne |
| `LICENSE` | Licence MIT (open source) |

---

## 🗑️ Fichiers Obsolètes (v1.x)

Ces fichiers peuvent être **supprimés** si vous n'utilisez plus la v1.x :

```
❌ src/                          # Dossier obsolète
❌ music_overlay_server.py       # Ancienne version monolithique
❌ start_server.bat              # Ancien script (remplacé par start.bat)
❌ CONFIGURATION.md              # Documentation v1.x
❌ QUICKSTART.md                 # Guide v1.x
❌ CHANGELOG.md                  # Historique v1.x
```

**Recommandation** : Gardez-les temporairement pour référence, puis supprimez-les une fois la migration terminée.

---

## 🎯 Workflow Utilisateur

### 1️⃣ Installation (une seule fois)

```
1. Double-cliquer sur install.bat
2. Attendre la fin de l'installation
3. Terminé !
```

### 2️⃣ Configuration (optionnel)

```
1. Ouvrir config/settings.json
2. Modifier le port si nécessaire
3. Ouvrir config/media_filter.json
4. Ajouter/retirer des applications
5. Sauvegarder
```

### 3️⃣ Utilisation (à chaque fois)

```
1. Double-cliquer sur start.bat
2. Ouvrir http://127.0.0.1:48952 dans un navigateur
3. Ou ajouter l'URL dans OBS
4. Laisser la fenêtre ouverte pendant le stream
```

---

## 🔀 Comparaison v1.x vs v2.0

| Aspect | v1.x | v2.0 |
|--------|------|------|
| **Fichiers Python** | 2 (server + filter) | 1 (tout-en-un) |
| **Structure** | src/ + root | Tout à la racine |
| **Config** | Création manuelle | Auto-création au démarrage |
| **Documentation** | README technique | README + INSTALL pour tous |
| **Messages** | Anglais + emojis | Français + ASCII |
| **Scripts** | start_server.bat | start.bat + vérifications |

---

## 📊 Tailles des Fichiers

| Fichier | Taille | Commentaire |
|---------|--------|-------------|
| `server.py` | ~21 KB | Tout-en-un (server + filter + HTML) |
| `README.md` | ~8 KB | Documentation complète |
| `INSTALL.md` | ~7 KB | Guide détaillé |
| `install.bat` | ~3 KB | Script d'installation |
| `config/settings.json` | <1 KB | Configuration serveur |
| `config/media_filter.json` | <1 KB | Filtre média |

**Total du projet** : ~50 KB (sans dépendances)

---

## 🛠️ Pour les Développeurs

### Modifier le code

1. **Serveur Flask** : Éditer `server.py` (lignes 1-150)
2. **Filtre média** : Éditer `server.py` (lignes 160-200)
3. **Template HTML** : Éditer `server.py` (lignes 280-540)

### Ajouter une fonctionnalité

1. Éditer `server.py`
2. Ajouter des routes Flask ou modifier le template HTML
3. Mettre à jour `README.md` si nécessaire
4. Tester avec `python server.py`

### Contribuer

1. Fork le projet
2. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
3. Commit : `git commit -m "Ajout de ma fonctionnalité"`
4. Push : `git push origin feature/ma-fonctionnalite`
5. Créer une Pull Request

---

## ✅ Checklist de Déploiement

Avant de partager le projet :

- [ ] Supprimer les anciens fichiers (src/, music_overlay_server.py, etc.)
- [ ] Vérifier que `.gitignore` est à jour
- [ ] Tester `install.bat` sur une machine propre
- [ ] Tester `start.bat` après installation
- [ ] Vérifier que `server.py` fonctionne
- [ ] Mettre à jour `README.md` si nécessaire
- [ ] Vérifier la `LICENSE`
- [ ] Créer un tag Git : `git tag v2.0.0`

---

## 📝 Notes Importantes

### Port par défaut

Le port **48952** a été choisi dans la plage des ports privés/dynamiques (49152-65535) pour minimiser les conflits.

### Configuration auto

Les fichiers `config/settings.json` et `config/media_filter.json` sont créés automatiquement au premier lancement si absents.

### Encodage

Tous les fichiers utilisent **UTF-8** pour la compatibilité maximale.

### Fins de ligne

- `.gitattributes` force **LF** pour les fichiers Python/JSON/Markdown
- Force **CRLF** pour les fichiers `.bat` (Windows)

---

## 🚀 Prochaines Étapes

Pour améliorer le projet :

1. **Tests automatisés** : Ajouter des tests unitaires avec pytest
2. **Thèmes** : Permettre de changer le style de l'overlay
3. **Multi-langues** : Support anglais/français dans l'interface
4. **Historique** : Garder un historique des pistes jouées
5. **Stats** : Afficher des statistiques d'écoute

---

**Version** : 2.0.0
**Dernière mise à jour** : Décembre 2025
**Auteur** : [@dexteee-r](https://github.com/dexteee-r)
