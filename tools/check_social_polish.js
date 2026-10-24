// Real clock regression, strict house-bound overlays, and revised NPC/avatar inventory.
const assert=require('node:assert/strict'),{chromium}=require('playwright');require('node:fs').mkdirSync('/workspace/artifacts/social-hud',{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:1100,height:850}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8786/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1600);
 async function prepare(){await page.evaluate(()=>{closeGuide();closePicker();closeRing();closeSocialSheet();hidePeerSay(true);restoreSocial(socialSnapshot());cardMoment=()=>false;rollCard=()=>false;rollEvents=()=>false;speed=0;sim.t=720;sim.place='home';sim.mode='idle';sim.act=null;sim.talk=null;sim.item=null;sim.windup=null;sim.chosen=null;sim.idleUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));socialState.guest=null;socialState.nextCall=1e9;socialState.nextVisit=1e9;});}
 await prepare();
 await page.evaluate(()=>{
  for(const g of ['f','m']){if(doll.NAME_GROUPS[g][0].length!==57||doll.NAME_GROUPS[g][2].length!==33)throw Error('Name balance');}
  const saved=socialSnapshot(),friend=contactFor('friend','abu');saved.namePoolVersion=1;saved.worldStyleVersion=1;
  const unknown=saved.world.find(p=>!saved.contacts.some(c=>c.id===p.id));unknown.name='旧名字';const oldLook=JSON.stringify(unknown.look);
  restoreSocial(saved);if(contactFor('friend','abu').name!==friend.name)throw Error('Known person renamed');
  const updated=socialState.world.find(p=>p.id===unknown.id);if(updated.name==='旧名字')throw Error('Unmet names not migrated');
  if(JSON.stringify({...updated.look,name:undefined,style:undefined,acc:undefined})!==JSON.stringify({...JSON.parse(oldLook),name:undefined,style:undefined,acc:undefined}))throw Error('Unmet colours/outfit changed');
  const second=socialSnapshot();restoreSocial(second);if(JSON.stringify(socialState.world)!==JSON.stringify(second.world))throw Error('Migration repeats');
  if(new Set(socialState.world.map(p=>p.name)).size!==200)throw Error('Migrated duplicate names');
  const styles=['split_spike','part37','hedgehog','quiff','flat_top','wave_short','wave_long','mullet','updo','twist','braid'],acc=['half_glasses','flat_glasses','ribbon','bow_small','flower_clip','heart_clip','barrette','cap'];
  for(const style of styles)for(const wear of [[],['cap'],['cap','headphones'],['half_glasses'],['flat_glasses']])for(const bob of [0,1]){
    const lk=doll.normalize({...doll.PRESETS.f,style,acc:wear}),f={expr:'neutral',look:0,bob,sway:1,wave:null};
    if(!D.doll.layers[`head/${style}/${bob}/${wear.includes('cap')?1:0}`])throw Error('Missing hairstyle/hat layer');
    if(!doll.pixels(lk,f).some(v=>v)||!doll.pixelsBack(lk,f).some(v=>v)||!doll.sitPixels(doll.pixels(lk,f),lk).some(v=>v))throw Error('Avatar pose failed');
  }
  for(const a of acc)if(!D.doll.options.acc.some(o=>o[0]===a))throw Error('Missing accessory '+a);
  const lk=doll.normalize({acc:['glasses','half_glasses','flat_glasses','cap','beanie','cap']});
  if(lk.acc.filter(a=>D.doll.eyewear.includes(a)).length!==1||lk.acc.filter(a=>D.doll.hats.includes(a)).length!==1)throw Error('Conflicting eyewear/hats');
  if(SOCIAL_TEXT.visitReasons.length!==40||new Set(SOCIAL_TEXT.visitReasons.map(r=>r[1])).size!==40)throw Error('Visit reasons');
 });
 assert.equal(await page.locator('.need[data-k="fun"]').getAttribute('aria-label'),'娱乐');
 await page.evaluate(()=>setNeedsOpen(true));await page.waitForTimeout(600);
 assert.equal(await page.locator('.need .fill').first().evaluate(e=>getComputedStyle(e,'::after').animationPlayState),'running');
 await page.evaluate(()=>setNeedsOpen(false));
 // A new utterance fades the old text before replacing it; bursts keep the latest.
 await page.evaluate(()=>showSay('旧台词','阿布：',contactFor('friend','abu')));await page.waitForTimeout(750);
 await page.evaluate(()=>showSay('第一句新台词','阿布：',contactFor('friend','abu')));
 assert.ok((await page.locator('#peerBubble span').textContent()).includes('旧台词'));
 await page.waitForTimeout(65);const mid=await page.locator('#peerBubble>span').evaluate(e=>+getComputedStyle(e).opacity);assert.ok(mid>0&&mid<1);
 await page.evaluate(()=>showSay('最后一句新台词','阿布：',contactFor('friend','abu')));await page.waitForTimeout(380);
 assert.ok((await page.locator('#peerBubble span').textContent()).includes('最后一句'));assert.equal(await page.locator('#peerBubble>span').evaluate(e=>+getComputedStyle(e).opacity),1);
 await page.evaluate(()=>{peerSpeech.until=performance.now()+10;showSay('读完新台词再收起','阿布：',contactFor('friend','abu'));tickPeerSpeech(performance.now()+20);if(peerSpeech.phase!=='visible')throw Error('Old expiry cancelled a new line');});await page.waitForTimeout(350);
 if(process.env.ONLY!=='layout'){
 // Each real call lasts six seconds, including speed changes and unrelated frame clocks.
 for(const initialSpeed of [1,3,8]){
  await prepare();const start=await page.evaluate(v=>{speed=v;sayShownAt=-Infinity;requestIncomingCall('abu');tickSocial(0,performance.now());window.clockStart=performance.now();window.clockSim=sim.t;tickSocial(9999,performance.now()+1e9);return {t:clockSim,at:clockStart};},initialSpeed);
  assert.equal(await page.evaluate(()=>phoneCall.phase),'ringing');
  await page.waitForTimeout(3000);await page.evaluate(()=>speed=speed===3?1:3);
  await page.waitForTimeout(2400);assert.equal(await page.evaluate(()=>phoneCall.phase),'ringing','No early timeout at '+initialSpeed+'x');assert.equal(await page.evaluate(()=>sim.t),start.t);
  await page.waitForFunction(()=>phoneCall.phase!=='ringing',null,{timeout:1800});const elapsed=await page.evaluate(()=>performance.now()-clockStart);assert.ok(elapsed>=5950&&elapsed<7300,elapsed);
  await page.waitForTimeout(450);
 }
 // Manual polite decline and protected parent ignore; only explicit ignore may cost 1.
 for(const [id,action,loss]of [['abu','decline',0],['abu','ignore',1],['dad','ignore',0]]){
  await prepare();const result=await page.evaluate(({id,action})=>{const c=socialState.contacts.find(c=>c.id===id);c.rejectLoss=0;c.rejectDay=Math.floor(sim.t/1440);const before=c.affinity;showVisitOffer(c,SOCIAL_TEXT.visitReasons[1]);const random=Math.random;Math.random=()=>0;resolveVisitOffer(action);Math.random=random;return before-c.affinity;},{id,action});assert.equal(result,loss);
 }
 await prepare();await page.evaluate(()=>{const c=contactFor('friend','abu'),before=c.affinity;sayShownAt=-Infinity;requestIncomingCall(c.id,'visit');tickSocial(0,performance.now());finishIncomingCall(false,true);if(c.affinity!==before)throw Error('Unanswered visit invitation cost affinity');});
 // Automatic outcomes never ignore or penalise, and remain paused for real six seconds.
 for(const [v,random]of [[3,.99],[8,0]]){
  await prepare();const baseline=await page.evaluate(({v,random})=>{speed=v;const c=contactFor('friend','abu');window.visitRandom=Math.random;Math.random=()=>random;showVisitOffer(c,SOCIAL_TEXT.visitReasons[3]);window.visitAt=performance.now();return {t:sim.t,affinity:c.affinity};},{v,random});
  await page.waitForTimeout(5400);assert.equal(await page.evaluate(()=>socialSheet.hidden),false);assert.equal(await page.evaluate(()=>sim.t),baseline.t);
  await page.waitForFunction(()=>visitOffer.id===null,null,{timeout:1800});assert.ok(await page.evaluate(()=>performance.now()-visitAt)>=5950);
  assert.equal(await page.evaluate(()=>contactFor('friend','abu').affinity),baseline.affinity);
  assert.equal(await page.evaluate(()=>!!socialState.guest),random===0);await page.evaluate(()=>Math.random=visitRandom);
 }
 // Cancellation cannot resolve a replacement sheet six seconds later.
 await prepare();await page.evaluate(()=>{showVisitOffer(contactFor('friend','abu'));visitNotice('新提示','这是另一个窗口。');});assert.equal(await page.evaluate(()=>visitOffer.timer),0);
 }
 // Sample every animation frame, not just its final box, on desktop and phone.
 async function bounded(selector,animation=false){const result=await page.evaluate(async({selector,animation})=>{
  const target=document.querySelector(selector),violations=[];const check=()=>{const a=target.getBoundingClientRect(),b=view.getBoundingClientRect();if(a.left<b.left-.6||a.top<b.top-.6||a.right>b.right+.6||a.bottom>b.bottom+.6)violations.push([a.toJSON(),b.toJSON()]);};
  const end=performance.now()+(animation?720:0);do{check();await new Promise(requestAnimationFrame);}while(performance.now()<end);return violations;
 },{selector,animation});assert.equal(result.length,0,selector+' leaves house: '+JSON.stringify(result[0]));}
 for(const [width,height,scale]of [[1100,850,25],[1100,850,50],[1100,850,75],[390,844,'auto'],[320,640,'auto']]){
  await prepare();await page.setViewportSize({width,height});await page.evaluate(scale=>setScale(scale),scale);await page.waitForTimeout(200);
  await page.evaluate(()=>showVisitOffer(contactFor('friend','abu'),SOCIAL_TEXT.visitReasons[29]));await bounded('.social-sheet',true);
  for(const sel of ['.visit-ignore','.visit-accept','.visit-decline']){await bounded(sel);assert.ok(await page.locator(sel).isVisible());}
  await page.screenshot({path:`/workspace/artifacts/social-hud/visit-${width}-${scale}.png`});
  await page.evaluate(()=>{closeSocialSheet();showSocialMemories('abu');});await bounded('.social-sheet',true);
  await page.evaluate(()=>{closeSocialSheet();showCard(CARDS.find(c=>!c.service));});await bounded('#card',true);await bounded('#card .cd-opt[data-k="a"]');await bounded('#card .cd-opt[data-k="b"]');
  await page.screenshot({path:`/workspace/artifacts/social-hud/card-${width}-${scale}.png`});
  await page.evaluate(()=>chooseCard('a'));await page.waitForFunction(()=>card?.phase==='result');await bounded('#cardRes',true);await page.screenshot({path:`/workspace/artifacts/social-hud/result-${width}-${scale}.png`});
  await page.evaluate(()=>{clearTimeout(card.timer);card=null;cardEl.hidden=cardRes.hidden=true;dimHouse(false);});
 }
 // Every authored card must keep BOTH replies usable at the smallest phone size.
 const authored=await page.evaluate(()=>{const bad=[];for(const cd of CARDS){showCard(cd);clearTimeout(card.timer);cardEl.style.animation='none';cardEl.style.transform='none';const a=cardEl.getBoundingClientRect();for(const option of cardOpts){const b=option.getBoundingClientRect();if(b.left<a.left-.6||b.right>a.right+.6||b.top<a.top-.6||b.bottom>a.bottom+.6)bad.push(cd.n);}}cardEl.hidden=true;card=null;dimHouse(false);return {count:CARDS.length,bad};});
 assert.ok(authored.count>=600);assert.deepEqual(authored.bad,[]);
 assert.deepEqual(errors,[]);
 console.log('PASS: pool balance/save migration, 11 hairstyles/8 accessories, entertainment/stripes, smooth/latest peer speech, '+(process.env.ONLY==='layout'?'timing cases skipped':'six REAL seconds across simulation speeds, paused invites, manual-only penalty, timeout outcomes, timer cancellation')+', house bounds throughout animations at five sizes and all 600 authored cards.');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
