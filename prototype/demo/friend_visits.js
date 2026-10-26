// Real visits use the same native house assets as the gallery, with their own
// routing/state. No temporary changes to the hero's rooms, furniture or spots.
let friendVisit=null;
let friendHomes=Object.create(null);
let friendHomeSeed=Math.floor(Math.random()*4294967296)>>>0;
const atFriendHome=()=>sim.place==='friend_home'&&friendVisit?.phase==='inside';
const visitingFriend=()=>friendVisit&&socialState.contacts.find(c=>c.id===friendVisit.id);
const visitingHouse=()=>atFriendHome()?D.friendHouses[friendVisit.houseId]:null;
const sceneHouseHeight=()=>friendHousePreview?D.friendHouses[friendHousePreview.id].h:visitingHouse()?.h||H;
OUT.friend_home={img:{},kind:'walk',doorX:171,feet:108,walk:[6,336]};
TRIP_COL.friend_home='#759bc9';TRIP_MOTIF.friend_home=TRIP_MOTIF.home;
ACTS.friend_visit={label:'在朋友家做客',spot:null,dur:30};
const FRIEND_VISIT_ACTS={chat:'聊天',sit:'坐一会儿',eat:'吃点东西',toilet:'使用卫生间',bath:'洗漱',sleep:'睡觉',walk:'走动',leave:'向朋友道别'};
function friendHomeFor(c){
 const key=c.family?'parents':c.id;
 if(friendHomes[key]&&Object.hasOwn(D.friendHouses,friendHomes[key].houseId))return friendHomes[key];
 const keys=Object.keys(D.friendHouses),houseId=c.family?'maple':keys[hashOf(friendHomeSeed+':'+key)%keys.length];
 const beds=D.friendHouses[houseId].furniture.filter(f=>f.kind==='bed').length;
 // One bed belongs to the host. A second room holds either the parents who
 // share a bed, or one adult sibling. Residents never occupy the guest's sofa.
 const roll=hashOf(key+':family:'+friendHomeSeed),relations=beds<2||c.family?[]:roll%3===0?['爸爸','妈妈']:[['哥哥','姐姐','弟弟','妹妹'][roll%4]];
 return friendHomes[key]={houseId,relations};
}
function restoreFriendHomes(data){
 friendHomeSeed=Number.isInteger(data?.homeSeed)?data.homeSeed>>>0:friendHomeSeed;friendHomes=Object.create(null);
 for(const [key,value]of Object.entries(data?.homes||{})){
  if(!/^[-a-zA-Z0-9_]{1,64}$/.test(key)||!value||!Object.hasOwn(D.friendHouses,value.houseId))continue;
  const beds=D.friendHouses[value.houseId].furniture.filter(f=>f.kind==='bed').length;
  const allowed=['爸爸','妈妈','哥哥','姐姐','弟弟','妹妹'];
  let relations=Array.isArray(value.relations)?[...new Set(value.relations.filter(r=>allowed.includes(r)))]:[];
  if(beds<2)relations=[];else if(relations.length>1)relations=relations.includes('爸爸')&&relations.includes('妈妈')?['爸爸','妈妈']:relations.slice(0,beds-1);
  friendHomes[key]={houseId:value.houseId,relations};
 }
 friendVisit=null;
}
function friendVisitSnapshot(){
 if(friendVisit?.phase==='departing')return {id:friendVisit.id,phase:'departing'};
 if(!atFriendHome())return null;
 const p=here(),v=friendVisit;
 return {id:v.id,houseId:v.houseId,phase:'inside',arrived:v.arrived,until:v.until,position:[p.x,p.y],stay:!!v.stay,askedDay:v.askedDay??null,action:sim.mode==='act'?v.action:null,objectId:v.objectId||null,seatId:v.seatId||null,lamps:v.lamps||{},mealItem:v.mealItem||null,bedIndex:v.bedIndex??null,seen:v.seen.slice(-100),familySeen:v.familySeen.slice(-100),present:v.present||[],count:v.count};
}
function restoreFriendVisit(raw){
 if(sim.place!=='friend_home'){
  friendVisit=null;const c=socialState.contacts.find(c=>c.id===raw?.id);
  if(raw?.phase==='departing'&&sim.place==='home'&&c&&sim.mode!=='down'){
   friendVisit={id:c.id,houseId:friendHomeFor(c).houseId,phase:'departing'};sim.dest='friend_home';sim.mode='idle';sim.act=null;sim.queue=[];sim.windup={act:'go_out',at:realClock+1};sim.player=true;
  }
  return;
 }
 const c=socialState.contacts.find(c=>c.id===raw?.id),home=c&&friendHomeFor(c);
 if(!c||!home||raw?.phase!=='inside'){
  friendVisit=null;sim.place='home';sim.route=[[D.spots.front_door[1],FLOOR_Y[0]]];sim.s=sim.target=0;sim.mode='idle';sim.act=null;return;
 }
 const h=D.friendHouses[home.houseId];
 friendVisit={id:c.id,houseId:home.houseId,phase:'inside',arrived:Number.isFinite(raw.arrived)?raw.arrived:sim.t,until:Number.isFinite(raw.until)?raw.until:sim.t+180,stay:raw.stay===true,askedDay:Number.isInteger(raw.askedDay)?raw.askedDay:null,action:null,next:realClock+8,seen:Array.isArray(raw.seen)?raw.seen.filter(s=>typeof s==='string').slice(-100):[],familySeen:Array.isArray(raw.familySeen)?raw.familySeen.filter(s=>typeof s==='string').slice(-100):[],count:Number.isFinite(raw.count)?raw.count:0};
 const savedDown=sim.mode==='down'?sim.down:null;
 const p=Array.isArray(raw.position)&&raw.position.length===2&&raw.position.every(Number.isFinite)?raw.position:[(W-h.w)/2+h.entry[0],h.entry[1]];
 const off=(W-h.w)/2,r=friendVisitRoom(h,p[0]-off,p[1]);
 sim.route=[[Math.max(off+r.x+5,Math.min(off+r.x+r.w-5,p[0])),r.floor]];sim.s=sim.target=0;sim.mode=savedDown?'down':'idle';sim.act=savedDown?null:'friend_visit';sim.windup=null;sim.down=savedDown;
 friendVisit.present=Array.isArray(raw.present)?raw.present.filter(r=>home.relations.includes(r)):null;
 initFriendHomeActors();
 friendVisit.lamps=Object.fromEntries(Object.entries(raw.lamps||{}).filter(([id,on])=>h.furniture.some(f=>f.id===id&&['lamp','floor_lamp'].includes(f.kind))&&typeof on==='boolean'));
 if(!savedDown&&typeof raw.action==='string'&&Object.hasOwn(FRIEND_VISIT_ACTS,raw.action)&&!(raw.action==='sleep'&&!friendVisit.stay)){
  const object=h.furniture.find(f=>f.id===raw.objectId);startFriendHouseAction(raw.action,object,raw.mealItem&&typeof raw.mealItem==='object'?raw.mealItem:null);
 }
 if(booted){fit();makeRoom();}
}
function friendVisitRoom(h,x,y){return h.rooms.reduce((best,r)=>{
 const distance=Math.abs(y-r.floor)*4+Math.max(r.x-x,0,x-(r.x+r.w));return !best||distance<best.d?{r,d:distance}:best;
 },null).r;}
function friendVisitRoute(from,to){
 const h=visitingHouse(),off=(W-h.w)/2,a=friendVisitRoom(h,from.x-off,from.y),b=friendVisitRoom(h,to.x-off,to.y),q=[a.id],prev=new Map([[a.id,null]]);
 for(let i=0;i<q.length&&!prev.has(b.id);i++)for(const link of h.links){const id=link.from===q[i]?link.to:link.to===q[i]?link.from:null;if(id&&!prev.has(id)){prev.set(id,{id:q[i],link});q.push(id);}}
 if(!prev.has(b.id))return [[from.x,from.y]];
 const chain=[];for(let id=b.id;prev.get(id);id=prev.get(id).id)chain.unshift({id,...prev.get(id)});
 const route=[[from.x,from.y]];let current=a;
 for(const edge of chain){const next=h.rooms.find(r=>r.id===(edge.link.from===current.id?edge.link.to:edge.link.from));
  route.push([off+edge.link.x,current.floor]);if(edge.link.kind==='stairs')route.push([off+edge.link.x,next.floor]);current=next;
 }
 route.push([to.x,to.y]);return route;
}
function visitActor(c){return {look:c.look,ramps:doll.rampsOf(c.look),cache:new Map(),kid:false};}
function initFriendHomeActors(){
 const v=friendVisit,c=visitingFriend(),h=visitingHouse();if(!v||!c||!h)return;
 const off=(W-h.w)/2,bedrooms=h.rooms.filter(r=>['bed','guest_bed','tatami'].includes(r.role));
 const hostRoom=h.rooms.find(r=>['living','tea','dining'].includes(r.role))||bedrooms[0];
 v.host={npc:visitActor(c),x:off+hostRoom.x+Math.min(hostRoom.w-15,40),y:hostRoom.floor,room:hostRoom.id,next:sim.t+30};
 const home=friendHomeFor(c),beds=h.furniture.filter(f=>f.kind==='bed').length;
 if(!Array.isArray(v.present))v.present=home.relations.filter(()=>Math.random()<.8);
 const present=beds<2?[]:v.present.filter(r=>home.relations.includes(r));
 v.family=present.map((relation,i)=>{
  const gender=['爸爸','哥哥','弟弟'].includes(relation)?'m':'f',seed=hashOf(c.id+relation+friendHomeSeed),pool=socialState.world.filter(p=>p.look.gender===gender&&!p.child),source=pool[seed%pool.length];
  const speaker={id:'resident_'+c.id+'_'+i,name:contactName(c)+'的'+relation,look:doll.normalize({...source.look,name:relation,acc:source.look.acc||[]}),affinity:0};
  const room=h.rooms.filter(r=>!['bath','laundry','stair','entry_stair'].includes(r.role))[(seed+i)%h.rooms.filter(r=>!['bath','laundry','stair','entry_stair'].includes(r.role)).length];
  return {relation,speaker,npc:visitActor(speaker),x:off+room.x+Math.max(12,room.w-22-i*18),y:room.floor,room:room.id,next:sim.t+35+i*20};
 });
}
function friendVisitRestReply(c){
 const h=hour();if(h>=8&&h<23)return false;
 const lines=h>=23||h<5?['我已经钻被窝啦，今天先不招待你了，明天来呗','眼睛都快睁不开了……咱明天再见吧','刚关灯呢，今天让我先睡，改天来坐坐','我这边准备睡啦，你也早点休息，明天再约']
  :['我还没起呢……等我睡醒再来吧','这么早呀？我还裹着被子呢，晚点再约嘛','还没洗漱，家里也没收拾好，等白天再来呗'];
 showSay(pick(lines),contactName(c)+'：',c);log(`想去${contactName(c)}家坐坐，对方正在休息，约好晚点再联系。`);return true;
}
function requestFriendVisit(id,incoming=false){
 const c=socialState.contacts.find(c=>c.id===id);if(!c)return false;
 if(c.family){showHint('老家离这里太远了。');return false;}
 if(friendVisit&&(!atFriendHome()||c.id===friendVisit.id)){showHint(atFriendHome()?'已经在这位朋友家啦。':'正在去朋友家的路上，稍等一下吧。');return false;}
 let reason=friendHousePreview?'先退出房屋预览，再出发吧。':socialState.guest?'家里还有客人，先陪完客人再出门吧。':friendOutingState?'已经约好一起出门，先结束同行吧。':asleep()||sim.mode==='down'||wiping||cardHolds()?'先忙完眼前的事情，再去做客吧。':c.child?'小朋友还不能自己安排接待，先和家里人说好吧。':null;
 if(reason){if(c&&!friendHousePreview)showSay(reason,contactName(c)+'：',c);else showHint(reason);return false;}
 if(friendVisitRestReply(c))return false;
 const home=friendHomeFor(c);closeSocialSheet();setContactsOpen(false);closeRing();closePicker();hidePeerSay(true);stopNpcTalk();
 const nextVisit={id,houseId:home.houseId,phase:'departing',incoming};
 if(atFriendHome()){
  const previous=visitingFriend();finishContactTalk(previous.id,'visit');addSocialMemory(previous,'去家里做客','坐了一会儿，和朋友道别后去了下一位朋友家。');
  log(`和${contactName(previous)}道别，接着去${contactName(c)}家坐坐。`);enterFriendHome(nextVisit);return true;
 }
 friendVisit=nextVisit;
 log(`准备去${contactName(c)}家做客。`);showSay(incoming?'好，我收拾一下就出门。':'去你家坐会儿，给我留个位置啊。');
 if(sim.place==='home'){sim.dest='friend_home';command('go_out');}else enterFriendHome();
 return true;
}
function relayoutFriendVisit(change){
 const old=housePreviewRects(),r=view.getBoundingClientRect();friendHouseAnimations.forEach(a=>a.cancel());friendHouseAnimations=[];
 change();fit();makeRoom();render();animateHousePreviewLayout(old,r.bottom,r.height);fitWindow();
}
function friendDestinationIcon(c){
 const canvas=document.createElement('canvas');canvas.width=canvas.height=25;const x=canvas.getContext('2d');x.imageSmoothingEnabled=false;
 x.fillStyle='#f7f6fb';x.fillRect(0,0,25,25);x.drawImage(npcCanvas(visitActor(c),{expr:'neutral',look:0,bob:0,sway:0,wave:null},'stand'),2,4);
 const pixels=x.getImageData(0,0,25,25);for(let y=0;y<25;y++)for(let i=0;i<25;i++){
  const distance=Math.hypot(i-12,y-12),p=(y*25+i)*4;
  if(distance>12)pixels.data[p+3]=0;
  else if(distance>11){pixels.data[p]=51;pixels.data[p+1]=37;pixels.data[p+2]=59;pixels.data[p+3]=255;}
 }x.putImageData(pixels,0,0);
 x.fillStyle='#334861';x.fillRect(15,17,10,8);x.fillStyle='#f2ead9';x.fillRect(16,18,8,6);x.fillStyle='#547fa8';x.fillRect(19,20,3,4);
 for(let row=0;row<4;row++){x.fillStyle=row===3?'#eef5fc':'#395c86';x.fillRect(14+row,18-row,11-row*2,1);}x.fillStyle='#e9cb7e';x.fillRect(17,20,1,2);return canvas;
}
function friendHouseWindows(){
 const h=visitingHouse(),off=(W-h.w)/2;
 return Object.fromEntries(IMG.friendHouses[friendVisit.houseId].windows.map((w,i)=>['friend_window_'+i,{...w,x:w.x+off}]));
}
function enterFriendHome(nextVisit=friendVisit){
 const v=nextVisit,c=v&&socialState.contacts.find(c=>c.id===v.id);if(!v||!c||v.phase!=='departing')return;
 if(friendVisitRestReply(c)){if(friendVisit===v)friendVisit=null;sim.dest=null;sim.mode='idle';sim.act=null;sim.idleUntil=sim.t+1;return;}
 onPetSceneChanged("friend_home");
 closeRing();closePicker();sim.windup=null;sim.queue=[];sim.talk=null;sim.chosen=null;remoteSocial=null;sim.mode='idle';sim.act=null;
 if(sim.place==='mall'){mallS.stop=mallS.goal=mallS.hover=mallS.pointer=mallS.toilet=mallS.emergency=mallS.visit=mallS.foodFront=mallS.menuShop=null;}
 hoverId=null;glow=null;walkMark=null;
 const icon=friendDestinationIcon(c);
 trip('friend_home',()=>{
  relayoutFriendVisit(()=>{
   friendVisit=v;sim.place='friend_home';sim.park=null;sim.bar=null;barScene=null;sim.crossing=[];sim.sleepPlace=null;v.phase='inside';v.arrived=sim.t;v.until=Math.min(sim.t+240,Math.floor(sim.t/1440)*1440+23*60);v.stay=false;v.seen=[];v.familySeen=[];v.count=0;v.next=realClock+7;v.action=null;
   const h=visitingHouse();sim.route=[[(W-h.w)/2+h.entry[0],h.entry[1]]];sim.s=sim.target=0;sim.mode='idle';sim.act='friend_visit';sim.idleUntil=sim.t+2;initFriendHomeActors();
  });
  life.npcs=[];life.talkQ=null;clearNpcPills();log(`到了${contactName(c)}家，${visitingHouse().name}里收拾得挺舒服。`);addSocialMemory(c,'去家里做客',`认真看了看${contactName(c)}家的陈设，坐下聊了会儿。`);showSay(pick(FRIEND_VISIT_TEXT.welcome),contactName(c)+'：',c);c.lastSeen=c.lastContact=sim.t;c.forgotten=false;contactsSig='';
 });
 if(tripRun)tripRun.destinationIcon=icon;
}
function leaveFriendHome(reason='玩得差不多了，和朋友说声下次再来。'){
 if(!atFriendHome()||wiping)return false;
 const c=visitingFriend();closeRing();closePicker();closeSocialSheet();friendVisit.talk=null;hidePeerSay(true);
 log(reason);if(c){addSocialMemory(c,'到家里做客',`去了${contactName(c)}家。${reason}`);finishContactTalk(c.id,'visit');}
 trip('home',()=>{relayoutFriendVisit(()=>{
  friendVisit=null;sim.place='home';sim.route=[[D.spots.front_door[1],FLOOR_Y[0]]];sim.s=sim.target=0;sim.mode='idle';sim.act=null;sim.windup=null;sim.queue=[];sim.chosen=null;sim.player=false;sim.idleUntil=sim.t+2;sim.outBack=null;sim.outWhy=null;
 });log('回到自己家，换上拖鞋。');});return true;
}
function friendVisitWalk(target,action='walk',duration=20,seat=false){
 const v=friendVisit;if(!atFriendHome()||sim.mode==='down')return;
 sim.route=friendVisitRoute(here(),target);sim.s=0;sim.target=routeLength(sim.route);sim.mode='walk';sim.act='friend_visit';sim.windup=null;
 v.action=action;v.duration=duration;v.seated=seat;v.end=null;v.talk=null;
}
function friendVisitAction(action,selected=null){return startFriendHouseAction(action,selected);}
function friendVisitCommand(name,item=null){
 if(!atFriendHome())return false;
 if(sim.mode==='down'){showHint('先长按主角五秒，把主角叫醒吧。');return true;}
 const selected=friendHouseObject(friendVisit.pendingFurnitureId);friendVisit.pendingFurnitureId=null;
 if(name==='go_home'||name==='go_out')leaveFriendHome();
 else startFriendHouseAction(({friend_snack:'eat',snack:'eat',sleep:'sleep',bed:'sleep',toilet:'toilet',bath:'bath',eat:'eat',cook:'cook',chat:'chat',tv:'tv',read:'read',computer:'computer'})[name]||'sit',selected,item);return true;
}
function requestFriendStay(){
 const v=friendVisit,c=visitingFriend();if(!atFriendHome()||!c||sim.mode==='down')return false;
 if(v.stay){showSay('都说好啦，困了就睡，别再问一遍啦。',contactName(c)+'：',c);return false;}
 const day=Math.floor(sim.t/1440);
 if(v.askedDay===day){showSay('今晚已经说好了呀，咱们下次提前约，好不好？',contactName(c)+'：',c);return false;}
 if(hour()<18){showSay('还早呢，晚上要是想住下，再跟我说一声呀。',contactName(c)+'：',c);return false;}
 v.askedDay=day;
 const chance=c.family?1:c.affinity>90?.96:c.affinity>=60?.8:c.affinity>=20?.3:0;
 const accept=Math.random()<chance;
 const sheet=openSocialSheet(accept?'今晚可以住下':'今晚不太方便留宿');sheet.classList.add('friend-stay-sheet');
 const content=socialContent(sheet),avatar=document.createElement('canvas');avatar.width=avatar.height=40;avatar.className='friend-stay-avatar';drawContactAvatar(avatar,c);content.append(avatar);
 const text=document.createElement('p');text.textContent=contactName(c)+'：'+pick(accept?FRIEND_VISIT_TEXT.stayAccept:FRIEND_VISIT_TEXT.stayDecline);content.append(text);
 const b=document.createElement('button');b.type='button';b.textContent=accept?'好，那就打扰一晚啦':'好呀，下回再约';b.onclick=closeSocialSheet;sheet.append(b);
 if(accept){v.stay=true;v.until=(day+1)*1440+10*60;log(`问${contactName(c)}能不能借住一晚，对方答应了。`);addSocialMemory(c,'借住一晚','主动问了能不能留宿，朋友帮忙安排了睡觉的位置。');}
 else{v.until=Math.min(v.until,day*1440+22.5*60);log(`${contactName(c)}今晚不太方便留宿，约好到点再回家。`);}
 return accept;
}
function nextFriendVisitText(pool,seen){const fresh=pool.filter(t=>!seen.includes(t[0]));if(!fresh.length)seen.length=0;const t=pick(fresh.length?fresh:pool);seen.push(t[0]);return t;}
function tickFriendHomeTalk(dt){
 const v=friendVisit,c=visitingFriend();if(!v||!c||asleep()||sim.mode==='down'||['toilet','bath'].includes(v.action)||remoteSocial)return;
 if(v.talk){
  v.talk.wait-=dt;if(v.talk.wait>0)return;
  const t=v.talk;
  if(t.i>=t.lines.length){log(`在${contactName(c)}家聊起「${t.title}」。`,null,t.said);v.count++;finishContactTalk(c.id,'visit-chat');v.talk=null;v.next=realClock+6+Math.random()*8;return;}
  const line=t.lines[t.i++],hero=line.startsWith('>'),text=line.replace(/^>/,'');showSay(text,hero?'':contactName(c)+'：',hero?null:c);t.said.push([hero?nameOf()+'：':contactName(c)+'：',text]);t.wait=Math.max(3,Math.min(5,text.length*.14));return;
 }
 if(realClock<v.next||sim.mode==='walk')return;
 const h=visitingHouse(),off=(W-h.w)/2,r=friendVisitRoom(h,here().x-off,here().y),present=v.family.filter(a=>a.room===r.id);
 if(present.length&&Math.random()<.4){
  const member=pick(present),pool=FRIEND_VISIT_TEXT.family[member.relation]||FRIEND_VISIT_TEXT.family['哥哥'],[title,raw]=nextFriendVisitText(pool,v.familySeen),text=fill(raw,{TA:doll.normalize(c.look).gender==='m'?'他':'她'});
  showSay(text,member.speaker.name+'：',member.speaker);log(`${member.speaker.name}：${text}`);v.next=realClock+10;return;
 }
 if(Math.abs(v.host.y-here().y)>3){v.next=realClock+3;return;}
 const pool=c.affinity<20?FRIEND_VISIT_TEXT.early:FRIEND_VISIT_TEXT.talks;
 const [title,...lines]=nextFriendVisitText(pool,v.seen);v.talk={title,lines,i:0,wait:.2,said:[]};
}
function tickFriendHomeActor(a,dt){
 const v=friendVisit,h=visitingHouse(),off=(W-h.w)/2;
 if(a.route){a.s=Math.min(a.length,a.s+WALK*.8*Math.min(speed,4)*dt);const p=routePos(a.route,a.s);a.x=p.x;a.y=p.y;a.moving=a.s<a.length;if(!a.moving){a.route=null;a.room=friendVisitRoom(h,a.x-off,a.y).id;}return;}
 a.moving=false;
 if(sim.t<a.next||asleep()||v.talk)return;
 a.next=sim.t+30+Math.random()*45;
 const hero=here(),room=a===v.host?friendVisitRoom(h,hero.x-off,hero.y):pick(h.rooms.filter(r=>!['bath','laundry','stair','entry_stair'].includes(r.role)));
 if(['bath','laundry'].includes(room.role))return;
 const x=off+room.x+Math.min(room.w-12,a===v.host?Math.max(12,hero.x-off-room.x-17):18+Math.random()*(room.w-32));
 a.route=friendVisitRoute(a,{x,y:room.floor});a.s=0;a.length=routeLength(a.route);
}
function stepFriendHome(dtGame,dtReal){
 if(!atFriendHome())return false;
 if(wiping||cardHolds()||!(dtGame>0||dtReal>0))return true;
 const v=friendVisit;sim.t+=dtGame;updateWeather(dtGame);
 const day=Math.floor(sim.t/1440)+1;if(day!==sim.lastDay){sim.lastDay=day;log(`—— 第 ${day} 天 · ${SEASONS[seasonOf(sim.t).i].name} ——`,'day');}
 const action=sim.mode==='act'?v.action:null,resting=action==='sleep';
 const effects=FRIEND_HOME_EFFECTS[action]||{};
 for(const k in sim.needs){const d=effects[k]>0?0:-DECAY[k]*(k==='fun'?petFunMultiplier():1)*(resting?(k==='bladder'?.35:.4):1);sim.needs[k]=clamp(sim.needs[k]+(d+(effects[k]||0))*dtGame);}
 applyNeedConsequences();checkCollapse();if(sim.mode==='down')return true;
 // Address needs locally before they reach zero; do not send guests straight
 // back home just because the host's house has its own bathroom and snacks.
 const addressing=['toilet','eat','bath','cook'].includes(v.action);
 if(!addressing){
  if(sim.needs.bladder<18)friendVisitAction('toilet');
  else if(sim.needs.hunger<20)friendVisitAction('eat');
  else if(sim.needs.hygiene<12)friendVisitAction('bath');
 }
 if((!v.stay&&(sim.t>=v.until||hour()>=23||hour()<5))||(v.stay&&sim.t>=v.until)){
  leaveFriendHome(v.stay?'在朋友家住了一晚，上午和朋友道别回家。':'时间不早了，和朋友道别，准备回家。');return true;
 }
 if(sim.needs.energy<18&&!v.stay&&(!addressing||sim.needs.energy<8)){leaveFriendHome('有点困了，先和朋友道别，回家好好睡一觉。');return true;}
 if(sim.mode==='walk'){
  const before=here();sim.s=Math.min(sim.target,sim.s+WALK*Math.min(speed,4)*dtReal*(before.dy?.7:1));sim.walkDist+=Math.abs(here().x-before.x);if(Math.abs(here().x-before.x)>.01)sim.facing=Math.sign(here().x-before.x);
  if(sim.s>=sim.target){sim.mode='act';v.end=sim.t+(v.duration||25);onFriendHouseActionStart();if(v.action==='sleep'){sim.act='sleep';sim.actEnd=v.end;showSay(pick(FRIEND_VISIT_TEXT.goodnight),contactName(visitingFriend())+'：',visitingFriend());log('借住朋友家，洗漱后躺下休息。');}}
 }else if(sim.mode==='act'){
  if(resting&&(hour()>=7&&hour()<18&&sim.needs.energy>=80||sim.t>=v.end)){
   sim.mode='idle';sim.act='friend_visit';v.action=null;v.sleepFurniture=null;log('在朋友家醒来，伸了个懒腰。');showSay(pick(FRIEND_VISIT_TEXT.morning),contactName(visitingFriend())+'：',visitingFriend());
  }else if(!resting&&sim.t>=v.end){if(finishFriendHouseAction())return true;sim.mode='idle';sim.act='friend_visit';v.action=null;v.seated=false;sim.idleUntil=sim.t+5;}
 }else if(sim.t>=(sim.idleUntil||0)){
  if(v.stay&&(hour()>=22||hour()<6))friendVisitAction('sleep');
  else friendVisitAction(Math.random()<.6?'sit':'chat');
 }
 tickFriendHomeActor(v.host,dtReal);for(const a of v.family)tickFriendHomeActor(a,dtReal);tickFriendHomeTalk(dtReal);checkCollapse();return true;
}
function friendVisitDoing(){return `${contactName(visitingFriend())}家 · ${FRIEND_VISIT_ACTS[friendVisit.action]||'做客'}`;}
function friendVisitHit(x,y){
 if(!atFriendHome()||!IMG.friendHouses?.[friendVisit.houseId]?.objects)return null;const v=friendVisit,h=visitingHouse(),off=(W-h.w)/2;
 const foreground=friendFurnitureAt(x,y,true);if(foreground)return foreground;
 if(Math.abs(x-v.host.x)<10&&y>v.host.y-DH&&y<v.host.y+3)return {kind:'host'};
 if(v.family.some(a=>Math.abs(x-a.x)<10&&y>a.y-DH&&y<a.y+3))return {kind:'family'};
 if(buddyHit(x,y))return {kind:'hero'};
 if(!h.furniture.some(f=>f.kind==='entry')&&Math.abs(x-off-h.entry[0])<10&&Math.abs(y-h.entry[1]+16)<20)return {kind:'door'};
 return friendFurnitureAt(x,y);
}
function friendVisitClick(x,y){
 if(!atFriendHome())return false;const hit=friendVisitHit(x,y),v=friendVisit;
 if(hit?.kind==='host'){
  RINGS.friend_host=[['fv:chat','聊聊天'],['fv:stay',v.stay?'已经约好留宿':'申请过夜'],['fv:leave','告辞回家']];openRing('friend_host','friend_host');return true;
 }
 if(hit?.kind==='hero'){RINGS.friend_guest=[['fv:eat','吃点东西'],['fv:toilet','借用卫生间'],['fv:leave','回家']];openRing('friend_guest');return true;}
 if(hit?.kind==='family')return true;
 if(hit?.kind==='door'){leaveFriendHome();return true;}
 if(hit?.kind==='furniture'){interactFriendFurniture(hit.f);return true;}
 const h=visitingHouse(),off=(W-h.w)/2,r=friendVisitRoom(h,x-off,y);
 if(y>=r.y&&y<=r.floor+6){v.objectId=v.seatId=null;friendVisitWalk({x:Math.max(off+r.x+9,Math.min(off+r.x+r.w-9,x)),y:r.floor});}return true;
}
function renderFriendHome(){
 if(!atFriendHome())return false;const v=friendVisit,h=visitingHouse(),imgs=IMG.friendHouses[v.houseId],off=(W-h.w)/2;
 vctx.save();vctx.setTransform(1,0,0,1,0,0);vctx.clearRect(0,0,view.width,view.height);vctx.scale(devPx,devPx);vctx.imageSmoothingEnabled=false;
 vctx.drawImage(imgs.day,off,0);const night=nightness(hour());if(night>0){vctx.globalAlpha=night;vctx.drawImage(imgs.night,off,0);vctx.globalAlpha=1;}
 const windows=friendHouseWindows();drawWeather(vctx,night>.5,windows,{},true);drawFriendHomeLamps(vctx);drawFriendHomeScreens(vctx);drawFriendFurnitureHover(vctx);
 const f={expr:Math.floor(realClock/3)%5===0?'blink':'neutral',look:0,bob:0,sway:0,wave:null};
 const actors=[v.host,...v.family].map(a=>({...a,draw:()=>{
  if(asleep()){
   const beds=h.furniture.filter(f=>f.kind==='bed');
   const bed=a===v.host?beds[0]:beds[Math.min(1,beds.length-1)];
   if(bed){
    let bx=off+bed.x,by=bed.y;
    if(a===v.host&&v.sleepFurniture===bed){const r=friendVisitRoom(h,bed.x+bed.w/2,bed.y+bed.h);bx=off+r.x+Math.max(5,r.w-42);by=r.floor-5;vctx.fillStyle='#c3bbab';vctx.fillRect(bx,by,36,5);vctx.fillStyle='#f0e9da';vctx.fillRect(bx+1,by,9,4);}
    const src=npcCanvas(a.npc,{...f,expr:'sleepy'},'stand');
    vctx.save();vctx.translate(Math.round(bx+5+(a.relation==='妈妈'?-3:0)),by+DW-5);vctx.rotate(-Math.PI/2);vctx.drawImage(src,0,0,DW,15,0,0,DW,15);vctx.restore();return;
   }
  }
  const pose=a.moving?(Math.floor(realClock*6)%2?'walkL':'walkR'):'stand';vctx.drawImage(npcCanvas(a.npc,{...f,bob:a.moving?Math.floor(realClock*5)%2:0},pose),Math.round(a.x-DW/2),Math.round(a.y-DH+1));
 }}));
 const p=here();actors.push({y:p.y+1,draw:()=>{
  if(sim.mode==='down'){vctx.drawImage(lyingBody({...f,expr:'dazed'}),Math.round(p.x-12),Math.round(p.y-15));return;}
  if(asleep()&&v.sleepFurniture){const bed=v.sleepFurniture;vctx.drawImage(lyingBody({...f,expr:'sleepy'}),Math.round(off+bed.x+5),bed.y-5);vctx.drawImage(IMG.fx.sofa_blanket[0],Math.round(off+bed.x+16),bed.y+2);return;}
  if(drawFriendFixtureUser(vctx,f))return;
  const pose=sim.mode==='walk'?(Math.floor(realClock*6)%2?'walkL':'walkR'):v.seated&&sim.mode==='act'?'sit':'stand';vctx.drawImage(dollCanvas(f,pose),Math.round(p.x-DW/2),Math.round(p.y-DH+1));
 }});
 actors.sort((a,b)=>a.y-b.y).forEach(a=>a.draw());vctx.drawImage(imgs.front,off,0);drawFriendActionForeground(vctx,f);
 drawStorm(vctx,{windows,states:{},height:h.h,rooms:h.rooms.map(r=>[off+r.x,r.y,r.w,r.floor-r.y+6])});
 if(sim.mode==='down'&&holding){const elapsed=realClock-holding.t0;drawRescue(vctx,p,elapsed);if(elapsed>=REVIVE_S)revive();}
 vctx.restore();return true;
}
function canOfferFriendVisit(c){return !!c&&!c.child&&!c.family&&c.affinity>=20&&!friendVisit&&!socialState.guest&&!friendOutingState&&hour()>=9&&hour()<20;}
function finishFriendVisitInvitation(c){
 if(!c||c.family)return;log(`${contactName(c)}打电话邀请我去家里坐坐。`);if(!requestFriendVisit(c.id,true))showSay('没事，那下次方便了再过来吧。',contactName(c)+'：',c);
}

function tickFriendVisitTravel(){
 if(friendVisit?.phase!=='departing'||wiping||cardHolds())return;
 if(!visitingFriend()||sim.mode==='down'||asleep()||sim.dest!=='friend_home'){
  friendVisit=null;if(sim.dest==='friend_home')sim.dest=null;log('这次拜访先改天，等方便了再联系。');
 }
}

document.getElementById('testFriendHomeInvite').onclick=()=>{
 const c=sortedContacts().find(canOfferFriendVisit);
 if(!c||!requestIncomingCall(c.id,'friend_home'))showHint('等主角醒着、空闲时再试好友邀约；已有客人或行程时先处理完。');
};
