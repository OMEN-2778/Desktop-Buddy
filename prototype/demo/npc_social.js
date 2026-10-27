// Click a visible person, walk over, then talk; references never survive scene changes.
ACTS.npc_chat={spot:null,label:'和路人聊天',emote:'chat',dur:Infinity,log:null};
OUT_ACTS.add('npc_chat');
let npcInteraction=null,npcPointer=null,hoverNpc=null;
const npcSceneKey=()=>sim.place==='park'?'park_'+parkLayout().id:sim.place;
function npcChatUrgent(){
  const n=sim.needs;
  return n.energy<20||n.hygiene<20||n.bladder<(sim.place==='park'?40:20)||n.hunger<(sim.place==='park'?35:sim.place==='mall'?25:20);
}
function canClickNpc(n){
  if(friendOutingActive())return false;
  if(!n||n.gone||sim.place==='home'||stormOutside()||mallInside()||parkInsideToilet()||barToiletInside())return false;
  if(sim.place==='mall'&&(mallS.toilet||mallS.visit)||sim.place==='bar'&&sim.bar?.toilet)return false;
  if(n.role==='fisher'||n.rod||n.role==='performer'||n.runner)return false;
  if(['park','mall'].includes(sim.place)&&(['clerk','hawker'].includes(n.role)||n.item))return false;
  return !!NPC_TALK_TEXT[npcSceneKey()]&&(life.npcs||[]).includes(n);
}
function npcAt(x,y){
  if(wiping||cardHolds()||sim.mode==='down'||mallInside())return null;
  // Front row wins; alpha pixels, plus their one-pixel rim, form the hit area.
  const layers={front:3,back:2,counter:1,stall:0};
  const people=[...(life.npcs||[])].reverse().filter(canClickNpc).sort((a,b)=>(layers[b.layer]||0)-(layers[a.layer]||0));
  for(const n of people){
    // The counter/table can cover a seated body; clicks belong to the visible surface.
    if(sim.place==='bar'){
      const covers=[IMG.out.bar.foreground,...(n.role==='bartender'?[IMG.out.bar.counter]:[])];
      if(covers.some(img=>{if(!outlineCache.has(img))outlineCache.set(img,outlineShape(img));return outlineCache.get(img).inside.has(Math.floor(x)+','+Math.floor(y));}))continue;
    }
    const [f,pose]=npcFrame(n),image=npcCanvas(n,f,pose,n.back),ox=Math.round(npcX(n)-DW/2),oy=Math.round(npcFeet(n)-DH+1);
    if(!outlineCache.has(image))outlineCache.set(image,outlineShape(image));
    if(outlineCache.get(image).near.has(Math.floor(x-ox)+','+Math.floor(y-oy)))return n;
  }return null;
}
function updateNpcHover(){
  hoverNpc=npcPointer&&npcPointer.scene===npcSceneKey()&&!buddyHit(npcPointer.x,npcPointer.y)?npcAt(npcPointer.x,npcPointer.y):null;
  if(hoverNpc){hoverId=null;mallS.hover=null;view.style.cursor='pointer';}
}
function drawNpcHover(ctx,n,image,x,y){if(hoverNpc===n&&canClickNpc(n))drawObjectHover(ctx,image,x,y);}
function npcTalkName(n){const c=socialState.contacts.find(c=>c.id===n.personId)||socialState.world.find(c=>c.id===n.personId);return c?contactName(c):'路人';}
function stopNpcTalk(reason='',resetBuddy=true){
  const state=npcInteraction,q=life.talkQ;
  if(q){q.n.dir=q.originalDir;q.n.paused=false;life.talkQ=null;
    if(reason&&q.said.length)log(`和${npcTalkName(q.n)}的闲聊暂时停下了，${reason}。`,null,q.said);
  }
  if(state){state.n.dir=state.originalDir;state.n.paused=false;npcInteraction=null;
    if(resetBuddy&&sim.act==='npc_chat'&&sim.mode!=='down'){
      const p=here();sim.route=[[p.x,p.y]];sim.s=sim.target=0;sim.player=false;sim.act=null;sim.mode='idle';sim.idleUntil=sim.t+1;
      if(sim.place==='mall'){sim.act='mall';sim.mode='act';sim.actEnd=Infinity;}
    }
  }
}
function requestNpcTalk(n){
  if(!canClickNpc(n)||wiping||cardHolds()||sim.mode==='down')return false;
  if(npcRefusesDirty(n,true))return false;
  if(npcInteraction?.n===n)return true;
  if(socialBusy()&&!npcInteraction){showHint('先聊完眼前的话，再打招呼吧。');return false;}
  if(npcChatUrgent()){showHint('先照顾好自己，等会儿再聊吧。');return false;}
  if(sim.place==='bar'&&barScene.chat){showHint('等酒保说完这句话，再聊吧。');return false;}
  stopNpcTalk('先忙眼前的事');closeRing();closePicker();sayQueue.length=0;
  const p=here(),x=npcX(n),side=(p.x<x?-1:1),offset=n.role==='bartender'?8:16;
  const target=Math.max(18,Math.min(W-18,x+side*offset));
  npcInteraction={n,scene:npcSceneKey(),phase:'approach',originalDir:n.dir,mallTarget:sim.place==='mall'?mallS.x+target-MALL.at:null};
  n.paused=true;sim.windup=null;sim.chosen=null;sim.item=null;sim.talk=null;sim.queue=[];sim.player=true;
  if(sim.place==='park')sim.park={...parkState(),seated:false,goal:null};
  if(sim.place==='bar'){sim.bar.seat=null;sim.bar.targetSeat=null;sim.bar.watching=false;}
  if(sim.place==='mall'){mallS.stop=null;mallS.goal=null;mallS.dir=side<0?1:-1;sim.route=[[MALL.at,MALL.feet]];}
  else sim.route=[[p.x,p.y],[target,sim.place==='park'?parkLayout().feet:OUT[sim.place].feet]];
  sim.s=0;sim.target=routeLength(sim.route);sim.mode='walk';sim.act='npc_chat';sim.pendingLog=null;
  return true;
}
function tickNpcInteraction(dtReal){
  const s=npcInteraction;if(!s)return false;
  if(!canClickNpc(s.n)||s.scene!==npcSceneKey()||sim.mode==='down'||sim.act!=='npc_chat'){
    stopNpcTalk('',sim.mode!=='down');return false;
  }
  if(npcChatUrgent()||sim.outBack!=null&&sim.t>=sim.outBack){
    stopNpcTalk('得先照顾自己，改天再继续');return false;
  }
  if(!dtReal||wiping||cardHolds())return true;
  s.n.paused=true;
  if(s.phase==='approach'){
    const v=WALK*Math.min(speed,4)*dtReal;
    let reached;
    if(sim.place==='mall'){
      const delta=s.mallTarget-mallS.x,move=Math.sign(delta)*Math.min(Math.abs(delta),v);
      mallS.x+=move;mallS.dist+=Math.abs(move);sim.walkDist+=Math.abs(move);sim.facing=Math.sign(delta)||sim.facing;mallS.dir=sim.facing;reached=Math.abs(delta)<=v;
    }else{
      const before=here();sim.s=Math.min(sim.target,sim.s+v);sim.walkDist+=Math.hypot(here().x-before.x,here().y-before.y);sim.facing=Math.sign(here().x-before.x)||sim.facing;reached=sim.s>=sim.target;
    }
    if(reached){
      sim.facing=Math.sign(npcX(s.n)-here().x)||1;s.n.dir=-sim.facing;s.n.back=false;
      sim.mode='act';sim.actEnd=Infinity;s.phase='talk';
      if(!startNpcTalk(s.n,true)){stopNpcTalk();return false;}
    }
  }
  if(sim.place==='bar'&&s.phase==='talk')advanceNpcTalk(dtReal);
  return !!npcInteraction;
}
function chooseNpcTalk(n){
  const c=socialState.contacts.find(c=>c.id===n.personId),scene=npcSceneKey();
  if(!n.kid&&(!c||c.affinity<20)&&SOCIAL_DIALOGUE.earlyMeet[scene]){
    const rows=SOCIAL_DIALOGUE.earlyMeet[scene],key=scene+'_early_'+n.personId,history=lifeFlags.npcChatSeen||={};
    const seen=Array.isArray(history[key])?history[key]:(history[key]=[]),row=nextGuestText(rows,seen);
    return {title:row[0],lines:row.slice(1),early:true,id:'adult_early_'+scene+'_'+rows.indexOf(row),scene};
  }
  if(c&&!n.kid&&Math.random()<.25){const t=pick(socialTalkPool('meet',c));return{title:t.title,lines:t.lines,id:null,scene};}
  const rows=NPC_TALK_TEXT[scene]?.[n.kid?'kid':'adult'];
  if(!rows?.length)return null;
  const seen=(lifeFlags.npcChatSeen||={}),ids=Array.isArray(seen[scene])?seen[scene]:[];
  const candidates=rows.map((row,i)=>({row,id:(n.kid?'kid_':'adult_')+i})).filter(t=>!c||c.affinity<20||!/(认识|陌生|第一句|开场|新招呼)/.test(t.row[0]));
  let pool=candidates.filter(t=>!ids.includes(t.id));
  if(!pool.length){seen[scene]=ids.slice(-3);pool=candidates.filter(t=>!seen[scene].includes(t.id));}
  const chosen=pick(pool),[title,...lines]=chosen.row;
  return{title,lines,id:chosen.id,scene};
}
function startNpcTalk(n,manual=false){
  if(!n||n.gone||life.talkQ||!manual&&(socialBusy()||phoneHolds()||asleep()||sim.mode==='down'))return false;
  if(npcRefusesDirty(n,manual))return false;
  const fest=festNpcTalk(n.role);let talk=fest?{lines:fest,title:'节日闲聊',scene:npcSceneKey(),id:null,early:true}:canClickNpc(n)?chooseNpcTalk(n):null;
  if(!talk){const lines=pick(((PT()?.talk||{})[n.role]||[]).filter(x=>!x.when).map(x=>x.lines||x));if(!lines)return false;talk={lines,title:'路上的闲聊',scene:npcSceneKey(),id:null};}
  talk={...talk,lines:talk.early?talk.lines:personalityTalk(talk.lines,personalityContact(n),'meet')};
  life.talkQ={...talk,n,manual,i:0,wait:0,said:[],originalDir:npcInteraction?.originalDir??n.dir};
  (life.npcTalked||=new WeakSet()).add(n);n.paused=true;
  if(manual)log(`走近${npcTalkName(n)}，在${sim.place==='park'?parkLayout().name:({front:'家门口',mall:'商场长廊',beach:'码头',bar:'酒吧'})[sim.place]}打了声招呼。`);
  return true;
}
// Keys are protagonist gender first, NPC gender second. Gender changes wording,
// not interests, affinity rewards or access to a topic.
function npcTalkLine(line,n){
  const pair=(look.gender==='m'?'m':'f')+(n.look.gender==='m'?'m':'f');
  return typeof line==='string'?line:line[pair]||line.base||'';
}
function npcTalkVars(n){
  const contact=socialState.contacts.find(c=>c.id===n.personId),known=contact&&contact.affinity>=20&&!contact.forgotten;
  return {...kidVars(),主角:nameOf(),朋友:npcTalkName(n),
    对方称呼:n.kid?'小朋友':known?contactName(contact):n.look.gender==='m'?'小哥':'姑娘',
    主角称呼:n.kid?(look.gender==='m'?'哥哥':'姐姐'):known?nameOf():look.gender==='m'?'小哥':'姑娘'};
}
function npcHasSpeech(n){
  const q=life.talkQ;
  return n.sayUntil>realClock||q?.n===n&&q.lastOther&&q.wait>0;
}
function npcKeepsBuddyLine(){
  const q=life.talkQ;
  return !!(q&&!q.lastOther&&q.wait>0&&q.lastText&&lastSaid===spaced(q.lastText));
}
function advanceNpcTalk(dt){
  const q=life.talkQ;if(!q||!dt)return;
  if(q.n.gone||!(life.npcs||[]).includes(q.n)||q.scene!==npcSceneKey()){stopNpcTalk();return;}
  // An automatic exchange is over if Buddy walks away or starts another activity.
  if(!q.manual&&(Math.abs(npcX(q.n)-here().x)>52||remoteSocial||sim.talk||asleep()||sim.mode==='down'||mallInside()||parkInsideToilet()||barToiletInside())){stopNpcTalk();return;}
  if(sim.needs.hygiene<=0){const n=q.n;stopNpcTalk('先去洗干净');npcRefusesDirty(n,true);return;}
  q.wait-=dt;if(q.wait>0)return;
  if(q.i>=q.lines.length){
    if(q.id){const ids=(lifeFlags.npcChatSeen||={})[q.scene]||=[];if(!ids.includes(q.id))ids.push(q.id);}
    const name=npcTalkName(q.n);log(`和${name}聊起「${q.title}」，散步时多了一段小故事。`,null,q.said);
    sim.needs.social=clamp(sim.needs.social+2);const contact=meetWorldNpc(q.n);
    if(contact){contact.lastTopic=q.title;addSocialMemory(contact,'路上聊起'+q.title,`在${sim.place==='park'?parkLayout().name:({front:'家门口',mall:'商场长廊',beach:'码头',bar:'酒吧'})[sim.place]}聊起「${q.title}」。`);}
    stopNpcTalk();life.chatNext=realClock+12+Math.random()*12;return;
  }
  const raw=npcTalkLine(q.lines[q.i++],q.n),other=raw.startsWith('>'),text=fill((other?raw.slice(1):raw).trim(),npcTalkVars(q.n));
  q.lastOther=other;q.lastText=text;
  if(other)npcSay(q.n,text);else{q.delivering=true;try{speak(text,true);}finally{q.delivering=false;}}
  q.said.push([other?npcTalkName(q.n)+'：':nameOf()+'：',text]);
  q.wait=Math.max(3,Math.min(6,2.3+text.length*.13));
}
