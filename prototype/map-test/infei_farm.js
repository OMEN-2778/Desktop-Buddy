// 茵菲谷 farm life (owner 2026-11-02: "做丰富"). Test page only, loaded after spring_story.js and
// built on its API (springFarm.X). Numbers follow DIDI_CURRENCY.md.
// - 果园: two empty pits in the orchard take a sapling (8 币, at most 2). Trees grow by themselves
//   (not in winter, except citrus), are grown after 8 days and fruit every 6 days in their season:
//   桃 summer, 梨 summer+autumn, 苹果 autumn, 橙 winter.
// - 牧场: 鸡 8 / 羊 24 / 牛 36 币 (first year at most 2 / 1 / 1). Spring to autumn they graze by
//   themselves; in winter they stay in the barn and want hay (free). Products every 4 / 6 / 4 fed days;
//   a daily pat builds friendship (5 hearts) and with 4+ hearts the product is the better kind.
// - 爸妈帮忙: some days 妈妈 or 爸爸 drops by and waters one dry bed (never pays, buys or sells).
// - 每日操盘: one made-up fund, a new price each day, in/out at most 10 a day, 60 at most, no debt.
// - 仓库/礼物/藏品: everything gathered is kept until sold or given; first finds fill the 藏品.
const infeiFarm=(()=>{
 const X=springFarm.X,D=SPRING_FARM_DATA,C=X.C,ICON=FARM_UI_ART.icons;
 const today=X.today,SK=['spring','summer','autumn','winter'];
 Object.assign(X.ITEMS,{
  peach:{name:'水蜜桃',icon:'peach',price:2,line:'自家树上摘的，软软的，很甜。'},
  pear:{name:'雪梨',icon:'pear',price:2,line:'水多，咬一口脆生生的。'},
  apple:{name:'苹果',icon:'apple',price:2,line:'红了一大半，削皮都舍不得。'},
  orange:{name:'橙子',icon:'orange',price:2,line:'冬天还挂在枝头的橙子。'},
  egg:{name:'一篮鸡蛋',icon:'egg',price:1,line:'自家母鸡下的。'},
  egg_big:{name:'一篮大鸡蛋',icon:'egg',price:1.5,line:'鸡跟你熟了，蛋都大了一圈。'},
  wool:{name:'一团羊毛',icon:'wool',price:3,line:'软乎乎的，可以织条围巾。'},
  wool_fine:{name:'一团细羊毛',icon:'wool',price:4.5,line:'又细又白，梳得最好的那种。'},
  milk:{name:'一桶牛奶',icon:'milk',price:2,line:'早上刚挤的。'},
  milk_rich:{name:'一桶浓牛奶',icon:'milk',price:3,line:'奶香特别浓，牛心情好的时候才有。'},
 });
 X.blank=()=>({trees:{},animals:[],fund:{held:0,locked:0,inDay:-1,inToday:0,outDay:-1,outToday:0,amount:1,pct:0,history:[]},help:null,gifts:{}});
 const S=()=>{const f=X.F,b=X.blank();for(const k in b)if(f[k]==null)f[k]=b[k];return f;};
 const se=()=>X.seasonAt(today()),inSpring=X.inSpring,ripeTree=t=>t.grown>=MATURE;
 const walk=(x,then)=>{closeRing();C().target(Math.round(x),103,then);};
 const r2=v=>Math.round(v*10)/10;
 // ================================================================ 果园
 const TREE={peach:{name:'桃树',fruit:'peach',seasons:[1]},pear:{name:'梨树',fruit:'pear',seasons:[1,2]},apple:{name:'苹果树',fruit:'apple',seasons:[2]},orange:{name:'橙子树',fruit:'orange',seasons:[3]}};
 const MATURE=8,CYCLE=6,TREE_COST=8,TREE_MAX=2,SN=X.SEASON_NAME;
 const fruitSeasons=k=>TREE[k].seasons.map(n=>SN[n]).join('、')+'天结果';
 function treeDay(d){for(const t of Object.values(S().trees)){const s=X.seasonAt(d);
  if(!ripeTree(t)){if(s!==3||t.kind==='orange'){t.grown++;if(ripeTree(t))t.cycle=CYCLE-1;}}
  else if(TREE[t.kind].seasons.includes(s)&&!t.ready&&++t.cycle>=CYCLE){t.ready=true;t.cycle=0;}
  if(t.ready&&!TREE[t.kind].seasons.includes(s))t.ready=false;}}   // last season's fruit drops
 const treeStage=t=>t.grown<3?0:!ripeTree(t)?1:t.ready?3:2;
 const pit=i=>D.pits[i];
 function drawTrees(ctx,info){if(info.inside||info.region!==5)return;
  for(const [i,t]of Object.entries(S().trees)){const [px,py]=pit(i),a=D.trees[t.kind][SK[se()]][treeStage(t)];ctx.drawImage(X.imgOf(a.src),px+a.dx,py+a.dy);}}
 function openPit(i){const t=S().trees[i],[px,py]=pit(i),at={x:px,y:py-22};
  if(!t)return X.ring('空树坑',[{id:'sf:plant:'+i,label:'种果树',icon:'sapling',off:Object.keys(S().trees).length>=TREE_MAX?'今年两棵种满了':''}],at);
  const k=TREE[t.kind],why=t.ready?'':!ripeTree(t)?`还要长 ${MATURE-t.grown} 天`:!k.seasons.includes(se())?fruitSeasons(t.kind):`再过 ${CYCLE-t.cycle} 天`;
  X.ring(k.name,[{id:'sf:fruit:'+i,label:'摘果',icon:'basket',off:why},{id:'sf:treelook:'+i,label:'查看',icon:'lens'}],at);}
 function treeShop(i){
  FarmUI.shop('sf_tree','果苗铺 · 种在这个坑里',X.F.coins,[{group:'果苗',note:`一棵 ${TREE_COST} 币，${MATURE} 天长成，之后每 ${CYCLE} 天一茬`,items:Object.entries(TREE).map(([k,t])=>({name:t.name+'苗',icon:t.fruit,cost:TREE_COST,info:fruitSeasons(k),line:`${X.ITEMS[t.fruit].name}每个约 ${X.ITEMS[t.fruit].price} 币。${k==='orange'?'冬天也不落叶。':'冬天落叶歇着。'}`,kind:k,pit:i}))}],{x:pit(i)[0],y:pit(i)[1]-10});}
 function plantTree(it){if(it.cost>X.F.coins||S().trees[it.pit]||Object.keys(S().trees).length>=TREE_MAX)return;
  walk(pit(it.pit)[0]+14,()=>{S().trees[it.pit]={kind:it.kind,grown:0,cycle:0,ready:false,at:today()};X.record('sapling',`种下一棵${TREE[it.kind].name}`,-it.cost);X.worked();speak('种好啦，快快长大',true);log(`在果园种下一棵${TREE[it.kind].name}。`);});}
 function pickFruit(i){const t=S().trees[i];if(!t?.ready)return;walk(pit(i)[0]+14,()=>{t.ready=false;X.addItem(TREE[t.kind].fruit,2);X.worked();speak(pick(['摘了一兜！','好香','这个最大']),true);});}
 function treeLook(i){const t=S().trees[i],k=TREE[t.kind],stages=D.trees[t.kind][SK[se()]].map(a=>a.src);
  FarmUI.plant({kind:'tree',plot:'果园',name:k.name,produce:k.fruit,cycle:`${fruitSeasons(t.kind)}，每 ${CYCLE} 天一茬`,stages,stageNames:['树苗','小树','长成','结果'],stage:treeStage(t),days:Math.min(t.grown,MATURE),total:MATURE,
   watered:true,waterLine:t.kind==='orange'||se()!==3?'不用浇水，自己会长':'冬天落叶歇着',waterIcon:'sapling',sellLine:`一茬两个，每个约 ${X.ITEMS[k.fruit].price} 币`,
   actions:[{label:'摘果',icon:'basket',primary:true,off:t.ready?'':'还没有果子',on:()=>{closeSocialSheet();pickFruit(i);}}]});}
 // ================================================================ 牧场
 const ANIMAL={chicken:{name:'鸡',cost:8,max:2,product:'egg',best:'egg_big',every:4,size:[11,11]},sheep:{name:'羊',cost:24,max:1,product:'wool',best:'wool_fine',every:6,baby:4,size:[24,18]},cow:{name:'牛',cost:36,max:1,product:'milk',best:'milk_rich',every:4,size:[40,26]}};
 const NAMES={chicken:['咕咕','小黄','豆豆','花卷'],sheep:['棉花','云朵','卷卷'],cow:['奶糖','大黄','哞哞']};
 const hearts=a=>Math.min(5,Math.floor(a.love/100)),baby=a=>a.kind==='sheep'&&today()-a.day<ANIMAL.sheep.baby;
 const grazing=()=>se()!==3,fedToday=a=>grazing()||a.fedDay===today();
 function animalDay(d){for(const a of S().animals){const fed=X.seasonAt(d)!==3||a.fedDay===d,k=ANIMAL[a.kind];
  if(!fed)a.love=Math.max(0,a.love-20);if(a.petDay!==d)a.love=Math.max(0,a.love-4);
  if(fed&&!a.ready&&!(a.kind==='sheep'&&d-a.day<k.baby)&&++a.prod>=k.every){a.ready=a.love>=400?k.best:k.product;a.prod=0;}}}
 // where they live: chickens by the farmhouse (home screen), sheep and cows behind the pasture fence
 // chickens live in the pasture fence too (owner 2026-11-03: "I keep chickens, why can't I see them in the fence")
 const AREA={chicken:{scene:5,x:[342+50,342+280],y:[82,88]},sheep:{scene:5,x:[342+40,342+300],y:[78,90]},cow:{scene:5,x:[342+40,342+290],y:[80,90]}};
 const rnd=(a,b)=>a+Math.random()*(b-a);
 function place(a){const r=AREA[a.kind];if(a.x!=null&&(a.x<r.x[0]-5||a.x>r.x[1]+5))a.x=a.y=null;   // older saves: chickens by the farmhouse
  a.x??=rnd(...r.x);a.y??=Math.round(rnd(...r.y));a.tx=null;a.f=a.f||Math.random()*6;}
 let lastT=0;
 function drawAnimals(ctx,info){if(info.inside||se()===3)return;const t=C().state.time,dt=Math.min(.1,Math.max(0,t-lastT));lastT=t;
  const mine=S().animals.filter(a=>AREA[a.kind].scene===info.region);if(!mine.length)return;
  for(const a of mine.sort((p,q)=>p.y-q.y)){place(a);const r=AREA[a.kind];
   if(a.tx==null&&Math.random()<.004)a.tx=Math.max(r.x[0],Math.min(r.x[1],a.x+rnd(-40,40)));
   if(a.tx!=null){const d=a.tx-a.x,st=dt*(a.kind==='chicken'?9:5);if(Math.abs(d)<=st)a.tx=null;else{a.x+=Math.sign(d)*st;a.dir=Math.sign(d);}}
   const kind=baby(a)?'lamb':a.kind,frames=D.animals[kind],moving=a.tx!=null,fi=a.kind==='chicken'?Math.floor(t*3+a.f)%2:moving?[0,3][Math.floor(t*4)%2]:Math.floor(t*1.4+a.f)%3,pic=X.imgOf(frames[fi%frames.length]);
   const w=pic.width||ANIMAL[a.kind].size[0],h=pic.height||ANIMAL[a.kind].size[1],x=Math.round(a.x-w/2),y=a.y-h;
   ctx.save();if((a.dir||1)<0){ctx.translate(x*2+w,0);ctx.scale(-1,1);}if(window.infeiHover?.animal===a.id)drawObjectHover(ctx,pic,x,y);ctx.drawImage(pic,x,y);ctx.restore();   // hover glow, like the house's furniture
   if(a.ready)bubble(ctx,Math.round(a.x),y-2,{egg:'#e8c88a',wool:'#d8d2e6',milk:'#9cc8ef'}[ANIMAL[a.kind].product],t);
  }
  if(info.region===5){const fr=C().current?.().front;if(fr)ctx.drawImage(X.imgOf(fr),0,0);}   // the fence stands in front of them
 }
 function bubble(ctx,x,y,c,t){y+=Math.round(Math.sin(t*3)*1);ctx.fillStyle='#22182a';ctx.fillRect(x-4,y-9,9,7);ctx.fillRect(x-1,y-2,3,1);ctx.fillStyle='#f7f6fb';ctx.fillRect(x-3,y-8,7,5);ctx.fillRect(x,y-3,1,1);ctx.fillStyle=c;ctx.fillRect(x-1,y-7,3,3);}
 function animalAt(x,y,region){return S().animals.filter(a=>AREA[a.kind].scene===region&&a.x!=null).reverse().find(a=>{const [w,h]=ANIMAL[a.kind].size;return Math.abs(x-a.x)<w/2+2&&y<=a.y+2&&y>=a.y-h-10;});}
 function openAnimal(a){const k=ANIMAL[a.kind],at={x:a.x-(C().state.camera||0),y:a.y-ANIMAL[a.kind].size[1]-6};
  X.ring(`${a.name} · ${'♥'.repeat(hearts(a))||'刚认识'}`,[{id:'sf:pat:'+a.id,label:'摸摸',icon:'heart',off:a.petDay===today()?'今天摸过了':''},
   {id:'sf:feed:'+a.id,label:'喂草料',icon:'hay',off:grazing()?'在外面吃草呢':a.fedDay===today()?'吃饱了':''},
   {id:'sf:collect:'+a.id,label:'收取',icon:'basket',off:a.ready?'':baby(a)?'还小呢':`再过 ${k.every-a.prod} 天`},{id:'sf:animal:'+a.id,label:'查看',icon:'lens'}],{x:Math.max(30,Math.min(312,at.x)),y:at.y});}
 const byId=id=>S().animals.find(a=>a.id===id);
 const near=(a,then)=>{if(se()===3||AREA[a.kind].scene!==C().state.scene){then();return;}walk(Math.max(20,Math.min(C().current().width-20,a.x)),then);};
 function pat(a){if(!a||a.petDay===today())return;near(a,()=>{a.petDay=today();a.love=Math.min(500,a.love+30);X.worked();speak(pick([`${a.name}乖`,`${a.name}的毛好暖`,'蹭蹭','它眯起眼睛了']),true);});}
 function feed(a){if(!a||grazing()||a.fedDay===today())return;a.fedDay=today();a.love=Math.min(500,a.love+10);X.worked();speak(`${a.name}，开饭啦`,true);}
 function collect(a){if(!a?.ready)return;near(a,()=>{const it=a.ready;a.ready=null;X.addItem(it);X.worked();speak(`收了${X.ITEMS[it].name}！`,true);});}
 function animalSheet(a){const k=ANIMAL[a.kind],s=FarmUI.sheet(`牧场 · ${a.name}`,'fu-ranch'),c=socialContent(s),el=FarmUI.el;
  const body=el('div','fu-ranch-body'),pen=el('div','fu-pen');pen.append(FarmUI.img(D.animals[baby(a)?'lamb':a.kind][0],'fu-animal',()=>Math.max(1,Math.round(scale))));
  const facts=el('div','fu-facts');facts.append(el('h4',null,`${a.name}（${k.name}）`),FarmUI.meter('亲密','heart',hearts(a),5));
  const st=el('p','fu-sub');st.append(FarmUI.icon('hay'),el('span',null,se()===3?(a.fedDay===today()?'今天喂过草料了':'冬天在棚里，要喂草料'):'在外面吃草，不用喂'));
  const pr=el('p','fu-sub');pr.append(FarmUI.icon(k.product),el('span',null,a.ready?`${X.ITEMS[a.ready].name}可以收了`:baby(a)?`小羊还要长 ${k.baby-(today()-a.day)} 天`:`再过 ${k.every-a.prod} 天有${X.ITEMS[k.product].name}`));
  facts.append(st,pr);body.append(pen,facts);
  c.append(body,el('p','fu-note',`每天摸一摸亲密会涨；四颗心以上，产出会变成${X.ITEMS[k.best].name}。`));
  const re=()=>animalSheet(a);
  s.append(FarmUI.actions([{label:'摸摸',icon:'heart',off:a.petDay===today()?'今天摸过了':'',on:()=>{a.petDay=today();a.love=Math.min(500,a.love+30);X.worked();re();}},
   {label:'喂草料',icon:'hay',off:grazing()?'在吃草':a.fedDay===today()?'吃饱了':'',on:()=>{feed(a);re();}},
   {label:'收取',icon:'basket',primary:true,off:a.ready?'':'还没有',on:()=>{const it=a.ready;a.ready=null;X.addItem(it);X.worked();re();}}]));}
 function herdSheet(){const list=S().animals;if(!list.length)return showHint('还没有牲畜，先去牲畜铺看看');animalSheet(list[0]);
  const s=socialSheet,tabs=FarmUI.el('div','fu-tabs');for(const a of list){const b=FarmUI.el('button',null,a.name);b.type='button';b.onclick=()=>{animalSheet(a);s.querySelector('.social-sheet-content').prepend(tabs);};tabs.append(b);}
  s.querySelector('.social-sheet-content').prepend(tabs);}
 function animalShop(){const count=k=>S().animals.filter(a=>a.kind===k).length;
  FarmUI.shop('sf_animal','牲畜铺 · 添点什么',X.F.coins,[{group:'牲畜',note:'清水和草料免费',items:Object.entries(ANIMAL).map(([k,a])=>({name:a.name,pic:D.animals[k==='sheep'?'lamb':k][0],cost:a.cost,info:`每 ${a.every} 天产${X.ITEMS[a.product].name.replace(/^一[篮团桶]/,'')}`,line:`${k==='chicken'?'住在农舍边。':k==='sheep'?'来的是小羊，4 天长大。':'住在牧场。'}已有 ${count(k)} 只，今年最多 ${a.max} 只。`,off:count(k)>=a.max?'今年养满了':'',kind:k}))}]);}
 function buy(it){const k=ANIMAL[it.kind];if(it.cost>X.F.coins||S().animals.filter(a=>a.kind===it.kind).length>=k.max)return;
  const used=new Set(S().animals.map(a=>a.name)),name=NAMES[it.kind].find(n=>!used.has(n))||k.name;
  const a={id:'a'+Date.now().toString(36),kind:it.kind,name,day:today(),love:0,petDay:-1,fedDay:-1,prod:0,ready:null};S().animals.push(a);place(a);
  X.record('farm',`买了${k.name}「${name}」`,-it.cost);log(`牧场来了一只${k.name}，起名叫「${name}」。`);speak(`你好呀，${name}`,true);}
 const BARN=[342+110,342+290,30,88];
 const inRect=(x,y,[x0,x1,y0,y1])=>x>=x0&&x<=x1&&y>=y0&&y<=y1;
 // ================================================================ 爸妈帮忙浇水
 const parent={on:false,who:'mom',x:380,tx:null,done:null,t:0,n:null,water:0,bed:null};
 // owner 2026-11-12: the help comes early (before she is up), goes in the diary, and the parent tells her themselves, so
 // she never walks out to water a bed that is already wet. Summer-ish seasons: every dry bed; winter: the animals' hay.
 function planHelp(d){if(Math.random()<.7)S().help={day:d,at:d*1440+Math.round((6*60+10)+Math.random()*50),who:Math.random()<.5?'mom':'dad',done:false};}
 const pName=w=>w==='mom'?'妈妈':'爸爸';
 function dryBeds(day){return X.F.open.filter(i=>{const b=X.bedOf(i);return b&&!X.CROP[b.crop]?.dry&&!X.ripe(b)&&b.watered!==day;});}   // owner 2026-11-12: if they help, they water every dry bed
 const hungry=()=>X.seasonAt(today())===3?S().animals.filter(a=>a.fedDay!==today()):[];
 function tellHer(who,text){window.seasonParents?.tell?.(who,text);}
 function wateredNote(who,beds){const n=beds.length>3?'所有没浇的':beds.map(i=>X.F.open.indexOf(i)+1).join('、');
  log(beds.length>3?`早上${pName(who)}把地全浇了一遍。`:`早上${pName(who)}帮你给第 ${n} 块地浇了水。`);
  tellHer(who,pick(who==='mom'?['地我早上都浇过了，今天不用再浇了。','早上顺手把菜地浇了一遍，你歇着吧。']:['菜地我起早浇完了，今天不用管了。','地都浇过了，你干点别的去。']));}
 function fedNote(who,list){log(`早上${pName(who)}把棚里的${list.length>2?'牲畜':list.map(a=>a.name).join('和')}都喂了草料。`);
  tellHer(who,pick([`棚里的${list.length>2?'牛羊':list.map(a=>a.name).join('和')}我早上喂过了，你不用管了。`,'草料我早上添过了，今天不用喂了。']));}
 // not in 茵菲谷 (or the day rolled by): it just happens
 function helpOff(d){const h=S().help;if(!h||h.day!==d||h.done)return;h.done=true;
  if(X.seasonAt(d)===3){const list=S().animals.filter(a=>a.fedDay!==d);if(!list.length)return;for(const a of list)a.fedDay=d;log(`${pName(h.who)}帮你把棚里的牲畜喂了。`);return;}
  const beds=dryBeds(d);if(!beds.length)return;for(const i of beds)X.bedOf(i).watered=d;log(`${pName(h.who)}帮你把地都浇了一遍。`);}
 // in 茵菲谷: the parent walks over (season_parents.js) and does it, bed by bed
 function helpTick(){const h=S().help;if(!h||h.day!==today()||h.done||sim.t<h.at)return;
  const sp=window.seasonParents;if(!sp?.doErrand){helpOff(today());return;}
  if(X.seasonAt(today())===3){const list=hungry();h.done=true;if(!list.length)return;
   sp.doErrand(h.who,{s:5,x:540,face:-1,fx:'grain',stay:3},()=>{const now=hungry();for(const a of now)a.fedDay=today();if(now.length)fedNote(h.who,now);});return;}
  if(X.rainedSoFar()){h.done=true;return;}
  const beds=dryBeds(today());h.done=true;if(!beds.length)return;
  const done=[],next=k=>{if(k>=beds.length){if(done.length)wateredNote(h.who,done);return;}const i=beds[k],[bx,,bw]=D.plots[i];
   sp.doErrand(h.who,{s:4,x:bx+bw+4,face:-1,fx:'water',stay:2.4},()=>{const b=X.bedOf(i);if(b&&b.watered!==today()&&!X.ripe(b)){b.watered=today();done.push(i);}next(k+1);});};
  next(0);}
 setInterval(()=>{try{if(sim.place==='spring_test'&&X.F.phase==='done'&&speed)helpTick();}catch(e){console.warn('parents help',e);}},500);
 function drawParent(ctx,info){if(!parent.on||info.inside||info.region!==4)return;const t=C().state.time,dt=Math.min(.1,Math.max(0,t-parent.t));parent.t=t;
  if(parent.water>0){parent.water-=dt;const [bx,top,bw,bh]=D.plots[parent.bed];ctx.fillStyle='#9cc8ef';for(let k=0;k<6;k++){const xx=bx+bw-4-((k*7+Math.floor(t*20))%Math.min(30,bw)),yy=top+((k*5+Math.floor(t*30))%(bh+4));ctx.fillRect(xx,yy,1,2);}
   if(parent.water<=0){const b=X.bedOf(parent.bed);if(b&&b.watered!==today()){b.watered=today();log(`${pName(parent.who)}回来了一趟，帮你给第 ${X.F.open.indexOf(parent.bed)+1} 块田浇了水。`);}parent.tx=380;parent.done=()=>parent.on=false;}}
  else if(parent.tx!=null){const d=parent.tx-parent.x,st=dt*WALK*1.1;if(Math.abs(d)<=st){parent.x=parent.tx;parent.tx=null;const f=parent.done;parent.done=null;f?.();}else{parent.x+=Math.sign(d)*st;parent.facing=Math.sign(d);}}
  const walking=parent.tx!=null,ph=Math.floor(t*7)%4,f={expr:'happy',look:parent.water>0?-1:parent.facing||-1,bob:walking?ph%2:0,sway:walking?ph%2:0,wave:null};
  ctx.drawImage(npcCanvas(parent.n,f,walking?(ph===1?'walkL':ph===3?'walkR':'stand'):'stand'),Math.round(parent.x)-10,76);}
 withHeroHooks.push(id=>parent.on&&id===parent.who&&inSpring());
 // ================================================================ 每日操盘
 // owner 2026-11-06: 波动太平滑 → every day moves (never 0), mostly 1-4 %, now and then a big day of 6-9 %
 const MOVES=[[-8,3],[-6,6],[-4,11],[-3,13],[-2,11],[-1,6],[1,6],[2,11],[3,13],[4,11],[6,6],[8,3]];
 function fundDay(d){const f=S().fund;let r=Math.random()*100,pct=0;for(const [p,w]of MOVES){if((r-=w)<0){pct=p;break;}}
  pct=Math.round((pct+(Math.random()-.5)*(Math.abs(pct)>1?1.6:.8))*10)/10||(Math.random()<.5?-.5:.5);   // a decimal, like a real price
  f.pct=pct;f.held=Math.round(f.held*(1+pct/100)*100)/100;f.locked=0;const last=f.history.at(-1)??10;f.history.push(Math.round(last*(1+pct/100)*100)/100);if(f.history.length>14)f.history.shift();}
 function fundLeft(){const f=S().fund,d=today();if(f.inDay!==d){f.inDay=d;f.inToday=0;}if(f.outDay!==d){f.outDay=d;f.outToday=0;}
  return {inLeft:Math.max(0,Math.floor(Math.min(10-f.inToday,60-f.held,X.F.coins))),outLeft:Math.max(0,Math.floor(Math.min(10-f.outToday,f.held-f.locked)*10)/10)};}
 // ================================================================ 仓库 / 礼物 / 藏品
 const contactOf=id=>socialState.contacts.find(c=>c.id===id);
 function sell(k,n){n=Math.min(n,S().inv[k]||0);if(!n)return;S().inv[k]-=n;if(!S().inv[k])delete S().inv[k];const it=X.ITEMS[k];X.record(it.icon,`卖掉${n>1?n+' 份':''}${it.name}`,r2(it.price*n));}
 function giveTo(k){closeSocialSheet();const cs=sortedContacts().filter(c=>c.family||c.affinity>0).slice(0,12);
  PICK.sf_give={title:`送礼 · ${X.ITEMS[k].name}送给谁`,groups:()=>[{name:'家人',items:cs.filter(c=>c.family).map(c=>({title:contactName(c),icon:ICON.gift,line:S().gifts[c.id]===today()?'今天已经送过了':'',item:{id:c.id,k}}))},
   {name:'朋友',items:cs.filter(c=>!c.family).map(c=>({title:contactName(c),info:contactRelation(c),icon:ICON.gift,line:S().gifts[c.id]===today()?'今天已经送过了':'',item:{id:c.id,k}}))}].filter(g=>g.items.length)};
  openPicker('sf_give',pickFrom('buddy'));}
 const hash=s=>[...s].reduce((a,ch)=>(a*31+ch.charCodeAt(0))>>>0,7);
 function give({id,k}){const c=contactOf(id);if(!c||!S().inv[k])return;if(S().gifts[id]===today())return showHint('今天已经送过了，明天再送');
  S().inv[k]--;if(!S().inv[k])delete S().inv[k];S().gifts[id]=today();const it=X.ITEMS[k],name=contactName(c),liked=c.family||hash(id+k)%3===0,gain=c.family?3:liked?4:2;
  const before=contactRelation(c);c.affinity=Math.min(100,(c.affinity||0)+gain);c.lastContact=sim.t;contactsSig='';
  const line=c.family?pick([`${name}说“自己种的就是香”，非让拍张照发给亲戚看。`,`${name}收下了，说下回寄点好吃的来。`]):liked?pick([`${name}说正好想吃这个，开心得不得了。`,`${name}拿着看了半天，说这是今年收到最好的礼物。`]):pick([`${name}收下了，说谢谢。`,`${name}有点意外，笑着收下了。`]);
  log(`把${it.name}送给了${name}。${line}`);if(typeof addSocialMemory==='function')addSocialMemory(c,'收到茵菲谷的礼物',`收到了${it.name}`);
  if(contactRelation(c)!==before)log(`和${name}从${before}成为了${contactRelation(c)}。`);speak(liked?'TA 好像很喜欢':'送出去啦',true);}
 // ================================================================ 丢丢平板电脑
 function pcState(){const f=S(),left=fundLeft(),fund=f.fund;if(!fund.history.length||fund.history.length>=14&&fund.history.every(v=>v===fund.history[0])){let v=10;fund.history=Array.from({length:14},()=>v=Math.round(v*(1+((Math.random()-.5)*8)/100)*100)/100);}   // no flat line before the first real day
  const base=X.pcStateBase(),inv=Object.entries(f.inv).filter(([,n])=>n>0),value=r2(inv.reduce((a,[k,n])=>a+X.ITEMS[k].price*n,0));
  const animals=Object.keys(ANIMAL).map(k=>`${ANIMAL[k].name} ${f.animals.filter(a=>a.kind===k).length}`).join(' · ');
  base.farm.trees=Object.keys(f.trees).length;base.farm.animals=animals;base.farm.animalsSub=f.animals.length?`最亲的：${[...f.animals].sort((a,b)=>b.love-a.love)[0].name}`:'去牧场的粮仓看看';
  base.farm.assets=f.open.length*3+Object.keys(f.trees).length*TREE_COST+f.animals.reduce((a,x)=>a+ANIMAL[x.kind].cost,0);
  base.farm.more=[['仓库',`${inv.reduce((a,[,n])=>a+n,0)} 份`,`约值 ${value} 币`],['季节',`${SN[se()]}天`,`还有 ${SEASON_DAYS-today()%SEASON_DAYS} 天换季`]];
  const refresh=tab=>()=>FarmUI.computer(tab,pcState());
  base.fund={held:r2(fund.held),pct:fund.pct,inLeft:left.inLeft,outLeft:left.outLeft,amount:fund.amount,history:fund.history,
   inOff:left.inLeft<fund.amount?(fund.held>=60?'最多 60 币':X.F.coins<fund.amount?'丢丢币不够':'今天投满了'):'',outOff:left.outLeft<fund.amount?(fund.locked>0&&fund.held-fund.locked<fund.amount?'今天投的明天才能赎':'今天赎不了这么多'):'',
   note:`一只虚构的基金，每天变一次价。今天 ${fund.pct>0?'+':''}${fund.pct}%。每天投入、赎回各最多 10 币，最多持有 60 币；今天投的明天才能赎回。不会欠钱。`,
   onStep:d=>{fund.amount=Math.max(1,Math.min(10,fund.amount+d));refresh('fund')();},
   onIn:()=>{const a=fund.amount;if(fundLeft().inLeft<a)return;fund.held+=a;fund.locked+=a;fund.inToday+=a;X.record('chart','投入每日操盘',-a);refresh('fund')();},
   onOut:()=>{const a=fund.amount;if(fundLeft().outLeft<a)return;fund.held-=a;fund.outToday+=a;X.record('chart','赎回每日操盘',a);refresh('fund')();}};
  base.gifts={tab:'gift',sel:0,tabs:[['gift','仓库'],['keep','藏品']],empty:'仓库是空的，去地里、果园、牧场收点什么吧。',
   items:inv.map(([k,n])=>{const it=X.ITEMS[k];return {icon:it.icon,name:it.name,n,line:`${it.line} 每份约 ${it.price} 币。`,actions:[{label:'送人',primary:true,on:()=>giveTo(k)},{label:'卖一份',on:()=>{sell(k,1);refresh('gift')();}},...(n>1?[{label:`全卖 ${r2(it.price*n)}`,on:()=>{sell(k,n);refresh('gift')();}}]:[])]};}),
   keep:Object.entries(X.ITEMS).map(([k,it])=>f.seen[k]!=null?{icon:it.icon,name:it.name,line:`第 ${f.seen[k]+1} 天第一次得到。${it.line}`,actions:[]}:{locked:1})};
  return base;}
 X.pcState=pcState;
 // ================================================================ hooks into the farm
 X.hooks.day.push(d=>{helpOff(d);treeDay(d);animalDay(d);fundDay(d);planHelp(d+1);});
 X.hooks.draw.push((ctx,info)=>{C().state.noHerd=true;drawTrees(ctx,info);drawAnimals(ctx,info);drawParent(ctx,info);});
 X.hooks.click.push((x,y,s)=>{if(s.inside)return false;
  if(s.scene===5){for(const i of D.pits.keys()){const [px,py]=pit(i);if(Math.abs(x-px)<12&&y>py-34&&y<py+4){openPit(i);return true;}}
   const a=se()!==3&&animalAt(x,y,5);if(a){openAnimal(a);return true;}
   if(inRect(x,y,BARN)){X.ring('粮仓 · 牲畜',[{id:'sf:ashop:0',label:'牲畜铺',icon:'farm'},{id:'sf:herd:0',label:se()===3?'棚里的牲畜':'看看牲畜',icon:'lens',off:S().animals.length?'':'还没有'},...(se()===3?[{id:'sf:feedall:0',label:'都喂草料',icon:'hay',off:S().animals.some(a=>a.fedDay!==today())?'':'都喂过了'}]:[])],{x:x-(s.camera||0),y:60});return true;}}
  return false;});
 Object.assign(X.hooks.pick,{plant:i=>treeShop(+i),fruit:i=>pickFruit(+i),treelook:i=>treeLook(+i),ashop:animalShop,herd:herdSheet,
  feedall:()=>{for(const a of S().animals)feed(a);showHint('都喂饱了');},pat:id=>pat(byId(id)),feed:id=>feed(byId(id)),collect:id=>collect(byId(id)),animal:id=>animalSheet(byId(id))});
 X.hooks.arrive.push(()=>{S();for(const a of S().animals){a.x=a.y=null;}const ready=S().animals.filter(a=>a.ready).length+Object.values(S().trees).filter(t=>t.ready).length;if(ready)setTimeout(()=>showHint(`有 ${ready} 样东西可以收了`),1600);});
 const oldCommand=command;command=function(act,item){
  if(act==='sf_tree'){if(item&&item.cost<=X.F.coins)plantTree(item);else if(item)showHint(`还差 ${X.coins(item.cost-X.F.coins)} 币`);return;}
  if(act==='sf_animal'){if(item&&!item.off&&item.cost<=X.F.coins)buy(item);else if(item)showHint(item.off||`还差 ${X.coins(item.cost-X.F.coins)} 币`);return;}
  if(act==='sf_give'){if(item)give(item);return;}
  return oldCommand(act,item);};
 // ================================================================ more chance cards on the farm (orchard, animals, 仓库)
 let n=9100;const M=(name,emo,pts=2,min=180)=>({name,emo,pts,min}),o=(text,say,mood,farm)=>({text,say,mood,...(farm?{farm}:{})});
 const c=(title,text,a,b,extra={})=>({n:++n,at:'spring_test',title,text,a,b,...extra});
 const CARDS2=[
  c('母鸡躲起来下蛋','鸡窝里少了一只鸡，草垛后面传来咯咯的叫声。',{label:'钻进草垛找找。',out:[o('草垛深处藏着一窝蛋，母鸡瞪着{名字}，像在说“被你发现了”。','原来藏这儿了',M('寻蛋成功','happy'),{item:{egg:1}}),o('找了半天只找到一只袜子，不知道是谁的。','这不是我的袜子',M('草垛里的袜子','dazed'))]},{label:'不打扰它。',out:[o('第二天母鸡大摇大摆回了窝，跟没事一样。','你开心就好',M('随它去','fine')),o('母鸡回来时特意绕到{名字}脚边蹭了蹭。','它记得我',M('鸡的谢意','happy'),{love:20})]},{farmIf:'chicken'}),
  c('想挠痒的羊','羊把脑袋抵在篱笆上蹭来蹭去，蹭得篱笆吱呀响。',{label:'帮它挠挠。',out:[o('挠到下巴的时候，它舒服得眼睛都眯上了。','是这儿吧',M('挠痒专家','happy'),{love:40}),o('它太享受了，整只羊压过来，差点把{名字}挤倒。','你也太重了',M('被羊压','embarrassed'),{love:20})]},{label:'给它找根木桩。',out:[o('木桩一立，它蹭得不亦乐乎，羊毛蹭下来一小团。','顺便收了点毛',M('木桩妙用','inspired'),{item:{wool:1}}),o('它对木桩没兴趣，还是来蹭{名字}的腿。','好吧好吧',M('还是蹭我','playful'),{love:20})]},{farmIf:'sheep'}),
  c('跟着走的牛','牛今天格外黏人，{名字}走到哪它就跟到哪，隔着篱笆一路慢慢走。',{label:'陪它走两圈。',out:[o('走完两圈，牛满足地哞了一声，回去吃草了。','散步完毕',M('遛牛','happy'),{love:40}),o('走着走着它停下来吃草，{名字}一个人走完了剩下一圈。','说好的陪我呢',M('被牛放鸽子','dazed'))]},{label:'拿把嫩草喂它。',out:[o('牛吃得很香，第二天的奶格外多。','多喝点',M('嫩草换牛奶','confident'),{ready:'cow'}),o('牛嫌弃地闻了闻，扭头吃自己的草去了。','挑食',M('牛很挑','embarrassed'))]},{farmIf:'cow'}),
  c('大风刮落了果子','夜里起了大风，早上果园地上滚着好几个果子。',{label:'捡起来收着。',out:[o('果子摔破了一点皮，但还挺甜，收进了仓库。','不浪费',M('捡果子','fine'),{fruitItem:1}),o('果子摔烂了，只能埋到树底下当肥料。','明年见',M('果子当肥料','sad'))]},{label:'去看看树有没有事。',out:[o('树没事，枝头剩下的果子看着更饱满了。','你挺住了',M('树没事','happy'),{fruit:true}),o('一根小枝被刮断了，{名字}找了根绳子把它绑好。','会长好的',M('给树包扎','focused'))]},{farmIf:'treeMature'}),
  c('来啄果子的鸟','一群灰喜鹊落在果树上，叽叽喳喳地挑果子吃。',{label:'挥手把它们赶走。',out:[o('喜鹊一哄而散，果子保住了，就是被啄了两个小口。','你们去别处吃',M('护果成功','confident')),o('赶走一群又来一群，最后被它们吃掉了好几个。','它们人多',M('喜鹊赢了','tense'),{fruitLose:true})]},{label:'分它们一点。',out:[o('{名字}摘了两个丢到地上，喜鹊吃完就飞走了，没再动树上的。','讲道理的鸟',M('和鸟谈判','playful')),o('鸟吃完地上的又飞回树上，嫌地上的不够甜。','得寸进尺',M('鸟的胃口','dazed'),{fruitLose:true})]},{farmIf:'treeReady'}),
  c('隔壁大爷教嫁接','隔壁大爷背着剪刀过来：“你这棵树，我教你嫁一枝，长得快。”',{label:'跟着学。',out:[o('大爷手很稳，一刀一缠，树好像精神了不少。','学会了一半',M('学嫁接','inspired'),{treeGrow:2}),o('{名字}缠的那一枝歪了，大爷笑着重新缠了一遍。','手笨',M('嫁接失败','embarrassed'),{treeGrow:1})]},{label:'谢谢，先不用了。',out:[o('大爷点点头，顺手帮忙松了松土。','谢谢大爷',M('大爷帮忙','happy'),{treeGrow:1}),o('大爷有点失望，背着剪刀走了。','下次一定',M('婉拒','tense'))]},{farmIf:'treeYoung'}),
  c('集市收鸡蛋','镇上饭馆的人在路口喊：“有鸡蛋吗？今天多给一个币！”',{label:'拿一篮去卖。',out:[o('饭馆的人数了数，给了比平时多一个币。','今天赚了',M('好价钱','confident'),{sellPremium:'egg'}),o('人家要的是大鸡蛋，嫌{名字}的小，最后还是按原价收了。','小也是鸡蛋',M('鸡蛋太小','embarrassed'),{sellPlain:'egg'})]},{label:'留着自己吃。',out:[o('晚上煎了两个荷包蛋，溏心的。','完美',M('溏心蛋','happy',3)),o('煎糊了一个，另一个还行。','五五开',M('煎蛋五五开','dazed'))]},{farmIf:'inv:egg'}),
  c('邻居想要一筐菜','隔壁大姐家来客人，隔着篱笆问能不能匀一筐菜，愿意多给点钱。',{label:'挑一筐好的给她。',out:[o('大姐多给了一个币，还说下次请{名字}吃饭。','邻里互助',M('邻居订单','confident'),{sellPremium:'crop'}),o('大姐说太多了，只要一半，按原价给了钱。','也行',M('半筐菜','fine'),{sellPlain:'crop'})]},{label:'说自己也不够吃。',out:[o('大姐笑着说没事，去别家问了。','不好意思啦',M('婉拒邻居','tense')),o('大姐走了，{名字}有点过意不去，晚上还是送了一筐过去。','给你送来了',M('还是送了','happy'),{giveCrop:true})]},{farmIf:'inv:crop'}),
  c('平板上的财经新闻','平板弹出一条新闻：“虚构基金今日或有波动。”',{label:'多看两眼。',out:[o('新闻说了半天，最后一句是“请理性投资”。','说了等于没说',M('财经废话','dazed')),o('看完觉得自己懂了，其实没懂。','嗯嗯嗯',M('似懂非懂','playful'))]},{label:'关掉，去干活。',out:[o('{名字}把平板一扣，拎起水壶出门了。','钱不如菜实在',M('脚踏实地','confident')),o('关掉前不小心点进了广告，退了三次才退出来。','烦死了',M('误点广告','angry'))]}),
  c('小羊长大了','小羊今天跑起来格外稳，个头也比刚来时大了一圈。',{label:'给它量量个头。',out:[o('它站着一动不动，好像知道自己在量身高。','长高了',M('量身高','happy'),{love:30}),o('刚把尺子拿出来它就跑了，追了三圈。','你别跑',M('追羊','playful'))]},{label:'拍张照片寄给妈妈。',out:[o('妈妈回了一串大拇指，还说“比你小时候长得快”。','这是夸谁呢',M('妈妈的点赞','happy')),o('照片糊了，只拍到一团白毛。','这是云还是羊',M('糊照','dazed'))]},{farmIf:'sheep'}),
 ];
 CARDS.push(...CARDS2);for(const cd of CARDS2)for(const k of ['a','b'])cd[k].out.forEach((oo,i)=>{if(oo.mood)ML[oo.id=`card${cd.n}${k}${i}`]={...oo.mood};});
 const hasInv=k=>k==='crop'?Object.keys(S().inv).some(x=>X.CROP[x]&&S().inv[x]):!!S().inv[k];
 X.fitsMore=cd=>{const f=cd.farmIf;if(!f||f==='crop')return true;S();
  if(['chicken','sheep','cow'].includes(f))return S().animals.some(a=>a.kind===f);
  const ts=Object.values(S().trees);if(f==='treeMature')return ts.some(ripeTree);if(f==='treeReady')return ts.some(t=>t.ready);if(f==='treeYoung')return ts.some(t=>!ripeTree(t));
  if(f.startsWith('inv:'))return hasInv(f.slice(4));return true;};
 X.applyMore=(f,title)=>{S();const kindOf=()=>card?.cd.farmIf,mine=S().animals.filter(a=>a.kind===kindOf()||!['chicken','sheep','cow'].includes(kindOf()));
  if(f.love&&mine.length){const a=pick(mine);a.love=Math.min(500,a.love+f.love);}
  if(f.ready){const a=S().animals.find(a=>a.kind===f.ready&&!a.ready);if(a)a.ready=ANIMAL[a.kind].product;}
  if(f.item)for(const [k,v]of Object.entries(f.item))X.addItem(k,v);
  const ts=Object.values(S().trees);
  if(f.fruit){const t=ts.find(t=>ripeTree(t)&&!t.ready);if(t)t.ready=true;}
  if(f.fruitItem){const t=ts.find(ripeTree);if(t)X.addItem(TREE[t.kind].fruit,f.fruitItem);}
  if(f.fruitLose){const t=ts.find(t=>t.ready);if(t)t.ready=false;}
  if(f.treeGrow){const t=ts.find(t=>!ripeTree(t));if(t){t.grown=Math.min(MATURE,t.grown+f.treeGrow);if(ripeTree(t))t.cycle=CYCLE-1;}}
  const crop=()=>Object.keys(S().inv).find(k=>X.CROP[k]&&S().inv[k]);
  if(f.sellPremium){const k=f.sellPremium==='crop'?crop():f.sellPremium;if(k&&S().inv[k]){sell(k,1);X.record('coin',`${title}多给的`,1);}}
  if(f.sellPlain){const k=f.sellPlain==='crop'?crop():f.sellPlain;if(k&&S().inv[k])sell(k,1);}
  if(f.giveCrop){const k=crop();if(k){S().inv[k]--;if(!S().inv[k])delete S().inv[k];}}};
 // ---------------------------------------------------------------- a few more farm calls
 SPRING_TALK.mom.push({title:'鸡下蛋了没',mood:{name:'妈妈问鸡',emo:'happy',pts:2,min:120},lines:['>鸡这两天下蛋了没？','下了，一篮。','>你摸摸它们，摸熟了蛋大。','真的假的？','>你姥姥说的，我也不知道真假。']},
  {title:'果树别乱剪',mood:{name:'护树',emo:'focused',pts:2,min:120},lines:['>果树你可别乱剪啊。','我没剪，就看了看。','>看可以。你爸去年剪秃了一棵。','后来呢？','>后来那棵长得最好。']});
 SPRING_TALK.dad.push({title:'牛认人',mood:{name:'牛认人',emo:'playful',pts:2,min:120},lines:['>你那头牛认你了没？','好像认了，看见我就叫。','>那是饿了。','……爸。','>开玩笑，它是想你了。']});
 SPRING_TALK.friend.push({title:'你家羊叫什么',mood:{name:'羊的名字',emo:'happy',pts:2,min:120},lines:['>听说你养羊了？叫什么名字？','棉花。','>好听！我能去摸摸吗？','能，它特别爱让人挠下巴。','>那我下周就去！']});
 for(const [key,pool]of Object.entries(SPRING_TALK))if(key!=='people')pool.forEach((t,i)=>{if(t.mood&&!t.id)ML[t.id=`spring_talk_${key}_${i}`]={...t.mood};});
 return {pcState,TREE,ANIMAL,give,sell,buy,parent,fundDay,treeDay,animalDay,planHelp,openPit,openAnimal,pat,feed,collect,pickFruit,AREA,pit,S};
})();
window.infeiFarm=infeiFarm;
