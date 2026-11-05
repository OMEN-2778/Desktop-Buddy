"""草帽湾 (summer map, owner 2026-11-04): Buddy's own beach stall, 蕾拉妮's flower stall, and the
item icons for what she gathers in the sea and sells at the stall.

- hero_stall: thatched straw roof with a fringe, a little flag with a straw hat on it (so the player
  can tell at a glance the stall is hers), wooden counter with a coral/white striped skirt, a menu
  slate. Three display spots on the counter top are left empty: the game draws the goods there.
- flower_stall: bamboo frame, palm-frond roof, leis hanging across the front, buckets of plumeria.
- farm_icon_<item>: 16x16 icons in the farm UI style (they join the 丢丢平板 仓库 by name).
Light from the top-left; every part outlined in the darkest shade of its own ramp."""

from pixelkit import P, Sprite

PREVIEW_SCALE = 6

STRAW = P.oat          # thatch
WOOD = P.oak
BAMBOO = P.wood
FLAG = P.porcelain
CLOTH_A = P.coral
CLOTH_B = P.porcelain


def hero_stall() -> Sprite:
    W, H = 52, 50
    s = Sprite(W, H)
    base = H - 1
    # posts
    for x in (5, W - 7):
        s.rect(x, 14, 2, base - 14 + 1, WOOD[2]).vline(x + 1, 14, base, WOOD[1]).vline(x, 14, base, WOOD[3])
    # counter: top board + front with striped skirt
    top = base - 17
    s.rect(2, top, W - 4, 3, WOOD[3]).hline(2, W - 3, top, WOOD[-1]).hline(2, W - 3, top + 2, WOOD[1])
    s.hline(2, W - 3, top - 1, WOOD[0]).vline(1, top - 1, top + 2, WOOD[0]).vline(W - 2, top - 1, top + 2, WOOD[0])
    front = top + 3
    s.rect(3, front, W - 6, base - front + 1, WOOD[1])
    for x in range(4, W - 4):
        stripe = ((x - 4) // 5) % 2
        R = CLOTH_A if stripe == 0 else CLOTH_B
        for y in range(front, base - 1):
            s.set(x, y, R[3] if y < front + 2 else R[2])
        s.set(x, base - 1, R[1])                          # hem shadow
    # scalloped hem
    for x in range(4, W - 4, 5):
        s.set(x + 2, base, (CLOTH_A if ((x - 4) // 5) % 2 == 0 else CLOTH_B)[1])
    s.vline(3, front, base, WOOD[0]).vline(W - 4, front, base, WOOD[0])
    # thatched roof: a wide straw hip with a fringe
    for k in range(10):
        y = 6 + k
        hw = 14 + k * 1.3
        cx = W // 2
        for x in range(int(cx - hw), int(cx + hw) + 1):
            if 0 <= x < W:
                shade = STRAW[3] if k < 3 else STRAW[2]
                if (x + k) % 4 == 0:
                    shade = STRAW[1] if k > 4 else STRAW[2]
                if x - (cx - hw) < 2:
                    shade = STRAW[-1] if k < 6 else STRAW[3]
                s.set(x, y, shade)
    for x in range(0, W):                                 # ragged fringe
        if x % 2 == 0:
            s.set(x, 16, STRAW[1])
        if x % 3 == 0:
            s.set(x, 17, STRAW[1])
    s.hline(10, W - 11, 5, STRAW[0])
    for k in range(10):                                   # roof outline sides
        hw = 14 + k * 1.3
        s.set(int(W // 2 - hw) - 1 if int(W // 2 - hw) > 0 else 0, 6 + k, STRAW[0])
        s.set(min(W - 1, int(W // 2 + hw) + 1), 6 + k, STRAW[0])
    # flag pole + flag with a straw hat on it
    px = W // 2 + 9
    s.vline(px, 0, 6, WOOD[1])
    s.rect(px + 1, 0, 9, 6, FLAG[3]).hline(px + 1, px + 9, 0, FLAG[-1]).hline(px + 1, px + 9, 5, FLAG[1]).vline(px + 9, 0, 5, FLAG[1])
    hat = [(px + 4, 2), (px + 5, 2), (px + 6, 2), (px + 3, 3), (px + 4, 3), (px + 5, 3), (px + 6, 3), (px + 7, 3)]
    for x, y in hat:
        s.set(x, y, P.mustard[3])
    s.set(px + 4, 3, P.coral[2]); s.set(px + 5, 3, P.coral[2]); s.set(px + 6, 3, P.coral[2])   # hat band
    s.set(px + 2, 4, P.mustard[2]); s.set(px + 8, 4, P.mustard[2])
    for x in range(px + 2, px + 9):
        s.set(x, 4, P.mustard[2])
    # menu slate leaning on the left post
    s.rect(7, top - 11, 9, 10, P.slate[1]).rect(8, top - 10, 7, 8, P.slate[0])
    s.hline(9, 13, top - 8, P.porcelain[3]).hline(9, 12, top - 6, P.porcelain[2]).hline(9, 13, top - 4, P.porcelain[2])
    s.set(14, top - 6, P.coral[3])
    # string of little shells under the roof
    for x in range(9, W - 9, 4):
        s.set(x, 18, P.reef_pearl[3] if hasattr(P, 'reef_pearl') else P.porcelain[3])
    return s


def flower_stall() -> Sprite:
    W, H = 50, 48
    s = Sprite(W, H)
    base = H - 1
    G = P.leaf
    for x in (4, W - 6):                                  # bamboo poles with nodes
        s.rect(x, 12, 2, base - 12 + 1, BAMBOO[3]).vline(x + 1, 12, base, BAMBOO[2])
        for y in range(15, base, 6):
            s.hline(x, x + 1, y, BAMBOO[1])
    # palm-frond roof: drooping leaves
    for k in range(9):
        y = 4 + k
        hw = 12 + k * 1.5
        cx = W // 2
        for x in range(int(cx - hw), int(cx + hw) + 1):
            if 0 <= x < W:
                c = G[3] if k < 3 else G[2]
                if (x * 3 + k) % 5 == 0:
                    c = G[1]
                if x - (cx - hw) < 2:
                    c = G[4] if hasattr(G, '__len__') and len(G) > 4 else G[3]
                s.set(x, y, c)
    for x in range(0, W, 2):                              # leaf tips hanging down
        L = 13 + (x * 7) % 4
        s.vline(x, 12, L, G[1])
    s.hline(13, W - 14, 3, G[0])
    # counter (bamboo slats) + front
    top = base - 15
    s.rect(2, top, W - 4, 2, BAMBOO[3]).hline(2, W - 3, top, BAMBOO[-1]).hline(2, W - 3, top - 1, BAMBOO[0])
    for x in range(3, W - 3):
        for y in range(top + 2, base + 1):
            s.set(x, y, BAMBOO[2] if (x // 3) % 2 == 0 else BAMBOO[3])
        s.set(x, base, BAMBOO[1])
    s.vline(2, top + 2, base, BAMBOO[0]).vline(W - 3, top + 2, base, BAMBOO[0])
    # leis hanging across the front (two swags), flowers in pink / yellow / white
    flowers = [P.blossom, P.mustard, P.porcelain, P.coral]
    for row, (y0, sag) in enumerate(((16, 5), (20, 4))):
        for x in range(6, W - 6):
            t = (x - 6) / (W - 13)
            y = int(y0 + sag * 4 * t * (1 - t))
            R = flowers[(x // 2 + row) % len(flowers)]
            s.set(x, y, R[3])
            if x % 2 == 0:
                s.set(x, y + 1, R[2])
    # buckets of plumeria on the counter
    for bx in (8, 22, 36):
        s.rect(bx, top - 5, 7, 5, P.steel[2]).hline(bx, bx + 6, top - 5, P.steel[3]).vline(bx + 6, top - 5, top - 1, P.steel[1])
        for i, (fx, fy) in enumerate(((1, -8), (4, -9), (2, -10), (5, -7), (0, -6))):
            R = flowers[(i + bx) % len(flowers)]
            s.set(bx + fx, top + fy, R[3]).set(bx + fx + 1, top + fy, R[2]).set(bx + fx, top + fy + 1, R[2])
            s.set(bx + fx + 1, top + fy + 1, P.mustard[3])
        s.vline(bx + 2, top - 6, top - 5, G[2]).vline(bx + 4, top - 7, top - 5, G[2])
    return s


# ---------------------------------------------------------------- 16x16 item icons
def g(rows, legend):
    return Sprite.from_grid("\n".join(r.ljust(16, ".") for r in rows), legend)


def ramp(R, o="o", d="d", m="m", l="l", h="h"):
    return {o: R[0], d: R[1], m: R[2], l: R[3], h: R[4] if len(R) > 4 else R[3]}


def seaweed():
    return g(["................", ".....o..........", "....omo.....o...", "....oml....omo..", ".....oml..omlo..",
              "......om..oml...", ".....oml..om....", "....omlo.omlo...", "....oml..oml..o.", ".....om.oml..omo",
              ".....oml.om..oml", "......om.oml.om.", ".....oml.om.oml.", ".....om..om.om..", "....odo.odo.odo.",
              "................"], {**ramp(P.leaf), })


def fish():
    return g(["................", "................", "................", "......oooo......", "....oollllo...o.",
              "...ollhllmlo.omo", "..olhwlmmmmloomo", "..oliKlmmmmmmmo.", "..olllmmmmdmmmo.", "...ommmmmdddoomo",
              "....oodddddo.omo", "......oooo....o.", "................", "................", "................",
              "................"], {**ramp(P.reef_blue), "w": P.porcelain[-1], "K": P.ink[0], "i": P.porcelain[-1]})


def shrimp():
    return g(["................", "...o............", "....o...........", ".....o..oooo....", "......oollllo...",
              ".....olhlmmmlo..", "....olllmmmmmlo.", "....oKlmmdmmmmo.", ".....oommdmmmo..", ".......ommmdmo..",
              "........oommo...", ".......omdoo....", "......omdo......", "......ooo.......", "................",
              "................"], {**ramp(P.reef_orange), "K": P.ink[0]})


def crab():
    return g(["................", "................", "..oo........oo..", ".olmo......omlo.", ".omdo......odmo.",
              "..oo..oKoK..oo..", "...o.ooooooo.o..", "....ollhlllmo...", "...olhlllmmmmo..", "...ollmmmmmmdo..",
              "..o.ommmmmmdo.o.", ".o..oo.oo.oo..o.", "................", "................", "................",
              "................"], {**ramp(P.reef_red), "K": P.ink[0]})


def pearl():
    """A round pearl sitting in a half-open pink clam."""
    return g(["................", "................", "................", "......oooo......", ".....ohhllo.....",
              "....ohhlllmo....", "....ohllllmo....", "....olllmmmo....", ".....ommmmo.....", "..ppppooooopp...",
              ".pPPPPPPPPPPPp..", ".pPqPPqPPqPPPp..", "..pPPPPPPPPPp...", "...ppppppppp....", "................",
              "................"], {"o": P.reef_pearl[0], "m": P.reef_pearl[2], "l": P.reef_pearl[3], "h": P.porcelain[-1],
                                   "p": P.blossom[0], "P": P.blossom[3], "q": P.blossom[2]})


def shell():
    return g(["................", "................", "................", ".......oo.......", "......ollo......",
              ".....ollllo.....", "....olhlmlmo....", "...olhlmlmlmo...", "...oldlmlmlmo...", "..olhldlmldlmo..",
              "..oldldlmldldo..", "...ommmmmmmmo...", "....oooddooo....", "......oddo......", ".......oo.......",
              "................"], ramp(P.blossom))


def seaglass():
    return g(["................", "................", "................", "................", ".......ooo......",
              ".....oollmo.....", "....olhllmmo....", "...olhlllmmmo...", "...ollllmmmdo...", "....olllmmddo...",
              ".....ommmddo....", "......ooooo.....", "................", "................", "................",
              "................"], ramp(P.mint))


def coconut():
    return g(["................", "................", "..........ll....", ".........lml....", "....oooooom.....",
              "...odmmmmdoo....", "..odmlmmmmddo...", "..omlhmmmmmdo...", "..ommmmmKmmdo...", "..ommmKmmKmdo...",
              "..oddmmmmmddo...", "...oddddddd o...", "....ooooooo.....", "................", "................",
              "................"], {**ramp(P.walnut), "K": P.walnut[0], "l": P.leaf[2], " ": P.walnut[0]})


# ---- products (served at the stall)
def coconut_water():
    return g(["................", "...........o....", "..........oko...", ".........oko....", "....ooooook.....",
              "...oWWWWWWoo....", "..odmmmmmmddo...", "..omlhmmmmmdo...", "..ommmmmmmmdo...", "..ommmmmmmmdo...",
              "..oddmmmmmddo...", "...oddddddddo...", "....oooooooo....", "................", "................",
              "................"], {**ramp(P.walnut), "W": P.porcelain[-1], "k": P.coral[3]})


def bowl(fill, legend_fill, garnish=None):
    rows = ["................", "................", "................", "................", fill[0], fill[1],
            "..oBBBBBBBBBBo..", "..obbbbbbbbbbo..", "...obbbbbbbbo...", "....obbbbbbo....", ".....oooooo.....",
            "................", "................", "................", "................", "................"]
    leg = {"o": P.porcelain[0], "B": P.porcelain[3], "b": P.porcelain[2]}
    leg.update(legend_fill)
    return g(rows, leg)


def seaweed_salad():
    return bowl(["....lmlmlmlm....", "...mlmrmlmlmr..."], {"l": P.leaf[3], "m": P.leaf[2], "r": P.coral[3]})


def salted_shrimp():
    return bowl(["....rRrRrRrR....", "...RrRwRrRrRwR.."], {"r": P.reef_orange[3], "R": P.reef_orange[2], "w": P.porcelain[-1]})


def seafood_stew():
    return bowl(["....cKcrlcrcK...", "...cyccrlcrcyc.."], {"c": P.mustard[3], "y": P.mustard[2], "r": P.reef_red[3], "l": P.leaf[3], "K": P.reef_blue[2]})


def fish_skewer():
    return g(["................", "................", "....ooooo.......", "...ollhlloo.....", "..olKlmmmmlo..oo",
              "..ommmmmmdmoodmo", "...odddddddooddo", "....ooooooo..oo.", "........w.......", ".......w........",
              "......w.........", ".....w..........", "....w...........", "...w............", "................",
              "................"], {**ramp(P.reef_brown if hasattr(P, 'reef_brown') else P.walnut), "K": P.ink[0], "w": P.wood[2]})


def spicy_crab():
    return bowl(["....oRoRRoRo....", "...RRpRRRpRRR..."], {"R": P.reef_red[3], "p": P.coral[2]})


def egg_pancake():
    return g(["................", "................", "................", "................", "................",
              "....oooooooo....", "...oyyYyyyyyo...", "..oyYlyylyyyyo..", "..oyyyyylyyGyo..", "..oyyGyyyyyyyo..",
              "...oyyyyyGyyo...", "....oooooooo....", "................", "................", "................",
              "................"], {"o": P.mustard[0], "y": P.mustard[3], "Y": P.mustard[-1], "l": P.porcelain[-1], "G": P.leaf[1]})


def cup(fill, top, straw=P.coral):
    rows = ["................", "..........s.....", ".........s......", "....oooooso.....", "...oTTTTTsTo....",
            "...oFFFFFFFo....", "...oFFFFFFFo....", "....oFFFFFo.....", "....oFFFFFo.....", "....oFFFFFo.....",
            ".....oFFFo......", ".....oFFFo......", ".....ooooo......", "................", "................",
            "................"]
    return g(rows, {"o": P.porcelain[0], "F": fill, "T": top, "s": straw[3]})


def juice():
    return cup(P.mustard[3], P.mustard[-1])


def milk_smoothie():
    return cup(P.blossom[3], P.porcelain[-1], P.mint)


def shave_ice():
    return g(["................", "......oooo......", "....oorRRroo....", "...orRRRRwRro...", "...oRRwRRRRRo...",
              "...oGGGGGGGGo...", "....oGgGGgGo....", "....oooooooo....", ".....oBBBBo.....", ".....oBbbBo.....",
              "......oBBo......", "......oBBo......", ".....oooooo.....", "................", "................",
              "................"], {"o": P.ink[0], "r": P.coral[2], "R": P.coral[3], "w": P.porcelain[-1], "G": P.leaf[3], "g": P.leaf[2],
                                    "B": P.porcelain[3], "b": P.porcelain[2]})


def shell_chime():
    return g(["................", ".....oooooo.....", "......owwo......", "......w..w......", ".....w....w.....",
              "....w......w....", "...w........w...", "...p...p....p...", "...l...m....g...", "..olo.omo..ogo..",
              "..olo.omo..ogo..", "...o...o....o...", "................", "................", "................",
              "................"], {"o": P.walnut[0], "w": P.wood[2], "p": P.porcelain[2], "l": P.blossom[3], "m": P.reef_pearl[3], "g": P.mint[3]})


def pearl_necklace():
    return g(["................", "..b..........b..", "..b..........b..", "...b........b...", "...b........b...",
              "....b......b....", "....b......b....", ".....bb..bb.....", ".......oo.......", "......ohlo......",
              "......olmo......", ".......oo.......", "................", "................", "................",
              "................"], {"b": P.blossom[3], "o": P.reef_pearl[0], "h": P.porcelain[-1], "l": P.reef_pearl[3], "m": P.reef_pearl[2]})


ICONS = {
    "seaweed": seaweed, "fish": fish, "shrimp": shrimp, "crab": crab, "pearl": pearl, "shell": shell,
    "seaglass": seaglass, "coconut": coconut,
    "coconut_water": coconut_water, "seaweed_salad": seaweed_salad, "fish_skewer": fish_skewer,
    "salted_shrimp": salted_shrimp, "spicy_crab": spicy_crab, "seafood_stew": seafood_stew,
    "egg_pancake": egg_pancake, "juice": juice, "milk_smoothie": milk_smoothie, "shave_ice": shave_ice,
    "shell_chime": shell_chime, "pearl_necklace": pearl_necklace,
}


def board():
    keys = list(ICONS)
    cols = 10
    s = Sprite(cols * 18 + 2, ((len(keys) + cols - 1) // cols) * 18 + 2 + 56)
    for i, k in enumerate(keys):
        s.blit(ICONS[k](), 2 + (i % cols) * 18, 2 + (i // cols) * 18)
    y = 2 + ((len(keys) + cols - 1) // cols) * 18
    s.blit(hero_stall(), 4, y)
    s.blit(flower_stall(), 70, y + 2)
    return s


def build():
    out = {"summer_stall_board": board(), "summer_hero_stall": hero_stall(), "summer_flower_stall": flower_stall()}
    out.update({f"farm_icon_{k}": f() for k, f in ICONS.items()})
    return out
