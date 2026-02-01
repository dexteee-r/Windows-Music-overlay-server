"""
Interface graphique pour Music Overlay Server
Permet de configurer et contrôler le serveur sans toucher au code
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
from pathlib import Path
import threading
from typing import Dict
from PIL import Image, ImageDraw, ImageTk, ImageFont
import pystray

# Imports des managers (logique métier)
from server_manager import ServerManager
from skin_manager import SkinManager
from config_manager import ConfigManager
from startup_manager import StartupManager


class MusicOverlayGUI:
    """Interface graphique principale (Vue uniquement)"""

    def __init__(self, root):
        self.root = root
        self.root.title("Music Overlay Server - Configuration")
        self.root.geometry("700x980")
        self.root.resizable(True, True)

        # Managers (logique métier)
        self.skin_manager = SkinManager()
        self.config_manager = ConfigManager()
        self.startup_manager = StartupManager()

        # ServerManager sera créé avec les bons paramètres au démarrage
        self.server_manager: ServerManager
        self._init_server_manager()

        # Dictionnaire pour stocker les skins {name: skin_object}
        self.skins_data: Dict[str, dict] = {}

        # Référence pour l'image de preview (éviter garbage collection)
        self.preview_image = None

        # System Tray
        self.tray_icon = None
        self.setup_system_tray()

        # Gérer la fermeture de la fenêtre (minimiser dans le tray au lieu de quitter)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        # Créer le système de tabs
        self.create_tabs()

        # Charger la liste des skins au démarrage
        self.root.after(500, self.load_skins_list)

        # Afficher le statut du démarrage automatique dans les logs
        self.root.after(600, self.log_startup_status)

    def create_tabs(self):
        """Crée le système d'onglets"""
        # Notebook (conteneur de tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Créer les 4 tabs
        self.tab_skins = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        self.tab_control = ttk.Frame(self.notebook)
        self.tab_about = ttk.Frame(self.notebook)

        # Ajouter les tabs au notebook
        self.notebook.add(self.tab_skins, text="  Skins  ")
        self.notebook.add(self.tab_settings, text="  Paramètres  ")
        self.notebook.add(self.tab_control, text="  Contrôle  ")
        self.notebook.add(self.tab_about, text="  À propos  ")

        # Remplir chaque tab
        self.create_skins_tab()
        self.create_settings_tab()
        self.create_control_tab()
        self.create_about_tab()

    def create_skins_tab(self):
        """Tab Skins : Liste des skins avec panneau de preview"""
        # Frame principal
        main_frame = ttk.Frame(self.tab_skins, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Titre
        title = ttk.Label(main_frame, text="Sélection du Skin", font=('Segoe UI', 14, 'bold'))
        title.pack(pady=(0, 10))

        # PanedWindow horizontal (liste à gauche, preview à droite)
        paned = ttk.PanedWindow(main_frame, orient='horizontal')
        paned.pack(fill='both', expand=True, pady=(0, 10))

        # === PANNEAU GAUCHE : Liste des skins ===
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        # Frame pour la liste
        list_frame = ttk.LabelFrame(left_frame, text="Skins disponibles", padding=10)
        list_frame.pack(fill='both', expand=True)

        # Listbox avec scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.skins_listbox = tk.Listbox(list_frame, height=12, font=('Segoe UI', 10),
                                        yscrollcommand=scrollbar.set, exportselection=False)
        self.skins_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.skins_listbox.yview)

        # Bind la sélection pour mettre à jour la preview
        self.skins_listbox.bind('<<ListboxSelect>>', self.on_skin_selected)

        # Bouton appliquer
        self.apply_skin_btn = ttk.Button(left_frame, text="Appliquer le skin sélectionné",
                                        command=self.apply_selected_skin)
        self.apply_skin_btn.pack(pady=(10, 0), fill='x')

        # === PANNEAU DROIT : Preview et détails ===
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        # Frame preview
        preview_frame = ttk.LabelFrame(right_frame, text="Aperçu", padding=10)
        preview_frame.pack(fill='both', expand=True)

        # Image de preview
        self.preview_image_label = ttk.Label(preview_frame)
        self.preview_image_label.pack(pady=(0, 10))

        # Créer un placeholder initial
        self.create_placeholder_preview("Sélectionnez un skin")

        # Métadonnées
        metadata_frame = ttk.Frame(preview_frame)
        metadata_frame.pack(fill='x', pady=(10, 0))

        # Nom du skin
        self.preview_name = ttk.Label(metadata_frame, text="", font=('Segoe UI', 12, 'bold'))
        self.preview_name.pack(anchor='w')

        # Description
        self.preview_description = ttk.Label(metadata_frame, text="", font=('Segoe UI', 9),
                                             wraplength=450, justify='left')
        self.preview_description.pack(anchor='w', pady=(5, 0))

        # Auteur et version
        info_frame = ttk.Frame(metadata_frame)
        info_frame.pack(fill='x', pady=(10, 0))

        self.preview_author = ttk.Label(info_frame, text="", font=('Segoe UI', 8),
                                        foreground='gray')
        self.preview_author.pack(anchor='w')

        self.preview_version = ttk.Label(info_frame, text="", font=('Segoe UI', 8),
                                         foreground='gray')
        self.preview_version.pack(anchor='w')

        # Label skin actif (en bas)
        self.active_skin_label = ttk.Label(main_frame, text="Skin actif : Chargement...",
                                          font=('Segoe UI', 9, 'italic'))
        self.active_skin_label.pack(pady=(5, 0))

    def create_settings_tab(self):
        """Tab Paramètres : Formulaire de configuration"""
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(self.tab_settings)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Titre
        title = ttk.Label(main_frame, text="Configuration du Serveur", font=('Segoe UI', 14, 'bold'))
        title.pack(pady=(0, 15))

        # Frame pour le formulaire
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)

        # Section Serveur
        server_frame = ttk.LabelFrame(form_frame, text="Paramètres Serveur", padding=10)
        server_frame.pack(fill='x', pady=(0, 10))

        # Avertissement
        warning_frame = ttk.Frame(server_frame)
        warning_frame.pack(fill='x', pady=(0, 10))
        warning_label = ttk.Label(warning_frame,
            text="⚠️ Arrêtez le serveur avant de modifier ces paramètres",
            font=('Segoe UI', 9, 'italic'),
            foreground='#d97706')
        warning_label.pack(anchor='w')

        # Port
        port_row = ttk.Frame(server_frame)
        port_row.pack(fill='x', pady=5)
        ttk.Label(port_row, text="Port :", width=20).pack(side='left')
        self.port_entry = ttk.Entry(port_row, width=15)
        self.port_entry.insert(0, "48952")
        self.port_entry.pack(side='left')
        ttk.Label(port_row, text="(1024-65535)", font=('Segoe UI', 8)).pack(side='left', padx=5)

        # Host
        host_row = ttk.Frame(server_frame)
        host_row.pack(fill='x', pady=5)
        ttk.Label(host_row, text="Adresse :", width=20).pack(side='left')
        self.host_entry = ttk.Entry(host_row, width=30)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(side='left')

        # Refresh interval
        refresh_row = ttk.Frame(server_frame)
        refresh_row.pack(fill='x', pady=5)
        ttk.Label(refresh_row, text="Intervalle de mise à jour :", width=20).pack(side='left')
        self.refresh_entry = ttk.Entry(refresh_row, width=10)
        self.refresh_entry.insert(0, "0.5")
        self.refresh_entry.pack(side='left')
        ttk.Label(refresh_row, text="secondes", font=('Segoe UI', 8)).pack(side='left', padx=5)

        # Section Filtre Média
        filter_frame = ttk.LabelFrame(form_frame, text="Filtre Applications Média", padding=10)
        filter_frame.pack(fill='x', pady=(0, 10))

        # Mode de filtrage
        mode_label = ttk.Label(filter_frame, text="Mode de filtrage :")
        mode_label.pack(anchor='w', pady=(0, 5))

        self.filter_mode = tk.StringVar(value="whitelist")
        ttk.Radiobutton(filter_frame, text="Tout accepter", variable=self.filter_mode,
                       value="all").pack(anchor='w')
        ttk.Radiobutton(filter_frame, text="Whitelist (uniquement apps autorisées)",
                       variable=self.filter_mode, value="whitelist").pack(anchor='w')
        ttk.Radiobutton(filter_frame, text="Blacklist (bloquer certaines apps)",
                       variable=self.filter_mode, value="blacklist").pack(anchor='w')

        # Applications autorisées (whitelist)
        ttk.Label(filter_frame, text="Applications autorisées (une par ligne) :",
                 font=('Segoe UI', 9)).pack(anchor='w', pady=(10, 5))
        self.allowed_apps_text = tk.Text(filter_frame, height=3, width=50, font=('Consolas', 8))
        self.allowed_apps_text.pack(fill='x', padx=5)

        # Applications bloquées (blacklist)
        ttk.Label(filter_frame, text="Applications bloquées (une par ligne) :",
                 font=('Segoe UI', 9)).pack(anchor='w', pady=(10, 5))
        self.blocked_apps_text = tk.Text(filter_frame, height=3, width=50, font=('Consolas', 8))
        self.blocked_apps_text.pack(fill='x', padx=5)

        # Aide pour trouver l'ID d'une app
        help_frame = ttk.Frame(filter_frame)
        help_frame.pack(fill='x', pady=(10, 0))
        ttk.Label(help_frame, text="💡 Pour trouver l'ID d'une app :",
                 font=('Segoe UI', 8, 'italic')).pack(anchor='w')
        ttk.Label(help_frame, text="   1. Mettez mode 'Tout accepter' et démarrez le serveur",
                 font=('Segoe UI', 8)).pack(anchor='w')
        ttk.Label(help_frame, text="   2. Lancez votre musique",
                 font=('Segoe UI', 8)).pack(anchor='w')
        ttk.Label(help_frame, text="   3. Visitez http://127.0.0.1:PORT/api/current-track",
                 font=('Segoe UI', 8)).pack(anchor='w')
        ttk.Label(help_frame, text="   4. Regardez la valeur de 'source_app'",
                 font=('Segoe UI', 8)).pack(anchor='w')

        # Section Démarrage
        startup_frame = ttk.LabelFrame(form_frame, text="Démarrage Automatique", padding=10)
        startup_frame.pack(fill='x', pady=(0, 10))

        self.auto_start_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(startup_frame, text="Lancer au démarrage de Windows",
                       variable=self.auto_start_var).pack(anchor='w')

        # Bouton enregistrer
        save_btn = ttk.Button(form_frame, text="Enregistrer les paramètres",
                             command=self.save_settings)
        save_btn.pack(pady=15)

        # Charger les paramètres existants
        self.load_settings()

    def create_control_tab(self):
        """Tab Contrôle : Gestion du serveur"""
        main_frame = ttk.Frame(self.tab_control, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Titre
        title = ttk.Label(main_frame, text="Contrôle du Serveur", font=('Segoe UI', 14, 'bold'))
        title.pack(pady=(0, 15))

        # Frame pour les boutons de contrôle
        control_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        control_frame.pack(fill='x', pady=(0, 10))

        # Boutons de contrôle
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill='x')

        self.start_btn = ttk.Button(btn_frame, text="Démarrer le serveur", width=20,
                                    command=self.start_server)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Arrêter le serveur", width=20,
                                   command=self.stop_server, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        self.browser_btn = ttk.Button(btn_frame, text="Ouvrir dans navigateur", width=20,
                                     command=self.open_in_browser)
        self.browser_btn.pack(side='left', padx=5)

        # Status
        status_frame = ttk.LabelFrame(main_frame, text="État du Serveur", padding=10)
        status_frame.pack(fill='x', pady=(0, 10))

        self.status_label = ttk.Label(status_frame, text="● Serveur arrêté",
                                     font=('Segoe UI', 10), foreground='red')
        self.status_label.pack(anchor='w')

        self.url_label = ttk.Label(status_frame, text=f"URL : {self.server_manager.get_url()}",
                                  font=('Segoe UI', 9))
        self.url_label.pack(anchor='w', pady=(5, 0))

        # Zone de logs
        logs_frame = ttk.LabelFrame(main_frame, text="Logs", padding=10)
        logs_frame.pack(fill='both', expand=True)

        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=10,
                                                   font=('Consolas', 9),
                                                   state='disabled',
                                                   bg='#f0f0f0')
        self.logs_text.pack(fill='both', expand=True)

        # Ajouter un message de démo
        self.add_log("Interface initialisée. Prêt à démarrer le serveur.")

    def create_about_tab(self):
        """Tab À propos : Informations sur l'application"""
        main_frame = ttk.Frame(self.tab_about, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Logo / Titre
        title = ttk.Label(main_frame, text="Music Overlay Server",
                         font=('Segoe UI', 18, 'bold'))
        title.pack(pady=(10, 5))

        version = ttk.Label(main_frame, text="Version 1.0",
                           font=('Segoe UI', 10))
        version.pack(pady=(0, 20))

        # Description
        desc_text = """
Serveur d'overlay musical pour OBS et autres logiciels de streaming.
Affiche en temps réel les informations de lecture depuis Apple Music
et autres applications média Windows.

Fonctionnalités :
  • 5 skins personnalisables
  • Configuration via interface graphique
  • Filtre des applications média
  • API REST pour intégrations personnalisées
  • Compatible OBS Browser Source

Développé pour Windows 10/11
Utilise l'API Windows Media Transport Controls
        """

        desc = ttk.Label(main_frame, text=desc_text,
                        font=('Segoe UI', 9), justify='left')
        desc.pack(pady=(0, 20))

        # Liens
        links_frame = ttk.Frame(main_frame)
        links_frame.pack()

        ttk.Label(links_frame, text="Port serveur par défaut : 48952",
                 font=('Segoe UI', 9, 'bold')).pack(pady=2)
        ttk.Label(links_frame, text="API : /api/current-track, /api/list-skins",
                 font=('Segoe UI', 9)).pack(pady=2)

        # Copyright
        copyright_label = ttk.Label(main_frame,
                                   text="\n© 2024 Music Overlay Server",
                                   font=('Segoe UI', 8))
        copyright_label.pack(side='bottom', pady=10)

    def add_log(self, message):
        """Ajoute un message dans la zone de logs"""
        self.logs_text.config(state='normal')
        self.logs_text.insert(tk.END, f"{message}\n")
        self.logs_text.see(tk.END)
        self.logs_text.config(state='disabled')

    # ========================================================================
    # MÉTHODES DE GESTION DU SERVEUR (utilise ServerManager)
    # ========================================================================

    def start_server(self):
        """Démarre le serveur Flask"""
        self.add_log("[INFO] Démarrage du serveur...")

        def on_success():
            self.update_server_status(True)
            self.add_log(f"[OK] Serveur démarré sur {self.server_manager.get_url()}")
            # Charger la liste des skins depuis l'API
            self.load_skins_list()

        def on_error(error):
            self.update_server_status(False)
            self.add_log(f"[ERROR] {error}")

        check_callback = self.server_manager.start(on_success, on_error)

        # Planifier la vérification après 1.5s
        if check_callback:
            self.root.after(1500, check_callback)

    def stop_server(self):
        """Arrête le serveur Flask"""
        self.server_manager.stop()
        self.update_server_status(False)
        self.add_log("[INFO] Serveur marqué comme arrêté")
        self.add_log("[INFO] Pour arrêter complètement Flask, fermez l'application")

        # Recharger depuis les fichiers maintenant que le serveur est "arrêté"
        self.load_skins_list()

    def update_server_status(self, running):
        """Met à jour l'interface selon l'état du serveur"""
        if running:
            self.status_label.config(text="● Serveur actif", foreground='green')
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
        else:
            self.status_label.config(text="● Serveur arrêté", foreground='red')
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')

    def open_in_browser(self):
        """Ouvre l'overlay dans le navigateur par défaut"""
        url = self.server_manager.get_url()

        if not self.server_manager.running:
            response = messagebox.askyesno(
                "Serveur arrêté",
                "Le serveur n'est pas démarré. Voulez-vous le démarrer maintenant ?"
            )
            if response:
                self.start_server()
                # Attendre que le serveur démarre puis ouvrir le navigateur
                self.root.after(2000, lambda: webbrowser.open(url))
            return

        webbrowser.open(url)
        self.add_log(f"[INFO] Ouverture de {url} dans le navigateur")

    # ========================================================================
    # MÉTHODES DE GESTION DES SKINS (utilise SkinManager)
    # ========================================================================

    def load_skins_list(self):
        """Charge la liste des skins (depuis API si serveur actif, sinon fichiers)"""
        data = None

        # Essayer de charger depuis l'API si le serveur tourne
        if self.server_manager.running:
            data = self.skin_manager.load_skins_from_api(self.server_manager.get_url())
            if data and data.get('count', 0) > 0:
                # API a retourné des données valides
                pass
            else:
                # API a échoué ou retourné 0 skins, fallback sur fichiers
                data = None

        # Sinon charger depuis les fichiers
        if data is None:
            data = self.skin_manager.load_skins_from_files()

        # Remplir la listbox
        self.populate_skins_list(data)

    def populate_skins_list(self, data):
        """Remplit la listbox avec les skins"""
        skins = data.get('skins', [])
        active_skin_id = data.get('active_skin', '')

        # Vider la listbox
        self.skins_listbox.delete(0, tk.END)
        self.skins_data = {}

        # Remplir avec les skins (stocker l'objet complet)
        for skin in skins:
            skin_name = skin.get('name', skin.get('id', ''))
            self.skins_listbox.insert(tk.END, skin_name)
            self.skins_data[skin_name] = skin  # Stocker l'objet complet

        # Mettre à jour le label du skin actif
        active_name = next((name for name, skin in self.skins_data.items()
                           if skin.get('id') == active_skin_id), "Aucun")
        self.active_skin_label.config(text=f"Skin actif : {active_name}")

        # Sélectionner le skin actif dans la liste
        for i, (name, skin) in enumerate(self.skins_data.items()):
            if skin.get('id') == active_skin_id:
                self.skins_listbox.selection_set(i)
                self.skins_listbox.see(i)
                # Mettre à jour la preview pour le skin actif
                self.update_preview(skin)
                break

        self.add_log(f"[OK] {len(skins)} skins chargés")

    def apply_selected_skin(self):
        """Applique le skin sélectionné dans la liste"""
        selection = self.skins_listbox.curselection()

        if not selection:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un skin dans la liste")
            return

        selected_name = self.skins_listbox.get(selection[0])
        selected_skin = self.skins_data.get(selected_name)

        if not selected_skin:
            messagebox.showerror("Erreur", "Impossible de trouver le skin sélectionné")
            return

        selected_id = selected_skin.get('id')

        # Si le serveur est actif, utiliser l'API
        if self.server_manager.running:
            result = self.skin_manager.set_active_skin_api(
                self.server_manager.get_url(),
                selected_id
            )

            if result.get('success'):
                self.active_skin_label.config(text=f"Skin actif : {selected_name}")
                self.add_log(f"[OK] Skin changé : {selected_name}")
                messagebox.showinfo("Succès",
                    f"Skin changé pour : {selected_name}\n\nActualisez votre navigateur ou OBS pour voir le changement.")
            else:
                messagebox.showerror("Erreur", result.get('message', 'Erreur inconnue'))

        else:
            # Sinon modifier directement le fichier
            if self.skin_manager.set_active_skin_file(selected_id):
                self.active_skin_label.config(text=f"Skin actif : {selected_name}")
                self.add_log(f"[OK] Skin changé : {selected_name} (redémarrez le serveur)")
                messagebox.showinfo("Succès",
                    f"Skin changé pour : {selected_name}\n\nDémarrez le serveur pour voir le changement.")
            else:
                messagebox.showerror("Erreur", "Impossible de sauvegarder le skin")

    def on_skin_selected(self, event):
        """Appelé quand l'utilisateur sélectionne un skin dans la liste"""
        selection = self.skins_listbox.curselection()
        if not selection:
            return

        skin_name = self.skins_listbox.get(selection[0])
        skin = self.skins_data.get(skin_name)

        if skin:
            self.update_preview(skin)

    def update_preview(self, skin):
        """Met à jour le panneau de preview avec les infos du skin"""
        # Mettre à jour les labels de métadonnées
        self.preview_name.config(text=skin.get('name', 'Skin inconnu'))
        self.preview_description.config(text=skin.get('description', 'Aucune description disponible'))
        self.preview_author.config(text=f"Auteur : {skin.get('author', 'Inconnu')}")
        self.preview_version.config(text=f"Version : {skin.get('version', '1.0')}")

        # Charger l'image de preview
        self.load_preview_image(skin.get('id', ''))

    def load_preview_image(self, skin_id):
        """Charge l'image de preview si disponible, sinon affiche un placeholder"""
        if not skin_id:
            self.create_placeholder_preview("Aucun skin")
            return

        # Chercher preview.png dans le dossier du skin
        preview_path = Path(__file__).parent.parent / "skins" / skin_id / "preview.png"

        if preview_path.exists():
            try:
                # Charger l'image
                img = Image.open(preview_path)

                # Utiliser thumbnail() pour conserver le ratio d'aspect
                max_size = (500, 300)
                img.thumbnail(max_size, Image.LANCZOS)

                photo = ImageTk.PhotoImage(img)

                self.preview_image_label.config(image=photo)
                self.preview_image = photo  # Garder la référence
            except Exception:
                # En cas d'erreur, afficher le placeholder
                self.create_placeholder_preview(skin_id)
        else:
            # Pas de preview.png, créer un placeholder
            self.create_placeholder_preview(skin_id)

    def create_placeholder_preview(self, text):
        """Crée une image placeholder avec le texte donné"""
        # Créer une image de fond (taille augmentée)
        width, height = 500, 300
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)

        # Dessiner un cadre avec un dégradé simulé
        draw.rectangle([2, 2, width-3, height-3], outline='#4a4a6a', width=2)

        # Icône de musique au centre (plus grande)
        center_x, center_y = width // 2, height // 2 - 20

        # Note de musique stylisée
        draw.ellipse([center_x - 25, center_y + 10, center_x + 5, center_y + 40],
                    fill='#667eea', outline='#764ba2', width=2)
        draw.rectangle([center_x + 2, center_y - 40, center_x + 8, center_y + 25],
                      fill='#667eea')
        draw.ellipse([center_x + 5, center_y - 45, center_x + 15, center_y - 35],
                    fill='#764ba2')

        # Ajouter le texte en bas
        try:
            font = ImageFont.truetype("segoeui.ttf", 14)
        except:
            font = ImageFont.load_default()

        # Texte "Pas de preview disponible"
        label = "Pas d'aperçu disponible"
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = center_y + 60

        draw.text((x, y), label, fill='#888888', font=font)

        # Convertir en PhotoImage
        photo = ImageTk.PhotoImage(img)
        self.preview_image_label.config(image=photo)
        self.preview_image = photo  # Garder la référence

    # ========================================================================
    # MÉTHODES DE GESTION DES PARAMÈTRES (utilise ConfigManager)
    # ========================================================================

    def load_settings(self):
        """Charge les paramètres depuis settings.json et media_filter.json"""
        # Charger settings.json
        settings = self.config_manager.load_settings()

        # Mettre à jour les champs
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, str(settings["port"]))

        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, settings["host"])

        self.refresh_entry.delete(0, tk.END)
        self.refresh_entry.insert(0, str(settings["refresh_interval"]))

        # Charger media_filter.json
        filter_config = self.config_manager.load_filter_config()
        self.filter_mode.set(filter_config["mode"])

        # Charger les listes d'applications
        self.allowed_apps_text.delete('1.0', tk.END)
        self.allowed_apps_text.insert('1.0', '\n'.join(filter_config["allowed_apps"]))

        self.blocked_apps_text.delete('1.0', tk.END)
        self.blocked_apps_text.insert('1.0', '\n'.join(filter_config["blocked_apps"]))

        # Charger l'état du démarrage automatique
        is_startup_enabled = self.startup_manager.is_enabled()
        self.auto_start_var.set(is_startup_enabled)

        # Log seulement si logs_text existe (pour éviter l'erreur au démarrage)
        if hasattr(self, 'logs_text'):
            self.add_log(f"[DEBUG] Démarrage auto détecté : {is_startup_enabled}")

    def log_startup_status(self):
        """Affiche le statut du démarrage automatique dans les logs"""
        is_enabled = self.startup_manager.is_enabled()
        if is_enabled:
            self.add_log("[INFO] Démarrage automatique activé")
        else:
            self.add_log("[INFO] Démarrage automatique désactivé")

    def save_settings(self):
        """Sauvegarde les paramètres dans settings.json et media_filter.json"""
        try:
            # Récupérer les valeurs des champs
            port = self.port_entry.get()
            host = self.host_entry.get()
            refresh_interval = self.refresh_entry.get()

            # Sauvegarder settings.json
            self.config_manager.save_settings(port, host, refresh_interval)

            # Sauvegarder media_filter.json
            filter_mode = self.filter_mode.get()

            # Récupérer les listes d'applications depuis les champs de texte
            allowed_apps_raw = self.allowed_apps_text.get('1.0', tk.END).strip()
            blocked_apps_raw = self.blocked_apps_text.get('1.0', tk.END).strip()

            # Convertir en listes (une app par ligne, en supprimant les lignes vides)
            allowed_apps = [app.strip() for app in allowed_apps_raw.split('\n') if app.strip()]
            blocked_apps = [app.strip() for app in blocked_apps_raw.split('\n') if app.strip()]

            self.config_manager.save_filter_config(
                filter_mode,
                allowed_apps,
                blocked_apps
            )

            # Gérer le démarrage automatique
            auto_start_enabled = self.auto_start_var.get()
            success, message = self.startup_manager.toggle(auto_start_enabled)
            if not success:
                self.add_log(f"[ERROR] Démarrage auto : {message}")
                messagebox.showwarning("Démarrage automatique", f"Impossible de configurer le démarrage automatique :\n{message}")
            else:
                status = "activé" if auto_start_enabled else "désactivé"
                self.add_log(f"[OK] Démarrage automatique {status}")

            # Recréer le ServerManager avec les nouveaux paramètres
            self._init_server_manager()

            messagebox.showinfo("Succès",
                "Paramètres sauvegardés avec succès !\n\n"
                "⚠️ Pour appliquer les changements :\n"
                "1. Arrêtez le serveur (bouton 'Arrêter le serveur')\n"
                "2. Fermez complètement l'application\n"
                "3. Relancez l'application\n"
                "4. Démarrez le serveur")
            self.add_log("[OK] Paramètres sauvegardés")
            self.add_log(f"[INFO] Nouveau port : {port}")

        except ValueError as e:
            messagebox.showerror("Erreur de validation", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder : {e}")

    # ========================================================================
    # MÉTHODES SYSTEM TRAY
    # ========================================================================

    def create_tray_icon(self):
        """Crée une icône simple pour le system tray"""
        # Créer une image 64x64 avec un cercle coloré
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='white')
        dc = ImageDraw.Draw(image)

        # Dessiner un cercle avec des notes de musique
        dc.ellipse([8, 8, 56, 56], fill='#667eea', outline='#764ba2', width=3)

        # Dessiner une note de musique simplifiée
        dc.ellipse([24, 30, 32, 38], fill='white')
        dc.rectangle([31, 20, 34, 38], fill='white')

        return image

    def setup_system_tray(self):
        """Configure l'icône dans le system tray"""
        icon_image = self.create_tray_icon()

        # Créer le menu contextuel
        menu = pystray.Menu(
            pystray.MenuItem("Afficher", self.show_window, default=True),
            pystray.MenuItem("Masquer", self.hide_window),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Démarrer serveur", self.tray_start_server),
            pystray.MenuItem("Arrêter serveur", self.tray_stop_server),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quitter", self.quit_app)
        )

        # Créer l'icône
        self.tray_icon = pystray.Icon(
            "music_overlay",
            icon_image,
            "Music Overlay Server",
            menu
        )

        # Lancer l'icône dans un thread séparé
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()

    def show_window(self, icon=None, item=None):
        """Affiche la fenêtre principale"""
        self.root.after(0, self._show_window)

    def _show_window(self):
        """Affiche la fenêtre (doit être appelé depuis le thread principal)"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self, icon=None, item=None):
        """Masque la fenêtre dans le system tray"""
        self.root.after(0, self._hide_window)

    def _hide_window(self):
        """Masque la fenêtre (doit être appelé depuis le thread principal)"""
        self.root.withdraw()

    def tray_start_server(self, icon=None, item=None):
        """Démarre le serveur depuis le system tray"""
        self.root.after(0, self.start_server)

    def tray_stop_server(self, icon=None, item=None):
        """Arrête le serveur depuis le system tray"""
        self.root.after(0, self.stop_server)

    def quit_app(self, icon=None, item=None):
        """Quitte complètement l'application"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()

    def _init_server_manager(self):
        """Initialise le ServerManager avec les paramètres de settings.json"""
        settings = self.config_manager.load_settings()
        self.server_manager = ServerManager(
            host=settings["host"],
            port=settings["port"]
        )

        # Mettre à jour l'URL affichée si le label existe déjà
        if hasattr(self, 'url_label'):
            self.url_label.config(text=f"URL : {self.server_manager.get_url()}")


def main():
    """Point d'entrée de l'application"""
    root = tk.Tk()
    app = MusicOverlayGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
