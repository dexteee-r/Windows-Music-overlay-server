# 📥 Guide d'Installation - Music Overlay Server

Guide pas à pas pour installer Music Overlay Server sur votre PC Windows 11.

---

## ✅ Prérequis

Avant de commencer, assurez-vous d'avoir :
- Windows 11 (requis pour l'API média)
- Une connexion Internet (pour télécharger Python et les dépendances)

---

## 📦 Étape 1 : Installer Python

### 1.1 Télécharger Python

1. Allez sur https://www.python.org/downloads/
2. Cliquez sur le gros bouton jaune **"Download Python 3.13.x"**
3. Attendez que le téléchargement se termine

### 1.2 Installer Python

1. **Double-cliquez** sur le fichier téléchargé (`python-3.13.x-amd64.exe`)

2. ⚠️ **IMPORTANT** : Avant de cliquer sur "Install Now" :
   - ✅ **Cochez la case** "Add python.exe to PATH" (en bas de la fenêtre)
   - ✅ **Cochez la case** "Use admin privileges when installing py.exe"

3. Cliquez sur **"Install Now"**

4. Attendez la fin de l'installation (1-2 minutes)

5. Cliquez sur **"Close"**

### 1.3 Vérifier l'installation

1. Appuyez sur `Windows + R`
2. Tapez `cmd` et appuyez sur Entrée
3. Dans la fenêtre noire qui s'ouvre, tapez :
   ```
   python --version
   ```
4. Vous devriez voir quelque chose comme :
   ```
   Python 3.13.1
   ```

✅ Si vous voyez un numéro de version, Python est installé correctement !

❌ Si vous voyez "Python n'est pas reconnu...", recommencez l'étape 1.2 en cochant bien "Add python.exe to PATH"

---

## 🚀 Étape 2 : Installer Music Overlay Server

### 2.1 Télécharger le projet

1. Si vous avez téléchargé le projet en ZIP :
   - **Clic droit** sur le fichier ZIP
   - Choisissez **"Extraire tout..."**
   - Choisissez un emplacement (ex: Bureau ou Documents)
   - Cliquez sur **"Extraire"**

2. Vous devriez maintenant avoir un dossier nommé `Windows-Music-overlay-server`

### 2.2 Installer les dépendances

1. Ouvrez le dossier `Windows-Music-overlay-server`

2. **Double-cliquez** sur le fichier `install.bat`

3. Une fenêtre noire s'ouvre et affiche :
   ```
   ============================================================
       INSTALLATION - MUSIC OVERLAY SERVER
   ============================================================

   Vérification de Python...
   Python détecté : 3.13.1

   Installation des dépendances...
   ```

4. Attendez que l'installation se termine (30 secondes à 2 minutes selon votre connexion)

5. Quand vous voyez :
   ```
   ============================================================
   Installation terminée avec succès!
   ============================================================
   ```
   L'installation est terminée !

6. Appuyez sur une touche pour fermer la fenêtre

✅ **Tout est installé !** Vous êtes prêt à utiliser Music Overlay Server.

---

## 🎵 Étape 3 : Premier démarrage

### 3.1 Lancer le serveur

1. **Double-cliquez** sur le fichier `start.bat`

2. Une fenêtre s'ouvre avec :
   ```
   ======================================================================
   🎵 MUSIC OVERLAY SERVER - APPLE MUSIC
   ======================================================================

   📺 URL de l'overlay : http://127.0.0.1:48952
   📊 API JSON         : http://127.0.0.1:48952/api/current-track

   🔒 Serveur local uniquement (127.0.0.1:48952)
   🎯 Mode de filtrage : whitelist

   💡 Pour utiliser dans OBS :
      1. Ajoutez une source 'Navigateur'
      2. URL : http://127.0.0.1:48952
      3. Dimensions : 600 x 150
   ======================================================================
   ```

3. **Laissez cette fenêtre ouverte** (ne la fermez pas)

### 3.2 Tester l'overlay

1. Ouvrez **Apple Music**

2. Lancez **une musique**

3. Ouvrez votre navigateur (Chrome, Firefox, Edge...)

4. Dans la barre d'adresse, tapez :
   ```
   http://127.0.0.1:48952
   ```

5. Appuyez sur **Entrée**

✅ **Vous devriez voir l'overlay** avec :
- La pochette de l'album (qui tourne si la musique joue)
- Le titre de la chanson
- L'artiste
- Une barre de progression
- Un equalizer animé

🎉 **Félicitations !** Music Overlay Server fonctionne !

---

## 🎬 Étape 4 : Intégrer dans OBS

### 4.1 Ajouter l'overlay dans OBS

1. Ouvrez **OBS Studio**

2. Dans "Sources", cliquez sur le bouton **"+"**

3. Choisissez **"Navigateur"**

4. Donnez un nom (ex: "Music Overlay") et cliquez sur **"OK"**

5. Dans la fenêtre qui s'ouvre, configurez :
   - **URL** : `http://127.0.0.1:48952`
   - **Largeur** : `600`
   - **Hauteur** : `150`
   - ✅ Cochez "Rafraîchir le navigateur lorsque la scène devient active"

6. Cliquez sur **"OK"**

### 4.2 Positionner l'overlay

1. Dans OBS, vous devriez voir l'overlay apparaître

2. **Cliquez et déplacez** l'overlay où vous voulez sur votre scène

3. Vous pouvez le **redimensionner** en tirant sur les coins

✅ **L'overlay est maintenant intégré dans votre stream !**

---

## ❓ Problèmes courants

### "Python n'est pas reconnu..."
➡️ Réinstallez Python en cochant bien **"Add python.exe to PATH"**

### "Le port 48952 est déjà utilisé"
➡️ Un autre programme utilise ce port. Solution :
1. Ouvrez `config/settings.json`
2. Changez `"port": 48952` vers `"port": 49500`
3. Redémarrez le serveur avec `start.bat`
4. Utilisez la nouvelle URL dans OBS : `http://127.0.0.1:49500`

### "No track playing" même avec Apple Music ouvert
➡️ Vérifiez que :
1. Apple Music est bien ouvert
2. Une musique est en train de jouer (pas en pause)
3. Le filtre est bien configuré (voir `config/media_filter.json`)

### La pochette d'album ne s'affiche pas
➡️ C'est normal si Apple Music ne fournit pas la pochette. Une icône par défaut sera affichée.

### Le serveur ne démarre pas
➡️ Vérifiez que :
1. Python est bien installé (`python --version` dans CMD)
2. Les dépendances sont installées (relancez `install.bat`)
3. Aucun antivirus ne bloque le serveur

---

## 🔧 Configuration avancée

### Changer le port

1. Ouvrez `config/settings.json`
2. Modifiez la ligne `"port": 48952`
3. Enregistrez le fichier
4. Redémarrez le serveur

### Autoriser d'autres applications

1. Ouvrez `config/media_filter.json`
2. Modifiez le mode ou ajoutez des applications
3. Visitez `http://127.0.0.1:48952/api/reload-config` pour recharger

Pour plus de détails, consultez le [README.md](README.md).

---

## 📞 Besoin d'aide ?

Si vous rencontrez un problème non listé ici :
1. Consultez le [README.md](README.md)
2. Vérifiez que vous avez bien suivi toutes les étapes
3. Ouvrez un "Issue" sur GitHub avec :
   - Votre version de Windows
   - Votre version de Python
   - Le message d'erreur exact

---

**Bon streaming !** 🎵🎬
