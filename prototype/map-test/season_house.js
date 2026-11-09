// 季节地图里的房子（茵菲谷农舍、草帽湾旅社）：直接跑主世界的动作（owner 2026-11-06：“生活精度要完全完全对标主世界”）。
// A piece of furniture starts the home's own act (ACTS / EFFECT / lifeArrive / lifeFinish / activityFrame): the same
// durations, need changes, face and pose, emote bubbles, diary lines, moods, cooked dish on the table, cook → eat, a
// break for the toilet, and so on. The houses (infei_home.js, summer_lodge.js) only walk her to the spot and draw the
// home's effects at their own furniture. Standard: docs/SEASON_MAP_STANDARD.md.
const seasonHouse=(function(){
 const PLACES=['spring_test','summer_test'],inSeason=()=>PLACES.includes(sim.place);
 // acts the home has no twin for, built like the home's own (durations take PACE like the rest)
 const own=(id,a,eff)=>{ACTS[id]={spot:'season',...a,dur:a.dur*PACE};EFFECT[id]={...eff};};
 own('season_sofa',{label:'坐着歇会儿',emote:'star',dur:40,log:null},EFFECT.tv);
 own('season_uke',{label:'弹尤克里里',emote:'note',dur:15,log:'借阿洛的尤克里里弹了一会儿。'},EFFECT.phone_game);
 own('season_shower',{label:'冲凉',emote:'soap',dur:25,log:'冲了个凉水澡。'},EFFECT.bath);
 own('season_tidy',{label:'整理衣柜',emote:'star',dur:6,log:'把衣柜里的衣服叠整齐。'},EFFECT.dress);
 const oFrame=baseActivityFrame;baseActivityFrame=function(ms){
  const a=sim.act,ph=Math.floor(ms/600)%2,showEm=sim.mode==='act'&&ACTS[a]?.emote&&Math.floor(ms/2400)%2===0;
  if(sim.mode==='act'&&a==='season_sofa'&&!(typeof reaction!=='undefined'&&reaction&&realClock<reaction.until))return {f:{expr:Math.floor(ms/2000)%3===0?'happy':'neutral',look:1},pose:'sit',emote:showEm?ACTS[a].emote:null};
  if(sim.mode==='act'&&a==='season_uke'&&!(typeof reaction!=='undefined'&&reaction&&realClock<reaction.until))return {f:{expr:'happy',bob:ph,sway:ph},pose:'stand',emote:showEm?'note':null};
  return oFrame(ms);};
 const running=act=>inSeason()&&sim.mode==='act'&&sim.act===act;
 const busy=()=>inSeason()&&sim.mode==='act'&&!!sim.act&&sim.act!=='season_explore'&&!!ACTS[sim.act];
 function explore(){sim.mode='act';sim.act='season_explore';sim.actEnd=Infinity;sim.item=null;sim.talk=null;}
 // the home's arrive() for this act, minus the walking (the house has walked her there)
 function start(act,o={}){const a=ACTS[act];if(!a)return;
  sim.mode='act';sim.act=act;sim.player=!o.auto;
  if(act==='cook'&&sim.place==='summer_test'&&sim.chosen?.act!=='cook')sim.chosen={act:'cook',item:dishItem(BAY,pick(BAY.dishes))};   // the lodge's kitchen cooks Hawaiian
  if(sim.chosen&&sim.chosen.act!==act)sim.chosen=null;   // lifeArrive takes the dish picked from the menu
  if(act==='sleep'){const h=hour();sim.nap=!(h>=21||h<6);}
  sim.actEnd=sim.t+(act==='sleep'?900:a.dur*(0.8+Math.random()*0.4));
  sim.recent=[act,...sim.recent].slice(0,3);
  const line=o.log!==undefined?o.log:a.log;if(line)log(line);
  lifeArrive(act);}
 // a stop for good (the player sent her elsewhere): the home simply drops what she was doing
 function drop(act){if(running(act))explore();}
 // the home's act ends → its next step (cook → eat, a queued meal after the toilet) is routed by the season wrappers
 const oFinish=finishAct;finishAct=function(){const was=inSeason();const r=oFinish.apply(this,arguments);
  if(was&&inSeason()&&sim.mode==='idle'){const q=sim.queue.shift();sim.queue=[];explore();if(q)startAct(q);}
  return r;};
 // a need running red outside sends her home: never in a season map, and never while she is using the house
 const oRed=redNeed;redNeed=function(){if(busy())return null;return oRed.apply(this,arguments);};
 // one table per place: a dish cooked in the lodge stays in the lodge, the home's stays at home
 const meals={};
 const oArrive=arriveAt;arriveAt=function(p){const from=sim.place;if(from!==p){meals[from]=sim.meal;sim.meal=meals[p]||null;delete meals[p];}return oArrive.apply(this,arguments);};
 // ---------------------------------------------------------------- the home's pictures at the house's furniture
 function frame(){return busy()?activityFrame(realClock*1000):null;}
 function emote(ctx,x,y){const fr=frame();if(fr?.emote)ctx.drawImage(emoteCanvas(fr.emote),x,y);}
 function cookFx(ctx,x,y){if(running('cook'))ctx.drawImage(frameOf(IMG.fx.cook,8),x,y);}
 function meal(ctx,x,y){if(!homeMeal())return;const pic=sim.meal.pic&&dishPic(sim.meal.pic);
  if(pic&&pic.complete)ctx.drawImage(pic,x+3-(pic.width>>1),y+13-pic.height+1);else ctx.drawImage(frameOf(IMG.fx.meal,4),x,y);}
 function sleepFx(ctx,x,y){const cyc=Math.floor(realClock/26),inDream=realClock%26>19;   // the home's: Zs, now and then a dream bubble
  if(inDream)ctx.drawImage(emoteCanvas(DREAMS[cyc%DREAMS.length]),x,y);else ctx.drawImage(frameOf(IMG.fx.sleep_z,4),x-2,y-6);}
 // ---------------------------------------------------------------- the kitchen's menu (owner 2026-11-06)
 // Clicking the stove opens the home's own dish picker. The 草帽湾 lodge cooks only 夏威夷菜 (pictures: the home's dishes).
 const BAY={name:'夏威夷菜',spicy:false,sweet:false,dishes:[
  {name:'夏威夷生鱼饭',look:'sushi',fill:45,time:15,blurb:'金枪鱼丁拌上酱油和芝麻，铺在热米饭上'},
  {name:'洛可莫可',look:'rice',fill:60,time:25,blurb:'米饭、汉堡肉、煎蛋，再浇一大勺肉汁'},
  {name:'午餐肉饭团',look:'sandwich',fill:35,time:12,blurb:'煎得焦香的午餐肉压在饭团上，海苔一裹'},
  {name:'卡鲁瓦烤猪',look:'meat',fill:55,time:40,blurb:'香蕉叶包着慢慢烤，筷子一碰就散'},
  {name:'蒜香黄油虾',look:'shrimp',fill:45,time:20,blurb:'一大块黄油、一大把蒜，满屋子都是香味'},
  {name:'菠萝炒饭',look:'rice',fill:50,time:20,blurb:'菠萝挖空当碗，炒饭里一粒粒都是甜的'},
  {name:'胡里胡里烤鸡',look:'skewer',fill:50,time:30,blurb:'边烤边翻边刷酱，甜咸甜咸的'},
  {name:'椰奶冻',look:'pudding',fill:20,time:15,blurb:'椰奶冻得滑滑的，切成一块一块'},
  {name:'彩虹刨冰',look:'icecream',fill:15,time:8,blurb:'三种颜色的糖浆，从上往下慢慢化'}]};
 const menuItems=c=>c.dishes.map(d=>({title:d.name,line:d.blurb||'',info:`饱食 ${d.fill} · ${d.time}分钟`,icon:dishIcon(d),item:dishItem(c,d)}));
 PICK.cook_bay={title:'旅舍厨房 · 做什么菜',groups:()=>[{name:BAY.name,note:'',items:menuItems(BAY)}]};
 PICK.cook_farm={title:'农舍灶台 · 做什么菜',groups:PICK.cook.groups};
 function menu(which){openPicker(which==='summer'?'cook_bay':'cook_farm');}
 const oCommand=command;command=function(act,item){
  if(act==='cook_bay'||act==='cook_farm'){
   if(!item){const all=act==='cook_bay'?menuItems(BAY):PICK.cook.groups().flatMap(g=>g.items);item=pick(all).item;}
   sim.chosen={act:'cook',item};(act==='cook_bay'?window.summerLodge:window.infeiHome)?.use('stove','menu');return;}
  return oCommand.apply(this,arguments);};
 // ---------------------------------------------------------------- 草帽湾 hidden rule (owner 2026-11-06): in the sea
 // (swimming on the surface, surfing or diving) every need runs down at half speed; since 2026-11-09 fun rises (~+30/h)
 // and cleanliness and social do not move
 let seaT=null;setInterval(()=>{try{
  const sm=window.seasonMapTest?.state?.summer,st=sm?.state,t=sim.t;
  const wet=sim.place==='summer_test'&&st&&!st.inside&&!st.market&&(window.summerFloat?.surfing||window.summerLife?.under?.()||sm.deep(st.x)&&st.suit&&st.suit!=='clothes');
  if(wet&&seaT!==null&&t>seaT&&t-seaT<30){const dt=t-seaT,eff=sim.mode==='act'?(EFFECT[sim.act]||{}):{};
   // owner 2026-11-09: in the sea fun goes up, cleanliness and social stand still; the rest at half speed
   for(const k of Object.keys(sim.needs))if(!(eff[k]>0))sim.needs[k]=clamp(sim.needs[k]+DECAY[k]*(k==='hygiene'||k==='social'?1:.5)*dt);
   sim.needs.fun=clamp(sim.needs.fun+.4*dt);}
  seaT=t;}catch(e){}},250);
 return {start,drop,running,busy,explore,frame,emote,cookFx,meal,sleepFx,inSeason,menu,BAY};
})();
window.seasonHouse=seasonHouse;
