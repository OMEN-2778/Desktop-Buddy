// 茵菲谷: the six extra side quests (infei_side.js), played through real clicks. Usage: node tools/check_infei_side.js [outDir]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/infei-side';fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});let n=0;try{
 const p=await b.newPage({viewport:{width:1400,height:1000},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>{errors.push(e.message);console.error('PAGE:',e.message);});p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE:',m.text());});await p.addInitScript(()=>addEventListener('unhandledrejection',e=>console.error('REJ',e.reason&&e.reason.stack||e.reason)));
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.infeiQuests&&seasonMapTest.state.spring.state.loaded,null,{timeout:60000});
 const ev=(f,a)=>p.evaluate(f,a);
 const shot=async name=>{await p.waitForTimeout(250);const v=await p.locator('#view').boundingBox();await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-'+name+'.png'),clip:{x:v.x-10,y:Math.max(0,v.y-150),width:v.width+20,height:v.height+170}});};
 const clickAt=async(x,y)=>{const v=await p.locator('#view').boundingBox(),[h,cam]=await ev(()=>[seasonMapTest.ctl().canvas.height,seasonMapTest.ctl().state.camera||0]);await p.mouse.click(v.x+(x-cam)/342*v.width,v.y+y/h*v.height);await p.waitForTimeout(300);};
 // plays a whole scene: clicks through lines, picks `pick` at each choice, screenshots the first line and choices
 const play=async(name,pick=[0])=>{let k=0,first=true,t0=Date.now();await p.waitForFunction(()=>infeiQuests.busy,null,{timeout:20000});
  while(await ev(()=>infeiQuests.busy)){
   if(await p.locator('.story-choices:not([hidden]) button').count()){await shot(name+'-选项');await p.locator('.story-choices button').nth(pick[Math.min(k++,pick.length-1)]).click();}
   else if(await p.locator('.story-bubble').count()){if(first){await shot(name);first=false;}await p.locator('.story-bubble').first().click();}
   if(Date.now()-t0>120000){console.log('STUCK',name,JSON.stringify(await ev(()=>[document.querySelector('.story-choices')?.outerHTML.slice(0,300),[...document.querySelectorAll('.story-bubble')].map(e=>e.id+':'+e.hidden+':'+e.textContent.slice(0,30)),seasonMapTest.ctl().state.target])));process.exit(2);}
   await p.waitForTimeout(120);}};
 const at=(scene,x,h)=>ev(([sc,x,h])=>{sim.t=Math.floor(sim.t/1440)*1440+h*60;const c=seasonMapTest.ctl();c.go(sc,x);seasonMapTest.state.autoAt=sim.t+1e9;},[scene,x,h]);
 const nextDay=()=>ev(()=>{sim.t=(Math.floor(sim.t/1440)+1)*1440+10*60;springFarm.roll();});
 await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=3*1440+10*60;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;weather.force='clear';
  setInterval(()=>{for(const k in sim.needs)sim.needs[k]=Math.max(sim.needs[k],80);},500);
  Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done',coins:20,inv:{carrot:2,cabbage:1,potato:1,strawberry:1}});seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 const Qs=()=>ev(()=>Object.fromEntries(Object.entries(infeiQuests.Q()).map(([k,v])=>[k,v.step])));
 // the next day (from now) at hour h on which `key` is out (or the dog is at the door)
 const findDay=async(key,h,dog)=>{for(let i=0;i<30;i++){const ok=await ev(([k,h,dog])=>{sim.t=Math.floor(sim.t/1440)*1440+h*60;return dog?infeiQuests.goals().some(g=>g.spot==='dog'):!!infeiQuests.at(infeiQuests.V[k]);},[key,h,dog]);if(ok)return;await nextDay();}throw new Error('never out: '+key);};
 const go=async(sc,x,h)=>{await at(sc,x>171?x-60:x+60,h);};
 // ---- 小吴的包裹 → 林老师
 await findDay('wu',10);await go(2,175,10);await shot('小吴');await clickAt(175,90);await play('包裹-小吴',[1]);
 assert.equal((await Qs()).parcel,1);
 await go(0,285,10);await clickAt(285,90);await play('包裹-林老师');assert.equal((await Qs()).parcel,9);
 // ---- 林老师的速写
 await findDay('lin',10);await go(0,285,10);await clickAt(285,90);await play('速写-别动',[0]);
 await clickAt(285,90);await play('速写-还没画完');assert.equal((await Qs()).sketch,1);
 await nextDay();await go(0,285,10);await clickAt(285,90);await play('速写-看画',[1]);assert.equal((await Qs()).sketch,9);
 // ---- 老蔡的蜂
 await findDay('cai',10);await go(1,95,10);await clickAt(95,90);await play('蜂-老蔡',[1]);
 await at(5,100,10);await shot('果园里的蜂');await clickAt(100,40);await play('蜂-果园');
 await go(1,95,10);await clickAt(95,90);await play('蜂-蜂蜜');assert.equal((await Qs()).bees,9);
 // ---- 门口的小狗 → 小吴
 await findDay(null,10,true);await go(3,262,10);await shot('门口的小狗');await clickAt(266,95);await play('小狗',[0,0]);
 assert.equal((await Qs()).dog,1);
 await at(2,115,10);await clickAt(175,90);await play('小狗-问小吴');assert.equal((await Qs()).dog,9);
 // ---- 刘婶借菜
 await findDay('liu',10);await go(4,296,10);await shot('刘婶');await clickAt(296,90);await play('借菜',[0]);
 assert.equal((await Qs()).borrow,1);await nextDay();await go(4,296,10);await clickAt(296,90);await play('饺子',[0]);assert.equal((await Qs()).borrow,9);
 // ---- 阿木的口琴
 await findDay('amu',10);await go(5,290,10);await shot('阿木');await clickAt(290,92);await play('口琴-阿木',[1]);
 await at(5,150,10);await clickAt(214,92);await play('口琴-草里');
 await go(5,290,10);await clickAt(290,92);await play('口琴-还',[0]);assert.equal((await Qs()).harp,9);
 // the panel lists them all
 await ev(()=>questBoard.open());await p.waitForTimeout(600);const pv=await p.locator('#view').boundingBox();
 await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-任务面板.png'),clip:{x:pv.x,y:Math.max(0,pv.y-150),width:pv.width,height:pv.height+170}});
 for(const t of ['小吴的包裹','林老师的速写','老蔡的蜂','门口的小狗','刘婶借菜','阿木的口琴'])assert(await p.locator('.qb-card',{hasText:t}).count(),t);
 assert.deepEqual(errors,[]);console.log('PASS',n,'shots in',out);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
