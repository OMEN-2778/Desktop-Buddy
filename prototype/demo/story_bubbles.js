// Story speech IS the native NPC pill (owner, 2026-11-02): the same small rounded
// bubble strangers talk in, over the speaker's head. No panel, no 继续 button: click
// the bubble (or Enter / Space) for the next line; a blinking pixel ▼ says there is
// more. Choices are pills right under the bubble. Esc folds it away (onClose).
// Quest lines tint the bubble white -> pale blue. Off-screen speakers are named and
// stay where they are (the bubble sits at the top of the scene), never teleported.
function createStorySpeech({view,host=view.parentElement,anchor,onClose=()=>{}}){
 const el=document.createElement('section');el.className='story-speech';el.hidden=true;
 el.setAttribute('role','dialog');el.setAttribute('aria-label','剧情对话');
 const bubble=document.createElement('div'),name=document.createElement('span'),text=document.createElement('span'),more=document.createElement('i'),choices=document.createElement('div');
 bubble.className='story-bubble';bubble.tabIndex=0;bubble.setAttribute('role','button');
 name.className='story-speaker';text.className='story-words';text.setAttribute('aria-live','polite');more.className='story-more';more.setAttribute('aria-hidden','true');choices.className='story-choices';
 bubble.append(name,text,more);el.append(bubble,choices);host.append(el);
 let who='',previous=null,advance=null;
 function position(){if(el.hidden)return;const box=view.getBoundingClientRect(),parent=host.getBoundingClientRect(),s=box.width/342,p=anchor(who);
  const visible=!!p&&p.x>=0&&p.x<=342&&p.y>=0&&p.y<=box.height/s;
  name.textContent=visible?'':who+'（画外）';name.hidden=visible;el.dataset.remote=String(!visible);
  el.style.setProperty('--story-w',Math.round(Math.min(box.width-16,Math.max(170,box.width*.46)))+'px');
  const w=el.offsetWidth,h=el.offsetHeight;
  const x=Math.max(8+w/2,Math.min(box.width-8-w/2,visible?p.x*s:box.width/2));
  const bottom=Math.max(h+4,visible?(p.y-29)*s:h+6*s);                            // just above the head
  el.style.left=box.left-parent.left+x+'px';el.style.top=box.top-parent.top+Math.min(box.height-4,bottom)+'px';
 }
 function show(speaker,words,{special=true,last=false,advance:next,choices:opts=null}={}){
  if(el.hidden)previous=document.activeElement;who=speaker;advance=opts?null:next;
  el.hidden=false;el.classList.toggle('quest-speech',special);el.classList.remove('pop');void el.offsetWidth;el.classList.add('pop');
  text.textContent=spokenText(words);more.hidden=!!opts;bubble.dataset.last=String(last);
  bubble.setAttribute('aria-label',`${speaker}：${text.textContent}${opts?'':last?'（点一下结束）':'（点一下继续）'}`);
  choices.replaceChildren(...(opts||[]).map(o=>{const b=document.createElement('button');b.type='button';b.textContent=o.label;b.onclick=e=>{e.stopPropagation();o.on?.();};return b;}));
  choices.hidden=!opts;position();(opts?choices.querySelector('button'):bubble).focus({preventScroll:true,focusVisible:false});
 }
 const go=e=>{if(!advance)return;e?.preventDefault?.();e?.stopPropagation?.();advance();};
 bubble.addEventListener('click',go);
 bubble.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' ')go(e);});
 el.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();onClose();}});
 function hide(){el.hidden=true;advance=null;choices.replaceChildren();if(previous?.isConnected)previous.focus({preventScroll:true});previous=null;}
 const observer=new ResizeObserver(position);observer.observe(view);window.addEventListener('resize',position);
 return {el,show,hide,position,get open(){return !el.hidden}};
}
