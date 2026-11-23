// 茵菲谷 side quests (owner 2026-11-02): dialogue-led little stories, all inside the valley. Test page only
// (make_season_game_test.py), never in make_demo.py or the release builds.
//   风车里的怪声  (funny)      小满 hears "a cow crying" in the windmill at night
//   溪边的阿婆    (wistful)    an old letter, a basket of vegetables, a reply
//   菜地里的脚印  (mystery)    nibbled leaves, tracks to the brook, a red hair tie, a night watch
//   老周的乱炖    (delivery)   three different crops from the 仓库 for a new dish
// Crops are given from the 仓库 (springFarm.state.inv) through dialogue choices.
const infeiQuests=(function(){
 const X=springFarm.X,T=seasonMapTest,C=()=>T.state.spring,S=()=>X.F,inSpring=()=>sim.place==='spring_test';
 const today=()=>Math.floor(sim.t/1440),hour=()=>sim.t%1440/60,night=()=>hour()>=19||hour()<4,me=()=>nameOf();
 const Q=()=>{const F=S();F.quests??={};for(const k of Object.keys(RUN))F.quests[k]??={step:0};return F.quests;};
 // ---------------------------------------------------------------- villagers (fixed looks, seeded)
 function seeded(seed,f){const r=Math.random;let s=seed;Math.random=()=>(s=s*16807%2147483647)/2147483647;try{return f();}finally{Math.random=r;}}
 function villager(name,gender,seed,o={}){let lk;for(let k=0;k<60;k++){lk=seeded(seed+k*977,npcLook);if(lk.gender===gender)break;}
  if(o.grey){const g=NSW.hair.map(h=>h[1]).sort((a,b)=>parseInt(b.slice(1),16)%256-parseInt(a.slice(1),16)%256)[0];lk=doll.normalize({...lk,hair:g,acc:[]});}
  return {name,look:lk,ramps:doll.rampsOf(lk),cache:new Map(),kid:!!o.kid,x:o.x,scene:o.scene,dir:-1};}
 const V={
  xiaoman:villager('小满','f',11,{kid:true,scene:1,x:236}),
  wang:villager('王叔','m',23,{scene:2,x:238}),
  apo:villager('阿婆','f',37,{scene:0,x:178,grey:true}),
  zhou:villager('老周','m',51,{scene:2,x:112})};
 const visible=v=>{const q=Q();if(v.vis)return v.vis(q);
  if(v===V.wang)return q.mill.step===1&&night();
  if(v===V.xiaoman&&q.prints.step===3&&night())return 'farm';
  if(v===V.xiaoman)return hour()>=6&&hour()<21;
  if(v===V.apo)return hour()>=5&&hour()<22;
  if(v===V.zhou)return q.stew.step<3&&hour()>=5&&hour()<22;
  return true;};
 const where=v=>visible(v)==='farm'?{scene:4,x:300}:{scene:v.scene,x:v.x};
 // what each quest waits for now: {v} a person, {spot} a place, {auto} a scene that plays by itself
 const SPOTS={mill:{scene:2,rect:[205,8,70,96],x:214},reeds:{scene:0,rect:[50,70,90,40],x:95}};
 function goals(){const q=Q(),g=[];
  if(q.mill.step===0)g.push({id:'mill',v:V.xiaoman,mark:'!'});
  if(q.mill.step===1)g.push({id:'mill',spot:'mill',mark:'?',hint:'天黑以后去风车那边看看'});
  if(q.mill.step===2)g.push({id:'mill',v:V.xiaoman,mark:'?',hint:'回去告诉小满'});
  if(q.letter.step<3)g.push({id:'letter',v:V.apo,mark:q.letter.step===0?'!':'?',hint:['','送阿婆一筐菜（仓库里拿）','第二天再去看看阿婆'][q.letter.step]});
  if(q.stew.step<3)g.push({id:'stew',v:V.zhou,mark:q.stew.step===0?'!':'?',hint:['','给老周送三样不同的菜','第二天再去找老周'][q.stew.step]});
  if(q.prints.step===1)g.push({id:'prints',spot:'reeds',mark:'?',hint:'顺着脚印往西找，小溪那边'});
  if(q.prints.step===2)g.push({id:'prints',v:V.xiaoman,mark:'?',hint:'问问小满'});
  if(q.prints.step===3)g.push({id:'prints',auto:4,hint:'晚上去菜地等着'});
  for(const f of MORE_GOALS)g.push(...f(q));
  return g;}
 // ---------------------------------------------------------------- dialogue helpers (the story's own rows)
 const speech=springFarm.speech;let busy=false;
 STORY_HOLDS.push(()=>busy);   // a quest scene is a story: no calls, cards or stray lines until it ends
 const say=(who,words)=>new Promise(res=>speech.show(who,words,{special:true,advance:res}));
 const ask=(who,words,opts)=>new Promise(res=>speech.show(who,words,{special:true,choices:opts.map((label,i)=>({label,on:()=>res(i)}))}));
 // if anything else takes over her walk the scene still goes on (owner 2026-11-10: a dropped walk locked every click in 茵菲谷)
 const walkTo=x=>new Promise(res=>{speech.hide();let done=false;const fin=()=>{if(!done){done=true;clearInterval(w);res();}};C().target(x,103,fin);
  const w=setInterval(()=>{const s=C().state;if(s.after!==fin&&!done)fin();},400);});
 const ML_=(id,name,emo,pts=2)=>{ML['sq_'+id]={name,emo,pts,min:240};return 'sq_'+id;};
 const MOODS={mill:ML_('mill','风车怪声','playful'),letter:ML_('letter','阿婆的饼子','sad',1),prints:ML_('prints','菜地里的小偷','happy',3),stew:ML_('stew','咸了一点的乱炖','happy')};
 // ---- quest log (owner 2026-11-03): every scene that moved a quest on is kept with its lines, choices and
 // letters, so the 任务 panel can replay the whole story. The farm's main line is kept the same way.
 const SCENE={mill:['小满的秘密','夜里的风车','告诉小满'],letter:['念信','送菜','回信'],prints:['菜叶被啃了','小溪边','问小满','夜里蹲守'],stew:['新菜','送菜','尝乱炖']};
 const STORY={arrive:'到了茵菲谷',room:'看看房间',field:'去地里',sow:'第一次播种',water:'第一次浇水',talk:'妈妈的嘱咐'};
 const SCENE_ICON={mill:['windmill','suona','smile'],letter:['letter','basket','letter'],prints:['footprints','lens','smile','moon'],stew:['stew','basket','stew'],
  story:{arrive:'heart',room:'house',field:'seedling',sow:'seedling',water:'drop',talk:'heart'}};
 let rec=null;
 const note=x=>{if(rec)rec.lines.push(x);};
 const rawShow=speech.show.bind(speech);
 speech.show=(who,words,o={})=>{
  let to=rec?.lines;
  if(!busy&&inSpring()&&STORY[S().phase]){const F=S();F.storyLog??=[];let g=F.storyLog[F.storyLog.length-1];
   if(!g||g.title!==STORY[F.phase]){g={day:today(),title:STORY[F.phase],icon:SCENE_ICON.story[F.phase],lines:[]};F.storyLog.push(g);}to=g.lines;}
  if(to){if(words)to.push([who,String(words)]);if(o.choices)o={...o,choices:o.choices.map(c=>({...c,on:()=>{to.push(['>',c.label]);c.on?.();}}))};}
  return rawShow(who,words,o);};
 async function scene(fn,id){if(busy)return;busy=true;T.state.autoAt=sim.t+1e9;closeRing();
  const before=id&&JSON.stringify(Q()[id]);rec=id?{id,step:Q()[id].step,lines:[]}:null;
  try{await fn();}finally{speech.hide();busy=false;T.state.autoAt=sim.t+30;
   if(rec&&JSON.stringify(Q()[id])!==before&&rec.lines.length){const q=Q()[id];q.log??=[];q.log.push({day:today(),title:SCENE[id][rec.step]||'',icon:SCENE_ICON[id][rec.step],lines:rec.lines});if(q.log.length>12)q.log.shift();}
   rec=null;}}
 function finish(id,text){Q()[id].step=9;Q()[id].day=today();addMood(MOODS[id]);log(text);showHint('支线完成');}
 const crops=(skip=[])=>Object.entries(S().inv).filter(([k,n])=>n>0&&X.CROP[k]&&!skip.includes(k)).map(([k])=>k);
 const take=k=>{S().inv[k]--;if(!S().inv[k])delete S().inv[k];};
 async function approach(v){const s=C().state,p=where(v);await walkTo(p.x+(s.x<p.x?-16:16));v.dir=s.x<p.x?-1:1;s.facing=-v.dir;}
 // ---------------------------------------------------------------- 风车里的怪声
 async function mill0(){
  await say('小满','哎，你就是新搬来那家的吧？');
  await say(me(),'嗯，就前头那个农舍。');
  await say('小满','那我跟你说个事儿啊，你可别告诉别人。');
  await say('小满','风车里头，一到晚上就有东西在叫！');
  await say(me(),'啊？啥东西啊？');
  await say('小满','不知道呀！呜——呜——的，跟牛哭似的。');
  if(await ask('小满','我不敢去。你是大人，你去看看呗。',['行吧，晚上我去看看','牛哭是啥声儿啊？'])===1){
   await say('小满','就……就可难听了那种。');await say('小满','哎呀反正你去嘛！');}
  Q().mill.step=1;showHint('天黑以后去风车那边看看');}
 async function mill1(){
  if(!night()){await walkTo(SPOTS.mill.x);await say(me(),'白天挺安静的啊，等天黑了再来听听吧。');return;}
  await walkTo(SPOTS.mill.x);C().state.facing=1;V.wang.dir=-1;
  await say('风车里','呜——呜哩哇——');
  await say(me(),'谁啊？谁在里头？');
  await say('王叔','哎哟我的妈！吓我一跳。');
  await say('王叔','你是……新来那家的孩子吧？');
  await say(me(),'叔，您大晚上在这儿干嘛呢？');
  await say('王叔','练唢呐呗。');
  await say('王叔','你婶子不让我在家吹，说吵得鸡都不下蛋了。');
  await say(me(),'呃……小满说风车里有牛在哭。');
  await say('王叔','啥？牛哭？');
  await say('王叔','我这吹的可是《百鸟朝凤》啊！');
  const q=Q().mill;
  if(await ask('王叔','这事儿你可别往外说啊。',['行，我不说','要不吹给婶子听听？'])===0){
   q.how='secret';await say('王叔','哎，好孩子。这几个币拿去买糖吃，别嫌少啊。');X.record('coin','王叔塞的“封口费”',3);}
  else{q.how='tell';await say('王叔','还吹给她听？上回吹完，她三天没搭理我。');await say(me(),'那是上回没吹好吧。');await say('王叔','嘿，你这孩子说话咋这么直呢。行行行，我再练练。');}
  q.step=2;showHint('回去告诉小满');}
 async function mill2(){const how=Q().mill.how;
  await say('小满','咋样咋样？是啥呀？');
  if(how==='secret'){
   await say(me(),'是……是只挺大的鸟，叫得有点儿怪。');
   await say('小满','我就说不是牛嘛！');
   await say('小满','那它吃人不？');
   await say(me(),'不吃不吃，它吃糖。');
   await say('小满','那我明天晚上带糖去喂它！');
   await say(me(),'别别别，它晚上要睡觉的，你别去吵它。');}
  else{
   await say(me(),'是你王叔，躲里头吹唢呐呢。');
   await say('小满','啊？王叔？！');
   await say('小满','那他吹的啥呀？');
   await say(me(),'说是《百鸟朝凤》。');
   await say('小满','……哪有鸟这么叫的呀。');}
  finish('mill','风车里的怪声原来是王叔在练唢呐。');}
 // ---------------------------------------------------------------- 溪边的阿婆
 async function letter0(){
  await say('阿婆','孩子，你认得字吧？');
  await say(me(),'认得啊，怎么了阿婆？');
  await say('阿婆','那你帮我念念这个。我这眼睛花喽，字又小。');
  await say(me(),'我看看啊……哦，是封信。');
  await say(me(),'“妈，城里活多，今年先不回了。明年春天一定回来，带小雨一起。”');
  note({letter:'儿子的信 · 前年寄来',text:'妈：\n城里活多，今年先不回了。\n明年春天一定回来，带小雨一起。'});
  await say('阿婆','嗯，是这么写的，没错。');
  await say(me(),'这是哪年寄来的啊？');
  await say('阿婆','前年喽。');
  if(await ask('阿婆','我就是想再听一遍。他说话就这个调调。',['他在哪儿上班啊？','那我再给您念一遍'])===0){
   await say('阿婆','南边，远着呢，坐火车得一天一夜。');await say('阿婆','电话倒也打，就是忙，说不上两句就挂了。');}
  else{await say(me(),'“……明年春天一定回来，带小雨一起。”');await say('阿婆','小雨是我孙女，今年该上小学了吧。');}
  await say('阿婆','他小时候啊，就爱吃我烙的菜饼子，地里有啥我就往里搁啥。');
  await say('阿婆','这会儿就剩我一个了，地也种不动喽。');
  Q().letter.step=1;showHint('送阿婆一筐菜（收的菜都在仓库里）');}
 async function letter1(){const have=crops();
  if(!have.length){await say('阿婆','哟，又来看我啦？');await say(me(),'嗯，路过看看您。');speech.hide();showHint('仓库里还没有菜，收了菜再来');return;}
  if(await ask('阿婆','哟，又来看我啦？',['给您带了点儿菜','没啥事，路过'])===1){await say(me(),'没啥事，路过看看您。');await say('阿婆','那坐会儿吧，这石头不凉。');return;}
  const i=await ask('阿婆','哎哟，还带东西。带的啥呀？',have.map(k=>X.CROP[k].name));
  take(have[i]);
  await say('阿婆',`哎哟，这么些${X.CROP[have[i]].name}，我一个人哪吃得了。`);
  await say('阿婆','明儿你再来啊，我给你烙饼子吃。');
  Object.assign(Q().letter,{step:2,day:today(),crop:have[i]});}
 async function letter2(){
  if(today()<=Q().letter.day){await say('阿婆','明儿再来，面还没发好呢。');return;}
  await say('阿婆','来啦？快，趁热吃。');
  await say(me(),'哇，好香啊！');
  await say('阿婆','他那会儿一顿能吃四个呢。');
  await say('阿婆','孩子，再麻烦你个事儿，帮我回封信吧。');
  await say(me(),'行，您说，我写。');
  const i=await ask('阿婆','就写……',['“地里都好，别惦记”','“春天了，想你们”','“小雨长高了吧”']);
  note({letter:'替阿婆写的回信',text:'儿子：\n'+['地里都好，别惦记。','春天了，想你们。','小雨长高了吧？上回说要学游泳，学会了没有。'][i]+'\n——妈'});
  await say('阿婆',['嗯。他忙，甭让他惦记。','……写上吧。','对对，问问小雨。上回电话里她说要学游泳呢。'][i]);
  if(i===1)await say('阿婆','写完我再瞅瞅，要是太那啥了，就给划了。');
  await say(me(),'写好了。要不我帮您寄了？');
  await say('阿婆','不用不用，我自个儿上镇上寄。');
  await say('阿婆','邮局那小伙子都认得我了，回回问：又是给儿子的吧？');
  sim.needs.hunger=Math.min(100,sim.needs.hunger+30);
  finish('letter','帮溪边的阿婆念了信，又替她回了一封。饼子很香。');}
 // ---------------------------------------------------------------- 菜地里的脚印
 async function prints0(){
  await say(me(),'嗯？');
  await say(me(),'这菜叶子咋缺了好几块啊……');
  await say(me(),'地上还有脚印呢，小小的一串。');
  await say(me(),'往西边去了吧这是。');
  Q().prints.step=1;showHint('顺着脚印往西找，小溪那边');}
 async function prints1(){
  await walkTo(SPOTS.reeds.x);
  await say(me(),'诶，脚印到这儿就没了。');
  await say(me(),'草里有几根啃过的胡萝卜缨子……');
  await say(me(),'还有根红头绳？');
  await say(me(),'这么细，大人不扎这个吧。');
  Q().prints.step=2;showHint('问问小满');}
 async function prints2(){
  await say(me(),'小满，这头绳是你的吧？');
  await say('小满','……不是。');
  await say('小满','是。');
  await say('小满','你在哪儿捡的呀？');
  await say(me(),'小溪边上。旁边还有啃剩的胡萝卜缨子呢。');
  if(await ask('小满','那不是我啃的！',['那是谁啃的啊？','行吧，那我不问了'])===0){await say('小满','不能说！说了它就让人抓走了。');await say(me(),'它？');}
  else{await say('小满','你真不问啦？');await say(me(),'不问了呀。');await say('小满','……');}
  await say('小满','……那你晚上来菜地吧，别出声啊。');
  Q().prints.step=3;showHint('晚上去菜地等着');}
 async function prints3(){
  const s=C().state;await walkTo(250);s.facing=1;
  await say(me(),'……');
  await say('小满','嘘——');
  await say('小满','出来吧，没事儿，是好人。');
  rabbit.on=true;
  await say(me(),'啊，是只兔子啊？');
  await say('小满','它腿伤了，我在溪边捡着的。');
  await say('小满','我妈说家里不让养，要拿集上卖了。');
  await say('小满','我就把它藏溪边了，晚上来……来拔你家胡萝卜喂它。');
  const q=Q().prints;
  if(await ask('小满','对不起嘛。',['那让它住我家鸡窝边上吧','我陪你回去跟你妈说说'])===0){
   q.rabbit='farm';await say('小满','真的呀？！');await say('小满','那我天天来看它！我还帮你浇水！');await say(me(),'浇水行啊。胡萝卜可别再拔了。');await say('小满','……就拔一根也不行吗？');}
  else{q.rabbit='home';await say('小满','她肯定要骂我的。');await say(me(),'没事儿，我先说，你站我后头。');await say('小满','……好。');}
  rabbit.on=false;finish('prints','菜地里的小偷是一只伤了腿的兔子，还有小满。');}
 // ---------------------------------------------------------------- 老周的乱炖
 async function stew0(){
  await say('老周','哎，你是新来那家的吧？我姓周，在镇上开了个小饭馆。');
  await say(me(),'周叔好。');
  await say('老周','是这么个事儿，我琢磨着出个新菜，叫茵菲谷乱炖。');
  await say('老周','菜呢，得是咱这片地里长的，要三样，还不能重样。');
  if(await ask('老周','你那块地，能帮我凑凑不？',['行啊，凑齐了给您送来','乱炖……能好吃吗？'])===1){
   await say('老周','嗐，好不好吃看菜呗。菜好，咋炖都香。');await say(me(),'那行，我试试吧。');}
  Object.assign(Q().stew,{step:1,got:[]});showHint('给老周送三样不同的菜（仓库里拿）');}
 async function stew1(){const q=Q().stew,have=crops(q.got);
  if(!have.length){await say('老周',q.got.length?`还差 ${3-q.got.length} 样啊，不着急。`:'菜凑得咋样了？');await say(me(),'还在地里长着呢，再等等。');return;}
  if(await ask('老周',q.got.length?`还差 ${3-q.got.length} 样啊。`:'哟，带菜来啦？',['带了带了','下回吧'])===1)return;
  const i=await ask('老周','来来，拿出来我瞅瞅。',have.map(k=>X.CROP[k].name));
  take(have[i]);q.got.push(have[i]);
  if(q.got.length<3){await say('老周',['行，先搁这儿。','好嘞，这个炖着香。'][q.got.length-1]);await say('老周',`还差 ${3-q.got.length} 样啊。`);return;}
  await say('老周','得嘞，齐了！');
  await say('老周','明儿这个点儿，我给你端一碗过来尝尝。');
  Object.assign(q,{step:2,day:today()});}
 async function stew2(){const q=Q().stew;
  if(today()<=q.day){await say('老周','明儿，明儿啊。炖菜这东西急不得。');return;}
  await say('老周','来来来，尝尝，刚出锅的。');
  await say(me(),'……');
  await say(me(),'……有点儿咸。');
  await say('老周','啊？咸了？');
  await say(me(),'就咸了一点点。');
  await say('老周','你看你看，我就说盐搁多了吧！我媳妇非说正好。');
  const pay=Math.round(q.got.reduce((s,k)=>s+X.CROP[k].sell,0)+4);
  X.record('coin','老周的菜钱',pay);
  await say('老周',['行行，记下了，下回少搁点儿。','嘿，你俩说的还不一样。成，我回去再调调。'][await ask('老周',`菜钱 ${pay} 个币，拿着拿着。`,['下回少搁点儿盐呗','挺好吃的，就是咸了点儿'])]);
  sim.needs.hunger=Math.min(100,sim.needs.hunger+25);
  finish('stew','老周的茵菲谷乱炖做好了，咸了一点。');}
 const RUN={mill:[mill0,mill1,mill2],letter:[letter0,letter1,letter2],prints:[prints0,prints1,prints2,prints3],stew:[stew0,stew1,stew2]};
 const MORE_GOALS=[];
 const spotAt=(sc,x,y)=>busy?null:goals().find(g=>{const sp=g.spot&&SPOTS[g.spot];if(!sp||sp.scene!==sc)return false;const [rx,ry,w,h]=sp.rect;return x>=rx&&x<rx+w&&y>=ry&&y<ry+h;});
 // more side quests from other files (infei_side.js): the same tables, filled in
 function register(o){const id=o.id;RUN[id]=o.run;TITLE[id]=o.title;KIND[id]=o.kind;END[id]=o.end;HOME[id]=o.home;PLACE[id]=o.place;SCENE[id]=o.scenes;SCENE_ICON[id]=o.icons;
  MOODS[id]=ML_(id,...o.mood);Object.assign(V,o.villagers||{});Object.assign(IDLE,o.idle||{});Object.assign(SPOTS,o.spots||{});if(o.goals)MORE_GOALS.push(o.goals);}
 const run=id=>{const st=Q()[id].step,fn=RUN[id][st];if(fn)scene(fn,id);};
 // ---------------------------------------------------------------- talking to someone with nothing new
 const IDLE={xiaoman:[['小满','你看见我妈没有啊？'],['小满','我刚捉着一只蚂蚱，又让它跑了！']],apo:[['阿婆','坐会儿吧，这石头不凉。'],['阿婆','今儿水流得急，夜里上头准是下雨了。']],
  zhou:[['老周','中午忙得脚不沾地，我出来透口气。'],['老周','你那胡萝卜长得可真水灵啊。']],wang:[['王叔','嘘——']]};
 async function chat(key){const [who,line]=pick(IDLE[key]||[[V[key].name,'嗯？']]);await say(who,line);}
 function talk(key){const v=V[key],g=goals().find(g=>g.v===v);scene(async()=>{await approach(v);if(g)await RUN[g.id][Q()[g.id].step]();else await chat(key);},g?.id);}
 // ---------------------------------------------------------------- drawing: villagers, marks, the rabbit
 const rabbit={on:false};
 function bunny(ctx,x,y,t){ctx.fillStyle='#e9e2d6';ctx.fillRect(x-4,y-5,8,5);ctx.fillRect(x+2,y-8,4,4);ctx.fillRect(x+3,y-12,1,4);ctx.fillRect(x+5,y-12,1,4);ctx.fillStyle='#b9ae9e';ctx.fillRect(x-4,y-1,8,1);ctx.fillStyle='#3a2a2e';ctx.fillRect(x+5,y-7,1,1);if(Math.floor(t*2)%2)ctx.fillRect(x-5,y-4,1,1);}
 X.hooks.draw.push((ctx,info)=>{if(info.inside||S().phase!=='done')return;const t=info.time,gs=goals();
  for(const [key,v]of Object.entries(V)){if(!visible(v))continue;const p=where(v);if(p.scene!==info.region)continue;
   const s=C().state;if(!busy&&Math.abs(s.x-p.x)<40)v.dir=s.x<p.x?-1:1;
   const f={expr:idleBreath.blink(p.x*.37)?'blink':'neutral',look:v.dir,bob:idleBreath.bob(p.x*.37),sway:0,wave:null};ctx.drawImage(npcCanvas(v,f,'stand'),Math.round(p.x)-10,103-27);
   const g=gs.find(g=>g.v===v);if(g&&!busy)drawQuestMarker(ctx,p.x,v.kid?80:76,g.mark);}
  for(const g of gs)if(g.spot&&SPOTS[g.spot].scene===info.region&&!busy){const sp=SPOTS[g.spot];drawQuestMarker(ctx,sp.x,sp.rect[1]+21,g.mark||'?');}
  if(rabbit.on&&info.region===4)bunny(ctx,318,103,t);
  if(Q().prints.rabbit==='farm'&&info.region===3&&!night())bunny(ctx,104+Math.round(Math.sin(t*.4)*6),103,t);
  autoTick(info);});
 function autoTick(info){if(busy||!inSpring()||speech.open||wiping||cardHolds()||ringOf||sim.mode==='down')return;const s=C().state,q=Q();
  if(s.door||s.target||s.inside)return;
  if(q.prints.step===0&&q.mill.step===9&&s.scene===4&&hour()>=6&&hour()<12&&Object.keys(S().beds).length)return run('prints');
  if(q.prints.step===3&&night()&&s.scene===4)return run('prints');
  // 小满 keeps her word: one dry bed watered a day once the rabbit lives on the farm
  if(q.prints.rabbit==='farm'&&q.prints.water!==today()&&hour()>=8){q.prints.water=today();const b=Object.values(S().beds).find(b=>b.watered!==today()&&!X.ripe(b));if(b){b.watered=today();log('小满来看兔子，顺手浇了一块地。');}}}
 // ---------------------------------------------------------------- clicks + the quest list
 const hit=(x,y,s)=>{if(s.inside||busy)return false;
  for(const [key,v]of Object.entries(V)){if(!visible(v))continue;const p=where(v);if(p.scene===s.scene&&Math.abs(x-p.x)<10&&y>103-44&&y<104){talk(key);return true;}   /* up to the !/? mark above the head (owner: clicking the mark did nothing) */}
  const g=spotAt(s.scene,x,y);if(g){run(g.id);return true;}
  return false;};
 X.hooks.click.push(hit);
 const TITLE={mill:'风车里的怪声',letter:'溪边的阿婆',prints:'菜地里的脚印',stew:'老周的乱炖'},KIND={mill:'windmill',letter:'letter',prints:'footprints',stew:'stew'};
 const END={mill:'原来是王叔在练唢呐',letter:'替阿婆回了一封信',prints:'小偷是一只伤了腿的兔子',stew:'乱炖咸了一点'};
 const STEP={letter:['','送阿婆一筐菜（仓库里拿）','明天去溪边吃阿婆的饼子'],stew:['','给老周送三样不同的菜','明天去找老周尝乱炖']};
 // the 任务 panel (quest_panel.js): started or finished quests, plus the farm's main line
 // where each quest is now (the panel's place pill)
 const PLACE={mill:['油菜花田','风车','油菜花田'],letter:['小溪边','小溪边','小溪边'],prints:['菜地','小溪边','油菜花田','菜地'],stew:['郁金香田','郁金香田','郁金香田']};
 const HOME={mill:'风车',letter:'小溪边',prints:'菜地',stew:'郁金香田'};
 questBoard.add(()=>{const q=Q(),gs=goals(),out=[],F=S();
  if(F.unlocked&&!['none','meet'].includes(F.phase)){const ph=F.phase,where=!F.unlocked?'家里信箱':ph==='none'?'机场':ph==='sow'||ph==='water'?'菜地':'农舍',step=!F.unlocked?'读妈妈寄来的信':ph==='none'?'去机场，坐去茵菲谷的航班':ph==='sow'||ph==='water'||ph==='field'?'去菜地看看':ph==='room'?'进屋看看':'跟着妈妈熟悉农庄';
   out.push({id:'farm',title:'妈妈的农庄',kind:'house',place:ph==='done'?'茵菲谷':where,done:ph==='done',step,end:'菜地交给你了',isNew:!F.unlocked||ph==='none',log:F.storyLog||[],go:ph==='done'?null:farmGo});}
  for(const id of Object.keys(TITLE)){const st=q[id].step;if(st===0)continue;const g=gs.find(g=>g.id===id);
   let step=g?.hint||(g?.v?`去找${g.v.name}聊聊`:'');
   if(STEP[id]&&st===2&&today()>q[id].day)step=id==='letter'?'去溪边找阿婆':'去郁金香田边找老周';
   out.push({id,title:TITLE[id],kind:KIND[id],place:st===9?HOME[id]:PLACE[id][st]||HOME[id],done:st===9,step,end:END[id],isNew:false,log:q[id].log||[],go:()=>questGo(id)});}
  // offered (someone has a "!") is not listed: only quests she has taken (owner 2026-11-03)
  return out;});
 // ---------------------------------------------------------------- 任务 panel: click a quest → she walks there, or a bubble says why not (owner 2026-11-10)
 const HRS={xiaoman:[6,21],apo:[5,22],zhou:[5,22]};
 const SCENE_NAME=['小溪边','油菜花田','风车','农舍','菜地','果园牧场'];
 function canGo(){if(!inSpring())return '先坐飞机去茵菲谷';if(busy||storyLocked())return '等这段对话说完';if(sim.mode==='down')return `先把${ta()}叫醒（长按${ta()}）`;
  if(asleep())return `${ta()}在睡觉，等${ta()}醒了再去`;if(wiping||cardHolds())return '等眼前的事忙完';return '';}
 function goTo(sc,x){const c=C(),s=c.state;window.seasonAuto?.cancel();T.state.autoAt=sim.t+90;closeRing();
  const fin=()=>{if(x!=null)C().target(Math.round(x),103);};
  if(!s.inside&&s.scene===sc){fin();return;}window.seasonAuto?.toScene(sc,fin);}
 function questGo(id){const no=canGo();if(no)return no;const q=Q()[id],g=goals().find(g=>g.id===id);
  if(!g)return '现在没有要做的，过一阵再看看';
  if(/^明天/.test(g.hint||'')||(STEP[id]&&q.step===2&&today()<=q.day))return '请等到明天再去';
  if(id==='letter'&&q.step===1&&!crops().length)return '仓库里还没有菜，先收获一些';
  if(id==='stew'&&q.step===1&&!crops(q.got).length)return '仓库里没有还没送过的菜，先去收获';
  if(g.v){const vis=visible(g.v);
   if(!vis){const key=Object.keys(V).find(k=>V[k]===g.v),h=g.v.hours||HRS[key];
    if(key==='wang'||id==='mill')return '请等到天黑（晚上 7 点后）';
    return h?`${g.v.name}现在不在，请等到 ${h[0]}–${h[1]} 点`:`${g.v.name}今天没出来，换一天再去`;}
   const p=where(g.v),s=C().state;goTo(p.scene,p.x+(s.scene===p.scene&&!s.inside&&s.x>p.x?16:-16));return {say:`去${PLACE[id]?.[q.step]||HOME[id]||SCENE_NAME[p.scene]||'那边'}找${g.v.name}`};}
  if(g.spot){const sp=SPOTS[g.spot];if(id==='mill'&&!night())return '请等到天黑（晚上 7 点后）';goTo(sp.scene,sp.x-10);return {say:`去${PLACE[id]?.[q.step]||SCENE_NAME[sp.scene]||'那边'}看看`};}
  if(g.auto!=null){if(id==='prints'&&!night())return '请等到晚上（7 点后）再去菜地等着';goTo(g.auto,200);return {say:'去菜地等着'};}
  return '现在没有要做的，过一阵再看看';}
 function farmGo(){const F=S();if(!inSpring())return '先坐飞机去茵菲谷';if(['sow','water','field'].includes(F.phase)){if(sim.mode==='down')return `先把${ta()}叫醒（长按${ta()}）`;goTo(4,150);return {say:'去菜地'};}
  return '跟着妈妈把开场走完就好';}
 X.hooks.pick.quests=()=>questBoard.open();
 return {V,Q,goals,run,talk,spotAt,hit,register,kit:{say,ask,walkTo,finish,crops,take,note,me,today,hour,night,villager,approach,X,S,C},at:v=>visible(v)?where(v):null,spots:SPOTS,list:()=>questBoard.open(),get busy(){return busy;},rabbit};
})();
window.infeiQuests=infeiQuests;
