"""Build isolated airport art review, publish only raster art + minified page."""
from pathlib import Path
import sys, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import airport

def main():
    out=ROOT/'desktop/dist/airport';out.mkdir(parents=True,exist_ok=True)
    assets=airport.build()
    for name,s in assets.items():s.save(out/(name+'.png'))
    fontpath=ROOT/'art/fonts/source-han-sans/BuddyAutumnSigns.otf'
    # Full local CJK font available for rendered signs; CI uses checked-in review image.
    candidates=list(Path('/usr/share/fonts').rglob('*CJK*'))
    font=ImageFont.truetype(str(candidates[0] if candidates else fontpath),22)
    im=assets['airport_terminal_preview'].to_image(4);d=ImageDraw.Draw(im)
    # signs carry pixel glyphs drawn in the art (owner: no readable text)
    checked=ROOT/'art/out/concept/airport_terminal_review.png'
    if candidates:im.save(checked)
    elif checked.exists():im=Image.open(checked)
    im.save(out/'terminal-review.png')
    sheet=Image.new('RGB',(1416,1600),'#e9edf1');d=ImageDraw.Draw(sheet)
    for i,(title,img) in enumerate((('01  机场大厅',im),('02  客机机舱 · 往返转场',assets['airport_cabin_preview'].to_image(4)),('03  家门 → 机场 · 银白转场',assets['airport_transition_preview'].to_image(4)))):
        y=18+i*530;d.text((24,y),title,font=font,fill='#40515c');sheet.paste(img,(24,y+38))
    combined=ROOT/'art/out/concept/airport_review.png'
    if candidates:sheet.save(combined)
    elif combined.exists():sheet=Image.open(combined)
    sheet.save(out/'airport-review.png')
    (out/'signs.otf').write_bytes(fontpath.read_bytes());(out/'FONT-LICENSE.txt').write_bytes((fontpath.parent/'LICENSE.txt').read_bytes())
    for name,source in [('spring-destination','spring_home_preview'),('home-destination','house_day')]:
        (out/(name+'.png')).write_bytes((ROOT/('art/out/concept/'+source+'.png')).read_bytes())
    page=(ROOT/'prototype/airport/index.src.html').read_text().replace('/*__FLIGHT_JS__*/',(ROOT/'prototype/airport/flight.js').read_text()+(ROOT/'prototype/airport/planes.js').read_text());a=page.index('<script>')+8;b=page.index('</script>',a)
    js=subprocess.run(['node',str(ROOT/'desktop/node_modules/terser/bin/terser'),'--compress','--mangle'],input=page[a:b],text=True,capture_output=True,check=True).stdout
    (out/'index.html').write_text(page[:a]+js+page[b:])
    print(out/'index.html')
if __name__=='__main__':main()
