"""pixelkit — tiny code-first pixel-art toolkit for Desktop-Buddy assets.

    from pixelkit import Sprite, Anim, P
    s = Sprite.from_grid('''
        .oo.
        oSSo
    ''', {"o": P.skin[0], "S": P.skin[2]})
"""

from .core import Anim, Sprite, hexstr, rgba
from .export import contact_sheet, gif, lint, palette_swatch, preview, sheet
from .palette import ALL_COLORS, P, RAMPS, ramp

__all__ = [
    "Anim", "Sprite", "hexstr", "rgba",
    "contact_sheet", "gif", "lint", "palette_swatch", "preview", "sheet",
    "ALL_COLORS", "P", "RAMPS", "ramp",
]
