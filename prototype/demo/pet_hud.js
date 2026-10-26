// A body-level layer keeps the whole pet toolbar above the time/needs HUD.
const petHud=document.createElement('section');petHud.id='petHud';petHud.className='pet-hud';petHud.hidden=true;petHud.inert=true;petHud.setAttribute('aria-label','宠物状态与互动');
const petHudState={open:false,submenu:null,anchor:null,closeTimer:0};
const petCard=petNode('div',undefined,'pet-status-card'),petNameButton=petButton('',()=>{closePetHud();petNaming(null,true);},'pet-name-button');petNameButton.setAttribute('aria-label','给宠物改名');petCard.append(petNameButton);
const petStats=petNode('div',undefined,'pet-stat-bars'),petStatNodes=new Map();
for(const [key,label,icon]of [['hunger','饱腹','hunger'],['energy','精力','energy'],['company','陪伴','social'],['affinity','亲密',null]]){
 const column=petNode('div',undefined,'pet-stat');column.dataset.stat=key;column.setAttribute('role','meter');column.setAttribute('aria-label',label);column.setAttribute('aria-valuemin','0');column.setAttribute('aria-valuemax','100');
 const well=petNode('span',undefined,'pet-stat-well'),fill=petNode('i',undefined,'pet-stat-fill');well.append(fill);const disc=petNode('span',undefined,'pet-stat-icon');
 if(icon){const image=petNode('img');image.alt='';image.src=D.needIcons[icon];disc.append(image);}else{const canvas=petNode('canvas');canvas.width=20;canvas.height=20;const ctx=canvas.getContext('2d'),img=emoteCanvas('heart');ctx.imageSmoothingEnabled=false;ctx.drawImage(img,0,0,img.width,img.height,0,0,20,20);disc.append(canvas);}
 column.append(well,disc);petStats.append(column);petStatNodes.set(key,{column,fill,label});
}
petCard.append(petStats);const petActions=petNode('div',undefined,'pet-hud-actions'),petSubmenu=petNode('div',undefined,'pet-hud-submenu');petSubmenu.hidden=true;petSubmenu.setAttribute('role','group');
const petHudButtons={};
for(const [id,label,fn]of [['walk','遛猫',()=>togglePetSubmenu('walk')],['treat','喂零食',()=>togglePetSubmenu('treat')],['play','逗逗它',()=>petInteract('play')],['hold','抱起来',()=>petInteract('hold')],['groom','梳毛',()=>petInteract('groom')]]){
 const button=petButton(label,fn);button.dataset.petAction=id;petHudButtons[id]=button;if(['walk','treat'].includes(id)){button.setAttribute('aria-expanded','false');button.setAttribute('aria-controls','petSubmenu');}petActions.append(button);
}
petSubmenu.id='petSubmenu';petHud.append(petCard,petActions,petSubmenu);document.body.append(petHud);
petHud.style.setProperty('--pet-bar-clip',roundClip(7,1));petHud.style.setProperty('--pet-icon-clip',roundClip(5,2));petHud.style.setProperty('--need-stripes',`url("${D.uiIcons.stripes}")`);
function openPetHud(){if(!petCanSee()||wiping||phoneHolds()||card||wardrobeOpen)return;closeRing();closePetMini();closePetPanel();setNeedsOpen(false);clearTimeout(petHudState.closeTimer);petHudState.open=true;petHudState.submenu=null;petHudState.anchor={...petPoint()};petHud.hidden=false;petHud.inert=false;petSubmenu.hidden=true;for(const id of ['walk','treat'])petHudButtons[id].setAttribute('aria-expanded','false');fitPetHud();requestAnimationFrame(()=>{if(petHudState.open)petHud.classList.add('on');});}
function closePetHud(){if(!petHudState.open)return;petHudState.open=false;petHud.classList.remove('on');petHud.inert=true;clearTimeout(petHudState.closeTimer);petHudState.closeTimer=setTimeout(()=>{if(!petHudState.open)petHud.hidden=true;},reduceMotionUI?0:180);}
function togglePetSubmenu(kind){const open=petHudState.submenu!==kind;petHudState.submenu=open?kind:null;petSubmenu.replaceChildren();petSubmenu.hidden=!open;petSubmenu.dataset.kind=kind;petSubmenu.setAttribute('aria-label',kind==='walk'?'遛宠物去哪里':'选择宠物零食');for(const id of ['walk','treat'])petHudButtons[id].setAttribute('aria-expanded',String(open&&id===kind));if(!open){fitPetHud();return;}
 const options=kind==='walk'?[['front','去门口'],['park','去公园'],['beach','去码头']]:PET_TREATS.map(t=>[t.id,t.name]);
 for(const [id,label]of options){const b=petButton(label,()=>kind==='walk'?beginPetWalk(id):offerPetTreat(id));b.dataset.petChoice=id;petSubmenu.append(b);}fitPetHud();
}
function fitPetHud(){if(!petHudState.open)return;if(!petCanSee()||wiping||phoneHolds()||card||wardrobeOpen||!petPanel.hidden){closePetHud();return;}
 const p=petState.pet,viewRect=view.getBoundingClientRect(),growth=Math.max(0,Math.min(1,(viewRect.width-342)/1026));
 petHud.style.setProperty('--pet-fs',Math.round(12+growth*4)+'px');petHud.style.setProperty('--pet-card-w',Math.round(124+growth*28)+'px');petHud.style.setProperty('--pet-action-w',Math.round(94+growth*24)+'px');petHud.style.setProperty('--pet-row-h',Math.round(32+growth*4)+'px');petHud.style.setProperty('--pet-gap',Math.round(6+growth*2)+'px');
 petNameButton.textContent=p.name;petNameButton.title='点击给'+p.name+'改名';petHudButtons.walk.textContent=petBreed(p.breed).species==='cat'?'遛猫':'遛狗';petHudButtons.hold.textContent=p.carried?'放下来':'抱起来';
 for(const [key,{column,fill,label}]of petStatNodes){const value=Math.round(key==='affinity'?(p.affinity??30):p.needs[key]);column.setAttribute('aria-valuenow',value);column.title=label+' '+value;fill.style.setProperty('--v',value/100);fill.style.backgroundColor=key==='affinity'?'#e9a1c0':value<20?'var(--need-low)':value<40?'var(--need-warn)':'var(--need-ok)';}
 const width=petHud.offsetWidth,height=petHud.offsetHeight,anchor=petHudState.anchor||petPoint();const left=Math.max(viewRect.left+4,Math.min(viewRect.right-width-4,viewRect.left+anchor.x*scale-width/2));const top=Math.max(8,Math.min(innerHeight-height-8,viewRect.top+(anchor.y-24)*scale-height-12));
 petHud.style.left=Math.round(left)+'px';petHud.style.top=Math.round(top)+'px';
}
document.addEventListener('pointerdown',e=>{if(petHudState.open&&!petHud.contains(e.target))closePetHud();});document.addEventListener('keydown',e=>{if(e.key==='Escape')closePetHud();});
