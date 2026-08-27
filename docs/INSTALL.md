# 📥 Installation

Deux façons d'installer, au choix. La première ne demande **rien** d'autre que Windows.

---

## Option 1 — Exécutable (recommandé)

1. Ouvrez la [page des releases](https://github.com/dexteee-r/Windows-Music-overlay-server/releases).
2. Téléchargez `MusicOverlayServer-vX.Y.Z.zip`.
3. **Décompressez le dossier** (clic droit → *Extraire tout*), par exemple dans
   `Documents\MusicOverlayServer`.
4. Double-cliquez sur **`MusicOverlayServer.exe`**.

> ⚠️ Ne lancez pas l'exécutable directement depuis le `.zip` : il a besoin
> d'écrire sa configuration à côté de lui.

Windows peut afficher un avertissement SmartScreen (application non signée) :
*Informations complémentaires* → *Exécuter quand même*.

---

## Option 2 — Depuis les sources

### 1. Installer Python 3.10 ou plus

Téléchargez Python sur [python.org/downloads](https://www.python.org/downloads/).

> ✅ **Cochez impérativement « Add python.exe to PATH »** sur le premier écran
> de l'installateur. C'est la cause n°1 des problèmes d'installation.

Vérifiez dans un terminal :

```bash
python --version
```

### 2. Récupérer le projet

Téléchargez `MusicOverlayServer-sources-vX.Y.Z.zip` depuis les releases, ou :

```bash
git clone https://github.com/dexteee-r/Windows-Music-overlay-server.git
```

### 3. Lancer

Double-cliquez sur **`DEMARRER.bat`**.

Au premier lancement, il crée un environnement isolé (`.venv`), installe les
dépendances et ouvre l'application. Comptez une à deux minutes ; les fois
suivantes, le démarrage est immédiat.

Pour lancer l'installation seule : `scripts\install.bat`.

---

## Vérifier que tout va bien

Double-cliquez sur **`scripts\diagnostic.bat`** (ou, dans l'application, onglet
**Contrôle** → bouton **Diagnostic**).

Le rapport liste chaque dépendance, le dossier de configuration, les skins
détectés et l'état du port :

```
[OK] Version de Python : 3.13.2
[OK] Dependance Flask
[OK] Dependance winrt
...
Tout est OK : l'application peut demarrer.
```

En cas de problème, chaque ligne en échec indique quoi faire.

---

## Désinstaller

L'application n'écrit rien en dehors de son dossier, à une exception près :

1. Décochez **« Lancer automatiquement au démarrage de Windows »** dans l'onglet
   Paramètres (cela supprime le raccourci dans le dossier Démarrage).
2. Supprimez le dossier de l'application.

---

## Et ensuite ?

👉 [Démarrage rapide avec OBS](QUICKSTART.md)
