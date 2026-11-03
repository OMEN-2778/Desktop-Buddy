// 茵菲谷 side quests on the game-shell test page: plays all four through real clicks and dialogue,
// screenshots the first line of each scene and every choice. Usage: node tools/check_infei_quests.js [outDir]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/infei-quests';fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});let n=0;try{
 const p=await b.newPage({viewport:{width:1400,height:1000},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error('PAGE:',e.message);});
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.infeiQuests&&seasonMapTest.state.spring.state.loaded,null,{timeout:60000});
 const ev=(f,a)=>p.evaluate(f,a);
 const shot=async name=>{await p.waitForTimeout(250);const v=await p.locator('#view').boundingBox();await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-'+name+'.png'),clip:{x:v.x-10,y:Math.max(0,v.y-150),width:v.width+20,height:v.height+170}});};
 const clickAt=async(x,y)=>{const v=await p.locator('#view').boundingBox(),[h,cam]=await ev(()=>[seasonMapTest.ctl().canvas.height,seasonMapTest.ctl().state.camera||0]);await p.mouse.click(v.x+(x-cam)/342*v.width,v.y+y/h*v.height);await p.waitForTimeout(300);};
 // plays a whole scene: clicks through lines, picks `pick` at each choice, screenshots the first line and choices
 const play=async(name,pick=[0])=>{let k=0,first=true;await p.waitForFunction(()=>infeiQuests.busy,null,{timeout:20000});
  while(await ev(()=>infeiQuests.busy)){
   if(await p.locator('.story-choices:not([hidden]) button').count()){await shot(name+'-选项');await p.locator('.story-choices button').nth(pick[Math.min(k++,pick.length-1)]).click();}
   else if(await p.locator('.story-bubble').count()){if(first){await shot(name);first=false;}await p.locator('.story-bubble').first().click();}
   await p.waitForTimeout(120);}};
 const at=(scene,x,h)=>ev(([sc,x,h])=>{sim.t=Math.floor(sim.t/1440)*1440+h*60;const c=seasonMapTest.ctl();c.go(sc,x);seasonMapTest.state.autoAt=sim.t+1e9;},[scene,x,h]);
 const nextDay=()=>ev(()=>{sim.t=(Math.floor(sim.t/1440)+1)*1440+10*60;springFarm.roll();});
 await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=3*1440+10*60;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;weather.force='clear';
  setInterval(()=>{for(const k in sim.needs)sim.needs[k]=Math.max(sim.needs[k],80);},500);
  Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done',coins:20,inv:{carrot:2,cabbage:1,potato:1,strawberry:1}});seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 // ---- 风车里的怪声
 await at(1,150,10);await shot('小满头上有感叹号');await clickAt(236,90);await play('风车-小满开口',[0]);
 await at(2,180,11);await clickAt(230,50);await play('风车-白天很安静');
 await at(2,180,21);await shot('夜里风车边的王叔');await clickAt(230,50);await play('风车-王叔',[1]);
 await at(1,150,10);await clickAt(236,90);await play('风车-告诉小满');assert.equal(await ev(()=>infeiQuests.Q().mill.step),9);
 // ---- 溪边的阿婆
 await at(0,120,15);await shot('溪边的阿婆');await clickAt(178,90);await play('阿婆-念信',[1]);
 await clickAt(178,90);await play('阿婆-送菜',[0,1]);assert.equal(await ev(()=>springFarm.state.inv.cabbage||0),0);
 await nextDay();await at(0,120,15);await clickAt(178,90);await play('阿婆-回信',[1]);assert.equal(await ev(()=>infeiQuests.Q().letter.step),9);
 // ---- 老周的乱炖
 await at(2,60,10);await clickAt(112,90);await play('老周-新菜',[1]);
 for(let i=0;i<3;i++){await clickAt(112,90);await play('老周-送菜'+(i+1),[0,0]);}
 assert.equal(await ev(()=>infeiQuests.Q().stew.step),2);const c0=await ev(()=>springFarm.state.coins);
 await nextDay();await at(2,60,10);await clickAt(112,90);await play('老周-尝乱炖',[0]);assert((await ev(()=>springFarm.state.coins))>c0);
 // ---- 菜地里的脚印 (needs a growing bed; starts by itself on the farm in the morning)
 await ev(()=>{springFarm.state.beds[9]={crop:'carrot',progress:1,watered:-1,at:sim.t,picks:0};});await at(4,150,8);await play('脚印-菜叶被啃');
 await at(0,160,10);await shot('小溪边的问号');await clickAt(95,90);await play('脚印-红头绳');
 await at(1,150,10);await clickAt(236,90);await play('脚印-问小满',[0]);
 await at(4,150,21);await play('脚印-夜里蹲守',[0]);assert.equal(await ev(()=>infeiQuests.Q().prints.rabbit),'farm');
 await nextDay();await at(3,120,10);await shot('兔子住在鸡窝边');
 await ev(()=>infeiQuests.list());await shot('支线任务列表');
 // replay: a finished quest opens its story — lines, choices, letters
 await p.locator('.qb-card',{hasText:'溪边的阿婆'}).click();await p.waitForTimeout(900);
 const pv=await p.locator('#questPanel').boundingBox();await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-任务回顾-阿婆.png'),clip:pv});
 const rv=await ev(()=>({ents:document.querySelectorAll('.qb-ent').length,letters:[...document.querySelectorAll('.qb-letter')].map(l=>l.textContent),picks:document.querySelectorAll('.qb-pick').length,says:document.querySelectorAll('.qb-say').length}));console.log(rv);
 assert(rv.letters.length===2&&rv.picks>=2&&rv.says>20);
 await p.locator('.qb-tl').evaluate(e=>e.scrollTop=e.scrollHeight);await p.waitForTimeout(300);await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-任务回顾-阿婆-下半.png'),clip:pv});
 await p.locator('.qb-back').click();await p.waitForTimeout(400);assert(!(await ev(()=>questBoard.panel.classList.contains('detail'))));
 await p.locator('.qb-card',{hasText:'菜地里的脚印'}).click();await p.waitForTimeout(900);await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-任务回顾-脚印.png'),clip:pv});
 assert.deepEqual(errors,[]);console.log('PASS',n,'shots in',out);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
