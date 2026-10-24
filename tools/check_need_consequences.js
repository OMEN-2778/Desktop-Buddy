const assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:1400,height:1100},reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8786/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1400);
 await page.evaluate(()=>{
  closeGuide();closePicker();closeSocialSheet();speed=0;socialState.nextCall=socialState.nextVisit=1e9;cardMoment=rollCard=rollEvents=()=>false;
  const ok=(value,message)=>{if(!value)throw Error(message);};
  const reset=()=>{stopNpcTalk();sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;sim.chosen=null;sim.down=null;sim.graceUntil=0;sim.t=720;for(const k in sim.needs)sim.needs[k]=90;moods.clear();};
  reset();sim.needs.hygiene=0;applyNeedConsequences();
  ok(moods.has('need_dirty_zero')&&ML.need_dirty_zero.pts===5,'Hygiene zero consequence missing');
  const first=moods.get('need_dirty_zero').t;sim.t+=30;applyNeedConsequences();ok(moods.get('need_dirty_zero').t===first,'Zero condition repeatedly re-added');
  sim.needs.hygiene=1;applyNeedConsequences();ok(!moods.has('need_dirty_zero'),'Cleaning does not lift disgust');
  for(const sensitivity of [-100,0,100]){
   reset();heroPersonality.sensitivity=sensitivity;sim.needs.bladder=0;applyNeedConsequences();
   ok(sim.needs.bladder===100&&sim.needs.hygiene===0,'Accident must empty hygiene and resolve bladder');
   ok(moods.has('need_dirty_zero')&&ML.accident.pts===5,'Accident moods');
   const start=moods.get('accident').t,until=moods.get('accident').until;
   ok(until-start===2160,'36-hour consequence changed by personality');
   sim.t+=20;applyNeedConsequences();ok(moods.get('accident').until===until,'Accident timer repeatedly extended');
   sim.needs.hygiene=100;applyNeedConsequences();ok(moods.has('accident')&&!moods.has('need_dirty_zero'),'Washing should remove disgust, retain embarrassment');
   sim.t=until-.01;updateConds();ok(moods.has('accident'),'Embarrassment ended early');sim.t=until;updateConds();ok(!moods.has('accident'),'Embarrassment did not expire');
  }
  reset();sim.needs.social=0;sim.needs.fun=0;applyNeedConsequences();
  ok(moods.has('need_social_zero')&&moods.has('need_fun_zero'),'Social/fun zero moods missing');
  sim.needs.fun=1;applyNeedConsequences();ok(!moods.has('need_fun_zero')&&moods.has('need_social_zero'),'Fun/social recovery coupled incorrectly');
  sim.needs.social=1;applyNeedConsequences();ok(!moods.has('need_social_zero'),'Social recovery does not lift sadness');
  reset();sim.needs.hygiene=sim.needs.social=sim.needs.fun=0;applyNeedConsequences();checkCollapse();ok(sim.mode!=='down','Nonfatal zero penalties caused a collapse');
  for(const k of ['hunger','energy']){reset();sim.needs[k]=0;checkCollapse();ok(sim.mode==='down'&&sim.down.cause===k,'Fatal needs no longer collapse: '+k);}
  reset();sim.place='front';sim.route=[[80,OUT.front.feet]];sim.s=sim.target=0;arriveAt('front');sim.mode='idle';sim.act=null;
  const n=makeNpc('walker',{x:96,feet:OUT.front.feet,layer:'front',dir:1,v:0});life.npcs=[n];life.npcNext=life.chatNext=Infinity;
  sim.needs.hygiene=0;const before=socialState.contacts.length;
  ok(!requestNpcTalk(n)&&!npcInteraction&&!life.talkQ,'Manual conversation bypassed dirt refusal');ok(n.sayText&&DIRTY_NPC_REPLIES.some(text=>spaced(text)===n.sayText),'No NPC refusal dialogue');
  ok(!startNpcTalk(n,false)&&!life.talkQ,'Automatic conversation bypassed dirt refusal');ok(socialState.contacts.length===before,'Refusal introduced a new friend');
  sim.needs.hygiene=1;ok(!npcRefusesDirty(n,true),'Dirt refusal persists after cleaning');
  reset();addMood('accident',{diary:false,words:false});const saved=snapshot();saved.flags.needRulesVersion=0;saved.moods=saved.moods.map(m=>m[0]==='accident'?[m[0],m[2]+360,m[2]]:m);restore(saved);
  ok(moods.get('accident').until-moods.get('accident').t===2160,'Old accident save not upgraded');
  const old={hunger:.115,energy:.065,hygiene:.045,bladder:.3,social:100/2880,fun:.11};for(const k in old)ok(Math.abs(DECAY[k]/old[k]-.9)<1e-9,'Baseline drain not 10% slower: '+k);
 });
 assert.deepEqual(errors,[]);console.log('PASS: all zero-need consequences; exact 36 game hours at all sensitivities; independent recovery; no repeated timers; hygiene gates both NPC conversation directions; hunger/energy collapse retained; old-save migration; 10% slower baseline drain.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
