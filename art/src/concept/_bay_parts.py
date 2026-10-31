"""Refined pieces for summer_bay (owner review 2026-10-31, round 4):
anime-style cumulus towers standing on the horizon, Hawaiian fluted mountains,
layered broadleaf canopy trees, a cabana with real depth, a sea stack.
All draw straight into a big Sprite in global coordinates."""
import math
import random

import numpy as np

from pixelkit import P

G = P.green          # broadleaf: 0 outline, 1 shade, 2 body, 3 lit, 4 highlight
B = P.oak            # bamboo
T = P.mustard        # thatch


def _poly(s, pts, colfn):
    ys = [p[1] for p in pts]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        xs = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for x in range(int(round(a)), int(round(b)) + 1):
                _set(s, x, y, colfn(x, y))


def _set(s, x, y, c):
    if 0 <= x < s.w and 0 <= y < s.h:
        s.set(x, y, c)


# ------------------------------------------------------------- clouds

def cumulus(s, cx, base, w, h, seed):
    """A big anime summer cloud (入道云) standing on the horizon: overlapping
    round lobes stacked into a tower. Bright warm-white tops, a cool blue-grey
    belly, each lobe keeps its own rounded shadow so the bubbles read one by
    one, crisp contours where a front lobe overlaps one behind; the foot sinks
    into the horizon haze."""
    from pixelkit import rgba
    rnd = random.Random(seed)
    LIT, MID, SH, DEEP = (np.array(rgba(c), np.uint8) for c in (P.porcelain[3], P.snow[2], P.sky_soft[2], P.sky_soft[1]))
    puffs = []
    y = base - 6
    t = 0.0
    while t <= 1.0:
        half = w / 2 * (1 - 0.55 * t ** 1.2)
        r = (17 + 9 * (1 - abs(t - 0.7))) * (w / 220) ** 0.5
        n = max(1, int(2 * half / (r * 1.25)))
        for k in range(n):
            x = cx - half + (k + 0.5) * (2 * half / n) + rnd.uniform(-r * 0.25, r * 0.25) + 8 * t * math.sin(seed * 1.7)
            puffs.append((x, y - rnd.uniform(0, r * 0.4), r * rnd.uniform(0.85, 1.15), t))
        y -= r * 0.7
        t = (base - 6 - y) / h
    puffs.sort(key=lambda p: p[1])                                   # crown first, front/lower lobes over it
    x0, x1 = max(0, int(cx - w / 2 - 30)), min(s.w, int(cx + w / 2 + 30))
    y0 = max(0, int(base - h - 30))
    yy, xx = np.mgrid[y0:base, x0:x1]
    reg = s.px[y0:base, x0:x1]
    cloud = np.zeros(yy.shape, bool)
    for px, py, r, tt in puffs:
        d2 = (xx - px) ** 2 + (yy - py) ** 2
        inside = d2 <= r * r
        lit = ((xx - px + r * 0.3) ** 2 + (yy - py + r * 0.36) ** 2) <= (r * 0.72) ** 2
        mid = ((xx - px + r * 0.14) ** 2 + (yy - py + r * 0.2) ** 2) <= (r * 0.88) ** 2
        belly = tt < 0.28                                            # the low lobes are in the cloud's own shade
        if belly:
            col = np.where(lit[..., None], MID, SH)
        else:
            col = np.where(lit[..., None], LIT, np.where(mid[..., None], MID, SH))
        rim = inside & (d2 > (r - 1.3) ** 2) & cloud & (yy > py - r * 0.2)
        reg[inside] = col[inside]
        reg[rim] = DEEP if belly else SH
        cloud |= inside
    reg[cloud & (yy >= base - 5)] = MID                              # foot in the haze
    reg[cloud & (yy >= base - 5) & ((xx + yy) % 2 == 0) & (yy < base - 3)] = SH
    return cloud


def wisp(s, cx, y, w, seed):
    """A small flat cloud high up."""
    rnd = random.Random(seed)
    for k in range(int(w / 7)):
        x = cx - w / 2 + k * 7 + rnd.uniform(-2, 2)
        r = rnd.uniform(3, 6)
        for dy in range(-int(r), int(r) + 1):
            hw = int(math.sqrt(max(0, r * r - dy * dy)) * 1.6)
            for dx in range(-hw, hw + 1):
                _set(s, int(x + dx), int(y + dy * 0.6), P.porcelain[3] if dy < r * 0.3 else P.sky_soft[3])


# ------------------------------------------------------------- mountains

def mountains(s, x0, x1, foot, peaks, seed, far=False):
    """Hawaiian volcanic ridges: a jagged ridgeline, deep vertical flutes
    (the Ko'olau look), lit west faces, a pale rim, mist at the foot.
    far=True: one pale, low-contrast layer behind."""
    rnd = random.Random(seed)
    if far:
        LIT, BODY, SH, RIM, FL = P.sky_soft[1], P.sky_soft[0], P.sky_soft[0], P.sky_soft[2], P.sky_soft[0]
    else:
        LIT, BODY, SH, RIM, FL = P.sea_grey[3], P.sea_grey[2], P.sea_grey[1], P.sea_grey[4], P.sea_grey[1]
    ph = [rnd.uniform(0, 6) for _ in range(4)]

    def hgt(x):
        v = sum(h * math.exp(-((x - c) / w) ** 2) for c, w, h in peaks)
        v += 3 * math.sin(x * 0.11 + ph[0]) + 1.5 * math.sin(x * 0.37 + ph[1]) + math.sin(x * 0.9 + ph[2])
        return v

    H = [hgt(x) for x in range(x0 - 1, x1 + 2)]
    for i, x in enumerate(range(x0, x1)):
        h = H[i + 1]
        if h < 4:
            continue
        top = int(foot - h)
        lit_face = H[i + 2] > H[i] - 0.3                             # rising to the right = facing the light
        flute = (x + int(3 * math.sin(x * 0.05))) % 6
        for y in range(top, foot):
            d = y - top
            col = LIT if lit_face else BODY
            if not far and d > 3:
                if flute == 0 and d < h * 0.85:
                    col = FL                                         # a flute groove
                elif flute == 1 and lit_face and d < h * 0.8:
                    col = LIT if lit_face else BODY
                elif not lit_face and flute in (3, 4):
                    col = SH
            _set(s, x, y, col)
        _set(s, x, top, RIM if lit_face else LIT)
    # mist at the foot: an irregular pale band
    for x in range(x0, x1):
        if H[x - x0 + 1] < 4:
            continue
        m = int(5 + 2 * math.sin(x * 0.07) + math.sin(x * 0.23))
        for y in range(foot - m, foot):
            if y > foot - m + 1 or (x + y) % 2 == 0:
                _set(s, x, y, P.sky_soft[3] if not far else P.sky_soft[2])


# ------------------------------------------------------------- trees

def canopy(s, x, base, w, h, seed, R=G, trunk=True):
    """A broadleaf tropical tree (monkeypod / kukui): a forked trunk under an
    umbrella crown built from many leaf clumps, each lit top-left with leafy
    notched edges and light flecks; darker clumps behind, a dark outline."""
    rnd = random.Random(seed)
    top = base - h
    crown_cy = top + h * 0.32
    rx, ry = w / 2, h * 0.3
    if trunk:
        tw = max(2, int(w / 14))
        for y in range(int(crown_cy), base):
            t = (y - crown_cy) / max(1, base - crown_cy)
            xx = x + int(2 * math.sin(t * 2.2 + seed))
            for k in range(tw + (1 if t > 0.85 else 0)):
                _set(s, xx + k, y, P.walnut[2] if k == 0 else P.walnut[1])
        for sgn in (-1, 1):                                          # two limbs into the crown
            for k in range(int(rx * 0.6)):
                _set(s, x + sgn * k, int(crown_cy + ry * 0.6 - k * 0.5), P.walnut[1])
    clumps = []
    for _ in range(int(w * h / 26)):
        a = rnd.uniform(0, math.tau)
        rr = math.sqrt(rnd.random())
        cx = x + math.cos(a) * rx * rr
        cy = crown_cy + math.sin(a) * ry * rr * (0.8 if math.sin(a) > 0 else 1.1)
        clumps.append((cx, cy, rnd.uniform(3.5, 6.5)))
    clumps.sort(key=lambda c: c[1] - (c[0] - x) * 0.2)              # back/top first, lower-left front last
    mask = set()
    for cx, cy, r in clumps:
        depth = (cy - (crown_cy - ry)) / (2 * ry)                    # 0 top .. 1 bottom
        for dy in range(-int(r) - 1, int(r) + 2):
            for dx in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(dx, dy * 1.15)
                edge_noise = 0.8 * math.sin((math.atan2(dy, dx)) * 5 + cx)      # notched leafy rim
                if d > r + edge_noise:
                    continue
                px, py = int(cx + dx), int(cy + dy)
                u = (dx + dy) / (r * 1.4)
                if u < -0.45:
                    col = R[3]
                elif u < 0.35:
                    col = R[2]
                else:
                    col = R[1]
                if depth > 0.75 and col == R[2]:
                    col = R[1]
                if col == R[3] and (px * 7 + py * 3) % 11 == 0:
                    col = R[4]
                _set(s, px, py, col)
                mask.add((px, py))
    for px, py in mask:                                              # outline
        for nx, ny in ((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)):
            if (nx, ny) not in mask:
                _set(s, nx, ny, R[0])


def understory(s, x0, x1, ground, seed):
    """Low ferns and shrubs along the foot of the trees."""
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        r = rnd.uniform(4, 7)
        canopy(s, int(x), ground(int(x)) + 1, int(r * 2.6), int(r * 2.2), rnd.randint(0, 9999), trunk=False)
        x += rnd.uniform(6, 11)


def jungle(s, x0, x1, ground, seed, skip=()):
    """Back row (hazy sage, smaller) then front row of canopy trees."""
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        w = rnd.randint(30, 44)
        if not any(a <= x <= b for a, b in skip):
            canopy(s, int(x), ground(int(x)) - 2, w, rnd.randint(22, 30), rnd.randint(0, 9999), R=P.sage)
        x += w * 0.55
    x = x0 + 10
    while x < x1:
        w = rnd.randint(26, 40)
        if not any(a <= x <= b for a, b in skip):
            canopy(s, int(x), ground(int(x)), w, rnd.randint(26, 38), rnd.randint(0, 9999))
        x += w * 0.7 + rnd.uniform(0, 14)


# ------------------------------------------------------------- cabana with depth

def cabana3d(s, x0, x1, base, doors):
    """The changing hut drawn with volume: a raised plank deck with a step,
    the bamboo front wall, the right side wall receding (darker), corner
    posts, a deep shadow band under the eaves, curtained door recesses, and a
    hip thatch roof with its own right-hand slope and underside."""
    D = 14                                                           # depth: side wall goes back up-right
    dx, dy = D, D // 2
    wall_top = base - 34
    deck = base - 3
    # side wall (parallelogram)
    for i in range(dx + 1):
        yt = wall_top - i * dy // dx
        yb = deck - i * dy // dx
        for y in range(yt, yb):
            c = B[1] if (i % 3) else B[0]
            if (y - yt) % 7 == 3:
                c = B[0]
            _set(s, x1 + i, y, c)
    # deck: top surface + front edge + step
    for i in range(dy + 1):
        s.hline(x0 - 4 + i * 2, x1 + 4 + i * 2, deck - i, B[3] if i < dy else B[2])
    s.rect(x0 - 4, deck, x1 - x0 + 9, 3, P.walnut[2]).hline(x0 - 4, x1 + 4, deck, P.walnut[3])
    for x in range(x0 - 4, x1 + 5, 6):
        s.vline(x, deck + 1, base - 1, P.walnut[1])
    # front wall
    s.rect(x0, wall_top, x1 - x0, deck - wall_top, B[2])
    for x in range(x0, x1, 3):
        s.vline(x, wall_top, deck - 1, B[3]).vline(x + 2, wall_top, deck - 1, B[1])
        for y in range(wall_top + (x % 5), deck, 7):
            s.hline(x, x + 2, y, B[1])
    for px in (x0, x1 - 2):                                          # corner posts
        s.rect(px, wall_top, 3, deck - wall_top, P.walnut[2]).vline(px, wall_top, deck - 1, P.walnut[3])
    s.rect(x0, wall_top, x1 - x0, 4, P.walnut[0])                    # shadow under the eaves
    s.hline(x0, x1, wall_top + 4, B[1])
    # doors: dark recess, curtain set back, sill
    for key, cx in doors.items():
        C = P.coral if key == "bikini" else P.hydrangea
        s.rect(cx - 10, deck - 27, 20, 27, P.walnut[0])
        for x in range(cx - 8, cx + 8):
            c = C[3] if (x - cx) % 4 in (0, 1) else C[2]
            s.vline(x, deck - 25, deck - 2, c)
            s.set(x, deck - 25, C[1])
        s.vline(cx - 8, deck - 25, deck - 2, C[1])
        s.hline(cx - 10, cx + 9, deck - 27, P.walnut[2])
        sy = deck - 31
        s.ellipse(cx, sy, 5, 4, P.walnut[2]).ellipse(cx, sy, 4, 3, P.oat[3])
        direction=1 if key=='bikini' else -1  # left enters, right exits
        s.vline(cx,sy-2,sy+2,P.walnut[0])
        s.line(cx,sy+direction*2,cx-2,sy,P.walnut[0]).line(cx,sy+direction*2,cx+2,sy,P.walnut[0])
    # Timber feet and a sand contact shadow join the deck to the beach.
    s.rect(x0-4,deck+3,x1-x0+9,3,P.walnut[1])
    s.hline(x0-6,x1+8,base+3,P.sand[1])
    # roof: front slope (trapezoid), right hip slope, ridge, ragged eave, underside
    top = wall_top - 24
    ex0, ex1 = x0 - 10, x1 + 10
    rnd = random.Random(x0)
    for y in range(top, wall_top + 2):
        t = (y - top) / (wall_top + 2 - top)
        a = int(ex0 + (1 - t) * 26)
        b = int(ex1 - (1 - t) * 26)
        for x in range(a, b + 1):
            c = T[2] if (x + y // 2) % 3 else T[1]
            if (x - a) < 2 or y - top < 1:
                c = T[3]
            _set(s, x, y, c)
    hip = [(ex1, wall_top + 2), (ex1 - 26, top), (ex1 - 26 + dx, top - dy), (ex1 + dx, wall_top + 2 - dy)]
    _poly(s, hip, lambda x, y: T[1] if (x + y // 2) % 3 else T[0])
    _poly(s, [(ex1 - 26, top), (ex0 + 26, top), (ex0 + 26 + dx, top - dy), (ex1 - 26 + dx, top - dy)],
          lambda x, y: T[3] if (x + y) % 3 else T[2])                # the ridge's top strip
    for i in range(dx + 1):                                          # ridge line running back
        _set(s, ex1 - 26 + i, top - i * dy // dx, T[3])
    s.hline(ex0 + 26, ex1 - 26, top, T[4])
    for x in range(ex0, ex1 + dx):                                   # ragged straw eave
        yb = wall_top + 2 - max(0, x - ex1) * dy // dx
        for k in range(rnd.randint(1, 3)):
            _set(s, x, yb + k, T[1] if k else T[2])
    # cast shadow on the sand to the right
    for i in range(10):
        s.hline(x1 + dx + 1, x1 + dx + 1 + 10 - i, base - 1 - i // 4, P.sand[2])


# ------------------------------------------------------------- beach chair

def beach_chair(s, cx, base, C):
    """A small wooden folding beach chair seen from the front (owner: the first
    one was too big): back posts, a striped canvas back, a sling seat, short
    armrests. Sized to a seated Buddy: the back peeks out round her shoulders."""
    Wd = P.walnut
    top, seat = base - 20, base - 6
    for px in (cx - 8, cx + 7):                                      # back posts
        s.vline(px, top, base - 1, Wd[2]).vline(px + 1, top, base - 1, Wd[1])
        s.set(px, top, Wd[3])
    for y in range(top + 1, seat):                                   # striped canvas back
        for x in range(cx - 6, cx + 7):
            col = C[3] if ((x - cx) // 2) % 2 == 0 else P.porcelain[3]
            if x == cx + 6 or y == seat - 1:
                col = C[1] if col == C[3] else P.porcelain[1]
            s.set(x, y, col)
    s.rect(cx - 7, seat, 15, 2, C[1]).hline(cx - 7, cx + 7, seat, C[2])   # sling seat
    for sgn in (-1, 1):                                              # armrests
        ax = cx + sgn * 9
        s.hline(min(ax, ax - sgn * 3), max(ax, ax - sgn * 3), seat - 3, Wd[3])
        s.vline(ax, seat - 3, base - 1, Wd[1])
    for k in range(4):                                               # crossed front legs
        s.set(cx - 5 + k * 3, seat + 2 + k // 2, Wd[2]).set(cx + 5 - k * 3, seat + 2 + k // 2, Wd[1])
    s.hline(cx - 9, cx + 9, base - 1, Wd[0])


# ------------------------------------------------------------- sea stack

def sea_stack(s, x0, x1, wl, floor, seed):
    """A lava sea stack closing the map on the right: one organic mass of
    overlapping rounded lumps (lower lumps in front), each faceted like the
    beach boulders (rust sunlit top-left, dark teal body, shadow lower right,
    a sandy chip), one outline round the whole mass, a wet dark band and foam
    at the waterline, a grassy cap."""
    rnd = random.Random(seed)
    cx = (x0 + x1) / 2
    W = x1 - x0
    lumps = []
    y = wl + 46
    while y > wl - 40:
        t = (wl + 46 - y) / 86
        half = W / 2 * (1 - 0.5 * t)
        for _ in range(3 if half > 30 else 2):
            lx = cx + rnd.uniform(-half * 0.8, half * 0.8) - t * 6
            rx = rnd.uniform(10, 17) * (1 - 0.3 * t)
            lumps.append((lx, y + rnd.uniform(-3, 3), rx, rx * rnd.uniform(0.6, 0.8)))
        y -= rnd.uniform(7, 10)
    # one mass: the union of the lumps, shaded as a whole (light from the
    # upper left), the lumps' upper rims kept as ledges and cracks
    bx0, by0 = int(x0 - 30), int(wl - 70)
    bw, bh = int(W + 60), 140
    yy, xx = np.mgrid[by0:by0 + bh, bx0:bx0 + bw]
    m = np.zeros(yy.shape, bool)
    ledges = np.zeros(yy.shape, bool)
    for lx, ly, rx, ry in lumps:
        e = ((xx - lx) / (rx * 1.25)) ** 2 + ((yy - ly) / (ry * 1.2)) ** 2
        inside = e <= 1 + 0.1 * np.sin(xx * 0.9 + yy * 0.7)
        ledges |= inside & (e > 0.72) & (yy < ly - ry * 0.3) & m     # its top rim where it sits on rock already
        m |= inside
    for r in range(bh):                                              # solid rock: no holes, and the lower part
        cs = np.nonzero(m[r])[0]                                     # runs on into the reef wall on the right
        if len(cs):
            m[r, cs[0]:cs[-1] + 1] = True
            if by0 + r > wl + 18:
                m[r, cs[0]:] = True

    def sh(dx, dy):
        out = np.zeros_like(m)
        out[max(0, dy):bh + min(0, dy), max(0, dx):bw + min(0, dx)] = \
            m[max(0, -dy):bh - max(0, dy), max(0, -dx):bw - max(0, dx)]
        return out
    lit1 = m & ~sh(2, 2)
    lit2 = m & ~sh(7, 8)
    dark = m & ~sh(-3, -3)
    cols = {}
    for name, sel, c in (("body", m, P.teal[1]), ("lit2", lit2, P.clay[2]), ("lit1", lit1, P.clay[3]),
                         ("led", ledges & ~lit1, P.clay[2]), ("dark", dark & ~lit1, P.teal[0])):
        for y, x in zip(*np.nonzero(sel)):
            cols[(x, y)] = c
    for y, x in zip(*np.nonzero(ledges & lit2)):
        cols[(x, y)] = P.sand[3]
    for (x, y), c in cols.items():
        gy = by0 + y
        if wl < gy < wl + 4:
            c = P.teal[0] if c in (P.teal[1], P.teal[0]) else P.clay[1]       # wet band at the waterline
        _set(s, bx0 + x, gy, c)
    edge = m & ~(sh(1, 0) & sh(-1, 0) & sh(0, 1) & sh(0, -1))
    for y, x in zip(*np.nonzero(edge)):
        _set(s, bx0 + x, by0 + y, P.teal[0])
    mask = {(bx0 + x, by0 + y) for y, x in zip(*np.nonzero(m))}
    top = min(py for px, py in mask)
    capx = int(sum(px for px, py in mask if py == top) / max(1, sum(1 for px, py in mask if py == top)))
    for k in range(-10, 11):
        for j in range(3 - abs(k) // 4):
            if (capx + k, top + 2) in mask or abs(k) < 6:
                _set(s, capx + k, top + 1 - j, G[3] if j == 2 - abs(k) // 4 else G[2])
    return capx, top
