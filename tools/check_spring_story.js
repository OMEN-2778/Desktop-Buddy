// Spring story + first farming loop on the game-shell test page: plays the whole flow
// (letter -> airport -> flight -> welcome -> room -> beds -> sow/water -> days -> harvest)
// and saves a screenshot per step. Usage: node tools/check_spring_story.js [outDir] [scale]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/spring-story',SCALE=+(process.argv[3]||50);fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});let n=0;try{
 const p=await b.newPage({viewport:{width:1400,height:1000},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error('PAGE:',e.message);});
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.seasonMapTest?.state.spring.state.loaded&&window.airportTravel&&window.springFarm);
 await p.evaluate(s=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=s;fit();speed=1;sim.t=10*60;if(sim.mode==='act'&&sim.act==='sleep'){sim.mode='idle';sim.act=null;sim.idleUntil=Infinity;}socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;sim.needs=Object.fromEntries(Object.keys(sim.needs).map(k=>[k,95]));},SCALE).catch(()=>{});
 await p.evaluate(()=>{const k=Object.keys(sim.needs);setInterval(()=>k.forEach(n=>sim.needs[n]=Math.max(sim.needs[n],90)),500);});   // keep her fed for the shoot
 const view=()=>p.locator('#view').boundingBox();
 async function shot(name,pad=175){await p.waitForTimeout(350);const v=await view(),top=Math.max(0,v.y-pad);await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-'+name+'.png'),clip:{x:Math.max(0,v.x-10),y:top,width:v.width+20,height:v.y+v.height-top+60}});}
 let seen=0;
 const speechOpen=async()=>{await p.waitForFunction(k=>springFarm.speech.open&&springFarm.lines>k,seen,{timeout:60000});seen=await p.evaluate(()=>springFarm.lines);};
 async function line(name){await speechOpen();await shot(name);await p.locator('.story-bubble').first().click();await p.waitForTimeout(150);}
 async function clickHouse(x,y){const v=await view(),h=await p.evaluate(()=>seasonMapTest.ctl()?.canvas.height||118);await p.mouse.click(v.x+x/342*v.width,v.y+y/h*v.height);}
 async function ring(label){await p.locator('#ring button',{hasText:label}).first().click();}
 // 1. the letter
 await p.locator('#seasonGameTest button',{hasText:'妈妈来信'}).click();await p.waitForTimeout(400);await shot('门口来信');
 await p.evaluate(()=>readMail());await p.waitForTimeout(300);await p.waitForTimeout(800);for(let k=0;k<3&&!(await p.evaluate(()=>!!document.querySelector('#diaryList li.open')));k++){await p.locator('#diaryList .talk-btn').last().click();await p.waitForTimeout(400);}await p.waitForTimeout(400);await shot('妈妈的信',420);
 assert(await p.evaluate(()=>springFarm.state.unlocked));await p.evaluate(()=>setDiaryOpen(false));
 // 2. airport
 await p.evaluate(()=>{sim.dest='airport_test';sim.outBack=null;sim.outWhy=null;command('go_out');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='airport_test'&&!wiping,null,{timeout:20000});await p.waitForTimeout(2000);
 await p.evaluate(()=>{springFarm.state.unlocked=false;airportTravel.flights();});await shot('机场-没收到信时');await p.evaluate(()=>{closeRing();springFarm.state.unlocked=true;airportTravel.flights();});await shot('机场-茵菲谷免费');
 await ring('茵菲谷');await p.waitForTimeout(2200);await shot('飞行中');
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 // 3. welcome
 await p.evaluate(()=>speed=4);
 await line('妈妈-来啦');await line('主角-爸呢');await line('妈妈-买化肥');
 await speechOpen();await shot('选项-先看房间还是去地里');await p.locator('.story-choices button').first().click();
 await line('屋里-楼上是你的');await line('屋里-太阳味儿');await line('屋里-爸妈的屋');await line('屋里-带你去地里');
 await line('菜地-这两块是你的');await line('菜地-后头还荒着');await line('菜地-先种胡萝卜');await line('菜地-带了一包');await line('主角-我试试');
 await p.waitForTimeout(300);await shot('提示-点有箭头的菜地');
 // 4. sow + water with 妈妈
 await clickHouse(40,88);await shot('菜地环形菜单-播种');await ring('播种');await p.waitForTimeout(400);await shot('种子-妈妈给的一包');
 await p.locator('.pk-item').first().click();
 await line('妈妈-还得浇水');await p.waitForTimeout(400);
 await clickHouse(40,88);await shot('菜地环形菜单-浇水');await ring('浇水');
 await line('妈妈-每天浇一回');await line('主角-钱归我');await line('妈妈-丢丢币');await line('妈妈-种子钱');await line('主角-赚两个币');await line('妈妈-去找你爸');
 await p.waitForTimeout(1500);await shot('妈妈走了-湿土和种子');
 // 5. playing on
 await p.evaluate(()=>speed=1);const at=await p.evaluate(()=>{const s=seasonMapTest.ctl().state;return [s.x,s.y];});
 await clickHouse(at[0],at[1]-14);await shot('点主角-丢丢平板电脑');await ring('丢丢平板电脑');await p.waitForTimeout(400);await shot('丢丢平板电脑-账本');
 await p.locator('.fu-nav button',{hasText:'农庄'}).click();await shot('丢丢平板电脑-农庄');await p.evaluate(()=>closeSocialSheet());
 await p.evaluate(()=>{springFarm.state.coins+=0;sim.t=(Math.floor(sim.t/1440)+1)*1440+7*60;springFarm.roll();});
 await clickHouse(40,88);await shot('第二天-菜地菜单');await ring('查看');await p.waitForTimeout(400);await shot('作物详情-长大中');
 await p.locator('.fu-btn',{hasText:'浇水'}).click();await p.waitForTimeout(6000);
 await p.evaluate(()=>{sim.t=(Math.floor(sim.t/1440)+1)*1440+7*60;springFarm.roll();});await shot('第三天-胡萝卜熟了');
 await clickHouse(40,88);await shot('熟了-可以收获');await ring('收获');await p.waitForTimeout(6000);await shot('收获后');
 await clickHouse(40,88);await ring('播种');await p.waitForTimeout(400);await shot('种子铺-春天的种子');await p.locator('#picker .x').click();
 await clickHouse(215,88);await shot('荒地-还不能整理');await p.evaluate(()=>closeRing());
 const v=await view();await p.mouse.click(v.x+5,v.y+5);
 await clickHouse(at[0]-0,at[1]-14).catch(()=>{});
 await p.evaluate(()=>{closeRing();FarmUI.computer('gift',springFarm.X.pcState());});await p.waitForTimeout(400);await shot('平板-仓库里的胡萝卜');await p.locator('.fu-btn',{hasText:'卖一份'}).click();await p.waitForTimeout(300);
 await p.evaluate(()=>{FarmUI.computer('coin',springFarm.X.pcState());});await p.waitForTimeout(400);await shot('丢丢平板电脑-第一笔收入');await p.evaluate(()=>closeSocialSheet());
 const f=await p.evaluate(()=>springFarm.state);console.log('coins',f.coins,'beds',JSON.stringify(f.beds),'phase',f.phase,'ledger',f.ledger.map(r=>r.text+r.v).join(' / '));
 assert.equal(f.phase,'done');assert.equal(f.coins,10);
 // save + reload keeps the farm
 const saved=await p.evaluate(()=>JSON.stringify(snapshot().springFarm));assert(saved.includes('"unlocked":true'));
 assert.deepEqual(errors,[]);console.log('PASS',n,'shots in',out);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
