// Real canvas clicks, approach/turn/resume, scene text, exclusions and interruptions.
const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
const dir='/workspace/artifacts/npc-social';fs.mkdirSync(dir,{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8786/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1500);
 await page.evaluate(()=>{
  closeGuide();closePicker();hidePeerSay(true);cardMoment=()=>false;rollCard=()=>false;rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e9;weather.force=weather.kind='clear';
  window.npcTestAt=(scene,role=null)=>{
   stopNpcTalk('',false);closePicker();closeSocialSheet();hidePeerSay(true);speed=0;sim.place=scene.startsWith('park_')?'park':scene;sim.t=scene==='bar'?1200:720;
   sim.park=sim.place==='park'?{zone:scene.slice(5),seated:false,goal:null}:null;sim.bar=null;sim.mode='idle';sim.act=null;sim.windup=null;sim.chosen=null;sim.item=null;sim.talk=null;sim.queue=[];sim.down=null;sim.outBack=null;sim.idleUntil=Infinity;
   sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));sim.route=[[60,OUT[sim.place].feet]];sim.s=sim.target=0;arriveAt(sim.place);
   if(sim.place==='mall'){mallS.x=1000;sim.route=[[MALL.at,MALL.feet]];sim.act='mall';sim.mode='act';sim.actEnd=Infinity;}
   const person=socialState.world.find(p=>!socialState.contacts.some(c=>c.id===p.id)&&!p.child);
   const n=scene==='bar'?barScene.guests[0]:makeNpc(role||(sim.place==='park'?'adult':sim.place==='mall'?'shopper':'walker'),{x:250,feet:107,layer:'front',dir:1,v:12});
   if(scene!=='bar'){n.personId=person.id;n.look=doll.normalize(person.look);n.ramps=doll.rampsOf(n.look);n.cache=new Map();}
   if(sim.place==='mall'){delete n.x;n.u=mallS.x+250-MALL.at;}
   if(scene==='bar'){barScene.nextChat=1e9;barScene.nextGuest=1e9;barScene.chat=null;}
   life.npcs=scene==='bar'?[barScene.bartender,...barScene.guests,barScene.performer]:[n];life.npcNext=life.chatNext=Infinity;life.npcTalked=new WeakSet();window.testNpc=n;
   render();return {id:n.personId,x:npcX(n),at:here().x,known:socialState.contacts.some(c=>c.id===n.personId)};
  };
  window.npcTestPoint=()=>{const n=testNpc,[f,pose]=npcFrame(n),cv=npcCanvas(n,f,pose,n.back),shape=outlineShape(cv);const points=[...shape.inside].map(s=>s.split(',').map(Number)).sort((a,b)=>(Math.abs(a[0]-10)+Math.abs(a[1]-8))-(Math.abs(b[0]-10)+Math.abs(b[1]-8)));return {x:Math.round(npcX(n)-DW/2)+points[0][0],y:Math.round(npcFeet(n)-DH+1)+points[0][1]};};
  for(const [key,groups]of Object.entries(NPC_TALK_TEXT)){
   const entries=[...groups.adult,...groups.kid];if(entries.length!==60||new Set(entries.map(e=>JSON.stringify(e))).size!==60)throw Error('Scene text count/duplicates '+key);
   for(const e of entries)for(const pair of ['mm','mf','fm','ff']){const line=v=>typeof v==='string'?v:v[pair];if(e.length!==5||e.slice(1).some(v=>!line(v))||!line(e[2]).startsWith('>')||!line(e[4]).startsWith('>'))throw Error('Dialogue turns '+key+'/'+pair);}
  }
 });
 const scenes=['front','park_gazebo','park_lakeside','park_central','park_meadow','park_grove','mall','beach','bar'];
 for(const scene of scenes){
  const start=await page.evaluate(scene=>npcTestAt(scene),scene),point=await page.evaluate(()=>npcTestPoint()),box=await page.locator('#view').boundingBox(),sc=await page.evaluate(()=>scale);
  await page.mouse.move(box.x+point.x*sc+.5,box.y+point.y*sc+.5);await page.waitForTimeout(80);
  assert.equal(await page.evaluate(()=>hoverNpc?.personId),start.id,scene+' actual sprite hover');
  if(scene==='park_central')await page.locator('#view').screenshot({path:dir+'/outline.png'});
  await page.mouse.click(box.x+point.x*sc+.5,box.y+point.y*sc+.5);
  assert.equal(await page.evaluate(()=>npcInteraction?.phase),'approach',scene+' click starts approach');assert.equal(await page.evaluate(()=>here().x),start.at,'No teleport');assert.equal(await page.evaluate(()=>!!life.talkQ),false);
  const approach=await page.evaluate(()=>{
   speed=3;const x=npcX(testNpc);for(let i=0;i<200&&npcInteraction?.phase==='approach';i++){step(0,.05);stepNpcs(.05);}
   speed=0;render();return {phase:npcInteraction?.phase,x:npcX(testNpc),hero:here().x,look:npcFrame(testNpc)[0].look,face:sim.facing,known:socialState.contacts.some(c=>c.id===testNpc.personId),count:life.talkQ?.lines.length,manual:life.talkQ?.manual};
  });
  assert.equal(approach.phase,'talk',scene+' arrives and talks');assert.equal(approach.manual,true);assert.ok(Math.abs(approach.x-approach.hero)>=8);assert.ok(Math.abs(approach.x-approach.hero)<=17);assert.equal(approach.look,-approach.face);
  if(!start.known)assert.equal(approach.known,false,'Approach never adds contacts');
  const text=await page.evaluate(()=>{const q=life.talkQ;for(let i=q.i;i<q.lines.length;i++){q.wait=0;advanceNpcTalk(.01);}
   placeNpcPills();const before=socialState.contacts.some(c=>c.id===q.n.personId),transcript=q.said.slice();return {before,transcript,npcBubble:npcPillEls.has(q.n),peer:peerSpeech.phase};});
  if(!start.known)assert.equal(text.before,false,scene+' last utterance must finish reading');assert.equal(text.npcBubble,true);assert.equal(text.peer,'idle','Scene NPC keeps their small bubble');
  if(scene==='park_grove')await page.screenshot({path:dir+'/grove-talk.png'});
  const done=await page.evaluate(()=>{life.talkQ.wait=0;advanceNpcTalk(.01);const c=socialState.contacts.find(c=>c.id===testNpc.personId),before=npcX(testNpc);stepNpcs(.1);return {active:!!npcInteraction,q:!!life.talkQ,c:c&&{id:c.id,affinity:c.affinity,memories:c.memories.length},moved:npcX(testNpc)!==before,dir:testNpc.dir};});
  assert.equal(done.active,false);assert.equal(done.q,false);assert.ok(done.c);assert.ok(done.c.memories>0);if(scene!=='bar'){assert.equal(done.moved,true,'Walker resumes');assert.equal(done.dir,1,'Original travel direction restored');}
 }
 await page.evaluate(()=>{npcTestAt('front');const upper=makeNpc('walker',{x:250,feet:107,layer:'front',dir:-1,v:10});life.npcs.push(upper);if(npcAt(250,92)!==upper)throw Error('Overlapping NPC hit order disagrees with paint order');});
 // Exercise all four gender pairings through the actual speaking runner.
 await page.evaluate(()=>{const original=look;for(const scene of Object.keys(NPC_TALK_TEXT)){
   const spoken=[];for(const [heroGender,npcGender]of [['m','m'],['m','f'],['f','m'],['f','f']]){
    npcTestAt(scene);setLook({...look,gender:heroGender});testNpc.look=doll.normalize({...testNpc.look,gender:npcGender});
    const row=NPC_TALK_TEXT[scene].adult[scene==='bar'?30:24];startNpcTalk(testNpc);
    life.talkQ.lines=row.slice(1);life.talkQ.title=row[0];while(life.talkQ&&life.talkQ.i<life.talkQ.lines.length){life.talkQ.wait=0;advanceNpcTalk(.01);}
    const text=life.talkQ.said.map(v=>v[1]).join(' / ');if(/[{}]/.test(text))throw Error('Unresolved gender text '+scene);spoken.push(text);stopNpcTalk();
   }if(new Set(spoken).size!==4)throw Error('Gender pairs have identical dialogue '+scene);
  }
  for(const gender of ['m','f']){npcTestAt('park_central','kid');setLook({...look,gender});const row=NPC_TALK_TEXT.park_central.kid[6];startNpcTalk(testNpc);life.talkQ.lines=row.slice(1);while(life.talkQ.i<2){life.talkQ.wait=0;advanceNpcTalk(.01);}const text=life.talkQ.said[1][1];if(!text.includes(gender==='m'?'哥哥':'姐姐'))throw Error('Child address mismatches protagonist');stopNpcTalk();}
  setLook(original);
 });
 // Familiar faces gain affection only on completion, within the existing daily cap.
 await page.evaluate(()=>{npcTestAt('front');const n=testNpc;for(let round=0;round<12;round++){
   requestNpcTalk(n);speed=3;for(let i=0;i<200&&npcInteraction?.phase==='approach';i++)step(0,.05);speed=0;
   while(life.talkQ){life.talkQ.wait=0;advanceNpcTalk(.01);}
  }const c=socialState.contacts.find(c=>c.id===n.personId);if(c.affinity!==14||c.dailyGain!==6)throw Error('Repeated chat exceeded daily cap');});
 await page.evaluate(()=>{npcTestAt('park_meadow','kid');const t=chooseNpcTalk(testNpc);if(!t.id.startsWith('kid_'))throw Error('Child uses adult text');});
 await page.dispatchEvent('#view','pointerleave');assert.equal(await page.evaluate(()=>hoverNpc),null);
 // The bartender uses the same approach/face/complete path without interrupting the stage.
 await page.evaluate(()=>{npcTestAt('bar');testNpc=barScene.bartender;requestNpcTalk(testNpc);speed=3;for(let i=0;i<200&&npcInteraction?.phase==='approach';i++)step(0,.05);speed=0;if(npcInteraction?.phase!=='talk')throw Error('Bartender approach');while(life.talkQ){life.talkQ.wait=0;advanceNpcTalk(.01);}if(npcInteraction)throw Error('Bartender release');});
 await page.evaluate(()=>{npcTestAt('bar');const n=barScene.bartender,[f,pose]=npcFrame(n),body=outlineShape(npcCanvas(n,f,pose)),counter=outlineShape(IMG.out.bar.counter);const covered=[...body.inside].map(v=>v.split(',').map(Number)).map(([x,y])=>[x+n.x-10,y+n.feet-DH+1]).filter(([x,y])=>counter.inside.has(x+','+y));if(!covered.length)throw Error('Counter coverage fixture');for(const [x,y]of covered)if(npcAt(x,y)===n)throw Error('Click passed through counter');});
 // Workers and fishers keep their pre-existing service interactions.
 for(const [scene,role]of [['park_grove','clerk'],['mall','clerk'],['mall','hawker'],['beach','fisher']]){
  await page.evaluate(({scene,role})=>{npcTestAt(scene,role);if(role==='fisher')testNpc.rod=true;render();},{scene,role});
  assert.equal(await page.evaluate(()=>canClickNpc(testNpc)),false);assert.equal(await page.evaluate(()=>requestNpcTalk(testNpc)),false);assert.equal(await page.evaluate(()=>npcInteraction),null);
  const point=await page.evaluate(()=>npcTestPoint()),box=await page.locator('#view').boundingBox(),sc=await page.evaluate(()=>scale);await page.mouse.move(box.x+point.x*sc+.5,box.y+point.y*sc+.5);assert.equal(await page.evaluate(()=>hoverNpc),null);
 }
 // A pending WC/meal journey must not lose its route to a chat click.
 await page.evaluate(()=>{npcTestAt('mall');mallS.toilet={phase:'search'};if(canClickNpc(testNpc)||requestNpcTalk(testNpc))throw Error('Interrupted mall WC search');mallS.toilet=null;mallS.visit={kind:'restaurant',phase:'search'};if(canClickNpc(testNpc)||requestNpcTalk(testNpc))throw Error('Interrupted meal search');npcTestAt('bar');sim.bar.toilet={phase:'walk',left:10};if(canClickNpc(testNpc)||requestNpcTalk(testNpc))throw Error('Interrupted bar WC route');});
 // Pausing, urgent services, another click, departure, restore and a vanished target.
 await page.evaluate(()=>{npcTestAt('front');requestNpcTalk(testNpc);speed=3;for(let i=0;i<200&&npcInteraction.phase==='approach';i++)step(0,.05);life.talkQ.wait=4;speed=0;});
 await page.waitForTimeout(400);assert.equal(await page.evaluate(()=>life.talkQ.wait),4,'Pause freezes dialogue countdown');
 await page.evaluate(()=>showCard(CARDS[0]));await page.waitForTimeout(200);assert.equal(await page.evaluate(()=>life.talkQ.wait),4,'Chance card freezes dialogue');await page.evaluate(()=>{clearTimeout(card.timer);card=null;cardEl.hidden=cardRes.hidden=true;dimHouse(false);});
 await page.evaluate(()=>{npcTestAt('park_central');requestNpcTalk(testNpc);sim.needs.bladder=19;speed=3;step(0,.05);speed=0;});assert.equal(await page.evaluate(()=>npcInteraction),null);assert.equal(await page.evaluate(()=>sim.park.goal),'toilet');
 await page.evaluate(()=>{npcTestAt('mall');requestNpcTalk(testNpc);sim.needs.hunger=24;speed=3;step(0,.05);speed=0;});assert.equal(await page.evaluate(()=>npcInteraction),null);assert.equal(await page.evaluate(()=>mallS.visit?.kind),'restaurant');
 await page.evaluate(()=>{npcTestAt('front');requestNpcTalk(testNpc);testNpc.gone=true;speed=3;step(0,.05);speed=0;});assert.equal(await page.evaluate(()=>npcInteraction),null);
 await page.evaluate(()=>{npcTestAt('front');requestNpcTalk(testNpc);command('go_home');});assert.equal(await page.evaluate(()=>npcInteraction),null);
 await page.evaluate(()=>{npcTestAt('park_meadow');requestNpcTalk(testNpc);speed=3;for(let i=0;i<200&&npcInteraction.phase==='approach';i++)step(0,.05);speed=0;restore(snapshot());});assert.equal(await page.evaluate(()=>npcInteraction),null);assert.notEqual(await page.evaluate(()=>sim.act),'npc_chat');
 await page.evaluate(()=>{npcTestAt('park_central');const n=testNpc;lifeFlags.npcChatSeen={};const seen=[];for(let i=0;i<24;i++){const t=chooseNpcTalk(n);if(seen.includes(t.id))throw Error('Repeat before pool exhausted');seen.push(t.id);(lifeFlags.npcChatSeen[t.scene]||=[]).push(t.id);}const saved=snapshot();restore(saved);if(lifeFlags.npcChatSeen.park_central.length!==24)throw Error('Seen text not saved');});
 assert.deepEqual(errors,[]);console.log('PASS: 540 authored exchanges with all four gender pairings and correct child addresses, actual canvas hover/click across 9 scenes, walking/no teleport, facing/stopping/resuming, full-conversation contact/memory, scene bubbles, excluded merchants/fishers, pause, urgent WC/restaurant, cancellation, vanished target, restore, and saved nonrepeat history.');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
