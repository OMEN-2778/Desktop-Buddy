"""Review board for art/src/concept/quest_icons.py -> docs/design/quest-icons-board.png (4x, labelled)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys
ROOT = Path(__file__).resolve().parents[1]; sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'art/src/concept')]
import quest_icons
names = list(quest_icons.ICONS); cols, S = 9, 4; cell = 16 * S + 24
try: font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 12)
except OSError: font = ImageFont.load_default()
b = Image.new('RGB', (cols * cell + 16, ((len(names) + cols - 1) // cols) * (cell + 16) + 16), '#f7f6fb'); d = ImageDraw.Draw(b)
for i, n in enumerate(names):
    im = Image.open(ROOT / f'art/out/concept/quest_icon_{n}.png').convert('RGBA').resize((16 * S, 16 * S), Image.NEAREST)
    x, y = 8 + (i % cols) * cell, 8 + (i // cols) * (cell + 16)
    d.rectangle([x, y, x + cell - 8, y + cell - 8], fill='#fff8dc', outline='#c79a52', width=2); b.paste(im, (x + 8, y + 8), im)
    d.text((x + (cell - 8) / 2, y + cell - 4), n, fill='#5e5b71', font=font, anchor='mt')
b.save(ROOT / 'docs/design/quest-icons-board.png'); print(b.size)
