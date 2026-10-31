"""Existing spring scenery in motion: reusable sails + one combined review GIF.
Art only; does not wire the map into the game. Run after the spring sprite build.
"""
from pathlib import Path
import json,math,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import spring_fields as F
from pixelkit import Sprite

FRAMES=144;MS=40

def main():
    root=ROOT/'art/out/concept';zones=[next(z for z in F.ZONES if z['id']==k) for k in ['rape','tulip']]
    sheets=[Image.open(root/f"spring_{z['id']}_wind.png").convert('RGBA') for z in zones]
    tops=[F.background(z,mill_sails=False,with_clouds=False) for z in zones]
    trees=[[F.trees(z,f) for f in (0,1)] for z in zones]
    cloud_layers=[]
    for z in zones:
        c=Sprite(F.W,F.H);F.clouds(c,z);cloud_layers.append(c)
    font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
    sails_sheet=Image.new('RGBA',(50*FRAMES,50));frames=[]
    for f in range(FRAMES):
        phase=math.tau*f/FRAMES;out=Image.new('RGB',(1400,278),'#eee8dd');draw=ImageDraw.Draw(out)
        for k,z in enumerate(zones):
            base=sheets[k].crop((342*(f%72),0,342*(f%72+1),118))
            s=Sprite(342,118,px=np.array(base).copy())
            # Retain animated flower frames; rebuild only the sky/tower area.
            s.px[:58]=tops[k].px[:58]
            s.blit(cloud_layers[k],round(4*math.sin(phase+k)),0)
            for j,(x,y) in enumerate([(70,16),(155,10),(275,23)]):
                a=phase+j*2+k*.4
                s.blit(F.FS.bird((f//4+j)%3),round(x+20*math.sin(a)),round(y+3*math.sin(2*a)))
            if k==1:
                rotor=Sprite(50,50);F.sails(rotor,25,25,phase/4)
                sails_sheet.paste(rotor.to_image(),(f*50,0))
                s.blit(rotor,211,2) # hub (236,27), fixed to the existing tower
            treephase=int(math.sin(phase+k)>.3)
            s.blit(trees[k][treephase],0,0)
            for j,(x,y) in enumerate([(80,80),(210,84),(285,74)]):
                a=phase+j*2.2+k
                s.blit(F.FY.butterfly((j%2)*2+(f//4+j)%2),round(x+9*math.sin(a)),round(y+3*math.sin(a*2)))
            if k==1:
                # One occasional, soft ray, as specified by the owner.
                envelope=max(0,math.sin(phase))**4
                if envelope>.02:
                    beam=Sprite(342,118);beam.blit(F.FS.sun_shaft(),round(100+35*math.sin(phase-.8)),0)
                    s=F.FS.blend(s,beam,.13*envelope)
            draw.text((12+k*700,6),['油菜花田 · 花海与鸟蝶','风车花圃 · 风车与光影'][k],font=font,fill='#3d3541')
            image=s.to_image().resize((684,236),Image.Resampling.NEAREST);out.paste(image,(12+k*700,34),image)
        frames.append(out)
    sails_sheet.save(root/'spring_windmill_sails.png')
    meta={'frame_w':50,'frame_h':50,'hub':[25,25],'scene_hub':[236,27],
          'anims':{'sails':{'row':0,'frames':FRAMES,'durations':[MS]*FRAMES,'loop':True}},
          'note':'Quarter-turn cycle; four identical sails make the loop continuous. Full turn 23.04s.'}
    (root/'spring_windmill_sails.json').write_text(json.dumps(meta,indent=2)+'\n')
    # A shared palette across the whole animation also covers the varying ray.
    palette_source=Image.new('RGB',(350,70*len(frames)))
    for i,im in enumerate(frames):palette_source.paste(im.resize((350,70),Image.Resampling.NEAREST),(0,70*i))
    palette=palette_source.quantize(colors=256,dither=Image.Dither.NONE)
    converted=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
    target=ROOT/'docs/design/spring-scenery-life.gif'
    converted[0].save(target,save_all=True,append_images=converted[1:],duration=MS,loop=0,optimize=False,disposal=2)
    frames[36].save('/tmp/buddy-spring-life-frame.png')
    print(target)
if __name__=='__main__':main()
