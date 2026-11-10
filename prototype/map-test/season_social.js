// 季节地图里的社交（owner 2026-11-06）：
//  - 社交低了她自己拿手机打电话、发消息、视频（主世界的 remoteSocial 聊天，边走边聊），不回旅舍/农舍；
//  - 草帽湾的电话、消息、视频有岛上的话题（没有电脑、晒黑、潜水……）；家里养了宠物时会说想它；
//  - 季节地图里不能邀请朋友或爸妈过来，也不能去朋友家、约出门：海岛/山谷太远了。
// 茵菲谷自己的电话话题在 spring_talk.js（spring_story.js 换话题），这里只补“想宠物”“没电脑”。
(function(){
 const PLACES=['spring_test','summer_test'],inSeason=()=>PLACES.includes(sim.place),inBay=()=>sim.place==='summer_test';
 const hasPet=()=>typeof petState!=='undefined'&&petState.pets?.some(p=>p.status!=='lost');
 // ---------------------------------------------------------------- 草帽湾的话题 (">" = the other person)
 const BAY_TALK={
  mom:[
   {title:'晒黑了',lines:['>到了没？那边热不热？','热，太阳跟不要钱似的。','>防晒霜带了吧？','带了，抹了三遍，还是黑了一圈。','>回来让我看看，黑成啥样了。']},
   {title:'吃得惯吗',lines:['>那边吃得惯吗？','旅舍老板做生鱼饭，酱油拌的，好吃。','>生的？你肠胃受得了？','受得了，我天天吃。','>少吃点生的，听妈的。']},
   {title:'别游太远',lines:['>你下海了没？','下了，还潜下去看鱼了。','>潜水？有人看着没？','有，阿洛就在岸上。','>那也别游太远，听见没？','听见了——']},
   {title:'照片怎么那么糊',lines:['>你发的照片怎么那么糊？','这儿只有手机，连电脑都没有。','>那你天天干啥？','游泳，晒太阳，逛集市。','>……我也想去。']},
   {title:'别带贝壳',lines:['>回来别带一堆贝壳，家里没地方放。','就几个。','>上回你也说就几个。','这回真的就几个。']},
   {title:'睡得好吗',lines:['>晚上睡得着吗？那边吵不吵？','就是海浪声，哗啦哗啦的。','>那不跟你小时候那个助眠机一样。','比那个好听多了。']}],
  dad:[
   {title:'能钓鱼不',lines:['>那边能钓鱼不？','能吧，码头上天天有人钓。','>都钓的啥鱼？','不知道，花花绿绿的。','>拍几张照片给我看看。']},
   {title:'学冲浪',lines:['>你妈说你在学冲浪？','学了几次，摔了好多回。','>摔就对了，我当年学自行车……','爸，那是自行车。','>道理是一样的。']},
   {title:'椰子多少钱',lines:['>钱够花不？','够，这儿东西不贵。','>椰子多少钱一个？','……爸你问这个干嘛？','>就问问。']},
   {title:'信号不好',lines:['>喂？喂？信号不好啊。','我在海边，风大。','>啥？','风——大——','>行，那你玩吧，挂了。']},
   {title:'晒伤了没',lines:['>后背晒伤了没？','有点，一碰就疼。','>芦荟，掰开往上抹。','这儿到处都是芦荟。','>那还等啥。']}],
  friend:[
   {title:'工位上看海',lines:['>你发的那个海是真的吗','真的，就在旅舍门口','>我在工位上看了三遍','回去给你带个椰子','>椰子带得回来吗','……那带个椰子壳']},
   {title:'帮我看个文件',lines:['>帮我看个文件呗','我这儿没电脑','>啊？那你怎么活的','游泳啊','>行，不打扰你过神仙日子了']},
   {title:'带点特产',lines:['>岛上有啥好玩的','有个集市，卖啥的都有','>给我带点特产','彩虹刨冰带不回去','>那你吃的时候替我多吃一口']},
   {title:'海里有啥',lines:['>潜水能看见啥','鱼，好多鱼，还有海龟','>真的假的','真的，它游得比我还慢','>哈哈哈哈']},
   {title:'啥时候回来',lines:['>你啥时候回来啊','还没想好','>还没想好？？','嗯，岛上没有闹钟','>我恨你']}],
  video:[
   {title:'让我看看海',lines:['>镜头转一下，让我看看海','你看，这是海','>哇……旁边那个是谁','旅舍老板阿洛','>他那顶草帽好好看']},
   {title:'你黑了',lines:['>等等，你是不是黑了','有吗？','>有，跟背景差不多一个色了','……你挂了吧']}]};
 // 想宠物 (only when she has one at home)
 const PET_TALK={
  mom:[{title:'宠物谁管',lines:['>你家{宠物}谁管着呢？','有喂食器，邻居每天也去看一眼。','>它肯定想你了。','我也想它，昨晚还梦见它了。']}],
  dad:[{title:'宠物胖了没',lines:['>你那{宠物}，回去不会饿瘦了吧？','不会，喂食器一天三顿。','>那回去胖了也是你的事。','爸……']}],
  friend:[{title:'想{宠物}了',lines:['>你家{宠物}最近咋样','不知道，好几天没见了','>不想它吗','想，照片翻了好几遍','>回去它估计要跟你闹别扭'],},
   {title:'它记得我吗',lines:['你说，{宠物}还记不记得我','你才走几天','几天也是好几天','>放心，你一开门它就扑上来了']}]};
 // 茵菲谷 extras for its own pool: no computer here
 const SPRING_EXTRA={friend:[{title:'没电脑',lines:['>你那儿有电脑吗','只有个平板，信号时有时无','>那我发你的视频你看了没','转了十分钟圈，没出来','>那你回来再看吧']}]};
 const mood=(name,emo='happy')=>({name,emo,pts:2,min:120});
 let n=0;const tag=(t,place,who,name='聊了聊家常')=>{t.id=`season_talk_${place}_${who}_${n++}`;t.mood=ML[t.id]=mood(name);return t;};
 for(const [who,list]of Object.entries(BAY_TALK))list.forEach(t=>tag(t,'bay',who));
 for(const [who,list]of Object.entries(PET_TALK))list.forEach(t=>tag(t,'pet',who,'想宠物了'));
 if(typeof SPRING_TALK!=='undefined')for(const [who,list]of Object.entries(SPRING_EXTRA)){list.forEach(t=>tag(t,'spring',who));(SPRING_TALK[who]||=[]).push(...list);}
 const seenOf=key=>((lifeFlags.talkSeen||={})['season_'+key]||=[]);
 function freshFrom(pool,key){const seen=seenOf(key);let ok=pool.map((t,i)=>i).filter(i=>!seen.includes(i));if(!ok.length){seen.length=0;ok=pool.map((t,i)=>i);}const i=pick(ok);seen.push(i);return pool[i];}
 const oldChat=chatItem;chatItem=function(kind,who,via,contactId){
  const it=oldChat(kind,who,via,contactId);
  if(!inSeason()||!['call','text','video'].includes(kind)||!it?.talk)return it;
  const c=contactId&&socialState.contacts.find(x=>x.id===contactId),key=c?.family||(c?'friend':who);
  let t=null;
  if(hasPet()&&PET_TALK[key]&&Math.random()<.18)t=freshFrom(PET_TALK[key],'pet_'+key);
  else if(inBay()&&Math.random()<.7){const pool=kind==='video'&&key==='friend'?[...BAY_TALK.friend,...BAY_TALK.video]:BAY_TALK[key];if(pool)t=freshFrom(pool,'bay_'+key+(kind==='video'?'_v':''));}
  if(!t)return it;
  const pet=hasPet()?petName():'',f=s=>s.replaceAll('{宠物}',pet),title=f(t.title);
  it.talk.end=it.talk.end.replace(it.talk.title,title);Object.assign(it.talk,{title,lines:t.lines.map(f),mood:t.mood,id:t.id});if(c)c.lastTopic=title;return it;};
 // ---------------------------------------------------------------- 宠物快跑了（owner 2026-11-10）
 // the first time a pet would run off while she is in 茵菲谷 / 草帽湾 it stays: her closest friend let themselves in with the
 // spare key and filled the bowls. A quest-style bubble says so; 「我马上回家」 flies her home as soon as nothing else is on.
 let rescueTalk=null,homeAsked=false;
 // owner 2026-11-10: while she is in a season map her pets at home get by slower (1/3), and the first time any need of a pet
 // drops under 5 her closest friend drops by, sorts it and texts her (once per need, per pet)
 window.petAwaySlow=()=>inSeason()?1/3:1;
 const HELP={hunger:['{宠物}的碗空了，我拿你家备用钥匙进去添满了，放心哈。','路过你家听见{宠物}在叫，一看饭碗见底了，给它倒满了。','你家{宠物}饿得直扒门，我给它添了粮，吃得可香了。'],
  energy:['去你家看了眼{宠物}，它好像一直没睡踏实，我把窝挪到太阳底下了，这会儿睡得呼呼的。','{宠物}看着蔫蔫的，我把屋里灯关了让它好好睡一觉。'],
  company:['去你家陪{宠物}玩了一下午，它一直往我怀里钻，估计是想你了。','{宠物}一个人在家闷坏了，我陪它玩了会儿球，现在高兴多了。','我去你家坐了会儿，{宠物}黏了我一下午，你快点回来哈。']};
 const THANKS=['谢谢！回去请你吃饭','哎呀太谢谢了','欠你一顿饭'];
 window.petLowHelp=(p,k)=>{if(!inSeason()||!HELP[k])return false;p.helped??={};if(p.helped[k])return false;p.helped[k]=true;
  const f=socialState.contacts.filter(c=>!c.family&&!c.child&&!String(c.id).startsWith('bay_')).sort((a,b)=>(b.affinity??0)-(a.affinity??0))[0];
  const who=f?contactName(f):'邻居',line=pick(HELP[k]).replaceAll('{宠物}',p.name||'小家伙');
  setTimeout(()=>{try{gameAudio?.sound?.('bell',.2,{gap:4});}catch(e){}if(!storyLocked()&&!asleep())showSay(line,who+'：',f||null);
   log(`${who}发来消息：帮忙照看了家里的${p.name||'宠物'}。`,null,[[who+'：',line],[nameOf()+'：',pick(THANKS)]]);},0);
  return true;};
 window.petRescue=p=>{if(!inSeason()||p.rescued)return false;p.rescued=true;
  p.needs.hunger=Math.max(p.needs.hunger,90);p.needs.company=Math.max(p.needs.company,50);p.needs.energy=Math.max(p.needs.energy,50);petState.feeder=900;
  const f=socialState.contacts.filter(c=>!c.family&&!c.child&&!String(c.id).startsWith('bay_')).sort((a,b)=>(b.affinity??0)-(a.affinity??0))[0];
  rescueTalk={who:f?contactName(f):'邻居',name:p.name};log(`${rescueTalk.who}用备用钥匙进了家门，给${p.name}添满了粮。`);return true;};
 setInterval(()=>{try{
  if(!rescueTalk||!inSeason()||!speed||storyLocked()||cardHolds()||wiping||sim.mode==='down'||asleep()||springFarm.speech.open)return;
  const r=rescueTalk;rescueTalk=null;const sp=springFarm.speech;
  sp.show(r.who,'你一定是忘记喂你的小宠物了，所以原谅我拿了你家的备用钥匙，给你的小家伙们放满了粮食。',{special:true,choices:[
   {label:'多谢！我会注意的',on:()=>{sp.hide();speak('回头得好好谢谢人家',true);}},
   {label:'我马上回家！',on:()=>{sp.hide();homeAsked=true;}}]});
 }catch(e){console.warn('pet rescue',e);}},1000);
 // 「我马上回家」: leave as soon as no story / event / card is going on
 setInterval(()=>{try{
  if(!homeAsked)return;if(!inSeason()){homeAsked=false;return;}
  if(!speed||storyLocked()||cardHolds()||wiping||sim.mode==='down'||springFarm.speech.open||socialBusy()||typeof remoteSocial!=='undefined'&&remoteSocial)return;
  homeAsked=false;closeRing();if(sim.place==='spring_test')infeiHome.leave();else ringPick('bay:leave');
 }catch(e){console.warn('pet rescue home',e);}},1000);
 // ---------------------------------------------------------------- 社交低了：拿手机找人聊（像主世界一样，不回屋）
 const ctl=()=>sim.place==='summer_test'?seasonMapTest.state.summer:sim.place==='spring_test'?seasonMapTest.state.spring:null;
 const wet=()=>{if(!inBay())return false;const c=ctl(),s=c.state;return !s.inside&&!s.market&&(window.summerFloat?.surfing||window.summerLife?.under?.()||c.deep(s.x));};
 let nextTry=0,lastChat=0;
 // owner 2026-11-10: while 爸妈 are right there in 茵菲谷 they do not phone or video her (and she does not phone them)
 const parentsHere=()=>sim.place==='spring_test'&&!!window.seasonParents?.here?.().length;
 const oTalk=startContactTalk;startContactTalk=function(id,kind,incoming){const c=socialState.contacts.find(c=>c.id===id);if(c?.family&&['mom','dad'].includes(c.id)&&parentsHere())return false;return oTalk.apply(this,arguments);};
 function phoneSomeone(){
  if(!inSeason()||remoteSocial||sim.mode==='down'||asleep()||wiping||cardHolds()||socialBusy()||storyLocked())return false;
  if(seasonHouse.busy()&&['bath','toilet','season_shower','sleep'].includes(sim.act))return false;
  if(wet())return false;
  const h=hour(),night=h>=22||h<8;
  const friends=socialState.contacts.filter(c=>!c.family&&!c.child&&!String(c.id).startsWith('bay_')&&!contactWithHero(c.id)&&(c.affinity??0)>=10);
  const family=socialState.contacts.filter(c=>c.family&&!contactWithHero(c.id)&&!(parentsHere()&&['mom','dad'].includes(c.id)));   // at night only a text (soak test 2026-11-09: no friends yet + no family at night = social ran down to 14)
  const list=[...family.map(c=>[c,c.id==='mom'?3:1.5]),...friends.map(c=>[c,1])];if(!list.length)return false;
  let r=Math.random()*list.reduce((a,x)=>a+x[1],0),c=list[0][0];for(const [x,w]of list)if((r-=w)<0){c=x;break;}
  const kind=c.family?(night?'text':Math.random()<.75?'call':'text'):night?'text':weighted([['text',3],['video',1.5],['call',1.5]]);
  return startContactTalk(c.id,kind);}
 setInterval(()=>{try{
  if(!inSeason()||!speed||sim.t<nextTry)return;
  // owner 2026-11-10: she should reach for the phone by herself here, not only when social is red
  if(sim.needs.social<45){nextTry=sim.t+20;if(phoneSomeone())nextTry=sim.t+90;}
  else if(sim.needs.social<75&&sim.t-lastChat>200&&Math.random()<.5){nextTry=sim.t+30;if(phoneSomeone()){lastChat=sim.t;nextTry=sim.t+90;}}
 }catch(e){console.warn('season social',e);}},1000);
 // a red social need: never into the house for it, the phone instead
 const oHome=homeFor;homeFor=function(k){if(inSeason()&&k==='social'){phoneSomeone();return;}return oHome.apply(this,arguments);};
 // the ring: 玩手机 ▸ in the season maps too
 const oOpen=openRing;openRing=function(which,at){
  if(which==='away'&&inSeason()&&!RINGS.away.some(r=>r[0]==='phone')){const keep=RINGS.away,i=keep.findIndex(r=>r[0]==='pat');RINGS.away=[...keep.slice(0,i+1),['phone','玩手机 ▸','more'],...keep.slice(i+1)];try{return oOpen.apply(this,arguments);}finally{RINGS.away=keep;}}
  return oOpen.apply(this,arguments);};
 // phone acts picked from the ring: the call runs alongside whatever she is doing (as at home); 刷动态 / 手游 right where she stands
 const oStart=startAct;startAct=function(name,quiet){
  if(inSeason()&&['phone_call','phone_video','phone_text'].includes(name)){
   if(!remoteSocial){const item=sim.chosen?.act===name?sim.chosen.item:pickItem(name);remoteSocial={item,i:0,wait:.5,said:[]};log(item.talk.start);}
   sim.chosen=null;sim.player=false;return;}
  if(inSeason()&&['phone_feed','phone_game'].includes(name)){if(wet()){showHint('在水里玩不了手机');return;}const c=ctl();c.state.target=null;seasonHouse.start(name,{auto:!sim.player});seasonMapTest.state.autoAt=sim.t+1e6;return;}
  return oStart.apply(this,arguments);};
 setInterval(()=>{if(!inSeason())return;const c=ctl();if(['phone_feed','phone_game'].includes(sim.act)&&sim.mode==='act'&&c?.state.target){seasonHouse.explore();seasonMapTest.state.autoAt=sim.t;}},300);
 // ---------------------------------------------------------------- nobody comes here, nobody is visited from here
 const far=()=>inBay()?'草帽湾在海岛上，离得太远了':'茵菲谷在山里，离得太远了';
 const oInvite=inviteHome;inviteHome=function(id,proactive){if(inSeason()){const c=socialState.contacts.find(c=>c.id===id);
   if(proactive&&c){const text=inBay()?'我现在在草帽湾呢，回去再约你！':'我在茵菲谷呢，回去再约你！';showSay(text);log(`${contactName(c)}想来家里坐坐，可我还在${inBay()?'草帽湾':'茵菲谷'}，约了回去再见。`);}
   else visitNotice('暂时不能邀请',far()+'，回去再约吧。');return false;}
  return oInvite.apply(this,arguments);};
 const oVisit=requestFriendVisit;requestFriendVisit=function(id,incoming){if(inSeason()){showHint(far()+'，回去再去做客吧。');return false;}return oVisit.apply(this,arguments);};
 const oOut=openFriendOuting;openFriendOuting=function(id){if(inSeason()){showHint(far()+'，回去再约出门吧。');return;}return oOut.apply(this,arguments);};
 const oOffer=canOfferFriendVisit;canOfferFriendVisit=function(c){return !inSeason()&&oOffer.apply(this,arguments);};
 const oFam=familyMayOfferVisit;familyMayOfferVisit=function(c){return !inSeason()&&oFam.apply(this,arguments);};
 const oActs=openContactActions;openContactActions=function(id){const r=oActs.apply(this,arguments);
  if(inSeason())for(const b of contactActions.querySelectorAll('button')){if(!['outing','visit','invite'].includes(b.dataset.action))continue;
   b.setAttribute('aria-disabled','true');b.title=far();b.setAttribute('aria-label',`${b.textContent}：${b.title}`);b.querySelector('small')?.remove();b.append(Object.assign(document.createElement('small'),{textContent:'太远了'}));}
  return r;};
})();
