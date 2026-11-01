"""Build art-only /autumn/ review. Only minified code and rendered artwork go public."""
from pathlib import Path
import sys, json, base64, io, subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'art/src/concept')]
import autumn_city as A

def main():
 out=ROOT/'desktop/dist/autumn';out.mkdir(parents=True,exist_ok=True)
 im=A.polluted_city().to_image();buf=io.BytesIO();im.save(buf,format='PNG');data=buf.getvalue();(out/'autumn-city-polluted.png').write_bytes(data)
 page=(ROOT/'prototype/autumn/index.src.html').read_text();page=page.replace('__DATA__',json.dumps(dict(routes=A.ROUTES,landmarks=A.LANDMARKS),ensure_ascii=False)).replace('__IMAGE__',base64.b64encode(data).decode())
 start=page.index('<script>')+8;end=page.index('</script>',start)
 script=subprocess.run(['node',str(ROOT/'desktop/node_modules/terser/bin/terser'),'--compress','--mangle'],input=page[start:end],text=True,capture_output=True,check=True).stdout
 page=page[:start]+script+page[end:];(out/'index.html').write_text(page)
 print(out/'index.html',len(page)//1024,'KiB')
if __name__=='__main__':main()
