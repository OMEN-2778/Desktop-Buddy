"""Labelled review sheet of art/src/concept/sea_life.py (Chinese names, 5x). Usage: python3 tools/make_sea_life_sheet.py [out.png]"""
import sys
sys.path[:0]=[str(__import__('pathlib').Path(__file__).resolve().parents[1]/'tools'),str(__import__('pathlib').Path(__file__).resolve().parents[1]/'art/src/concept')]
import sea_life as L
from PIL import Image, ImageDraw, ImageFont
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
hfont=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',28)
SC=5; W=1700
rows=[]
y=10
canvas=Image.new('RGB',(W,4000),(176,214,228))
d=ImageDraw.Draw(canvas)
for title,g in L.GROUPS:
    d.text((20,y),title,font=hfont,fill=(40,50,70)); y+=50
    x=20; rowh=0
    for key,(name,fn) in g.items():
        im=fn().to_image(); im=im.resize((im.width*SC,im.height*SC),0)
        if x+im.width>W-20: x=20; y+=rowh+44; rowh=0
        canvas.paste(im,(x,y),im)
        d.text((x,y+im.height+4),name,font=font,fill=(30,40,60))
        x+=max(im.width,len(name)*24)+40; rowh=max(rowh,im.height)
    y+=rowh+60
canvas=canvas.crop((0,0,W,y))
canvas.save(sys.argv[1] if len(sys.argv) > 1 else str(__import__('pathlib').Path(__file__).resolve().parents[1]/'art/preview/concept/sea_life_sheet.png')); print(canvas.size)
