"""Paper-doll character: gender, hairstyle, hair/skin/outfit colors, accessory,
expression and pose are independent layers composed into one 20x28 sprite.

Layer order (back -> front):
    back hair -> body (outfit, pose) -> head (front hair + face skin)
    -> face (expression) -> accessory -> raised arm -> emote bubble

Grids use role letters, not colors; a Doll maps roles to palette ramps, so
any outfit/hair works with any color.
    hair  O k h H Y      (outline, shadow, base, light, shine)
    skin  q s S L        (outline, shadow, mid, base)
    top   u c C T        (outline, shadow, base, light)
    bottom n p P         (outline, shadow, base)
    shoes o x X          (ink outline, base, accent)
    W  white trim (collar, drawstrings, socks)
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from pixelkit import Anim, P, Sprite

PREVIEW_SCALE = 8
W, H = 20, 28


def rows(src: str) -> list[str]:
    out = []
    for r in src.split("\n"):
        r = r.strip()
        if not r:  # joins between string blocks; real empty rows are written as "."
            continue
        if len(r) > W:
            raise ValueError(f"row wider than {W}: {r!r}")
        out.append(r.ljust(W, "."))
    return out


# ------------------------------------------------------------------ heads
# rows 0-14; face skin occupies cols 4..15 on rows 10-12

_CROWN = """......OOOOOOOO
....OOHHHhhhhhOO
...OHHYYhhhhhhhkO
..OHHYhhhhhhhhhhkO
..OhHhhhhhhhhhhhkO
..OhhhhhhhhhhhhhkO
"""

_FACE = """
..OhLLLLLLLLLLLLhO
..OkLLLLLLLLLLLLkO
..OkLLLLLLLLLLLLkO
...OSLLLLLLLLLLSO
....qqSLLLLLLSqq
"""

_TOP = ".\n.\n"  # rows 0-1 left free for ahoge / buns

HEADS = {
    # messy boy hair: round crown, choppy fringe; ahoge drawn separately so it can sway
    "messy": rows(_TOP + _CROWN + """
.OhhhShhhhShhShhhkO
..OhkLLhLLLLLhLLkO
""" + _FACE),
    # side-swept: parted on the left, fringe sweeps diagonally down-right,
    # a stray tuft at the back-right breaks the dome
    "neat": rows("""
.
...............O
......OOOOOOOOOkO
....OOHHkHHhhhOOkO
...OHHYkYYhhhhhkO
..OHHhkhhhhhhhhhkO
..OhHhhhhhhhhhhhkO
..OkhhhhhhhhhhhhkO
..OkLLLhhhhhhhhhkO
..OhLLLLLLhhhhhhkO
""" + _FACE),
    # long hair: blunt bangs + sidelocks framing the face
    "long": rows(_TOP + _CROWN + """
..OhhhhhhhhhhhhhkO
..OhhLhhhhhLLhhhkO
""" + _FACE.replace("...OSLLLLLLLLLLSO", "..OhSLLLLLLLLLLShO").replace(
        "....qqSLLLLLLSqq", "..OhqqSLLLLLLSqqkO") + """
..Ohk.........OkO
...OO..........OO
"""),
    # twin buns: same fringe as long, buns are a back layer
    "buns": rows(_TOP + _CROWN + """
..OhhhhhhhhhhhhhkO
..OhhLhhhhhLLhhhkO
""" + _FACE),
}

AHOGE = [  # two sway positions
    rows("""
..........OO
.........OHO
"""),
    rows("""
...........OO
..........OHO
"""),
]


def draw_back_hair(s: Sprite, d: "Doll", bob: int = 0):
    """Hair that sits behind the body/head."""
    h = d.hair
    shape = Sprite(W, H)
    if d.hair_style == "long":
        # a curtain from the crown to mid-back, a bit wider than the head
        shape.rect(2, 6, 16, 9, h[2])           # beside the face
        shape.rect(3, 15, 14, 4, h[2])          # behind the shoulders
        shape.rect(4, 19, 3, 1, h[2]).rect(13, 19, 3, 1, h[2])  # tapered tips
        shape.vline(3, 9, 17, h[3])             # lit strand on the left
        shape.rect(15, 8, 2, 11, h[1]).rect(13, 19, 3, 1, h[1])  # shadow side
    elif d.hair_style == "buns":
        for cx in (4, 15):
            shape.ellipse(cx, 4, 2.5, 2.5, h[2])
            shape.set(cx - 1, 3, h[3]).set(cx, 2, h[4]).set(cx + 1, 6, h[1]).set(cx + 2, 5, h[1])
    else:
        return
    s.blit(shape.outline(h[0], grow=False), 0, bob)


# ------------------------------------------------------------------ bodies
# rows 15-27

BODIES = {
    # open jacket over a printed tee, rolled jeans, sneakers
    "jacket": rows("""
......uTqssqcu
....uTTTWWWWCCcu
...uTTcTWWWWCcCcu
...uTTcTWGGWCcCcu
...uTTcTwWWwCcCcu
...qLLcTWWWWCcSSq
....qqcTwwwwCcqq
.....nPPPPPPPpn
.....nPPpnnPPpn
.....nPPpnnPPpn
.....nRRRnnRRRn
....oxXxxooxxXxo
....oooooooooooo
"""),
    "hoodie": rows("""
.....uTTqssqccu
....uTTTWCCWcccu
...uTTcTWCCWCcCcu
...uTTcTCCCCCcCcu
...uTTcTccccCcCcu
...qLLccCCCCccSSq
....qquccccccuqq
......nPPPPPpn
......nPpnnPpn
......qLSqqLSq
......oWWooWWo
.....oXxxooxXxo
.....oooooooooo
"""),
    "dress": rows("""
........qssq
....uTWWWCCWWWcu
...uTTcWWCCWWcCcu
...uTTcTCCCCCcCcu
...uTTcTCCCCCcCcu
...qLLcCCCCCCcSSq
....qquccccccuqq
.....nPpPpPpPpn
....nPpPPpPPpPpn
....nnnnnnnnnnnn
......oWWooWWo
.....oXxxooxXxo
.....oooooooooo
"""),
}

OUTFIT_SHOES = {  # (base, accent)
    "jacket": (P.coral[2], P.linen[3]),
    "hoodie": (P.linen[3], P.coral[2]),
    "dress": (P.wood[1], P.wood[2]),
}

ARM_ROWS = range(17, 22)  # rows where the viewer-right arm hangs (cols 14-16)


def lower_arm_removed(body: list[str]) -> list[str]:
    out = list(body)
    for y in ARM_ROWS:
        r = list(out[y - 15])
        r[14:17] = "..."
        if r[13] not in ".":
            r[13] = "u" if y < 21 else r[13]
        out[y - 15] = "".join(r)
    return out


# ------------------------------------------------------------------ face

EYE_X = (6, 12)  # left column of each 2px eye
EYE_Y = 10


def draw_face(s: Sprite, d: "Doll", expr: str, look: int = 0, dy: int = 0):
    ink, shine = P.ink[0], P.linen[3]
    iris = d.eye[2]
    mouth, mouth_in = P.coral[1], P.coral[3]
    y0 = EYE_Y + dy
    blush = P.blush[0]
    for i, ex in enumerate(EYE_X):
        x = ex + look
        if expr == "neutral" and d.gender == "m":
            s.set(x, y0 + 1, shine).set(x + 1, y0 + 1, ink)
            s.hline(x, x + 1, y0 + 2, ink)
        elif expr in ("neutral", "surprised"):
            s.hline(x, x + 1, y0, ink)
            s.set(x, y0 + 1, shine).set(x + 1, y0 + 1, ink)
            s.hline(x, x + 1, y0 + 2, iris)
            if expr == "surprised":
                s.set(x - 1 + 3 * i, y0 - 1, d.hair[1])
        elif expr == "happy":
            s.hline(x, x + 1, y0 + 1, ink).set(x - 1, y0 + 2, ink).set(x + 2, y0 + 2, ink)
        elif expr in ("blink", "sleepy"):
            s.hline(x, x + 1, y0 + 2, ink)
            if expr == "sleepy":
                s.set(x - 1 if i == 0 else x + 2, y0 + 2, ink)
        elif expr == "flustered":  # > <
            a, b = (x, x + 1) if i == 0 else (x + 1, x)
            s.set(a, y0, ink).set(b, y0 + 1, ink).set(a, y0 + 2, ink)
        if d.gender == "f" and expr in ("neutral", "surprised"):  # lash flick
            s.set(x - 1 if i == 0 else x + 2, y0, ink)
    if d.gender == "m" and expr != "sleepy" and d.accessory != "glasses":  # thick brows; frames replace them
        for i, ex in enumerate(EYE_X):
            x = ex + look
            if expr == "flustered":  # worried tilt
                s.set(x, y0 - 1 + (i == 0), d.hair[0]).set(x + 1, y0 - 1 + (i == 1), d.hair[0])
            else:
                s.hline(x, x + 1, y0 - 1, d.hair[1] if expr != "surprised" else d.hair[0])
    # blush
    for bx in (5, 13):
        s.hline(bx, bx + 1, y0 + 3, blush)
    # mouth
    my = y0 + 3
    if expr == "happy":
        s.set(8, my, mouth).hline(9, 10, my, mouth_in).set(11, my, mouth)
    elif expr == "surprised":
        s.hline(9, 10, my, mouth).hline(9, 10, my + 1, mouth)
    elif expr == "flustered":
        s.set(8, my, mouth).set(9, my + 1, mouth).set(10, my, mouth).set(11, my + 1, mouth)
        s.set(16, 6 + dy, P.glass[3]).set(16, 7 + dy, P.glass[2])  # sweat drop
    elif expr == "sleepy":
        s.set(10, my, mouth)
    elif d.gender == "m":  # lopsided smirk
        s.hline(9, 10, my, mouth).set(11, my - 1, mouth)
    else:
        s.hline(9, 10, my, mouth)


# ------------------------------------------------------------------ accessories


def draw_accessory(s: Sprite, d: "Doll", dy: int = 0):
    if d.accessory == "glasses":
        f = P.coral[1]
        for ex in EYE_X:  # round frames: open corners read as round at this size
            x, y = ex - 1, EYE_Y - 1 + dy
            s.hline(x + 1, x + 2, y, f).hline(x + 1, x + 2, y + 4, f)
            s.vline(x, y + 1, y + 3, f).vline(x + 3, y + 1, y + 3, f)
        s.hline(9, 10, EYE_Y + dy, f)
    elif d.accessory == "bow":
        c = P.coral
        bow = Sprite.from_grid("""
            oo...oo
            oLLoSSo
            oLoKoSo
            oLLoSSo
            oo...oo
        """, {"o": c[0], "L": c[3], "S": c[2], "K": c[4]})
        s.blit(bow, 13, 2 + dy)
    elif d.accessory == "headphones":
        m = P.metal
        s.line(3, 7 + dy, 9, 1 + dy, m[0]).line(10, 1 + dy, 16, 7 + dy, m[0])
        for hx in (1, 16):
            s.rect(hx, 7 + dy, 3, 5, m[0]).rect(hx + 1, 8 + dy, 1, 3, d.top[2])


def raised_arm(s: Sprite, d: "Doll", frame: int):
    """Viewer-right arm up, waving. frame 0/1 = hand in / out."""
    t, sk = d.top, d.skin
    hx = 16 + frame
    # sleeve from shoulder (15,17) up to elbow/hand
    pts = [(14, 17), (15, 16), (15, 15), (hx, 14), (hx, 13)]
    for x, y in pts:
        s.rect(x - 1, y - 1, 4, 3, t[0])
    for x, y in pts:
        s.rect(x, y, 2, 1, t[2])
    s.set(14, 17, t[3]).set(15, 16, t[3])
    # hand
    s.rect(hx - 1, 9, 4, 4, sk[0]).rect(hx, 10, 2, 2, sk[3]).set(hx + 1, 11, sk[2])


# ------------------------------------------------------------------ emotes

EMOTES = {
    "note": """
...oo.
...oSo
...o.o
...o..
.ooo..
oSSo..
.oo...
""",
    "heart": """
.oo.oo.
oSSoLLo
oSSSLLo
.oSSSo.
..oSo..
...o...
""",
    "bang": """
.ooo.
.oSo.
.oSo.
.oSo.
..o..
.ooo.
.oSo.
.ooo.
""",
}
EMOTES["star"] = """
...o...
..oLo..
ooSLSoo
oSSSSSo
.oSSSo.
oSSoSSo
oo...oo
"""
EMOTES["bowl"] = """
.L.L.L.
..L.L..
ooooooo
oSSSSSo
.oSSSo.
..ooo..
"""
EMOTES["book"] = """
.oo.oo.
oLLoLLo
oOLoOLo
oLLoLLo
oOLoOLo
ooo.ooo
"""
EMOTES["game"] = """
.ooooo.
oSLSSSo
oLLLSRo
oSLSRSo
oSSSSSo
.oo.oo.
"""
EMOTES["soap"] = """
..oo...
.oLLo..
.oLLo.o
..oo.oLo
......o.
.oo.....
oLLo....
.oo.....
"""
EMOTES["zzz"] = """
oooo...
...o...
..o....
.o.....
oooo...
....ooo
.....o.
....ooo
"""
EMOTE_COLORS = {"note": P.blue, "heart": P.coral, "bang": P.mustard, "star": P.mustard,
                "bowl": P.clay, "book": P.sage, "game": P.blue, "soap": P.sky_soft, "zzz": P.blue}
# per-emote extra legend entries (R = accent button, O = second page shade)
EMOTE_EXTRA = {"bowl": {"L": P.linen[1]}, "book": {"L": P.linen[3], "O": P.linen[1]},
               "game": {"L": P.linen[3], "R": P.coral[2]}, "soap": {"o": P.blue[1], "L": P.linen[3]}}


def emote(name: str) -> Sprite:
    """Icon on a small white speech bubble so it reads on any background."""
    r = EMOTE_COLORS[name]
    legend = {"o": r[0], "S": r[2], "L": r[3], **EMOTE_EXTRA.get(name, {})}
    icon = Sprite.from_grid(EMOTES[name], legend)
    bw, bh = icon.w + 4, icon.h + 4
    b = Sprite(bw, bh + 2)
    b.rect(0, 0, bw, bh, P.ink[1]).rect(1, 1, bw - 2, bh - 2, P.linen[3])
    for cx, cy in ((0, 0), (bw - 1, 0), (0, bh - 1), (bw - 1, bh - 1)):
        b.set(cx, cy, None)
    b.hline(1, bw - 2, bh - 2, P.linen[2])
    # tail pointing down-left toward the head
    b.set(2, bh - 1, P.linen[3]).set(1, bh, P.ink[1]).set(2, bh, P.linen[3]).set(3, bh, P.ink[1])
    b.set(2, bh + 1, P.ink[1])
    b.blit(icon, 2, 2)
    return b


# ------------------------------------------------------------------ doll


@dataclass(frozen=True)
class Doll:
    gender: str = "m"           # "m" | "f" — picks default hair/outfit set
    hair_style: str = "messy"
    hair: tuple = tuple(P.hair_brown)
    skin: tuple = tuple(P.skin)
    outfit: str = "hoodie"
    top: tuple = tuple(P.green)
    bottom: tuple = tuple(P.blue)
    shoes: tuple | None = None   # None = the outfit's own shoes
    eye: tuple = tuple(P.hair_brown)
    accessory: str | None = None
    print_color: str = P.coral[2]

    def legend(self):
        h, s, t, b = self.hair, self.skin, self.top, self.bottom
        shoes = self.shoes or OUTFIT_SHOES[self.outfit]
        return {
            "O": h[0], "k": h[1], "h": h[2], "H": h[3], "Y": h[4],
            "q": s[0], "s": s[1], "S": s[2], "L": s[3],
            "u": t[0], "c": t[1], "C": t[2], "T": t[3],
            "n": b[0], "p": b[1], "P": b[2],
            "o": P.ink[0], "x": shoes[0], "X": shoes[1],
            "W": P.linen[3], "w": P.linen[2], "G": self.print_color, "R": b[3],
        }

    def layers(self, expr="neutral", look=0, bob=0, sway=0, wave=None):
        """Ordered (key, draw) pairs, back to front. A key names everything the
        layer's pixels depend on except colors, so recolorable role maps can
        be exported once per key (see tools/make_creator.py)."""
        lg = self.legend()
        arm = wave is not None

        def grid_at(src, y):
            return lambda s: s.blit(Sprite.from_grid("\n".join(src), lg), 0, y)

        body = lower_arm_removed(BODIES[self.outfit]) if arm else BODIES[self.outfit]
        out = []
        if self.hair_style in ("long", "buns"):
            out.append((f"back/{self.hair_style}/{bob}", lambda s: draw_back_hair(s, self, bob)))
        out.append((f"body/{self.outfit}/{int(arm)}", grid_at(body, 15)))
        out.append((f"head/{self.hair_style}/{bob}", grid_at(HEADS[self.hair_style], bob)))
        if self.hair_style == "messy":
            out.append((f"ahoge/{sway % 2}/{bob}", grid_at(AHOGE[sway % 2], bob)))
        glasses = int(self.accessory == "glasses")
        out.append((f"face/{self.gender}/{expr}/{look}/{bob}/{glasses}",
                    lambda s: draw_face(s, self, expr, look, bob)))
        if self.accessory:
            out.append((f"acc/{self.accessory}/{bob}", lambda s: draw_accessory(s, self, bob)))
        if arm:
            out.append((f"arm/{wave}", lambda s: raised_arm(s, self, wave)))
        return out

    def render(self, **frame) -> Sprite:
        """Emotes live outside the 20x28 frame — wrap the result with with_emote()."""
        s = Sprite(W, H)
        for _, draw in self.layers(**frame):
            draw(s)
        return s


def with_emote(spr: Sprite, name: str | None, x=13, y=0) -> Sprite:
    """Place the doll on a taller canvas with an emote bubble above-right."""
    out = Sprite(W + 4, H + 15)
    out.blit(spr, 0, 15)
    if name:
        out.blit(emote(name), x, y)
    return out


# ------------------------------------------------------------------ presets

BOY = Doll(outfit="jacket")
GIRL = Doll(
    gender="f", hair_style="long", hair=tuple(P.hair_black), outfit="dress",
    top=tuple(P.coral), bottom=tuple(P.blue),
    eye=tuple(P.blue), accessory="bow",
)

VARIANTS = [
    ("boy", BOY),
    ("boy·glasses", replace(BOY, hair_style="neat", hair=tuple(P.hair_black), top=tuple(P.blue),
                            bottom=tuple(P.metal), accessory="glasses", skin=tuple(P.skin_tan))),
    ("boy·headphones", replace(BOY, hair=tuple(P.mustard), top=tuple(P.coral), bottom=tuple(P.green),
                               accessory="headphones", skin=tuple(P.skin_deep))),
    ("girl", GIRL),
    ("girl·buns", replace(GIRL, hair_style="buns", hair=tuple(P.hair_pink), top=tuple(P.mustard),
                          bottom=tuple(P.coral), accessory=None, skin=tuple(P.skin_tan))),
    ("girl·brown", replace(GIRL, hair=tuple(P.hair_brown), top=tuple(P.green), bottom=tuple(P.wood),
                           skin=tuple(P.skin_deep), accessory="glasses")),
]


# (frame params, emote, ms). "cheer" = heart for girls, star for boys.
IDLE_SEQ = [
    (dict(), None, 600),
    (dict(bob=1, sway=1), None, 350),
    (dict(), None, 450),
    (dict(expr="blink"), None, 110),
    (dict(), None, 500),
    (dict(look=-1), None, 650),
    (dict(look=1), None, 650),
    (dict(expr="surprised"), "bang", 500),
    (dict(expr="happy"), "note", 450),
    (dict(expr="happy", bob=1, sway=1), "note", 300),
    (dict(expr="happy"), "note", 450),
    (dict(expr="happy", wave=0), "cheer", 180),
    (dict(expr="happy", wave=1), "cheer", 180),
    (dict(expr="happy", wave=0), "cheer", 180),
    (dict(expr="happy", wave=1), "cheer", 180),
    (dict(expr="blink"), None, 110),
    (dict(), None, 500),
]


def idle_life(d: Doll) -> Anim:
    """A lively idle loop: breathe, blink, glance around, hum, wave."""
    cheer = "heart" if d.gender == "f" else "star"
    frames = [with_emote(d.render(**kw), cheer if em == "cheer" else em) for kw, em, _ in IDLE_SEQ]
    return Anim(frames, [ms for *_, ms in IDLE_SEQ])


EXPRS = ["neutral", "happy", "surprised", "sleepy", "flustered", "blink"]


def strip(sprites, gap=4):
    out = Sprite(sum(sp.w for sp in sprites) + gap * (len(sprites) - 1), max(sp.h for sp in sprites))
    x = 0
    for sp in sprites:
        out.blit(sp, x, out.h - sp.h)
        x += sp.w + gap
    return out


def build():
    out = {
        "variants": strip([d.render() for _, d in VARIANTS]),
        "expressions": strip([d.render(expr=e) for d in (BOY, GIRL) for e in EXPRS[:5]], gap=2),
    }
    for name, d in (("boy", BOY), ("girl", GIRL)):
        out[f"{name}_idle_life"] = idle_life(d)
    return out
