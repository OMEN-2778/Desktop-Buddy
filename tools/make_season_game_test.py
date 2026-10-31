"""Build a test-only full game with spring/summer scene adapters. Never changes EXE input."""
from pathlib import Path
import json,sys,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import make_spring_preview as SP
import make_summer_preview as SU

def controller(name,data):
    template=(ROOT/f'prototype/{name}/index.src.html').read_text()
    dom=re.search(r'<main>(.*?)</main>',template,re.S)[1]
    dom=re.sub(r'id="([^"]+)"',lambda m:f'id="season-{name}-{m[1]}"',dom)
    source=(ROOT/f'prototype/{name}/viewer.js').read_text().replace('/*__DATA__*/null',json.dumps(data,ensure_ascii=False,separators=(',',':')))
    source=source.replace('dt*42','dt*opts.walkSpeed').replace('Math.abs(dy)>0?27:42','Math.abs(dy)>0?opts.walkSpeed*.7:opts.walkSpeed').replace('inSea()?30:42','inSea()?opts.walkSpeed*1.15:opts.walkSpeed')
    source=source.replace("const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d'),images=new Map();","const canvas=document.getElementById('scene'),images=new Map();let ctx=canvas.getContext('2d');")
    exported='springPreview' if name=='spring' else 'summerPreview'
    extra="actor=()=>opts.drawHero(ctx,state.x,state.y,state,null);" if name=='spring' else "hero=(x,y)=>{if(state.inCabana)return;opts.drawHero(ctx,x,y,state,{under:under(),floating:floating(),sheet:img(DATA.heroes[state.gender][state.suit]),cell:cell()});};"
    ticks='if(!state.paused)state.time+=realDt;advanceDoor(state.paused?0:realDt);move(dt);draw();' if name=='spring' else 'if(!state.paused)fx.tickWater(realDt);if(!state.paused)state.time+=realDt;advanceDoor(state.paused?0:realDt);move(dt);camera(realDt);prepare();draw();updateUI();'
    return f'''function makeSeason_{name}(opts){{
 const realDocument=globalThis.document,realWindow=globalThis.window;
 const root=realDocument.createElement('section');root.className='season-controller';root.dataset.kind='{name}';root.innerHTML={json.dumps(dom,ensure_ascii=False)};root.hidden=true;
 const document=new Proxy(realDocument,{{get(obj,key){{if(key==='getElementById')return id=>root.querySelector('#season-{name}-'+id);if(key==='addEventListener')return (type,fn,...rest)=>obj.addEventListener(type,e=>{{if(opts.active())fn(e);}},...rest);const value=Reflect.get(obj,key,obj);return typeof value==='function'?value.bind(obj):value;}}}});
 const window={{addEventListener:(type,fn,...rest)=>realWindow.addEventListener(type,e=>{{if(opts.active())fn(e);}},...rest)}};
 const requestAnimationFrame=()=>0;
 {source}
 {extra}
 {"const originalDiscover=discover;discover=(id,text)=>{const fresh=!state.found.has(id);originalDiscover(id,text);if(fresh)opts.record(text);};" if name=='summer' else ''}
 const api=window.{exported};api.root=root;api.canvas=canvas;const renderCanvas=realDocument.createElement('canvas');api.renderCanvas=renderCanvas;
 let resolution=1;api.setResolution=r=>resolution=Math.max(1,r);
 function prepare(){{const w=canvas.width*resolution,h=canvas.height*resolution;if(renderCanvas.width!==w||renderCanvas.height!==h){{renderCanvas.width=w;renderCanvas.height=h;}}ctx=renderCanvas.getContext('2d');ctx.setTransform(resolution,0,0,resolution,0,0);ctx.imageSmoothingEnabled=false;}}
 api.personSheet=(gender,suit)=>{'img(DATA.heroes[gender][suit])' if name=='summer' else 'null'};
 api.tick=(dt,realDt=dt)=>{{prepare();{ticks}}};api.clearKeys=()=>keys.clear();
 canvas.getBoundingClientRect=()=>opts.view.getBoundingClientRect();canvas.focus=()=>opts.view.focus();
 root.querySelector('canvas').hidden=true;root.querySelector('h1')?.remove();root.querySelector('small')?.remove();root.querySelector('[id$="-pause"]')?.setAttribute('hidden','');root.querySelector('[id$="-gender"]')?.setAttribute('hidden','');
 return api;
}}
'''

def main():
    page=(ROOT/'prototype/demo/index.html').read_text()
    # Changes below apply to this page only. The public trial and EXE stay untouched.
    page=page.replace('const cardHolds =','let cardHolds =')
    page=page.replace("bar:'酒吧'}","bar:'酒吧',spring_test:'春日农庄',summer_test:'夏日海湾'}")
    page=page.replace('const sceneHouseHeight=()=>','let sceneHouseHeight=()=>')
    page=page.replace("if(place==='park')","if(place==='spring_test')return 'BGM/park/festival-streetlights.mp3';if(place==='summer_test')return 'BGM/harbor/dragon-boat-day.mp3';if(place==='park')")
    for key in ['buddy-save','buddy-settings','buddy-look-v2','buddy-look-at']:
        page=page.replace('"'+key+'"','"season-test-'+key+'"')
    source=(ROOT/'prototype/season/effects.js').read_text()+controller('spring',SP.runtime_data())+controller('summer',SU.runtime_data())+(ROOT/'prototype/map-test/people.js').read_text()+(ROOT/'prototype/map-test/cheats.js').read_text()+(ROOT/'prototype/map-test/adapter.js').read_text()
    mark='(async function boot() {'
    assert page.count(mark)==1
    page=page.replace(mark,source+'\n'+mark)
    page=page.replace('</style>',(ROOT/'prototype/map-test/style.css').read_text()+'\n</style>',1)
    page=page.replace('<title>Buddy 小屋</title>','<title>Desktop Buddy · 季节地图测试</title>')
    start=page.index('<script>')+8;end=page.index('</script>',start)
    with tempfile.TemporaryDirectory(prefix='buddy-season-test-') as tmp:
        a,b=Path(tmp)/'game.js',Path(tmp)/'game.min.js';a.write_text(page[start:end])
        subprocess.run(['node',str(ROOT/'desktop/node_modules/terser/bin/terser'),str(a),'--compress','--mangle','--output',str(b)],check=True)
        page=page[:start]+b.read_text().replace('</script','<\\/script')+page[end:]
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8">'+page+'\n</html>'
    out=ROOT/'desktop/dist/map-test/index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(page)
    # Full-game audio referenced relatively inside /map-test/, always kept under this page.
    import shutil
    for group in ['BGM','SFX/game','SFX/processed']:shutil.copytree(ROOT/'AUDIO_LIBRARY'/group,out.parent/'audio'/group,dirs_exist_ok=True)
    print(out,round(len(page)/1024),'KiB')
if __name__=='__main__':main()
