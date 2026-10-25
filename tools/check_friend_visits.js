const assert=require('node:assert/strict'),fs=require('node:fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1700,height:1400},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error(e.stack)});
 await p.goto(process.argv[2]||'http://127.0.0.1:8786/');await p.waitForFunction(()=>booted);await p.waitForTimeout(2100);fs.mkdirSync('/workspace/artifacts/friend-visits',{recursive:true});
 await p.evaluate(()=>{
  prefs.guided=false;closeGuide();closePicker();closeRing();closeSocialSheet();closeWardrobe();hidePeerSay(true);speed=0;sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.down=null;sim.queue=[];sim.t=18*60;sim.graceUntil=Infinity;socialState.guest=null;friendOutingState=null;socialState.nextCall=socialState.nextVisit=1e9;remoteSocial=null;sim.talk=null;sim.chosen=null;card=null;cardEl.hidden=cardRes.hidden=true;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,90]));
  window.visitSettle=()=>{speed=1;for(let i=0;i<600&&sim.mode==='walk';i++)stepFriendHome(0,.1);speed=0;};
  window.visitEnter=(houseId='maple')=>{if(atFriendHome())leaveFriendHome();friendVisit=null;const c=contactFor('friend','abu');c.affinity=75;friendHomes[c.id]={houseId,relations:['爸爸','妈妈']};sim.place='home';sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;remoteSocial=null;sim.t=18*60;friendVisit={id:c.id,houseId,phase:'departing'};enterFriendHome();speed=0;};
 });
 // Fixed assignment is preserved by JSON save/reload and cannot grow more beds.
 const bindings=await p.evaluate(()=>{const c=contactFor('friend','abu'),home=friendHomeFor(c);const a=JSON.stringify(home);restore(snapshot());return [a,JSON.stringify(friendHomeFor(contactFor('friend','abu')))];});assert.equal(bindings[0],bindings[1]);
 await p.evaluate(()=>{const c=contactFor('friend','abu');openContactActions(c.id)});assert.equal(await p.locator('[data-action="visit"]').getAttribute('aria-disabled'),null);
 // All real houses render and their door graph reaches every room.
 for(const id of await p.evaluate(()=>Object.keys(D.friendHouses))){
  await p.evaluate(id=>visitEnter(id),id);
  const result=await p.evaluate(()=>{
   const h=visitingHouse(),off=(W-h.w)/2;for(const r of h.rooms){const route=friendVisitRoute(here(),{x:off+r.x+r.w/2,y:r.floor});const last=route.at(-1);if(last[1]!==r.floor)throw Error('Unreachable '+r.id);}
   render();syncUI();return {height:view.height,expected:Math.round(h.h*devPx),family:friendVisit.family.length};
  });assert.equal(result.height,result.expected);if(['cream','mint','tatami'].includes(id))assert.equal(result.family,0,'Single bedrooms spawned relatives');
 }
 await p.evaluate(()=>{visitEnter('maple');friendVisitAction('chat');visitSettle();render()});await p.locator('#view').screenshot({path:'/workspace/artifacts/friend-visits/arrival-family.png'});
 // Needs use the host's facilities, preserve location, and actually replenish.
 for(const [need,action]of [['bladder','toilet'],['hunger','eat'],['hygiene','bath']]){
  await p.evaluate(([need,action])=>{friendVisitAction(action);visitSettle();sim.needs[need]=15;speed=1;for(let i=0;i<120;i++)stepFriendHome(.1,.1);speed=0;},[need,action]);assert.equal(await p.evaluate(()=>sim.place),'friend_home');assert.ok(await p.evaluate(need=>sim.needs[need]>20,need),JSON.stringify(await p.evaluate(()=>({needs:sim.needs,mode:sim.mode,action:friendVisit.action,s:sim.s,target:sim.target,holds:cardHolds(),sheet:!socialSheet.hidden,guideOn,wardrobeOpen,preview:!!friendHousePreview,phone:phoneCall.phase,card:card?.cd?.n,ring:ringOf}))))
 }
 // Several urgent needs must finish in order rather than alternate routes.
 await p.evaluate(()=>{sim.needs.bladder=15;sim.needs.hunger=15;sim.needs.hygiene=10;friendVisit.action=null;sim.mode='idle';speed=1;stepFriendHome(.1,.1);for(let i=0;i<10;i++)stepFriendHome(.1,.1);speed=0;});
 assert.equal(await p.evaluate(()=>friendVisit.action),'toilet');await p.evaluate(()=>{visitSettle();speed=1;for(let i=0;i<1000;i++)stepFriendHome(.1,.1);speed=0;});
 assert.ok(await p.evaluate(()=>sim.needs.bladder>20&&sim.needs.hunger>20&&sim.needs.hygiene>20));
 // Low affinity refuses, only a deliberate request can authorize overnight.
 await p.evaluate(()=>{const c=visitingFriend();c.affinity=1;friendVisit.action=null;sim.mode='idle';sim.t=20*60;requestFriendStay()});assert.equal(await p.evaluate(()=>friendVisit.stay),false);assert.equal(await p.locator('.friend-stay-sheet').isVisible(),true);await p.evaluate(()=>closeSocialSheet());
 await p.evaluate(()=>{const c=visitingFriend();c.affinity=98;friendVisit.askedDay=null;const r=Math.random;Math.random=()=>0;requestFriendStay();Math.random=r;closeSocialSheet();});assert.equal(await p.evaluate(()=>friendVisit.stay),true);
 await p.evaluate(()=>{friendVisitAction('sleep');visitSettle();render()});assert.equal(await p.evaluate(()=>asleep()),true);await p.locator('#view').screenshot({path:'/workspace/artifacts/friend-visits/sleep.png'});
 // Save a sleeping guest in a tall home; restore without losing house or location.
 const saved=await p.evaluate(()=>{const s=JSON.parse(JSON.stringify(snapshot()));restore(s);return {house:friendVisit?.houseId,stay:friendVisit?.stay,place:sim.place};});assert.deepEqual(saved,{house:'maple',stay:true,place:'friend_home'});
 await p.evaluate(()=>{sim.t=friendVisit.until;speed=1;stepFriendHome(.1,.1);speed=0;});assert.equal(await p.evaluate(()=>sim.place),'home');
 // Incoming invitation has dedicated copy, orange/blue buttons, and a fixed six seconds.
 await p.evaluate(()=>{closeSocialSheet();sim.mode='idle';sim.act=null;sim.windup=null;sim.talk=null;remoteSocial=null;sim.t=12*60;sim.route=[[D.spots.bed[1],FLOOR_Y[1]]];sim.s=sim.target=0;requestIncomingCall('abu','friend_home');showIncomingCall();speed=6});
 assert.equal(await p.locator('.call-answer').textContent(),'去你家');assert.equal(await p.locator('.call-decline').textContent(),'下次吧');assert.equal(await p.evaluate(()=>phoneCall.deadline-performance.now()>5000),true);
 await p.evaluate(()=>speed=0);await p.locator('.call-answer').click();await p.waitForTimeout(500);assert.equal(await p.evaluate(()=>friendVisit?.phase),'departing');
 await p.evaluate(()=>{speed=1;if(sim.windup)sim.windup.at=realClock;for(let i=0;i<800&&sim.place==='home';i++)step(.1,.1);speed=0;});assert.equal(await p.evaluate(()=>sim.place),'friend_home');
 // Current host cannot call themselves; other home visits / outings are blocked.
 assert.equal(await p.evaluate(()=>requestIncomingCall(friendVisit.id)),false);
 assert.equal(await p.evaluate(()=>inviteHome('rain')),false);await p.evaluate(()=>closeSocialSheet());
 // Smaller homes never spawn a family and refusal leads home at the deadline.
 await p.evaluate(()=>{visitEnter('cream');const c=visitingFriend();const old=friendHomes[c.id];delete friendHomes[c.id];friendHomes[c.id]={houseId:'cream',relations:[]};initFriendHomeActors();sim.t=22.6*60;speed=1;stepFriendHome(.1,.1);speed=0;});assert.equal(await p.evaluate(()=>sim.place),'home');
 // Exhaustion still collapses on the current floor and survives a save.
 await p.evaluate(()=>{visitEnter('maple');sim.graceUntil=0;sim.needs.energy=0;speed=1;stepFriendHome(.1,.1);speed=0;});
 assert.equal(await p.evaluate(()=>sim.mode),'down');
 const collapsed=await p.evaluate(()=>{const y=here().y,s=JSON.parse(JSON.stringify(snapshot()));restore(s);return {mode:sim.mode,y:here().y,oldY:y};});assert.equal(collapsed.mode,'down');assert.equal(collapsed.y,collapsed.oldY);
 assert.equal(await p.evaluate(()=>Object.values(FRIEND_VISIT_TEXT.family).flat().length),144);
 assert.deepEqual(errors,[]);console.log('PASS: 30 real homes, graph routing, fixed saved addresses, needs, residents, active/deferred travel, invite call, six-second deadline, overnight request/refusal/sleep/reload/morning return.');
 }finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
