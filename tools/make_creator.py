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
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "art/src/concept")]

import doll  # noqa: E402
from pixelkit import Sprite, hexstr  # noqa: E402
from pixelkit.palette import CLOTH_STEPS, LIGHT_HUE, RAMPS, SHADOW_HUE, SKIN_SHADOW_HUE, SKIN_STEPS, SWATCHES  # noqa: E402

SRC = ROOT / "prototype/creator/index.src.html"
OUT = ROOT / "prototype/creator/index.html"

ROLES = ["hair", "skin", "top", "bottom", "eye", "sock"]
MARK = {r: tuple("#%02x%02xfe" % (g + 1, i) for i in range(5)) for g, r in enumerate(ROLES)}
MARK_LOOKUP = {m: (r, i) for r, ms in MARK.items() for i, m in enumerate(ms)}

LOOKS, BOBS, SWAYS, WAVES = (-1, 0, 1), (0, 1), (0, 1), (None, 0, 1)
TOKENS = [c for c in string.ascii_letters + string.digits + "!#$%&()*+,-/:;<=>?@[]^_{}~" if c != "."]
SHARED = ROOT / "prototype/shared"


def collect_layers() -> dict[str, Sprite]:
    """Every layer key any look can ask for, drawn once with marker colors.
    Layers depend on few options each, so walk the options per part instead
    of the full product of every option."""
    layers: dict[str, Sprite] = {}
    marked = {r: MARK[r] for r in ROLES}

    def add(d, frames):
        for f in frames:
            for key, draw in d.layers(**f):
                if key not in layers:
                    s = Sprite(doll.W, doll.H)
                    draw(s)
                    layers[key] = s

    all_frames = [dict(expr=e, look=lk, bob=b, sway=sw, wave=wv)
                  for e, lk, b, sw, wv in itertools.product(doll.EXPRS, LOOKS, BOBS, SWAYS, WAVES)]
    still = [dict(bob=b, sway=sw, wave=wv) for b, sw, wv in itertools.product(BOBS, SWAYS, WAVES)]
    base = doll.Doll(hair=marked["hair"], skin=marked["skin"], top=marked["top"], bottom=marked["bottom"],
                     eye=marked["eye"], sock=marked["sock"])
    # faces: gender x eye shape x brows (hidden under eyewear) x every frame
    for gender, shape, acc in itertools.product("mf", doll.EYE_SHAPES, ((), ("glasses",))):
        add(replace(base, gender=gender, eye_shape=shape, accessories=acc), all_frames)
    for style in doll.HEADS:                       # hair (front, back, ahoge)
        add(replace(base, hair_style=style), still)
    for top in doll.TOPS:                          # tops + raised arms
        add(replace(base, top_style=top), still)
    for bottom, socks in itertools.product(doll.BOTTOMS, doll.SOCKS):
        add(replace(base, bottom_style=bottom, socks=socks), still[:1])
    for a in doll.ACCESSORIES:
        add(replace(base, accessories=(a,)), still)
    for style in doll.HEADS:                       # hair under a beanie, headphones fitted per head
        add(replace(base, hair_style=style, accessories=("beanie", "headphones")), still)
        add(replace(base, hair_style=style, accessories=("headphones",)), still)
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


def doll_data() -> dict:
    """Everything a page needs to draw and dress Buddy (role maps + option tables)."""
    layers = collect_layers()
    emotes = {f"emote/{n}": doll.emote(n) for n in doll.EMOTES}
    table, enc = encode({**layers, **emotes})
    return {
        "W": doll.W, "H": doll.H,
        "colors": table,
        "layers": enc,
        "seq": [{**{"expr": "neutral", "look": 0, "bob": 0, "sway": 0, "wave": None}, **kw, "emote": em, "ms": ms}
                for kw, em, ms in doll.IDLE_SEQ],
        "options": doll.OPTIONS,
        "shortStyles": doll.SHORT_STYLES,
        "sleeves": doll.SLEEVES,
        "pose": {k: {"shoes": sh, "legStart": ls, "sitDrop": list(sd)} for k, (sh, ls, sd) in doll.BOTTOM_POSE.items()},
        "headAcc": doll.HEAD_ACC_ORDER,
        "eyewear": list(doll.EYEWEAR),
        "swatches": {**SWATCHES, "eye": [["棕", RAMPS["hair_brown"][2]], ["黑", RAMPS["hair_black"][2]],
                                         ["蓝", RAMPS["blue"][2]], ["绿", RAMPS["green"][2]], ["紫", "#7a5aa6"],
                                         ["琥珀", RAMPS["mustard"][2]], ["粉", "#c75f81"]]},
        "ramp": {"cloth": CLOTH_STEPS, "skin": SKIN_STEPS, "shadowHue": SHADOW_HUE,
                 "skinShadowHue": SKIN_SHADOW_HUE, "lightHue": LIGHT_HUE},
    }


def inline_shared(html: str) -> str:
    """Paste the shared doll + dressing-room code into a page."""
    for name in ("doll.js", "studio.js", "studio.css"):
        html = html.replace(f"/*__SHARED_{name.replace('.', '_').upper()}__*/", (SHARED / name).read_text())
    return html


def main():
    data = doll_data()
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = inline_shared(SRC.read_text()).replace("/*__DOLL_DATA__*/null", blob)
    OUT.write_text(html)
    print(f"{OUT.relative_to(ROOT)}: {len(data['layers'])} layers, {len(data['colors'])} colors, {len(html) // 1024} KB")


if __name__ == "__main__":
    main()
