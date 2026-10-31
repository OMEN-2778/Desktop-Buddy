// Actual game shell + test-only map adapters. Exercises live transition, needs and save state.
const assert=require('node:assert/strict'),fs=require('fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1500,height:1200},ignoreHTTPSErrors:true,reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error('PAGE:',e.message);});
 if(process.argv[2])await p.goto(process.argv[2]);else{await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');}
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.seasonMapTest?.state.spring.state.loaded&&seasonMapTest.state.summer.state.loaded);
 await p.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=720;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,90]));});
 const initial=await p.evaluate(()=>({look:JSON.stringify(look),key:SAVE_KEY,rings:RINGS.door.map(r=>r[0])}));assert.equal(initial.key,'season-test-buddy-save');assert(initial.rings.includes('go:spring_test')&&initial.rings.includes('go:summer_test'));
 fs.mkdirSync('/workspace/artifacts/season-game',{recursive:true});
 async function depart(dest){await p.evaluate(dest=>{if(sim.place==='home'){seasonMapTest.start(dest);sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();}else seasonMapTest.start(dest);},dest);await p.waitForFunction(dest=>sim.place===dest&&!wiping,dest,{timeout:20000});}
 await depart('spring_test');assert.equal(await p.evaluate(()=>sim.act),'season_explore');
 const before=await p.evaluate(()=>({t:sim.t,hunger:sim.needs.hunger,x:seasonMapTest.ctl().state.x}));
 const box=await p.locator('#view').boundingBox();await p.mouse.click(box.x+box.width*.8,box.y+box.height*.87);await p.waitForTimeout(500);
 const after=await p.evaluate(()=>({t:sim.t,hunger:sim.needs.hunger,x:seasonMapTest.ctl().state.x,at:here().x,look:JSON.stringify(look)}));assert(after.t>before.t&&after.hunger<before.hunger&&after.x>before.x+2);assert(Math.abs(after.at-after.x)<2);assert.equal(after.look,initial.look);
 for(let i=0;i<6;i++){await p.locator('#season-spring-maps button').nth(i).click();await p.waitForTimeout(80);}assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.scene),5);
 await p.locator('#view').screenshot({path:'/workspace/artifacts/season-game/spring.png'});
 const saved=await p.evaluate(()=>{const save=JSON.parse(JSON.stringify(snapshot()));restore(save);return {place:sim.place,scene:seasonMapTest.ctl().state.scene};});assert.equal(saved.place,'spring_test');assert.equal(saved.scene,5);
 await depart('summer_test');await p.waitForTimeout(300);assert.equal(await p.evaluate(()=>sim.act),'season_explore');
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.state.suit='wetsuit';c.state.breath=90;c.state.x=1550;c.state.y=c.gr(1550)>120?130:100;c.state.camX=1400;c.pick(1570,180);});await p.waitForTimeout(800);
 assert(await p.evaluate(()=>seasonMapTest.ctl().canvas.height)>118);
 await p.locator('#view').screenshot({path:'/workspace/artifacts/season-game/summer.png'});await p.locator('#widget').screenshot({path:'/workspace/artifacts/season-game/summer-game-ui.png'});
 const t=await p.evaluate(()=>{speed=0;return seasonMapTest.ctl().state.time;});await p.waitForTimeout(120);assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.time),t);await p.evaluate(()=>speed=1);
 await p.evaluate(async()=>{await store.save(snapshot());});await p.reload();await p.waitForFunction(()=>booted&&seasonMapTest.state.summer.state.loaded);await p.evaluate(()=>closeGuide());assert.equal(await p.evaluate(()=>sim.place),'summer_test');
 await p.evaluate(()=>{sim.needs.hunger=14;speed=1;});await p.waitForFunction(()=>sim.place==='home'&&!wiping,{timeout:20000});assert.equal(await p.evaluate(()=>sceneHouseHeight()),118);
 assert.equal(await p.evaluate(()=>JSON.stringify(look)),initial.look);assert.deepEqual(errors,[]);console.log('PASS actual game: both door destinations, native travel/home, live time/needs, same protagonist, all spring zones, summer height/swim, pause, separate saves/reload, emergency self-care home; no page errors');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
