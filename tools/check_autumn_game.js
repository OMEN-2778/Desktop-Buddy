// Real game shell integration: door, orthogonal traversal, local services, story/save and four scales.
const assert=require('node:assert/strict'),fs=require('fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1600,height:1300},ignoreHTTPSErrors:true,reducedMotion:'no-preference'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error(e.message)});
 if(process.argv[2])await p.goto(process.argv[2]);else{await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');}
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&seasonMapTest.state.autumn.state.loaded);
 await p.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=720;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;seasonMapTest.cheats.fillHero();});
 const coat=p.locator('[data-key="topStyle"][data-v="detective_coat"]');
 await p.evaluate(()=>openWardrobe());assert(await coat.isDisabled());await p.evaluate(()=>closeWardrobe());
 assert.equal(await p.evaluate(()=>new Set(seasonMapTest.state.autumn.DATA.npcs.map(pair=>pair[0])).size),9);
 // Native foliage stays still. Map signs keep their embedded font.
 const detail=await p.evaluate(()=>{const c=seasonMapTest.state.autumn;c.state.paused=true;const before=c.state.time;c.tick(1,1);c.state.paused=false;const cv=document.createElement('canvas');cv.width=120;cv.height=40;const g=cv.getContext('2d');g.font='24px "Buddy Autumn Signs"';g.fillText('工人食堂',0,30);const rgba=g.getImageData(0,0,120,40).data;let smooth=0;for(let i=3;i<rgba.length;i+=4)if(rgba[i]>0&&rgba[i]<255)smooth++;return {frozen:c.state.time===before,font:[...document.fonts].some(f=>f.family.includes("Buddy Autumn Signs")&&f.status==="loaded"),smooth}});assert(detail.frozen&&detail.font&&detail.smooth>20,JSON.stringify(detail));
 // Autumn remains available through the explicitly labelled test toolbar.
 await p.evaluate(()=>{seasonMapTest.start('autumn_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive()});await p.waitForFunction(()=>sim.place==='autumn_test'&&!wiping);
 let box;
 await p.waitForFunction(()=>sceneHouseHeight()===236);
 const local=await p.evaluate(()=>{
  const c=seasonMapTest.ctl(),s=c.state,got={};
  for(const [id,need] of [['toilet','bladder'],['market','hunger'],['detective_home','energy']]){
   const spot=c.DATA.landmarks.find(p=>p.id===id);
   Object.assign(s,c.nearest(spot.x-12,spot.y));
   c.care(need,true);got[need]=s.goal?.id;c.clearRoute();
  }
  c.reset();
  const renderPeople=autumnPedestrians(c.DATA);
  const park={...s,camX:355,camY:1178,streetTime:0};
  const visitors=t=>renderPeople({...park,streetTime:t},236).filter(n=>n.depth>=1206&&n.depth<=1290);
  const samples=[0,1,2,20,21,22,42].map(visitors);
  return {got,count:samples[0].length,
    continuous:samples[0].every((n,i)=>Math.hypot(n.x-samples[1][i].x,n.y-samples[1][i].y)<=14),
    vendors:renderPeople({...park,camY:1350},236).filter(n=>n.vendor).length};
 });
 assert.deepEqual(local.got,{bladder:'toilet',hunger:'market',energy:'detective_home'});
 assert.equal(local.count,4);assert(local.continuous);assert.equal(local.vendors,4);
 const originalLook=await p.evaluate(()=>JSON.stringify(look));
 const nav=await p.evaluate(()=>{const c=seasonMapTest.ctl();return c.DATA.landmarks.map(p=>{const path=c.plan(p.x,p.y);let prev=c.state;const valid=path.every(n=>{const ok=Math.abs(n.x-prev.x)<.01||Math.abs(n.y-prev.y)<.01;prev=n;return ok});return {id:p.id,len:path.length,valid,end:path.at(-1),want:{x:p.x,y:p.y}}})});
 for(const n of nav){assert(n.valid,n.id);if(n.end)assert(Math.hypot(n.end.x-n.want.x,n.end.y-n.want.y)<.1,n.id);else assert.equal(n.id,'airstrip')}
 // Walk every landmark through the movement controller on the new road surface.
 const walked=await p.evaluate(()=>{
  const c=seasonMapTest.ctl();
  for(const {id,x,y} of c.DATA.landmarks){
   c.state.paused=false;c.goTo(x,y);
   for(let i=0;i<1000&&c.state.target;i++)c.tick(.25,0);
   if(Math.hypot(c.state.x-x,c.state.y-y)>1)return {blocked:id,x:c.state.x,y:c.state.y};
  }
  c.reset();
  return {count:c.DATA.landmarks.length};
 });
 assert.equal(walked.count,26,JSON.stringify(walked));
 // Simulation acceleration below moves along real graph segments, never teleports a route.
 async function finishRoute(){await p.evaluate(()=>{const c=seasonMapTest.ctl();c.state.paused=false;for(let i=0;i<10000&&(c.state.target||c.state.door);i++)c.tick(.1,.01)});}
 // The dialogue ignores clicks in the first 300 ms after each new line appears.
 async function advanceLine(){
  await p.waitForTimeout(320);
  await p.locator('.story-bubble').click();
 }
 async function talk(id){await p.evaluate(id=>seasonMapTest.ctl().converse(id),id);await drain();}
 async function drain(){for(let i=0;i<35;i++){if(await p.locator('.story-speech').isVisible())await advanceLine();else if(await p.locator('.autumn-panel').isVisible())await p.locator('.autumn-actions button').first().click();else return;}throw Error('dialog did not end')}
 // The requested left ascent is continuous; arrival reveals the distant mountains smoothly.
 const summit=await p.evaluate(()=>{const c=seasonMapTest.ctl(),spot=c.DATA.landmarks.find(p=>p.id==='lookout');c.state.paused=false;c.goTo(spot.x,spot.y);let maxJump=0;for(let i=0;i<12000&&(c.state.target||i<50);i++){const prev=c.state.camY;c.tick(.05,.05);maxJump=Math.max(maxJump,Math.abs(c.state.camY-prev))}for(let i=0;i<100;i++)c.tick(.016,.016);const out={x:c.state.x,y:c.state.y,want:spot,cam:c.state.camY,maxJump};c.reset();return out});assert.equal(summit.x,summit.want.x);assert.equal(summit.y,summit.want.y);assert(summit.y-summit.cam<=236&&summit.y-summit.cam>=28&&summit.maxJump<30,JSON.stringify(summit));
 // The lake frame changes with time and the water stays outside the walking surface.
 const lake=await p.evaluate(()=>{
  const c=seasonMapTest.ctl(),old={x:c.state.camX,y:c.state.camY,t:c.state.time};
  c.state.camX=690;c.state.camY=2050;
  const frames=[0,.85].map(t=>{
   c.state.time=t;c.draw();
   return c.renderCanvas.toDataURL();
  });
  c.state.camX=old.x;c.state.camY=old.y;c.state.time=old.t;
  return {motion:frames[0]!==frames[1],water:c.nearest(820,2100).d>13};
 });
 assert(lake.water && lake.motion);
 // Keyboard stops on release; minimap click starts a route, never teleports.
 await p.locator('#view').focus();const x0=await p.evaluate(()=>seasonMapTest.ctl().state.x);await p.keyboard.down('ArrowLeft');await p.waitForTimeout(220);await p.keyboard.up('ArrowLeft');const x1=await p.evaluate(()=>seasonMapTest.ctl().state.x);assert(x1<x0-1);await p.waitForTimeout(120);assert(Math.abs(await p.evaluate(()=>seasonMapTest.ctl().state.x)-x1)<.2);
 await p.locator('[data-kind=autumn] [data-map]').click();const map=await p.evaluate(()=>{const c=seasonMapTest.ctl(),p=c.DATA.landmarks.find(p=>p.id==='canteen'),sc=c.canvas.height/c.DATA.height;return {x:(342-c.DATA.width*sc)/2+p.x*sc,y:p.y*sc,hero:c.state.x}});box=await p.locator('#view').boundingBox();await p.mouse.click(box.x+map.x*box.width/342,box.y+map.y*box.height/236);assert(!await p.evaluate(()=>seasonMapTest.ctl().state.mapOpen));assert(await p.evaluate(()=>!!seasonMapTest.ctl().state.target));assert(Math.abs(await p.evaluate(()=>seasonMapTest.ctl().state.x)-map.hero)<5);await p.evaluate(()=>seasonMapTest.ctl().reset());
 // The office's visible pixels are clickable at its authored position.
 const office=await p.evaluate(()=>{
  const c=seasonMapTest.ctl(),door=c.DATA.landmarks.find(p=>p.id==='detective_home');
  return c.hit(door.x,door.y-25)?.id;
 });
 assert.equal(office,'detective_home');
 await talk('jian');assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.quest),1);
 await p.evaluate(()=>{sim.needs.hunger=25;seasonMapTest.ctl().visit('canteen')});await finishRoute();const noodles=p.locator('#picker .pk-item').filter({hasText:'吃碗热面'});await noodles.waitFor();await noodles.click();
 await p.evaluate(()=>{const c=seasonMapTest.ctl();sim.needs.hunger=25;c.state.paused=false;c.stepNeeds(12)});assert(await p.evaluate(()=>sim.needs.hunger)>50);assert.equal(await p.evaluate(()=>sim.place),'autumn_test');fs.mkdirSync('/workspace/artifacts/autumn-game',{recursive:true});await p.locator('#view').screenshot({path:'/workspace/artifacts/autumn-game/polluted.png'});
 // Pause holds both needs and local service progress.
 const paused=await p.evaluate(()=>{speed=0;return seasonMapTest.ctl().state.service.elapsed});await p.waitForTimeout(130);assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.service.elapsed),paused);await p.evaluate(()=>speed=1);
 await p.evaluate(()=>{
  const c=seasonMapTest.ctl(),door=c.DATA.landmarks.find(p=>p.id==='detective_home');
  c.state.service=null;c.state.pose=null;c.goTo(door.x-38,door.y+10);
 });
 await finishRoute();
 const screenDoor=await p.evaluate(()=>{
  const c=seasonMapTest.ctl(),door=c.DATA.landmarks.find(p=>p.id==='detective_home');
  const bounds=view.getBoundingClientRect();
  return {x:bounds.left+(door.x-c.state.camX)*bounds.width/342,
          y:bounds.top+(door.y-25-c.state.camY)*bounds.height/c.canvas.height};
 });
 await p.mouse.click(screenDoor.x,screenDoor.y);
 await finishRoute();await p.getByRole('button',{name:'进屋',exact:true}).click();await finishRoute();assert(await p.evaluate(()=>seasonMapTest.ctl().state.inside));await p.waitForFunction(()=>sceneHouseHeight()===118);
 // owner 2026-11-11: the house runs the home's own acts (map-test/autumn_home.js → season_house.js); social is the phone
 for(const [need,act] of [['hunger','snack'],['energy','sleep'],['hygiene','bath'],['bladder','toilet'],['fun','season_sofa']]){await p.evaluate(need=>{const c=seasonMapTest.ctl();c.state.goal=null;seasonHouse.explore();sim.needs[need]=20;c.care(need,true)},need);await finishRoute();await p.waitForFunction(act=>sim.act===act&&autumnHome.svc,act,{timeout:5000});await p.evaluate(need=>{seasonHouse.explore();sim.meal=null;sim.needs[need]=95},need);await p.waitForFunction(()=>!autumnHome.svc,null,{timeout:3000})}
 fs.mkdirSync('/workspace/artifacts/autumn-game',{recursive:true});await p.locator('#view').screenshot({path:'/workspace/artifacts/autumn-game/inside.png'});
 await p.evaluate(()=>seasonMapTest.ctl().leave());await finishRoute();assert(!await p.evaluate(()=>seasonMapTest.ctl().state.inside));
 // Automatic hunger care remains local, including at night; multiple low needs do not ping-pong.
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.state.service=null;c.state.goal=null;sim.needs.hunger=20;sim.needs.energy=21;sim.t=23*60;
  c.clearRoute();c.playerInput();const now=performance.now.bind(performance);
  try{
   c.care('hunger');assertIdle();
   const spot=c.DATA.landmarks.find(p=>p.id==='market');c.goTo(spot.x,spot.y);
   performance.now=()=>now()+21000;
   c.care('hunger');if(c.state.goal||!c.state.target)throw Error('need interrupted manual route');
   c.clearRoute();step(1,.05);
  }finally{performance.now=now;}
  function assertIdle(){if(c.state.target||c.state.goal||c.state.door)throw Error('need interrupted manual grace');}});
 assert(await p.evaluate(()=>seasonMapTest.ctl().state.goal?.id==='detective_home'||seasonMapTest.ctl().state.goal?.id==='home_use'||seasonMapTest.ctl().state.door?.need==='hunger'));await finishRoute();await p.waitForFunction(()=>['fridge','stove','table'].includes(autumnHome.svc?.id),null,{timeout:5000});assert.equal(await p.evaluate(()=>sim.place),'autumn_test');
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.state.goal=null;seasonHouse.explore();sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));sim.t=720});
 // Approved story can be completed explicitly, preserving every chapter effect.
 for(const who of ['qing','zhou'])await talk(who);await p.evaluate(()=>seasonMapTest.ctl().converse('doctor'));
 for(let i=0;i<25;i++){if((await p.locator('.story-words').textContent()).startsWith('诊所里好几个'))break;await advanceLine()}
 await p.keyboard.press('Escape');assert(!await p.locator('.autumn-panel').isVisible());assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.quest),1);await talk('qing');assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.stage),1);
 await talk('father');assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.stage),2);
 await talk('doctor');await talk('zhou');await talk('qing');assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.stage),3);
 await talk('qing');await p.evaluate(()=>seasonMapTest.ctl().interact('townhall'));await drain();assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.stage),4);
 await p.evaluate(()=>seasonMapTest.ctl().interact('plaza'));await drain();assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.quest),6);
 await p.evaluate(()=>openWardrobe());assert(!(await coat.isDisabled()));await p.evaluate(()=>closeWardrobe());
 // Optional office visit does not grant stats, work penalties or a service.
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.state.service=null;c.interact('mine_office')});await drain();assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.service),null);
 await p.emulateMedia({reducedMotion:'reduce'});
 // All desktop scales: card remains within scenic window; scroll handles long text.
 for(const size of [25,50,75,100]){await p.evaluate(size=>{prefs.scale=size;fit();seasonMapTest.ctl().interact('notice')},size);const bounds=await p.evaluate(()=>{const a=document.querySelector('.autumn-panel').getBoundingClientRect(),b=view.getBoundingClientRect();return {w:Math.abs(a.width-b.width),below:a.top>=b.bottom-1,fs:parseFloat(getComputedStyle(document.querySelector('.autumn-panel-body')).fontSize)}});assert(bounds.w<2&&bounds.below&&bounds.fs>=13,JSON.stringify({size,bounds}));await p.locator('.autumn-actions button').last().click();}
 await p.evaluate(()=>{prefs.scale=50;fit();const c=seasonMapTest.ctl();c.state.inside=false;c.visit('lookout')});await finishRoute();await drain();await p.locator('#view').screenshot({path:'/workspace/artifacts/autumn-game/city.png'});
 await p.evaluate(async()=>store.save(snapshot()));await p.reload();await p.waitForFunction(()=>booted&&seasonMapTest.state.autumn.state.loaded);assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.quest),6);assert.equal(await p.evaluate(()=>JSON.stringify(look)),originalLook);
 // Upgrade a saved large-map position while retaining the finished story and discoveries.
 const migrated=await p.evaluate(()=>{const save=snapshot();for(const row of [save.testAutumn,save.seasonMapTest.state]){delete row.layoutVersion;row.x=900;row.y=1100;row.liftY=1048;row.found=['notice']}restore(save);const c=seasonMapTest.ctl();return {x:c.state.x,y:c.state.y,q:c.state.quest,found:c.state.found,lift:c.state.liftY,version:c.state.layoutVersion,want:c.DATA.landmarks[0]}});assert.equal(migrated.version,6);assert.equal(migrated.q,6);assert.deepEqual(migrated.found,['notice']);assert.equal(migrated.x,migrated.want.x);assert.equal(migrated.y,migrated.want.y);assert(migrated.lift<=744);
 await p.evaluate(()=>{seasonMapTest.start('home');sim.windup=null;startAct('go_home')});await p.waitForFunction(()=>sim.place==='home'&&!wiping);assert.equal(await p.evaluate(()=>sceneHouseHeight()),118);
 assert.equal(await p.evaluate(()=>snapshot().testAutumn.quest),6);assert.deepEqual(errors,[]);console.log('PASS autumn game: test-toolbar entry, all hotspots reachable by orthogonal graph, local house/services and pause, no automatic departure/need oscillation, full story stages, four-scale cards, save/reload, explicit return, native look, no page errors');
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
