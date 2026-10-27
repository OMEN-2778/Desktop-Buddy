"""怪兽夜 giants, v2 (preview only, not wired into the game yet).

Costumed giants 2.5-3x Buddy's height, people inside: a kaiju suit, a sheet
ghost carried by three, a walking tree spirit, a skeleton on stilts.
Each part is drawn on its own layer with volume shading (light from the
top-left, dithered between tones) and outlined in its own darkest shade.
Two walk frames each.
"""

import math

from pixelkit import P, Sprite

PREVIEW_SCALE = 6
LIGHT = (-0.55, -0.8)


def layer(w, h):
    return Sprite(w, h)


def lit(nx, ny):
    """Brightness of a point on a bulging surface (-1..1 across), top-left light."""
    nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
    return -(nx * LIGHT[0] + ny * LIGHT[1]) * 0.75 + nz * 0.45


def tone(R, l, x, y, lo=1):
    """Pick a ramp shade for brightness l, dithering where two bands meet."""
    idx, edges = [lo, 2, 3, len(R) - 1], (-0.15, 0.25, 0.62)
    i = sum(l >= e for e in edges)
    if i and l < edges[i - 1] + 0.07 and (x + y) % 2:
        i -= 1
    return R[min(len(R) - 1, idx[i])]


def blob(s, cx, cy, rx, ry, R, lo=1, tilt=0.0):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            dx, dy = dx * math.cos(tilt) + dy * math.sin(tilt), -dx * math.sin(tilt) + dy * math.cos(tilt)
            if dx * dx + dy * dy <= 1 and 0 <= x < s.w and 0 <= y < s.h:
                s.set(x, y, tone(R, lit(dx, dy), x, y, lo))


def limb(s, x0, y0, x1, y1, r0, r1, R, lo=1):
    """A tapered cylinder from (x0,y0) to (x1,y1), shaded across its width."""
    L = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    for y in range(int(min(y0, y1) - max(r0, r1)) - 1, int(max(y0, y1) + max(r0, r1)) + 2):
        for x in range(int(min(x0, x1) - max(r0, r1)) - 1, int(max(x0, x1) + max(r0, r1)) + 2):
            px, py = x + 0.5 - x0, y + 0.5 - y0
            t = max(0, min(1, px * ux + py * uy))
            r = r0 + (r1 - r0) * t
            d = (px - ux * t * L) * -uy + (py - uy * t * L) * ux       # signed distance across
            along = math.hypot(px - ux * t * L, py - uy * t * L)
            if along <= r and 0 <= x < s.w and 0 <= y < s.h:
                nx = d / r * -uy if r else 0
                ny = d / r * ux if r else 0
                s.set(x, y, tone(R, lit(nx * 0.95, ny * 0.95), x, y, lo))


def done(s, out):
    return s.outline(out, grow=False)


def stack(w, h, layers):
    s = Sprite(w, h)
    for l in layers:
        s.blit(l, 0, 0)
    return s


def sneaker(s, x, y, c=P.slate, sole=P.linen[3]):
    s.rect(x, y, 5, 2, c[1]).hline(x, x + 3, y, c[3]).set(x + 4, y + 1, c[0]).hline(x, x + 4, y + 2, sole).set(x + 1, y, P.linen[3])


# ---------------------------------------------------------------- kaiju suit
def godzilla(f=0):
    W_, H_ = 60, 76
    G, Pl, B = P.green, P.mint, P.sage
    feet = H_ - 3
    stepL, stepR = (2, 0) if f else (0, 2)
    tail = layer(W_, H_)
    for i in range(14):                                       # tail: a chain of shrinking shaded lumps down to the ground
        t = i / 13
        cx, cy = 22 - t * 20, 52 + t * 16 - math.sin(t * 3.1) * 2
        blob(tail, cx, cy, 6.5 - t * 4.3, 5.5 - t * 3.5, G)
    legs = layer(W_, H_)
    for x0, lift in ((22, stepL), (34, stepR)):
        blob(legs, x0, 52 - lift, 7.5, 9, G)                  # thigh
        limb(legs, x0, 55 - lift, x0 + 1, feet - 4 - lift, 6, 5, G)
        blob(legs, x0 + 2, feet - 3 - lift, 6.5, 3, G)        # foot
    body = layer(W_, H_)
    blob(body, 28, 38, 15, 19, G)
    belly = layer(W_, H_)
    blob(belly, 33, 40, 8, 15, B, lo=2)
    arms = layer(W_, H_)
    limb(arms, 39, 31, 46, 36, 3.2, 2.4, G)
    limb(arms, 46, 36, 49, 33, 2.4, 1.8, G)
    head = layer(W_, H_)
    blob(head, 37, 15, 10, 8.5, G)
    limb(head, 40, 16, 53, 18, 6, 4.5, G)                     # snout
    blob(head, 44, 22, 8, 3.2, G, lo=0)                       # jaw
    plates = layer(W_, H_)
    spine = [(27, 7, 3.2), (22, 12, 4.4), (18, 19, 5.2), (15, 27, 5.4), (14, 35, 5), (13, 43, 4.4), (10, 51, 3.6), (6, 57, 2.8), (2, 62, 2)]
    for x, y, sz in spine:                                    # dorsal plates: separate jagged leaves standing off the back
        blob(plates, x - sz * 0.7, y - sz * 0.2, sz * 0.62, sz * 1.15, Pl, lo=1, tilt=-0.75)
        blob(plates, x - sz * 0.2, y + sz * 0.6, sz * 0.4, sz * 0.7, Pl, lo=1, tilt=-0.5)
    s = stack(W_, H_, [done(tail, G[0]), done(legs, G[0]), done(body, G[0]), done(belly, B[0]),
                       done(arms, G[0]), done(plates, Pl[0]), done(head, G[0])])
    for i in range(160):                                      # pebbly hide
        x, y = (i * 37) % W_, (i * 53) % H_
        c = s.px[y, x]
        if c[3] and tuple(c[:3]) in ({tuple(int(G[2][j:j + 2], 16) for j in (1, 3, 5))}):
            s.set(x, y, G[3] if (x + y) % 3 else G[1])
    for y in range(28, 54, 3):                                # belly plate seams
        for x in range(27, 40):
            if s.px[y, x][3] and tuple(s.px[y, x][:3]) in {tuple(int(B[k][j:j + 2], 16) for j in (1, 3, 5)) for k in (2, 3, 4)}:
                s.set(x, y, B[1])
    s.rect(38, 11, 4, 3, P.mustard[4]).set(40, 11, P.ink[0]).set(40, 12, P.ink[0]).set(38, 11, P.linen[3])   # eye
    s.hline(35, 42, 9, G[1]).hline(36, 41, 8, G[3])           # brow ridge
    s.set(51, 15, G[0]).set(52, 16, G[0])                     # nostril
    s.hline(43, 54, 20, G[0])                                 # mouth line, teeth
    for x in range(44, 54, 2):
        s.set(x, 19, P.linen[3]).set(x + 1, 21, P.porcelain[2])
    for x0, lift in ((22, stepL), (34, stepR)):               # claws
        for k in range(3):
            s.set(x0 + 4 + k * 2, feet - 1 - lift, P.oat[3]).set(x0 + 5 + k * 2, feet - 1 - lift, P.oat[1])
    for k in range(3):
        s.set(50, 32 + k, P.oat[3])
    for x0, lift in ((22, stepL), (34, stepR)):               # the person inside shows at the ankles
        sneaker(s, x0 - 1, feet - lift)
    s.vline(19, 30, 46, P.metal[3]).set(19, 47, P.metal[4])   # zip half-hidden by the plates
    return s


# ---------------------------------------------------------------- the sheet ghost (three people under it)
def giant_ghost(f=0):
    W_, H_ = 50, 78
    L = P.linen
    sheet = layer(W_, H_)
    hem = 66
    for y in range(2, hem + 4):
        for x in range(W_):
            if y < 20:                                         # the dome of the head
                dx, dy = (x + 0.5 - 25) / 17, (y + 0.5 - 20) / 18
                if dx * dx + dy * dy > 1:
                    continue
                l = lit(dx, dy)
            else:                                              # the drape widens as it falls, folds swaying
                half = 17 + (y - 20) * 0.12
                sway = math.sin(y * 0.05 + f * 0.8) * 1.2
                dx = (x + 0.5 - 25 - sway) / half
                if abs(dx) > 1:
                    continue
                edge = hem + round(2.5 * math.sin((x + f * 3) * 0.55)) + (1 if x % 7 == 3 else 0)
                if y > edge:
                    continue
                fold = math.sin((x - 25) * 0.62 + y * 0.03 + f * 0.5)
                l = lit(dx * 0.9, -0.15) + fold * 0.22 - max(0, (y - 50) / 60)
            sheet.set(x, y, tone(L, l, x, y))
    for (cx, cy) in ((8, 40), (42, 38)):                        # arms pushing the sheet out
        blob(sheet, cx, cy, 4, 6, L)
    s = done(sheet, L[0])
    for x0 in (15, 29):                                         # eyes: deep holes with a rim of shadow
        blob(s, x0 + 3, 22, 4, 5, P.ink, lo=0)
        s.set(x0 + 2, 19, P.ink[1]).set(x0 + 1, 21, L[1])
        s.set(x0 + 4, 24, P.lilac[1])
    blob(s, 25, 36, 3, 4.5, P.ink, lo=0)                        # the "O" mouth
    s.hline(11, 14, 30, P.blossom[3]).hline(36, 39, 30, P.blossom[3])
    # the lantern one of them carries out of the sheet
    s.vline(44, 33, 38, P.ink[1])
    blob(s, 44, 42, 3.2, 3.8, P.coral)
    s.hline(42, 46, 38, P.mustard[3]).hline(42, 46, 46, P.mustard[3]).set(43, 41, P.light[1]).vline(44, 47, 48, P.mustard[4])
    for k, x in enumerate((12, 23, 34)):                        # three pairs of legs under the hem
        up = (k + f) % 2
        for j, (dx, lift) in enumerate(((0, up), (4, 1 - up))):
            jeans = (P.blue, P.slate, P.teal)[k]
            s.rect(x + dx, hem + 1 - lift, 3, H_ - hem - 4, jeans[2]).vline(x + dx, hem + 1 - lift, H_ - 4 - lift, jeans[3]).vline(x + dx + 2, hem + 1 - lift, H_ - 4 - lift, jeans[1])
            sneaker(s, x + dx - 1, H_ - 3 - lift, (P.coral, P.metal, P.mustard)[k])
    return s


# ---------------------------------------------------------------- the tree spirit
def tree_spirit(f=0):
    W_, H_ = 58, 80
    B, A, M = P.walnut, P.autumn, P.green
    trunk = layer(W_, H_)
    for y in range(28, 70):
        for x in range(W_):
            half = 9 + max(0, (y - 58) * 0.5)                    # flares into roots at the bottom
            dx = (x + 0.5 - 29) / half
            if abs(dx) <= 1:
                l = lit(dx, -0.1) + (0.25 if (x * 3 + y // 4) % 9 == 0 else 0) - (0.35 if (x + (y // 6) * 2) % 5 == 0 else 0)
                trunk.set(x, y, tone(B, l, x, y))
    arms = layer(W_, H_)
    limb(arms, 21, 38, 9, 30, 3.5, 2, B)
    limb(arms, 9, 30, 3, 22, 2, 1.2, B)
    limb(arms, 9, 30, 4, 33, 1.5, 1, B)
    limb(arms, 37, 40, 49, 31, 3.5, 2, B)
    limb(arms, 49, 31, 54, 24, 2, 1.2, B)
    limb(arms, 49, 31, 55, 34, 1.5, 1, B)
    crown = layer(W_, H_)
    for cx, cy, rx, ry in ((29, 17, 18, 12), (13, 22, 10, 8), (45, 21, 10, 8), (20, 8, 10, 7), (38, 8, 10, 7),
                           (29, 4, 8, 4.5), (8, 30, 5, 4), (52, 28, 5, 4)):
        blob(crown, cx, cy, rx, ry, A)
    s = stack(W_, H_, [done(arms, B[0]), done(trunk, B[0]), done(crown, A[0])])
    for i in range(220):                                         # leaf clumps: lit tips, shaded pockets
        x, y = (i * 29 + i // 7) % W_, (i * 13) % 36
        if s.px[y, x][3] and tuple(s.px[y, x][:3]) != tuple(int(A[0][j:j + 2], 16) for j in (1, 3, 5)):
            up = (x - 29) * -0.02 + (y - 18) * -0.04
            c = A[4] if up > 0.45 else A[3] if up > 0.05 else A[1]
            s.set(x, y, c)
            if x + 1 < W_ and s.px[y, x + 1][3]:
                s.set(x + 1, y, A[2])
    for x, y in ((14, 14), (40, 12), (30, 24), (22, 27)):        # a few late green leaves
        s.set(x, y, M[3]).set(x + 1, y, M[2])
    # the face, carved into the bark: hollow eyes glowing amber, a crooked mouth
    for x0 in (22, 33):
        blob(s, x0, 44, 3.4, 4, B, lo=0)
        s.rect(x0 - 1, 44, 2, 2, P.mustard[3]).set(x0 - 1, 44, P.light[1])
        s.hline(x0 - 3, x0 + 3, 39, B[1])                        # brow knot
    for x in range(21, 36):
        y = 53 + round(math.sin(x * 0.9) * 1)
        s.set(x, y, B[0]).set(x, y + 1, B[1])
    for x in (24, 30):
        s.set(x, 54, P.oat[3])
    s.ellipse(35, 61, 2, 1.5, B[0])                              # a knothole
    blob(s, 20, 63, 3, 1.6, P.coral, lo=1)                       # a toadstool on the trunk
    s.set(19, 62, P.linen[3]).set(21, 63, P.linen[3]).vline(20, 64, 65, P.oat[3])
    for x, y in ((33, 66), (35, 66), (25, 67)):                  # moss at the roots
        s.set(x, y, M[2]).set(x + 1, y, M[3])
    up = f % 2
    for k, x in enumerate((24, 31)):                             # the person's legs under the bark skirt
        dy = up if k == 0 else 1 - up
        s.rect(x, 70 - dy, 4, 6, P.oak[1]).vline(x, 70 - dy, 75 - dy, P.oak[2])
        sneaker(s, x - 1, 76 - dy, P.walnut)
    for x, y in ((6, 40), (50, 45), (44, 58)):                   # a few leaves falling off it
        s.set(x + f, y + f * 2, A[3]).set(x + 1 + f, y + f * 2, A[2])
    return s


# ---------------------------------------------------------------- the skeleton on stilts
def giant_skeleton(f=0):
    W_, H_ = 48, 88
    K, Wt = P.hair_black, P.porcelain
    robe = layer(W_, H_)
    for y in range(22, 58):
        for x in range(W_):
            if y < 27:                                             # shoulders
                half = 4 + (y - 22) * 1.2
            elif y < 46:                                           # pulled in at the waist
                half = 10 - 3 * math.sin(math.pi * (y - 27) / 22)
            else:                                                  # flaring out to a ragged hem
                half = 8 + (y - 46) * 0.7
            dx = (x + 0.5 - 24) / half
            if abs(dx) <= 1 and not (y > 53 and (x * 7 + f) % 5 < 2 and y > 55 - (x % 3)):
                fold = math.sin((x - 24) * 0.8 + y * 0.05 + f * 0.6)
                robe.set(x, y, tone(K, lit(dx * 0.9, -0.1) + fold * 0.18, x, y))
    blob(robe, 24, 13, 13.5, 13, K, lo=0)                       # a hood behind the skull
    for side in (-1, 1):                                         # sleeves
        limb(robe, 24 + side * 9, 27, 24 + side * 13, 47, 2.6, 3.6, K)                     # sleeves, widening to the cuff
    skull = layer(W_, H_)
    blob(skull, 24, 11, 11, 10.5, Wt)
    blob(skull, 24, 19, 7, 4.5, Wt)                              # jaw
    s = stack(W_, H_, [done(robe, K[0]), done(skull, Wt[0])])
    for x0 in (19, 29):                                          # sockets with depth and a faint glint
        blob(s, x0, 12, 3.2, 3.6, P.ink, lo=0)
        s.set(x0 + 1, 11, P.coral[3])
    s.set(23, 16, P.ink[1]).set(24, 16, P.ink[1]).set(24, 17, P.ink[0])   # nasal cavity
    s.hline(16, 18, 15, Wt[1]).hline(30, 32, 15, Wt[1])          # cheekbones
    for x in range(19, 30):                                      # teeth row and the gap of the jaw
        s.set(x, 20, Wt[3] if x % 2 else Wt[1]).set(x, 21, Wt[0] if x % 2 == 0 else Wt[2])
    s.hline(17, 21, 5, Wt[4] if len(Wt) > 4 else Wt[3]).set(16, 7, Wt[3])
    for i in range(3):                                           # a crack on the crown
        s.set(28 + i, 3 + i, Wt[1])
    bone = Wt[3]
    s.vline(24, 25, 50, bone).vline(25, 25, 50, Wt[2])           # spine
    for k, y in enumerate(range(28, 44, 3)):                     # curved ribs
        w = 7 - abs(k - 2)
        for d in range(1, w + 1):
            yy = y + round(d * d / 14)
            s.set(24 - d, yy, bone).set(25 + d, yy, Wt[2])
    for x in range(18, 32):                                      # pelvis
        s.set(x, 50 + round(abs(x - 24.5) / 3), bone)
    s.hline(20, 29, 52, Wt[2])
    for side in (-1, 1):                                         # arm bones down the sleeves, elbows, finger bones
        x = 24 + side * 12
        s.vline(x, 27, 37, bone).set(x, 38, Wt[4] if len(Wt) > 4 else bone).vline(x + side, 39, 48, bone)
        for k in range(4):
            s.vline(x + side + (k - 1.5 > 0 and 1 or -1) * (k % 2), 51, 53 + k % 2, bone)
    up = f % 2
    for k, x in enumerate((19, 27)):                             # stilts in black trousers, bone print
        dy = up if k == 0 else 1 - up
        limb(s, x + 1, 56 - dy, x + 1, H_ - 6 - dy, 2.2, 1.8, K)
        s.vline(x + 1, 58 - dy, H_ - 8 - dy, bone)
        for y in (62, 72):
            s.set(x, y - dy, bone).set(x + 2, y - dy, bone)
        sneaker(s, x - 1, H_ - 4 - dy, P.metal)
    return s


GIANTS = {"godzilla": godzilla, "ghost": giant_ghost, "tree": tree_spirit, "skeleton": giant_skeleton}


def build():
    out = {}
    for k, fn in GIANTS.items():
        out[f"giant2_{k}"] = fn(0)
    a = [fn(0) for fn in GIANTS.values()]
    sheet = Sprite(sum(x.w for x in a) + 6 * len(a), max(x.h for x in a) + 2)
    x = 0
    for spr in a:
        sheet.blit(spr, x, sheet.h - spr.h - 1)
        x += spr.w + 6
    out["giants2_sheet"] = sheet
    return out
