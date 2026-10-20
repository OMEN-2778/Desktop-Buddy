"""Build the life-sim demo: prototype/demo/index.html.

Packs everything the page needs into one JSON blob:
  - Buddy's paper-doll role maps + dressing-room options (same as the creator)
  - the empty house, day windows and night windows (lamps off: the page
    lights rooms itself), as PNG data URIs
  - door gaps and door leaves, appliance "on" overlays, the sleep/bath
    covers drawn in front of Buddy's head
  - the walkable floors (one y per storey) and the stair column joining
    them, activity spots, lights and room rectangles

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
import house as Hs  # noqa: E402
import need_icons  # noqa: E402
import sky_icons  # noqa: E402
import ui_icons  # noqa: E402
import mood_icons  # noqa: E402
import make_creator as mc  # noqa: E402
from pixelkit import P, Sprite, rgba  # noqa: E402

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
        "desk_lamp": overlay(F.desk_lamp(on=True), *A["desk_lamp"]),
        "pendant": overlay(F.pendant(on=True), *A["pendant"]),
        "coffee_table": overlay(F.coffee_table(), *A["coffee_table"]),
        "sleep_cover": overlay(Hs.sleep_cover(), bed_x + Hs.SLEEP_COVER[0], bed_y + Hs.SLEEP_COVER[1]),
        "tub_front": overlay(tub_front, tub_x, tub_y + 21),
        "bubbles": overlay(bubbles, tub_x, tub_y + 18),
    }

    # clickable furniture (taken from the daytime furnish)
    Hs.CLICK.clear()
    empty_house(False)
    C = dict(Hs.CLICK)
    clickables = {cid: {"src": png(spr), "x": int(x), "y": int(y)} for cid, (spr, x, y) in C.items()}

    # window open states: day/night, three sway frames
    # upstairs windows look out on sky only; the living room sees the hill
    WIN = (("win_bed", F.OAT, False), ("win_living", F.OAT, True), ("win_study", None, False))
    windows = {}
    for cid, curt, ground in WIN:
        _, x, y = C[cid]
        windows[cid] = {"x": int(x), "y": int(y),
                        "drawn": png(F.window("day", curtains=curt, ground=ground, drawn=True)), **{
            f"{sky}{sw}": png(F.window(sky, curtains=curt, opened=True, sway=sw, ground=ground))
            for sky in ("day", "night") for sw in (0, 1, 2)}}

    # weather through the windows: where the glass shows sky, and where it
    # shows the hill (tinted per season). Open casements cover part of the
    # glass and the curtains drift, so the open mask keeps only pixels that
    # are sky in every sway frame.
    sky_cols = {rgba(c) for c in P.sky_soft}
    ground_cols = {rgba(c) for c in F.LEAF}

    def masks(sprites):
        sky = ground = None
        for spr in sprites:
            px = spr.px
            cols = [tuple(v) for v in px.reshape(-1, 4)]
            ks = [c in sky_cols for c in cols]
            gs = [c in ground_cols for c in cols]
            sky = ks if sky is None else [a and b for a, b in zip(sky, ks)]
            ground = gs if ground is None else [a and b for a, b in zip(ground, gs)]
        out = []
        for m in (sky, ground):
            spr = Sprite(sprites[0].w, sprites[0].h)
            for i, on in enumerate(m):
                if on:
                    spr.set(i % spr.w, i // spr.w, "#ffffff")
            out.append(png(spr))
        return {"sky": out[0], "ground": out[1]}

    weather_masks = {}
    for cid, curt, ground in WIN:
        _, x, y = C[cid]
        weather_masks[cid] = {"x": int(x), "y": int(y), "closed": masks([F.window("day", curtains=curt, ground=ground)]),
                              "open": masks([F.window("day", curtains=curt, opened=True, sway=sw, ground=ground)
                                             for sw in (0, 1, 2)])}
    weather_masks["win_round"] = {"x": Hs.STAIRS[0] + 4, "y": Hs.UP_WALL + 10, "closed": masks([F.round_window()]), "open": None}

    # screens (drawn after the night pass, they glow) and effects
    tvx, tvy = A["tv"]
    mx, my = A["monitor"]
    hx, hy = A["hob"]
    tx, ty = A["dining_table"]
    screens = {
        "tv": {"x": tvx + 1, "y": tvy + 1, "channels": {c: [png(F.tv_screen(c, f)) for f in range(4)] for c in F.TV_CHANNELS}},
        "monitor": {"x": mx + 1, "y": my + 1, "games": {g: [png(F.monitor_screen(g, f)) for f in range(4)] for g in F.GAMES},
                    "apps": {g: [png(F.monitor_screen(g, f)) for f in range(4)] for g in F.APPS}},
    }
    fx = {
        "cook": {"x": hx - 1, "y": hy - 23, "frames": [png(F.cook_fx(f)) for f in range(12)]},
        "meal": {"x": tx + 11, "y": ty - 13, "frames": [png(F.meal_fx(f)) for f in range(4)]},
        "water_living": {"x": A["plant_living"][0] + 4, "y": A["plant_living"][1] - 6, "frames": [png(F.water_fx(f)) for f in range(4)]},
        "water_study": {"x": A["plant_study"][0] + 4, "y": A["plant_study"][1] - 6, "frames": [png(F.water_fx(f)) for f in range(4)]},
        # her phone, placed relative to Buddy by the page
        "phone": {"frames": [png(F.phone_held(False, f)) for f in range(2)]},
        "phone_call": {"frames": [png(F.phone_held(True))]},
        "chair": {"frames": [png(F.office_chair_front())]},   # conjured at the computer, placed by the page
        "sleep_z": {"frames": [png(F.sleep_z_fx(f)) for f in range(12)]},   # over her pillow, placed by the page
    }

    # walking: feet y on each floor, and the flight Buddy climbs (straight up,
    # into the screen) at the stair column's centre
    floors = [Hs.GR_FLOOR + 3, Hs.UP_FLOOR + 3]
    stair = {"x": Hs.STAIR_COL[0] + Hs.STAIR_COL[1] // 2, "x0": Hs.STAIRS[0], "x1": Hs.STAIRS[0] + Hs.STAIRS[1]}
    k, lv, bd, bt, st = (Hs.room_x(r) for r in ("kitchen", "living", "bedroom", "bath", "study"))
    spots = {
        # name: storey, x, pose ("stand" | "sit" | "sleep" | "bath")
        "cook": (0, k + 49, "stand"),        # beside the pot, looking at it
        "fridge": (0, k + 62, "stand"),
        "eat": (0, k + 75, "sit"),           # left side of the table, bowl to her right
        "sofa": (0, lv + 55, "sit"),
        "art": (0, lv + 128, "stand"),
        "plant": (0, lv + 20, "stand"),
        "bed": (1, bd + 26, "sleep"),
        "wardrobe": (1, bd + 87, "stand"),
        "bath": (1, bt + 16, "bath"),
        "mirror": (1, bt + 56, "stand"),
        "computer": (1, st + 26, "sit"),      # the conjured chair (26 wide) stays clear of the monitor
        "toilet": (1, bt + 39, "sit"),
        "vanity": (1, bt + 56, "stand"),
        "towel": (1, bt + 38, "stand"),
        "water_living": (0, lv + 25, "stand"),
        "water_study": (1, st + 78, "stand"),
        "bookshelf": (1, st + 13, "stand"),
        "study_window": (1, st + 78, "stand"),
    }
    rooms = {key: Hs.room_rect(key) for key in ["stairs"] + [r[0] for r in Hs.ROOMS]}
    room_x = {r[0]: (r[2], r[3], r[3] + r[4]) for r in Hs.ROOMS}
    sx_, sy_ = A["sconce"]
    lights = {   # id: x, y, radius, colour, room (pools never leave their room)
        "bed_lamp": (A["bed_lamp"][0] + 4, A["bed_lamp"][1] + 4, 32, (1.0, 0.86, 0.62), "bedroom"),
        "floor_lamp": (A["floor_lamp"][0] + 6, A["floor_lamp"][1] + 4, 40, (1.0, 0.88, 0.64), "living"),
        "desk_lamp": (A["desk_lamp"][0] + 7, A["desk_lamp"][1] + 5, 22, (1.0, 0.9, 0.7), "study"),
        "kitchen": (A["hood"][0] + 11, A["hood"][1] + 10, 30, (1.0, 0.9, 0.72), "kitchen"),
        "stairs": (sx_ + 3, sy_ + 3, 26, (1.0, 0.85, 0.62), "stairs"),
        "study": (A["pendant"][0] + 5, A["pendant"][1] + 12, 36, (1.0, 0.9, 0.72), "study"),
        "bath": (bt + 33, Hs.UP_WALL + 8, 34, (0.95, 0.95, 1.0), "bath"),
        "tv": (tvx + 13, tvy + 8, 30, (0.7, 0.85, 1.05), "living"),
        "monitor": (mx + 8, my + 5, 18, (0.75, 0.9, 1.05), "study"),
    }

    data = {
        "W": Hs.W, "H": Hs.H,
        "doll": mc.doll_data(),   # Buddy's role maps + dressing-room options (shared with the creator)
        "bg": {"day": png(day), "night": png(night)},
        "needIcons": {k: png(need_icons.icon(k)) for k in need_icons.GRIDS},
        "uiIcons": {"gear": png(ui_icons.icon("gear"))},
        "uiGlyphs": ui_icons.GLYPHS,
        "skyIcons": {k: [png(f) for f in sky_icons.frames(k)] for k in sky_icons.NAMES},
        "moodIcons": {k: [png(f) for f in mood_icons.frames(k)] for k in mood_icons.NAMES},
        "moods": [list(m) for m in mood_icons.EMOTIONS],
        "weatherMasks": weather_masks,
        "doors": doors, "leaves": leaves, "overlays": overlays,
        "sleepLying": [bed_x + Hs.SLEEP_HEAD[0], bed_y + Hs.SLEEP_HEAD[1]],
        "clickables": clickables, "windows": windows, "screens": screens, "fx": fx,
        "bathHead": [tub_x + 5, tub_y + 6],
        "floors": floors, "stair": stair, "spots": spots, "rooms": rooms, "roomX": room_x, "lights": lights,
        "emissive": sorted({c.lower() for c in Hs.EMISSIVE}),
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = mc.inline_shared(SRC.read_text()).replace("/*__LIFE_TEXT_JS__*/", (SRC.parent / "life_text.js").read_text())
    OUT.write_text(html.replace("/*__DEMO_DATA__*/null", blob))
    print(f"{OUT.relative_to(ROOT)}: {len(OUT.read_text()) // 1024} KB")


if __name__ == "__main__":
    main()
