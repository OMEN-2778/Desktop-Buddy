// 手机版 frame check (owner 2026-11-03: nothing may ever leave the phone screen).
// Opens every screen of prototype/demo/mobile.html at a phone size and fails if any visible element
// sticks out of the viewport (elements clipped by an in-frame scroller are fine).
// Usage: node tools/check_mobile_frame.js [W H] [screen,screen] [--shots dir]
// Build first: PYTHONPATH=tools python3 tools/make_demo.py && PYTHONPATH=tools python3 tools/make_season_game_test.py --mobile
const {chromium}=require('playwright');const fs=require('fs');
const clear=`(async()=>{for(let i=0;i<8;i++){try{if(card&&card.phase==='ask')chooseCard('a',true)}catch(e){}await new Promise(r=>setTimeout(r,900));if(!document.documentElement.classList.contains('sheet'))break}})()`;
const path=require('path');const ROOT=path.resolve(__dirname,'..');
const args=process.argv.slice(2);const si=args.indexOf('--shots');const shots=si>=0?args.splice(si,2)[1]:null;
const page='prototype/demo/mobile.html';const [W='740',H='360',only='']=args;let failed=0;
const screens={
 main:'0',
 storypeer:"(()=>{asleep=()=>false;window.__sp=createStorySpeech({view});__sp.show('妈妈','你那边下雨了吗？我看天气预报说今天降温，记得多穿点，别又跟上次一样感冒了。',{advance:()=>{}})})()",
 storychoice:"(()=>{asleep=()=>false;window.__sp=createStorySpeech({view});__sp.show('妈妈','周末回来吃饭吗？你爸念叨好几天了。',{choices:[{label:'好啊，我想吃红烧肉'},{label:'这周有点忙'},{label:'下周吧'}]})})()",

 front:"(async()=>{throughDoor('front');await new Promise(r=>setTimeout(r,6000))})()",
 park:"(async()=>{throughDoor('park');await new Promise(r=>setTimeout(r,6000))})()",
 mall:"(async()=>{throughDoor('mall');await new Promise(r=>setTimeout(r,6000))})()",
 beach:"(async()=>{throughDoor('beach');await new Promise(r=>setTimeout(r,6000))})()",
 bar:"(async()=>{throughDoor('bar');await new Promise(r=>setTimeout(r,6000))})()",
 disco:"(async()=>{throughDoor('disco');await new Promise(r=>setTimeout(r,6000))})()",

 settings:"document.getElementById('setGear').click()",
 diary:"document.getElementById('diaryBox').click()",
 contacts:"document.getElementById('networkTrigger').click()",
 tv:"openPicker('tv')",
 cook:"openPicker('cook')",
 studio:"openWardrobe()",
 guide:"openGuide()",
 card:"(()=>{const c=CARDS.find(c=>c.on==='idle')||CARDS[0];showCard(c)})()",
 ring:"openRing('buddy')",
 ringpc:"openRing('computer')",
 pets:"(()=>{const b=[...document.querySelectorAll('button')].find(b=>/宠物/.test(b.textContent));if(b)b.click()})()",
};
(async()=>{const b=await chromium.launch();
for(const [name,act] of Object.entries(screens)){ if(only&&!only.split(',').includes(name))continue;
const p=await b.newPage({viewport:{width:+W,height:+H},deviceScaleFactor:1.5,isMobile:true,hasTouch:true});const e=[];p.on('pageerror',x=>e.push(x.message));
await p.addInitScript(()=>{try{localStorage.setItem('buddy-settings',JSON.stringify({guided:true,speed:1}))}catch(e){}});
await p.goto('file://'+path.join(ROOT,page));await p.waitForTimeout(3000);
await p.evaluate(clear);
try{await p.evaluate(act)}catch(x){e.push('act:'+x.message)} await p.waitForTimeout(1200);
const bad=await p.evaluate(()=>{const W=innerWidth,H=innerHeight,o=[];const vis=el=>{for(let x=el;x&&x!==document.body;x=x.parentElement){const cs=getComputedStyle(x);if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0||x.hidden)return false}return true};
for(const el of document.querySelectorAll('body *')){if(el.closest('.console'))continue;const r=el.getBoundingClientRect();if(r.width<2||r.height<2)continue;if(!(r.left<-1||r.top<-1||r.right>W+1||r.bottom>H+1))continue;if(!vis(el))continue;
// clipped by a scrolling/hidden-overflow ancestor that is itself inside? skip if an ancestor clips it and that ancestor is in frame
let clipped=false;for(let x=el.parentElement;x&&x!==document.body;x=x.parentElement){const cs=getComputedStyle(x);if(cs.overflow!=='visible'||cs.overflowX!=='visible'||cs.overflowY!=='visible'){const q=x.getBoundingClientRect();if(q.left>=-1&&q.top>=-1&&q.right<=W+1&&q.bottom<=H+1){clipped=true;break}}}
if(!clipped)o.push((el.id||el.className||el.tagName).toString().slice(0,30)+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(','))}return o.slice(0,10)});
if(shots)await p.screenshot({path:path.join(shots,`m_${name}.png`)});
if(bad.length||e.length){failed++;console.log('FAIL',name,'errors',e.slice(0,2),'outside',bad)}else console.log('ok',name);await p.close()}
await b.close();if(failed){console.log(failed+' screen(s) broke the phone frame');process.exit(1)}console.log('PASS: every screen stays inside the phone frame at '+W+'x'+H)})()
