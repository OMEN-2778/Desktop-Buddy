const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
 const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'no-preference'}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8781/');
 await page.waitForFunction(()=>typeof booted!=='undefined'&&booted);await page.waitForTimeout(1500);
 await page.evaluate(()=>{
  closeGuide();closePicker();closeRing();speed=0;sim.mode='idle';sim.act=null;sim.windup=null;sim.t=720;
  cardMoment=()=>false;rollCard=()=>false;rollEvents=()=>false;
  sim.idleUntil=Infinity;sim.graceUntil=Infinity;sim.needs={hunger:90,energy:70,hygiene:65,bladder:30,social:80,fun:12};
  socialState.nextCall=1e9;showSay('今天想和朋友聊聊天。');syncUI();
 });await page.waitForTimeout(650);
 fs.mkdirSync('/workspace/artifacts/social-hud',{recursive:true});
 const house=await page.locator('#view').boundingBox(),need=await page.locator('#needs').boundingBox(),sky=await page.locator('#skybar').boundingBox();
 assert.ok(Math.abs(need.width-sky.width)<1);assert.ok(Math.abs(need.x-house.x)<1);assert.ok(Math.abs(sky.x+sky.width-house.x-house.width)<1);
 assert.ok(need.y<house.y&&Math.abs(need.y-sky.y)<1,'Shared horizontal track line');
 await page.screenshot({path:'/workspace/artifacts/social-hud/compact.png'});
 await page.locator('#needs').hover();await page.waitForTimeout(90);
 const mid=await page.locator('#needsPanel').evaluate(el=>({opacity:+getComputedStyle(el).opacity,transform:getComputedStyle(el).transform}));
 assert.ok(mid.opacity>0&&mid.opacity<=1);assert.notEqual(mid.transform,'none','Popover is animating');
 const early=await page.locator('.need-well').evaluateAll(es=>es.map(e=>+getComputedStyle(e).opacity));
 assert.ok(early[0]>early[5]&&early[5]<.1,'Individual meters unfold one after another');
 await page.waitForTimeout(1000);assert.equal(await page.locator('#needs').getAttribute('aria-expanded'),'true');
 assert.equal(await page.locator('#needsPanel .need').count(),6);
 assert.deepEqual(await page.locator('#view').boundingBox(),house,'Expanding needs does not move the game');
 await page.screenshot({path:'/workspace/artifacts/social-hud/needs.png'});
 const panel=await page.locator('#needsPanel').boundingBox();await page.mouse.move(panel.x+panel.width/2,panel.y+30);await page.waitForTimeout(30);
 assert.equal(await page.locator('#needs').getAttribute('aria-expanded'),'false','Leaving the compact track closes even over the expanded panel');
 await page.waitForTimeout(70);const closing=await page.locator('.need-well').evaluateAll(es=>es.map(e=>+getComputedStyle(e).opacity));
 assert.ok(closing[5]<closing[0],'Meters fold in reverse order');
 await page.mouse.move(need.x+need.width/2,need.y+need.height/2);await page.waitForTimeout(60);
 assert.equal(await page.locator('#needs').getAttribute('aria-expanded'),'true','Interrupted closing reverses on the original compact track');
 await page.mouse.move(20,20);await page.waitForTimeout(700);assert.equal(await page.locator('#needs').getAttribute('aria-expanded'),'false');
 await page.locator('#moodFace').hover();await page.waitForTimeout(500);await page.locator('#networkTrigger').hover();await page.waitForTimeout(500);
 assert.equal(await page.locator('#contactsPanel').getAttribute('aria-hidden'),'false');
 for(const [selector,pseudo]of [['.needs-summary',null],['.needs-panel','::before'],['.contacts-panel','::before'],['.contact-card','::before'],['.affinity',null]]){
  const shape=await page.locator(selector).first().evaluate((el,pseudo)=>{const s=getComputedStyle(el,pseudo);return {clip:s.clipPath,radius:s.borderRadius};},pseudo);
  assert.ok(shape.clip.startsWith('polygon('),selector+' uses stepped pixel geometry');assert.equal(shape.radius,'0px');
 }
 assert.equal(await page.locator('#networkTrigger img').evaluate(img=>img.naturalWidth),16,'Use the palette-only pixel people icon');
 for(const selector of ['#networkTrigger','.contact-card'])assert.equal(await page.locator(selector).first().evaluate(el=>getComputedStyle(el).boxShadow),'none','Pixel frames must not inherit rectangular button shadows');
 assert.deepEqual(await page.locator('.contact-card').evaluateAll(els=>els.map(e=>e.dataset.id)),['dad','mom','abu']);
 assert.deepEqual(await page.locator('.contact-copy strong').allTextContents(),['爸爸','妈妈','阿布']);
 assert.equal(await page.locator('.settings').evaluate(el=>getComputedStyle(el).visibility),'hidden');
 await page.screenshot({path:'/workspace/artifacts/social-hud/contacts.png'});
 await page.locator('.contact-card[data-id="abu"]').click();await page.waitForTimeout(450);
 assert.equal(await page.locator('#contactActions button').count(),6);
 assert.equal(await page.locator('#contactActions [aria-disabled="true"]').count(),3);
 await page.screenshot({path:'/workspace/artifacts/social-hud/actions.png'});
 await page.locator('#contactActions [data-action="text"]').click();
 assert.equal(await page.evaluate(()=>sim.chosen?.item?.contactId),'abu');
 assert.equal(await page.evaluate(()=>sim.chosen?.item?.talk?.name),'阿布');
 assert.equal(await page.evaluate(()=>sim.windup?.act),'phone_text');
 await page.evaluate(()=>{
  sim.windup=null;startAct('phone_text');sim.s=sim.target;arrive();
  while(sim.talk.i<sim.item.talk.lines.length)playTalk(10);
  finishAct();
  if(!logEl.textContent.includes('和阿布发消息：')||!sim.item?.contactId)throw Error('Targeted message transcript');
  sim.mode='idle';sim.act=null;sim.item=null;sim.talk=null;
  if(!startContactTalk('dad','video'))throw Error('Video request');
  sim.windup=null;startAct('phone_video');sim.s=sim.target;arrive();
  if(sim.item.talk.name!=='爸爸'||sim.item.contactId!=='dad')throw Error('Targeted video identity');
  while(sim.talk.i<sim.item.talk.lines.length)playTalk(10);
  finishAct();if(!logEl.textContent.includes('和爸爸视频：'))throw Error('Video diary');
  sim.windup=null;sim.chosen=null;sim.mode='idle';sim.act=null;
  socialState.contacts.find(c=>c.id==='abu').dailyGain=0;
  const before=socialState.contacts.find(c=>c.id==='abu').affinity;
  finishContactTalk('abu','text');finishContactTalk('abu','video');finishContactTalk('abu','video');
  if(socialState.contacts.find(c=>c.id==='abu').affinity!==before+6)throw Error('Daily friendship gain cap');
  socialState.contacts.push({id:'oldfriend',name:'小满',family:null,affinity:99,look:doll.PRESETS.f});
  if(sortedContacts().map(c=>c.id).join()!=='dad,mom,oldfriend,abu')throw Error('Parents first, then affinity');
  const saved=socialSnapshot();restoreSocial(saved);if(JSON.stringify(socialSnapshot())!==JSON.stringify(saved))throw Error('Contact save round trip');
 });
 // Queue behind a fresh line; only the incoming UI holds the clock, not the two-second grace period.
 await page.evaluate(()=>{speed=3;sim.idleUntil=Infinity;sim.chosen=null;showSay('这句话至少要让我说完两秒。');requestIncomingCall('abu');});
 await page.waitForTimeout(1100);assert.equal(await page.evaluate(()=>phoneCall.phase),'waiting');
 await page.waitForFunction(()=>phoneCall.phase==='ringing');
 assert.equal(await page.locator('#incomingCall strong').textContent(),'好友阿布');
 assert.equal(await page.locator('#incomingCall .caller-copy span').textContent(),'打来电话，要接吗？');
 const paused=await page.evaluate(()=>({t:sim.t,needs:{...sim.needs},speed}));
 await page.waitForTimeout(700);assert.deepEqual(await page.evaluate(()=>({t:sim.t,needs:{...sim.needs},speed})),paused,'Ringing pauses time and needs without changing speed');
 await page.screenshot({path:'/workspace/artifacts/social-hud/incoming.png'});
 await page.locator('.call-answer').click();assert.equal(await page.evaluate(()=>phoneCall.phase),'accepting');await page.waitForTimeout(420);
 assert.equal(await page.evaluate(()=>phoneCall.phase),'idle');assert.equal(await page.locator('#incomingCall').isHidden(),true);
 assert.equal(await page.evaluate(()=>sim.chosen?.item?.contactId||sim.item?.contactId),'abu');
 // Decline/timeout must preserve an interrupted activity and its queue, and never reduce affection.
 const reject=await page.evaluate(()=>{
  speed=3;sim.windup=null;sim.chosen=null;sim.talk=null;sim.item=null;sim.mode='idle';sim.act=null;sim.queue=['read'];sim.idleUntil=Infinity;
  sayShownAt=-Infinity;requestIncomingCall('dad');tickSocial(0,performance.now());return {t:sim.t,affinity:socialState.contacts.find(c=>c.id==='dad').affinity};
 });
 assert.equal(await page.locator('#incomingCall strong').textContent(),'爸爸');
 await page.locator('.call-decline').click();assert.equal(await page.evaluate(()=>phoneCall.phase),'declining');await page.waitForTimeout(350);
 assert.deepEqual(await page.evaluate(()=>sim.queue),['read']);assert.equal(await page.evaluate(()=>socialState.contacts.find(c=>c.id==='dad').affinity),reject.affinity);
 await page.evaluate(()=>{sayShownAt=-Infinity;requestIncomingCall('mom');tickSocial(0,performance.now());});
 const ringStart=Date.now();await page.waitForFunction(()=>phoneCall.phase==='idle',null,{timeout:7500});
 assert.ok(Date.now()-ringStart>=5700&&Date.now()-ringStart<7200,'Six-second automatic rejection');
 assert.equal(await page.locator('#incomingCall').isHidden(),true);assert.deepEqual(await page.evaluate(()=>sim.queue),['read']);
 assert.ok(await page.locator('#log').textContent().then(t=>t.includes('六秒后停了')));
 // Restore legacy saves with no social payload; never restore a ringing pause.
 await page.evaluate(()=>{const saved=snapshot();delete saved.social;restore(saved);if(sortedContacts().slice(0,2).map(c=>c.id).join()!=='dad,mom'||phoneHolds())throw Error('Legacy social migration');speed=0;});
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(550);
 const mobile=await page.locator('#view').boundingBox();assert.ok(mobile.x>=0&&mobile.x+mobile.width<=390);
 await page.evaluate(()=>setContactsOpen(true));await page.waitForTimeout(450);await page.locator('.contact-card').first().click();await page.waitForTimeout(400);
 for(const box of await page.locator('#contactActions button').evaluateAll(es=>es.map(e=>({left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right}))))assert.ok(box.left>=0&&box.right<=390,'Mobile actions fit the viewport');
 await page.screenshot({path:'/workspace/artifacts/social-hud/mobile.png'});
 await page.emulateMedia({reducedMotion:'reduce'});await page.reload();await page.waitForFunction(()=>booted);await page.waitForTimeout(1400);
 await page.evaluate(()=>{closeGuide();speed=0;setNeedsOpen(true);setContactsOpen(false);});
 assert.equal(await page.locator('#needsPanel').evaluate(el=>getComputedStyle(el).transitionDuration),'0s');
 assert.deepEqual(errors,[]);
 console.log('PASS: pixel frames and glyph, staggered expand/reverse collapse, track-only hover, interrupted reversal, compact layout, stable parents-first contacts, action ring, targeted messages, capped affection, saved contacts, delayed incoming call, pause, distinct answer/decline, six-second timeout, legacy saves, mobile bounds and reduced motion.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
