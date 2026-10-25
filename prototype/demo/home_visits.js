// Guest movement, family travel and overnight stays share one saved visit state.
D.spots.guest_seat=D.spots.guest_study;
ACTS.guest_seat={spot:'guest_seat',label:'坐客椅歇会儿',emote:null,dur:25,log:'在书房的客椅上坐了一会儿。'};
EFFECT.guest_seat={energy:.04,fun:.08};D.seatLifts.guest_seat=4;
const cForGuest=g=>socialState.contacts.find(c=>c.id===g?.id);
let visitSleepPreview=null;
function previewSleepScene(choice){
  if(!booted)return false;
  if(card||phoneHolds()||wardrobeOpen||guideOn){showHint('先处理或关闭眼前的窗口，再打开睡眠测试。');return false;}
  if(!visitSleepPreview){
    visitSleepPreview={snapshot:JSON.parse(JSON.stringify(snapshot())),autosave:prefs.autosave,weatherForce:weather.force,weatherKind:weather.kind};
    if(prefs.autosave)store.save(visitSleepPreview.snapshot).catch(error=>console.warn('Could not preserve pre-preview save',error));
  }
  prefs.autosave=false;stopNpcTalk();closeSocialSheet();closeRing();closePicker();setContactsOpen(false);hidePeerSay(true);setNeedsOpen(false);
  remoteSocial=null;sim.windup=null;sim.chosen=null;sim.item=null;sim.queue=[];sim.down=null;sim.player=false;sim.nap=false;
  sim.t=Math.floor(visitSleepPreview.snapshot.sim.t/1440)*1440+22.5*60;sim.place='home';sim.act='sleep';sim.mode='act';sim.actEnd=sim.t+900;
  for(const key in sim.needs)sim.needs[key]=85;moods.clear();weather.force='clear';weather.kind='clear';
  let c=socialState.contacts.find(c=>!c.family&&!c.child&&doll.normalize(c.look).gender===look.gender);
  if(!c){c={id:'preview_friend',name:look.gender==='m'?'阿布':'小雨',look:doll.normalize(doll.PRESETS[look.gender]),affinity:75,memories:[]};socialState.contacts.push(c);}
  c.affinity=75;const berth=choice==='chat'?'shared':choice;
  const hero=berth==='hero-sofa'?D.spots.sofa:D.spots.bed;sim.sleepPlace=berth==='hero-sofa'?'sofa':'bed';sim.route=[[hero[1],FLOOR_Y[hero[0]]]];sim.s=sim.target=0;
  const point=berth==='guest-sofa'?{x:D.spots.sofa[1]+9,y:FLOOR_Y[0]}:{x:D.spots.bed[1]+10,y:FLOOR_Y[1]};
  socialState.guest={id:c.id,phase:'visiting',at:sim.t,arrivedAt:sim.t,until:sim.t+720,s:1,position:point,walkS:0,walkLength:0,next:Infinity,count:0,said:[],sleeping:true,sleepAt:sim.t,
    overnight:{accepted:true,berth,until:sim.t+720,bedTalkDone:choice!=='chat'}};
  lamps.bed_lamp=false;lamps.floor_lamp=false;socialState.nextCall=socialState.nextVisit=Infinity;speed=0;
  popSay.hidden=true;if(choice==='chat')tickBedConversation(socialState.guest,c,1);
  document.getElementById('sleepPreviewNote').hidden=false;
  for(const button of document.querySelectorAll('[data-sleep-preview]'))button.setAttribute('aria-pressed',String(button.dataset.sleepPreview===choice));
  contactsSig='';syncUI();render();return true;
}
function exitSleepScenePreview(){
  if(!visitSleepPreview)return;const previous=visitSleepPreview;
  restore(previous.snapshot);prefs.autosave=previous.autosave;weather.force=previous.weatherForce;weather.kind=previous.weatherKind;visitSleepPreview=null;
  document.getElementById('sleepPreviewNote').hidden=true;
  for(const button of document.querySelectorAll('[data-sleep-preview]'))button.setAttribute('aria-pressed','false');
  syncUI();render();
}
for(const button of document.querySelectorAll('[data-sleep-preview]'))button.onclick=()=>previewSleepScene(button.dataset.sleepPreview);
document.getElementById('exitSleepPreview').onclick=exitSleepScenePreview;
function parentVisitPlan(c,proactive){
  const period=Math.floor(sim.t/(7*1440)),resting=hour()<8||hour()>=21;
  if(!proactive&&!resting&&c.parentVisitRoll?.period!==period)c.parentVisitRoll={period,available:Math.random()<.03};
  if(!proactive&&(resting||!c.parentVisitRoll?.available)){
    const text=pick(HOME_VISIT_TEXT.parents[c.family].decline);
    showSay(text,contactName(c)+'：',c);log(`约${contactName(c)}来家里坐坐，但两座城市隔着路程，这次没能成行。`,null,[[contactName(c)+'：',text]]);
    addSocialMemory(c,'隔着城市的邀请',text);return null;
  }
  if(c.parentLastVisit!==null&&c.parentLastVisit!==undefined&&sim.t-c.parentLastVisit<7*1440){
    showSay('刚回去没几天呢，来回跑也得缓缓呀。咱先打电话聊，下回再去看你。',contactName(c)+'：',c);return null;
  }
  let at=sim.t+120+Math.floor(Math.random()*121);
  if(at%1440>=20*60)at=(Math.floor(at/1440)+1)*1440+10*60;
  const when=(Math.floor(at/1440)>Math.floor(sim.t/1440)?'明天':'今天')+fmt(at);
  c.parentVisitRoll={period,available:false};
  return {minutes:Math.ceil(at-sim.t),reply:fill(pick(HOME_VISIT_TEXT.parents[c.family].accept),{到达时间:when})};
}
function familyMayOfferVisit(c){return sim.t-(c.parentLastVisit??-Infinity)>14*1440&&Math.random()<.015;}

function visitRoomTarget(room){
  const p=here();
  if(room==='study')return {x:sim.act==='guest_seat'?D.spots.computer[1]-15:D.spots.guest_study[1],y:FLOOR_Y[1]};
  if(room==='bedroom')return {x:D.spots.bed[1]+37,y:FLOOR_Y[1]};
  if(room==='kitchen')return {x:D.spots.eat[1]+15,y:FLOOR_Y[0]};
  return {x:D.spots.sofa[1]+13,y:FLOOR_Y[0]};
}
function homeGuestDestination(g){
  const o=g.overnight;
  if(o?.accepted&&o.berth&&!o.morning&&(hour()>=21||hour()<6||sim.act==='sleep')){
    return o.berth==='guest-sofa'?{x:D.spots.sofa[1]+9,y:FLOOR_Y[0]}:{x:D.spots.bed[1]+10,y:FLOOR_Y[1]};
  }
  const heroRoom=roomAt(here()),room=heroRoom==='stairs'?(g.lastHeroRoom||'living'):['living','kitchen','study','bedroom'].includes(heroRoom)&&!asleep()?heroRoom:'living';
  if(g.lastHeroRoom!==room){g.lastHeroRoom=room;g.roamRoom=null;g.roamStage=null;g.roamUntil=0;g.roamAt=sim.t+12+Math.random()*14;}
  if(g.roamRoom&&(g.roamStage==='walking'||sim.t<g.roamUntil))return visitRoomTarget(g.roamRoom);
  g.roamRoom=null;
  if(sim.t>=(g.roamAt??Infinity)&&!g.talk&&!(g.walkS<g.walkLength)){
    g.roamAt=sim.t+16+Math.random()*18;
    if(Math.random()<.28){g.roamRoom=pick(['living','kitchen','study',...(!asleep()?['bedroom']:[])].filter(r=>r!==room));g.roamStage='walking';g.roamUntil=0;const c=cForGuest(g);if(c&&!remoteSocial)showSay(({living:'我去沙发那儿坐会儿啊。',kitchen:'我去倒点水啊。',study:'我去那边看看书啊。',bedroom:'我去里面转转，一会儿出来。'})[g.roamRoom],contactName(c)+'：',c);return visitRoomTarget(g.roamRoom);}
  }
  return visitRoomTarget(room);
}

function canStayOver(c){return !!c&&!c.family&&!c.child&&c.affinity>=60&&c.affinity<=90&&doll.normalize(c.look).gender===look.gender;}
function showOvernightChoice(g,c,kind){
  const sheet=openSocialSheet(kind==='invite'?`${contactName(c)}想在你家过夜，可以吗？`:`${contactName(c)}：今晚我睡哪里呀？`);
  sheet.classList.add('overnight-sheet');sheet.dataset.nightKind=kind;sheet.querySelector('.social-sheet-close').remove();
  const avatar=document.createElement('canvas');avatar.width=avatar.height=40;avatar.className='overnight-avatar';drawContactAvatar(avatar,c);avatar.setAttribute('aria-label',contactName(c)+'的头像');
  const badge=document.createElement('span');badge.className='overnight-badge';badge.textContent=kind==='invite'?'留宿邀请':'今晚的安排';
  sheet.prepend(avatar,badge);const actions=document.createElement('div');actions.className='overnight-actions';
  const choices=kind==='invite'?[['接受','accept'],['拒绝','decline']]:[['你睡沙发','guest-sofa'],['我睡沙发','hero-sofa'],['一起睡吧','shared']];
  actions.style.setProperty('--night-choices',choices.length);
  for(const [label,value]of choices){const button=document.createElement('button');button.type='button';button.textContent=label;button.dataset.choice=value;button.onclick=()=>resolveOvernightChoice(g.id,kind,value);actions.append(button);}
  sheet.append(actions);actions.firstElementChild.focus({preventScroll:true});
}
function resolveOvernightChoice(id,kind,value){
  const g=socialState.guest,c=cForGuest(g);if(!g||g.id!==id||!c)return;closeSocialSheet();
  const o=g.overnight;
  if(kind==='invite'){
    if(value==='decline'){o.accepted=false;o.declined=true;showSay(pick(HOME_VISIT_TEXT.stayDecline),contactName(c)+'：',c);log(`婉拒了${contactName(c)}的留宿请求，约好下次再聚。`);return;}
    o.accepted=true;o.until=(Math.floor(sim.t/1440)+1)*1440+10*60;g.until=o.until;g.talk=null;
    showSay(pick(HOME_VISIT_TEXT.stayAccept),contactName(c)+'：',c);addSocialMemory(c,'答应留宿',`答应让${contactName(c)}在家留宿一晚。`);log(`${contactName(c)}今晚留宿，先把洗漱和睡觉的位置慢慢安排好。`);
  }else if(['guest-sofa','hero-sofa','shared'].includes(value)){
    o.berth=value;g.talk=null;g.sleeping=false;g.destination=null;
    const label={'guest-sofa':'朋友睡沙发，主角睡床','hero-sofa':'把床让给朋友，主角睡沙发',shared:'两个人一起睡床，各盖各的被子'}[value];
    log(`今晚的安排：${label}。`);addSocialMemory(c,'今晚睡哪里',label);showSay(pick(HOME_VISIT_TEXT.berth[value]),contactName(c)+'：',c);
    if(sim.act==='sleep')startAct('sleep');
  }
  autoSave();
}
function sleepoverChatAwake(){
  const g=socialState.guest,o=g?.overnight;
  return !!(g?.phase==='visiting'&&o?.accepted&&o.berth==='shared'&&!o.morning&&!o.bedTalkDone&&sim.place==='home'&&sim.mode==='act'&&sim.act==='sleep'&&(hour()>=20||hour()<5));
}
function sleepoverSharedBed(){const g=socialState.guest;return !!(g?.phase==='visiting'&&g.overnight?.accepted&&g.overnight.berth==='shared');}
function heroSleepTarget(){return socialState.guest?.phase==='visiting'&&socialState.guest.overnight?.accepted&&socialState.guest.overnight.berth==='hero-sofa'?D.spots.sofa:D.spots.bed;}
function heroSleepingOnSofa(){return sim.act==='sleep'&&(sim.sleepPlace==='sofa'||sim.sleepPlace!=='bed'&&heroSleepTarget()===D.spots.sofa);}
function onSleepoverBedArrival(){
  sim.sleepPlace=heroSleepTarget()===D.spots.sofa?'sofa':'bed';
  const g=socialState.guest;
  if(heroSleepingOnSofa()){lamps.floor_lamp=false;log('把床让给朋友，自己抱着枕头在沙发上躺好了。');}
  if(g?.overnight?.accepted&&!g.overnight.berth&&!socialDialogHolds())showOvernightChoice(g,cForGuest(g),'berth');
}
function finishBedConversation(g,early=false){
  if(!g?.overnight)return;const c=cForGuest(g),tk=g.bedTalk;
  if(c&&tk?.said?.length){log(`和${contactName(c)}躺下后聊起「${tk.title}」。`,null,tk.said);addSocialMemory(c,'枕边闲聊 · '+tk.title,tk.said.map(([,s])=>s).join(' '));}
  g.bedTalk=null;g.overnight.bedTalkDone=true;hidePeerSay();
  if(early)showSay('先睡啦，剩下的明天接着说。');
}
function tickBedConversation(g,c,dt){
  if(!g.bedTalk){
    c.bedTalkSeen||=[];const row=nextGuestText(HOME_VISIT_TEXT.bedTalks,c.bedTalkSeen);
    g.bedTalk={title:row[0],lines:row.slice(1),i:0,wait:.8,said:[]};
  }
  const tk=g.bedTalk;tk.wait-=dt;if(tk.wait>0)return;
  if(tk.i>=tk.lines.length){
    log(`和${contactName(c)}躺下后聊起「${tk.title}」。`,null,tk.said);addSocialMemory(c,'枕边闲聊 · '+tk.title,tk.said.map(([,s])=>s).join(' '));
    g.bedTalk=null;g.overnight.bedTalkCount=(g.overnight.bedTalkCount||0)+1;
    if(g.overnight.bedTalkCount>=2){g.overnight.bedTalkDone=true;finishContactTalk(c.id,'visit-chat');hidePeerSay();}return;
  }
  const raw=tk.lines[tk.i++],other=raw.startsWith('>'),text=raw.replace(/^>/,'');
  showSay(text,other?contactName(c)+'：':'',other?c:null);tk.said.push([other?contactName(c)+'：':'',text]);tk.wait=Math.max(2.8,Math.min(5,2+text.length*.08));
}
function tickOvernightVisit(g,c,dt){
  if(sim.place!=='home'||sim.mode==='down')return false;
  if(!g.overnight&&canStayOver(c)&&hour()>=18&&hour()<21.5&&sim.t-(g.arrivedAt??g.at)>=25){
    g.nextStayCheck??=sim.t+5+Math.random()*10;
    if(sim.t>=g.nextStayCheck&&!g.talk&&!remoteSocial&&!sim.talk&&!socialDialogHolds()){
      g.nextStayCheck=sim.t+20;if(Math.random()<.16){g.overnight={accepted:false,offered:true,offeredAt:sim.t};showOvernightChoice(g,c,'invite');return true;}
    }
  }
  const o=g.overnight;if(!o||o.declined)return false;
  if(!o.accepted){if(o.offered&&!socialDialogHolds())showOvernightChoice(g,c,'invite');return true;}
  if(!o.berth&&(hour()>=21||hour()<5||sim.act==='sleep')){if(!socialDialogHolds())showOvernightChoice(g,c,'berth');return true;}
  if(g.sleeping&&sim.t>=(g.sleepAt??sim.t)+180&&hour()>=7&&hour()<18){
    g.sleeping=false;o.morning=true;o.bedTalkDone=true;g.bedTalk=null;g.destination=null;
    log(`${contactName(c)}起床了，昨晚的留宿成了两个人的新回忆。`);addSocialMemory(c,'在家留宿了一晚',HOME_VISIT_TEXT.morning[0]);showSay(pick(HOME_VISIT_TEXT.morning),contactName(c)+'：',c);
  }
  if(sim.t>=o.until){endHomeVisit('睡了一晚，收拾好东西，约好下回再来。');return true;}
  if(o.berth&&!o.morning&&!g.sleeping&&(hour()>=21||hour()<6||sim.act==='sleep')){
    const target=homeGuestDestination(g),p=homeGuestPoint(g);
    if(Math.hypot(p.x-target.x,p.y-target.y)<1){g.sleeping=true;g.sleepAt=sim.t;g.talk=null;if(o.berth==='hero-sofa')lamps.bed_lamp=false;log(`${contactName(c)}在${o.berth==='guest-sofa'?'沙发':'床'}上躺好了。`);}
  }
  if(g.sleeping&&sleepoverChatAwake())tickBedConversation(g,c,dt);
  return !!g.sleeping;
}

function restoreHomeVisitProgress(g,raw){
  if(!g||!raw)return;
  for(const key of ['arrivedAt','nextStayCheck','sleepAt','roamAt','roamUntil'])if(Number.isFinite(raw[key]))g[key]=raw[key];
  g.familyTrip=raw.familyTrip===true;g.sleeping=raw.sleeping===true;
  if(raw.position&&Number.isFinite(raw.position.x)&&Number.isFinite(raw.position.y))g.position={x:Math.max(8,Math.min(W-8,raw.position.x)),y:Math.max(FLOOR_Y[1],Math.min(FLOOR_Y[0],raw.position.y)),dy:0};
  const oldTalk=raw.bedTalk,row=oldTalk&&HOME_VISIT_TEXT.bedTalks.find(r=>r[0]===oldTalk.title);
  if(row)g.bedTalk={title:row[0],lines:row.slice(1),i:Number.isInteger(oldTalk.i)?Math.max(0,Math.min(row.length-1,oldTalk.i)):0,wait:.8,said:Array.isArray(oldTalk.said)?oldTalk.said.filter(v=>Array.isArray(v)&&v.length===2&&v.every(s=>typeof s==='string')).slice(-4):[]};
  const o=raw.overnight;
  if(o&&typeof o==='object')g.overnight={accepted:o.accepted===true,offered:o.offered===true,declined:o.declined===true,
    berth:['guest-sofa','hero-sofa','shared'].includes(o.berth)?o.berth:null,until:Number.isFinite(o.until)?o.until:sim.t+720,
    morning:o.morning===true,bedTalkDone:o.bedTalkDone===true,bedTalkCount:Number.isInteger(o.bedTalkCount)?Math.max(0,Math.min(2,o.bedTalkCount)):0};
  g.sleeping=g.sleeping&&!!g.overnight?.accepted&&!!g.overnight?.berth;
}

function guestLyingCanvas(g,c,expr,headOnly=false){
  const n=guestNpc(g),src=npcCanvas(n,{expr,look:0,bob:0,sway:0,wave:null},'stand',false),height=headOnly?15:DH;
  const key=expr+'_'+headOnly,cache=n.sleepCache||=new Map();if(cache.has(key))return cache.get(key);
  const canvas=document.createElement('canvas');canvas.width=height;canvas.height=DW;
  const ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.translate(0,DW);ctx.rotate(-Math.PI/2);ctx.drawImage(src,0,0,DW,height,0,0,DW,height);cache.set(key,canvas);return canvas;
}
function drawSleepoverBedding(ctx){
  if(sleepoverSharedBed()){const [x,y]=D.sleepover.bed;ctx.drawImage(IMG.fx.shared_bed[0],x,y);ctx.drawImage(IMG.fx.shared_cover[0],x,y);}
}
function drawSofaSleeper(ctx,canvas){
  const [x,y]=D.sleepover.sofa;ctx.fillStyle='#ede8dd';ctx.fillRect(x,y+1,13,16);ctx.drawImage(canvas,x,y);ctx.drawImage(IMG.fx.sofa_blanket[0],x+15,y+4);
}
function drawSleepingGuest(ctx,g,c){
  if(!g.sleeping||!c)return false;
  if(g.overnight.berth==='shared'&&sim.mode==='act'&&sim.act==='sleep')return true;
  if(g.overnight.berth==='guest-sofa')drawSofaSleeper(ctx,guestLyingCanvas(g,c,'sleepy'));
  else if(g.overnight.berth==='shared'){const [x,y]=D.sleepover.bed;ctx.drawImage(guestLyingCanvas(g,c,'sleepy',true),x+1,y+9);ctx.drawImage(IMG.fx.shared_cover[0],x,y);}
  else{ctx.drawImage(guestLyingCanvas(g,c,'sleepy',true),...D.sleepLying);drawOverlay(ctx,'sleep_cover');}
  return true;
}
function drawHeroSleepover(ctx,full){
  if(heroSleepingOnSofa()){drawSofaSleeper(ctx,lyingBody({...full,expr:'sleepy',look:0,bob:0,sway:0,wave:null}));return true;}
  const g=socialState.guest,c=cForGuest(g);
  if(!sleepoverSharedBed()||!c)return false;
  const [x,y]=D.sleepover.bed,expr=sleepoverChatAwake()?'neutral':'sleepy';
  // Same vertical position; the rear head is only 3px left, drawn first.
  if(g.sleeping)ctx.drawImage(guestLyingCanvas(g,c,expr,true),x+1,y+9);
  ctx.drawImage(lyingHead({...full,expr,look:0,bob:0,sway:0,wave:null}),x+4,y+9);
  ctx.drawImage(IMG.fx.shared_cover[0],x,y);return true;
}
