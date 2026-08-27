"""Onglet Skins : liste des skins installés, aperçu et activation."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

from PIL import Image, ImageTk

from ..skins import Skin, SkinNotFoundError
from . import assets

if TYPE_CHECKING:
    from .window import MusicOverlayWindow

logger = logging.getLogger(__name__)

PREVIEW_MAX_SIZE = (480, 290)


class SkinsTab(ttk.Frame):
    """Sélection du skin, avec aperçu et métadonnées."""

    def __init__(self, parent: tk.Misc, app: MusicOverlayWindow):
        super().__init__(parent)
        self.app = app

        self._skins_by_label: dict[str, Skin] = {}
        self._preview_cache: dict[str, ImageTk.PhotoImage] = {}
        self._placeholder: ImageTk.PhotoImage | None = None
        self._current_preview: ImageTk.PhotoImage | None = None

        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Selection du skin", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        paned = ttk.PanedWindow(frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        list_frame = ttk.LabelFrame(left, text="Skins installes", padding=8)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.listbox = tk.Listbox(
            list_frame,
            height=12,
            font=("Segoe UI", 10),
            yscrollcommand=scrollbar.set,
            exportselection=False,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_selection)
        self.listbox.bind("<Double-Button-1>", lambda _event: self.apply_selected())

        buttons = ttk.Frame(left)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Appliquer", command=self.apply_selected).pack(fill="x", pady=2)
        ttk.Button(buttons, text="Rafraichir la liste", command=self.refresh).pack(fill="x", pady=2)

        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        preview = ttk.LabelFrame(right, text="Apercu", padding=10)
        preview.pack(fill="both", expand=True)

        self.preview_label = ttk.Label(preview)
        self.preview_label.pack(pady=(0, 10))

        self.preview_name = ttk.Label(preview, text="", font=("Segoe UI", 12, "bold"))
        self.preview_name.pack(anchor="w")
        self.preview_description = ttk.Label(
            preview, text="", font=("Segoe UI", 9), wraplength=420, justify="left"
        )
        self.preview_description.pack(anchor="w", pady=(4, 0))
        self.preview_meta = ttk.Label(
            preview, text="", font=("Segoe UI", 8), foreground="gray", justify="left"
        )
        self.preview_meta.pack(anchor="w", pady=(8, 0))

        self.active_skin_label = ttk.Label(
            frame, text="Skin actif : ...", font=("Segoe UI", 9, "italic")
        )
        self.active_skin_label.pack(pady=(8, 0))

        self._show_placeholder()

    # ------------------------------------------------------------------
    # Liste
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Relit le dossier des skins et repeuple la liste."""
        repository = self.app.skins
        repository.invalidate()
        skins = repository.list_skins()

        self.listbox.delete(0, tk.END)
        self._skins_by_label = {}

        try:
            active_id = repository.active_id
        except SkinNotFoundError:
            active_id = ""

        for index, skin in enumerate(skins):
            # Deux skins peuvent porter le meme nom : on desambigue par l'id.
            label = skin.name
            if label in self._skins_by_label:
                label = f"{skin.name} ({skin.id})"
            self._skins_by_label[label] = skin
            self.listbox.insert(tk.END, label)
            if skin.id == active_id:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(index)
                self.listbox.see(index)
                self._show_skin(skin)

        active = next((skin for skin in skins if skin.id == active_id), None)
        self.active_skin_label.config(text=f"Skin actif : {active.name if active else 'aucun'}")
        logger.info("%d skin(s) disponibles", len(skins))
        self.app.about_tab.refresh()

    def _selected_skin(self) -> Skin | None:
        selection = self.listbox.curselection()
        if not selection:
            return None
        return self._skins_by_label.get(self.listbox.get(selection[0]))

    def _on_selection(self, _event: object) -> None:
        skin = self._selected_skin()
        if skin is not None:
            self._show_skin(skin)

    def apply_selected(self) -> None:
        """Active le skin sélectionné (effet immédiat, serveur démarré ou non)."""
        skin = self._selected_skin()
        if skin is None:
            messagebox.showwarning("Aucune selection", "Selectionnez un skin dans la liste.")
            return

        try:
            self.app.skins.set_active(skin.id)
        except SkinNotFoundError as exc:
            messagebox.showerror("Erreur", str(exc))
            return

        self.active_skin_label.config(text=f"Skin actif : {skin.name}")
        logger.info("Skin applique : %s", skin.name)
        messagebox.showinfo(
            "Skin applique",
            f"Skin actif : {skin.name}\n\nRafraichissez la source navigateur dans OBS.",
        )

    # ------------------------------------------------------------------
    # Aperçu
    # ------------------------------------------------------------------
    def _show_skin(self, skin: Skin) -> None:
        self.preview_name.config(text=skin.name)
        self.preview_description.config(text=skin.description)
        self.preview_meta.config(text=f"Auteur : {skin.author}\nVersion : {skin.version}")

        cached = self._preview_cache.get(skin.id)
        if cached is not None:
            self._set_preview(cached)
            return

        preview_file = skin.preview_file
        if preview_file is None:
            self._show_placeholder()
            return

        try:
            image = Image.open(preview_file)
            image.thumbnail(PREVIEW_MAX_SIZE, Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        except (OSError, ValueError) as exc:
            logger.debug("Apercu illisible pour %s : %s", skin.id, exc)
            self._show_placeholder()
            return

        self._preview_cache[skin.id] = photo
        self._set_preview(photo)

    def _show_placeholder(self) -> None:
        if self._placeholder is None:
            self._placeholder = ImageTk.PhotoImage(assets.create_placeholder_image())
        self._set_preview(self._placeholder)

    def _set_preview(self, photo: ImageTk.PhotoImage) -> None:
        # Référence conservée : sans cela Tk libère l'image et affiche du vide.
        self._current_preview = photo
        self.preview_label.config(image=photo)
