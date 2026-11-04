// 茵菲谷 farmhouse (game-shell test page only, never in make_demo.py / releases).
// Inside the house: click furniture to sleep, bathe, use the toilet, cook, eat or rest.
// 回家 in 茵菲谷 means this farmhouse; low needs walk her in here by herself (season-map rule:
// she never leaves the map on her own). Leaving the valley is a separate, player-only item.
const infeiHome=(function(){
 const X=springFarm.X,T=seasonMapTest,C=()=>T.state.spring,inSpring=()=>sim.place==='spring_test';
 // canvas coords inside the house (floor y 50 upstairs, 108 downstairs); rect [x,y,w,h]
 const SPOTS={
  bed:{name:'我的床',rect:[82,14,46,37],x:105,y:50,need:'energy',label:'睡一觉',hide:true,line:['被子晒过，有太阳的味道','睡一会儿……'],zz:[100,30]},
  wardrobe:{name:'衣柜',rect:[141,12,24,39],x:152,y:50,need:'fun',label:'整理衣柜',line:['把衣服叠整齐','这件好久没穿了'],max:85},
  bath:{name:'木浴桶',rect:[171,28,25,23],x:184,y:50,need:'hygiene',label:'泡个澡',hide:true,line:['热水泡一泡，舒服','木桶的味道真好闻']},
  toilet:{name:'卫生间',rect:[196,24,16,27],x:204,y:50,need:'bladder',label:'上厕所',pose:'sit',line:['马上出来']},
  parents:{name:'爸妈的房间',rect:[216,10,92,41],x:240,y:50,look:['这是爸妈的床，我不睡这儿','被子是妈妈新缝的']},
  settee:{name:'长椅',rect:[90,84,48,25],x:114,y:108,need:'fun',label:'坐着歇会儿',pose:'sit',line:['坐一会儿，看看窗外','这椅子坐着真舒服'],max:90},
  table:{name:'饭桌',rect:[176,80,52,29],x:200,y:108,need:'hunger',label:'吃点东西',pose:'sit',line:['妈妈留的饭菜，热一热就能吃','真香'],rate:2},
  stove:{name:'灶台',rect:[226,66,46,43],x:250,y:108,need:'hunger',label:'做顿饭',line:['生火、切菜……','自己做的就是香'],rate:3},
  jar:{name:'水缸',rect:[272,82,34,27],x:285,y:108,need:'hunger',label:'喝口水',line:['井水凉丝丝的'],max:60}
 };
 const RATE={hunger:2.4,energy:.45,hygiene:3,bladder:8,fun:1.3,social:1.6};
 const NEED_SPOT={energy:'bed',hygiene:'bath',bladder:'toilet',hunger:'stove',fun:'settee'};
 let svc=null,lastT=sim.t,hinted=false,wasInside=false,leaving=false;
 const inRect=(x,y,[rx,ry,w,h])=>x>=rx&&x<rx+w&&y>=ry&&y<ry+h;
 function stop(){if(!svc)return;const s=C().state;s.pose=null;s.hideHero=false;svc=null;T.state.autoAt=sim.t+30;}
 function use(id,auto){
  const p=SPOTS[id],c=C();if(!p||!p.need)return;stop();closeRing();T.state.autoAt=sim.t+60;
  const begin=()=>{const s=c.state;s.x=p.x;s.facing=p.x>170?1:-1;svc={id,need:p.need,auto};s.pose=p.pose||null;s.hideHero=!!p.hide;speak(pick(p.line),true);};
  if(!c.state.inside){c.state.target=null;c.state.after=null;c.state.door={to:true,elapsed:0,duration:.65,mid:false};
   const wait=()=>{if(!inSpring())return;if(c.state.door||!c.state.inside)return setTimeout(wait,120);c.target(p.x,p.y,begin);};setTimeout(wait,120);}
  else c.target(p.x,p.y,begin);
 }
 function care(need){const id=NEED_SPOT[need],c=C();if(!id||svc||c.state.door||c.state.inside&&c.state.target)return;use(id,true);}
 // one click uses the furniture (owner 2026-11-03: "no second menu, click the furniture and use it"; only things like
 // the computer have a menu). Look-only spots: she walks over and says her line.
 function openSpot(id){const p=SPOTS[id];closeRing();
  if(p.look){C().target(p.x,p.y,()=>speak(pick(p.look),true));return;}
  if(sim.needs[p.need]>=(p.max||97)){speak(pick(['现在不用','等会儿再说']),true);return;}
  use(id);}
 X.hooks.click.push((x,y,s)=>{if(!s.inside)return false;
  for(const [id,p]of Object.entries(SPOTS))if(inRect(x,y,p.rect)){openSpot(id);return true;}
  if(svc)stop();return false;});
 X.hooks.pick.home=id=>use(id);
 X.hooks.pick.homelook=id=>{const p=SPOTS[id];C().target(p.x,p.y,()=>speak(pick(p.look),true));};
 X.hooks.pick.indoor=()=>{const c=C();if(!c.state.inside){c.state.target=null;c.state.door={to:true,elapsed:0,duration:.65,mid:false};}};
 X.hooks.pick.leave=()=>{leaving=true;stop();command('go_home');};
 // each frame: needs fill while she uses something; she walks in by herself when a need runs low
 X.hooks.draw.push((ctx,info)=>{
  const c=C(),s=c.state,dt=Math.max(0,Math.min(30,sim.t-lastT));lastT=sim.t;
  if(s.inside&&!wasInside&&!storyLocked()&&!hinted){hinted=true;setTimeout(()=>showHint('点家具能睡觉、洗澡、做饭'),700);}
  if(s.inside&&!wasInside)T.state.autoAt=Math.max(T.state.autoAt,sim.t+60);
  wasInside=s.inside;
  if(info.inside)sleepers(ctx,!!svc&&svc.id==='bed'&&s.inside&&!s.target);
  if(info.inside&&svc&&svc.id==='bath'&&s.inside&&!s.target){const p=SPOTS.bath,top=TUB_RIM-15,src=dollCanvas({expr:'happy',look:0,bob:0,sway:0,wave:null},'stand');
   ctx.drawImage(src,0,0,src.width,TUB_RIM-top,p.x-10,top,src.width,TUB_RIM-top);}   // in the tub: head and shoulders above the rim
  if(svc){
   if(s.target||!s.inside){s.pose=null;s.hideHero=false;svc=null;return;}
   const p=SPOTS[svc.id];T.state.autoAt=sim.t+1e6;
   if(info.inside&&p.zz&&!reduced()){const k=Math.floor(s.time*1.5)%3;ctx.fillStyle='#5d6176';ctx.font='8px monospace';ctx.fillText('z'.repeat(k+1),p.zz[0],p.zz[1]-k*2);}
   const n=sim.needs;n[svc.need]=Math.min(100,n[svc.need]+(p.rate||RATE[svc.need])*dt);
   if(n[svc.need]>=(p.max||97)){stop();log(pick(['歇好了。','舒服多了。','好了，接着干活。']));}
   return;}
  if(!inSpring()||springFarm.state.phase!=='done'||s.door||s.target||wiping||cardHolds()||ringOf||sim.mode==='down'||life.talkQ)return;
  const low=Object.entries(sim.needs).filter(([k,v])=>v<25&&NEED_SPOT[k]).sort((a,b)=>a[1]-b[1])[0];
  if(low){care(low[0]);return;}
  if(s.inside&&sim.t>=T.state.autoAt){T.state.autoAt=sim.t+40;c.leave();}   // nothing to do inside: back out to the yard
 });
 // asleep in a 架子床 (owner 2026-11-03): a head on its side on the pillow, the bed's own quilt bulging over the body
 // (art/src/concept/infei_bed_covers.py). Hers while she sleeps; 爸妈 in theirs at night (22:00-6:00), unless 妈妈 is up.
 const BEDS={mine:[81,16],parents:[219,16]};let covers=null;   // INFEI_COVERS is injected after this file: load on first use
 const lie=new Map();function lying(src){if(lie.has(src))return lie.get(src);const c=document.createElement('canvas');c.width=15;c.height=src.width;const g=c.getContext('2d');g.translate(0,src.width);g.rotate(-Math.PI/2);g.drawImage(src,0,0,src.width,15,0,0,src.width,15);lie.set(src,c);return c;}
 let dadN=null;const npcOf=(id,preset)=>{const lk=socialState.contacts.find(c=>c.id===id)?.look||doll.PRESETS[preset];return {look:lk,ramps:doll.rampsOf(lk),cache:new Map()};};
 const SLEEPY={expr:'sleepy',look:0,bob:0,sway:0,wave:null};
 function sleepers(ctx,she){
  if(!covers){covers={};for(const [k,u]of Object.entries(INFEI_COVERS)){const im=new Image();im.src=u;covers[k]=im;}}
  const m=sim.t%1440,night=m>=22*60||m<6*60;
  if(night&&!springFarm.mom.on&&covers.parents?.complete){const [bx,by]=BEDS.parents;dadN??=npcOf('dad','m');
   ctx.drawImage(lying(npcCanvas(dadN,SLEEPY,'stand')),bx+HEAD[0]+4,by+HEAD[1]-5);ctx.drawImage(lying(npcCanvas(springFarm.momNpc(),SLEEPY,'stand')),bx+HEAD[0],by+HEAD[1]);ctx.drawImage(covers.parents,bx,by);}
  if(she&&covers.mine?.complete){const [bx,by]=BEDS.mine;ctx.drawImage(lyingHead(SLEEPY),bx+HEAD[0],by+HEAD[1]);ctx.drawImage(covers.mine,bx,by);}
 }
 const HEAD=[2,8];
 const TUB_RIM=34;   // the bath tub's top edge (house px)   // the rotated head's place on the pillow, in bed-sprite coordinates
 const reduced=()=>matchMedia('(prefers-reduced-motion:reduce)').matches;
 // 回家 = the farmhouse; 离开茵菲谷 is the only way out (player only)
 const oldOpen=openRing;openRing=function(which,at){
  // owner 2026-11-04: the player can always leave, story finished or not (an unfinished welcome replays next time)
  if(which==='away'&&inSpring()){const keep=RINGS.away,inside=C().state.inside,done=springFarm.state.phase==='done';
   RINGS.away=(done?keep.map(r=>r[0]==='go_home'?(inside?['sf:home:bed','回房间歇歇']:['sf:indoor','回家']):r):keep.filter(r=>r[0]!=='go_home')).concat([['sf:leave','离开茵菲谷']]);
   try{return oldOpen(which,at);}finally{RINGS.away=keep;}}
  return oldOpen(which,at);};
 const oldHomeFor=homeFor;homeFor=function(k){if(inSpring()&&!leaving){speak(pick(['回屋里歇歇','先进屋一趟']),true);return;}return oldHomeFor(k);};
 const oldStart=startAct;startAct=function(name,quiet){
  if(inSpring()&&name==='go_home'&&!leaving){const low=Object.entries(sim.needs).sort((a,b)=>a[1]-b[1])[0];if(low[1]<40)care(low[0]);sim.mode='act';sim.act='season_explore';sim.actEnd=Infinity;return;}
  return oldStart(name,quiet);};
 const oldArrive=arriveAt;arriveAt=function(place){leaving=false;stop();hinted=false;if(place==='spring_test'){sim.outBack=null;sim.outWhy=null;}return oldArrive(place);};
 return {SPOTS,use,care,stop,get svc(){return svc;},leave:()=>X.hooks.pick.leave()};
})();
window.infeiHome=infeiHome;
