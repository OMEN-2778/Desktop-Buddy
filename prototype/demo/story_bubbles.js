// Shared story speech uses the native NPC pill skin/motion; never a full-scene panel.
function createStorySpeech({view,host=view.parentElement,anchor,onClose=()=>{}}){
 const el=document.createElement('section');el.className='npcsay story-speech';el.hidden=true;
 el.setAttribute('role','dialog');el.setAttribute('aria-label','剧情对话');
 const name=document.createElement('strong'),text=document.createElement('div'),actions=document.createElement('div');
 name.className='story-speaker';text.className='story-words';text.setAttribute('aria-live','polite');actions.className='story-actions';
 const next=document.createElement('button'),exit=document.createElement('button');next.type=exit.type='button';exit.textContent='暂时收起';exit.onclick=onClose;actions.append(next,exit);el.append(name,text,actions);host.append(el);
 let who='',previous=null;
 function position(){if(el.hidden)return;const box=view.getBoundingClientRect(),parent=host.getBoundingClientRect(),s=box.width/342,p=anchor(who);
  const visible=p&&p.x>=0&&p.x<=342&&p.y>=0&&p.y<=box.height/s;
  name.textContent=who+(visible?'':' · 画外');el.dataset.remote=String(!visible);
  el.style.width=Math.min(box.width-16,Math.max(250,box.width*.54))+'px';el.style.maxHeight=Math.max(90,box.height-12)+'px';
  const x=visible?p.x*s:box.width/2,y=visible?(p.y-30)*s:box.height;
  const w=el.offsetWidth,h=el.offsetHeight,left=Math.max(8,Math.min(box.width-w-8,x-w/2));
  let top=y-h-7;if(top<6)top=Math.min(box.height-h-6,Math.max(6,y+34*s));
  el.style.left=box.left-parent.left+left+w/2+'px';el.style.top=box.top-parent.top+Math.max(6,top)+h+'px';
 }
 function show(speaker,words,{special=true,last=false,advance}={}){if(el.hidden)previous=document.activeElement;who=speaker;el.hidden=false;el.classList.toggle('quest-speech',special);text.textContent=spokenText(words);next.textContent=last?'说完了':'继续';next.onclick=advance;position();next.focus({preventScroll:true});}
 function hide(){el.hidden=true;next.onclick=null;if(previous?.isConnected)previous.focus({preventScroll:true});previous=null;}
 const observer=new ResizeObserver(position);observer.observe(view);window.addEventListener('resize',position);
 return {el,show,hide,position,get open(){return !el.hidden}};
}
