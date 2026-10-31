"""Build the owner's isolated, minified spring-map walk-through (no game save)."""
from pathlib import Path
import sys,io,base64,json,subprocess,tempfile
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import spring_fields as F
import doll
from pixelkit import Sprite

def uri(im):
    if isinstance(im,Sprite):im=im.to_image()
    if isinstance(im,Path):im=Image.open(im)
    out=io.BytesIO();im.save(out,format='PNG');return 'data:image/png;base64,'+base64.b64encode(out.getvalue()).decode()

def runtime_data():
    art=ROOT/'art/out/concept';zones={z['id']:z for z in F.ZONES};scenes=[]
    for key in ['brook','rape','tulip','home','farm','ranch']:
        if key=='ranch':
            # Wide terrain already generated as one seamless scene.
            bg=Image.open(art/'spring_ranch.png');tree=[uri(art/f'spring_ranch_tree_{i}.png') for i in (0,1)]
            front=uri(art/'spring_ranch_front.png');width=684;cloud=Sprite(684,118)
        else:
            z=zones[key];bg=F.background(z,mill_sails=False,with_clouds=False);tree=[uri(F.trees(z,i)) for i in (0,1)];front=None;width=342;cloud=Sprite(342,118)
            F.clouds(cloud,z)
            if key=='farm':
                for i,(x,y,w,h) in enumerate(F.PLOTS):
                    if i in (3,10):continue
                    for j,(cx,base) in enumerate(F.plot_slots(x,y,w,h)):F.crop(bg,F.CROPS[i%len(F.CROPS)],(3,3,2,3,1,2)[(i+j)%6],cx,base)
        # Clear only the exact sky pixels from the opaque scenic plane.
        sky=Sprite(width,118);F.PK.sky(sky)
        bp=np.array(bg.to_image() if isinstance(bg,Sprite) else bg.convert('RGBA'))
        mask=np.all(bp[:118,:,:3]==sky.px[:118,:,:3],axis=2)
        bp[:118,:,3][mask]=0;bg=Image.fromarray(bp)
        entry={'sky':uri(sky),'id':key,'name':{'brook':'溪桥樱堤','rape':'油菜花田','tulip':'风车花圃','home':'农舍','farm':'菜园','ranch':'果园与牧场'}[key],'width':width,'bg':uri(bg),'trees':tree,'front':front,'clouds':uri(cloud)}
        if key in ('rape','tulip'):
            wind=np.array(Image.open(art/f'spring_{key}_wind.png').convert('RGBA'))
            wind[:,:,3][np.tile(mask,(1,wind.shape[1]//342))]=0
            entry['wind']=uri(Image.fromarray(wind));entry['cleanTop']=uri(bg)
        scenes.append(entry)
    inside,_=F.FS.cn_farmhouse_inside()
    poses=['stand','walkL','stand','walkR'];hero=Image.new('RGBA',(80,28))
    for i,pose in enumerate(poses):
        image=doll.GIRL.render(bob=i%2,sway=i%2).to_image()
        if pose!='stand':
            legs=image.crop((0,22,20,28));image.paste((0,0,0,0),(0,22,20,28))
            for half in (0,1):
                limb=legs.crop((half*10,0,half*10+10,6))
                image.paste(limb,(half*10,21 if half==(i//2)%2 else 22),limb)
        hero.paste(image,(i*20,0))
    data={'scenes':scenes,'inside':uri(inside),'hero':uri(hero),'sails':uri(art/'spring_windmill_sails.png'),'birds':[uri(F.FS.bird(i)) for i in range(3)],'butterflies':[uri(F.FY.butterfly(i)) for i in range(4)],'animals':{k:[uri(F.animal(k,f)) for f in range(4)] for k in ('cow','sheep','lamb')},'chickens':[uri(F.FS.chicken(f,r)) for r in (False,True) for f in (0,1)],'herd':F.HERD,'coop':F.COOP,'beam':uri(F.FS.sun_shaft())}
    return data


def main():
    data=runtime_data()
    # Public output contains built assets and minified preview code only.
    js=(ROOT/'prototype/season/effects.js').read_text()+'\n'+(ROOT/'prototype/spring/viewer.js').read_text().replace('/*__DATA__*/null',json.dumps(data,ensure_ascii=False,separators=(',',':')))
    with tempfile.TemporaryDirectory(prefix='buddy-spring-preview-') as temp:
        source=Path(temp)/'viewer.js';target=Path(temp)/'viewer.min.js';source.write_text(js)
        subprocess.run(['node',str(ROOT/'desktop/node_modules/terser/bin/terser'),str(source),'--compress','--mangle','toplevel','--output',str(target)],check=True)
        script=target.read_text().replace('</script','<\\/script')
    html=(ROOT/'prototype/spring/index.src.html').read_text().replace('/*__SCRIPT__*/',script)
    out=ROOT/'desktop/dist/spring/index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(html);print(out,round(len(html)/1024),'KiB')
if __name__=='__main__':main()
