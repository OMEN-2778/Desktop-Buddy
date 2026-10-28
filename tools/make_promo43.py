#!/usr/bin/env python3
"""4:3 promo, part 2: edits the clips from tools/make_promo43.js into a calm, poster-style video.

A desktop full of (quiet) work windows; the pointer double-clicks the game icon, the little
house pops up and the camera eases in onto it. Then one section per poster, each with its
headline easing in: 桌面小屋 (a long run of home life, her words and diary lines, a pill naming
what she's doing), 出门逛逛 and 节日 (three live scenes in rounded cards, stickers popping in one
by one and floating), 机会卡 (card-title pills: a tidy grid -> a loose cloud -> neat columns
around the card), 人际关系 (three chats filling in bubble by bubble). Back to the desktop, title,
fade. Every move is a quartic ease-in-out: no cuts on the beat, no shakes.

  python3 tools/make_promo43.py CLIP_DIR STICKER_DIR MUSIC.mp3 OUT.mp4 [preview frames]
"""
from pathlib import Path
import json, math, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CLIPS, STK, MUSIC, OUT = (Path(a) for a in sys.argv[1:5])
M = json.loads((CLIPS / 'clips.json').read_text())
ART = ROOT / 'art/out/concept'
FPS, W, H, OW, OH = 30, 2400, 1800, 1440, 1080          # composed at 2400x1800, written at 1440x1080
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
INK, SOFT = (36, 28, 58), (98, 90, 122)


def font(px, w='Black'): return ImageFont.truetype(NOTO.format(w), int(px), index=2)
def quart(u): u = min(1, max(0, u)); return 8 * u ** 4 if u < .5 else 1 - (-2 * u + 2) ** 4 / 2
def quart_out(u): u = min(1, max(0, u)); return 1 - (1 - u) ** 4
def lerp(a, b, u): return a + (b - a) * u


# ================================================================ clips
_cache = {}
def frame(name, i):
    c = M['clips'][name]; i = int(i) % c['frames']; key = (name, i)
    if key not in _cache:
        if len(_cache) > 60: _cache.pop(next(iter(_cache)))
        _cache[key] = (Image.open(CLIPS / 'clips' / name / f'{i:03d}.png').convert('RGBA'), c['info'][i])
    return _cache[key]


def view(name, i, trim=40):                            # the game picture only (place views lose the arrow buttons)
    im, info = frame(name, i); x, y, w, h = info['view']
    return im.crop((int(x * 2) + trim, int(y * 2), int((x + w) * 2) - trim, int((y + h) * 2)))


HOME = ['home_tv', 'home_computer', 'home_cook', 'home_eat', 'home_pc_video', 'home_read', 'home_water_living', 'home_snack', 'home_bath', 'home_wash', 'home_sleep']
LABEL = {'home_tv': '看电视', 'home_computer': '打游戏', 'home_cook': '做饭', 'home_eat': '吃饭', 'home_pc_video': '视频聊天', 'home_read': '看书',
         'home_water_living': '浇花', 'home_snack': '偷吃零食', 'home_bath': '泡澡', 'home_wash': '洗脸刷牙', 'home_sleep': '睡觉'}
def _union_box():
    b = None
    for n in HOME + ['idle']:
        for i in (0, 30, M['clips'][n]['frames'] - 1):
            bb = frame(n, i)[0].getbbox(); b = bb if b is None else (min(b[0], bb[0]), min(b[1], bb[1]), max(b[2], bb[2]), max(b[3], bb[3]))
    return b
FULL = _union_box()                                     # house + needs + mood + speech + diary, same box for every clip
def full(name, i): return frame(name, i)[0].crop(FULL)


# ================================================================ drawing helpers
def backdrop(c0, c1, blobs):
    yy, xx = np.mgrid[0:H, 0:W]; g = Image.fromarray(np.uint8(255 * np.clip((xx / W * .55 + yy / H * .45), 0, 1)))
    bg = Image.composite(Image.new('RGBA', (W, H), c1), Image.new('RGBA', (W, H), c0), g)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for (x, y, r, col) in blobs: d.ellipse([x - r, y - r, x + r, y + r], fill=col + (120,))
    bg.alpha_composite(layer.filter(ImageFilter.GaussianBlur(160)))
    return bg


def shadowed(c, shadow=70, blur=30, off=(8, 28)):
    """c with its soft drop shadow baked in; returns (image, pad) — draw it pad px up-left of c's spot."""
    pad = blur * 3 + max(off); out = Image.new('RGBA', (c.width + 2 * pad, c.height + 2 * pad), (0, 0, 0, 0))
    a = c.getchannel('A').point(lambda v: v * shadow // 255)
    out.paste(Image.new('RGBA', c.size, (30, 20, 60, 255)), (pad + off[0], pad + off[1]), a)
    out = out.filter(ImageFilter.GaussianBlur(blur)); out.alpha_composite(c, (pad, pad))
    return out, pad


def put(canvas, img, cx, cy, alpha=1.0, scale=1.0, angle=0.0):
    """Draw img centred at (cx, cy), faded, scaled and turned (only resampled when it has to be)."""
    if alpha <= 0.003: return
    if abs(scale - 1) > .002: img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.BICUBIC)
    if abs(angle) > .02: img = img.rotate(angle, Image.BICUBIC, expand=True)
    if alpha < .997: img = img.copy(); img.putalpha(img.getchannel('A').point(lambda v: int(v * alpha)))
    x, y = int(round(cx - img.width / 2)), int(round(cy - img.height / 2))
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy: img = img.crop((sx, sy, img.width, img.height)); x += sx; y += sy
    canvas.alpha_composite(img, (x, y))


def text_img(s, px, col, w='Black'):
    f = font(px, w); l, t, r, b = f.getbbox(s); im = Image.new('RGBA', (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - l, 4 - t), s, font=f, fill=col); return im


def grad_img(s, px, cols, w='Black'):
    m = text_img(s, px, (255, 255, 255), w); a = m.getchannel('A'); n = len(cols) - 1
    xs = np.linspace(0, n, m.width); i = np.minimum(xs.astype(int), n - 1); f = (xs - i)[:, None]
    c0, c1 = np.array(cols)[i], np.array(cols)[i + 1]; row = (c0 * (1 - f) + c1 * f).astype(np.uint8)
    g = Image.fromarray(np.repeat(row[None], m.height, 0)).convert('RGBA'); g.putalpha(a); return g


class Headline:
    """small / big / sub lines that rise in one after another and leave together."""
    def __init__(self, small, big, cols, sub, y=230):
        self.parts = []
        if small: self.parts.append((text_img(small, 64, SOFT, 'Bold'), y - 110))
        self.parts.append((grad_img(big, 150, cols), y + 10))
        if sub: self.parts.append((text_img(sub, 50, SOFT, 'Medium'), y + 140))
    def draw(self, cv, t, dy=0):
        for k, (im, y) in enumerate(self.parts):
            u = quart_out((t - 4 - k * 5) / 20); put(cv, im, W / 2, y + 40 * (1 - u) + dy, u)


def card_frame(w, h, radius=34, border=10):
    """A white rounded card of outer size w x h with its shadow; returns (image, pad, inner mask)."""
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(c).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=(255, 255, 255, 255) if border else (0, 0, 0, 255))
    img, pad = shadowed(c)
    if not border: img.paste((0, 0, 0, 0), (pad, pad, pad + w, pad + h), c.getchannel('A'))   # shadow only
    m = Image.new('L', (w - 2 * border, h - 2 * border), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, m.width - 1, m.height - 1], radius - border, fill=255)
    return img, pad, m


class LiveCard:
    """A rounded card showing a live clip; enters by easing up and in."""
    def __init__(self, width, aspect, cx, cy, angle=0, border=10, radius=34):
        self.w, self.h = int(width), int(width / aspect); self.b = border
        self.frame, self.pad, self.mask = card_frame(self.w + 2 * border, self.h + 2 * border, radius, border)
        self.cx, self.cy, self.angle = cx, cy, angle
    def draw(self, cv, src, u=1.0, dy=0, cx=None, cy=None, scale=1.0):
        c = self.frame.copy(); inner = src.resize((self.w, self.h), Image.NEAREST if self.w >= src.width * 1.4 else Image.BILINEAR)
        c.paste(inner, (self.pad + self.b, self.pad + self.b), self.mask)
        put(cv, c, (self.cx if cx is None else cx), (self.cy if cy is None else cy) + 50 * (1 - u) + dy, u, scale * (.94 + .06 * u), self.angle)


def sticker_img(img, k, rim=9):
    im = img.convert('RGBA'); im = im.crop(im.getbbox()); im = im.resize((im.width * k, im.height * k), Image.NEAREST)
    pad = rim + 4; c = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); c.alpha_composite(im, (pad, pad))
    a = c.getchannel('A').point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(2 * rim + 1)).filter(ImageFilter.GaussianBlur(1.2))
    base = Image.new('RGBA', c.size, (255, 255, 255, 0)); base.putalpha(a); base.alpha_composite(c)
    return shadowed(base, 60, 14, (4, 12))[0]


class Stickers:
    """Stickers that pop in one by one (ease-out scale + fade) and then float gently."""
    def __init__(self, items, start=24, gap=5):
        self.items = [(sticker_img(img, k), cx, cy, a, start + n * gap, n) for n, (img, k, cx, cy, a) in enumerate(items)]
    def draw(self, cv, t, dy=0):
        for im, cx, cy, a, t0, n in self.items:
            u = quart_out((t - t0) / 16)
            if u <= 0: continue
            bob = 7 * math.sin((t + n * 11) / 26); tilt = 1.6 * math.sin((t + n * 17) / 41)
            put(cv, im, cx, cy + bob + dy, u, .55 + .45 * u, a + tilt)


def pill_img(s, px, col):
    f = font(px, 'Bold'); w = int(f.getlength(s)) + px * 2; h = int(px * 2.1)
    c = Image.new('RGBA', (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle([4, 4, w + 3, h + 3], h // 2, fill=(255, 255, 255, 255), outline=col + (255,), width=5)
    d.text((w / 2 + 4, h / 2 + 4), s, font=f, fill=col, anchor='mm')
    return shadowed(c, 45, 12, (3, 10))[0]


def brand(cv, a=1.0): put(cv, BRAND, W / 2, H - 70, a)
BRAND = text_img('Desktop Buddy', 40, (120, 110, 150), 'Bold')
STK_IMG = lambda n: Image.open(STK / f'{n}.png')
ART_IMG = lambda n: Image.open(ART / f'{n}.png')


# ================================================================ desktop (4:3)
DS = 1.25                                               # desktop drawn at 1920x1440 logical px
ICON_AT = (70, 60)
def rounded(d, box, r, **k): d.rounded_rectangle([int(v * DS) for v in box], int(r * DS), **k)


def make_desktop(running):
    LW, LH = W / DS, H / DS
    g = np.linspace(0, 1, H)[:, None, None]
    im = Image.fromarray(np.uint8(np.array([124, 158, 214]) * (1 - g) + np.array([236, 200, 220]) * g).repeat(W, 1)).convert('RGBA')
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for x, y, r, c in ((380, 300, 460, (255, 236, 220, 110)), (1560, 260, 380, (200, 224, 255, 90)), (1100, 1100, 520, (255, 208, 230, 80))):
        gd.ellipse([(x - r) * DS, (y - r) * DS, (x + r) * DS, (y + r) * DS], fill=c)
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(160))); d = ImageDraw.Draw(im)
    icon = Image.open(ROOT / 'desktop/src-tauri/icons/128x128.png').convert('RGBA').resize((int(64 * DS), int(64 * DS)), Image.LANCZOS)
    f = font(14 * DS, 'Medium'); ix, iy = ICON_AT
    def label(x, y, t): d.text((x * DS, y * DS), t, font=f, fill='white', anchor='ma', stroke_width=2, stroke_fill=(40, 40, 60, 160))
    im.alpha_composite(icon, (int(ix * DS), int(iy * DS))); label(ix + 32, iy + 70, 'Desktop Buddy')
    for k, (kind, name) in enumerate((('folder', '照片'), ('doc', '待办.txt'), ('folder', '工作'), ('sheet', '预算.xlsx'), ('trash', '回收站'))):
        x, y = ix + 4, iy + 112 * (k + 1)
        if kind == 'folder':
            rounded(d, [x + 6, y + 10, x + 54, y + 52], 6, fill=(246, 199, 92)); rounded(d, [x + 6, y + 4, x + 28, y + 16], 4, fill=(232, 178, 70))
        elif kind in ('doc', 'sheet'):
            rounded(d, [x + 13, y + 4, x + 47, y + 54], 4, fill=(250, 250, 252))
            for j in range(4): d.line([(x + 19) * DS, (y + 16 + j * 9) * DS, (x + 41) * DS, (y + 16 + j * 9) * DS], fill=(170, 176, 196) if kind == 'doc' else (110, 190, 140), width=int(2 * DS))
        else:
            rounded(d, [x + 14, y + 12, x + 46, y + 54], 5, fill=(214, 220, 236)); d.rectangle([(x + 10) * DS, (y + 6) * DS, (x + 50) * DS, (y + 11) * DS], fill=(190, 198, 218))
        label(x + 30, y + 62, name)
    def window(wx, wy, ww, wh, title, draw):
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([(wx + 6) * DS, (wy + 16) * DS, (wx + ww + 6) * DS, (wy + wh + 16) * DS], int(14 * DS), fill=(30, 20, 50, 70))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); dd = ImageDraw.Draw(im)
        rounded(dd, [wx, wy, wx + ww, wy + wh], 12, fill=(252, 252, 254)); rounded(dd, [wx, wy, wx + ww, wy + 40], 12, fill=(237, 238, 245))
        dd.rectangle([wx * DS, (wy + 28) * DS, (wx + ww) * DS, (wy + 40) * DS], fill=(237, 238, 245))
        for k, c in enumerate(((240, 108, 98), (240, 190, 80), (108, 200, 120))): dd.ellipse([(wx + 16 + k * 22) * DS, (wy + 13) * DS, (wx + 30 + k * 22) * DS, (wy + 27) * DS], fill=c)
        dd.text(((wx + ww / 2) * DS, (wy + 20) * DS), title, font=font(15 * DS, 'Medium'), fill=(90, 92, 110), anchor='mm'); draw(dd, wx, wy + 40)
    def doc(dd, x, y):
        for j, (t, s) in enumerate((('本周进度', 22), ('· 首页改版：完成 80%', 18), ('· 接口联调：明天上午', 18), ('· 周五前提交测试', 18))):
            dd.text(((x + 32) * DS, (y + 28 + j * 40) * DS), t, font=font(s * DS, 'Bold' if j == 0 else 'Regular'), fill=(66, 68, 88))
        for j in range(5): rounded(dd, [x + 32, y + 200 + j * 26, x + 32 + (420, 380, 440, 300, 360)[j], y + 210 + j * 26], 4, fill=(232, 234, 242))
    def sheet(dd, x, y):
        for r in range(9):
            for c in range(5):
                dd.rectangle([(x + 16 + c * 92) * DS, (y + 14 + r * 30) * DS, (x + 106 + c * 92) * DS, (y + 42 + r * 30) * DS], outline=(222, 226, 236), fill=(240, 246, 242) if r == 0 else None)
        for r, v in enumerate((None, 12, 30, 18, 42, 26, 35, 20, 28)):
            if v: rounded(dd, [x + 110, y + 22 + r * 30, x + 110 + v * 4, y + 34 + r * 30], 3, fill=(120, 196, 150))
    def chat(dd, x, y):
        for j, (side, wdt) in enumerate((('l', 210), ('r', 160), ('l', 250), ('r', 120))):
            bx = x + 20 if side == 'l' else x + 360 - wdt; rounded(dd, [bx, y + 20 + j * 50, bx + wdt, y + 56 + j * 50], 16, fill=(236, 238, 246) if side == 'l' else (150, 196, 255))
    window(250, 120, 640, 470, '周报.docx', doc)
    window(860, 200, 560, 360, '预算.xlsx', sheet)
    window(380, 660, 400, 300, '消息', chat)
    bar = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(bar).rectangle([0, (LH - 56) * DS, W, H], fill=(24, 26, 38, 220)); im.alpha_composite(bar); d = ImageDraw.Draw(im)
    rounded(d, [LW / 2 - 330, LH - 44, LW / 2 - 110, LH - 12], 16, fill=(52, 55, 72)); d.text(((LW / 2 - 300) * DS, (LH - 28) * DS), '搜索', font=font(14 * DS, 'Regular'), fill=(170, 172, 190), anchor='lm')
    cols = [(92, 150, 240), (240, 200, 90), (120, 200, 160), (220, 120, 140), (160, 130, 230)]
    for k, c in enumerate(cols): rounded(d, [LW / 2 - 90 + k * 56, LH - 46, LW / 2 - 54 + k * 56, LH - 10], 9, fill=c)
    if running:
        x = LW / 2 - 90 + len(cols) * 56; im.alpha_composite(icon.resize((int(36 * DS), int(36 * DS)), Image.LANCZOS), (int(x * DS), int((LH - 46) * DS)))
        d.line([(x + 10) * DS, (LH - 5) * DS, (x + 26) * DS, (LH - 5) * DS], fill=(140, 200, 255), width=int(3 * DS))
    d.text(((LW - 64) * DS, (LH - 38) * DS), '15:24', font=font(15 * DS, 'Medium'), fill='white', anchor='mm')
    d.text(((LW - 64) * DS, (LH - 18) * DS), '2026/10/28', font=font(12 * DS, 'Regular'), fill=(210, 212, 225), anchor='mm')
    return im


DESK = [make_desktop(False), make_desktop(True)]
GK = .78 * DS / 1.25                                     # 2x screenshot px -> desktop px (house at its real size)
GW, GH = int((FULL[2] - FULL[0]) * GK), int((FULL[3] - FULL[1]) * GK)
GX, GY = W - GW - 70, H - int(56 * DS) - GH - 30            # the game window: bottom-right, above the taskbar


def pointer(cv, x, y, press):
    s = 1.6 * DS * (.9 if press else 1); p = [(0, 0), (0, 17), (4.6, 13), (8, 20.5), (10.6, 19.4), (7.4, 12.2), (13, 12.2)]
    sh = Image.new('RGBA', (80, 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(20 + a * s, 20 + b * s) for a, b in p], fill=(0, 0, 0, 90))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)), (int(x) - 17, int(y) - 14))
    d = ImageDraw.Draw(cv); d.polygon([(x + a * s, y + b * s) for a, b in p], fill='white', outline=(30, 30, 40), width=2)


# ================================================================ sections
class Section:
    def __init__(self, n, bg): self.n, self.bg = n, bg
    def content(self, t): raise NotImplementedError


class Opening(Section):                                 # desktop, double-click, pop-up, ease in onto the house
    CLICK, POP, ZOOM0, ZOOM1 = 42, 56, 84, 132
    def __init__(self): super().__init__(150, None)
    def layer(self, t):
        return full('idle', t).resize((GW, GH), Image.BILINEAR)
    def cam(self, t):                                   # crop box in desktop px
        u = quart((t - self.ZOOM0) / (self.ZOOM1 - self.ZOOM0))
        cx, cy = GX + GW / 2, GY + GH / 2; tw = GW * 1.22; th = tw * H / W
        tx, ty = min(max(0, cx - tw / 2), W - tw), min(max(0, cy - th / 2), H - th)
        return (lerp(0, tx, u), lerp(0, ty, u), lerp(W, tx + tw, u), lerp(H, ty + th, u))
    def frame(self, t):
        im = DESK[1 if t >= self.POP else 0].copy()
        if t >= self.POP:
            u = quart_out((t - self.POP) / 14); L = self.layer(t)
            put(im, L, GX + GW / 2, GY + GH / 2 + 30 * (1 - u), u, .9 + .1 * u)
        ix, iy = (ICON_AT[0] + 32) * DS, (ICON_AT[1] + 34) * DS
        if self.CLICK <= t < self.CLICK + 16:
            d = ImageDraw.Draw(im); rounded(d, [ICON_AT[0] - 10, ICON_AT[1] - 8, ICON_AT[0] + 74, ICON_AT[1] + 92], 10, fill=(255, 255, 255, 60), outline=(255, 255, 255, 200), width=2)
        if t < self.ZOOM0:
            u = quart(t / 36); x, y = lerp(1500, ix, u), lerp(1300, iy, u)
            if t > self.POP: v = quart((t - self.POP) / 24); x, y = lerp(x, W - 300, v), lerp(y, H - 520, v)
            press = any(0 <= t - c < 4 for c in (self.CLICK, self.CLICK + 7)); pointer(im, x, y, press)
        x0, y0, x1, y1 = self.cam(t)
        return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x1, y1)) if (x0, y0) != (0, 0) else im
    def end_rect(self):                                 # where the house layer sits on screen once zoomed in
        x0, y0, x1, y1 = self.cam(self.ZOOM1); k = W / (x1 - x0)
        return ((GX - x0) * k, (GY - y0) * k, GW * k, GH * k)


class Home(Section):
    PER, FADE = 45, 8
    def __init__(self):
        super().__init__(len(HOME) * self.PER + 10, backdrop((255, 240, 236), (232, 226, 255), [(300, 1500, 500, (255, 190, 200)), (2100, 400, 520, (200, 200, 255))]))
        self.head = Headline('一个小人住在你的桌面上', '桌面小屋', [(238, 70, 120), (150, 80, 230)], '吃饭睡觉样样精通……')
        aspect = (FULL[2] - FULL[0]) / (FULL[3] - FULL[1]); self.card = LiveCard(1640, aspect, W / 2, 1090, border=0, radius=28)
        self.pills = {n: pill_img(LABEL[n], 40, (150, 80, 230)) for n in HOME}
    def src(self, t):
        k = min(len(HOME) - 1, max(0, t) // self.PER); a = full(HOME[k], 12 + t - k * self.PER)
        f = t - k * self.PER
        if f < self.FADE: a = Image.blend(full(HOME[k - 1], 12 + self.PER + f) if k else full('idle', T_HOME + t), a, quart(f / self.FADE))
        return a, k, f
    def content(self, t, cv, dy=0, card=True):
        self.head.draw(cv, t, dy)
        src, k, f = self.src(t)
        if card: self.card.draw(cv, src, 1, dy)
        u = quart_out(f / 12); put(cv, self.pills[HOME[k]], W / 2, self.card.cy + self.card.h / 2 + 4 + dy + 20 * (1 - u), u)


class Showcase(Section):                                # poster 4 / 5: three live cards and stickers
    def __init__(self, n, bg, head, cards, stickers):
        super().__init__(n, bg); self.head = head; self.cards = cards; self.st = Stickers(stickers)
    def content(self, t, cv, dy=0):
        self.head.draw(cv, t, dy)
        for k, (card, name, off) in enumerate(self.cards):
            card.draw(cv, view(name, off + t), quart_out((t - 6 - k * 6) / 22), dy)
        self.st.draw(cv, t, dy)


class Cards(Section):                                   # pills: tidy grid -> loose cloud -> neat columns
    def __init__(self):
        super().__init__(240, backdrop((236, 244, 255), (240, 232, 255), [(2000, 400, 520, (190, 215, 255)), (300, 1500, 500, (220, 200, 255))]))
        self.head = Headline('800+ 张', '奇思妙想机会卡', [(92, 170, 255), (178, 140, 255)], '这种问题得你来拿主意')
        titles = ['我的遥控器呢？', '一根头发的胜利', '剩饭选举', '深夜重大问题', '撤回的诱惑', '失踪鞋员', '愿望博物馆', '差评里的文学天赋', '椅子的可疑叫声',
                  '给朋友当闹钟', '一分钱的胜利', '发错窗口', '梦里有你', '摆盘尊严', '宣布早睡', '煮饭按钮的沉默', '热水壶的掌声', '锅盖失踪',
                  '一块顽强的污渍', '酸得有态度', '互不信任', '一部神作', '请您假装懂行', '群里的免费专家', '验证码的审美门槛', '自动续费的纪念日',
                  '分享欲的时差', '小众忧郁款', '房间里的怪味', '今天的背景音']
        cols = [(236, 92, 140), (90, 140, 230), (240, 140, 60), (60, 170, 140), (150, 100, 220), (220, 90, 90)]
        self.pills = [pill_img(s, 34, cols[k % len(cols)]) for k, s in enumerate(titles)]
        n = len(self.pills); rnd = random.Random(3)
        # A: a tidy grid, rows centred under the headline
        per = 5; self.A = []
        for k, p in enumerate(self.pills):
            r, c = divmod(k, per); row = self.pills[r * per:(r + 1) * per]; ws = [q.width - 30 for q in row]
            x = W / 2 - sum(ws) / 2 + sum(ws[:c]) + ws[c] / 2; self.A.append((x, 560 + r * 160, 0))
        # B: a loose cloud with tilts, kept off the card and the headline
        taken = [(560, 820, 1840, 1350), (480, 40, 1920, 430)]; self.B = []
        for p in self.pills:
            w, h = p.width - 30, p.height - 30
            for _ in range(600):
                cx, cy = rnd.uniform(70 + w / 2, W - 70 - w / 2), rnd.uniform(120, H - 150)
                b = (cx - w / 2 - 12, cy - h / 2 - 12, cx + w / 2 + 12, cy + h / 2 + 12)
                if not any(b[0] < r[2] and b[2] > r[0] and b[1] < r[3] and b[3] > r[1] for r in taken): break
            taken.append(b); self.B.append((cx, cy, rnd.uniform(-9, 9)))
        # C: neat columns either side of the card, plus a row above and below
        slots = [(330, 560 + 150 * i) for i in range(7)] + [(2070, 560 + 150 * i) for i in range(7)] + \
                [(760 + 300 * i, 1660) for i in range(4)] + [(520 + 340 * i, 450) for i in range(5)]
        order = sorted(range(n), key=lambda k: self.B[k][1])
        self.C = [None] * n
        for k, s in zip(order, slots + [(W / 2, 1660)] * n): self.C[k] = (s[0], s[1], 0)
        v = view('card', 0, 0); self.card = LiveCard(1220, v.width / v.height, W / 2, 1085)
    def content(self, t, cv, dy=0):
        self.head.draw(cv, t, dy)
        for k, p in enumerate(self.pills):
            d = k * 1.2
            a = quart_out((t - 6 - k * 1.5) / 14)
            u1 = quart((t - 64 - d) / 40); u2 = quart((t - 150 - d) / 40)
            x = lerp(lerp(self.A[k][0], self.B[k][0], u1), self.C[k][0], u2); y = lerp(lerp(self.A[k][1], self.B[k][1], u1), self.C[k][1], u2)
            r = lerp(lerp(0, self.B[k][2], u1), 0, u2)
            fl = (1 - u2) * u1 * 6 * math.sin((t + k * 9) / 18)
            put(cv, p, x, y + fl + dy, a, .7 + .3 * a, r)
        cu = quart_out((t - 96) / 24)
        if cu > 0: self.card.draw(cv, view('card', t, 0), cu, dy)


class Friends(Section):                                 # three chats filling in, bubble by bubble
    CHATS = [('爸爸', 3, [('o', '喂？能看见我吗？'), ('me', '爸，我只看见你的下巴。'), ('o', '往上挪点……现在呢？'), ('me', '现在是天花板的灯。'), ('o', '也行，那灯是我新换的。')]),
             ('朋友', 9, [('o', '新公司第一天，我坐错了工位。'), ('me', '坐了多久才发现？'), ('o', '一上午，还帮人回了邮件。'), ('me', '那人家没说什么？'), ('o', '他说我回得比他还好。')]),
             ('妈妈', 2, [('o', '吃饭了吗？吃的什么？'), ('me', '泡面加了个蛋。'), ('o', '镜头对着冰箱，我看看。'), ('me', '……里面只有一瓶辣酱。'), ('o', '我明天就寄两箱饺子。')])]
    def __init__(self):
        super().__init__(250, backdrop((255, 242, 236), (236, 236, 255), [(300, 1500, 520, (255, 200, 190)), (2100, 400, 520, (200, 210, 255))]))
        self.head = Headline('爸妈 · 朋友 · 邻居', '人际关系', [(255, 110, 140), (255, 160, 90)], '聊着聊着，话题就去了奇怪的地方')
        fb, fh = font(46, 'Medium'), font(48, 'Black'); self.panels = []
        for k, (who, dk, lines) in enumerate(self.CHATS):
            pw = 720; base = Image.new('RGBA', (pw, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
            bubbles = []; y = 166
            for side, s in lines:
                rows, cur = [], ''
                for ch in s:
                    if d.textlength(cur + ch, font=fb) > 500 and ch not in '，。？！…、': rows.append(cur); cur = ch
                    else: cur += ch
                rows.append(cur); tw = max(d.textlength(r, font=fb) for r in rows); bh = 36 + 62 * len(rows)
                b = Image.new('RGBA', (int(tw) + 56, bh), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
                bd.rounded_rectangle([0, 0, b.width - 1, bh - 1], 34, fill=(240, 238, 246) if side == 'o' else (255, 128, 150))
                for i, r in enumerate(rows): bd.text((28, 16 + 62 * i), r, font=fb, fill=INK if side == 'o' else (255, 255, 255))
                x0 = 36 if side == 'o' else pw - 36 - b.width; bubbles.append((b, x0, y)); y += bh + 40
            h = y + 30; panel = Image.new('RGBA', (pw, h), (0, 0, 0, 0)); pd = ImageDraw.Draw(panel)
            pd.rounded_rectangle([0, 0, pw - 1, h - 1], 44, fill=(255, 255, 255, 236)); pd.text((pw / 2, 70), who, font=fh, fill=INK, anchor='mm')
            pd.line([(40, 124), (pw - 40, 124)], fill=(230, 226, 240), width=3)
            self.panels.append((shadowed(panel, 50)[0], bubbles, 430 + k * 770, 520 + h / 2, (-2, 1.5, -1)[k], h, sticker_img(STK_IMG(f'doll{dk}'), 8)))
        self.me = sticker_img(STK_IMG('doll0'), 9)
    def content(self, t, cv, dy=0):
        self.head.draw(cv, t, dy)
        for k, (panel, bubbles, cx, cy, ang, h, av) in enumerate(self.panels):
            u = quart_out((t - 8 - k * 7) / 22)
            if u <= 0: continue
            p = panel.copy(); pad = (p.width - 720) // 2
            for j, (b, x0, y0) in enumerate(bubbles):
                v = quart_out((t - 34 - (j * 3 + k) * 9) / 12)
                if v <= 0: continue
                bb = b.copy(); bb.putalpha(bb.getchannel('A').point(lambda a: int(a * v))); p.alpha_composite(bb, (pad + x0, pad + y0 + int(18 * (1 - v))))
            put(cv, p, cx, cy + 50 * (1 - u) + dy, u, 1, ang)
            put(cv, av, cx - 320, 520 + 40 * (1 - u) + dy + 6 * math.sin((t + k * 13) / 24), u, .6 + .4 * u, (-6, 5, -4)[k])
        u = quart_out((t - 60) / 16); put(cv, self.me, 2240, 1600 + 7 * math.sin(t / 22) + dy, u, .55 + .45 * u, 6)


class Ending(Section):                                  # back to the desktop, title, fade
    def __init__(self): super().__init__(150, None)
    def frame(self, t):
        im = DESK[1].copy(); put(im, full('idle', 40 + t).resize((GW, GH), Image.BILINEAR), GX + GW / 2, GY + GH / 2)
        u = quart(t / 50); veil = Image.new('RGBA', (W, H), (250, 246, 255, int(150 * quart((t - 40) / 30)))); im.alpha_composite(veil)
        put(im, TITLE[0], W / 2, H / 2 - 120 + 40 * (1 - quart_out((t - 52) / 24)), quart_out((t - 52) / 24))
        put(im, TITLE[1], W / 2, H / 2 + 50 + 30 * (1 - quart_out((t - 62) / 24)), quart_out((t - 62) / 24))
        put(im, TITLE[2], W / 2, H / 2 + 140 + 30 * (1 - quart_out((t - 70) / 24)), quart_out((t - 70) / 24))
        return im
TITLE = [grad_img('Desktop Buddy', 170, [(255, 120, 170), (255, 190, 90), (120, 220, 160), (100, 170, 255), (180, 130, 255)]),
         text_img('住在桌面上的像素小家', 60, INK, 'Bold'), text_img('内容丰富 · 挂机有趣 · 随时互动', 40, SOFT, 'Medium')]


def tree(n): return STK_IMG(n)
OPEN, HOMES = Opening(), Home()
PLACES = Showcase(200, backdrop((228, 248, 242), (226, 238, 255), [(300, 1500, 520, (170, 235, 210)), (2100, 300, 520, (180, 210, 255))]),
                  Headline('公园  商场  码头  酒吧', '出门逛逛', [(70, 210, 170), (90, 170, 255)], '还有一些隐藏地图！'),
                  [(LiveCard(1130, 1288 / 472, 690, 1000, 5), 'place_mall', 0), (LiveCard(1130, 1288 / 472, 1720, 1050, -4), 'place_beach', 0), (LiveCard(1130, 1288 / 472, 1200, 1290, 0), 'place_park', 0)],
                  [(tree('tree2'), 7, 190, 1270, -3), (tree('tree4'), 6, 2220, 1240, 3), (tree('bush0'), 8, 470, 1620, -2), (tree('bench0'), 6, 1010, 1620, 0),
                   (tree('bush2'), 8, 1480, 1630, 3), (tree('bush1'), 8, 1930, 1600, -3), (tree('shrub4'), 9, 760, 1650, 2), (tree('tree3'), 5, 2050, 520, 4), (tree('shrub6'), 9, 330, 560, -3)])
FESTS = Showcase(200, backdrop((255, 240, 246), (230, 240, 255), [(400, 1500, 520, (255, 200, 170)), (2000, 300, 540, (190, 220, 255)), (1200, 900, 420, (210, 245, 220))]),
                 Headline('18 个节日', '每个节日都不一样', [(255, 120, 170), (255, 190, 90), (120, 220, 160), (100, 170, 255), (180, 130, 255)], '怪兽夜戴面具、跳舞日蹦蹦蹦，甜品节吃到爽'),
                 [(LiveCard(1100, 1288 / 472, 720, 900, -5), 'fest_怪兽夜', 0), (LiveCard(1100, 1288 / 472, 1700, 940, 4), 'fest_跳舞日', 0), (LiveCard(1100, 1288 / 472, 1200, 1300, 0), 'fest_甜品节', 0)],
                 [(ART_IMG('pumpkin'), 14, 230, 1180, -8), (ART_IMG('balloon_ghost'), 14, 2170, 1230, 8), (ART_IMG('mirror_ball'), 8, 2190, 560, 6), (ART_IMG('snowman_7'), 8, 210, 560, -6),
                  (ART_IMG('dragon_boat_0'), 5, 460, 1600, -3), (ART_IMG('fest_stall_mooncake'), 5, 1960, 1580, 4), (ART_IMG('lantern_red'), 14, 420, 1350, 6), (ART_IMG('balloon_heart'), 14, 2000, 1330, -6), (ART_IMG('bat'), 10, 1230, 640, 0)])
CARDS, FRIENDS, END = Cards(), Friends(), Ending()
POSTERS = [HOMES, PLACES, FESTS, CARDS, FRIENDS]
X = 20                                                  # frames each poster-to-poster change takes

# timeline: opening, then posters back to back (each change overlaps X frames), ending
T_HOME = OPEN.n
starts, t = [], T_HOME
for s in POSTERS: starts.append(t); t += s.n
T_END = t; N = T_END + END.n


def poster_frame(k, t, dy=0):
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0)); POSTERS[k].content(t, cv, dy); return cv


def render(f):
    if f < T_HOME:
        out = OPEN.frame(f)
        if f >= OPEN.ZOOM1:                             # the desktop gives way to poster 1, the house glides into its card
            u = quart((f - OPEN.ZOOM1) / (T_HOME - OPEN.ZOOM1)); bg = HOMES.bg.copy(); bg.putalpha(int(255 * u)); out.alpha_composite(bg)
            x, y, w, h = OPEN.end_rect(); c = HOMES.card
            tx, ty, tw = c.cx - c.w / 2, c.cy - c.h / 2, c.w
            nw = lerp(w, tw, u); L = full('idle', f).resize((int(nw), int(nw * h / w)), Image.BILINEAR)
            put(out, L, lerp(x + w / 2, c.cx, u), lerp(y + h / 2, c.cy, u))
        return out.convert('RGB')
    if f >= T_END:
        im = END.frame(f - T_END)
        if f < T_END + X:                               # poster 5 fades off the desktop
            u = quart((f - T_END) / X); old = FRIENDS.bg.copy(); old.alpha_composite(poster_frame(4, f - starts[4], -60 * u)); old.putalpha(int(255 * (1 - u))); im.alpha_composite(old)
        g = max(0, (f - (N - 24)) / 24); im = Image.blend(im, Image.new('RGBA', im.size, (0, 0, 0, 255)), g) if g > 0 else im
        return im.convert('RGB')
    k = max(i for i, s in enumerate(starts) if f >= s); t = f - starts[k]; s = POSTERS[k]
    out = s.bg.copy(); out.alpha_composite(poster_frame(k, t))
    nxt = k + 1 < len(POSTERS) and f >= starts[k + 1] - X
    if nxt:                                             # hand over: this poster slides up and fades, the next rises in
        u = quart((f - (starts[k + 1] - X)) / X); n = POSTERS[k + 1]
        out = s.bg.copy(); nb = n.bg.copy(); nb.putalpha(int(255 * u)); out.alpha_composite(nb)
        a = poster_frame(k, t, -70 * u); a.putalpha(a.getchannel('A').point(lambda v: int(v * (1 - u)))); out.alpha_composite(a)
        b = poster_frame(k + 1, 0, 70 * (1 - u)); b.putalpha(b.getchannel('A').point(lambda v: int(v * u))); out.alpha_composite(b)
    return out.convert('RGB')


def main():
    if len(sys.argv) > 5:
        for f in (int(a) for a in sys.argv[5].split(',')): render(f).resize((OW, OH), Image.LANCZOS).save(OUT.parent / f'p43-{f:04d}.png')
        return
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                            '-i', str(MUSIC), '-af', f'afade=t=out:st={N / FPS - 3.5}:d=3.5', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-shortest', str(OUT)], stdin=subprocess.PIPE)
    for f in range(N):
        enc.stdin.write(render(f).resize((OW, OH), Image.BILINEAR).tobytes())
        if f % 150 == 0: print('frame', f, '/', N, flush=True)
    enc.stdin.close(); enc.wait(); print('wrote', OUT, N / FPS, 's')


if __name__ == '__main__':
    main()
