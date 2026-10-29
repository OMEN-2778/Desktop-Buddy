// Clicking the pet (user: redone to match the rest of the UI): the same ring
// of round pixel buttons that pops around Buddy pops around the pet (its name
// on top; 遛猫 ▸ / 喂零食 ▸ swap in a second ring with 返回), and above it a
// status card styled like the needs panel: four bars springing up one after
// another (饱腹 / 精力 / 陪伴 / 亲密), the pet's name in a title pill on top
// (click it to rename). Both follow the pet while open.
const petHud=document.createElement('section');petHud.id='petHud';petHud.className='pet-card';petHud.hidden=true;petHud.setAttribute('aria-label','宠物状态');
const petHudState={open:false,closeTimer:0,raf:0};
const petNameButton=petButton('',()=>{closePetHud();petNaming(null,true);},'pc-name');petNameButton.setAttribute('aria-label','给宠物改名');
const petStats=petNode('div',undefined,'pc-stats'),petStatNodes=new Map();
[['hunger','饱腹','hunger'],['energy','精力','energy'],['company','陪伴','smile'],['affinity','亲密',null]].forEach(([key,label,icon],i)=>{
 const column=petNode('div',undefined,'pc-stat');column.style.setProperty('--i',i);column.dataset.stat=key;column.setAttribute('role','meter');column.setAttribute('aria-label',label);column.setAttribute('aria-valuemin','0');column.setAttribute('aria-valuemax','100');
 const well=petNode('span',undefined,'pc-well'),fill=petNode('i',undefined,'pc-fill'),val=petNode('b',undefined,'pc-val');well.append(fill,val);
 let pic;
 if(icon==='smile'){pic=petNode('canvas');pic.width=20;pic.height=20;const ctx=pic.getContext('2d');ctx.fillStyle='#d49438';ctx.fillRect(5,2,10,16);ctx.fillRect(2,5,16,10);ctx.fillStyle='#ffdc78';ctx.fillRect(5,4,10,12);ctx.fillRect(4,6,12,8);ctx.fillStyle='#503540';ctx.fillRect(6,7,2,2);ctx.fillRect(12,7,2,2);ctx.fillRect(6,11,2,2);ctx.fillRect(8,13,4,2);ctx.fillRect(12,11,2,2);}
 else if(icon){pic=petNode('img');pic.alt='';pic.src=D.needIcons[icon];}
 else{pic=petNode('canvas');pic.width=20;pic.height=20;const ctx=pic.getContext('2d'),img=emoteCanvas('heart');ctx.imageSmoothingEnabled=false;ctx.drawImage(img,0,0,img.width,img.height,0,0,20,20);}
 pic.classList.add('pc-icon');const name=petNode('span',label,'pc-label');
 column.append(well,pic,name);petStats.append(column);petStatNodes.set(key,{column,fill,val,label});
});
petHud.append(petNameButton,petStats);document.body.append(petHud);
petHud.style.setProperty('--pc-bar-clip',roundClip(7,1));petHud.style.setProperty('--need-stripes',`url("${D.uiIcons.stripes}")`);
function petRings(){
 const p=petState.pet,cat=petBreed(p.breed).species==='cat';
 RINGS.pet=[['pet:walk',(cat?'遛猫':'遛狗')+' ▸','more'],['pet:treat','喂零食 ▸','more'],['pet:close','亲近 ▸','more'],['pet:fun','玩耍 ▸','more'],['pet:groom','梳毛'],['pet:name','改名字']];
 RINGS.pet_close=[['pet:pat','摸摸头'],['pet:belly','挠肚皮'],['pet:kiss','亲一口'],['pet:hold',p.carried?'放下来':'抱起来'],['pet:talk','聊聊天'],['pet:back','返回','back']];
 RINGS.pet_fun=[['pet:play','逗逗它'],['pet:toy',cat?'逗猫棒':'扔球'],['pet:train','教它小动作'],['pet:photo','拍张照'],['pet:back','返回','back']];
 RINGS.pet_walk=[['pet:go:front','去门口'],['pet:go:park','去公园'],['pet:go:beach','去码头'],['pet:back','返回','back']];
 RINGS.pet_treat=[...PET_TREATS.map(t=>['pet:treat:'+t.id,t.name]),['pet:back','返回','back']];
}
function openPetHud(){
 if(!petCanSee()||wiping||phoneHolds()||card||wardrobeOpen)return;
 closePetMini();closePetPanel();setNeedsOpen(false);clearTimeout(petHudState.closeTimer);
 petRings();openRing('pet','pet');
 const ws=getComputedStyle(document.getElementById('widget'));   // the HUD's clip shapes and colours live on the widget
 for(const k of ['--hud-panel-clip','--hud-panel-in','--hud-small-clip','--clip-btn','--title','--hud-frame','--panel','--panel-2','--edge','--bevel-hi','--bevel-lo','--shadow','--ink','--need-ok','--need-warn','--need-low','--ui-font-label','--focus']){const v=ws.getPropertyValue(k);if(v)petHud.style.setProperty(k,v);}
 petHudState.open=true;petHud.hidden=false;petHud.classList.remove('on','off');fitPetHud();
 void petHud.offsetWidth;petHud.classList.add('on');
 cancelAnimationFrame(petHudState.raf);const follow=()=>{if(!petHudState.open)return;fitPetHud();petHudState.raf=requestAnimationFrame(follow);};petHudState.raf=requestAnimationFrame(follow);
}
function closePetHud(){
 if(!petHudState.open)return;petHudState.open=false;cancelAnimationFrame(petHudState.raf);
 if(typeof ringAt!=='undefined'&&ringAt==='pet'&&ringOf)closeRing();
 petHud.classList.remove('on');petHud.classList.add('off');clearTimeout(petHudState.closeTimer);
 petHudState.closeTimer=setTimeout(()=>{if(!petHudState.open){petHud.hidden=true;petHud.classList.remove('off');}},reduceMotionUI?0:260);
}
// a pick on the pet's ring
function petRingPick(k){
 if(['walk','treat','close','fun'].includes(k)){openRing('pet_'+k,'pet');return;}
 if(k==='back'){petRings();openRing('pet','pet');
 const ws=getComputedStyle(document.getElementById('widget'));   // the HUD's clip shapes and colours live on the widget
 for(const k of ['--hud-panel-clip','--hud-panel-in','--hud-small-clip','--clip-btn','--title','--hud-frame','--panel','--panel-2','--edge','--bevel-hi','--bevel-lo','--shadow','--ink','--need-ok','--need-warn','--need-low','--ui-font-label','--focus']){const v=ws.getPropertyValue(k);if(v)petHud.style.setProperty(k,v);}return;}
 if(k.startsWith('go:')){closePetHud();beginPetWalk(k.slice(3));return;}
 if(k.startsWith('treat:')){closePetHud();offerPetTreat(k.slice(6));return;}
 if(k==='name'){closePetHud();petNaming(null,true);return;}
 petInteract(k);
}
function togglePetSubmenu(kind){if(!petHudState.open)openPetHud();petRingPick(kind);}   // (old name, kept for callers)
function fitPetHud(){
 if(!petHudState.open)return;
 if(!petCanSee()||wiping||phoneHolds()||card||wardrobeOpen||!petPanel.hidden||!(ringAt==='pet'&&ringOf)){closePetHud();return;}
 const p=petState.pet,v=view.getBoundingClientRect(),growth=Math.max(0,Math.min(1,(v.width-342)/1026));
 petHud.style.setProperty('--pc-fs',Math.round(12+growth*3)+'px');petHud.style.setProperty('--pc-col',Math.round(34+growth*8)+'px');
 if(petNameButton.textContent!==p.name){petNameButton.textContent=p.name;petNameButton.title='点击给'+p.name+'改名';}
 for(const [key,{column,fill,val,label}]of petStatNodes){
  const value=Math.round(key==='affinity'?(p.affinity??30):p.needs[key]);
  if(column.getAttribute('aria-valuenow')!==String(value)){column.setAttribute('aria-valuenow',value);column.title=label+' '+value;val.textContent=value;fill.style.setProperty('--v',value/100);
   fill.style.setProperty('--c',key==='affinity'?'#e9a1c0':value<20?'var(--need-low)':value<40?'var(--need-warn)':'var(--need-ok)');column.classList.toggle('low',key!=='affinity'&&value<20);}
 }
 // left of the column of pills (petColumnLayout), as tall as it: slim, tall bars (user)
 const btns=[...ringEl.children].map(b=>b.getBoundingClientRect()).filter(r=>r.width);if(!btns.length)return;
 const colL=Math.min(...btns.map(r=>r.left)),colT=Math.min(...btns.map(r=>r.top)),colB=Math.max(...btns.map(r=>r.bottom)),w=petHud.offsetWidth;
 petHud.style.setProperty('--pc-h',Math.round(colB-colT)+'px');
 const left=colL-PET_CARD_GAP-w;
 petHud.style.left=Math.round(left)+'px';petHud.style.top=Math.round(colT)+'px';petHud.style.setProperty('--pc-ox','100%');petHud.classList.remove('below');
}
// the menu's pills stacked in one column right of the card; the pair sits centred over the pet
const PET_CARD_GAP=10;
function petCardWidth(){const v=view.getBoundingClientRect(),growth=Math.max(0,Math.min(1,(v.width-342)/1026));return 4*Math.round(34+growth*8)+6+16;}
function petColumnLayout(sz,gap){
 const g=6,H=sz.reduce((a,[,h])=>a+h,0)+g*(sz.length-1),colW=Math.max(...sz.map(([w])=>w)),cardW=petCardWidth();
 const groupW=cardW+PET_CARD_GAP+colW,above=Math.round(10*scale);   // its bottom just over the pet's head
 const colX=Math.round(-groupW/2+cardW+PET_CARD_GAP+colW/2);let y=-above-H;
 const pos=sz.map(([,h])=>{const p=[colX,Math.round(y+h/2)];y+=h+g;return p;});
 return {pos,extra:{l:-groupW/2,t:-above-H,h:H}};
}
document.addEventListener('pointerdown',e=>{if(petHudState.open&&!petHud.contains(e.target)&&!ringEl.contains(e.target))closePetHud();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closePetHud();});
