# 🎵 Overlay Musical Apple Music pour Windows 11

Un overlay musical en temps réel qui affiche ce que vous écoutez sur Apple Music, accessible via HTTP pour une intégration dans OBS ou autres logiciels de streaming.

## ✨ Fonctionnalités

- 🎨 Design moderne et élégant avec animations
- 🖼️ Affichage de la pochette d'album
- 📊 Barre de progression en temps réel
- ⏱️ Temps écoulé et durée totale
- 🎚️ Equalizer animé
- 🔄 Mise à jour automatique toutes les 500ms
- 🌐 Accessible via HTTP (parfait pour OBS)

## 📋 Prérequis

- Windows 11
- Python 3.8 ou supérieur
- Apple Music installé et en cours d'exécution
- Connexion Internet (pour l'installation des dépendances)

## 🚀 Installation

### Étape 1 : Installer Python

Si Python n'est pas déjà installé :
1. Téléchargez Python depuis https://www.python.org/downloads/
2. Cochez "Add Python to PATH" lors de l'installation
3. Installez Python

### Étape 2 : Installer les dépendances

Ouvrez PowerShell ou l'Invite de commandes dans le dossier contenant les fichiers et exécutez :

```bash
pip install -r requirements.txt
```

Si vous rencontrez des erreurs, essayez :

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 🎮 Utilisation

### Démarrer le serveur

1. Assurez-vous qu'Apple Music est ouvert et qu'une musique est en cours de lecture
2. Exécutez le serveur :

```bash
python music_overlay_server.py
```

3. Vous devriez voir :
```
============================================================
🎵 Music Overlay Server Started!
============================================================

📺 Overlay URL: http://localhost:5000
📊 API URL: http://localhost:5000/api/current-track

ℹ️  Open the overlay URL in OBS Browser Source
============================================================
```

### Accéder à l'overlay

#### Dans un navigateur web
- Ouvrez : `http://localhost:5000`

#### Dans OBS Studio
1. Ajoutez une source "Navigateur"
2. URL : `http://localhost:5000`
3. Largeur : 600
4. Hauteur : 150
5. Cochez "Rafraîchir le navigateur lorsque la scène devient active"

### Accéder aux données JSON (API)

Pour intégrer dans vos propres applications :
- URL : `http://localhost:5000/api/current-track`
- Format : JSON

Exemple de réponse :
```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "thumbnail": "data:image/jpeg;base64,...",
  "is_playing": true,
  "position": 45,
  "duration": 180
}
```

## 🎨 Personnalisation

Vous pouvez modifier l'apparence de l'overlay en éditant le code HTML/CSS dans le fichier `music_overlay_server.py` :

- **Couleurs** : Modifiez les valeurs dans les `linear-gradient`
- **Taille** : Ajustez `max-width` de `.music-widget`
- **Animations** : Modifiez les `@keyframes`
- **Police** : Changez `font-family`

## 🔧 Dépannage

### Le serveur ne démarre pas
- Vérifiez que le port 5000 n'est pas déjà utilisé
- Essayez de changer le port dans `app.run(port=5000)` vers un autre numéro

### Aucune information n'apparaît
- Vérifiez qu'Apple Music est bien ouvert
- Lancez une musique dans Apple Music
- Redémarrez le serveur

### Erreur lors de l'installation des dépendances
Si vous avez des erreurs avec les anciens packages (comme winsdk), utilisez :
```bash
pip uninstall winsdk -y
pip install -r requirements.txt
```

Les nouveaux packages `winrt-*` sont précompilés et ne nécessitent **PAS** Visual Studio.

### L'image de la pochette ne s'affiche pas
- C'est normal si Apple Music ne fournit pas la pochette
- Une icône par défaut sera affichée

## 🔒 Sécurité

Le serveur est configuré pour être **strictement local** :
- ✅ Accessible uniquement depuis votre PC (127.0.0.1)
- ✅ NON accessible depuis Internet
- ✅ NON accessible depuis d'autres appareils sur votre réseau local
- ✅ Données privées et sécurisées

Si vous souhaitez y accéder depuis un autre appareil sur votre réseau (tablette, téléphone, autre PC), vous devrez modifier `host='127.0.0.1'` en `host='0.0.0.0'` dans le fichier `music_overlay_server.py`.

## 📝 Notes

- Le serveur doit rester actif pour que l'overlay fonctionne
- L'overlay se met à jour automatiquement toutes les 500ms
- Compatible avec tous les logiciels supportant les sources web (OBS, Streamlabs, etc.)

## 🐛 Problèmes connus

- Parfois, au démarrage d'Apple Music, il peut falloir quelques secondes pour que les informations apparaissent
- La rotation de la pochette d'album ne fonctionne que lorsque la musique est en lecture

## 📄 Licence

Projet open source - Libre d'utilisation et de modification

## 🤝 Support

Si vous rencontrez des problèmes, vérifiez :
1. Que Python est correctement installé
2. Que toutes les dépendances sont installées
3. Qu'Apple Music est ouvert et en cours de lecture
4. Que le pare-feu Windows autorise le serveur