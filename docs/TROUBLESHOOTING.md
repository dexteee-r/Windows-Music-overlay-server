# 🔧 Dépannage

**Le premier réflexe :** onglet **Contrôle** → bouton **Diagnostic**
(ou `scripts\diagnostic.bat`). Le rapport indique précisément ce qui manque.

**Le second :** `logs\music-overlay.log`, qui contient le détail des erreurs.

---

## L'application ne démarre pas

### « Python n'est pas reconnu… »

Python n'est pas installé, ou pas dans le PATH. Réinstallez-le depuis
[python.org](https://www.python.org/downloads/) en cochant
**« Add python.exe to PATH »**, puis relancez `DEMARRER.bat`.

### Double-clic sans aucun effet

Lancez `scripts\start_gui.bat` : identique, mais la console reste ouverte et
affiche l'erreur. Joignez cette fenêtre (ou le journal) à votre demande d'aide.

### « Installation incomplète » au lancement

Une dépendance manque. Relancez `scripts\install.bat`, puis
`scripts\diagnostic.bat` pour vérifier.

### L'installation échoue sur `pip install`

- Vérifiez votre connexion internet.
- Un antivirus ou un proxy d'entreprise peut bloquer PyPI.
- Si le dossier est synchronisé (OneDrive, Dropbox), essayez depuis un dossier local.

---

## Aucune musique détectée

### « No track playing » alors que la musique tourne

Dans l'ordre :

1. **Le lecteur alimente-t-il Windows ?** Appuyez sur la touche
   Lecture/Pause du clavier : si la vignette média de Windows n'apparaît pas,
   l'application n'expose pas ses informations et l'overlay ne peut rien afficher.
2. **Le filtre bloque-t-il l'application ?** Onglet Paramètres →
   **Détecter les applications en cours** : celles marquées « déjà autorisée »
   passent le filtre, les autres non.
3. **Test rapide** : passez en mode *Tout accepter* et enregistrez. Si le titre
   apparaît, c'était bien le filtre.

### La détection ne liste pas mon lecteur

La détection ne voit que les applications déclarées auprès des contrôles média
de Windows. Pour les autres, saisissez l'identifiant à la main :

1. Onglet Paramètres → mode **Tout accepter** → **Enregistrer**.
2. Lancez votre musique.
3. Cliquez sur **« Ouvrir la page source_app »** : la page `/api/current-track`
   s'ouvre dans le navigateur.
4. Recopiez la valeur de `source_app` dans **Applications autorisées** (ou
   **bloquées**), une par ligne.
5. Remettez le mode voulu, puis **Enregistrer**.

Si `source_app` est vide, c'est que Windows lui-même ne reçoit rien du lecteur :
aucun réglage de l'overlay ne pourra le détecter.

### La pochette ne s'affiche pas

Certaines applications ne fournissent pas d'image (notamment les navigateurs).
Le skin affiche alors une icône par défaut. Rien à corriger.

### La barre de progression reste bloquée

Tous les lecteurs ne publient pas leur position. Spotify et Apple Music le font,
la plupart des navigateurs non.

---

## Problèmes de serveur

### « Le port est déjà utilisé »

L'application bascule normalement sur le port libre suivant et affiche la
nouvelle URL — pensez à la mettre à jour dans OBS. Pour fixer un autre port :
onglet Paramètres → **Port** → **Enregistrer**.

### Le serveur ne redémarre pas

Ce défaut existait jusqu'à la v2.1.0 : « Arrêter » ne libérait pas réellement le
port. Mettez à jour vers la v3.0.0 ou ultérieure.

### L'overlay reste blanc dans OBS

1. Ouvrez l'URL dans un navigateur (bouton **Ouvrir l'overlay**) : si elle
   fonctionne là, le problème vient d'OBS.
2. Dans OBS : clic droit sur la source → **Actualiser**.
3. Vérifiez que le serveur est **démarré** (état vert) et que l'URL d'OBS
   correspond au port affiché.

### L'overlay est coupé ou minuscule

Ajustez la taille de la source (650 × 180 pour la plupart des skins ;
650 × 220 pour les skins vinyle).

---

## Interface

### Pas d'icône dans la barre des tâches

`pystray` n'est pas installé : relancez `scripts\install.bat`. Sans lui,
l'application fonctionne, mais la croix ferme réellement la fenêtre.

### « Impossible de configurer le démarrage automatique »

`pywin32` est manquant (relancez l'installation), ou une stratégie d'entreprise
interdit l'écriture dans le dossier Démarrage. Solution manuelle : créez
vous-même un raccourci vers `launcher.pyw` (ou vers le `.exe`) dans le dossier
obtenu en tapant `shell:startup` dans la boîte *Exécuter* (`Win + R`).

### Les aperçus de skins sont vides

Trois skins n'ont pas encore de `preview.png` : un visuel générique s'affiche à
la place. Le skin lui-même fonctionne normalement.

---

## Configuration

### Mes changements ne s'appliquent pas

Depuis la v3.0.0, filtres et skins s'appliquent immédiatement ; seul un
changement de port ou d'adresse demande un redémarrage du serveur (proposé
automatiquement). Si vous éditez les fichiers JSON à la main pendant que
l'application tourne, appelez `POST /api/reload-config`.

### J'ai cassé un fichier de configuration

Supprimez le fichier fautif dans `config/` : il sera recréé avec les valeurs par
défaut au prochain lancement.

---

## Demander de l'aide

Ouvrez une [issue GitHub](https://github.com/dexteee-r/Windows-Music-overlay-server/issues)
avec :

1. la sortie de `scripts\diagnostic.bat` ;
2. le contenu de `logs\music-overlay.log` ;
3. ce que vous faisiez et le résultat attendu ;
4. votre version de Windows et le lecteur audio utilisé.
