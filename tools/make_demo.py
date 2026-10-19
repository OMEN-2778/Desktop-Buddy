"""Build the life-sim demo: prototype/demo/index.html.

Packs everything the page needs into one JSON blob:
  - Buddy's paper-doll role maps (same as the creator) + emote bubbles
  - the empty house, day windows and night windows (lamps off: the page
    lights rooms itself), as PNG data URIs
  - door gaps and door leaves, appliance "on" overlays, the sleep/bath
    covers drawn in front of Buddy's head
  - the walk path (one polyline: kitchen -> living -> stairs -> bedroom ->
    bath -> study), activity spots, lights and room rectangles

    PYTHONPATH=tools python3 tools/make_demo.py
"""

from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "art/src/concept")]

import _furniture as F  # noqa: E402
import doll  # noqa: E402
import house as Hs  # noqa: E402
import make_creator as mc  # noqa: E402
from pixelkit import P, Sprite, rgba  # noqa: E402
from pixelkit.palette import CLOTH_STEPS, LIGHT_HUE, SHADOW_HUE, SKIN_SHADOW_HUE, SKIN_STEPS, SWATCHES  # noqa: E402

SRC = ROOT / "prototype/demo/index.src.html"
OUT = ROOT / "prototype/demo/index.html"


def png(s: Sprite) -> str:
    buf = io.BytesIO()
    s.to_image().save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def empty_house(night: bool) -> Sprite:
    s = Hs.shell(night)
    Hs.furnish(s, night, buddy=None, lamps=False)
    return s


def overlay(spr, x, y):
    return {"src": png(spr), "x": int(x), "y": int(y)}


def main():
    day = empty_house(False)
    night = empty_house(True)
    A = dict(Hs.ANCHORS)

    # doors: the 4px gap (wall + floor of each side) and leaves
    doors = []
    for did, storey, x, left, right in Hs.DOORS:
        top, fl = Hs.levels(storey)
        opened = Hs.shell(False, open_doors=[did])
        y = top + Hs.LINTEL
        gap = opened.crop(x, y, Hs.INNER, fl + Hs.BAND - y)
        doors.append({"id": did, "x": x, "y": y, "h": fl - y, "gap": png(gap), "storey": storey})
    leaves = {f"{w}{h[0]}": png(F.door_leaf(w, 37, hinge=h)) for w in (5, 10, 13) for h in ("left", "right")}

    # appliances / lamps switched on, and things drawn in front of Buddy
    bed_x, bed_y = A["bed"]
    tub_x, tub_y = A["bathtub"]
    tub = F.bathtub()
    tub_front = tub.crop(0, 21, tub.w, tub.h - 21)
    bubbles = Sprite(tub.w, 6)
    for bx, by, r in ((6, 3, 2.5), (11, 2, 3), (17, 3, 2.5), (23, 3, 2)):
        bubbles.ellipse(bx, by, r, r, P.linen[1])
    for bx, by, r in ((6, 3, 1.5), (11, 2, 2), (17, 3, 1.5), (23, 3, 1)):
        bubbles.ellipse(bx, by, r, r, P.linen[3])
    overlays = {
        "tv": overlay(F.tv(on=True), *A["tv"]),
        "monitor": overlay(F.monitor(on=True), *A["monitor"]),
        "bed_lamp": overlay(F.lamp(on=True), *A["bed_lamp"]),
        "floor_lamp": overlay(F.floor_lamp(on=True), *A["floor_lamp"]),
        "sconce": overlay(F.sconce(on=True), *A["sconce"]),
        "pendant": overlay(F.pendant(on=True), *A["pendant"]),
        "coffee_table": overlay(F.coffee_table(), *A["coffee_table"]),
        "sleep_cover": overlay(Hs.sleep_cover(), bed_x + Hs.SLEEP_COVER[0], bed_y + Hs.SLEEP_COVER[1]),
        "tub_front": overlay(tub_front, tub_x, tub_y + 21),
        "bubbles": overlay(bubbles, tub_x, tub_y + 18),
    }

    # walk path, feet positions (x = Buddy's centre column)
    gy, uy = Hs.GR_FLOOR + 3, Hs.UP_FLOOR + 3
    path = [
        (322, gy), (56, gy),                  # kitchen + living (ground floor)
        (51, Hs.GR_FLOOR - 3), (22, 79),      # flight 1, up to the left
        (18, 78), (22, 75),                   # landing turn
        (51, 51), (56, uy),                   # flight 2, up to the right
        (322, uy),                            # bedroom, bath, study
    ]
    k, lv, bd, bt, st = (Hs.room_x(r) for r in ("kitchen", "living", "bedroom", "bath", "study"))
    spots = {
        # name: storey, x, pose ("stand" | "sit" | "sleep" | "bath")
        "cook": (0, k + 36, "stand"),
        "fridge": (0, k + 62, "stand"),
        "eat": (0, k + 80, "sit"),
        "sofa": (0, lv + 55, "sit"),
        "art": (0, lv + 128, "stand"),
        "plant": (0, lv + 20, "stand"),
        "bed": (1, bd + 26, "sleep"),
        "wardrobe": (1, bd + 87, "stand"),
        "bath": (1, bt + 16, "bath"),
        "mirror": (1, bt + 56, "stand"),
        "computer": (1, st + 28, "sit"),
        "bookshelf": (1, st + 13, "stand"),
        "study_window": (1, st + 78, "stand"),
    }
    rooms = {key: Hs.room_rect(key) for key in ["stairs"] + [r[0] for r in Hs.ROOMS]}
    room_x = {r[0]: (r[2], r[3], r[3] + r[4]) for r in Hs.ROOMS}
    lights = {
        "bedroom": (A["bed_lamp"][0] + 4, A["bed_lamp"][1] + 4, 32, (1.0, 0.86, 0.62)),
        "living": (A["floor_lamp"][0] + 6, A["floor_lamp"][1] + 4, 40, (1.0, 0.88, 0.64)),
        "kitchen": (A["hood"][0] + 11, A["hood"][1] + 10, 30, (1.0, 0.9, 0.72)),
        "stairs": (A["sconce"][0] + 3, A["sconce"][1] + 3, 26, (1.0, 0.85, 0.62)),
        "study": (A["pendant"][0] + 5, A["pendant"][1] + 12, 36, (1.0, 0.9, 0.72)),
        "bath": (bt + 33, Hs.UP_WALL + 8, 34, (0.95, 0.95, 1.0)),
    }

    layers = mc.collect_layers()
    emotes = {f"emote/{n}": doll.emote(n) for n in doll.EMOTES}
    table, enc = mc.encode({**layers, **emotes})

    data = {
        "W": Hs.W, "H": Hs.H, "dollW": doll.W, "dollH": doll.H,
        "bg": {"day": png(day), "night": png(night)},
        "doors": doors, "leaves": leaves, "overlays": overlays,
        "sleepHead": [bed_x + Hs.SLEEP_HEAD[0], bed_y + Hs.SLEEP_HEAD[1]],
        "bathHead": [tub_x + 5, tub_y + 6],
        "path": path, "spots": spots, "rooms": rooms, "roomX": room_x, "lights": lights,
        "emissive": sorted({c.lower() for c in Hs.EMISSIVE}),
        "colors": table, "layers": enc,
        "seq": [{**{"expr": "neutral", "look": 0, "bob": 0, "sway": 0, "wave": None}, **kw, "emote": em, "ms": ms}
                for kw, em, ms in doll.IDLE_SEQ],
        "swatches": SWATCHES,
        "ramp": {"cloth": CLOTH_STEPS, "skin": SKIN_STEPS, "shadowHue": SHADOW_HUE,
                 "skinShadowHue": SKIN_SHADOW_HUE, "lightHue": LIGHT_HUE},
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(SRC.read_text().replace("/*__DEMO_DATA__*/null", blob))
    print(f"{OUT.relative_to(ROOT)}: {len(OUT.read_text()) // 1024} KB")


if __name__ == "__main__":
    main()
