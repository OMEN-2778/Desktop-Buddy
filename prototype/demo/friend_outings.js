// One persistent companion, independent of transient street NPCs.
let friendOutingState=null;
const FRIEND_OUTING_PLACES={front:'家门口',park:'公园',mall:'商场',beach:'码头',bar:'酒吧'};
const outingFriend=()=>friendOutingState&&socialState.contacts.find(c=>c.id===friendOutingState.id);
const friendOutingActive=()=>!!friendOutingState&&['active','returning'].includes(friendOutingState.phase)&&sim.place!=='home';
const friendOutingWaiting=()=>!!friendOutingState&&['waiting','departing'].includes(friendOutingState.phase);
function openFriendOuting(id){
  if(friendVisit){visitNotice("正在做客","先结束这次拜访，再约朋友一起出门吧。");return;}
  const c=socialState.contacts.find(c=>c.id===id);if(!c)return;
  if(friendOutingState){
    if(friendOutingState.id!==id){visitNotice('已经约了人','先结束这次同行，再约其他朋友吧。');return;}
    const sheet=openSocialSheet('结束同行？'),p=document.createElement('p');p.textContent=friendOutingWaiting()?'还没出发，要取消这次约定吗？':'要和朋友一起回家，结束这次出游吗？';socialContent(sheet).append(p);
    const b=document.createElement('button');b.textContent=friendOutingWaiting()?'取消约定':'一起回去';b.onclick=()=>{closeSocialSheet();if(friendOutingWaiting())finishFriendOuting('出发前改了时间，约好下回再去。');else{friendOutingState.phase='returning';friendOutingState.talk=null;command('go_home');}};sheet.append(b);return;
  }
  let reason='';
  if(asleep()||sim.mode==='down'||wiping||cardHolds()||socialBusy())reason='先忙完眼前的事，再约朋友出门吧。';
  else if(c.child)reason='小朋友暂时不能单独约出门。';
  else if(c.family&&!(socialState.guest?.id===id&&socialState.guest.phase==='visiting'))reason='爸爸妈妈住在另一座城市，等他们来探望时再一起出去吧。';
  else if(!c.family&&c.affinity<20)reason=`${contactName(c)}：咱们先多聊几次吧，出门玩等熟一点再约。`;
  else if(socialState.guest&&!(socialState.guest.id===id&&socialState.guest.phase==='visiting'&&!socialState.guest.overnight?.accepted))reason='先安排好家里的客人，再约出门吧。';
  else if(sim.needs.energy<30||sim.needs.hunger<30||sim.needs.hygiene<20)reason='先吃点东西、休息或洗漱好，再出门玩吧。';
  if(reason){visitNotice('暂时不能约出门',reason);return;}
  closeSocialSheet();setContactsOpen(false);closePicker();setDiaryOpen(false);
  RINGS.outing=Object.entries(FRIEND_OUTING_PLACES).map(([place,label])=>['outing:'+place,place==='front'?'去门口':place==='beach'?'去海边':'去'+label]);
  openRing('outing','door');ringEl.dataset.contactId=id;ringEl.setAttribute('aria-label','和'+contactName(c)+'去哪里玩');
  for(const button of ringEl.querySelectorAll('button')){
    const place=button.dataset.outingPlace;
    button.disabled=place==='bar'&&!barIsOpen()||['front','park','beach'].includes(place)&&weather.kind==='storm';
    if(button.disabled)button.title=place==='bar'?'现在酒吧还没开门哦！':'雷雨太大，先选室内吧';
  }
}
function scheduleFriendOuting(c,place){
  if(!FRIEND_OUTING_PLACES[place]||friendOutingState)return false;
  if(place==='bar'&&!barIsOpen()){showHint('现在酒吧还没开门哦！');return false;}
  const already=socialState.guest?.id===c.id&&socialState.guest.phase==='visiting';
  if(socialState.guest&&!already)return false;
  if(already){socialState.guest=null;guestBubble.hidden=true;}
  const minutes=already?0:10+Math.floor(Math.random()*11);
  friendOutingState={id:c.id,dest:place,phase:'waiting',at:sim.t+minutes,bookedAt:sim.t,nextTalk:realClock+7,seen:[],count:0,said:[],distance:0};
  log(`约${contactName(c)}一起去${FRIEND_OUTING_PLACES[place]}，${minutes?`大约 ${minutes} 分钟后碰面。`:'在门口一起出发。'}`);
  showSay(minutes?(sim.place==='home'?`好啊，我大概 ${minutes} 分钟到，咱们一起去。`:`好呀，大概 ${minutes} 分钟到，我过去找你，碰面了再一起逛！`):'行，我拿上东西，咱们走吧。',contactName(c)+'：',c);return true;
}
function finishFriendOuting(reason='一起走到家门口，挥手道别。'){
  const st=friendOutingState,c=outingFriend();if(!st)return;
  if(c){const text=`和${contactName(c)}去${FRIEND_OUTING_PLACES[st.dest]}玩，${reason}`;log(text,null,st.said?.length?st.said:undefined);if(st.startedAt!=null){finishContactTalk(c.id,'outing');addSocialMemory(c,'一起去'+FRIEND_OUTING_PLACES[st.dest],text);}}
  friendOutingState=null;hidePeerSay();contactsSig='';if(c&&st.startedAt!=null)showSay('那我先回去啦，下次再约。',contactName(c)+'：',c);
}
function restoreFriendOuting(raw,locationReady=true){
  friendOutingState=null;if(!raw||!socialState.contacts.some(c=>c.id===raw.id)||!FRIEND_OUTING_PLACES[raw.dest])return;
  const phase=['waiting','departing','active','returning'].includes(raw.phase)?raw.phase:null;if(!phase)return;
  friendOutingState={id:raw.id,dest:raw.dest,phase,at:Number.isFinite(raw.at)?raw.at:sim.t,bookedAt:Number.isFinite(raw.bookedAt)?raw.bookedAt:sim.t,startedAt:Number.isFinite(raw.startedAt)?raw.startedAt:null,nextTalk:realClock+8,seen:Array.isArray(raw.seen)?raw.seen.filter(s=>typeof s==='string').slice(-600):[],count:Number.isFinite(raw.count)?raw.count:0,said:[],distance:0};
  if(locationReady){
    if(['active','returning'].includes(phase)&&sim.place==='home')friendOutingState=null;
    if(friendOutingState&&phase==='departing'&&sim.place==='home'){friendOutingState.phase='waiting';friendOutingState.at=sim.t;friendOutingState.startedAt=null;}
    if(friendOutingState&&sim.place==='park'&&sim.park?.seated){sim.route=[[parkLayout().bench.x-9,parkLayout().bench.feet]];sim.s=0;sim.target=0;}
  }
}
function friendOutingSnapshot(){const s=friendOutingState;return s?{id:s.id,dest:s.dest,phase:s.phase,at:s.at,bookedAt:s.bookedAt,startedAt:s.startedAt,seen:s.seen,count:s.count}:null;}
function companionContext(){return sim.place+':'+(sim.place==='park'?parkLayout().id:mallVisitInside()?mallS.visit.kind:'');}
function companionPosition(){
  const st=friendOutingState;if(!st||!friendOutingActive())return null;
  if(sim.place==='bar'&&!sim.bar?.seat){st.barSeat=null;st.heroSeat=null;}
  const p=buddyFeet(),room=mallVisitInside(),seated=room||sim.place==='park'&&(sim.park?.seated||parkEating())||sim.place==='bar'&&!!sim.bar?.seat;
  let x=p.x-(sim.facing||1)*17,y=p.y+1;
  if(parkInsideToilet()){x=parkLayout().facility.x+20;y=parkLayout().feet;}
  else if(barToiletInside()){x=277;y=107;}
  else if(room){if(mallS.visit.kind==='restaurant'){const seat=MALL.dining.companion;x=seat.x;y=seat.feet-seat.lift;}else{x=p.x-28;y=p.y;}}
  else if(sim.place==='park'&&sim.park?.seated){x=parkLayout().bench.x+9;y=p.y;}
  else if(parkEating()){x=201;y=p.y;}
  else if(sim.place==='bar'&&sim.bar?.seat){
    if(st.heroSeat!==sim.bar.seat||!barSeat(st.barSeat)){st.heroSeat=sim.bar.seat;const seats=BAR_SEATS.filter(seat=>seat.id!==sim.bar.seat&&!barScene?.guests.some(n=>n.seat===seat.id));st.barSeat=seats.sort((a,b)=>Math.abs(a.x-p.x)-Math.abs(b.x-p.x))[0]?.id||null;}
    const seat=barSeat(st.barSeat);if(seat){x=seat.x;y=seat.feet-seat.lift;}
  }else if(seated){x=p.x+(p.x>W/2?-18:18);y=p.y;}
  const key=companionContext();if(st.scene!==key||!st.position){st.scene=key;st.position={x:Math.max(12,Math.min(W-12,x)),y};st.lastHeroX=p.x;}
  return {x:Math.max(12,Math.min(W-12,x)),y,seated:seated&&!contactPrivacyBreak()&&!(sim.place==='bar'&&!barSeat(st.barSeat))};
}
function tickFriendOuting(dt){
  const st=friendOutingState,c=outingFriend();if(!st)return;if(!c){friendOutingState=null;return;}
  if(!speed||cardHolds()||wiping)return;
  if(st.phase==='waiting'){
    if(sim.t<st.at)return;
    if(asleep()||sim.mode==='down'||redNeed(['fun','social'])){finishFriendOuting('临时身体不舒服，这次先取消。');return;}
    if(contactPrivacyBreak()||wardrobeOpen||remoteSocial||sim.talk||socialDialogHolds())return;
    if(['front','park','beach'].includes(st.dest)&&weather.kind==='storm'){finishFriendOuting('雷雨来了，商量改天再去。');return;}
    if(st.dest==='bar'&&!barIsOpen()){finishFriendOuting('酒吧还没开门，先改天再约。');return;}
    if(sim.place!=='home'){
      st.phase='active';st.startedAt=sim.t;st.nextTalk=realClock+7;c.lastSeen=sim.t;c.lastContact=sim.t;c.forgotten=false;contactsSig='';
      sim.outWhy='friend';sim.lastOut=sim.t;sim.outBack=sim.t+180;
      log(`${contactName(c)}按约定赶来碰面，接下来一起去${FRIEND_OUTING_PLACES[st.dest]}。`);showSay('找到你啦！等很久没？',contactName(c)+'：',c);
      if(sim.place!==st.dest){sim.queue=[];throughDoor(st.dest);}
      else if(sim.act==='go_home'){sim.windup=null;sim.queue=[];sim.player=false;sim.mode='idle';sim.act=null;sim.idleUntil=sim.t+2;}
      return;
    }
    st.phase='departing';sim.dest=st.dest;sim.outWhy='friend';sim.lastOut=sim.t;sim.outBack=sim.t+180;log(`${contactName(c)}到了，一起向门口走去。`);showSay('走吧，东西带齐了。',contactName(c)+'：',c);command('go_out');return;
  }
  if(st.phase==='departing'&&sim.place==='home'&&(asleep()||sim.mode==='down')){finishFriendOuting('临时需要休息，约好改天再出发。');return;}
  if(st.phase==='departing'&&sim.place==='home'&&!headingOut()){sim.dest=null;sim.outBack=null;sim.outWhy=null;finishFriendOuting('临时改了主意，这次先不出门了。');return;}   // sent elsewhere before the door
  if(st.phase==='departing'){if(sim.place==='home')return;st.phase='active';st.startedAt=sim.t;st.nextTalk=realClock+7;c.lastSeen=sim.t;c.lastContact=sim.t;c.forgotten=false;contactsSig='';}
  if(sim.place==='home'){finishFriendOuting();return;}
  const current=companionPosition(),pos=st.position;
  if(current&&pos){
    // Keep a short, scene-local motion history: start, turn and stop a beat later.
    const scrolling=sim.place==='mall'&&!mallInside();
    const scrollDistance=scrolling?Math.abs(mallS.dist-(st.mallDist??mallS.dist)):0;st.mallDist=mallS.dist;
    if(st.followScene!==st.scene){st.followScene=st.scene;st.followClock=0;st.followTrail=[];}
    st.followClock+=dt;st.followTrail.push({...current,t:st.followClock,scrollDistance,scrollDir:mallS.dir});
    const cutoff=st.followClock-.24;
    while(st.followTrail.length>1&&st.followTrail[1].t<=cutoff)st.followTrail.shift();
    const target=st.followTrail[0];
    const dx=target.x-pos.x,dy=target.y-pos.y,dist=Math.hypot(dx,dy),amount=Math.min(dist,WALK*(1+Math.min(1,dist/35))*.91*dt*Math.min(speed,4));
    if(dist>0){pos.x+=dx/dist*amount;pos.y+=dy/dist*amount;st.distance+=amount;}
    const scrollMoving=target.scrollDistance>.01;st.distance+=target.scrollDistance;
    st.moving=dist>2||scrollMoving;st.dir=scrollMoving?target.scrollDir:dx>0?1:dx<0?-1:0;st.seated=target.seated&&!st.moving;
  }
  if(st.phase==='active'&&stormOutside()){st.phase='returning';st.talk=null;log(`雷雨下大了，和${contactName(c)}商量先回家。`);command('go_home');return;}
  if(st.phase==='returning'||asleep()||sim.mode==='down'||contactPrivacyBreak()||mallSleeping()||remoteSocial||sim.talk||life.talkQ||barScene?.chat){st.talk=null;return;}
  if(st.talk){const tk=st.talk;if((tk.wait-=dt)>0)return;if(tk.i>=tk.lines.length){st.count++;if(tk.gain!==0)finishContactTalk(c.id,'visit-chat');if(tk.mood&&ML[tk.effectId])addMood(tk.effectId,{words:false,diary:false});log(`和${contactName(c)}在${FRIEND_OUTING_PLACES[st.dest]}聊起「${tk.title}」。`,null,tk.said);addSocialMemory(c,'一起出门 · '+tk.title,tk.said.map(([,t])=>t).join(' '));st.talk=null;st.nextTalk=realClock+14+Math.random()*14;return;}
    const raw=tk.lines[tk.i++],other=raw.startsWith('>'),text=fill(other?raw.slice(1):raw,{朋友:contactName(c)}),who=other?contactName(c)+'：':'';showSay(text,who,other?c:null);tk.said.push([who,text]);st.said.push([who,text]);st.said=st.said.slice(-100);tk.wait=Math.min(4.6,Math.max(2.6,1.4+text.length*.13));return;}
  if(realClock<st.nextTalk||pickOn||npcInteraction)return;
  const context=sim.place==='park'?'park_'+parkLayout().id:mallVisitInside()?mallS.visit.kind:sim.place;
  const key=context!=='cinema'&&Math.random()<.3?'common':context;
  const pool=(FRIEND_OUTING_TEXT.talks[key]||[]).filter(row=>outingTalkFits(key,row,c));
  if(!pool.length){st.nextTalk=realClock+5;return;}
  const id=row=>key+':'+row[0];
  let fresh=pool.filter(row=>!st.seen.includes(id(row)));
  if(!fresh.length){const recent=new Set(st.seen.slice(-3));st.seen=st.seen.filter(s=>!pool.some(row=>id(row)===s)||recent.has(s));fresh=pool.filter(row=>!st.seen.includes(id(row)));}
  const row=pick(fresh.length?fresh:pool);st.seen.push(id(row));st.seen=st.seen.slice(-600);
  const effect=FRIEND_OUTING_TEXT.effects?.[id(row)]||{};st.talk={title:row[0],effectId:'outing_talk_'+id(row),lines:row.slice(1),i:0,wait:.4,said:[],gain:effect.gain??1,mood:effect.mood||null,expr:effect.expr||'neutral'};
}
function outingTalkFits(key,row,c){
  const when=FRIEND_OUTING_TEXT.effects?.[key+':'+row[0]]?.when||{};
  if(when.meal&&!parkEating())return false;
  if(when.affinity&&c.affinity<when.affinity)return false;
  if(when.day&&!(hour()>=6&&hour()<18))return false;
  if(when.dry&&isRain(weather.kind))return false;
  if(when.seasons&&!when.seasons.includes(seasonOf(sim.t).i))return false;
  if(when.seated&&!sim.park?.seated&&!sim.bar?.seat)return false;
  return true;
}
function drawOutingFriend(ctx,layer=null){
  const st=friendOutingState;if(!st)return;const boarding=st.phase==='departing'&&sim.place==='home';if(!boarding&&(!friendOutingActive()||!st.position))return;const c=outingFriend();if(!c)return;
  const p=boarding?{x:D.spots.front_door[1]+13,y:FLOOR_Y[D.spots.front_door[0]]}:st.position,interior=mallVisitInside(),paint=interior?'back':p.y<buddyFeet().y?'back':'front';if(layer&&layer!==paint)return;
  const cache=st.npc||=( {look:c.look,ramps:doll.rampsOf(c.look),cache:new Map(),kid:!!c.child});
  const i=Math.floor(st.distance/4+.8)%4,pose=st.seated?'sit':st.moving?['stand','walkR','stand','walkL'][i]:'stand';
  const f={expr:st.talk?st.talk.expr:Math.floor(realClock*1000/2600)%5===0?'blink':'neutral',look:st.moving?st.dir:0,bob:st.moving?i%2:0,sway:st.moving?i%2:0,wave:null};
  ctx.drawImage(npcCanvas(cache,f,pose,interior&&mallS.visit.kind==='cinema'),Math.round(p.x-DW/2),Math.round(p.y-DH+1));
}
function friendOutingCardFits(cd){
  if(!friendOutingActive())return cd.service!=='friend_outing';
  if(cd.service!=='friend_outing'||friendOutingState.phase!=='active')return false;
  if(cd.outingZones&&!cd.outingZones.includes(parkLayout().id))return false;
  if(cd.outingContexts&&!cd.outingContexts.includes(mallVisitInside()?mallS.visit.kind:'mall'))return false;
  if(cd.outingDay&&!(hour()>=6&&hour()<18))return false;
  return true;
}
function applyFriendOutingCard(){
  if(card.cd.service!=='friend_outing')return;const c=socialState.contacts.find(c=>c.id===card.vars.outingFriendId);if(!c)return;
  const before=c.affinity;c.affinity=clamp(c.affinity+(card.o.friendship||0));if(c.affinity>before){discoverPersonality(c,c.affinity-before);showFriendshipGain(c,c.affinity-before);}c.lastContact=sim.t;contactsSig='';addSocialMemory(c,fill(card.cd.title,card.vars),fill(card.o.text,card.vars));
}

for(const cd of CARDS.filter(cd=>cd.service==='friend_outing'))for(const k of ['a','b'])cd[k].out.forEach((o,i)=>{if(o.mood)ML[o.id=`card${cd.n}${k}${i}`]={...o.mood};});
for(const [key,effect]of Object.entries(FRIEND_OUTING_TEXT.effects||{}))if(effect.mood)ML['outing_talk_'+key]={name:key.slice(key.indexOf(':')+1),emo:effect.mood,pts:1,min:90};
