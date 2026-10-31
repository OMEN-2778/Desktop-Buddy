// Focused regression for owner-requested seasonal test-page polish.
const assert=require('node:assert/strict'),fs=require('fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1400,height:1100},reducedMotion:'no-preference',ignoreHTTPSErrors:true}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 if(process.argv[2])await p.goto(process.argv[2]);else{await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');}
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&seasonMapTest.state.summer.state.loaded&&seasonMapTest.state.spring.state.loaded);
 await p.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=720;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;seasonMapTest.cheats.flags.hero=true;seasonMapTest.cheats.enforce();});
 async function depart(dest){await p.evaluate(dest=>{if(sim.place==='home'){seasonMapTest.start(dest);sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();}else seasonMapTest.start(dest);},dest);await p.waitForFunction(dest=>sim.place===dest&&!wiping,dest,{timeout:20000});}
 await depart('spring_test');
 for(let i=0;i<6;i++){await p.evaluate(i=>seasonMapTest.ctl().go(i,80),i);await p.waitForTimeout(80);assert.equal(await p.evaluate(()=>life.npcs.length),i<3?2:0);}
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.go(1,328);c.target(342);c.tick(.02);});assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.scene),2);
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.go(0,90);seasonMapTest.people.sync();const n=life.npcs[0];n.x=110;n.paused=true;seasonMapTest.people.click(n.x,90);});
 await p.waitForFunction(()=>!!life.talkQ,{timeout:10000});
 await p.evaluate(()=>{const n=life.talkQ.n;for(let i=0;i<10&&life.talkQ;i++){life.talkQ.wait=0;advanceNpcTalk(1);}window.testKnown=socialState.contacts.some(c=>c.id===n.personId);});assert(await p.evaluate(()=>window.testKnown));
 await depart('summer_test');
 assert.deepEqual(await p.evaluate(()=>({swim:life.npcs.filter(n=>n.seasonKind==='swim').length,dive:life.npcs.filter(n=>n.seasonKind==='dive').length})),{swim:4,dive:2});
 // Clicking the whole hut, not a door-only hotspot; wait for left entry.
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.state.x=480;c.state.y=c.gr(480);c.pick(500,c.gr(500)-50);});
 await p.waitForFunction(()=>seasonMapTest.ctl().state.inCabana,{timeout:15000});assert(await p.locator('.bay-wardrobe').isVisible());
 const frozen=await p.evaluate(()=>sim.t);await p.waitForTimeout(150);assert.equal(await p.evaluate(()=>sim.t),frozen);
 await p.locator('.bay-wardrobe [data-suit="wetsuit"]').click();assert.equal(await p.evaluate(()=>seasonMapTest.ctl().state.suit),'wetsuit');assert(await p.evaluate(()=>seasonMapTest.ctl().state.target.x>seasonMapTest.ctl().state.x));
 // Reach deep water, no oxygen HUD/timer, slow travel and high-resolution camera.
 const r=await p.evaluate(()=>{const c=seasonMapTest.ctl();c.state.x=2100;c.state.y=200;c.state.target=null;c.state.camX=1950;c.state.camY=100;c.state.paused=false;c.goTo(2150,'dive',200);const x=c.state.x;for(let i=0;i<60;i++)c.tick(1/60);return {distance:c.state.x-x,height:c.canvas.height,renderW:c.renderCanvas.width,viewW:view.width};});
 assert(r.distance>5&&r.distance<13);assert.equal(r.height,236);assert.equal(r.renderW,r.viewW);
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.state.target=null;for(let i=0;i<100;i++)c.tick(1);});assert(await p.evaluate(()=>seasonMapTest.ctl().state.y>135));
 // Both pets, including independent low-demand timers; verify opt-out resumes decay.
 const cheats=await p.evaluate(()=>{const before=petSnapshot();const offers=PetRules.weekly(petState,sim.t,D.pets.breeds);for(let i=petState.pets.length;i<2;i++){if(!PetRules.adopt(petState,offers[i],'测试',sim.t))throw Error('Test adoption failed');petState.pets.at(-1).status='home';}for(const p of petState.pets){p.status='home';p.needs={hunger:2,energy:3,company:4};p.low={hunger:100,energy:100,company:100};}const cheats=seasonMapTest.cheats;cheats.flags.pets=true;cheats.enforce();tickPets(sim.t,sim.t+10);const out=petState.pets.map(p=>({needs:p.needs,low:p.low}));cheats.flags.hero=false;sim.needs.hunger=80;step(1,.1);const decay=sim.needs.hunger<80;restorePets(before);return {out,decay};});assert.equal(cheats.out.length,2);for(const p of cheats.out){assert(Object.values(p.needs).every(v=>v===100));assert(Object.values(p.low).every(v=>v===0));}assert(cheats.decay);
 // Check pixel wardrobe bounds at all supported desktop scales and NPC re-entry.
 for(const size of [25,50,75,100]){await p.evaluate(size=>{speed=0;prefs.scale=size;fit();const c=seasonMapTest.ctl();c.state.inCabana=true;c.wardrobe.hidden=false;},size);const r=await p.evaluate(()=>{const d=document.querySelector('.bay-wardrobe'),r=d.getBoundingClientRect(),v=view.getBoundingClientRect();return {left:r.left-v.left,right:r.right-v.right,overflow:d.scrollWidth>d.clientWidth+1};});assert(r.left>=0&&r.right<=0&&!r.overflow);}
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.leaveCabana('wetsuit');sim.place='home';arriveAt('home');sim.place='summer_test';arriveAt('summer_test');prefs.scale=50;fit();});assert.equal(await p.evaluate(()=>life.npcs.length),9);
 await p.evaluate(()=>{speed=0;const c=seasonMapTest.ctl();c.state.x=2450;c.state.y=580;c.state.camX=2280;c.state.camY=450;});await p.waitForTimeout(100);
 fs.mkdirSync('/workspace/artifacts/season-polish',{recursive:true});await p.locator('#widget').screenshot({path:'/workspace/artifacts/season-polish/deep.png'});
 assert.deepEqual(errors,[]);console.log('PASS seasonal polish: public/private NPC regions, early edge switch, native NPC friendship, 4 swimmers/2 divers, whole-hut entry/choice/exit + paused time, slower diving/no oxygen timeout, high-resolution render, both pets + hero need cheats, zero page errors');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
