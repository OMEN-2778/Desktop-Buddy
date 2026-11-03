// 任务 panel (owner 2026-11-03), game-shell test page only (never make_demo.py / releases).
// Like 人脉: hovering the diary button slides a 任务 button out to its left; hovering that opens one big
// panel on the right, from above the diary row down to the house's bottom. Unfinished quests first:
// a big title, then a small line with what to do now. Sources register with questBoard.add(fn).
const questBoard=(function(){
 const sources=[];
 const css=`
.quest-trigger{position:absolute;z-index:18;width:48px;height:48px;margin:0;padding:8px;border:0;background:none;box-shadow:none;border-radius:0;cursor:pointer;opacity:0;visibility:hidden;pointer-events:none;
 transform:translateX(-46px) scale(.7);transition:transform .46s var(--hud-spring),opacity .18s,visibility 0s .46s;isolation:isolate;filter:drop-shadow(2px 2px 0 var(--shadow,#0002))}
.quest-trigger::before,.quest-trigger::after{content:"";position:absolute;pointer-events:none}
.quest-trigger::before{inset:0;z-index:-2;background:var(--ring,#bebdcc);clip-path:var(--hud-circle-clip)}
.quest-trigger::after{inset:2px;z-index:-1;background:#fff4c4;clip-path:var(--hud-circle-in);box-shadow:inset 0 2px 0 #fff,inset 0 -2px 0 #e2c98f}
.quest-trigger canvas{display:block;width:32px;height:32px;image-rendering:pixelated;transition:translate .12s var(--hud-settle)}
.quest-trigger:hover{background:none}.quest-trigger:hover canvas{translate:0 -1px}.quest-trigger:active canvas{translate:0 2px}
.moodrow.quest-ready .quest-trigger,.moodrow.quests-open .quest-trigger,.quest-trigger:focus-visible{z-index:23;pointer-events:auto;transform:translateX(-62px) scale(1);opacity:1;visibility:visible;transition-delay:0s}
.quest-trigger b{position:absolute;right:-2px;top:-2px;min-width:16px;height:16px;padding:0 3px;font:700 11px/16px var(--font);color:#fff;background:#d9534f;
 clip-path:var(--hud-small-clip);animation:qbPulse 1.6s ease-in-out infinite}
.quest-trigger b:empty{display:none}
.quest-bridge{position:absolute;z-index:22;width:72px;height:52px;display:none}
.moodrow.quest-ready .quest-bridge,.moodrow.quests-open .quest-bridge{display:block}
.quest-panel{position:absolute;z-index:70;padding:14px 14px 12px;opacity:0;visibility:hidden;pointer-events:none;isolation:isolate;color:var(--ink);
 transform:translateX(-14px) scale(.97);transform-origin:0 18%;transition:transform .44s var(--hud-spring),opacity .2s,visibility 0s .44s;filter:drop-shadow(3px 3px 0 var(--shadow,#0002));
 display:flex;flex-direction:column;gap:10px}
.quest-panel::before,.quest-panel::after{content:"";position:absolute;pointer-events:none}
.quest-panel::before{inset:0;z-index:-2;background:var(--edge);clip-path:var(--hud-panel-clip)}
.quest-panel::after{inset:2px;z-index:-1;background:var(--panel);clip-path:var(--hud-panel-in);box-shadow:inset 0 2px 0 var(--bevel-hi),inset 0 -2px 0 var(--bevel-lo)}
.quest-panel.on{opacity:1;visibility:visible;pointer-events:auto;transform:none;transition-delay:0s}
.quest-tail{position:absolute;left:-12px;top:20px;width:14px;height:20px;background:var(--edge);clip-path:polygon(100% 0,10px 0,10px 2px,8px 2px,8px 4px,6px 4px,6px 6px,4px 6px,4px 8px,2px 8px,2px 12px,4px 12px,4px 14px,6px 14px,6px 16px,8px 16px,8px 18px,10px 18px,10px 20px,100% 20px)}
.quest-tail::after{content:"";position:absolute;inset:2px -2px 2px 2px;background:var(--panel);clip-path:inherit}
.qb-head{display:flex;align-items:center;gap:10px;padding:0 4px 8px;border-bottom:2px dashed var(--bevel-lo)}
.qb-head canvas{width:32px;height:32px;image-rendering:pixelated}
.qb-head h3{margin:0;font:700 calc(20px * var(--fs,1))/1.1 var(--font);letter-spacing:2px}
.qb-head small{margin-left:auto;color:var(--muted);font-size:calc(12px * var(--fs,1))}
.qb-head small i{font-style:normal;color:#b5452f;font-weight:700}
.qb-list{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;display:flex;flex-direction:column;gap:8px;padding:2px 6px 4px 2px;scrollbar-width:thin;scrollbar-color:var(--bevel-lo) transparent;overscroll-behavior:contain}
.qb-card{position:relative;isolation:isolate;display:grid;grid-template-columns:36px minmax(0,1fr) auto;align-items:center;gap:2px 12px;padding:10px 14px 10px 10px;flex:none;
 opacity:0;translate:0 8px;transition:translate .25s var(--hud-settle),filter .2s}
.qb-card::before,.qb-card::after{content:"";position:absolute;pointer-events:none}
.qb-card::before{inset:0;z-index:-2;background:var(--qb-edge,var(--bevel-lo));clip-path:var(--hud-card-clip)}
.qb-card::after{inset:2px;z-index:-1;background:var(--qb-bg,var(--panel-2));clip-path:var(--hud-card-in);box-shadow:inset 0 2px 0 var(--bevel-hi)}
.quest-panel.on .qb-card{animation:qbIn .42s var(--hud-spring) forwards;animation-delay:calc(.06s + var(--i) * .05s)}
.qb-card.live{--qb-edge:#c79a52;--qb-bg:#fff8dc}
.qb-card.live:hover{translate:0 -2px;--qb-edge:#b5452f}
.qb-card.done{--qb-bg:var(--panel);filter:saturate(.35)}
.qb-ico{grid-row:1/3;width:36px;height:36px;display:grid;place-items:center;position:relative}
.qb-ico canvas{width:32px;height:32px;image-rendering:pixelated}
.qb-card.live.new .qb-ico canvas{animation:qbBob 1.4s ease-in-out infinite}
.qb-card strong{font:700 calc(18px * var(--fs,1))/1.2 var(--font);min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.qb-card.done strong{color:var(--muted);text-decoration:line-through 2px #b9b6c8}
.qb-card p{grid-column:2;margin:0;font-size:calc(13px * var(--fs,1));color:var(--muted);display:flex;align-items:center;gap:6px;min-width:0}
.qb-card.live p{color:#7a5a2c}
.qb-card.live p::before{content:"";flex:none;width:6px;height:8px;background:#c4632f;clip-path:polygon(0 0,2px 0,2px 2px,4px 2px,4px 4px,6px 4px,6px 4px,4px 4px,4px 6px,2px 6px,2px 8px,0 8px);animation:qbNudge 1.2s ease-in-out infinite}
.qb-tags{grid-row:1/3;grid-column:3;display:flex;flex-direction:column;align-items:flex-end;gap:4px}
.qb-tags span{padding:1px 7px;font-size:calc(11px * var(--fs,1));line-height:17px;white-space:nowrap;color:#fff;background:var(--tag,#8a87a0);clip-path:var(--hud-trait-clip)}
.qb-tags span.place{background:#7aa86a}
.qb-sep{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:calc(12px * var(--fs,1));margin:4px 2px 0;opacity:0}
.quest-panel.on .qb-sep{animation:qbIn .42s var(--hud-spring) forwards;animation-delay:calc(.06s + var(--i) * .05s)}
.qb-sep::after{content:"";flex:1;border-top:2px dotted var(--bevel-lo)}
.qb-stamp{position:absolute;right:86px;top:50%;translate:0 -50%;rotate:-8deg;padding:0 6px;font:700 12px/18px var(--font);color:#b5452f;border:2px solid #b5452f;opacity:.75}
.qb-empty{margin:auto;text-align:center;color:var(--muted);font-size:calc(14px * var(--fs,1));line-height:1.8}
@keyframes qbIn{to{opacity:1;translate:0 0}}
@keyframes qbBob{50%{translate:0 -2px}}
@keyframes qbNudge{50%{translate:2px 0}}
@keyframes qbPulse{50%{scale:1.12}}
@media (prefers-reduced-motion:reduce){.quest-trigger,.quest-panel,.qb-card,.qb-sep{transition:none!important;animation:none!important;opacity:1;translate:none}.quest-trigger b,.qb-card canvas,.qb-card p::before{animation:none!important}}
`;
 document.head.append(Object.assign(document.createElement('style'),{textContent:css}));
 // ---------------------------------------------------------------- pixel icons (16x16, drawn 2x)
 const PAL={o:'#22182a',p:'#f6e7c1',s:'#dcc28e',l:'#a4865a',r:'#d9534f',R:'#9e3a3a',w:'#fffaf0',g:'#7aa86a',G:'#4f7a45',y:'#f6d36b',Y:'#c99a2e',b:'#6f9fd0',B:'#3f6f9e',k:'#b9b6c8',K:'#8a87a0'};
 const ICON={
  scroll:['................','.oooooooooooooo.','osswwwwwwwwwwsso','.oooooooooooooo.','..owpppppppppo..','..opllllllppso..','..opppppppppso..','..oplllllllpso..','..opppppppppso..','..oplllllrrrso..','..opppppprRrso..','..opppppprrrso..','.oooooooooooooo.','osswwwwwwwwwwsso','.oooooooooooooo.','................'],
  funny:['................','.....oooooo.....','...ooyyyyyyoo...','..oyyyyyyyyyYo..','..oyyoyyyyoyYo..','.oyyyoyyyyoyyYo.','.oyyyyyyyyyyyYo.','.oyyoyyyyyyoyYo.','.oyyyooooooyyYo.','.oyyyoRRRRoyyYo.','..oyyyoRRoyyYo..','..oYyyyooyyYYo..','...ooYYYYYYoo...','.....oooooo.....','................','................'],
  sad:['................','.......oo.......','......obbo......','.....obbbbo.....','....obbbbbbo....','....obwbbbbo....','...obwbbbbbbo...','...obbbbbbbBo...','...obbbbbbbBo...','...obbbbbbBBo...','....obbbbBBo....','.....oBBBBo.....','......oooo......','................','................','................'],
  mystery:['................','....oooo........','...okkkko.......','..okwkkkko......','.okwkkkkkko.....','.okkkkkkkko.....','.okkkkkkkko.....','.okkkkkkkko.....','..okkkkkKo......','...okkKKoo......','....oooooKo.....','.........oKo....','..........oKo...','...........oo...','................','................'],
  gift:['................','.....oo..oo.....','....orro.orro...','.....orroRro....','..ooooooooooo...','..orrrrrRrrro...','..ooooooooooo...','...oggggRgggo...','...ogwggRgggo...','...oggggRgggo...','...oggggRggGo...','...oggggRgGGo...','...ooooooooo....','................','................','................'],
  home:['................','.......oo.......','......orro......','.....orrrro.....','....orrrrrro....','...orrrrrrrro...','..oooooooooooo..','...oppppppppo...','...oplloppllo...','...oplloppllo...','...oppppppppo...','...opppoopppo...','...opppoYppo....','...oooooooooo...','................','................']};
 function iconCanvas(name){const rows=ICON[name]||ICON.scroll,c=document.createElement('canvas');c.width=c.height=16;const g=c.getContext('2d');
  rows.forEach((r,y)=>[...r].forEach((ch,x)=>{if(PAL[ch]){g.fillStyle=PAL[ch];g.fillRect(x,y,1,1);}}));return c;}
 // ---------------------------------------------------------------- DOM
 const moodrow=document.getElementById('moodrow'),diary=document.getElementById('diary'),col=moodrow.parentElement;
 const trigger=document.createElement('button');trigger.type='button';trigger.className='quest-trigger';trigger.id='questTrigger';trigger.setAttribute('aria-label','任务');trigger.title='任务';
 trigger.setAttribute('aria-expanded','false');trigger.setAttribute('aria-controls','questPanel');trigger.append(iconCanvas('scroll'),document.createElement('b'));
 const bridge=document.createElement('i');bridge.className='quest-bridge';bridge.setAttribute('aria-hidden','true');
 moodrow.append(bridge,trigger);
 const panel=document.createElement('section');panel.className='quest-panel';panel.id='questPanel';panel.setAttribute('aria-label','任务');panel.setAttribute('aria-hidden','true');panel.inert=true;
 panel.innerHTML='<i class="quest-tail" aria-hidden="true"></i><header class="qb-head"><h3>任务</h3><small></small></header><div class="qb-list" role="list"></div>';
 panel.querySelector('.qb-head').prepend(iconCanvas('scroll'));col.append(panel);
 const list=panel.querySelector('.qb-list'),count=panel.querySelector('.qb-head small');
 function place(){   // trigger: left of the diary circle; panel: right of it, from the diary's top to the house's bottom
  const mr=moodrow.getBoundingClientRect(),dr=diary.getBoundingClientRect(),cr=col.getBoundingClientRect(),vr=view.getBoundingClientRect();
  trigger.style.left=(dr.left-mr.left)+'px';trigger.style.top=(dr.top-mr.top+(dr.height-48)/2)+'px';
  bridge.style.left=(dr.left-mr.left-66)+'px';bridge.style.top=(dr.top-mr.top)+'px';
  const top=dr.top-cr.top-6,left=dr.left-cr.left-6;
  Object.assign(panel.style,{top:top+'px',left:left+'px',width:(vr.right-cr.left-left)+'px',height:(vr.bottom-cr.top-top+6)+'px'});
 }
 // ---------------------------------------------------------------- content
 const KIND={funny:['搞笑','#e0a03a'],sad:['惆怅','#6f9fd0'],mystery:['悬疑','#8a87a0'],gift:['送菜','#7aa86a'],home:['主线','#d9534f']};
 const all=()=>sources.flatMap(f=>{try{return f()||[];}catch(e){console.error(e);return [];}});
 function fill(){const qs=all(),live=qs.filter(q=>!q.done),done=qs.filter(q=>q.done);
  count.innerHTML=qs.length?`进行中 <i>${live.length}</i> · 已完成 ${done.length}`:'';list.replaceChildren();let i=0;
  const card=q=>{const c=document.createElement('div');c.className='qb-card '+(q.done?'done':'live')+(q.isNew?' new':'');c.setAttribute('role','listitem');c.style.setProperty('--i',i++);
   const ico=document.createElement('span');ico.className='qb-ico';ico.append(iconCanvas(q.kind));
   const t=document.createElement('strong');t.textContent=q.title;const p=document.createElement('p');p.textContent=q.done?(q.end||'完成了'):q.step;
   const tags=document.createElement('span');tags.className='qb-tags';
   const k=KIND[q.kind];if(k){const s=document.createElement('span');s.textContent=k[0];s.style.setProperty('--tag',k[1]);tags.append(s);}
   if(q.place){const s=document.createElement('span');s.className='place';s.textContent=q.place;tags.append(s);}
   c.append(ico,t,tags,p);if(q.done){const st=document.createElement('em');st.className='qb-stamp';st.textContent='完成';c.append(st);}return c;};
  live.forEach(q=>list.append(card(q)));
  if(done.length){const s=document.createElement('div');s.className='qb-sep';s.style.setProperty('--i',i++);s.textContent='已完成';list.append(s);done.forEach(q=>list.append(card(q)));}
  if(!qs.length)list.innerHTML='<p class="qb-empty">还没有任务。<br>到处走走，和人聊聊，也许有人需要帮忙。</p>';
 }
 function badge(){const n=all().filter(q=>!q.done&&q.isNew).length;trigger.querySelector('b').textContent=n?String(n):'';}
 setInterval(badge,1500);
 // ---------------------------------------------------------------- open / close (人脉 timings)
 let closeT=0,hideT=0,isOpen=false;
 function reveal(){clearTimeout(hideT);place();moodrow.classList.add('quest-ready');}
 function queueHide(){clearTimeout(hideT);hideT=setTimeout(()=>{if(!isOpen)moodrow.classList.remove('quest-ready');},300);}
 function setOpen(on){clearTimeout(closeT);clearTimeout(hideT);if(on===isOpen)return;isOpen=on;
  if(on){if(typeof phoneHolds==='function'&&phoneHolds()){isOpen=false;return;}reveal();try{setContactsOpen(false);setDiaryOpen(false);setNeedsOpen(false);}catch(e){}fill();badge();}
  moodrow.classList.toggle('quests-open',on);panel.classList.toggle('on',on);panel.inert=!on;panel.setAttribute('aria-hidden',String(!on));trigger.setAttribute('aria-expanded',String(on));
  if(!on)queueHide();}
 function queueClose(){clearTimeout(closeT);closeT=setTimeout(()=>setOpen(false),280);}
 diary.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse')reveal();});
 diary.addEventListener('pointerleave',queueHide);
 bridge.addEventListener('pointerenter',()=>clearTimeout(hideT));bridge.addEventListener('pointerleave',queueHide);
 trigger.addEventListener('pointerenter',e=>{reveal();if(e.pointerType==='mouse')setOpen(true);});
 trigger.addEventListener('pointerleave',e=>{if(e.pointerType==='mouse')queueClose();});
 trigger.addEventListener('focus',reveal);trigger.addEventListener('click',()=>setOpen(!isOpen));
 panel.addEventListener('pointerenter',()=>{clearTimeout(closeT);clearTimeout(hideT);});
 panel.addEventListener('pointerleave',e=>{if(e.pointerType!=='touch')queueClose();});
 document.addEventListener('pointerdown',e=>{if(isOpen&&!panel.contains(e.target)&&!trigger.contains(e.target))setOpen(false);});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&isOpen){setOpen(false);trigger.focus();}});
 window.addEventListener('resize',()=>{if(isOpen||moodrow.classList.contains('quest-ready'))place();});
 return {add:f=>sources.push(f),open:()=>setOpen(true),close:()=>setOpen(false),fill,get isOpen(){return isOpen;},panel,trigger};
})();
window.questBoard=questBoard;
