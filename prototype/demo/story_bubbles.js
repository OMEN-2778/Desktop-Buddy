// Story speech goes into the game's own conversation rows (owner, 2026-11-02):
// other people speak in the upper 对方 row (peer_dialogue.js: wooden bubble, "妈妈：",
// their avatar on the right), Buddy in her own lower bubble. No extra panel and no
// 继续 button: click the bubble (or Enter / Space) for the next line; a blinking
// pixel ▼ says there is more. Choices take Buddy's own bubble row (she is not
// speaking then): same height and round ends, the row split evenly between them. Esc
// folds the talk away (onClose). Quest lines tint the bubble white -> pale blue.
// While a talk is open the rows never time out. API kept for autumn/spring/summer.
function createStorySpeech({view,host=view.parentElement,anchor,onClose=()=>{}}){
 const popSpan=popSay.querySelector('span'),peerSpan=peerBubble.querySelector('span');
 const more=document.createElement('i');more.className='story-more';more.setAttribute('aria-hidden','true');
 const choices=document.createElement('div');choices.className='story-choices';choices.hidden=true;document.getElementById('moodTalk').append(choices);
 let open=false,advance=null,hero=false,previous=null,keep=0,busyWas=0;
 function mark(){   // exactly one row carries the story classes (tests and styles find it)
  for(const [box,span,on] of [[peerHud,peerSpan,!hero],[popSay,popSpan,hero]]){
   box.classList.toggle('story-speech',open&&on);(box===peerHud?peerBubble:popSay).classList.toggle('story-bubble',open&&on);span.classList.toggle('story-words',open&&on);
  }
 }
 function hold(){   // keep the rows up while the talk waits for a click
  if(!open)return;
  if(!hero)peerSpeech.until=performance.now()+6e4;else{clearTimeout(popSay._t);clearTimeout(popSay._t2);popSay.hidden=false;popSay.classList.remove('out');}
  sayBusy=realClock+60;
  const box=hero?popSay:peerBubble;if(more.parentElement!==box)box.append(more);
  keep=requestAnimationFrame(hold);
 }
 function show(speaker,words,{special=true,last=false,advance:next,choices:opts=null}={}){
  if(!open)previous=document.activeElement,busyWas=sayBusy;
  open=true;hero=speaker===nameOf();advance=opts?null:next;
  peerHud.classList.toggle('quest',!hero&&special);popSay.classList.toggle('quest',hero&&special);
  if(hero){if(peerSpeech.phase!=='idle')hidePeerSay();showSay(words);}
  else showPeerSay(words,speaker+'：');
  more.hidden=!!opts;
  choices.replaceChildren(...(opts||[]).map(o=>{const b=document.createElement('button');b.type='button';b.innerHTML='<i class="bg" aria-hidden="true"></i><span></span>';b.lastChild.textContent=o.label;b.onclick=e=>{e.stopPropagation();o.on?.();};return b;}));
  choices.hidden=!opts||hero;choices.classList.toggle('quest',special);
  if(!choices.hidden){const H=popSay.offsetHeight||parseFloat(getComputedStyle(widget).getPropertyValue('--say-h'))||48,[outer,inner]=sayClip(Math.round(H/2)*2,0,12,12,2,0);
   choices.style.setProperty('--choice-clip',outer);choices.style.setProperty('--choice-in',inner);popBubble(popSay,0);popSay.hidden=true;}
  const box=hero?popSay:peerBubble;box.tabIndex=0;box.setAttribute('role','button');
  box.setAttribute('aria-label',`${speaker}：${spokenText(words)}${opts?'':last?'（点一下结束）':'（点一下继续）'}`);
  mark();cancelAnimationFrame(keep);hold();
  (opts&&!hero?choices.querySelector('button'):box).focus({preventScroll:true,focusVisible:false});
 }
 const go=e=>{if(!open||!advance)return;e.preventDefault();e.stopPropagation();advance();};
 for(const box of [peerBubble,popSay]){
  box.addEventListener('click',e=>{if(open&&box.classList.contains('story-bubble'))go(e);});
  box.addEventListener('keydown',e=>{if(open&&box.classList.contains('story-bubble')&&(e.key==='Enter'||e.key===' '))go(e);});
 }
 document.addEventListener('keydown',e=>{if(open&&e.key==='Escape'){e.preventDefault();e.stopPropagation();onClose();}},true);
 function hide(){
  if(!open)return;open=false;advance=null;cancelAnimationFrame(keep);more.remove();choices.replaceChildren();choices.hidden=true;
  peerHud.classList.remove('quest');popSay.classList.remove('quest');mark();
  for(const box of [peerBubble,popSay]){box.removeAttribute('tabindex');box.removeAttribute('role');box.removeAttribute('aria-label');}
  hidePeerSay();popBubble(popSay,0);sayBusy=busyWas;
  if(previous?.isConnected)previous.focus({preventScroll:true});previous=null;
 }
 return {el:peerHud,show,hide,position(){},get open(){return open}};
}
