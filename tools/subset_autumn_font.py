"""Subset upstream Source Han Sans SC Medium for autumn signs (authoring only).
Usage: python tools/subset_autumn_font.py /path/to/SourceHanSansSC-Medium.otf
Requires fontTools. Outputs OTF for art review and WOFF for offline browser rendering.
"""
import re,sys
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
font=TTFont(sys.argv[1]);opts=subset.Options()
opts.name_IDs=['*'];opts.name_legacy=True;opts.name_languages=['*']
sub=subset.Subsetter(options=opts)
sub.populate(text=''.join(re.findall(r'[\u3400-\u9fff]',(ROOT/'art/src/concept/autumn_city.py').read_text()))+'0123456789 ')
sub.subset(font)
for record in font['name'].names:
 if record.nameID in (1,4,6,16):
  record.string=('BuddyAutumnSigns' if record.nameID==6 else 'Buddy Autumn Signs').encode(record.getEncoding())
out=ROOT/'art/fonts/source-han-sans';out.mkdir(parents=True,exist_ok=True)
font.save(out/'BuddyAutumnSigns.otf');font.flavor='woff';font.save(out/'BuddyAutumnSigns.woff')
