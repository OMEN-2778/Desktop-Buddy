// A world's people keep their identity; only acquaintances appear in the HUD.
function makeSocialWorld(){
  let seed=2778;const random=()=>((seed=Math.imul(seed,1664525)+1013904223>>>0)/4294967296),take=a=>a[Math.floor(random()*a.length)];
  const names=new Set(DEFAULT_CONTACTS.map(c=>c.name)),looks=new Set(),world=DEFAULT_CONTACTS.filter(c=>!c.family).map(c=>({id:c.id,name:c.name,look:doll.normalize(c.look),child:false}));
  for(let i=world.length;i<200;i++){
    const gender=i%2?'m':'f',pool=doll.NAMES[gender].filter(n=>!names.has(n)),name=take(pool);names.add(name);
    let lk,key;do{const colors=D.doll.swatches,options=D.doll.options;
      lk=doll.normalize({...doll.PRESETS[gender],name,gender,style:take(options.style)[0],eyes:take(options.eyes)[0],topStyle:take(options.top)[0],bottomStyle:take(options.bottom)[0],socks:take(options.socks)[0],acc:random()<.35?[take(options.acc)[0]]:[],hair:take(colors.hair)[1],skin:take(colors.skin)[1],top:take(colors.cloth)[1],bottom:take(colors.cloth)[1],eye:take(colors.eye)[1]});
      key=JSON.stringify({...lk,name:undefined});
    }while(looks.has(key));looks.add(key);world.push({id:'person_'+i,name,look:lk,child:i%9===0});
  }return world;
}
socialState.world=makeSocialWorld();socialState.archive={};socialState.decayDay=Math.floor(sim.t/1440);socialState.nextVisit=sim.t+1440;socialState.guest=null;
const socialSheet=document.createElement('section');socialSheet.className='social-sheet';socialSheet.hidden=true;socialSheet.setAttribute('role','dialog');socialSheet.setAttribute('aria-modal','true');socialSheet.setAttribute('aria-labelledby','socialSheetTitle');document.getElementById('widget').append(socialSheet);
let sheetReturnFocus=null;
function socialDialogHolds(){return !socialSheet.hidden;}
function closeSocialSheet(){socialSheet.hidden=true;if(sheetReturnFocus?.isConnected&&!sheetReturnFocus.closest('[inert]'))sheetReturnFocus.focus({preventScroll:true});}
function openSocialSheet(title){
  sheetReturnFocus=document.activeElement;setContactsOpen(false);closeRing();closePicker();setDiaryOpen(false);setSettingsOpen(false);socialSheet.replaceChildren();
  const heading=document.createElement('h3');heading.id='socialSheetTitle';heading.textContent=title;socialSheet.append(heading);
  const close=document.createElement('button');close.type='button';close.className='social-sheet-close';close.textContent='关闭';close.onclick=closeSocialSheet;socialSheet.append(close);socialSheet.hidden=false;close.focus({preventScroll:true});return socialSheet;
}
socialSheet.addEventListener('keydown',e=>{if(e.key==='Escape'){e.stopPropagation();closeSocialSheet();}if(e.key==='Tab'){const buttons=[...socialSheet.querySelectorAll('button')],i=buttons.indexOf(document.activeElement);if(e.shiftKey&&i===0){e.preventDefault();buttons.at(-1).focus();}else if(!e.shiftKey&&i===buttons.length-1){e.preventDefault();buttons[0].focus();}}});
function addSocialMemory(c,title,text){
  c.memories||=[];const last=c.memories.at(-1);if(last&&last.title===title&&Math.abs(last.t-sim.t)<60)return;
  c.memories.push({t:sim.t,title,text});
}
function showSocialMemories(id){
  const c=socialState.contacts.find(c=>c.id===id);if(!c)return;
  const sheet=openSocialSheet(`和${contactName(c)}的经历`),list=document.createElement('ol');list.className='social-memories';
  if(!c.memories?.length){const p=document.createElement('p');p.textContent='共同的故事还没写下。下一次认真聊天，或者一起度过一段时光，就从这里开始。';sheet.append(p);}
  for(const memory of [...(c.memories||[])].reverse()){
    const row=document.createElement('li'),time=document.createElement('time'),title=document.createElement('strong'),text=document.createElement('p');
    time.textContent=`第 ${Math.floor(memory.t/1440)+1} 天 · ${String(Math.floor(memory.t/60)%24).padStart(2,'0')}:${String(Math.floor(memory.t)%60).padStart(2,'0')}`;
    title.textContent=memory.title;text.textContent=memory.text;row.append(time,title,text);list.append(row);
  }sheet.append(list);
}
function worldNpcIdentity(role){
  if(role==='bartender')return socialState.world.find(c=>c.id==='person_10');
  const occupied=new Set((life.npcs||[]).map(n=>n.personId));if(typeof barScene!=='undefined'&&barScene){for(const n of [barScene.bartender,...(barScene.guests||[])])if(n)occupied.add(n.personId);}
  const pool=socialState.world.filter(c=>c.child===(role==='kid')&&!occupied.has(c.id)&&!(c.look.style===look.style&&c.look.hair===look.hair));return pick(pool.length?pool:socialState.world);
}
function meetWorldNpc(n){
  const person=socialState.world.find(c=>c.id===n.personId);if(!person)return null;
  let c=socialState.contacts.find(c=>c.id===person.id);
  if(!c){c={...person,family:null,affinity:8,lastContact:sim.t,lastSeen:sim.t,metAt:sim.t,memories:[...(socialState.archive[person.id]?.memories||[])]};const returning=!!socialState.archive[person.id];socialState.contacts.push(c);delete socialState.archive[person.id];
    const text=`在${({park:'公园',bar:'酒吧',mall:'商场',front:'街边',beach:'码头'})[sim.place]||'路上'}和${c.name}聊了几句，${returning?'重新':'第一次'}交换了联系方式。`;log(text);addSocialMemory(c,returning?'再次遇见':'第一次认识',text);
  }else{c.lastSeen=sim.t;c.forgotten=false;finishContactTalk(c.id,'meet');}
  contactsSig='';return c;
}
function socialLevel(c){return c.affinity>90?'best':c.affinity>=60?'close':c.affinity>=20?'friend':'familiar';}
function socialTalkPool(kind,c){
  const level=socialLevel(c),entries=SOCIAL_TEXT.conversations[level];
  const conversations=entries.map(([title,...lines],i)=>({title,lines:[...(kind==='video'?['>看得清吗？我把镜头挪过来一点。']:kind==='call'?['>喂，我在，听得到你。']:[]),...lines],id:'social_'+level+'_'+i}));
  if(level!=='familiar')conversations.push(...(CHATS[kind]?.friend?.talks||[]));
  return conversations;
}
for(const [level,entries] of Object.entries(SOCIAL_TEXT.conversations))entries.forEach((entry,i)=>{ML['social_'+level+'_'+i]={name:{familiar:'慢慢熟悉',friend:'聊得来',close:'有人懂我',best:'一直在身边'}[level],emo:'happy',pts:level==='best'?3:2,min:150};});
SOCIAL_TEXT.visitEvents.forEach(([name,text,say,emo],i)=>{ML['home_guest_event_'+i]={name,emo,pts:2,min:120};});
function socialRejected(c,reason){
  if(!c||c.family)return;
  const day=Math.floor(sim.t/1440);if(c.rejectDay!==day){c.rejectDay=day;c.rejectLoss=0;}
  const loss=Math.min(1,2-(c.rejectLoss||0));if(loss<=0)return;c.rejectLoss=(c.rejectLoss||0)+loss;
  c.affinity=Math.max(0,c.affinity-loss);contactsSig='';
  log(`${contactName(c)}${reason}，彼此的联系淡了一点。`);
  if(c.affinity<=0)removeSocialContact(c,'最近总没能联系上，彼此渐渐失去了联系。');
}
function removeSocialContact(c,reason){
  if(c.family)return;if(socialState.guest?.id===c.id)endHomeVisit('改天再来坐坐。',false);
  addSocialMemory(c,'暂时走散',reason);socialState.archive[c.id]={...c,affinity:0};socialState.contacts=socialState.contacts.filter(p=>p.id!==c.id);contactsSig='';
  if(selectedContact===c.id)closeContactActions();log(`和${contactName(c)}渐渐失去了联系。`);if(moodrow.classList.contains('contacts-open'))fillContacts();
}
function tickSocialDecay(){
  const day=Math.floor(sim.t/1440);if(day<=socialState.decayDay)return;
  const previous=socialState.decayDay;socialState.decayDay=day;
  for(const c of [...socialState.contacts]){
    if(c.family)continue;
    const lastDay=Math.floor((c.lastContact??c.metAt??sim.t)/1440),days=Math.max(0,day-Math.max(previous,lastDay+4));
    if(!days)continue;const old=contactRelation(c);c.affinity=Math.max(0,c.affinity-days);contactsSig='';
    if(c.affinity<10&&sim.t-(c.lastSeen??c.metAt??sim.t)>7*1440)c.forgotten=true;
    if(c.affinity<=5&&!c.farewellTried){c.farewellTried=true;if(Math.random()<.12)c.farewellPending=true;}
    if(c.farewellPending&&c.affinity<=0)c.affinity=1;
    if(c.affinity<=0)removeSocialContact(c,'许多天没再说上话，这段联系慢慢淡了。');
    else if(old!==contactRelation(c)){const text=`这些天没和${c.name}联系，从${old}慢慢变成了${contactRelation(c)}。`;log(text);addSocialMemory(c,'关系渐渐疏远',text);}
  }if(moodrow.classList.contains('contacts-open'))fillContacts();
}
function socialCallDue(c){const gap=c.family?1440:c.affinity>90?600:c.affinity>=60?1080:c.affinity>=20?1800:3600;return sim.t-(c.lastIncoming??-Infinity)>=gap;}
function socialLifeSnapshot(){return {world:socialState.world,archive:socialState.archive,decayDay:socialState.decayDay,nextVisit:socialState.nextVisit,guest:socialState.guest?{...socialState.guest,npc:undefined}:null};}
function restoreSocialLife(data){
  const memories=value=>Array.isArray(value)?value.filter(m=>m&&Number.isFinite(m.t)&&typeof m.title==='string'&&typeof m.text==='string').map(m=>({t:m.t,title:m.title.slice(0,100),text:m.text.slice(0,2000)})):[];
  socialState.world=makeSocialWorld();
  const worldData=new Map((Array.isArray(data?.world)?data.world:[]).filter(p=>p&&typeof p.id==='string'&&typeof p.name==='string').map(p=>[p.id,p]));
  for(const p of socialState.world){const saved=worldData.get(p.id)||socialState.contacts.find(c=>c.id===p.id);if(saved){p.name=doll.cleanName(saved.name)||p.name;p.look=doll.normalize(saved.look);}}
  socialState.archive={};for(const [id,c]of Object.entries(data?.archive||{})){if(!socialState.world.some(p=>p.id===id)||!c||typeof c!=='object')continue;socialState.archive[id]={id,name:socialState.world.find(p=>p.id===id).name,memories:memories(c.memories)};}
  for(const c of socialState.contacts){const saved=(Array.isArray(data?.contacts)?data.contacts:[]).find(p=>p&&p.id===c.id)||{};c.memories=memories(saved.memories);for(const key of ['metAt','lastSeen','lastIncoming','rejectDay','rejectLoss','lastVisitOffer'])c[key]=Number.isFinite(saved[key])?saved[key]:key==='rejectLoss'?0:null;
    c.child=!!socialState.world.find(p=>p.id===c.id)?.child;c.forgotten=!c.family&&!!saved.forgotten;c.farewellTried=!!saved.farewellTried;c.farewellPending=!!saved.farewellPending;
  }
  socialState.decayDay=Number.isInteger(data?.decayDay)?data.decayDay:null;
  socialState.nextVisit=Number.isFinite(data?.nextVisit)?data.nextVisit:null;socialState.guest=null;
  const guest=data?.guest;if(guest&&socialState.contacts.some(c=>c.id===guest.id)&&Number.isFinite(guest.until)){
    socialState.guest={id:guest.id,phase:['scheduled','entering','visiting','leaving'].includes(guest.phase)?guest.phase:'scheduled',at:Number.isFinite(guest.at)?guest.at:sim.t,until:guest.until,s:Number.isFinite(guest.s)?guest.s:0,next:0,said:[],count:0,activity:guest.activity||'chat'};
  }closeSocialSheet();
}

D.spots.host=[D.spots.sofa[0],D.spots.sofa[1]-6,'sit'];
ACTS.host={spot:'host',label:'招待朋友',emote:'chat',dur:600,log:null};EFFECT.host={social:.3,fun:.2};D.seatLifts.host=4;
const guestBubble=document.createElement('div');guestBubble.className='npcsay home-guest-say';guestBubble.hidden=true;document.getElementById('widget').append(guestBubble);
function homeVisitActive(){return sim.place==='home'&&socialState.guest?.phase==='visiting';}
function inviteHome(id,proactive=false){
  const c=socialState.contacts.find(c=>c.id===id);if(!c)return false;
  if(sim.place!=='home'||asleep()||sim.mode==='down'||socialState.guest||hour()<8||hour()>=21||socialBusy()){
    log(`现在不太方便招待${contactName(c)}，等回家休息好再约。`);return false;
  }
  if(!c.family&&c.affinity<20){log(`${c.name}：我们先多聊聊天，熟悉一点再登门吧。`);return false;}
  const at=sim.t+12+Math.floor(Math.random()*14);socialState.guest={id,phase:'scheduled',at,until:at+150,s:0,next:0,said:[],count:0,usedTalks:[],usedEvents:[],activity:'chat',proactive};
  socialState.nextVisit=sim.t+1440;log(`${contactName(c)}答应来家里坐坐，正在路上。`);showSay(`那我在家等你，路上慢点。`);return true;
}
function endHomeVisit(reason='今天聊得很开心，下次再来。',completed=true){
  const g=socialState.guest;if(!g)return;const c=socialState.contacts.find(c=>c.id===g.id);
  if(g.phase==='scheduled'){log(`和${c?contactName(c):'朋友'}约好了改天再来。`);socialState.guest=null;return;}
  if(g.phase==='leaving')return;
  if(c){const text=`${contactName(c)}来家里做客，${g.count?`一起聊起了${g.count}件小事，`:''}${reason}`;log(text,null,g.said?.length?g.said:undefined);addSocialMemory(c,'来家里做客',text);if(completed)finishContactTalk(c.id,'visit');}
  g.phase='leaving';g.talk=null;guestBubble.hidden=true;
  if(sim.act==='host'){sim.act=null;sim.mode='idle';sim.idleUntil=sim.t+1;sim.queue=[];}
}
function homeGuestSay(text,c){guestBubble.textContent=text;guestBubble.hidden=false;guestBubble.dataset.until=realClock+4.5;guestBubble.setAttribute('aria-label',`${contactName(c)}：${text}`);}
function guestNpc(g){const c=socialState.contacts.find(c=>c.id===g.id);if(!c)return null;
  if(!g.npc||g.npc.look!==c.look)g.npc={look:c.look,ramps:doll.rampsOf(c.look),cache:new Map(),kid:!!c.child};return g.npc;}
function homeGuestPoint(g){const from=D.spots.front_door[1],to=D.spots.sofa[1]+13;return {x:from+(to-from)*g.s,y:FLOOR_Y[0]};}
function drawHomeGuest(ctx){
  const g=socialState.guest;if(!g||g.phase==='scheduled'||sim.place!=='home')return;const n=guestNpc(g);if(!n)return;
  const p=homeGuestPoint(g),sit=g.phase==='visiting',moving=!sit,fr={expr:sit?'happy':'neutral',look:sit?-1:0,bob:moving?Math.floor(realClock*5)%2:0,sway:Math.floor(realClock*3)%2,wave:null};
  ctx.drawImage(npcCanvas(n,fr,sit?'sit':'stand',false),Math.round(p.x-DW/2),Math.round(p.y-DH+1-(sit?4:0)));
  if(!guestBubble.hidden){guestBubble.style.left=view.offsetLeft+p.x*scale+'px';guestBubble.style.top=view.offsetTop+(p.y-DH-8)*scale+'px';}
}
function nextGuestText(pool,seen){let fresh=pool.map((_,i)=>i).filter(i=>!seen.includes(i));if(!fresh.length){seen.splice(0,Math.max(0,seen.length-3));fresh=pool.map((_,i)=>i).filter(i=>!seen.includes(i));}const i=pick(fresh);seen.push(i);return pool[i];}
function tickHomeVisit(dt){
  const g=socialState.guest;if(!g)return;const c=socialState.contacts.find(c=>c.id===g.id);if(!c){socialState.guest=null;guestBubble.hidden=true;return;}
  if(!guestBubble.hidden&&realClock>Number(guestBubble.dataset.until))guestBubble.hidden=true;
  if(g.phase==='scheduled'){
    if(sim.t<g.at)return;
    if(sim.place!=='home'||asleep()||sim.mode==='down'||sim.needs.energy<20||sim.needs.hunger<10){if(sim.t>g.until)endHomeVisit('改天再来。',false);return;}
    g.phase='entering';g.s=0;g.until=sim.t+150;c.lastSeen=sim.t;c.forgotten=false;contactsSig='';log(`${contactName(c)}到了，换好鞋走进客厅。`);showSay(`你来啦，进来坐！`);
  }
  if(g.phase==='entering'||g.phase==='leaving'){
    if(sim.place!=='home'){socialState.guest=null;guestBubble.hidden=true;return;}
    const distance=Math.max(1,Math.abs(D.spots.front_door[1]-D.spots.sofa[1]-13)),direction=g.phase==='entering'?1:-1;
    g.s=Math.max(0,Math.min(1,g.s+direction*WALK*Math.min(speed,4)*dt/distance));
    if(g.phase==='leaving'&&g.s<=0){socialState.guest=null;guestBubble.hidden=true;return;}
    if(g.phase==='entering'&&g.s>=1){g.phase='visiting';g.next=realClock+3;if(!['bath','toilet','cook','eat','sleep'].includes(sim.act)&&!sim.windup)command('host');}return;
  }
  if(sim.place!=='home'||asleep()||sim.mode==='down'||sim.needs.energy<20||sim.needs.hunger<12||hour()>=22){endHomeVisit(sim.place!=='home'?'主角要出门，约好下次再聚。':'先好好照顾自己，我们下次再聊。');return;}
  if(sim.t>=g.until){endHomeVisit();return;}
  if(sim.mode==='idle'&&!sim.windup&&sim.needs.bladder>25&&sim.needs.hunger>30)command('host');
  if(sim.act!=='host'||sim.mode!=='act')return;
  if(g.talk){const tk=g.talk;tk.wait-=dt;if(tk.wait>0)return;
    if(tk.i>=tk.lines.length){g.count++;log(`和${contactName(c)}在家聊起「${tk.title}」。`,null,tk.said);addSocialMemory(c,tk.title,`${contactName(c)}来家里时，${tk.said.map(([,s])=>s).join(' ')}`);g.talk=null;g.next=realClock+8+Math.random()*8;return;}
    const raw=tk.lines[tk.i++],other=raw.startsWith('>'),text=fill(raw.replace(/^>/,''),{主角:nameOf(),朋友:contactName(c)});if(other)homeGuestSay(text,c);else showSay(text);tk.said.push([other?contactName(c)+'：':'',text]);g.said.push([other?contactName(c)+'：':'',text]);tk.wait=3+text.length*.04;return;
  }
  if(realClock<g.next)return;g.usedTalks||=[];g.usedEvents||=[];
  if(Math.random()<.35){const [title,text,say,emo]=nextGuestText(SOCIAL_TEXT.visitEvents,g.usedEvents),vars={朋友:contactName(c)};log(fill(text,vars));showSay(say);addMood('home_guest_event_'+SOCIAL_TEXT.visitEvents.findIndex(row=>row[0]===title),{diary:false,words:false});addSocialMemory(c,title,fill(text,vars));g.next=realClock+14;}
  else {const [title,...lines]=nextGuestText([...SOCIAL_TEXT.visitTalks,...(c.family?[]:SOCIAL_TEXT.conversations[socialLevel(c)])],g.usedTalks);g.talk={title,lines,i:0,wait:.4,said:[]};}
}
function tickSocialLife(dt){
  if(socialDialogHolds()||phoneHolds()||!speed||cardHolds()||wiping)return;
  const day=Math.floor(sim.t/1440);if(socialState.decayDay===null){socialState.decayDay=day;for(const c of socialState.contacts){c.metAt??=sim.t;c.lastSeen??=sim.t;}}
  tickSocialDecay();tickHomeVisit(dt);
  if(!Number.isFinite(socialState.nextVisit))socialState.nextVisit=sim.t+1440;
  if(sim.t<socialState.nextVisit||socialState.guest||!canReceiveCall()||sim.place!=='home'||hour()<10||hour()>=20)return;
  socialState.nextVisit=sim.t+720+Math.random()*720;
  const eligible=sortedContacts().filter(c=>(c.family||c.affinity>=20)&&sim.t-(c.lastVisitOffer??-Infinity)>2*1440);
  if(eligible.length&&Math.random()<.4){const c=pick(eligible);c.lastVisitOffer=sim.t;requestIncomingCall(c.id,'visit');}
}
function showVisitOffer(c){
  const sheet=openSocialSheet(`${contactName(c)}想来坐坐`),p=document.createElement('p');p.textContent=`${contactName(c)}：今天有空吗？想去你家聊聊天，方便的话我就过来。`;sheet.append(p);
  for(const [label,accept]of [['欢迎来坐坐',true],['今天不方便',false]]){const button=document.createElement('button');button.type='button';button.textContent=label;button.onclick=()=>{closeSocialSheet();if(accept)inviteHome(c.id,true);else{socialRejected(c,'的来访邀请被婉拒了');log(`告诉${contactName(c)}今天不方便，改天再约。`);}};sheet.append(button);}
}
function showFarewellOffer(c){
  const sheet=openSocialSheet(`${contactName(c)}想和你说几句话`),p=document.createElement('p');p.textContent=`${contactName(c)}：我们好像很久没好好说过话了。我有点不知道，还该不该再联系你。`;sheet.append(p);
  for(const [label,keep]of [['认真聊聊，留住这段关系',true],['好好告别',false]]){const button=document.createElement('button');button.type='button';button.textContent=label;button.onclick=()=>{closeSocialSheet();if(keep){c.affinity=Math.max(8,c.affinity+5);c.lastContact=sim.t;c.farewellPending=false;contactsSig='';const text=`接住了${contactName(c)}的告别电话，坦诚说开后，决定重新认真联系。`;log(text);addSocialMemory(c,'差一点走散',text);}else removeSocialContact(c,'通完告别电话，两个人决定把这段联系留在过去。');};sheet.append(button);}
}
for(const c of socialState.contacts){c.metAt??=sim.t;c.lastSeen??=sim.t;c.memories||=[];}
