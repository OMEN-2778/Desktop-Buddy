"""Build the owner's isolated, minified summer-bay walk-through (no game save):
旅舍 -> 更衣室 -> 沙滩 -> 水底 as one seamless map. Output: desktop/dist/summer/index.html."""
from pathlib import Path
import sys, io, base64, json, subprocess, tempfile
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


def hero():
    poses = ['stand', 'walkL', 'stand', 'walkR']
    sheet = Image.new('RGBA', (80, 28))
    for i, pose in enumerate(poses):
        image = doll.GIRL.render(bob=i % 2, sway=i % 2).to_image()
        if pose != 'stand':
            legs = image.crop((0, 22, 20, 28))
            image.paste((0, 0, 0, 0), (0, 22, 20, 28))
            for half in (0, 1):
                limb = legs.crop((half * 10, 0, half * 10 + 10, 6))
                image.paste(limb, (half * 10, 21 if half == (i // 2) % 2 else 22), limb)
        sheet.paste(image, (i * 20, 0))
    return sheet


def life():
    """Creatures the page swims back and forth (global coords, from calm_life)."""
    L, S = B.LAND, B.SKY
    out = []

    def add(fr, x, y, rng, v):
        out.append({'f': [uri(fr(0)), uri(fr(1))], 'x': L + x, 'y': S + y, 'r': rng, 'v': v})
    add(SS.turtle, 150, 70, 60, 4)
    add(SS.manta, 480, 150, 80, 5)
    add(lambda f: SS.diver(f, P.hydrangea, P.skin_tan), 330, 60, 50, 6)
    add(lambda f: SS.diver(f, P.coral, P.skin), 700, 120, 60, 5)
    add(SS.jelly, 620, 40, 6, 1)
    add(lambda f: SS.big_fish('eagleray', f), 900, 110, 50, 5)
    import math
    for k in range(14):
        add(lambda f: SS.fish('school', f), 560 + int(22 * math.cos(k * 1.3)), 70 + int(8 * math.sin(k * 1.7)), 70, 9)
    for x, y in ((230, 150), (244, 158), (238, 168), (262, 146), (300, 160)):
        add(lambda f: SS.fish('tang', f), x, y, 24, 7)
    for x, y in ((760, 190), (780, 200), (880, 150)):
        add(lambda f: SS.fish('butterflyfish', f), x, y, 20, 6)
    return out


def main():
    bg = B.bay(clouds=False, life=False)
    data = {
        'bg': uri(bg), 'W': B.GW, 'H': B.GH, 'WL': B.WL, 'ground': B.GROUND,
        'lodgeDoor': SI.LODGE_DOOR, 'cabana': {k: 342 + v for k, v in SI.CABANA_DOORS.items()},
        'zones': [[0, '旅舍'], [342, '更衣室'], [B.PRE, '沙滩'], [B.LAND, '海湾'], [B.LAND + 380, '沉船谷']],
        'inside': uri(ROOT / 'art/out/concept/summer_lodge_inside.png'),
        'clouds': [uri(BE.cloud(i)) for i in range(3)], 'hero': uri(hero()), 'life': life(),
    }
    js = (ROOT / 'prototype/summer/viewer.js').read_text().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    with tempfile.TemporaryDirectory(prefix='buddy-summer-preview-') as temp:
        source, target = Path(temp) / 'viewer.js', Path(temp) / 'viewer.min.js'
        source.write_text(js)
        subprocess.run(['node', str(ROOT / 'desktop/node_modules/terser/bin/terser'), str(source), '--compress', '--mangle', 'toplevel', '--output', str(target)], check=True)
        script = target.read_text().replace('</script', '<\\/script')
    html = (ROOT / 'prototype/summer/index.src.html').read_text().replace('/*__SCRIPT__*/', script)
    out = ROOT / 'desktop/dist/summer/index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(out, round(len(html) / 1024), 'KiB')


if __name__ == '__main__':
    main()
