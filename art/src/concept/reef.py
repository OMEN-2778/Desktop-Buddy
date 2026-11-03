"""热带海洋 v2 (owner 2026-11-03): every fish and coral redrawn, vivid and lively,
a diving-game feel (big readable sprites, saturated hue-shifted ramps, round
shading, glinting eyes). Original art. Seaweeds stay in sea_life.py (owner likes them).
Art only: a review sheet; nothing is wired into the game yet.

Light from the top left. Each part is outlined in the darkest shade of its own
ramp. Fish face right; the game flips them.
"""
import math
import random

import numpy as np

from pixelkit import P, Sprite, rgba

PREVIEW_SCALE = 4


def C(c):
    return np.array(rgba(c), np.uint8)


# ----------------------------------------------------------------- helpers

def poly_mask(w, h, pts):
    """Filled polygon (pixel centres inside)."""
    m = np.zeros((h, w), bool)
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs + 0.5, ys + 0.5
    inside = np.zeros((h, w), bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        cond = ((y1 > py) != (y2 > py))
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (x2 - x1) * (py - y1) / (y2 - y1 + 1e-9) + x1
        inside ^= cond & (px < xint)
    m |= inside
    return m


def ring(mask):
    """Pixels of the mask that touch the outside (4-neighbour)."""
    a = mask
    inner = a.copy()
    inner[1:-1, 1:-1] = a[1:-1, 1:-1] & a[:-2, 1:-1] & a[2:, 1:-1] & a[1:-1, :-2] & a[1:-1, 2:]
    inner[0, :] = inner[-1, :] = False
    inner[:, 0] = inner[:, -1] = False
    return a & ~inner


def grow(mask):
    g = mask.copy()
    g[1:] |= mask[:-1]
    g[:-1] |= mask[1:]
    g[:, 1:] |= mask[:, :-1]
    g[:, :-1] |= mask[:, 1:]
    return g


def paint(s, mask, colour):
    s.px[mask] = C(colour)


def smooth_curve(keys, n):
    """keys: [(t, value)] t in 0..1 -> n samples, cosine-eased between keys."""
    ts = np.linspace(0, 1, n)
    out = np.zeros(n)
    for i, t in enumerate(ts):
        for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / max(1e-9, t1 - t0)
                u = (1 - math.cos(u * math.pi)) / 2
                out[i] = v0 + (v1 - v0) * u
                break
    return out


def tone_of(v, x, y, t=0.5):
    """Shade index (0..4) for a body pixel: v -1 back .. 1 belly. Round form,
    lit from above-left, a lit belly rim (reflected light from the sand)."""
    k = v - 0.18 * (t - 0.5)                 # the head side catches a bit more light
    edges = [(-0.62, 4), (-0.2, 3), (0.42, 2), (0.82, 1), (9, 2)]
    prev = 4
    for lim, idx in edges:
        if k < lim:
            # soft band edges: a checker step near each boundary
            if abs(k - lim) < 0.07 and (x + y) % 2 and idx != prev:
                return prev if k > lim else idx
            return idx
        prev = idx
    return 2


# ----------------------------------------------------------------- the fish engine

def fish(L, top, bot, body, *, fin=None, tail=("fork", 7, 10), dorsal=None, anal=None, pelvic=None,
         pectoral=True, pattern=None, eye=(0.86, -0.2), eye_r=1, iris=None, gill=0.72, mouth=0.0,
         scales=False, glow=True):
    """A fish facing right, body length L.
    top/bot: keys [(t, y)] for the back and belly lines, t 0 (tail root) .. 1 (snout), y in px from the
      centre line (top negative). body: 5-shade ramp. fin: fin ramp.
    tail: (shape, length, height) shape fork|lunate|round|square|point.
    dorsal/anal: list of (t, extra height) keys over the back / belly, or None.
    pattern(t, v, x, y) -> ramp (shaded) | '#hex' (flat) | None.
    """
    fin = fin or body
    TL, TH = tail[1], tail[2]
    top_c = smooth_curve(top, L)
    bot_c = smooth_curve(bot, L)
    d_c = smooth_curve(dorsal, L) if dorsal else np.zeros(L)
    a_c = smooth_curve(anal, L) if anal else np.zeros(L)
    up = int(math.ceil(max(-(top_c - d_c).min(), TH / 2))) + 3
    dn = int(math.ceil(max((bot_c + a_c).max(), TH / 2))) + 3
    W, H = L + TL + 4, up + dn + 1
    cy = up
    x0 = TL + 2
    s = Sprite(W, H)

    def layer(mask, ramp, rays=None, rim_hi=True):
        """A fin layer: fill with ramp[2], rays ramp[1], lit top edge ramp[3], outline ramp[0]."""
        paint(s, mask, ramp[3])
        if rays is not None:
            paint(s, mask & rays, ramp[2])
        if rim_hi:
            hi = mask & ~np.roll(mask, 1, axis=0)
            hi[0] = mask[0]
            paint(s, hi, ramp[3])
        out = grow(mask) & ~mask
        out &= s.px[..., 3] == 0
        paint(s, out, ramp[0])

    ys, xs = np.mgrid[0:H, 0:W]
    # rays: oblique stripes every 2 px
    rays_fwd = ((xs + ys) % 3 == 0)
    rays_v = (xs % 3 == 0)

    # --- tail
    shape = tail[0]
    tx1 = x0 + 1
    tx0 = x0 - TL
    root_h = max(2, (bot_c[0] - top_c[0]) * 0.55)
    if shape == "fork":
        pts = [(tx1, cy - root_h / 2), (tx0, cy - TH / 2), (tx0 + TL * 0.55, cy), (tx0, cy + TH / 2), (tx1, cy + root_h / 2)]
    elif shape == "lunate":
        pts = [(tx1, cy - root_h / 2), (tx0 - 1, cy - TH / 2 - 1), (tx0 + TL * 0.3, cy - TH / 4), (tx0 + TL * 0.45, cy),
               (tx0 + TL * 0.3, cy + TH / 4), (tx0 - 1, cy + TH / 2 + 1), (tx1, cy + root_h / 2)]
    elif shape == "round":
        pts = [(tx1, cy - root_h / 2)] + [(tx1 - TL * math.sin(a), cy - TH / 2 * math.cos(a)) for a in np.linspace(0.25, math.pi - 0.25, 9)] + [(tx1, cy + root_h / 2)]
    elif shape == "point":
        pts = [(tx1, cy - root_h / 2), (tx0, cy), (tx1, cy + root_h / 2)]
    else:  # square / slightly concave
        pts = [(tx1, cy - root_h / 2), (tx0, cy - TH / 2), (tx0 + 1, cy), (tx0, cy + TH / 2), (tx1, cy + root_h / 2)]
    tail_m = poly_mask(W, H, pts)
    layer(tail_m, fin, rays_fwd if shape != "point" else None)

    # --- dorsal + anal fins (behind the body)
    body_m = np.zeros((H, W), bool)
    for i in range(L):
        x = x0 + i
        y0, y1 = cy + top_c[i], cy + bot_c[i]
        body_m[int(round(y0)):int(round(y1)) + 1, x] = True
    if dorsal:
        dm = np.zeros((H, W), bool)
        for i in range(L):
            if d_c[i] > 0.4:
                y0 = cy + top_c[i]
                dm[int(round(y0 - d_c[i])):int(round(y0)) + 1, x0 + i] = True
        layer(dm & ~body_m, fin, rays_v)
    if anal:
        am = np.zeros((H, W), bool)
        for i in range(L):
            if a_c[i] > 0.4:
                y1 = cy + bot_c[i]
                am[int(round(y1)):int(round(y1 + a_c[i])) + 1, x0 + i] = True
        layer(am & ~body_m, fin, rays_v, rim_hi=False)
    if pelvic:
        pt, plen = pelvic
        i = int(pt * L)
        yb = cy + bot_c[i]
        pm = poly_mask(W, H, [(x0 + i - 1, yb - 1), (x0 + i + 2, yb - 1), (x0 + i - 2, yb + plen)])
        layer(pm & ~body_m, fin, None, rim_hi=False)

    # --- body: shaded round form
    for i in range(L):
        x = x0 + i
        t = i / max(1, L - 1)
        y0, y1 = cy + top_c[i], cy + bot_c[i]
        mid, half = (y0 + y1) / 2, max(0.5, (y1 - y0) / 2)
        for y in range(int(round(y0)), int(round(y1)) + 1):
            v = (y - mid) / half
            idx = tone_of(v, x, y, t)
            ramp = body
            if pattern:
                p = pattern(t, v, x, y)
                if isinstance(p, str):
                    s.set(x, y, p)
                    continue
                if p is not None:
                    ramp = p
            s.set(x, y, ramp[idx])
    if scales:          # scale hints: a sparse lattice of darker ticks on the mid flank
        for i in range(2, L - 4):
            x = x0 + i
            t = i / L
            if t > gill - 0.04:
                continue
            y0, y1 = cy + top_c[i], cy + bot_c[i]
            for y in range(int(y0) + 2, int(y1) - 1):
                if (x * 2 + (y % 4) * 3) % 6 == 0 and y % 2 == 0 and body_m[y, x]:
                    cur = s.px[y, x].copy()
                    for r in (body, scales if isinstance(scales, list) else body):
                        hexes = [C(c) for c in r]
                        for k in range(1, 5):
                            if (cur == hexes[k]).all():
                                s.px[y, x] = hexes[k - 1]
                                break
    # body outline: darkest body shade (but a lit back line at the very top)
    rim = ring(body_m)
    out = grow(body_m) & ~body_m
    paint(s, out & (s.px[..., 3] == 0), body[0])
    # the outline ring of the body itself stays shaded; re-dark the lower rim for weight
    low = rim & np.roll(~body_m, -1, axis=0)
    paint(s, low, body[0])
    # back line highlight
    hi = rim & np.roll(~body_m, 1, axis=0)
    hi[:, :x0 + 2] = False
    if glow:
        paint(s, hi, body[4])
        # re-outline above the highlight so it reads as edge-lit, not a gap
        above = np.roll(hi, -1, axis=0) & ~body_m
        paint(s, above, body[0])

    # --- gill line: a soft arc
    gi = int(gill * L)
    if 0 < gi < L - 2:
        y0, y1 = cy + top_c[gi], cy + bot_c[gi]
        for y in range(int(round(y0)) + 2, int(round(y1)) - 1):
            v = (y - (y0 + y1) / 2) / max(1, (y1 - y0) / 2)
            xx = x0 + gi - int(round(1.6 * v * v))
            cur = s.px[y, xx]
            ramp = body
            s.set(xx, y, ramp[1] if v > -0.4 else ramp[2])

    # --- pectoral fin: a small fan on the flank behind the gill
    if pectoral:
        pi_ = max(2, gi - 1)
        y0, y1 = cy + top_c[pi_], cy + bot_c[pi_]
        py = y0 + (y1 - y0) * 0.55
        plen = max(3, int(L * 0.16))
        pm = poly_mask(W, H, [(x0 + pi_, py - 1), (x0 + pi_ + 1, py + 1.5), (x0 + pi_ - plen, py + 2.5), (x0 + pi_ - plen + 1, py - 0.5)])
        pr = fin if fin is not body else body
        paint(s, pm, pr[3])
        paint(s, pm & rays_fwd, pr[2])
        paint(s, ring(pm) & np.roll(~pm, -1, axis=0), pr[1])

    # --- mouth
    sx = x0 + L - 1
    sy = int(round(cy + (top_c[-1] + bot_c[-1]) / 2 + mouth))
    s.set(sx, sy, body[0])
    s.set(sx - 1, sy, body[1])

    # --- eye: dark pupil, iris ring, white glint (top-left)
    ex = x0 + int(round(eye[0] * (L - 1)))
    ei = min(L - 1, int(eye[0] * (L - 1)))
    ey = int(round(cy + (top_c[ei] + bot_c[ei]) / 2 + eye[1] * (bot_c[ei] - top_c[ei]) / 2))
    if eye_r == 0 or (eye_r == 1 and L <= 12):
        s.rect(ex, ey, 2, 2, P.ink[0])
        s.set(ex, ey, P.reef_pearl[4])
    elif eye_r <= 1:
        # a big cartoon eye: light sclera ring (rounded), 2x2 pupil, a glint
        for dy in range(-1, 3):
            for dx in range(-1, 3):
                if dx in (-1, 2) and dy in (-1, 2):
                    continue
                s.set(ex + dx, ey + dy, iris or P.reef_pearl[3])
        s.rect(ex, ey, 2, 2, P.ink[0])
        s.set(ex, ey, P.reef_pearl[4])
    else:
        r = eye_r
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d = dx * dx + dy * dy
                if d <= r * r + 0.5:
                    s.set(ex + dx, ey + dy, (iris or P.reef_pearl[3]) if d > (r - 1) ** 2 + 0.5 else P.ink[0])
        s.set(ex - 1, ey - 1, P.reef_pearl[4])
    return s


# ----------------------------------------------------------------- small reef fish

def yellow_tang():
    """Lāʻīpala: a lemon disc, pointed snout, white scalpel by the tail."""
    Y = P.reef_yellow
    s = fish(18, [(0, -3), (0.35, -8), (0.7, -7), (0.92, -3), (1, -1)], [(0, 3), (0.35, 8), (0.7, 6), (0.92, 2), (1, 0)], Y,
             tail=("square", 5, 9), dorsal=[(0, 0), (0.08, 3), (0.6, 3), (0.8, 0), (1, 0)],
             anal=[(0, 0), (0.08, 3), (0.55, 2.5), (0.7, 0), (1, 0)], eye=(0.8, -0.35), mouth=-0.5)
    s.set(7, s.h // 2, P.reef_pearl[4])
    s.set(8, s.h // 2, P.reef_pearl[3])
    return s


def regal_tang():
    """Blue tang: electric blue, a black 'palette' swoop, a yellow tail."""
    B = P.reef_blue

    def pat(t, v, x, y):
        if not 0.1 < t < 0.86:
            return None
        top = -0.5 + 0.1 * math.sin(t * 6)                       # band from the eye back along the upper flank
        loop = -0.45 + 0.85 * math.sin(min(1, max(0, (t - 0.1) / 0.62)) * math.pi)   # the loop dips down mid-body
        if abs(v - top) < 0.2 or (0.12 < t < 0.72 and abs(v - loop) < 0.17):
            return P.reef_night[1] if v > -0.55 else P.reef_night[2]
        return None
    s = fish(22, [(0, -3), (0.35, -7), (0.75, -6), (0.95, -2), (1, -1)], [(0, 3), (0.4, 7), (0.75, 5), (0.95, 2), (1, 0)], B,
             fin=P.reef_night, tail=("fork", 6, 11), dorsal=[(0, 0), (0.1, 2), (0.65, 2.5), (0.85, 0), (1, 0)],
             anal=[(0, 0), (0.1, 2), (0.55, 2), (0.7, 0), (1, 0)], pattern=pat, eye=(0.84, -0.25))
    # yellow tail
    Y = P.reef_yellow
    for y in range(s.h):
        for x in range(0, 7):
            c = s.px[y, x]
            if c[3] and not (c[:3] == C(P.reef_night[0])[:3]).all():
                s.px[y, x] = C(Y[3] if (y < s.h / 2) else Y[2])
    return s


def clownfish():
    """Orange with three white bars edged in black, rounded fins with black rims."""
    O = P.reef_orange

    def pat(t, v, x, y):
        for c, w in ((0.76, 0.06), (0.46, 0.07), (0.1, 0.05)):
            if abs(t - c) < w:
                return P.reef_pearl
            if abs(t - c) < w + 0.05:
                return P.reef_night[0]
        return None
    s = fish(20, [(0, -3), (0.4, -5.5), (0.8, -5), (0.95, -3), (1, -1)], [(0, 3), (0.4, 5.5), (0.8, 4.5), (0.95, 2), (1, 0)], O,
             tail=("round", 5, 8), dorsal=[(0, 0), (0.08, 2.5), (0.4, 3.5), (0.5, 1.5), (0.7, 2.5), (0.85, 0), (1, 0)],
             anal=[(0, 0), (0.1, 2.5), (0.35, 2.5), (0.45, 0), (1, 0)], pelvic=(0.6, 2), pattern=pat, eye=(0.86, -0.3), pectoral=False)
    return s


def moorish_idol():
    """Kihikihi: tall black/white/yellow bands, orange snout saddle, a long white streamer."""
    def pat(t, v, x, y):
        if 0.5 < t < 0.68 or 0.06 < t < 0.2:
            return P.reef_night
        if t > 0.86 and v < 0.0:
            return P.reef_orange
        if 0.2 <= t <= 0.5:
            return P.reef_yellow if v < 0.25 else P.reef_pearl
        return P.reef_pearl if v > -0.3 else P.reef_yellow
    s = fish(18, [(0, -2), (0.3, -9), (0.6, -10), (0.85, -4), (1, -1)], [(0, 2), (0.3, 9), (0.6, 8), (0.85, 3), (1, 0)], P.reef_pearl,
             fin=P.reef_night, tail=("fork", 5, 8), dorsal=[(0, 0), (0.25, 0), (0.42, 5), (0.6, 2), (0.7, 0), (1, 0)],
             anal=[(0, 0), (0.25, 0), (0.42, 4), (0.62, 1), (0.7, 0), (1, 0)], pattern=pat, eye=(0.8, -0.3))
    s2 = Sprite(s.w + 6, s.h + 7)
    s2.blit(s, 6, 7)
    ys, xs = np.nonzero(s.px[..., 3] > 0)
    tx = int(xs[ys == ys.min()].mean()) + 6
    ty = int(ys.min()) + 7
    for k in range(22):
        x = tx - k
        y = ty - int(5 * math.sin(min(1, k / 8) * math.pi / 2)) + max(0, (k - 12) // 2)
        if 0 <= x < s2.w and s2.px[y, x, 3] == 0 or k < 2:
            s2.set(x, y, P.reef_pearl[4] if k % 5 else P.reef_pearl[3])
    return s2


def butterflyfish():
    """Raccoon butterflyfish: yellow, black mask with a white band, oblique lines."""
    def pat(t, v, x, y):
        if 0.74 < t < 0.88 and v < 0.3:
            return P.reef_night
        if 0.64 < t <= 0.74 and v < 0.1:
            return P.reef_pearl
        if t < 0.62 and (x + y * 2) % 5 == 0 and abs(v) < 0.8:
            return P.reef_yellow[1]
        return None
    return fish(18, [(0, -3), (0.35, -7), (0.75, -6), (0.95, -2), (1, -1)], [(0, 3), (0.4, 7), (0.75, 5), (0.95, 1.5), (1, 0)], P.reef_yellow,
                tail=("round", 4, 8), dorsal=[(0, 0), (0.05, 3), (0.65, 2.5), (0.8, 0), (1, 0)],
                anal=[(0, 0), (0.08, 3), (0.5, 2), (0.65, 0), (1, 0)], pattern=pat, eye=(0.82, -0.15), mouth=0.5)


def triggerfish():
    """Humuhumunukunukuāpuaʻa: a sandy diamond, black wedge, blue bars at the eye, yellow lip."""
    def pat(t, v, x, y):
        if 0.3 < t < 0.55 and 0.1 < v < 0.8 - (t - 0.3) * 2.2:
            return P.reef_night
        if t > 0.66 and abs(v - (t - 0.8) * 3) < 0.2:
            return P.reef_blue
        if t > 0.92 and v > -0.1:
            return P.reef_yellow
        if t < 0.18 and v > -0.6 and v < 0.6:
            return P.reef_night if (x // 2) % 2 else P.reef_pearl
        if v > 0.5:
            return P.reef_pearl
        return None
    return fish(26, [(0, -2), (0.4, -7), (0.7, -6), (0.95, -2), (1, -1)], [(0, 2), (0.45, 7), (0.75, 5), (0.95, 2), (1, 0)], P.sand,
                tail=("round", 5, 8), dorsal=[(0, 0), (0.15, 2.5), (0.45, 2.5), (0.5, 0), (1, 0)],
                anal=[(0, 0), (0.15, 2.5), (0.45, 2.5), (0.5, 0), (1, 0)], pattern=pat, eye=(0.66, -0.45), mouth=-0.5)


def flame_angel():
    """Flame angelfish: red-orange with dark vertical bars and blue-tipped back fins."""
    def pat(t, v, x, y):
        if 0.15 < t < 0.75 and (int(t * 30) % 5 == 0) and abs(v) < 0.75:
            return P.reef_red
        return None
    s = fish(18, [(0, -3), (0.4, -7), (0.8, -5), (0.95, -2), (1, -1)], [(0, 3), (0.4, 7), (0.8, 5), (0.95, 2), (1, 0)], P.reef_orange,
             fin=P.reef_red, tail=("round", 5, 8), dorsal=[(0, 0), (0.05, 3), (0.65, 2.5), (0.8, 0), (1, 0)],
             anal=[(0, 0), (0.08, 3), (0.5, 2), (0.65, 0), (1, 0)], pattern=pat, eye=(0.84, -0.2))
    # blue fin edges
    edge = (s.px[..., 3] > 0)
    for y in range(s.h):
        for x in range(s.w):
            if (s.px[y, x, :3] == C(P.reef_red[0])[:3]).all() and (y < s.h * 0.25 or y > s.h * 0.75):
                s.px[y, x] = C(P.reef_blue[3])
    return s


def lionfish():
    """Red-white striped body, fan of spined pectoral feathers, tall separated spines."""
    def pat(t, v, x, y):
        k = int(t * 26 + v * 2)
        return P.reef_red if k % 3 else P.reef_pearl
    s = fish(26, [(0, -2), (0.4, -5), (0.75, -5), (0.95, -2), (1, -1)], [(0, 2), (0.4, 5), (0.75, 4), (0.95, 2), (1, 0)], P.reef_red,
             fin=P.reef_red, tail=("round", 5, 7), anal=[(0, 0), (0.15, 3), (0.35, 2), (0.45, 0), (1, 0)],
             pattern=pat, pectoral=False, eye=(0.84, -0.3), eye_r=1)
    W, H = s.w + 2, s.h + 12
    o = Sprite(W, H)
    # spines over the back
    base_y = 10 + 0
    ys, xs = np.nonzero(s.px[..., 3] > 0)
    top = {x: ys[xs == x].min() for x in set(xs)}
    for k in range(7):
        x = 12 + k * 2 + 4
        y0 = top.get(x - 0, 4) + 10
        ln = 9 - abs(k - 2)
        for j in range(ln):
            o.set(x - j // 4, y0 - j, P.reef_pearl[3] if (j // 2) % 2 else P.reef_red[2])
        o.set(x - ln // 4, y0 - ln, P.reef_red[0])
    # pectoral fan: a pale membrane with rows of red dots, spread down and back
    cx, cy = 21, 10 + s.h // 2
    fan = poly_mask(W, H, [(cx, cy - 1), (cx + 1, cy + 1)] + [(cx - math.sin(a) * 16, cy + math.cos(a) * 13) for a in np.linspace(0.5, 1.8, 9)])
    paint(o, fan, P.reef_pink[3])
    ys, xs = np.nonzero(fan)
    for y, x in zip(ys, xs):
        if (round(math.hypot(x - cx, (y - cy) * 1.2)) % 3 == 0):
            o.set(x, y, P.reef_red[1])
    paint(o, grow(fan) & ~fan & (o.px[..., 3] == 0), P.reef_red[0])
    o.blit(s, 0, 10, blend=True)
    return o


def boxfish():
    """Yellow boxfish: a cube with a little round tail, black-ringed white spots."""
    def pat(t, v, x, y):
        if (x % 5 == 2 and y % 4 == 1) and 0.1 < t < 0.9:
            return "#fffbe6"
        if ((x % 5 in (1, 3) and y % 4 == 1) or (x % 5 == 2 and y % 4 in (0, 2))) and 0.1 < t < 0.9:
            return P.reef_night[1]
        return None
    return fish(18, [(0, -3), (0.15, -6), (0.85, -6), (1, -3)], [(0, 3), (0.15, 6), (0.85, 6), (1, 2)], P.reef_yellow,
                tail=("round", 4, 6), dorsal=[(0, 0), (0.1, 1.5), (0.2, 0), (1, 0)], anal=[(0, 0), (0.1, 1.5), (0.2, 0), (1, 0)],
                pattern=pat, eye=(0.8, -0.35), mouth=0.8, glow=True)


def pufferfish():
    """A porcupine puffer: round, sandy with dark blotches, little spines, big kind eyes."""
    def pat(t, v, x, y):
        if v > 0.35:
            return P.reef_pearl
        if ((x * 3 + y * 5) % 11 == 0 or (x * 3 + y * 5) % 11 == 1) and v < 0.3:
            return P.reef_brown
        return None
    s = fish(20, [(0, -3), (0.25, -7), (0.6, -8), (0.9, -5), (1, -2)], [(0, 3), (0.25, 7), (0.6, 8), (0.9, 5), (1, 2)], P.sand,
             fin=P.reef_yellow, tail=("round", 4, 6), dorsal=[(0, 0), (0.08, 2), (0.15, 0), (1, 0)],
             anal=[(0, 0), (0.08, 2), (0.15, 0), (1, 0)], pattern=pat, eye=(0.74, -0.35), eye_r=2, iris=P.reef_lime[2], mouth=0.3)
    # spines: tiny ticks on the outline
    a = s.px[..., 3] > 0
    for y in range(1, s.h - 1):
        for x in range(6, s.w - 2):
            if a[y, x] and not a[y - 1, x] and x % 3 == 0:
                s.set(x, y - 1, P.sand[0])
            if a[y, x] and not a[y + 1, x] and x % 3 == 1:
                s.set(x, y + 1, P.sand[0])
    return s


def saddle_wrasse():
    """Hīnālea lauwili: slim, green-blue with an orange saddle and a purple head."""
    def pat(t, v, x, y):
        if 0.62 < t < 0.72:
            return P.reef_orange
        if t >= 0.72:
            if abs(v - 0.2) < 0.15 or abs(v + 0.35) < 0.12:
                return P.reef_lime
            return P.reef_purple
        return None
    return fish(28, [(0, -2), (0.4, -4.5), (0.8, -4), (0.95, -2), (1, -1)], [(0, 2), (0.4, 4.5), (0.8, 3.5), (0.95, 1.5), (1, 0)], P.reef_cyan,
                fin=P.reef_cyan, tail=("lunate", 5, 9), dorsal=[(0, 0), (0.1, 1.5), (0.7, 1.5), (0.75, 0), (1, 0)],
                anal=[(0, 0), (0.1, 1.5), (0.55, 1.5), (0.6, 0), (1, 0)], pattern=pat, eye=(0.88, -0.3))


# ----------------------------------------------------------------- bigger fish

def parrotfish():
    """Uhu: big blue-green parrotfish, scales edged in pink, a pale beak, pink lunate tail."""
    def pat(t, v, x, y):
        if t > 0.93:
            return P.reef_pearl if v > -0.3 else None
        if 0.78 < t < 0.93 and abs(v - (t - 0.85) * 3) < 0.15:
            return P.reef_pink
        if 0.1 < t < 0.75 and (x + (y // 3) * 2) % 4 == 0 and y % 3 == 0:
            return P.reef_pink[3]
        return None
    return fish(40, [(0, -4), (0.3, -10), (0.7, -10), (0.92, -5), (1, -2)], [(0, 4), (0.35, 10), (0.7, 8), (0.92, 4), (1, 1)], P.reef_cyan,
                fin=P.reef_pink, tail=("lunate", 8, 18), dorsal=[(0, 0), (0.1, 2.5), (0.85, 2.5), (0.9, 0), (1, 0)],
                anal=[(0, 0), (0.12, 2.5), (0.5, 2.5), (0.55, 0), (1, 0)], pelvic=(0.65, 3), pattern=pat, eye=(0.86, -0.3),
                eye_r=2, iris=P.reef_yellow[3], scales=True)


def grouper():
    """A peacock grouper: deep brown-red, blue spots, a heavy jaw, round tail."""
    def pat(t, v, x, y):
        if ((x * 7 + y * 13) % 17 == 0) and abs(v) < 0.85:
            return P.reef_blue[4]
        if 0.3 < t < 0.7 and (int(t * 18) % 3 == 0) and v < 0.3:
            return P.reef_brown
        return None
    return fish(48, [(0, -4), (0.3, -11), (0.75, -12), (0.94, -7), (1, -3)], [(0, 4), (0.35, 11), (0.75, 12), (0.94, 8), (1, 6)], P.reef_red,
                fin=P.reef_red, tail=("round", 9, 18), dorsal=[(0, 0), (0.12, 3), (0.8, 3.5), (0.88, 0), (1, 0)],
                anal=[(0, 0), (0.12, 3.5), (0.4, 3.5), (0.45, 0), (1, 0)], pelvic=(0.7, 4), pattern=pat, eye=(0.84, -0.45),
                eye_r=2, iris=P.reef_yellow[2], mouth=2.5, scales=True)


def trevally():
    """Ulua (giant trevally): silver with a steep blue-grey forehead and a yellow-edged forked tail."""
    def pat(t, v, x, y):
        if v < -0.45:
            return P.reef_grey
        return None
    s = fish(46, [(0, -2), (0.3, -8), (0.65, -12), (0.9, -8), (1, -2)], [(0, 2), (0.35, 8), (0.7, 10), (0.9, 6), (1, 1)], P.reef_pearl,
             fin=P.reef_grey, tail=("fork", 10, 22), dorsal=[(0, 0), (0.1, 2), (0.5, 2), (0.6, 4), (0.65, 0), (1, 0)],
             anal=[(0, 0), (0.1, 2), (0.45, 3), (0.5, 0), (1, 0)], pattern=pat, eye=(0.86, -0.15), eye_r=2, iris=P.reef_yellow[3])
    # scute line near the tail
    cy = s.h // 2
    for x in range(12, 26):
        s.set(x, cy + (1 if x > 20 else 0), P.reef_grey[2] if x % 2 else P.reef_grey[3])
    return s


def barracuda():
    """Long, silver-blue with dark chevrons, an undershot jaw, forked tail."""
    def pat(t, v, x, y):
        if v < -0.35:
            return P.reef_grey
        if 0.15 < t < 0.75 and x % 6 in (0, 1) and -0.45 < v < 0.05:
            return P.reef_grey[1]
        return None
    return fish(58, [(0, -2), (0.3, -5), (0.7, -5), (0.92, -3), (1, -1)], [(0, 2), (0.3, 5), (0.7, 4), (0.95, 2), (1, 1)], P.reef_pearl,
                fin=P.reef_grey, tail=("fork", 9, 14), dorsal=[(0, 0), (0.1, 3), (0.2, 0), (0.55, 0), (0.6, 4), (0.68, 0), (1, 0)],
                anal=[(0, 0), (0.1, 3), (0.2, 0), (1, 0)], pattern=pat, eye=(0.88, -0.2), mouth=1.2)


# ----------------------------------------------------------------- big animals (drawn as shapes)

def body_shade(s, m, ramp, x_bias=0.0):
    """Shade an arbitrary blob mask as a lit round form."""
    H, W = m.shape
    for x in range(W):
        col = np.nonzero(m[:, x])[0]
        if not len(col):
            continue
        y0, y1 = col.min(), col.max()
        mid, half = (y0 + y1) / 2, max(0.5, (y1 - y0) / 2)
        for y in col:
            v = (y - mid) / half
            s.set(x, y, ramp[tone_of(v, x, y, 0.5 + x_bias * (x / W - 0.5))])
    paint(s, grow(m) & ~m & (s.px[..., 3] == 0), ramp[0])
    r = ring(m)
    paint(s, r & np.roll(~m, -1, axis=0), ramp[0])
    paint(s, r & np.roll(~m, 1, axis=0), ramp[4])


def whitetip():
    """Whitetip reef shark: grey back, white belly, white fin tips, a calm eye."""
    W, H = 92, 30
    s = Sprite(W, H)
    cy = 15
    top = smooth_curve([(0, -1.5), (0.25, -4), (0.55, -7), (0.85, -5), (0.97, -2), (1, 0)], 70)
    bot = smooth_curve([(0, 1.5), (0.25, 3.5), (0.55, 6), (0.85, 4), (0.97, 1), (1, 0)], 70)
    x0 = 20
    bm = np.zeros((H, W), bool)
    for i in range(70):
        bm[int(round(cy + top[i])):int(round(cy + bot[i])) + 1, x0 + i] = True
    G = P.reef_grey
    fins = [
        [(x0 + 2, cy - 2), (x0 - 4, cy - 6), (3, cy - 14), (6, cy - 13), (x0 - 6, cy), (9, cy + 6), (6, cy + 9), (x0 - 2, cy + 3), (x0 + 2, cy + 2)],   # tail
        [(x0 + 34, cy - 6), (x0 + 42, cy - 15), (x0 + 46, cy - 14), (x0 + 47, cy - 6)],                          # dorsal
        [(x0 + 43, cy + 4), (x0 + 36, cy + 13), (x0 + 40, cy + 13), (x0 + 50, cy + 5)],                           # pectoral
        [(x0 + 14, cy + 2), (x0 + 11, cy + 7), (x0 + 16, cy + 3)],                                               # anal
        [(x0 + 12, cy - 3), (x0 + 10, cy - 7), (x0 + 15, cy - 3)],                                               # 2nd dorsal
    ]
    for pts in fins:
        fm = poly_mask(W, H, pts) & ~bm
        paint(s, fm, G[2])
        hi = fm & np.roll(~fm, 1, axis=0)
        paint(s, hi, G[3])
        tip = fm & (np.cumsum(fm, axis=0) < 0)  # placeholder
        paint(s, grow(fm) & ~fm & ~bm & (s.px[..., 3] == 0), G[0])
    # white tips on the dorsal and tail top
    for (x, y) in [(x0 + 42, cy - 14), (x0 + 43, cy - 14), (x0 + 42, cy - 13), (3, cy - 12), (4, cy - 12), (3, cy - 11), (37 + x0 - 34 + 3, cy + 12), (x0 + 37, cy + 12)]:
        if s.px[y, x, 3]:
            s.set(x, y, P.reef_pearl[4])
    for x in range(W):
        col = np.nonzero(bm[:, x])[0]
        if not len(col):
            continue
        y0, y1 = col.min(), col.max()
        mid, half = (y0 + y1) / 2, max(0.5, (y1 - y0) / 2)
        for y in col:
            v = (y - mid) / half
            if v > 0.2 + 0.1 * math.sin(x * 0.4):
                s.set(x, y, P.reef_pearl[3] if v < 0.75 else P.reef_pearl[2])
            else:
                s.set(x, y, G[tone_of(v, x, y)])
    paint(s, grow(bm) & ~bm & (s.px[..., 3] == 0), G[0])
    r = ring(bm)
    paint(s, r & np.roll(~bm, 1, axis=0), G[4])
    paint(s, r & np.roll(~bm, -1, axis=0), P.reef_pearl[1])
    # gill slits, eye, mouth
    for k in range(3):
        s.vline(x0 + 52 + k * 2, cy - 2, cy + 2, G[1])
    ex, ey = x0 + 62, cy - 2
    s.rect(ex, ey, 2, 2, P.ink[0])
    s.set(ex, ey, P.reef_pearl[4])
    s.hline(x0 + 60, x0 + 66, cy + 3, P.reef_pearl[1])
    return s


def turtle():
    """Honu: a green sea turtle side-on, streamlined shell with amber scutes,
    a big front flipper sweeping back, a small rear flipper, beaked head."""
    W, H = 64, 30
    s = Sprite(W, H)
    skin = P.reef_lime
    sh = P.reef_brown
    shell = poly_mask(W, H, [(12 + 36 * (1 - math.cos(a)) / 2, 15 - 10 * math.sin(a) ** 0.8) for a in np.linspace(0, math.pi, 24)] +
                      [(48, 17), (44, 19), (16, 19), (12, 17)])
    rear = poly_mask(W, H, [(16, 17), (8, 21), (4, 24), (9, 24), (18, 19)]) & ~shell
    front = poly_mask(W, H, [(40, 16), (46, 19), (54, 25), (58, 29), (51, 28), (38, 20)]) & ~shell
    head = poly_mask(W, H, [(46, 11), (52, 9), (58, 10), (61, 13), (58, 16), (51, 16), (46, 16)]) & ~shell
    for m in (rear, head):
        body_shade(s, m, skin)
    body_shade(s, shell, sh)
    # scutes: dark seams, amber centres fading to olive
    seams = [((22, 6), (22, 18)), ((30, 5), (30, 18)), ((38, 6), (38, 18)), ((14, 12), (46, 12))]
    for (x1, y1), (x2, y2) in seams:
        s.line(x1, y1, x2, y2, sh[1])
    for (cx, cy) in ((18, 10), (26, 8), (34, 8), (42, 10), (18, 15), (26, 15), (34, 15), (42, 15)):
        for dy in (-1, 0, 1):
            for dx in (-2, -1, 0, 1, 2):
                x, y = cx + dx, cy + dy
                if shell[y, x] and abs(dx) + abs(dy) * 2 < 3:
                    s.set(x, y, P.reef_yellow[2] if (dx, dy) != (0, 0) else P.reef_yellow[3])
    s.hline(13, 47, 18, P.reef_yellow[1])
    s.hline(15, 45, 19, sh[0])
    body_shade(s, front, skin)
    ys, xs = np.nonzero(front | head | rear)
    for y, x in zip(ys, xs):
        if (x + 2 * y) % 4 == 0 and not ring(front | head | rear)[y, x]:
            s.set(x, y, skin[4] if y < 20 else skin[3])
    s.rect(55, 11, 2, 2, P.ink[0])
    s.set(55, 11, P.reef_pearl[4])
    s.line(58, 14, 61, 13, skin[0])
    return s


def manta():
    """A manta ray seen from above at a slight angle: dark back, white shoulder patches, cephalic fins."""
    W, H = 84, 40
    s = Sprite(W, H)
    pts = [(42, 6), (52, 8), (66, 14), (82, 18), (70, 22), (54, 26), (44, 30), (40, 30), (30, 26), (14, 22), (2, 18), (18, 14), (32, 8)]
    m = poly_mask(W, H, pts)
    D = P.reef_night
    body_shade(s, m, D)
    # shoulder patches
    for cx in (30, 54):
        for dy in range(-3, 4):
            for dx in range(-6, 7):
                x, y = cx + dx, 16 + dy
                if m[y, x] and (dx / 6.5) ** 2 + (dy / 3.5) ** 2 < 1:
                    s.set(x, y, P.reef_pearl[2] if dy > 0 else P.reef_pearl[3])
    # cephalic fins + tail
    for pts2 in ([(38, 6), (36, 1), (40, 1), (41, 6)], [(46, 6), (48, 1), (44, 1), (43, 6)]):
        fm = poly_mask(W, H, pts2) & ~m
        body_shade(s, fm, D)
    for k in range(9):
        s.set(42, 31 + k, D[1] if k % 2 else D[2])
    s.set(36, 9, P.reef_pearl[4])
    s.set(48, 9, P.reef_pearl[4])
    return s


def eagle_ray():
    """Spotted eagle ray, side-on gliding: dark blue back with white spots, a long whip tail."""
    W, H = 80, 26
    s = Sprite(W, H)
    pts = [(56, 12), (50, 4), (40, 2), (28, 6), (22, 12), (28, 16), (40, 20), (50, 18)]
    m = poly_mask(W, H, pts)
    head = poly_mask(W, H, [(54, 9), (62, 10), (66, 12), (62, 14), (54, 15)])
    B = P.reef_blue
    body_shade(s, m | head, P.reef_night)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        if (x * 5 + y * 7) % 13 == 0 and y < 14:
            s.set(x, y, P.reef_pearl[4])
    for k in range(24):
        x = 22 - k
        y = 13 + int(2 * math.sin(k / 6))
        s.set(x, y, P.reef_night[2] if k % 2 else P.reef_night[1])
    s.set(61, 11, P.reef_pearl[4])
    return s


def octopus():
    """Day octopus: a domed mantle, eight thick arms tapering and curling at the tips,
    red-brown mottling, pale suckers, a golden eye."""
    W, H = 46, 34
    s = Sprite(W, H)
    R = P.reef_red
    m = _blob(W, H, 22, 10, 9, 8, random.Random(4), 0.06)
    under = np.zeros((H, W), bool)
    for k in range(8):
        side = -1 if k < 4 else 1
        spread = (k % 4) / 3
        x, y = 22 + side * (2 + spread * 3), 15.0
        ang = math.pi / 2 - side * (0.35 + spread * 0.9)
        for j in range(18):
            w = max(1, 3 - j // 6)
            ang += side * (0.02 + (0.28 if j > 12 else 0))     # tips curl
            x += math.cos(ang) * 1.1 * side if False else math.cos(ang)
            y += math.sin(ang) * 0.9
            for dx in range(w):
                for dy in range(w):
                    xi, yi = int(round(x + dx - w / 2)), int(round(y + dy - w / 2))
                    if 0 <= xi < W and 0 <= yi < H:
                        m[yi, xi] = True
                        if dy == w - 1 and j > 2:
                            under[yi, xi] = True
    body_shade(s, m, R)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        if y < 17 and (x * 3 + y * 7) % 11 == 0:
            s.set(x, y, R[4])
        elif y < 17 and (x * 5 + y * 3) % 13 == 0:
            s.set(x, y, R[1])
    for y, x in zip(*np.nonzero(under & ~ring(m))):
        if x % 2 == 0:
            s.set(x, y, P.reef_pink[4])
    s.rect(25, 12, 2, 2, P.reef_yellow[3])
    s.set(26, 13, P.ink[0])
    s.hline(25, 26, 11, R[0])
    return s


def moray():
    """Yellow-margin moray leaning out of a dark rock hole, jaw open, speckled."""
    W, H = 46, 30
    s = Sprite(W, H)
    rock = _blob(W, H + 10, 22, 26, 22, 16, random.Random(8), 0.1)[:H]
    body_shade(s, rock, P.slate)
    hole = _blob(W, H, 15, 20, 7, 6, random.Random(1), 0.1)
    paint(s, hole, P.reef_night[0])
    paint(s, ring(hole) & np.roll(~hole, -1, axis=0), P.slate[3])
    eel = np.zeros((H, W), bool)
    path = []
    for k in range(30):
        t = k / 29
        x = 15 + t * 26
        y = 20 - 12 * math.sin(t * math.pi * 0.62) + 2 * t
        path.append((x, y))
        r = 3.2 - t * 0.4
        for dy in np.arange(-r, r + 0.1, 0.5):
            for dx in (0, 0.5):
                xi, yi = int(round(x + dx)), int(round(y + dy))
                if 0 <= xi < W and 0 <= yi < H:
                    eel[yi, xi] = True
    eel &= ~(rock & ~hole) | (np.arange(W)[None, :] > 17)
    body_shade(s, eel, P.reef_brown)
    ys, xs = np.nonzero(eel)
    for y, x in zip(ys, xs):
        if (x * 5 + y * 3) % 6 == 0 and not ring(eel)[y, x]:
            s.set(x, y, P.reef_yellow[3])
    # dorsal margin: yellow line along the back
    for (x, y) in path[6:]:
        top = int(round(y - 3))
        if 0 <= top < H:
            s.set(int(round(x)), top, P.reef_yellow[3])
    hx, hy = path[-1]
    hx, hy = int(round(hx)), int(round(hy))
    s.rect(hx - 3, hy - 2, 2, 2, P.ink[0])
    s.set(hx - 3, hy - 2, P.reef_pearl[4])
    s.hline(hx - 4, hx + 1, hy + 1, P.reef_red[1])          # the open jaw
    s.set(hx + 1, hy + 2, P.reef_pearl[4])
    s.set(hx - 1, hy + 2, P.reef_pearl[4])
    return s


def school(spr, n, w, h, seed, jitter=1):
    rnd = random.Random(seed)
    s = Sprite(w, h)
    placed = 0
    tries = 0
    while placed < n and tries < 500:
        tries += 1
        x, y = rnd.randint(0, w - spr.w), rnd.randint(0, h - spr.h)
        if (s.px[y:y + spr.h, x:x + spr.w, 3] > 0).any():
            continue
        s.blit(spr, x, y, blend=True)
        placed += 1
    return s


def anthias():
    """Tiny orange-pink anthias with a lyre tail."""
    def pat(t, v, x, y):
        if t > 0.7 and abs(v - 0.1) < 0.2:
            return P.reef_purple
        return None
    return fish(10, [(0, -1.5), (0.5, -3), (0.9, -2), (1, -1)], [(0, 1.5), (0.5, 3), (0.9, 1.5), (1, 0)], P.reef_orange,
                fin=P.reef_pink, tail=("lunate", 4, 7), pattern=pat, pectoral=False, eye=(0.8, -0.3), gill=0.0)


def bluestripe_snapper():
    def pat(t, v, x, y):
        if abs(v + 0.1) < 0.14 or abs(v - 0.4) < 0.1 or abs(v + 0.55) < 0.1:
            return P.reef_blue
        return None
    return fish(14, [(0, -2), (0.5, -4), (0.9, -3), (1, -1)], [(0, 2), (0.5, 4), (0.9, 2), (1, 0)], P.reef_yellow,
                tail=("fork", 4, 7), dorsal=[(0, 0), (0.2, 1.5), (0.7, 1.5), (0.8, 0), (1, 0)], pattern=pat, pectoral=False,
                eye=(0.84, -0.25), gill=0.0)


def convict_tang():
    def pat(t, v, x, y):
        if int(t * 22) % 4 == 0 and t < 0.92:
            return P.reef_night
        return None
    return fish(12, [(0, -2), (0.4, -5), (0.85, -4), (1, -1)], [(0, 2), (0.4, 5), (0.85, 3), (1, 0)], P.reef_pearl,
                fin=P.reef_pearl, tail=("square", 3, 6), dorsal=[(0, 0), (0.1, 1.5), (0.7, 1.5), (0.8, 0), (1, 0)], pattern=pat,
                pectoral=False, eye=(0.82, -0.2), gill=0.0)


def bait():
    s = Sprite(9, 4)
    s.hline(1, 6, 1, P.reef_grey[4])
    s.hline(1, 6, 2, P.reef_pearl[3])
    s.set(0, 0, P.reef_grey[3]); s.set(0, 3, P.reef_grey[3])
    s.set(7, 1, P.reef_grey[2]); s.set(7, 2, P.reef_grey[2])
    s.set(6, 1, P.ink[0])
    return s


def bait_ball():
    rnd = random.Random(7)
    W, H = 70, 40
    s = Sprite(W, H)
    b = bait()
    for k in range(70):
        a = rnd.random() * math.tau
        r = math.sqrt(rnd.random())
        x = int(W / 2 + math.cos(a) * r * (W / 2 - 6) - 4)
        y = int(H / 2 + math.sin(a) * r * (H / 2 - 4) - 2)
        spr = b if rnd.random() < 0.5 else b.flip_h()
        s.blit(spr, x, y, blend=True)
    return s


# ----------------------------------------------------------------- corals

def _blob(W, H, cx, cy, rx, ry, rnd, wob=0.15):
    pts = []
    for a in np.linspace(0, math.tau, 28, endpoint=False):
        r = 1 + rnd.uniform(-wob, wob)
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    return poly_mask(W, H, pts)


def brain_coral():
    """A domed brain coral: meandering grooves, warm cream-to-gold, lit top-left."""
    W, H = 34, 20
    s = Sprite(W, H)
    rnd = random.Random(3)
    m = _blob(W, H + 6, 17, 18, 16, 15, rnd, 0.05)[:H]
    body_shade(s, m, P.reef_yellow)
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        g = math.sin(x * 0.9 + math.sin(y * 0.8) * 2.2)
        if g > 0.72 and not ring(m)[y, x]:
            s.set(x, y, P.reef_yellow[1] if y > 6 else P.reef_yellow[2])
    return s


def staghorn():
    """Staghorn / acropora: branching antlers, purple with glowing lilac tips."""
    W, H = 40, 34
    s = Sprite(W, H)
    rnd = random.Random(5)
    m = np.zeros((H, W), bool)
    tips = []

    def branch(x, y, ang, ln, w, depth):
        for j in range(ln):
            x += math.cos(ang)
            y -= math.sin(ang)
            for d in range(w):
                xi, yi = int(round(x + d * math.sin(ang))), int(round(y))
                if 0 <= xi < W and 0 <= yi < H:
                    m[yi, xi] = True
            ang += rnd.uniform(-0.08, 0.08)
        tips.append((int(round(x)), int(round(y))))
        if depth > 0:
            for da in (-0.5, 0.45):
                branch(x, y, ang + da + rnd.uniform(-0.15, 0.15), int(ln * 0.7), max(1, w - 1), depth - 1)

    for bx, ang in ((14, 1.9), (20, 1.55), (26, 1.2)):
        branch(bx, H - 1, ang, 9, 3, 2)
    body_shade(s, m, P.reef_purple)
    for (x, y) in tips:
        for dx, dy in ((0, 0), (1, 0), (0, 1)):
            if 0 <= x + dx < W and 0 <= y + dy < H and m[y + dy, x + dx]:
                s.set(x + dx, y + dy, P.reef_pink[4] if dy == 0 else P.reef_pink[3])
    return s


def table_coral():
    """A wide table acropora on a short trunk: teal plate with a pale lit rim, frilly edge."""
    W, H = 50, 22
    s = Sprite(W, H)
    plate = np.zeros((H, W), bool)
    for x in range(2, W - 2):
        t = (x - 2) / (W - 4)
        top = 5 - 3 * math.sin(t * math.pi)
        plate[int(top):int(top) + 5 + (x % 3 == 0), x] = True
    trunk = poly_mask(W, H, [(21, 9), (29, 9), (27, 22), (23, 22)])
    body_shade(s, trunk, P.reef_brown)
    body_shade(s, plate, P.reef_cyan)
    for x in range(3, W - 3):
        ys = np.nonzero(plate[:, x])[0]
        if len(ys):
            s.set(x, ys.min(), P.reef_cyan[4] if x % 2 else P.reef_pearl[4])
            if x % 2 == 0:
                s.set(x, ys.max(), P.reef_cyan[0])
    return s


def sea_fan():
    """A gorgonian fan: a red-orange lace of branches in one plane."""
    W, H = 46, 44
    s = Sprite(W, H)
    rnd = random.Random(11)
    m = np.zeros((H, W), bool)

    def br(x, y, ang, ln, depth):
        for j in range(ln):
            x += math.cos(ang)
            y -= math.sin(ang)
            xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < W and 0 <= yi < H:
                m[yi, xi] = True
        if depth:
            for da in (-0.42, 0.42):
                br(x, y, ang + da + rnd.uniform(-0.1, 0.1), max(3, int(ln * 0.75)), depth - 1)
    br(23, H - 1, math.pi / 2, 7, 6)
    # cross-links make a lattice
    for y in range(4, H - 6, 3):
        row = np.nonzero(m[y])[0]
        for a, b in zip(row, row[1:]):
            if b - a < 5:
                m[y, a:b] = True
    paint(s, m, P.reef_orange[2])
    paint(s, m & (np.arange(H)[:, None] < H * 0.5), P.reef_orange[3])
    paint(s, ring(m) & np.roll(~m, 1, axis=0), P.reef_orange[4])
    paint(s, grow(m) & ~m, P.reef_red[0])
    return s


def tube_sponges():
    """Purple and orange tube sponges with dark open mouths."""
    W, H = 30, 30
    s = Sprite(W, H)
    for (x, h, w, ramp) in ((4, 22, 6, P.reef_purple), (12, 28, 7, P.reef_orange), (21, 18, 6, P.reef_pink)):
        m = poly_mask(W, H, [(x, H), (x + 0.5, H - h), (x + w - 0.5, H - h), (x + w, H)])
        body_shade(s, m, ramp)
        # vertical shading: lit left side
        for y in range(H - h, H):
            s.set(x + 1, y, ramp[3])
            s.set(x + w - 2, y, ramp[1])
        s.hline(x + 1, x + w - 2, H - h, ramp[0])
        s.hline(x + 1, x + w - 2, H - h + 1, ramp[0])
        s.set(x + 1, H - h, ramp[4])
    return s


def soft_coral():
    """A soft tree coral: a pale trunk with clusters of pink polyp puffs."""
    W, H = 34, 34
    s = Sprite(W, H)
    rnd = random.Random(2)
    trunk = np.zeros((H, W), bool)
    for y in range(12, H):
        w = 2 + (H - y) // 10
        trunk[y, 16 - w // 2:16 + w // 2 + 1] = True
    for (x1, y1) in ((8, 14), (25, 12), (16, 8)):
        for k in range(14):
            t = k / 13
            x = int(round(16 + (x1 - 16) * t))
            y = int(round(24 + (y1 - 24) * t))
            trunk[y, x] = True
            trunk[y, min(W - 1, x + 1)] = True
    body_shade(s, trunk, P.blossom)
    for (cx, cy, r) in ((8, 12, 6), (25, 10, 6), (16, 6, 6), (12, 16, 4), (21, 16, 4)):
        m = _blob(W, H, cx, cy, r, r * 0.85, rnd, 0.12)
        body_shade(s, m, P.reef_pink)
        ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs):
            if (x + y * 2) % 4 == 0 and y < cy:
                s.set(x, y, P.reef_pink[4])
    return s


def bubble_coral():
    """Bubble coral: pearly translucent grape-like bubbles."""
    W, H = 26, 16
    s = Sprite(W, H)
    rnd = random.Random(9)
    for (cx, cy, r) in ((6, 11, 4), (12, 9, 5), (19, 11, 4), (9, 5, 3), (16, 4, 3), (22, 6, 3), (3, 6, 2)):
        m = _blob(W, H, cx, cy, r, r, rnd, 0.05)
        body_shade(s, m, P.reef_pearl)
        s.set(cx - r // 2, cy - r // 2, P.reef_pearl[4])
    return s


def mushroom_coral():
    """A free-living mushroom coral: an oval disc with radiating ridges, lime-green."""
    W, H = 22, 10
    s = Sprite(W, H)
    m = poly_mask(W, H, [(11 + 10 * math.cos(a), 6 + 4 * math.sin(a)) for a in np.linspace(0, math.tau, 24, endpoint=False)])
    body_shade(s, m, P.reef_lime)
    for a in np.linspace(0, math.pi, 9):
        for j in range(2, 9):
            x, y = int(round(11 + math.cos(a) * j)), int(round(6 - math.sin(a) * j * 0.4))
            if m[y, x]:
                s.set(x, y, P.reef_lime[3])
    s.hline(9, 13, 5, P.reef_lime[1])
    return s


def lettuce_coral():
    """Lettuce / plate coral: overlapping wavy frills, orange-peach."""
    W, H = 34, 18
    s = Sprite(W, H)
    for k, (y0, x0, x1) in enumerate(((12, 2, 32), (8, 5, 28), (4, 9, 24))):
        m = np.zeros((H, W), bool)
        for x in range(x0, x1):
            yy = y0 + int(round(1.5 * math.sin(x * 0.7 + k)))
            m[yy:min(H, yy + 4), x] = True
        body_shade(s, m, P.reef_orange)
        for x in range(x0, x1):
            yy = y0 + int(round(1.5 * math.sin(x * 0.7 + k)))
            s.set(x, yy, P.reef_orange[4])
    return s


def anemone(frame=0, k=1.0):
    """A magnificent anemone: a crimson column, a skirt of fat lilac-tipped tentacles."""
    W, H = int(34 * k), int(22 * k)
    s = Sprite(W, H)
    cx, ty = W / 2, H - 8 * k
    col = poly_mask(W, H, [(cx - 7 * k, H), (cx - 5 * k, ty), (cx + 5 * k, ty), (cx + 7 * k, H)])
    body_shade(s, col, P.reef_red)
    n = int(13 * k)
    for i in range(n):
        a = math.pi * (0.05 + i * 0.9 / (n - 1))
        sway = math.sin(frame * 0.8 + i) * 1.2
        ln = int(10 * k)
        for j in range(ln):
            x = cx - math.cos(a) * j * 1.5 + sway * j / ln
            y = ty - math.sin(a) * j * 0.9
            for d in (0, 1):
                xi, yi = int(round(x + d)), int(round(y))
                if 0 <= xi < W and 0 <= yi < H:
                    s.set(xi, yi, P.reef_purple[4] if j >= ln - 2 else (P.reef_pink[3] if d == 0 else P.reef_pink[2]))
    paint(s, grow(s.px[..., 3] > 0) & (s.px[..., 3] == 0), P.reef_pink[0])
    return s


def clown_home():
    """A big anemone with a pair of small clownfish nestled in its tentacles."""
    a = anemone(k=1.5)
    big = Sprite(a.w + 6, a.h + 2)
    big.blit(a, 3, 2, blend=True)
    O = P.reef_orange

    def pat(t, v, x, y):
        for c, w in ((0.62, 0.05), (0.3, 0.05)):
            if abs(t - c) < w:
                return P.reef_pearl
            if abs(t - c) < w + 0.05:
                return P.reef_night[0]
        return None
    c = fish(11, [(0, -2), (0.5, -3.5), (0.9, -2.5), (1, -1)], [(0, 2), (0.5, 3.5), (0.9, 2), (1, 0)], O,
             tail=("round", 3, 5), dorsal=[(0, 0), (0.1, 1.5), (0.6, 2), (0.8, 0), (1, 0)], pattern=pat, pectoral=False,
             eye=(0.82, -0.3), gill=0.0)
    big.blit(c, 10, 6, blend=True)
    big.blit(c.flip_h(), 30, 12, blend=True)
    return big


def giant_clam():
    """A giant clam: wavy grey shell lips and a vivid blue-green mottled mantle."""
    W, H = 30, 14
    s = Sprite(W, H)
    shell = poly_mask(W, H, [(1, 13), (3, 5), (8, 3), (15, 2), (22, 3), (27, 5), (29, 13)])
    body_shade(s, shell, P.reef_pearl)
    for x in range(3, 28):
        y = 6 + int(round(1.5 * math.sin(x * 0.9)))
        for d in range(3):
            s.set(x, y + d, P.reef_blue[3] if (x + d) % 3 else P.reef_cyan[4])
        s.set(x, y - 1, P.reef_pearl[1])
    for x in (8, 15, 22):
        s.set(x, 7, P.reef_lime[4])
    return s


def sea_star():
    """A blue Linckia sea star: five long rounded arms."""
    W, H = 20, 18
    s = Sprite(W, H)
    m = np.zeros((H, W), bool)
    for k in range(5):
        a = -math.pi / 2 + k * math.tau / 5
        for j in range(9):
            x, y = 10 + math.cos(a) * j, 9 + math.sin(a) * j * 0.8
            for dx in (0, 1):
                for dy in (0, 1):
                    if j < 7 or (dx == 0 and dy == 0):
                        xi, yi = int(round(x + dx - 0.5)), int(round(y + dy - 0.5))
                        if 0 <= xi < W and 0 <= yi < H:
                            m[yi, xi] = True
    body_shade(s, m, P.reef_blue)
    return s


def nudibranch():
    """A purple nudibranch with an orange-rimmed mantle and orange rhinophores."""
    W, H = 20, 9
    s = Sprite(W, H)
    m = poly_mask(W, H, [(1, 8), (3, 4), (8, 3), (15, 3), (19, 6), (18, 8)])
    body_shade(s, m, P.reef_purple)
    for x in range(2, 19):
        ys = np.nonzero(m[:, x])[0]
        if len(ys):
            s.set(x, ys.max(), P.reef_orange[3])
    s.set(15, 1, P.reef_orange[3]); s.set(15, 2, P.reef_orange[2])
    s.set(17, 1, P.reef_orange[3]); s.set(17, 2, P.reef_orange[2])
    for x in (4, 5, 6):
        s.set(x, 2, P.reef_pearl[4])
    return s


# ----------------------------------------------------------------- catalogue

FISH = {
    "yellow_tang": ("黄高鳍刺尾鲷", yellow_tang), "regal_tang": ("拟刺尾鲷（蓝倒吊）", regal_tang),
    "clownfish": ("小丑鱼", clownfish), "moorish_idol": ("镰鱼", moorish_idol), "butterflyfish": ("浣熊蝴蝶鱼", butterflyfish),
    "triggerfish": ("夏威夷州鱼", triggerfish), "flame_angel": ("火焰神仙鱼", flame_angel), "lionfish": ("狮子鱼", lionfish),
    "boxfish": ("黄箱鲀", boxfish), "pufferfish": ("刺鲀", pufferfish), "saddle_wrasse": ("鞍斑锦鱼", saddle_wrasse),
}
BIG = {
    "parrotfish": ("鹦嘴鱼", parrotfish), "grouper": ("蓝点石斑", grouper), "trevally": ("浪人鲹", trevally),
    "barracuda": ("梭鱼", barracuda), "whitetip": ("白鳍礁鲨", whitetip), "turtle": ("绿海龟", turtle),
    "manta": ("蝠鲼", manta), "eagle_ray": ("斑点鹞鲼", eagle_ray), "octopus": ("章鱼", octopus), "moray": ("海鳗", moray),
}
SCHOOLS = {
    "anthias": ("金拟花鲈群", lambda: school(anthias(), 9, 80, 44, 4)),
    "bluestripe": ("蓝纹笛鲷群", lambda: school(bluestripe_snapper(), 10, 90, 44, 1)),
    "convict": ("横带刺尾鱼群", lambda: school(convict_tang(), 8, 76, 40, 2)),
    "bait_ball": ("银色小鱼球", bait_ball),
}
CORAL = {
    "brain": ("脑珊瑚", brain_coral), "staghorn": ("鹿角珊瑚", staghorn), "table": ("桌面珊瑚", table_coral),
    "sea_fan": ("海扇", sea_fan), "tube_sponges": ("管状海绵", tube_sponges), "soft": ("软珊瑚", soft_coral),
    "bubble": ("气泡珊瑚", bubble_coral), "mushroom": ("蘑菇珊瑚", mushroom_coral), "lettuce": ("莴苣珊瑚", lettuce_coral),
    "anemone": ("海葵", anemone), "clown_home": ("海葵和小丑鱼", clown_home), "giant_clam": ("砗磲", giant_clam),
    "sea_star": ("蓝海星", sea_star), "nudibranch": ("海蛞蝓", nudibranch),
}
GROUPS = [("小型礁鱼", FISH), ("大鱼和大型动物", BIG), ("鱼群", SCHOOLS), ("珊瑚和海底生物", CORAL)]


def build():
    out = {}
    for _, g in GROUPS:
        for k, (_, f) in g.items():
            out["reef_" + k] = f()
    return out
