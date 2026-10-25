// Dining and cinema stay in the mall, sharing needs, cards, menus and saves.
const MALL_RESTAURANTS=Object.fromEntries(MALL_LIFE.restaurants.map(r=>[r.id,r]));
const MALL_FILMS=Object.fromEntries(MALL_LIFE.films.map(f=>[f.id,f]));
const mallVisitInside=()=>sim.place==='mall'&&mallS.visit?.phase==='inside';
const mallSleeping=()=>mallVisitInside()&&mallS.visit.kind==='cinema'&&mallS.visit.sleeping&&sim.mode!=='down';
const mallDishList=()=>T.cuisines.flatMap(c=>c.dishes.filter(d=>typeof d==='object').map(d=>({c,d})));
const mallDish=()=>mallDishList().find(({d})=>d.name===mallS.visit?.dish)?.d;
const mallFilm=()=>MALL_FILMS[mallS.visit?.film];
for(const f of MALL_LIFE.films) ML['mall_film_'+f.id]={name:'余味·'+f.name,emo:f.emo,pts:2,min:210};
ML.mall_dinner={name:'商场里的一顿热饭',emo:'happy',pts:2,min:150};
ML.mall_nap={name:'在电影里充了个电',emo:'energized',pts:2,min:120};
for(const [kind,events] of Object.entries(MALL_LIFE.events))events.forEach((e,i)=>ML[`mall_${kind}_event_${i}`]={name:e[3],emo:e[2],pts:1,min:90});
PICK.mall_food={title:'商场餐厅 · 坐下来吃点什么',groups:()=>PICK.cook.groups()};
PICK.mall_film={title:'电影院 · 今天看哪部电影',groups:()=>[...new Set(MALL_LIFE.films.map(f=>f.genre))].map(name=>({name,
  items:MALL_LIFE.films.filter(f=>f.genre===name).map(f=>({title:f.name,line:f.beats[0],info:`${f.duration}分钟`,icon:D.mallPosters[f.id],item:{id:f.id}}))}))};
function mallClearInteraction(){
  stopNpcTalk('先完成眼前的事');
  closeRing();closePicker();hoverId=null;hoverBuddy=false;glow=null;walkMark=null;
  sim.windup=null;sim.queue=[];sim.chosen=null;sim.talk=null;life.talkQ=null;reaction=null;
  mallS.stop=null;mallS.goal=null;mallS.hover=null;mallS.pointer=null;clearNpcPills();
}
function mallChoose(kind,it){
  if(mallS.toilet||sim.mode==='down'||wiping||cardHolds())return;
  mallS.menuShop=it.id;mallS.stop=null;mallS.goal=null;
  sim.mode='act';sim.act='mall';sim.actEnd=Infinity;
  openPicker(kind==='cinema'?'mall_film':'mall_food',{x:itemX(it),y:65});
}
function mallPlanVisit(kind,item=null,auto=false){
  if(sim.place!=='mall'||sim.mode==='down'||wiping||cardHolds())return;
  if(mallS.toilet){showHint('先用完卫生间，再继续吧。');return;}
  let chosen=kind==='cinema'?MALL_FILMS[item?.id]:mallDishList().find(({d})=>d.name===item?.dish?.name)?.d;
  if(!chosen)chosen=kind==='cinema'?pick(MALL_LIFE.films):pick(mallDishList().filter(({d})=>sim.needs.hunger<35?d.fill>=45:true))?.d;
  if(!chosen)return;
  let it=mallItems().find(it=>it.id===mallS.menuShop&&(kind==='cinema'?it.id==='cinema':!!MALL_RESTAURANTS[it.id]));
  if(auto||!it){
    const dir=mallS.dir===1?1:-1,budget=mallServiceBudget(sim.needs.hunger),ahead=it=>mod((it.stop-mallS.x)*dir,MALL.nearW);
    it=mallItems().filter(it=>kind==='cinema'?it.id==='cinema':MALL_RESTAURANTS[it.id]&&ahead(it)<=budget).sort((a,b)=>ahead(a)-ahead(b))[0];
    if(!it&&kind==='restaurant'){
      const target=mallS.x+dir*budget;
      it=mallS.foodFront={id:pick(MALL_LIFE.restaurants).id,name:'餐厅',kind:'shop',dynamic:true,food:true,
        u:target-74+5,w:91,top:MALL.restroom.top,stop:target,born:realClock};
      log('循着饭菜香，在前方看见了'+MALL_RESTAURANTS[it.id].name+'。');
    }
  }
  if(!it)return;
  if(mallVisitInside()){mallLeaveVisit(false,false);}
  const dir=mallS.dir;mallClearInteraction();
  mallS.visit={kind,phase:'search',shop:it.id,dynamic:!!it.dynamic,dish:kind==='restaurant'?chosen.name:null,
    film:kind==='cinema'?chosen.id:null,elapsed:0,served:0,sleeping:false,napped:false,nextEvent:8,nextCard:4,beat:-1,resumeDir:dir};
  mallS.goal={x:mallS.x+(itemX(it)-MALL.at),it};sim.mode='act';sim.act='mall';sim.actEnd=Infinity;
  log(kind==='restaurant'?`${auto?'肚子饿了，先在商场找餐厅':'选好菜品'}，去${MALL_RESTAURANTS[it.id].name}吃${chosen.name}。`:`选了《${chosen.name}》，朝电影院走去。`);
  speak(kind==='restaurant'?pick(["先找家餐厅吃点吧。",'点一份'+chosen.name+'，慢慢吃。',"饿了，去餐厅吃点东西。"]):'今天就看《'+chosen.name+'》，把手机调成静音。',true);
}
function mallRoomSetup(){
  clearNpcPills();life.npcs=[];
  if(mallS.visit.kind==='restaurant'){
    const guest=MALL.dining.guest;
    life.npcs.push(makeNpc('clerk',{x:245,feet:64,layer:'back'}));life.npcs.push(makeNpc('guest',{x:guest.x,feet:guest.feet,seatLift:guest.lift,sit:true,layer:'back'}));
  }else for(const x of [113,253])life.npcs.push(makeNpc('guest',{x,feet:106,sit:true,back:true,layer:'back'}));
}
function mallSetSeat(){
  const seat=MALL.dining.seat;
  sim.route=[mallS.visit.kind==='cinema'?[197,110]:[seat.x,seat.feet]];sim.s=0;sim.target=0;
  sim.mode='act';sim.act='mall';sim.actEnd=Infinity;
}
function mallEnterVisit(){
  const st=mallS.visit;if(!st)return;
  mallClearInteraction();
  wipe(()=>{
    if(sim.place!=='mall'||mallS.visit!==st)return;
    gameAudio.sound('real-auto-door-cc0',.15);
    st.phase='inside';st.startHunger=sim.needs.hunger;mallSetSeat();mallRoomSetup();
    log(st.kind==='restaurant'?`走进${MALL_RESTAURANTS[st.shop].name}，在软椅上坐好，热腾腾的${st.dish}端上了桌。`:`检票后走进放映厅，在红色软椅上坐好，大银幕开始放映《${mallFilm().name}》。`);
    mallVisitTalk();
  });
}
function mallVisitVars(){return {食物:mallDish()?.name||'热饭',电影:mallFilm()?.name||'电影'};}
function mallVisitTalk(){
  const st=mallS.visit;if(!st||st.sleeping||friendOutingActive())return;
  const pool=MALL_LIFE[st.kind==='restaurant'?'restaurantTalks':'cinemaTalks'];
  const key='mallTalk_'+st.kind,seen=(lifeFlags[key]||=[]);let fresh=pool.map((_,i)=>i).filter(i=>!seen.includes(i));
  if(!fresh.length){seen.splice(0,seen.length);fresh=pool.map((_,i)=>i);}
  const i=pick(fresh);seen.push(i);const lines=pool[i].map(s=>fill(s,mallVisitVars()));
  const n=life.npcs[0];if(n)npcSay(n,(st.kind==='restaurant'?'服务员：':'邻座：')+lines[0]);
  speak(lines[1],true);sim.needs.social=clamp(sim.needs.social+2);
  log(`在${st.kind==='restaurant'?'餐桌边':'放映厅里'}小声聊了两句：${lines[0]}`);
}
function mallVisitEvent(){
  const st=mallS.visit;if(!st||st.sleeping||friendOutingActive())return;
  const pool=MALL_LIFE.events[st.kind],seen=(st.events||=[]);let fresh=pool.map((_,i)=>i).filter(i=>!seen.includes(i));
  if(!fresh.length){seen.length=0;fresh=pool.map((_,i)=>i);}
  const i=pick(fresh),e=pool[i];seen.push(i);log(fill(e[0],mallVisitVars()));speak(e[1],true);
  addMood(`mall_${st.kind}_event_${i}`,{words:false});
  for(const [k,v]of Object.entries(e[4]))sim.needs[k]=clamp(sim.needs[k]+v);
}
function mallLeaveVisit(completed=false,transition=true){
  const st=mallS.visit;if(!st)return;
  if(st.kind==='cinema'){
    sim.needs.fun=100;
    if(completed){addMood('mall_film_'+st.film,{words:false});speak(mallFilm().reaction,true);}
    log(`从《${mallFilm().name}》的放映厅出来，${st.napped?'还在座位上补了一觉，':'心里装着银幕上的故事，'}娱乐值满满。`);
  }else if(completed){
    const d=mallDish();addMood('mall_dinner',{words:false});
    if(d?.moods?.length){const mood=weighted(d.moods);if(ML[mood])addMood(mood,{words:false});}
    for(const[k,v]of Object.entries(d?.plus||{}))if(k in sim.needs)sim.needs[k]=clamp(sim.needs[k]+v);
    log(`坐着吃完了${st.dish}，向服务员道谢，带着饱足回到商场走廊。`);speak('吃得好舒服，接下来可以慢慢逛了。',true);
  }else log('暂时离开餐桌，先照顾更着急的需要。');
  const exit=()=>{mallClearInteraction();mallS.visit=null;mallS.dir=st.resumeDir===1?1:-1;
    sim.route=[[MALL.at,MALL.feet]];sim.s=0;sim.target=0;sim.mode='act';sim.act='mall';sim.actEnd=Infinity;sim.player=false;npcSetup('mall');};
  if(transition)wipe(exit);else exit();
}
function mallTickVisit(dtGame,dtReal){
  const st=mallS.visit;if(!st)return false;
  if(st.phase==='search'){mallStep(dtReal);return true;}
  st.elapsed+=dtGame;
  if(st.kind==='restaurant'){
    const d=mallDish(),duration=12,fillAmount=Math.max(d.fill,95-st.startHunger);
    const gain=fillAmount/duration*dtGame;sim.needs.hunger=clamp(sim.needs.hunger+gain);st.served+=gain;
    if(st.elapsed>=duration){mallLeaveVisit(true);return true;}
  }else{
    if(sim.needs.energy<20&&!st.sleeping){
      st.sleeping=true;st.napped=true;log(`《${mallFilm().name}》的配乐像摇篮曲，逛街的疲惫涌上来，在影院软椅上睡着了。`);
      speak(pick(['眼皮撑不住了……就在这儿眯一会儿。','椅子好舒服，借着配乐睡一下。','电影还在放，我先充一小会儿电。']),true);
    }
    if(st.sleeping){
      sim.needs.energy=clamp(sim.needs.energy+1.8*dtGame);
      if(sim.needs.energy>=85){st.sleeping=false;addMood('mall_nap',{words:false});log('在放映厅里睡得很踏实，睁开眼时体力恢复了，继续坐着看电影。');speak('刚才补了一觉，好像重新充满电了。',true);}
    }
    const beat=Math.min(2,Math.floor(st.elapsed/mallFilm().duration*3));
    if(beat!==st.beat){st.beat=beat;if(!st.sleeping)log(`《${mallFilm().name}》：${mallFilm().beats[beat]}`);}
    if(st.elapsed>=mallFilm().duration&&!st.sleeping){mallLeaveVisit(true);return true;}
  }
  if(!st.sleeping&&st.elapsed>=st.nextEvent){st.nextEvent=st.elapsed+12+Math.random()*9;mallVisitEvent();if(Math.random()<.5)mallVisitTalk();}
  if(!st.sleeping&&st.elapsed>=st.nextCard){st.nextCard=st.elapsed+25;rollCard(lifeCtx(),st.kind);}
  return true;
}
function mallInteriorHit(x,y){
  if(x>=307&&x<=334&&y>=14&&y<=78)return 'mall_exit';
  if(mallS.visit.kind==='restaurant'&&x>=141&&x<=201&&y>=72&&y<=111)return 'mall_menu';
  return null;
}
function mallInteriorClick(id){
  if(wiping||cardHolds()||sim.mode==='down')return;
  if(id==='mall_exit')mallLeaveVisit(false);
  if(id==='mall_menu'){mallS.menuShop=mallS.visit.shop;openPicker('mall_food',{x:173,y:87});}
}
function mallDoing(){const st=mallS.visit;return st.phase==='search'?(st.kind==='restaurant'?'寻找餐厅':'走向电影院'):st.kind==='restaurant'?'坐着享用'+st.dish:st.sleeping?'在影院座位上睡觉':'观看《'+mallFilm().name+'》';}
function mallRoomFrame(ms){return {f:{expr:mallSleeping()?'sleepy':Math.floor(ms/2200)%3===0?'happy':'neutral',look:0,bob:0,sway:0,wave:null},pose:'sit',back:mallS.visit.kind==='cinema',emote:mallSleeping()?'zzz':null};}
function renderMallRoom(){
  const st=mallS.visit,room=st.kind==='cinema'?'cinema':st.shop,O=IMG.out.mall.rooms[room];
  bctx.clearRect(0,0,W,H);bctx.drawImage(O.bg,0,0);
  if(st.kind==='cinema'){
    const beat=Math.min(2,Math.floor(st.elapsed/mallFilm().duration*3));bctx.drawImage(IMG.out.mall.films[st.film][beat],79,11);
    // A slow light spill, no strobe; screen, aisle and seats keep their own planes.
    bctx.save();bctx.fillStyle='rgba(166,197,231,.06)';bctx.beginPath();bctx.moveTo(79,63);bctx.lineTo(263,63);bctx.lineTo(296,112);bctx.lineTo(45,112);bctx.fill();bctx.restore();
  }
  drawNpcs(bctx,'back');
  const fr=mallRoomFrame(realClock*1000);drawOutBuddy(bctx,fr);
  if(st.kind==='restaurant'){
    bctx.drawImage(O.front,0,0);const pic=dishPic(dishIcon(mallDish()));
    const table=MALL.dining.table;
    if(pic?.complete)bctx.drawImage(pic,table.x+9-Math.floor(pic.width/2),table.y+3-pic.height);
    if(friendOutingActive()&&pic?.complete)bctx.drawImage(pic,table.x-12-Math.floor(pic.width/2),table.y+3-pic.height);
    if(!reduceMotionUI){bctx.fillStyle='rgba(247,246,251,.6)';for(const x of [table.x+6,table.x+12])bctx.fillRect(x,table.y-14-Math.floor(realClock*2+x)%4,1,2);}
  }else bctx.drawImage(O.front,0,0);
  drawObjectHover(bctx,O.hover[hoverId]);
  finishOut(fr,[here().x+4,here().y-44]);
}
function restoreMallVisit(raw){
  const st=raw.visit;if(!st||!['restaurant','cinema'].includes(st.kind)||!['search','inside'].includes(st.phase))return;
  if(st.kind==='restaurant'&&(!MALL_RESTAURANTS[st.shop]||!mallDishList().some(({d})=>d.name===st.dish)))return;
  if(st.kind==='cinema'&&!MALL_FILMS[st.film])return;
  mallS.visit={kind:st.kind,phase:st.phase,shop:st.shop,dynamic:!!st.dynamic,dish:st.dish,film:st.film,
    elapsed:Math.max(0,Math.min(1000,Number(st.elapsed)||0)),served:Math.max(0,Number(st.served)||0),startHunger:clamp(Number(st.startHunger)||0),
    sleeping:!!st.sleeping,napped:!!st.napped,nextEvent:Math.max(0,Number(st.nextEvent)||8),nextCard:Math.max(0,Number(st.nextCard)||12),beat:Number(st.beat)||0,resumeDir:st.resumeDir===1?1:-1};
  sim.mode='act';sim.act='mall';sim.actEnd=Infinity;sim.windup=null;
  if(st.phase==='inside'){mallSetSeat();mallRoomSetup();}
  else{const it=st.dynamic?mallS.foodFront:MALL.items.find(it=>it.id===st.shop);if(it)mallS.goal={x:mallS.x+(itemX(it)-MALL.at),it};else mallS.visit=null;}
}
