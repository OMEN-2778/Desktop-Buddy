const fs=require('fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const W=1920,H=1080;
const ctx=await b.newContext({viewport:{width:W,height:H},recordVideo:{dir:'/tmp/claude-0/promo/raw2',size:{width:W,height:H}}});const p=await ctx.newPage();const T0=Date.now();const now=()=>(Date.now()-T0)/1000;
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('/home/user/Desktop-Buddy/desktop/dist/map-test/index.html')}));
await p.goto('http://season.test/');await p.waitForFunction(()=>typeof booted!=='undefined'&&booted,null,{timeout:60000});
const ev=(f,a)=>p.evaluate(f,a),wait=ms=>p.waitForTimeout(ms);
await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;cardMoment=rollCard=rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e12;weather.force='clear';
 sim.t=Math.floor(sim.t/1440)*1440+40*1440+19*60+30;for(const k in sim.needs)sim.needs[k]=95;setInterval(()=>{for(const k in sim.needs)sim.needs[k]=Math.max(sim.needs[k],85);},400);
 if(sim.place!=='home'){sim.place='home';arriveAt('home');}sim.mode='idle';sim.act=null;});
await wait(2500);
const info=await ev(()=>{const r=document.getElementById('view').getBoundingClientRect();const c=CLICK.tv;return {view:[r.x,r.y,r.width,r.height].map(Math.round),cw:view.width,ch:view.height,tv:c?[c.x,c.y,c.w??c.img?.width,c.h??c.img?.height]:null,hero:here()};});
console.log(JSON.stringify(info));
const s=now();await ev(()=>{command('tv');});await wait(7000);const e=now();
// she watches: a happy moment for the ending
await ev(()=>{addMood?.('fest',{words:false});speak('好想去草帽湾！',true);});await wait(3500);const e2=now();
fs.writeFileSync('/tmp/claude-0/promo/marks2.json',JSON.stringify({info,tv:[s,e],happy:[e,e2]}));console.log(errs.slice(0,3));
await ctx.close();await b.close();})();
