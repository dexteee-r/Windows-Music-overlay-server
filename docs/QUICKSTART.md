# 🚀 Démarrage rapide

Objectif : votre musique affichée dans OBS en cinq minutes.
L'application est déjà installée ([sinon, c'est ici](INSTALL.md)).

---

## 1. Lancer l'application

Double-cliquez sur **`MusicOverlayServer.exe`** (version exécutable) ou sur
**`DEMARRER.bat`** (version sources).

L'application s'ouvre sur l'onglet **Contrôle**.

## 2. Démarrer le serveur

Cliquez sur **« Démarrer »**.

L'état passe au vert et l'URL s'affiche : `http://127.0.0.1:49450`.
Cliquez sur **« Copier »**.

> Si le port était occupé, l'application en choisit un autre et vous le dit :
> utilisez l'URL affichée, pas celle de ce guide.

## 3. Autoriser votre lecteur

Lancez votre musique (Spotify, Apple Music, YouTube…), puis :

1. Onglet **Paramètres**
2. **« Détecter les applications en cours »**
3. Cochez votre lecteur → **Ajouter la sélection**
4. **Enregistrer**

C'est immédiat, aucun redémarrage n'est nécessaire.

## 4. Ajouter la source dans OBS

1. Dans OBS : panneau **Sources** → **+** → **Navigateur**
2. Nommez la source (« Musique »), puis **OK**
3. **URL** : collez l'adresse copiée à l'étape 2
4. **Largeur** : `650` — **Hauteur** : `180`
5. Cochez **« Actualiser le navigateur lorsque la scène devient active »**
6. **OK**

L'overlay apparaît. Déplacez-le et redimensionnez-le comme n'importe quelle source.

## 5. Choisir un skin

Onglet **Skins** → cliquez sur un skin pour voir son aperçu → **Appliquer**.

Dans OBS, clic droit sur la source → **Actualiser** pour voir le changement.

---

## Pendant le stream

- L'application doit rester lancée ; la croix la réduit dans la barre des tâches.
- Un clic droit sur l'icône permet de démarrer/arrêter le serveur ou de quitter.
- Pour la lancer automatiquement : onglet **Paramètres** →
  **« Lancer automatiquement au démarrage de Windows »**.

---

## La suite

- [Guide d'utilisation complet](USAGE.md)
- [Options de configuration](CONFIGURATION.md)
- [Ça ne marche pas](TROUBLESHOOTING.md)
