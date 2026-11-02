// 茵菲谷 farm life on the game-shell test page: seasonal seeds, rain, regrowing crops, 仓库, parents'
// help, orchard, livestock (summer + winter barn), 每日操盘, gifts and 藏品. Saves a shot per step.
// Usage: node tools/check_infei_farm.js [outDir]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/infei-farm';fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});let n=0;try{
 const p=await b.newPage({viewport:{width:1400,height:1000},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error('PAGE:',e.message);});
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.infeiFarm&&seasonMapTest.state.spring.state.loaded,null,{timeout:60000});
 const shot=async(name,pad=150)=>{await p.waitForTimeout(500);const v=await p.locator('#view').boundingBox(),top=Math.max(0,v.y-pad);await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-'+name+'.png'),clip:{x:Math.max(0,v.x-10),y:top,width:v.width+20,height:v.y+v.height-top+10}});};
 const ev=(f,a)=>p.evaluate(f,a);
 const S=()=>ev(()=>JSON.parse(JSON.stringify(springFarm.state)));
 const box=async()=>p.locator('#view').boundingBox();
 const park=()=>ev(()=>{const s=seasonMapTest.ctl().state;s.x=s.scene===5?(s.camera||0)+171:200;s.target=null;s.after=null;seasonMapTest.state.autoAt=sim.t+1e9;});
 const clickAt=async(x,y)=>{await park();const v=await box(),h=await ev(()=>seasonMapTest.ctl().canvas.height);const cam=await ev(()=>seasonMapTest.ctl().state.camera||0);await p.mouse.click(v.x+(x-cam)/342*v.width,v.y+y/h*v.height);await p.waitForTimeout(300);};
 const ring=async label=>{await p.locator('#ring button',{hasText:label}).first().click();await p.waitForTimeout(300);};
 const day=async(d,h=8)=>{await ev(([d,h])=>{sim.t=d*1440+h*60;springFarm.roll();},[d,h]);};
 const walkDone=()=>p.waitForFunction(()=>!seasonMapTest.ctl().state.target&&!seasonMapTest.ctl().state.after,null,{timeout:30000});
 await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=4;sim.t=2*1440+8*60;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;weather.force='clear';
  setInterval(()=>{for(const k in sim.needs)sim.needs[k]=Math.max(sim.needs[k],90);},500);
  Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done',coins:120});seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 // ---- spring seeds, sow strawberry (regrows)
 await ev(()=>seasonMapTest.ctl().go(4,100));await p.waitForTimeout(400);
 await clickAt(40,88);await ring('播种');await shot('春天种子铺');
 const springSeeds=await ev(()=>[...document.querySelectorAll('#picker .pk-item b')].map(b=>b.textContent));assert.deepEqual(springSeeds,['胡萝卜','白菜','草莓','土豆']);
 await p.locator('#picker .pk-item',{hasText:'草莓'}).click();await walkDone();
 // ---- rain waters the bed by itself
 await ev(()=>{weather.force='rain';});await p.waitForTimeout(300);await clickAt(40,88);await shot('下雨-不用浇水');
 assert(await ev(()=>[...document.querySelectorAll('#ring button')].some(b=>b.textContent.includes('下过雨了'))));await ev(()=>{closeRing();weather.force='clear';});
 for(let d=3;d<=7;d++){await ev(d=>{springFarm.state.beds[9].watered=d-1;},d);await day(d);}
 assert.equal((await S()).beds[9].progress,5);await shot('草莓熟了');
 await clickAt(40,88);await ring('收获');await walkDone();
 let f=await S();assert.equal(f.inv.strawberry,1);assert.equal(f.beds[9].progress,2);   // stays, regrows
 // ---- parents water a dry bed while she watches
 await ev(()=>{const F=springFarm.state;F.beds[10]={crop:'carrot',progress:0,watered:-1,at:sim.t,picks:0};F.beds[9].watered=Math.floor(sim.t/1440);F.help={day:Math.floor(sim.t/1440),at:sim.t-1,who:'mom',done:false};});
 await p.waitForFunction(()=>infeiFarm.parent.on&&infeiFarm.parent.water>0,null,{timeout:30000});await shot('妈妈回来帮忙浇水');
 await p.waitForFunction(()=>springFarm.state.beds[10].watered===Math.floor(sim.t/1440),null,{timeout:15000});
 // ---- orchard: plant a peach tree in the pit
 await ev(()=>seasonMapTest.ctl().go(5,300));await p.waitForTimeout(500);
 await clickAt(330,75);await shot('果园-空树坑');await ring('种果树');await shot('果苗铺');
 await p.locator('#picker .pk-item',{hasText:'桃树苗'}).click();await walkDone();
 assert.equal((await S()).trees[0].kind,'peach');
 // ---- pasture: buy a chicken, a lamb and a cow
 await ev(()=>seasonMapTest.ctl().go(5,520));await p.waitForTimeout(500);
 await clickAt(500,38);await shot('粮仓菜单');await ring('牲畜铺');await shot('牲畜铺');
 for(const k of ['羊','牛']){await p.locator('#picker .pk-item',{hasText:k}).first().click();await p.waitForTimeout(900);await clickAt(500,38);await ring('牲畜铺');}
 await p.locator('#picker .pk-item',{hasText:'鸡'}).first().click();await p.waitForTimeout(300);
 f=await S();assert.deepEqual(f.animals.map(a=>a.kind),['sheep','cow','chicken']);
 // ---- summer: days pass, the peach grows, the animals give products
 for(let d=8;d<=17;d++){await ev(()=>{for(const a of springFarm.state.animals)a.petDay=Math.floor(sim.t/1440);});await day(d);}
 await ev(()=>{const t=springFarm.state.trees[0];t.grown=8;t.ready=true;});
 await ev(()=>seasonMapTest.ctl().go(5,520));await p.waitForTimeout(800);await shot('夏天牧场-有产物');
 const cow=await ev(()=>{const a=springFarm.state.animals.find(a=>a.kind==='cow');return [a.x,a.y];});
 await clickAt(cow[0],cow[1]-12);await shot('牛的菜单');await ring('查看');await shot('牛的详情');await ev(()=>closeSocialSheet());
 await ev(()=>seasonMapTest.ctl().go(5,300));await p.waitForTimeout(600);await shot('夏天果园-桃子熟了');
 await clickAt(330,75);await ring('摘果');await walkDone();
 await ev(()=>{for(const a of springFarm.state.animals)if(a.ready){springFarm.state.inv[a.ready]=(springFarm.state.inv[a.ready]||0)+1;springFarm.state.seen[a.ready]??=Math.floor(sim.t/1440);a.ready=null;}});
 // ---- 丢丢平板电脑: 仓库, gift, 藏品, 每日操盘
 await ev(()=>FarmUI.computer('gift',springFarm.X.pcState()));await shot('平板-仓库');
 await p.locator('.fu-btn',{hasText:'卖一份'}).first().click();await p.waitForTimeout(300);
 await ev(()=>FarmUI.computer('farm',springFarm.X.pcState()));await shot('平板-农庄总览');
 await ev(()=>{const g=springFarm.X.pcState();g.gifts.tab='keep';FarmUI.computer('gift',g);});await shot('平板-藏品');
 await ev(()=>FarmUI.computer('fund',springFarm.X.pcState()));await p.locator('.fu-step button',{hasText:'+'}).click();await p.locator('.fu-btn',{hasText:'投入'}).click();await shot('平板-每日操盘');
 f=await S();assert.equal(f.fund.held,2);await ev(()=>closeSocialSheet());
 const before=await ev(()=>socialState.contacts.find(c=>c.id==='mom').affinity);
 await ev(()=>{const k=Object.keys(springFarm.state.inv)[0];infeiFarm.give({id:'mom',k});});
 const after=await ev(()=>[socialState.contacts.find(c=>c.id==='mom').affinity,JSON.stringify(springFarm.state.inv),JSON.stringify(springFarm.state.gifts)]);console.log('GIFT',before,after);assert(after[0]>before||before>=100);
 // ---- autumn: summer crops wither at the change, autumn seeds
 await day(27);await ev(()=>{springFarm.state.beds[10]={crop:'tomato',progress:1,watered:-1,at:sim.t,picks:0};});await day(28);
 f=await S();assert(!f.beds[10]);await ev(()=>{seasonMapTest.ctl().go(4,100);springFarm.state.beds={};});await p.waitForTimeout(400);
 await clickAt(40,88);await ring('播种');const autumnSeeds=await ev(()=>[...document.querySelectorAll('#picker .pk-item b')].map(b=>b.textContent));await shot('秋天种子铺');await p.locator('#picker .x').click();
 assert.deepEqual(autumnSeeds,['白菜','玉米','南瓜','萝卜','茄子']);
 // ---- winter: animals in the barn, hay
 await day(43);await ev(()=>seasonMapTest.ctl().go(5,520));await p.waitForTimeout(600);await shot('冬天牧场-都进棚了');
 await clickAt(500,38);await shot('冬天粮仓菜单');await ring('都喂草料');
 assert(await ev(()=>springFarm.state.animals.every(a=>a.fedDay===Math.floor(sim.t/1440))));
 assert.deepEqual(errors,[]);console.log('PASS',n,'shots in',out);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
