// 爸妈住在茵菲谷（owner 2026-11-06）。2026-11-12 起他们像她一样真的走动：进出家门、上下楼、走过一块块地、去镇上再回来（见「真的走动」一节）。
//  - 平时：早上、傍晚妈妈在灶台、爸爸在饭桌，晚上两人坐长椅，22 点后在自己床上（infei_home.js 画睡觉）；白天下地/去镇上
//    （infei_farm.js 帮忙浇水，现在七成的日子会来）。点爸妈说一句。她在屋里有爸妈陪着，社交慢慢涨。
//  - 春节她在茵菲谷：爸妈在农舍过年，主世界春节的每一步都有（贴春联、包饺子、午饭、压岁钱、三连问、年夜饭、春晚、零点、睡觉），
//    台词每年换（spring_festival.js → cnyVariant(step,'farm')），夜里山谷放烟花。
//  - 主世界人脉点爸妈的「拜访」：自己去机场、飞茵菲谷，当天爸妈都在家等她。
(function(){
 const X=springFarm.X,C=()=>seasonMapTest.state.spring,inSpring=()=>sim.place==='spring_test',F=()=>springFarm.state;
 const today=()=>Math.floor(sim.t/1440),mins=()=>((sim.t%1440)+1440)%1440,HOME=3;   // the farmhouse's yard is scene 3
 const ready=()=>F().phase==='done';
 const look=id=>socialState.contacts.find(c=>c.id===id)?.look||doll.PRESETS[id==='mom'?'f':'m'];
 const npc={};const npcOf=id=>{const lk=look(id);if(!npc[id]||npc[id].look!==lk)npc[id]={look:lk,ramps:doll.rampsOf(lk),cache:new Map(),kid:false};return npc[id];};
 const name=id=>id==='mom'?'妈妈':'爸爸',contact=id=>socialState.contacts.find(c=>c.id===id);
 // farmhouse ground floor (house px): where they stand or sit
 const AT={stove:[262,'stand'],jar:[300,'stand'],tableL:[200,'sit'],tableR:[216,'sit'],setteeL:[99,'sit'],setteeR:[124,'sit'],door:[60,'stand'],kitchen:[240,'stand']};
 let visit=null;   // {day} — she flew in to see them: both home all day
 // ---------------------------------------------------------------- the day's plan → {mom:spot,dad:spot}
 function plan(){if(!ready())return {};const m=mins(),v=visit&&visit.day===today(),fc=farmCny();
  if(fc)return fc.where;
  const cook=infeiHome.svc?.id==='stove'?'jar':'stove',o={};
  if(m>=6*60+30&&m<8*60)o.mom=cook;if(m>=7*60&&m<8*60)o.dad='tableR';
  if(m>=17*60+30&&m<19*60)o.mom=cook;if(m>=18*60&&m<19*60)o.dad='tableR';
  if(m>=19*60&&m<21*60+30){o.mom=today()%3===0?'tableL':'setteeL';o.dad='setteeR';}
  // owner 2026-11-10: they live here too — lunch at home, and a slow afternoon in now and then (rain: both stay in)
  if(m>=11*60+30&&m<12*60+40){o.mom=cook;if(today()%2===0)o.dad='tableR';}
  if(m>=12*60+40&&m<13*60+30&&today()%2===0){o.mom='tableL';o.dad='tableR';}
  if(m>=14*60&&m<16*60&&today()%3===1)o.mom=Math.floor(m/40)%2?'jar':'setteeL';
  if(typeof weather!=='undefined'&&weather.kind==='rain'&&m>=8*60&&m<17*60+30){o.mom=Math.floor(m/50)%3===0?cook:'setteeL';o.dad=Math.floor(m/70)%2?'tableR':'setteeR';}
  if(v&&m>=8*60&&m<17*60+30){o.mom=Math.floor(m/90)%2?'tableL':cook;o.dad=Math.floor(m/120)%2?'tableR':'setteeR';}
  if(infeiHome.svc?.id==='settee'&&o.dad==='setteeR')o.dad='tableR';   // she took the middle of the bench: 爸爸 moves to the table
  return o;}
 // ================================================================ 爸妈像她一样真的走动（owner 2026-11-12：不要闪现）
 // Each parent is a little walker with a place in the valley (in the farmhouse on a floor, out in a field, or gone to town).
 // The day's plan names a spot; they walk there the way she does: across the room, up the stairs (x 61), through the door
 // (inside x 51 / the yard x 182), field to field over the scene edges, off the brook's left edge to town and back.
 const WIDTH=[342,342,342,342,342,684],FLOOR=[108,50],STAIR=61,DOOR_IN=51,DOOR_OUT=182;
 const SPOT={stove:{in:1,f:0,x:262},jar:{in:1,f:0,x:300},tableL:{in:1,f:0,x:200,pose:'sit'},tableR:{in:1,f:0,x:216,pose:'sit'},
  setteeL:{in:1,f:0,x:99,pose:'sit'},setteeR:{in:1,f:0,x:124,pose:'sit'},kitchen:{in:1,f:0,x:240},
  bedM:{in:1,f:1,x:236,pose:'sleep'},bedD:{in:1,f:1,x:256,pose:'sleep'},
  coop:{s:3,x:82,face:-1,fx:'grain',roam:[72,104]},yardL:{s:3,x:166,face:1},yardR:{s:3,x:198,face:-1},
  field:{s:4,x:150,roam:[40,300],fx:'weed'},orchard:{s:5,x:190,roam:[70,300]},pasture:{s:5,x:520,roam:[410,640]},town:{away:1}};
 const ag={mom:{id:'mom'},dad:{id:'dad'}};let errand={};
 // the rest of the day: chores outside when the house plan has nothing for them
 function outdoor(id,m){const d=today(),winter=springFarm.seasonAt(d)===3,f=k=>winter&&k==='field'?'jar':k;
  if(m>=22*60||m<6*60)return id==='mom'?'bedM':'bedD';
  if(m>=21*60+30)return id==='mom'?'kitchen':'tableR';
  if(id==='mom'){if(m<6*60+30)return 'kitchen';if(m<9*60+30)return 'coop';if(m<11*60+30)return d%4===1?'town':f('field');
   return f(['field','orchard','coop'][Math.floor(m/90)%3]);}
  if(m<7*60)return 'pasture';if(m<11*60+30)return d%4===3?'town':Math.floor(m/80)%2?'pasture':'orchard';
  return f(['field','pasture','orchard'][Math.floor(m/100)%3]);}
 function want(id){const e=errand[id];if(e)return e;const fc=farmCny();
  if(fc){if(fc.step.id==='couplets')return id==='mom'?'yardL':'yardR';const w=fc.where[id];if(w)return w;}
  return plan()[id]||outdoor(id,mins());}
 const spotOf=k=>typeof k==='object'?k:SPOT[k];
 function snap(a){const k=want(a.id),t=spotOf(k);a.k=k;a.ops=[];a.op=null;a.idle=0;a.wander=null;
  if(t.away)Object.assign(a,{w:'away'});else if(t.in)Object.assign(a,{w:'in',f:t.f,x:t.x});else Object.assign(a,{w:'out',s:t.s,x:t.x});}
 function route(a,t){const r=[];let c={w:a.w,s:a.s,f:a.f};
  const out=()=>{if(c.w==='in'){if(c.f===1)r.push({walk:STAIR},{stairs:0});r.push({walk:DOOR_IN},{door:'out'});c={w:'out',s:3};}
   else if(c.w==='away'){r.push({enter:1});c={w:'out',s:0};}};
  const to=s=>{while(c.s<s){r.push({edge:1});c.s++;}while(c.s>s){r.push({edge:-1});c.s--;}};
  if(t.away){out();to(0);r.push({walk:-8},{leave:1});return r;}
  if(t.in){if(c.w!=='in'){out();to(3);r.push({walk:DOOR_OUT},{door:'in'});c={w:'in',f:0};}
   if(c.f!==t.f)r.push({walk:STAIR},{stairs:t.f});r.push({walk:t.x});return r;}
  out();to(t.s);r.push({walk:t.x});return r;}
 const seen=a=>inSpring()&&(a.w==='in'?C().state.inside:a.w==='out'&&!C().state.inside&&C().state.scene===a.s);
 function step(a,dt){
  const k=want(a.id),same=JSON.stringify(k)===JSON.stringify(a.k);
  if(!same&&(!a.op||a.op.walk!=null)){a.k=k;a.ops=route(a,spotOf(k));a.op=null;a.wander=null;a.sleep=false;}
  const v=34*dt*(seen(a)?1:5);a.moving=false;
  if(!a.op&&a.ops.length){a.op=a.ops.shift();a.t=0;}
  const o=a.op;
  if(o){a.t+=dt;
   if(o.walk!=null||o.edge){const tx=o.walk!=null?o.walk:o.edge<0?-8:WIDTH[a.s]+8,d=tx-a.x;a.moving=Math.abs(d)>.5;if(a.moving)a.face=Math.sign(d);
    if(Math.abs(d)<=v){a.x=tx;if(o.edge){a.s+=o.edge;a.x=o.edge<0?WIDTH[a.s]+8:-8;}a.op=null;}else a.x+=Math.sign(d)*v;}
   else if(o.door){a.hidden=true;if(a.t>.65){a.hidden=false;if(o.door==='out')Object.assign(a,{w:'out',s:3,x:DOOR_OUT});else Object.assign(a,{w:'in',f:0,x:DOOR_IN});a.op=null;}}
   else if(o.stairs!=null){a.moving=true;a.climb=Math.min(1,a.t/1.6);a.face=1;if(a.climb>=1){a.f=o.stairs;a.climb=null;a.op=null;}}
   else if(o.leave){a.w='away';a.op=null;}else if(o.enter){Object.assign(a,{w:'out',s:0,x:-8});a.op=null;}
   return;}
  // arrived: sleep / pottering about a field / the errand
  const t=spotOf(a.k);a.sleep=t.pose==='sleep';
  if(t.stay!=null){a.stayed=(a.stayed||0)+dt;if(a.stayed>=t.stay){a.stayed=0;const e=errand[a.id];delete errand[a.id];e?.done?.();}return;}
  if(t.roam&&!a.wander){a.idle+=dt;if(a.idle>6+Math.random()*10){a.idle=0;a.wander={x:t.roam[0]+Math.random()*(t.roam[1]-t.roam[0])};}}
  if(a.wander){const d=a.wander.x-a.x;a.moving=Math.abs(d)>.5;if(a.moving){a.face=Math.sign(d);a.x+=Math.sign(d)*Math.min(Math.abs(d),v*.6);}else a.wander=null;}}
 let lastTick=realClock,wasIn=false;
 setInterval(()=>{try{const dt=Math.min(.25,Math.max(0,realClock-lastTick));lastTick=realClock;
  if(!inSpring()||!ready()){wasIn=false;return;}
  if(!wasIn){wasIn=true;snap(ag.mom);snap(ag.dad);return;}
  if(!speed)return;for(const a of Object.values(ag))step(a,dt);}catch(e){console.warn('parents walk',e);}},50);
 // compatibility: who is in the farmhouse (with the old shape {id,q:{x,tx,out},pose,k})
 function here(){if(!ready()||!inSpring())return [];const up=C().state.y<80?1:0;
  return Object.values(ag).filter(a=>a.w==='in'&&!a.hidden&&!a.sleep&&a.climb==null).map(a=>({id:a.id,q:{x:a.x,tx:a.op||a.wander?NaN:a.x,out:a.f!==up},pose:spotOf(a.k).pose||'stand',k:a.k}));}
 const sleeping=id=>inSpring()&&ready()&&ag[id].w==='in'&&ag[id].sleep&&!ag[id].op;
 // ---------------------------------------------------------------- drawing
 function drawWalker(ctx,a,feet){const t=spotOf(a.k),arrived=!a.op&&!a.wander,sit=arrived&&t.pose==='sit',s=C().state;
  const look=a.moving?a.face:arrived&&t.face?t.face:Math.sign(s.x-a.x)||1;
  const f={expr:sit?'happy':'neutral',look,bob:a.moving?Math.floor(realClock*5)%2:0,sway:a.moving?Math.floor(realClock*3)%2:0,wave:null};
  const p=sit?'sit':a.moving?['walkL','stand','walkR','stand'][Math.floor(realClock*6)%4]:'stand';
  ctx.drawImage(npcCanvas(npcOf(a.id),f,p,false),Math.round(a.x)-10,feet-27-(sit?(String(a.k).startsWith('settee')?5:3):0));
  if(arrived&&t.fx==='grain'){ctx.fillStyle='#e8cf7a';for(let i=0;i<4;i++){const u=(realClock*1.3+i/4)%1;ctx.fillRect(Math.round(a.x-6-u*10-i),Math.round(feet-14+u*13),1,1);}}
  if(arrived&&t.fx==='water'){ctx.fillStyle='#9cc8ef';for(let k=0;k<6;k++){const u=(realClock*1.6+k/6)%1;ctx.fillRect(Math.round(a.x-8-k*3),Math.round(feet-16+u*16),1,2);}}
  if(arrived&&t.fx==='weed'&&Math.floor(realClock*1.5+a.x)%4===0){ctx.fillStyle='#7aa35a';ctx.fillRect(Math.round(a.x+a.face*7),feet-4-Math.floor(realClock*6)%3,2,1);}}
 function drawIn(ctx){if(!ready())return;
  for(const a of Object.values(ag)){if(a.w!=='in'||a.hidden||(a.sleep&&!a.op))continue;
   const feet=a.climb!=null?FLOOR[1-a.op.stairs]+(FLOOR[a.op.stairs]-FLOOR[1-a.op.stairs])*a.climb:FLOOR[a.f];if(a.climb!=null)a.x=STAIR;drawWalker(ctx,a,Math.round(feet));}
  if(farmCny())drawCnyInside(ctx);}
 function drawOutside(ctx,info){if(!ready())return;for(const a of Object.values(ag))if(a.w==='out'&&!a.hidden&&a.s===info.region)drawWalker(ctx,a,103);}
 // 爸妈帮忙浇水 (infei_farm.js): the parent who is about walks to the bed and waters it
 function doErrand(id,spot,done){errand[id]={...spot,stay:spot.stay??2.4,done};}
 // a parent tells her something themselves (the help they gave this morning): when she is up and they are in sight,
 // or, if she has not run into them within an hour of being up, they call it across the yard anyway
 const tells=[];function tell(id,text){tells.push({id,text,at:sim.t});}
 setInterval(()=>{try{if(!tells.length||!inSpring()||!ready()||!speed||asleep()||talkQ.length||storyLocked()||cardHolds()||sim.mode==='down'||farmCny())return;
  if(typeof remoteSocial!=='undefined'&&remoteSocial)return;const i=tells.findIndex(t=>seen(ag[t.id])&&!ag[t.id].sleep||sim.t-t.at>60);if(i<0)return;
  const t=tells.splice(i,1)[0];talkQ.push([t.id,t.text],['me',pick(['好，谢谢'+(t.id==='mom'?'妈':'爸')+'！','知道啦','哇，那我省事了','嗯嗯，辛苦啦'])]);talkAt=0;}catch(e){console.warn('parents tell',e);}},700);
 // ---------------------------------------------------------------- clicks: a word with them
 const TALK={
  mom:{morning:['早饭在锅里，自己盛。','今天天好，被子拿出去晒晒。','鸡蛋我捡了，今天下了五个。','头发扎起来，干活方便。'],
   day:['菜地那边我看了，长得不错。','镇上的豆腐今天没买着，明天再去。','你那件外套扣子掉了，我给你缝上了。','别光顾着地里，水也要喝。','中午想吃面还是吃饭？'],
   evening:['晚上想吃啥？','灶上热着汤，喝一碗再睡。','你爸又在长椅上打盹了。','明天说是要下雨。','脚冷不冷？给你灌个热水袋。']},
  dad:{morning:['我去看看牛。','今天风大，帽子戴上。','你起得比我还早？'],
   day:['篱笆那边松了，下午我去钉钉。','井水凉，别一口气喝太多。','你那块地，草该拔了。','这牛脾气跟你小时候一样，犟。'],
   evening:['来，坐会儿。','这长椅是我修的，结实吧？','山里晚上真安静，虫子叫得清清楚楚。','明天早上我叫你，一起去镇上。','你妈做饭比城里饭馆好吃，你说是不是？']}};
 const REPLY=['好～','知道啦','嗯嗯','哈哈，好','我一会儿就去','真的吗？','爸妈最好了'];
 let talkQ=[],talkAt=0;
 const say=(who,text)=>{if(who==='me'){speak(text,true);return;}showSay(text,name(who)+'：',contact(who));};
 setInterval(()=>{if(!talkQ.length||!speed||realClock<talkAt||!inSpring())return;const [w,t]=talkQ.shift();say(w,t);talkAt=realClock+2.6;},200);
 function click(x,y,s){if(!ready())return false;
  const near=Object.values(ag).filter(a=>!a.hidden&&!(a.sleep&&!a.op)&&(s.inside?a.w==='in'&&y>FLOOR[a.f]-27&&y<FLOOR[a.f]:a.w==='out'&&a.s===s.scene&&y>103-27&&y<103)).map(a=>({id:a.id,q:{x:a.x}}));
  for(const {id,q}of near){if(Math.abs(x-q.x)>6)continue;
   const fc=farmCny();if(fc&&typeof CNY_TALK!=='undefined'){const m=mins(),pool=CNY_TALK[m<11*60?'morning':m<21*60?'day':'night'].filter(([w])=>w===id);const [,text]=pick(pool.length?pool:CNY_TALK.day);talkQ.unshift([id,text],['me',pick(CNY_REPLY)]);}
   else{if(typeof remoteSocial!=='undefined'&&remoteSocial){showHint('正在打电话，打完再聊');return true;}talkQ.length=0;talkQ.push(...liveTalk(id));}
   talkAt=0;if(sim.needs.social!=null)sim.needs.social=Math.min(100,sim.needs.social+6);return true;}
  return false;}
 // ---------------------------------------------------------------- 点爸妈：当场聊一段（owner 2026-11-10，茵菲谷专属，各 100 段）
 // '|' splits the lines, '~' marks hers, a leading {tag} limits when it fits (rain / dry / day / night / hot = summer)
 const LIVE={mom:["来，尝尝这个汤咸不咸。|~刚好。|那我就不加盐了，你爸口重，让他自己加。", "你头发是不是又长了？|~好像是。|镇上那家理发店换了个小伙子，手艺还行，改天去剪剪。", "今天鸡又不肯回窝，我追了半个院子。|~哈哈，那只花母鸡？|就是它，脾气跟你爸一样倔。", "你那双鞋底都磨平了吧。|~还能穿。|还能穿什么，走路都打滑，赶集给你买双新的。", "~妈，你在腌什么？|萝卜干，晒了三天了。|~闻着好香。|别偷吃，还没好。", "隔壁王婶家的狗生了，一窝五只。|~去看了吗？|看了，有只黑白的像戴了眼罩，你肯定喜欢。", "你吃饭了没？|~吃了。|吃的什么？|~……面包。|那不叫吃饭，锅里还有粥，自己盛。", "我跟你说，这个灶得先烧旺了再放锅。|~知道了。|知道了还每回都把锅烧糊。", "~妈，这个罐子是装什么的？|红糖，你小时候一感冒就给你冲一碗。|~我都忘了。|我记着呢。", "被子我给你换了薄的，晚上热就踢开。|~好。|别全踢了，后半夜凉。", "今天去镇上，碰见你小学同学了。|~谁啊？|那个扎两个辫子的，现在开了家奶茶店。|~真的？下次去喝。", "你爸今天又把我的花当草拔了。|~哈哈哈。|还笑，那是我养了一年的。", "~妈，晚上吃什么？|你想吃啥？|~都行。|“都行”最难做了，那就西红柿炒蛋。", "我织了个杯套，你看看。|~好看！|那给你，冬天捂手正好。", "你在城里自己做饭吗？|~偶尔。|偶尔是多偶尔？|~……一礼拜一回。|那得多练练。", "这茶是今年新采的，你闻闻。|~好清香。|山那边阿婆家的，她送了一小包。", "~妈，你手怎么了？|切菜划了一下，没事。|~贴个创可贴吧。|贴了，你看，小熊的。", "{dry}今天天好，被子都拿出去晒了。|~晚上肯定香。|那当然，太阳味儿。", "我给你缝了个香包，放枕头边。|~里面是什么？|艾草和薰衣草，睡得踏实。", "~妈，你看我这件衣服好看吗？|好看，就是薄了点。|~现在又不冷。|山里早晚凉，带件外套。", "你爸说想吃饺子，我一个人包不过来。|~我帮你。|你会捏边吗？|~……我学。", "今天的鸡蛋特别多，七个。|~鸡们心情好吧。|我喂了点玉米，它们就来劲了。", "你那盆花浇水别太勤，根会烂。|~我以为多浇点好。|跟人一样，喂太饱也不舒服。", "~妈，这个菜叫什么？|马齿苋，田埂上一大片，焯水凉拌好吃。|~原来能吃啊。|山里好多东西都能吃，你慢慢认。", "我前两天学会了用手机拍视频。|~拍什么了？|拍了一段鸡吃米，发家族群了，你二姨点了个赞。", "你小时候最爱吃我做的糖醋排骨。|~现在也爱。|那晚上做。", "{day}下午要下雨，衣服我先收了。|~好，我帮你叠。|你叠的我还得重叠，算了你去歇着。", "你看你，袖口又蹭了一块灰。|~刚才去仓库了。|脱下来我给你搓搓。", "~妈，你累不累？|累什么，活儿又不多。|~那你坐会儿。|行，坐会儿，你给我倒杯水。", "今天集上的桃子不错，买了一兜。|~我去洗。|洗完给你爸留两个大的。", "晚上蚊子多，蚊香我给你点上了。|~谢谢妈。|别离床太近，熏得慌。", "我听说你种的萝卜长得挺好。|~还行，就是有一块被虫咬了。|撒点草木灰，虫就不来了。", "~妈，咱家那只猫呢？|哪有猫，那是隔壁的，天天来蹭饭。|~那它叫什么？|我叫它“又来了”。", "你那件毛衣起球了，我给你剪剪。|~不用这么麻烦。|一会儿的事，脱下来。", "你说城里的菜贵不贵？|~挺贵的。|那走的时候多带点，家里吃不完。", "今天的米饭是用新米煮的。|~怪不得这么香。|新米就是这样，你多吃一碗。", "~妈，你年轻时候是什么样的？|跟你差不多，就是比你勤快。|~……|哈哈，逗你的。", "厨房那个水龙头有点漏，你跟你爸说一声。|~你怎么不说？|我说了三遍了，他听你的。", "你最近睡得好吗？|~挺好的，这边特别安静。|那就好，城里车多，吵得慌。", "这个南瓜我留着做南瓜饼。|~我想吃！|那你去帮我把面揉了。", "~妈，你包的粽子怎么这么好吃？|叶子是自己摘的，米泡了一夜。|~我学学。|明年端午教你。", "你别老坐着，起来走走。|~刚坐下……|刚坐下也得起来，腰不好。", "{dry}今天下午太阳好，我把你的书拿出来晒了晒。|~书也要晒？|放久了有霉味，晒晒就没了。", "~妈，鸡窝那边好像有动静。|又是黄鼠狼吧，你爸晚上去看看。|~我也去。|你别去，你一叫比鸡还响。", "你喝不喝绿豆汤？|~喝！|在井里镇着呢，自己去提。", "我把你小时候的照片翻出来了，一大本。|~让我看看。|你看这张，在澡盆里哭的。|~快收起来！", "晚上想吃啥，我提前泡上。|~想吃红豆粥。|那我现在就泡豆子。", "你那几件衣服我给你洗了，晾在后院。|~我自己洗就行。|顺手的事，你那洗衣机又不在这儿。", "~妈，你听说过山那边的瀑布吗？|听说过，你爸年轻时带我去过一回。|~远吗？|走过去得半天，你要去带够水。", "今天做了点酸梅汤，在冰箱里。|~太好了。|别一口气喝完，喝多了牙酸。", "你袜子破了个洞，我补上了。|~啊，谢谢。|补得不太好看，反正穿鞋里看不见。", "我想养几只鸭子，你觉得呢？|~好啊，鸭子可爱。|可爱什么，我是想吃鸭蛋。", "~妈，这件事你别告诉爸。|什么事？|~我把他的茶杯碰了个口子。|……你自己去说，他不会骂你。", "这几天风大，窗户关严实点。|~好。|昨晚我听见你屋窗户一直哐哐响。", "你喜欢吃辣的还是甜的？|~都喜欢。|跟你爸一样，什么都吃，好养活。", "今天剁了一上午馅，手都酸了。|~我给你捏捏。|轻点轻点……嗯，就这样。", "~妈，你怎么起这么早？|习惯了，鸡一叫就醒。|~那你中午睡一会儿。|嗯，中午眯一会儿。", "你那个手机老是响，谁找你？|~朋友发消息。|那你回人家啊，别让人等。", "今天给你做了个新菜，你猜是什么。|~闻着像……韭菜盒子？|哟，鼻子挺灵。", "咱家后头那棵枣树今年结得多。|~能打下来吗？|过阵子红了，叫你爸拿竹竿打。", "~妈，这个线团是干嘛的？|给你爸织围巾，织了半个月了。|~他知道吗？|不知道，你别说漏嘴。", "你看着瘦了。|~没有吧。|有，脸都尖了，多吃点。", "今天镇上有人卖小鸡仔，我差点又买了。|~买啊。|再买窝都住不下了。", "你那房间我收拾了一下，抽屉里东西没动。|~好，谢谢妈。|抽屉里那堆糖纸你还留着啊？", "{night}~妈，晚上想看星星吗？|看什么星星，冷。|~穿厚点就不冷了。|……行吧，就看一会儿。", "我做了点豆腐乳，你走的时候带一瓶。|~好啊。|别放太久，开了要放冰箱。", "你那个指甲该剪了。|~我自己会剪。|那就剪，别等我提醒。", "今天的菜你爸说淡了。|~我觉得刚好。|你俩口味就没对上过。", "~妈，你看我种的那排葱。|长得不错，就是太挤了。|~要拔一些吗？|拔一半，拔下来的晚上炒蛋。", "有个事我想问你，你别嫌我啰嗦。|~你说。|你在外面有没有被人欺负？|~没有啦。|那就好。", "你看这块布，做个围裙怎么样？|~花挺好看。|那给你也做一条，做饭别弄脏衣服。", "~妈，你最喜欢吃什么？|我啊……你做的我都喜欢。|~我又不会做。|那你就学着做。", "{rain}这雨下得好，地里不用浇了。|~那我今天干嘛？|歇着呗，难得。", "你爸今天又去河边了，说要钓条大的回来。|~上次钓了多大？|巴掌大，还说是“小的放了”。", "~妈，这个灯泡好像不亮了。|又坏了？去柜子里拿个新的，等你爸回来换。|~我会换。|那你小心点，先关开关。", "你吃不吃煮玉米？|~吃！|刚出锅，烫，晾一下。", "今天看你一直在地里，晒黑了。|~有吗？|有，脖子后头都红了，戴个帽子。", "我给你烙了几张饼，饿了就吃。|~好香。|葱油的，你小时候能吃三张。", "~妈，你会不会觉得这儿太安静？|不会啊，安静好。|~我以为你会想城里。|城里有什么好，买个菜都要排队。", "那几只鹅又跑到菜地里去了。|~我去赶。|拿根竹竿，它们咬人。", "你那件红外套哪去了？挺好看的。|~放城里了。|下次带来，山里穿红的显眼，好找你。", "我听你爸说你想多开一块地。|~嗯，想试试。|行，缺什么跟我说，种子我那儿还有。", "~妈，你做饭的时候哼什么歌？|我哼了吗？|~一直在哼。|……年轻时候的歌，你没听过。", "今天腌了一坛酸菜。|~闻着就酸。|过一个月才能吃，到时候做酸菜鱼。", "你晚上别看手机太晚，眼睛要坏。|~就看一会儿。|你那一会儿我知道，两个钟头。", "~妈，咱家有针线吗？|有，抽屉第二层。怎么了？|~扣子掉了。|拿来，我给你缝。", "今天给鸡窝铺了新稻草，鸡都不愿意出来了。|~太舒服了吧。|跟你一样，被窝里赖着。", "你看后山那片云，像不像只兔子？|~像！耳朵都有。|你小时候也爱看云，一看半天。", "~妈，你有没有想去的地方？|想去海边看看。|~那我带你去！|好啊，等地里活儿忙完的。", "这个菜你多吃点，补眼睛的。|~胡萝卜吗？|对，你天天看手机，得补补。", "晚上我跟你爸要去王婶家坐坐。|~我也去吗？|你想去就去，她老念叨你。", "~妈，你记得我小时候怕什么吗？|怕打雷，一打雷就往我被窝里钻。|~现在不怕了。|那今晚打雷你别过来。", "~妈，我帮你剥蒜吧。|好，剥一头就够，别剥多了。|~剥完手好臭。|拿柠檬搓搓就没味了。", "你爸那件衬衫领子又磨破了，我给他翻个面。|~还能翻？|翻过来又能穿两年。", "~妈，你怎么知道我回来了？|听脚步声，你走路跟小时候一样，噔噔噔的。", "今天去井边打水，碰见一只小刺猬。|~真的？在哪？|往竹林那边钻了，晚上可能还会出来。", "你把这碗汤给你爸端过去。|~他在哪？|牛棚，喊他吃饭他老不来。", "~妈，这个枕头怎么这么软？|新弹的棉花，你试试。|~像躺在云上。|那今晚早点睡。", "我想在院子里种棵桂花，你说种哪儿好？|~门口吧，一进门就香。|嗯，你跟我想到一块了。", "你别光顾着地里，也去村里转转，认识认识人。|~我不认识谁啊。|去王婶家，她嘴碎，一会儿全村你都认识了。"],dad:["来，帮我扶一下这块板。|~好。|往左点……行，别动。", "牛今天吃了两捆草。|~它胃口真好。|干活的嘛。", "~爸，你在修什么？|篱笆，松了。|~要帮忙吗？|你递钉子。", "你那块地，草该拔了。|~我明天拔。|今天拔，明天又长了。", "天要变了。|~你怎么知道？|膝盖疼。", "~爸，喝茶吗？|喝。|~要放糖吗？|茶放什么糖。", "这锄头你用着顺手吗？|~有点沉。|我给你磨磨，换个短把。", "晚上别出去乱走，山里黑。|~我拿手电。|拿手电也别走远。", "~爸，你看这只鸟。|那是喜鹊。|~好看。|它天天来偷鸡食。", "你妈又说我把她花拔了。|~你拔了吗？|我以为是草。", "~爸，今天钓到鱼了吗？|钓到了。|~多大？|……一条小的，放了。", "井水凉，别一口气喝太多。|~嗯。|肚子疼了又得你妈熬姜汤。", "这把椅子我修好了，你坐坐。|~还挺稳。|那当然，加了根木条。", "~爸，你年轻时候干嘛的？|种地。|~一直种地？|还开过拖拉机，后来卖了。", "牛棚的灯坏了，晚上我去换。|~我帮你照着。|行。", "你那双手套哪来的？|~镇上买的。|太薄，戴我那双，厚。", "~爸，这是什么树？|核桃树，你爷爷种的。|~这么老了？|比我岁数都大。", "下回进城给我带包烟丝。|~妈不让你抽。|……那就带包茶叶。", "来，下盘棋。|~我不太会。|我教你，马走日。", "~爸，你看我挖的沟直不直？|歪了。|~哪里歪了？|你蹲下来看。", "{hot}这天热，中午别下地。|~那什么时候去？|傍晚，凉快。", "~爸，咱家鸡有名字吗？|没有。|~我给起几个？|随你，它们也听不懂。", "你把那桶水拎过来。|~好重。|两只手拎，别闪了腰。", "~爸，那个铁家伙是什么？|播种机，坏了好几年了。|~还能修吗？|修过三回，算了。", "你妈做饭的时候别进厨房。|~为什么？|她嫌碍事。", "今天镇上的豆腐不错，买了两块。|~妈说晚上做麻婆豆腐。|那多放辣。", "~爸，你听说后山有野猪吗？|有，前年拱了人家一亩地。|~那咱家的地呢？|有我在，不怕。", "这扫帚用秃了，明天编个新的。|~你会编？|你爷爷教的。", "~爸，你看我这个筐编得怎么样？|……漏。|~哪里漏了？|底下，这儿，手指头都能伸进去。", "你冷不冷？|~还好。|穿我那件褂子，挂门后头。", "{rain}~爸，雨停了，我去看看地。|去吧，水沟要是堵了掏一掏。|~知道啦。", "那头牛今天不肯走，跟我犟了半天。|~后来呢？|给了它一把豆子。", "~爸，这个钉子怎么老弯？|你锤子拿歪了。|~那怎么拿？|手往后握，看准了再敲。", "你小时候在这儿摔过一跤，门牙磕掉一颗。|~我不记得了。|你哭得全村都听见了。", "~爸，你喜欢城里吗？|不喜欢，挤。|~那你上次去待了几天？|三天，最后一天就想回了。", "来，尝尝我泡的酒。|~我不喝。|就舔一口，梅子的，甜。", "~爸，牛今天好像不太高兴。|它跟隔壁那头吵架了。|~牛还会吵架？|会，顶了半天角。", "柴火够不够烧？|~够吧。|我明天再劈点，冬天要用。", "~爸，我能骑一下牛吗？|它不让人骑。|~你试过？|……试过，被它甩下来了。", "你那个车子气不足了，我给你打一下。|~谢谢爸。|别骑太快，下坡刹着点。", "{night}~爸，今天晚上有月亮吗？|有，挺亮的。|~那出去看看？|搬两把椅子到院里。", "这锅底要刷干净，不然下回煮饭有糊味。|~妈刷的。|那就是你妈没刷干净，别说是我说的。", "~爸，你会做饭吗？|会煮面。|~就面？|还会煎蛋。", "刮风了，把晾的东西收收。|~我去收。|那件白的轻，别让风吹跑了。", "~爸，这边晚上怎么这么多虫叫？|蛐蛐，天暖和就这样。|~吵得睡不着。|听惯了就睡得香。", "你有空去看看那几棵果树，有没有生虫。|~怎么看？|叶子背面，有白点就是。", "~爸，你看我抓的这只蚂蚱。|放了吧，地里还指望它们……不对，它吃庄稼，扔远点。|~哈哈。", "你那桶颜料别放太阳底下，会干。|~知道了。|上回干了一桶，你妈心疼半天。", "~爸，咱家房子多少年了？|三十多年，我跟你妈结婚那年盖的。|~自己盖的？|一砖一瓦。", "吃饭别看手机。|~就看一眼。|一眼看了十分钟。", "~爸，那边那个山叫什么？|老鹰岭。|~有老鹰吗？|以前有，现在少了。", "屋顶有块瓦松了，下雨前得上去换。|~你小心点。|爬了几十年了。", "~爸，你说我种什么最赚钱？|西瓜，就是费工夫。|~那种什么省事？|萝卜，扔下去就长。", "这水壶的把松了，拿来我紧紧。|~好。|螺丝刀给我。", "~爸，你看我挑的这个西瓜熟没熟？|拍拍。|~咚咚的。|熟了，切。", "晚上我去巡一圈，你锁好门。|~巡什么？|看看鸡窝，看看牛。", "~爸，你年轻时候帅吗？|问你妈。|~妈说一般。|……她骗你的。", "这锄头把上的漆掉了，别扎手。|~我戴手套。|嗯。", "~爸，镇上有修手机的吗？|有一家，老李开的。|~靠谱吗？|修过我那个，修完响铃声音变大了。", "你那几块地，下礼拜该追肥了。|~追什么肥？|鸡粪，后头那堆，捂了半年了。", "~爸，你怎么不爱说话？|说什么。|~随便说说呗。|……今天天挺好。", "牛圈那个门你出来记得关。|~我关了啊。|上次牛跑到你妈菜园里去了。", "~爸，这个草帽给你。|哪来的？|~集上买的。|嗯，挺好，比我那顶强。", "今天来了个收山货的，问咱家有没有蘑菇。|~有！我种的。|那下回卖给他。", "~爸，你教我编筐吧。|行，先学劈竹篾。|~会不会划手？|会，所以戴手套。", "{day}你看那片云，下午要下雨。|~那我把种子先收进屋。|嗯，抓紧。", "~爸，你觉得我在这儿干得怎么样？|还行。|~就还行？|比我当年强。", "这把刀磨好了，切菜的时候小心。|~好。|刀口别朝自己。", "~爸，牛吃不吃西瓜皮？|吃，它最爱。|~那我拿去喂。|别喂太多，拉肚子。", "你那个水管别乱扔，压坏了漏水。|~我卷起来。|卷整齐点。", "~爸，你看我堆的柴火。|……挺像样。|~真的？|就是要往里收一收，不然会倒。", "你明天早点起，跟我去镇上拉化肥。|~几点？|五点。|~……这么早？", "~爸，你说今年能丰收吗？|看天。|~天说什么？|天不说话。", "这个老收音机还能响，你听听。|~好有年代感。|你爷爷的，天天听戏。", "~爸，你怕不怕蛇？|不怕，草里见了绕开就是。|~我怕。|那走路拿根棍子打打草。", "你妈今天不太舒服，晚饭你做。|~我？|我帮你烧火。", "~爸，你那个旧皮带好帅。|当兵时候的。|~你当过兵？|两年，没跟你说过？", "那几只鹅又欺负鸡了。|~怎么办？|分开养，我明天再搭个棚。", "{night}~爸，你看天上那颗最亮的星。|那是金星，傍晚最亮。|~你懂好多。|老看天，看多了就懂了。", "这个梯子有一阶坏了，别踩第三阶。|~好。|我明天修。", "~爸，咱家能养只狗吗？|能，看门正好。|~那去哪找？|王婶家刚生了一窝。", "你那几块地种得不赖。|~真的？|比隔壁老张家的齐整。", "~爸，这个桶为什么底下有个洞？|那是漏桶，浇花用的。|~我还以为坏了。|没坏，故意的。", "{rain}下雨了，鸡还在外头，赶进来。|~它们不听我的。|撒把米，它们就跟你走了。", "~爸，你想吃什么，我给你做。|面。|~就面？|多放个蛋。", "你那块地边上种排向日葵，好看。|~你也喜欢花？|……你妈喜欢。", "~爸，牛有名字吗？|有，叫大黄。|~它是黑的啊。|小时候是黄的。", "今天风大，你别去河边。|~我就看看。|看看也别去，水急。", "~爸，这把锁怎么打不开？|往里推一下再拧。|~开了！|这锁跟我一样，得顺着来。", "晚上蚊子多，我在门口挂了艾草。|~管用吗？|你妈说管用，我觉得一般。", "~爸，你会不会想我？|……会。|~想我什么？|想你小时候在院里跑，摔了也不哭。", "~爸，你帮我看看这个锄头是不是钝了。|拿来。……是钝了，磨磨。|~我来磨。|斜着磨，别磨平了。", "你把那袋土豆搬到地窖去。|~好重！|弯腿，别弯腰。", "~爸，你钓鱼的时候想什么？|不想什么。|~那多无聊。|就是不想什么才好。", "今天在镇上碰见你小学老师了，问你呢。|~问我什么？|问你还画不画画。", "~爸，你看我的新草帽。|挺好，就是绳子太短，风一吹就掉。|~那怎么办？|我给你换根长的。", "你那块地边的石头，我帮你搬走了。|~哪块？|大的那块，绊了你两回了。", "~爸，我想给牛刷刷毛。|行，用那把硬刷子，它喜欢。|~它会踢我吗？|别站它屁股后头就不会。", "晚上吃完饭陪你妈散会儿步，她爱念叨你不陪她。|~那你呢？|我去巡牛棚。", "~爸，你笑起来挺好看的，干嘛老板着脸。|……谁板着脸了。|~你现在就板着。|吃你的饭。"]};
 function liveFits(t){const m=/^\{(\w+)\}/.exec(t);if(!m)return true;const h=mins()/60,rain=typeof weather!=='undefined'&&(weather.kind==='rain'||weather.kind==='storm');
  return {rain,dry:!rain,day:h>=7&&h<17,night:h>=18||h<5,hot:springFarm.seasonAt(today())===1}[m[1]]??true;}
 function liveTalk(id){const pool=LIVE[id],seen=((lifeFlags.parentTalkSeen||={})[id]||=[]);
  let ok=pool.map((t,i)=>i).filter(i=>!seen.includes(i)&&liveFits(pool[i]));if(!ok.length){seen.length=0;ok=pool.map((t,i)=>i).filter(i=>liveFits(pool[i]));}
  const i=pick(ok);seen.push(i);return pool[i].replace(/^\{\w+\}/,'').split('|').map(l=>l.startsWith('~')?['me',l.slice(1)]:[id,l]);}
 X.hooks.click.unshift(click);
 // ---------------------------------------------------------------- 爸妈自己找她说话（owner 2026-11-10：在家要有来有回）
 // when she is in the house with one of them and nothing else is going on, every hour or so one of them starts a little chat
 const CHATS=[
  ['mom','今天地里累不累？',['me','还行，就是腰有点酸'],['mom','晚上给你贴块膏药。']],
  ['mom','你小时候最怕那只大白鹅，还记得吗？',['me','它追了我半个村子！'],['mom','哈哈，后来它见你就跑了。']],
  ['mom','城里那边房租贵不贵？',['me','还行，能付得起'],['mom','不够就说，家里有。']],
  ['mom','隔壁婶子问你有没有对象。',['me','妈——'],['mom','我就说你忙，没空想这个。']],
  ['mom','这菜是你种的那块地里的吧？',['me','嗯，今早刚摘的'],['mom','嫩，炒着好吃。']],
  ['mom','你那几个朋友，有空叫来家里玩。',['me','他们说想来看看牛'],['mom','那我多蒸一屉包子。']],
  ['mom','衣服给你洗了，晾在后院。',['me','我自己洗就行'],['mom','顺手的事。']],
  ['mom','鸡今天又少下了一个蛋。',['me','是不是被黄鼠狼惦记上了'],['dad','我晚上去看看鸡笼。']],
  ['mom','尝尝这个咸菜，今年腌得好。',['me','嗯，下饭！'],['mom','走的时候带一罐。']],
  ['mom','你手机老看，眼睛要看坏了。',['me','我就看一会儿'],['mom','一会儿是多久？']],
  ['mom','下礼拜镇上有集，去不去？',['me','去！想吃那家糖糕'],['mom','那早点起。']],
  ['mom','这几天睡得好不好？',['me','山里安静，睡得香'],['mom','那就多住几天。']],
  ['dad','来，看看我新编的筐。',['me','爸你手真巧'],['dad','你爷爷教的，比我编得还好。']],
  ['dad','牛今天吃了两捆草，胃口真好。',['me','比我还能吃'],['dad','那可不，它干的活也多。']],
  ['dad','你那块地垄沟挖浅了，下雨要积水。',['me','那明天我再挖挖'],['dad','我跟你一起。']],
  ['dad','今年的柿子挂得多。',['me','能做柿饼吗？'],['dad','能，等霜降了晒。']],
  ['dad','城里住得惯不惯？',['me','还行，就是有点吵'],['dad','吵了就回来，山里安静。']],
  ['dad','你看这天，明天准下雨。',['me','你怎么知道？'],['dad','山那边起云了，八九不离十。']],
  ['dad','老屋那根梁该换了。',['me','要我帮忙吗'],['dad','你递钉子就行。']],
  ['dad','你小时候爬那棵枣树，下不来哭了一下午。',['me','这事能不能别提了'],['dad','哈哈，好好，不提。']],
  ['dad','镇上新开了家修车铺。',['me','咱家又没车'],['dad','先认识认识，以后用得上。']],
  ['dad','喝茶不？今年的新茶。',['me','来一杯'],['dad','烫，慢点喝。']],
  ['dad','你妈今天念叨你一上午。',['me','念叨我啥？'],['dad','说你瘦了。']],
  ['dad','晚上风凉，窗户我关小点。',['me','好，谢谢爸']]];
 const TOPICS={morning:[0,4,6,10,13,16,21],day:[2,3,5,7,8,9,12,14,15,17,18,20],evening:[1,3,5,9,11,15,19,22,23]};
 let chatAt=sim.t+30;const used=[];
 setInterval(()=>{try{
  if(!inSpring()||!ready()||!speed||talkQ.length||sim.t<chatAt)return;const s=C().state;
  if(!s.inside||asleep()||storyLocked()||cardHolds()||ringOf||sim.mode==='down'||farmCny()||typeof remoteSocial!=='undefined'&&remoteSocial)return;
  if(['bath','toilet','season_shower','sleep'].includes(sim.act))return;
  const by=here().filter(p=>!p.q.out&&Math.abs(p.q.x-p.q.tx)<1).map(p=>p.id);if(!by.length)return;
  const m=mins(),pool=TOPICS[m<9*60?'morning':m<18*60?'day':'evening'].filter(i=>by.includes(CHATS[i][0])&&CHATS[i].slice(1).every(l=>!Array.isArray(l)||l[0]==='me'||by.includes(l[0]))&&!used.includes(i));
  chatAt=sim.t+50+Math.random()*40;if(!pool.length){used.length=0;return;}
  const i=pick(pool);used.push(i);if(used.length>12)used.shift();const c=CHATS[i];
  talkQ.push([c[0],c[1]],...c.slice(2));talkAt=0;sim.needs.social=Math.min(100,sim.needs.social+8);
 }catch(e){console.warn('parents chat',e);}},1000);
 // with them in the house: social slowly fills (as with guests at home)
 let lastT=sim.t;setInterval(()=>{const dt=Math.max(0,Math.min(30,sim.t-lastT));lastT=sim.t;if(!inSpring()||!C().state.inside||asleep()||!here().length)return;sim.needs.social=Math.min(100,sim.needs.social+dt*(farmCny()?.12:.05));},500);
 // ================================================================ 春节 in 茵菲谷
 // the main world's CNY_STEPS, played in the farmhouse; where: the parents' places for each step, act: her furniture
 const STEP_AT={arrive:{mom:'kitchen',dad:'tableR'},couplets:{},dumplings:{mom:'stove',dad:'tableR'},lunch:{mom:'tableL',dad:'tableR'},
  envelope:{mom:'setteeL',dad:'setteeR'},questions:{mom:'setteeL',dad:'setteeR'},feast:{mom:'tableL',dad:'tableR'},gala:{mom:'setteeL',dad:'setteeR'},countdown:{mom:'setteeL',dad:'setteeR'},bedtime:{mom:'kitchen',dad:'kitchen'}};
 const STEP_USE={arrive:'in',couplets:'out',dumplings:'stove',lunch:'table',envelope:'settee',questions:'settee',feast:'table',gala:'settee',countdown:'settee'};
 const fc={day:null,done:new Set(),gone:false,couplets:false};
 // it is 春节 and she spends it here (not if the city flat already had them over this morning)
 function farmCny(){if(typeof CNY_STEPS==='undefined'||!ready())return null;
  const fest=festName()==='春节',d=today(),late=fc.day===d-1&&mins()<60;if(!fest&&!late)return null;
  const base=fest?d:d-1;
  if(fc.day!==base){if(!inSpring())return null;if(cny.day===base&&cny.done.size&&!cny.farm)return null;
   Object.assign(fc,{day:base,done:new Set(),gone:false,couplets:false});for(const k of Object.keys(cny.v||{}))if(k.startsWith('farm:'))delete cny.v[k];}
  cny.day=base;cny.gone=true;cny.farm=true;cny.v||={};   // the city flat has nobody this year
  const m=sim.t-base*1440;if(fc.gone||m<CNY_STEPS[0].at)return null;
  const last=[...CNY_STEPS].reverse().find(s=>m>=s.at);return {step:last,where:STEP_AT[last.id]||{}};}
 function runStep(step,live){
  if(step.id==='couplets')fc.couplets=true;if(step.leave)fc.leaving=true;
  if(!live)return;
  const v={...step,...cnyVariant(step,'farm')};
  const u=STEP_USE[step.id],c=C();
  if(u&&!asleep()&&sim.mode!=='down'&&!['bath','toilet'].includes(sim.act)){
   seasonMapTest.state.autoAt=sim.t+60;   // the family's moment: no wandering off
   if(u==='out'){if(c.state.inside)c.leave();}else if(u==='in'){if(!c.state.inside)X.hooks.pick.indoor();}else infeiHome.use(u,true);}
  talkQ.push(...v.lines.map(([w,t])=>[w,t]));
  const said=v.lines.map(([w,t])=>[(w==='me'?nameOf():name(w))+'：',t]);if(v.diary)log(v.diary,null,said);
  if(step.mood)addMood(step.mood,{words:false});addMood('cnyFamily',{words:false,diary:false});
  if(step.envelope)fc.envelopeUntil=realClock+6;}
 setInterval(()=>{try{const f=farmCny();if(!f||!inSpring()||!speed)return;const m=sim.t-fc.day*1440;
  const due=CNY_STEPS.filter(s=>m>=s.at&&!fc.done.has(s.id));due.forEach((s,i)=>{fc.done.add(s.id);runStep(s,i===due.length-1&&m-s.at<50);});
  if(fc.leaving&&!talkQ.length&&realClock>talkAt+2)fc.gone=true;}catch(e){console.warn('farm cny',e);}},500);
 // the couplets step: they stand at the front door outside
 function drawOut(ctx,info){drawOutside(ctx,info);if(info.region!==HOME)return;
  if(fc.couplets&&fc.day!=null&&today()-fc.day<=1)drawCouplets(ctx);
  const f=farmCny();
  if(f&&mins()>=19*60)fireworks(ctx);}
 function drawCouplets(ctx){ctx.fillStyle='#c8312f';ctx.fillRect(169,66,3,30);ctx.fillRect(192,66,3,30);ctx.fillRect(172,62,20,3);
  ctx.fillStyle='#f2b33d';for(let k=0;k<5;k++){ctx.fillRect(170,70+k*5,1,1);ctx.fillRect(193,70+k*5,1,1);}for(let k=0;k<4;k++)ctx.fillRect(175+k*4,63,1,1);
  ctx.fillStyle='#c8312f';ctx.fillRect(179,72,7,7);ctx.fillStyle='#f2b33d';ctx.fillRect(181,74,3,3);}
 function fireworks(ctx){const W=ctx.canvas.width;
  for(let k=0;k<3;k++){const per=2.4+k*.7,n=Math.floor((realClock+k)/per),u=((realClock+k)%per)/per,h=(a,b)=>((Math.sin(n*12.9898+a*78.233+b)*43758.5453)%1+1)%1;
   const cx=30+h(k,1)*(W-60),cy=12+h(k,2)*30,r=2+u*12,a=(1-u),col=['255,120,120','255,214,110','140,220,255','200,150,255'][(n+k)%4];
   ctx.fillStyle=`rgba(${col},${a.toFixed(2)})`;for(let i=0;i<12;i++){const th=i/12*6.283;ctx.fillRect(Math.round(cx+Math.cos(th)*r),Math.round(cy+Math.sin(th)*r+u*4),1,1);}}}
 // red lanterns and a 福 in the farmhouse, the envelope over her head
 function drawCnyInside(ctx){for(const x of [60,150,240,300]){ctx.fillStyle='#5e5b71';ctx.fillRect(x,62,1,3);ctx.fillStyle='#c8312f';ctx.fillRect(x-2,65,5,5);ctx.fillStyle='#e0534d';ctx.fillRect(x-1,65,3,1);ctx.fillStyle='#f2b33d';ctx.fillRect(x,70,1,2);}
  if(realClock<(fc.envelopeUntil||0)){const s=C().state,u=1-(fc.envelopeUntil-realClock)/6,x=Math.round(s.x)-3,y=Math.round(s.y-27-10-Math.min(1,u*4)*4);
   ctx.fillStyle='#c8312f';ctx.fillRect(x,y,7,9);ctx.fillStyle='#e0534d';ctx.fillRect(x+1,y+1,5,1);ctx.fillStyle='#f2b33d';ctx.fillRect(x+2,y+4,3,2);}}
 X.hooks.draw.push((ctx,info)=>{try{if(info.inside)drawIn(ctx);else drawOut(ctx,info);}catch(e){console.warn('season parents',e);}});
 // 春节 morning: no farm chores pulling her away from the family
 // ================================================================ 人脉 → 拜访爸妈 = fly to 茵菲谷
 const canFly=()=>F().unlocked&&ready();
 function goSee(c){
  if(sim.place==='spring_test'){showHint(`${name(c.id)}就在家里呢`);return true;}
  if(!canFly())return false;
  if(sim.mode==='down'||asleep()||wiping||cardHolds()||socialState.guest||friendVisit||friendOutingState){showHint('先忙完眼前的事情，再去看爸妈吧。');return true;}
  visit={day:null,pending:true};log(`想爸妈了，去茵菲谷看看他们。`);showSay(pick(['好久没见爸妈了，去茵菲谷看看！','去茵菲谷，给爸妈一个惊喜。']));
  closeSocialSheet?.();setContactsOpen?.(false);closeRing();
  if(window.airportTravel){throughDoor('airport_test');const t0=Date.now(),step=()=>{if(Date.now()-t0>30000)return;
    if(sim.place==='airport_test'&&!wiping&&!airportTravel.flight.busy){airportTravel.walkTo(283,()=>ringPick('airport:spring'));return;}setTimeout(step,300);};setTimeout(step,600);}
  else throughDoor('spring_test');
  return true;}
 const oVisit=requestFriendVisit;requestFriendVisit=function(id){const c=socialState.contacts.find(c=>c.id===id);if(c?.family&&goSee(c))return true;return oVisit.apply(this,arguments);};
 const oActs=openContactActions;openContactActions=function(id){const r=oActs.apply(this,arguments);const c=socialState.contacts.find(c=>c.id===id);
  if(c?.family&&canFly()&&!['summer_test','spring_test'].includes(sim.place)){const b=contactActions.querySelector('[data-action=visit]');
   if(b){b.removeAttribute('aria-disabled');b.title='爸妈住在茵菲谷，坐飞机过去';b.setAttribute('aria-label','拜访：'+b.title);b.querySelector('small')&&(b.querySelector('small').textContent='去茵菲谷');}}
  if(c?.family&&sim.place==='spring_test'){const b=contactActions.querySelector('[data-action=visit]');if(b){b.setAttribute('aria-disabled','true');b.title='就在家里呢';b.querySelector('small')?.remove();}}
  return r;};
 // arrived: both home all day, at the door to meet her
 const oArrive=arriveAt;arriveAt=function(p){const r=oArrive.apply(this,arguments);
  if(p==='spring_test'&&visit?.pending){visit={day:today()};setTimeout(()=>{if(!inSpring())return;if(ready()&&!C().state.inside)X.hooks.pick.indoor();talkQ.push(['mom',pick(['来啦！路上累不累？','哎呀，怎么突然回来了，也不说一声！','正念叨你呢，你就到了。'])],['dad',pick(['我去杀只鸡。','屋里坐，外头风大。','行李给我。'])],['me',pick(['想你们了嘛！','回来看看你们～','饿了！'])]);
   log('飞到茵菲谷，爸妈都在家。');addSocialMemory?.(contact('mom'),'回茵菲谷看爸妈','坐飞机去茵菲谷，爸妈都在家等着。');},1800);}
  return r;};
 window.seasonParents={plan,here,farmCny,goSee,sleeping,doErrand,tell,walkers:ag,get visit(){return visit;}};
})();
