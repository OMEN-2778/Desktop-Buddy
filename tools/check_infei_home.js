// 茵菲谷 farmhouse on the game-shell test page: furniture rings, stairs, needs filled at home,
// 回家 = farmhouse, low needs walk her in, 离开茵菲谷 leaves; no decorative herd.
// Usage: node tools/check_infei_home.js [outDir]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/infei-home';fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});let n=0;try{
 const p=await b.newPage({viewport:{width:1400,height:1000}}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error('PAGE:',e.message);});
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.infeiHome&&seasonMapTest.state.spring.state.loaded,null,{timeout:60000});
 const ev=(f,a)=>p.evaluate(f,a),S=()=>seasonMapTest.ctl().state;
 const shot=async name=>{await p.waitForTimeout(400);const v=await p.locator('#view').boundingBox();await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-'+name+'.png'),clip:{x:v.x,y:Math.max(0,v.y-60),width:v.width,height:v.height+60}});};
 const clickAt=async(x,y)=>{const v=await p.locator('#view').boundingBox(),[h,cam]=await ev(()=>[seasonMapTest.ctl().canvas.height,seasonMapTest.ctl().state.camera||0]);await p.mouse.click(v.x+(x-cam)/342*v.width,v.y+y/h*v.height);await p.waitForTimeout(350);};
 const ring=async label=>{await p.locator('#ring button',{hasText:label}).first().click();await p.waitForTimeout(300);};
 const idle=()=>p.waitForFunction(()=>{const s=seasonMapTest.ctl().state;return !s.target&&!s.after&&!s.door;},null,{timeout:30000});
 await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=4;sim.t=2*1440+9*60;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;weather.force='clear';
  for(const k in sim.needs)sim.needs[k]=80;Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done',coins:20});seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 // no decorative animals at the start
 await ev(()=>seasonMapTest.ctl().go(5,520));await shot('牧场一开始是空的');assert.equal(await ev(()=>springFarm.state.animals?.length||0),0);
 // walk into the farmhouse by its door
 await ev(()=>{seasonMapTest.ctl().go(3,150);seasonMapTest.state.autoAt=sim.t+1e9;});await p.waitForTimeout(300);await clickAt(182,90);
 await p.waitForFunction(()=>seasonMapTest.ctl().state.inside&&!seasonMapTest.ctl().state.door,null,{timeout:20000});await p.waitForTimeout(900);await shot('进屋-提示');
 assert(await ev(()=>document.body.innerText.includes('点家具')));
 // bed: ring, she climbs the stairs at their middle and sleeps
 await ev(()=>{sim.needs.energy=30;});await clickAt(105,35);   // one click uses it (owner 2026-11-03: no second menu)
 await p.waitForFunction(()=>{const s=seasonMapTest.ctl().state;return s.y<100&&s.y>60;},null,{timeout:15000});
 const sx=await ev(()=>seasonMapTest.ctl().state.x);await shot('走楼梯');assert(Math.abs(sx-61)<1,'stairs x '+sx);
 await p.waitForFunction(()=>infeiHome.svc?.id==='bed',null,{timeout:20000});await shot('睡觉');
 const e0=await ev(()=>sim.needs.energy);await p.waitForTimeout(2500);assert(await ev(()=>sim.needs.energy)>e0);
 // stove downstairs: cancels sleep, cooks
 await ev(()=>{sim.needs.hunger=30;});await clickAt(250,90);
 // the stove opens the home's dish menu (owner 2026-11-06); pick the first dish
 await p.waitForFunction(()=>pickOn==='cook_farm',null,{timeout:5000});await p.locator('#picker .pk-item').first().click();
 await p.waitForFunction(()=>infeiHome.svc?.id==='stove',null,{timeout:20000});await shot('做饭');
 // parents' room is look-only: no menu, she only looks
 await clickAt(250,30);const items=await ev(()=>[...document.querySelectorAll('#ring button')].map(b=>b.textContent));assert.deepEqual(items.filter(t=>t.includes('睡')),[]);await ev(()=>closeRing());
 // 回家 in her ring = the farmhouse; low needs walk her in by herself
 await ev(()=>{infeiHome.stop();sim.needs.hunger=80;const c=seasonMapTest.ctl();c.leave();});await idle();await p.waitForTimeout(800);await ev(()=>{seasonMapTest.ctl().go(4,150);seasonMapTest.state.autoAt=sim.t+1e9;});await p.waitForTimeout(300);
 await ev(()=>{const s=seasonMapTest.ctl().state;openRing('away','buddy');});await shot('小人菜单');
 const labels=await ev(()=>[...document.querySelectorAll('#ring button')].map(b=>b.textContent));console.log(labels);assert(labels.includes('回家')&&labels.includes('离开茵菲谷'));
 await ring('回家');await p.waitForFunction(()=>seasonMapTest.ctl().state.inside&&sim.place==='spring_test',null,{timeout:10000});await shot('回家=回农舍');
 await ev(()=>{const c=seasonMapTest.ctl();c.state.inside=false;c.go(1,150);sim.needs.hygiene=10;});
 await p.waitForFunction(()=>infeiHome.svc?.id==='bath',null,{timeout:30000});await p.waitForFunction(()=>infeiHome.svc?.id==='bath',null,{timeout:30000});await shot('自己回屋洗澡');assert.equal(await ev(()=>sim.place),'spring_test');
 // 离开茵菲谷 goes back to the real home
 await ev(()=>{infeiHome.stop();sim.needs.hygiene=90;openRing('away','buddy');});await ring('离开茵菲谷');
 await p.waitForFunction(()=>sim.place==='home'&&!wiping,null,{timeout:60000});
 assert.deepEqual(errors,[]);console.log('PASS',n,'shots in',out);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
