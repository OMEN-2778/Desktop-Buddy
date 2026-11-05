// 草帽湾 life (owner 2026-11-04/05), test page (make_season_game_test.py): her own beach stall, gathering in
// the sea and on the sand, customers who really walk up and buy, the guide 阿洛 on the first visit, the
// 蕾拉妮 / 卡伊诺 side stories and summer chance cards. Everything lasting lives in the save (springFarm F.bay,
// items in F.inv, coins through X.record): owner rule "everything the player changes is in the save".
//   Gathering: swimming past a 海草 clump picks one (each clump once a day); every dive has a 45% chance of a
//   小鱼 / 小虾米 / 小螃蟹; the giant clam gives a 珍珠 every 3 days; 2 coconuts lie under the palm each morning;
//   at low tide (6-9, 17-19) shells (and sometimes sea glass) wash up on the sand.
//   Stall: click the straw-hat stall to make goods from the 仓库 (made goods only sell at the stall, worth about
//   2-3x their materials); 10:00-18:00 customers come by (8 a day, 4 in rain), each buys one thing; the same thing
//   sells for 20% less each time that day; cold drinks +20% at noon. When she is away, they leave the coins in the
//   honesty jar.
const summerLife=(function(){
 if(typeof springFarm==='undefined'||typeof seasonMapTest==='undefined')return null;
 const X=springFarm.X,T=seasonMapTest,C=()=>T.state.summer,S=()=>X.F,ART=typeof SUMMER_LIFE_ART!=='undefined'?SUMMER_LIFE_ART:{};
 const inBay=()=>sim.place==='summer_test'&&C()&&!C().state.inside;
 const today=()=>Math.floor(sim.t/1440),hour=()=>sim.t%1440/60,night=()=>hour()>=20||hour()<5;
 const WL=116,SURF=WL+12,under=()=>C().state.y>SURF+3,me=()=>nameOf();
 // 市集 (owner 2026-11-05): her stall and 蕾拉妮's flowers moved into the market district left of the lodge (market x)
 const STALL_X=432,FLOWER_X=240,FRUIT_X=96,FISH_X=168,FOUNTAIN_X=336,HAT_X=508,CAFE_X=600,MW=684,FEET=104;
 const SHORE_X=1004,PALM_X=764,ARRIVE_X=232,inMarket=()=>inBay()&&!!C().state.market;
 const B=()=>{const F=S();F.bay??={};const b=F.bay;b.stock??=[];b.kinds??={};b.weed??={};b.q??={};b.q.lei??={step:0};b.q.kai??={step:0};
  if(b.day!==today()){b.day=today();b.sold=0;b.kinds={};b.weed={};b.coco=2;b.shells=null;b.nextAt=0;}return b;};
 const img=src=>{if(!src)return null;img.c??=new Map();if(!img.c.has(src)){const i=new Image();i.src=src;img.c.set(src,i);}return img.c.get(src);};
 const icon=k=>img(FARM_UI_ART.icons[k]);
 // ---------------------------------------------------------------- items and recipes
 Object.assign(X.ITEMS,{
  seaweed:{name:'一片海草',icon:'seaweed',price:.5,line:'游过海草丛时顺手采的，滑溜溜的。'},
  fish:{name:'一条小鱼',icon:'fish',price:.5,line:'下潜时一把捞上来的，还在扑腾。'},
  shrimp:{name:'一只小虾米',icon:'shrimp',price:.5,line:'透明的小虾，跳得比人还高。'},
  crab:{name:'一只小螃蟹',icon:'crab',price:1,line:'横着走的小家伙，钳子有点疼。'},
  pearl:{name:'一颗珍珠',icon:'pearl',price:4,line:'巨蚌里藏的，圆滚滚，会发光。'},
  shell:{name:'一个贝壳',icon:'shell',price:.5,line:'退潮时捡的，贴在耳边能听到海。'},
  seaglass:{name:'一块海玻璃',icon:'seaglass',price:1,line:'被海浪磨圆的玻璃，像一颗糖。'},
  coconut:{name:'一个椰子',icon:'coconut',price:.5,line:'椰子树下捡的，摇一摇有水声。'}});
 const FRUIT=['peach','pear','apple','orange','strawberry'],EGG=['egg_big','egg'],MILK=['milk_rich','milk'];
 const R=(name,icon,price,need,o={})=>({name,icon,price,need,...o});
 const RECIPES={
  coconut_water:R('鲜椰子水','coconut_water',1.5,[[['coconut'],1]],{cold:true}),
  seaweed_salad:R('凉拌海草','seaweed_salad',3,[[['seaweed'],2]]),
  fish_skewer:R('烤小鱼串','fish_skewer',3,[[['fish'],2]],{hot:true}),
  salted_shrimp:R('椒盐虾米','salted_shrimp',3,[[['shrimp'],2]],{hot:true}),
  spicy_crab:R('香辣小螃蟹','spicy_crab',4.5,[[['crab'],1],[['pepper'],1]],{hot:true}),
  seafood_stew:R('海鲜杂烩','seafood_stew',7.5,[[['fish'],1],[['shrimp'],1],[['crab'],1],[['seaweed'],1]],{hot:true}),
  egg_pancake:R('海苔鸡蛋饼','egg_pancake',3.5,[[EGG,1],[['seaweed'],1]],{hot:true}),
  juice:R('鲜榨果汁','juice',7,[[FRUIT,2]],{cold:true}),
  milk_smoothie:R('牛奶冰沙','milk_smoothie',7,[[MILK,1],[FRUIT,1]],{cold:true}),
  shave_ice:R('西瓜刨冰','shave_ice',4,[[['watermelon'],1]],{cold:true,makes:4}),
  shell_chime:R('贝壳风铃','shell_chime',7,[[['shell'],3],[['seaglass'],1]],{keep:true}),
  pearl_necklace:R('珍珠项链','pearl_necklace',14,[[['pearl'],1],[['shell'],3]],{keep:true})};
 const STOCK_MAX=6,nameOf2=k=>X.ITEMS[k]?.name.replace(/^一(片|条|只|颗|个|块|篮|团|桶)/,'')||(X.CROP?.[k]?.name)||k;
 const have=keys=>keys.reduce((a,k)=>a+(S().inv[k]||0),0);
 const canMake=r=>r.need.every(([keys,n])=>have(keys)>=n);
 function take(keys,n){for(const k of keys){while(n>0&&S().inv[k]){S().inv[k]--;if(!S().inv[k])delete S().inv[k];n--;}}}
 function make(k){const r=RECIPES[k],b=B();if(!canMake(r)||b.stock.length>=STOCK_MAX)return false;for(const [keys,n]of r.need)take(keys,n);
  for(let i=0;i<(r.makes||1)&&b.stock.length<STOCK_MAX;i++)b.stock.push(k);X.worked?.();return true;}
 function priceNow(k){const r=RECIPES[k],h=hour(),n=B().kinds[k]||0;let p=r.price*Math.max(.5,Math.pow(.8,n));if(r.cold&&h>=11&&h<15)p*=1.2;return Math.max(.5,Math.round(p*2)/2);}
 const fmt=v=>Number.isInteger(v)?String(v):v.toFixed(1);
 // ---------------------------------------------------------------- the stall sheet
 function openStall(){const b=B();if(!b.stallSeen){b.stallSeen=true;}
  const s=FarmUI.sheet('我的小摊 · 草帽湾','fu-stall'),c=socialContent(s),el=FarmUI.el;
  const head=el('div','fu-stall-head');head.append(FarmUI.coinPill(S().coins),el('p','fu-sub',`营业 10:00–18:00 · 今天来了 ${b.sold} 位客人 · 摊上 ${b.stock.length}/${STOCK_MAX} 份`));c.append(head);
  const shelf=el('div','fu-stall-shelf');
  if(!b.stock.length)shelf.append(el('p','fu-sub','摊上还是空的。从下面挑一样做好摆上去，客人就会来买。'));
  const counts={};for(const k of b.stock)counts[k]=(counts[k]||0)+1;
  for(const [k,n]of Object.entries(counts)){const r=RECIPES[k],row=el('div','fu-stall-item');row.append(FarmUI.icon(r.icon),el('span',null,`${r.name} ×${n}`),el('em',null,`现价 ${fmt(priceNow(k))} 币`));shelf.append(row);}
  c.append(el('h4',null,'摊上在卖'),shelf,el('h4',null,'做一份摆上摊'));
  const list=el('div','fu-stall-recipes');
  for(const [k,r]of Object.entries(RECIPES)){const row=el('div','fu-stall-recipe'+(canMake(r)?'':' fu-off'));
   const need=r.need.map(([keys,n])=>`${keys.length>1?(keys===FRUIT?'水果':keys===EGG?'鸡蛋':'牛奶'):nameOf2(keys[0])} ${Math.min(have(keys),n)}/${n}`).join(' · ');
   row.append(FarmUI.icon(r.icon));const t=el('div','fu-stall-text');t.append(el('b',null,r.name+(r.makes?` (一次 ${r.makes} 份)`:'')),el('small',null,need+` · 售价 ${fmt(r.price)}${r.cold?' · 冷饮':''}${r.keep?' · 纪念品':''}`));row.append(t);
   row.append(FarmUI.actions([{label:'做一份',off:b.stock.length>=STOCK_MAX?'摊上摆满了':canMake(r)?'':'材料不够',on:()=>{if(make(k)){speakBay(`做好了${r.name}，摆上摊～`);openStall();}}}]));list.append(row);}
  c.append(list,el('p','fu-sub','做好的东西只能在摊上卖，比单卖原料值钱得多。原料在海里、沙滩上都能找到，也可以带茵菲谷的水果、鸡蛋、牛奶、西瓜来。'));}
 // ---------------------------------------------------------------- gathering
 let wasUnder=false,lastT=0,pearlTold=false;
 const SHELL_SPOTS=[700,742,800,858,930,996];
 function gather(){const c=C(),s=c.state,b=B();
  if(under()&&!wasUnder){if(Math.random()<.45){const r=Math.random(),k=r<.45?'fish':r<.78?'shrimp':'crab';X.addItem(k);speakBay(pick({fish:['抓到一条小鱼！','小鱼溜进手心了'],shrimp:['一只小虾米跳进了手里','抓到小虾米～'],crab:['一只小螃蟹夹住了手指！','抓到小螃蟹，嘶——'],}[k]));}}
  wasUnder=under();
  if(under())for(const [i,k]of (c.kelp||[]).entries()){if(b.weed[i])continue;if(Math.abs(k.x-s.x)<10&&Math.abs((k.y-k.h/2)-s.y)<k.h/2+12){b.weed[i]=1;X.addItem('seaweed');showHint('采到一片海草');break;}}
  if(under()&&Math.hypot(s.x-1306,s.y-269)<26&&today()-(b.pearlDay??-99)>=3){b.pearlDay=today();X.addItem('pearl');speakBay('巨蚌张开了一条缝，里面有一颗珍珠！');}}
 function shells(){const b=B(),h=hour();if(!((h>=6&&h<9)||(h>=17&&h<19)))return [];
  if(!b.shells){b.shells=SHELL_SPOTS.filter((_,i)=>(today()*7+i*3)%5<3).map(x=>({x,glass:(today()+x)%4===0}));}return b.shells;}
 // ---------------------------------------------------------------- customers
 const custs=[];
 const BUY_LINES=[['老板，来一份{货}！','好嘞～'],['这个{货}看着好香','您慢用！'],['给我来个{货}，走路吃','拿好～'],['还有{货}吗？我要一份','最后几份了，给您'],['哇，{货}！小时候在海边吃过','那今天再吃一次'],['孩子吵着要{货}','小朋友拿好哦']];
 function spawn(){const b=B(),h=hour(),c=C();if(h<10||h>=18||!b.stock.length)return;const cap=(typeof weather!=='undefined'&&weather.kind!=='clear')?4:8;if(b.sold+custs.length>=cap)return;
  if(sim.t<(b.nextAt||0))return;b.nextAt=sim.t+35+Math.random()*35;
  const from=Math.random()<.5?STALL_X-150:STALL_X+160,n=makeNpc('adult',{x:from,feet:FEET,dir:from<STALL_X?1:-1,v:9});n.phase=Math.random()*6;n.shop={state:'in',t:0};custs.push(n);}
 function buy(n){const b=B();if(!b.stock.length){n.say='卖完啦？下次早点来';return;}const h=hour();
  let pool=b.stock.map((k,i)=>[k,i]),w=pool.map(([k])=>{const r=RECIPES[k];return 1+(r.cold&&h>=11&&h<15?2:0)+(r.hot&&h>=16?2:0)+(r.keep&&typeof weather!=='undefined'&&weather.kind!=='clear'?3:0);});
  let x=Math.random()*w.reduce((a,v)=>a+v,0),j=0;while(x>w[j]){x-=w[j];j++;}const [k,i]=pool[j],r=RECIPES[k],price=priceNow(k);
  b.stock.splice(i,1);b.kinds[k]=(b.kinds[k]||0)+1;b.sold++;X.record(r.icon,`小摊卖出${r.name}`,price);
  const s=C().state,near=!!s.market&&Math.abs(s.x-STALL_X)<46;const [ask,reply]=pick(BUY_LINES);n.say=ask.replace('{货}',r.name);
  if(near)setTimeout(()=>speakBay(reply),900);else if(!B().jarTold){B().jarTold=true;showHint('你不在的时候，客人把钱放进了小摊的诚信罐');}
  pops.push({x:STALL_X,y:56,t:0,text:'+'+fmt(price)});}
 const pops=[];
 function tickCusts(dt){for(const n of [...custs]){const sh=n.shop;sh.t+=dt;
  if(sh.state==='in'){const tx=STALL_X+(n.x<STALL_X?-12:12);n.dir=Math.sign(tx-n.x)||n.dir;n.x+=n.dir*n.v*dt*4;n.dist=(n.dist||0)+n.v*dt*4;if(Math.abs(tx-n.x)<2.5){sh.state='buy';sh.t=0;buy(n);n.sayUntil=realClock+2.6;}}
  else if(sh.state==='buy'){if(sh.t>2.8){sh.state='out';n.dir=n.x<STALL_X?-1:1;}}
  else{n.x+=n.dir*n.v*dt*3;n.dist=(n.dist||0)+n.v*dt*3;if(Math.abs(n.x-STALL_X)>190||n.x<0||n.x>MW)custs.splice(custs.indexOf(n),1);}}
  for(const p of pops)p.t+=dt;while(pops.length&&pops[0].t>1.6)pops.shift();}
 // ---------------------------------------------------------------- people of the bay
 function seeded(seed,f){const r=Math.random;let s=seed;Math.random=()=>(s=s*16807%2147483647)/2147483647;try{return f();}finally{Math.random=r;}}
 function person(name,gender,seed){let lk;for(let k=0;k<60;k++){lk=seeded(seed+k*977,npcLook);if(lk.gender===gender)break;}return {name,look:lk,ramps:doll.rampsOf(lk),cache:new Map(),dir:-1,x:0,feet:106};}
 const P={alo:person('阿洛','m',301),lei:person('蕾拉妮','f',433),kai:person('卡伊诺','m',577)};
 function pose(v,ms,o={}){const f={expr:o.expr||'neutral',look:0,bob:Math.floor(ms/600)%2,sway:0,wave:o.wave?Math.floor(ms/240)%2:null};if(Math.floor(ms/2600)%6===0)f.expr='blink';return npcCanvas(v,f,o.walk?'walk'+(Math.floor(ms/180)%2):'stand',false);}
 function where(){const q=B().q,h=hour(),out={};
  if(!B().met&&inBay())out.alo={x:ARRIVE_X};
  const fin=q.lei.step>=4&&q.kai.step>=5&&!q.done&&h>=16&&h<20;
  if(fin)out.leiShore={x:SHORE_X+26};else if(h>=8&&h<19)out.lei={x:FLOWER_X+2};
  if(night()&&(q.lei.step===1||q.kai.step===1))out.kai={x:1290,dive:true};
  else if(h>=16&&h<20)out.kai={x:SHORE_X,song:true};
  else if(h>=9&&h<16&&q.kai.step>=1&&q.kai.step<5)out.kai={x:SHORE_X-6};
  return out;}
 function mark(v){const q=B().q,h=hour();
  if(v===P.lei){if(q.lei.step===0||q.lei.step===3||q.kai.step===3)return q.lei.step===0?'!':'?';return null;}
  if(v===P.kai){if(q.kai.step===0&&B().met)return '!';if(q.kai.step===1&&have(['pearl']))return '?';if(q.kai.step===2&&h>=16&&h<20)return '?';if(q.kai.step===4)return '?';return null;}
  return null;}
 // ---------------------------------------------------------------- scenes (the game's own talk rows)
 const speech=springFarm.speech;let busy=false;STORY_HOLDS.push(()=>busy&&inBay());
 const say=(who,words)=>new Promise(res=>speech.show(who,words,{special:true,advance:res}));
 const ask=(who,words,opts)=>new Promise(res=>speech.show(who,words,{special:true,choices:opts.map((label,i)=>({label,on:()=>res(i)}))}));
 // walk there, but never hang: the map's own wandering can replace the target (and drop its callback)
 const walk=x=>new Promise(res=>{speech.hide();let done=false;const end=()=>{if(!done){done=true;clearInterval(t);res();}};C().goTo(x,'walk',0,end);const t0=performance.now(),t=setInterval(()=>{const s=C().state;if(Math.abs(s.x-x)<4)end();else if(performance.now()-t0>8000){s.x=x;end();}else if(!s.target)C().goTo(x,'walk',0,end);},200);});
 function speakBay(t){try{speak(t,true);}catch(e){showHint(t);}}
 async function scene(fn){if(busy)return;busy=true;closeRing();try{await fn();}finally{speech.hide();busy=false;}}
 const ML_=(id,name,emo,pts=2)=>{ML['bay_'+id]={name,emo,pts,min:240};return 'bay_'+id;};
 const MOOD={hello:ML_('hello','草帽湾的花环','happy'),first:ML_('first','开张大吉','confident',3),lei:ML_('lei','海边的心事','sad',1),song:ML_('song','没听过的歌','dazed'),
  pearl:ML_('pearl','帮了个大忙','happy'),flower:ML_('flower','插花小助手','confident'),propose:ML_('propose','海边的求婚','happy',4),oops:ML_('oops','好心办坏事','embarrassed',2),wish:ML_('wish','喷泉许愿','happy',1)};
 const arrive=()=>scene(async()=>{const b=B(),v=P.alo;await walk(ARRIVE_X-18);C().state.facing=1;
  await say('阿洛','Aloha～欢迎来到草帽湾！我是导游阿洛。');
  await say('阿洛','这儿只有三条规矩：慢慢走、多吃水果、帽子要戴好——这边的风专偷帽子。');
  await say('阿洛','海边的花，插左耳是“有人了”，插右耳是“还单着”，可别插错了。');
  await say('阿洛','对了，旅舍再往左是市集，那儿有个插着草帽小旗的小摊，是给你留的。做点好吃的摆上去，客人自己会来。');
  await say(me(),'我的小摊？好耶！');
  b.met=true;addMood(MOOD.hello);log('到了草帽湾。导游阿洛给我挂了一串花环，还说沙滩上有个小摊是我的。');
  showHint('往左走就是市集，插着草帽小旗的就是你的小摊');setTimeout(async()=>{await walk(50);if(!C().state.market)C().beginDoor('market');},0);});
 // ---- 蕾拉妮 ·《他耳边的花》 and 卡伊诺 ·《一串花环》
 async function leiTalk(){const q=B().q;
  if(q.lei.step===0)return scene(async()=>{await say('蕾拉妮','嘘——过来一下，帮我个忙好不好？');
   await say('蕾拉妮','我男朋友卡伊诺，最近怪怪的。问他去哪，他就支支吾吾。');
   await say('蕾拉妮','你帮我盯着他一点？就……看看他晚上都去干嘛。');
   if(await ask('蕾拉妮','你会帮我的吧？',['好，我帮你看看','这样不太好吧……'])===1){await say('蕾拉妮','我知道……可我真的睡不着。拜托啦。');}
   q.lei.step=1;log('蕾拉妮拜托我看看卡伊诺晚上都去哪。');showHint('晚上去海边看看卡伊诺');});
  if(q.lei.step===3)return scene(async()=>{await say(me(),'他在码头弹了一首歌，我没听过。');
   await say('蕾拉妮','……什么样的歌？');await say(me(),'很慢，很温柔，像是写给谁的。');
   await say('蕾拉妮','我们在一起三年了，他从来没给我写过歌。');await say('蕾拉妮','那首歌……不是写给我的。');
   q.lei.step=4;addMood(MOOD.lei);log('蕾拉妮听说了那首歌，眼眶红了。');if(q.kai.step>=5)showHint('傍晚去海边看看');});
  if(q.kai.step===3)return scene(async()=>{await say(me(),'有人托我来订一串花环，要全岛最好看的那种。');
   await say('蕾拉妮','最好看的？送给谁啊？');await say(me(),'他说……是给一位很重要的人。');
   await say('蕾拉妮','很重要的人……好，我给她编一串最好看的。');await say('蕾拉妮','（一边编一边小声）编得好看有什么用，又不是给我的。');
   q.kai.step=4;log('替卡伊诺在蕾拉妮那里订了一串花环。蕾拉妮编得很用心，就是脸色不太好。');showHint('把花环带给卡伊诺');});
  return scene(async()=>{await say('蕾拉妮',pick(['今天的花开得真好，要不要插一朵？','鸡蛋花要早上摘，香味才足。','你的小摊生意怎么样？我这儿天天有人来买花环。']));});}
 async function kaiTalk(){const q=B().q,h=hour();
  if(q.kai.step===0)return scene(async()=>{await say('卡伊诺','……那个，你好。能不能……帮我一个忙？');
   await say('卡伊诺','别告诉任何人。尤其是蕾拉妮。');await say('卡伊诺','我需要一颗珍珠。我找了好几个晚上，巨蚌就是不张嘴。');
   await say(me(),'巨蚌？我下海的时候去看看。');q.kai.step=1;log('卡伊诺偷偷拜托我找一颗珍珠，还不让告诉蕾拉妮。');showHint('去海底的巨蚌那里找珍珠');});
  if(q.kai.step===1){if(!have(['pearl']))return scene(async()=>{await say('卡伊诺','珍珠……找到了吗？巨蚌在珊瑚花园往下一点。');});
   return scene(async()=>{await say(me(),'给，巨蚌里的珍珠。');take(['pearl'],1);await say('卡伊诺','（捧着看了好久）……谢谢。真的谢谢。');
    await say('卡伊诺','原来不是我找的地方不对，是它不肯给我。');q.kai.step=2;addMood(MOOD.pearl);log('把珍珠给了卡伊诺。他捧着看了好久。');showHint('傍晚去海边找卡伊诺');});}
  if(q.kai.step===2){if(h<16||h>=20)return scene(async()=>{await say('卡伊诺','傍晚……傍晚再来找我吧，我想请你听个东西。');});
   return scene(async()=>{await say('卡伊诺','我写了一首歌。一紧张就弹错，你……帮我听听？');
    await say('卡伊诺','♪ ……海风把帽子吹远，我把心放在你的花环里……');await say(me(),'好好听！');await say('卡伊诺','真的吗？那我就……再练一百遍。');
    if(q.lei.step===2||q.lei.step===1){q.lei.step=3;}q.kai.step=3;addMood(MOOD.song);log('卡伊诺给我弹了他写的歌，很好听。');
    await say('卡伊诺','还有……我想要一串全岛最好看的花环。可全岛编得最好的就是她……你能帮我去订吗？');showHint('去蕾拉妮的花摊订一串花环');});}
  if(q.kai.step===4)return scene(async()=>{await say(me(),'花环取来了，蕾拉妮编的。');
   await say('卡伊诺','（把珍珠穿在花环正中间）好了。');await say('卡伊诺','还有最后一件事……我手抖，插不好花。你帮我插一下吧，插在左边。');
   await say(me(),'好！');log(`${me()}面对着卡伊诺，认认真真把花插在了自己的左手边。`);
   await say('卡伊诺','谢谢！这下她一定会懂的。');q.kai.step=5;addMood(MOOD.flower);showHint(q.lei.step>=4?'傍晚去海边看看':'蕾拉妮那边，好像也有心事');});
  if(night()&&(q.lei.step===1))return;
  if(h>=16&&h<20)return scene(async()=>{await say('卡伊诺',pick(['♪ ……（他弹着尤克里里，冲你点了点头）','傍晚的风最舒服了。','今天的浪不大，适合发呆。']));});
  return scene(async()=>{await say('卡伊诺',pick(['……你好。','今天出海早，鱼都还没醒。','嗯。']));});}
 // finale: both stories done -> the next evening on the shore
 const finale=()=>scene(async()=>{const q=B().q;await walk(SHORE_X-30);
  await say('卡伊诺','（单膝跪下，拨了一下琴弦）蕾拉妮。');await say('卡伊诺','♪ ……海风把帽子吹远，我把心放在你的花环里……');
  await say('卡伊诺','这串花环，是全岛最会编花环的人编的。我想……以后每年都请她给我编。');
  await say('蕾拉妮','（愣住）……这、这是我编的那串？中间这颗珍珠……');
  await say('蕾拉妮','那你右耳的花是什么意思？！');await say('卡伊诺','右……右耳？我明明让她插在左边的——');
  await say(me(),'……我是插在我的左边啊。');await say('蕾拉妮','（愣了一下，笑出眼泪）你们两个笨蛋！');
  log('蕾拉妮伸手，把卡伊诺耳边的花挪到了左边。原来一切都是个误会——还是我造成的。');
  q.done=true;q.doneDay=today();addMood(MOOD.propose);addMood(MOOD.oops);
  await say('蕾拉妮','谢谢你。下次来，婚礼花环我送你一串。');showHint('支线完成：他耳边的花 · 一串花环');});
 // ---------------------------------------------------------------- drawing
 let clock=0;
 function drawPerson(ctx,v,x,y,o={}){const pic=pose(v,realClock*1000,o);ctx.drawImage(pic,Math.round(x-10),Math.round(y-27));
  const m=mark(v);if(m){const by=Math.round(y-36+Math.sin(realClock*4)*1.5);ctx.fillStyle='#2b2236';ctx.fillRect(x-3,by-1,7,9);ctx.fillStyle='#f6c45a';ctx.fillRect(x-2,by,5,7);ctx.fillStyle='#2b2236';if(m==='!'){ctx.fillRect(x,by+1,1,3);ctx.fillRect(x,by+5,1,1);}else{ctx.fillRect(x-1,by+1,3,1);ctx.fillRect(x+1,by+2,1,1);ctx.fillRect(x,by+3,1,1);ctx.fillRect(x,by+5,1,1);}}}
 function tick(){const now=realClock,dt=Math.min(.1,now-(clock||now));clock=now;const c=C(),s=c.state,b=B();
  if(busy)return;gather();spawn();tickCusts(dt);tickWalkers(dt);if(!b.met&&!s.target&&!s.market&&!storyLocked()&&!window.__noBayGuide)arrive();   // __noBayGuide: automated checks only
  const q=b.q;if(!s.market&&q.lei.step>=4&&q.kai.step>=5&&!q.done&&hour()>=16&&hour()<20&&Math.abs(s.x-SHORE_X)<120&&!storyLocked())finale();
  if(!s.market&&q.lei.step===1&&night()&&s.x>990&&s.x<1330&&!storyLocked())scene(async()=>{await say(me(),'（岸边放着一双拖鞋……水里有人？）');await say(me(),'是卡伊诺！他一个人潜进了夜里的海，在巨蚌那一带找什么。');q.lei.step=2;log('夜里看见卡伊诺一个人下海，在巨蚌那一带找东西。');showHint('傍晚去海边听听卡伊诺弹琴');});}
 function arrow(ctx,x,y0,now){const ay=Math.round(y0+Math.sin(now*5)*2);ctx.fillStyle='#2b2236';ctx.fillRect(x-4,ay-1,9,6);ctx.fillRect(x-2,ay+5,5,2);ctx.fillRect(x-1,ay+7,3,1);ctx.fillStyle='#f6c45a';ctx.fillRect(x-3,ay,7,4);ctx.fillRect(x-1,ay+4,3,2);}
 function pop(ctx){for(const p of pops){ctx.globalAlpha=Math.max(0,1-p.t/1.6);ctx.font='bold 8px sans-serif';ctx.fillStyle='#2b2236';ctx.fillText(p.text,p.x-6+1,p.y-p.t*10+1);ctx.fillStyle='#f6c45a';ctx.fillText(p.text,p.x-6,p.y-p.t*10);ctx.globalAlpha=1;}}
 /* mid-ground sun (owner 2026-11-05): soft slanted shafts that drift and breathe, plus dappled glints on the town */
 const RAYS=[[0,14,.9],[83,8,.6],[150,20,1],[231,10,.7],[302,16,.85],[389,9,.55],[455,18,.9]];
 function sunRays(ctx,cx,now){if(typeof weather!=='undefined'&&weather.kind!=='clear')return;const h=hour();const day=Math.max(0,Math.min(1,(h-7)/2,(19-h)/2));if(day<=0)return;
  ctx.save();ctx.globalCompositeOperation='screen';
  for(const [i,[x0,w,k]]of RAYS.entries()){const a=day*k*(.24+.12*Math.sin(now*.35+i*1.9))*(.75+.25*Math.sin(now*.11+i));if(a<=.01)continue;
   const x=((x0-cx*.6+Math.sin(now*.07+i)*6)%520+520)%520-80,g=ctx.createLinearGradient(0,0,0,92);
   g.addColorStop(0,`rgba(255,244,206,${a})`);g.addColorStop(.6,`rgba(255,240,200,${a*.55})`);g.addColorStop(1,'rgba(255,240,200,0)');
   ctx.fillStyle=g;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x+w,0);ctx.lineTo(x+w+44+w*.6,92);ctx.lineTo(x+40,92);ctx.closePath();ctx.fill();}
  for(let i=0;i<14;i++){const t=now*.2+i*2.3,a=day*Math.max(0,Math.sin(t))*.35;if(a<.03)continue;const x=((i*61+Math.sin(t*.5)*8-cx*.6)%560+560)%560-60,y=58+(i*17)%22;
   ctx.fillStyle=`rgba(255,248,220,${a})`;ctx.fillRect(Math.round(x),y,3,1);ctx.fillRect(Math.round(x)+1,y-1,1,1);}
  ctx.restore();}
 /* customers talk in the same DOM pill as every other NPC (.npcsay, people.js / the city), owner 2026-11-05 */
 const pills=new Map();
 function sayPills(list,camX){const scale=Number(view.style.width.replace('px',''))/342||view.width/342;
  for(const [n,el]of pills)if(!list.includes(n)||!inMarket()){el.remove();pills.delete(n);}
  if(!inMarket())return;
  for(const n of list){let el=pills.get(n);if(!el){el=document.createElement('div');el.className='npcsay';widget.append(el);pills.set(n,el);}
   if(el.textContent!==n.say)el.textContent=n.say;const half=el.offsetWidth/2+4;el.style.left=Math.max(half,Math.min(342*scale-half,(n.x-camX)*scale))+'px';el.style.top=((FEET-30)*scale)+'px';}}
 setInterval(()=>{if(!inMarket()&&pills.size)sayPills([],0);},500);
 function bubble(ctx,x,y,text){ctx.font='7px sans-serif';const tw=Math.min(116,ctx.measureText(text).width+8);const bx=Math.round(x-tw/2);ctx.fillStyle='rgba(247,241,226,.96)';ctx.fillRect(bx,y,tw,11);ctx.fillStyle='#4a3b30';ctx.fillText(text,bx+4,y+8,tw-8);}
 // ---- the bay (beach and sea): coconuts, shells, seaweed glints, 阿洛, 卡伊诺, the finale on the shore
 function draw(ctx,info){if(!inBay())return;tick();const now=realClock,c=C(),s=c.state,b=B();
  if(b.met&&!b.stallSeen&&s.x<260&&!s.inside)arrow(ctx,24,72,now);   // which way the market is
  for(let i=0;i<(b.coco||0);i++){const ic=icon('coconut');if(ic?.complete)ctx.drawImage(ic,0,0,16,16,PALM_X+i*7,100,8,8);}
  for(const sh of shells()){if(sh.got)continue;const ic=icon(sh.glass?'seaglass':'shell');if(ic?.complete)ctx.drawImage(ic,0,0,16,16,sh.x-3,101,7,7);if(Math.sin(now*3+sh.x)>.6){ctx.fillStyle='#fffbe6';ctx.fillRect(sh.x,98,1,3);ctx.fillRect(sh.x-1,99,3,1);}}
  if(under())for(const [i,k]of (c.kelp||[]).entries())if(!b.weed[i]&&Math.sin(now*2.5+i)>.7){ctx.fillStyle='#e9fbe9';ctx.fillRect(k.x,k.y-k.h/2,1,3);ctx.fillRect(k.x-1,k.y-k.h/2+1,3,1);}
  const w=where();
  if(w.alo)drawPerson(ctx,P.alo,w.alo.x,c.gr(w.alo.x),{wave:true});
  if(w.leiShore)drawPerson(ctx,P.lei,w.leiShore.x,c.gr(w.leiShore.x));
  if(w.kai){if(w.kai.dive){const t=s.time,x=w.kai.x+Math.sin(t*.4)*30,y=230+Math.sin(t*.7)*18,head=pose(P.kai,now*1000);c.fx.swimmer(ctx,{head,skinRamp:P.kai.ramps.skin,sheet:c.personSheet(P.kai.look.gender,'wetsuit'),x,y,time:t,facing:Math.cos(t*.4)>0?1:-1,diving:true,moving:true,wetsuit:true,waterline:WL,phase:1});}
   else{drawPerson(ctx,P.kai,w.kai.x,c.gr(w.kai.x));if(w.kai.song&&Math.floor(now*1.5)%2){ctx.fillStyle='#2b2236';const nx=w.kai.x+8,ny=c.gr(w.kai.x)-34-(now*6%6);ctx.fillRect(nx,ny,1,4);ctx.fillRect(nx+1,ny,2,1);ctx.fillRect(nx-1,ny+3,2,2);}}}}
 // ---- 市集: vendors behind their stalls, 蕾拉妮, her stall, the fountain, the café, strollers and customers
 const V={fruit:person('果果阿姨','f',611),fish:person('老渔夫','m',709),hat:person('草帽爷爷','m',811),cafe:person('咖啡店的米娅','f',919)};
 V.hat.look={...V.hat.look,hair:V.hat.look.hair};
 const walkers=[];
 function tickWalkers(dt){if(!inMarket())return;const h=hour();const want=h>=8&&h<21?(typeof weather!=='undefined'&&weather.kind!=='clear'?1:3):0;
  while(walkers.length<want){const n=makeNpc('adult',{x:60+Math.random()*560,feet:FEET,dir:Math.random()<.5?-1:1,v:5});n.home=n.x;walkers.push(n);}
  while(walkers.length>want)walkers.pop();
  for(const n of walkers){n.x+=n.dir*n.v*dt*3;n.dist=(n.dist||0)+n.v*dt*3;if(Math.abs(n.x-n.home)>90||n.x<50||n.x>MW-30)n.dir*=-1;}}
 const sprite=k=>img(ART[k]);
 function put(ctx,k,cx,w,h){const im=sprite(k);if(im?.complete)ctx.drawImage(im,Math.round(cx-im.width/2),FEET+1-im.height);}
 function drawNpc(ctx,n){const [f,p]=npcFrame(n);const pic=npcCanvas(n,f,p,false);ctx.drawImage(pic,Math.round(n.x-10),Math.round(FEET-27));}
 function marketDraw(ctx,info){tick();const now=realClock,c=C(),s=c.state,b=B(),cx=info.camX||0,h=hour(),open=h>=7&&h<20;
  /* layers (owner 2026-11-05): sky still, hazy far town at 0.3, mid town at 0.6, street at 1 */for(const [k,f,veil]of [['msky',0,0],['mfar',.3,.5],['mmid',.6,.22],['mbg',1,0]]){if(k==='mbg')sunRays(ctx,cx,now);const im=sprite(k);if(im?.complete)ctx.drawImage(im,-Math.round(cx*f),0);if(veil){ctx.fillStyle=`rgba(236,245,252,${veil})`;ctx.fillRect(0,0,342,118);}}/* a pale blue veil over each distant layer: the further, the lighter (owner) */
  ctx.save();ctx.translate(-Math.round(cx),0);
  // vendors stand behind their counters
  if(open){for(const [v,x]of [[V.fruit,FRUIT_X],[V.fish,FISH_X],[V.hat,HAT_X]])drawPerson(ctx,v,x+4,FEET-9);drawPerson(ctx,V.cafe,CAFE_X-30,FEET);}
  if(where().lei)drawPerson(ctx,P.lei,FLOWER_X+3,FEET-9);
  put(ctx,'fruit',FRUIT_X);put(ctx,'fish',FISH_X);put(ctx,'hat',HAT_X);put(ctx,'cafe',CAFE_X);
  const fl=sprite('flower');if(fl?.complete)ctx.drawImage(fl,FLOWER_X-25,FEET+1-fl.height);
  const fo=sprite('fountain');if(fo?.complete){ctx.drawImage(fo,FOUNTAIN_X-35,FEET+1-fo.height);ctx.fillStyle='rgba(205,236,248,.85)';
   for(let k=0;k<10;k++){const t=(now*1.6+k/10)%1,dx=(k%2?1:-1)*(2+t*9),dy=-34+t*t*24+t*-6;ctx.fillRect(Math.round(FOUNTAIN_X+dx),Math.round(FEET+dy),1,1);}}
  const st=sprite('stall');if(st?.complete)ctx.drawImage(st,STALL_X-26,FEET+1-st.height);
  [...new Set(b.stock)].slice(0,3).forEach((k,i)=>{const ic=icon(RECIPES[k].icon);if(ic?.complete)ctx.drawImage(ic,0,0,16,16,STALL_X-19+i*13,FEET-17-10,10,10);});
  if(b.met&&!b.stallSeen)arrow(ctx,STALL_X,40,now);
  for(const n of walkers)drawNpc(ctx,n);
  for(const n of custs){const [f,p]=npcFrame(n);const pic=npcCanvas(n,f,n.shop.state==='buy'?'stand':p,false);ctx.drawImage(pic,Math.round(n.x-10),Math.round(FEET-27));}
  info.hero();
  sayPills(custs.filter(n=>n.shop.state==='buy'&&n.say),cx);
  pop(ctx);ctx.restore();}
 // shops (buying costs about twice the selling price, so only cooking at the stall turns a profit)
 const SHOPS={
  fruit:{title:'果果阿姨的水果摊',lines:['挑一个吧，今天的都甜！','西瓜是早上刚到的。'],goods:[['watermelon',10],['peach',3],['orange',3],['apple',3]]},
  fish:{title:'老渔夫的鱼摊',lines:['早上刚捞的，新鲜着呢。','小螃蟹别拿手指逗它。'],goods:[['fish',1],['shrimp',1],['crab',2]]},
  hat:{title:'草帽爷爷的草帽铺',lines:['在草帽湾，没有草帽可不行。','这顶编了三天。'],goods:[['strawhat',8],['shell',1],['seaglass',2]]}};
 X.ITEMS.strawhat={name:'一顶草帽',icon:'hat',price:4,line:'草帽爷爷编的，戴上就是草帽湾的人了。'};
 function openShop(id){const sh=SHOPS[id];speakBay(pick(sh.lines));
  FarmUI.shop('bay_shop_'+id,sh.title+' · 买点什么',S().coins,[{group:'今天有',note:'丢丢币买',items:sh.goods.map(([k,cost])=>({name:X.ITEMS[k]?.name||X.CROP?.[k]?.name||k,icon:k==='strawhat'?'hat':k,pic:FARM_UI_ART.icons[k==='strawhat'?'hat':k],cost,key:k,line:X.ITEMS[k]?.line||''}))}]);}
 const oldCommand=command;command=function(act,item){
  if(typeof act==='string'&&act.startsWith('bay_shop_')){if(item&&item.cost<=S().coins){X.record('coin','在市集买了'+item.name.replace(/^一(片|条|只|颗|个|块|篮|团|桶|顶)/,''),-item.cost);X.addItem(item.key);speakBay('买到了'+item.name.replace(/^一(片|条|只|颗|个|块|篮|团|桶|顶)/,''));}else if(item)showHint('丢丢币不够');return;}
  return oldCommand(act,item);};
 function openCafe(){const s=FarmUI.sheet('咖啡店的米娅 · 露天座','fu-stall'),c=socialContent(s),el=FarmUI.el;
  c.append(el('p','fu-sub','米娅：坐下歇歇吧，今天的海风刚刚好。'),FarmUI.coinPill(S().coins));
  const opts=[['来一杯冰咖啡',2,{fun:18,energy:10},'冰咖啡下肚，整个人都醒了'],['来一份海鲜饭',4,{hunger:45},'海鲜饭的锅巴最香'],['坐着和邻桌聊天',0,{social:30},'邻桌的阿婆讲了一下午她年轻时的事']];
  c.append(FarmUI.actions(opts.map(([label,cost,fx,line])=>({label:label+(cost?` (${cost} 币)`:''),off:cost>S().coins?'丢丢币不够':'',on:()=>{if(cost)X.record('coin','咖啡座：'+label.slice(2),-cost);for(const [k,v]of Object.entries(fx))sim.needs[k]=Math.min(100,sim.needs[k]+v);closeSocialSheet();speakBay(line);}}))));}
 function wish(){if(S().coins<1)return showHint('身上没有丢丢币可以许愿');X.record('coin','往喷泉里扔了一枚丢丢币',-1);
  speakBay(pick(['许了个愿：明天也是晴天','许了个愿：小摊天天卖光','许了个愿……不能说出来','硬币沉下去的时候闪了一下']));addMood(MOOD.wish);}
 function marketPick(x,y){if(busy)return true;const c=C(),hit=(px,w=24)=>Math.abs(x-px)<w&&y>FEET-46&&y<FEET+4;
  if(where().lei&&hit(FLOWER_X,26)){c.goTo(FLOWER_X-30,'walk',0,()=>{c.state.facing=1;leiTalk();});return true;}
  if(hit(STALL_X,28)){c.goTo(STALL_X+30,'walk',0,()=>{c.state.facing=-1;openStall();});return true;}
  for(const [id,px]of [['fruit',FRUIT_X],['fish',FISH_X],['hat',HAT_X]])if(hit(px)){c.goTo(px+30,'walk',0,()=>{c.state.facing=-1;if(hour()>=7&&hour()<20)openShop(id);else showHint('摊子收了，明天早上再来');});return true;}
  if(Math.abs(x-CAFE_X)<48&&y>FEET-50){c.goTo(CAFE_X-44,'walk',0,()=>{c.state.facing=1;openCafe();});return true;}
  if(Math.abs(x-FOUNTAIN_X)<34&&y>FEET-44){c.goTo(FOUNTAIN_X-38,'walk',0,()=>{c.state.facing=1;wish();});return true;}
  return false;}
 (function register(){const c=C();if(c?.setMarket){c.setMarket({w:MW,draw:marketDraw,pick:marketPick});return;}setTimeout(register,300);})();
 // ---------------------------------------------------------------- clicks (world coordinates)
 function click(x,y){if(!inBay()||busy||C().state.market)return false;const c=C(),s=c.state,b=B(),g=c.gr(x),w=where();
  const hitP=(px,py)=>Math.abs(x-px)<10&&y>py-30&&y<py+3;
  if(w.alo&&hitP(w.alo.x,c.gr(w.alo.x))){arrive();return true;}
  if(w.kai&&!w.kai.dive&&hitP(w.kai.x,c.gr(w.kai.x))){c.goTo(w.kai.x-16,'walk',0,()=>{c.state.facing=1;kaiTalk();});return true;}
  if((b.coco||0)>0&&x>PALM_X-3&&x<PALM_X+16&&y>94&&y<110){c.goTo(PALM_X+4,'walk',0,()=>{const n=B().coco||0;if(n){X.addItem('coconut',n);B().coco=0;speakBay(`捡到${n}个椰子`);}});return true;}
  for(const sh of shells())if(!sh.got&&Math.abs(x-sh.x)<7&&y>94&&y<110){c.goTo(sh.x,'walk',0,()=>{if(sh.got)return;sh.got=true;X.addItem(sh.glass?'seaglass':'shell');speakBay(sh.glass?'捡到一块海玻璃，像颗糖':'捡到一个贝壳');});return true;}
  return false;}
 // ---------------------------------------------------------------- summer chance cards (small coin effects)
 const BAY_CARDS=(()=>{let n=9500;const M=(name,emo,pts=2,min=180)=>({name,emo,pts,min});const o=(text,say,mood,bay)=>({text,say,mood,...(bay?{bay}:{})});
  const c=(title,text,a,b2,extra={})=>({n:++n,at:'summer_test',title,text,a,b:b2,...extra});return [
  c('海鸥小偷','一只海鸥落在小摊上，盯着摊上的吃的，眼神很不善良。',{label:'挥手赶走它。',out:[o('海鸥扑腾着飞走了，顺走一张餐巾纸。','还好不是吃的',M('赶跑海鸥','confident')),o('它叼起一份吃的就跑，边飞边嚼。','它付钱了吗',M('被海鸥打劫','dazed'),{loseStock:1})]},{label:'丢点面包屑给它。',out:[o('海鸥吃完，冲{名字}点了点头，像在说下次还来。','交了个朋友',M('海鸥朋友','happy')),o('一只变成了七只。摊位前全是海鸥。','这下热闹了',M('海鸥开会','playful'))]}),
  c('游客问路','一个背着大包的游客满头大汗，问哪里能买到冰的东西。',{label:'指指自己的小摊。',out:[o('游客一口气买了两份，还多给了一个币当小费。','谢谢惠顾',M('意外的小费','happy'),{coins:1}),o('游客说太贵了，扭头去找便利店。岛上没有便利店。','会回来的',M('嫌贵的游客','fine'))]},{label:'告诉他去旅舍。',out:[o('游客走了。过了一会儿，阿洛笑着来说：“谢谢你帮我介绍客人。”','互相帮忙',M('热心肠','happy')),o('游客走错了路，走进了更衣室。','方向感很差',M('指错路','embarrassed'))]}),
  c('沙滩上的硬币','退潮的沙子里，有什么东西在闪光。',{label:'蹲下挖一挖。',out:[o('一枚旧硬币，擦一擦还能用。','海边捡钱',M('海边捡钱','happy'),{coins:1}),o('挖出来是个瓶盖。','也算收藏',M('瓶盖收藏家','playful'))]},{label:'不管它。',out:[o('走了两步回头看，被一个小孩捡走了，小孩开心得跳起来。','值了',M('让给小孩','fine')),o('后来才知道是块海玻璃。','算了',M('错过海玻璃','dazed'))]}),
  c('大风来了','天边一阵风卷过来，沙滩上的伞都歪了。',{label:'赶紧按住小摊的顶棚。',out:[o('顶棚保住了，只是草帽小旗被吹到了礁石上。','旗子我会去找的',M('护摊成功','confident')),o('顶棚保住了，自己的帽子飞了。','这边的风果然专偷帽子',M('帽子被偷','dazed'))]},{label:'躲到椰子树后面。',out:[o('风过去了。摊上的东西都在，就是沾了点沙。','吹吹就好',M('躲风','fine')),o('风把一个椰子吹了下来，正好滚到脚边。','风的礼物',M('天降椰子','happy'),{item:{coconut:1}})]}),
  c('卖完了','一个小孩跑过来，攥着皱巴巴的零钱，问还有没有冰的。',{label:'给他做一杯椰子水。',out:[o('小孩接过去，小口小口喝，说是这辈子喝过最好喝的。','这辈子还长呢',M('最好喝的椰子水','happy')),o('小孩喝完，把零钱塞进诚信罐，还鞠了一躬。','好有礼貌',M('小小顾客','happy'),{coins:1})]},{label:'说明天早点来。',out:[o('小孩点点头，第二天一早就站在摊前。','守信的小家伙',M('第一位客人','happy')),o('小孩撇撇嘴走了。','下次多做点',M('没东西卖','sad'))]}),
  c('涨潮了','潮水比平时涨得快，浪花已经快打到小摊的脚了。',{label:'把小摊往后挪一挪。',out:[o('挪完正好，浪就停在原来摊脚的位置。','刚刚好',M('看准潮水','focused')),o('挪的时候绊了一跤，摔进沙子里。','满嘴沙',M('摔进沙里','embarrassed'))]},{label:'看着浪打过来。',out:[o('浪舔了一下摊脚就退了，留下一个贝壳。','海浪送的',M('海浪的礼物','happy'),{item:{shell:1}}),o('浪把一份摆在边上的吃的冲走了。','喂鱼了',M('喂鱼','sad'),{loseStock:1})]}),
  c('网红打卡','一个举着手机的人在小摊前拍了半天照片。',{label:'摆个姿势一起拍。',out:[o('照片发出去了，下午来了一波人，说是“看了照片来的”。','我火了？',M('小摊上热门','happy'),{coins:2}),o('拍了二十张，对方一张都没满意。','我尽力了',M('拍照好累','dazed'))]},{label:'继续忙自己的。',out:[o('那人拍完买了一份，说“谢谢老板配合”。','我没配合啊',M('被拍了','fine'),{coins:1}),o('那人拍完就走了，一份都没买。','光看不买',M('白拍','bored'))]}),
  c('珍珠贩子','一个戴墨镜的人凑过来，问要不要买“真珍珠”，一个币一颗。',{label:'买一颗看看。',out:[o('拿回来一看，是塑料的，还印着“玩具”两个字。','交学费了',M('买到假珍珠','embarrassed'),{coins:-1}),o('居然是真的！那人说“看你面善”。','今天运气不错',M('捡到便宜','happy'),{coins:-1,item:{pearl:1}})]},{label:'摇摇头走开。',out:[o('后来听阿洛说，那人卖的全是塑料的。','还好没买',M('火眼金睛','confident')),o('那人在后面喊“便宜点也行”。','不用了',M('拒绝推销','fine'))]}),
  c('夕阳','太阳落进海里，整片海都被染成了橘红色。',{label:'坐在沙滩上看完。',out:[o('看到天完全黑下来，才发现忘了收摊。','明天再收',M('看日落','happy',3)),o('看着看着，阿洛也坐了过来，两个人谁都没说话。','这样就很好',M('安静的傍晚','happy',3))]},{label:'拍一张寄给家人。',out:[o('妈妈回了三个字：“真好看。”','是吧',M('寄出夕阳','happy')),o('爸爸回：“你那边几点了？我这边也看见太阳下山了。”','我们看的是同一个太阳',M('同一个太阳','happy'))]}),
  c('椰子掉了','“咚”的一声，一个椰子砸在摊子旁边的沙子里。',{label:'捡起来。',out:[o('又是一个好椰子，摇一摇咣当咣当。','今天的椰子水有了',M('椰子雨','happy'),{item:{coconut:1}}),o('捡起来才发现是裂的，椰子水流了一地。','好可惜',M('裂开的椰子','sad'))]},{label:'抬头看看还有没有。',out:[o('又掉下来一个，差点砸到脑袋。','这树在跟我开玩笑',M('惊险','dazed'),{item:{coconut:1}}),o('树上的松鼠冲你叽叽叫了两声。','原来是你干的',M('松鼠的恶作剧','playful'))]})];})();
 CARDS.push(...BAY_CARDS);for(const cd of BAY_CARDS)for(const k of ['a','b'])cd[k].out.forEach((oo,i)=>{if(oo.mood)ML[oo.id=`card${cd.n}${k}${i}`]={...oo.mood};});
 const oldNeeds=cardNeeds;cardNeeds=function(){const r=oldNeeds();try{if(card?.cd.at==='summer_test'&&card.o.bay){const f=card.o.bay,b=B();
  if(f.coins){const v=f.coins<0?-Math.min(S().coins,-f.coins):f.coins;if(v)X.record('coin',fill(card.cd.title,card.vars),v);}
  if(f.item)for(const [k,v]of Object.entries(f.item))X.addItem(k,v);
  if(f.loseStock&&b.stock.length)b.stock.splice(Math.floor(Math.random()*b.stock.length),1);}}catch(e){console.error(e);}return r;};
 const oldFits=cardFits;cardFits=function(cd,c){if(cd.at==='summer_test'&&!inBay())return false;return oldFits(cd,c);};
 return {draw,click,openStall,openCafe,make,RECIPES,priceNow,B,P,arrive,leiTalk,kaiTalk,finale,custs,spawn,buy};
})();
window.summerLife=summerLife;
