"""Review sheet: furniture states, screens and effects used by the demo."""

from pixelkit import Anim, P, Sprite

import _furniture as F

PREVIEW_SCALE = 6


def strip(sprites, gap=3, bg=None):
    w = sum(s.w for s in sprites) + gap * (len(sprites) + 1)
    h = max(s.h for s in sprites) + gap * 2
    out = Sprite(w, h, fill=bg or P.plaster_living[2])
    x = gap
    for s in sprites:
        out.blit(s, x, h - gap - s.h)
        x += s.w + gap
    return out


def build():
    return {
        "fx_windows": strip([F.window("day"), F.window("day", opened=True, sway=1), F.window("day", opened=True, sway=2),
                             F.window("night", opened=True, sway=1), F.window("day", curtains=None, opened=True),
                             F.desk_lamp(), F.desk_lamp(on=True)]),
        "fx_tv": strip([F.tv_screen(c, f) for c in F.TV_CHANNELS for f in range(4)], bg=P.ink[0]),
        "fx_games": strip([F.monitor_screen(g, f) for g in F.GAMES for f in range(4)], bg=P.ink[0]),
        "fx_cook": Anim([strip([F.cook_fx(f)]) for f in range(12)], 120),
        "fx_meal": Anim([strip([F.meal_fx(f)]) for f in range(4)], 260),
        "fx_still": strip([F.cook_fx(f) for f in (0, 3, 6, 9)] + [F.meal_fx(f) for f in range(2)] + [F.water_fx(f) for f in range(3)]),
    }
