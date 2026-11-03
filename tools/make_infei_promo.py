#!/usr/bin/env python3
"""茵菲谷 promo, part 2: a 4:3 motion-graphics edit of the clips from tools/make_infei_promo.js, in the look of
the 4:3 promo and the posters (pastel gradients, gradient headlines, the game in white rounded cards, die-cut
pixel stickers). It tells the update as a little story: mom's letter -> the airport -> the flight -> 茵菲谷 ->
mom's welcome -> sowing, growth and rain -> orchard and ranch -> four seasons -> the farmhouse -> three side
quests -> the 任务 panel and its replay -> the tablet -> evening on the farm. Every move eases (quartic, or a
soft overshoot on entry); headlines rise in character by character.

  python3 tools/make_infei_promo.py CLIP_DIR MUSIC.mp3 OUT.mp4 [preview seconds,...]
"""
import math, subprocess, sys, random
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
from infei_marketing import *

W, H, FPS = 1440, 1080, 30
CL = Clips(sys.argv[1]); MUSIC, OUT = Path(sys.argv[2]), Path(sys.argv[3])
PREVIEW = [float(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
CFPS = CL.meta['fps']


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def quart(x): x = clamp(x); return 8 * x ** 4 if x < .5 else 1 - (-2 * x + 2) ** 4 / 2
def out_back(x, s=1.4): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def out_quart(x): return 1 - (1 - clamp(x)) ** 4


_cache = {}
def clip(name, t, ui=False, speed=1.):
    i = int(t * CFPS * speed); key = (name, min(i, CL.n(name) - 1), ui)
    if key not in _cache:
        if len(_cache) > 40: _cache.clear()
        _cache[key] = CL.frame(name, i, ui)
    return _cache[key]


def lift_env(t, dur, tin=.55, tout=.4, delay=0.):
    """(progress in, progress out) for an element living through a section."""
    return out_back((t - delay) / tin), quart((t - (dur - tout)) / tout)


def put_card(bg, img, width, cx, cy, t, dur, delay=0., angle=0, tin=.6, ui=False, rise=90):
    pin, pout = lift_env(t, dur, tin, .4, delay)
    if pin <= 0: return
    a = clamp((t - delay) / (tin * .6)) * (1 - pout)
    if a <= 0: return
    k = (.86 + .14 * min(pin, 1.06)) * (1 - .06 * pout)
    c = card(img, width * k, radius=int(26 * k), border=max(4, int(8 * k)), angle=angle, smooth=True)
    place(bg, c, cx, cy + rise * (1 - min(pin, 1)) - 30 * pout, shadow=70, alpha=a)


STK = {}
EVENTS, SEEN, NOW = [], set(), [0., 0]   # sound cues: (seconds, sound, gain); NOW = [absolute time, section]
def cue(key, snd, g=.5, at=None):
    k = (NOW[1],) + key
    if k not in SEEN: SEEN.add(k); EVENTS.append((NOW[0] if at is None else at, snd, g))

def stk(name, k, rim=7):
    key = (name, k)
    if key not in STK: STK[key] = sticker_img(art(name), k, rim)
    return STK[key]


def put_sticker(bg, name, k, cx, cy, t, dur, delay=0., angle=0, bob=8, phase=0.):
    pin, pout = lift_env(t, dur, .5, .35, delay)
    if pin <= 0 or pout >= 1: return
    cue(('stk', name, delay), 'infei-pop', .22)
    s = stk(name, k); sc = max(.05, min(pin, 1.12)) * (1 - pout)
    if sc <= .05: return
    im = s.resize((max(1, int(s.width * sc)), max(1, int(s.height * sc))), Image.BICUBIC)
    if angle or True: im = im.rotate(angle + 4 * math.sin(t * 1.3 + phase), Image.BICUBIC, expand=True)
    place(bg, im, cx, cy + bob * math.sin(t * 2.1 + phase), shadow=55, blur=10, drop=10)


_heads = {}
def headline(bg, t, dur, kicker, big, sub, cols, y=150, bigpx=92):
    key = (kicker, big, sub)
    if key not in _heads:
        bi = grad_text_img(big, bigpx, cols); f = font(bigpx)
        xs = [0] + [int(f.getlength(big[:i + 1])) for i in range(len(big))]
        _heads[key] = (text_img(kicker, 34, SOFT, 'Bold') if kicker else None, bi, xs, text_img(sub, 30, SOFT, 'Medium') if sub else None)
    ki, bi, xs, si = _heads[key]
    pout = quart((t - (dur - .4)) / .4); a_all = 1 - pout; dy_out = -24 * pout
    if ki:
        p = out_quart(t / .5); im = ki.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * p * a_all)))
        bg.alpha_composite(im, (int(W / 2 - im.width / 2), int(y - bi.height / 2 - im.height - 2 + 20 * (1 - p) + dy_out)))
    x0 = W / 2 - bi.width / 2
    for i in range(len(xs) - 1):           # characters rise in out of nothing, one after another
        p = out_back((t - .15 - i * .07) / .55, 1.2)
        if p <= 0: continue
        sl = bi.crop((xs[i], 0, min(bi.width, xs[i + 1] + 8), bi.height))
        al = clamp((t - .15 - i * .07) / .3) * a_all
        sl.putalpha(sl.getchannel('A').point(lambda v: int(v * al)))
        bg.alpha_composite(sl, (int(x0 + xs[i]), int(y - bi.height / 2 + 40 * (1 - min(p, 1)) + dy_out)))
    if si:
        p = out_quart((t - .5 - len(big) * .07) / .5); im = si.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * p * a_all)))
        bg.alpha_composite(im, (int(W / 2 - im.width / 2), int(y + bi.height / 2 + 4 + 16 * (1 - p) + dy_out)))


def put_img(bg, im, cx, cy, t, dur, delay=0., angle=0, shadow=50, tin=.5):
    pin, pout = lift_env(t, dur, tin, .35, delay)
    if pin <= 0 or pout >= 1: return
    sc = max(.05, min(pin, 1.08)) * (1 - .1 * pout); a = clamp((t - delay) / .25) * (1 - pout)
    m = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if angle: m = m.rotate(angle, Image.BICUBIC, expand=True)
    place(bg, m, cx, cy, shadow=shadow, blur=12, drop=12, alpha=a)


# ------------------------------------------------------------------ sections
BG = {}
def bgfor(key, c0, c1, blobs):
    if key not in BG: BG[key] = backdrop(W, H, c0, c1, blobs)
    return BG[key]


PINK, LAV, MINT, SKY, PEACH, BUTTER = (255, 232, 240), (232, 226, 255), (222, 246, 236), (222, 236, 255), (255, 236, 222), (255, 247, 220)
G_SPRING = [(245, 120, 160), (190, 110, 230)]; G_GREEN = [(70, 180, 120), (60, 160, 200)]; G_WARM = [(240, 140, 60), (230, 90, 120)]
G_BLUE = [(90, 140, 230), (150, 100, 230)]; G_GOLD = [(225, 160, 40), (230, 110, 70)]
LETTER = ['我和你爸在茵菲谷承包了一小片农庄，', '有菜地、果园，还有几只鸡。', '春天正是播种的时候，想请你来帮帮忙。', '机场有去农庄的航班，票我们买好了。', '你的房间收拾好了，被子也晒过了。等你来！']


def s_letter(bg, t, d):
    headline(bg, t, d, '某天，信箱里来了一封信', '妈妈来信了', '', G_SPRING)
    put_card(bg, clip('letter', t, ui=True), 900, W / 2 - 150, 650, t, d, .1)
    put_sticker(bg, 'quest_icon_letter', 7, 1170, 330, t, d, .9, -8)
    # the letter unfolds and its lines write themselves in
    p = out_back((t - 1.5) / .6)
    if p > 0:
        n = clamp((t - 1.9) / 2.2) * sum(len(l) for l in LETTER); shown = []
        for l in LETTER:
            shown.append(l[:max(0, int(n))]); n -= len(l)
        im = letter_img([s for s in shown], 22, '妈妈的信', width=520)
        put_img(bg, im, 1080, 690, t, d, 1.5, -3)


def s_airport(bg, t, d):
    headline(bg, t, d, '机票买好了', '出发，去茵菲谷', '', G_BLUE)
    put_card(bg, clip('airport', t), 1150, W / 2, 620, t, d, .1)
    p = quart((t - .9) / 2.6)
    if 0 < p < 1:
        pl = stk('airport_plane', 3, 6); x = -200 + (W + 400) * p; y = 380 - 120 * p
        dr = ImageDraw.Draw(bg)
        for k in range(14):
            tx = x - 120 - k * 34
            if tx < -50: break
            dr.ellipse([tx - 5, y + 30 + k * 2.7 - 5, tx + 5, y + 30 + k * 2.7 + 5], fill=(255, 255, 255, int(200 * (1 - k / 14))))
        place(bg, pl.rotate(6, Image.BICUBIC, expand=True), x, y, shadow=40, blur=14, drop=40)


def s_flight(bg, t, d):
    put_card(bg, clip('flight', t, speed=1.0), 1260, W / 2, 560, t, d, 0, tin=.4)
    put_img(bg, pill_img('飞往  茵菲谷', 34, (90, 120, 200)), W / 2, 140, t, d, .3)


def s_title(bg, t, d):
    name = 'fields' if t < 3.2 else 'tulips'; lt = t if t < 3.2 else t - 3.2
    im = clip(name, lt)
    if 3.0 < t < 3.4:                                   # a soft cross-dissolve between the two fields
        a = clamp((t - 3.0) / .4); im = Image.blend(clip('fields', t), clip('tulips', 0), a)
    put_card(bg, im, 1300, W / 2, 660, t, d, .05)
    headline(bg, t, d, '一座会过四季的山谷', '茵菲谷', '油菜花、风车、小溪，还有妈妈的农庄', G_SPRING, y=180, bigpx=130)
    put_sticker(bg, 'quest_icon_flower', 6, 160, 380, t, d, 1.2, -10)
    put_sticker(bg, 'quest_icon_windmill', 6, 1290, 360, t, d, 1.4, 8, phase=1)


def s_welcome(bg, t, d):
    headline(bg, t, d, '妈妈在门口等你', '欢迎来到农庄', '先看房间，还是先去地里？', G_WARM)
    put_card(bg, clip('welcome', t * 1.5, ui=True), 1180, W / 2, 660, t, d, .1)
    put_sticker(bg, 'quest_icon_house', 6, 150, 330, t, d, .8, -8)
    put_sticker(bg, 'quest_icon_heart', 5, 1300, 340, t, d, 1.0, 8, phase=2)


CROPS = ['carrot', 'strawberry', 'cabbage', 'potato', 'tomato', 'corn', 'watermelon', 'pepper', 'pumpkin', 'radish', 'eggplant']
def s_farm(bg, t, d):
    headline(bg, t, d, '春种 · 夏长 · 秋收', '自己种菜', '11 种作物，按季节播种，熟了就收', G_GREEN)
    parts = [('sow', 0, 1.8), ('water', 1.8, 3.3), ('grow', 3.3, 6.0), ('rain', 6.0, d)]
    for name, a, b in parts:
        if a <= t < b:
            lt = t - a; sp = CL.n(name) / CFPS / (b - a) if name == 'grow' else 1
            im = clip(name, lt, speed=sp)
            if lt < .18 and a > 0:                     # a quick white flash between the shots
                im = Image.blend(im, Image.new('RGBA', im.size, (255, 255, 255, 255)), 1 - lt / .18)
            put_card(bg, im, 1120, W / 2, 640, t, d, .1)
    for i, c in enumerate(CROPS):                      # the seeds pop up around the field, one by one
        ang = -math.pi * .95 + i * (math.pi * .9 / (len(CROPS) - 1)) if i < 6 else math.pi * .05 + (i - 6) * (math.pi * .9 / 4)
        x = W / 2 + math.cos(ang) * 640; y = 650 + math.sin(ang) * 330
        put_sticker(bg, f'farm_icon_{c}', 5, x, y, t, d, .6 + i * .12, phase=i)
    if t > 6.2: put_img(bg, pill_img('下雨天，地自己就浇好了', 30, (70, 130, 200)), W / 2, 965, t, d, 6.2)
    elif t > 3.4: put_img(bg, pill_img('浇过水的一天，长一天', 30, (60, 150, 90)), W / 2, 965, t, 6.0, 3.4)


def s_ranch(bg, t, d):
    headline(bg, t, d, '果园 · 牧场', '养鸡养羊养牛', '摸摸它们，会越来越亲', G_GOLD)
    put_card(bg, clip('orchard', t), 760, 470, 600, t, d, .15, -3)
    put_card(bg, clip('ranch', t), 760, 970, 740, t, d, .45, 3)
    for i, (n, k, x, y) in enumerate([('spring_cow_0', 4, 1230, 420), ('spring_sheep_0', 4, 130, 860), ('spring_hen_0', 6, 640, 960)]):
        put_sticker(bg, n, k + 1, x, y, t, d, .9 + i * .2, phase=i)
    for i, (n, x, y) in enumerate([('farm_icon_peach', 210, 380), ('farm_icon_egg', 760, 400), ('farm_icon_milk', 1340, 620), ('farm_icon_wool', 330, 1000)]):
        put_sticker(bg, n, 5, x, y, t, d, 1.3 + i * .15, phase=i + 3)
    for k in range(5):                                 # hearts float up from the cow
        u = (t - 1.6 - k * .45) % 2.2
        if t > 1.6 + k * .45 and t < d - .4:
            hs = stk('farm_icon_heart', 3); a = clamp(1 - u / 2.2)
            place(bg, hs, 1060 + 40 * math.sin(k * 2 + u * 3), 640 - u * 120, shadow=0, alpha=a)


SEASONS = [('spring', '春', (245, 120, 160)), ('summer', '夏', (60, 170, 110)), ('autumn', '秋', (225, 130, 50)), ('winter', '冬', (100, 140, 220))]
def s_seasons(bg, t, d):
    headline(bg, t, d, '春 · 夏 · 秋 · 冬', '四季轮转', '冬天下雪，菜地也要歇一歇', G_BLUE)
    seg = 1.15; i = min(3, int(max(0, t - .3) / seg)); lt = max(0, t - .3) - i * seg
    cur = clip('season_' + SEASONS[i][0], lt)
    if i > 0 and lt < .5:                              # a round wipe opens the next season from the middle
        prev = clip('season_' + SEASONS[i - 1][0], lt + seg)
        r = out_quart(lt / .5) * math.hypot(cur.width, cur.height) / 2
        m = Image.new('L', cur.size, 0); ImageDraw.Draw(m).ellipse([cur.width / 2 - r, cur.height / 2 - r, cur.width / 2 + r, cur.height / 2 + r], fill=255)
        cur = Image.composite(cur, prev, m)
    put_card(bg, cur, 1160, W / 2, 640, t, d, .1)
    for k, (key, ch, col) in enumerate(SEASONS):
        on = k == i; im = pill_img(ch, 40 if on else 30, col if on else (170, 165, 190))
        put_img(bg, im, W / 2 - 240 + k * 160, 960, t, d, .4 + k * .1)


def s_house(bg, t, d):
    headline(bg, t, d, '忙完了，回屋歇歇', '农舍里过日子', '睡觉、洗澡、做饭，都在自己家', G_WARM)
    put_card(bg, clip('home_sleep', t), 760, 480, 560, t, d, .15, -2)
    put_card(bg, clip('home_cook', t), 760, 960, 800, t, d, .45, 2)
    put_sticker(bg, 'quest_icon_moon', 5, 1200, 420, t, d, .9)
    put_sticker(bg, 'quest_icon_stew', 5, 220, 900, t, d, 1.1, phase=2)


QUESTS = [('q_mill', '风车里的怪声', 'quest_icon_suona', (225, 160, 40)), ('q_apo', '溪边的阿婆', 'quest_icon_letter', (100, 140, 220)), ('q_rabbit', '菜地里的脚印', 'quest_icon_footprints', (150, 110, 80))]
def s_quests(bg, t, d):
    headline(bg, t, d, '风车、小溪、菜地', '茵菲谷的小故事', '有好笑的，也有让人想家的', G_SPRING)
    seg = (d - .3) / 3; i = min(2, int(max(0, t - .3) / seg)); lt = max(0, t - .3) - i * seg
    name, title, icon, col = QUESTS[i]
    sp = CL.n(name) / CFPS / seg
    im = clip(name, lt, ui=True, speed=sp * .95)
    put_card(bg, im, 1140, W / 2, 660, lt + (0 if i == 0 else .6), seg + (0 if i == 0 else .6) if i < 2 else d - .3 - 2 * seg + .6, 0 if i == 0 else 0)
    put_img(bg, pill_img(title, 34, col), W / 2 + 260, 345, lt, seg if i < 2 else d - .3 - 2 * seg, .25)
    put_sticker(bg, icon, 6, W / 2 + 470, 330, lt, seg if i < 2 else d - .3 - 2 * seg, .35, -8)


def s_panel(bg, t, d):
    headline(bg, t, d, '做过的事，都记得', '任务回顾', '对话、选择、写过的信，随时翻看', G_GOLD)
    put_card(bg, clip('panel', t, ui=True, speed=CL.n('panel') / CFPS / (d - .2)), 1120, W / 2, 660, t, d, .1)
    put_sticker(bg, 'quest_icon_scroll', 6, 170, 360, t, d, .9, -8)
    put_sticker(bg, 'quest_icon_book', 5, 1290, 900, t, d, 1.1, phase=1)


def s_tablet(bg, t, d):
    headline(bg, t, d, '丢丢平板电脑', '仓库 · 送礼 · 每日操盘', '收来的菜和蛋，卖掉还是送人？', G_GREEN, bigpx=80)
    put_card(bg, clip('tablet', t, ui=True, speed=CL.n('tablet') / CFPS / (d - .2)), 1060, W / 2, 660, t, d, .1)
    for i, (n, x, y) in enumerate([('farm_icon_coin', 170, 470), ('farm_icon_basket', 1280, 450), ('farm_icon_gift', 200, 900), ('farm_icon_chart', 1270, 900)]):
        put_sticker(bg, n, 6, x, y, t, d, .7 + i * .15, phase=i)


def s_end(bg, t, d):
    put_card(bg, clip('ending', t, speed=CL.n('ending') / CFPS / d), 1240, W / 2, 600, t, d + 9, .05)
    headline(bg, t, d + 9, '', '茵菲谷', '', G_SPRING, y=170, bigpx=130)
    put_img(bg, pill_img('测试版现已开放', 34, (230, 110, 150)), W / 2, 960, t, d + 9, 1.4)
    b = brand_img(W); bg.alpha_composite(b, (int(W / 2 - b.width / 2), H - 70))
    if t > d - .8:
        f = Image.new('RGBA', (W, H), (255, 255, 255, int(255 * quart((t - (d - .8)) / .8)))); bg.alpha_composite(f)


SECTION_SFX = {   # (seconds into the section, sound, gain)
    's_letter': [(.9, 'infei-letter', .6), (1.5, 'infei-letter', .5)] + [(1.9 + k * .09, 'infei-type', .25) for k in range(26)],
    's_airport': [(.3, 'infei-chime', .5), (.9, 'infei-plane', .7)],
    's_flight': [(0, 'infei-cabin', .6)],
    's_title': [(.2, 'infei-chime', .55), (1.5, 'birds', .5)],
    's_welcome': [(.6, 'ui-message', .4), (2.0, 'ui-message', .4), (3.4, 'ui-message', .4)],
    's_farm': [(.4, 'infei-sow', .7), (2.0, 'watering', .6), (3.6, 'infei-harvest', .45), (4.6, 'infei-harvest', .45), (5.5, 'infei-harvest', .5), (6.0, 'rain-soft-loop-cc0', .5)],
    's_ranch': [(1.0, 'infei-moo', .55), (2.2, 'infei-cluck', .5), (3.3, 'infei-baa', .5), (4.2, 'infei-pat', .4)],
    's_seasons': [(.3 + 1.15 * k, 'infei-whoosh', .3) for k in range(1, 4)] + [(3.8, 'wind', .35)],
    's_house': [(.6, 'fabric', .5), (1.6, 'cook', .45)],
    's_quests': [(.4, 'infei-quest', .45), (.9, 'infei-suona', .55), (3.0, 'infei-quest', .45), (3.4, 'infei-letter', .45), (5.6, 'infei-quest', .45), (6.0, 'real-night-cc0', .4)],
    's_panel': [(.5, 'ui-open', .5), (1.2, 'infei-letter', .45), (2.4, 'page', .45)],
    's_tablet': [(.5, 'ui-open', .5), (1.2, 'infei-coin', .5), (2.2, 'infei-coin', .5)],
    's_end': [(.4, 'infei-done', .6), (1.4, 'birds', .4)],
}
SECTIONS = [  # (draw, seconds, background colours, blobs)
    (s_letter, 5.6, PINK, LAV), (s_airport, 4.4, SKY, LAV), (s_flight, 3.4, SKY, (236, 244, 255)), (s_title, 6.2, PINK, MINT),
    (s_welcome, 5.2, PEACH, PINK), (s_farm, 8.8, MINT, BUTTER), (s_ranch, 5.6, BUTTER, PEACH), (s_seasons, 5.2, SKY, MINT),
    (s_house, 4.8, PEACH, LAV), (s_quests, 8.4, LAV, PINK), (s_panel, 4.6, BUTTER, LAV), (s_tablet, 4.0, MINT, SKY), (s_end, 4.8, PINK, LAV)]
STARTS = []; acc = 0.
for s in SECTIONS: STARTS.append(acc); acc += s[1]
TOTAL = acc
BLOBS = [(.15, .2, .22, (255, 255, 255)), (.85, .8, .25, (255, 255, 255)), (.8, .15, .18, (255, 220, 240)), (.2, .85, .2, (220, 240, 255))]


def render(t):
    i = max(k for k, s in enumerate(STARTS) if s <= t) if t >= 0 else 0
    fn, dur, c0, c1 = SECTIONS[i]; lt = t - STARTS[i]; NOW[0], NOW[1] = t, i
    cue(('enter',), 'infei-whoosh', .35)
    for (a, snd, g) in SECTION_SFX.get(fn.__name__, []): cue(('fx', a, snd), snd, g, STARTS[i] + a) if lt >= a else None
    bg = bgfor(i, c0, c1, BLOBS).copy()
    if i > 0 and lt < .5:                              # backgrounds melt into each other
        prev = bgfor(i - 1, SECTIONS[i - 1][2], SECTIONS[i - 1][3], BLOBS); bg = Image.blend(prev, bg, quart(lt / .5))
    if fn is not s_end:
        b = brand_img(W); bg.alpha_composite(b, (int(W / 2 - b.width / 2), H - 62))
    fn(bg, lt, dur)
    return bg.convert('RGB')


if PREVIEW:
    for s in PREVIEW: render(s).save(OUT.with_name(f'{OUT.stem}_{s:05.1f}.jpg'), quality=88)
    sys.exit()
N = int(TOTAL * FPS)
import numpy as np, tempfile
SR = 48000
def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)
AUD = [ROOT / 'AUDIO_LIBRARY/INFEI/SFX', ROOT / 'AUDIO_LIBRARY/SFX/game', ROOT / 'AUDIO_LIBRARY/SFX/processed']
def sfx(name):
    for d in AUD:
        if (d / f'{name}.mp3').exists(): return decode(d / f'{name}.mp3')
    raise FileNotFoundError(name)
with tempfile.TemporaryDirectory() as tmp:
    vid = Path(tmp) / 'v.mp4'
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', str(vid)], stdin=subprocess.PIPE)
    for f in range(N):
        ff.stdin.write(render(f / FPS).tobytes())
        if f % 300 == 0: print(f'{f}/{N}', flush=True)
    ff.stdin.close(); ff.wait()
    L = int(TOTAL * SR); mixd = np.zeros((L, 2), np.float32)
    mus = decode(MUSIC)[:L]; n = len(mus); fade = np.ones(n, np.float32)
    fade[:int(.6 * SR)] = np.linspace(0, 1, int(.6 * SR)); k = int(3.2 * SR); fade[-k:] = np.linspace(1, 0, k)
    mixd[:n] += mus * fade[:, None] * .72
    cache = {}
    for at, name, g in sorted(EVENTS):
        if name not in cache: cache[name] = sfx(name)
        a = cache[name]; k = int(at * SR); m = min(len(a), L - k, int(4.5 * SR))
        if m > 0:
            env = np.ones(m, np.float32); r = min(m, int(.4 * SR)); env[-r:] = np.linspace(1, 0, r)
            mixd[k:k + m] += a[:m] * env[:, None] * g
    mixd = np.tanh(mixd * 1.1) / 1.1
    wav = Path(tmp) / 'a.wav'
    from scipy.io.wavfile import write as wwrite
    wwrite(wav, SR, (mixd * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(vid), '-i', str(wav), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(OUT)], check=True)
print('done', OUT, round(TOTAL, 1), 's,', len(EVENTS), 'sound cues')
