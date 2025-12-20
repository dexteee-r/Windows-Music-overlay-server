# 🚀 Guide de Démarrage Rapide

## ⚡ Installation Express (2 minutes)

### Étape 1 : Installation
```bash
# Double-cliquez sur ce fichier :
install.bat
```
✅ Crée la structure du projet
✅ Génère les fichiers de configuration
✅ Installe toutes les dépendances Python

### Étape 2 : Démarrage
```bash
# Double-cliquez sur ce fichier :
start_server.bat
```
🎵 Le serveur démarre sur `http://127.0.0.1:48952`

### Étape 3 : Test
1. Ouvrez Apple Music
2. Lancez une musique
3. Visitez : `http://127.0.0.1:48952`

🎉 **Ça fonctionne !**

---

## 🎯 Configuration Rapide

### Scénario 1 : Apple Music uniquement (Recommandé)

Le serveur est **déjà configuré** pour Apple Music uniquement !

Fichier `config/media_filter.json` :
```json
{
  "mode": "whitelist",
  "allowed_apps": ["Music.UI.exe", "Apple Music.exe"]
}
```

**Résultat** :
- ✅ Apple Music → Affiche les infos
- ❌ YouTube, Spotify, etc. → Bloqués

---

### Scénario 2 : Tout autoriser (Mode découverte)

**Fichier** : `config/media_filter.json`

Changez le mode :
```json
{
  "mode": "allow_all"
}
```

**Résultat** :
- ✅ Toutes les applications média → Affichées
- 🔍 Utile pour identifier les noms d'applications

---

### Scénario 3 : Changer le port

**Fichier** : `config/settings.json`

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 50000  ← Changez ici
  }
}
```

Puis redémarrez le serveur.

---

## 🎨 Intégration OBS

### Méthode simple (5 étapes)

1. **Dans OBS**, ajoutez une source → **Navigateur**

2. **URL** : `http://127.0.0.1:48952`

3. **Dimensions** :
   - Largeur : `600`
   - Hauteur : `150`

4. **Options** :
   - ✅ Cochez "Rafraîchir le navigateur lorsque la scène devient active"

5. **Positionnez** la source où vous voulez dans votre scène

✅ **Terminé !**

---

## 🔍 Vérification

### Le serveur fonctionne-t-il ?

Visitez ces URLs dans votre navigateur :

1. **Overlay** : http://127.0.0.1:48952
   - Doit afficher l'interface graphique

2. **API** : http://127.0.0.1:48952/api/current-track
   - Doit retourner du JSON

3. **Config** : http://127.0.0.1:48952/api/filter-config
   - Doit afficher la configuration du filtre

Si toutes ces URLs fonctionnent → **Tout est OK !** ✅

---

## ❓ Problèmes Courants

### Le serveur ne démarre pas

**Solution** :
1. Vérifiez que Python est installé : `python --version`
2. Relancez `install.bat`
3. Essayez de changer le port dans `config/settings.json`

### Aucune info ne s'affiche

**Solution** :
1. Vérifiez qu'Apple Music est ouvert et joue une musique
2. Vérifiez le filtre dans `config/media_filter.json`
3. Testez en mode `"allow_all"` pour identifier le problème

### Erreur "Port already in use"

**Solution** :
1. Ouvrez `config/settings.json`
2. Changez `"port": 48952` vers `"port": 49000` (ou autre)
3. Redémarrez le serveur

---

## 🎯 Prochaines Étapes

Vous avez terminé le démarrage rapide ? Parfait !

📖 **Pour aller plus loin** :
- [README.md](README.md) - Documentation complète
- [CONFIGURATION.md](CONFIGURATION.md) - Guide de configuration détaillé
- [CHANGELOG.md](CHANGELOG.md) - Historique des versions

💡 **Personnalisations avancées** :
- Modifier l'apparence dans `src/music_overlay_server.py`
- Configurer des filtres complexes dans `config/media_filter.json`
- Activer l'accès réseau dans `config/settings.json`

---

## 📞 Support

Des questions ? Consultez la section **🔧 Dépannage** du [README.md](README.md)

---

**Bon streaming !** 🎵🎬
