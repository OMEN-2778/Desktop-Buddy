// 茵菲谷 through the year on the game-shell test page: the map art follows the game season,
// late-autumn seeds that cannot ripen are greyed, winter freezes unripe crops and closes sowing.
// Usage: node tools/check_infei_seasons.js [outDir]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/infei-seasons';fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});let n=0;try{
 const p=await b.newPage({viewport:{width:1400,height:1000},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error('PAGE:',e.message);});
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.springFarm&&seasonMapTest.state.spring.state.loaded,null,{timeout:60000});
 const shot=async name=>{await p.waitForTimeout(600);const v=await p.locator('#view').boundingBox(),top=Math.max(0,v.y-120);await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-'+name+'.png'),clip:{x:Math.max(0,v.x-10),y:top,width:v.width+20,height:v.y+v.height-top+10}});};
 await p.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=600;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;
  Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done',coins:20});seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 const at=async(day,scene,x=170)=>{await p.evaluate(([d,sc,x])=>{weather.force='clear';sim.t=d*1440+11*60;springFarm.roll();const c=seasonMapTest.ctl();c.go(sc,x);},[day,scene,x]);};
 for(const [season,day]of [['春',4],['夏',18],['秋',32],['冬',46]])for(const [scene,name]of [[1,'油菜花田'],[3,'农舍'],[4,'菜园'],[5,'果园']]){await at(day,scene);await shot(season+'-'+name);}
 // late autumn: slow seeds greyed
 await at(38,4,110);await p.evaluate(()=>{springFarm.state.beds={};springFarm.openBed(9);});await p.waitForTimeout(300);await p.locator('#ring button',{hasText:'播种'}).click();await p.waitForTimeout(400);await shot('秋末-种子铺');
 const offs=await p.evaluate(()=>[...document.querySelectorAll('#picker .pk-item')].map(b=>b.classList.contains('fu-off')));await p.locator('#picker .x').click();
 assert.deepEqual(offs,[false,false,true,true]);   // 4 days to winter: carrot 2, cabbage 4 fit; corn 6, pumpkin 8 do not
 // winter frost: an unripe crop is lost, a ripe one stays
 await p.evaluate(()=>{const F=springFarm.state;F.beds={9:{crop:'pumpkin',progress:2,watered:-1,at:sim.t},10:{crop:'carrot',progress:2,watered:-1,at:sim.t}};F.day=41;sim.t=42*1440+8*60;springFarm.roll();});
 const beds=await p.evaluate(()=>Object.keys(springFarm.state.beds));assert.deepEqual(beds,['10']);
 await p.evaluate(()=>{delete springFarm.state.beds[10];springFarm.openBed(9);});await p.waitForTimeout(300);await shot('冬天-不能播种');
 assert(await p.evaluate(()=>[...document.querySelectorAll('#ring button')].some(b=>b.textContent.includes('冬天休耕'))));
 assert.deepEqual(errors,[]);console.log('PASS',n,'shots in',out);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
