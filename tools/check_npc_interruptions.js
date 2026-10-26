// Regressions found by auditing concurrency and older-save behaviour.
const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'}),errors=[],failures=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8786/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1500);
 await page.evaluate(()=>{
  closeGuide();closePicker();closeSocialSheet();hidePeerSay(true);cardMoment=()=>false;rollCard=()=>false;rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e9;
  window.interruptionAt=(place='front')=>{
   stopNpcTalk('',false);remoteSocial=null;sayQueue.length=0;clearTimeout(popSay._t);clearTimeout(popSay._t2);hidePeerSay(true);closePicker();closeSocialSheet();speed=0;
   sim.place=place;sim.t=place==='bar'?1200:720;sim.mode='idle';sim.act=null;sim.windup=null;sim.chosen=null;sim.item=null;sim.talk=null;sim.down=null;sim.queue=[];sim.outBack=null;sim.bar=null;sim.park=null;sim.idleUntil=Infinity;
   sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));sim.route=[[145,OUT[place].feet]];sim.s=sim.target=0;weather.force=weather.kind='clear';arriveAt(place);
   const person=socialState.world.find(c=>!c.child&&!socialState.contacts.some(p=>p.id===c.id));
   const n=place==='bar'?barScene.guests[0]:makeNpc('walker',{x:161,feet:107,layer:'front',v:12,dir:1});
   if(place!=='bar'){n.personId=person.id;n.look=doll.normalize(person.look);n.ramps=doll.rampsOf(n.look);n.cache=new Map();}
   else{barScene.chat=null;barScene.nextChat=barScene.nextGuest=1e9;}
   life.npcs=place==='bar'?[barScene.bartender,...barScene.guests,barScene.performer]:[n];life.npcNext=life.chatNext=Infinity;life.npcTalked=new WeakSet();window.auditNpc=n;render();
  };
  window.beginAuditTalk=()=>{requestNpcTalk(auditNpc);speed=3;for(let i=0;i<200&&npcInteraction?.phase==='approach';i++)step(0,.05);speed=0;life.talkQ.lines=['先把眼前这一句认真说完。','>我在这里，听你慢慢说。'];life.talkQ.i=0;life.talkQ.wait=0;};
 });
 async function check(name,fn){try{await fn();console.log('PASS: '+name);}catch(e){failures.push(name+': '+e.message);console.error('FAIL: '+name+': '+e.message);}}
 await check('A phone conversation excludes automatic NPC exchanges',async()=>{
  const r=await page.evaluate(()=>{interruptionAt();if(!startContactTalk('dad','call'))throw Error('Phone fixture');const started=startNpcTalk(auditNpc);const result={started,q:!!life.talkQ,call:!!remoteSocial};stopNpcTalk();remoteSocial=null;return result;});assert.deepEqual(r,{started:false,q:false,call:true});
 });
 await check('Automatic NPC conversations reserve the phone/speech channel',async()=>{
  const r=await page.evaluate(()=>{interruptionAt();if(!startNpcTalk(auditNpc))throw Error('NPC fixture');sayShownAt=-Infinity;const accepted=requestIncomingCall('dad');restoreSocial(socialSnapshot());stopNpcTalk();return accepted;});assert.equal(r,false);
 });
 await check('Walking out of earshot cannot complete an encounter or add a friend',async()=>{
  const r=await page.evaluate(()=>{interruptionAt();const id=auditNpc.personId;startNpcTalk(auditNpc);life.talkQ.wait=0;advanceNpcTalk(.01);sim.route=[[20,OUT.front.feet]];sim.s=sim.target=0;for(let i=0;i<10&&life.talkQ;i++){life.talkQ.wait=0;advanceNpcTalk(.01);}return {talk:!!life.talkQ,known:socialState.contacts.some(c=>c.id===id),paused:!!auditNpc.paused};});assert.deepEqual(r,{talk:false,known:false,paused:false});
 });
 await check('Old saves reset absent NPC topic history rather than retaining future progress',async()=>{
  const r=await page.evaluate(()=>{interruptionAt();const older=JSON.parse(JSON.stringify(snapshot()));delete older.flags.npcChatSeen;lifeFlags.npcChatSeen={front:['adult_47']};restore(older);return lifeFlags.npcChatSeen||{};});assert.deepEqual(r,{});
 });
 await check('Loading a save discards speech from the abandoned timeline',async()=>{
  const r=await page.evaluate(()=>{interruptionAt();const saved=JSON.parse(JSON.stringify(snapshot()));showSay('读档以前的对话');sayQueue.push('旧时间线排队的话');restore(saved);return {pending:sayQueue.length,visible:!popSay.hidden};});assert.deepEqual(r,{pending:0,visible:false});
 });
 await check('Paused NPC speech remains visible until its reading time finishes',async()=>{
  const r=await page.evaluate(()=>{interruptionAt();beginAuditTalk();advanceNpcTalk(.01);life.talkQ.wait=0;advanceNpcTalk(.01);life.talkQ.wait=4;realClock+=10;render();placeNpcPills();return {wait:life.talkQ.wait,visible:npcPillEls.has(auditNpc)};});assert.deepEqual(r,{wait:4,visible:true});
 });
 await check('Departed NPCs cannot leave or recreate speech bubbles',async()=>{
  const r=await page.evaluate(()=>{interruptionAt();npcSay(auditNpc,'已经离场的人的话');auditNpc.gone=true;placeNpcPills();return npcPillEls.has(auditNpc);});assert.equal(r,false);
 });
 await check('Paused protagonist speech remains visible too',async()=>{
  await page.evaluate(()=>{interruptionAt();beginAuditTalk();advanceNpcTalk(.01);life.talkQ.wait=4;});await page.waitForTimeout(6100);
  const r=await page.evaluate(()=>({wait:life.talkQ?.wait,visible:!popSay.hidden,text:popSay.querySelector('span').textContent}));assert.equal(r.wait,4);assert.equal(r.visible,true);assert.ok(r.text.includes('眼前这一句'));
  await page.evaluate(()=>stopNpcTalk());await page.waitForTimeout(700);assert.ok(await page.evaluate(()=>popSay.hidden||!popSay.querySelector('span').textContent.includes('眼前这一句')),'Cancelled timer must release the old sentence; queued remarks may follow');
 });
 await check('Bar activity status describes the conversation rather than a seat or drink',async()=>{
  const r=await page.evaluate(()=>{interruptionAt('bar');beginAuditTalk();syncUI();return document.getElementById('doing').textContent;});assert.ok(r.includes('聊天'),r);
 });
 await check('Drink completion cannot overwrite an active conversation',async()=>{
  const r=await page.evaluate(()=>{interruptionAt('bar');beginAuditTalk();advanceNpcTalk(.01);const before=popSay.querySelector('span').textContent;sim.bar.drink=Object.keys(BAR_DRINKS)[0];sim.bar.remaining=0;barFinishDrink();return {same:popSay.querySelector('span').textContent===before,pending:sayQueue.length};});assert.equal(r.same,true);assert.ok(r.pending>0);
 });
 await check('Delayed bar words are delivered after the conversation finishes',async()=>{
  const r=await page.evaluate(()=>{if(!life.talkQ)throw Error('Expected bar conversation');while(life.talkQ){life.talkQ.wait=0;advanceNpcTalk(.01);}realClock+=8;updateMood();return {pending:sayQueue.length,text:popSay.querySelector('span').textContent};});assert.equal(r.pending,0);assert.ok(!r.text.includes('眼前这一句'));
 });
 await check('Automatic bartender dialogue is also protected from drink remarks',async()=>{
  const r=await page.evaluate(()=>{interruptionAt('bar');barChat('player');showSay('我先听酒保说完。');sim.bar.drink=Object.keys(BAR_DRINKS)[0];barFinishDrink();const waiting=popSay.querySelector('span').textContent.includes('听酒保说完');const queued=sayQueue.length;barScene.chat.wait=0;stepBar(0,.01);const replied=popSay.querySelector('span').textContent;realClock+=8;updateMood();return {waiting,queued,ended:!barScene.chat,delivered:popSay.querySelector('span').textContent!==replied};});assert.equal(r.waiting,true);assert.ok(r.queued>0);assert.equal(r.ended,true);assert.equal(r.delivered,true);
 });
 await check('An urgent trip home interrupts bartender dialogue and speaks immediately',async()=>{
  const r=await page.evaluate(()=>{interruptionAt('bar');barChat('player');showSay('我先听酒保说完。');sim.needs.energy=10;stepBar(0,.01);return {place:sim.place,q:!!life.talkQ,text:popSay.querySelector('span').textContent};});assert.equal(r.place,'home');assert.equal(r.q,false);assert.ok(r.text.includes('回家'),r.text);
 });
 await check('Calls resume after NPC conversations and keep ten real seconds at 3x speed',async()=>{
  const before=await page.evaluate(()=>{interruptionAt();startNpcTalk(auditNpc);while(life.talkQ){life.talkQ.wait=0;advanceNpcTalk(.01);}sayShownAt=-Infinity;if(!requestIncomingCall('dad'))throw Error('Call channel remained locked');speed=9;tickSocial(0,performance.now());window.auditCallAt=performance.now();return sim.t;});
  await page.waitForTimeout(9400);assert.equal(await page.evaluate(()=>phoneCall.phase),'ringing');assert.equal(await page.evaluate(()=>sim.t),before);await page.waitForFunction(()=>phoneCall.phase!=='ringing',null,{timeout:1800});assert.ok(await page.evaluate(()=>performance.now()-auditCallAt)>=9950);
 });
 assert.deepEqual(errors,[]);if(failures.length)throw Error(failures.join('\n'));console.log('PASS: NPC concurrency, distance, pause visibility, deferred speech and old-save reset.');
 }finally{await browser.close();}})().catch(e=>{console.error(e.message);process.exitCode=1;});
