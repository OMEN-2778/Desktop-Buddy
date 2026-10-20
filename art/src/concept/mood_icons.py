"""Emotion emoji for the mood circle: 16 round chibi faces, 16x16, two
frames each (blink, tear, steam, sparkle...). The circle frame around them
(white ring + emotion colour) is drawn by the page; COLORS holds that tint.
Each face is tinted in its emotion's colour family (user), lighter than the
circle behind it, and the colours are spread round the wheel so no two
emotions look alike: hue first, then lightness for neighbours (rust 焦虑 vs
orange 元气满满, olive 浑身难受 vs yellow 美滋滋, lilac 发懵 vs violet 专心致志).

    frames(name) -> [Sprite, Sprite]
"""

from __future__ import annotations

from pixelkit import Anim, P, Sprite

PREVIEW_SCALE = 10
SIZE = 16

# (key, name shown in the game, frame tint). Names echo The Sims 4's
# emotions, reworded.
EMOTIONS = [
    ("happy", "美滋滋", "#f5c938"),          # sunny yellow
    ("confident", "小得意", "#3dbd8a"),      # emerald
    ("energized", "元气满满", "#ff9330"),     # bright orange
    ("flirty", "心动", "#e070c8"),           # magenta
    ("focused", "专心致志", "#8a68e6"),       # violet
    ("inspired", "灵光一闪", "#36c3d6"),      # cyan
    ("playful", "调皮", "#98cf3c"),          # lime
    ("fine", "平静", "#e6e4ee"),             # near white
    ("bored", "好无聊", "#a6a2b5"),          # cool grey
    ("embarrassed", "难为情", "#f585a6"),     # rose pink
    ("uncomfortable", "浑身难受", "#a59a42"),  # olive
    ("tense", "焦虑", "#c4673a"),            # rust
    ("angry", "气鼓鼓", "#e34646"),          # red
    ("sad", "失落", "#4e9be6"),              # blue
    ("dazed", "发懵", "#cdb6ef"),            # pale lilac
    ("scared", "害怕", "#5d6cbf"),           # slate indigo
    # not an emotion: shown the whole time she's asleep (user: a dark grey sleeping face)
    ("asleep", "睡着了", "#5e5a6b"),
]
NAMES = [k for k, _, _ in EMOTIONS]
COLORS = {k: c for k, _, c in EMOTIONS}
LABELS = {k: n for k, n, _ in EMOTIONS}

M = P.mustard
E = P.walnut[0]                  # features
MOUTH, TONGUE = P.coral[1], P.coral[3]
BLUSH = P.blush[0]
TEAR = P.glass[3]


def _ramp(hex_color: str) -> list[str]:
    """Five face tones in one colour family: outline, shade, rim, fill,
    highlight. Shadows lean a little cool, highlights a little warm."""
    import colorsys
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    s = min(0.85, s) if s > 0.12 else s
    out = []
    for light, shift, sat in ((0.30, -0.025, 1.0), (0.46, -0.012, 1.0), (0.62, 0, 0.95), (0.78, 0.008, 0.9), (0.91, 0.02, 0.8)):
        hh = h + (shift if 0.12 < h < 0.65 else -shift)     # cool shadows / warm lights, either side of the wheel
        rr, gg, bb = colorsys.hls_to_rgb(hh % 1, light, s * sat)
        out.append("#%02x%02x%02x" % (round(rr * 255), round(gg * 255), round(bb * 255)))
    return out


RAMPS = {k: _ramp(c) for k, _, c in EMOTIONS if k != "asleep"}


def face(ramp=M) -> Sprite:
    """A round face lit from the top-left."""
    s = Sprite(SIZE, SIZE)
    s.ellipse(7.5, 7.5, 7, 7, ramp[0])
    s.ellipse(7.5, 7.5, 6, 6, ramp[2])
    s.ellipse(7, 7, 5.3, 5.3, ramp[3])
    s.rect(4, 3, 2, 1, ramp[4]).set(3, 4, ramp[4])
    return s


def dot_eyes(s, y=7, dx=0):
    s.rect(4 + dx, y - 1, 2, 2, E).rect(10 + dx, y - 1, 2, 2, E)
    s.set(4 + dx, y - 1, P.linen[3]).set(10 + dx, y - 1, P.linen[3])


def closed_eyes(s, y=7):
    s.hline(4, 5, y, E).hline(10, 11, y, E)


def happy_eyes(s, y=7):        # ^ ^
    for x in (3, 9):
        s.set(x, y, E).set(x + 1, y - 1, E).set(x + 2, y - 1, E).set(x + 3, y, E)


def blush(s, y=9):
    s.hline(2, 3, y, BLUSH).hline(12, 13, y, BLUSH)


def smile(s, y=10, w=2):
    s.set(7 - w, y, E).set(8 + w, y, E).hline(7 - w + 1, 8 + w - 1, y + 1, E)


def big_grin(s, y=10):
    s.hline(4, 11, y, E).set(4, y + 1, E).set(11, y + 1, E).hline(5, 10, y + 1, MOUTH)
    s.hline(5, 10, y + 2, E).hline(6, 9, y + 2, MOUTH).hline(6, 9, y + 3, E)
    s.hline(5, 10, y, P.linen[3])


def frown(s, y=11):
    s.hline(6, 9, y, E).set(5, y + 1, E).set(10, y + 1, E)


def drop(s, x, y, c=TEAR):
    s.set(x, y, c).rect(x - 1, y + 1, 3, 2, c).set(x - 1, y + 1, P.glass[4])


def heart(s, x, y, c=P.coral[2]):
    s.set(x, y, c).set(x + 2, y, c).hline(x, x + 2, y + 1, c).set(x + 1, y + 2, c).set(x, y, P.coral[3])


def sparkle(s, x, y, big, c=P.linen[3]):
    s.set(x, y, c)
    if big:
        s.set(x - 1, y, c).set(x + 1, y, c).set(x, y - 1, c).set(x, y + 1, c)


def draw(name: str, f: int) -> Sprite:
    if name == "asleep":
        s = face([P.metal[1], P.metal[2], P.metal[3], P.metal[4], P.metal[5]])
    else:
        R = RAMPS[name]
        s = face(R)
    if name == "happy":
        happy_eyes(s, 7 - f)
        big_grin(s, 9)
        blush(s)
    elif name == "confident":
        s.hline(3, 6, 6, E).hline(9, 12, 6, E)            # level, lowered lids
        s.rect(4, 7, 2, 1, E).rect(10, 7, 2, 1, E)
        s.line(5, 11, 10, 10, E).set(11, 9, E)            # smirk
        sparkle(s, 13, 2, f == 0, M[4])
    elif name == "energized":
        dot_eyes(s, 6)
        s.set(3, 4, E).set(4, 3, E).set(11, 3, E).set(12, 4, E)  # raised brows
        big_grin(s, 9)
        bolt = [(13, 0), (12, 1), (12, 2), (13, 2), (12, 3)] if f == 0 else [(14, 0), (13, 1), (13, 2), (14, 2), (13, 3)]
        for x, y in bolt:
            s.set(x, y, M[4])
    elif name == "flirty":
        heart(s, 3, 5)
        heart(s, 9, 5)
        smile(s, 10, 1)
        blush(s, 10)
        if f:
            heart(s, 12, 0, P.coral[3])
    elif name == "focused":
        s.line(3, 4, 6, 5, E).line(9, 5, 12, 4, E)        # knitted brows
        if f == 0:
            s.rect(4, 7, 2, 2, E).rect(10, 7, 2, 2, E)
        else:
            closed_eyes(s, 8)
        s.hline(6, 9, 11, E)
    elif name == "inspired":
        for x in (4, 10):                                 # star eyes
            s.set(x + 1, 5, E).hline(x, x + 2, 6, E).set(x + 1, 7, E)
            s.set(x + 1, 6, M[4])
        smile(s, 10, 2)
        bulb = P.light
        s.rect(13, 0, 2, 2, bulb[0]).set(13, 0, bulb[1]).set(13, 2, M[1]).set(14, 2, M[1])
        if f:
            s.set(12, 0, bulb[1]).set(15, 1, bulb[1])
    elif name == "playful":
        if f == 0:
            happy_eyes(s, 7)
            s.rect(10, 6, 2, 2, E)
            s.hline(3, 6, 7, None)
            s.set(3, 7, E).set(4, 6, E).set(5, 6, E).set(6, 7, E)
            s.rect(10, 6, 2, 2, E)
        else:
            s.rect(4, 6, 2, 2, E)
            s.set(9, 7, E).set(10, 6, E).set(11, 6, E).set(12, 7, E)
        s.hline(5, 10, 10, E).rect(8, 11, 2, 2, TONGUE).set(8, 12, MOUTH)
        blush(s)
    elif name == "fine":
        if f == 0:
            s.rect(4, 6, 2, 2, E).rect(10, 6, 2, 2, E)
        else:
            closed_eyes(s, 7)
        smile(s, 10, 1)
    elif name == "bored":
        s.hline(3, 6, 6, R[1]).hline(9, 12, 6, R[1])     # heavy lids
        s.hline(4, 5, 7, E).hline(10, 11, 7, E)
        s.hline(6, 9, 11, E)
        if f:                                             # a sigh puff
            s.rect(12, 10, 2, 1, P.linen[3]).set(14, 9, P.linen[3])
    elif name == "embarrassed":
        for x in (3, 9):                                  # > <
            s.set(x, 5, E).set(x + 1, 6, E).set(x + 2, 7, E) if x == 3 else s.set(x + 2, 5, E).set(x + 1, 6, E).set(x, 7, E)
            s.set(x, 7, E) if x == 3 else s.set(x + 2, 7, E)
        s.hline(2, 5, 9, BLUSH).hline(10, 13, 9, BLUSH).hline(3, 4, 10, BLUSH).hline(11, 12, 10, BLUSH)
        s.set(5, 12, E).set(6, 11, E).set(7, 12, E).set(8, 11, E).set(9, 12, E).set(10, 11, E)
        drop(s, 13, 2 + f)
    elif name == "uncomfortable":
        s.hline(4, 5, 7, E).hline(10, 11, 7, E).set(3, 6, E).set(12, 6, E)
        wav = [(5, 11), (6, 10), (7, 11), (8, 10), (9, 11), (10, 10)] if f == 0 else [(5, 10), (6, 11), (7, 10), (8, 11), (9, 10), (10, 11)]
        for x, y in wav:
            s.set(x, y, E)
    elif name == "tense":
        s.line(3, 5, 5, 4, E).line(10, 4, 12, 5, E)       # worried brows
        dot_eyes(s, 7)
        s.rect(5, 10, 6, 3, E).rect(6, 11, 4, 1, P.linen[3]).set(7, 11, E).set(8, 11, P.linen[3])
        drop(s, 13, 3 + f)
    elif name == "angry":
        s.line(3, 4, 6, 6, E).line(9, 6, 12, 4, E)        # V brows
        s.rect(4, 7, 2, 1, E).rect(10, 7, 2, 1, E)
        frown(s, 11)
        v = P.coral[1]                                     # anger vein
        s.set(12, 1, v).set(14, 1, v).set(13, 2, v).set(12, 3, v).set(14, 3, v)
        if f:
            s.rect(0, 0, 2, 1, P.linen[2]).set(1, 1, P.linen[2]).rect(14, 5, 2, 1, P.linen[2])
    elif name == "sad":
        s.line(3, 5, 5, 4, E).line(10, 4, 12, 5, E)
        s.rect(4, 7, 2, 1, E).rect(10, 7, 2, 1, E)
        frown(s, 11)
        drop(s, 4, 9 + f * 2)
    elif name == "dazed":
        for x in (3, 9):                                  # spiral eyes
            s.hline(x, x + 3, 5, E).vline(x + 3, 5, 8, E).hline(x + 1, x + 3, 8, E).set(x + 1, 7, E)
            if f:
                s.set(x + 1, 7, None).set(x + 2, 6, E)
        s.set(6, 11, E).set(7, 10, E).set(8, 11, E).set(9, 10, E)
        sparkle(s, 13 if f else 2, 1, True, M[4])
    elif name == "scared":
        dot_eyes(s, 7)
        s.set(4, 7, E).set(10, 7, E)
        s.rect(6, 10, 4, 3, E).rect(7, 11, 2, 1, MOUTH)
        drop(s, 13, 2)
        if f:                                              # shiver
            out = Sprite(SIZE, SIZE)
            out.blit(s, 1, 0)
            s = out
    elif name == "asleep":
        for x in (4, 10):                                  # peaceful closed eyes: little arcs
            s.set(x - 1, 7, P.metal[0]).hline(x, x + 1, 8, P.metal[0]).set(x + 2, 7, P.metal[0])
        s.hline(7, 8, 11, P.metal[1])                     # a small, soft mouth
        s.set(3, 9, P.hair_pink[3]).set(12, 9, P.hair_pink[3])   # sleepy blush
        z = P.linen[3]                                      # a z drifting up
        if f == 0:
            s.hline(11, 13, 1, z).set(12, 2, z).hline(11, 13, 3, z)
        else:
            s.hline(12, 15, 0, z).set(14, 1, z).set(13, 2, z).hline(12, 15, 3, z)
    return s


def frames(name: str) -> list[Sprite]:
    return [draw(name, f) for f in (0, 1)]


def build():
    out = {}
    cols = 8
    sheet = Sprite(cols * 22 + 4, 4 * 22 + 4, fill=P.linen[2])
    for i, (k, _, tint) in enumerate(EMOTIONS):
        fr = frames(k)
        out[f"mood_{k}"] = Anim(fr, 400)
        for j, f in enumerate(fr):
            x, y = 4 + (i % cols) * 22, 4 + (i // cols) * 44 + j * 22
            sheet.ellipse(x + 7.5, y + 7.5, 9.5, 9.5, P.linen[3])
            sheet.ellipse(x + 7.5, y + 7.5, 8.5, 8.5, tint)
            sheet.blit(f, x, y)
    out["mood_icons"] = sheet
    return out
