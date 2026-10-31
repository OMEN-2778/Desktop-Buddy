"""Hawaiian reef life, refined sprites for the summer sea (owner, 2026-10-31:
"海洋生物不够逼真精致，多画几种鱼或鱼群和海底生物和植物、珊瑚的立绘").
Art only: a review sheet for the owner; nothing is wired into the game yet.

Light from the top left. Every animal and plant is outlined in the darkest
shade of its own material. Fish face right; the page flips them.
"""
import math
import random

import numpy as np

from pixelkit import P, Sprite, rgba

PREVIEW_SCALE = 5
INK = P.ink[0]


def col(c):
    return np.array(rgba(c), np.uint8)


def outline(s, colour, keep=None):
    """Outline the opaque area (no wrap-around, unlike Sprite.outline)."""
    a = s.px[..., 3] > 0
    edge = np.zeros_like(a)
    edge[1:] |= a[:-1]
    edge[:-1] |= a[1:]
    edge[:, 1:] |= a[:, :-1]
    edge[:, :-1] |= a[:, 1:]
    edge &= ~a
    s.px[edge] = col(colour)
    return s


def inner_edge(s, colour):
    """Recolour the outermost ring of the opaque area (a crisp rim)."""
    a = s.px[..., 3] > 0
    inner = a.copy()
    inner[1:-1, 1:-1] = a[1:-1, 1:-1] & a[:-2, 1:-1] & a[2:, 1:-1] & a[1:-1, :-2] & a[1:-1, 2:]
    s.px[a & ~inner] = col(colour)


# ------------------------------------------------------------- the fish engine

def fish(L, H, R, *, peak=0.58, blunt=1.0, snout=0.0, tail="fork", T=5, TH=None, dorsal=(0.25, 0.8, 2),
         anal=(0.3, 0.75, 1), fin=None, pattern=None, eye=0.84, eye_v=-0.25, belly=None, big_eye=False):
    """A side-view fish facing right. L body length, H body height. The body is
    a profile (peak = where it is tallest, blunt shapes the snout), shaded
    lit-back / mid / shaded belly-edge; fins are drawn behind in `fin` tones
    with ray lines; `pattern(t, v)` (t 0 tail .. 1 snout, v -1 back .. 1
    belly) may return a colour for any body pixel."""
    TH = TH or H * 0.9
    fin = fin or R
    fh = max(dorsal[2], anal[2]) + 1
    W, Hc = L + T + 2, H + 2 * fh + 2
    s = Sprite(W, Hc)
    x0, cy = T + 1, Hc / 2 - 0.5
    p = math.log(0.5) / math.log(peak)

    def half(t):
        if t <= 0 or t >= 1:
            return 0
        v = math.sin(math.pi * t ** p)
        if t > 0.8:
            v *= 1 - (t - 0.8) / 0.2 * (1 - blunt) * 0.6
        return H / 2 * v ** 0.75

    body = np.zeros((Hc, W), bool)
    for x in range(L):
        t = (x + 0.5) / L
        h = half(t)
        top, bot = cy - h + snout * max(0, t - 0.7) * H, cy + h
        for y in range(Hc):
            if top <= y <= bot:
                body[y, x0 + x] = True
    # fins (behind): dorsal on the back, anal under the belly, the tail
    F = np.zeros((Hc, W), bool)
    for (t0, t1, fhh), sgn in ((dorsal, -1), (anal, 1)):
        for x in range(int(t0 * L), int(t1 * L)):
            t = (x - t0 * L) / max(1, (t1 - t0) * L)
            hh = fhh * math.sin(math.pi * min(1, t * 1.3)) + 0.5
            edge = cy + sgn * half((x + 0.5) / L)
            for k in range(int(round(hh)) + 1):
                y = int(round(edge + sgn * k))
                if 0 <= y < Hc:
                    F[y, x0 + x] = True
    for x in range(T + 1):
        d = T - x                                                    # 0 at the peduncle .. T at the tip
        spread = 1 + d / T * TH / 2
        for y in range(Hc):
            dy = abs(y - cy)
            if tail == "fork":
                ok = dy <= spread and not (dy < (d - T * 0.45) * TH / T * 0.6)
            elif tail == "lunate":
                ok = dy <= spread and not (dy < (d - T * 0.7) * TH / T * 1.2)
            else:                                                    # round
                ok = dy <= spread * (1 - (d / T) ** 3 * 0.4)
            if ok:
                F[y, x0 - T + x] = True
    F &= ~body
    for y, x in zip(*np.nonzero(F)):
        c = fin[2] if (x + y) % 3 else fin[1]                        # rays
        if (y < cy and x > x0) or (x < x0 and y < cy):
            c = fin[3] if (x + y) % 3 else fin[2]
        s.set(int(x), int(y), c)
    # body shading + pattern
    for y, x in zip(*np.nonzero(body)):
        t = (x - x0 + 0.5) / L
        h = max(0.5, half(t))
        v = (y - cy) / h
        c = R[3] if v < -0.45 else R[2] if v < 0.55 else (belly[2] if belly else R[2])
        if v > 0.8:
            c = belly[1] if belly else R[1]
        if pattern:
            pc = pattern(t, v)
            if pc:
                c = pc
        s.set(int(x), int(y), c)
    outline(s, R[0])
    # gill line + eye
    gx = x0 + int(L * (eye - 0.13))
    for y in range(int(cy - half(eye - 0.13) * 0.55), int(cy + half(eye - 0.13) * 0.5)):
        if body[y, gx]:
            s.set(gx, y, R[1])
    ex, ey = x0 + int(L * eye), int(round(cy + eye_v * half(eye)))
    if big_eye:
        s.rect(ex - 1, ey - 1, 2, 2, INK).set(ex - 1, ey - 1, P.porcelain[3])
    else:
        s.set(ex, ey, INK)
    return s


def school(spr, n, w, h, seed, flip_some=False):
    """A shoal: copies in loose staggered rows, all heading the same way."""
    rnd = random.Random(seed)
    s = Sprite(w, h)
    pts = []
    for i in range(n):
        for _ in range(30):
            x, y = rnd.randint(0, w - spr.w), rnd.randint(0, h - spr.h)
            if all(abs(x - a) > spr.w + 1 or abs(y - b) > spr.h + 1 for a, b in pts):
                pts.append((x, y))
                break
    for x, y in sorted(pts, key=lambda p: p[1]):
        s.blit(spr, x, y)
    return s


# ------------------------------------------------------------- species

def yellow_tang():
    """Lāʻīpala: a lemon-yellow disc, a pointed snout, a white scalpel by the tail."""
    s = fish(14, 13, P.mustard, peak=0.5, blunt=0.55, T=4, TH=9, dorsal=(0.12, 0.85, 3), anal=(0.2, 0.8, 3),
             fin=P.mustard, belly=P.mustard, big_eye=True, eye=0.78, eye_v=-0.3,
             pattern=lambda t, v: P.mustard[4] if v < -0.6 and 0.3 < t < 0.8 else None)
    s.set(6, s.h // 2, P.porcelain[3])
    return s


def moorish_idol():
    """Kihikihi: tall black-white-yellow bands, an orange saddle on the snout, a
    long white streamer trailing from the dorsal fin."""
    def pat(t, v):
        if 0.52 < t < 0.7 or 0.14 < t < 0.26:
            return P.ink[1] if v > -0.95 else None
        if t >= 0.86 and v < 0.1:
            return P.autumn[3]
        if 0.26 <= t <= 0.52:
            return P.mustard[3] if v < 0.2 else P.porcelain[3]
        return P.porcelain[3] if v > -0.3 else P.mustard[4]
    s = fish(13, 14, P.porcelain + [P.porcelain[3]], peak=0.5, blunt=0.4, T=4, TH=8, dorsal=(0.3, 0.62, 3),
             anal=(0.3, 0.6, 3), fin=[P.ink[0], P.ink[1], P.slate[1], P.slate[2], P.slate[3]], pattern=pat, eye=0.76)
    s2 = Sprite(s.w + 4, s.h + 5)
    s2.blit(s, 4, 5)
    ys, xs = np.nonzero(s.px[..., 3] > 0)
    tx = int(xs[ys == ys.min()].mean()) + 4                          # the dorsal tip
    for k in range(16):                                              # a white streamer sweeping back
        x = tx - k
        y = 5 + int(ys.min()) - 1 - int(4 * math.sin(min(1, k / 7) * math.pi / 2)) + max(0, k - 9)
        if s2.px[y, x, 3] == 0 or k < 2:
            s2.set(x, y, P.porcelain[3])
    return s2


def humuhumu():
    """Humuhumunukunukuāpuaʻa, the reef triggerfish: a sandy diamond with a black
    wedge, blue bars across the eye, a yellow lip line, black-and-white tail base."""
    def pat(t, v):
        if 0.3 < t < 0.5 and 0.15 < v < 0.75 - (t - 0.3) * 2:
            return P.ink[1]
        if t > 0.66 and abs(v - (t - 0.8) * 3) < 0.18:
            return P.hydrangea[3]
        if t > 0.9 and v > 0.1:
            return P.mustard[3]
        if t < 0.2:
            return P.ink[1] if int(v * 4) % 2 else P.porcelain[3]
        if v > 0.45:
            return P.porcelain[3]
        return None
    return fish(20, 11, P.sand, peak=0.55, blunt=0.3, T=4, TH=7, tail="round", dorsal=(0.2, 0.45, 2), anal=(0.2, 0.45, 2),
                fin=P.sand, pattern=pat, eye=0.68, eye_v=-0.4, big_eye=True)


def parrotfish():
    """Uhu: a big blue-green parrotfish, every scale edged in pink, a pale beak,
    a lunate tail with pink tips."""
    def pat(t, v):
        x, y = int(t * 26), int((v + 1) * 6)
        if t > 0.9:
            return P.mint[3] if v > -0.2 else None
        if (x + (y // 2) * 2) % 4 == 0 and y % 2 == 0 and 0.15 < t < 0.85:
            return P.blossom[2]
        if t > 0.78 and abs(v + 0.1 - (t - 0.8)) < 0.12:
            return P.blossom[3]
        return None
    return fish(26, 12, P.teal, peak=0.5, blunt=1.0, T=6, TH=12, tail="lunate", dorsal=(0.2, 0.85, 2), anal=(0.4, 0.8, 2),
                fin=P.blossom, pattern=pat, eye=0.82, eye_v=-0.35, big_eye=True)


def butterflyfish():
    """Kīkākapu (raccoon butterflyfish): yellow, a black mask through the eye with a
    white band behind it, fine oblique lines."""
    def pat(t, v):
        if 0.72 < t < 0.86 and v < 0.25:
            return P.ink[1]
        if 0.62 < t <= 0.72 and v < 0.1:
            return P.porcelain[3]
        if (int(t * 30) + int(v * 6)) % 5 == 0 and t < 0.6:
            return P.mustard[2]
        return None
    return fish(12, 11, P.mustard, peak=0.48, blunt=0.35, T=3, TH=7, tail="round", dorsal=(0.1, 0.75, 2), anal=(0.25, 0.7, 2),
                fin=P.mustard, pattern=pat, eye=0.8, eye_v=-0.15)


def saddle_wrasse():
    """Hīnālea lauwili: long and slim, blue-green with an orange saddle behind the
    head and a purple-blue head with green lines."""
    def pat(t, v):
        if 0.62 < t < 0.72:
            return P.autumn[3] if v < 0.3 else P.autumn[2]
        if t >= 0.72:
            return P.hydrangea[2] if (int(t * 40) + int(v * 3)) % 3 else P.green[3]
        if v < -0.4 and int(t * 20) % 3 == 0:
            return P.mint[3]
        return None
    return fish(20, 6, P.teal, peak=0.55, blunt=0.9, T=3, TH=6, tail="lunate", dorsal=(0.15, 0.7, 1), anal=(0.25, 0.6, 1),
                fin=P.teal, pattern=pat, eye=0.88, eye_v=-0.3)


def bluestripe():
    """Taʻape (bluestripe snapper): yellow with blue lengthwise stripes."""
    return fish(10, 4, P.mustard, peak=0.55, T=3, TH=4, dorsal=(0.3, 0.7, 1), anal=(0.4, 0.6, 0),
                pattern=lambda t, v: P.hydrangea[3] if abs(v + 0.25) < 0.22 or abs(v - 0.4) < 0.18 else None, eye=0.85)


def convict_tang():
    """Manini (convict tang): pale silver-yellow with five black bars."""
    return fish(9, 6, P.porcelain + [P.porcelain[3]], peak=0.5, blunt=0.6, T=3, TH=5, dorsal=(0.15, 0.8, 1), anal=(0.25, 0.75, 1),
                fin=P.sand, pattern=lambda t, v: P.ink[1] if int(t * 10) in (2, 4, 6, 8) else (P.sand[4] if v < 0 else None), eye=0.82)


def baitfish():
    """A tiny silver baitfish (nehu): 5x2, a dark back and a bright flank."""
    s = Sprite(6, 3)
    s.hline(1, 4, 1, P.porcelain[3]).hline(1, 3, 0, P.slate[3]).set(0, 0, P.slate[2]).set(0, 2, P.slate[2]).set(5, 1, P.porcelain[2])
    return s


def bait_ball():
    """Nehu swirling in a ball: the top of the ball streams right, the bottom
    left, thinner at the edge, glinting where the flanks catch the light."""
    s = Sprite(60, 36)
    rnd = random.Random(4)
    b = baitfish()
    bl = Sprite(0, 0, px=b.px[:, ::-1].copy())
    pts = []
    for _ in range(400):
        a = rnd.uniform(0, math.tau)
        r = rnd.random() ** 0.6
        x, y = 30 + math.cos(a) * r * 26, 18 + math.sin(a) * r * 15
        if all(abs(x - p) > 6.5 or abs(y - q) > 2.6 for p, q in pts):
            pts.append((x, y))
    for x, y in pts:
        s.blit(b if y < 18 else bl, int(x) - 3, int(y) - 1)
    return s


def turtle():
    """Honu (green sea turtle): a domed shell with scutes, mottled flippers, a
    stubby head with a beak."""
    s = Sprite(36, 22)
    sh = P.leaf
    for y in range(4, 17):                                           # carapace
        t = (y - 4) / 13
        hw = int(14 * math.sqrt(max(0, 1 - (1 - t) ** 2 * 0.9)))
        for x in range(17 - hw, 17 + hw + 1):
            u = (x - 17) / max(1, hw)
            c = sh[2]
            if t < 0.35 and u < 0.3:
                c = sh[3]
            if t > 0.8:
                c = sh[1]
            s.set(x, y, c)
    for cx, cy in ((11, 9), (17, 8), (23, 9), (8, 13), (14, 13), (20, 13), (26, 13)):   # scutes
        s.set(cx, cy, P.mustard[1]).set(cx + 1, cy, P.mustard[1]).set(cx - 1, cy + 1, P.mustard[2])
        for k in range(-2, 3):
            s.set(cx + k, cy - 2, sh[1] if abs(k) < 2 else sh[2])
    s.hline(4, 30, 17, P.sand[3]).hline(5, 29, 18, P.sand[2])        # plastron edge
    F = P.sage
    for pts in (((24, 15), (33, 19), (30, 21), (22, 18)), ((10, 15), (3, 18), (5, 20), (12, 18)), ((22, 4), (30, 0), (31, 2), (25, 6))):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            for x in range(min(xs), max(xs) + 1):
                if _inside(pts, x, y):
                    s.set(x, y, F[2] if (x * 3 + y) % 5 else F[3])
    for y in range(7, 13):                                           # head
        for x in range(30, 36):
            if (x - 32) ** 2 / 9 + (y - 10) ** 2 / 6 <= 1:
                s.set(x, y, F[2] if y > 9 else F[3])
    s.set(33, 9, INK).set(35, 11, F[1])
    outline(s, sh[0])
    return s


def _inside(pts, x, y):
    c = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def eagle_ray():
    """Hīhīmanu (spotted eagle ray), seen from above as it glides: pointed swept
    wings full of white spots, a rounded head with a duck-bill snout, a long
    whip tail."""
    s = Sprite(46, 22)
    cx, cy = 26, 11
    for y in range(0, 22):
        for x in range(10, 40):
            dy = abs(y - cy) / 10
            # wing outline: leading edge from the head to the tip, trailing edge curving back
            front = cx + 10 - dy * 9
            back = cx - 6 - dy * 8 + (dy ** 2) * 6
            if back <= x <= front and dy <= 1:
                u = (x - back) / max(1, front - back)
                c = P.slate[2] if u > 0.35 else P.slate[1]
                if y < cy and u > 0.6:
                    c = P.slate[3]
                s.set(x, y, c)
    for y in range(cy - 2, cy + 3):                                  # head and snout
        for x in range(cx + 8, cx + 14):
            if ((x - cx - 9) / 5) ** 2 + ((y - cy) / 2.6) ** 2 <= 1:
                s.set(x, y, P.slate[3] if y < cy else P.slate[2])
    s.set(cx + 10, cy - 2, INK).set(cx + 10, cy + 2, INK)
    rnd = random.Random(2)
    for _ in range(40):
        x, y = rnd.randint(14, 34), rnd.randint(2, 20)
        if s.px[y, x, 3] and abs(y - cy) > 1:
            s.set(x, y, P.porcelain[3])
    for k in range(22):                                              # whip tail
        s.set(cx - 6 - k, cy + (k // 8), P.slate[1])
    outline(s, P.slate[0])
    return s


def whitetip():
    """Manō lālākea (whitetip reef shark): a slim grey shark, white tips on the
    dorsal fin and tail, a pale belly."""
    s = fish(40, 9, P.slate, peak=0.62, blunt=0.6, T=9, TH=12, tail="lunate", dorsal=(0.5, 0.62, 5), anal=(0.25, 0.3, 2),
             fin=P.slate, belly=P.porcelain + [P.porcelain[3]], eye=0.9, eye_v=-0.2,
             pattern=lambda t, v: P.porcelain[3] if v > 0.35 and t > 0.3 else None)
    a = s.px[..., 3] > 0
    ys, xs = np.nonzero(a)
    top = ys.min()
    for x in xs[ys == top]:                                          # white fin tip
        s.set(int(x), int(top) + 1, P.porcelain[3])
    s.set(2, 1 + s.h // 2 - 6, P.porcelain[3])
    for k in range(3):                                               # gill slits
        s.vline(9 + 27 + k * 1 - 2, s.h // 2 - 1, s.h // 2 + 1, P.slate[1])
    return s


# ------------------------------------------------------------- sea floor life

def octopus():
    """Heʻe (day octopus) draped over a rock: a mottled reddish mantle, a gold eye,
    arms curling out with pale suckers."""
    s = Sprite(26, 18)
    R = P.terracotta
    for y in range(1, 10):                                           # mantle
        for x in range(8, 18):
            if (x - 13) ** 2 / 25 + (y - 5.5) ** 2 / 20 <= 1:
                c = R[3] if (x - 13) + (y - 5) < -2 else R[2]
                if (x * 7 + y * 5) % 9 == 0:
                    c = R[1]
                s.set(x, y, c)
    s.set(15, 7, P.mustard[3]).set(16, 7, INK)
    for k, (a0, curl) in enumerate(((-2.6, 1), (-2.0, -1), (-1.2, 1), (-0.4, -1), (0.3, 1), (1.0, -1))):
        x, y = 13 + 3 * math.cos(a0), 10
        ang = a0
        for i in range(12):
            ang += curl * 0.18 * (i / 6)
            x += math.cos(ang * 0.5 + 1.57 * (1 if a0 < -1.6 else 0)) * 0.9 + math.cos(a0) * 0.6
            y += 0.5 + 0.2 * math.sin(i * 0.8)
            xi, yi = int(x), int(min(17, y))
            s.set(xi, yi, R[2]).set(xi, yi - 1 if i < 6 else yi, R[3] if i < 4 else R[2])
            if i % 3 == 1:
                s.set(xi, yi + 1 if yi < 17 else yi, P.blossom[3])
    outline(s, R[0])
    return s


def moray():
    """Puhi (yellow-margin moray) peeking out of a lava hole: a speckled head, a
    gaping mouth, a beady eye; the rock around it."""
    s = Sprite(24, 20)
    for y in range(4, 20):                                           # lava rock with a dark hole
        for x in range(0, 24):
            if (x - 10) ** 2 / 150 + (y - 15) ** 2 / 80 <= 1:
                s.set(x, y, P.slate[2] if (x + y) % 4 else P.slate[1])
    for y in range(9, 18):
        for x in range(3, 11):
            if (x - 7) ** 2 / 12 + (y - 13) ** 2 / 18 <= 1:
                s.set(x, y, INK)
    for i in range(14):                                              # the eel's neck and head arcing out
        x = 7 + i
        y = 13 - int(5 * math.sin(i / 14 * math.pi * 0.8))
        for k in range(-2, 3):
            c = P.mustard[2] if k < 0 else P.mustard[1]
            if (x * 5 + (y + k) * 3) % 4 == 0:
                c = P.mustard[0]
            s.set(x, y + k, c)
    s.set(20, 9, INK).set(19, 9, P.porcelain[3])
    s.hline(20, 23, 11, P.coral[1]).hline(21, 23, 12, P.mustard[1])    # open mouth
    s.set(22, 10, P.mustard[3])
    outline(s, P.slate[0])
    return s


def pencil_urchin():
    """Hāʻukeʻuke ʻulaʻula (slate pencil urchin): a dark test bristling with thick,
    blunt red spines."""
    s = Sprite(18, 11)
    for k in range(9):
        a = math.pi * (0.08 + k * 0.105)
        for r in range(2, 8):
            x, y = 9 - math.cos(a) * r, 9 - math.sin(a) * r * 0.9
            s.set(int(x), int(y), P.coral[2] if r < 6 else P.coral[3])
            s.set(int(x) + 1, int(y), P.coral[1])
    s.ellipse(9, 9, 3, 2, P.terracotta[1]).set(8, 8, P.terracotta[3])
    outline(s, P.coral[0])
    return s


def anemone(frame=0):
    """An anemone: a short column and a wide crown of many wavy tentacles with
    pale violet tips, swaying with the swell."""
    s = Sprite(20, 16)
    s.rect(7, 11, 6, 5, P.blossom[1]).vline(7, 11, 15, P.blossom[2]).hline(7, 12, 11, P.blossom[2])
    for k in range(13):
        a = math.pi * (0.06 + k * 0.068)
        for r in range(1, 10):
            wig = math.sin(r * 0.9 + k * 1.3 + frame * 1.6) * 0.6
            x = 10 - math.cos(a) * r * 0.95 + wig
            y = 11 - math.sin(a) * r * 0.9
            c = P.lilac[4] if r >= 8 else P.lilac[3] if r > 5 else P.blossom[2] if k % 2 else P.blossom[3]
            s.set(int(round(x)), int(round(y)), c)
    outline(s, P.blossom[0])
    return s


def hermit_crab():
    """A hermit crab in a borrowed spiral shell, red legs and stalk eyes."""
    s = Sprite(14, 11)
    for y in range(1, 9):
        for x in range(2, 11):
            if (x - 6) ** 2 / 16 + (y - 5) ** 2 / 12 <= 1:
                a = math.atan2(y - 5, x - 6)
                s.set(x, y, P.sand[3] if int(a * 2 + math.hypot(x - 6, y - 5)) % 3 else P.clay[2])
    for k in range(3):
        s.set(10 + k, 8 - k % 2, P.coral[2]).set(10 + k, 9, P.coral[1])
    s.vline(11, 4, 6, P.coral[2]).set(11, 3, INK).vline(12, 5, 6, P.coral[2]).set(12, 4, INK)
    outline(s, P.clay[0])
    return s


def cowry():
    """Leho (tiger cowry): a glossy spotted dome."""
    s = Sprite(12, 7)
    s.ellipse(6, 4, 5, 3, P.sand[3])
    rnd = random.Random(3)
    for _ in range(9):
        s.set(rnd.randint(2, 9), rnd.randint(2, 5), P.walnut[1])
    s.hline(4, 7, 2, P.porcelain[3])
    outline(s, P.walnut[0])
    return s


def sea_star():
    """A cushion sea star, orange, with a raised studded centre."""
    s = Sprite(15, 9)
    for k in range(5):
        a = -math.pi / 2 + k * math.tau / 5
        for r in range(0, 7):
            x, y = 7 + math.cos(a) * r, 4.5 + math.sin(a) * r * 0.55
            s.set(int(round(x)), int(round(y)), P.autumn[3] if r < 4 else P.autumn[2])
    s.set(7, 4, P.mustard[4]).set(6, 3, P.mustard[4]).set(8, 5, P.autumn[1])
    outline(s, P.autumn[0])
    return s


def nudibranch():
    """A Hawaiian nudibranch: a purple body with an orange frill and gills."""
    s = Sprite(14, 7)
    for x in range(1, 12):
        s.set(x, 4, P.lilac[2]).set(x, 5, P.lilac[1]).set(x, 3, P.lilac[3] if x % 2 else P.autumn[3])
    s.set(12, 4, P.lilac[2]).set(11, 2, P.lilac[3]).set(12, 1, P.autumn[3])
    for k in range(3):
        s.set(2 + k, 2 - (k == 1), P.autumn[3])
    outline(s, P.lilac[0])
    return s


def cucumber():
    """A sea cucumber lying in the sand, warty and dark."""
    s = Sprite(18, 6)
    for x in range(1, 17):
        h = 2 if 2 < x < 15 else 1
        for y in range(5 - h - 1, 5):
            s.set(x, y, P.walnut[2] if y < 3 else P.walnut[1])
        if x % 3 == 0:
            s.set(x, 5 - h - 2, P.walnut[3])
    outline(s, P.walnut[0])
    return s


def xmas_worms():
    """Christmas-tree worms on a coral boulder: little spiral plumes in colours."""
    s = Sprite(18, 12)
    s.ellipse(9, 9, 8, 3.5, P.sand[2])
    for cx, C in ((4, P.blue), (9, P.autumn), (14, P.mustard), (7, P.coral), (12, P.hydrangea)):
        base = 7 if cx not in (7, 12) else 8
        for k in range(4):
            s.hline(cx - (3 - k) // 1 + 1, cx + (3 - k) - 1, base - k, C[3] if k % 2 else C[2])
    outline(s, P.sand[0])
    return s


# ------------------------------------------------------------- corals and plants

def blob_coral(w, h, R, seed, knob=2.5, rim=True):
    """Shared: a dome built from many small rounded knobs, lit top-left."""
    rnd = random.Random(seed)
    s = Sprite(w, h)
    for _ in range(int(w * h / 5)):
        u = rnd.uniform(-1, 1)
        x = w / 2 + u * (w / 2 - knob)
        top = h - (h - knob) * math.sqrt(max(0, 1 - u * u))
        y = rnd.uniform(top, h - knob)
        r = rnd.uniform(knob * 0.7, knob)
        for dy in range(-int(r), int(r) + 1):
            for dx in range(-int(r), int(r) + 1):
                if dx * dx + dy * dy <= r * r:
                    px, py = int(x + dx), int(y + dy)
                    if 0 <= px < w and 0 <= py < h:
                        c = R[3] if dx + dy < -r * 0.5 else R[2] if dx + dy < r * 0.6 else R[1]
                        s.set(px, py, c)
    if rim:
        outline(s, R[0])
    return s


def cauliflower():
    """Pocillopora meandrina (cauliflower coral): a pink-brown head of crowded warty knobs."""
    return blob_coral(20, 13, P.blossom, 1, knob=2.2)


def lobe_coral():
    """Porites lobata (lobe coral): smooth rounded mounds, yellow-green."""
    s = Sprite(30, 15)
    for cx, cy, rx, ry in ((9, 10, 9, 6), (20, 9, 10, 7), (14, 6, 7, 5), (26, 12, 5, 4)):
        for y in range(cy - ry, 15):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 or y >= cy:
                    if 0 <= x < 30 and abs(x - cx) <= rx:
                        u, v = (x - cx) / rx, (y - cy) / ry
                        s.set(x, y, P.green[4] if u + v < -0.9 else P.green[3] if u + v < 0.4 else P.leaf[3])
    rnd = random.Random(5)
    for _ in range(40):                                              # polyp pores
        x, y = rnd.randrange(30), rnd.randrange(15)
        if s.px[y, x, 3]:
            s.set(x, y, P.leaf[2])
    outline(s, P.leaf[1])
    return s


def finger_coral():
    """Porites compressa (finger coral): a thicket of blunt lilac fingers."""
    s = Sprite(22, 16)
    rnd = random.Random(2)
    for k in range(9):
        x = 2 + k * 2.2 + rnd.uniform(-0.5, 0.5)
        h = rnd.randint(8, 15)
        lean = rnd.uniform(-0.3, 0.3)
        for i in range(h):
            px = int(x + lean * i)
            y = 15 - i
            s.set(px, y, P.lilac[3] if i > h - 3 else P.lilac[2]).set(px + 1, y, P.lilac[1])
        s.set(int(x + lean * (h - 1)), 15 - h, P.lilac[4])
    outline(s, P.lilac[0])
    return s


def antler_coral():
    """Pocillopora eydouxi (antler coral): thick branching arms in cream-brown."""
    s = Sprite(24, 18)

    def branch(x, y, ang, length, w):
        for i in range(int(length)):
            x += math.cos(ang)
            y -= math.sin(ang)
            for k in range(w):
                s.set(int(x) + k, int(y), P.sand[3] if k == 0 else P.sand[2])
        if length > 4:
            branch(x, y, ang + 0.45, length * 0.6, max(1, w - 1))
            branch(x, y, ang - 0.4, length * 0.6, max(1, w - 1))
        else:
            s.set(int(x), int(y), P.sand[4])
    branch(11, 17, math.pi / 2, 7, 3)
    branch(11, 17, math.pi / 2 + 0.6, 6, 2)
    branch(12, 17, math.pi / 2 - 0.6, 6, 2)
    rnd = random.Random(1)
    for _ in range(30):
        x, y = rnd.randrange(24), rnd.randrange(18)
        if s.px[y, x, 3]:
            s.set(x, y, P.clay[3])
    outline(s, P.clay[0])
    return s


def table_coral():
    """A plate coral: a wide flat table on a short stalk, blue-grey with a pale rim."""
    s = Sprite(28, 13)
    s.rect(12, 6, 4, 7, P.sea_grey[2]).vline(12, 6, 12, P.sea_grey[3])
    for x in range(1, 27):
        t = abs(x - 14) / 13
        y0 = int(3 + t * t * 3)
        s.vline(x, y0, y0 + 2, P.hydrangea[2]).set(x, y0, P.hydrangea[4])
        s.set(x, y0 + 2, P.hydrangea[1])
    outline(s, P.hydrangea[0])
    return s


def sea_fan():
    """A gorgonian sea fan: a red lattice spreading from one stem."""
    s = Sprite(22, 24)
    rnd = random.Random(3)

    def br(x, y, ang, n):
        for i in range(n):
            x += math.cos(ang) * 1.0
            y -= math.sin(ang) * 1.0
            s.set(int(x), int(y), P.coral[2] if i < n - 2 else P.coral[3])
            if rnd.random() < 0.2 and n > 4:
                br(x, y, ang + rnd.choice((-0.5, 0.5)), n // 2)
    for a in (1.05, 1.3, 1.57, 1.84, 2.1):
        br(11, 23, a, 19)
    for y in range(4, 20, 4):                                        # a few fine cross-links
        row = [x for x in range(22) if s.px[y, x, 3]]
        for a, b in zip(row, row[1:]):
            if 2 < b - a < 5 and rnd.random() < 0.5:
                s.hline(a + 1, b - 1, y, P.coral[3])
    s.vline(11, 19, 23, P.coral[1])
    outline(s, P.coral[0])
    return s


def tube_sponges():
    """A cluster of tube sponges, orange and lilac, open mouths lit inside."""
    s = Sprite(16, 16)
    for x, h, R in ((2, 10, P.autumn), (6, 14, P.lilac), (10, 11, P.autumn), (13, 7, P.lilac)):
        s.rect(x, 16 - h, 3, h, R[2]).vline(x, 16 - h, 15, R[3]).vline(x + 2, 16 - h, 15, R[1])
        s.hline(x, x + 2, 16 - h, R[4]).set(x + 1, 16 - h, R[0])
    outline(s, P.lilac[0])
    return s


def leather_coral():
    """A soft leather coral: a mushroom cap with a furry fringe of polyps."""
    s = Sprite(18, 12)
    s.rect(7, 6, 4, 6, P.sand[2]).vline(7, 6, 11, P.sand[3])
    for x in range(1, 17):
        t = abs(x - 8.5) / 8
        y0 = int(2 + t * t * 3)
        s.vline(x, y0, 6, P.mint[2]).set(x, y0, P.mint[4] if x % 2 else P.mint[3])
        s.set(x, 6, P.mint[1])
    outline(s, P.mint[0])
    return s


def seagrass(frame=0):
    """A tuft of sea grass, the blades bending with the swell."""
    s = Sprite(12, 18)
    for k in range(6):
        x = 2 + k * 1.6
        h = 10 + (k * 5) % 7
        for i in range(h):
            bend = math.sin(i / h * 1.5) * (1.5 + k % 2) * (1 if frame == 0 else 0.4)
            s.set(int(x + bend), 17 - i, P.green[3] if i > h * 0.6 else P.green[2])
    outline(s, P.green[0])
    return s


def limu():
    """Limu kohu (red seaweed): soft feathery red tufts."""
    s = Sprite(14, 11)
    rnd = random.Random(7)
    for k in range(5):
        x = 2 + k * 2.4
        for i in range(rnd.randint(5, 9)):
            s.set(int(x + math.sin(i * 0.9 + k) * 1.2), 10 - i, P.coral[3] if i % 2 else P.coral[2])
            if i % 2:
                s.set(int(x + 1), 10 - i, P.blossom[3])
    outline(s, P.coral[0])
    return s


def sargassum():
    """Sargassum: a long brown frond with leaflets and round air bladders."""
    s = Sprite(12, 32)
    for i in range(30):
        x = 6 + 2 * math.sin(i * 0.25)
        s.set(int(x), 31 - i, P.mustard[1])
        if i % 4 == 1:
            d = 1 if i % 8 == 1 else -1
            s.hline(int(x) + min(0, d * 3), int(x) + max(0, d * 3), 31 - i, P.mustard[2])
            s.set(int(x) + d * 3, 30 - i, P.mustard[3])
        if i % 5 == 3:
            s.set(int(x) - 1, 31 - i, P.mustard[3]).set(int(x) - 1, 30 - i, P.mustard[2])
    outline(s, P.mustard[0])
    return s


# ------------------------------------------------------------- build

FISH = {"yellow_tang": ("黄高鳍刺尾鲷", yellow_tang), "moorish_idol": ("镰鱼", moorish_idol),
        "humuhumu": ("夏威夷州鱼", humuhumu), "parrotfish": ("鹦嘴鱼", parrotfish),
        "butterflyfish": ("浣熊蝴蝶鱼", butterflyfish), "saddle_wrasse": ("鞍斑锦鱼", saddle_wrasse),
        "whitetip": ("白鳍礁鲨", whitetip), "turtle": ("绿海龟", turtle), "eagle_ray": ("斑点鹞鲼", eagle_ray)}
SCHOOLS = {"bluestripe": ("蓝纹笛鲷群", lambda: school(bluestripe(), 12, 60, 26, 1)),
           "convict": ("横带刺尾鱼群", lambda: school(convict_tang(), 10, 54, 28, 2)),
           "bait_ball": ("银色小鱼球", bait_ball)}
FLOOR = {"octopus": ("章鱼", octopus), "moray": ("海鳗", moray), "pencil_urchin": ("石笔海胆", pencil_urchin),
         "anemone": ("海葵", anemone), "hermit_crab": ("寄居蟹", hermit_crab), "cowry": ("虎斑宝螺", cowry),
         "sea_star": ("海星", sea_star), "nudibranch": ("海蛞蝓", nudibranch), "cucumber": ("海参", cucumber),
         "xmas_worms": ("圣诞树蠕虫", xmas_worms)}
CORAL = {"cauliflower": ("花椰菜珊瑚", cauliflower), "lobe": ("团块滨珊瑚", lobe_coral), "finger": ("指状珊瑚", finger_coral),
         "antler": ("鹿角珊瑚", antler_coral), "table": ("桌面珊瑚", table_coral), "sea_fan": ("海扇", sea_fan),
         "tube_sponge": ("管状海绵", tube_sponges), "leather": ("软珊瑚", leather_coral), "seagrass": ("海草", seagrass),
         "limu": ("红藻", limu), "sargassum": ("马尾藻", sargassum)}
GROUPS = [("鱼和大型动物", FISH), ("鱼群", SCHOOLS), ("海底生物", FLOOR), ("珊瑚和海藻", CORAL)]


def build():
    out = {}
    for _, g in GROUPS:
        for key, (_, fn) in g.items():
            out[f"life_{key}"] = fn()
    return out
