"""Build the character-creator prototype: prototype/creator/index.html.

Every doll layer is rendered once with *marker* colors instead of real ones,
then stored as a role map: each pixel says "hair shade 2" or "skin shade 0"
(or a fixed color like the ink outline). The page recolors those roles with
ramps generated from whatever color the player picks — the same way the game
will do palette swaps at runtime.

    PYTHONPATH=tools python3 tools/make_creator.py
"""

from __future__ import annotations

import itertools
import json
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "art/src/concept")]

import doll  # noqa: E402
from pixelkit import Sprite, hexstr  # noqa: E402
from pixelkit.palette import CLOTH_STEPS, LIGHT_HUE, RAMPS, SHADOW_HUE, SKIN_SHADOW_HUE, SKIN_STEPS, SWATCHES  # noqa: E402

SRC = ROOT / "prototype/creator/index.src.html"
OUT = ROOT / "prototype/creator/index.html"

ROLES = ["hair", "skin", "top", "bottom", "eye"]
MARK = {r: tuple("#%02x%02xfe" % (g + 1, i) for i in range(5)) for g, r in enumerate(ROLES)}
MARK_LOOKUP = {m: (r, i) for r, ms in MARK.items() for i, m in enumerate(ms)}

ACCESSORIES = [None, "glasses", "bow", "headphones"]
LOOKS, BOBS, SWAYS, WAVES = (-1, 0, 1), (0, 1), (0, 1), (None, 0, 1)
TOKENS = [c for c in string.ascii_letters + string.digits + "!#$%&()*+,-/:;<=>?@[]^_{}~" if c != "."]


def collect_layers() -> dict[str, Sprite]:
    layers: dict[str, Sprite] = {}
    for gender, style, outfit, acc in itertools.product("mf", doll.HEADS, doll.BODIES, ACCESSORIES):
        d = doll.Doll(gender=gender, hair_style=style, outfit=outfit, accessory=acc,
                      hair=MARK["hair"], skin=MARK["skin"], top=MARK["top"],
                      bottom=MARK["bottom"], eye=MARK["eye"])
        for expr, look, bob, sway, wave in itertools.product(doll.EXPRS, LOOKS, BOBS, SWAYS, WAVES):
            for key, draw in d.layers(expr=expr, look=look, bob=bob, sway=sway, wave=wave):
                if key not in layers:
                    s = Sprite(doll.W, doll.H)
                    draw(s)
                    layers[key] = s
    return layers


def encode(sprites: dict[str, Sprite]):
    """Token-per-pixel rows, trimmed to the rows that hold pixels."""
    colors: dict[str, str] = {}
    table: dict[str, object] = {}
    out = {}
    for key, s in sprites.items():
        rows = []
        for y in range(s.h):
            row = []
            for x in range(s.w):
                px = s.px[y, x]
                if px[3] == 0:
                    row.append(".")
                    continue
                c = hexstr(tuple(px))
                if c not in colors:
                    tok = TOKENS[len(colors)]
                    colors[c] = tok
                    table[tok] = list(MARK_LOOKUP[c]) if c in MARK_LOOKUP else c
                row.append(colors[c])
            rows.append("".join(row))
        filled = [i for i, r in enumerate(rows) if r.strip(".")]
        y0 = filled[0] if filled else 0
        y1 = filled[-1] + 1 if filled else 0
        out[key] = {"y": y0, "rows": rows[y0:y1]} if s.w == doll.W else {"w": s.w, "h": s.h, "rows": rows}
    return table, out


def main():
    layers = collect_layers()
    emotes = {f"emote/{n}": doll.emote(n) for n in doll.EMOTES}
    table, enc = encode({**layers, **emotes})
    data = {
        "W": doll.W, "H": doll.H,
        "colors": table,
        "layers": enc,
        "seq": [{**{"expr": "neutral", "look": 0, "bob": 0, "sway": 0, "wave": None}, **kw, "emote": em, "ms": ms}
                for kw, em, ms in doll.IDLE_SEQ],
        "swatches": SWATCHES,
        "eyes": [["棕", RAMPS["hair_brown"][2]], ["黑", RAMPS["hair_black"][2]], ["蓝", RAMPS["blue"][2]],
                 ["绿", RAMPS["green"][2]], ["紫", "#7a5aa6"], ["琥珀", RAMPS["mustard"][2]]],
        "ramp": {"cloth": CLOTH_STEPS, "skin": SKIN_STEPS, "shadowHue": SHADOW_HUE,
                 "skinShadowHue": SKIN_SHADOW_HUE, "lightHue": LIGHT_HUE},
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = SRC.read_text().replace("/*__DOLL_DATA__*/null", blob)
    OUT.write_text(html)
    print(f"{OUT.relative_to(ROOT)}: {len(enc)} layers, {len(table)} colors, {len(html) // 1024} KB")


if __name__ == "__main__":
    main()
