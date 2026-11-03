"""Build the full game with the season-map adapters.
  default: test-only page desktop/dist/map-test/index.html (all season maps, cheats, own save keys).
  --release (owner 2026-11-03, version 0.2): the formal game with 茵菲谷 only (summer/autumn unreachable,
  no cheats or test panel, the player's own save), written over prototype/demo/index.html for
  desktop/scripts/copy-web.mjs. Run tools/make_demo.py first."""
from pathlib import Path
import json,sys,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import make_spring_preview as SP
import make_summer_preview as SU
from autumn_runtime import runtime_data as autumn_data

def controller(name,data):
    template=(ROOT/f'prototype/{name}/index.src.html').read_text()
    dom=re.search(r'<main>(.*?)</main>',template,re.S)[1]
    dom=re.sub(r'id="([^"]+)"',lambda m:f'id="season-{name}-{m[1]}"',dom)
    source=(ROOT/f'prototype/{name}/viewer.js').read_text().replace('/*__DATA__*/null',json.dumps(data,ensure_ascii=False,separators=(',',':')))
    source=source.replace('dt*42','dt*opts.walkSpeed').replace('Math.abs(dy)>0?27:42','Math.abs(dy)>0?opts.walkSpeed*.7:opts.walkSpeed').replace('inSea()?30:42','inSea()?opts.walkSpeed*1.15:opts.walkSpeed')
    source=source.replace("const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d'),images=new Map();","const canvas=document.getElementById('scene'),images=new Map();let ctx=canvas.getContext('2d');")
    exported='springPreview' if name=='spring' else 'summerPreview'
    if name=='spring':source=source.replace('paint(DATA.inside,27,0);actor();','paint(DATA.inside,27,0);peopleRenderer?.(ctx,{region:-1,inside:true,time:state.time});actor();')
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

def quest_icons():
    """任务 icons (art/src/concept/quest_icons.py, built to art/out/concept/quest_icon_*.png)."""
    out={}
    for f in sorted((ROOT/'art/out/concept').glob('quest_icon_*.png')):out[f.stem[len('quest_icon_'):]]=SP.uri(f)
    assert 'scroll' in out,'build art/src/concept/quest_icons.py first'
    return out

def infei_seasons(spring):
    """茵菲谷 in summer / autumn / winter (art/src/concept/infei_seasons.py): same scene list as spring."""
    from PIL import Image
    import numpy as np
    art=ROOT/'art/out/concept';out={}
    def masked(im,sky):
        a=np.array(im.convert('RGBA'));s=np.array(sky.convert('RGBA'))
        a[...,3][np.all(a[...,:3]==s[:a.shape[0],:a.shape[1],:3],axis=2)]=0;return Image.fromarray(a)
    for season in ('summer','autumn','winter'):
        scenes=[]
        for sp in spring:
            key=sp['id'];pre=f'infei_{season}_'
            if key=='ranch':
                def wide(names):
                    im=Image.new('RGBA',(684,118))
                    for i,n in enumerate(names):
                        if (art/(n+'.png')).exists():im.paste(Image.open(art/(n+'.png')).convert('RGBA'),(i*342,0))
                    return im
                bg=wide([pre+'orchard',pre+'pasture']);trees=[SP.uri(wide([pre+'orchard_trees_'+str(f),pre+'pasture_trees_'+str(f)])) for f in (0,1)]
                front=SP.uri(wide(['__none__',pre+'pasture_front']))
            else:
                bg=Image.open(art/(pre+key+'.png'));trees=[SP.uri(art/(pre+key+'_trees_'+str(f)+'.png')) for f in (0,1)];front=None
            sky=Image.open(__import__('io').BytesIO(__import__('base64').b64decode(sp['sky'].split(',')[1])))
            scenes.append({**{k:sp[k] for k in ('sky','id','name','width','clouds')},'bg':SP.uri(masked(bg,sky)),'trees':trees,'front':front})
        out[season]=scenes
    return out

def farm_story_source():
    # Spring story + first farming loop (test page only): farm UI art, empty-bed crops, the farm module.
    import make_farm_ui_preview as FU
    import spring_fields as F
    from pixelkit import Sprite
    art=FU.art();art.pop('backs')
    hexc=lambda c:c if isinstance(c,str) else '#%02x%02x%02x'%tuple(c[:3])
    import infei_crops as IC, infei_seasons as IS, front_yard as FY, random as R
    kinds=list(F.CROPS)+list(IC.NEW)
    def crop_sprite(kind,stage):
        s=Sprite(16,20);IC.crop(s,kind,stage,8,19);return FU.uri(s.to_image())
    def stage_pic(kind,stage):   # the farm-UI stage strip: a bit of bed soil under the plant
        s=Sprite(16,24);s.hline(1,14,23,F.SOIL[2]).hline(3,12,22,F.SOIL[3]);IC.crop(s,kind,stage,8,22);return FU.uri(s.to_image().crop((0,6,16,24)))
    for k in IC.NEW:art['stages'][k]=[stage_pic(k,i) for i in range(4)]
    def tree_pic(kind,season,stage):
        # One fruit tree for a pit, per season and stage (0 sapling, 1 young, 2 grown, 3 with fruit).
        x,base=60,80;at=(x,base-16,base,10,9)
        s2=season if season!='winter' or kind!='orange' else 'summer'   # citrus keeps its leaves
        if s2!='spring':IS._season(s2)
        try:
            if season=='winter' and kind!='orange' and stage>=2:t=FY.tree('fruit','winter',0,at=at)
            elif stage==2 and season!='spring':t=FY.tree(kind if kind!='orange' else 'fruit',F.SEASON,0,at=at)
            else:t=F.fruit_tree(kind,0,at,stage=stage)
        finally:IS._restore()
        if season=='winter':IS.snowcap(t,t.px[...,3]>0,R.Random(kind+str(stage)))
        im=t.to_image();bb=im.getbbox();return {'src':FU.uri(im.crop(bb)),'dx':bb[0]-x,'dy':bb[1]-base}
    trees={k:{se:[tree_pic(k,se,st) for st in range(4)] for se in ('spring','summer','autumn','winter')} for k in ('peach','pear','apple','orange')}
    FS=F.FS;trim=lambda sp:(lambda im:im.crop(im.getbbox()))(sp.to_image() if hasattr(sp,'to_image') else sp)
    animals={'cow':[FU.uri(trim(FS.cow(f))) for f in range(4)],'sheep':[FU.uri(trim(FS.sheep(f))) for f in range(4)],
             'lamb':[FU.uri(trim(FS.sheep(f,lamb=True))) for f in range(4)],'chicken':[FU.uri(trim(FS.chicken(f,False))) for f in (0,1)]}
    data={'plots':F.PLOTS,'slots':[F.plot_slots(*p) for p in F.PLOTS],'soil':[hexc(c) for c in F.SOIL],
          'crops':{k:[crop_sprite(k,i) for i in range(4)] for k in kinds},'trees':trees,'pits':F.PITS,'animals':animals}
    return ('\nconst FARM_UI_ART='+json.dumps(art,separators=(',',':'))+';\nconst SPRING_FARM_DATA='+json.dumps(data,separators=(',',':'))+';\n'
            +(ROOT/'prototype/demo/farm_ui.js').read_text()+'\n')

def spring_data():
    d=SP.runtime_data(bare_farm=True);d['seasons']=infei_seasons(d['scenes']);return d

RELEASE='--release' in sys.argv
RELEASE_CHEATS='function installSeasonCheats(){return {flags:{},fillHero(){},fillPets(){},enforce(){}};}\n'
def main():
    page=(ROOT/'prototype/demo/index.html').read_text()
    assert 'seasonalTest' not in page,'run tools/make_demo.py first'
    # Changes below apply to this page only. The public trial and EXE stay untouched.
    page=page.replace('const cardHolds =','let cardHolds =')
    page=page.replace("bar:'酒吧'}","bar:'酒吧',spring_test:'茵菲谷',summer_test:'夏日海湾',autumn_test:'枫叶城'}")
    page=page.replace('const sceneHouseHeight=()=>','let sceneHouseHeight=()=>')
    page=page.replace("if(place==='park')","if(place==='autumn_test')return 'BGM/park/festival-streetlights.mp3';if(place==='spring_test')return 'BGM/infei/infei-'+(night?'night':season)+'.mp3';if(place==='airport_test')return 'BGM/infei/infei-airport.mp3';if(place==='summer_test')return 'BGM/harbor/dragon-boat-day.mp3';if(place==='park')")
    for key in ([] if RELEASE else ['buddy-save','buddy-settings','buddy-look-v2','buddy-look-at']):
        page=page.replace('"'+key+'"','"season-test-'+key+'"')
    autumn=(ROOT/'prototype/autumn/story.js').read_text()+(ROOT/'prototype/autumn/game.js').read_text()+'\nconst AUTUMN_MAP_DATA='+json.dumps(autumn_data(),ensure_ascii=False,separators=(',',':'))+';\n'
    source=autumn+(ROOT/'prototype/season/effects.js').read_text()+controller('spring',spring_data())+controller('summer',SU.runtime_data())+(ROOT/'prototype/map-test/people.js').read_text()+(RELEASE_CHEATS if RELEASE else (ROOT/'prototype/map-test/cheats.js').read_text())+(ROOT/'prototype/map-test/adapter.js').read_text()
    import base64
    airport_images={k:'data:image/png;base64,'+base64.b64encode((ROOT/('art/out/concept/'+k+'.png')).read_bytes()).decode() for k in ['airport_terminal','airport_vista','airport_terminal_front','airport_plane','airport_cabin','airport_cabin_front','trip_airport']}
    source+=farm_story_source()
    source+='\nconst AIRPORT_IMAGES='+json.dumps(airport_images)+';\n'+(ROOT/'prototype/airport/flight.js').read_text()+(ROOT/'prototype/airport/planes.js').read_text()+'\n'+(ROOT/'prototype/map-test/airport.js').read_text()+'\n'+(ROOT/'prototype/map-test/spring_cards.js').read_text()+(ROOT/'prototype/map-test/spring_talk.js').read_text()+(ROOT/'prototype/map-test/spring_story.js').read_text()+(ROOT/'prototype/map-test/infei_farm.js').read_text()+'\n'+(ROOT/'prototype/map-test/infei_more.js').read_text()+'\n'+(ROOT/'prototype/map-test/infei_home.js').read_text()+'\nconst QUEST_ICONS='+json.dumps(quest_icons())+';\nconst INFEI_COVERS='+json.dumps({k:SP.uri(ROOT/f'art/out/concept/infei_cover_{k}.png') for k in ('mine','parents')})+';\n'+'\n'+(ROOT/'prototype/map-test/quest_panel.js').read_text()+'\n'+(ROOT/'prototype/map-test/infei_quests.js').read_text()+'\n'+(ROOT/'prototype/map-test/infei_audio.js').read_text()+'\n'+(ROOT/'prototype/map-test/infei_hover.js').read_text()
    # 茵菲谷 audio (AUDIO_LIBRARY/INFEI, never in the release): served from /map-test/audio/ like the game's own files
    infei=[f'BGM/infei/{f.name}' for f in sorted((ROOT/'AUDIO_LIBRARY/INFEI/BGM').glob('*.mp3'))]+[f'SFX/game/{f.name}' for f in sorted((ROOT/'AUDIO_LIBRARY/INFEI/SFX').glob('*.mp3'))]
    k=page.index('const GAME_AUDIO_FILES = [')+len('const GAME_AUDIO_FILES = [')
    page=page[:k]+','.join(json.dumps(f) for f in infei)+','+page[k:]
    if RELEASE:
        source=source.replace('再测试季节地图吧','再出发吧').replace("label:'在季节地图探索'","label:'在茵菲谷'")
    mark='(async function boot() {'
    assert page.count(mark)==1
    page=page.replace(mark,source+'\n'+mark)
    page=page.replace('</style>',(ROOT/'prototype/map-test/style.css').read_text()+(ROOT/'prototype/demo/farm_ui.css').read_text()+'\n</style>',1)
    if RELEASE:
        page=page.replace('</style>','#seasonGameTest{display:none!important}\n</style>',1)
        (ROOT/'prototype/demo/index.html').write_text(page);print('release page with 茵菲谷',round(len(page)/1024),'KiB');return
    page=page.replace('<title>Buddy 小屋</title>','<title>Desktop Buddy · 季节地图测试</title>')
    start=page.index('<script>')+8;end=page.index('</script>',start)
    with tempfile.TemporaryDirectory(prefix='buddy-season-test-') as tmp:
        a,b=Path(tmp)/'game.js',Path(tmp)/'game.min.js';a.write_text(page[start:end])
        subprocess.run(['node',str(ROOT/'desktop/node_modules/terser/bin/terser'),str(a),'--compress','--mangle','--output',str(b)],check=True)
        page=page[:start]+b.read_text().replace('</script','<\\/script')+page[end:]
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8">'+page+'\n</html>'
    out=ROOT/'desktop/dist/map-test/index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(page)
    (out.parent/'FONT-LICENSE.txt').write_bytes((ROOT/'art/fonts/source-han-sans/LICENSE.txt').read_bytes())
    # Full-game audio referenced relatively inside /map-test/, always kept under this page.
    import shutil
    for group in ['BGM','SFX/game','SFX/processed']:shutil.copytree(ROOT/'AUDIO_LIBRARY'/group,out.parent/'audio'/group,dirs_exist_ok=True)
    shutil.copytree(ROOT/'AUDIO_LIBRARY/INFEI/BGM',out.parent/'audio/BGM/infei',dirs_exist_ok=True)
    shutil.copy2(ROOT/'prototype/map-test/bgm.html',out.parent/'bgm.html')   # 茵菲谷 music listening page (/map-test/bgm.html)
    for f in (ROOT/'AUDIO_LIBRARY/INFEI/SFX').glob('*.mp3'):shutil.copy2(f,out.parent/'audio/SFX/game'/f.name)
    print(out,round(len(page)/1024),'KiB')
if __name__=='__main__':main()
