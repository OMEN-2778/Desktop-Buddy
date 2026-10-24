// The diary yields its row before another speaker enters; Buddy keeps her own row.
const peerHud=document.getElementById('peerHud'),peerBubble=document.getElementById('peerBubble'),peerText=peerBubble.querySelector('span'),peerAvatar=peerHud.querySelector('canvas');
const peerSpeech={phase:'idle',entry:0,exit:0,pending:null,until:0,speakerId:null,lineTimer:0,currentText:null};
function showFriendshipGain(c,gain){
  if(!(gain>0)||peerSpeech.speakerId!==c.id||peerHud.hidden)return;
  peerSpeech.until=Math.max(peerSpeech.until,performance.now()+1600);
  const plus=document.createElement('span');plus.className='friendship-gain';
  plus.setAttribute('role','status');plus.setAttribute('aria-label',`与${contactName(c)}的友谊增加 ${Number(gain.toFixed(2))}`);
  plus.textContent='+';peerHud.append(plus);setTimeout(()=>plus.remove(),1500);
}
function peerDiaryReserved(){return peerSpeech.phase!=='idle';}
function peerSpeaker(who,speaker){
  const label=String(who).replace(/[：:]\s*$/,'');
  if(speaker?.id)return speaker;
  const contact=socialState.contacts.find(c=>contactName(c)===label||c.name===label);
  return contact||{id:'anonymous_'+label,name:label||'对方',anonymous:true};
}
function drawPeerAvatar(speaker){
  if(!speaker.anonymous){drawContactAvatar(peerAvatar,speaker);return;}
  const ctx=peerAvatar.getContext('2d');ctx.clearRect(0,0,40,40);
  ctx.fillStyle='#edf2f3';ctx.fillRect(0,0,40,40);
  ctx.fillStyle='#a3bfd5';ctx.fillRect(10,28,20,12);ctx.fillRect(6,32,28,8);
  ctx.fillStyle='#d8d5de';ctx.fillRect(12,10,16,16);ctx.fillRect(16,24,8,6);
  ctx.fillStyle='#777182';ctx.fillRect(14,6,12,4);ctx.fillRect(10,10,20,6);ctx.fillRect(10,16,4,4);ctx.fillRect(26,16,4,4);
}
function fitPeerSpeech(){
  if(peerHud.hidden)return;
  // Anchor the growing row above the house, with room for Buddy's wrapped text.
  const [outline,inner]=sayClip(48,0,12,12,2,0);peerHud.style.setProperty('--peer-clip',outline);peerHud.style.setProperty('--peer-inner',inner);
  let height=48+fitText(peerBubble,peerText,SAY_FS(),0,48,'--peer-clip','--peer-inner');
  peerHud.style.height=height+'px';liftDiary();
}
function renderPeerLine(line){
  peerSpeech.currentText=line.text;peerText.classList.remove('line-out');
  const speaker=line.speaker,name=speaker.anonymous?speaker.name:contactName(speaker);
  peerText.replaceChildren(Object.assign(document.createElement('em'),{className:'who',textContent:name+'：'}),document.createTextNode(spaced(line.text)));
  peerHud.setAttribute('aria-label',name+'的对话');peerAvatar.setAttribute('aria-label',name+'的头像');peerAvatar.title=name;
  if(peerSpeech.speakerId!==speaker.id){drawPeerAvatar(speaker);peerSpeech.speakerId=speaker.id;}
  fitPeerSpeech();peerSpeech.until=performance.now()+5200;
}
function revealPeerLine(){
  peerSpeech.entry=0;
  if(!peerSpeech.pending||phoneHolds()){hidePeerSay(true);return;}
  renderPeerLine(peerSpeech.pending);peerSpeech.phase='visible';peerHud.classList.add('on');peerHud.setAttribute('aria-hidden','false');
  sayShownAt=performance.now();
}
function showPeerSay(text,who,speaker=null){
  if(!text)return;
  const line={text,who,speaker:peerSpeaker(who,speaker)};peerSpeech.pending=line;
  if(phoneHolds())return; // Keep identity while an incoming call owns the speech area.
  clearTimeout(peerSpeech.exit);peerSpeech.exit=0;
  if(peerSpeech.phase==='visible'){
    sayShownAt=performance.now();peerSpeech.until=sayShownAt+5200;
    clearTimeout(peerSpeech.lineTimer);
    if(reduceMotionUI||peerSpeech.currentText===line.text){renderPeerLine(line);sayShownAt=performance.now();return;}
    peerText.classList.add('line-out');
    peerSpeech.lineTimer=setTimeout(()=>{peerSpeech.lineTimer=0;if(peerSpeech.phase!=='visible'||!peerSpeech.pending)return;renderPeerLine(peerSpeech.pending);sayShownAt=performance.now();},130);
    return;
  }
  if(peerSpeech.phase==='preparing')return;
  const wasLeaving=peerSpeech.phase==='leaving';
  peerSpeech.phase='preparing';setDiaryOpen(false);diaryEl.classList.add('peer-away');diaryEl.inert=true;
  peerHud.hidden=false;peerHud.classList.remove('leaving');
  clearTimeout(peerSpeech.entry);
  peerSpeech.entry=setTimeout(revealPeerLine,reduceMotionUI||wasLeaving?0:240);
}
function hidePeerSay(immediate=false){
  clearTimeout(peerSpeech.lineTimer);peerSpeech.lineTimer=0;peerSpeech.currentText=null;peerText.classList.remove('line-out');
  clearTimeout(peerSpeech.entry);clearTimeout(peerSpeech.exit);peerSpeech.entry=peerSpeech.exit=0;peerSpeech.pending=null;
  if(peerSpeech.phase==='idle'){peerHud.hidden=true;return;}
  peerSpeech.phase='leaving';peerHud.classList.remove('on');peerHud.classList.add('leaving');peerHud.setAttribute('aria-hidden','true');
  const done=()=>{peerSpeech.exit=0;peerSpeech.phase='idle';peerSpeech.speakerId=null;peerHud.hidden=true;peerHud.classList.remove('leaving');
    diaryEl.classList.remove('peer-away');diaryEl.inert=moodrow.classList.contains('contacts-open');fitDiary();};
  if(immediate||reduceMotionUI)done();else peerSpeech.exit=setTimeout(done,240);
}
function tickPeerSpeech(now){
  if(phoneHolds())return;
  if(peerSpeech.phase==='idle'&&peerSpeech.pending){const line=peerSpeech.pending;showPeerSay(line.text,line.who,line.speaker);return;}
  if(!['visible','preparing'].includes(peerSpeech.phase))return;
  if(asleep()||sim.mode==='down'){hidePeerSay();return;}
  const talking=friendOutingState?.talk||remoteSocial||socialState.guest?.talk||socialState.guest?.bedTalk||sim.talk&&sim.item?.talk;
  if(!talking&&peerSpeech.phase==='visible'&&now>=peerSpeech.until)hidePeerSay();
}
