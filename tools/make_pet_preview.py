"""Build the isolated pet art viewer; does not alter the game or its saves."""
from __future__ import annotations
import hashlib
import base64
import io
import json
from pathlib import Path
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import pets
import doll

OUT=ROOT/'prototype/pets'
REVIEW=ROOT/'docs/design/pets'

def data_url(image):
    buf=io.BytesIO();image.save(buf,format='PNG');return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()

def runtime_data():
    """Generate the same canonical atlases for the game, without viewer artifacts."""
    import pet_furniture
    inputs=[Path(pets.__file__),Path(pet_furniture.__file__),ROOT/'tools/pixelkit/core.py',ROOT/'tools/pixelkit/palette.py']
    signature=hashlib.sha256(b''.join(p.read_bytes() for p in inputs)).hexdigest()
    cache=OUT/'assets/runtime.json'
    if cache.exists():
        saved=json.loads(cache.read_text())
        if saved.get('signature')==signature:return saved['data']
    rows=[]
    for breed in pets.BREEDS:
        clips=[]; atlas=Image.new("RGBA",(8*pets.W,len(pets.actions(breed.species))*4*pets.H))
        for action,(label,count,duration) in pets.actions(breed.species).items():
            for direction in pets.DIRECTIONS:
                row=len(clips)
                for frame in range(count):atlas.paste(pets.render(breed,action,frame,direction).to_image(),(frame*pets.W,row*pets.H))
                clips.append(dict(id=action,name=label,direction=direction,row=row,frames=count,ms=duration))
        rows.append(dict(id=breed.id,name=breed.name,species=breed.species,image=data_url(atlas),clips=clips))
    data=dict(breeds=rows,furniture={k:data_url(v.to_image()) for k,v in pet_furniture.build().items()})
    cache.parent.mkdir(parents=True,exist_ok=True)
    cache.write_text(json.dumps(dict(signature=signature,data=data),ensure_ascii=False))
    return data

def build(review=False):
    OUT.mkdir(parents=True,exist_ok=True)
    assets=OUT/'assets';assets.mkdir(exist_ok=True)
    rows=[];manifest={'version':1,'frame':{'w':pets.W,'h':pets.H,'feet':pets.FEET},'directions':pets.DIRECTIONS,'breeds':[]}
    for breed in pets.BREEDS:
        clips=[];a=pets.actions(breed.species)
        atlas=Image.new('RGBA',(8*pets.W,len(a)*len(pets.DIRECTIONS)*pets.H))
        for action,(label,count,duration) in a.items():
            for direction in pets.DIRECTIONS:
                row=len(clips)
                for frame in range(count):
                    image=pets.render(breed,action,frame,direction).to_image()
                    atlas.paste(image,(frame*pets.W,row*pets.H))
                clips.append({'id':action,'name':label,'direction':direction,'row':row,'frames':count,'ms':duration,'loop':action not in ['sit_down','stand_up','lie_down','wake','pounce']})
        atlas.save(assets/(breed.id+'.png'))
        metadata={'id':breed.id,'name':breed.name,'species':breed.species,'atlas':breed.id+'.png','clips':clips}
        manifest['breeds'].append(metadata)
        rows.append({**metadata,'image':data_url(atlas)})
    (assets/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    hero=data_url(doll.BOY.render().to_image())
    template=(OUT/'index.src.html').read_text()
    html=template.replace('/*__PET_DATA__*/',json.dumps({'breeds':rows,'hero':hero,'w':pets.W,'h':pets.H,'feet':pets.FEET},ensure_ascii=False))
    (OUT/'index.html').write_text(html)
    print(f'{len(rows)} breeds; '+str(sum(len(x['clips']) for x in rows))+' directional clips; isolated viewer '+str(OUT/'index.html'))
    if not review:return manifest
    REVIEW.mkdir(parents=True,exist_ok=True)
    catalog=Image.new('RGB',(1200,1140),'#eee6d9');draw=ImageDraw.Draw(catalog)
    font_path=next((p for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'] if Path(p).exists()),None)
    if not font_path:raise RuntimeError('Review catalog needs a CJK font; web-only build does not.')
    title=ImageFont.truetype(font_path,28);font=ImageFont.truetype(font_path,17)
    draw.text((32,20),'Desktop Buddy · 猫狗品种与动作素材',font=title,fill='#33253b')
    draw.text((32,64),'每行：站立 / 坐下 / 睡觉 · 共用猫体型，狗按品种区分 · 素材预览，未接入领养',font=font,fill='#65536d')
    for i,b in enumerate(pets.BREEDS):
        x=(i%4)*300;y=(i//4)*170+110
        draw.rounded_rectangle((x+12,y,x+288,y+154),radius=8,fill='#faf5eb',outline='#c5b6ac',width=2)
        draw.text((x+27,y+11),b.name,font=font,fill='#33253b')
        for j,action in enumerate(['idle','sit','sleep']):
            spr=pets.render(b,action,0).to_image(3)
            catalog.paste(spr,(x+8+j*91,y+48),spr)
    catalog.save(REVIEW/'pet-breeds.png')
    with zipfile.ZipFile(REVIEW/'pet-art-preview.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('pet-preview.html',html)
        z.writestr('README.txt','双击 pet-preview.html 查看全部品种和动作，无需联网。\nassets 中是透明 PNG 动作图集和 manifest.json。\n这只是素材试作，不含领养、需求或宠物 AI。\n')
        for path in sorted(assets.iterdir()):
            if path.suffix=='.png' or path.name=='manifest.json':z.write(path,'assets/'+path.name)
        z.write(REVIEW/'pet-breeds.png','pet-breeds.png')
    return manifest

if __name__=='__main__':build('--review' in sys.argv)
