"""Build the owner's isolated, minified summer-bay walk-through (no game save):
旅舍 -> 更衣室 -> 沙滩 -> 水底 as one seamless map. Output: desktop/dist/summer/index.html."""
from pathlib import Path
import os, sys, io, base64, json, subprocess, tempfile
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'art/src/concept')]
import summer_bay as B
import summer_sea as SS
import summer_isle as SI
import beach as BE
import doll
from pixelkit import Sprite, P


def uri(im):
    if isinstance(im, Sprite):
        im = im.to_image()
    if isinstance(im, Path):
        im = Image.open(im)
    out = io.BytesIO()
    im.save(out, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(out.getvalue()).decode()


def outfit(kind, **frame):
    """Buddy (the GIRL preset) in her clothes, a bikini or a wetsuit. Swimwear is
    drawn on the bare doll: the clothing layers are skipped, legs and bare feet
    redrawn, then a blue bikini or a slate wetsuit with a hydrangea stripe."""
    from dataclasses import replace
    if kind == 'clothes':
        return doll.GIRL.render(**frame).to_image()
    d = replace(doll.GIRL, top_style='tank')
    s = Sprite(20, 28)
    for key, draw in d.layers(**frame):
        if key.split('/')[0] not in ('top', 'bottom', 'socks', 'shoes', 'bib'):
            draw(s)
    sk = d.skin
    s.px[22:28] = 0
    for x0 in (7, 11):
        for y in range(22, 27):
            s.set(x0, y, sk[2]).set(x0 + 1, y, sk[1])
        s.set(x0 - (1 if x0 == 7 else 0), 26, sk[1])
        s.hline(x0 - 1 if x0 == 7 else x0, x0 + 1 if x0 == 7 else x0 + 2, 27, sk[0])
    if kind == 'bikini':
        C = P.blue
        for x in list(range(6, 9)) + list(range(11, 14)):
            s.set(x, 17, C[3]).set(x, 18, C[2])
        s.hline(9, 10, 17, C[1])
        s.hline(6, 13, 22, C[2]).hline(7, 12, 23, C[1])
        s.set(6, 22, C[3])
    else:
        from pixelkit.core import rgba
        skin = [tuple(rgba(c)) for c in sk]
        S2 = P.slate
        for y in range(16, 28):
            for x in range(20):
                c = tuple(s.px[y, x])
                if c in skin and not (y >= 20 and (x <= 4 or x >= 15)):   # hands stay bare
                    s.set(x, y, S2[min(4, skin.index(c))])
        s.hline(5, 14, 17, P.hydrangea[2])
        s.vline(9, 18, 21, P.hydrangea[3])
    return s.to_image()


CELL = 28


def hero_sheet(kind):
    """Cells of 28x28: 0-3 walk, 4-5 float (arm stroke), 6-7 dive (kick), 8 lie."""
    sheet = Image.new('RGBA', (CELL * 9, CELL))
    walk = []
    for i in range(4):
        image = outfit(kind, bob=i % 2, sway=i % 2)
        if i % 2:
            legs = image.crop((0, 22, 20, 28))
            image.paste((0, 0, 0, 0), (0, 22, 20, 28))
            for half in (0, 1):
                limb = legs.crop((half * 10, 0, half * 10 + 10, 6))
                image.paste(limb, (half * 10, 21 if half == (i // 2) % 2 else 22), limb)
        walk.append(image)
        sheet.paste(image, (i * CELL + 4, 0))
    for f in (0, 1):
        sheet.paste(outfit(kind, bob=f, wave=f) if kind != 'clothes' else walk[0], ((4 + f) * CELL + 4, 0))
        rot = walk[1 + 2 * f].rotate(-90, expand=True)                 # head forward (right), legs kicking
        sheet.paste(rot, ((6 + f) * CELL, 8))
    sheet.paste(walk[0].rotate(90, expand=True), (8 * CELL, 8))          # lying, head on the backrest (left)
    return sheet


def solid_mask():
    """Where Buddy cannot go: under the ground line, the reef rocks (pinnacle,
    boulders; the arch keeps its hole), the sea stack. Alpha = solid."""
    import numpy as np
    m = np.zeros((B.GH, B.GW), bool)
    for x in range(B.GW):
        m[B.GROUND[x]:, x] = True
    terr = SS.terrain().px[..., 3] > 0
    m[B.SKY:, B.LAND:] |= terr
    m[:, B.STACK[0] + 8:] |= np.arange(B.GH)[:, None] > B.WL - 40
    out = np.zeros((B.GH, B.GW, 4), np.uint8)
    out[m] = (0, 0, 0, 255)
    return Image.fromarray(out, 'RGBA')


HOTSPOT_TEXT = {
    'turtle_rock': '海龟在这块礁石上歇脚，让小鱼帮它清理壳。慢慢游在旁边，它一点也不怕。',
    'clam': '巨蚌张开了一条缝……里面有一颗小小的珍珠！',
    'coral_photo': '咔嚓！和珊瑚花园合影一张，小鱼被吓散又游了回来。',
    'octopus_den': '洞里伸出一只触手，章鱼探头看了看，身体从红色变成了沙色。',
    'wreck_chest': '沉船的船舱里有个旧箱子：几枚金币，还有一个装着信的漂流瓶。',
    'kelp_forest': '海藻轻轻摇摆，一群小鱼躲在里面捉迷藏。',
    'pinnacle': '绕着珊瑚尖塔转一圈，鱼群也跟着一起打转。',
    'arch': '从熔岩拱门中间穿过去了！',
    'tiki': '对着沉没的提基像许了个愿。',
    'eel_crevice': '石缝里的海鳗探出头，又害羞地缩了回去。',
    'seal_rock': '夏威夷僧海豹在礁石边打盹，翻了个身继续睡。',
}
LIFE_TEXT = {
    'turtle': '绿海龟（honu）慢悠悠地划水，看了你一眼。',
    'manta': '蝠鲼像一张大毯子一样从头顶滑过去。',
    'diver': '潜水员朝你比了个 OK 的手势。',
    'jelly': '小水母一张一合地漂着，别碰它哦。',
    'eagleray': '斑点鹞鲼扇着“翅膀”飞过沙地。',
    'school': '银色的鱼群“哗”地一下散开，又聚了回来。',
    'tang': '黄色的刺尾鲷成群结队，在珊瑚之间穿梭。',
    'butterflyfish': '蝴蝶鱼两两成对，在珊瑚边上啄食。',
}


def life():
    """Creatures the page swims back and forth (global coords, from calm_life)."""
    L, S = B.LAND, B.SKY
    out = []

    def add(fr, x, y, rng, v, kind=None):
        out.append({'f': [uri(fr(0)), uri(fr(1))], 'x': L + x, 'y': S + y, 'r': rng, 'v': v, 'k': kind})
    add(SS.turtle, 150, 70, 60, 4, 'turtle')
    add(SS.manta, 480, 150, 80, 5, 'manta')
    add(lambda f: SS.diver(f, P.hydrangea, P.skin_tan), 330, 60, 50, 6, 'diver')
    add(lambda f: SS.diver(f, P.coral, P.skin), 700, 120, 60, 5, 'diver')
    add(SS.jelly, 620, 40, 6, 1, 'jelly')
    add(lambda f: SS.big_fish('eagleray', f), 900, 110, 50, 5, 'eagleray')
    import math
    for k in range(14):
        add(lambda f: SS.fish('school', f), 560 + int(22 * math.cos(k * 1.3)), 70 + int(8 * math.sin(k * 1.7)), 70, 9, 'school')
    for x, y in ((230, 150), (244, 158), (238, 168), (262, 146), (300, 160)):
        add(lambda f: SS.fish('tang', f), x, y, 24, 7, 'tang')
    for x, y in ((760, 190), (780, 200), (880, 150)):
        add(lambda f: SS.fish('butterflyfish', f), x, y, 20, 6, 'butterflyfish')
    return out


def main():
    bg = B.bay(clouds=False, life=False)
    data = {
        'bg': uri(bg), 'W': B.GW, 'H': B.GH, 'WL': B.WL, 'ground': B.GROUND,
        'lodgeDoor': SI.LODGE_DOOR, 'cabana': {k: 342 + v for k, v in SI.CABANA_DOORS.items()},
        'zones': [[0, '旅舍'], [342, '更衣室'], [B.PRE, '沙滩'], [B.LAND, '海湾'], [B.LAND + 380, '沉船谷']],
        'inside': uri(ROOT / 'art/out/concept/summer_lodge_inside.png'),
        'clouds': [uri(BE.cloud(i)) for i in range(3)], 'life': life(),
        'heroes': {k: uri(hero_sheet(k)) for k in ('clothes', 'bikini', 'wetsuit')},
        'solid': uri(solid_mask()),
        'loungers': [[B.PRE + 184 + 13, B.GROUND[B.PRE + 190] - 7], [B.PRE + 214 + 13, B.GROUND[B.PRE + 218] - 7]],
        'hotspots': [{'id': h['id'], 'name': h['name'], 'text': HOTSPOT_TEXT[h['id']], 'x': B.LAND + h['x'],
                      'y': min(B.SKY + h['y'], B.GROUND[B.LAND + h['x']] - 6)} for h in SS.HOTSPOTS],
        'lifeText': LIFE_TEXT, 'seal': [uri(SS.seal(0)), uri(SS.seal(1))], 'sealAt': [B.STACK[0] + 4, B.WL - 4],
        'seaEnd': B.STACK[0] - 6,
    }
    js = (ROOT / 'prototype/summer/viewer.js').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    with tempfile.TemporaryDirectory(prefix='buddy-summer-preview-') as temp:
        source, target = Path(temp) / 'viewer.js', Path(temp) / 'viewer.min.js'
        source.write_text(js)
        if os.environ.get('BUDDY_NO_MINIFY'):
            target.write_text(js)                                     # debugging only; the public build is minified
        else:
            subprocess.run(['node', str(ROOT / 'desktop/node_modules/terser/bin/terser'), str(source), '--compress', '--mangle', 'toplevel', '--output', str(target)], check=True)
        script = target.read_text().replace('</script', '<\\/script')
    html = (ROOT / 'prototype/summer/index.src.html').read_text().replace('/*__SCRIPT__*/', script)
    out = ROOT / 'desktop/dist/summer/index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(out, round(len(html) / 1024), 'KiB')


if __name__ == '__main__':
    main()
