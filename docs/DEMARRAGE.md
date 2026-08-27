# 📥 Installation et premier démarrage

De zéro à un overlay affiché dans OBS.

---

## 1. Installer

Deux façons, au choix. La première ne demande **rien** d'autre que Windows.

### Option A — Exécutable (recommandé)

1. Ouvrez la [page des releases](https://github.com/dexteee-r/Windows-Music-overlay-server/releases).
2. Téléchargez `MusicOverlayServer-vX.Y.Z.zip`.
3. **Décompressez le dossier** (clic droit → *Extraire tout*), par exemple dans
   `Documents\MusicOverlayServer`.
4. Double-cliquez sur **`MusicOverlayServer.exe`**.

> ⚠️ Ne lancez pas l'exécutable depuis l'intérieur du `.zip` : il a besoin
> d'écrire sa configuration à côté de lui.

Windows peut afficher un avertissement SmartScreen (application non signée) :
*Informations complémentaires* → *Exécuter quand même*.

### Option B — Depuis les sources

**Installez Python 3.10 ou plus**, depuis
[python.org/downloads](https://www.python.org/downloads/).

> ✅ **Cochez « Add python.exe to PATH »** sur le premier écran de
> l'installateur. C'est la cause n°1 des problèmes d'installation.

Vérifiez dans un terminal :

```bash
python --version
```

**Récupérez le projet** — archive `MusicOverlayServer-sources-vX.Y.Z.zip` depuis
les releases, ou :

```bash
git clone https://github.com/dexteee-r/Windows-Music-overlay-server.git
```

**Lancez `DEMARRER.bat`.** Au premier lancement, il crée un environnement isolé
(`.venv`), installe les dépendances et ouvre l'application : comptez une à deux
minutes. Les fois suivantes, le démarrage est immédiat.

Pour lancer l'installation seule : `scripts\install.bat`.

---

## 2. Vérifier que tout va bien

Dans l'application : onglet **Contrôle** → bouton **Diagnostic**.
Sans lancer l'application : `scripts\diagnostic.bat`.

Le rapport liste chaque dépendance, le dossier de configuration, les skins
détectés et l'état du port :

```
[OK] Version de Python : 3.13.2
[OK] Dependance Flask
[OK] Dependance winrt
...
Tout est OK : l'application peut demarrer.
```

Chaque ligne en échec indique quoi faire.

---

## 3. Démarrer le serveur

Onglet **Contrôle** → **« Démarrer »**.

L'état passe au vert et l'URL s'affiche : `http://127.0.0.1:49450`.
Cliquez sur **« Copier »**.

> Si le port était occupé, l'application en choisit un autre et vous le dit :
> utilisez l'URL affichée, pas celle de ce guide.

---

## 4. Autoriser votre lecteur

Lancez votre musique (Spotify, Apple Music, YouTube…), puis :

1. Onglet **Paramètres**
2. **« Détecter les applications en cours »**
3. Cochez votre lecteur → **Ajouter la sélection**
4. **Enregistrer**

C'est immédiat, aucun redémarrage n'est nécessaire. Si la détection ne trouve
pas votre lecteur, la [saisie manuelle est décrite dans le guide](GUIDE.md#choisir-ce-qui-saffiche).

---

## 5. Ajouter la source dans OBS

1. Panneau **Sources** → **+** → **Navigateur**
2. Nommez la source (« Musique »), puis **OK**
3. **URL** : collez l'adresse copiée à l'étape 3
4. **Largeur** : `650` — **Hauteur** : `180`
5. Cochez **« Actualiser le navigateur lorsque la scène devient active »**
6. **OK**

L'overlay apparaît. Déplacez-le et redimensionnez-le comme n'importe quelle
source.

---

## 6. Choisir un skin

Onglet **Skins** → cliquez sur un skin pour voir son aperçu → **Appliquer**.

Dans OBS, clic droit sur la source → **Actualiser** pour voir le changement.

---

## Pendant le stream

- L'application doit rester lancée ; la croix la réduit dans la barre des tâches.
- Un clic droit sur l'icône permet de démarrer/arrêter le serveur ou de quitter.
- Pour la lancer automatiquement : onglet **Paramètres** →
  **« Lancer automatiquement au démarrage de Windows »**.

---

## Désinstaller

L'application n'écrit rien en dehors de son dossier, à une exception près :

1. Décochez **« Lancer automatiquement au démarrage de Windows »** dans l'onglet
   Paramètres (cela supprime le raccourci dans le dossier Démarrage).
2. Supprimez le dossier de l'application.

---

## La suite

- [Guide complet](GUIDE.md) — interface, filtres, configuration, API
- [Dépannage](TROUBLESHOOTING.md) — quand ça ne marche pas
