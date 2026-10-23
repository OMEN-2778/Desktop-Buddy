const assert=require('node:assert/strict');const fs=require('node:fs');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{const p=await b.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8778/');await p.waitForFunction(()=>typeof booted!=='undefined'&&booted);await p.waitForTimeout(1300);
 const stats=await p.evaluate(()=>{
 closeGuide();closePicker();closeRing();speed=0;sim.mode='idle';sim.act=null;sim.windup=null;sim.t=720;sim.idleUntil=Infinity;sim.graceUntil=Infinity;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,100]));
 const oldPlan=weather.plan;weather.plan=new Map();const counts=[0,0,0,0];for(let y=0;y<100;y++)for(let se=0;se<4;se++)for(let day=0;day<14;day++)for(const e of planDay(y*56+se*14+day))if(e.kind==='storm')counts[se]++;
 weather.plan=oldPlan;if(!counts[0]||!counts[2]||counts[1]<=Math.max(counts[0],counts[2])*2||counts[3])throw Error('Season storm distribution: '+counts);
 weather.force='storm';weather.kind='storm';
 let maps=0;for(const place of ['front','park','beach']){
  sim.place=place;sim.park=place==='park'?{zone:'central',seated:false}:null;sim.route=[[OUT[place].doorX,OUT[place].feet]];sim.s=0;arriveAt(place);life.npcs.push(makeNpc('walker',{x:50,feet:100}));npcTick(.1,true);
  if(life.npcs.length)throw Error('Outdoor citizens in thunderstorm');lightningStrike();stormFX.left=stormFX.duration/2;render();maps++;
 }
 sim.place='home';sim.route=[[D.spots.front_door[1],FLOOR_Y[0]]];arriveAt('home');stormFX.left=0;render();const dark=buf.toDataURL();
 lightningStrike();stormFX.left=stormFX.duration/2;render();if(buf.toDataURL()===dark)throw Error('Missing house flash');
 for(let i=0;i<100;i++){stormReaction(false);if([...moods.keys()].filter(id=>id.startsWith('storm_')).length!==1)throw Error('Weather mood stacking');}
 const pos=(lifeFlags.stormSeen||[]).filter(id=>id.startsWith('positive')).length;if(!pos)throw Error('No positive responses');
 for(const place of ['mall','bar']){sim.t=1200;sim.place=place;sim.route=[[OUT[place].doorX,OUT[place].feet]];sim.s=0;sim.mode='idle';sim.act=null;sim.bar=null;arriveAt(place);moods.clear();stormReaction();updateConds();if(moods.has('rainy')||[...moods.keys()].some(id=>id.startsWith('storm_'))||stormExposed())throw Error('Indoor storm effects');render();}
 sim.place='home';sim.route=[[D.spots.front_door[1],FLOOR_Y[0]]];sim.s=0;arriveAt('home');weather.nextLightning=sim.t+12;const next=weather.nextLightning;stormFX.left=0;tickStorm(0);if(weather.nextLightning!==next||stormFX.left)throw Error('Pause');
 const saved=snapshot();if(saved.weather.nextLightning!==next)throw Error('Storm persistence');
 return {seasonStorms:counts,maps,reactions:STORM_TEXT.negative.length+STORM_TEXT.positive.length+STORM_TEXT.outdoor.length,cards:CARDS.filter(c=>c.at==='storm').length};
 });
 fs.mkdirSync('/workspace/artifacts/storm',{recursive:true});
 for(const place of ['home','park','beach']){await p.evaluate(place=>{sim.place=place;sim.mode='idle';sim.act=null;sim.park=place==='park'?{zone:'central',seated:false}:null;sim.route=[[place==='home'?D.spots.front_door[1]:OUT[place].doorX,place==='home'?FLOOR_Y[0]:OUT[place].feet]];sim.s=0;arriveAt(place);weather.kind='storm';weather.force='storm';lightningStrike();stormFX.left=stormFX.duration/2;render();},place);await p.locator('#view').screenshot({path:`/workspace/artifacts/storm/${place}.png`});}
 assert.deepEqual(errors,[]);console.log('PASS: '+JSON.stringify(stats)+'; window/room lightning, no exposed citizens, indoor immunity, non-stacking mixed emotions, pause and saved schedule');
 await p.emulateMedia({reducedMotion:'no-preference'});
 await p.reload();await p.waitForFunction(()=>booted);
 const timing=await p.evaluate(()=>{
  sim.place='home';weather.kind='storm';closeGuide();speed=0;
  const random=Math.random,groups=[];
  try{for(const roll of [0,.9]){
   Math.random=()=>roll;lightningStrike();const length=stormFX.duration;
   let count=0,start=0,wasLit=false;const holds=[],values=new Set();
   for(let t=0;t<=length+.02;t+=.01){
    stormFX.left=length-t;const alpha=stormFlash(),lit=alpha>0;values.add(alpha);
    if(lit&&!wasLit){count++;start=t;}
    if(!lit&&wasLit)holds.push(Math.round((t-start)*1000));
    wasLit=lit;
   }
   groups.push({count,holds,values:[...values].sort(),length});
  }}finally{Math.random=random;}
  lightningStrike();stormFX.left=stormFX.duration-.12;
  const left=stormFX.left;tickStorm(0);if(stormFX.left!==left)throw Error('Pause advanced a flash group');
  const c=document.createElement('canvas');c.width=W;c.height=H;const ctx=c.getContext('2d');
  const reset=()=>{ctx.clearRect(0,0,W,H);ctx.fillStyle='#262a36';ctx.fillRect(0,0,W,H);};
  const sample=(x,y)=>[...ctx.getImageData(Math.floor(x),Math.floor(y),1,1).data];
  const oldWindows={...windowState};for(const id of Object.keys(WMASK))windowState[id]='drawn';
  reset();drawStorm(ctx);const ambient=sample(50,50);
  const [id,win]=Object.entries(WMASK).find(([,win])=>{
   const m=win.closed,x=win.x+m.w/2,y=win.y+m.h/2;
   return Object.values(D.rooms).some(([rx,ry,rw,rh])=>x>=rx&&x<rx+rw&&y>=ry&&y<ry+rh);
  });
  const m=win.closed,x=win.x+m.w/2,y=win.y+m.h/2;
  const room=Object.values(D.rooms).find(([rx,ry,rw,rh])=>x>=rx&&x<rx+rw&&y>=ry&&y<ry+rh);
  const [rx,ry,rw,rh]=room,corners=[[rx+2,ry+2],[rx+rw-3,ry+2],[rx+2,ry+rh-3],[rx+rw-3,ry+rh-3]];
  corners.sort((a,b)=>Math.hypot(b[0]-x,b[1]-y)-Math.hypot(a[0]-x,a[1]-y));
  windowState[id]='closed';reset();drawStorm(ctx);const near=sample(x,y),far=sample(...corners[0]);
  const other=Object.values(D.rooms).find(r=>r!==room),outside=sample(other[0]+other[2]/2,other[1]+other[3]/2);
  windowState[id]='drawn';reset();drawStorm(ctx);const curtained=sample(x,y);
  for(const key of Object.keys(windowState))if(!(key in oldWindows))delete windowState[key];Object.assign(windowState,oldWindows);
  sim.place='front';const old=realClock;realClock=0;let lines=0;const starts=[];
  const rain={fillRect(){},beginPath(){},moveTo(x,y){starts.push([x,y]);},lineTo(){},stroke(){lines++;}};
  drawOutsideWeather(rain);const first=starts[0];realClock=.1;starts.length=0;drawOutsideWeather(rain);const travel=starts[0][1]-first[1];realClock=old;
  return {groups,ambient,near,far,outside,curtained,lines,travel};
 });
 assert.deepEqual(timing.groups.map(g=>g.count),[2,3],'Both two- and three-pulse groups must occur');
 for(const group of timing.groups){
  assert.deepEqual(group.values,[0,.8],'Pulses keep hard edges and an 80% white overlay');
  assert.ok(group.holds.every(ms=>ms>=250&&ms<=430),'Each pulse is visibly longer than the old 100 ms flash');
  assert.ok(group.length>=1.1,'Keep a readable gap between pulses');
 }
 assert.ok(timing.ambient.slice(0,3).every(v=>v>200&&v<240),'An 80% flash keeps scene detail visible');
 assert.ok(timing.near[0]>timing.far[0]+5,'Window surroundings must be brighter than the far side of the room');
 assert.deepEqual(timing.curtained,timing.ambient,'Curtains block the additional window spill');
 assert.deepEqual(timing.outside,timing.ambient,'Window light must not cross the room walls or floor slab');
 assert.deepEqual([timing.lines,timing.travel],[480,21],'Keep the dense, fast rain');
 await p.evaluate(()=>{
  closeGuide();closeRing();closePicker();speed=0;sim.place='home';sim.mode='idle';sim.act=null;sim.idleUntil=Infinity;
  sim.route=[[D.spots.front_door[1],FLOOR_Y[0]]];sim.s=0;weather.kind='storm';weather.force='storm';
  for(const id of Object.keys(windowState))windowState[id]='closed';lightningStrike();stormFX.left=stormFX.duration-.12;render();
 });
 await p.locator('#view').screenshot({path:'/workspace/artifacts/storm/window-spill.png'});
 assert.deepEqual(errors,[]);
 console.log('PASS: 2/3 hard-edged flashes per group at 80%, 260–420 ms holds, dark gaps, pause; stronger window spill confined to rooms and blocked by curtains; heavy rain unchanged');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
