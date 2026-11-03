// 茵菲谷 sound on the game-shell test page: the valley theme per season / night, the airport track, ambience
// beds per spot (brook, windmill), farm sounds from state changes, the suona. Real Chromium audio.
// Usage: node tools/check_infei_audio.js
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const DIST=path.resolve('desktop/dist/map-test');
(async()=>{const b=await chromium.launch({args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});try{
 const p=await b.newPage({viewport:{width:1400,height:1000}}),errors=[],loaded=[];p.on('pageerror',e=>errors.push(e.message));
 await p.route('http://season.test/**',r=>{const u=new URL(r.request().url()),f=u.pathname==='/'?'index.html':decodeURIComponent(u.pathname.slice(1));const fp=path.join(DIST,f);
  if(!fs.existsSync(fp))return r.fulfill({status:404,body:''});if(f.endsWith('.mp3'))loaded.push(f);r.fulfill({body:fs.readFileSync(fp),contentType:f.endsWith('.html')?'text/html; charset=utf-8':'audio/mpeg'});});
 await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.infeiAudio&&seasonMapTest.state.spring.state.loaded,null,{timeout:60000});
 await p.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=3*1440+10*60;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;weather.force='clear';});
 for(const k of ['bgm','sfx']){await p.evaluate(()=>setSettingsOpen(true));const s=p.locator('#volume-'+k);await s.focus();await s.press('End');await p.waitForTimeout(200);}
 await p.evaluate(()=>setSettingsOpen(false));
 await p.evaluate(()=>{Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done',coins:50,open:[9,10,11,12]});seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 const dbg=()=>p.evaluate(()=>gameAudio.debug());
 assert.equal((await dbg()).desiredMusic,'BGM/infei/infei-spring.mp3');
 await p.waitForFunction(()=>gameAudio.debug().musicTracks.some(t=>t.path.includes('infei-spring')&&!t.paused),null,{timeout:20000});
 await p.evaluate(()=>{sim.t=3*1440+21*60;});assert.equal((await dbg()).desiredMusic,'BGM/infei/infei-night.mp3');
 await p.evaluate(()=>{sim.t=17*1440+10*60;springFarm.roll();});assert.equal((await dbg()).desiredMusic,'BGM/infei/infei-summer.mp3');
 await p.evaluate(()=>{sim.t=3*1440+10*60;});
 // ambience per spot
 await p.evaluate(()=>seasonMapTest.ctl().go(0,150));let beds=await p.evaluate(()=>Object.keys(gameAudio.ambience()));console.log('brook',beds);assert(beds.includes('brook'));
 await p.evaluate(()=>seasonMapTest.ctl().go(2,150));beds=await p.evaluate(()=>Object.keys(gameAudio.ambience()));assert(beds.includes('mill'));
 await p.waitForFunction(()=>gameAudio.debug().loopPaths.some(x=>x.includes('infei-windmill')),null,{timeout:15000});
 // farm sounds from state changes
 const heard=async(id,fn)=>{await p.evaluate(fn);await p.waitForFunction(id=>gameAudio.debug().stats.last.includes(id),id,{timeout:8000});};
 await heard('infei-sow',()=>{springFarm.state.beds[9]={crop:'carrot',progress:0,watered:-1,at:sim.t,picks:0};});
 await heard('watering',()=>{springFarm.state.beds[9].watered=Math.floor(sim.t/1440);});
 await heard('infei-moo',()=>infeiFarm.buy({kind:'cow',cost:0}));
 await heard('infei-coin',()=>{springFarm.state.coins+=5;});
 await heard('infei-suona',()=>springFarm.speech.show('风车里','呜——',{special:true,advance:()=>{}}));
 await p.evaluate(()=>springFarm.speech.hide());
 // the airport has its own track
 await p.evaluate(()=>throughDoor('airport_test'));await p.waitForFunction(()=>sim.place==='airport_test'&&!wiping,null,{timeout:30000});
 assert.equal((await dbg()).desiredMusic,'BGM/infei/infei-airport.mp3');
 await p.waitForFunction(()=>gameAudio.debug().musicTracks.some(t=>t.path.includes('infei-airport')),null,{timeout:20000});
 console.log('loaded',[...new Set(loaded.filter(f=>f.includes('infei')))]);
 assert.deepEqual(errors,[]);console.log('PASS');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
