// records one long video of 草帽湾 scenes; prints [name,start,end,rect] markers (seconds since page creation)
const fs=require('fs'),{chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const W=1920,H=1080;
const ctx=await b.newContext({viewport:{width:W,height:H},recordVideo:{dir:'/tmp/claude-0/promo/raw',size:{width:W,height:H}}});const p=await ctx.newPage();const T0=Date.now();const now=()=>(Date.now()-T0)/1000;
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.route('http://season.test/',r=>r.fulfill({contentType:'text/html; charset=utf-8',body:fs.readFileSync('/home/user/Desktop-Buddy/desktop/dist/map-test/index.html')}));
await p.goto('http://season.test/');await p.waitForFunction(()=>typeof booted!=='undefined'&&booted&&window.summerMore&&seasonMapTest.state.summer.state.loaded,null,{timeout:60000});
const ev=(f,a)=>p.evaluate(f,a),wait=ms=>p.waitForTimeout(ms);const marks=[];
const view=()=>ev(()=>{const r=document.getElementById('view').getBoundingClientRect();return [r.x,r.y,r.width,r.height].map(Math.round);});
const full=()=>ev(()=>{const a=document.getElementById('view').getBoundingClientRect(),d=(document.getElementById('diaryBox')||document.querySelector('.diary')).getBoundingClientRect();const y=Math.min(a.y,d.y)-10;return [Math.round(a.x-20),Math.round(y),Math.round(a.width+40),Math.round(a.bottom-y+12)];});
const shot=async(name,ms,rect)=>{const r=rect||await view();const s=now();await wait(ms);marks.push([name,s,now(),r]);};
const toMarket=async()=>{for(let i=0;i<6;i++){if(await ev(()=>seasonMapTest.state.summer.state.market))return;await ev(()=>{const c=seasonMapTest.state.summer;if(!c.state.door){c.state.target=null;c.state.x=60;c.state.y=c.gr(60);c.beginDoor('market');}});await wait(1800);await talk();}};
const talk=async()=>{for(let i=0;i<30;i++){const s=await ev(()=>{const ch=document.querySelector('.story-choices:not([hidden]) button');if(ch){ch.click();return 1;}return document.querySelector('.story-speech')?1:0;});if(!s)break;await p.mouse.click(5,5);await wait(350);}};
await ev(()=>{closeGuide();prefs.guided=true;prefs.autosave=false;cardMoment=rollCard=rollEvents=()=>false;socialState.nextCall=socialState.nextVisit=1e12;weather.force='clear';window.__noBayGuide=true;
 sim.t=Math.floor(sim.t/1440)*1440+40*1440+10*60;for(const k in sim.needs)sim.needs[k]=95;setInterval(()=>{for(const k in sim.needs)sim.needs[k]=Math.max(sim.needs[k],85);},400);
 seasonMapTest.start('summer_test');sim.windup=null;startAct('go_out');sim.s=sim.target;arrive();});
await p.waitForFunction(()=>sim.place==='summer_test'&&!wiping,null,{timeout:40000});await wait(1500);await talk();
await ev(()=>{summerLife.B().met=true;seasonMapTest.state.autoAt=sim.t+1e9;});
console.log('view',await view());
const C='seasonMapTest.state.summer';
// 1 beach walk past the lodge and palms
await ev(()=>{const c=seasonMapTest.state.summer;c.state.x=250;c.state.y=c.gr(250);c.goTo(900);});await shot('beach',6000);
// 2 surf
await ev(()=>{const c=seasonMapTest.state.summer;c.state.target=null;c.state.suit='swim';c.state.x=1450;c.state.y=128;summerFloat.startSurf();});await wait(800);await shot('surf',5500);await ev(()=>summerFloat.endSurf());
// 3 float
await ev(()=>{const c=seasonMapTest.state.summer;c.state.target=null;c.state.x=1500;c.state.y=128;let f=summerFloat.FLOATS.findIndex((f,i)=>!summerFloat.sitter(i));if(f<0)f=0;summerFloat.goFloat(f);});await wait(3500);await shot('float',3500);await ev(()=>summerFloat.stand());
// 4 dive
await ev(()=>{const c=seasonMapTest.state.summer;c.state.target=null;c.state.x=1480;c.state.y=128;c.goTo(1650,'dive',195);});await wait(2500);await shot('dive',5000);
await ev(()=>{const c=seasonMapTest.state.summer;c.goTo(2250,'dive',205);});await shot('dive2',6000);
// photos: snap the fish in sight (flash + photo card), which also fills the 图鉴 with real pictures
for(let i=0;i<3;i++){await ev(i=>{const c=seasonMapTest.state.summer,s=c.state,L=c.seaLife.filter(f=>Math.abs(f.cx-s.x)<150&&Math.abs(f.cy-s.y)<80&&(f.fa??1)>.9);const f=L[i%Math.max(1,L.length)];if(f)summerMore.snap(f.k,f.cx,f.cy);},i);await shot('photo'+i,1700);}
await ev(()=>{const c=seasonMapTest.state.summer;for(const x of [1550,1700,1850,2000,2150,2300]){}const L=c.seaLife.filter(f=>f.when==='day'||!f.when);const seen=new Set();for(const f of L){if(seen.has(f.k))continue;seen.add(f.k);summerMore.snap(f.k,f.cx,f.cy);}document.querySelectorAll('.bay-photo').forEach(e=>e.remove());});await wait(300);
// 5 market
await ev(()=>{const c=seasonMapTest.state.summer;c.state.target=null;c.state.suit='clothes';c.state.x=60;c.state.y=c.gr(60);c.beginDoor('market');});await wait(2600);await talk();await toMarket();
await ev(()=>{const c=seasonMapTest.state.summer;c.goTo(500);});await shot('market',5000);
// 6 stall UI
await ev(()=>{const v=document.getElementById('view').getBoundingClientRect();dispatchEvent(new PointerEvent('pointerdown',{clientX:v.x+v.width*.35,clientY:v.y+v.height*.6}));summerLife.openStall();});await shot('stall',3500,await full());
await ev(()=>{const c=document.querySelector('.social-sheet-content');c&&c.scrollBy({top:300});});await shot('stall2',1500,await full());await ev(()=>closeSocialSheet());await wait(800);
// 7 lodge cooking
await ev(()=>{const c=seasonMapTest.state.summer;c.beginDoor('bay');});await wait(2500);
await ev(()=>{const c=seasonMapTest.state.summer;c.state.inside=true;c.state.x=150;c.state.y=84;summerLodge.use('stove');});await wait(700);await shot('menu',2600);
await ev(()=>{const b=document.querySelector('.pk-item');b&&b.click();});await wait(2500);await shot('cook',4000);
// 8 dex
await ev(()=>{dispatchEvent(new PointerEvent('pointerdown',{clientX:900,clientY:500}));summerMore.openDex();});await shot('dex',2500,await full());
await ev(()=>socialSheet.querySelectorAll('.dex-tab')[2]?.click());await shot('dex2',1600,await full());await ev(()=>closeSocialSheet());await wait(600);
// 9 dusk and night
await ev(()=>{const c=seasonMapTest.state.summer;c.state.inside=false;c.state.x=1000;c.state.y=c.gr(1000);summerLodge.stop();sim.t=Math.floor(sim.t/1440)*1440+18*60+40;speed=1;});await wait(800);await shot('dusk',4500);
await ev(()=>{sim.t=Math.floor(sim.t/1440)*1440+21*60;const c=seasonMapTest.state.summer;c.state.suit='swim';c.state.x=2400;c.state.y=128;c.goTo(2700,'dive',260);});await wait(2500);await shot('nightdive',5000);
// 10 festivals
const fests=await ev(()=>{const out=[],t0=sim.t;for(let d=0;d<240&&out.length<summerMore.FESTS.length;d++){sim.t=t0+d*1440;const f=summerMore.fest();if(f&&!out.some(o=>o[0]===f.n))out.push([f.n,Math.floor(sim.t/1440)]);}sim.t=t0;return out;});
for(const [n,d] of fests){await ev(([d,n])=>{sim.t=d*1440+(n==='椰灯夜'?19*60+30:11*60);const c=seasonMapTest.state.summer;c.state.suit='clothes';c.state.x=60;c.state.y=c.gr(60);c.state.target=null;if(!c.state.market)c.beginDoor('market');},[d,n]);await wait(2600);await talk();await toMarket();await ev(()=>seasonMapTest.state.summer.goTo(420));await shot('fest:'+n,3500);}
fs.writeFileSync('/tmp/claude-0/promo/marks.json',JSON.stringify(marks));console.log(marks.map(m=>m[0]+' '+m[1].toFixed(1)).join(' | '));console.log(errs.slice(0,3));
await ctx.close();await b.close();})();
