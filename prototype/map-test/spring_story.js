// Spring farm story + first farming loop. Test page only (make_season_game_test.py);
// never in make_demo.py or the release builds.
// Story (owner, 2026-11-02): on 写信日 妈妈 writes: they leased a little farm and the
// ticket is paid. The letter opens the 茵菲谷 flight (free). First landing: 妈妈 waits
// at the farmhouse, shows the room (or not: the player picks), then the two front beds,
// a pack of carrot seeds, sow + water together; then she goes to find 爸爸 in town.
// After that the beds work all year: seeds cost 丢丢币, a watered day grows a crop one
// day, harvest sells it. Numbers: DIDI_CURRENCY.md. Dialogue lives in the game's own
// rows (story_bubbles.js): 妈妈 in the upper 对方 row, Buddy in her own bubble.
const springFarm=(()=>{
 const T=seasonMapTest,C=()=>T.state.spring,D=SPRING_FARM_DATA;
 const CROP={carrot:{name:'胡萝卜',cost:1,days:2,sell:2,icon:'carrot'},cabbage:{name:'白菜',cost:2,days:4,sell:4,icon:'cabbage'},corn:{name:'玉米',cost:2,days:6,sell:5,icon:'corn'},pumpkin:{name:'南瓜',cost:3,days:8,sell:7,icon:'pumpkin'}};
 const START=[9,10],MORE=[[11,14,6],[12,35,10]];   // front-row beds; [bed, working days, cost] to clear more
 const STAGE=['种子','发芽','长大','成熟'];
 const blank=()=>({letter:0,unlocked:false,phase:'none',coins:8,beds:{},open:[...START],ledger:[],day:-1,work:0,workDay:-1,firstHarvest:false});
 let F=blank();
 const inSpring=()=>sim.place==='spring_test',today=()=>Math.floor(sim.t/1440);
 const hero=()=>nameOf(),coins=v=>(Math.round(v*10)/10).toString();
 const clock=t=>`第 ${Math.floor(t/1440)+1} 天 ${String(Math.floor(t%1440/60)).padStart(2,'0')}:${String(Math.floor(t%60)).padStart(2,'0')}`;
 // ---------------------------------------------------------------- 妈妈 on the map
 const momContact=()=>socialState.contacts.find(c=>c.id==='mom');
 const mom={on:false,scene:3,inside:false,x:200,y:103,tx:null,facing:-1,done:null,t:0,n:null};
 function momNpc(){const c=momContact(),lk=c?.look||doll.PRESETS.f;if(!mom.n||mom.n.look!==lk)mom.n={look:lk,ramps:doll.rampsOf(lk),cache:new Map()};return mom.n;}
 function momTick(t){const dt=Math.max(0,Math.min(.1,t-mom.t));mom.t=t;if(mom.tx==null)return;const d=mom.tx-mom.x,st=dt*WALK*1.2;
  if(Math.abs(d)<=st){mom.x=mom.tx;mom.tx=null;const f=mom.done;mom.done=null;f?.();}else{mom.x+=Math.sign(d)*st;mom.facing=Math.sign(d);}}
 function drawMom(ctx,info){
  if(!mom.on||(mom.inside?!info.inside:(info.inside||mom.scene!==info.region)))return;
  const walking=mom.tx!=null,ph=Math.floor(info.time*7)%4,f={expr:'happy',look:mom.facing,bob:walking?ph%2:0,sway:walking?ph%2:0,wave:null};
  ctx.drawImage(npcCanvas(momNpc(),f,walking?(ph===1?'walkL':ph===3?'walkR':'stand'):'stand'),Math.round(mom.x)-10,Math.round(mom.y)-27);
 }
 const momTo=x=>new Promise(res=>{mom.tx=x;mom.done=res;});
 // ---------------------------------------------------------------- beds
 const bedOf=i=>F.beds[i]||null,total=b=>CROP[b.crop].days;
 const ripe=b=>b&&b.progress>=total(b);
 const stageOf=b=>ripe(b)?3:b.progress===0?0:b.progress/total(b)<.5?1:2;
 function roll(){const d=today();if(F.day<0)F.day=d;while(F.day<d){for(const b of Object.values(F.beds))if(b.watered===F.day&&!ripe(b))b.progress++;F.day++;}}
 function worked(){if(F.workDay!==today()){F.workDay=today();F.work++;}}
 function drawBeds(ctx,info){
  if(info.inside||info.region!==4)return;roll();
  const soil=D.soil;
  for(const i of F.open){const b=bedOf(i),[x,top,w,h]=D.plots[i];
   if(b&&b.watered===today()){ctx.fillStyle=soil[1];ctx.fillRect(x,top,w,h);for(let yy=top;yy<top+h;yy+=3){ctx.fillStyle=soil[2];ctx.fillRect(x,yy,w,1);if(yy+2<top+h){ctx.fillStyle=soil[0];ctx.fillRect(x,yy+2,w,1);}}}   // wet soil: the bed's furrows one shade darker
   if(b){const pic=imgOf(D.crops[b.crop][stageOf(b)]);for(const [cx,base]of D.slots[i])ctx.drawImage(pic,cx-8,base-19);}
  }
  if(['sow','water'].includes(F.phase)){const [x,top,w]=D.plots[START[0]],bob=Math.round(Math.sin(info.time*4)*1.5),ax=x+w/2,ay=top-14+bob;   // a pixel arrow over the first bed
   ctx.fillStyle='#22182a';for(let i=0;i<5;i++)ctx.fillRect(ax-5+i,ay+i,11-i*2,1);ctx.fillStyle='#f6d36b';for(let i=0;i<4;i++)ctx.fillRect(ax-4+i,ay+i,9-i*2,1);}
 }
 const pics=new Map();function imgOf(src){let i=pics.get(src);if(!i){i=new Image();i.src=src;pics.set(src,i);}return i;}
 Object.values(D.crops).flat().forEach(imgOf);
 // ---------------------------------------------------------------- drawing hook (scene coords, camera applied)
 const oldPeople=T.people.draw;C().setPeopleRenderer((ctx,info)=>{if(info.region>=0)oldPeople(ctx,info);drawBeds(ctx,info);momTick(C().state.time);drawMom(ctx,info);});
 // ---------------------------------------------------------------- story
 const speech=createStorySpeech({view,onClose:()=>speech.hide()});
 const oldHolds=cardHolds;cardHolds=()=>oldHolds()||speech.open;
 let lines=0;
 const say=(who,words)=>new Promise(res=>(lines++,speech.show(who,words,{special:true,advance:res})));
 const ask=(who,words,opts)=>new Promise(res=>(lines++,speech.show(who,words,{special:true,choices:opts.map((label,i)=>({label,on:()=>res(i)}))})));
 const walk=(x,y=103)=>new Promise(res=>{speech.hide();C().target(x,y,res);});
 const until=f=>new Promise(res=>{const t=setInterval(()=>{if(f()){clearInterval(t);res();}},80);});
 const quiet=()=>T.state.autoAt=sim.t+1e9;   // no wandering off while 妈妈 is showing her round
 async function arrive(){
  F.phase='arrive';quiet();const c=C();c.go(3,96);Object.assign(mom,{on:true,scene:3,inside:false,x:205,y:103,tx:null,facing:-1});
  await walk(170);
  await say('妈妈','来啦！路上累不累？');
  await say(hero(),'还行，飞机上睡了一觉。爸呢？');
  await say('妈妈','去镇上买化肥了，晚饭前回来。');
  const room=await ask('妈妈','先进屋看看你的房间，还是先去地里转转？',['先看房间','去地里看看']);
  if(room===0)await showRoom();else await say('妈妈','行，先干活后歇着，像我闺女。');
  await toField();
 }
 async function showRoom(){
  F.phase='room';speech.hide();mom.tx=null;
  await Promise.all([momTo(182),walk(182)]);
  C().enter();await until(()=>C().state.inside&&!C().state.door);
  Object.assign(mom,{inside:true,x:92,y:108,facing:1});
  await walk(122,50);
  await say('妈妈','楼上左边那间是你的，被子昨天刚晒过。');
  await say(hero(),'嗯……一股太阳味儿。');
  await say('妈妈','右边是我跟你爸的屋，中间那间洗澡。');
  await say('妈妈','饿了灶上有饭，自己热。走，带你去地里。');
  speech.hide();C().leave();await until(()=>!C().state.inside&&!C().state.door);
  Object.assign(mom,{inside:false,scene:3,x:196,y:103});
 }
 async function toField(){
  F.phase='field';speech.hide();quiet();
  mom.scene=4;mom.x=150;mom.facing=-1;mom.tx=null;   // she takes the short cut along the beds
  C().travel(1);
  await until(()=>C().state.scene===4&&!C().state.target);
  await walk(110);mom.facing=-1;
  await say('妈妈','前面这两块是你的。');
  await say('妈妈','后头那几块还荒着，以后慢慢收拾。');
  await say('妈妈','先种胡萝卜吧，浇两天水就能拔。');
  await say('妈妈','种子我给你带了一包，喏。');
  await say(hero(),'行，我试试。');
  speech.hide();F.phase='sow';showHint('点一下有箭头的菜地，选「播种」');
 }
 async function afterSow(){
  F.phase='water';await say('妈妈','种下了？还得浇水，不浇不长。');speech.hide();showHint('再点一下菜地，选「浇水」');
 }
 async function afterWater(){
  F.phase='talk';
  await say('妈妈','就这样。每天浇一回，熟了就收，收了就能卖。');
  await say(hero(),'卖的钱归我？');
  await say('妈妈','归你，记在你的丢丢币上。');
  await say('妈妈','种子钱也从那儿出，自己算着花。');
  await say(hero(),'那我先赚它两个币。');
  await say('妈妈','口气不小。我去镇上找你爸，晚上见！');
  speech.hide();F.phase='done';momTo(400).then(()=>mom.on=false);
  log('到了茵菲谷爸妈的农庄，在前头那块地里种下了第一垄胡萝卜。');
  T.state.autoAt=sim.t+60;setTimeout(()=>showHint(`点一下${nameOf()}，可以打开丢丢平板电脑看账`),900);
 }
 // ---------------------------------------------------------------- letter + flight
 const LETTER=['我和你爸在茵菲谷承包了一小片农庄，地方不大，有菜地、果园，还有几只鸡。','春天正是播种的时候，想请你来帮帮忙。机场有去农庄的航班，票我们买好了。','你的房间收拾好了，被子也晒过了。等你来！'];
 function sendLetter(){if(F.letter)return false;F.letter=1;const m=mailState();m.box.push({from:'mom',title:'妈妈寄来一封信',lines:[...LETTER],springFarm:true});return true;}
 const oldMail=mailTick;mailTick=function(){if(!F.letter&&festName()==='写信日'&&sim.t%1440>=9*60&&!asleep())sendLetter();return oldMail();};
 const oldRead=readMail;readMail=function(){const l=lifeFlags.mail?.box?.[0],r=oldRead();if(l?.springFarm&&!F.unlocked){F.unlocked=true;setTimeout(()=>showHint('机场的「茵菲谷」航班开通了'),1200);}return r;};
 const oldOpen=openRing;openRing=function(which,at){
  if(which==='away'&&inSpring()&&F.phase==='done'){const keep=RINGS.away;RINGS.away=[keep[0],['sf:pc','丢丢平板电脑'],...keep.slice(1)];try{return oldOpen(which,at);}finally{RINGS.away=keep;}}
  const r=oldOpen(which,at);
  if(which==='airportFlights'){const b=ringEl.querySelector('button');if(b){b.textContent=F.unlocked?'茵菲谷 · 免费':'茵菲谷';if(!F.unlocked){b.classList.add('sf-wait');b.title='等家里的消息';b.append(Object.assign(document.createElement('small'),{className:'fu-why',textContent:'等家里的消息'}));}}}
  return r;
 };
 // ---------------------------------------------------------------- arrival
 const oldArrive=arriveAt;arriveAt=function(place){const r=oldArrive(place);
  if(place==='spring_test'&&F.unlocked&&F.phase!=='done'){
   if(['sow','water','talk'].includes(F.phase)){C().go(4,90);Object.assign(mom,{on:true,scene:4,inside:false,x:150,y:103,tx:null,facing:-1});quiet();if(F.phase==='talk')afterWater();else showHint(F.phase==='sow'?'点一下有箭头的菜地，选「播种」':'再点一下菜地，选「浇水」');}
   else setTimeout(arrive,700);
  }else mom.on=false;
  return r;};
 // ---------------------------------------------------------------- clicking the beds
 function bedAt(x,y){return F.open.concat(MORE.map(m=>m[0])).find(i=>{const [bx,top,w,h]=D.plots[i];return x>=bx-2&&x<=bx+w+2&&y>=top-12&&y<=top+h+3;});}
 let offs=new Map();
 function farmRing(title,items,i){offs=new Map(items.filter(it=>it.off).map(it=>[it.id,it.off]));const [x,top,w]=D.plots[i];FarmUI.ring(title,items,{x:x+w/2,y:top-4});}
 function openBed(i){
  const name=`菜地 · 第 ${F.open.indexOf(i)+1} 块`,b=bedOf(i);
  if(!F.open.includes(i)){const [,days,cost]=MORE.find(m=>m[0]===i),left=Math.max(0,days-F.work),first=MORE.find(m=>!F.open.includes(m[0]))[0]===i;
   const off=!first?'先整理前一块':left?`再经营 ${left} 天`:F.coins<cost?`还差 ${coins(cost-F.coins)} 币`:'';
   return farmRing('荒着的地',[{id:'sf:clear:'+i,label:`整理 · ${cost} 币`,icon:'hoe',off}],i);}
  if(F.phase==='sow'&&!START.includes(i))return showHint('先种有箭头的那块');
  if(!b)return farmRing(name,[{id:'sf:sow:'+i,label:'播种',icon:'seeds'},{id:'sf:look:'+i,label:'查看',icon:'lens',off:'还空着'}],i);
  farmRing(name,[{id:'sf:water:'+i,label:'浇水',icon:'can',off:ripe(b)?'已经熟了':b.watered===today()?'今天浇过了':''},
   {id:'sf:harvest:'+i,label:'收获',icon:'basket',off:ripe(b)?'':'还没熟'},{id:'sf:look:'+i,label:'查看',icon:'lens'}],i);
 }
 view.parentElement.addEventListener('pointerdown',e=>{
  if(e.target!==view||!inSpring()||!['sow','water','done'].includes(F.phase))return;const c=C(),s=c.state;
  if(s.inside||s.scene!==4||s.door||wiping||cardHolds()||sim.mode==='down')return;
  const r=view.getBoundingClientRect(),x=(e.clientX-r.left)*342/r.width+(s.camera||0),y=(e.clientY-r.top)*c.canvas.height/r.height,i=bedAt(x,y);
  if(Math.abs(x-s.x)<10&&y<s.y&&y>s.y-28)return;   // clicks on her still open her own ring
  if(i==null)return;e.stopPropagation();e.preventDefault();openBed(i);
 },true);
 // ---------------------------------------------------------------- actions
 function goBed(i,then){const [x,,w]=D.plots[i];closeRing();T.state.autoAt=sim.t+60;C().target(x+w+4,103,then);}   // she works from the gap after the bed, so the bed stays clickable
 function record(icon,text,v){F.ledger.unshift({icon,text,when:clock(sim.t),v,t:sim.t});F.ledger.length=Math.min(F.ledger.length,30);F.coins=Math.round((F.coins+v)*10)/10;}
 function seedShop(i){
  const story=F.phase==='sow';
  const goods=story?[{group:'种子',note:'妈妈带来的',items:[{name:'胡萝卜',icon:'carrot',cost:0,info:'2 天',line:'妈妈给的一包，种满这一块。',crop:'carrot',bed:i}]}]
   :[{group:'种子',note:'一包种满一块田',items:Object.entries(CROP).map(([k,c])=>({name:c.name,icon:c.icon,cost:c.cost,info:`${c.days} 天`,line:`全部卖掉约 ${c.sell} 币。`,crop:k,bed:i}))}];
  if(!story&&F.coins<1&&!Object.keys(F.beds).length)goods[0].items.unshift({name:'胡萝卜 · 救急',icon:'carrot',cost:0,info:'2 天',line:'手头紧时种子铺送的一包，一次一包。',crop:'carrot',bed:i});
  FarmUI.shop('sf_seed','种子铺 · 这块田种什么',F.coins,goods,{x:D.plots[i][0]+D.plots[i][2]/2,y:D.plots[i][1]});
 }
 function sow(item){
  if(item.cost>F.coins||bedOf(item.bed))return;const c=CROP[item.crop];
  goBed(item.bed,()=>{F.beds[item.bed]={crop:item.crop,progress:0,watered:-1,at:sim.t};if(item.cost)record('seeds',`买${c.name}种子`,-item.cost);worked();speak(pick(['一颗一颗埋好了','种下去了，快点长呀','嗯，土挺松的']),true);if(F.phase==='sow')afterSow();});
 }
 function water(i){const b=bedOf(i);if(!b||ripe(b)||b.watered===today())return;goBed(i,()=>{b.watered=today();worked();speak(pick(['浇透了','喝饱水，好好长','咕嘟咕嘟']),true);if(F.phase==='water')afterWater();});}
 function harvest(i){const b=bedOf(i);if(!ripe(b))return;const c=CROP[b.crop];goBed(i,()=>{delete F.beds[i];record(c.icon,`卖掉一田${c.name}`,c.sell);worked();speak(`拔了一大把${c.name}！`,true);
  if(!F.firstHarvest){F.firstHarvest=true;log(`茵菲谷第一次收成：一田${c.name}，卖了 ${c.sell} 个丢丢币。`);}});}
 function look(i){const b=bedOf(i);if(!b)return;const c=CROP[b.crop],r=ripe(b);
  FarmUI.plant({kind:'crop',plot:`菜地 · 第 ${F.open.indexOf(i)+1} 块`,name:c.name,produce:c.icon,stages:FARM_UI_ART.stages[b.crop],stageNames:STAGE,stage:stageOf(b),days:Math.min(b.progress,c.days),total:c.days,watered:b.watered===today(),sell:c.sell,
   actions:[{label:'浇水',icon:'can',off:r?'已经熟了':b.watered===today()?'今天浇过了':'',on:()=>{closeSocialSheet();water(i);}},{label:'收获',icon:'basket',off:r?'':'还没熟',primary:true,on:()=>{closeSocialSheet();harvest(i);}}]});}
 function clear(i){const [,days,cost]=MORE.find(m=>m[0]===i);if(F.work<days||F.coins<cost||F.open.includes(i))return;goBed(i,()=>{F.open.push(i);record('hoe','整理一块新田',-cost);speak('又多了一块地！',true);});}
 function pcState(){
  const dayStart=today()*1440,todayV=F.ledger.filter(r=>r.t>=dayStart).reduce((a,r)=>a+r.v,0),next=MORE.find(m=>!F.open.includes(m[0]));
  return {farm:{fields:F.open.length,nextField:next?(F.work>=next[1]?`可以整理第 ${F.open.length+1} 块（${next[2]} 币）`:`再经营 ${next[1]-F.work} 天可整理第 ${F.open.length+1} 块（${next[2]} 币）`):'今年的田都整理好了',trees:0,animals:'还没有',assets:F.open.length*3},
   account:{balance:F.coins,today:Math.round(todayV*10)/10,ledger:F.ledger.slice(0,8)},
   fund:{held:0,pct:0,inLeft:0,outLeft:0,amount:0,history:[10,10,10,10,10,10,10,10,10,10,10,10,10,10]},gifts:{tab:'gift',sel:0,items:[],keep:[{locked:1},{locked:1},{locked:1}]}};
 }
 const oldPick=ringPick;ringPick=function(id){
  if(id==='airport:spring'&&!F.unlocked){closeRing();showHint('还没收到家里的消息');return;}
  if(!id.startsWith('sf:'))return oldPick(id);
  if(offs.has(id)){showHint(offs.get(id));return;}
  const [,act,n]=id.split(':'),i=+n;closeRing();
  if(act==='pc')return FarmUI.computer('coin',pcState());
  ({sow:seedShop,water,harvest,look,clear})[act]?.(i);
 };
 const oldCommand=command;command=function(act,item){if(act==='sf_seed'){if(item&&!(item.cost>F.coins))sow(item);else if(item)showHint(`还差 ${coins(item.cost-F.coins)} 币`);return;}return oldCommand(act,item);};
 // ---------------------------------------------------------------- spring-only cards, talk and calls (owner, 2026-11-02)
 CARDS.push(...SPRING_CARDS);
 for(const cd of SPRING_CARDS)for(const k of ['a','b'])cd[k].out.forEach((o,i)=>{if(o.mood)ML[o.id=`card${cd.n}${k}${i}`]={...o.mood};});
 for(const [key,pool]of Object.entries(SPRING_TALK))if(key!=='people')pool.forEach((t,i)=>{if(t.mood)ML[t.id=`spring_talk_${key}_${i}`]={...t.mood};});
 const growing=()=>Object.entries(F.beds).filter(([,b])=>!ripe(b));
 const oldFits=cardFits;cardFits=function(cd,c){if(cd.at==='spring_test'&&(F.phase!=='done'||cd.farmIf==='crop'&&!growing().length))return false;return oldFits(cd,c);};
 function applyFarm(f,title){
  if(f.coins){const v=f.coins<0?-Math.min(F.coins,-f.coins):f.coins;if(v)record('coin',title,v);}
  const g=growing();
  if(f.water)for(const [,b]of g)b.watered=today();
  if(f.grow){for(const [,b]of f.grow==='all'?g:g.slice(0,1).length?[pick(g)]:[])b.progress++;}
  if(f.pest){const hit=g.filter(([,b])=>b.progress>0);if(hit.length)pick(hit)[1].progress--;}
  if(f.eat&&g.length)delete F.beds[pick(g)[0]];
 }
 const oldNeeds=cardNeeds;cardNeeds=function(){const r=oldNeeds();if(card?.cd.at==='spring_test'&&card.o.farm)applyFarm(card.o.farm,fill(card.cd.title,card.vars));return r;};
 const oldChat=chatItem;chatItem=function(kind,who,via,contactId){
  const it=oldChat(kind,who,via,contactId);
  if(!inSpring()||!['call','text','video'].includes(kind)||Math.random()<.3)return it;
  const c=contactId&&socialState.contacts.find(x=>x.id===contactId),key=c?.family||(c?'friend':who),pool=SPRING_TALK[key];if(!pool)return it;
  const seen=((lifeFlags.talkSeen||={})['spring_'+key]||=[]);let fresh=pool.map((t,i)=>i).filter(i=>!seen.includes(i));if(!fresh.length){seen.length=0;fresh=pool.map((t,i)=>i);}
  const i=pick(fresh),t=pool[i];seen.push(i);it.talk.end=it.talk.end.replace(it.talk.title,t.title);Object.assign(it.talk,{title:t.title,lines:t.lines,mood:t.mood,id:t.id});if(c)c.lastTopic=t.title;return it;};
 NPC_TALK_TEXT.spring_test?.adult.push(...SPRING_TALK.people);
 withHeroHooks.push(id=>id==='mom'&&mom.on&&inSpring());   // 妈妈 beside her on the farm never phones her
 const oldCan=canReceiveCall;canReceiveCall=function(){return oldCan()&&!speech.open;};
 const oldReq=requestIncomingCall;requestIncomingCall=function(id,kind='call'){if(inSpring()&&['friend_home','visit'].includes(kind))kind='call';return oldReq(id,kind);};   // nobody can be visited from the farm
 // ---------------------------------------------------------------- saves
 const oldSnap=snapshot;snapshot=function(){const s=oldSnap();s.springFarm=JSON.parse(JSON.stringify(F));return s;};
 const oldRestore=restore;restore=function(save){const r=oldRestore(save);F=Object.assign(blank(),save?.springFarm||{});if(['arrive','room','field'].includes(F.phase))F.phase='none';   // an unfinished welcome replays on the next landing
  speech.hide();mom.on=false;if(inSpring()&&F.unlocked&&F.phase!=='done'&&F.phase!=='none')arriveAt('spring_test');return r;};
 // ---------------------------------------------------------------- test toolbar
 const bar=T.root.querySelector('header');
 for(const [label,fn]of [['妈妈来信（测试）',()=>{if(!sendLetter())showHint('信已经寄过了');else if(!['home','front'].includes(sim.place))showHint('信在家门口，回家就能看到');}],['快进到明早（测试）',()=>{sim.t=(today()+1)*1440+7*60;roll();}]]){const b=document.createElement('button');b.textContent=label;b.onclick=fn;bar.append(b);}
 return {get lines(){return lines;},get state(){return F;},set state(v){F=v;},speech,mom,openBed,sendLetter,arrive,roll,pcState};
})();
window.springFarm=springFarm;
