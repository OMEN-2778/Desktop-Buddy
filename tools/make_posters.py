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
headline(bg, '一个小人住在你的桌面上', '桌面小屋', [(238, 70, 120), (150, 80, 230)], '吃饭睡觉样样精通……')
im, info = frame('home_idle', 30); full = im.crop(im.getbbox())
place(bg, card(full, 1700, border=0, radius=28), W / 2, 1110); brand(bg); bg.convert('RGB').save(OUT / '1-home.png')

# 2 -- dress-up: the studio, ringed by outfit stickers
bg = backdrop((255, 236, 246), (226, 232, 255), [(2000, 1400, 520, (255, 190, 230)), (300, 300, 480, (190, 210, 255))])
headline(bg, '', '百变造型', CANDY, '我已经尽可能多做款式了！')
im, info = frame('dressup', 20); studio = im.crop((164, 28, 1544, 1010))
place(bg, card(studio, 1080), W / 2, 1110)
for k, (cx, cy, a) in enumerate([(300, 760, -6), (500, 1160, 5), (270, 1500, -3), (2100, 760, 6), (1900, 1160, -5), (2130, 1500, 4),
                                  (560, 260, 4), (1840, 260, -4), (760, 1620, -4), (1640, 1620, 5)]):
    sticker(bg, Image.open(STK / f'doll{k}.png'), 11 if k < 6 else 8, cx, cy, a)
brand(bg); bg.convert('RGB').save(OUT / '2-style.png')

# 3 -- pets: the house, cats and dogs in all sorts of poses, and Buddy holding the cat
bg = backdrop((255, 244, 228), (255, 228, 222), [(400, 400, 500, (255, 210, 150)), (2000, 1500, 520, (255, 180, 170))])
headline(bg, '还能领养', '一只宠物', FIRE, '模拟小人也要有陪伴')
place(bg, card(view('cat_fridge', 30), 1400), W / 2, 1060)
sticker(bg, Image.open(STK / 'hold.png'), 13, 380, 1420, -4)
for k, (cx, cy, a, z) in enumerate([(300, 620, -5, 9), (2090, 600, 5, 10), (2140, 1080, -4, 6), (800, 1590, 3, 7), (1260, 1620, -3, 5), (1720, 1570, 4, 9),
                                    (2120, 1500, -5, 6), (200, 210, 6, 5), (2200, 230, -6, 6), (250, 1010, 4, 6)]):
    sticker(bg, Image.open(STK / f'pet{k}.png'), z, cx, cy, a)
brand(bg); bg.convert('RGB').save(OUT / '3-pet.png')

# 4 -- going out
bg = backdrop((228, 248, 242), (226, 238, 255), [(300, 1500, 520, (170, 235, 210)), (2100, 300, 520, (180, 210, 255))])
headline(bg, '公园  商场  码头  酒吧', '出门逛逛', MINT, '还有一些隐藏地图！')
for k, (n, ang, cx, cy) in enumerate([('place_mall', 5, 690, 1010), ('place_beach', -4, 1720, 1060), ('place_park', 0, 1200, 1290)]):
    place(bg, card(scene(n, 20), 1150, angle=ang), cx, cy)
for n, k, cx, cy, a in [('tree2', 7, 190, 1270, -3), ('tree4', 6, 2220, 1240, 3), ('bush0', 8, 470, 1620, -2), ('bench0', 6, 1010, 1610, 0),
                        ('bush2', 8, 1480, 1630, 3), ('bush1', 8, 1930, 1600, -3), ('shrub4', 9, 760, 1650, 2), ('tree3', 5, 2050, 520, 4), ('shrub6', 9, 330, 560, -3)]:
    sticker(bg, Image.open(STK / f'{n}.png'), k, cx, cy, a)
brand(bg); bg.convert('RGB').save(OUT / '4-places.png')

# 5 -- festivals: 怪兽夜, the disco and a park fair, festival props as stickers
bg = backdrop((255, 240, 246), (230, 240, 255), [(400, 1500, 520, (255, 200, 170)), (2000, 300, 540, (190, 220, 255)), (1200, 900, 420, (210, 245, 220))])
text(bg, f"{M['stats']['festivals']} 个节日", 64, W / 2, 120, SOFT, 'Bold')
grad_text(bg, '每个节日都不一样', 150, W / 2, 240, AURORA)
text(bg, '怪兽夜戴面具、跳舞日蹦蹦蹦，甜品节吃到爽', 50, W / 2, 370, SOFT, 'Medium')
for n, i, b, ang, cx, cy in [('fest_怪兽夜', 10, 1.0, -5, 720, 900), ('fest_跳舞日', 40, 1.1, 4, 1700, 940), ('fest_甜品节', 10, 1.0, 0, 1200, 1300)]:
    place(bg, card(scene(n, i, b), 1100, angle=ang), cx, cy)
for n, k, cx, cy, a in [('pumpkin', 14, 230, 1180, -8), ('balloon_ghost', 14, 2170, 1230, 8), ('mirror_ball', 8, 2190, 560, 6), ('snowman_7', 8, 210, 560, -6),
                        ('dragon_boat_0', 5, 460, 1600, -3), ('fest_stall_mooncake', 5, 1960, 1580, 4), ('lantern_red', 14, 420, 1350, 6), ('balloon_heart', 14, 2000, 1330, -6),
                        ('bat', 10, 1230, 640, 0)]:
    sticker(bg, Image.open(ART / f'{n}.png'), k, cx, cy, a)
brand(bg); bg.convert('RGB').save(OUT / '5-festivals.png')

# 6 -- chance cards: one card in play, a cloud of other card titles around it
bg = backdrop((236, 244, 255), (240, 232, 255), [(2000, 400, 520, (190, 215, 255)), (300, 1500, 500, (220, 200, 255))])
text(bg, '800+ 张', 64, W / 2, 120, SOFT, 'Bold')
grad_text(bg, '奇思妙想机会卡', 150, W / 2, 240, SKY)
text(bg, '这种问题得你来拿主意', 50, W / 2, 370, SOFT, 'Medium')
place(bg, card(view('card', 20), 1250), W / 2, 1085)
titles = json.loads((STK / 'cards.json').read_text()); rnd = random.Random(7)
fav = ['我的遥控器呢？', '一根头发的胜利', '剩饭选举', '深夜重大问题', '撤回的诱惑', '失踪鞋员', '愿望博物馆', '差评里的文学天赋', '椅子的可疑叫声',
       '给朋友当闹钟', '一分钱的胜利', '发错窗口', '梦里有你', '摆盘尊严', '宣布早睡', '煮饭按钮的沉默', '热水壶的掌声', '锅盖失踪', '一块顽强的污渍',
       '酸得有态度', '互不信任', '句号。。。。', '一部神作', '请您假装懂行', '群里的免费专家', '验证码的审美门槛', '自动续费的纪念日', '分享欲的时差',
       '小众忧郁款', '房间里的怪味', '今天的背景音', '一个过于准确的推荐', '朋友更换了头像', '被拉进了兴趣群']
pick = [t for t in fav if t in titles]
cols = [(236, 92, 140), (90, 140, 230), (240, 140, 60), (60, 170, 140), (150, 100, 220), (220, 90, 90)]
taken = [(560, 840, 1840, 1330), (520, 40, 1880, 420)]          # the card and the headline stay clear
f = font(34, 'Bold'); k = 0
for t in pick:
    w, h = int(ImageDraw.Draw(bg).textlength(t, font=f)) + 80, 84
    for _ in range(400):
        cx, cy = rnd.uniform(60 + w / 2, W - 60 - w / 2), rnd.uniform(110, H - 140)
        box = (cx - w / 2 - 14, cy - h / 2 - 14, cx + w / 2 + 14, cy + h / 2 + 14)
        if not any(box[0] < r[2] and box[2] > r[0] and box[1] < r[3] and box[3] > r[1] for r in taken):
            taken.append(box); pill(bg, t, 34, cx, cy, cols[k % len(cols)], rnd.uniform(-5, 5)); k += 1; break
brand(bg); bg.convert('RGB').save(OUT / '6-cards.png')
# 7 -- relationships: three video chats that drift somewhere odd
CHATS = [('爸爸', 3, [('o', '喂？能看见我吗？'), ('me', '爸，我只看见你的下巴。'), ('o', '往上挪点……现在呢？'), ('me', '现在是天花板的灯。'), ('o', '也行，那灯是我新换的。')]),
         ('朋友', 9, [('o', '新公司第一天，我坐错了工位。'), ('me', '坐了多久才发现？'), ('o', '一上午，还帮人回了邮件。'), ('me', '那人家没说什么？'), ('o', '他说我回得比他还好。')]),
         ('妈妈', 2, [('o', '吃饭了吗？吃的什么？'), ('me', '泡面加了个蛋。'), ('o', '镜头对着冰箱，我看看。'), ('me', '……里面只有一瓶辣酱。'), ('o', '我明天就寄两箱饺子。')])]
bg = backdrop((255, 242, 236), (236, 236, 255), [(300, 1500, 520, (255, 200, 190)), (2100, 400, 520, (200, 210, 255))])
headline(bg, '爸妈 · 朋友 · 邻居', '人际关系', [(255, 110, 140), (255, 160, 90)], '聊着聊着，话题就去了奇怪的地方')
fb = font(46, 'Medium'); fh = font(48, 'Black')
for k, (who, dk, lines) in enumerate(CHATS):
    pw, cx = 720, 430 + k * 770; panel = Image.new('RGBA', (pw, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(panel)
    d.rounded_rectangle([0, 0, pw - 1, 1079], 44, fill=(255, 255, 255, 236))
    d.text((pw / 2, 70), who, font=fh, fill=INK, anchor='mm'); d.line([(40, 124), (pw - 40, 124)], fill=(230, 226, 240), width=3)
    y = 166
    for side, t in lines:
        rows, cur = [], ''
        for ch in t:
            if d.textlength(cur + ch, font=fb) > 500 and ch not in '，。？！…、': rows.append(cur); cur = ch
            else: cur += ch
        rows.append(cur); tw = max(d.textlength(r, font=fb) for r in rows); bh = 36 + 62 * len(rows)
        x0 = 36 if side == 'o' else pw - 36 - tw - 56
        d.rounded_rectangle([x0, y, x0 + tw + 56, y + bh], 34, fill=(240, 238, 246) if side == 'o' else (255, 128, 150))
        for i, r in enumerate(rows): d.text((x0 + 28, y + 16 + 62 * i), r, font=fb, fill=INK if side == 'o' else (255, 255, 255))
        y += bh + 40
    panel = panel.crop((0, 0, pw, y + 30)).rotate((-2, 1.5, -1)[k], Image.BICUBIC, expand=True)
    place(bg, panel, cx, 520 + panel.height / 2, shadow=50)
    sticker(bg, Image.open(STK / f'doll{dk}.png'), 8, cx - pw / 2 + 40, 520, (-6, 5, -4)[k])
sticker(bg, Image.open(STK / 'doll0.png'), 9, 2240, 1600, 6)
brand(bg); bg.convert('RGB').save(OUT / '7-friends.png')
print('posters ->', OUT)
