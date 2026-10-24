const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1600,height:1200},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(1300);
 await p.evaluate(()=>{
  window.nightExpect=(value,message)=>{if(!value)throw Error(message);};
  window.resetNight=()=>{closeGuide();closePicker();closeSocialSheet();closeRing();hidePeerSay(true);stopNpcTalk();speed=0;sim.t=18*60;sim.place='home';sim.act=null;sim.mode='idle';sim.windup=null;sim.talk=null;sim.chosen=null;sim.item=null;sim.queue=[];sim.sleepPlace=null;sim.idleUntil=Infinity;remoteSocial=null;socialState.guest=null;socialState.nextCall=socialState.nextVisit=1e9;for(const k in sim.needs)sim.needs[k]=90;sim.route=[[D.spots.sofa[1],FLOOR_Y[0]]];sim.s=sim.target=0;cardMoment=rollCard=rollEvents=()=>false;};resetNight();
  const c=contactFor('friend','abu');c.affinity=75;c.look=doll.normalize({...c.look,gender:look.gender});c.child=false;
  nightExpect(canStayOver(c),'Close same-gender adult not eligible');c.affinity=90;nightExpect(canStayOver(c),'90 boundary');c.affinity=90.01;nightExpect(!canStayOver(c),'Best friends must not trigger');c.affinity=59.99;nightExpect(!canStayOver(c),'Below close tier eligible');c.affinity=75;c.child=true;nightExpect(!canStayOver(c),'Child eligible');c.child=false;
  const same=c.look;c.look=doll.normalize({...same,gender:look.gender==='m'?'f':'m'});nightExpect(!canStayOver(c),'Opposite gender eligible');c.look=same;nightExpect(!canStayOver(contactFor('dad')),'Parent overnight friend event');
  const dad=contactFor('dad'),aff=dad.affinity;dad.parentVisitRoll=null;dad.parentLastVisit=null;sim.t=12*60;speed=1;
  const random=Math.random;Math.random=()=>.5;nightExpect(!inviteHome(dad.id),'Distant parent should usually decline');nightExpect(!socialState.guest&&dad.affinity===aff,'Parent refusal changed affinity/scheduled guest');Math.random=()=>0;nightExpect(!inviteHome(dad.id),'Repeated invitations rerolled family travel');sim.t+=7*1440;nightExpect(inviteHome(dad.id),'Rare parent trip cannot occur');Math.random=random;
  nightExpect(socialState.guest.at-sim.t>=120&&socialState.guest.familyTrip,'Parent teleported from another city');nightExpect(!peerSpeech.pending.text.includes('游戏分钟'),'Immersion-breaking arrival wording');
  const save=snapshot();restore(save);nightExpect(contactFor('dad').parentVisitRoll&&socialState.guest.familyTrip,'Parent travel progress lost');resetNight();
  window.seedNightGuest=()=>{const c=contactFor('friend','abu');c.affinity=75;c.look=doll.normalize({...c.look,gender:look.gender});c.child=false;socialState.guest={id:c.id,phase:'visiting',s:1,at:sim.t-40,arrivedAt:sim.t-40,until:sim.t+150,nextStayCheck:0,next:Infinity,count:0,said:[]};return socialState.guest;};
  const g=seedNightGuest(),random2=Math.random;Math.random=()=>0;tickHomeVisit(.1);Math.random=random2;
  nightExpect(!socialSheet.hidden&&socialSheet.classList.contains('overnight-sheet'),'Overnight invite did not trigger');speed=3;
 });
 const paused=await p.evaluate(()=>sim.t);await p.waitForTimeout(500);assert.equal(await p.evaluate(()=>sim.t),paused,'Overnight choice must pause game time');
 fs.mkdirSync('/workspace/artifacts/overnight',{recursive:true});
 for(const scale of [25,50,75,100]){
  await p.evaluate(scale=>{setScale(scale);const c=contactFor('friend','abu');c.name='亚历山大';showOvernightChoice(socialState.guest,c,'invite');},scale);await p.waitForTimeout(70);
  const layout=await p.evaluate(()=>{const r=socialSheet.getBoundingClientRect(),house=view.getBoundingClientRect();return {fits:Math.abs(r.x-house.x)<1&&Math.abs(r.y-house.y)<1&&Math.abs(r.width-house.width)<1&&Math.abs(r.height-house.height)<1,inside:[...socialSheet.querySelectorAll('canvas,h3,button')].every(e=>{const b=e.getBoundingClientRect();return b.top>=r.top&&b.bottom<=r.bottom&&b.left>=r.left&&b.right<=r.right;}),avatarAbove:socialSheet.querySelector('canvas').getBoundingClientRect().bottom<=socialSheet.querySelector('h3').getBoundingClientRect().top+1};});assert.deepEqual(layout,{fits:true,inside:true,avatarAbove:true},'Invitation layout at '+scale);
  await p.locator('.overnight-sheet').screenshot({path:`/workspace/artifacts/overnight/invite-${scale}.png`});
 }
 await p.locator('.overnight-actions [data-choice="accept"]').click();
 await p.evaluate(()=>{nightExpect(socialState.guest.overnight.accepted,'Accept not stored');sim.t=21*60+5;speed=0;tickHomeVisit(.1);nightExpect(socialSheet.dataset.nightKind==='berth'&&!socialSheet.hidden,'Bedtime location question missing');});
 for(const scale of [25,50,75,100]){
  await p.evaluate(scale=>{setScale(scale);showOvernightChoice(socialState.guest,cForGuest(socialState.guest),'berth');},scale);await p.waitForTimeout(60);
  assert.equal(await p.evaluate(()=>{const r=socialSheet.getBoundingClientRect();return [...socialSheet.querySelectorAll('canvas,h3,button')].every(e=>{const b=e.getBoundingClientRect();return b.top>=r.top&&b.bottom<=r.bottom&&b.left>=r.left&&b.right<=r.right;});}),true,'Three-way bed choice layout at '+scale);
 }
 await p.locator('.overnight-sheet').screenshot({path:'/workspace/artifacts/overnight/where.png'});
 for(const berth of ['guest-sofa','hero-sofa','shared']){
  await p.evaluate(berth=>{
   resetNight();const g=seedNightGuest();g.overnight={accepted:true,until:1440+10*60,bedTalkDone:false};g.until=g.overnight.until;sim.t=21*60+10;resolveOvernightChoice(g.id,'berth',berth);speed=1;sim.windup=null;startAct('sleep');
   for(let i=0;i<260&&!(sim.mode==='act'&&g.sleeping);i++){step(0,.2);tickHomeVisit(.2);}
   nightExpect(sim.mode==='act'&&sim.act==='sleep'&&g.sleeping,'People did not walk to sleeping positions: '+berth);
   nightExpect(Math.abs(here().y-FLOOR_Y[berth==='hero-sofa'?0:1])<1,'Hero route to wrong floor');
   nightExpect(Math.abs(homeGuestPoint(g).y-FLOOR_Y[berth==='guest-sofa'?0:1])<1,'Guest route to wrong floor');
   if(berth==='shared'){
    nightExpect(sleepoverChatAwake()&&!asleep(),'Shared bed should be awake for talk');
    tickHomeVisit(1);const sv=snapshot(),index=g.bedTalk.i;restore(sv);
    nightExpect(socialState.guest.bedTalk?.i===index&&sleepoverChatAwake(),'Bed conversation lost on reload');
   }else{
    nightExpect(asleep(),'Separate sleeping should recover normally');
    const sv=snapshot();restore(sv);nightExpect(heroSleepingOnSofa()===(berth==='hero-sofa'),'Sofa sleep not restored');
   }
   speed=0;setScale(75);render();
  },berth);
  await p.screenshot({path:`/workspace/artifacts/overnight/${berth}.png`});
 }
 await p.evaluate(()=>{
  const g=socialState.guest,c=cForGuest(g),seenBefore=c.bedTalkSeen.length;speed=1;
  for(let i=0;i<35&&!g.overnight.bedTalkDone;i++){if(g.bedTalk)g.bedTalk.wait=0;tickHomeVisit(.2);}
  nightExpect(g.overnight.bedTalkDone&&asleep(),'Bed talk never finishes/sleep never resumes');nightExpect(c.memories.filter(m=>m.title.startsWith('枕边闲聊')).length>=2,'No bedside transcripts');nightExpect(c.bedTalkSeen.length>=seenBefore,'Conversation history lost');
  sim.t=1440+7*60+5;tickHomeVisit(.1);nightExpect(g.overnight.morning&&!g.sleeping,'Guest never wakes');sim.t=1440+10*60;tickHomeVisit(.1);nightExpect(g.phase==='leaving','Guest never departs next day');resetNight();
  const guest=seedNightGuest();speed=1;sim.act=null;sim.mode='idle';const [st,x]=D.spots.computer;sim.route=[[x,FLOOR_Y[st]]];sim.s=0;
  for(let i=0;i<200;i++)moveHomeGuest(guest,.2);nightExpect(Math.abs(homeGuestPoint(guest).x-D.spots.guest_study[1])<1,'Guest not using right-hand study chair');
  nightExpect(!!CLICK.guest_chair,'Chair lacks outline-based interaction');resetNight();
 });
 await p.evaluate(()=>{speed=0;sim.place='park';sim.park={zone:'central',seated:false,goal:null};sim.act=null;sim.mode='idle';sim.route=[[W/2,parkLayout().feet]];sim.s=sim.target=0;arriveAt('park');render();});
 assert.equal(await p.locator('.park-arrow:visible').count(),2);
 await p.locator('.park-arrow[data-dir="-1"]').click();
 await p.evaluate(()=>{nightExpect(parkLayout().id==='central'&&sim.strollX===8,'Arrow teleported instead of choosing walking target');sim.windup=null;speed=1;startAct('stroll');for(let i=0;i<220&&!wiping&&parkLayout().id==='central';i++)step(0,.15);nightExpect(!!wiping||parkLayout().id==='lakeside','Arrow did not reach transition edge');speed=0;});
 await p.waitForTimeout(900);assert.equal(await p.evaluate(()=>parkLayout().id),'lakeside');
 await p.evaluate(()=>{sim.park.zone=PARK_ZONES[0].id;arriveAt('park');render();});assert.equal(await p.locator('.park-arrow[data-dir="-1"]').isHidden(),true);
 await p.evaluate(()=>{sim.park.zone=PARK_ZONES.at(-1).id;arriveAt('park');render();});assert.equal(await p.locator('.park-arrow[data-dir="1"]').isHidden(),true);
 await p.screenshot({path:'/workspace/artifacts/overnight/park-arrows.png'});
 await p.evaluate(async()=>{resetNight();sim.t=720;prefs.autosave=true;await saveGame();document.querySelector('.console').open=true;});
 const original=await p.evaluate(()=>({t:sim.t,needs:{...sim.needs},contacts:socialState.contacts.length}));
 for(const choice of ['shared','hero-sofa','guest-sofa','chat']){
  await p.locator(`[data-sleep-preview="${choice}"]`).click();
  const state=await p.evaluate(async()=>({active:!!visitSleepPreview,berth:socialState.guest.overnight.berth,chat:sleepoverChatAwake(),saving:await saveGame(),stored:JSON.parse(localStorage.getItem(SAVE_KEY)).sim.t}));
  assert.equal(state.active,true);assert.equal(state.berth,choice==='chat'?'shared':choice);assert.equal(state.chat,choice==='chat');assert.equal(state.saving,false);assert.equal(state.stored,original.t,'Preview overwrote real progress');
  await p.locator('#view').screenshot({path:`/workspace/artifacts/overnight/console-${choice}.png`});
 }
 await p.locator('#exitSleepPreview').click();
 assert.deepEqual(await p.evaluate(()=>({t:sim.t,needs:{...sim.needs},contacts:socialState.contacts.length})),original,'Exiting preview did not restore progress');
 assert.equal(await p.evaluate(()=>visitSleepPreview),null);
 assert.deepEqual(errors,[]);console.log('PASS: immersive arrival wording; mostly declined/rare saved parent travel; strict 60–90 same-gender adult overnight eligibility; paused bounded avatar dialogs at 4 scales; all 3 sleeping routes, bedding and saved sleep positions; 80 nonrepeating bedside conversations, wake/departure; right-hand study guest chair; park arrows walk before transition and hide at map ends.');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
