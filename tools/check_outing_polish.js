const assert=require('node:assert/strict'),{chromium}=require('playwright');
require('node:fs').mkdirSync('/workspace/artifacts/friend-outings',{recursive:true});
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1500,height:1000},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(1400);
 await p.evaluate(()=>{closeGuide();closePicker();closeSocialSheet();closeRing();cardMoment=rollCard=rollEvents=()=>false;speed=0;sim.place='home';sim.mode='idle';sim.act=null;sim.talk=null;sim.windup=null;sim.chosen=null;remoteSocial=null;life.talkQ=null;sim.queue=[];sim.t=720;for(const k in sim.needs)sim.needs[k]=90;socialState.guest=null;socialState.nextCall=socialState.nextVisit=1e9;});
 // Real secondary bubble click, boundaries, keyboard cancellation and no accidental invite.
 for(const size of [25,50,75,100]){
  await p.evaluate(size=>{closeRing();setScale(size);openFriendOuting('abu');},size);
  assert.equal(await p.locator('#ring [data-outing-place]').count(),5);
  assert.equal(await p.evaluate(()=>{const r=view.getBoundingClientRect();return !socialDialogHolds()&&cardHolds()&&[...ringEl.children].every(b=>{const q=b.getBoundingClientRect();return q.left>=r.left&&q.right<=r.right&&parseFloat(getComputedStyle(b).fontSize)>=12;});}),true);
  await p.screenshot({path:`/workspace/artifacts/friend-outings/bubble-menu-${size}.png`});
  await p.keyboard.press('Escape');assert.equal(await p.evaluate(()=>friendOutingState===null&&ringEl.hidden),true);
 }
 await p.evaluate(()=>openFriendOuting('abu'));await p.locator('[data-outing-place="park"]').click();assert.equal(await p.evaluate(()=>friendOutingState.dest==='park'&&ringEl.hidden),true);
 await p.evaluate(()=>{
  const c=contactFor('friend','abu');friendOutingState.phase='active';sim.place='park';sim.park={zone:'central',seated:false};arriveAt('park');sim.route=[[140,103]];sim.s=sim.target=0;sim.mode='idle';sim.act=null;friendOutingState.nextTalk=1e9;
  for(const phase of ['departing','active','returning']){friendOutingState.phase=phase;if(requestIncomingCall(c.id)||requestIncomingCall(c.id,'video'))throw Error('Companion still calls '+phase);}
  phoneCall.phase='waiting';phoneCall.contactId=c.id;friendOutingState.phase='active';speed=1;tickSocial(.1,performance.now());if(phoneCall.phase!=='idle')throw Error('Queued companion call not cancelled');
  if(!requestIncomingCall('xiaoyu'))throw Error('Other friends cannot call');phoneCall.phase='idle';
  // Initialize the local trail before changing the hero position.
  for(let i=0;i<8;i++)tickFriendOuting(.05);const initial=friendOutingState.position.x;
  sim.route=[[180,103]];sim.s=sim.target=0;tickFriendOuting(.05);if(friendOutingState.moving||friendOutingState.position.x!==initial)throw Error('Follower started immediately');
  for(let i=0;i<8;i++)tickFriendOuting(.05);if(!friendOutingState.moving||friendOutingState.position.x<=initial)throw Error('Follower never followed');
  for(let i=0;i<100;i++)tickFriendOuting(.05);if(Math.abs(friendOutingState.position.x-companionPosition().x)>1||friendOutingState.moving)throw Error('Follower does not catch up / stop');speed=0;
  friendOutingState=null;sim.place='home';sim.act=null;sim.mode='idle';sim.talk=null;sim.windup=null;sim.chosen=null;remoteSocial=null;life.talkQ=null;socialState.guest=null;
  window.lastVisitRefusal=null;const say=showSay;showSay=(text,who,c)=>{lastVisitRefusal={text,who,id:c?.id};};
  try{
   for(const h of [6,7.9,21,23,1]){sim.t=h*60;const affinity=c.affinity;if(inviteHome(c.id)||socialDialogHolds()||socialState.guest||lastVisitRefusal.id!==c.id||c.affinity!==affinity)throw Error('Refusal is not a peer dialogue '+h);const pool=HOME_VISIT_TEXT.inviteRest[h>=5&&h<8?'early':'late'];if(!pool.includes(lastVisitRefusal.text))throw Error('Wrong refusal period '+h);}
   const dad=contactFor('dad');dad.parentVisitRoll={period:Math.floor(sim.t/(7*1440)),available:false};sim.t=23*60;inviteHome(dad.id);if(!HOME_VISIT_TEXT.parents.dad.decline.includes(lastVisitRefusal.text))throw Error('Parent city reason changed');dad.parentVisitRoll.available=true;inviteHome(dad.id);if(socialState.guest||!HOME_VISIT_TEXT.parents.dad.decline.includes(lastVisitRefusal.text))throw Error('Parent travels during rest hours');
  }finally{showSay=say;}
 });
 assert.deepEqual(errors,[]);console.log('PASS: four-scale secondary pixel bubbles, real selection/Escape, companion and queued-call blocking with other callers preserved, delayed follow/catch-up, early/late peer refusals without penalty, parent city reasons.');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
