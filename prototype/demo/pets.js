// Adoption UI and pet actor. Rules, activities and toolbar live in separate modules.
let petState=PetRules.fresh(),petPanelPage=null,petSelection=null,petHover=null;
const petImages=new Map(),petFurnitureImages={},petClips=new Map(D.pets.breeds.map(b=>[b.id,new Map(b.clips.map(c=>[c.id+':'+c.direction,c]))]));
const petBreed=id=>D.pets.breeds.find(b=>b.id===id);
const petName=()=>petState.pet?.name||'小家伙';
const petText=key=>(PET_TEXT[key]||[''])[Math.floor(PetRules.random(petState)*(PET_TEXT[key]||['']).length)].replaceAll('{宠物}',petName());
const petIsHome=()=>sim.place==='home'&&!atFriendHome()&&!friendHousePreview;
const petCanSee=()=>petState.pet?.status==='home'&&(petIsHome()||petWalkActive());
const petNearby=()=>petCanSee()&&(petWalkActive()||roomAt(here())===roomAt(petPoint()))&&!['bath','toilet'].includes(sim.act);
const petFunMultiplier=()=>sim.t<petState.sadUntil?2:1;
Object.assign(ML,{
 pet_escape:{name:'宠物走丢了',emo:'sad',pts:5,min:2880,fixedDuration:true,noCollapse:true},
 pet_company:{name:'毛茸茸的陪伴',emo:'happy',pts:2,min:120,noCollapse:true},
 pet_return:{name:'小家伙回来了',emo:'happy',pts:3,min:240,noCollapse:true}
});
const petPanel=document.createElement('section');petPanel.id='petPanel';petPanel.hidden=true;petPanel.setAttribute('role','dialog');petPanel.setAttribute('aria-modal','true');petPanel.setAttribute('aria-label','宠物领养与照顾');
petPanel.tabIndex=-1;
petPanel.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const nodes=[...petPanel.querySelectorAll('button,input')].filter(n=>!n.disabled),first=nodes[0],last=nodes[nodes.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}});
petPanel.innerHTML='<header><h3></h3><button type="button" class="pet-close" aria-label="关闭宠物窗口">×</button></header><div class="pet-panel-body"></div>';
document.getElementById('widget').append(petPanel);petPanel.querySelector('.pet-close').onclick=closePetPanel;
function petNode(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function petButton(text,fn,cls){const b=petNode('button',text,cls);b.type='button';b.onclick=()=>{gameAudio.sound('ui-click',.35);fn();};return b;}
function fitPetPanel(){fitPetHud();fitPetMini();if(petPanel.hidden)return;overHouse(petPanel);petPanel.dataset.compact=String(view.offsetWidth<520);}
function closePetPanel(){petPanel.hidden=true;petPanelPage=null;petSelection=null;for(const id of petImages.keys())if(id!==petState.pet?.breed){petImages.delete(id);petImageLoads.delete(id);}}
function petSheet(title,page){closePetHud();closeRing();closePicker();setContactsOpen(false);petPanelPage=page;petPanel.dataset.page=page;petPanel.querySelector('h3').textContent=title;petPanel.hidden=false;const body=petPanel.querySelector('.pet-panel-body');body.replaceChildren();fitPetPanel();petPanel.focus({preventScroll:true});return body;}
function petRefusal(){const reason=PetRules.refusal(petState,sim.t);if(!reason)return false;const body=petSheet('收容所的回复','notice');body.append(petNode('p',reason==='ban'?`这次走失后，我们想先给你和小家伙一点时间。请在 ${Math.ceil((petState.banUntil-sim.t)/1440)} 天后再来申请领养。`:petState.pet.status==='pending'?'送养安排已经记下啦，小家伙还在路上。每个家庭只能领养一只宠物哦。':'家里已经有一位毛茸茸的成员啦，每个家庭只能领养一只宠物。'));body.append(petButton('我知道了',closePetPanel));return true;}
function openPetAdoption(){if(!booted||wiping||phoneHolds()||card||sim.mode==='down')return;if(petRefusal())return;const body=petSheet('每周领养','list');
 const note=petNode('p','这是本周待领养的小猫小狗','pet-list-note');body.append(note);const grid=petNode('div',undefined,'pet-grid');
 for(const offer of PetRules.weekly(petState,sim.t,D.pets.breeds)){const breed=petBreed(offer.breed),b=petButton('',()=>petConfirm(offer),'pet-offer');b.dataset.offer=offer.id;b.setAttribute('aria-label',`${breed.name}，${petTraits(offer)}`);const c=petNode('canvas');c.width=64;c.height=56;paintPetPortrait(c,offer.breed);b.append(c,petNode('strong',breed.name),petNode('span',petTraits(offer)));grid.append(b);}body.append(grid);autoSave();
}
function petTraits(p){return (p.activity==='active'?'活跃':'慵懒')+' · '+(p.attachment==='clingy'?'黏人':'独立');}
function petConfirm(offer){if(petRefusal())return;petSelection=offer;const body=petSheet('宠物领养中心提示','confirm');petSelection=offer;body.append(petNode('p','领养宠物意味着长久的责任，您做好准备了吗？'),petNode('p','记得添粮、陪伴，困了让它好好休息。长期忽略需求，小家伙可能会离家。'),petNode('p','我们为您免费提供了喂食机和睡垫，不用客气！'));const row=petNode('div',undefined,'pet-options');row.append(petButton('我明白',()=>petNaming(offer),'pet-positive'),petButton('我再考虑考虑',openPetAdoption));body.append(row);}
function petNaming(offer,rename=false){
 if(rename?!petState.pet:petRefusal())return;const body=petSheet(rename?'给宠物改个名字':'给新家人取个名字','name');petSelection=offer;
 const nameRow=petNode('div',undefined,'pet-name-row'),input=petNode('input');input.type='text';input.maxLength=16;input.setAttribute('aria-label','宠物名字');input.placeholder='最多 8 个字';if(rename)input.value=petName();
 const dice=petButton('',()=>{const pool=PET_TEXT.petNames.filter(name=>name!==input.value);input.value=pool[Math.floor(PetRules.random(petState)*pool.length)];error.hidden=true;input.focus();},'pet-die');
 dice.setAttribute('aria-label','随机起个宠物名字');dice.title='随机起个宠物名字';
 dice.innerHTML=`<svg width="20" height="20" viewBox="0 0 10 10" fill="currentColor" shape-rendering="crispEdges" aria-hidden="true">${DIE.flatMap((row,y)=>[...row].map((c,x)=>c==='#'?`<rect x="${x}" y="${y}" width="1" height="1"/>`:'')).join('')}</svg>`;
 const field=petNode('label',undefined,'pet-name-field');field.append(input);nameRow.append(field,dice);const error=petNode('p','','pet-error');error.hidden=true;error.setAttribute('role','alert');body.append(nameRow,error);
 const submit=()=>{if(rename){const name=[...input.value.trim()].slice(0,8).join('');if(!name){error.hidden=false;error.textContent='先写个名字吧';return;}const old=petName();petState.pet.name=name;if(old!==name)log(`给${old}改了名字，以后叫「${name}」。`);closePetPanel();autoSave();return;}if(petRefusal())return;if(!PetRules.adopt(petState,offer,input.value,sim.t)){error.hidden=false;error.textContent='给小家伙起个名字吧（最多 8 个字）';return;}ensurePetImage(offer.breed);log(`感谢您的领养，「${petName()}」大概一天后就会送到您家！`);speak('得把家里收拾一下，等新室友报到！',true);closePetPanel();autoSave();};
 input.oninput=()=>{input.value=[...input.value].slice(0,8).join('');error.hidden=true;};input.onkeydown=e=>{e.stopPropagation();if(e.key==='Enter')submit();};body.append(petButton('就叫这个！',submit,'pet-positive'));requestAnimationFrame(()=>input.focus());
}
function paintPetPortrait(canvas,id){
 if(!petImages.has(id)){ensurePetImage(id).then(()=>paintPetPortrait(canvas,id));return;}const ctx=canvas.getContext('2d'),b=petBreed(id),clip=petClips.get(id)?.get('idle:right'),img=petImages.get(id);ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,canvas.width,canvas.height);if(img&&clip)ctx.drawImage(img,0,clip.row*28,32,28,0,0,canvas.width,canvas.height);}

function petPoint(){const p=petState.pet;if(!p)return {x:155,y:FLOOR_Y[0]};if(p.carried){const h=buddyFeet();return {x:h.x+(sim.facing||1)*9,y:h.y-6};}if(p.walk?.position)return p.walk.position;if(p.motion?.route)return routePos(p.motion.route,p.motion.s);return p.position||{x:155,y:FLOOR_Y[0]};}
function petWalkTo(x,y,after='idle',duration=20){const p=petState.pet,from=petPoint();p.motion={route:planRoute(from.x,from.y,x,y),s:0,after,duration};p.activityNow='walk';}
function petStartAction(action,duration){const p=petState.pet;p.animTime=0;p.activityNow=action;if(action==='eat')p.direction='left';p.actionUntil=sim.t+duration;p.motion=null;}
function petInteract(kind){closePetHud();if(!petCanSee()){closePetPanel();showHint('回到家再陪小家伙玩吧');return;}const p=petState.pet;
 if(['bath','toilet','sleep'].includes(sim.act)||sim.mode==='down'){closePetPanel();showHint('先让小人忙完，等会儿再陪它');return;}
 closePetPanel();if(petWalkActive()){petOutdoorInteraction(kind);return;}if(kind==='hold'&&petState.pet.carried){dropCarriedPet();return;}if(kind!=='call'){command('pet_'+kind);return;}const h=here();petWalkTo(Math.max(20,Math.min(325,h.x+(h.x>160?-16:16))),h.y,kind==='play'?'play':kind==='pat'?'nuzzle':'happy',kind==='play'?25:12);
 p.interaction={kind,at:sim.t};autoSave();
}
function petEvent(type,p){if(type==='arrival'){p.position={x:D.spots.front_door[1]-16,y:FLOOR_Y[0]};log(petText('arrival'));if(petIsHome())speak(petText('welcome'),true);}
 else if(type==='escape'){log(petText('escape'));addMood('pet_escape',{diary:false,words:false});moods.get('pet_escape').until=petState.sadUntil;if(petIsHome())speak(petText('missing'),true);autoSave();}
 else if(type==='return'){p.position={x:D.spots.front_door[1]-16,y:FLOOR_Y[0]};log(petText('return'));addMood('pet_return',{diary:false,words:false});autoSave();}
 else if(type==='lost'){log(petText('lost'));autoSave();}
 else if(type.startsWith('warning:')){log(petText(type.replace('warning:','warning_')));}
}
function tickPets(from,to){if(!(to>from)||friendHousePreview||visitSleepPreview)return;const p=petState.pet;if(!p)return;
 tickPetActivities(from,to);
 const point=petPoint(),near=petNearby(),atFeeder=Math.hypot(point.x-119,point.y-FLOOR_Y[0])<4;
 PetRules.tick(petState,from,to,{nearby:near,atFeeder},petEvent);
 if(p.status!=='home')return;
 p.animTime=(p.animTime||0)+(to-from);
 if(p.walk||p.carried){/* Walking/carrying owns the actor, needs still advance above. */}
 else if(p.motion){const m=p.motion,old=petPoint();m.s=Math.min(routeLength(m.route),m.s+(to-from)*(p.activity==='active'?8:5));const now=petPoint();p.direction=Math.abs(now.y-old.y)>.01?(now.y<old.y?'back':'front'):now.x<old.x?'left':'right';
  if(m.s>=routeLength(m.route)){p.position={x:now.x,y:now.y};petStartAction(m.after,m.duration);if(p.interaction){p.needs.company=clamp(p.needs.company+(p.interaction.kind==='play'?30:18));sim.needs.social=clamp(sim.needs.social+4);sim.needs.fun=clamp(sim.needs.fun+3);log(petText(p.interaction.kind));speak(petText('hero_'+p.interaction.kind));addMood('pet_company',{diary:false,words:false});p.interaction=null;}}
 }else if(p.reservedUntil>to){/* Let a person approach without chasing a moving target. */}
 else if(p.needs.hunger<60&&petState.feeder>0&&p.activityNow!=='eat')petWalkTo(119,FLOOR_Y[0],'eat',30);
 else if(p.activityNow==='eat'&&(p.needs.hunger>=97||petState.feeder<=0))petStartAction('groom',8);
 else if(p.needs.energy<25&&!['sleep','rest'].includes(p.activityNow))petWalkTo(155,FLOOR_Y[0],'sleep',300);
 else if(p.activityNow==='sleep'&&p.needs.energy<90){p.actionUntil=to+10;}
 else if(!p.motion&&(!p.actionUntil||to>=p.actionUntil)){
  if(p.attachment==='clingy'&&near&&PetRules.random(petState)<.45){const h=here();petWalkTo(Math.max(20,Math.min(325,h.x-17)),h.y,'sit',25);}
  else if(p.attachment==='clingy'&&petIsHome()&&!['bath','toilet'].includes(sim.act)&&PetRules.random(petState)<.35){const h=here();petWalkTo(Math.max(20,Math.min(325,h.x-17)),h.y,'nuzzle',20);}
  else{const a=petBreed(p.breed).species==='cat'?['blink','sit','rest','sniff','look','groom','scratch','stretch','play','knead','pounce','roll']:['blink','sit','rest','sniff','look','groom','scratch','stretch','play','wag','pant','bark','shake'];if(PetRules.random(petState)<(p.activity==='active'?.5:.25)){const level=PetRules.random(petState)<.25?1:0;const xs=level?[30,85,125,260,300]:[28,90,112,155,255,300];petWalkTo(xs[Math.floor(PetRules.random(petState)*xs.length)],FLOOR_Y[level],'sniff',15);}else petStartAction(a[Math.floor(PetRules.random(petState)*a.length)],15+PetRules.random(petState)*35);}
 }
 if(to>=p.nextEvent){p.nextEvent=to+120+PetRules.random(petState)*150;if(petIsHome()){log(petText(p.activityNow==='sleep'?'sleep':p.needs.hunger<20?'hungry':p.needs.company<25?'lonely':petBreed(p.breed).species+'_daily'));if(near&&!asleep()&&PetRules.random(petState)<.5)speak(petText('hero_daily'));}}
}
function petClip(){const p=petState.pet;if(!p)return null;const id=p.activityNow||'idle',direction=p.direction||'right';return petClips.get(p.breed)?.get(id+':'+direction)||petClips.get(p.breed)?.get('idle:right');}
function petSpriteFrame(){const c=petClip(),p=petState.pet;return c?Math.floor((p?.animTime||0)*1000/c.ms)%c.frames:0;}
function drawPetKit(ctx){if(!petState.installed||!petIsHome())return;const mat=petMatImage(),feeder=petFurnitureImages.pet_feeder;if(mat)ctx.drawImage(mat,142,FLOOR_Y[0]-5);if(feeder)ctx.drawImage(feeder,91,FLOOR_Y[0]-21);if(petHover==='feeder'&&feeder)drawObjectHover(ctx,feeder,91,FLOOR_Y[0]-21);if(petHover==='mat'&&mat)drawObjectHover(ctx,mat,142,FLOOR_Y[0]-5);}
const petFrameCache=new Map();
function petFrameCanvas(){const p=petState.pet,c=petClip(),img=p&&petImages.get(p.breed);if(!c||!img)return null;const frame=petSpriteFrame(),key=p.breed+':'+c.row+':'+frame;let canvas=petFrameCache.get(key);if(!canvas){canvas=document.createElement('canvas');canvas.width=32;canvas.height=28;canvas.getContext('2d').drawImage(img,frame*32,c.row*28,32,28,0,0,32,28);petFrameCache.set(key,canvas);if(petFrameCache.size>96)petFrameCache.delete(petFrameCache.keys().next().value);}return canvas;}
function drawPetActor(ctx,held=false){if(!petCanSee()||!!petState.pet.carried!==held)return;const img=petFrameCanvas(),point=petPoint();if(!img)return;if(!held)drawPetToy(ctx);const x=Math.round(point.x-16),y=Math.round(point.y-25);ctx.drawImage(img,x,y);if(petHover==='pet')drawObjectHover(ctx,img,x,y);}
function petHit(x,y){if(!petIsHome()&&!petWalkActive())return null;const shapes=[];if(petCanSee()){const p=petPoint();shapes.push(['pet',petFrameCanvas(),Math.round(p.x-16),Math.round(p.y-25)]);}if(petState.installed&&petIsHome())shapes.push(['feeder',petFurnitureImages.pet_feeder,91,FLOOR_Y[0]-21],['mat',petMatImage(),142,FLOOR_Y[0]-5]);for(const [id,img,ox,oy]of shapes)if(img){if(!outlineCache.has(img))outlineCache.set(img,outlineShape(img));if(outlineCache.get(img).near.has(Math.floor(x-ox)+','+Math.floor(y-oy)))return id;}return null;}

const petImageLoads=new Map();
function ensurePetImage(id){if(petImages.has(id))return Promise.resolve(petImages.get(id));if(!petImageLoads.has(id))petImageLoads.set(id,loadImg(petBreed(id).image).then(img=>{petImages.set(id,img);return img;}));return petImageLoads.get(id);}
async function loadPets(){if(petState.pet)await ensurePetImage(petState.pet.breed);await Promise.all(Object.entries(D.pets.furniture).map(async([id,src])=>petFurnitureImages[id]=await loadImg(src)));}
function petSnapshot(){const data=JSON.parse(JSON.stringify(petState));if(data.pet){const p=petPoint();data.pet.position={x:p.x,y:p.y};data.pet.motion=null;data.pet.interaction=null;data.pet.reservedUntil=0;if(data.pet.walk)data.pet.walk={dest:data.pet.walk.dest,phase:data.pet.walk.phase,startedAt:data.pet.walk.startedAt,until:data.pet.walk.until};}return data;}
function restorePets(raw){petState=PetRules.restore(raw,D.pets.breeds);if(petState.pet){const p=petState.pet;if(p.position){p.position.x=Math.max(18,Math.min(324,p.position.x));p.position.y=FLOOR_Y[storeyOfY(p.position.y)];}p.actionUntil=0;ensurePetImage(p.breed);}closePetHud();closePetPanel();closePetMini();petHover=null;}
RINGS.computer.push(['pet_adopt','领养宠物']);RINGS.phone.splice(RINGS.phone.length-1,0,['pet_adopt','领养宠物']);
window.addEventListener('resize',fitPetPanel);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!petPanel.hidden){e.preventDefault();closePetPanel();}});

// Human-side pet actions use the normal walking/action scheduler, so urgent
// needs can interrupt them exactly like reading or TV. They never block a call.
for(const [id,label,dur] of [['pat','摸摸宠物',10],['play','陪宠物玩',20],['groom','给宠物梳毛',16],['train','和宠物练个小动作',15],['talk','跟宠物说说话',10],['feed','检查并添粮',8],['hold','抱起宠物',12],['treat','给宠物喂零食',8]]){
 ACTS['pet_'+id]={spot:'pet_interact',label,emote:'heart',dur,log:null};EFFECT['pet_'+id]={fun:.25,social:.25};
}
D.spots.pet_interact=[0,112];
function petChoiceScores(score){const p=petState.pet;if(!petCanSee()||p.activityNow==='sleep'||p.interaction||p.reservedUntil>sim.t||sim.t<(p.nextHero??0)||hour()<7||hour()>=22||remoteSocial||sim.talk||Object.values(sim.needs).some(n=>n<40))return;
 const hungry=p.needs.hunger<35&&petState.feeder<10;
 if(hungry)score.pet_feed=130;
 else{const id=['pet_pat','pet_play','pet_groom','pet_train','pet_talk'][Math.floor(PetRules.random(petState)*5)];score[id]=p.needs.company<50?90:sim.t>(p.nextHero??0)+60?62:32;}
}
function preparePetHumanAction(act){const p=petState.pet;if(!petCanSee()||p.activityNow==='sleep')return false;const point=petPoint();if(point.dy)return false;
 if(p.carried)dropCarriedPet();
 const feed=act==='pet_feed';D.spots.pet_interact=[feed?0:storeyOfY(point.y),feed?85:Math.max(21,Math.min(320,point.x+(point.x>160?-17:17)))];
 p.position={x:point.x,y:point.y};p.playUntil=0;p.toyUntil=0;petStartAction('look',40);p.reservedUntil=sim.t+80;p.interaction=null;return true;
}
function onPetHumanArrive(act){const p=petState.pet;if(!petCanSee())return;const kind=act.slice(4);
 if(kind==='hold'){p.carried=true;p.direction=(sim.facing||1)>0?'right':'left';p.motion=null;petStartAction('sit',12);p.needs.company=clamp(p.needs.company+12);gainPetAffinity(3,'hold');log(petText('hold'));speak(petText('hero_hold'));return;}
 if(kind==='treat'){servePetTreat(p.pendingTreat);delete p.pendingTreat;return;}p.nextHero=sim.t+75+PetRules.random(petState)*75;p.reservedUntil=sim.t+(ACTS[act]?.dur||15);
 if(kind==='feed'){petState.feeder=900;log(petText('refill'));petWalkTo(119,FLOOR_Y[0],'eat',30);speak(petText('hero_feed'));}
 else{if(kind==='play')startPetPlay();petStartAction(({pat:'nuzzle',play:petPlayAction(),groom:'sit',train:petBreed(p.breed).species==='dog'?'wag':'pounce',talk:'look'})[kind]||'happy',ACTS[act].dur);p.needs.company=clamp(p.needs.company+(kind==='play'?30:20));gainPetAffinity(kind==='play'?4:2,kind);log(petText(kind));speak(petText('hero_'+kind));addMood('pet_company',{diary:false,words:false});}
}
function tickGuestPet(g,c){const p=petState.pet;if(!petCanSee()||g.sleeping||asleep()||sim.mode==='down'||remoteSocial||sim.talk||['bath','toilet'].includes(sim.act)){g.petVisit=null;return;}
 const visit=g.petVisit;
 if(visit){if(sim.t>=visit.until||p.status!=='home'){g.petVisit=null;return;}const gp=homeGuestPoint(g);if(!visit.started&&Math.hypot(gp.x-visit.target.x,gp.y-visit.target.y)<2){
   visit.started=true;p.reservedUntil=visit.until;petStartAction(visit.action,25);p.needs.company=clamp(p.needs.company+22);gainPetAffinity(1,'guest');
   const pool=PET_TEXT.guestTalks.map(row=>row.map(t=>t.replaceAll('{宠物}',p.name))),row=nextGuestText(pool,g.usedPetTalks||(g.usedPetTalks=[]));
   g.talk={title:row[0],lines:row.slice(1),i:0,wait:.2,said:[]};log(`${contactName(c)}蹲到${p.name}旁边，陪小家伙玩了一会儿。`);g.next=realClock+25;
  }return;
 }
 g.petNext??=sim.t+12+PetRules.random(petState)*15;
 if(sim.t<g.petNext||g.talk||g.walkS<g.walkLength||p.motion||p.reservedUntil>sim.t||['sleep','eat'].includes(p.activityNow))return;
 const point=petPoint(),gp=homeGuestPoint(g);if(point.dy||roomAt(point)!==roomAt(gp)||['stairs','bath'].includes(roomAt(point)))return;
 g.petNext=sim.t+40+PetRules.random(petState)*40;g.petVisit={target:{x:Math.max(23,Math.min(318,point.x+(point.x>160?-18:18))),y:point.y},until:sim.t+40,action:PetRules.random(petState)<.5?'nuzzle':'play',started:false};
 p.position={x:point.x,y:point.y};p.playUntil=0;p.toyUntil=0;petStartAction('look',40);p.reservedUntil=sim.t+40;
}

// Small object popovers carry only the task at hand; personality is shown
// in the adoption list only. In daily life it is expressed by the actor.
const petMini=petNode('section',undefined,'pet-mini');petMini.id='petMini';petMini.hidden=true;petMini.setAttribute('role','dialog');document.getElementById('widget').append(petMini);
const petMatImage=()=>petFurnitureImages['pet_mat_'+petState.matColor]||petFurnitureImages.pet_mat;
function feederDescription(amount){return '看起来还剩'+(amount>600?'很多':amount>=400?'一些':amount>=100?'不多':amount>=10?'一点点':'两粒');}
function closePetMini(){petMini.hidden=true;}
function openPetMini(kind,label){closePetHud();closePetPanel();closeRing();petMini.dataset.kind=kind;petMini.setAttribute('aria-label',label);petMini.replaceChildren();petMini.hidden=false;return petMini;}
function openPetFeeder(){if(!petState.installed||!petIsHome())return;const panel=openPetMini('feeder','自动喂食机');panel.append(petNode('span',feederDescription(petState.feeder)),petButton('加满！',()=>{petState.feeder=900;log(petText('refill'));autoSave();fitPetMini();},'pet-refill'));fitPetMini();}
function openPetMatColors(){if(!petState.installed||!petIsHome())return;const panel=openPetMini('mat','睡垫颜色');panel.append(petNode('strong','睡垫颜色'));const colors=petNode('div',undefined,'pet-mat-colors');for(const color of D.pets.matColors){const b=petButton('',()=>{petState.matColor=color.id;for(const button of colors.children)button.setAttribute('aria-pressed',String(button.dataset.color===color.id));autoSave();render();});b.dataset.color=color.id;b.setAttribute('aria-label',color.name);b.setAttribute('aria-pressed',String(petState.matColor===color.id));const swatch=petNode('i');swatch.style.backgroundColor=color.color;swatch.setAttribute('aria-hidden','true');b.append(swatch,petNode('span',color.name));colors.append(b);}panel.append(colors);fitPetMini();}
function fitPetMini(){if(petMini.hidden)return;if(!petIsHome()){closePetMini();return;}if(petMini.dataset.kind==='feeder'){const label=petMini.querySelector('span'),text=feederDescription(petState.feeder);if(label.textContent!==text)label.textContent=text;}
 const mat=petMini.dataset.kind==='mat',x=mat?155:103,padding=4,w=view.offsetWidth;petMini.style.maxWidth=Math.max(0,w-padding*2)+'px';const pw=petMini.offsetWidth,ph=petMini.offsetHeight;
 petMini.style.left=view.offsetLeft+Math.max(padding,Math.min(w-pw-padding,x*scale-pw/2))+'px';petMini.style.top=view.offsetTop+Math.max(padding,Math.min(view.offsetHeight-ph-padding,(FLOOR_Y[0]-28)*scale-ph))+'px';
}
function openPetInteractions(){openPetHud();}
document.addEventListener('pointerdown',e=>{if(!petMini.hidden&&!petMini.contains(e.target))closePetMini();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closePetMini();});
