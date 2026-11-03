// Story lock (owner 2026-11-03): while a story talk / quest scene is on, no calls, texts, visits, chance cards,
// stray lines or leaving, and her needs stand still; a story never starts over a phone call (it waits).
// Usage: node tools/check_story_lock.js
const fs=require('fs'),assert=require('node:assert/strict'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1400,height:1000}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.infeiQuests&&seasonMapTest.state.spring.state.loaded,null,{timeout:60000});
 const ev=(f,a)=>p.evaluate(f,a);
 await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=4;sim.t=3*1440+10*60;weather.force='clear';
  Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done',coins:20});seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 await ev(()=>{const c=seasonMapTest.ctl();c.go(0,120);for(const k in sim.needs)sim.needs[k]=70;});
 // a quest talk opens
 await ev(()=>infeiQuests.talk('apo'));await p.waitForFunction(()=>springFarm.speech.open,null,{timeout:20000});
 const r=await ev(async()=>{const n0=JSON.stringify(sim.needs),t0=sim.t,act=sim.act;
  const out={locked:storyLocked(),holds:cardHolds(),call:canReceiveCall(),ring:requestIncomingCall(socialState.contacts[0].id),card:(lifeFlags.cards.last=-1e9,rollCard(lifeCtx())),moment:cardMoment('cook')};
  speak('这句不该出现');out.say=popSay.textContent.includes('这句不该出现');startAct('go_home');out.home=sim.act==='go_home';
  await new Promise(r=>setTimeout(r,2500));out.needsSame=JSON.stringify(sim.needs)===n0;out.clock=sim.t===t0;return out;});
 console.log(r);assert.deepEqual(r,{locked:true,holds:true,call:false,ring:false,card:false,moment:false,say:false,home:false,needsSame:true,clock:true});
 // finish the talk: everything is back
 for(let k=0;k<80&&await ev(()=>infeiQuests.busy);k++){await ev(()=>{const c=document.querySelector('.story-choices:not([hidden]) button');if(c)c.click();else document.querySelector('.story-bubble')?.click();});await p.waitForTimeout(150);}
 await p.waitForFunction(()=>!infeiQuests.busy,null,{timeout:20000});
 assert.equal(await ev(()=>storyLocked()||cardHolds()),false);assert.equal(await ev(()=>canReceiveCall()),true);
 // a story never starts over a call: it waits, then speaks
 await ev(()=>{phoneCall.phase='ringing';phoneCall.deadline=performance.now()+1e9;phoneCall.contactId=socialState.contacts[0].id;infeiQuests.Q().stew.step=0;sim.t=Math.floor(sim.t/1440)*1440+10*60;seasonMapTest.ctl().go(2,60);infeiQuests.talk('zhou');});
 await p.waitForTimeout(2500);assert.equal(await ev(()=>springFarm.speech.open),false,'no story over a ringing phone');
 await ev(()=>{phoneCall.phase='idle';phoneCall.contactId=null;});
 await p.waitForFunction(()=>springFarm.speech.open,null,{timeout:10000});
 assert.deepEqual(errors,[]);console.log('PASS');
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
