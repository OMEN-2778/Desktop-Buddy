const assert=require('node:assert/strict');const {chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:1100,height:850}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8785/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1700);
 async function prepare(scenario){await page.evaluate(scenario=>{
  closeGuide();closeSocialSheet();closeRing();closePicker();cardMoment=()=>false;rollCard=()=>false;rollEvents=()=>false;speed=0;
  socialState.guest=null;guestBubble.hidden=true;sim.place='home';sim.t=scenario==='night'?1380:720;sim.mode='idle';sim.act=null;sim.windup=null;sim.chosen=null;sim.item=null;sim.talk=scenario==='busy'?{i:0}:null;
  sim.route=[[D.spots.host[1],FLOOR_Y[0]]];sim.s=0;sim.target=0;sim.idleUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));
  if(scenario==='hungry')sim.needs.hunger=10;contactFor('friend','abu').affinity=scenario==='familiar'?8:65;
  socialState.nextCall=1e9;socialState.nextVisit=1e9;setContactsOpen(true);
 },scenario);await page.waitForTimeout(500);await page.locator('.contact-card[data-id="abu"]').scrollIntoViewIfNeeded();await page.waitForTimeout(150);await page.locator('.contact-card[data-id="abu"]').click();await page.waitForTimeout(400);}
 const invite=()=>page.locator('#contactActions [data-action="invite"]');
 for(const [scenario,reason]of [['busy','正在聊天'],['night','休息时间'],['familiar','先多聊聊天'],['hungry','有点饿或累了']]){
  await prepare(scenario);assert.notEqual(await invite().getAttribute('aria-disabled'),'true');await invite().click();
  await page.waitForTimeout(350);assert.ok((await page.locator('.social-sheet p').textContent()).includes(reason),scenario+' explains why');
  assert.equal(await page.evaluate(()=>socialState.guest),null);await page.locator('.social-sheet-close').click();
 }
 // The menu opened while chatting must use the current state when clicked.
 await prepare('busy');await page.evaluate(()=>sim.talk=null);await invite().click();
 assert.equal(await page.evaluate(()=>socialState.guest?.phase),'scheduled');
 const arrival=await page.evaluate(()=>socialState.guest.at-sim.t);assert.ok(arrival>=12&&arrival<=25);
 assert.ok((await page.locator('.social-sheet p').textContent()).includes('游戏已暂停'));
 assert.ok((await page.locator('#popSay span').textContent()).includes('游戏分钟后到'));
 await page.locator('.social-sheet button').filter({hasText:'恢复时间，等朋友来'}).click();assert.equal(await page.evaluate(()=>speed),1);
 await page.evaluate(()=>socialState.guest.at=sim.t);
 await page.waitForFunction(()=>homeVisitActive()&&sim.act==='host'&&sim.mode==='act',null,{timeout:15000});
 await page.evaluate(()=>setContactsOpen(true));await page.waitForTimeout(450);await page.locator('.contact-card[data-id="abu"]').scrollIntoViewIfNeeded();await page.waitForTimeout(150);await page.locator('.contact-card[data-id="abu"]').click();await page.waitForTimeout(400);
 assert.equal(await invite().textContent(),'送客');await invite().click();
 await page.waitForFunction(()=>socialState.guest===null,null,{timeout:10000});
 assert.deepEqual(errors,[]);console.log('PASS: real invitation button explains busy/night/familiar/hungry states, rechecks a finished chat without reopening, shows arrival time and pause/resume, receives and seats the guest, and sends them home.');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
