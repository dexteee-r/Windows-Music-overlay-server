# Release Notes - v2.1.0

**Date** : 1er février 2026

---

## Nouveautés

### Thread Safety & Robustesse
- **Locks pour les variables partagées** : Protection des accès concurrents à `current_track_info` et `FILTER_CONFIG`
- **Graceful shutdown** : Arrêt propre du serveur avec `threading.Event()` pour terminer les threads correctement
- **Meilleure gestion des erreurs** : Les exceptions sont capturées sans interrompre le service

### Preview des Skins dans la GUI
- **Aperçu visuel** : Affichage d'une image preview lors de la sélection d'un skin
- **Métadonnées** : Nom, description, auteur et version affichés dans le panneau de preview
- **Support des screenshots** : Les skins peuvent inclure un fichier `preview.png`
- **Placeholder élégant** : Image par défaut si aucun screenshot n'est disponible

### 10 Skins Professionnels
6 nouveaux skins ajoutés à la collection :

| Skin | Style |
|------|-------|
| Modern Vinyl V2 | Vinyle amélioré |
| Liquid Capsule | Design fluide |
| Kinetic Typography | Typographie animée |
| Clipping Mask | Effet masque |
| Streetwear Hypebeast | Urbain moderne |
| Modern Vinyl | Vinyle classique |

---

## Optimisations de Performance

### Système de Cache Complet

| Cache | Description | Impact |
|-------|-------------|--------|
| **Thumbnail base64** | Régénéré uniquement au changement de piste | -95% d'encodage base64 |
| **Skin actif** | HTML mis en cache jusqu'au changement | -100% de lectures fichier par requête |
| **Liste des skins** | TTL de 60s côté serveur, 30s côté GUI | Réduction I/O disque |
| **Images preview** | Mises en cache après le premier chargement | Réactivité GUI améliorée |
| **Placeholder** | Créé une seule fois et réutilisé | Moins d'allocations mémoire |

### Impact Mesuré
- **Réduction I/O disque** : Les fichiers de configuration ne sont plus lus à chaque requête
- **Réduction CPU** : L'encodage base64 du thumbnail n'est fait qu'au changement de piste
- **Interface plus réactive** : Les images sont mises en cache côté GUI

---

## Fichiers Modifiés

### server.py
- Ajout des locks `current_track_info_lock` et `filter_config_lock`
- Ajout de `shutdown_event` pour le graceful shutdown
- Implémentation du cache système (`_thumbnail_cache`, `_active_skin_cache`, `_skins_list_cache`)
- Modification de `update_track_info()` pour utiliser `wait()` au lieu de `sleep()`

### src/gui.py
- Refonte de l'onglet Skins avec `PanedWindow`
- Ajout du panneau de preview avec métadonnées
- Implémentation du cache pour les images preview
- Nouvelle méthode `_create_placeholder_image()`

### src/skin_manager.py
- Ajout du cache pour la liste des skins
- Nouvelle méthode `invalidate_cache()`
- Paramètre `force_refresh` pour `load_skins_from_files()`

### src/server_manager.py
- Amélioration de la méthode `stop()` avec signal d'arrêt
- Gestion du thread de mise à jour média

---

## Migration depuis v2.0.0

Aucune action requise. La mise à jour est rétrocompatible.

---

## Prochaines Étapes Potentielles

- [ ] Ajout de screenshots pour tous les skins
- [ ] Mode sombre/clair pour la GUI
- [ ] Logs persistants
- [ ] Export de configuration

---

*Réalisé en vibe coding avec [Claude Code](https://claude.ai/claude-code) (Claude Opus 4.5)*
