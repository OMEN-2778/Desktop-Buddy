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
 const AT={stove:[262,'stand'],jar:[300,'stand'],tableL:[200,'sit'],tableR:[216,'sit'],setteeL:[100,'sit'],setteeR:[126,'sit'],door:[60,'stand'],kitchen:[240,'stand']};
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
  // owner 2026-11-14: the sofa seats three (she sits in the middle), and on some days they watch television:
  // after lunch for a while, and now and then in the afternoon
  if(m>=13*60+30&&m<14*60+30&&today()%3!==1){o.dad='setteeR';if(today()%2)o.mom='setteeL';}
  if(m>=15*60+30&&m<16*60+40&&today()%4===2){o.mom='setteeL';o.dad='setteeR';}
  return o;}
 // ================================================================ 爸妈像她一样真的走动（owner 2026-11-12：不要闪现）
 // Each parent is a little walker with a place in the valley (in the farmhouse on a floor, out in a field, or gone to town).
 // The day's plan names a spot; they walk there the way she does: across the room, up the stairs (x 61), through the door
 // (inside x 51 / the yard x 182), field to field over the scene edges, off the brook's left edge to town and back.
 const WIDTH=[342,342,342,342,342,684],FLOOR=[108,50],STAIR=61,DOOR_IN=51,DOOR_OUT=182;
 const SPOT={stove:{in:1,f:0,x:262},jar:{in:1,f:0,x:300},tableL:{in:1,f:0,x:200,pose:'sit'},tableR:{in:1,f:0,x:216,pose:'sit'},
  setteeL:{in:1,f:0,x:100,pose:'sit',face:1},setteeR:{in:1,f:0,x:126,pose:'sit',face:1},kitchen:{in:1,f:0,x:240},
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
 // someone is sitting on the sofa in front of the television (the set is on for them)
 const watching=()=>inSpring()&&ready()&&Object.values(ag).some(a=>a.w==='in'&&!a.op&&!a.wander&&String(a.k).startsWith('settee'));
 const sleeping=id=>inSpring()&&ready()&&ag[id].w==='in'&&ag[id].sleep&&!ag[id].op;
 // ---------------------------------------------------------------- drawing
 function drawWalker(ctx,a,feet){const t=spotOf(a.k),arrived=!a.op&&!a.wander,sit=arrived&&t.pose==='sit',s=C().state;
  const look=a.moving?a.face:arrived&&t.face?t.face:Math.sign(s.x-a.x)||1;
  const f={expr:sit?'happy':'neutral',look,bob:a.moving?Math.floor(realClock*5)%2:idleBreath.bob(a.id==='mom'?.6:1.3),sway:a.moving?Math.floor(realClock*3)%2:0,wave:null};
  if(!a.moving&&idleBreath.blink(a.id==='mom'?1.1:2.7))f.expr='blink';
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
  const t=tells.splice(i,1)[0];talkQ.push([t.id,t.text],['me',pick(['好，谢谢'+(t.id==='mom'?'妈':'爸')+'！','知道啦','啊，那我省事儿了','哦哦，辛苦啦'])]);talkAt=0;}catch(e){console.warn('parents tell',e);}},700);
 // ---------------------------------------------------------------- clicks: a word with them
 const TALK={
  mom:{morning:['早饭在锅里呢，自个儿盛啊。','今儿天好，把被子抱出去晒晒。','鸡蛋我捡了，今儿下了五个。','头发扎起来，干活儿利索。'],
   day:['菜地我去瞅了，长得不赖。','今儿镇上豆腐没买着，明儿再去。','你那外套扣子掉了，我给你钉上了啊。','甭光顾着干活儿，喝口水。','晌午想吃面条还是米饭？'],
   evening:['晚上想吃啥？','灶上热着汤呢，喝一碗再睡。','你瞅你爸，又在沙发上打盹儿了。','明儿说是有雨。','脚冷不冷？给你灌个暖水袋吧。']},
  dad:{morning:['我去瞅瞅牛。','今儿风大，把帽子戴上。','哟，起得比我还早？'],
   day:['篱笆那头松了，后晌我去钉钉。','井水凉，甭一气儿喝太多。','你那块地，草该薅了啊。','这牛今儿又犟上了。'],
   evening:['来，坐会儿。','这电视还是你妈非要买的。','夜里凉，窗户关上点儿。','明儿早上我喊你，一块儿上镇上。','你妈做的饭，比城里馆子强吧？']}};
 const REPLY=['好嘞','知道啦','嗯嗯','哈哈，行','我一会儿就去','真的啊？','哦哦，好'];
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
 const LIVE={mom:["来，尝尝这汤咸不咸。|~嗯……正好。|那我就不搁盐了。你爸口重，让他自个儿加去。", "你这头发是不是又长了啊？|~好像是有点儿。|镇上理发店新来了个小伙子，剪得还行，哪天去拾掇拾掇。", "今儿那鸡又不回窝，撵得我满院子跑。|~是不是那只花母鸡啊？|可不就是它嘛，倔得很。", "你那双鞋，底儿都磨平了吧。|~还能穿呢。|还穿啥呀，走道都打滑。赶集给你买双新的。", "~妈，你腌啥呢？|萝卜干，晒了三天了。|~闻着好香啊。|哎别动，还没腌好呢。", "隔壁你王婶家的狗下崽了，一窝五只。|~你去看啦？|看了。有只黑白花的，你见了准喜欢。", "吃饭了没？|~吃了。|吃的啥？|~……面包。|那能叫饭啊？锅里有粥，自个儿盛去。", "我跟你说啊，这灶得先烧旺了再坐锅。|~知道了知道了。|知道了还回回给我烧糊。", "~妈，这罐子里装的啥啊？|红糖。你小时候一感冒，我就给你冲一碗。|~是吗，我都不记得了。|你那会儿才多大。", "被子给你换了床薄的，夜里热就蹬开点儿。|~好。|也别全蹬了啊，后半夜凉。", "今儿上镇上，碰见你小学同学了。|~谁啊？|就扎俩小辫儿那个，人家现在开奶茶店了。|~真的啊？那我下回去喝一杯。", "你爸今天又把我的花当草给拔了。|~哈哈哈哈。|你还笑！我养了一年多呢。", "~妈，晚上吃啥啊？|你想吃啥？|~都行。|又是都行。那就西红柿炒鸡蛋吧。", "我钩了个杯套，你瞅瞅。|~挺好看的啊。|那给你了，天冷了套杯子上不烫手。", "你在城里自个儿做饭不？|~偶尔吧。|偶尔是多久一回啊？|~……一礼拜一回？|那哪儿行，在家多练练。", "这茶是今年的新茶，你闻闻。|~嗯，香。|山那头阿婆给的，就给了一小包。", "~妈，你手咋了？|切菜划了一下，没事儿。|~贴个创可贴吧。|贴了贴了，你看。", "{dry}今儿天好，被子我都抱出去晒了。|~那晚上盖着舒服。|可不嘛，晒过的就是不一样。", "给你缝了个香包，搁枕头边上吧。|~里头装的啥啊？|艾草。闻着好睡。", "~妈，我这件衣服好看不？|好看是好看，就是薄了点儿。|~现在又不冷。|山里早晚凉，出门带件外套啊。", "你爸说想吃饺子，我一个人包不过来。|~我帮你包呗。|你会捏边儿不？|~呃……不太会。|那你擀皮儿吧。", "今儿鸡蛋捡得多，七个呢。|~这么多啊。|昨儿喂了点儿玉米，可能是吃好了。", "你那盆花甭老浇水，根要烂的。|~啊？我还以为多浇点儿好呢。|哪能啊，土干了再浇。", "~妈，这是啥菜啊？|马齿苋，田埂上多的是，焯一下凉拌着吃。|~这也能吃啊。|能吃的多着呢，慢慢儿认吧。", "我前两天学会拿手机拍视频了。|~是吗，拍的啥？|拍了段鸡吃米，发给你二姨了，她还回了个大拇指。", "你小时候就爱吃我做的糖醋排骨。|~现在也爱吃啊。|那行，晚上做。", "{day}下午怕是有雨，衣裳我先收了啊。|~好，我来叠吧。|算了算了，你叠完我还得返工。", "你瞅瞅你，袖口又蹭一块灰。|~哦，刚去了趟仓库。|脱下来，我给你搓两把。", "~妈，你累不累啊？|累啥，又没多少活儿。|~那你也坐会儿嘛。|行，坐会儿。你给我倒杯水去。", "今儿集上桃子不错，买了一兜。|~我去洗几个。|洗完给你爸留俩大的啊。", "晚上蚊子多，蚊香给你点上了。|~谢谢妈。|甭搁床跟前，呛得慌。", "听说你那萝卜长得还行？|~还行吧，就是有一块让虫给咬了。|撒点儿草木灰，虫就不来了。", "~妈，咱家是不是养猫了？|哪儿是咱家的，隔壁的，天天来蹭饭。|~哦，我说呢。|喂了它两回，就赖上了。", "你那毛衣起球了，我给你剪剪。|~不用那么麻烦吧。|麻烦啥，一会儿的事儿。脱下来。", "城里菜贵不贵啊？|~挺贵的。|那走的时候多带点儿，家里也吃不了。", "今儿这饭是新米煮的。|~怪不得这么香啊。|香就多吃一碗。", "~妈，你年轻时候啥样啊？|跟你差不多吧，就是比你勤快。|~……|哈哈哈，逗你呢。", "厨房那水龙头有点儿漏，你跟你爸说一声。|~你咋不自己说啊？|我都说三遍了！你说他才听。", "这几天睡得咋样？|~挺好的，这边安静。|那就行。城里车多，吵得人睡不踏实。", "这南瓜我留着做南瓜饼。|~我想吃！|想吃就过来帮我和面。", "~妈，你包的粽子咋这么好吃啊？|叶子是自个儿摘的，米泡了一宿。|~教教我呗。|行啊，等端午吧。", "甭老坐着，起来走两步。|~我刚坐下……|刚坐下也起来，回头又嚷嚷腰疼。", "{dry}下午太阳好，我把你那些书拿出去晒了晒。|~书还用晒啊？|搁久了一股霉味儿，晒晒就好了。", "~妈，鸡窝那边好像有动静。|又是黄鼠狼吧。等你爸晚上去瞅瞅。|~我也去看看？|你甭去了，黑灯瞎火的。", "喝不喝绿豆汤？|~喝！|在井里镇着呢，自个儿提上来。", "我把你小时候的相册翻出来了，老厚一本。|~我看看我看看。|你瞅这张，坐澡盆里哭呢。|~哎呀妈！快收起来。", "晚上想吃啥？我好提前泡上。|~想喝红豆粥。|行，那我这就泡豆子去。", "你那几件衣裳我给你洗了，晾后院了。|~我自己洗就行啊。|顺手的事儿，跟我客气啥。", "~妈，你知道山那边有个瀑布不？|知道啊，你爸年轻时候带我去过一回。|~远不远？|远着呢，得走半天。要去多带点儿水。", "今儿熬了点酸梅汤，在井里镇着呢。|~太好了。|甭一气儿喝完啊，喝多了倒牙。", "你袜子破了个洞，我给补上了。|~啊，谢谢妈。|补得不咋好看，凑合穿吧。", "我想养几只鸭子，你说咋样？|~好啊，小鸭子多可爱。|可爱啥呀，我是想吃鸭蛋。", "~妈，有个事儿你别告诉我爸啊。|啥事儿？|~我把他茶杯磕了个口子。|嗐，多大点事儿。你自个儿跟他说去，他不能说你。", "这两天风大，窗户关严实点儿。|~好。|昨儿夜里你那屋窗户哐哐响了半宿。", "你爱吃辣的还是甜的啊？|~都爱吃。|随你爸，啥都吃。", "剁了一上午馅儿，手都酸了。|~我给你捏捏。|哎哟轻点儿轻点儿……嗯，这样行。", "~妈，你咋起这么早啊？|惯了，鸡一叫就醒。|~那你中午睡会儿。|嗯，中午眯一觉。", "你那手机老响，谁找你啊？|~朋友发的消息。|那你倒是回人家啊，别让人干等着。", "今儿给你做了个新鲜的，你猜是啥。|~闻着像……韭菜盒子？|哟，鼻子还挺灵。", "咱家后头那棵枣树，今年结得可多了。|~现在能打不？|还青着呢。等红了让你爸拿竿子打。", "~妈，这线团是干啥的啊？|给你爸织围脖儿呢，都织半个月了。|~他知道不？|不知道，你可别说漏了啊。", "我瞅着你瘦了。|~没有吧。|咋没有，下巴都尖了。多吃点儿。", "今儿镇上有卖小鸡崽儿的，我差点儿又买了。|~买呗。|再买窝里搁不下了。", "你那屋我给归置了一下，抽屉里的东西没动。|~好，谢谢妈。|抽屉里那堆糖纸你还留着呢？", "{night}~妈，出来看星星不？|看啥星星啊，怪冷的。|~多穿点儿嘛。|……行吧，就看一会儿啊。", "我做了点儿豆腐乳，你走的时候带一瓶。|~好啊。|开了盖儿可得赶紧吃，放不住。", "你那指甲该铰了。|~我自己会剪。|会剪就剪啊，非等我说。", "今儿这菜你爸嫌淡。|~我吃着正好啊。|你俩这口儿就没对上过。", "~妈，你看我种的那排葱。|长得还行，就是太密了。|~要拔掉点儿不？|拔一半儿吧，拔下来的晚上炒鸡蛋。", "问你个事儿啊，你别嫌我啰嗦。|~你说呗。|你在外头没让人欺负吧？|~没有，谁欺负我啊。|没有就行。", "你看这块布，做个围裙咋样？|~这花儿还挺好看的。|那给你也做一条，省得做饭弄一身油。", "~妈，你最爱吃啥啊？|我啊？我啥都行。|~那不跟我一样嘛，都行。|去，少学我。", "{rain}这雨下得好啊，地都不用浇了。|~那我今天干啥去？|歇着呗，难得下回雨。", "你爸又上河边去了，说要钓条大的回来。|~他上回钓了多大的？|就巴掌大，还跟我说“小的都放了”。", "~妈，这灯泡好像不亮了。|又坏啦？柜子里有新的，等你爸回来换。|~我会换。|那你先把电闸拉了啊，小心点儿。", "吃不吃煮玉米？|~吃！|刚出锅的，烫，晾晾再啃。", "看你在地里待了一天，都晒黑了。|~有吗？|咋没有，后脖颈子都红了。明儿戴个草帽。", "给你烙了几张饼，饿了就吃。|~好香啊。|葱油的。你小时候一顿能吃三张。", "~妈，你住这儿不嫌太静啊？|不嫌啊，静点儿好。|~我还以为你会想城里呢。|城里有啥好的，买个菜还得排队。", "那几只鹅又跑菜地里去了！|~我去撵。|拿根竹竿儿啊，它们拧人。", "你那件红外套呢？挺好看的那件。|~放城里了，没带来。|下回带来呗，山里穿个红的，老远就能瞅见你。", "听你爸说，你想再开一块地？|~嗯，想试试。|行啊。缺啥跟我说，种子我那儿还有。", "~妈，你做饭的时候哼的啥歌啊？|我哼了吗？|~一直在哼啊。|……老歌了，说了你也没听过。", "今儿腌了一坛酸菜。|~闻着就酸。|得一个月才能吃呢。到时候给你炖酸菜鱼。", "晚上甭看手机看太晚，眼睛还要不要了。|~就看一会儿。|你那“一会儿”我还不知道，俩钟头打不住。", "~妈，咱家有针线没？|有啊，抽屉第二层。咋了？|~扣子掉了。|拿来吧，我给你钉上。", "今儿给鸡窝换了新稻草，一个个的都不乐意出来了。|~太舒服了吧。|跟你早上赖被窝一个样。", "你瞅后山那片云，像不像只兔子？|~诶，还真像，耳朵都有。|你小时候就爱看云，一看看半天。", "~妈，你有没有啥想去的地方啊？|想去海边瞅瞅，还没见过海呢。|~那我带你去啊。|行啊，等地里活儿忙完的。", "这菜你多吃点儿，对眼睛好。|~胡萝卜啊？|嗯。你天天盯着个手机。", "晚上我跟你爸上你王婶家坐坐。|~我也去吗？|想去就去呗，她老念叨你。", "~妈，我小时候是不是特别怕打雷啊？|可不嘛，一打雷就往我被窝里钻。|~现在不怕了。|不怕了好。", "~妈，我帮你剥蒜吧。|行，剥一头就够了，甭剥多了。|~剥完手上一股味儿。|拿醋搓搓就没了。", "你爸那衬衫领子又磨破了，我给他翻个面儿。|~这还能翻啊？|咋不能，翻过来还能再穿两年。", "~妈，你咋知道是我回来了？|听脚步声啊，噔噔噔的，打小儿就这么走道。", "今儿上井边打水，碰见只小刺猬。|~真的啊？在哪儿呢？|钻竹林里去了。晚上兴许还出来。", "把这碗汤给你爸端过去。|~他在哪儿呢？|牛棚呢。喊他吃饭，喊八遍都不来。", "~妈，这枕头咋这么软啊？|新弹的棉花，你枕枕看。|~嗯，舒服。|舒服今晚就早点儿睡。", "我想在院里种棵桂花，你说种哪儿好？|~门口吧，一进门就能闻着。|嗯，我也琢磨着种门口。", "甭光守着地里，也上村里转转，认认人。|~我谁也不认识啊。|去你王婶家坐坐呗，她嘴快，坐一下午全村你都认全了。"],
  dad:["来，帮我扶一下这块板子。|~好。|往左点儿……行了，甭动。", "牛今儿吃了两捆草。|~这么能吃啊。|干活的嘛，不吃咋行。", "~爸，你修啥呢？|篱笆，松了。|~要帮忙不？|你给我递钉子就行。", "你那块地，草该薅了啊。|~我明天薅。|今儿就薅，明儿又长一茬。", "要变天了。|~你咋知道？|膝盖疼上了。", "~爸，喝茶不？|喝。|~放糖吗？|茶里放啥糖。", "这锄头你使着顺手不？|~有点儿沉。|我给你换个短把儿的。", "晚上甭出去乱走啊，山里黑。|~我带手电。|带手电也甭走远了。", "~爸，你看那只鸟。|喜鹊。|~还挺好看的。|好看啥，天天来偷鸡食。", "你妈又说我把她花给拔了。|~那你拔了没？|……我当是草呢。", "~爸，今天钓着鱼没？|钓着了。|~多大啊？|……不大，放了。", "井水凉，甭一气儿喝太多。|~嗯。|回头闹肚子，你妈又得熬姜汤。", "这椅子我修好了，你坐坐看。|~嗯，挺稳的。|加了根撑子。", "~爸，你年轻时候干啥的啊？|种地。|~一直种地啊？|也开过几年拖拉机，后来卖了。", "牛棚那灯坏了，晚上我去换。|~我给你打手电。|行。", "你那手套哪儿来的？|~镇上买的。|太薄了。戴我那副，厚实。", "~爸，这是啥树啊？|核桃，你爷爷栽的。|~这么老了啊？|比我岁数都大。", "下回进城给我捎包烟丝。|~我妈不让你抽。|……那捎包茶叶吧。", "来，下盘棋。|~我不咋会啊。|我教你。马走日，象走田。", "~爸，你看我挖的这沟直不直？|歪了。|~哪儿歪了啊？|你蹲下瞅瞅。", "{hot}这天儿太热，晌午甭下地了。|~那啥时候去？|傍黑儿吧，凉快。", "~爸，咱家鸡有名儿不？|没有。|~那我给起几个？|随你，反正它们也听不懂。", "把那桶水拎过来。|~好沉啊。|俩手拎，甭闪着腰。", "~爸，那个铁家伙是啥啊？|播种机，坏好几年了。|~还能修不？|修过三回了，算了。", "你妈做饭的时候甭往厨房钻。|~为啥？|她嫌碍事儿。我都挨过好几回说了。", "今儿镇上豆腐不赖，我买了两块。|~我妈说晚上做麻婆豆腐。|那让她多搁点儿辣子。", "~爸，听说后山有野猪？|有，前年拱了人家一亩地呢。|~那咱家地咋办？|甭怕，它不咋往这边来。", "这扫帚都秃了，明儿扎个新的。|~你还会扎扫帚啊？|你爷爷教的。", "~爸，你看我编的这筐咋样？|……漏。|~哪儿漏了？|底下，你瞅这儿，手指头都能伸进去。", "冷不冷？|~还行。|穿我那件褂子吧，门后头挂着呢。", "{rain}~爸，雨停了，我去地里瞅瞅。|去吧。水沟要是堵了就掏掏。|~知道啦。", "那牛今儿死活不走，跟我犟了半天。|~后来呢？|给了把豆子，走了。", "~爸，这钉子咋老是弯啊？|锤子拿歪了。|~那咋拿？|手往后握点儿，瞅准了再敲。", "你小时候在这儿摔过一跤，门牙磕掉一颗。|~啊？我咋不记得了。|你那会儿嚎得全村都听见了。", "~爸，你喜欢城里不？|不喜欢，挤得慌。|~那你上回去住了几天啊？|三天。第三天就想回了。", "来，尝尝我泡的酒。|~我不喝酒。|抿一口，梅子泡的，甜。", "~爸，牛今天好像不咋高兴。|跟隔壁那头顶架了。|~牛还顶架啊？|咋不顶，顶了半天呢。", "柴火够不够烧？|~够吧。|明儿我再劈点儿，冬天用得多。", "~爸，我能骑一下牛不？|它不让人骑。|~你试过啊？|……试过，让它甩下来了。", "你那车子气不足了，我给你打打。|~谢谢爸。|下坡捏着点儿闸，甭骑太快。", "{night}~爸，今晚有月亮不？|有，挺亮的。|~那出去坐会儿？|搬俩凳子到院里吧。", "这锅底得刷干净，要不下回煮饭一股糊味儿。|~我妈刷的。|……那你甭说是我说的。", "~爸，你会做饭不？|会下面条。|~就面条啊？|还会煎个鸡蛋。", "起风了，把晾的东西收收。|~我去收。|那件白的轻，甭让风刮跑了。", "~爸，这边晚上咋这么多虫子叫啊？|蛐蛐，天一暖和就这样。|~吵得我睡不着。|听惯就好了。", "得空去瞅瞅那几棵果树，看生没生虫。|~咋看啊？|翻叶子背面，有白点儿就是。", "~爸，你看我逮的蚂蚱。|放了吧……不对，这玩意儿吃庄稼，扔远点儿。|~哈哈哈。", "你那桶漆甭搁太阳底下，要干的。|~知道了。|上回就干了半桶，白瞎了。", "~爸，咱家这房子多少年了？|三十多年了，我跟你妈结婚那年盖的。|~自己盖的啊？|可不，砖都是我一块块码的。", "吃饭甭看手机。|~就看一眼。|你这一眼看了十分钟了。", "~爸，那边那座山叫啥啊？|老鹰岭。|~有老鹰吗？|早先有，这些年少了。", "房顶有块瓦松了，下雨前得上去换了。|~你小心点儿啊。|没事儿，爬了几十年了。", "~爸，你说种啥最赚钱啊？|西瓜，就是费工夫。|~那种啥省事儿？|萝卜，撒下去就长。", "这水壶把儿松了，拿来我给紧紧。|~好。|螺丝刀递我。", "~爸，你看我挑的这西瓜熟了没？|拍拍。|~咚咚的。|熟了，切吧。", "晚上我出去转一圈，你把门插好。|~转啥啊？|瞅瞅鸡窝，瞅瞅牛。", "~爸，你年轻时候帅不帅？|问你妈去。|~我妈说一般。|……她瞎说。", "这锄头把儿上漆掉了，小心扎手。|~我戴手套了。|嗯。", "~爸，镇上有修手机的没？|有一家，老李开的。|~靠谱不？|给我修过，还行，就是修完铃声变大了。", "你那几块地，下礼拜该追肥了啊。|~追啥肥？|鸡粪，后头那堆，沤了半年了。", "~爸，你咋不爱说话啊？|说啥。|~随便说点儿啥呗。|……今儿天挺好。", "出牛圈记着关门啊。|~我关了啊。|上回牛跑你妈菜园子里去了，把我好一顿说。", "~爸，这草帽给你。|哪儿来的？|~集上买的。|嗯，不赖，比我那顶强。", "今儿来了个收山货的，问咱家有蘑菇没。|~有啊！我种的。|那下回卖给他。", "~爸，你教我编筐呗。|行，先学劈篾子。|~会不会划着手啊？|会，所以得戴手套。", "{day}你瞅那片云，下午准有雨。|~那我先把种子收屋里去。|嗯，麻利点儿。", "~爸，你觉着我在这儿干得咋样？|还行。|~就还行啊？|比我刚下地那会儿强。", "这刀我磨好了，切菜当心点儿。|~好。|刀口甭冲着自个儿。", "~爸，牛吃不吃西瓜皮啊？|吃，可爱吃了。|~那我拿去喂了啊。|甭喂多了，拉稀。", "你那水管子甭乱扔，压坏了漏水。|~我给卷起来。|卷齐整点儿。", "~爸，你看我码的柴火。|……还像个样儿。|~真的啊？|就是得往里收收，要不得倒。", "明儿早点儿起，跟我上镇上拉化肥。|~几点啊？|五点。|~啊……这么早。", "~爸，你说今年收成能好不？|看天呗。|~天咋说？|天又不会说话。", "这老收音机还能响呢，你听听。|~这得多少年了啊。|你爷爷的，那会儿天天抱着听戏。", "~爸，你怕不怕蛇？|不怕，草里碰见了绕着走就是。|~我怕。|那走道拿根棍儿，敲敲草。", "你妈今儿不大舒坦，晚饭你做。|~啊？我做？|我给你烧火。", "~爸，你那条旧皮带挺好看的啊。|当兵那会儿发的。|~你还当过兵？|当过两年。没跟你说过？", "那几只鹅又欺负鸡了。|~那咋办啊？|分开养吧，明儿我再搭个棚。", "{night}~爸，你看天上最亮的那颗。|金星，傍黑儿就它最亮。|~你咋啥都知道。|老抬头瞅呗。", "这梯子有一磴坏了，甭踩第三磴。|~好。|明儿我修。", "~爸，咱家能养条狗不？|能啊，正好看门。|~上哪儿弄去啊？|你王婶家刚下了一窝。", "你那几块地种得不赖。|~真的啊？|比隔壁老张家的齐整。", "~爸，这桶底下咋有个洞啊？|那是漏桶，浇花使的。|~我还当是坏了呢。|没坏，特意凿的。", "{rain}下雨了，鸡还在外头呢，撵进来。|~它们不听我的啊。|撒把米就跟你走了。", "~爸，你想吃啥，我给你做。|面条。|~就面条啊？|卧个鸡蛋。", "你那块地边儿上种排向日葵吧，好看。|~爸你还喜欢花啊？|……你妈喜欢。", "~爸，牛有名儿没？|有，叫大黄。|~它不是黑的吗？|小时候是黄的。", "今儿风大，甭上河边去。|~我就看看。|看看也甭去，水急。", "~爸，这锁咋打不开啊？|往里顶一下再拧。|~诶，开了。|这锁老了，得顺着它来。", "晚上蚊子多，我在门口挂了把艾草。|~管用不？|你妈说管用。我觉着一般。", "~爸，我不在的时候你想不想我？|……想啥想。|~不想啊？|你妈想。行了，吃饭。", "~爸，你帮我瞅瞅这锄头是不是钝了。|拿来。……是钝了，得磨磨。|~我来磨吧。|斜着磨啊，甭给磨平了。", "把那袋土豆搬地窖去。|~好沉！|蹲下搬，甭弯腰。", "~爸，你钓鱼的时候都想啥啊？|啥也不想。|~那多没意思。|啥也不想才舒坦呢。", "今儿在镇上碰见你小学老师了，还问起你。|~问我啥了？|问你现在在哪儿，过得好不好。", "~爸，你看我新买的草帽。|还行，就是绳儿短了，风一刮就掉。|~那咋整？|我给你换根长的。", "你地边儿上那块石头，我给搬走了。|~哪块啊？|大的那块，绊你两回了都。", "~爸，我想给牛刷刷毛。|行，使那把硬刷子，它得劲儿。|~它不踢我吧？|甭站它屁股后头就没事儿。", "吃完饭陪你妈遛个弯儿去，她老念叨你不陪她。|~那你呢？|我去瞅瞅牛棚。", "~爸，你笑起来挺好看的，干嘛老板着脸啊。|……谁板着脸了。|~你现在就板着呢。|吃你的饭。"]};
 function liveFits(t){const m=/^\{(\w+)\}/.exec(t);if(!m)return true;const h=mins()/60,rain=typeof weather!=='undefined'&&(weather.kind==='rain'||weather.kind==='storm');
  return {rain,dry:!rain,day:h>=7&&h<17,night:h>=18||h<5,hot:springFarm.seasonAt(today())===1}[m[1]]??true;}
 function liveTalk(id){const pool=LIVE[id],seen=((lifeFlags.parentTalkSeen||={})[id]||=[]);
  let ok=pool.map((t,i)=>i).filter(i=>!seen.includes(i)&&liveFits(pool[i]));if(!ok.length){seen.length=0;ok=pool.map((t,i)=>i).filter(i=>liveFits(pool[i]));}
  const i=pick(ok);seen.push(i);return pool[i].replace(/^\{\w+\}/,'').split('|').map(l=>l.startsWith('~')?['me',l.slice(1)]:[id,l]);}
 X.hooks.click.unshift(click);
 // ---------------------------------------------------------------- 爸妈自己找她说话（owner 2026-11-10：在家要有来有回）
 // when she is in the house with one of them and nothing else is going on, every hour or so one of them starts a little chat
 const CHATS=[
  ['mom','今儿在地里累不累啊？',['me','还行，就是腰有点儿酸'],['mom','晚上给你贴块膏药吧。']],
  ['mom','你小时候最怕那只大白鹅，还记得不？',['me','记得啊，它追了我半个村！'],['mom','哈哈哈，可不嘛。']],
  ['mom','城里房租贵不贵啊？',['me','还行吧，付得起'],['mom','不够就吱声啊，家里有。']],
  ['mom','隔壁你婶子问你有对象没。',['me','妈——'],['mom','行行行，我不问，是她问的。']],
  ['mom','这菜是你那块地里的吧？',['me','嗯，早上刚摘的'],['mom','怪嫩的，炒着吃正好。']],
  ['mom','你那几个朋友，得空叫家里来玩儿啊。',['me','他们老说想来看牛'],['mom','来呗，我多蒸一屉包子。']],
  ['mom','衣裳给你洗了，晾后院了啊。',['me','我自己洗就行'],['mom','顺手的事儿。']],
  ['mom','今儿鸡又少下一个蛋。',['me','不会是让黄鼠狼盯上了吧'],['dad','晚上我去鸡窝那边瞅瞅。']],
  ['mom','尝尝这咸菜，今年腌得不赖。',['me','嗯，下饭！'],['mom','走的时候带一罐儿。']],
  ['mom','老盯着个手机，眼睛还要不要了。',['me','我就看一会儿'],['mom','你那一会儿是多会儿啊？']],
  ['mom','下礼拜镇上有集，去不去？',['me','去啊！我想吃那家的糖糕'],['mom','那得早点儿起啊。']],
  ['mom','这几天睡得咋样？',['me','挺好的，山里安静'],['mom','那就多住些日子。']],
  ['dad','来，瞅瞅我新编的筐。',['me','可以啊爸，手真巧'],['dad','跟你爷爷学的，他编得比我强。']],
  ['dad','牛今儿吃了两捆草。',['me','比我还能吃'],['dad','它干的活儿也比你多。']],
  ['dad','你那块地垄沟挖浅了，一下雨得积水。',['me','那我明天再挖挖'],['dad','我跟你一块儿弄。']],
  ['dad','今年柿子挂得多。',['me','能做柿饼不？'],['dad','能啊，等霜降了晒。']],
  ['dad','城里住得惯不？',['me','还行，就是有点儿吵'],['dad','嫌吵就回来住。']],
  ['dad','你瞅这天，明儿准下雨。',['me','你咋知道的？'],['dad','山那头起云了。']],
  ['dad','老屋那根梁该换了。',['me','要我帮忙不'],['dad','到时候你给我递钉子。']],
  ['dad','你小时候爬那棵枣树，下不来，哭了一后晌。',['me','哎呀这事儿能不能别提了'],['dad','行行，不提了。']],
  ['dad','镇上新开了个修车铺。',['me','咱家又没车'],['dad','拖拉机不是车啊？']],
  ['dad','喝茶不？今年的新茶。',['me','来一杯'],['dad','烫啊，慢点儿喝。']],
  ['dad','你妈今儿念叨你一上午。',['me','念叨我啥了？'],['dad','说你瘦了。']],
  ['dad','夜里风凉，窗户我给你关小点儿。',['me','好，谢谢爸']]];
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
  visit={day:null,pending:true};log(`想爸妈了，去茵菲谷看看他们。`);showSay(pick(['好久没见我爸我妈了，回茵菲谷看看吧。','回趟茵菲谷，不跟他们说，吓他们一跳。']));
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
  if(p==='spring_test'&&visit?.pending){visit={day:today()};setTimeout(()=>{if(!inSpring())return;if(ready()&&!C().state.inside)X.hooks.pick.indoor();talkQ.push(['mom',pick(['哎哟来啦！路上累不累啊？','哎呀，咋突然回来了，也不说一声！','刚还念叨你呢，这就到了。'])],['dad',pick(['我去逮只鸡。','进屋坐，外头风大。','包给我。'])],['me',pick(['想你们了嘛！','回来看看你们呗。','妈，我饿了！'])]);
   log('飞到茵菲谷，爸妈都在家。');addSocialMemory?.(contact('mom'),'回茵菲谷看爸妈','坐飞机去茵菲谷，爸妈都在家等着。');},1800);}
  return r;};
 window.seasonParents={plan,here,farmCny,goSee,sleeping,doErrand,tell,walkers:ag,watching,get visit(){return visit;}};
})();
