// Prototype houses remain isolated from real life, saves and social state.
const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1700,height:1400},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(1400);fs.mkdirSync('/workspace/artifacts/friend-houses',{recursive:true});
 await p.evaluate(()=>{closeGuide();closePicker();closeSocialSheet();closeRing();cardMoment=rollCard=rollEvents=()=>false;sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;sim.chosen=null;sim.idleUntil=Infinity;speed=0;socialState.nextCall=socialState.nextVisit=1e9;document.querySelector('.console').open=true;});
 assert.equal(await p.locator('#friendHouseSelect option').count(),31);
 await p.locator('#friendHouseSelect').selectOption('cream');
 assert.equal(await p.evaluate(()=>friendHousePreview?.id==='cream'&&cardHolds()),true);
 await p.locator('#setGear').click();assert.equal(await p.locator('#setPop').isVisible(),true,'Preview disables zoom/settings');await p.evaluate(()=>setSettingsOpen(false));
 const before=await p.evaluate(()=>{speed=6;sim.windup={act:'toilet',at:realClock+.1};return JSON.stringify({sim:snapshot().sim,social:socialSnapshot(),diary:snapshot().diary});});
 await p.waitForTimeout(500);assert.equal(await p.evaluate(()=>JSON.stringify({sim:snapshot().sim,social:socialSnapshot(),diary:snapshot().diary})),before,'Preview advances normal life');
 assert.equal(await p.evaluate(()=>saveGame()),false,'Preview writes a save');
 await p.evaluate(()=>{speed=0;sim.windup=null;});
 const keys=await p.evaluate(()=>Object.keys(D.friendHouses));
 let cases=0;
 for(const size of [25,50,75,100]){
  await p.evaluate(size=>setScale(size),size);
  for(const id of keys){
   await p.evaluate(id=>openFriendHousePreview(id),id);
   const issue=await p.evaluate(()=>{
    const h=D.friendHouses[friendHousePreview.id],r=view.getBoundingClientRect(),c=friendHouseControls.getBoundingClientRect();
    if(h.w>W||view.height!==Math.round(h.h*devPx)||Math.abs(r.width-W*scale)>1||Math.abs(r.height-h.h*scale)>1)return 'Image is stretched or clipped';
    if(c.left<r.left-1||c.right>r.right+1||c.top<r.bottom)return 'Controls overlap house / overflow';
    for(const e of friendHouseControls.querySelectorAll('button,select,label,p')){const q=e.getBoundingClientRect(),s=getComputedStyle(e);if(q.left<c.left||q.right>c.right||parseFloat(s.fontSize)<12||e.scrollWidth>e.clientWidth+2)return 'Clipped/tiny control '+e.textContent;}
    if(document.querySelector('.status-row').getBoundingClientRect().bottom>r.top+1)return 'Time/needs overlap house';
    return null;
   });assert.equal(issue,null,`${id} at${size}`);
   await p.locator('#view').screenshot({path:`/workspace/artifacts/friend-houses/game-${id}-${size}.png`});
   await p.locator('#friendHouseNight').check();await p.locator('#friendHouseFigures').uncheck();
   assert.equal(await p.evaluate(()=>friendHousePreview.night&&!friendHousePreview.figures),true);
   await p.locator('#friendHouseNight').uncheck();await p.locator('#friendHouseFigures').check();cases+=2;
  }
 }
 // Next/previous wrap; Escape restores dimensions and all simulation data.
 await p.locator('#friendHouseNext').click();assert.equal(await p.evaluate(()=>friendHousePreview.id),'cream');await p.locator('#friendHousePrev').click();assert.equal(await p.evaluate(()=>friendHousePreview.id),'walnut');
 const saved=await p.evaluate(()=>JSON.stringify({sim:snapshot().sim,social:socialSnapshot()}));
 await p.keyboard.press('Escape');assert.equal(await p.evaluate(()=>friendHousePreview===null&&view.height===Math.round(H*devPx)&&view.style.pointerEvents===''),true);
 assert.equal(await p.evaluate(()=>JSON.stringify({sim:snapshot().sim,social:socialSnapshot()})),saved);
 assert.equal(await p.evaluate(()=>friendHouseControls.closest('.console')!==null),true);
 // Motion is measured on a page with normal animations, not a reduced-motion stub.
 const m=await b.newPage({viewport:{width:1700,height:1400},reducedMotion:'no-preference'});m.on('pageerror',e=>errors.push(e.message));const link=new URL(process.argv[2]||'http://127.0.0.1:8786/');link.searchParams.set('house-preview','cream');await m.goto(link.href);await m.waitForFunction(()=>booted&&friendHousePreview?.id==='cream');await m.waitForTimeout(1300);
 await m.evaluate(()=>{closeGuide();closePicker();closeSocialSheet();closeRing();cardMoment=rollCard=rollEvents=()=>false;speed=0;openFriendHousePreview('cream');});await m.waitForTimeout(700);
 const start=await m.locator('#moodrow').boundingBox();const offsets=await m.evaluate(()=>['settings','diary','peerHud'].map(id=>document.getElementById(id)).filter(e=>!e.hidden).map(e=>[e.id,e.getBoundingClientRect().top-moodrow.getBoundingClientRect().top]));
 await m.evaluate(()=>openFriendHousePreview('library'));
 assert.equal(await m.evaluate(()=>friendHouseAnimations.length>=3),true,'No upward HUD animation');await m.waitForTimeout(180);const middle=await m.locator('#moodrow').boundingBox();assert.equal(await m.evaluate(offsets=>offsets.every(([id,y])=>Math.abs(document.getElementById(id).getBoundingClientRect().top-moodrow.getBoundingClientRect().top-y)<2),offsets),true,'Nested HUD children received the movement twice');await m.screenshot({path:'/workspace/artifacts/friend-houses/expanding-ui.png'});await m.waitForTimeout(600);const end=await m.locator('#moodrow').boundingBox();
 assert.ok(end.y<start.y-20&&middle.y> end.y&&middle.y<start.y,'HUD does not move smoothly upward');
 await m.evaluate(()=>{openFriendHousePreview('town');openFriendHousePreview('garden');});await m.waitForTimeout(700);assert.equal(await m.evaluate(()=>friendHousePreview.id),'garden');
 // An existing awake save with guided cards must open the gallery before any roll.
 await m.evaluate(async()=>{closeFriendHousePreview();prefs.guided=true;sim.place='home';sim.mode='act';sim.act='tv';sim.actEnd=sim.t+100;sim.t=720;lifeFlags.cards={seen:[],last:-1e9};speed=0;saveSettings();await saveGame();});
 await m.addInitScript(()=>{Math.random=()=>0;});link.searchParams.set('house-preview','library');await m.goto(link.href);await m.waitForFunction(()=>booted);assert.equal(await m.evaluate(()=>friendHousePreview?.id==='library'&&!card&&!guideOn),true,'A life event blocked direct preview from an existing save');
 const bad=await b.newPage();bad.on('pageerror',e=>errors.push(e.message));link.searchParams.set('house-preview','__proto__');await bad.goto(link.href);await bad.waitForFunction(()=>booted);assert.equal(await bad.evaluate(()=>friendHousePreview),null);
 assert.deepEqual(errors,[]);console.log('PASS:',keys.length,'house plans,',cases,'day/night four-scale previews, controls, clock/social/save isolation, wrap/exit, smooth upward HUD motion and rapid switching.');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
