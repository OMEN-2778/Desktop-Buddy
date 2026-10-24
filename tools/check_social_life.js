const assert=require('node:assert/strict');require('node:fs').mkdirSync('/workspace/artifacts/social-hud',{recursive:true});const {chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const page=await browser.newPage({viewport:{width:1100,height:850}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]||'http://127.0.0.1:8785/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1800);
 await page.evaluate(()=>{closeGuide();closePicker();cardMoment=()=>false;rollCard=()=>false;rollEvents=()=>false;speed=0;sim.t=720;sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.chosen=null;sim.idleUntil=Infinity;sim.needs={hunger:95,energy:95,bladder:95,social:95,hygiene:95,fun:95};socialState.nextCall=1e9;socialState.nextVisit=1e9;});
 const inventory=await page.evaluate(()=>({names:[doll.NAMES.f.length,new Set(doll.NAMES.f).size,doll.NAMES.m.length,new Set(doll.NAMES.m).size],world:socialState.world.length,ids:new Set(socialState.world.map(p=>p.id)).size,npcNames:new Set(socialState.world.map(p=>p.name)).size,looks:new Set(socialState.world.map(p=>JSON.stringify({...p.look,name:undefined}))).size,tiers:[0,.5,1,19.99,20,59.99,60,80,90,90.01,100].map(affinity=>contactRelation({affinity})),cards:CARDS.filter(c=>c.service==='visit').length,talks:Object.values(SOCIAL_TEXT.conversations).reduce((s,v)=>s+v.length,0)}));
 assert.deepEqual(inventory.names,[200,200,200,200]);for(const k of ['world','ids','npcNames','looks'])assert.equal(inventory[k],200,k);
 assert.deepEqual(inventory.tiers,['陌生','面熟','面熟','面熟','朋友','朋友','挚友','挚友','挚友','最好的朋友','最好的朋友']);assert.equal(inventory.cards,40);assert.equal(inventory.talks,128);
 await page.evaluate(()=>{
  const n=makeNpc('walker');if(socialState.contacts.some(c=>c.id===n.personId)&&!['abu','xiaoyu','linzhou','tangtang','achen','xiaokui','muzi','dake','ningning','xiaoye'].includes(n.personId))throw Error('Unmet passerby entered contacts');
  const p=socialState.world.find(p=>p.id==='person_199'),npc={personId:p.id};const c=meetWorldNpc(npc);if(c.id!==p.id||c.name!==p.name||JSON.stringify(c.look)!==JSON.stringify(p.look))throw Error('NPC identity mismatch');
  const count=socialState.contacts.length;meetWorldNpc(npc);if(socialState.contacts.length!==count)throw Error('Duplicate acquaintance');
  if(!c.memories.length)throw Error('First meeting memory');
  c.affinity=12;c.metAt=0;c.lastContact=0;c.lastSeen=0;c.farewellTried=true;socialState.decayDay=0;sim.t=9*1440;tickSocialDecay();
  if(Math.abs(c.affinity-(12-5*personalityDecay(c)))>1e-8||!c.forgotten)throw Error('Grace period / game-day decay / forgotten appearance');
  const before=c.affinity;socialRejected(c,'没能联系上');socialRejected(c,'没能联系上');socialRejected(c,'没能联系上');if(c.affinity!==before-2)throw Error('Daily refusal loss cap');
  const dad=contactFor('dad'),dadBefore=dad.affinity;socialRejected(dad,'未接');if(dad.affinity!==dadBefore||dad.forgotten)throw Error('Parent protection');
  c.affinity=.5;c.lastContact=0;socialState.decayDay=9;sim.t=10*1440;tickSocialDecay();if(socialState.contacts.includes(c)||!socialState.archive[c.id])throw Error('Zero removes and archives identity');
  const again=meetWorldNpc(npc);if(again.id!==c.id||again.memories.length<=c.memories.length)throw Error('Re-encounter preserves memories');
  const saved=socialSnapshot();restoreSocial(saved);if(socialState.decayDay!==saved.decayDay)throw Error('Offline reload applies decay');
  if(socialState.contacts.filter(c=>c.family).length!==2)throw Error('Parents were removed');
  const friend=contactFor('friend','abu');friend.affinity=95;const best=chatItem('text','friend','call',friend.id);friend.affinity=5;const distant=chatItem('text','friend','call',friend.id);if(!distant.talk.id.startsWith('social_early_text_')||best.talk.name!==distant.talk.name)throw Error('Relationship-specific dialogue identity');friend.affinity=65;
  showSocialMemories(again.id);
 });
 await page.waitForTimeout(600);assert.equal(await page.locator('.social-sheet').isVisible(),true);assert.ok(await page.locator('.social-memories li').count()>0);await page.screenshot({path:'/workspace/artifacts/social-hud/memories.png'});await page.locator('.social-sheet-close').click();
 // Familiar callers have no relationship prefix, including forgotten portraits.
 await page.evaluate(()=>{sim.t=720;socialState.guest=null;const c=contactFor('friend','xiaoyu');c.affinity=5;c.forgotten=true;sayShownAt=-Infinity;requestIncomingCall(c.id);tickSocial(0,performance.now());});
 assert.equal(await page.locator('#incomingCall strong').textContent(),'小雨');assert.equal(await page.locator('#incomingCall .caller-copy span').textContent(),'打来电话');
 await page.locator('.call-decline').click();await page.waitForTimeout(350);
 // A visit uses the regular house, the shared seated pose, and an independent guest.
 await page.evaluate(()=>{sim.mode='idle';sim.act=null;sim.windup=null;sim.chosen=null;sim.talk=null;sim.item=null;speed=0;sim.needs.energy=90;sim.needs.hunger=90;sim.needs.bladder=90;sim.t=720;
  if(!inviteHome('abu'))throw Error('Invite failed');const g=socialState.guest;g.at=sim.t;speed=1;tickHomeVisit(1);for(let i=0;i<30;i++)tickHomeVisit(.5);speed=0;
  if(g.phase!=='visiting')throw Error('Guest did not enter and sit');sim.windup=null;startAct('host');sim.s=sim.target;arrive();
  const before=socialSnapshot();restoreSocial(before);if(socialState.guest?.id!=='abu'||socialState.guest.phase!=='visiting')throw Error('Active visit save');
  const restored=socialState.guest;restored.next=0;restored.usedTalks=[];restored.usedEvents=[];speed=1;tickHomeVisit(.1);for(let i=0;i<20;i++){if(restored.talk)restored.talk.wait=0;tickHomeVisit(.1);}speed=0;render();
 });
 await page.waitForTimeout(500);await page.screenshot({path:'/workspace/artifacts/social-hud/home-visit.png'});
 await page.evaluate(()=>{
  const guest=socialState.guest,c=contactFor('friend',guest.id);if(!c.memories?.length)throw Error('Visit memories missing');
  const deck=CARDS.filter(cd=>cd.service==='visit');for(const cd of deck){if(!cardFits(cd,lifeCtx()))throw Error('Visit card context');for(const key of ['a','b']){if(cd[key].out.length!==2)throw Error('Missing outcomes');for(const o of cd[key].out)if(!ML[o.id])throw Error('Unregistered visit mood');}}
  const item=deck[0];card={cd:item,vars:cardVars(),o:item.a.out[0]};const before=c.affinity;cardNeeds();if(c.affinity!==Math.min(100,before+1))throw Error('Card friendship / memory');card=null;
  sim.needs.energy=10;speed=1;tickHomeVisit(.1);if(guest.phase!=='leaving'||sim.act==='host')throw Error('Low energy fails safe departure');for(let i=0;i<40;i++)tickHomeVisit(.5);speed=0;if(socialState.guest)throw Error('Guest stuck leaving');
  if(cardFits(item,lifeCtx()))throw Error('Visit cards leak into solo home');
  sim.needs.energy=90;const c2=contactFor('friend','abu');c2.affinity=3;showFarewellOffer(c2);
 });
 await page.locator('.social-sheet button').filter({hasText:'认真聊聊'}).click();assert.ok(await page.evaluate(()=>contactFor('friend','abu').affinity)>=8);
 assert.deepEqual(errors,[]);console.log('PASS: 400 names, 200 stable unique NPCs, thresholds, meeting and re-encounter, memories, game-day decay, refusal cap, parents, forgotten portrait, archive, offline restore, tier dialogue, familiar incoming call, guest entry/sitting/conversation/save/departure, 40 contextual chance cards and reconciliation.');
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
