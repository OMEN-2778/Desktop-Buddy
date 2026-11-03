// Hover glow in 茵菲谷 and the airport (game-shell test page): beds, villagers, trees, animals, barn, coop, door,
// furniture, airport board. Saves a crop per target. Usage: node tools/check_infei_hover.js [outDir]
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const out=process.argv[2]||'/tmp/infei-hover';fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});try{
 const p=await b.newPage({viewport:{width:1400,height:1000},reducedMotion:'reduce'}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
 await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.infeiHoverApi&&seasonMapTest.state.spring.state.loaded,null,{timeout:60000});
 const ev=(f,a)=>p.evaluate(f,a);
 await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=3*1440+10*60;socialState.nextCall=socialState.nextVisit=1e12;cardMoment=rollCard=rollEvents=()=>false;weather.force='clear';
  Object.assign(springFarm.state,{letter:1,unlocked:true,phase:'done',coins:100,trees:{0:{kind:'peach',grown:8,cycle:0,ready:true,at:0}}});seasonMapTest.start('spring_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='spring_test'&&!wiping,null,{timeout:20000});
 await ev(()=>{for(const k of ['chicken','sheep','cow'])infeiFarm.buy({kind:k,cost:0});});
 let n=0;
 const hover=async(name,scene,camX,x,y,expect,inside=false)=>{
  await ev(([sc,cx,ins])=>{const c=seasonMapTest.ctl();c.state.inside=ins;if(!ins)c.go(sc,cx);c.state.x=ins?280:(cx<342?20:cx-150);c.state.y=ins?108:103;c.state.target=null;seasonMapTest.state.autoAt=sim.t+1e9;},[scene,camX,inside]);
  await p.waitForTimeout(400);const v=await p.locator('#view').boundingBox(),[h,cam]=await ev(()=>[seasonMapTest.ctl().canvas.height,seasonMapTest.ctl().state.inside?0:seasonMapTest.ctl().state.camera||0]);
  const at=typeof x==='function'?await ev(x):[x,y];
  await p.mouse.move(v.x+(at[0]-cam)/342*v.width,v.y+at[1]/h*v.height);await p.waitForTimeout(300);
  const hv=await ev(()=>{const h=infeiHoverApi.hv;return h?(h.npc?'npc':h.animal?'animal':'img'):null;});
  await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-'+name+'.png'),clip:v});
  console.log(name,hv);assert.equal(hv,expect,name);};
 await hover('菜地',4,171,40,88,'img');
 await hover('小满',1,171,236,90,'npc');
 await hover('桃树',5,300,()=>{const [x,y]=springFarm.X.D.pits[0];return [x,y-15];},null,'img');
 await hover('牛',5,560,()=>{const a=springFarm.state.animals.find(a=>a.kind==='cow');return [a.x,a.y-10];},null,'animal');
 await hover('粮仓',5,560,520,50,'img');
 await hover('鸡',3,171,()=>{const a=springFarm.state.animals.find(a=>a.kind==='chicken');return [a.x,a.y-4];},null,'animal');
 await hover('农舍门',3,171,182,85,'img');
 await hover('空地-无',4,171,200,40,null);
 await hover('屋里-床',3,171,105,35,'img',true);
 await hover('屋里-灶台',3,171,250,90,'img',true);
 // airport board
 await ev(()=>throughDoor('airport_test'));await p.waitForFunction(()=>sim.place==='airport_test'&&!wiping,null,{timeout:30000});await p.waitForTimeout(800);
 const v=await p.locator('#view').boundingBox();await p.mouse.move(v.x+70/342*v.width,v.y+36/118*v.height);await p.waitForTimeout(400);await p.screenshot({path:path.join(out,String(++n).padStart(2,'0')+'-机场航班牌.png'),clip:v});
 assert.deepEqual(errors,[]);console.log('PASS',n);
}finally{await b.close();}})().catch(e=>{console.error(e);process.exit(1);});
