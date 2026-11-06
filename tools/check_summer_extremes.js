// 草帽湾 extreme cases (owner 2026-11-06): autumn turning to winter wherever she is on the island (beach, deep sea,
// surfing, on a float, asleep in the lodge, in the market, mid-card), a winter save, the airport in winter, passing
// out / an accident under water, reloading in odd places, and a long fast-forward. Fails on page errors or a stuck state.
// Build first (see check_summer_smoke.js).
const fs=require('fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1100,height:900}});const p=await ctx.newPage();const errs=[],fails=[];
p.on('pageerror',e=>errs.push(e.message.slice(0,160)));
await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));
const ev=(f,a)=>p.evaluate(f,a),wait=ms=>p.waitForTimeout(ms);
const ok=(name,cond,info='')=>{if(!cond)fails.push(name);console.log((cond?'ok   ':'FAIL ')+name+(info?' — '+info:''));};
const boot=async()=>{await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.summerFloat&&seasonMapTest.state.summer.state.loaded,null,{timeout:60000});
 await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;cardMoment=rollCard=rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e12;weather.force='clear';window.__noBayGuide=true;
  if(!window.__keep){window.__keep=setInterval(()=>{if(!window.__lowNeeds)for(const k in sim.needs)sim.needs[k]=Math.max(sim.needs[k],70);},400);}});};
await p.goto('http://season.test/');await boot();
const YEAR=await ev(()=>4*SEASON_DAYS*1440);
const autumnEnd=await ev(()=>4*SEASON_DAYS*1440+(3*SEASON_DAYS)*1440-2);   // 2 game minutes before winter, year 2
const enter=async()=>{await ev(()=>{window.__home=0;if(sim.place!=='home'){sim.place='home';arriveAt('home');}sim.t=4*SEASON_DAYS*1440+SEASON_DAYS*1440+10*60;seasonMapTest.start('summer_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
 await p.waitForFunction(()=>sim.place==='summer_test'&&!wiping&&!airportTravel.flight.busy,null,{timeout:40000});await ev(()=>{summerLife.B().met=true;seasonMapTest.state.autoAt=sim.t+1e9;});await wait(600);};
const goneHome=async(max=60)=>{for(let i=0;i<max;i++){await wait(500);if(await ev(()=>window.__home&&!airportTravel.flight.busy&&!wiping))return true;}return false;};
const said=()=>ev(()=>[...document.querySelectorAll('#say span,.say span,#popSay span')].map(e=>e.textContent).join('|')+' '+(window.__lastSay||''));
const hookSay=()=>ev(()=>{if(window.__hooked)return;window.__hooked=1;const oa=arriveAt;arriveAt=function(pl){if(pl==='home')window.__home=1;return oa.apply(this,arguments);};const o=speak;speak=function(w){window.__lastSay=w;return o.apply(this,arguments);};const o2=summerLife.speakBay;if(o2)summerLife.speakBay=function(w){window.__lastSay=w;return o2.apply(this,arguments);};});await hookSay();
const winterFrom=async(name,setup,after)=>{await enter();await ev(setup);await wait(1500);
 await ev(t=>{sim.t=t;window.__lastSay='';},autumnEnd);
 if(after){await wait(4000);ok('waits while '+name,await ev(()=>sim.place==='summer_test'));await ev(after);}
 const home=await goneHome(50);const line=await ev(()=>/航班|飞机/.test(window.__lastSay||''));
 ok('winter → home from '+name,home&&line,await ev(()=>sim.place+' '+(window.__lastSay||'')));};
await winterFrom('the beach',()=>{const c=seasonMapTest.state.summer;c.state.x=700;c.state.y=c.gr(700);});
await winterFrom('deep sea',()=>{const c=seasonMapTest.state.summer;c.state.suit='swim';c.state.x=3000;c.state.y=340;});
await winterFrom('surfing',()=>{const c=seasonMapTest.state.summer;c.state.suit='swim';c.state.x=1500;c.state.y=128;summerFloat.startSurf();});
await winterFrom('a float',()=>{const c=seasonMapTest.state.summer;c.state.suit='swim';c.state.x=1520;c.state.y=128;const i=summerFloat.FLOATS.findIndex((f,i)=>!summerFloat.sitter(i));summerFloat.goFloat(i);});
await winterFrom('asleep in the lodge',async()=>{const c=seasonMapTest.state.summer;c.state.inside=true;c.state.x=150;c.state.y=84;summerLodge.use('bed');await new Promise(r=>setTimeout(r,3500));});
await winterFrom('the market',()=>{const c=seasonMapTest.state.summer;c.state.x=60;c.beginDoor('market');});
await winterFrom('a chance card',()=>{const c=seasonMapTest.state.summer;c.state.x=700;c.state.y=c.gr(700);showCard(CARDS.find(c=>c.at==='summer_test'));},()=>{chooseCard('a',true);});
// a save made in autumn on the island, opened in winter
await enter();await ev(t=>{const c=seasonMapTest.state.summer;c.state.x=700;c.state.y=c.gr(700);sim.t=t-600;const s=snapshot();s.sim.t=t+600;localStorage.setItem('season-test-buddy-save',JSON.stringify(s));localStorage.setItem('buddy-save',JSON.stringify(s));},autumnEnd);
await p.reload();await boot();await hookSay();await wait(6000);ok('test toolbar / a save in winter: stays (only a season ending sends her)',await ev(()=>sim.place==='summer_test'),await ev(()=>sim.place));
await ev(()=>{sim.place='home';arriveAt('home');});
// the airport in winter: no flight to 草帽湾
await ev(t=>{sim.t=t+3000;},autumnEnd);
const blocked=await ev(()=>{const was=sim.place;try{ringPick('airport:summer');}catch(e){return 'err '+e.message;}return sim.dest!=='summer_test'&&!airportTravel.flight.busy;});
ok('no 草帽湾 flight in winter',blocked===true,String(blocked));
// passing out under water, then woken by the player: she carries on
await enter();await ev(()=>{window.__lowNeeds=true;const c=seasonMapTest.state.summer;c.state.suit='swim';c.state.x=2600;c.state.y=300;sim.needs.energy=0;});await wait(4000);
const down=await ev(()=>sim.mode);await ev(()=>{if(sim.mode==='down'){sim.mode='idle';sim.down=null;}for(const k in sim.needs)sim.needs[k]=60;window.__lowNeeds=false;});await wait(3000);
ok('passes out under water and comes round',['down','act','idle'].includes(down)&&await ev(()=>sim.place==='summer_test'),down);
// an accident under water: a shower in the lodge, not home
await ev(()=>{window.__lowNeeds=true;const c=seasonMapTest.state.summer;c.state.x=2400;c.state.y=260;sim.needs.bladder=0;});
let showered=false;for(let i=0;i<90;i++){await wait(500);const r=await ev(()=>[sim.place,summerLodge.svc?.id,sim.act]);if(r[0]!=='summer_test')break;if(r[1]==='shower'||r[2]==='season_shower'){showered=true;break;}}
await ev(()=>{window.__lowNeeds=false;for(const k in sim.needs)sim.needs[k]=80;});
ok('accident under water → lodge shower',showered,await ev(()=>sim.place+' '+sim.act+' '+Math.round(seasonMapTest.state.summer.state.x)));
// reloading in odd places (the island in summer): comes back on the island, no errors
for(const [name,setup] of [['surfing',()=>{const c=seasonMapTest.state.summer;c.state.inside=false;c.state.suit='swim';c.state.x=1500;c.state.y=128;summerFloat.startSurf();}],
 ['deep sea',()=>{const c=seasonMapTest.state.summer;summerFloat.endSurf();c.state.suit='swim';c.state.x=3200;c.state.y=360;}],
 ['the lodge',()=>{const c=seasonMapTest.state.summer;c.state.inside=true;c.state.x=150;c.state.y=84;summerLodge.use('sofa');}]]){
 if(await ev(()=>sim.place!=='summer_test'))await enter();await ev(setup);await wait(2500);
 await ev(()=>{localStorage.setItem('season-test-buddy-save',JSON.stringify(snapshot()));});await p.reload();await boot();await hookSay();await wait(2500);
 ok('reload while '+name,await ev(()=>sim.place==='summer_test'||sim.place==='home'),await ev(()=>sim.place+' '+sim.mode+' '+sim.act));}
// a long fast-forward in summer: her own life for a few days, never leaves
if(await ev(()=>sim.place!=='summer_test'))await enter();
await ev(()=>{seasonMapTest.state.autoAt=sim.t;window.__lowNeeds=true;speed=30;});
let left=false;for(let i=0;i<60;i++){await wait(1000);if(await ev(()=>sim.place!=='summer_test'&&[1,2].includes(seasonOf(sim.t).i))){left=true;break;}}
ok('3 game days at 30x: stays on the island',!left,await ev(()=>sim.place+' day '+seasonOf(sim.t).day+' '+sim.act));
await ev(()=>{speed=1;window.__lowNeeds=false;});
ok('no page errors',!errs.length,[...new Set(errs)].slice(0,5).join(' | '));
await b.close();console.log(fails.length?`FAIL ${fails.length}: ${fails.join('; ')}`:'PASS 草帽湾 extremes');process.exit(fails.length?1:0);})();
