# App-Store-style posters (4:3 landscape) from trailer clip frames: soft gradient backdrop,
# headline + subline, the game shown as crisp, pixel-scaled cards with shadows and a zoom callout.
#   python3 tools/make_posters.py CLIP_DIR OUT_DIR
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CLIPS, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
M = json.loads((CLIPS / 'clips.json').read_text())
W, H = 2400, 1800
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
INK, SOFT = (36, 28, 58), (98, 90, 122)


def font(px, w='Black'): return ImageFont.truetype(NOTO.format(w), px, index=2)


def frame(name, i):
    return Image.open(CLIPS / 'clips' / name / f'{i:03d}.png').convert('RGBA'), M['clips'][name]['info'][i]


def view(name, i, pad=(0, 0, 0, 0)):
    """The game picture only (no menus), in screen pixels (2 per css px)."""
    im, info = frame(name, i); x, y, w, h = info['view']; l, t, r, b = pad
    return im.crop((int((x - l) * 2), int((y - t) * 2), int((x + w + r) * 2), int((y + h + b) * 2)))


def backdrop(c0, c1, blobs):
    yy, xx = np.mgrid[0:H, 0:W]; g = Image.fromarray(np.uint8(255 * np.clip((xx / W * .55 + yy / H * .45), 0, 1)))
    bg = Image.composite(Image.new('RGBA', (W, H), c1), Image.new('RGBA', (W, H), c0), g)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for (x, y, r, col) in blobs: d.ellipse([x - r, y - r, x + r, y + r], fill=col + (120,))
    bg.alpha_composite(layer.filter(ImageFilter.GaussianBlur(160)))
    return bg


def card(img, width, radius=34, border=10, angle=0):
    k = width / img.width
    im = img.resize((round(img.width * k), round(img.height * k)), Image.NEAREST if k >= 1.5 else Image.LANCZOS)
    w, h = im.width + 2 * border, im.height + 2 * border
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    c.paste(Image.new('RGBA', (w, h), (255, 255, 255, 255)), (0, 0), m)
    inner = Image.new('L', im.size, 0); ImageDraw.Draw(inner).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius - border, fill=255)
    c.paste(im, (border, border), inner)
    return c.rotate(angle, Image.BICUBIC, expand=True) if angle else c


def place(bg, c, cx, cy, shadow=70):
    x, y = int(cx - c.width / 2), int(cy - c.height / 2)
    sh = Image.new('RGBA', bg.size, (0, 0, 0, 0)); a = c.getchannel('A').point(lambda v: v * shadow // 255)
    sh.paste(Image.new('RGBA', c.size, (30, 20, 60, 255)), (x + 10, y + 34), a)
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(36))); bg.alpha_composite(c, (x, y))


def callout(bg, src, box, k, at, r, ring=(255, 255, 255)):
    """A round magnifier: src region `box` scaled k (nearest), centred at `at`, radius r."""
    z = src.crop(box); z = z.resize((z.width * k, z.height * k), Image.NEAREST)
    z = z.crop((z.width // 2 - r, z.height // 2 - r, z.width // 2 + r, z.height // 2 + r))
    m = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    c = Image.new('RGBA', (2 * r + 24, 2 * r + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.ellipse([0, 0, 2 * r + 23, 2 * r + 23], fill=ring + (255,)); c.paste(z, (12, 12), m)
    place(bg, c, *at, shadow=90)


def grad_text(bg, text, px, x, y, cols, anchor='mm', w='Black'):
    f = font(px, w); d = ImageDraw.Draw(bg); l, t, r, b = (int(v) for v in d.textbbox((x, y), text, font=f, anchor=anchor))
    m = Image.new('L', bg.size, 0); ImageDraw.Draw(m).text((x, y), text, font=f, anchor=anchor, fill=255)
    g = Image.linear_gradient('L').rotate(90).resize((max(1, r - l), max(1, b - t)))
    fill = Image.new('RGBA', bg.size, (0, 0, 0, 0)); seg = len(cols) - 1
    strip = Image.new('RGBA', (r - l, b - t))
    for i in range(seg):                                 # piecewise horizontal gradient
        a, c = cols[i], cols[i + 1]; x0, x1 = (r - l) * i // seg, (r - l) * (i + 1) // seg
        part = Image.composite(Image.new('RGBA', (x1 - x0, b - t), c + (255,)), Image.new('RGBA', (x1 - x0, b - t), a + (255,)), g.resize((x1 - x0, b - t)))
        strip.paste(part, (x0, 0))
    fill.paste(strip, (l, t)); bg.paste(fill, (0, 0), m)


def text(bg, s, px, x, y, col=INK, w='Black', anchor='mm'):
    ImageDraw.Draw(bg).text((x, y), s, font=font(px, w), fill=col, anchor=anchor)


def headline(bg, small, big, cols, sub, y=230):
    if small: text(bg, small, 64, W / 2, y - 110, SOFT, 'Bold')
    grad_text(bg, big, 150, W / 2, y + 10, cols)
    if sub: text(bg, sub, 50, W / 2, y + 140, SOFT, 'Medium')


def brand(bg, dark=False):
    text(bg, 'Desktop Buddy', 40, W / 2, H - 70, (255, 255, 255, 200) if dark else (120, 110, 150), 'Bold')


SUNSET, CANDY, SKY, FIRE, MINT, AURORA = [(255, 128, 171), (255, 196, 92)], [(255, 120, 180), (176, 120, 255), (110, 170, 255)], \
    [(92, 170, 255), (178, 140, 255)], [(255, 196, 70), (255, 110, 80)], [(70, 210, 170), (90, 170, 255)], \
    [(255, 120, 170), (255, 190, 90), (120, 220, 160), (100, 170, 255), (180, 130, 255)]

# 1 -- a little house on your desktop
bg = backdrop((255, 240, 236), (232, 226, 255), [(300, 1500, 500, (255, 190, 200)), (2100, 400, 520, (200, 200, 255))])
headline(bg, '', '一个小人，住在你的桌面上', SUNSET, '吃饭、睡觉、看电视、出门玩，TA 自己过日子')
im, info = frame('home_idle', 30); full = im.crop(im.getbbox())
place(bg, card(full, 1700), W / 2, 1110); brand(bg); bg.convert('RGB').save(OUT / '1-home.png')

# 2 -- dress-up: the studio, plus a line-up of outfits (dolls from tools/poster_dolls.js)
bg = backdrop((255, 236, 246), (226, 232, 255), [(2000, 1400, 520, (255, 190, 230)), (300, 300, 480, (190, 210, 255))])
headline(bg, '', '百变造型', CANDY, '发型、五官、衣服、饰品，颜色也能随便调')
im, info = frame('dressup', 20); studio = im.crop((164, 28, 1544, 1010))
place(bg, card(studio, 1080), 700, 1100)
for k in range(6):
    d = Image.open(CLIPS / 'dolls' / f'{k}.png').convert('RGBA'); d = d.resize((d.width * 12, d.height * 12), Image.NEAREST)
    cx, top = 1560 + (k % 3) * 300, 700 + (k // 3) * 440
    sh = Image.new('RGBA', bg.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - 110, top + d.height - 26, cx + 110, top + d.height + 14], fill=(60, 40, 90, 70))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); bg.alpha_composite(d, (cx - d.width // 2, top))
brand(bg); bg.convert('RGB').save(OUT / '2-style.png')

# 3 -- pets
bg = backdrop((255, 244, 228), (255, 228, 222), [(400, 400, 500, (255, 210, 150)), (2000, 1500, 520, (255, 180, 170))])
headline(bg, '还能领养', '一只宠物', FIRE, '趴沙发、蹲冰箱、钻花盆，还能抱起来撸')
house = view('cat_fridge', 30); place(bg, card(house, 1700), W / 2, 1120)
pt = M['clips']['cat_fridge']['info'][30]['pet']; vx, vy = M['clips']['cat_fridge']['info'][30]['view'][:2]
px, py = (pt[0] - vx) * 2, (pt[1] - vy) * 2 - 14
callout(bg, house, (int(px - 60), int(py - 80), int(px + 60), int(py + 40)), 5, (1980, 1400), 250)
brand(bg); bg.convert('RGB').save(OUT / '3-pet.png')

# 4 -- going out
bg = backdrop((228, 248, 242), (226, 238, 255), [(300, 1500, 520, (170, 235, 210)), (2100, 300, 520, (180, 210, 255))])
headline(bg, '出门逛逛', '公园  商场  码头  酒吧', MINT, '每个地方都有路人、小摊和偶遇')
for k, (n, ang, cx, cy) in enumerate([('place_mall', 5, 690, 1010), ('place_beach', -4, 1720, 1060), ('place_park', 0, 1200, 1290)]):
    place(bg, card(view(n, 20), 1150, angle=ang), cx, cy)
brand(bg); bg.convert('RGB').save(OUT / '4-places.png')

# 5 -- festivals (daytime ones, light backdrop)
bg = backdrop((255, 240, 246), (230, 240, 255), [(400, 1500, 520, (255, 200, 170)), (2000, 300, 540, (190, 220, 255)), (1200, 900, 420, (210, 245, 220))])
text(bg, f"{M['stats']['festivals']} 个节日", 64, W / 2, 120, SOFT, 'Bold')
grad_text(bg, '每个节日都不一样', 150, W / 2, 240, AURORA)
text(bg, '赛龙舟、甜品节、堆雪人、赏月……场景和玩法都会变', 50, W / 2, 370, SOFT, 'Medium')
for n, i, ang, cx, cy in [('fest_甜品节', 10, -5, 700, 1000), ('fest_雪人日', 10, 4, 1720, 1020), ('fest_端午节', 10, 0, 1200, 1300)]:
    place(bg, card(view(n, i), 1150, angle=ang), cx, cy)
brand(bg); bg.convert('RGB').save(OUT / '5-festivals.png')

# 6 -- chance cards
bg = backdrop((236, 244, 255), (240, 232, 255), [(2000, 400, 520, (190, 215, 255)), (300, 1500, 500, (220, 200, 255))])
text(bg, f"{M['stats']['cards']} 张", 64, W / 2, 120, SOFT, 'Bold')
grad_text(bg, '奇思妙想的机会卡', 150, W / 2, 240, SKY)
text(bg, '时不时冒出一件怪事，由你替 TA 拿主意', 50, W / 2, 370, SOFT, 'Medium')
place(bg, card(view('card', 20, (0, 0, 0, 0)), 1750), W / 2, 1110); brand(bg); bg.convert('RGB').save(OUT / '6-cards.png')
print('posters ->', OUT)
