// 爸妈住在茵菲谷（owner 2026-11-06）：
//  - 平时：早上、傍晚妈妈在灶台、爸爸在饭桌，晚上两人坐长椅，22 点后在自己床上（infei_home.js 画睡觉）；白天下地/去镇上
//    （infei_farm.js 帮忙浇水，现在七成的日子会来）。点爸妈说一句。她在屋里有爸妈陪着，社交慢慢涨。
//  - 春节她在茵菲谷：爸妈在农舍过年，主世界春节的每一步都有（贴春联、包饺子、午饭、压岁钱、三连问、年夜饭、春晚、零点、睡觉），
//    台词每年换（spring_festival.js → cnyVariant(step,'farm')），夜里山谷放烟花。
//  - 主世界人脉点爸妈的「拜访」：自己去机场、飞茵菲谷，当天爸妈都在家等她。
(function(){
 const X=springFarm.X,C=()=>seasonMapTest.state.spring,inSpring=()=>sim.place==='spring_test',F=()=>springFarm.state;
 const today=()=>Math.floor(sim.t/1440),mins=()=>((sim.t%1440)+1440)%1440,HOME=3;   // the farmhouse's yard is scene 3
 const ready=()=>F().phase==='done';
 const look=id=>socialState.contacts.find(c=>c.id===id)?.look||doll.PRESETS[id==='mom'?'f':'m'];
 const npc={};const npcOf=id=>{const lk=look(id);if(!npc[id]||npc[id].look!==lk)npc[id]={look:lk,ramps:doll.rampsOf(lk),cache:new Map(),kid:false};return npc[id];};
 const name=id=>id==='mom'?'妈妈':'爸爸',contact=id=>socialState.contacts.find(c=>c.id===id);
 // farmhouse ground floor (house px): where they stand or sit
 const AT={stove:[262,'stand'],jar:[300,'stand'],tableL:[200,'sit'],tableR:[216,'sit'],setteeL:[99,'sit'],setteeR:[124,'sit'],door:[60,'stand'],kitchen:[240,'stand']};
 let visit=null;   // {day} — she flew in to see them: both home all day
 // ---------------------------------------------------------------- the day's plan → {mom:spot,dad:spot}
 function plan(){if(!ready())return {};const m=mins(),v=visit&&visit.day===today(),fc=farmCny();
  if(fc)return fc.where;
  const cook=infeiHome.svc?.id==='stove'?'jar':'stove',o={};
  if(m>=6*60+30&&m<8*60)o.mom=cook;if(m>=7*60&&m<8*60)o.dad='tableR';
  if(m>=17*60+30&&m<19*60)o.mom=cook;if(m>=18*60&&m<19*60)o.dad='tableR';
  if(m>=19*60&&m<21*60+30){o.mom=today()%3===0?'tableL':'setteeL';o.dad='setteeR';}
  if(v&&m>=8*60&&m<17*60+30){o.mom=Math.floor(m/90)%2?'tableL':cook;o.dad=Math.floor(m/120)%2?'tableR':'setteeR';}
  if(infeiHome.svc?.id==='settee'&&o.dad==='setteeR')o.dad='tableR';   // she took the middle of the bench: 爸爸 moves to the table
  return o;}
 // who is in the house right now (and where)
 const pos={};
 function here(){const p=plan(),out=[];for(const id of ['mom','dad']){const k=p[id];if(!k){delete pos[id];continue;}
  const [x,pose]=AT[k];const q=pos[id]||(pos[id]={x,born:realClock});if(q.k!==k){q.k=k;q.tx=x;}out.push({id,q,pose,k});}return out;}
 // ---------------------------------------------------------------- drawing (inside the farmhouse)
 function drawIn(ctx){
  if(!ready())return;const list=here(),dt=Math.min(.1,realClock-(drawIn.t||realClock));drawIn.t=realClock;
  const s=C().state;
  for(const {id,q,pose}of list){const d=q.tx-q.x,moving=Math.abs(d)>.5;if(moving&&speed)q.x+=Math.sign(d)*Math.min(Math.abs(d),34*dt);
   const sit=!moving&&pose==='sit',a=Math.min(1,(realClock-q.born)/.6);
   const f={expr:sit?'happy':'neutral',look:s.inside?Math.sign(s.x-q.x)||1:1,bob:moving?Math.floor(realClock*5)%2:0,sway:moving?Math.floor(realClock*3)%2:0,wave:null};
   const p=sit?'sit':moving?['walkL','stand','walkR','stand'][Math.floor(realClock*6)%4]:'stand';
   ctx.save();ctx.globalAlpha=a;ctx.drawImage(npcCanvas(npcOf(id),f,p,false),Math.round(q.x)-10,108-27-(sit?(q.k?.startsWith('settee')?5:3):0));ctx.restore();}
  if(farmCny())drawCnyInside(ctx);}
 // ---------------------------------------------------------------- clicks: a word with them
 const TALK={
  mom:{morning:['早饭在锅里，自己盛。','今天天好，被子拿出去晒晒。','鸡蛋我捡了，今天下了五个。','头发扎起来，干活方便。'],
   day:['菜地那边我看了，长得不错。','镇上的豆腐今天没买着，明天再去。','你那件外套扣子掉了，我给你缝上了。','别光顾着地里，水也要喝。','中午想吃面还是吃饭？'],
   evening:['晚上想吃啥？','灶上热着汤，喝一碗再睡。','你爸又在长椅上打盹了。','明天说是要下雨。','脚冷不冷？给你灌个热水袋。']},
  dad:{morning:['我去看看牛。','今天风大，帽子戴上。','你起得比我还早？'],
   day:['篱笆那边松了，下午我去钉钉。','井水凉，别一口气喝太多。','你那块地，草该拔了。','这牛脾气跟你小时候一样，犟。'],
   evening:['来，坐会儿。','这长椅是我修的，结实吧？','山里晚上真安静，虫子叫得清清楚楚。','明天早上我叫你，一起去镇上。','你妈做饭比城里饭馆好吃，你说是不是？']}};
 const REPLY=['好～','知道啦','嗯嗯','哈哈，好','我一会儿就去','真的吗？','爸妈最好了'];
 let talkQ=[],talkAt=0;
 const say=(who,text)=>{if(who==='me'){speak(text,true);return;}showSay(text,name(who)+'：',contact(who));};
 setInterval(()=>{if(!talkQ.length||!speed||realClock<talkAt||!inSpring())return;const [w,t]=talkQ.shift();say(w,t);talkAt=realClock+2.6;},200);
 function click(x,y,s){if(!s.inside||!ready())return false;
  for(const {id,q,pose}of here()){if(Math.abs(x-q.x)>8||y<108-28||y>109)continue;
   const fc=farmCny();if(fc&&typeof CNY_TALK!=='undefined'){const m=mins(),pool=CNY_TALK[m<11*60?'morning':m<21*60?'day':'night'].filter(([w])=>w===id);const [,text]=pick(pool.length?pool:CNY_TALK.day);talkQ.unshift([id,text],['me',pick(CNY_REPLY)]);}
   else{const m=mins(),pool=TALK[id][m<9*60?'morning':m<18*60?'day':'evening'];talkQ.unshift([id,pick(pool)],['me',pick(REPLY)]);}
   talkAt=0;if(sim.needs.social!=null)sim.needs.social=Math.min(100,sim.needs.social+3);return true;}
  return false;}
 X.hooks.click.unshift(click);
 // with them in the house: social slowly fills (as with guests at home)
 let lastT=sim.t;setInterval(()=>{const dt=Math.max(0,Math.min(30,sim.t-lastT));lastT=sim.t;if(!inSpring()||!C().state.inside||asleep()||!here().length)return;sim.needs.social=Math.min(100,sim.needs.social+dt*(farmCny()?.12:.05));},500);
 // ================================================================ 春节 in 茵菲谷
 // the main world's CNY_STEPS, played in the farmhouse; where: the parents' places for each step, act: her furniture
 const STEP_AT={arrive:{mom:'kitchen',dad:'tableR'},couplets:{},dumplings:{mom:'stove',dad:'tableR'},lunch:{mom:'tableL',dad:'tableR'},
  envelope:{mom:'setteeL',dad:'setteeR'},questions:{mom:'setteeL',dad:'setteeR'},feast:{mom:'tableL',dad:'tableR'},gala:{mom:'setteeL',dad:'setteeR'},countdown:{mom:'setteeL',dad:'setteeR'},bedtime:{mom:'kitchen',dad:'kitchen'}};
 const STEP_USE={arrive:'in',couplets:'out',dumplings:'stove',lunch:'table',envelope:'settee',questions:'settee',feast:'table',gala:'settee',countdown:'settee'};
 const fc={day:null,done:new Set(),gone:false,couplets:false};
 // it is 春节 and she spends it here (not if the city flat already had them over this morning)
 function farmCny(){if(typeof CNY_STEPS==='undefined'||!ready())return null;
  const fest=festName()==='春节',d=today(),late=fc.day===d-1&&mins()<60;if(!fest&&!late)return null;
  const base=fest?d:d-1;
  if(fc.day!==base){if(!inSpring())return null;if(cny.day===base&&cny.done.size&&!cny.farm)return null;
   Object.assign(fc,{day:base,done:new Set(),gone:false,couplets:false});for(const k of Object.keys(cny.v||{}))if(k.startsWith('farm:'))delete cny.v[k];}
  cny.day=base;cny.gone=true;cny.farm=true;cny.v||={};   // the city flat has nobody this year
  const m=sim.t-base*1440;if(fc.gone||m<CNY_STEPS[0].at)return null;
  const last=[...CNY_STEPS].reverse().find(s=>m>=s.at);return {step:last,where:STEP_AT[last.id]||{}};}
 function runStep(step,live){
  if(step.id==='couplets')fc.couplets=true;if(step.leave)fc.leaving=true;
  if(!live)return;
  const v={...step,...cnyVariant(step,'farm')};
  const u=STEP_USE[step.id],c=C();
  if(u&&!asleep()&&sim.mode!=='down'&&!['bath','toilet'].includes(sim.act)){
   seasonMapTest.state.autoAt=sim.t+60;   // the family's moment: no wandering off
   if(u==='out'){if(c.state.inside)c.leave();}else if(u==='in'){if(!c.state.inside)X.hooks.pick.indoor();}else infeiHome.use(u,true);}
  talkQ.push(...v.lines.map(([w,t])=>[w,t]));
  const said=v.lines.map(([w,t])=>[(w==='me'?nameOf():name(w))+'：',t]);if(v.diary)log(v.diary,null,said);
  if(step.mood)addMood(step.mood,{words:false});addMood('cnyFamily',{words:false,diary:false});
  if(step.envelope)fc.envelopeUntil=realClock+6;}
 setInterval(()=>{try{const f=farmCny();if(!f||!inSpring()||!speed)return;const m=sim.t-fc.day*1440;
  const due=CNY_STEPS.filter(s=>m>=s.at&&!fc.done.has(s.id));due.forEach((s,i)=>{fc.done.add(s.id);runStep(s,i===due.length-1&&m-s.at<50);});
  if(fc.leaving&&!talkQ.length&&realClock>talkAt+2)fc.gone=true;}catch(e){console.warn('farm cny',e);}},500);
 // the couplets step: they stand at the front door outside
 function drawOut(ctx,info){if(info.region!==HOME)return;
  if(fc.couplets&&fc.day!=null&&today()-fc.day<=1)drawCouplets(ctx);
  const f=farmCny();if(f&&f.step.id==='couplets')['mom','dad'].forEach((id,i)=>{const fr={expr:'happy',look:i?-1:1,bob:0,sway:0,wave:null};ctx.drawImage(npcCanvas(npcOf(id),fr,'stand',false),166+i*32-10,103-27);});
  if(f&&mins()>=19*60)fireworks(ctx);}
 function drawCouplets(ctx){ctx.fillStyle='#c8312f';ctx.fillRect(169,66,3,30);ctx.fillRect(192,66,3,30);ctx.fillRect(172,62,20,3);
  ctx.fillStyle='#f2b33d';for(let k=0;k<5;k++){ctx.fillRect(170,70+k*5,1,1);ctx.fillRect(193,70+k*5,1,1);}for(let k=0;k<4;k++)ctx.fillRect(175+k*4,63,1,1);
  ctx.fillStyle='#c8312f';ctx.fillRect(179,72,7,7);ctx.fillStyle='#f2b33d';ctx.fillRect(181,74,3,3);}
 function fireworks(ctx){const W=ctx.canvas.width;
  for(let k=0;k<3;k++){const per=2.4+k*.7,n=Math.floor((realClock+k)/per),u=((realClock+k)%per)/per,h=(a,b)=>((Math.sin(n*12.9898+a*78.233+b)*43758.5453)%1+1)%1;
   const cx=30+h(k,1)*(W-60),cy=12+h(k,2)*30,r=2+u*12,a=(1-u),col=['255,120,120','255,214,110','140,220,255','200,150,255'][(n+k)%4];
   ctx.fillStyle=`rgba(${col},${a.toFixed(2)})`;for(let i=0;i<12;i++){const th=i/12*6.283;ctx.fillRect(Math.round(cx+Math.cos(th)*r),Math.round(cy+Math.sin(th)*r+u*4),1,1);}}}
 // red lanterns and a 福 in the farmhouse, the envelope over her head
 function drawCnyInside(ctx){for(const x of [60,150,240,300]){ctx.fillStyle='#5e5b71';ctx.fillRect(x,62,1,3);ctx.fillStyle='#c8312f';ctx.fillRect(x-2,65,5,5);ctx.fillStyle='#e0534d';ctx.fillRect(x-1,65,3,1);ctx.fillStyle='#f2b33d';ctx.fillRect(x,70,1,2);}
  if(realClock<(fc.envelopeUntil||0)){const s=C().state,u=1-(fc.envelopeUntil-realClock)/6,x=Math.round(s.x)-3,y=Math.round(s.y-27-10-Math.min(1,u*4)*4);
   ctx.fillStyle='#c8312f';ctx.fillRect(x,y,7,9);ctx.fillStyle='#e0534d';ctx.fillRect(x+1,y+1,5,1);ctx.fillStyle='#f2b33d';ctx.fillRect(x+2,y+4,3,2);}}
 X.hooks.draw.push((ctx,info)=>{try{if(info.inside)drawIn(ctx);else drawOut(ctx,info);}catch(e){console.warn('season parents',e);}});
 // 春节 morning: no farm chores pulling her away from the family
 // ================================================================ 人脉 → 拜访爸妈 = fly to 茵菲谷
 const canFly=()=>F().unlocked&&ready();
 function goSee(c){
  if(sim.place==='spring_test'){showHint(`${name(c.id)}就在家里呢`);return true;}
  if(!canFly())return false;
  if(sim.mode==='down'||asleep()||wiping||cardHolds()||socialState.guest||friendVisit||friendOutingState){showHint('先忙完眼前的事情，再去看爸妈吧。');return true;}
  visit={day:null,pending:true};log(`想爸妈了，去茵菲谷看看他们。`);showSay(pick(['好久没见爸妈了，去茵菲谷看看！','去茵菲谷，给爸妈一个惊喜。']));
  closeSocialSheet?.();setContactsOpen?.(false);closeRing();
  if(window.airportTravel){throughDoor('airport_test');const t0=Date.now(),step=()=>{if(Date.now()-t0>30000)return;
    if(sim.place==='airport_test'&&!wiping&&!airportTravel.flight.busy){airportTravel.walkTo(283,()=>ringPick('airport:spring'));return;}setTimeout(step,300);};setTimeout(step,600);}
  else throughDoor('spring_test');
  return true;}
 const oVisit=requestFriendVisit;requestFriendVisit=function(id){const c=socialState.contacts.find(c=>c.id===id);if(c?.family&&goSee(c))return true;return oVisit.apply(this,arguments);};
 const oActs=openContactActions;openContactActions=function(id){const r=oActs.apply(this,arguments);const c=socialState.contacts.find(c=>c.id===id);
  if(c?.family&&canFly()&&!['summer_test','spring_test'].includes(sim.place)){const b=contactActions.querySelector('[data-action=visit]');
   if(b){b.removeAttribute('aria-disabled');b.title='爸妈住在茵菲谷，坐飞机过去';b.setAttribute('aria-label','拜访：'+b.title);b.querySelector('small')&&(b.querySelector('small').textContent='去茵菲谷');}}
  if(c?.family&&sim.place==='spring_test'){const b=contactActions.querySelector('[data-action=visit]');if(b){b.setAttribute('aria-disabled','true');b.title='就在家里呢';b.querySelector('small')?.remove();}}
  return r;};
 // arrived: both home all day, at the door to meet her
 const oArrive=arriveAt;arriveAt=function(p){const r=oArrive.apply(this,arguments);
  if(p==='spring_test'&&visit?.pending){visit={day:today()};setTimeout(()=>{if(!inSpring())return;if(ready()&&!C().state.inside)X.hooks.pick.indoor();talkQ.push(['mom',pick(['来啦！路上累不累？','哎呀，怎么突然回来了，也不说一声！','正念叨你呢，你就到了。'])],['dad',pick(['我去杀只鸡。','屋里坐，外头风大。','行李给我。'])],['me',pick(['想你们了嘛！','回来看看你们～','饿了！'])]);
   log('飞到茵菲谷，爸妈都在家。');addSocialMemory?.(contact('mom'),'回茵菲谷看爸妈','坐飞机去茵菲谷，爸妈都在家等着。');},1800);}
  return r;};
 window.seasonParents={plan,here,farmCny,goSee,get visit(){return visit;}};
})();
