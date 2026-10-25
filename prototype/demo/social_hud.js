// Stable contacts are saved separately from transient hover / ringing state.
const LEGACY_CONTACT_SEEDS=[
  {id:'dad',name:'爸爸',family:'dad',affinity:94,look:{...doll.PRESETS.m,style:'neat',hair:'#8c8e9a',top:'#8a9dae'}},
  {id:'mom',name:'妈妈',family:'mom',affinity:96,look:{...doll.PRESETS.f,style:'buns',hair:'#706172',top:'#bb8fa4',acc:[]}},
  {id:'abu',name:'阿布',family:null,affinity:65,look:{...doll.PRESETS.m,style:'curly',hair:'#655070',top:'#7aa88a'}},
  {id:'xiaoyu',name:'小雨',family:null,affinity:60,look:{...doll.PRESETS.f,style:'bob',hair:'#5b475e',top:'#92abc6'}},
  {id:'linzhou',name:'林舟',family:null,affinity:56,look:{...doll.PRESETS.m,style:'neat',hair:'#484354',top:'#b39476'}},
  {id:'tangtang',name:'糖糖',family:null,affinity:50,look:{...doll.PRESETS.f,style:'twin',hair:'#9b6a52',top:'#cc92a3'}},
  {id:'achen',name:'阿辰',family:null,affinity:44,look:{...doll.PRESETS.m,style:'messy',hair:'#6a5551',top:'#8c9cae'}},
  {id:'xiaokui',name:'小葵',family:null,affinity:38,look:{...doll.PRESETS.f,style:'pony',hair:'#80633f',top:'#d6b77a'}},
  {id:'muzi',name:'木子',family:null,affinity:30,look:{...doll.PRESETS.f,style:'long',hair:'#413d51',top:'#91ad9a'}},
  {id:'dake',name:'大可',family:null,affinity:22,look:{...doll.PRESETS.m,style:'buzz',hair:'#675448',top:'#b59bc5'}},
  {id:'ningning',name:'宁宁',family:null,affinity:14,look:{...doll.PRESETS.f,style:'buns',hair:'#6a5063',top:'#a1bfcc'}},
  {id:'xiaoye',name:'小野',family:null,affinity:8,look:{...doll.PRESETS.m,style:'curly',hair:'#986b51',top:'#bfa27e'}}
];
const DEFAULT_CONTACTS=LEGACY_CONTACT_SEEDS.slice(0,4);
const SOCIAL_CHANNELS=['text','call','video','meet','visit','visit-chat','outing'];
const socialState={contacts:DEFAULT_CONTACTS.map(c=>({...c,look:doll.normalize(c.look)})),nextCall:null,rosterVersion:2};
const networkTrigger=document.getElementById('networkTrigger'),contactsPanel=document.getElementById('contactsPanel');
const contactsList=document.getElementById('contactsList'),contactActions=document.getElementById('contactActions');
const incomingCall=document.getElementById('incomingCall');
networkTrigger.querySelector('img').src=D.uiIcons.people;
needsEl.style.setProperty('--need-stripes',`url("${D.uiIcons.stripes}")`);
for(const [selector,key]of [['.call-answer','answer'],['.call-decline','decline']])incomingCall.querySelector(selector).style.setProperty('--hud-relief-img',`url(${D.uiRelief[key]})`);
// Share the same stepped circles and two-pixel frames as diary/settings UI.
function sizeSocialHud(){
  const style=document.getElementById('widget').style,b=skyGeo.b,small=false;
  style.setProperty('--hud-badge-img',`url(${D.uiRelief[small?'badgeSmall':'badge']})`);
  for(const [name,n,p]of [['panel',12,2],['card',8,2],['button',9,2],['call-button',7,2],['circle',small?10:12,2],['avatar',small?6:8,2],['small',5,2],['trait',2,1],['meter',2,2],['track',4,b],['caller',small?7:9,2]]){
    style.setProperty(`--hud-${name}-clip`,roundClip(n,p));
    style.setProperty(`--hud-${name}-in`,roundClip(Math.max(1,n-1),p));
  }
  // Follow the game's actual width, including desktop display scaling.
  const houseWidth=view.getBoundingClientRect().width,metrics=uiMetrics(houseWidth,view.offsetHeight),compact=metrics.contactCompact;
  contactsPanel.classList.toggle('compact',compact);
  contactsPanel.classList.toggle('two-columns',metrics.contactColumns===2);
  contactsPanel.classList.toggle('stacked',metrics.stackedContacts);
  incomingCall.classList.toggle('compact',metrics.callStacked);
  style.setProperty('--contact-avatar-clip',roundClip(compact?5:8,2));
  style.setProperty('--needs-fill-clip',roundClip(7,1));
  style.setProperty('--hud-track-in',roundClip(2,b));
  style.setProperty('--hud-track-edge',2*b+'px');
}
let networkCloseT=0,contactsCloseT=0,selectedContact=null,contactsSig='',remoteSocial=null;
const phoneCall={phase:'idle',contactId:null,kind:'call',deadline:0,timeout:0,exitTimer:0,returnFocus:null};
function phoneHolds(){return ['ringing','accepting','declining'].includes(phoneCall.phase);}
function contactName(c){return c.family==='dad'?'爸爸':c.family==='mom'?'妈妈':c.name;}
function contactRelation(c){return c.family?'家人':c.affinity>90?'最好的朋友':c.affinity>=60?'挚友':c.affinity>=20?'朋友':c.affinity>0?'面熟':'陌生';}
function sortedContacts(){const rank=c=>c.family==='dad'?0:c.family==='mom'?1:2;return [...socialState.contacts].sort((a,b)=>rank(a)-rank(b)||b.affinity-a.affinity||a.id.localeCompare(b.id));}
function contactFor(who,id=null){return socialState.contacts.find(c=>c.id===id)||socialState.contacts.find(c=>c.family===who)|| (who==='friend'?sortedContacts().find(c=>!c.family):null);}
function drawContactAvatar(canvas,c){
  if(c.forgotten&&!c.family){const ctx=canvas.getContext('2d');ctx.clearRect(0,0,40,40);ctx.fillStyle='#e4e1ec';ctx.fillRect(0,0,40,40);ctx.fillStyle='#666078';for(const [y,row]of ['01110','11011','00011','00110','00100','00000','00100'].entries())for(let x=0;x<row.length;x++)if(row[x]==='1')ctx.fillRect(10+x*4,6+y*4,4,4);return;}
  const lk=doll.normalize(c.look||doll.PRESETS[c.family==='mom'?'f':'m']);
  const body=doll.toCanvas(doll.pixels(lk,{expr:'neutral',look:0,bob:0,sway:0},doll.rampsOf(lk)),DW,DH);
  const ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,40,40);
  ctx.fillStyle='#eef3f1';ctx.fillRect(0,0,40,40);ctx.drawImage(body,0,0,DW,17,0,2,40,34);
}
function fillContacts(){
  const contacts=sortedContacts(),sig=JSON.stringify(contacts.map(c=>[c.id,c.name,c.family,c.affinity,c.look,!!c.forgotten,knownPersonalityTraits(c)]));if(sig===contactsSig)return;
  contactsSig=sig;const scrollTop=contactsList.scrollTop;contactsList.replaceChildren();
  for(const c of contacts){
    const card=document.createElement('button');card.type='button';card.className='contact-card';card.dataset.id=c.id;
    card.setAttribute('aria-label',`${contactName(c)}，${contactRelation(c)}，好感 ${Math.round(c.affinity)}`);card.setAttribute('aria-expanded',String(selectedContact===c.id));
    const avatar=document.createElement('canvas');avatar.width=avatar.height=40;avatar.setAttribute('aria-hidden','true');drawContactAvatar(avatar,c);
    const copy=document.createElement('span');copy.className='contact-copy';
    copy.append(Object.assign(document.createElement('strong'),{textContent:contactName(c),title:contactName(c)}),Object.assign(document.createElement('small'),{textContent:contactRelation(c)}));
    const meter=document.createElement('span');meter.className='affinity';meter.title=`好感 ${Math.round(c.affinity)} / 100`;meter.style.setProperty('--affinity',c.affinity);meter.append(document.createElement('i'));
    const traits=document.createElement('span');traits.className='contact-traits';
    for(const label of knownPersonalityTraits(c)){const chip=document.createElement('span');chip.textContent=label;traits.append(chip);}
    traits.hidden=!traits.childElementCount;
    card.append(avatar,copy,traits,meter);contactsList.append(card);
  }
  contactsList.scrollTop=scrollTop;
}
function revealNetwork(){clearTimeout(networkCloseT);moodrow.classList.add('network-ready');}
function queueNetworkClose(){clearTimeout(networkCloseT);networkCloseT=setTimeout(()=>{if(!moodrow.classList.contains('contacts-open'))moodrow.classList.remove('network-ready');},300);}
function setContactsOpen(open){
  clearTimeout(contactsCloseT);clearTimeout(networkCloseT);
  if(open&&phoneHolds())return;
  if(open){revealNetwork();setNeedsOpen(false);showMoodTip(false);setDiaryOpen(false);setSettingsOpen(false);fillContacts();}
  else closeContactActions();
  moodrow.classList.toggle('contacts-open',open);contactsPanel.inert=!open;contactsPanel.setAttribute('aria-hidden',String(!open));networkTrigger.setAttribute('aria-expanded',String(open));
  if(open){document.getElementById('settings').inert=true;document.getElementById('diary').inert=true;moodFace.inert=true;moodTalk.inert=true;}
  else{document.getElementById('settings').inert=false;document.getElementById('diary').inert=peerDiaryReserved();moodFace.inert=false;moodTalk.inert=false;queueNetworkClose();}
}
function queueContactsClose(){clearTimeout(contactsCloseT);if(!selectedContact)contactsCloseT=setTimeout(()=>setContactsOpen(false),280);}
moodFace.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse')revealNetwork();});
moodFace.addEventListener('pointerleave',queueNetworkClose);moodFace.addEventListener('focus',revealNetwork);
moodFace.addEventListener('click',revealNetwork);
moodrow.addEventListener('pointerleave',e=>{if(e.pointerType==='touch')return;queueNetworkClose();queueContactsClose();});
networkTrigger.addEventListener('pointerenter',e=>{revealNetwork();if(e.pointerType==='mouse')setContactsOpen(true);});
networkTrigger.addEventListener('focus',revealNetwork);
networkTrigger.addEventListener('click',()=>setContactsOpen(!moodrow.classList.contains('contacts-open')));
contactsPanel.addEventListener('pointerenter',()=>{clearTimeout(contactsCloseT);clearTimeout(networkCloseT);});
contactsPanel.addEventListener('pointerleave',e=>{if(e.pointerType!=='touch')queueContactsClose();});
contactsPanel.addEventListener('focusout',e=>{if(!contactsPanel.contains(e.relatedTarget)&&!contactActions.contains(e.relatedTarget)&&e.relatedTarget!==networkTrigger)queueContactsClose();});
contactsList.addEventListener('scroll',()=>closeContactActions(),{passive:true});
contactsList.addEventListener('click',e=>{const card=e.target.closest('.contact-card');if(card)openContactActions(card.dataset.id);});
function closeContactActions(){selectedContact=null;contactActions.classList.remove('on');contactActions.inert=true;contactActions.setAttribute('aria-hidden','true');contactsList.querySelectorAll('button').forEach(b=>b.setAttribute('aria-expanded','false'));}
function openContactActions(id){
  if(selectedContact===id){closeContactActions();return;}
  const c=socialState.contacts.find(c=>c.id===id);if(!c)return;closeRing();selectedContact=id;contactActions.replaceChildren();
  const visitLabel=socialState.guest?.id===id?(socialState.guest.phase==='scheduled'?'取消邀请':'送客'):'来我家';
  const actions=[['text','发消息'],['video','打视频'],['outing',friendOutingState?.id===id?'结束同行':'出门玩'],['visit','拜访'],['invite',visitLabel],['memories','经历'],['cancel','算了']];
  for(const [i,[action,label]]of actions.entries()){
    const b=document.createElement('button');b.type='button';b.textContent=label;b.dataset.action=action;b.setAttribute('role','menuitem');
    const a=-Math.PI/2+i*2*Math.PI/actions.length;b.style.setProperty('--x',`${Math.cos(a)*112}px`);b.style.setProperty('--y',`${Math.sin(a)*72}px`);
    if(['text','video'].includes(action)&&(asleep()||sim.mode==='down'||wiping||cardHolds()||socialBusy())){
      b.setAttribute('aria-disabled','true');b.title=asleep()?'等主角醒来再联系':sim.mode==='down'?'先唤醒晕倒的主角':'正在忙，稍后再联系';b.setAttribute('aria-label',`${label}：${b.title}`);
    }
    contactActions.append(b);
  }
  contactsList.querySelectorAll('button').forEach(b=>b.setAttribute('aria-expanded',String(b.dataset.id===id)));
  placeContactActions();contactActions.inert=false;contactActions.setAttribute('aria-hidden','false');contactActions.classList.add('on');
  contactActions.firstElementChild?.focus({preventScroll:true});
}
function placeContactActions(){
  if(!selectedContact)return;const card=[...contactsList.children].find(b=>b.dataset.id===selectedContact);if(!card){closeContactActions();return;}
  const buttons=[...contactActions.children],edgeX=Math.max(...buttons.map(b=>Math.abs(parseFloat(b.style.getPropertyValue('--x')))+b.offsetWidth/2))+8;
  const r=card.getBoundingClientRect(),viewportWidth=document.documentElement.clientWidth,x=Math.max(edgeX,Math.min(viewportWidth-edgeX,r.x+r.width/2)),y=Math.max(100,Math.min(innerHeight-100,r.y+r.height/2));
  contactActions.style.left=x+'px';contactActions.style.top=y+'px';
}
contactActions.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b||b.getAttribute('aria-disabled')==='true')return;
  const id=selectedContact;closeContactActions();if(b.dataset.action==='cancel')return;
  setContactsOpen(false);if(b.dataset.action==='memories')showSocialMemories(id);else if(b.dataset.action==='invite'){if(socialState.guest?.id===id)endHomeVisit('主角和客人道别，约好下次再聚。');else inviteHome(id);}else if(b.dataset.action==='visit')requestFriendVisit(id);else if(b.dataset.action==='outing')openFriendOuting(id);else startContactTalk(id,b.dataset.action);
});
document.addEventListener('pointerdown',e=>{if(!contactsPanel.contains(e.target)&&!contactActions.contains(e.target)&&!networkTrigger.contains(e.target)&&!moodFace.contains(e.target))setContactsOpen(false);});
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){if(selectedContact){const id=selectedContact;closeContactActions();contactsList.querySelector(`[data-id="${id}"]`)?.focus();}else if(moodrow.classList.contains('contacts-open')){setContactsOpen(false);moodFace.focus();}}
  if(e.key==='ArrowLeft'&&document.activeElement===moodFace){e.preventDefault();revealNetwork();networkTrigger.focus();}
  if(e.key==='ArrowDown'&&document.activeElement===networkTrigger){e.preventDefault();setContactsOpen(true);contactsList.firstElementChild?.focus();}
  if(contactActions.contains(document.activeElement)&&['ArrowRight','ArrowDown','ArrowLeft','ArrowUp'].includes(e.key)){
    e.preventDefault();const buttons=[...contactActions.children],i=buttons.indexOf(document.activeElement),d=['ArrowRight','ArrowDown'].includes(e.key)?1:-1;buttons[(i+d+buttons.length)%buttons.length].focus();
  }
});

const TEXT_TALKS=[
  [
    "今天吃什么",
    [
      "吃啥呢？我又不知道吃什么了。",
      ">我也在想。你冰箱里还有东西没？",
      "有，得翻翻。",
      ">先看看吧，别又拿饼干凑一顿。"
    ]
  ],
  [
    "分享一朵云",
    [
      "我刚看到朵云，挺像一只猫。",
      ">照片呢？",
      "没拍，刚拿出手机就散了。",
      ">哈哈，下回手快点。"
    ]
  ],
  [
    "晚一点也没关系",
    [
      "我今天这点事磨蹭半天了。",
      ">现在做到哪儿了？",
      "还剩一点。",
      ">那先弄完这点，别一边做一边骂自己。"
    ]
  ],
  [
    "路过花店",
    [
      "刚路过花店，看到一束挺好看的。",
      ">买了吗？",
      "没，站门口看了会儿。",
      ">拍张我看看呗。"
    ]
  ],
  [
    "天气提醒",
    [
      "你出门没？记得带伞啊。",
      ">还没，伞我找找。",
      "别又放门口忘拿。",
      ">看到了，这回真装包里了。"
    ]
  ],
  [
    "发来一张照片",
    [
      ">看，我刚拍的。",
      "这在哪儿？看着挺舒服。",
      ">路上随便拐进去的一个地方。",
      "把位置发我呗，下次我也看看。"
    ]
  ],
  [
    "一句早安",
    [
      "早啊，起来没？",
      ">醒了，还没起来。",
      "哈哈，我也刚醒。",
      ">那先不聊了，我去找点吃的。"
    ]
  ],
  [
    "突然想起",
    [
      ">刚听到一首歌，你应该也听过。",
      "哪首？发我。",
      ">发了，副歌那段。",
      "哦这首，我刚才还没想起来。"
    ]
  ],
  [
    "一件小好事",
    [
      "今天有件事居然一次就弄好了。",
      ">什么事呀？",
      "我还以为得来回跑几趟。",
      ">那挺好，省下的时间歇会儿呗。"
    ]
  ],
  [
    "无事也联系",
    [
      "在干嘛？",
      ">没啥，随便看看手机。",
      "我也没什么事，就问问。",
      ">嗯，刚好聊两句。"
    ]
  ],
  [
    "注意休息",
    [
      ">你是不是还没睡？",
      "嗯，再看一点就睡。",
      ">你这句我都见好几回了。",
      "好好好，我放下了，你也早点睡。"
    ]
  ],
  [
    "笑话交换",
    [
      "我刚看到个冷笑话。",
      ">多冷？",
      "我发你，你自己看。",
      ">……行，确实有点冷。"
    ]
  ]
];
CHATS.text={};CHAT_ACT.phone_text='text';
for(const who of ['dad','mom','friend'])CHATS.text[who]={name:who==='dad'?'爸爸':who==='mom'?'妈妈':'{朋友}',talks:TEXT_TALKS.map(([title,lines],i)=>{
 const id=`contact_text_${who}_${i}`;ML[id]={name:'互相惦记',emo:'happy',pts:1,min:90};return {title,lines,id};
})};
function socialBusy(){return friendVisit?.talk||friendOutingState?.talk||socialState.guest?.talk||socialState.guest?.bedTalk||npcInteraction||life.talkQ||(sim.place==='bar'&&barScene?.chat)||remoteSocial||sim.talk||sim.chosen?.item?.talk||sim.windup&&CHAT_ACT[sim.windup.act];}
function startContactTalk(id,kind='text',incoming=false){
  const c=socialState.contacts.find(c=>c.id===id);if(!c)return false;
  if(sim.mode==='down'||asleep()||wiping||cardHolds()||socialBusy())return false;
  const who=c.family||'friend',item=chatItem(kind,who,kind==='video'?'phone':'call',id);
  if(incoming)item.talk.start=`接听了${contactName(c)}的${kind==='video'?'视频':'电话'}。`;
  // This session accompanies daily life; it owns no route, action or needs lock.
  remoteSocial={item,i:0,wait:.5,said:[]};log(item.talk.start);
  return true;
}
function finishContactTalk(id,kind){
  const c=socialState.contacts.find(c=>c.id===id);if(!c)return;
  const day=Math.floor(sim.t/1440);if(c.gainDay!==day){c.gainDay=day;c.dailyGain=0;}
  const before=c.affinity;const previous=contactRelation(c),gain=Math.min(['meet','visit-chat'].includes(kind)?1:kind==='text'?2:4,Math.max(0,6-(c.dailyGain||0)));
  c.affinity=clamp(c.affinity+gain);c.dailyGain=(c.dailyGain||0)+gain;c.lastContact=sim.t;c.contactCounts||={};c.contactCounts[kind]=(c.contactCounts[kind]||0)+1;discoverPersonality(c,c.affinity-before);if(c.affinity>before)showFriendshipGain(c,c.affinity-before);
  if(kind==='video'||kind==='meet'||kind==='visit'){c.forgotten=false;c.lastSeen=sim.t;}
  if(previous!==contactRelation(c)){const message=`和${contactName(c)}从${previous}成为了${contactRelation(c)}。`;log(message);addSocialMemory(c,'关系更近了一步',message);}
  if(['text','call','video'].includes(kind))addSocialMemory(c,{text:'互发消息',call:'通了电话',video:'视频见面'}[kind],`和${contactName(c)}聊起「${c.lastTopic||'彼此的近况'}」。`);
  sim.needs.social=clamp(sim.needs.social+(kind==='text'?5:10));applyNeedConsequences();contactsSig='';if(moodrow.classList.contains('contacts-open'))fillContacts();
}
function canReceiveCall(){return !friendVisit&&!friendHousePreview&&ringOf!=='outing'&&!asleep()&&sim.mode!=='down'&&!wiping&&!guideOn&&!card&&!wardrobeOpen&&!socialBusy()&&!socialDialogHolds()&&!homeVisitActive();}
function contactWithHero(id){
  return atFriendHome()&&friendVisit.id===id||friendOutingState?.id===id&&friendOutingState.phase!=='waiting'||socialState.guest?.id===id&&['entering','visiting','leaving'].includes(socialState.guest.phase);
}
function requestIncomingCall(id,kind='call'){
  if(contactWithHero(id))return false;
  if(phoneCall.phase!=='idle'||!socialState.contacts.some(c=>c.id===id)||!canReceiveCall())return false;
  phoneCall.phase='waiting';phoneCall.contactId=id;phoneCall.kind=kind;return true;
}
function showIncomingCall(){
  const now=performance.now();
  const c=socialState.contacts.find(c=>c.id===phoneCall.contactId);if(!c||contactWithHero(c.id)){phoneCall.phase='idle';return;}
  hidePeerSay(true);setContactsOpen(false);setNeedsOpen(false);showMoodTip(false);closeRing();closePicker();
  incomingCall.querySelector('strong').textContent=c.family||c.affinity<20?contactName(c):contactRelation(c)+contactName(c);
  incomingCall.classList.toggle('friend-home-invite',phoneCall.kind==='friend_home');
  incomingCall.querySelector('.call-answer').textContent=phoneCall.kind==='friend_home'?'去你家':'接听';incomingCall.querySelector('.call-decline').textContent=phoneCall.kind==='friend_home'?'下次吧':'拒绝';
  for(const [selector,key]of [['.call-answer',phoneCall.kind==='friend_home'?'invite':'answer'],['.call-decline',phoneCall.kind==='friend_home'?'later':'decline']])incomingCall.querySelector(selector).style.setProperty('--hud-relief-img',`url(${D.uiRelief[key]})`);
  incomingCall.querySelector('.caller-copy span').textContent=phoneCall.kind==='friend_home'?pick(FRIEND_VISIT_TEXT.invitations):phoneCall.kind==='video'?'打来视频':'打来电话';
  drawContactAvatar(incomingCall.querySelector('canvas'),c);incomingCall.classList.remove('accepting','declining');incomingCall.hidden=false;
  moodTalk.classList.add('phone-active');phoneCall.phase='ringing';phoneCall.deadline=now+6000;incomingCall.style.setProperty('--call-remaining',1);
  phoneCall.returnFocus=document.activeElement;incomingCall.querySelector('.call-answer').focus({preventScroll:true});
  phoneCall.timeout=setTimeout(()=>finishIncomingCall(false,true),6000);
  c.lastIncoming=sim.t;socialState.nextCall=sim.t+180+Math.random()*300;
}
function finishIncomingCall(accepted,automatic=false){
  if(phoneCall.phase!=='ringing')return;clearTimeout(phoneCall.timeout);
  const id=phoneCall.contactId,kind=phoneCall.kind,c=socialState.contacts.find(c=>c.id===id);
  phoneCall.phase=accepted?'accepting':'declining';incomingCall.classList.add(phoneCall.phase);
  if(!accepted&&c&&!['visit','friend_home'].includes(kind)){socialRejected(c,'的来电没能接通');}
  if(!accepted&&c)log(automatic?`没来得及接听${contactName(c)}的来电，铃声在六秒后停了。`:`暂时婉拒了${contactName(c)}的来电，晚点再联系。`);
  phoneCall.exitTimer=setTimeout(()=>{
    phoneCall.phase='idle';phoneCall.contactId=null;incomingCall.hidden=true;moodTalk.classList.remove('phone-active');
    if(phoneCall.returnFocus?.isConnected&&!phoneCall.returnFocus.closest('[inert]'))phoneCall.returnFocus.focus({preventScroll:true});
    if(accepted){
      if(kind==='friend_home'){if(c)finishFriendVisitInvitation(c);}
      else if(kind==='visit'){if(c)showVisitOffer(c);}
      else if(kind==='farewell'){if(c)showFarewellOffer(c);}
      else if(!startContactTalk(id,kind,true)&&c){log(`记下了${contactName(c)}的来电，等忙完再回拨。`);}
    }else if(!popSay.hidden&&performance.now()-sayShownAt<5200){popBubble(popSay,Math.max(600,5200-(performance.now()-sayShownAt)));}
  },reduceMotionUI?0:accepted?360:280);
}
incomingCall.querySelector('.call-answer').addEventListener('click',()=>finishIncomingCall(true));
incomingCall.querySelector('.call-decline').addEventListener('click',()=>finishIncomingCall(false));
document.getElementById('testIncoming').addEventListener('click',()=>{if(!requestIncomingCall('abu'))log(asleep()?'先等主角醒来，再试试来电通知。':'现在正在忙，等当前活动结束再试试来电。');});
function contactPrivacyBreak(){
  if(atFriendHome()&&sim.mode==='act'&&['bath','toilet'].includes(friendVisit.action))return friendVisit.action==='bath'?'洗澡':'上厕所';
  if(sim.act==='bath')return '洗澡';
  if(['toilet','park_toilet'].includes(sim.act)||mallToiletInside()||barToiletInside()||parkInsideToilet())return '上厕所';
  return null;
}
function tickSocial(dt,now){
  if(friendHousePreview)return;
  // Real time has one source, independent of the simulation's speed and frame clock.
  const callNow=performance.now();
  if(phoneCall.phase==='ringing'){incomingCall.style.setProperty('--call-remaining',Math.max(0,(phoneCall.deadline-callNow)/6000));if(callNow>=phoneCall.deadline)finishIncomingCall(false,true);return;}
  if(phoneHolds())return;
  if(!Number.isFinite(socialState.nextCall))socialState.nextCall=sim.t+210;
  if(phoneCall.phase==='waiting'){
    if(contactWithHero(phoneCall.contactId)||asleep()||sim.mode==='down'||!socialState.contacts.some(c=>c.id===phoneCall.contactId)){phoneCall.phase='idle';socialState.nextCall=sim.t+120;return;}
    if(canReceiveCall()&&callNow-sayShownAt>=2000)showIncomingCall();
  }else if(speed&&sim.t>=socialState.nextCall&&hour()>=9&&hour()<21&&canReceiveCall()){
    const farewell=socialState.contacts.find(c=>c.farewellPending&&!contactWithHero(c.id)),eligible=sortedContacts().filter(c=>!contactWithHero(c.id)&&socialCallDue(c));
    if(farewell){farewell.farewellPending=false;requestIncomingCall(farewell.id,'farewell');}
    else if(eligible.length){const c=pick(eligible);requestIncomingCall(c.id,canOfferFriendVisit(c)&&Math.random()<.3?'friend_home':'call');}socialState.nextCall=sim.t+180+Math.random()*300;
  }
  if(remoteSocial&&speed&&!cardHolds()&&!wiping){
    const session=remoteSocial;
    if(asleep()||sim.mode==='down'){log(`和${session.item.talk.name}的联系暂时中断，等方便时再聊。`,null,session.said);remoteSocial=null;return;}
    const privacy=contactPrivacyBreak();
    if(privacy){
      if(!session.pausedFor){session.pausedFor=privacy;hidePeerSay();showSay(privacy==='洗澡'?'我先洗个澡，等会儿接着聊。':'我先去一下卫生间，等会儿接着说。');log(`和${session.item.talk.name}的聊天暂时停一下，先${privacy}。`);}
      return;
    }
    if(session.pausedFor){session.pausedFor=null;session.resumeWait=2.6;showSay('回来啦，咱们接着聊。');log(`回来后，接着和${session.item.talk.name}聊刚才的话题。`);return;}
    if(session.resumeWait>0){session.resumeWait=Math.max(0,session.resumeWait-dt);return;}
    session.wait-=dt;if(session.wait>0)return;
    const tk=session.item.talk;
    if(session.i>=tk.lines.length){
      log(fill(tk.end,session.item.vars),null,session.said);if(tk.id)addMood(tk.id,{vars:session.item.vars,diary:false,words:false});finishContactTalk(session.item.contactId,tk.kind);remoteSocial=null;return;
    }
    const raw=tk.lines[session.i++],other=raw.startsWith('>'),text=fill(other?raw.slice(1).trim():raw,session.item.vars),who=other?`${tk.name}：`:'';
    showSay(text,who,socialState.contacts.find(c=>c.id===session.item.contactId));session.said.push([who,text]);session.wait=Math.min(4.6,Math.max(2.6,1.4+(who+text).length*.13));
  }
}
function socialSnapshot(){return {...socialLifeSnapshot(),rosterVersion:socialState.rosterVersion,contacts:socialState.contacts.map(c=>({personality:{...personalityOf(c)},personalityBond:{gain:c.personalityBond?.gain||0,days:[...(c.personalityBond?.days||[])]},parentVisitRoll:c.parentVisitRoll||null,parentLastVisit:c.parentLastVisit??null,bedTalkSeen:c.bedTalkSeen||[],contactCounts:Object.fromEntries(SOCIAL_CHANNELS.map(k=>[k,c.contactCounts?.[k]||0])),personalityTalks:c.personalityTalks||0,personalitySeen:c.personalitySeen||[],personalityTextSeen:c.personalityTextSeen||{},id:c.id,name:c.name,family:c.family||null,affinity:c.affinity,look:doll.normalize(c.look),lastContact:c.lastContact??null,gainDay:c.gainDay??null,dailyGain:c.dailyGain||0,memories:c.memories||[],metAt:c.metAt??null,lastSeen:c.lastSeen??null,forgotten:!!c.forgotten,lastIncoming:c.lastIncoming??null,rejectDay:c.rejectDay??null,rejectLoss:c.rejectLoss||0,farewellTried:!!c.farewellTried,farewellPending:!!c.farewellPending,lastVisitOffer:c.lastVisitOffer??null})),nextCall:socialState.nextCall};}
function restoreSocial(data,sourceIsDesktop=!!TAURI){
  hidePeerSay(true);
  clearTimeout(phoneCall.timeout);clearTimeout(phoneCall.exitTimer);phoneCall.phase='idle';phoneCall.contactId=null;incomingCall.hidden=true;moodTalk.classList.remove('phone-active');remoteSocial=null;
  const stored=Array.isArray(data?.contacts)?data.contacts:DEFAULT_CONTACTS;
  // Retire the browser testing roster once. Existing desktop saves keep every contact.
  const list=!sourceIsDesktop&&(data?.rosterVersion||0)<2?stored.filter(c=>DEFAULT_CONTACTS.some(p=>p.id===c?.id)):stored;
  const seen=new Set();socialState.contacts=[];
  for(const c of list){
    if(!c||typeof c.id!=='string'||!/^[-a-zA-Z0-9_]{1,64}$/.test(c.id)||seen.has(c.id)||typeof c.name!=='string'||!c.name.trim())continue;
    seen.add(c.id);socialState.contacts.push({id:c.id,name:c.name.slice(0,24),family:c.id==='dad'?'dad':c.id==='mom'?'mom':null,affinity:Number.isFinite(c.affinity)?clamp(c.affinity):50,look:doll.normalize(c.look||doll.PRESETS.m),lastContact:Number.isFinite(c.lastContact)?c.lastContact:null,gainDay:Number.isInteger(c.gainDay)?c.gainDay:null,dailyGain:Number.isFinite(c.dailyGain)?Math.max(0,Math.min(6,c.dailyGain)):0});
  }
  // New saves start with two friends; never re-add a friend removed by later gameplay.
  const additions=data?.rosterVersion>=2?DEFAULT_CONTACTS.slice(0,2):DEFAULT_CONTACTS;
  for(const c of additions)if(!seen.has(c.id))socialState.contacts.push({...c,look:doll.normalize(c.look)});
  socialState.rosterVersion=2;socialState.nextCall=Number.isFinite(data?.nextCall)?data.nextCall:null;contactsSig='';selectedContact=null;restoreSocialLife(data);
}
