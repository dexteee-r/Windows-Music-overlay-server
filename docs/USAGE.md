# Guide d'Utilisation - Music Overlay Server

## 🚀 Démarrage Rapide

### Lancer l'Application

Double-cliquez sur **`launcher.pyw`** à la racine du projet.

L'application se lance sans fenêtre CMD et affiche une icône dans la barre des tâches (system tray).

### Interface Graphique

L'application possède 4 onglets :

#### 1. 🎨 Skins
- **Affiche la liste des 5 skins disponibles**
- **Sélectionnez un skin** dans la liste
- **Cliquez sur "Appliquer"** pour changer de skin
- Le changement sera effectif au prochain rafraîchissement du navigateur/OBS

#### 2. ⚙️ Paramètres

**Configuration du serveur :**
- **Port** : Port du serveur local (par défaut : 49450)
- **Adresse** : 127.0.0.1 (local uniquement)
- **Intervalle de mise à jour** : Temps entre chaque rafraîchissement en secondes

**Filtre Applications Média :**
- **Tout accepter** : Affiche la musique de toutes les applications
- **Whitelist** : Affiche uniquement les apps dans la liste autorisée
- **Blacklist** : Affiche toutes les apps SAUF celles dans la liste bloquée

**Applications autorisées/bloquées :**
- Une application par ligne
- Pour trouver l'ID d'une app :
  1. Mettez mode "Tout accepter"
  2. Démarrez le serveur et lancez votre musique
  3. Visitez `http://127.0.0.1:PORT/api/current-track`
  4. Regardez la valeur de `source_app`

**Démarrage automatique :**
- Cochez pour lancer l'application au démarrage de Windows

⚠️ **Important** : Après avoir modifié les paramètres :
1. Arrêtez le serveur
2. Fermez complètement l'application
3. Relancez l'application
4. Démarrez le serveur

#### 3. 🎮 Contrôle

**Actions :**
- **Démarrer le serveur** : Lance le serveur Flask
- **Arrêter le serveur** : Arrête le serveur (nécessite de fermer l'app)
- **Ouvrir dans navigateur** : Ouvre l'overlay dans votre navigateur par défaut

**État du Serveur :**
- ● **Serveur actif** (vert) : Le serveur fonctionne
- ● **Serveur arrêté** (rouge) : Le serveur est éteint
- **URL** : Affiche l'URL à utiliser dans OBS

**Logs :**
- Affiche tous les messages et actions en temps réel

#### 4. ℹ️ À propos

Informations sur l'application et sa version.

---

## 🎥 Utilisation avec OBS

### Configuration

1. **Démarrez le serveur** depuis l'onglet "Contrôle"
2. Dans OBS, ajoutez une source **"Navigateur"**
3. Configurez la source :
   - **URL** : `http://127.0.0.1:PORT` (voir l'onglet Contrôle)
   - **Largeur** : 800px (ou selon votre skin)
   - **Hauteur** : 200px (ou selon votre skin)
   - Cochez **"Actualiser le navigateur quand la scène devient active"**

4. **Positionnez et redimensionnez** l'overlay dans votre scène

### Changer de Skin en Live

1. Allez dans l'onglet "Skins"
2. Sélectionnez un nouveau skin
3. Cliquez sur "Appliquer"
4. **Actualisez** la source navigateur dans OBS (clic droit > Actualiser)

---

## 🎨 Skins Disponibles

### 1. Zen Minimalist
Design épuré avec fond sombre et animations douces. Parfait pour un stream minimaliste.

### 2. Neon Cyberpunk
Style futuriste avec néons colorés et effets lumineux. Pour les streams gaming/tech.

### 3. Retro Cassette
Design vintage inspiré des cassettes audio des années 80. Look rétro unique.

### 4. RGB Gamer
Bordures RGB animées et style gaming. Idéal pour les streams gaming.

### 5. Glassmorphism Frosted
Effet verre dépoli moderne avec flou en arrière-plan. Style élégant et professionnel.

---

## 🔧 Dépannage

### Le serveur ne démarre pas
- Vérifiez que le port n'est pas déjà utilisé
- Changez le port dans l'onglet Paramètres

### La musique ne s'affiche pas
1. Vérifiez que votre application de musique est dans la whitelist
2. Lancez Apple Music/Spotify et jouez une musique
3. Visitez `/api/current-track` pour voir les données

### Le skin ne change pas
- Actualisez votre navigateur ou OBS après le changement de skin

### L'application ne se lance pas au démarrage
- Vérifiez dans l'onglet Paramètres que "Lancer au démarrage de Windows" est coché
- Vérifiez dans `shell:startup` qu'un raccourci "Music Overlay Server" existe

---

## ⌨️ Raccourcis System Tray

**Clic droit** sur l'icône dans la barre des tâches :
- **Afficher** : Affiche la fenêtre principale
- **Masquer** : Cache la fenêtre dans le tray
- **Démarrer serveur** : Démarre le serveur
- **Arrêter serveur** : Arrête le serveur
- **Quitter** : Ferme complètement l'application

---

## 📝 Notes

- L'application fonctionne **uniquement en local** (127.0.0.1)
- Aucune donnée n'est envoyée sur Internet
- Les configurations sont sauvegardées dans `config/*.json`
- Les skins sont dans `skins/*/skin.html`

---

## 🆘 Support

Pour signaler un bug ou demander de l'aide :
- [GitHub Issues](https://github.com/username/music-overlay-server/issues)
