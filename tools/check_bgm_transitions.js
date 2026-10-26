// Exercise real media playback with slow/failed loads and real scene transitions.
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  const page=await browser.newPage({ignoreHTTPSErrors:true,reducedMotion:'reduce'}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>{
   const play=HTMLMediaElement.prototype.play;
   window.bgmHold='';window.bgmHeld=[];
   HTMLMediaElement.prototype.play=function(){
    const result=play.call(this);
    if(window.bgmHold&&this.src.includes(window.bgmHold)){
     window.bgmHold='';
     return result.then(()=>new Promise(resolve=>window.bgmHeld.push(resolve)));
    }
    return result;
   };
  });
  await page.goto(process.argv[2]||'http://127.0.0.1:8786/');
  await page.waitForFunction(()=>booted);
  await page.evaluate(()=>{
   closeGuide();prefs.guided=true;prefs.autosave=false;speed=0;sim.t=18*60;sim.place='home';sim.mode='idle';sim.act=null;
   sim.idleUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));
   socialState.nextCall=socialState.nextVisit=1e9;cardMoment=rollCard=rollEvents=()=>false;
   setSettingsOpen(true);
  });
  await page.locator('#volume-bgm').focus();await page.locator('#volume-bgm').press('End');
  const ready=()=>page.waitForFunction(()=>{const d=gameAudio.debug();return d.music===d.desiredMusic&&d.musicTime>.05;});
  await ready();
  await page.evaluate(()=>setSettingsOpen(false));
  for(const place of ['park','home','mall','home','bar','home','beach','home']){
   await page.evaluate(place=>throughDoor(place),place);
   await page.waitForFunction(place=>sim.place===place&&!wiping,place);await ready();
   await page.waitForTimeout(300);
   const d=await page.evaluate(()=>gameAudio.debug());
   assert.equal(d.tracks,1,place+' must release the old player');
   assert.equal(d.musicTracks[0].path,d.desiredMusic);
   console.log('PASS scene',place);
  }
  await page.evaluate(()=>throughDoor('park'));
  await page.waitForFunction(()=>sim.place==='park'&&!wiping);await ready();
  const visit=await page.evaluate(()=>{contactFor('friend','abu').affinity=75;return {accepted:requestFriendVisit('abu'),place:sim.place,wiping,card:cardHolds(),guest:!!socialState.guest,child:contactFor('friend','abu').child};});
  assert.equal(visit.accepted,true,JSON.stringify(visit));
  await page.waitForFunction(()=>atFriendHome()&&!wiping);await ready();
  assert.ok((await page.evaluate(()=>gameAudio.debug().music)).includes('/home/'));
  await page.evaluate(()=>leaveFriendHome());
  await page.waitForFunction(()=>sim.place==='home'&&!wiping);await ready();
  console.log('PASS friend home');
  // Hold a newly selected track's readiness: the old scene must still stop.
  await page.evaluate(()=>{bgmHold='BGM/park/';sim.place='park';gameAudio.tick(true);});
  await page.waitForFunction(()=>bgmHeld.length===1);
  await page.waitForTimeout(300);
  let d=await page.evaluate(()=>gameAudio.debug());
  assert.equal(d.music,'');assert.ok(!d.musicTracks.some(t=>t.path.includes('/home/')));
  // A → B → A: an older A promise must not replace the newer A player.
  await page.evaluate(()=>{sim.place='home';gameAudio.tick(true);});await ready();
  await page.evaluate(()=>{sim.place='park';gameAudio.tick(true);});await ready();
  await page.evaluate(()=>{bgmHeld.splice(0).forEach(resolve=>resolve());});
  await page.waitForTimeout(500);d=await page.evaluate(()=>gameAudio.debug());
  assert.equal(d.tracks,1);assert.equal(d.music,d.desiredMusic);assert.equal(d.musicTracks[0].retiring,false);
  // A failed outdoor track must not impose its 30-second backoff on home.
  await page.route('**/audio/BGM/mall/**',route=>route.fulfill({status:503,body:'unavailable'}));
  await page.evaluate(()=>{sim.place='mall';gameAudio.tick(true);});
  await page.waitForFunction(()=>gameAudio.debug().stats.errors.some(e=>e.path.includes('/mall/')));
  const began=Date.now();
  await page.evaluate(()=>{sim.place='home';gameAudio.tick(true);});await ready();
  assert.ok(Date.now()-began<5000,'Home must not wait for the mall retry delay');
  await page.waitForTimeout(300);
  // Revisiting a failed destination during backoff must also stop home music.
  await page.evaluate(()=>{sim.place='mall';gameAudio.tick(true);});await page.waitForTimeout(300);
  d=await page.evaluate(()=>gameAudio.debug());assert.equal(d.music,'');assert.equal(d.tracks,0);
  await page.evaluate(()=>{sim.place='home';gameAudio.tick(true);});await ready();
  assert.deepEqual(errors,[]);
  console.log('PASS: real scene round trips; slow loads silence old scene; A-B-A promise race; failed-track retry isolation; no stale BGM during backoff');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
