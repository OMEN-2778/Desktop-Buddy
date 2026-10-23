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
 for(const place of ['mall','bar']){sim.t=1200;sim.place=place;sim.route=[[OUT[place].doorX,OUT[place].feet]];sim.s=0;sim.mode='idle';sim.act=null;sim.bar=null;arriveAt(place);moods.clear();stormReaction();if([...moods.keys()].some(id=>id.startsWith('storm_'))||stormExposed())throw Error('Indoor storm effects');render();}
 sim.place='home';sim.route=[[D.spots.front_door[1],FLOOR_Y[0]]];sim.s=0;arriveAt('home');weather.nextLightning=sim.t+12;const next=weather.nextLightning;stormFX.left=0;tickStorm(0);if(weather.nextLightning!==next||stormFX.left)throw Error('Pause');
 const saved=snapshot();if(saved.weather.nextLightning!==next)throw Error('Storm persistence');
 return {seasonStorms:counts,maps,reactions:STORM_TEXT.negative.length+STORM_TEXT.positive.length+STORM_TEXT.outdoor.length,cards:CARDS.filter(c=>c.at==='storm').length};
 });
 fs.mkdirSync('/workspace/artifacts/storm',{recursive:true});
 for(const place of ['home','park','beach']){await p.evaluate(place=>{sim.place=place;sim.mode='idle';sim.act=null;sim.park=place==='park'?{zone:'central',seated:false}:null;sim.route=[[place==='home'?D.spots.front_door[1]:OUT[place].doorX,place==='home'?FLOOR_Y[0]:OUT[place].feet]];sim.s=0;arriveAt(place);weather.kind='storm';weather.force='storm';lightningStrike();stormFX.left=stormFX.duration/2;render();},place);await p.locator('#view').screenshot({path:`/workspace/artifacts/storm/${place}.png`});}
 assert.deepEqual(errors,[]);console.log('PASS: '+JSON.stringify(stats)+'; window/room lightning, no exposed citizens, indoor immunity, non-stacking mixed emotions, pause and saved schedule');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
