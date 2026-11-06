// 草帽湾 smoke test (before going live, owner 2026-11-06): runs every island feature once on the season test page
// and fails on any page error, a talk that never ends, or a feature that does nothing.
// Build first: PYTHONPATH=tools python3 tools/make_demo.py && PYTHONPATH=tools python3 tools/make_season_game_test.py
//              && (cd desktop && node scripts/copy-web.mjs)
const fs=require('fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1300,height:1000}});const errs=[],fails=[];
p.on('pageerror',e=>{errs.push(e.message);if(errs.length===1)console.log('STACK',e.stack.split('\n').slice(0,6).join(' <- '));});p.on('console',m=>{if(m.type()==='error'||/season auto|bay friend|warn/i.test(m.type()==='warning'?m.text():''))errs.push('console: '+m.text().slice(0,200));});
await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('desktop/dist/map-test/index.html')}));
await p.goto('http://season.test/');await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.summerMore&&seasonMapTest.state.summer.state.loaded,null,{timeout:60000});
const ev=(f,a)=>p.evaluate(f,a),wait=ms=>p.waitForTimeout(ms);
const ok=(name,cond,info='')=>{if(!cond)fails.push(name+(info?' '+info:''));console.log((cond?'ok   ':'FAIL ')+name+(info?' '+info:''));};
// click through any open talk (lines need a click now); choices: the first one
const talkThrough=async(max=40)=>{for(let i=0;i<max;i++){const st=await ev(()=>{const ch=document.querySelector('.story-choices:not([hidden]) button');if(ch){ch.click();return 'choice';}return document.querySelector('.story-speech')?'line':'none';});
 if(st==='none'){await wait(300);if(await ev(()=>!document.querySelector('.story-speech')))return true;}
 if(st==='line'){await wait(380);await p.mouse.click(5,5);}else await wait(250);}return false;};
await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;cardMoment=rollCard=rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e12;weather.force='clear';
 sim.t=Math.floor(sim.t/1440)*1440+10*60;for(const k in sim.needs)sim.needs[k]=90;setInterval(()=>{for(const k in sim.needs)sim.needs[k]=Math.max(sim.needs[k],70);},500);
 seasonMapTest.start('summer_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
await p.waitForFunction(()=>sim.place==='summer_test'&&!wiping,null,{timeout:30000});
await p.waitForFunction(()=>!!document.querySelector('.story-speech'),null,{timeout:20000}).catch(()=>{});   // 阿洛 walks over first
ok('guide intro ends',await talkThrough());
await p.waitForFunction(()=>!summerLife.isBusy()&&!seasonMapTest.state.summer.state.door&&!seasonMapTest.state.summer.state.target,null,{timeout:30000}).catch(()=>{});await wait(1500);   // the guide walks her to the market
ok('阿洛 in 人脉',await ev(()=>socialState.contacts.some(c=>c.id==='bay_alo')));
const C='seasonMapTest.state.summer';
await ev(()=>{seasonMapTest.state.autoAt=sim.t+1e9;});
// ---- market, stall, cafe, vendors
await ev(()=>{const c=seasonMapTest.state.summer;c.state.x=60;c.beginDoor('market');});await wait(2500);
ok('market opens',await ev(()=>seasonMapTest.state.summer.state.market===true));
await talkThrough();
for(const f of ['openStall','openCafe']){const r=await ev(f=>{try{summerLife[f]();return !!document.querySelector('.fu-sheet,[class*=sheet]');}catch(e){return 'err '+e.message;}},f);ok(f,r===true,String(r));await wait(400);await ev(()=>{closeSocialSheet();});await p.keyboard.press('Escape');await wait(300);}
await ev(()=>{seasonMapTest.state.summer.beginDoor('bay');});await wait(2500);
ok('back to the bay',await ev(()=>!seasonMapTest.state.summer.state.market),await ev(()=>{const s=seasonMapTest.state.summer.state;return JSON.stringify({door:s.door,paused:s.paused,sheet:!socialSheet.hidden,speech:!!document.querySelector('.story-speech'),card:!!card,ring:!!ringOf,busy:summerLife.isBusy()});}));
// ---- every quest giver: one talk each, it must end
for(const id of Object.keys(await ev(()=>Object.fromEntries(Object.keys(summerMore.Q).map(k=>[k,1]))))){
 const r=await ev(id=>{try{summerLife.scene(()=>summerMore.talk(id));return true;}catch(e){return 'err '+e.message;}},id);await wait(600);   // as a click does: inside a scene
 const ended=await talkThrough(60);ok('quest talk '+id,r===true&&ended,r===true?'':String(r));
 if(!ended)console.log(id,await ev(()=>{const s=seasonMapTest.state.summer.state;return JSON.stringify({x:Math.round(s.x),t:s.target,door:s.door,market:s.market,busy:summerLife.isBusy(),sp:document.querySelector('.story-speech')?.textContent?.slice(0,60),ch:document.querySelectorAll('.story-choices button').length,hid:document.querySelector('.story-choices')?.hidden});}));
 await ev(()=>{const c=seasonMapTest.state.summer;if(c.state.market)c.beginDoor('bay');c.state.target=null;});await wait(300);}
// ---- the lodge: every piece of furniture
await ev(()=>{const c=seasonMapTest.state.summer;c.state.market=false;c.state.inside=true;c.state.x=150;c.state.y=84;});
for(const id of Object.keys(await ev(()=>Object.fromEntries(Object.keys(summerLodge.SPOTS).map(k=>[k,1]))))){
 await ev(id=>{summerLodge.stop();summerLodge.use(id);},id);let used=false;
 for(let i=0;i<30;i++){await wait(300);used=await ev(id=>{const p=summerLodge.SPOTS[id];return p.look?!seasonMapTest.state.summer.state.target:summerLodge.svc?.id===id||(id==='dine'&&summerLodge.svc?.id==='stove');},id);if(used)break;}
 ok('lodge '+id,used);}
await ev(()=>{summerLodge.stop();seasonMapTest.state.summer.state.inside=false;seasonMapTest.state.summer.state.x=700;});
// ---- swimsuit, floats, surfing, diving, photos, dex
await ev(()=>{const c=seasonMapTest.state.summer;c.state.suit='swim';c.state.x=1400;c.state.y=128;});await wait(500);
await ev(()=>{const f=summerFloat.FLOATS.findIndex((f,i)=>!summerFloat.sitter(i));summerFloat.goFloat(f);});
let sat=false;for(let i=0;i<40;i++){await wait(300);if(await ev(()=>summerFloat.sitting?.on)){sat=true;break;}}ok('sits on a float',sat);
await ev(()=>{summerFloat.stand();const c=seasonMapTest.state.summer;c.state.target=null;c.state.x=1500;c.state.y=128;});await wait(300);
await ev(()=>summerFloat.startSurf());await wait(1500);const x0=await ev(()=>seasonMapTest.state.summer.state.x);await wait(1500);
ok('surfs',await ev(x0=>summerFloat.surfing&&Math.abs(seasonMapTest.state.summer.state.x-x0)>10,x0));
await ev(()=>summerFloat.endSurf());
await ev(()=>{const c=seasonMapTest.state.summer;c.goTo(2600,'dive',260);});await wait(6000);
ok('dives',await ev(()=>summerLife.under()),String(await ev(()=>Math.round(seasonMapTest.state.summer.state.y))));
ok('dex opens',await ev(()=>{try{summerMore.openDex();return true;}catch(e){return e.message;}}));await wait(500);await p.keyboard.press('Escape');await ev(()=>{closeSocialSheet();});
// ---- night, rain, every festival: frames draw without errors
await ev(()=>{const c=seasonMapTest.state.summer;c.state.x=900;c.state.y=c.gr(900);});
for(const h of [5,12,19,23]){await ev(h=>{sim.t=Math.floor(sim.t/1440)*1440+h*60;},h);await wait(600);}
await ev(()=>{weather.force='rain';});await wait(800);await ev(()=>{weather.force='clear';});
const fests=await ev(()=>{const out=[],t0=sim.t;for(let d=0;d<4*30*2&&out.length<summerMore.FESTS.length;d++){sim.t=t0+d*1440;const f=summerMore.fest();if(f&&!out.some(o=>o[0]===f.n))out.push([f.n,sim.t]);}sim.t=t0;return out;});
for(const [n,t] of fests){await ev(t=>{sim.t=t+12*60;},t);await wait(700);}
ok('festivals found',fests.length===await ev(()=>summerMore.FESTS.length),fests.map(f=>f[0]).join(','));
// ---- every bay chance card: shows, answers both ways
const cards=await ev(()=>CARDS.filter(c=>c.at==='summer_test').map(c=>c.n));let cardErr=0;
for(const n of cards)for(const k of ['a','b']){const r=await ev(([n,k])=>{try{const cd=CARDS.find(c=>c.n===n);showCard(cd);chooseCard(k,true);return true;}catch(e){return e.message;}},[n,k]);await wait(460);if(r!==true){cardErr++;if(cardErr<4)console.log('card',n,k,r);}}
await ev(()=>{try{hideCard?.();}catch(e){}cardEl.hidden=true;card=null;dimHouse(false);});
ok('bay cards '+cards.length,cardErr===0,cardErr?cardErr+' errors':'');
// ---- the way home
await ev(()=>{openRing('away','buddy');ringPick('bay:leave');});
let home=false;for(let i=0;i<60;i++){await wait(300);if(await ev(()=>sim.place==='home'&&!airportTravel.flight.busy)){home=true;break;}}ok('离开草帽湾 → home',home);
ok('no page errors',!errs.length,errs.slice(0,6).join(' | '));
await b.close();
console.log(fails.length?`FAIL ${fails.length}: ${fails.join('; ')}`:'PASS 草帽湾 smoke');process.exit(fails.length?1:0);})();
