// Pet intimacy is a relationship value, separate from the three needs.
function gainPetAffinity(amount,kind){const p=petState.pet;if(!p)return;p.bondAt||={};if(sim.t-(p.bondAt[kind]??-Infinity)<10)return;p.bondAt[kind]=sim.t;p.affinity=clamp((p.affinity??30)+amount);}
function petWalkActive(){return !!(petState.pet?.walk?.phase==='active'&&['front','park','beach'].includes(sim.place)&&!atFriendHome());}
function dropCarriedPet(){const p=petState.pet;if(!p?.carried)return;const h=here();p.carried=false;p.position={x:Math.max(19,Math.min(W-19,h.x-17)),y:FLOOR_Y[storeyOfY(h.y)]};p.motion=null;if(petWalkActive())p.walk.position={x:Math.max(18,Math.min(W-18,h.x-18)),y:OUT[sim.place].feet};petStartAction('stretch',8);}
function beginPetWalk(place){const p=petState.pet;if(!petCanSee()||!['front','park','beach'].includes(place))return false;
 if(wiping||phoneHolds()||sim.mode==='down'||asleep()){petNotice('先忙完眼前的事，再带它出去吧');return false;}
 if(friendOutingState||friendVisit||homeGuestPresent()){petNotice('先安排好朋友这边，再单独带小家伙出去吧');return false;}
 if(weather.kind==='storm'){petNotice('外面雷雨太大，等天气好一点再出门吧');return false;}
 if(sim.needs.hunger<15||sim.needs.energy<15||p.needs.hunger<15||p.needs.energy<15){petNotice('先吃点东西、休息一下，再出门走走吧');return false;}
 closePetHud();dropCarriedPet();const origin={...petPoint()};p.motion=null;p.toyUntil=0;p.playUntil=0;p.walk={dest:place,phase:'departing',startedAt:sim.t,until:sim.t+90,position:origin};sim.outBack=sim.t+90;sim.outWhy='pet';
 log(petText('walk_start'));if(sim.place==='home'){sim.dest=place;command('go_out');}else throughDoor(place);autoSave();return true;
}
function onPetSceneChanged(to){const p=petState.pet;if(!p?.walk)return;
 if(to==='home'){p.walk=null;p.position={x:D.spots.front_door[1]-18,y:FLOOR_Y[0]};p.motion=null;p.carried=false;petStartAction('sniff',10);gainPetAffinity(5,'walk');log(petText('walk_home'));autoSave();return;}
 if(!['front','park','beach'].includes(to)){p.walk=null;p.carried=false;p.position={x:155,y:FLOOR_Y[0]};p.motion=null;petStartAction('rest',10);return;}
 p.walk.phase='active';p.walk.position={x:Math.max(18,Math.min(W-18,here().x-18)),y:OUT[to].feet};p.walk.nextTalk=sim.t+15;p.activityNow='walk';p.direction='right';p.motion=null;sim.outBack=p.walk.until;
}
function tickPetActivities(from,to){const p=petState.pet,dt=to-from;if(!p||p.status!=='home')return;
 if(p.carried){if((!petIsHome()&&!petWalkActive())||sim.mode==='down'||petIsHome()&&sim.mode==='act'&&!['pet_hold','tv','host'].includes(sim.act)||p.needs.hunger<25||p.needs.energy<15)dropCarriedPet();else{p.activityNow='sit';p.needs.company=clamp(p.needs.company+dt*.12);if(!p.walk)return;}}
 if(p.playUntil>to&&petIsHome()&&!p.carried&&p.playOrigin){const room=D.roomX[roomAt(p.playOrigin)];if(room){const target=p.playOrigin.x+Math.sin((to-p.playAt)*.7)*9;p.position={x:Math.max(room[1]+16,Math.min(room[2]-16,target)),y:p.playOrigin.y};p.direction=Math.cos((to-p.playAt)*.7)<0?'left':'right';}}
 const w=p.walk;if(!w)return;
 // Friend-home travel has its own transition, outside throughDoor's callback.
 if(w.phase==='active'&&!petWalkActive()){if(petIsHome())onPetSceneChanged('home');else{p.walk=null;p.carried=false;p.position={x:155,y:FLOOR_Y[0]};petStartAction('rest',20);}return;}
 if(w.phase==='departing'&&petIsHome()&&!headingOut()){p.walk=null;if(sim.outWhy==='pet'){sim.outWhy=null;sim.outBack=null;sim.dest=null;}petStartAction('rest',5);return;}   // sent elsewhere before the door
 if(w.phase==='departing'&&petIsHome()){
  const h=here(),goal={x:Math.max(18,Math.min(W-18,h.x-(sim.facing||1)*18)),y:FLOOR_Y[storeyOfY(h.y)]},pos=w.position||p.position||goal;
  if(!w.route||Math.hypot(goal.x-w.goal.x,goal.y-w.goal.y)>14){w.route=planRoute(pos.x,pos.y,goal.x,goal.y);w.s=0;w.goal=goal;}
  w.s=Math.min(routeLength(w.route),w.s+dt*16);const next=routePos(w.route,w.s);p.direction=next.dy?(next.dy<0?'back':'front'):next.x<pos.x?'left':'right';w.position=next;p.activityNow='walk';return;
 }
 if(!petWalkActive())return;
 const h=here(),foot=sim.place==='park'?parkLayout().feet:OUT[sim.place].feet,walk=sim.mode==='walk',goal={x:Math.max(18,Math.min(W-18,h.x-(sim.facing||1)*19)),y:foot};
 if(parkInsideToilet())goal.x=parkLayout().facility.x+20;
 const pos=w.position||goal;if(Math.abs(pos.x-goal.x)>W*.5){pos.x=goal.x;pos.y=goal.y;}
 const delta=goal.x-pos.x,motion=Math.min(Math.abs(delta),dt*(Math.abs(delta)>45?28:16));pos.x+=Math.sign(delta)*motion;pos.y=goal.y;w.position=pos;p.direction=delta<0?'left':'right';p.activityNow=motion>.05?'walk':p.outdoorUntil>to?p.outdoorAction:walk?'look':'sniff';p.needs.company=clamp(p.needs.company+dt*.1);if(p.carried){p.activityNow='sit';p.direction=(sim.facing||1)>0?'right':'left';}
 if(sim.t>=(w.nextTalk??Infinity)&&!asleep()){w.nextTalk=sim.t+20+PetRules.random(petState)*20;log(petText('walk_'+sim.place));if(Math.random()<.5)speak(petText('hero_walk'));gainPetAffinity(1,'walk_time');}
 if(sim.t>=w.until||p.needs.hunger<12||p.needs.energy<12||weather.kind==='storm'){if(sim.act!=='go_home'&&!sim.windup){closePetHud();command('go_home');}}
}
function drawPetOutside(ctx,layer){if(!petWalkActive()||layer!=='front')return;drawPetActor(ctx,!!petState.pet.carried);}
function petOutdoorInteraction(kind){const p=petState.pet;if(!petWalkActive())return;pauseForPet();if(kind==='hold'){if(p.carried)dropCarriedPet();else{p.carried=true;p.direction=(sim.facing||1)>0?'right':'left';p.activityNow='sit';log(petText('hold'));gainPetAffinity(3,'hold');}return;}if(kind==='play')startPetPlay();else{p.playUntil=0;p.toyUntil=0;}p.outdoorAction=kind==='play'?petPlayAction():kind==='groom'?'groom':kind==='hold'?'nuzzle':'happy';p.outdoorUntil=sim.t+12;p.needs.company=clamp(p.needs.company+12);gainPetAffinity(2,kind);log(petText(kind==='hold'?'hold':kind));speak(petText('hero_'+kind));}
const PET_TREATS=[{id:'biscuit',name:'宠物饼干',fill:12},{id:'sausage',name:'火腿肠',fill:18},{id:'fish',name:'小鱼干',fill:10}];
function offerPetTreat(id){const p=petState.pet,food=PET_TREATS.find(t=>t.id===id);if(!petCanSee()||!food)return;if(sim.t-(p.lastTreat??-Infinity)<15){petNotice('刚吃过零食啦，等一会儿再喂吧');return;}if(['bath','toilet','sleep'].includes(sim.act)||sim.mode==='down'){petNotice('先让小人忙完，再喂零食吧');return;}
 closePetHud();if(petWalkActive()){servePetTreat(id);return;}p.pendingTreat=id;command('pet_treat');
}
function servePetTreat(id){if(petWalkActive())pauseForPet();const p=petState.pet,food=PET_TREATS.find(t=>t.id===id);if(!p||!food)return;p.lastTreat=sim.t;p.playUntil=0;p.toyUntil=0;p.needs.hunger=clamp(p.needs.hunger+food.fill);p.needs.company=clamp(p.needs.company+8);gainPetAffinity(3,'treat');petStartAction('eat',8);p.outdoorAction='eat';p.outdoorUntil=sim.t+8;p.reservedUntil=sim.t+8;log(petText('treat_'+food.id));speak(petText('hero_treat'));autoSave();}
function restorePetActivityLocation(){const p=petState.pet;if(!p)return;if(p.carried&&!petIsHome()&&!petWalkActive())p.carried=false;if(!p.walk)return;if(p.walk.phase==='departing'&&petIsHome()){const dest=p.walk.dest;p.walk=null;beginPetWalk(dest);}else if(['front','park','beach'].includes(sim.place)){p.walk.phase='active';p.walk.position={x:Math.max(18,here().x-18),y:sim.place==='park'?parkLayout().feet:OUT[sim.place].feet};sim.outBack=p.walk.until;}else p.walk=null;}

function petPlayAction(){const species=petBreed(petState.pet.breed).species,list=species==='cat'?['play','pounce','roll']:['play','run','wag'];return list[Math.floor(PetRules.random(petState)*list.length)];}
function startPetPlay(){const p=petState.pet;p.playOrigin={...petPoint()};p.playAt=sim.t;p.playUntil=sim.t+20;p.toyUntil=p.playUntil;}
function drawPetToy(ctx){const p=petState.pet,ball=petFurnitureImages.pet_toy;if(!p||!ball||p.carried||!(p.toyUntil>sim.t))return;const point=petPoint(),phase=p.animTime||0,sign=p.direction==='left'?-1:1;const x=Math.max(4,Math.min(W-10,point.x+sign*(13+Math.sin(phase*2)*4))),y=point.y-5-Math.abs(Math.sin(phase*3))*4;ctx.drawImage(ball,Math.round(x),Math.round(y));}

function pauseForPet(){if(!petWalkActive())return;stopNpcTalk('陪小家伙玩一会儿');const h=here();sim.route=[[h.x,sim.place==='park'?parkLayout().feet:OUT[sim.place].feet]];sim.s=sim.target=0;sim.mode='idle';sim.act=null;sim.windup=null;sim.idleUntil=sim.t+12;}

function petNotice(text){closePetHud();showHint(text);}
