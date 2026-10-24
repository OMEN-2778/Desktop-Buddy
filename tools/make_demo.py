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
import dusk as DUSK  # noqa: E402
import rescue  # noqa: E402
import trip_icons  # noqa: E402
import ui_icons  # noqa: E402
import item_icons  # noqa: E402
import mood_icons  # noqa: E402
import front_yard as FY  # noqa: E402
import park as PK  # noqa: E402
import park_expansion as PX  # noqa: E402
import park_food as PF  # noqa: E402
import beach as BC  # noqa: E402
import mall as MALL  # noqa: E402
import mall_rooms as MR  # noqa: E402
import storm as STORM  # noqa: E402
import bar as BAR  # noqa: E402
import make_creator as mc  # noqa: E402
from pixelkit import P, Sprite, rgba  # noqa: E402

SRC = ROOT / "prototype/demo/index.src.html"
OUT = ROOT / "prototype/demo/index.html"


def guide_shots() -> dict:
    """The 新手教程's screenshots (tools/make_guide_shots.js): {id: {src, w, h, marks}}."""
    d = ROOT / "art/out/guide"
    meta = json.loads((d / "guide.json").read_text()) if (d / "guide.json").exists() else {}
    return {k: {**v, "src": "data:image/webp;base64," + base64.b64encode((d / f"{k}.webp").read_bytes()).decode()}
            for k, v in meta.items() if (d / f"{k}.webp").exists()}


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


def places_js():
    """places_text.js plus the outing texts in outing/ (why she goes out, what she says, mood-tagged musings)."""
    d = SRC.parent / "outing"
    def body(name):
        f = d / (name + ".js")
        return f.read_text().strip() if f.exists() else "{}"
    out = (SRC.parent / "places_text.js").read_text()
    out += f"\nconst OUTING_TEXT = Object.assign({{}}, {body('go_a')}, {body('go_b')});\n"
    for name in ("say_pb", "say_fm"):
        out += f"for (const [k, list] of Object.entries({body(name)})) PLACE_TEXT[k].say.push(...list);\n"
    return out


def chats_js():
    """chats_text.js plus the longer lists in chats/: phone calls (CHATS.call) and more forum posts."""
    d = SRC.parent / "chats"
    out = (SRC.parent / "chats_text.js").read_text()
    def talks(name):
        f = d / (name + ".js")
        return f.read_text().strip() if f.exists() else "[]"
    out += "\nCHATS.call = {\n" + ",\n".join(
        f'  {who}: {{ name: "{nm}", talks: {talks("call_" + who)}\n  }}'
        for who, nm in (("dad", "爸爸"), ("mom", "妈妈"), ("friend", "{朋友}"))) + "\n};\n"
    for k in ("yinfu", "xiaohongben", "shudong", "lengzhishi"):
        out += f"CHATS.forum.{k}.talks.push(...{talks(k)}\n);\n"
    return out


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
        # the potted trees stand in front of the windows: drawn again after
        # the open-window / curtain / weather layers so those never cover them
        "plant_study": overlay(F.plant(), *A["plant_study"]),
        "plant_living": overlay(F.plant(), *A["plant_living"]),
        "sleep_cover": overlay(Hs.sleep_cover(), bed_x + Hs.SLEEP_COVER[0], bed_y + Hs.SLEEP_COVER[1]),
        "tub_front": overlay(tub_front, tub_x, tub_y + 21),
        "bubbles": overlay(bubbles, tub_x, tub_y + 18),
    }

    # clickable furniture (taken from the daytime furnish)
    Hs.CLICK.clear()
    empty_house(False)
    C = dict(Hs.CLICK)
    clickables = {cid: {"src": png(spr), "x": int(x), "y": int(y)} for cid, (spr, x, y) in C.items()}

    # the front door (user: it opens a ring of places to go) and, outside,
    # 家门口: the street side of the house (art/src/concept/front_yard.py)
    door = Sprite(Hs.W, Hs.H)
    Hs.entry_door(door)
    x0, y0, x1, y1 = door.bbox()
    clickables["front_door"] = {"src": png(door.crop(x0, y0, x1 - x0, y1 - y0)), "x": x0, "y": y0}
    dx, dw = FY.DOOR
    dy = FY.BASE - 37
    door = Sprite(FY.W, FY.H)
    FY.door(door)
    x0, y0, x1, y1 = door.bbox()
    clickables["out_door"] = {"src": png(door.crop(x0, y0, x1 - x0, y1 - y0)), "x": x0, "y": y0}
    crown = {"maple": (19, 16), "cherry": (17, 15), "linden": (19, 16)}
    # places to go (user): 家门口, 公园 (five walkable areas), 商场 (she walks
    # on, the mall scrolls past), 海边. "img" holds every picture (the page
    # loads it as is), the rest is layout.
    clouds = [png(BC.cloud(i)) for i in range(3)]
    mall_items = MALL.items()
    mall_near = MALL.near()[0]
    sparrows = [png(FY.sparrow(f)) for f in range(4)]
    flies = [png(FY.butterfly(f)) for f in range(4)]
    park_food = json.loads((SRC.parent / "park_food.json").read_text())
    def park_season(zone, season):
        bg = PX.background(zone,season)
        sky = Sprite(PK.W,PK.H); PK.sky(sky)
        return {"bg":png(bg),"skyMask":png(DUSK.sky_mask(bg,sky)),
                "trees":[png(PX.trees(zone,season,f)) for f in (0,1)],"foreground":png(PX.foreground(zone,season))}

    def beach_season(season):
        bg = BC.background(season)
        sky = Sprite(BC.W,BC.H); BC.sky(sky,season)
        return {"bg":png(bg),"skyMask":png(DUSK.sky_mask(bg,sky)),"seaMask":png(DUSK.sea_mask(bg,season))}

    outside = {"front": {
        "kind": "walk",
        "img": {"seasons": {se: {"bg": png(FY.background(se)), "skyMask":png(DUSK.sky_mask(FY.background(se))), "trees": [png(FY.trees(se, f)) for f in (0, 1)]} for se in FY.SEASONS},
                "snow": png(FY.snow_layer()), "wet": png(FY.wet_layer()), "lit": png(FY.lit()),
                "cat": [png(FY.cat(f)) for f in (0, 1)], "sparrow": sparrows, "butterfly": flies},
        "sill": list(FY.SILL_CAT), "trees": [[kind, x, cy, *crown[kind]] for kind, x, cy in FY.TREES],
        "bushes": [[cx, hw, ht] for _, cx, hw, ht in FY.BUSHES], "side": FY.SIDE, "base": FY.BASE,
        "feet": FY.FEET, "walk": list(FY.WALK), "doorX": dx + dw // 2, "door": [dx - 2, dy - 8, dw + 4, 47]},
      "park": {
        "kind": "walk", "feet": PK.FEET, "walk": [8, PK.W - 8], "doorX": PK.BENCH, "side": PK.PATH[0],
        "img": {"zones": {z["id"]: {
            "seasons": {se: park_season(z,se) for se in PK.SEASONS},
            "snow": png(PX.snow(z)), "wet": png(PK.wet_layer()), "lit": png(PX.lit(z)), "bench": png(PX.bench_layer(z)), "facilityFront": png(PX.facility_front(z)), "props": png(PX.props(z,"summer")),
            "hover": {key: png(spr) for key, spr in PX.interaction_sprites(z).items()}
          } for z in PX.ZONES},
          "duck": [png(PK.duck(f)) for f in range(3)], "plane": png(PK.plane()), "sparrow": sparrows, "butterfly": flies, "cloud": clouds,
          "food": {d["id"]: png(PF.dish(d["kind"])) for d in park_food["dishes"]}},
        "zones": [{"id": z["id"], "name": z["name"], "pond": z["pond"], "lamp": z["lamp"],
                   "trees": [[kind, x, cy, rx, ry] for kind, x, cy, _, rx, ry in z["trees"]],
                   "horizon": PK.HORIZON, "path": list(PK.PATH), "feet": PK.FEET, "side": PK.PATH[0],
                   "facility": {"kind": "toilet", "x": 270, "feet": 97, "hit": [230,27,90,70]} if z["id"] == "lakeside"
                     else {"kind": "food", "x": 177, "feet": 103, "lift": 5, "hit": [111,31,118,70]} if z["id"] == "grove" else None,
                   "bench": {"x": z["bench"], "feet": 92, "lift": 5, "hit": [z["bench"] - 23, 64, 47, 30]}}
                  for z in PX.ZONES]},
      "beach": {
        "kind": "walk",
        "img": {"seasons": {se: beach_season(se) for se in BC.SEASONS},
                "snow": png(BC.snow_layer()), "wet": png(BC.wet_layer()), "lit": png(BC.lit()),
                "ship": png(BC.ship()), "speedboat": png(BC.speedboat()), "gull": [png(BC.gull(f)) for f in range(3)], "cloud": clouds},
        "horizon": BC.HORIZON, "deck": BC.DECK, "side": BC.DECK + 2, "feet": BC.FEET, "walk": list(BC.WALK),
        "doorX": 200, "lamps": list(BC.LAMPS)},
      "mall": {
        "kind": "scroll",
        "img": {"far": png(MALL.far()), "near": png(MALL.near()[0]), "rail": png(MALL.rail()), "skyNight": png(MALL.sky_night()),
                "deco": {se: png(MALL.deco(se)) for se in MALL.SEASONS},
                "shopper": [[png(MALL.shopper(k, f)) for f in (0, 1)] for k in range(5)],
                "props": {it["id"]: png(it["sprite"]) for it in mall_items if "sprite" in it},
                "restroom": png(MALL.restroom_sprite()),
                "hover": {it["id"]: png(mall_near.crop(it["u"], it["top"], it["w"], MALL.FLOOR - it["top"])) for it in mall_items if it["kind"] == "shop"}},
        "farW": MALL.FAR_W, "nearW": MALL.NEAR_W, "at": MALL.AT, "feet": MALL.FEET, "upWalk": MALL.UP_WALK,
        "fascia": MALL.FASCIA, "floor": MALL.FLOOR, "walk": [MALL.AT, MALL.AT], "doorX": MALL.AT,
        "restroom": {"w":74,"door":45,"top":MALL.SHOP_TOP},
        "items": [{k: v for k, v in it.items() if k != "sprite"} for it in mall_items]}}

    bar_text = json.loads((SRC.parent / "bar_text.json").read_text())
    mall_life = json.loads((SRC.parent / "mall_life.json").read_text())
    outside["mall"]["img"]["rooms"] = {}
    for kind in [*MR.RESTAURANTS,"cinema"]:
        front=Sprite(MR.W,MR.H)
        if kind=="cinema":
            MR.cinema_seat(front,197,110)
        else:
            MR.table(front,MR.DINING['table']['x'],MR.DINING['table']['y'],False)
            front.rect(212,61,85,14,P.walnut[1]).rect(214,63,81,10,MR.RESTAURANTS[kind][1]).rect(210,58,89,4,P.ash[3]).hline(210,298,58,P.ash[4])
        outside["mall"]["img"]["rooms"][kind]={"bg":png(MR.cinema() if kind=="cinema" else MR.restaurant(kind)),
            "front":png(front),"hover":{k:png(v) for k,v in MR.hover(kind).items()}}
    outside["mall"]["img"]["foodFront"]={k:png(MR.restaurant_front(k)) for k in MR.RESTAURANTS}
    outside["mall"]["dining"]=MR.DINING
    outside["mall"]["img"]["films"]={f["id"]:[png(MR.film_frame(f["art"],b)) for b in range(3)] for f in mall_life["films"]}
    outside["bar"] = {"kind": "bar", "img": {"day": png(BAR.scene()), "night": png(BAR.scene(True)), "counter": png(BAR.counter()), "foreground": png(BAR.foreground()),
                                             "hover": {key: png(spr) for key, spr in BAR.interaction_sprites().items()}},
                      "feet": 107, "walk": [18, 322], "doorX": 128}

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
        "guardian": {"frames": [png(rescue.angel(f)) for f in range(4)]},
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
        "front_door": (0, Hs.ENTRY[0] + Hs.ENTRY[1] // 2, "stand"),   # inside, at the front door
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
        "uiIcons": {**{name: png(ui_icons.icon(name)) for name in ("gear", "people")}, "stripes": png(ui_icons.need_stripes())},
        "uiRelief": {"badge": png(ui_icons.relief_plate(22, 11)),
                     "badgeSmall": png(ui_icons.relief_plate(19, 9)),
                     "answer": png(ui_icons.relief_plate()), "decline": png(ui_icons.relief_plate(kind="red"))},
        "uiGlyphs": ui_icons.GLYPHS,
        # pick-a-thing panels: covers matched to titles by hash, dishes by look
        "items": {**{k: [png(c) for c in item_icons.covers(k)] for k in ("book", "tv", "game", "app")},
                  "dish": {k: [png(d) for d in v] for k, v in item_icons.dishes().items()}},
        "skyIcons": {**{k: [png(f) for f in sky_icons.frames(k)] for k in sky_icons.NAMES},"storm":[png(STORM.icon(i)) for i in range(4)]},
        "moodIcons": {k: [png(f) for f in mood_icons.frames(k)] for k in mood_icons.NAMES},
        "moods": [list(m) for m in mood_icons.EMOTIONS],
        "weatherMasks": weather_masks,
        "doors": doors, "leaves": leaves, "overlays": overlays,
        "sleepLying": [bed_x + Hs.SLEEP_HEAD[0], bed_y + Hs.SLEEP_HEAD[1]],
        "clickables": clickables, "outside": outside,
        "trip": {k.split("_")[1]: png(v) for k, v in trip_icons.build().items()}, "windows": windows, "screens": screens, "fx": fx,
        "bathHead": [tub_x + 5, tub_y + 6],
        "floors": floors, "stair": stair, "spots": spots, "rooms": rooms, "roomX": room_x, "lights": lights,
        "seatLifts": {"tv": 4, "eat": 4, "toilet": 7, "computer": 3, "pc_code": 3, "pc_forum": 3, "pc_video": 3},
        "emissive": sorted({c.lower() for c in Hs.EMISSIVE}),
        "guide": guide_shots(),
        "barDrinks": {d["id"]: png(BAR.drink_icon(d["color"], d["glass"])) for d in bar_text["drinks"]},
        "dusk": {"warm":png(DUSK.sky("warm")),"rose":png(DUSK.sky("rose")),"sun":png(DUSK.sun())},
        "mallPosters": {f["id"]:png(MR.poster(f["art"])) for f in mall_life["films"]},
        "storm": {"bolts":[png(STORM.bolt(i)) for i in range(3)]},
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = mc.inline_shared(SRC.read_text()).replace("/*__LIFE_TEXT_JS__*/", (SRC.parent / "life_text.js").read_text()).replace("/*__CARDS_JS__*/", (SRC.parent / "cards_text.js").read_text()).replace("/*__CHATS_JS__*/", chats_js()).replace("/*__PLACES_JS__*/", places_js()).replace("/*__PLACE_CARDS_JS__*/", (SRC.parent / "place_cards.js").read_text()).replace("/*__GUIDE_JS__*/", (SRC.parent / "guide_text.js").read_text())
    html = html.replace("/*__BAR_TEXT_JS__*/", "const BAR_TEXT = " + json.dumps(bar_text, ensure_ascii=False) + ";")
    html = html.replace("/*__BAR_CARDS_JS__*/", "CARDS.push(..." + (SRC.parent / "bar_cards.json").read_text() + ");")
    html = html.replace("/*__SLEEP_CARDS_JS__*/", "CARDS.push(..." + (SRC.parent / "sleep_cards.json").read_text() + ");")
    html = html.replace("/*__PARK_CARDS_JS__*/", "CARDS.push(..." + (SRC.parent / "park_cards.json").read_text() + ");")
    html = html.replace("/*__PARK_FOOD_JS__*/", "const PARK_FOOD = " + json.dumps(park_food, ensure_ascii=False) + ";")
    html = html.replace("/*__NPC_SOCIAL_JS__*/", "const NPC_TALK_TEXT = " + (SRC.parent / "npc_talk.json").read_text() + ";\n" + (SRC.parent / "npc_social.js").read_text())
    html = html.replace("/*__PARK_JS__*/", (SRC.parent / "park.js").read_text())
    html = html.replace("/*__BAR_JS__*/", (SRC.parent / "bar.js").read_text())
    html = html.replace("/*__DUSK_JS__*/", (SRC.parent / "dusk.js").read_text())
    html = html.replace("/*__RESTROOMS_JS__*/", (SRC.parent / "restrooms.js").read_text())
    html = html.replace("/*__MALL_LIFE_JS__*/", "const MALL_LIFE = " + json.dumps(mall_life,ensure_ascii=False) + ";\n" + (SRC.parent / "mall_life.js").read_text())
    html = html.replace("/*__MALL_CARDS_JS__*/", "CARDS.push(..." + (SRC.parent / "mall_cards.json").read_text() + ");")
    html = html.replace("/*__STORM_CARDS_JS__*/", "CARDS.push(..." + (SRC.parent / "storm_cards.json").read_text() + ");")
    html = html.replace("/*__SOCIAL_HUD_CSS__*/", (SRC.parent / "social_hud.css").read_text()+"\n"+(SRC.parent / "peer_dialogue.css").read_text())
    html = html.replace("/*__PERSONALITY_JS__*/", (SRC.parent / "personality.js").read_text())
    html = html.replace("/*__SOCIAL_HUD_JS__*/", (SRC.parent / "social_hud.js").read_text())
    html = html.replace("/*__STORM_JS__*/", "const STORM_TEXT = " + (SRC.parent / "storm_text.json").read_text() + ";\n" + (SRC.parent / "storm.js").read_text())
    html = html.replace("/*__SOCIAL_LIFE_JS__*/", "const SOCIAL_TEXT = " + (SRC.parent / "social_text.json").read_text() + ";\n" + (SRC.parent / "social_life.js").read_text())
    html = html.replace("/*__SOCIAL_CARDS_JS__*/", "CARDS.push(..." + (SRC.parent / "social_cards.json").read_text() + ");")
    html = html.replace("/*__PEER_DIALOGUE_JS__*/", (SRC.parent / "peer_dialogue.js").read_text())
    OUT.write_text(html.replace("/*__DEMO_DATA__*/null", blob))
    print(f"{OUT.relative_to(ROOT)}: {len(OUT.read_text()) // 1024} KB")


if __name__ == "__main__":
    main()
