// Companion integration: real venue entry, seats, reload, self-care and return.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  const page=await browser.newPage({viewport:{width:1600,height:1100},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error(e.stack);});
  await page.goto(process.argv[2]||'http://127.0.0.1:8786/');await page.waitForFunction(()=>booted);await page.waitForTimeout(1500);
  fs.mkdirSync('/workspace/artifacts/friend-outings',{recursive:true});
  await page.evaluate(()=>{
   window.outingRollCard=rollCard;cardMoment=rollCard=rollEvents=()=>false;
   window.resetCompanion=(place='park')=>{
    closeGuide();closePicker();closeRing();closeSocialSheet();closeWardrobe();hidePeerSay(true);
    card=null;cardEl.hidden=cardRes.hidden=true;speed=0;sim.place=place;sim.mode='idle';sim.act=null;sim.down=null;sim.windup=null;sim.chosen=null;sim.talk=null;sim.queue=[];sim.t=20*60;sim.player=false;sim.idleUntil=Infinity;sim.graceUntil=Infinity;
    remoteSocial=null;socialState.guest=null;socialState.nextCall=socialState.nextVisit=1e9;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,90]));weather.kind='clear';weather.force='clear';moods.clear();lifeFlags.cards={seen:[],last:1e9};
    sim.park=place==='park'?{zone:'central',seated:false}:null;
    const c=contactFor('friend','abu');c.affinity=65;c.dailyGain=0;c.gainDay=Math.floor(sim.t/1440);c.forgotten=false;
    friendOutingState={id:c.id,dest:place,phase:'active',startedAt:sim.t,at:sim.t,bookedAt:sim.t,nextTalk:1e9,seen:[],count:0,said:[],distance:0};
    sim.outWhy='friend';sim.lastOut=sim.t;sim.outBack=sim.t+180;sim.route=[[OUT[place]?.doorX||D.spots.front_door[1],OUT[place]?.feet||FLOOR_Y[0]]];sim.s=sim.target=0;arriveAt(place);
   };
   window.settleCompanion=()=>{speed=1;for(let i=0;i<100;i++)tickFriendOuting(.1);speed=0;render();};
  });
  // Authored counts, complete exchanges, unique content and valid effects.
  const catalog=await page.evaluate(()=>{
   const pools=FRIEND_OUTING_TEXT.talks;
   for(const [key,pool]of Object.entries(pools)){
    if(pool.length!==(key==='common'?200:100))throw Error('Dialogue count '+key);
    if(new Set(pool.map(row=>row[0])).size!==pool.length)throw Error('Duplicate title '+key);
    if(new Set(pool.map(row=>JSON.stringify(row.slice(1)))).size!==pool.length)throw Error('Duplicate exchange '+key);
    if(pool.some(row=>row.length!==5||!row[1].startsWith('>')||!row[3].startsWith('>')))throw Error('Broken turns '+key);
   }
   for(const [key,e]of Object.entries(FRIEND_OUTING_TEXT.effects))if(e.mood&&!MOOD[e.mood])throw Error('Unknown emotion '+key);
   if(SOCIAL_DIALOGUE.visit.common.length!==300)throw Error('Home dialogue count');
   return {outing:Object.values(pools).reduce((n,p)=>n+p.length,0),home:SOCIAL_DIALOGUE.visit.common.length,cards:CARDS.filter(c=>c.service==='friend_outing').length};
  });assert.deepEqual(catalog,{outing:1300,home:300,cards:40});
  // Entry goes through the same search / door / wipe as solo dining.
  for(const shop of ['diner','bistro','noodle','cinema']){
   await page.evaluate(shop=>{resetCompanion('mall');mallS.menuShop=shop;mallPlanVisit(shop==='cinema'?'cinema':'restaurant',shop==='cinema'?{id:'star'}:null);mallS.x=mallS.goal.x;stopAt(mallS.goal.it);},shop);
   await page.waitForFunction(()=>mallVisitInside()&&!wiping);
   await page.evaluate(()=>{settleCompanion();const p=friendOutingState.position,hero=buddyFeet();if(!friendOutingState.seated||!Number.isFinite(p.x)||Math.abs(p.x-hero.x)<20)throw Error('Overlapping or missing seats');if(mallS.visit.kind==='restaurant'&&(p.x!==MALL.dining.companion.x||hero.x!==MALL.dining.seat.x))throw Error('Not at the same dining table');});
   await page.locator('#view').screenshot({path:`/workspace/artifacts/friend-outings/together-${shop}.png`});
   await page.evaluate(()=>{const saved=snapshot();restore(saved);settleCompanion();if(!friendOutingActive()||!mallVisitInside()||!friendOutingState.seated)throw Error('Interior reload loses companion');});
  }
  // Every movie has an adjacent seat; a sleeping hero does not receive chatter.
  await page.evaluate(()=>{
   for(const film of MALL_LIFE.films){resetCompanion('mall');mallS.visit={kind:'cinema',phase:'inside',shop:'cinema',film:film.id,elapsed:0,served:0,nextCard:1e9,nextEvent:1e9};mallSetSeat();mallRoomSetup();settleCompanion();if(friendOutingState.position.x!==169)throw Error('Cinema seat '+film.id);render();}
   sim.needs.energy=2;speed=1;step(.3,.1);tickFriendOuting(.1);if(!mallSleeping()||friendOutingState.talk)throw Error('Cinema sleeping was interrupted');speed=0;
  });
  // Every bar seat uses another real, free seat, reserved from subsequent NPCs.
  await page.evaluate(()=>{
   for(const seat of BAR_SEATS){resetCompanion('bar');barScene.guests=[];sim.bar.seat=seat.id;sim.route=[[seat.x,seat.feet]];sim.s=sim.target=0;settleCompanion();const other=barSeat(friendOutingState.barSeat);if(!other||other.id===seat.id||!barOccupied(other.id)||!friendOutingState.seated||friendOutingState.position.x!==other.x)throw Error('Bar pair '+seat.id);}
   const s=barSeat(sim.bar.seat);barScene.guests=BAR_SEATS.filter(x=>x.id!==s.id).map(x=>makeNpc('bar_guest',{x:x.x,feet:x.feet,seat:x.id,seatLift:x.lift,sit:true,layer:'front'}));friendOutingState.heroSeat=null;settleCompanion();if(friendOutingState.seated)throw Error('Companion floats when all chairs are occupied');
   resetCompanion('bar');barScene.guests=barScene.guests.filter(n=>!['booth_l','booth_r'].includes(n.seat));sim.bar.seat='booth_l';sim.route=[[28,92]];settleCompanion();
  });await page.locator('#view').screenshot({path:'/workspace/artifacts/friend-outings/together-bar.png'});
  // Private errands, dialogue completion and reward idempotency.
  await page.evaluate(()=>{
   resetCompanion('park');sim.park.zone='lakeside';arriveAt('park');sim.act='park_toilet';sim.mode='act';sim.route=[[parkLayout().facility.x,parkLayout().facility.feet]];settleCompanion();
   if(friendOutingState.seated||friendOutingState.talk||friendOutingState.position.x===here().x)throw Error('Companion enters toilet');
   resetCompanion('park');const c=outingFriend(),before=c.affinity;friendOutingState.talk={title:'验收对话',lines:['>走慢点。','好。','>这里挺舒服。','嗯。'],i:0,wait:0,said:[],gain:1};speed=1;
   for(let i=0;i<5;i++){friendOutingState.talk.wait=0;tickFriendOuting(.1);}
   if(c.affinity!==before+1||friendOutingState.count!==1||!c.memories.some(m=>m.title.includes('验收对话')))throw Error('Completion reward / diary');
   tickFriendOuting(.1);if(c.affinity!==before+1)throw Error('Reward repeated');speed=0;
   sim.park.zone='grove';arriveAt('park');sim.act='stroll';if(outingTalkFits('park_grove',['汤还在冒热气'],c))throw Error('Meal dialogue during walk');sim.mode='act';sim.act='park_eat';if(!outingTalkFits('park_grove',['汤还在冒热气'],c))throw Error('Meal dialogue unreachable');
   sim.t=22*60;if(outingTalkFits('park_central',['晒太阳也挑地方'],c))throw Error('Sun dialogue at night');
  });
  // Contextual opportunity decks and their actual result effects.
  await page.evaluate(()=>{
   resetCompanion('park');const c=outingFriend();const deck=CARDS.filter(cd=>cd.service==='friend_outing');
   for(const cd of CARDS.filter(cd=>cd.service!=='friend_outing'))if(cardFits(cd,lifeCtx()))throw Error('Ordinary card during outing');
   for(const cd of deck){
    sim.place=cd.at;if(cd.at==='park')sim.park={zone:cd.outingZones?.[0]||'central'};
    if(cd.at==='mall'){mallS.visit=cd.outingContexts?.[0]==='restaurant'?{kind:'restaurant',phase:'inside'}:cd.outingContexts?.[0]==='cinema'?{kind:'cinema',phase:'inside'}:null;}
    sim.t=12*60;if(!cardFits(cd,lifeCtx()))throw Error('Dedicated card unreachable '+cd.n);
    for(const k of ['a','b'])for(const o of cd[k].out)if(o.mood&&!ML[o.id])throw Error('Missing card mood '+cd.n);
   }
   sim.place='park';sim.park.zone='grove';const lake=deck.find(cd=>cd.n===3008);if(cardFits(lake,lifeCtx()))throw Error('Lake card at food stall');
   const cd=deck[0],before=c.affinity;card={cd,vars:cardVars(),o:cd.a.out[0]};cardNeeds();if(c.affinity!==before+(cd.a.out[0].friendship||0))throw Error('Card affinity target');card=null;
   friendOutingState=null;arriveAt('park');for(const cd of deck)if(cardFits(cd,lifeCtx()))throw Error('Companion card while solo');
  });
  // Waiting/departure cancellation, restore and conversion of an existing guest.
  await page.evaluate(()=>{
   resetCompanion('home');friendOutingState=null;const c=contactFor('friend','abu'),before=c.affinity;scheduleFriendOuting(c,'park');finishFriendOuting('临时改约。');if(c.affinity!==before)throw Error('Cancelled outing gives reward');
   socialState.guest={id:c.id,phase:'visiting',until:sim.t+100};scheduleFriendOuting(c,'park');if(socialState.guest||friendOutingState.at!==sim.t)throw Error('Guest not converted');
   const saved=friendOutingSnapshot();saved.phase='departing';restoreFriendOuting(saved);if(friendOutingState.phase!=='waiting')throw Error('Restored departure stuck');speed=1;tickFriendOuting(.1);if(sim.windup?.act!=='go_out')throw Error('Restored departure did not restart');speed=0;
  });
  // Low needs still route to food / toilets, while a storm ends outdoor outings.
  await page.evaluate(()=>{
   resetCompanion('mall');sim.needs.hunger=19;speed=1;step(.3,.1);if(mallS.visit?.kind!=='restaurant'||!friendOutingActive())throw Error('Companion blocks mall food search');speed=0;
   resetCompanion('park');sim.needs.bladder=10;speed=1;step(.3,.1);if(sim.park.goal!=='toilet'||!friendOutingActive())throw Error('Companion blocks park WC');speed=0;
   resetCompanion('park');weather.kind='storm';speed=1;tickFriendOuting(.1);if(friendOutingState.phase!=='returning'||sim.windup?.act!=='go_home')throw Error('Storm does not end outing');speed=0;
  });
  // Real browser reload, then real bar-to-home transition; no deadlock.
  await page.evaluate(async()=>{resetCompanion('bar');settleCompanion();speed=0;await saveGame();saveSettings();});
  await page.reload();await page.waitForFunction(()=>booted);await page.waitForTimeout(1200);
  assert.equal(await page.evaluate(()=>friendOutingActive()&&outingFriend().id==='abu'&&sim.place==='bar'),true);
  await page.evaluate(()=>{closeGuide();closeSocialSheet();card=null;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,90]));speed=1;friendOutingState.phase='returning';command('go_home');if(sim.windup){realClock=sim.windup.at+.1;step(0,.1);}speed=0;});
  await page.waitForFunction(()=>sim.place==='home'&&!wiping);
  assert.equal(await page.evaluate(()=>friendOutingState),null);
  assert.deepEqual(errors,[]);
  console.log('PASS:',JSON.stringify(catalog),'all dining rooms / 16 films / 6 bar seats, private errands, rewards, contextual decks, cancellation, departure restore, need searches, storm and actual reload / return.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
