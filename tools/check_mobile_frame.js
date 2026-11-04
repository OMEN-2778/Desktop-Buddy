// 手机版 frame check (owner 2026-11-03: nothing may ever leave the phone screen).
// Opens every screen of prototype/demo/mobile.html at a phone size and fails if any visible element
// sticks out of the viewport (elements clipped by an in-frame scroller are fine).
// Usage: node tools/check_mobile_frame.js [W H] [screen,screen] [--shots dir]
// Build first: PYTHONPATH=tools python3 tools/make_demo.py && PYTHONPATH=tools python3 tools/make_season_game_test.py --mobile
const {chromium}=require('playwright');const fs=require('fs');
const clear=`(async()=>{for(let i=0;i<8;i++){try{if(card&&card.phase==='ask')chooseCard('a',true)}catch(e){}await new Promise(r=>setTimeout(r,900));if(!document.documentElement.classList.contains('sheet'))break}})()`;
const path=require('path');const ROOT=path.resolve(__dirname,'..');
const args=process.argv.slice(2);const si=args.indexOf('--shots');const shots=si>=0?args.splice(si,2)[1]:null;
const page='prototype/demo/mobile.html';const CLICKABLE='button,input,select,textarea,a[href],[role=menuitem],[role=button],.contact-card';const [W='740',H='360',only='']=args;let failed=0;
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
 contactact:"(async()=>{document.getElementById('networkTrigger').click();await new Promise(r=>setTimeout(r,500));document.querySelector('.contact-card').click()})()",
 pets:"(()=>{const b=[...document.querySelectorAll('button')].find(b=>/宠物/.test(b.textContent));if(b)b.click()})()",
};
(async()=>{const b=await chromium.launch();
for(const [name,act] of Object.entries(screens)){ if(only&&!only.split(',').includes(name))continue;
const p=await b.newPage({viewport:{width:+W,height:+H},deviceScaleFactor:1.5,isMobile:true,hasTouch:true});const e=[];p.on('pageerror',x=>e.push(x.message));
await p.addInitScript(()=>{try{localStorage.setItem('buddy-settings',JSON.stringify({guided:true,speed:1}))}catch(e){}});
await p.goto('file://'+path.join(ROOT,page));await p.waitForTimeout(3000);
await p.evaluate(clear);
await p.evaluate(CLICKABLE=>{for(const el of document.querySelectorAll(CLICKABLE)){const r=el.getBoundingClientRect();if(r.width>1&&r.height>1)el.dataset.pre='1'}},CLICKABLE);
try{await p.evaluate(act)}catch(x){e.push('act:'+x.message)} await p.waitForTimeout(1200);
const bad=await p.evaluate(()=>{const W=innerWidth,H=innerHeight,o=[];const vis=el=>{for(let x=el;x&&x!==document.body;x=x.parentElement){const cs=getComputedStyle(x);if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0||x.hidden)return false}return true};
for(const el of document.querySelectorAll('body *')){if(el.closest('.console'))continue;const r=el.getBoundingClientRect();if(r.width<2||r.height<2)continue;if(!(r.left<-1||r.top<-1||r.right>W+1||r.bottom>H+1))continue;if(!vis(el))continue;
// clipped by a scrolling/hidden-overflow ancestor that is itself inside? skip if an ancestor clips it and that ancestor is in frame
let clipped=false;for(let x=el.parentElement;x&&x!==document.body;x=x.parentElement){const cs=getComputedStyle(x);if(cs.overflow!=='visible'||cs.overflowX!=='visible'||cs.overflowY!=='visible'){const q=x.getBoundingClientRect();if(q.left>=-1&&q.top>=-1&&q.right<=W+1&&q.bottom<=H+1){clipped=true;break}}}
if(!clipped)o.push((el.id||el.className||el.tagName).toString().slice(0,30)+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(','))}return o.slice(0,10)});
// anything that opened with this screen must be on top where you tap it (not under a sheet or the blur)
const hid=await p.evaluate(CLICKABLE=>{const o=[];const W=innerWidth,H=innerHeight;
for(const el of document.querySelectorAll(CLICKABLE)){if(el.dataset.pre||el.closest('.console'))continue;const r=el.getBoundingClientRect();if(r.width<2||r.height<2)continue;
const cs=getComputedStyle(el);if(cs.visibility==='hidden'||el.closest('[hidden],[inert],[aria-hidden=true]'))continue;let op=1;for(let x=el;x;x=x.parentElement)op*=+getComputedStyle(x).opacity;if(op<.05)continue;
const cx=(r.left+r.right)/2,cy=(r.top+r.bottom)/2;if(cx<0||cy<0||cx>W||cy>H)continue;
let cut=false;for(let x=el.parentElement;x&&x!==document.body;x=x.parentElement){const s=getComputedStyle(x);if(s.overflow!=='visible'){const q=x.getBoundingClientRect();if(cx<q.left||cx>q.right||cy<q.top||cy>q.bottom){cut=true;break}}}if(cut)continue;
const hit=document.elementFromPoint(cx,cy);if(!hit||el.contains(hit)||hit.contains(el)||hit.closest('[role=menuitem]'))continue;
o.push(((el.textContent||'').trim().slice(0,8)||el.className.toString().slice(0,20))+' under '+(hit.id||hit.className||hit.tagName).toString().slice(0,24))}return o.slice(0,8)},CLICKABLE);
if(hid.length)bad.push(...hid.map(h=>'covered: '+h));
// content cut off inside a panel with no way to scroll to it (owner: the 造型室 hid most of its options)
const cut=await p.evaluate(()=>{const o=[];const vis=el=>{for(let x=el;x&&x!==document.body;x=x.parentElement){const cs=getComputedStyle(x);if(cs.display==='none'||cs.visibility==='hidden'||x.hidden)return false}return true};
for(const el of document.querySelectorAll('body *')){if(el.closest('.console'))continue;const cs=getComputedStyle(el);if(cs.overflowY!=='hidden'&&cs.overflowY!=='clip')continue;if(el.scrollHeight<=el.clientHeight+24||el.clientHeight<60||!vis(el))continue;
const r=el.getBoundingClientRect();if(r.width<120)continue;
// fine if what sticks out sits in a child that scrolls itself
const sc=[...el.querySelectorAll('*')].some(c=>{const s=getComputedStyle(c).overflowY;return (s==='auto'||s==='scroll')&&c.scrollHeight>c.clientHeight+2});if(sc)continue;
// fine if nothing clickable is below the cut
const cutY=r.bottom;const lost=[...el.querySelectorAll('button,input,[role=menuitem]')].filter(b=>{const q=b.getBoundingClientRect();return q.height>0&&q.top>=cutY-2});if(!lost.length)continue;
o.push((el.id||el.className).toString().slice(0,26)+' hides '+lost.length+' buttons')}return o.slice(0,5)});
if(cut.length)bad.push(...cut.map(c=>'cut off: '+c));
if(shots)await p.screenshot({path:path.join(shots,`m_${name}.png`)});
if(bad.length||e.length){failed++;console.log('FAIL',name,'errors',e.slice(0,2),'outside',bad)}else console.log('ok',name);await p.close()}
await b.close();if(failed){console.log(failed+' screen(s) broke the phone frame');process.exit(1)}console.log('PASS: every screen stays inside the phone frame at '+W+'x'+H)})()
