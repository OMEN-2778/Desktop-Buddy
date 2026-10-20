"""Little pictures for the pick-a-thing panels (user): a cover for every book,
a card for every TV show, a box for every computer game, an app icon for
every phone game, and a plate or bowl for every dish.

Covers, cards, boxes and app icons are deliberately simple — a rectangle in
one colour ramp with one simple pattern — and the page matches them to
titles at random (by a hash of the title), so a few dozen designs cover
every title. Dishes are drawn per `look` (noodles, rice, cake…), each in a
couple of colour variants. All at 1 art pixel; the page shows them at 2x.
"""

from pixelkit import P, Sprite

PREVIEW_SCALE = 6
POR, INK, LIN = P.porcelain, P.ink, P.linen

# colour ramps for covers and cards: [dark, mid-dark, mid, light, highlight]
HUES = [P.blue, P.coral, P.mustard, P.green, P.terracotta, P.clay, P.sage, P.glass[0:5],
        P.hair_pink, P.birch, P.oak, ["#2b2348", "#4a3a78", "#7160a8", "#9d8fcc", "#cbc2ea"]]
PATTERNS = ["plain", "hstripes", "vstripes", "dots", "diamond", "band", "star", "circle",
            "grid", "chevron", "wave", "heart"]


def _shape(s, kind, x0, y0, w, h, c, c2):
    """One simple pattern inside the box (x0, y0, w, h)."""
    cx, cy = x0 + w // 2, y0 + h // 2
    if kind == "hstripes":
        for y in range(y0 + 1, y0 + h, 3):
            s.hline(x0, x0 + w - 1, y, c)
    elif kind == "vstripes":
        for x in range(x0 + 1, x0 + w, 3):
            s.vline(x, y0, y0 + h - 1, c)
    elif kind == "dots":
        for y in range(y0 + 1, y0 + h - 1, 3):
            for x in range(x0 + 1 + (y // 3) % 2, x0 + w - 1, 3):
                s.set(x, y, c)
    elif kind == "diamond":
        r = min(w, h) // 2 - 1
        for d in range(-r, r + 1):
            s.hline(cx - (r - abs(d)), cx + (r - abs(d)), cy + d, c)
        s.set(cx, cy, c2)
    elif kind == "band":
        s.rect(x0, cy - 2, w, 4, c).hline(x0, x0 + w - 1, cy - 2, c2)
    elif kind == "star":
        s.vline(cx, cy - 3, cy + 3, c).hline(cx - 3, cx + 3, cy, c)
        s.rect(cx - 1, cy - 1, 3, 3, c).set(cx, cy, c2)
    elif kind == "circle":
        s.ellipse(cx, cy, 3, 3, c).ellipse(cx - 1, cy - 1, 1, 1, c2)
    elif kind == "grid":
        for y in range(y0, y0 + h, 3):
            s.hline(x0, x0 + w - 1, y, c)
        for x in range(x0, x0 + w, 3):
            s.vline(x, y0, y0 + h - 1, c)
    elif kind == "chevron":
        for k in range(0, h - 2, 4):
            for i in range(w // 2 + 1):
                s.set(x0 + i, y0 + k + i // 2, c).set(x0 + w - 1 - i, y0 + k + i // 2, c)
    elif kind == "wave":
        for k in range(y0 + 1, y0 + h - 1, 4):
            for x in range(x0, x0 + w):
                s.set(x, k + (1 if (x // 2) % 2 else 0), c)
    elif kind == "heart":
        s.rect(cx - 3, cy - 2, 3, 3, c).rect(cx + 1, cy - 2, 3, 3, c)
        s.rect(cx - 3, cy, 7, 2, c).hline(cx - 2, cx + 2, cy + 2, c).set(cx, cy + 3, c)
        s.set(cx - 2, cy - 1, c2)


def _variants(n, seed):
    """n (hue, pattern) pairs spread over all combinations, in a fixed order."""
    pairs = [(h, p) for p in range(len(PATTERNS)) for h in range(len(HUES))]
    out, i = [], seed % len(pairs)
    while len(out) < n:
        out.append(pairs[i])
        i = (i + 37) % len(pairs)
    return out


def book(h, p):
    """A book cover, 16x20: spine on the left, pages showing at the right."""
    r = HUES[h]
    s = Sprite(16, 20)
    s.rect(0, 0, 15, 20, r[0]).rect(1, 1, 13, 18, r[2])
    s.rect(1, 1, 2, 18, r[1])                                   # spine
    s.vline(15, 1, 18, LIN[3]).vline(14, 19, 19, LIN[1])         # pages
    s.hline(3, 13, 1, r[3])                                      # top light
    _shape(s, PATTERNS[p], 4, 5, 9, 12, r[3], r[4])
    s.rect(5, 2, 7, 2, LIN[3])                                    # title plate
    return s


def tv(h, p):
    """A show card: a little screen, 20x15."""
    r = HUES[h]
    s = Sprite(20, 15)
    s.rect(1, 0, 18, 13, INK[1]).rect(0, 1, 20, 11, INK[1])
    s.rect(2, 2, 16, 9, r[2]).hline(2, 17, 2, r[3])
    _shape(s, PATTERNS[p], 3, 3, 14, 8, r[4], r[0])
    s.rect(8, 13, 4, 1, INK[1]).rect(6, 14, 8, 1, INK[0])         # stand
    return s


def game(h, p):
    """A game box / cartridge, 16x18 with a label."""
    r = HUES[h]
    s = Sprite(16, 18)
    s.rect(0, 1, 16, 17, r[0]).rect(1, 0, 14, 1, r[0])
    s.rect(1, 1, 14, 16, r[1]).rect(1, 1, 14, 2, r[2])
    s.rect(3, 4, 10, 10, LIN[3]).frame(3, 4, 10, 10, r[3])
    _shape(s, PATTERNS[p], 4, 5, 8, 8, r[2], r[0])
    for x in range(3, 13, 2):                                     # pins
        s.set(x, 16, P.mustard[3])
    return s


def app(h, p):
    """A phone app icon, 16x16 rounded square."""
    r = HUES[h]
    s = Sprite(16, 16)
    s.rect(0, 0, 16, 16, r[0]).rect(1, 1, 14, 14, r[2]).rect(1, 1, 14, 6, r[3])
    for x, y in ((0, 0), (15, 0), (0, 15), (15, 15)):
        s.set(x, y, None)
    for x, y in ((1, 1), (14, 1), (1, 14), (14, 14)):
        s.set(x, y, r[0])
    _shape(s, PATTERNS[p], 3, 3, 10, 10, LIN[3], r[0])
    return s


N_COVERS = 48


def covers(kind):
    """N_COVERS designs of one kind ("book", "tv", "game", "app")."""
    f = {"book": book, "tv": tv, "game": game, "app": app}[kind]
    seed = {"book": 0, "tv": 11, "game": 23, "app": 5}[kind]
    return [f(h, p) for h, p in _variants(N_COVERS, seed)]


# ---------------------------------------------------------------- dishes, 20x16
SOUPS = {"orange": P.mustard, "red": P.coral, "green": P.green, "clear": P.birch, "brown": P.clay}


def _plate(s, y=12):
    s.ellipse(9.5, y, 9, 2.5, POR[1]).ellipse(9.5, y - 0.5, 8, 2, POR[3])
    s.hline(4, 15, y + 2, POR[0])


def _bowl(s, rim=POR[3], band=P.blue[2]):
    s.ellipse(9.5, 6.5, 8, 2, POR[1])                              # rim
    for y in range(7, 14):
        k = (y - 7) * 0.6
        s.hline(int(2 + k), int(17 - k), y, rim)
    s.hline(4, 15, 10, band).hline(6, 13, 14, POR[0]).hline(7, 12, 15, POR[1])
    s.hline(2, 17, 7, POR[2])


def _fill_bowl(s, c_dark, c_light):
    s.ellipse(9.5, 6.5, 7, 1.5, c_dark).ellipse(9.5, 6, 5, 1, c_light)


def dish(look, v=0):
    s = Sprite(20, 16)
    soup = list(SOUPS.values())[v % len(SOUPS)]
    if look in ("noodles", "rice", "soup", "porridge", "salad", "curry", "hotpot"):
        if look == "hotpot":
            s.rect(1, 6, 18, 8, INK[1]).rect(2, 7, 16, 6, P.metal[2]).hline(0, 19, 6, INK[0])
            s.ellipse(9.5, 6, 8, 1.5, P.coral[2] if v % 2 == 0 else P.mustard[3])
            for x in (5, 9, 13):
                s.set(x, 5, P.coral[4]).set(x + 1, 6, P.green[3])
            s.rect(0, 9, 1, 2, INK[0]).rect(19, 9, 1, 2, INK[0])
            return s
        _bowl(s, band=[P.blue[2], P.coral[2], P.green[2]][v % 3])
        if look == "noodles":
            _fill_bowl(s, soup[2], soup[3])
            for x in range(4, 16, 2):
                s.set(x, 5 + (x // 2) % 2, P.mustard[4]).set(x + 1, 6, P.mustard[3])
            s.set(7, 5, P.green[3]).set(12, 5, P.green[3]).set(10, 4, P.coral[3])
        elif look == "rice":
            s.ellipse(9.5, 5, 6, 2.5, POR[3]).ellipse(8.5, 4, 3, 1, "#ffffff")
            s.set(12, 4, P.green[3]) if v % 2 else None
        elif look == "soup":
            _fill_bowl(s, soup[2], soup[4])
            for x, y in ((6, 6), (10, 5), (13, 6)):
                s.set(x, y, [P.green[3], P.coral[3], P.birch[4]][(x + v) % 3])
        elif look == "porridge":
            _fill_bowl(s, P.oat[3], P.oat[4])
            s.set(9, 5, P.coral[3]).set(11, 6, P.green[3])
        elif look == "salad":
            s.ellipse(9.5, 5.5, 6.5, 2, P.green[3])
            for x, y, c in ((6, 4, P.green[4]), (9, 4, P.coral[3]), (12, 5, P.mustard[4]), (11, 3, P.green[2]), (7, 6, P.coral[3])):
                s.set(x, y, c).set(x + 1, y, c)
        elif look == "curry":
            s.ellipse(9.5, 5.5, 6.5, 2, P.mustard[2]).ellipse(6.5, 5, 3, 1.5, POR[3])
            s.set(11, 5, P.coral[3]).set(13, 6, P.green[3]).set(10, 6, P.clay[2])
        return s
    if look in ("dumplings", "meat", "fish", "shrimp", "vegetables", "egg", "tofu", "sushi", "pasta",
                "pudding", "pancake", "taco", "sandwich", "skewer", "cookie", "cake", "pizza"):
        _plate(s)
        if look == "dumplings":
            for x in (4, 9, 14):
                s.ellipse(x, 9, 2.5, 2, POR[3]).hline(x - 2, x + 2, 11, POR[1]).set(x, 7, POR[1])
        elif look == "meat":
            c = [P.clay, P.terracotta, P.wood][v % 3]
            for x, y in ((6, 9), (10, 8), (13, 10), (8, 11)):
                s.rect(x - 1, y - 1, 3, 3, c[2]).set(x - 1, y - 1, c[3]).set(x + 1, y + 1, c[1])
            s.set(11, 10, P.green[3])
        elif look == "fish":
            s.ellipse(9, 9.5, 5, 2, P.metal[3] if v % 2 else P.coral[3]).set(5, 9, INK[0])
            s.rect(14, 8, 2, 4, P.metal[2] if v % 2 else P.coral[2]).hline(6, 12, 8, P.green[3])
        elif look == "shrimp":
            for x in (5, 10, 14):
                s.ellipse(x, 9.5, 2, 1.5, P.coral[3]).set(x - 1, 9, P.coral[4]).set(x + 2, 10, P.coral[2])
        elif look == "vegetables":
            for x, y in ((5, 9), (9, 8), (13, 9), (7, 11), (12, 11)):
                s.ellipse(x, y, 2, 1.5, P.green[2 + (x % 2)]).set(x, y - 1, P.green[4])
        elif look == "egg":
            s.ellipse(9.5, 9.5, 5, 2.5, "#ffffff").ellipse(9.5, 9.5, 2, 1.5, P.mustard[3]).set(9, 9, P.mustard[4])
            if v % 2:
                s.ellipse(5, 10, 1.5, 1, P.coral[3]).ellipse(14, 10, 1.5, 1, P.coral[3])
        elif look == "tofu":
            s.ellipse(9.5, 10, 7, 2, P.coral[2])
            for x, y in ((5, 8), (9, 9), (13, 8), (11, 10)):
                s.rect(x, y, 3, 2, POR[3]).set(x, y, "#ffffff")
            s.set(7, 10, P.green[3]).set(15, 10, P.green[3])
        elif look == "sushi":
            for x in (3, 8, 13):
                s.rect(x, 8, 4, 3, POR[3]).rect(x, 7, 4, 2, [P.coral[3], P.mustard[4], P.coral[2]][(x + v) % 3]).hline(x, x + 3, 9, INK[1])
        elif look == "pasta":
            s.ellipse(9.5, 9.5, 6, 2.5, P.mustard[4])
            for x in range(5, 15, 2):
                s.set(x, 9 + (x // 2) % 2, P.mustard[3])
            s.ellipse(9.5, 9, 2.5, 1.5, P.coral[2] if v % 2 == 0 else P.green[3]).set(9, 7, P.green[3])
        elif look == "pudding":
            s.rect(6, 6, 8, 5, P.mustard[4]).rect(7, 5, 6, 1, P.mustard[4]).rect(6, 5, 8, 2, P.clay[2]).set(9, 3, P.coral[3]).set(9, 4, P.green[3])
        elif look == "pancake":
            for y in (10, 8, 6):
                s.ellipse(9.5, y, 6, 1.5, P.birch[2]).hline(4, 15, y, P.birch[3])
            s.rect(8, 4, 3, 2, P.mustard[4]).vline(5, 6, 10, P.clay[2]).vline(14, 7, 9, P.clay[2])
        elif look == "taco":
            s.ellipse(9.5, 9, 7, 3, P.mustard[3]).ellipse(9.5, 8, 6, 2, P.green[3])
            s.set(7, 7, P.coral[3]).set(11, 7, P.coral[3]).set(9, 6, P.mustard[4]).hline(3, 16, 11, P.mustard[2])
        elif look == "sandwich":
            for x0 in (3, 10):
                s.rect(x0, 6, 7, 2, P.birch[4]).rect(x0, 8, 7, 1, P.green[3]).rect(x0, 9, 7, 1, P.coral[3]).rect(x0, 10, 7, 2, P.birch[3])
        elif look == "skewer":
            for x0 in (5, 12):
                s.line(x0 - 3, 12, x0 + 3, 2, P.birch[2])
                for k in range(3):
                    s.rect(x0 - 2 + k * 2 - 1, 9 - k * 3, 3, 2, [P.clay[2], P.green[3], P.coral[3]][(k + v) % 3])
        elif look == "cookie":
            for x, y in ((6, 9), (13, 9), (9.5, 7)):
                s.ellipse(x, y, 3, 2, P.birch[3]).set(int(x), int(y), P.wood[1]).set(int(x) + 1, int(y) + 1, P.wood[1])
        elif look == "cake":
            s.rect(5, 5, 10, 6, P.birch[4]).rect(5, 7, 10, 1, P.coral[3] if v % 2 == 0 else P.wood[2]).rect(5, 5, 10, 1, "#ffffff")
            s.ellipse(10, 3.5, 1.5, 1.5, P.coral[2]).set(10, 2, P.green[3])
        elif look == "pizza":
            s.ellipse(9.5, 9, 7.5, 3, P.mustard[2]).ellipse(9.5, 9, 6.5, 2.2, P.mustard[4])
            for x, y in ((6, 8), (10, 10), (13, 8), (9, 7)):
                s.set(x, y, P.coral[2]).set(x + 1, y, P.coral[2])
            s.set(8, 10, P.green[3])
        return s
    if look == "buns":
        s.rect(1, 9, 18, 5, P.birch[2]).hline(1, 18, 9, P.birch[3]).hline(1, 18, 13, P.birch[1])
        for x in (6, 13):
            s.ellipse(x, 7.5, 3.5, 2.5, "#ffffff").set(x, 6, POR[1]).set(x - 1, 7, POR[2])
        return s
    if look == "bread":
        s.ellipse(9.5, 9, 8, 4, P.birch[2]).ellipse(9.5, 8, 7, 3, P.birch[3])
        for x in (6, 9, 12):
            s.line(x, 7, x + 2, 9, P.birch[1])
        return s
    if look == "icecream":
        s.ellipse(9.5, 5, 4, 3, [P.hair_pink[3], P.mustard[4], P.green[4]][v % 3]).set(9, 3, "#ffffff")
        for y in range(8, 15):
            s.hline(6 + (y - 8) // 2, 13 - (y - 8) // 2, y, P.birch[3] if y % 2 else P.birch[2])
        return s
    if look == "drink":
        c = [P.wood[2], P.coral[3], P.green[3], P.mustard[3]][v % 4]
        s.rect(5, 4, 9, 11, POR[3]).rect(6, 5, 7, 8, c).hline(6, 12, 5, POR[2] if v else c)
        s.rect(14, 7, 2, 4, POR[2]).set(15, 8, None).set(15, 9, None) if v == 0 else s.line(11, 0, 9, 5, P.coral[2])
        if v == 0:
            s.set(8, 2, POR[2]).set(9, 1, POR[2]).set(10, 2, POR[2])
        return s
    if look == "burger":
        s.ellipse(9.5, 5, 7, 3, P.birch[2]).rect(3, 7, 14, 1, P.green[3]).rect(3, 8, 14, 2, P.wood[1])
        s.rect(3, 10, 14, 1, P.mustard[3]).rect(3, 11, 14, 2, P.birch[2]).set(7, 4, P.birch[4]).set(11, 3, P.birch[4])
        return s
    s.rect(4, 4, 12, 8, P.mustard[3])                               # unknown look: a parcel of food
    return s


LOOKS = ["noodles", "rice", "curry", "soup", "porridge", "dumplings", "buns", "meat", "fish", "shrimp",
         "vegetables", "salad", "egg", "tofu", "hotpot", "skewer", "sushi", "pizza", "pasta", "bread",
         "cake", "cookie", "pudding", "icecream", "drink", "sandwich", "burger", "taco", "pancake"]


def dishes():
    """look -> [variants]"""
    return {k: [dish(k, v) for v in range(3)] for k in LOOKS}


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "items.png"
    rows = [covers("book")[:16], covers("tv")[:16], covers("game")[:16], covers("app")[:16],
            [d[0] for d in dishes().values()][:16], [d[0] for d in list(dishes().values())[16:]] + [d[1] for d in dishes().values()][:3]]
    sheet = Sprite(16 * 24, len(rows) * 24, fill="#eae6df")
    for j, row in enumerate(rows):
        for i, spr in enumerate(row):
            sheet.blit(spr, i * 24 + 2, j * 24 + 2)
    sheet.save(out, scale=PREVIEW_SCALE)
