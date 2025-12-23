# 🔧 Dépannage - Music Overlay Server

## Le launcher.pyw ne se lance pas

### Solution 1: Utiliser le script de test

1. **Double-cliquez sur** `scripts/test_install.bat`
2. Le script va tester votre installation
3. **Prenez une capture d'écran** du résultat
4. Suivez les instructions affichées

### Solution 2: Lancer avec affichage des erreurs

Au lieu de `launcher.pyw`, utilisez :

1. **Double-cliquez sur** `scripts/start_gui.bat`
2. Une fenêtre CMD s'ouvrira avec les détails
3. Si une erreur apparaît, **prenez une capture d'écran**

### Solution 3: Lancer en ligne de commande

1. **Ouvrez CMD** dans le dossier du projet
2. Tapez : `python launcher.pyw`
3. Les erreurs s'afficheront dans la console
4. **Copiez le message d'erreur**

## Problèmes courants

### ❌ "Python n'est pas reconnu"

**Cause** : Python n'est pas installé ou pas dans le PATH

**Solution** :
1. Installez Python 3.13+ : https://www.python.org/downloads/
2. **IMPORTANT** : Cochez "Add python.exe to PATH" pendant l'installation
3. Redémarrez votre PC
4. Relancez `scripts/install.bat`

### ❌ "No module named 'tkinter'"

**Cause** : tkinter n'est pas installé avec Python

**Solution** :
1. Réinstallez Python
2. Dans l'installateur, cliquez sur "Customize installation"
3. **Cochez "tcl/tk and IDLE"**
4. Terminez l'installation

### ❌ "No module named 'flask'" ou autres modules

**Cause** : Les dépendances ne sont pas installées

**Solution** :
1. Lancez `scripts/install.bat`
2. Attendez la fin de l'installation
3. Relancez `launcher.pyw`

### ❌ Rien ne se passe (aucune fenêtre, aucune erreur)

**Cause** : L'extension .pyw cache les erreurs

**Solution** :
1. Lancez `scripts/start_gui.bat` à la place
2. Vous verrez les erreurs s'il y en a

### ❌ "tkinter.TclError" ou erreurs graphiques

**Cause** : Problème avec l'affichage graphique

**Solution** :
1. Vérifiez que vous êtes sur Windows (pas WSL ou terminal SSH)
2. Vérifiez que vous avez une interface graphique active
3. Essayez de redémarrer votre PC

## Scripts de diagnostic

| Script | Utilité |
|--------|---------|
| `scripts/test_install.bat` | Teste toute l'installation (recommandé) |
| `scripts/start_gui.bat` | Lance la GUI avec affichage des erreurs |
| `scripts/install.bat` | Installe/réinstalle les dépendances |
| `scripts/start.bat` | Lance le serveur seul (sans GUI) |

## Vérification manuelle

### Tester Python

Ouvrez CMD et tapez :
```bash
python --version
```
Doit afficher : `Python 3.13.x` ou supérieur

### Tester tkinter

```bash
python -c "import tkinter; print('tkinter OK')"
```
Doit afficher : `tkinter OK`

### Tester les dépendances

```bash
cd "chemin\vers\Windows-Music-overlay-server"
python -c "import flask, pystray, winrt; print('Tout OK')"
```
Doit afficher : `Tout OK`

### Tester le launcher manuellement

```bash
cd "chemin\vers\Windows-Music-overlay-server"
python launcher.pyw
```
La GUI doit s'ouvrir. Si erreur, copiez le message.

## Besoin d'aide ?

Si aucune solution ne fonctionne :

1. **Lancez** `scripts/test_install.bat`
2. **Prenez une capture d'écran** complète de la fenêtre
3. **Envoyez** la capture avec votre message d'erreur

## Configuration minimale requise

- ✅ **Windows 10/11** (64-bit)
- ✅ **Python 3.13+** avec tkinter
- ✅ **Connexion internet** (pour installation des dépendances)
- ✅ **Interface graphique active** (pas WSL/SSH)
