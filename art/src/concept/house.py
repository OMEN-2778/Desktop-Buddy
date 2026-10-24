"""Two-storey cross-section house, no roof.

    upper:   bathroom | bedroom     | stairwell | study (computer + books)
    ground:  living room            | stairwell | kitchen

The stairwell sits between the bedroom/living room and the study/kitchen:
downstairs the front door is on its left and the stairs run straight into
the screen on its right (seen front-on, treads stacked upward); upstairs a
railing guards the stair opening.

Calm scheme: warm off-white walls (each room only slightly tinted), one oak
floor, ash/walnut furniture, white appliances; sage and clay are the only
accents, so Buddy is the most colourful thing in the house. Rooms are kept
sparse — a few real pieces each, with space to walk.
"""

import numpy as np
from pixelkit import Anim, P, Sprite, rgba

import _furniture as F
import doll
import visit_furniture

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

STAIRS = (184, 44)            # the stairwell, both storeys
STAIR_COL = (205, 22)         # the flight inside it (right part), x and width
ENTRY = (188, 15)             # the front door (left part, ground floor)

# (key, name, storey, x, width, wall ramp, floor kind)
ROOMS = [
    ("bath", "卫生间", 1, 10, 66, P.plaster_bath, "tile"),
    ("bedroom", "卧室", 1, 80, 100, P.plaster_bed, "wood"),
    ("study", "电脑房·书屋", 1, 232, 100, P.plaster_study, "wood"),
    ("living", "客厅", 0, 10, 170, P.plaster_living, "wood"),
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

# Doors sit in the interior walls. Closed, the wall is solid and seamless;
# open, the wall shows a 2.1m gap and the leaf swings into one room.
# (id, storey, wall x, left side, right side)
DOORS = [
    ("bath|bedroom", 1, 76, "bath", "bedroom"),
    ("bedroom|stair", 1, 180, "bedroom", "stairs"),
    ("stair|study", 1, 228, "stairs", "study"),
    ("living|stair", 0, 180, "living", "stairs"),
    ("stair|kitchen", 0, 228, "stairs", "kitchen"),
]
DOOR_W = {0: 0, 30: 5, 60: 10, 90: 13}  # leaf width seen front-on at each angle


def side_style(key):
    if key == "stairs":
        return P.plaster_stair, "wood"
    r = next(r for r in ROOMS if r[0] == key)
    return r[5], r[6]


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


def structure_mask(open_doors=()):
    """Every cut surface (slabs, outer and inner walls) as one boolean mask,
    so it can be drawn as a single seamless shape."""
    m = np.zeros((H, W), bool)

    def add(x, y, w, h):
        m[y : y + h, x : x + w] = True

    cx, cw = STAIR_COL
    add(X0, 0, X1 - X0, SLAB)
    add(X0, MID_SLAB, cx - X0, SLAB)                     # the upper floor, open over the flight
    add(cx + cw, MID_SLAB, X1 - (cx + cw), SLAB)
    add(X0, FOUND, X1 - X0, SLAB + 1)
    add(X0, 0, OUTER, FOUND + SLAB + 1)
    add(X1 - OUTER, 0, OUTER, FOUND + SLAB + 1)
    for did, storey, x, _, _ in DOORS:
        top, fl = levels(storey)
        add(x, top, INNER, fl + BAND - top)
        if did in open_doors:
            m[top + LINTEL : fl + BAND, x : x + INNER] = False
    return m


def draw_structure(s, m):
    """Fill the mask, outline only its outer boundary, light its top edges."""
    pad = np.pad(m, 1, constant_values=False)
    inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    edge = m & ~inner
    lit = np.zeros_like(m)
    lit[1:] = edge[:-1] & ~pad[:-2, 1:-1][:-1]  # just below a top edge
    lit &= m & ~edge
    s.px[m] = rgba(FR[2])
    s.px[lit] = rgba(FR[3])
    s.px[edge] = rgba(FR[0])


def stairs(s):
    """A straight flight running into the screen, seen front-on: treads
    stacked from the ground floor up through the hole in the slab, a shade
    darker and a touch narrower the further back (higher) they are, between
    two walnut strings."""
    x0, w = STAIR_COL
    top, bottom = UP_FLOOR + BAND, GR_FLOOR + 1
    WAL = P.walnut
    s.rect(x0, top, w, bottom - top, P.plaster_stair[1])                # the shaft behind
    n = (bottom - top) // 4
    for i in range(n):
        y = bottom - 4 * (i + 1)
        far = i / max(1, n - 1)                                         # 0 at the bottom, 1 at the top
        inset = 1 + round(far * 2)
        lo, hi = x0 + inset, x0 + w - 1 - inset
        ramp = OAK if far < 0.5 else [OAK[0], OAK[0], OAK[1], OAK[2], OAK[3]]
        s.hline(lo, hi, y, ramp[4]).hline(lo, hi, y + 1, ramp[2]).hline(lo, hi, y + 2, ramp[2]).hline(lo, hi, y + 3, ramp[1])
        s.set(lo, y + 1, ramp[3]).set(lo, y + 2, ramp[3])               # the lit end of each riser
        s.vline(lo - 1, y, y + 3, WAL[1]).vline(hi + 1, y, y + 3, WAL[0])  # strings
    # a wall handrail up the left side, its brackets every few treads
    for i in range(0, n, 3):
        y = bottom - 4 * i - 9
        s.set(x0 + 1, y, WAL[3]).set(x0 + 1, y + 1, WAL[1])


def stair_railing(s):
    """Upstairs: a balustrade along the back of the walkway, guarding the
    stair opening — newel posts at both ends, slim balusters, a walnut rail."""
    x0, w = STAIR_COL
    WAL = P.walnut
    rail_y = UP_FLOOR - 11
    for x in range(x0 + 3, x0 + w - 2, 4):
        s.vline(x, rail_y + 2, UP_FLOOR - 1, P.steel[2]).set(x, rail_y + 2, P.steel[3])
    for x in (x0, x0 + w - 2):                                          # newel posts
        s.rect(x, rail_y - 1, 2, UP_FLOOR - rail_y + 1, WAL[1]).hline(x, x + 1, rail_y - 1, WAL[3])
        s.set(x, rail_y, WAL[2])
    s.hline(x0, x0 + w - 1, rail_y, WAL[2]).hline(x0 + 2, x0 + w - 3, rail_y + 1, WAL[0])
    s.hline(x0 + 2, x0 + w - 3, rail_y, WAL[3])


def entry_door(s):
    """The front door (for a future outdoor scene): sage panel in a walnut
    frame, a small window, a brass knob, a mat in front."""
    x, w = ENTRY
    h = 37
    y = GR_FLOOR - h
    WAL, SG = P.walnut, P.sage
    s.rect(x - 1, y - 1, w + 2, h + 1, WAL[1]).hline(x - 1, x + w, y - 1, WAL[3])
    s.rect(x, y, w, h, SG[2]).vline(x, y, GR_FLOOR - 1, SG[3]).vline(x + w - 1, y, GR_FLOOR - 1, SG[1])
    s.rect(x + 3, y + 4, w - 6, 7, WAL[0]).rect(x + 4, y + 5, w - 8, 5, P.sky_soft[1]).set(x + 4, y + 5, P.sky_soft[3])
    s.rect(x + 3, y + 15, w - 6, 9, SG[1]).rect(x + 4, y + 16, w - 8, 7, SG[2])
    s.rect(x + 3, y + 27, w - 6, 7, SG[1]).rect(x + 4, y + 28, w - 8, 5, SG[2])
    s.set(x + w - 3, y + 19, P.mustard[3]).set(x + w - 3, y + 20, P.mustard[1])
    s.hline(x - 1, x + w, GR_FLOOR + 1, P.oat[2]).hline(x, x + w - 1, GR_FLOOR + 2, P.oat[1])


def shell(night=False, open_doors=()):
    s = Sprite(W, H)
    sx, sw = STAIRS
    for storey in (1, 0):
        top, fl = levels(storey)
        back_wall(s, sx, sw, top, fl, P.plaster_stair)
        floor_band(s, sx, sw, fl, "wood")
    for _, _, storey, x, w, ramp, kind in ROOMS:
        top, fl = levels(storey)
        back_wall(s, x, w, top, fl, ramp)
        floor_band(s, x, w, fl, kind)
    # what shows through a door gap when it opens: each side's wall and floor
    for _, storey, x, left, right in DOORS:
        top, fl = levels(storey)
        for dx, key in ((0, left), (INNER // 2, right)):
            ramp, kind = side_style(key)
            back_wall(s, x + dx, INNER // 2, top, fl, ramp)
            floor_band(s, x + dx, INNER // 2, fl, kind)
    stairs(s)
    entry_door(s)
    draw_structure(s, structure_mask(open_doors))
    stair_railing(s)
    return s


def draw_doors(s, doors):
    """doors: {door id: (angle, side)} — side 'l'/'r' = room the leaf swings into."""
    for did, storey, x, _, _ in DOORS:
        if did not in doors:
            continue
        angle, side = doors[did]
        top, fl = levels(storey)
        y = top + LINTEL
        # shadowed reveal inside the opening
        s.vline(x, y, fl - 1, FR[1]) if side == "r" else s.vline(x + INNER - 1, y, fl - 1, FR[1])
        w = DOOR_W[angle]
        if not w:
            continue
        leaf = F.door_leaf(w, fl - y, hinge="left" if side == "r" else "right")
        lx = x + INNER if side == "r" else x - w
        s.blit(leaf, lx, y)


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


# Where key pieces ended up — filled by furnish(), read by the demo exporter.
ANCHORS = {}
# Furniture the player can click in the demo: id -> (sprite, x, y).
CLICK = {}


def reg(cid, spr, x, y):
    CLICK[cid] = (spr, x, y)
    return y


def furnish(s, night=False, buddy=doll.GIRL, lamps=None):
    """buddy=None draws the empty house (the demo animates Buddy at runtime).
    lamps=False keeps every lamp off even at night (the demo lights rooms itself)."""
    sky = "night" if night else "day"
    lit = night if lamps is None else lamps
    lights, z_at = [], None

    # --- stairwell: a porthole window upstairs, a sconce over the flight
    s.blit(F.round_window(night), STAIRS[0] + 5, UP_WALL + 10)
    sc = (STAIR_COL[0] + 8, UP_WALL + 9)
    place(s, F.sconce(on=lit), *sc)
    ANCHORS["sconce"] = sc
    ANCHORS["round_window"] = (STAIRS[0] + 5, UP_WALL + 10)

    # --- bedroom: window over the bed, nightstand + lamp, wardrobe
    x, (top, fl) = room_x("bedroom"), levels(1)
    w = F.window(sky, ground=False)
    reg("win_bed", w, x + 7, place(s, w, x + 7, top + 5))
    bed = F.bed()
    bed_y = reg("bed", bed, x + 2, on_floor(s, bed, x + 2, 1))
    ns_y = on_floor(s, F.nightstand(), x + 46, 1, 0)
    lamp = F.lamp(on=lit)
    reg("bed_lamp", lamp, x + 47, place(s, lamp, x + 47, ns_y - 12))
    ANCHORS["bed"] = (x + 2, bed_y)
    ANCHORS["bed_lamp"] = (x + 47, ns_y - 12)
    wr = F.wardrobe()
    reg("wardrobe", wr, x + 76, on_floor(s, wr, x + 76, 1, 0))
    if night and buddy:
        z_at = sleeper(s, x + 2, bed_y, buddy)
        lights.append((x + 51, ns_y - 8, 30, (1.0, 0.86, 0.62), "bedroom"))

    # --- bathroom: tiled to dado height; every fixture helps hygiene
    x = room_x("bath")
    s.blit(F.backsplash(66, 18), x, fl - 21)
    s.hline(x, x + 65, fl - 21, POR[3])
    tub = F.bathtub()
    ANCHORS["bathtub"] = (x + 1, reg("bathtub", tub, x + 1, on_floor(s, tub, x + 1, 1, 1)))
    toilet = F.toilet()
    ANCHORS["toilet"] = (x + 33, reg("toilet", toilet, x + 33, on_floor(s, toilet, x + 33, 1, 1)))
    towel = F.towel()
    reg("towel", towel, x + 34, place(s, towel, x + 34, top + 12))
    van = F.vanity()
    reg("vanity", van, x + 48, on_floor(s, van, x + 48, 1, 0))

    # --- study
    x = room_x("study")
    w = F.window(sky, curtains=None, ground=False)
    reg("win_study", w, x + 66, place(s, w, x + 66, top + 5))
    bs = F.bookshelf()
    reg("bookshelf", bs, x + 3, on_floor(s, bs, x + 3, 1, 0))
    dy = on_floor(s, F.desk(), x + 30, 1, 0)
    mon = F.monitor(on=bool(buddy) and not night)
    reg("computer", mon, x + 38, place(s, mon, x + 38, dy - 13))
    ANCHORS["monitor"] = (x + 38, dy - 13)
    place(s, F.keyboard(), x + 39, dy - 2, shadow=False)
    dl = F.desk_lamp()
    reg("desk_lamp", dl, x + 55, place(s, dl, x + 55, dy - 11))
    ANCHORS["desk_lamp"] = (x + 55, dy - 11)
    place(s, F.mug(), x + 33, dy - 4)
    place(s, F.pendant(on=False), x + 42, top)
    ANCHORS["pendant"] = (x + 42, top)
    # no chair here: she conjures one (F.office_chair_front) when she sits at the computer (user)
    reg("guest_chair", visit_furniture.study_chair(), x + 61,
        on_floor(s, visit_furniture.study_chair(), x + 61, 1, 0))
    pl = F.plant()
    ANCHORS["plant_study"] = (x + 82, reg("plant_study", pl, x + 82, on_floor(s, pl, x + 82, 1, 1)))

    # --- living room
    x, (top, fl) = room_x("living"), levels(0)
    w = F.window(sky)
    reg("win_living", w, x + 42, place(s, w, x + 42, top + 5))
    pl = F.plant()
    ANCHORS["plant_living"] = (x + 6, reg("plant_living", pl, x + 6, on_floor(s, pl, x + 6, 0, 1)))
    s.blit(F.rug(46), x + 35, fl + 2)
    fl_lamp = F.floor_lamp(on=lit)
    ANCHORS["floor_lamp"] = (x + 26, reg("floor_lamp", fl_lamp, x + 26, on_floor(s, fl_lamp, x + 26, 0, 1)))
    sofa = F.sofa()
    ANCHORS["sofa"] = (x + 38, reg("sofa", sofa, x + 38, on_floor(s, sofa, x + 38, 0, 1)))
    ANCHORS["coffee_table"] = (x + 47, on_floor(s, F.coffee_table(), x + 47, 0, 5))
    art = F.art_print(18, 13, "hills")
    reg("art", art, x + 119, place(s, art, x + 119, top + 7))
    c_y = on_floor(s, F.media_console(), x + 112, 0, 0)
    tv = F.tv()
    reg("tv", tv, x + 115, place(s, tv, x + 115, c_y - 15))
    ANCHORS["tv"] = (x + 115, c_y - 15)
    if night:
        lights.append((x + 32, top + 20, 34, (1.0, 0.88, 0.64), "living"))

    # --- kitchen
    x = room_x("kitchen")
    place(s, F.wall_cabinets(), x + 2, top + 8)
    s.blit(F.backsplash(52, 10), x + 2, top + 19)
    kb = F.kitchen_base()
    kb_y = reg("stove", kb, x + 2, on_floor(s, kb, x + 2, 0, 0))
    ANCHORS["hob"] = (x + 2 + 26, kb_y + 6)          # left burner, worktop row
    fr = F.fridge()
    reg("fridge", fr, x + 55, on_floor(s, fr, x + 55, 0, 0))
    on_floor(s, F.chair("right"), x + 70, 0, 3)
    tbl = F.dining_table()
    t_y = reg("table", tbl, x + 75, on_floor(s, tbl, x + 75, 0, 2))
    ANCHORS["dining_table"] = (x + 75, t_y)
    if buddy:
        place(s, F.bowl(), x + 82, t_y - 4, shadow=False)
    on_floor(s, F.chair("left"), x + 91, 0, 3)
    ANCHORS["hood"] = (x + 2 + 27, top + 8)
    if buddy and not night:
        on_floor(s, doll.with_emote(buddy.render(expr="happy"), "note"), x + 18, 0, 5, shadow=False)
    else:
        lights.append((x + 40, top + 18, 16, (1.0, 0.9, 0.72), "kitchen"))

    if night:
        lights.append((sc[0] + 3, sc[1] + 4, 26, (1.0, 0.85, 0.62), "stairs"))
    return lights, z_at


ZZZ = """
ooooo
...o.
..o..
.o...
ooooo
"""


SLEEP_HEAD = (3, -7)      # the head turned on its side (rotated 90 deg), from the bed's top-left
SLEEP_COVER = (18, -12)   # duvet offset from the bed's top-left (top row is the outline)

# Duvet over a body lying on its side, chin at bed x 17: ONE soft, round
# mound (user: no camel humps). Its left side, right beside the head, is
# already taller than the head on the pillow (head top is about bed y -4,
# the bow -6): a rounded shoulder corner by the chin, a crown only a pixel
# above that shoulder (user), then a
# long easy slope down to the feet. The mattress top is y 10.
SLEEP_PROFILE = {18: -5, 19: -7, 20: -7, 21: -8, 22: -8, 23: -8, 24: -8, 25: -8, 26: -8, 27: -8,
                 28: -8, 29: -7, 30: -7, 31: -6, 32: -6, 33: -5, 34: -4, 35: -3, 36: -2, 37: -1, 38: 0,
                 39: 1, 40: 2, 41: 4}
SLEEP_PEAK_X, SLEEP_PEAK_Y = 24, -8


def sleep_cover():
    """The duvet pulled up to the chin over one soft, round mound: lit on
    the upper left, shading softly toward the right and where the body
    turns under toward the bed, a crease where it bends over the mattress,
    the sheet turned down at the neck and the clay throw over the feet."""
    D, C = P.oat, P.clay
    ox, oy = SLEEP_COVER
    s = Sprite(42 - ox, 18 - oy)
    top = {x - ox: y - oy for x, y in SLEEP_PROFILE.items()}
    crease, hem = 9 - oy, 16 - oy
    peak_x, peak_y = SLEEP_PEAK_X - ox, SLEEP_PEAK_Y - oy
    for x, t in top.items():
        s.vline(x, t, hem - 1, D[3])
        for y in range(t, crease):
            # light from the top-left over a round form: normal from the
            # mound's centre, a little highlight cap, soft shade bottom-right
            nx = (x - peak_x) / 14
            ny = (y - (crease + 2)) / (crease + 2 - peak_y)
            lit = -0.55 * nx - 0.85 * ny
            if y <= t + 1 and lit > 0.62:
                c = D[4]
            elif lit > 0.78:
                c = D[4]
            elif lit < 0.18 or y >= crease - 2:
                c = D[2]
            else:
                c = D[3]
            s.set(x, y, c)
        s.set(x, crease, D[2]).set(x, hem - 1, D[2])
    for fx in (25, 31, 37):                          # soft folds on the side face
        s.vline(fx - ox, crease + 2, hem - 2, D[2])
    out = s.outline(D[0], grow=True).crop(1, 1, s.w, s.h)
    for wx in range(20 - ox, 42 - ox, 4):            # draped hem
        out.set(wx, hem, None)
    # sheet turned down at the neck: a narrow white fold
    out.vline(0, top[0] + 1, crease - 1, POR[3]).vline(1, top[1] + 1, crease - 1, POR[2])
    # clay throw across the feet, following the slope
    tx0, tx1 = 37 - ox, 40 - ox
    for x in range(tx0, tx1 + 1):
        t = top[x]
        out.vline(x, t, hem + 1, C[2])
        out.set(x, t, C[3]).set(x, t + 1, C[3] if x < tx1 else C[2])
    out.vline(tx0, top[tx0], hem + 1, C[0]).vline(tx1, top[tx1], hem + 1, C[0])
    out.vline(tx1 - 1, top[tx1 - 1] + 2, hem, C[1])
    out.set(tx0, hem + 1, None).set(tx1, hem + 1, None)
    return out


def sleeper(s, bed_x, bed_y, buddy=doll.GIRL):
    """Buddy asleep on her side: head turned on the pillow, body under the duvet."""
    head = buddy.render(expr="sleepy").crop(0, 0, doll.W, 15)
    head = Sprite(0, 0, px=np.ascontiguousarray(np.rot90(head.px, 1)))
    s.blit(head, bed_x + SLEEP_HEAD[0], bed_y + SLEEP_HEAD[1])
    s.blit(sleep_cover(), bed_x + SLEEP_COVER[0], bed_y + SLEEP_COVER[1])
    return bed_x + 13, bed_y - 21


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


def scene(night=False, buddy=doll.GIRL, doors=None, grade=True):
    doors = doors or {}
    s = shell(night, open_doors=[d for d, (a, _) in doors.items() if a])
    lights, z_at = furnish(s, night, buddy)
    draw_doors(s, doors)
    if night and grade:
        s = night_grade(s, lights)
    if night and z_at:
        zzz(s, *z_at)
    return s


def furniture_sheet():
    """All pieces side by side on a wall swatch, for reviewing them up close."""
    pieces = [F.bed(), F.nightstand(), F.lamp(), F.wardrobe(), F.window(), F.bathtub(), F.toilet(),
              F.vanity(), F.towel(), F.bookshelf(), F.desk(), F.monitor(), F.office_chair_front(), F.plant(),
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


def door_demo():
    """Stairwell -> kitchen door: closed, swings open, holds, swings shut.
    Cropped around the wall; the leaf swings into the living room."""
    seq = [(0, 500), (30, 70), (60, 70), (90, 600), (60, 70), (30, 70), (0, 400)]
    x, storey = 228, 0
    top, fl = levels(storey)
    frames = []
    for angle, _ in seq:
        full = scene(doors={"stair|kitchen": (angle, "l")} if angle else {})
        frames.append(full.crop(x - 40, top - SLAB, 84, WALL_H + BAND + SLAB * 2))
    return Anim(frames, [ms for _, ms in seq])


def build():
    return {
        "door_demo": door_demo(),
        "house_day": scene(),
        "house_night": scene(night=True),
        "house_day_boy": scene(buddy=doll.BOY),
        "furniture": furniture_sheet(),
    }
