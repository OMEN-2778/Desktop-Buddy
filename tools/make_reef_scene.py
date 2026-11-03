"""Mock underwater scene with the reef.py v2 animals and corals (+ the seaweeds the
owner kept from sea_life.py), to judge the overall tropical-sea feel.
Usage: python3 tools/make_reef_scene.py [out.png] [scale=3]"""
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'art/src/concept')]
import numpy as np
from PIL import Image
from pixelkit import P, rgba
import reef as R
import sea_life as SL

W, H = 520, 300
SC = int(sys.argv[2]) if len(sys.argv) > 2 else 3


def rgb(c):
    return np.array(rgba(c)[:3], float)


stops = [(0, P.sea[4]), (70, P.sea[3]), (170, P.sea[2]), (300, P.sea[1])]
img = np.zeros((H, W, 3))
for y in range(H):
    for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            img[y] = rgb(c0) * (1 - t) + rgb(c1) * t
            break
# sun shafts
for x0, w in ((80, 22), (210, 14), (330, 26), (450, 12)):
    for y in range(0, 220):
        x = int(x0 + y * 0.35)
        a = 0.10 * (1 - y / 220)
        img[y, max(0, x):min(W, x + w)] = img[y, max(0, x):min(W, x + w)] * (1 - a) + 255 * a
canvas = Image.fromarray(img.astype(np.uint8)).convert('RGBA')

# sand floor + rocks
rnd = random.Random(3)
floor = [int(258 + 6 * math.sin(x / 37) + 4 * math.sin(x / 13)) for x in range(W)]
fl = Image.new('RGBA', (W, H))
px = fl.load()
for x in range(W):
    for y in range(floor[x], H):
        d = y - floor[x]
        c = P.sand[3] if d < 2 else P.sand[2] if d < 10 else P.sand[1]
        if d >= 2 and (x * 7 + y * 3) % 23 == 0:
            c = P.sand[3]
        px[x, y] = rgba(c)
canvas.alpha_composite(fl)


def put(spr, x, y_bottom=None, y=None, flip=False):
    im = (spr.flip_h() if flip else spr).to_image()
    if y is None:
        y = y_bottom - im.height
    canvas.alpha_composite(im, (int(x), int(y)))


def rock(cx, w, h):
    s = R.Sprite(w, h)
    m = R._blob(w, h * 2, w / 2, h, w / 2 - 1, h - 1, random.Random(cx), 0.12)[:h]
    R.body_shade(s, m, P.slate)
    return s


# back layer: rocks + tall corals
put(rock(40, 70, 34), 20, floor[50] + 4)
put(rock(300, 90, 40), 280, floor[320] + 4)
put(R.sea_fan(), 44, floor[60] - 22)
put(R.staghorn(), 300, floor[320] - 30)
put(R.tube_sponges(), 360, floor[370] - 2)
put(R.table_coral(), 150, floor[170] + 2)
put(SL.sargassum(), 470, floor[475] + 2)
put(SL.limu(), 250, floor[255] + 2)
# a dense reef band: corals clustered on and between the rocks
for k, (fn, x) in enumerate([(R.staghorn, 10), (R.brain_coral, 60), (R.soft_coral, 250), (R.tube_sponges, 140), (R.staghorn, 430),
                             (R.lettuce_coral, 470), (R.sea_fan, 228), (R.brain_coral, 390), (R.soft_coral, 330)]):
    spr = fn()
    put(spr, x, floor[min(W - 1, x + spr.w // 2)] + 3 - (k % 3) * 2)
# front layer
put(R.brain_coral(), 92, floor[100] + 3)
put(R.soft_coral(), 205, floor[215] + 3)
put(R.clown_home(), 410, floor[430] + 3)
put(R.lettuce_coral(), 120, floor[130] + 3)
put(R.bubble_coral(), 268, floor[275] + 3)
put(R.mushroom_coral(), 335, floor[340] + 2)
put(R.giant_clam(), 30, floor[40] + 3)
put(R.sea_star(), 180, floor[185] + 6)
put(R.nudibranch(), 390, floor[395] + 3)
put(SL.seagrass(), 2, floor[5] + 2)
put(SL.seagrass(1), 492, floor[495] + 2)
put(R.moray(), 300 + 46, floor[320] - 2 - 0)
# life
put(R.turtle(), 360, y=36)
put(R.manta(), 40, y=14)
put(R.bait_ball(), 200, y=40)
put(R.parrotfish(), 120, y=150, flip=True)
put(R.SCHOOLS['anthias'][1](), 230, y=150)
put(R.SCHOOLS['bluestripe'][1](), 410, y=110)
put(R.yellow_tang(), 70, y=200)
put(R.regal_tang(), 160, y=215, flip=True)
put(R.moorish_idol(), 250, y=190)
put(R.butterflyfish(), 330, y=208, flip=True)
put(R.flame_angel(), 470, y=215)
put(R.triggerfish(), 20, y=120)
put(R.pufferfish(), 470, y=160, flip=True)
put(R.boxfish(), 210, y=118)
put(R.octopus(), 150, floor[170] - 36)

out = canvas.resize((W * SC, H * SC), Image.NEAREST)
out.save(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / 'art/preview/concept/reef_scene.png'))
print(out.size)
