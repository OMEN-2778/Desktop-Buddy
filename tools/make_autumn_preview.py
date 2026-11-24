"""Build art-only /autumn/ review. Only minified code and rendered artwork go public."""
from pathlib import Path
import sys, json, base64, subprocess, shutil
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import autumn_city as A

def main():
 out=ROOT/'desktop/dist/autumn';out.mkdir(parents=True,exist_ok=True)
 (out/'FONT-LICENSE.txt').write_bytes((ROOT/'art/fonts/source-han-sans/LICENSE.txt').read_bytes())
 # Publish the reviewed pixelkit output exactly; rendering Chinese signs needs the
 # author's Noto CJK font, which is not guaranteed on CI runners.
 data=(ROOT/'art/out/concept/autumn_city_review.png').read_bytes();(out/'autumn-city-polluted.png').write_bytes(data)
 page=(ROOT/'prototype/autumn/index.src.html').read_text().replace('width="1152" height="1408"',f'width="{A.MAP_W}" height="{A.MAP_H}"');page=page.replace('__DATA__',json.dumps(dict(routes=A.runtime_routes(),landmarks=A.runtime_landmarks()),ensure_ascii=False)).replace('__IMAGE__',base64.b64encode(data).decode())
 start=page.index('<script>')+8;end=page.index('</script>',start)
 script=subprocess.run(['node',str(ROOT/'desktop/node_modules/terser/bin/terser'),'--compress','--mangle'],input=page[start:end],text=True,capture_output=True,check=True).stdout
 page=page[:start]+script+page[end:];(out/'index.html').write_text(page)
 # Separate design review. Live autumn content keeps its current geometry until approval.
 plan=out/'new-town';plan.mkdir(exist_ok=True)
 source=ROOT/'art/out/concept/liwei-plan'
 version=sha256()
 for image in sorted(source.glob('*.png')):
  shutil.copyfile(image,plan/image.name)
  version.update(image.read_bytes())
 review=(ROOT/'prototype/autumn/plan-review.src.html').read_text().replace('__LAYOUT__',(source/'layout.json').read_text())
 review=review.replace('__ART_VERSION__',version.hexdigest()[:12])
 before,script=review.split('<script>',1);script,after=script.split('</script>',1)
 compressed=subprocess.run(['node',str(ROOT/'desktop/node_modules/terser/bin/terser'),'--compress','--mangle'],input=script,text=True,capture_output=True,check=True).stdout
 (plan/'index.html').write_text(before+'<script>'+compressed+'</script>'+after)
 print(out/'index.html',len(page)//1024,'KiB')
if __name__=='__main__':main()
