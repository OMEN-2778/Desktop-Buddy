"""草帽湾 图鉴, second batch (owner 2026-11-05: "double the dex; the new ones should not always be there:
sometimes, at night, in some weather, or very rare"). 33 new species in the reef.py style (fish() profiles,
shaded top-left, outlined in their own darkest shade). WHEN says when each one swims:
  day / night / rain / dawn (5-8h) / dusk (17-20h) / rare (some days) / vrare (a few days a season).
Placement (sea-local x, y) and dex page come from SPOTS; the sea animates them like every other swimmer.
"""
import math
import numpy as np
from pixelkit import P, Sprite
import reef as RF
from reef import fish, poly_mask, paint, grow, smooth_curve

Y, O, R, K, B, C, G, W, PU, PI, BR, LI = (P.reef_yellow, P.reef_orange, P.reef_red, P.reef_night, P.reef_blue, P.reef_cyan,
                                          P.reef_grey, P.reef_pearl, P.reef_purple, P.reef_pink, P.reef_brown, P.reef_lime)
OVAL_T = [(0, -2), (0.4, -5), (0.8, -4.5), (0.95, -2), (1, -1)]
OVAL_B = [(0, 2), (0.4, 5), (0.8, 4), (0.95, 2), (1, 0)]
DISC_T = [(0, -3), (0.3, -8), (0.7, -8), (0.92, -4), (1, -1)]
DISC_B = [(0, 3), (0.3, 8), (0.7, 7), (0.92, 3), (1, 0)]
LONG_T = [(0, -1.5), (0.5, -3), (0.85, -2.5), (1, -1)]
LONG_B = [(0, 1.5), (0.5, 2.5), (0.85, 2), (1, 0)]


# ------------------------------------------------------------------ fish-shaped species
def achilles_tang():
    def pat(t, v, x, y):
        if 0.12 < t < 0.3 and abs(v) < 0.45: return O          # the orange teardrop by the tail
        return None
    return fish(20, DISC_T, DISC_B, K, fin=K, tail=("lunate", 5, 10), pattern=pat,
                dorsal=[(0, 0), (0.1, 1.5), (0.8, 2), (0.9, 0), (1, 0)], anal=[(0, 0), (0.1, 1.5), (0.7, 1.5), (0.8, 0), (1, 0)], eye=(0.85, -0.3))


def sailfin_tang():
    def pat(t, v, x, y):
        if int(t * 12) % 2 == 0 and t < 0.85: return BR
        return Y if t > 0.85 else None
    return fish(18, DISC_T, DISC_B, Y, fin=BR, tail=("square", 4, 8), pattern=pat,
                dorsal=[(0, 0), (0.1, 5), (0.5, 7), (0.85, 3), (1, 0)], anal=[(0, 0), (0.1, 5), (0.5, 6), (0.8, 0), (1, 0)], eye=(0.84, -0.3))


def longnose_butterfly():
    s = fish(18, [(0, -3), (0.35, -7), (0.7, -6), (0.85, -2), (1, -0.5)], [(0, 3), (0.35, 7), (0.7, 5), (0.85, 1.5), (1, 0.5)], Y,
             fin=Y, tail=("square", 3, 6), pattern=lambda t, v, x, y: K if t > 0.7 and v < -0.1 else (W if t > 0.72 and v >= -0.1 else None),
             dorsal=[(0, 0), (0.1, 2), (0.6, 2), (0.7, 0), (1, 0)], anal=[(0, 0), (0.1, 2), (0.5, 2), (0.6, 0), (1, 0)], eye=(0.12, 0.35), eye_r=1)
    return s


def cleaner_wrasse():
    return fish(12, LONG_T, LONG_B, B, fin=B, tail=("round", 3, 4),
                pattern=lambda t, v, x, y: K if abs(v) < 0.28 and t > 0.08 else (W if v < -0.5 else None), pectoral=False, eye=(0.86, -0.2))


def yellowtail_coris():
    def pat(t, v, x, y):
        if t < 0.15: return Y
        if (x * 3 + y * 5) % 7 == 0: return C
        return None
    return fish(20, LONG_T, LONG_B, R, fin=O, tail=("round", 4, 5), pattern=pat, eye=(0.88, -0.2))


def goatfish():
    s = fish(20, [(0, -1.5), (0.5, -4), (0.85, -3), (1, -1)], [(0, 1.5), (0.5, 3.5), (0.85, 3), (1, 1)], W,
             fin=Y, tail=("fork", 5, 7), pattern=lambda t, v, x, y: Y if abs(v + 0.05) < 0.18 else None, eye=(0.84, -0.3))
    s.set(s.w - 3, s.h // 2 + 3, Y[3]).set(s.w - 4, s.h // 2 + 4, Y[3])          # the barbels
    return s


def domino():
    def pat(t, v, x, y):
        if abs(t - 0.5) < 0.09 and abs(v + 0.55) < 0.25: return W
        if abs(t - 0.86) < 0.05 and v < -0.6: return W
        return None
    return fish(14, [(0, -3), (0.3, -6.5), (0.7, -6.5), (0.92, -3), (1, -1)], [(0, 3), (0.3, 6.5), (0.7, 5.5), (0.92, 2.5), (1, 0)], K,
                fin=K, tail=("round", 3, 7), pattern=pat, eye=(0.84, -0.25), gill=0.0,
                dorsal=[(0, 0), (0.1, 1.5), (0.7, 1.5), (0.8, 0), (1, 0)], anal=[(0, 0), (0.1, 1.5), (0.6, 1.5), (0.7, 0), (1, 0)])


def flagtail():
    def tailbars(t, v, x, y):
        return K if t < 0.12 and abs(v) > 0.3 else None
    return fish(18, OVAL_T, OVAL_B, G, fin=G, tail=("fork", 6, 9), pattern=tailbars, eye=(0.84, -0.2), eye_r=2, scales=True)


def needlefish():
    s = fish(30, [(0, -1), (0.5, -2), (0.8, -1.5), (1, -0.5)], [(0, 1), (0.5, 2), (0.8, 1), (1, 0.5)], C,
             fin=C, tail=("fork", 4, 5), pattern=lambda t, v, x, y: W if v > 0.2 else None, eye=(0.75, -0.3), pectoral=False, gill=0.0)
    return s


def flying_fish():
    s = fish(18, OVAL_T, OVAL_B, B, fin=C, tail=("fork", 6, 9),
             pattern=lambda t, v, x, y: W if v > 0.25 else None, eye=(0.86, -0.2), pectoral=False)
    h = s.h // 2                                                                  # the big glassy "wings"
    for k in range(9):
        for j in range(k // 2 + 1):
            x, y = s.w - 10 - k, h - 2 - j
            if 0 <= y < s.h: s.set(x, y, C[3] if j else C[4])
    return s


def cornetfish():
    s = fish(34, [(0, -1), (0.4, -2), (0.7, -1.5), (0.8, -0.8), (1, -0.5)], [(0, 1), (0.4, 2), (0.7, 1.5), (0.8, 0.8), (1, 0.5)], G,
             fin=C, tail=("point", 6, 3), pattern=lambda t, v, x, y: C if (x // 3) % 3 == 0 and v < 0 else None, eye=(0.72, -0.3), pectoral=False, gill=0.0)
    return s


def hawkfish():
    def pat(t, v, x, y):
        if abs(t - 0.82) < 0.05: return O                                        # the arc behind the eye
        return R if (x + y) % 4 == 0 else None
    return fish(14, OVAL_T, OVAL_B, W, fin=R, tail=("square", 3, 6), pattern=pat,
                dorsal=[(0, 0), (0.1, 2.5), (0.7, 3), (0.8, 0), (1, 0)], eye=(0.86, -0.3))


def squirrelfish():
    return fish(18, OVAL_T, OVAL_B, R, fin=R, tail=("fork", 5, 9),
                pattern=lambda t, v, x, y: W if abs(v) in (0.3,) or (int(v * 6) % 2 == 0 and v > -0.4) and t < 0.8 else None,
                dorsal=[(0, 0), (0.1, 2), (0.7, 3), (0.8, 0), (1, 0)], eye=(0.85, -0.25), eye_r=2, scales=True)


def soldierfish():
    return fish(18, DISC_T, DISC_B, R, fin=R, tail=("fork", 5, 9), pattern=lambda t, v, x, y: O if v < -0.4 else None,
                eye=(0.85, -0.25), eye_r=2, scales=True, dorsal=[(0, 0), (0.1, 2), (0.6, 2), (0.7, 0), (1, 0)])


def cardinalfish():
    return fish(11, OVAL_T, OVAL_B, PI, fin=PI, tail=("fork", 3, 5),
                pattern=lambda t, v, x, y: R if abs(v) < 0.18 else None, eye=(0.82, -0.25), eye_r=1, pectoral=False)


def bigeye():
    return fish(18, DISC_T, DISC_B, R, fin=R, tail=("square", 4, 8), eye=(0.82, -0.2), eye_r=2,
                dorsal=[(0, 0), (0.1, 3), (0.7, 3), (0.8, 0), (1, 0)], anal=[(0, 0), (0.1, 3), (0.6, 3), (0.7, 0), (1, 0)])


def mullet():
    return fish(22, LONG_T, LONG_B, G, fin=G, tail=("fork", 5, 8),
                pattern=lambda t, v, x, y: G if int(v * 8) % 2 and v < 0.2 else (W if v >= 0.2 else None), eye=(0.88, -0.2), scales=True)


def milkfish():
    return fish(26, [(0, -1.5), (0.5, -4), (0.85, -3), (1, -1)], [(0, 1.5), (0.5, 3.5), (0.85, 2.5), (1, 0.5)], W,
                fin=G, tail=("fork", 8, 11), pattern=lambda t, v, x, y: G if v < -0.3 else None, eye=(0.88, -0.2))


def bluefin_trevally():
    def pat(t, v, x, y):
        if (x * 7 + y * 3) % 11 == 0 and v < 0.3: return K
        return None
    return fish(24, DISC_T, DISC_B, C, fin=B, tail=("lunate", 6, 11), pattern=pat, eye=(0.86, -0.2))


def mahimahi():
    s = fish(30, [(0, -1.5), (0.4, -4), (0.85, -7), (0.97, -6), (1, -3)], [(0, 1.5), (0.5, 4), (0.9, 4), (1, 2)], LI,
             fin=B, tail=("fork", 8, 12), pattern=lambda t, v, x, y: Y if v > 0.1 else (B if (x + y) % 5 == 0 else None),
             dorsal=[(0, 0), (0.05, 2), (0.95, 3), (1, 0)], eye=(0.9, -0.1))
    return s


def wahoo():
    def pat(t, v, x, y):
        if v < 0.2 and int(t * 16) % 2 == 0: return B
        return W if v >= 0.2 else None
    return fish(34, LONG_T, LONG_B, C, fin=B, tail=("lunate", 6, 10), pattern=pat, eye=(0.9, -0.2))


def masked_angel():
    def pat(t, v, x, y):
        if t > 0.75 and v < -0.2: return K                                      # the dark mask
        if v < -0.75: return K
        return None
    return fish(18, DISC_T, DISC_B, W, fin=K, tail=("square", 4, 8), pattern=pat,
                dorsal=[(0, 0), (0.1, 3), (0.6, 3), (0.7, 0), (1, 0)], anal=[(0, 0), (0.1, 3), (0.6, 3), (0.7, 0), (1, 0)], eye=(0.86, -0.3))


def tiger_shark():
    s = RF.whitetip()
    rng = np.random.default_rng(5)
    for x in range(22, 80, 4):                                                   # dark tiger bars on the back
        for y in range(s.h):
            c = s.px[y, x]
            if c[3] and y < s.h // 2 + 1:
                s.set(x, y, G[1]); s.set(x + 1, y, G[1]) if s.px[y, x + 1, 3] else None
                break
        for y in range(4, s.h // 2):
            if s.px[y, x, 3] and rng.random() < .5: s.set(x, y, G[1])
    return s


def hammerhead():
    s = RF.whitetip()
    h, w = s.h, s.w
    cy = h // 2
    nose = max(x for x in range(w) if s.px[cy, x, 3])
    for x in range(nose - 3, min(w, nose + 3)):                                   # the flat "hammer": a thin wing ahead of the eyes
        for y in (cy - 3, cy - 2):
            s.set(x, y, G[3] if y == cy - 3 else G[2])
        s.set(x, cy - 4, G[1]) if x > nose - 3 else None
    s.set(min(w - 1, nose + 2), cy - 2, K[0])
    return s


# ------------------------------------------------------------------ drawn by hand
def squid():
    s = Sprite(26, 12)
    for x in range(4, 22):                                                       # mantle, pointing back (left)
        hw = 1 + min(x - 4, 22 - x) * 0.35
        for y in range(round(6 - hw), round(6 + hw) + 1):
            s.set(x, y, PI[3] if y < 6 else PI[2])
        s.set(x, round(6 - hw) - 1, PI[1]).set(x, round(6 + hw) + 1, PI[1])
    for k in range(3): s.set(4 - k, 6 - k, PI[2]).set(4 - k, 6 + k, PI[2])      # fins
    for j in range(4):                                                           # arms trailing forward
        for x in range(22, 26): s.set(x, 4 + j * 2 - (1 if x > 24 and j % 2 else 0), PI[1] if j % 2 else PI[2])
    s.set(19, 5, K[0]).set(19, 6, W[4])
    return s


def spinner_dolphin():
    s = Sprite(40, 16)
    for x in range(5, 34):
        t = (x - 5) / 29
        top, bot = -4 * math.sin(math.pi * min(1, t * 1.1)) - 0.5, 3 * math.sin(math.pi * t) + 0.5
        for y in range(round(8 + top), round(8 + bot) + 1):
            v = (y - 8 - top) / max(1, bot - top)
            s.set(x, y, G[1] if v < 0.35 else G[2] if v < 0.7 else W[3])
    for x in range(34, 39): s.set(x, 9, G[2]).set(x, 10, W[2])                  # the long beak
    for pts in ([(20, 4), (23, 0), (25, 4)], [(5, 7), (0, 3), (2, 8), (0, 13), (5, 9)], [(24, 11), (21, 15), (26, 11)]):
        paint(s, poly_mask(40, 16, pts) & (s.px[..., 3] == 0), G[1])
    s.set(31, 7, K[0])
    return s


def whale_shark():
    s = Sprite(120, 34)
    for x in range(14, 112):
        t = (x - 14) / 98
        top = -9 * math.sin(math.pi * min(1, 0.15 + t * 0.85)) - 1
        bot = 7 * math.sin(math.pi * min(1, 0.1 + t * 0.9)) + 1
        for y in range(round(17 + top), round(17 + bot) + 1):
            v = (y - 17 - top) / max(1, bot - top)
            c = B[1] if v < 0.15 else B[2] if v < 0.62 else W[2]
            if v < 0.6 and ((x % 6 == 0 and y % 4 == 1) or (x % 6 == 3 and y % 4 == 3)): c = W[3]   # the pale spots
            s.set(x, y, c)
    for pts in ([(16, 15), (2, 2), (8, 2), (18, 13)], [(16, 19), (6, 28), (10, 28), (18, 20)], [(64, 8), (72, -1), (76, 8)], [(80, 23), (72, 33), (82, 24)]):
        paint(s, poly_mask(120, 34, pts) & (s.px[..., 3] == 0), B[1])
    for y in range(17, 22): s.set(111, y, B[0])                                  # the wide flat mouth
    s.set(106, 15, K[0])
    return s


def sunfish():
    s = Sprite(30, 44)
    for y in range(10, 34):
        for x in range(5, 26):
            d = ((x - 15) / 10.5) ** 2 + ((y - 22) / 12) ** 2
            if d <= 1:
                v = (y - 10) / 24
                c = G[3] if v < 0.25 else G[2] if v < 0.7 else W[2]
                if d > 0.84: c = G[1] if y > 16 else G[2]
                s.set(x, y, c)
    for pts, c in (([(13, 11), (15, 0), (18, 0), (19, 11)], G[2]), ([(13, 33), (15, 44), (18, 44), (19, 33)], G[1])):
        paint(s, poly_mask(30, 44, pts) & (s.px[..., 3] == 0), c)
    for y in range(13, 32):                                                       # the clavus: a wavy clipped tail
        x = 4 - (1 if (y // 3) % 2 else 0)
        s.set(x, y, G[2]).set(x + 1, y, G[1])
    s.set(22, 19, K[0]).set(22, 18, W[4]).set(25, 23, G[0]).set(19, 21, G[1]).set(19, 22, G[1])   # eye, mouth, gill slit
    return s


def grid(rows, colors):
    s = Sprite(max(len(r) for r in rows), len(rows))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in colors: s.set(x, y, colors[ch])
    return s


def seahorse():
    rows = ["....oo......",
            "...oHHo.....",
            "..oHHHhoooo.",
            "..oHEhhSSSSo",
            "..oHHhhoooo.",
            "...oHHho....",
            "...oHhhFo...",
            "..oHHhhFFo..",
            "..oHHhh.o...",
            "..oHhhho....",
            "...oHhho....",
            "...oHhho....",
            "....oHho....",
            "....oHho....",
            ".....oHo....",
            "..oo.oHo....",
            ".oHho.oHo...",
            ".oHo..oHo...",
            "..oHhhHo....",
            "...oooo....."]
    return grid(rows, {"o": Y[1], "H": Y[3], "h": Y[2], "S": Y[2], "E": K[0], "F": Y[4]})


def frogfish():
    s = Sprite(16, 14)
    for y in range(2, 14):
        for x in range(1, 15):
            if ((x - 8) / 7) ** 2 + ((y - 8) / 6) ** 2 <= 1:
                s.set(x, y, O[3] if (x * y) % 7 == 0 else O[2] if y < 10 else O[1])
    for x in (4, 11): s.set(x, 13, O[1]).set(x - 1, 13, O[1])                    # walking fins
    s.set(12, 5, K[0]).set(13, 3, O[3]).set(14, 2, O[4])                         # eye + the lure
    return s


def ribbon_eel():
    s = Sprite(36, 10)
    for x in range(36):
        y = 5 + round(math.sin(x * 0.35) * 2.5)
        s.set(x, y, B[2]).set(x, y + 1, B[3])
        if x % 2: s.set(x, y - 1, Y[3])                                           # the yellow dorsal frill
    s.set(35, 5 + round(math.sin(35 * 0.35) * 2.5) - 1, Y[4]).set(33, 4 + round(math.sin(33 * 0.35) * 2.5), K[0])
    return s


def oarfish():
    s = Sprite(90, 18)
    for x in range(90):
        y = 9 + round(math.sin(x * 0.12) * 3)
        for d in range(-1, 2): s.set(x, y + d, W[3] if d < 1 else G[3])
        s.set(x, y - 2, R[2] if x % 3 else R[3])                                  # the long red crest
    for k in range(5): s.set(88 - k, 9 + round(math.sin((88 - k) * 0.12) * 3) - 3 - k, R[3])
    s.set(86, 9 + round(math.sin(86 * 0.12) * 3), K[0])
    return s


def glass_shrimp():
    s = Sprite(10, 6)
    for x in range(1, 8): s.set(x, 3, C[3] if x % 2 else W[3])
    for x in range(2, 7): s.set(x, 2, W[4])
    s.set(8, 2, K[0]).set(9, 1, C[4]).set(9, 0, C[4]).set(0, 4, C[3])
    return s


# ------------------------------------------------------------------ catalogue
# key: (name, draw, when, page, sea-local x, y, line)
SPECIES = {
    'achilles_tang': ('阿基里斯刺尾鱼', achilles_tang, 'day', 1, 170, 120, '黑得发亮的刺尾鱼，尾巴前面点着一颗橘色的泪珠。'),
    'sailfin_tang': ('高鳍刺尾鲷', sailfin_tang, 'day', 1, 300, 110, '一下子把背鳍和臀鳍全竖起来，像撑开了一面帆。'),
    'longnose_butterfly': ('长吻蝴蝶鱼', longnose_butterfly, 'day', 1, 380, 135, '用长长的嘴伸进珊瑚缝里找吃的。'),
    'cleaner_wrasse': ('裂唇鱼', cleaner_wrasse, 'day', 1, 214, 146, '在大鱼身上跳来跳去，帮它们清理身体的小清洁工。'),
    'yellowtail_coris': ('黄尾龙', yellowtail_coris, 'day', 0, 90, 120, '红底蓝点，尾巴是黄色的，游起来一扭一扭。'),
    'goatfish': ('条纹羊鱼', goatfish, 'day', 0, 140, 150, '用下巴上的两根小须在沙子里翻东西。'),
    'domino': ('三点白', domino, 'day', 0, 120, 132, '黑黑小小的一条，背上的白点像骰子。'),
    'flagtail': ('夏威夷汤鲤', flagtail, 'day', 0, 160, 95, '大眼睛的银色小鱼，尾巴上有黑色的斜纹。'),
    'needlefish': ('颌针鱼', needlefish, 'day', 0, 330, 34, '细长得像一根针，贴着海面一闪而过。'),
    'cornetfish': ('烟管鱼', cornetfish, 'day', 2, 470, 120, '长长的一根，几乎是透明的，慢慢地漂。'),
    'hawkfish': ('弓纹鹰鱼', hawkfish, 'day', 1, 250, 156, '趴在珊瑚枝上一动不动，像在站岗。'),
    'squirrelfish': ('金鳞鱼', squirrelfish, 'night', 1, 280, 160, '白天躲在洞里，天黑才出来，眼睛又大又亮。'),
    'soldierfish': ('锯鳞鱼', soldierfish, 'night', 2, 420, 150, '一身红色的盔甲，夜里成群地巡逻。'),
    'cardinalfish': ('天竺鲷', cardinalfish, 'night', 0, 200, 110, '粉红色的小鱼，晚上从珊瑚缝里钻出来。'),
    'squid': ('夜里的小乌贼', squid, 'night', 0, 300, 90, '一会儿变红一会儿变白，像在打信号。'),
    'bigeye': ('大眼鲷', bigeye, 'night', 2, 520, 170, '眼睛占了半个脸，黑漆漆的海里也看得清。'),
    'glass_shrimp': ('玻璃虾', glass_shrimp, 'night', 0, 250, 166, '透明得几乎看不见，只有眼睛是两个小黑点。'),
    'mullet': ('鲻鱼', mullet, 'rain', 0, 100, 40, '下雨天成群游到水面，嘴巴一张一合地喝雨。'),
    'milkfish': ('遮目鱼', milkfish, 'rain', 2, 420, 60, '银光闪闪，雨点打下来的时候特别爱往上游。'),
    'bluefin_trevally': ('蓝鳍鲹', bluefin_trevally, 'rain', 2, 560, 90, '雨天的海水浑了，它趁机出来打猎。'),
    'mahimahi': ('鲯鳅', mahimahi, 'dusk', 3, 'S120', 60, '傍晚才靠近海湾，绿色和金色闪成一片。'),
    'wahoo': ('刺鲅', wahoo, 'dusk', 3, 'S260', 80, '游得飞快，一眨眼就从身边过去了。'),
    'spinner_dolphin': ('飞旋海豚', spinner_dolphin, 'dawn', 3, 'S60', 20, '清晨一群海豚游进海湾，有一只跳出水面转了个圈。'),
    'flying_fish': ('飞鱼', flying_fish, 'dawn', 0, 520, 30, '一下子跃出水面，张开大大的胸鳍滑了好远。'),
    'whale_shark': ('鲸鲨', whale_shark, 'vrare', 3, 'S340', 180, '比小船还大的鲸鲨慢慢游过，身上的白点像星星。'),
    'sunfish': ('翻车鱼', sunfish, 'rare', 3, 'S200', 250, '圆圆的一大片，晒着太阳似地侧着身子漂。'),
    'hammerhead': ('双髻鲨', hammerhead, 'rare', 3, 'S480', 300, '头像一把锤子，远远地绕了一圈就走了。'),
    'tiger_shark': ('虎鲨', tiger_shark, 'vrare', 3, 'S560', 420, '身上带着淡淡的条纹，在深处慢慢巡游。离远点。'),
    'seahorse': ('海马', seahorse, 'rare', 1, 350, 170, '用尾巴卷着海草，跟着水流轻轻晃。'),
    'frogfish': ('躄鱼', frogfish, 'rare', 2, 600, 190, '长得像一块海绵，头上还挂着一根小钓竿。'),
    'masked_angel': ('面罩神仙鱼', masked_angel, 'vrare', 2, 640, 200, '只在很深的礁石边出现，潜水的人一辈子也难见一次。'),
    'ribbon_eel': ('五彩鳗', ribbon_eel, 'rare', 2, 700, 210, '蓝色的身子，黄色的鼻子，从沙洞里探出一截。'),
    'oarfish': ('皇带鱼', oarfish, 'vrare', 3, 'S420', 560, '传说中的大鱼，银色的身子长长一条，头顶飘着红冠。'),
}
WHEN_TEXT = {'day': '白天', 'night': '夜里才有', 'rain': '下雨天才有', 'dawn': '清晨才有', 'dusk': '傍晚才有', 'rare': '偶尔出现', 'vrare': '极其罕见'}


def build():
    """A review sheet: every new species at 1x on a sea-blue strip, with its time tag."""
    items = [(k, v[1]()) for k, v in SPECIES.items()]
    pad, cols = 6, 6
    cw = max(s.w for _, s in items) // 2 + 30
    rows = [items[i:i + cols] for i in range(0, len(items), cols)]
    hs = [max(s.h for _, s in r) + pad * 2 for r in rows]
    sheet = Sprite(max(sum(max(70, s.w + pad) for _, s in r) for r in rows) + pad, sum(hs))
    sheet.rect(0, 0, sheet.w, sheet.h, P.sea[2])
    y = 0
    for r, h in zip(rows, hs):
        x = pad
        for k, s in r:
            sheet.blit(s, x, y + pad)
            x += max(70, s.w + pad)
        y += h
    return {"reef2_sheet": sheet}
