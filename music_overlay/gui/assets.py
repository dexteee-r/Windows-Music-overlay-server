"""Images générées à la volée pour l'interface (icône et aperçu par défaut).

Aucune ressource binaire à embarquer : tout est dessiné avec Pillow, ce qui
simplifie la compilation en exécutable.
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

ACCENT = "#667eea"
ACCENT_DARK = "#764ba2"
BACKGROUND = "#1a1a2e"
BORDER = "#4a4a6a"
MUTED = "#888888"

PREVIEW_SIZE = (500, 300)
TRAY_SIZE = 64


def create_tray_image(size: int = TRAY_SIZE) -> Image.Image:
    """Icône ronde avec une note de musique, pour la barre des tâches."""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    margin = size // 8
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=ACCENT,
        outline=ACCENT_DARK,
        width=max(2, size // 20),
    )

    head = size * 0.38
    draw.ellipse([head - 4, head + 6, head + 8, head + 18], fill="white")
    draw.rectangle([head + 5, head - 10, head + 8, head + 12], fill="white")
    return image


def _load_font(size: int) -> ImageFont.ImageFont:
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def create_placeholder_image(
    text: str = "Pas d'apercu disponible", size: tuple[int, int] = PREVIEW_SIZE
) -> Image.Image:
    """Vignette affichée quand un skin ne fournit pas de ``preview.png``."""
    width, height = size
    image = Image.new("RGB", size, color=BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle([2, 2, width - 3, height - 3], outline=BORDER, width=2)

    center_x, center_y = width // 2, height // 2 - 20
    draw.ellipse(
        [center_x - 25, center_y + 10, center_x + 5, center_y + 40],
        fill=ACCENT,
        outline=ACCENT_DARK,
        width=2,
    )
    draw.rectangle([center_x + 2, center_y - 40, center_x + 8, center_y + 25], fill=ACCENT)
    draw.ellipse([center_x + 5, center_y - 45, center_x + 15, center_y - 35], fill=ACCENT_DARK)

    font = _load_font(14)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(
        ((width - (box[2] - box[0])) // 2, center_y + 60),
        text,
        fill=MUTED,
        font=font,
    )
    return image
