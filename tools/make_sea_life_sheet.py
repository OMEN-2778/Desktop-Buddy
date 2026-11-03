"""Labelled review sheet of a sea art module (Chinese names). Usage: python3 tools/make_sea_life_sheet.py [out.png] [module=sea_life] [scale=5]"""
import sys
sys.path[:0]=[str(__import__('pathlib').Path(__file__).resolve().parents[1]/'tools'),str(__import__('pathlib').Path(__file__).resolve().parents[1]/'art/src/concept')]
import importlib; L=importlib.import_module(sys.argv[2] if len(sys.argv)>2 else "sea_life")
from PIL import Image, ImageDraw, ImageFont
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
hfont=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',28)
SC=int(sys.argv[3]) if len(sys.argv)>3 else 5; W=1700
rows=[]
y=10
canvas=Image.new('RGB',(W,4000),(38,110,150))
d=ImageDraw.Draw(canvas)
for title,g in L.GROUPS:
    d.text((20,y),title,font=hfont,fill=(230,245,250)); y+=50
    x=20; rowh=0
    for key,(name,fn) in g.items():
        im=fn().to_image(); im=im.resize((im.width*SC,im.height*SC),0)
        if x+im.width>W-20: x=20; y+=rowh+44; rowh=0
        canvas.paste(im,(x,y),im)
        d.text((x,y+im.height+4),name,font=font,fill=(220,240,248))
        x+=max(im.width,len(name)*24)+40; rowh=max(rowh,im.height)
    y+=rowh+60
canvas=canvas.crop((0,0,W,y))
canvas.save(sys.argv[1] if len(sys.argv) > 1 else str(__import__('pathlib').Path(__file__).resolve().parents[1]/'art/preview/concept/sea_life_sheet.png')); print(canvas.size)
