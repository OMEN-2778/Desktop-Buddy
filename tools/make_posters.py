# App-Store-style posters (4:3 landscape) from trailer clip frames: soft gradient backdrop,
# headline + subline, the game shown as crisp, pixel-scaled cards with shadows and a zoom callout.
#   python3 tools/make_posters.py CLIP_DIR OUT_DIR
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import random

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


ART, STK = Path('art/out/concept'), CLIPS / 'stickers'


def sticker(bg, img, k, cx, cy, angle=0, rim=9):
    """A die-cut sticker: the sprite scaled k (nearest) with a white rim and a soft shadow."""
    im = img.convert('RGBA'); im = im.crop(im.getbbox()); im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    pad = rim + 4; c = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); c.alpha_composite(im, (pad, pad))
    a = c.getchannel('A').point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(2 * rim + 1)).filter(ImageFilter.GaussianBlur(1.2))
    base = Image.new('RGBA', c.size, (255, 255, 255, 0)); base.putalpha(a); base.alpha_composite(c)
    if angle: base = base.rotate(angle, Image.BICUBIC, expand=True)
    place(bg, base, cx, cy, shadow=60)


def pill(bg, s, px, cx, cy, col, angle=0):
    f = font(px, 'Bold'); w = int(ImageDraw.Draw(bg).textlength(s, font=f)) + px * 2; h = int(px * 2.1)
    c = Image.new('RGBA', (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([4, 4, w + 3, h + 3], h // 2, fill=(255, 255, 255, 255), outline=col + (255,), width=5)
    d.text((w / 2 + 4, h / 2 + 4), s, font=f, fill=col, anchor='mm')
    if angle: c = c.rotate(angle, Image.BICUBIC, expand=True)
    place(bg, c, cx, cy, shadow=45)


def lift(im, k=1.35):                                   # night scenes read dark on a light poster
    return ImageEnhance.Color(ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(k)).enhance(1.05)).enhance(1.15)


def scene(name, i, bright=1.0):                          # a place view without the side arrow buttons
    v = view(name, i); v = v.crop((40, 0, v.width - 40, v.height))
    return lift(v, bright) if bright != 1 else v


SUNSET, CANDY, SKY, FIRE, MINT, AURORA = [(255, 128, 171), (255, 196, 92)], [(255, 120, 180), (176, 120, 255), (110, 170, 255)], \
    [(92, 170, 255), (178, 140, 255)], [(255, 196, 70), (255, 110, 80)], [(70, 210, 170), (90, 170, 255)], \
    [(255, 120, 170), (255, 190, 90), (120, 220, 160), (100, 170, 255), (180, 130, 255)]

# 1 -- a little house on your desktop
bg = backdrop((255, 240, 236), (232, 226, 255), [(300, 1500, 500, (255, 190, 200)), (2100, 400, 520, (200, 200, 255))])
headline(bg, '', '一个小人，住在你的桌面上', SUNSET, '吃饭、睡觉、看电视、出门玩，TA 自己过日子')
im, info = frame('home_idle', 30); full = im.crop(im.getbbox())
place(bg, card(full, 1700), W / 2, 1110); brand(bg); bg.convert('RGB').save(OUT / '1-home.png')

# 2 -- dress-up: the studio, ringed by outfit stickers
bg = backdrop((255, 236, 246), (226, 232, 255), [(2000, 1400, 520, (255, 190, 230)), (300, 300, 480, (190, 210, 255))])
headline(bg, '', '百变造型', CANDY, '发型、五官、衣服、饰品，颜色也能随便调')
im, info = frame('dressup', 20); studio = im.crop((164, 28, 1544, 1010))
place(bg, card(studio, 1080), W / 2, 1110)
for k, (cx, cy, a) in enumerate([(300, 760, -6), (500, 1160, 5), (270, 1500, -3), (2100, 760, 6), (1900, 1160, -5), (2130, 1500, 4),
                                  (560, 260, 4), (1840, 260, -4), (760, 1620, -4), (1640, 1620, 5)]):
    sticker(bg, Image.open(STK / f'doll{k}.png'), 11 if k < 6 else 8, cx, cy, a)
brand(bg); bg.convert('RGB').save(OUT / '2-style.png')

# 3 -- pets: the house, cats and dogs in all sorts of poses, and Buddy holding the cat
bg = backdrop((255, 244, 228), (255, 228, 222), [(400, 400, 500, (255, 210, 150)), (2000, 1500, 520, (255, 180, 170))])
headline(bg, '还能领养', '一只宠物', FIRE, '12 种猫、12 种狗，会趴沙发、蹲冰箱、钻花盆，还能抱起来撸')
place(bg, card(view('cat_fridge', 30), 1400), W / 2, 1060)
sticker(bg, Image.open(STK / 'hold.png'), 13, 380, 1420, -4)
for k, (cx, cy, a) in enumerate([(330, 640, -5), (2080, 640, 5), (2120, 1080, -4), (820, 1580, 3), (1250, 1600, -3), (1680, 1580, 4),
                                 (2120, 1480, -5), (210, 250, 6), (2190, 250, -6), (300, 1020, 4)]):
    sticker(bg, Image.open(STK / f'pet{k}.png'), 7, cx, cy, a)
brand(bg); bg.convert('RGB').save(OUT / '3-pet.png')

# 4 -- going out
bg = backdrop((228, 248, 242), (226, 238, 255), [(300, 1500, 520, (170, 235, 210)), (2100, 300, 520, (180, 210, 255))])
headline(bg, '出门逛逛', '公园  商场  码头  酒吧', MINT, '每个地方都有路人、小摊和偶遇')
for k, (n, ang, cx, cy) in enumerate([('place_mall', 5, 690, 1010), ('place_beach', -4, 1720, 1060), ('place_park', 0, 1200, 1290)]):
    place(bg, card(scene(n, 20), 1150, angle=ang), cx, cy)
brand(bg); bg.convert('RGB').save(OUT / '4-places.png')

# 5 -- festivals: 怪兽夜, the disco and a park fair, festival props as stickers
bg = backdrop((255, 240, 246), (230, 240, 255), [(400, 1500, 520, (255, 200, 170)), (2000, 300, 540, (190, 220, 255)), (1200, 900, 420, (210, 245, 220))])
text(bg, f"{M['stats']['festivals']} 个节日", 64, W / 2, 120, SOFT, 'Bold')
grad_text(bg, '每个节日都不一样', 150, W / 2, 240, AURORA)
text(bg, '怪兽夜、跳舞日、甜品节、赛龙舟……场景和玩法都会变', 50, W / 2, 370, SOFT, 'Medium')
for n, i, b, ang, cx, cy in [('fest_怪兽夜', 10, 1.7, -5, 720, 900), ('fest_跳舞日', 40, 1.3, 4, 1700, 940), ('fest_甜品节', 10, 1.0, 0, 1200, 1300)]:
    place(bg, card(scene(n, i, b), 1100, angle=ang), cx, cy)
for n, k, cx, cy, a in [('pumpkin', 14, 230, 1180, -8), ('balloon_ghost', 14, 2170, 1230, 8), ('mirror_ball', 8, 2190, 560, 6), ('snowman_7', 8, 210, 560, -6),
                        ('dragon_boat_0', 5, 460, 1600, -3), ('fest_stall_mooncake', 5, 1960, 1580, 4), ('lantern_red', 14, 420, 1350, 6), ('balloon_heart', 14, 2000, 1330, -6),
                        ('bat', 10, 1230, 640, 0)]:
    sticker(bg, Image.open(ART / f'{n}.png'), k, cx, cy, a)
brand(bg); bg.convert('RGB').save(OUT / '5-festivals.png')

# 6 -- chance cards: one card in play, a cloud of other card titles around it
bg = backdrop((236, 244, 255), (240, 232, 255), [(2000, 400, 520, (190, 215, 255)), (300, 1500, 500, (220, 200, 255))])
text(bg, f"{M['stats']['cards']} 张", 64, W / 2, 120, SOFT, 'Bold')
grad_text(bg, '奇思妙想的机会卡', 150, W / 2, 240, SKY)
text(bg, '时不时冒出一件怪事，由你替 TA 拿主意', 50, W / 2, 370, SOFT, 'Medium')
place(bg, card(view('card', 20), 1250), W / 2, 1080)
titles = json.loads((STK / 'cards.json').read_text()); rnd = random.Random(7)
pick = [t for t in ['我的遥控器呢？', '一根头发的胜利', '剩饭选举', '煮饭按钮的沉默', '深夜重大问题', '撤回的诱惑', '失踪鞋员', '愿望博物馆',
                    '差评里的文学天赋', '椅子的可疑叫声', '给朋友当闹钟', '一分钱的胜利', '发错窗口', '梦里有你', '摆盘尊严', '宣布早睡'] if t in titles]
cols = [(236, 92, 140), (90, 140, 230), (240, 140, 60), (60, 170, 140), (150, 100, 220), (220, 90, 90)]
spots = [(300, 620), (330, 820), (280, 1020), (330, 1220), (300, 1420), (420, 1600), (2100, 620), (2070, 820), (2120, 1020), (2070, 1220),
         (2100, 1420), (1980, 1600), (820, 1590), (1200, 1620), (1580, 1590), (1200, 520)]
for k, (t, (cx, cy)) in enumerate(zip(pick, spots)):
    pill(bg, t, 40, cx, cy, cols[k % len(cols)], rnd.uniform(-5, 5))
brand(bg); bg.convert('RGB').save(OUT / '6-cards.png')
print('posters ->', OUT)
