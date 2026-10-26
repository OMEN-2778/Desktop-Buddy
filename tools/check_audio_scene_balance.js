const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  const p=await browser.newPage({ignoreHTTPSErrors:true,reducedMotion:'reduce'}),errors=[];
  p.on('pageerror',e=>errors.push(e.stack||e.message));
  await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);
  await p.evaluate(()=>{
   closeGuide();prefs.guided=true;prefs.autosave=false;speed=0;sim.t=720;sim.place='home';sim.mode='idle';sim.act=null;
   sim.idleUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));
   socialState.nextCall=socialState.nextVisit=1e9;cardMoment=rollCard=rollEvents=()=>false;
   weather.kind=weather.force='clear';for(const key of Object.keys(windowState))windowState[key]='closed';
   setSettingsOpen(true);
  });
  await p.locator('#volume-sfx').focus();await p.locator('#volume-sfx').press('End');
  await p.waitForFunction(()=>gameAudio.debug().state==='running');
  await p.evaluate(()=>setSettingsOpen(false));await p.waitForTimeout(700);
  const peak=()=>p.evaluate(()=>new Promise(resolve=>{
   let value=0;const until=performance.now()+800;
   const sample=()=>{value=Math.max(value,gameAudio.debug().effectsLevel);if(performance.now()<until)requestAnimationFrame(sample);else resolve(value);};sample();
  }));
  await p.evaluate(()=>gameAudio.sound('ui-click',.65,{gap:0}));const ui=await peak();assert.ok(ui>.0001);
  const levels={};
  for(const act of ['cook','bath','tv']){
   await p.evaluate(act=>{speed=1;startAct(act,true);if(sim.mode==='walk'){sim.s=sim.target;arrive();}sim.actEnd=sim.t+1000;gameAudio.tick(true);},act);
   await p.waitForFunction(()=>gameAudio.debug().loopDetails.some(e=>e.key==='action'&&e.filter));
   await p.waitForTimeout(500);
   if(act==='cook')assert.ok((await p.evaluate(()=>gameAudio.debug().loopPaths)).includes('SFX/processed/real-cooking-stir-cc0.mp3'));
   levels[act]=await peak();assert.ok(levels[act]>0,act+' must remain audible');
   assert.ok(levels[act]<ui*.8,act+' should stay below UI feedback: '+JSON.stringify({ui,levels}));
   assert.ok(Math.abs(await p.evaluate(()=>gameAudio.debug().actionVolume)-.4)<.00001);
   await p.evaluate(()=>{speed=0;sim.mode='idle';sim.act=null;gameAudio.tick(true);});await p.waitForTimeout(700);
  }
  await p.evaluate(()=>throughDoor('park'));await p.waitForFunction(()=>sim.place==='park'&&!wiping);
  const park=await p.evaluate(()=>{
   const results=[],before=sim.park;
   for(const zone of PARK_ZONES)for(const h of [12,22]){
    sim.park=parkState({zone:zone.id,seated:false});sim.t=h*60;weather.kind=weather.force='clear';
    results.push({zone:zone.id,h,beds:audioSceneBeds()});
   }
   sim.park=before;return results;
  });
  for(const row of park){
   for(const key of ['air','leaves','water','lake','pot'])assert.ok(!row.beds[key],JSON.stringify(row));
   if(row.h===12){assert.equal(row.beds.birds[0],'park-birds-cc0');assert.ok(!row.beds.night);}
   else {assert.equal(row.beds.night[0],'park-cicadas-cc0');assert.ok(!row.beds.birds);}
  }
  await p.evaluate(()=>{gameAudio.tick(true);});
  await p.waitForFunction(()=>gameAudio.debug().loopDetails.some(e=>e.key==='night'&&e.filter));
  assert.ok((await p.evaluate(()=>gameAudio.debug().loopPaths)).includes('SFX/processed/park-cicadas-cc0.mp3'));
  assert.deepEqual(errors,[]);
  console.log('PASS: quiet audible home cook/bath/TV below UI; all park zones use daytime birds/night cicadas; no water/leaves/wind bed',JSON.stringify({ui,levels,zones:park.length/2}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
