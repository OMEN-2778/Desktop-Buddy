// Story speech goes into the game's own conversation rows (owner, 2026-11-02):
// other people speak in the upper 对方 row (peer_dialogue.js: wooden bubble, "妈妈：",
// their avatar on the right), Buddy in her own lower bubble. No extra panel and no
// 继续 button: a line moves on by itself after 4 s, or at a click anywhere (or Enter / Space) (owner 2026-11-03); a blinking
// pixel ▼ says there is more. Choices take Buddy's own bubble row (she is not
// speaking then): same height and round ends, the row split evenly between them. Esc
// folds the talk away (onClose). Quest lines tint the bubble white -> pale blue.
// While a talk is open the rows never time out. API kept for autumn/spring/summer.
// Story lock (owner, 2026-11-03: "story talks must be immersive"). While a story talk is open, or a story
// scene holds (STORY_HOLDS, e.g. a quest walking between lines), nothing interrupts: no calls, texts or visits,
// no chance cards or events, no stray lines from her, no leaving; while the talk itself is on screen the clock
// stops (cardHolds), so her needs stand still. A story never starts over a phone call: it waits for it to end.
var STORY_SPEECHES=[],STORY_HOLDS=[];   // var: speak() may run before this line during boot
function storySpeechOpen(){return !!STORY_SPEECHES&&STORY_SPEECHES.some(s=>s.open);}
function storyLocked(){return storySpeechOpen()||!!STORY_HOLDS&&STORY_HOLDS.some(f=>{try{return !!f();}catch(e){return false;}});}
function storyWaitsForPhone(){
 if(typeof phoneCall!=='undefined'&&phoneCall.phase==='waiting'){phoneCall.phase='idle';phoneCall.contactId=null;socialState.nextCall=sim.t+120;}   // a call not yet ringing gives way
 return (typeof phoneHolds==='function'&&phoneHolds())||(typeof remoteSocial!=='undefined'&&!!remoteSocial);
}
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
 let waiting=null,waitT=0;
 const AUTO_MS=4000;let autoT=0;
 function show(speaker,words,o){   // over a call: wait until it is over, then speak
  if(!open&&storyWaitsForPhone()){waiting=[speaker,words,o];if(!waitT)waitT=setInterval(()=>{if(storyWaitsForPhone())return;clearInterval(waitT);waitT=0;const w=waiting;waiting=null;if(w)show0(...w);},250);return;}
  return show0(speaker,words,o);
 }
 function show0(speaker,words,{special=true,last=false,advance:next,choices:opts=null}={}){
  if(!open)previous=document.activeElement,busyWas=sayBusy;
  open=true;hero=speaker===nameOf();advance=opts?null:next;
  peerHud.classList.toggle('quest',!hero&&special);popSay.classList.toggle('quest',hero&&special);
  if(hero){if(peerSpeech.phase!=='idle')hidePeerSay();showSay(words);}
  else{if(!popSay.hidden)popBubble(popSay,0);showPeerSay(words,speaker+'：');}   // her own row stays quiet while someone else talks
  more.hidden=!!opts;
  choices.replaceChildren(...(opts||[]).map(o=>{const b=document.createElement('button');b.type='button';b.innerHTML='<i class="bg" aria-hidden="true"></i><span></span>';b.lastChild.textContent=o.label;b.onclick=e=>{e.stopPropagation();o.on?.();};return b;}));
  choices.hidden=!opts||hero;choices.classList.toggle('quest',special);
  choices.classList.remove('wrap');if(!choices.hidden&&[...choices.querySelectorAll('span')].some(s=>s.scrollWidth>s.clientWidth+1))choices.classList.add('wrap');   // too many to fit: the rest go on a second row
  if(!choices.hidden){const H=popSay.offsetHeight||parseFloat(getComputedStyle(widget).getPropertyValue('--say-h'))||48,[outer,inner]=sayClip(Math.round(H/2)*2,0,12,12,2,0);
   choices.style.setProperty('--choice-clip',outer);choices.style.setProperty('--choice-in',inner);popBubble(popSay,0);popSay.hidden=true;}
  requestAnimationFrame(()=>{if(typeof liftDiary==='function')liftDiary();});
  const box=hero?popSay:peerBubble;box.tabIndex=0;box.setAttribute('role','button');
  box.setAttribute('aria-label',`${speaker}：${spokenText(words)}${opts?'':last?'（点一下结束）':'（点一下继续）'}`);
  mark();cancelAnimationFrame(keep);hold();
  (opts&&!hero?choices.querySelector('button'):box).focus({preventScroll:true,focusVisible:false});

  clearTimeout(autoT);if(advance){const mine=advance;autoT=setTimeout(()=>{if(open&&advance===mine)advance();},AUTO_MS);}   // a line moves on by itself after 4 s
 }
 const go=e=>{if(!open||!advance)return;e.preventDefault();e.stopPropagation();advance();};
 // a click anywhere moves the talk on (owner 2026-11-03), and goes no further (the scene does not get it); choices take their own clicks
 let swallow=false;
 document.addEventListener('pointerdown',e=>{swallow=false;if(!open||!advance||e.button!==0)return;swallow=true;go(e);},true);
 document.addEventListener('click',e=>{if(!swallow)return;swallow=false;e.preventDefault();e.stopPropagation();},true);
 for(const box of [peerBubble,popSay]){
  box.addEventListener('click',e=>{if(open&&box.classList.contains('story-bubble'))go(e);});
  box.addEventListener('keydown',e=>{if(open&&box.classList.contains('story-bubble')&&(e.key==='Enter'||e.key===' '))go(e);});
 }
 document.addEventListener('keydown',e=>{if(open&&e.key==='Escape'){e.preventDefault();e.stopPropagation();onClose();}},true);
 function hide(){
  if(!open)return;open=false;advance=null;clearTimeout(autoT);cancelAnimationFrame(keep);more.remove();choices.replaceChildren();choices.hidden=true;
  peerHud.classList.remove('quest');popSay.classList.remove('quest');mark();
  for(const box of [peerBubble,popSay]){box.removeAttribute('tabindex');box.removeAttribute('role');box.removeAttribute('aria-label');}
  hidePeerSay();popBubble(popSay,0);sayBusy=busyWas;
  if(previous?.isConnected)previous.focus({preventScroll:true});previous=null;
 }
 const api={el:peerHud,show,hide,position(){},get open(){return open},get waiting(){return !!waiting}};STORY_SPEECHES.push(api);return api;
}
