"""Combine canonical field animation sheets into the owner's animated review."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=ROOT/'art/out/concept'
    names=['spring_rape_wind_preview','spring_tulip_wind_preview']
    meta=json.loads((source/(names[0]+'.json')).read_text())
    spec=meta['anims'][names[0]];w,h=meta['frame_w'],meta['frame_h']
    sheets=[Image.open(source/(name+'.png')).convert('RGBA') for name in names]
    font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
    frames=[]
    for f in range(spec['frames']):
        out=Image.new('RGB',(1400,278),'#eee8dd');draw=ImageDraw.Draw(out)
        for k,label in enumerate(['油菜花田 · 随风摇曳','风车花圃 · 随风摇曳']):
            draw.text((12+k*700,6),label,font=font,fill='#3d3541')
            im=sheets[k].crop((w*f,0,w*(f+1),h)).resize((w*2,h*2),Image.Resampling.NEAREST)
            out.paste(im,(12+k*700,34),im)
        frames.append(out)
    # A shared palette prevents a different quantization flash on every frame.
    palette=frames[0].quantize(colors=256,dither=Image.Dither.NONE)
    frames=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
    target=ROOT/'docs/design/spring-flower-wind.gif';target.parent.mkdir(exist_ok=True)
    frames[0].save(target,save_all=True,append_images=frames[1:],duration=spec['durations'],loop=0,optimize=False,disposal=2)
    with Image.open(target) as gif:
        assert gif.n_frames==spec['frames']
        assert gif.info['duration']==spec['durations'][0]
    print(target)
if __name__=='__main__':main()
