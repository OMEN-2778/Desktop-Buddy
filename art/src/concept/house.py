"""Two-storey cross-section house, no roof.

    upper:   stairs | bedroom | bathroom | study (computer + books)
    ground:  stairs | living room          | kitchen

The stairwell is one double-height column on the left. Rooms are separated by
cut walls with an open doorway under a lintel.
"""

import numpy as np
from pixelkit import P, Sprite, rgba

import _furniture as F
import doll

PREVIEW_SCALE = 4

W_, M_, L_ = P.wood, P.metal, P.linen

# ---------------------------------------------------------------- layout
W, H = 342, 122
SLAB = 5                    # thickness of cut floor/ceiling slabs
WALL_H, BAND = 45, 6        # back-wall height, visible floor depth
X0, X1 = 4, 338             # outer edge of the outer walls
OUTER, INNER = 6, 4         # wall thickness
DOOR_H = 18                 # cut wall above each doorway

UP_WALL = SLAB                       # 5   upper back wall top
UP_FLOOR = UP_WALL + WALL_H          # 50  upper floor band top
MID_SLAB = UP_FLOOR + BAND           # 56
GR_WALL = MID_SLAB + SLAB            # 61
GR_FLOOR = GR_WALL + WALL_H          # 106
FOUND = GR_FLOOR + BAND              # 112

STAIRS = (10, 44)  # x, width of the stairwell column (both storeys)

# (key, name, storey, x, width, wall ramp, floor kind)
ROOMS = [
    ("bedroom", "卧室", 1, 58, 100, P.wall_blush, "wood"),
    ("bath", "卫生间", 1, 162, 66, P.wall_sky, "tile"),
    ("study", "电脑房·书屋", 1, 232, 100, P.wall_sage, "wood"),
    ("living", "客厅", 0, 58, 170, P.wall_butter, "wood"),
    ("kitchen", "厨房", 0, 232, 100, P.wall_cream, "tile"),
]


def levels(storey):
    """(wall_top, floor_top) for a storey (1 = upper)."""
    return (UP_WALL, UP_FLOOR) if storey == 1 else (GR_WALL, GR_FLOOR)


# ---------------------------------------------------------------- shell


def cut_block(s, x, y, w, h):
    C = P.cut
    s.rect(x, y, w, h, C[0])
    if w > 2 and h > 2:
        s.rect(x + 1, y + 1, w - 2, h - 2, C[2])
        s.hline(x + 1, x + w - 2, y + 1, C[3])


def back_wall(s, x, w, top, bottom, ramp):
    s.rect(x, top, w, bottom - top, ramp[2])
    s.hline(x, x + w - 1, top, ramp[0]).hline(x, x + w - 1, top + 1, ramp[1])
    s.dither(x, top + 2, w, 1, ramp[1], pattern="checker")
    s.rect(x, bottom - 3, w, 3, L_[2]).hline(x, x + w - 1, bottom - 3, L_[3]).hline(x, x + w - 1, bottom - 1, L_[0])


def floor_band(s, x, w, y, kind):
    if kind == "tile":
        s.rect(x, y, w, BAND, L_[2])
        s.hline(x, x + w - 1, y, L_[0]).hline(x, x + w - 1, y + 1, L_[3]).hline(x, x + w - 1, y + 3, L_[1])
        for tx in range(x + 2, x + w, 7):
            s.vline(tx, y + 1, y + 2, L_[1]).vline(tx + 3, y + 4, y + BAND - 1, L_[1])
    else:
        s.rect(x, y, w, BAND, W_[3])
        s.hline(x, x + w - 1, y, W_[1]).hline(x, x + w - 1, y + 1, W_[4])
        for i, yy in enumerate(range(y + 1, y + BAND, 2)):
            s.hline(x, x + w - 1, yy + 1, W_[2])
            for sx in range(x + (i * 7) % 17, x + w, 17):
                s.set(sx, yy, W_[2])


def doorway_wall(s, x, storey, left_ramp, right_ramp, left_kind, right_kind):
    """Interior wall: cut slab-to-lintel, open passage below."""
    top, fl = levels(storey)
    back_wall(s, x, INNER // 2, top, fl, left_ramp)
    back_wall(s, x + INNER // 2, INNER // 2, top, fl, right_ramp)
    floor_band(s, x, INNER // 2, fl, left_kind)
    floor_band(s, x + INNER // 2, INNER // 2, fl, right_kind)
    cut_block(s, x, top, INNER, DOOR_H)
    s.rect(x - 2, top + DOOR_H, INNER + 4, 2, W_[0]).hline(x - 1, x + INNER, top + DOOR_H, W_[3])


def stairs(s):
    """14 steps (3px run, 4px rise) from the ground floor up to the upper floor."""
    x0, w = STAIRS
    n, run, rise = 14, 3, 4
    for i in range(n):
        x = x0 + i * run
        top = GR_FLOOR - rise * (i + 1)
        under = min(top + 14, GR_FLOOR + 1)
        s.rect(x, top, run, under - top, W_[2])
        s.hline(x, x + run - 1, top, W_[4]).hline(x, x + run - 1, top + 1, W_[3])
        s.hline(x, x + run - 1, under - 1, W_[0])
        if i:
            s.vline(x, top, top + rise - 1, W_[1])  # riser shadow
    # landing joins the upper floor at the doorway
    s.rect(x0 + n * run, UP_FLOOR, w - n * run, 4, W_[3])
    s.hline(x0 + n * run, x0 + w - 1, UP_FLOOR, W_[4]).hline(x0 + n * run, x0 + w - 1, UP_FLOOR + 3, W_[0])
    # handrail with posts
    rail = lambda x: int(GR_FLOOR - 12 - (x - x0) * rise / run)
    for x in range(x0 + 1, x0 + n * run):
        s.set(x, rail(x), W_[0]).set(x, rail(x) + 1, W_[3])
    for px in range(x0 + 4, x0 + n * run, 6):
        top = GR_FLOOR - rise * ((px - x0) // run + 1)
        s.vline(px, rail(px) + 2, top - 1, W_[1])


def shell(night=False):
    s = Sprite(W, H)
    # stairwell: one double-height space
    sx, sw = STAIRS
    back_wall(s, sx, sw, UP_WALL, GR_FLOOR, P.wall_cream)
    floor_band(s, sx, sw, GR_FLOOR, "wood")
    for key, _, storey, x, w, ramp, kind in ROOMS:
        top, fl = levels(storey)
        back_wall(s, x, w, top, fl, ramp)
        floor_band(s, x, w, fl, kind)
    # slabs: top, between storeys (open over the stairwell), foundation
    cut_block(s, X0, 0, X1 - X0, SLAB)
    cut_block(s, sx + sw, MID_SLAB, X1 - (sx + sw), SLAB)
    cut_block(s, X0, FOUND, X1 - X0, SLAB + 1)
    # outer walls
    cut_block(s, X0, 0, OUTER, FOUND)
    cut_block(s, X1 - OUTER, 0, OUTER, FOUND)
    # interior walls with doorways
    room = {k: (ramp, kind) for k, _, _, _, _, ramp, kind in ROOMS}
    doorway_wall(s, 54, 1, P.wall_cream, *[room["bedroom"][0]], "wood", "wood")
    doorway_wall(s, 158, 1, room["bedroom"][0], room["bath"][0], "wood", "tile")
    doorway_wall(s, 228, 1, room["bath"][0], room["study"][0], "tile", "wood")
    doorway_wall(s, 54, 0, P.wall_cream, room["living"][0], "wood", "wood")
    doorway_wall(s, 228, 0, room["living"][0], room["kitchen"][0], "wood", "tile")
    stairs(s)
    s.blit(F.round_window(night), sx + 8, UP_WALL + 10)
    s.blit(F.sconce(on=night), sx + 3, GR_WALL + 10)
    # grass lip
    G = P.green
    gy = FOUND + SLAB + 1
    s.rect(X0 - 3, gy, X1 - X0 + 6, H - gy, G[2])
    s.hline(X0 - 4, X1 + 3, gy, G[0]).hline(X0 - 3, X1 + 2, gy, G[3])
    for gx in range(X0 - 2, X1 + 3, 7):
        s.set(gx, gy - 1, G[3]).set(gx + 3, gy - 1, G[2])
    s.hline(X0 - 3, X1 + 2, H - 1, G[1])
    return s


# ---------------------------------------------------------------- placing


def on_floor(s, spr, x, storey, depth=3, shadow=True):
    """Stand a sprite on a storey's floor band; depth = px into the band."""
    _, fl = levels(storey)
    y = fl + depth - spr.h + 1
    sy = fl + depth + 1
    if shadow and sy < fl + BAND:
        feet = np.nonzero(spr.px[-1, :, 3])[0]
        if len(feet):
            s.hline(x + int(feet.min()), x + int(feet.max()), sy, W_[1])
    s.blit(spr, x, y)
    return y


def room_x(key):
    return next(r[3] for r in ROOMS if r[0] == key)


def furnish(s, night=False, buddy=doll.GIRL):
    sky = "night" if night else "day"
    lights, z_at = [], None

    # --- bedroom (upper)
    x, (top, fl) = room_x("bedroom"), levels(1)
    s.blit(F.picture(), x + 14, top + 10)
    s.blit(F.window(sky), x + 46, top + 7)
    on_floor(s, F.rug(36), x + 40, 1, 4)
    on_floor(s, F.bed(), x + 2, 1, 1)
    ns_y = on_floor(s, F.nightstand(), x + 46, 1, 0)
    s.blit(F.lamp(on=night), x + 47, ns_y - 13)
    on_floor(s, F.wardrobe(), x + 72, 1, 0)
    if night:
        z_at = sleeper(s, x + 2, fl + 1 - 22 + 1, buddy)
        lights.append((x + 53, ns_y - 7, 30, (1.0, 0.86, 0.6), "bedroom"))

    # --- bathroom (upper)
    x = room_x("bath")
    s.blit(F.tiles(40, 20), x, fl - 20)
    s.blit(F.shower(), x + 4, top + 6)
    s.blit(F.towel_rail(), x + 40, top + 12)
    s.blit(F.mirror(), x + 51, top + 9)
    on_floor(s, F.rug(18), x + 9, 1, 4)
    on_floor(s, F.bathtub(), x + 2, 1, 1)
    on_floor(s, F.toilet(), x + 39, 1, 1)
    on_floor(s, F.washbasin(), x + 51, 1, 1)

    # --- study (upper)
    x = room_x("study")
    s.blit(F.clock(), x + 10, top + 7)
    s.blit(F.pendant(on=False), x + 30, top)
    s.blit(F.wall_shelf(), x + 46, top + 5)
    on_floor(s, F.plant(), x + 2, 1, 1)
    on_floor(s, F.bookshelf(), x + 70, 1, 0)
    d = F.desk()
    dy = on_floor(s, d, x + 26, 1, 0)
    s.blit(F.monitor(on=not night), x + 34, dy - 14)
    s.blit(F.mug(), x + 54, dy - 4)
    on_floor(s, F.chair(), x + 18, 1, 2)

    # --- living room (ground)
    x, (top, fl) = room_x("living"), levels(0)
    s.blit(F.window(sky), x + 66, top + 7)
    s.blit(F.picture(), x + 18, top + 12)
    on_floor(s, F.plant(), x + 3, 0, 1)
    on_floor(s, F.rug(54), x + 54, 0, 4)
    on_floor(s, F.floor_lamp(on=night), x + 42, 0, 1)
    on_floor(s, F.sofa(), x + 56, 0, 1)
    on_floor(s, F.coffee_table(), x + 66, 0, 5)
    on_floor(s, F.tv_unit(on=False), x + 116, 0, 0)
    on_floor(s, F.plant(tall=False), x + 154, 0, 1)
    if night:
        lights.append((x + 48, top + 12, 34, (1.0, 0.88, 0.62), "living"))

    # --- kitchen (ground)
    x = room_x("kitchen")
    s.blit(F.upper_cabinet(28), x + 2, top + 6)
    s.blit(F.range_hood(), x + 30, top + 13)
    s.vline(x + 39, top, top + 12, M_[0]).vline(x + 38, top, top + 12, M_[3])
    cy = on_floor(s, F.counter(), x + 2, 0, 0)
    t = F.dining_table()
    ty = on_floor(s, t, x + 56, 0, 2)
    s.blit(F.fruit_bowl(), x + 65, ty - 6)
    on_floor(s, F.stool(), x + 52, 0, 4)
    on_floor(s, F.stool(), x + 74, 0, 4)
    on_floor(s, F.fridge(), x + 80, 0, 0)
    if not night:
        on_floor(s, doll.with_emote(buddy.render(expr="happy"), "note"), x + 28, 0, 5)
    else:
        lights.append((x + 40, top + 22, 16, (1.0, 0.9, 0.7), "kitchen"))

    # --- stairwell nightlight
    if night:
        lights.append((STAIRS[0] + 6, GR_WALL + 13, 16, (1.0, 0.85, 0.6), "stairs"))
    return lights, z_at


ZZZ = """
ooooo
...o.
..o..
.o...
ooooo
"""


def sleeper(s, bed_x, bed_y, buddy=doll.GIRL):
    """Buddy asleep: head on the pillow, quilt pulled up to the chin."""
    head = buddy.render(expr="sleepy").crop(0, 0, doll.W, 15)
    s.blit(head, bed_x - 1, bed_y - 5)
    C = P.coral
    qx, qy, qw = bed_x + 15, bed_y + 8, 21
    s.rect(qx, qy, qw, 9, C[0])
    s.ellipse(qx + 11, qy, 7, 1.5, C[0])
    s.ellipse(qx + 11, qy + 1, 6, 1, C[2])
    s.rect(qx + 1, qy + 1, qw - 2, 7, C[2])
    s.hline(qx + 7, qx + 15, qy - 1, C[3]).hline(qx + 1, qx + qw - 2, qy + 7, C[1])
    s.rect(qx + 1, qy + 1, 4, 7, C[3]).vline(qx + 5, qy + 2, qy + 7, C[1]).hline(qx + 1, qx + 4, qy + 1, C[4])
    for zx in range(qx + 9, qx + qw - 2, 4):
        for zy in (qy + 3, qy + 6):
            s.set(zx, zy, C[4])
    return bed_x + 22, bed_y - 4


def zzz(s, x, y):
    s.blit(Sprite.from_grid(ZZZ, {"o": L_[3]}), x, y)
    s.blit(Sprite.from_grid("""
        oooo
        ..o.
        .o..
        oooo
    """, {"o": L_[2]}), x + 7, y - 6)


# ---------------------------------------------------------------- night

EMISSIVE = set(P.sky_night) | set(P.light) | set(P.glass[2:])


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
    night = rgb * np.array([0.38, 0.41, 0.64])
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


def build():
    return {
        "house_day": scene(),
        "house_night": scene(night=True),
        "house_day_boy": scene(buddy=doll.BOY),
    }
