// Airport hall: click floor to walk, click Buddy for 选择航班/回家, board opens flights, 回家 walks out. Usage: node tools/check_airport_walk.js <outDir>
const fs=require('fs'),{chromium}=require('playwright');const T=process.argv[2];
(async()=>{const b=await chromium.launch({args:['--no-sandbox']});const p=await b.newPage({viewport:{width:1400,height:1000}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));await p.goto('http://season.test/');
await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.airportTravel&&seasonMapTest.state.spring.state.loaded);
await p.evaluate(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;prefs.scale=50;fit();speed=1;sim.t=600;cardMoment=rollCard=rollEvents=()=>false;sim.dest='airport_test';command('go_out');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
await p.waitForFunction(()=>sim.place==='airport_test'&&!wiping,null,{timeout:20000});await p.waitForTimeout(3000);
const v=await p.locator('#view').boundingBox(),at=(x,y)=>p.mouse.click(v.x+x/342*v.width,v.y+y/118*v.height);
const x0=await p.evaluate(()=>airportTravel.hero.x);await at(260,100);await p.waitForTimeout(4000);const x1=await p.evaluate(()=>airportTravel.hero.x);console.log('walk',x0,'->',x1);
await at(x1,92);await p.waitForTimeout(400);await p.screenshot({path:T+'/air-ring.png',clip:{x:v.x-10,y:v.y-60,width:v.width+20,height:v.height+70}});
console.log('ring',await p.evaluate(()=>[...document.querySelectorAll('#ring button')].map(b=>b.textContent)));
await at(70,35);await p.waitForTimeout(8000);console.log('board->',await p.evaluate(()=>ringOf));await p.evaluate(()=>closeRing());await p.waitForTimeout(600);
await at(await p.evaluate(()=>airportTravel.hero.x),92);await p.waitForTimeout(300);console.log(await p.evaluate(([px,py])=>({el:document.elementFromPoint(px,py)?.outerHTML.slice(0,120),ringOf,hidden:ringEl.hidden,hx:airportTravel.hero.x,html:1}),[v.x+110/342*v.width,v.y+92/118*v.height]));await p.locator('#ring button',{hasText:'回家'}).click({timeout:3000});
await p.waitForFunction(()=>sim.place==='home'&&!wiping,null,{timeout:30000});console.log('home ok; errors',errs);await b.close();})().catch(e=>{console.error(e.message);process.exit(1)});
