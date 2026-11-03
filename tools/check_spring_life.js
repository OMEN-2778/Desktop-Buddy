// Spring-map life on the game-shell test page: spring-only chance cards (with farm effects),
// spring phone talk, no calls from someone beside her (妈妈 on the farm, 爸妈 home for 春节).
// Usage: node tools/check_spring_life.js [outDir]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/spring-life';fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});let n=0;try{
 const p=await b.newPage({viewport:{width:1400,height:1000},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error('PAGE:',e.message);});
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.springFarm&&seasonMapTest.state.spring.state.loaded);
 const shot=async name=>{await p.waitForTimeout(500);const v=await p.locator('#view').boundingBox(),top=Math.max(0,v.y-175);await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-'+name+'.png'),clip:{x:Math.max(0,v.x-10),y:top,width:v.width+20,height:v.y+v.height-top+20}});};
 // 春节: parents at home never ring; a friend still can
 const cny=await p.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=600;socialState.nextCall=socialState.nextVisit=1e12;
  const real=cnyPresent;cnyPresent=()=>true;const r={mom:requestIncomingCall('mom'),dad:requestIncomingCall('dad'),withMom:contactWithHero('mom')};phoneCall.phase='idle';cnyPresent=real;r.after=contactWithHero('mom');return r;});
 assert.deepEqual(cny,{mom:false,dad:false,withMom:true,after:false});
 await p.evaluate(()=>{const F=springFarm.state;Object.assign(F,{letter:1,unlocked:true,phase:'done',coins:5});F.beds={9:{crop:'carrot',progress:0,watered:-1,at:sim.t},10:{crop:'cabbage',progress:1,watered:-1,at:sim.t}};
  seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 await p.evaluate(()=>{const c=seasonMapTest.ctl();c.go(4,120);springFarm.mom.on=false;});
 // natural rolls on the farm only draw spring cards
 const rolled=await p.evaluate(()=>{if(card){card=null;cardEl.hidden=true;}const seen=[];const real=showCard;showCard=cd=>seen.push(cd.at);for(let i=0;i<60;i++){lifeFlags.cards.last=-1e9;rollCard(lifeCtx());}showCard=real;return seen;});
 assert(rolled.length>10&&rolled.every(a=>a==='spring_test'),JSON.stringify(rolled));
 // three cards with farm effects, played by hand
 for(const [title,k]of [['跑出来的小羊','a'],['一场及时雨','a'],['卖菜的小摊','a']]){
  const before=await p.evaluate(()=>JSON.stringify(springFarm.state));
  await p.evaluate(t=>{const cd=SPRING_CARDS.find(c=>c.title===t);Math.random=(r=>()=>0.1)(Math.random);showCard(cd);},title);await shot('机会卡-'+title);
  await p.locator(`.cd-opt[data-k="${k}"]`).click();await p.waitForFunction(()=>card?.phase==='result',null,{timeout:5000});await shot('结果-'+title);
  await p.mouse.click(10,10);await p.waitForTimeout(700);
  const after=await p.evaluate(()=>JSON.stringify(springFarm.state));console.log(title,before===after?'(no farm change)':'farm changed',await p.evaluate(()=>springFarm.state.coins));
 }
 const F=await p.evaluate(()=>springFarm.state);assert.equal(F.coins,5+1+2);assert.equal(F.beds[9].watered,await p.evaluate(()=>Math.floor(sim.t/1440)));
 // a call on the farm uses spring talk; 妈妈 beside her never calls
 await p.evaluate(()=>{springFarm.mom.on=true;});assert.equal(await p.evaluate(()=>requestIncomingCall('mom')),false);await p.evaluate(()=>{springFarm.mom.on=false;});
 const talk=await p.evaluate(()=>{Math.random=()=>0.5;const it=chatItem('call','friend','call',sortedContacts().find(c=>!c.family)?.id);return it.talk.title;});
 assert(await p.evaluate(t=>SPRING_TALK.friend.some(x=>x.title===t),talk),talk);
 await p.evaluate(()=>{socialState.nextCall=sim.t;});await p.waitForFunction(()=>phoneCall.phase==='ringing',null,{timeout:15000});await shot('农庄来电');
 console.log('spring call title:',talk);assert.deepEqual(errors,[]);console.log('PASS',n,'shots in',out);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
