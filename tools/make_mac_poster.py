# The "Mac 版来了" poster (4:3, same look as tools/make_posters.py): a drawn
# MacBook whose desktop shows the game see-through, the menu bar icon with its
# menu open, the Dock; pixel-art computer, doll and pet stickers around it.
#   python3 tools/make_mac_poster.py GAME_PNG STICKER_DIR OUT_JPG
# GAME_PNG: the game shot with a transparent background (Playwright,
# omitBackground). STICKER_DIR: the trailer's stickers (doll*.png, pet*.png).
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

GAME, STK, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
W, H = 2400, 1800
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
INK, SOFT = (36, 28, 58), (98, 90, 122)


def font(px, w='Black'): return ImageFont.truetype(NOTO.format(w), px, index=2)


def backdrop(c0, c1, blobs):
    yy, xx = np.mgrid[0:H, 0:W]; g = Image.fromarray(np.uint8(255 * np.clip((xx / W * .55 + yy / H * .45), 0, 1)))
    bg = Image.composite(Image.new('RGBA', (W, H), c1), Image.new('RGBA', (W, H), c0), g)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for (x, y, r, col) in blobs: d.ellipse([x - r, y - r, x + r, y + r], fill=col + (120,))
    bg.alpha_composite(layer.filter(ImageFilter.GaussianBlur(160)))
    return bg


def place(bg, c, x, y, shadow=70, blur=36, dy=34):
    """Top-left at x, y with a soft drop shadow."""
    x, y = int(x), int(y)
    sh = Image.new('RGBA', bg.size, (0, 0, 0, 0)); a = c.getchannel('A').point(lambda v: v * shadow // 255)
    sh.paste(Image.new('RGBA', c.size, (30, 20, 60, 255)), (x + 10, y + dy), a)
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); bg.alpha_composite(c, (x, y))


def placec(bg, c, cx, cy, **k): place(bg, c, cx - c.width / 2, cy - c.height / 2, **k)


def grad_fill(size, cols, vertical=False):
    """An even multi-stop gradient, left to right (or top to bottom)."""
    w, h = size; n = h if vertical else w
    t = np.linspace(0, len(cols) - 1, max(n, 1)); i = np.minimum(t.astype(int), len(cols) - 2); f = (t - i)[:, None]
    c = np.array(cols, float); line = c[i] * (1 - f) + c[i + 1] * f
    arr = np.repeat(line[:, None, :], w, 1) if vertical else np.repeat(line[None, :, :], h, 0)
    return Image.fromarray(np.uint8(arr)).convert('RGBA')


def grad_text(bg, text, px, x, y, cols, anchor='mm', w='Black'):
    f = font(px, w); d = ImageDraw.Draw(bg); l, t, r, b = (int(v) for v in d.textbbox((x, y), text, font=f, anchor=anchor))
    m = Image.new('L', bg.size, 0); ImageDraw.Draw(m).text((x, y), text, font=f, anchor=anchor, fill=255)
    fill = Image.new('RGBA', bg.size, (0, 0, 0, 0)); fill.paste(grad_fill((r - l, b - t), cols), (l, t)); bg.paste(fill, (0, 0), m)


def text(d, s, px, x, y, col=INK, w='Black', anchor='mm'): d.text((x, y), s, font=font(px, w), fill=col, anchor=anchor)


def sticker(bg, img, k, cx, cy, angle=0, rim=9):
    """A die-cut sticker: the sprite scaled k (nearest) with a white rim and a soft shadow."""
    im = img.convert('RGBA'); im = im.crop(im.getbbox()); im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    pad = rim + 4; c = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); c.alpha_composite(im, (pad, pad))
    a = c.getchannel('A').point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(2 * rim + 1)).filter(ImageFilter.GaussianBlur(1.2))
    base = Image.new('RGBA', c.size, (255, 255, 255, 0)); base.putalpha(a); base.alpha_composite(c)
    if angle: base = base.rotate(angle, Image.BICUBIC, expand=True)
    placec(bg, base, cx, cy, shadow=60)


# ---------------------------------------------------------------- pixel stickers
OL = (52, 42, 70)


def pix(w, h, rows):
    """rows: list of (x0, x1, y, rgb) spans."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); px = im.load()
    for x0, x1, y, c in rows:
        for x in range(x0, x1 + 1): px[x, y] = c + (255,)
    return im


def rect(spans, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1): spans.append((x0, x1, y, c))


def buddy_face(s, x, y):
    """A 6x6 Buddy head (dark hair, bow) at x, y."""
    hair, skin, bow, eye = (54, 44, 70), (252, 214, 184), (226, 70, 84), (40, 30, 50)
    rect(s, x + 1, y, x + 4, y, hair); rect(s, x, y + 1, x + 5, y + 1, hair); rect(s, x + 5, y - 1, x + 6, y, bow)
    rect(s, x, y + 2, x + 5, y + 4, skin); s += [(x, x, y + 2, hair), (x + 5, x + 5, y + 2, hair)]
    rect(s, x - 1, y + 1, x - 1, y + 6, hair); rect(s, x + 6, y + 1, x + 6, y + 6, hair)          # long hair
    s += [(x + 1, x + 1, y + 3, eye), (x + 4, x + 4, y + 3, eye), (x + 2, x + 3, y + 5, skin), (x + 1, x + 1, y + 4, (250, 170, 170)), (x + 4, x + 4, y + 4, (250, 170, 170))]


def retro_mac():
    """A boxy all-in-one with Buddy waving on its screen."""
    body, mid, shade, dark = (240, 233, 216), (220, 210, 190), (190, 178, 158), (120, 108, 96)
    s = []
    rect(s, 2, 0, 21, 0, OL); rect(s, 1, 1, 22, 22, OL)
    rect(s, 2, 1, 21, 21, body); rect(s, 21, 2, 21, 21, shade); rect(s, 2, 20, 20, 21, mid)
    rect(s, 4, 3, 19, 14, dark); rect(s, 5, 4, 18, 13, (130, 196, 238))
    rect(s, 5, 11, 18, 13, (150, 210, 140))                                  # a hill on the screen
    rect(s, 5, 4, 18, 4, (170, 216, 246)); buddy_face(s, 8, 6); rect(s, 8, 12, 13, 13, (226, 70, 84))
    rect(s, 16, 5, 17, 6, (255, 214, 90))                                                         # sun
    rect(s, 12, 17, 18, 17, dark); rect(s, 12, 18, 18, 18, mid); s.append((5, 5, 17, (110, 200, 120)))   # disk slot, light
    rect(s, 4, 23, 19, 23, OL); rect(s, 5, 22, 18, 22, mid); rect(s, 3, 24, 20, 24, OL); rect(s, 4, 23, 19, 23, shade)
    return pix(24, 25, s)


def laptop():
    """An open laptop showing the little house."""
    alu, alu2, alu3 = (214, 218, 228), (188, 192, 206), (150, 154, 172)
    s = []
    rect(s, 2, 0, 29, 0, OL); rect(s, 1, 1, 30, 18, OL); rect(s, 2, 1, 29, 17, (40, 40, 48))
    rect(s, 3, 2, 28, 16, (196, 186, 250)); rect(s, 3, 2, 28, 4, (214, 204, 255))                     # wallpaper
    rect(s, 3, 2, 28, 2, (236, 234, 248))                                                             # menu bar
    rect(s, 9, 8, 22, 15, (84, 72, 80)); rect(s, 10, 9, 15, 11, (250, 238, 222)); rect(s, 17, 9, 21, 11, (232, 240, 222))
    rect(s, 10, 13, 15, 14, (246, 232, 214)); rect(s, 17, 13, 21, 14, (250, 238, 222)); rect(s, 16, 9, 16, 14, (84, 72, 80))
    s += [(13, 13, 10, (226, 70, 84)), (13, 13, 11, (54, 44, 70))]                                    # Buddy, tiny
    rect(s, 9, 6, 22, 6, (150, 210, 140)); rect(s, 9, 7, 22, 7, (255, 200, 90))                      # needs + time bars
    rect(s, 0, 19, 31, 19, OL); rect(s, 0, 20, 31, 21, OL); rect(s, 1, 19, 30, 19, alu); rect(s, 1, 20, 30, 20, alu2)
    rect(s, 13, 19, 18, 19, alu3); rect(s, 1, 22, 30, 22, OL)
    return pix(32, 23, s)


# ---------------------------------------------------------------- the MacBook
def rounded(size, r, fill):
    im = Image.new('RGBA', size, (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=fill); return im


def macbook(game, app_icon):
    SW, SH, BZ = 1560, 980, 26                    # screen with bezel
    dw, dh = SW - 2 * BZ, SH - 2 * BZ - 10         # the display
    disp = grad_fill((dw, dh), [(255, 206, 222), (214, 196, 255), (168, 210, 255)])
    blob = Image.new('RGBA', (dw, dh), (0, 0, 0, 0)); d = ImageDraw.Draw(blob)
    for x, y, r, c in [(200, 820, 420, (255, 170, 200)), (1300, 200, 380, (150, 190, 255)), (760, 980, 520, (190, 160, 255))]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (140,))
    disp.alpha_composite(blob.filter(ImageFilter.GaussianBlur(120)))
    hills = Image.new('RGBA', (dw, dh), (0, 0, 0, 0)); d = ImageDraw.Draw(hills)     # soft rolling hills
    for base, amp, ph, col in [(700, 60, 0.0, (255, 255, 255, 70)), (780, 50, 1.7, (255, 255, 255, 90))]:
        pts = [(x, base - amp * np.sin(x / 260 + ph)) for x in range(0, dw + 20, 20)] + [(dw, dh), (0, dh)]
        d.polygon(pts, fill=col)
    disp.alpha_composite(hills.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(disp)
    # menu bar: our app's own menu on the left, its icon on the right
    mb = Image.new('RGBA', (dw, 40), (255, 255, 255, 150)); disp.alpha_composite(mb)
    text(d, 'Desktop Buddy', 22, 30, 20, INK, 'Black', 'lm'); text(d, '编辑', 22, 210, 20, INK, 'Medium', 'lm')
    text(d, '周五 21:30', 22, dw - 28, 20, INK, 'Medium', 'rm')
    ix = dw - 200; ic = app_icon.resize((28, 28), Image.LANCZOS)
    d.rounded_rectangle([ix - 8, 4, ix + 36, 36], 8, fill=(255, 255, 255, 170)); disp.alpha_composite(ic, (ix, 6))
    # the tray menu, open
    items = [('显示 / 隐藏', False), ('置顶游戏', True), ('检查更新', False), (None, False), ('退出', False)]
    mw, mh = 280, 34 + 46 * 4 + 14
    menu = rounded((mw, mh), 18, (250, 248, 255, 238)); md = ImageDraw.Draw(menu); y = 18
    for s, tick in items:
        if s is None: md.line([(16, y + 8), (mw - 16, y + 8)], fill=(214, 208, 228), width=2); y += 18; continue
        if s == '置顶游戏': md.rounded_rectangle([8, y - 2, mw - 8, y + 40], 10, fill=(108, 132, 240))
        col = (255, 255, 255) if s == '置顶游戏' else INK
        if tick: text(md, '✓', 22, 26, y + 19, col, 'Bold')
        text(md, s, 24, 52, y + 19, col, 'Medium', 'lm'); y += 46
    place(disp, menu, ix - 30, 46, shadow=60, blur=14, dy=8)
    # Dock
    dock_w, n = 620, 8
    dock = rounded((dock_w, 96), 30, (255, 255, 255, 120)); dk = ImageDraw.Draw(dock)
    cols = [(255, 140, 120), (120, 200, 255), (130, 220, 150), (255, 200, 90), (190, 150, 255), (255, 150, 200), (150, 160, 180)]
    for k in range(n):
        x = 22 + k * 74
        if k == 5: dock.alpha_composite(app_icon.resize((62, 62), Image.LANCZOS), (x, 14)); dk.ellipse([x + 28, 84, x + 34, 90], fill=INK); continue
        c = cols[k if k < 5 else k - 1]; dk.rounded_rectangle([x, 14, x + 61, 75], 16, fill=c + (255,))
        dk.rounded_rectangle([x + 16, 30, x + 45, 59], 8, fill=(255, 255, 255, 120))
    place(disp, dock, (dw - dock_w) // 2, dh - 112, shadow=40, blur=12, dy=6)
    # the game, see-through, sitting on the desktop
    g = game.resize((int(game.width * 0.8), int(game.height * 0.8)), Image.LANCZOS)
    place(disp, g, dw - g.width - 380, dh - g.height - 150, shadow=55, blur=18, dy=14)
    # assemble: bezel, display, base
    scr = rounded((SW, SH), 44, (26, 26, 32, 255)); m = Image.new('L', (dw, dh), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, dw - 1, dh - 1], 20, fill=255); scr.paste(disp, (BZ, BZ), m)
    ImageDraw.Draw(scr).rounded_rectangle([1, 1, SW - 2, SH - 2], 44, outline=(80, 80, 92), width=3)
    BW, BH = SW + 200, 54
    base = Image.new('RGBA', (BW, BH), (0, 0, 0, 0)); bd = ImageDraw.Draw(base)
    bd.polygon([(0, 8), (BW, 8), (BW - 40, BH), (40, BH)], fill=(170, 174, 188))
    bd.rounded_rectangle([0, 0, BW - 1, 22], 10, fill=(222, 225, 234)); bd.rectangle([0, 14, BW - 1, 22], fill=(206, 210, 222))
    bd.rounded_rectangle([BW // 2 - 110, 0, BW // 2 + 110, 12], 6, fill=(190, 194, 208))
    out = Image.new('RGBA', (BW, SH + BH - 6), (0, 0, 0, 0)); out.alpha_composite(scr, (100, 0)); out.alpha_composite(base, (0, SH - 6))
    return out


# ---------------------------------------------------------------- the poster
bg = backdrop((246, 242, 255), (226, 236, 255), [(300, 1500, 520, (255, 200, 222)), (2100, 380, 540, (190, 210, 255)), (1200, 950, 460, (226, 214, 255))])
d = ImageDraw.Draw(bg)
grad_text(bg, 'Mac 版来了！', 170, W / 2, 175, [(255, 110, 160), (160, 110, 255), (90, 160, 255)])
text(d, 'Desktop-Buddy Mac 端震撼（也许）发布', 56, W / 2, 318, SOFT, 'Bold')

icon = Image.open('art/out/concept/app_icon.png').convert('RGBA')
mb = macbook(Image.open(GAME).convert('RGBA'), icon)
k = 1800 / mb.width; mb = mb.resize((int(mb.width * k), int(mb.height * k)), Image.LANCZOS)
placec(bg, mb, W / 2, 420 + mb.height / 2, shadow=80, blur=40, dy=40)


sticker(bg, retro_mac(), 13, 270, 220, -8)
sticker(bg, laptop(), 10, 2130, 220, 7)
sticker(bg, Image.open(STK / 'doll0.png'), 9, 160, 980, -5)
sticker(bg, Image.open(STK / 'doll5.png'), 8, 2245, 960, 6)
sticker(bg, Image.open(STK / 'pet2.png'), 6, 170, 1420, 4)
sticker(bg, Image.open(STK / 'pet6.png'), 6, 2235, 1420, -4)
for n, k, cx, cy, a in [('doll2', 8, 640, 1660, -4), ('pet0', 6, 1000, 1690, 3), ('doll7', 8, 1400, 1660, 4), ('pet4', 6, 1760, 1690, -3)]:
    sticker(bg, Image.open(STK / f'{n}.png'), k, cx, cy, a)
OUT.parent.mkdir(parents=True, exist_ok=True)
bg.convert('RGB').save(OUT, quality=92)
print('poster ->', OUT)
