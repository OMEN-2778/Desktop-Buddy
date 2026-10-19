"""Two-storey cross-section house, no roof.

    upper:   stairs | bedroom | bathroom | study (computer + books)
    ground:  stairs | living room          | kitchen

Calm scheme: warm off-white walls (each room only slightly tinted), one oak
floor, ash/walnut furniture, white appliances; sage and clay are the only
accents, so Buddy is the most colourful thing in the house. Rooms are kept
sparse — a few real pieces each, with space to walk.
"""

import numpy as np
from pixelkit import P, Sprite, rgba

import _furniture as F
import doll

PREVIEW_SCALE = 4

OAK, POR, TILE, FR = P.oak, P.porcelain, P.tile, P.frame

# ---------------------------------------------------------------- layout
W, H = 342, 118
SLAB = 5
WALL_H, BAND = 45, 6        # 45px ≈ 2.6m
X0, X1 = 4, 338
OUTER, INNER = 6, 4
LINTEL = 8                  # door openings are 37px ≈ 2.1m tall

UP_WALL = SLAB
UP_FLOOR = UP_WALL + WALL_H
MID_SLAB = UP_FLOOR + BAND
GR_WALL = MID_SLAB + SLAB
GR_FLOOR = GR_WALL + WALL_H
FOUND = GR_FLOOR + BAND

STAIRS = (10, 44)

# (key, name, storey, x, width, wall ramp, floor kind)
ROOMS = [
    ("bedroom", "卧室", 1, 58, 100, P.plaster_bed, "wood"),
    ("bath", "卫生间", 1, 162, 66, P.plaster_bath, "tile"),
    ("study", "电脑房·书屋", 1, 232, 100, P.plaster_study, "wood"),
    ("living", "客厅", 0, 58, 170, P.plaster_living, "wood"),
    ("kitchen", "厨房", 0, 232, 100, P.plaster_kitchen, "tile"),
]
WALL_RAMPS = [r[5] for r in ROOMS] + [P.plaster_stair]


def levels(storey):
    return (UP_WALL, UP_FLOOR) if storey == 1 else (GR_WALL, GR_FLOOR)


# Shadow tones used when furniture casts onto the wall behind it.
DARKEN = {}
for _r in WALL_RAMPS:
    DARKEN[rgba(_r[2])] = rgba(_r[1])
    DARKEN[rgba(_r[3])] = rgba(_r[1])
for _c in (POR[2], POR[3]):
    DARKEN[rgba(_c)] = rgba(POR[1])
for _c in (TILE[2], TILE[3]):
    DARKEN[rgba(_c)] = rgba(TILE[1])
for _c in (OAK[2], OAK[3], OAK[4]):
    DARKEN[rgba(_c)] = rgba(OAK[1])


# ---------------------------------------------------------------- shell


def cut_block(s, x, y, w, h):
    s.rect(x, y, w, h, FR[0])
    if w > 2 and h > 2:
        s.rect(x + 1, y + 1, w - 2, h - 2, FR[2])
        s.hline(x + 1, x + w - 2, y + 1, FR[3])


def back_wall(s, x, w, top, bottom, ramp):
    s.rect(x, top, w, bottom - top, ramp[2])
    s.hline(x, x + w - 1, top, ramp[0]).hline(x, x + w - 1, top + 1, ramp[1])  # ceiling shadow
    s.rect(x, bottom - 3, w, 3, POR[3]).hline(x, x + w - 1, bottom - 1, POR[1])  # skirting


def floor_band(s, x, w, y, kind):
    if kind == "tile":
        s.rect(x, y, w, BAND, TILE[2])
        s.hline(x, x + w - 1, y, TILE[0]).hline(x, x + w - 1, y + 1, TILE[3]).hline(x, x + w - 1, y + 3, TILE[1])
        for tx in range(x + 3, x + w, 8):
            s.vline(tx, y + 1, y + 2, TILE[1]).vline(tx + 4, y + 4, y + BAND - 1, TILE[1])
    else:
        s.rect(x, y, w, BAND, OAK[2])
        s.hline(x, x + w - 1, y, OAK[0]).hline(x, x + w - 1, y + 1, OAK[3])
        s.hline(x, x + w - 1, y + 3, OAK[1])
        for i, yy in enumerate((y + 2, y + 4)):
            for sx in range(x + (i * 11) % 23, x + w, 23):
                s.set(sx, yy, OAK[1])


def doorway_wall(s, x, storey, left, right):
    top, fl = levels(storey)
    for dx, (ramp, kind) in ((0, left), (INNER // 2, right)):
        back_wall(s, x + dx, INNER // 2, top, fl, ramp)
        floor_band(s, x + dx, INNER // 2, fl, kind)
    cut_block(s, x, top, INNER, LINTEL)
    s.rect(x - 2, top + LINTEL, INNER + 4, 2, POR[1]).hline(x - 1, x + INNER, top + LINTEL, POR[3])


def stairs(s):
    """Oak treads on a white stringer, slim steel balusters, walnut rail."""
    x0, w = STAIRS
    n, run, rise = 14, 3, 4
    for i in range(n):
        x = x0 + i * run
        top = GR_FLOOR - rise * (i + 1)
        under = min(top + 12, GR_FLOOR + 1)
        s.rect(x, top, run, under - top, POR[2])
        s.vline(x, top + 2, under - 1, POR[3])
        s.hline(x, x + run - 1, top, OAK[4]).hline(x, x + run - 1, top + 1, OAK[1])
        s.hline(x, x + run - 1, under - 1, POR[0])
    s.rect(x0 + n * run, UP_FLOOR, w - n * run, 2, OAK[2]).hline(x0 + n * run, x0 + w - 1, UP_FLOOR, OAK[3])
    s.rect(x0 + n * run, UP_FLOOR + 2, w - n * run, 2, POR[2])
    rail = lambda x: int(GR_FLOOR - 15 - (x - x0) * rise / run)
    for px in range(x0 + 2, x0 + n * run, 4):
        tread = GR_FLOOR - rise * ((px - x0) // run + 1)
        s.vline(px, rail(px) + 1, tread - 1, P.steel[2])
    for x in range(x0, x0 + n * run + 1):
        s.set(x, rail(x), P.walnut[1]).set(x, rail(x) - 1, P.walnut[3])


def shell(night=False):
    s = Sprite(W, H)
    sx, sw = STAIRS
    back_wall(s, sx, sw, UP_WALL, GR_FLOOR, P.plaster_stair)
    floor_band(s, sx, sw, GR_FLOOR, "wood")
    for _, _, storey, x, w, ramp, kind in ROOMS:
        top, fl = levels(storey)
        back_wall(s, x, w, top, fl, ramp)
        floor_band(s, x, w, fl, kind)
    cut_block(s, X0, 0, X1 - X0, SLAB)
    cut_block(s, sx + sw, MID_SLAB, X1 - (sx + sw), SLAB)
    cut_block(s, X0, FOUND, X1 - X0, SLAB + 1)
    cut_block(s, X0, 0, OUTER, FOUND + SLAB + 1)
    cut_block(s, X1 - OUTER, 0, OUTER, FOUND + SLAB + 1)
    room = {k: (ramp, kind) for k, _, _, _, _, ramp, kind in ROOMS}
    stair = (P.plaster_stair, "wood")
    doorway_wall(s, 54, 1, stair, room["bedroom"])
    doorway_wall(s, 158, 1, room["bedroom"], room["bath"])
    doorway_wall(s, 228, 1, room["bath"], room["study"])
    doorway_wall(s, 54, 0, stair, room["living"])
    doorway_wall(s, 228, 0, room["living"], room["kitchen"])
    stairs(s)
    return s


# ---------------------------------------------------------------- placing


def cast_shadow(s, spr, x, y, dx=2, dy=1):
    """Light from the top-left: a soft offset silhouette darkens the wall."""
    ys, xs = np.nonzero(spr.px[..., 3])
    for j, i in zip(ys, xs):
        tx, ty = x + i + dx, y + j + dy
        if 0 <= tx < s.w and 0 <= ty < s.h:
            c = DARKEN.get(tuple(int(v) for v in s.px[ty, tx]))
            if c:
                s.px[ty, tx] = c


def place(s, spr, x, y, shadow=True):
    if shadow:
        cast_shadow(s, spr, x, y)
    s.blit(spr, x, y)
    return y


def on_floor(s, spr, x, storey, depth=1, shadow=True):
    """Stand a sprite on a storey's floor band; depth = px into the band."""
    _, fl = levels(storey)
    y = fl + depth - spr.h + 1
    if shadow:
        cast_shadow(s, spr, x, y)
        feet = np.nonzero(spr.px[-1, :, 3])[0]
        sy = fl + depth + 1
        if len(feet) and sy < fl + BAND:  # contact shadow on the floor
            for fx in range(x + int(feet.min()), x + int(feet.max()) + 2):
                c = DARKEN.get(tuple(int(v) for v in s.px[sy, fx]))
                if c:
                    s.px[sy, fx] = c
    s.blit(spr, x, y)
    return y


def room_x(key):
    return next(r[3] for r in ROOMS if r[0] == key)


def furnish(s, night=False, buddy=doll.GIRL):
    sky = "night" if night else "day"
    lights, z_at = [], None

    # --- stairwell
    s.blit(F.round_window(night), STAIRS[0] + 8, UP_WALL + 10)
    place(s, F.sconce(on=night), STAIRS[0] + 3, GR_WALL + 12)

    # --- bedroom: window over the bed, nightstand + lamp, wardrobe
    x, (top, fl) = room_x("bedroom"), levels(1)
    place(s, F.window(sky), x + 7, top + 5)
    bed_y = on_floor(s, F.bed(), x + 2, 1)
    ns_y = on_floor(s, F.nightstand(), x + 46, 1, 0)
    place(s, F.lamp(on=night), x + 47, ns_y - 12)
    on_floor(s, F.wardrobe(), x + 76, 1, 0)
    if night:
        z_at = sleeper(s, x + 2, bed_y, buddy)
        lights.append((x + 51, ns_y - 8, 30, (1.0, 0.86, 0.62), "bedroom"))

    # --- bathroom: tiled to dado height
    x = room_x("bath")
    s.blit(F.backsplash(66, 18), x, fl - 21)
    s.hline(x, x + 65, fl - 21, POR[3])
    on_floor(s, F.bathtub(), x + 1, 1, 1)
    on_floor(s, F.toilet(), x + 33, 1, 1)
    place(s, F.towel(), x + 34, top + 12)
    on_floor(s, F.vanity(), x + 48, 1, 0)

    # --- study
    x = room_x("study")
    place(s, F.window(sky, curtains=None), x + 66, top + 5)
    on_floor(s, F.bookshelf(), x + 3, 1, 0)
    dy = on_floor(s, F.desk(), x + 30, 1, 0)
    place(s, F.monitor(on=not night), x + 38, dy - 13)
    place(s, F.keyboard(), x + 39, dy - 2, shadow=False)
    place(s, F.desk_lamp(), x + 55, dy - 11)
    place(s, F.mug(), x + 33, dy - 4)
    place(s, F.pendant(on=False), x + 42, top)
    on_floor(s, F.office_chair(), x + 22, 1, 2)
    on_floor(s, F.plant(), x + 82, 1, 1)

    # --- living room
    x, (top, fl) = room_x("living"), levels(0)
    place(s, F.window(sky), x + 42, top + 5)
    on_floor(s, F.plant(), x + 6, 0, 1)
    s.blit(F.rug(46), x + 35, fl + 2)
    on_floor(s, F.floor_lamp(on=night), x + 26, 0, 1)
    on_floor(s, F.sofa(), x + 38, 0, 1)
    on_floor(s, F.coffee_table(), x + 47, 0, 5)
    place(s, F.art_print(18, 13, "hills"), x + 119, top + 7)
    c_y = on_floor(s, F.media_console(), x + 112, 0, 0)
    place(s, F.tv(), x + 115, c_y - 15)
    if night:
        lights.append((x + 32, top + 20, 34, (1.0, 0.88, 0.64), "living"))

    # --- kitchen
    x = room_x("kitchen")
    place(s, F.wall_cabinets(), x + 2, top + 8)
    s.blit(F.backsplash(52, 10), x + 2, top + 19)
    on_floor(s, F.kitchen_base(), x + 2, 0, 0)
    on_floor(s, F.fridge(), x + 55, 0, 0)
    on_floor(s, F.chair("right"), x + 70, 0, 3)
    t_y = on_floor(s, F.dining_table(), x + 75, 0, 2)
    place(s, F.bowl(), x + 82, t_y - 4, shadow=False)
    on_floor(s, F.chair("left"), x + 91, 0, 3)
    if not night:
        on_floor(s, doll.with_emote(buddy.render(expr="happy"), "note"), x + 18, 0, 5, shadow=False)
    else:
        lights.append((x + 40, top + 18, 16, (1.0, 0.9, 0.72), "kitchen"))

    if night:
        lights.append((STAIRS[0] + 6, GR_WALL + 15, 18, (1.0, 0.85, 0.62), "stairs"))
    return lights, z_at


ZZZ = """
ooooo
...o.
..o..
.o...
ooooo
"""


def sleeper(s, bed_x, bed_y, buddy=doll.GIRL):
    """Buddy asleep: head on the pillow, duvet pulled up to the chin."""
    head = buddy.render(expr="sleepy").crop(0, 0, doll.W, 15)
    s.blit(head, bed_x - 1, bed_y - 5)
    D = P.oat
    qx, qy, qw = bed_x + 14, bed_y + 6, 18
    s.rect(qx, qy, qw, 11, D[0])
    s.ellipse(qx + 9, qy, 7, 1.5, D[0]).ellipse(qx + 9, qy + 1, 6, 1, D[3])
    s.rect(qx + 1, qy + 1, qw - 2, 9, D[3]).rect(qx + 1, qy + 1, qw - 2, 2, D[4]).hline(qx + 1, qx + qw - 2, qy + 9, D[2])
    s.rect(qx + 1, qy + 1, 4, 9, POR[3]).vline(qx + 5, qy + 2, qy + 9, D[2])
    return bed_x + 22, bed_y - 4


def zzz(s, x, y):
    s.blit(Sprite.from_grid(ZZZ, {"o": POR[3]}), x, y)
    s.blit(Sprite.from_grid("""
        oooo
        ..o.
        .o..
        oooo
    """, {"o": POR[2]}), x + 7, y - 6)


# ---------------------------------------------------------------- night

EMISSIVE = set(P.sky_night) | set(P.light) | set(P.glass[1:])


def room_rect(key):
    if key == "stairs":
        return STAIRS[0], UP_WALL, STAIRS[1], GR_FLOOR + BAND - UP_WALL
    r = next(r for r in ROOMS if r[0] == key)
    top, fl = levels(r[2])
    return r[3], top, r[4], fl + BAND - top


def night_grade(s, lights, bands=4):
    """Preview of the runtime night pass: cool multiply, then banded warm
    pools of light that stay inside their own room (walls block light)."""
    rgb = s.px[..., :3].astype(np.float32)
    Y, X = np.mgrid[0 : s.h, 0 : s.w]
    night = rgb * np.array([0.40, 0.42, 0.62])
    out = night.copy()
    for lx, ly, r, col, key in lights:
        rx, ry, rw, rh = room_rect(key)
        inside = np.zeros((s.h, s.w), bool)
        inside[ry : ry + rh, rx : rx + rw] = True
        d = np.sqrt((X - lx) ** 2 + ((Y - ly) * 1.15) ** 2) / r
        g = np.ceil(np.clip(1 - d, 0, 1) * bands) / bands * 0.9
        g = np.where(inside, g, 0)[..., None]
        out = np.maximum(out, night * (1 - g) + rgb * np.array(col) * g)
    glow = np.zeros((s.h, s.w), bool)
    for c in EMISSIVE:
        glow |= np.all(s.px[..., :3] == np.array(rgba(c)[:3]), axis=-1)
    out[glow] = rgb[glow]
    s.px[..., :3] = np.clip(np.rint(out), 0, 255).astype(np.uint8)
    return s


def scene(night=False, buddy=doll.GIRL):
    s = shell(night)
    lights, z_at = furnish(s, night, buddy)
    if night:
        s = night_grade(s, lights)
        zzz(s, *z_at)
    return s


def furniture_sheet():
    """All pieces side by side on a wall swatch, for reviewing them up close."""
    pieces = [F.bed(), F.nightstand(), F.lamp(), F.wardrobe(), F.window(), F.bathtub(), F.toilet(),
              F.vanity(), F.towel(), F.bookshelf(), F.desk(), F.monitor(), F.office_chair(), F.plant(),
              F.sofa(), F.coffee_table(), F.media_console(), F.tv(), F.floor_lamp(), F.kitchen_base(),
              F.wall_cabinets(), F.fridge(), F.dining_table(), F.chair(), F.art_print()]
    w = sum(p.w for p in pieces) + 4 * (len(pieces) + 1)
    s = Sprite(w, 44, fill=P.plaster_living[2])
    s.rect(0, 40, w, 4, OAK[3])
    x = 4
    for p in pieces:
        cast_shadow(s, p, x, 40 - p.h)
        s.blit(p, x, 40 - p.h)
        x += p.w + 4
    return s


def build():
    return {
        "house_day": scene(),
        "house_night": scene(night=True),
        "house_day_boy": scene(buddy=doll.BOY),
        "furniture": furniture_sheet(),
    }
