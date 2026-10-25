// The main night scene must remain the hero's home after packing friend homes.
const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1700,height:1200},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(2100);
 const result=await p.evaluate(()=>{
  const pixels=image=>{const c=document.createElement('canvas');c.width=image.width;c.height=image.height;const ctx=c.getContext('2d');ctx.drawImage(image,0,0);return ctx.getImageData(0,0,c.width,c.height).data;};
  const day=pixels(IMG.day),night=pixels(IMG.night),windows=Object.values(D.windows);
  const allowed=(x,y)=>windows.some(w=>x>=w.x&&x<w.x+32&&y>=w.y&&y<w.y+27)||x>=D.weatherMasks.win_round.x&&x<D.weatherMasks.win_round.x+16&&y>=D.weatherMasks.win_round.y&&y<D.weatherMasks.win_round.y+16;
  let changed=0,alphaChanges=0,outsideWindows=0;
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){const i=(y*W+x)*4;if(day[i+3]!==night[i+3])alphaChanges++;if(day[i]!==night[i]||day[i+1]!==night[i+1]||day[i+2]!==night[i+2]){changed++;if(!allowed(x,y))outsideWindows++;}}
  return {day:[IMG.day.width,IMG.day.height],night:[IMG.night.width,IMG.night.height],expected:[W,H],changed,alphaChanges,outsideWindows};
 });
 assert.deepEqual(result.day,result.expected);assert.deepEqual(result.night,result.expected,'A friend house replaced the main night background');assert.ok(result.changed>0,'Night windows did not change');assert.equal(result.alphaChanges,0,'House silhouette moved at night');assert.equal(result.outsideWindows,0,'Furniture/room geometry changed at night');
 fs.mkdirSync('/workspace/artifacts/home-night',{recursive:true});
 await p.evaluate(()=>{prefs.guided=false;closeGuide();closePicker();closeSocialSheet();closeRing();card=null;cardEl.hidden=cardRes.hidden=true;cardMoment=rollCard=rollEvents=()=>false;speed=0;friendVisit=null;friendHousePreview=null;friendOutingState=null;socialState.guest=null;sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;sim.route=[[95,FLOOR_Y[0]]];sim.s=0;sim.idleUntil=Infinity;socialState.nextCall=socialState.nextVisit=1e9;weather.kind=weather.force='clear';setScale(100);});
 for(const hour of [12,18,22]){await p.evaluate(h=>{sim.t=h*60;render()},hour);await p.locator('#view').screenshot({path:`/workspace/artifacts/home-night/home-${hour}.png`});}
 assert.deepEqual(errors,[]);console.log('PASS: hero day/night assets retain identical size, silhouette and furniture positions; changes restricted to windows; noon/dusk/night renders.',result);
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
