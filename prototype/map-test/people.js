// Real native identities, avatar rendering and social dialogue on test-only terrain.
function installSeasonPeople(active,ctl){
 const cache=new Map(),walkers=[];let region='',hover=null,approaching=null;
 const bubble=makeNpcPill(widget);bubble.id='seasonNpcBubble';bubble.hidden=true;
 const lines={
 spring_test:[['花田','>你也是顺着花香走来的？','差不多，走着走着就到这儿了','>我绕了两圈，鞋上都沾花粉了'],['风车','>刚才那阵风，把我帽子都吹跑了','追回来了吗？','>追到了，差点比帽子先起飞'],['拍照','>能帮我看看头发乱没？','有一点，风还挺大的','>算了，拍出来就当很有动感'],['散步','>今天这天气，不出来走走亏了','是啊，在家坐着也没什么事','>我本来只想走十分钟……现在都走饿了'],['花粉','>阿嚏！花是好看，鼻子不太同意','要不要往风车那边走？','>行，先给鼻子放个假']],
 summer_test:[['海风','>这海风吹得，头发都不用做造型了','免费的造型师，就是有点随意','>哈哈，回去估计梳不开'],['沙子','>鞋里全是沙，走一步响一下','你这是把沙滩打包带走了','>还没收我行李超重费呢'],['游泳','>看着岸挺近，游起来真不是一回事','慢慢来，别急','>嗯，我先在这儿漂会儿'],['浪花','>刚才一个浪过来，我喝了一口','味道怎么样？','>不推荐，也没得退'],['海底','>那边的鱼一转弯就不见了','我刚也看见了，颜色好亮','>它们这拐弯技术，比我好多了'],['晒太阳','>我带了防晒，结果忘了带毛巾','各有各的忘法，我忘了拖鞋','>咱俩凑一凑，刚好都不齐全'],['漂浮','>我就想安静漂着，什么也不干','这也挺好啊','>对，今天不努力了，努力也游不快'],['潜水','>那边珊瑚缝里有只小家伙','我等会儿绕过去看看','>别追它哈，它胆子可小了']]
 };
 for(const [key,adult]of Object.entries(lines))NPC_TALK_TEXT[key]={adult,kid:adult};
 function key(){const c=ctl();return sim.place+':'+(sim.place==='spring_test'?c.state.inside?'inside':c.state.scene:c.state.inside?'inside':c.state.market?'market':'bay');}   // 市集 people come from summer_life.js
 function make(x,kind,range=38){const n=makeNpc('adult',{x,feet:103,seasonKind:kind,origin:x,range,v:6,dir:Math.random()<.5?-1:1});n.phase=Math.random()*6;return n;}
 function sync(force=false){
  if(force)region='';
  if(!active()){if(region){stopNpcTalk();life.npcs=[];walkers.length=0;region='';}bubble.hidden=true;return;}
  const k=key();if(region===k)return;stopNpcTalk();approaching=null;hover=null;walkers.length=0;region=k;
  if(!cache.has(k)){
   const c=ctl(),s=c.state;let rows=[];
   if(!s.inside&&sim.place==='spring_test'&&s.scene<3)rows=[make(112,'walk'),make(245,'walk',45)];
   if(!s.inside&&!s.market&&sim.place==='summer_test')rows=[make(165,'walk'),make(510,'walk'),make(855,'walk'),...Array.from({length:4},(_,i)=>make(1230+i*88,'swim',26)),make(1510,'dive',45),make(1970,'dive',60)];
   cache.set(k,rows);
  }life.npcs=cache.get(k);
 }
 function tick(dt){sync();if(!active())return;const c=ctl();if(approaching&&!c.state.after&&!life.talkQ){approaching.paused=false;approaching=null;}
  for(const n of life.npcs){if(!n.paused){n.x+=n.dir*n.v*dt;if(Math.abs(n.x-n.origin)>n.range)n.dir*=-1;n.dist+=n.v*dt;}
   n.feet=sim.place==='spring_test'?103:n.seasonKind==='walk'?c.gr(n.x):n.seasonKind==='swim'?128+Math.sin(realClock*1.7+n.phase)*.5:Math.min(c.gr(n.x)-20,170+Math.sin(realClock*.35+n.phase)*12);
  }
  if(sim.place==='summer_test')for(const n of life.npcs)if(n.seasonKind!=='walk'&&Math.abs(n.x-c.state.camX-171)<250&&Math.abs(n.feet-c.state.camY-c.canvas.height/2)<c.canvas.height/2+40)c.fx.waterActor(n.personId,n.x,n.feet,n.dir,!n.paused,n.seasonKind==='dive',dt,116);
  if(life.talkQ)advanceNpcTalk(dt);
  const q=life.talkQ,n=q?.n||life.npcs.find(n=>n.sayUntil>realClock);
  const text=n&&(n.sayUntil>realClock||q?.lastOther)&&(q?.lastOther?q.lastText:n.sayText);
  if(text){
   if(bubble.textContent!==text)bubble.textContent=text;
   const p=seasonMapTest.viewport(c).scene(n.x,n.feet-30);
   positionNpcPill(bubble,p.x,p.y);
  }else bubble.hidden=true;
 }
 function draw(ctx){sync();walkers.length=0;const c=ctl(),s=c.state;for(const n of life.npcs){const cx=s.camera??s.camX??0,cy=s.camY||0;if(n.x<cx-60||n.x>cx+400||n.feet<cy-5||n.feet>cy+c.canvas.height+40)continue;const [f,pose]=npcFrame(n),water=n.seasonKind!=='walk';if(water){f.wave=Math.floor(s.time/.28+n.phase)%2;f.bob=0;f.sway=0;}const pic=npcCanvas(n,f,water?'stand':pose,false);
  if(n.seasonKind!=='walk'){const diving=n.seasonKind==='dive';c.fx.swimmer(ctx,{head:pic,skinRamp:n.ramps.skin,sheet:c.personSheet(n.look.gender,diving?'wetsuit':'swim'),x:n.x,y:n.feet,time:s.time,facing:n.dir,diving,moving:!n.paused,wetsuit:diving,waterline:116,phase:n.phase});}
  else{
   const x=Math.round(n.x-10),y=Math.round(n.feet-27);
   if(hover===n)drawObjectHover(ctx,pic,x,y);
   ctx.drawImage(pic,x,y);walkers.push({img:pic,x,y,npc:n});
  }
 }}
 function hit(x,y){
  return sceneTargetAt(walkers,x,y)?.npc||life.npcs.findLast(n=>n.seasonKind!=='walk'&&Math.abs(n.x-x)<(n.seasonKind==='dive'?17:12)&&Math.abs(n.feet-y-14)<18);
 }
 function click(x,y){const n=hit(x,y);if(!n)return false;if(!canClickNpc(n)||npcRefusesDirty(n,true))return true;
  const c=ctl(),s=c.state;if(n.seasonKind!=='walk'&&s.suit==='clothes'){showHint('先换上泳装再游过去吧');return true;}
  stopNpcTalk();if(approaching)approaching.paused=false;approaching=n;n.paused=true;
  const tx=n.x+(s.x<n.x?-15:15),done=()=>{if(active()&&life.npcs.includes(n)){s.facing=Math.sign(n.x-s.x)||1;n.dir=-s.facing;if(!startNpcTalk(n,true))n.paused=false;}approaching=null;};
  if(sim.place==='spring_test')c.target(tx,103,done);else c.goTo(tx,n.seasonKind==='dive'?'dive':'walk',n.feet,done);return true;
 }
 function cancel(){if(approaching)approaching.paused=false;approaching=null;stopNpcTalk();bubble.hidden=true;}
 return {sync,tick,draw,hit,click,cancel,hover:(x,y)=>hover=hit(x,y),cache};
}

// Walk within each street's paved segment. Stable slots let returning players
// recognize who stayed after the relocation, and keep masks stable for a day.
function autumnPedestrians(data) {
 const streets=data.residentRoutes||data.routes.filter(([name])=>['山顶街','矿业街','中城街','工人街','河岸街'].includes(name));
 const models=new WeakMap();
 return function residents(state,height,reserved=[]) {
  const sprites=[];
  const locals=data.town?.residents;
  const people=locals||socialState.world;
  if(!people.length)return sprites;
  const moved=window.liweiStory?.progress.done.includes('S12B');
  const day=Math.floor(sim.t/1440);
  const chance=[.64,.5,.35,.18,.06][state.stage];
  function resident(i,x,y,distance,direction,moving=true,sitting=false,vendor=null,shopVisitor=false){
   if(x<state.camX-12||x>state.camX+354||y<state.camY||y-28>state.camY+height)return;
   const identity=people[i%people.length];
   const person=locals?{look:identity}:identity,masked=(i*17+day*7)%30 < 30*chance;
   let variants=models.get(identity);
   if(!variants){variants=new Map();models.set(identity,variants);}
   if(!variants.has(masked)){
    const acc=person.look.acc.filter(a=>a!=='mask');
    if(masked)acc.push('mask');
    const look=doll.normalize({...person.look,acc});
    variants.set(masked,{look,ramps:doll.rampsOf(look),kid:person.child,cache:new Map()});
   }
   const model=variants.get(masked);
   const npc=locals&&!vendor?{id:'liwei-local:'+i,name:identity.name,x,y,local:i,shopVisitor}:null;
   const waiting=npc&&state.goal?.id==='npc:'+npc.id;
   Object.assign(model,{dist:distance,dir:direction,v:moving&&!waiting?1:0,ph:i*291});
   const [frame,pose]=npcFrame(model);
   sprites.push({depth:y,walker:true,vendor,npc,img:npcCanvas(model,frame,sitting?'sit':pose,false),x:x-10,y:y-29});
  }
  streets.forEach(([,points],street)=>{
   const [left,y]=points[0],right=points.at(-1)[0];
   const population=locals?8:6,lane=(right-left)/population;
   for(let slot=0;slot<population;slot++){
    if(moved&&slot!==1&&slot!==4)continue;
    const i=street*population+slot,distance=state.streetTime*(5+i%4)+i*31;
    let from=left+slot*lane+11,to=from+lane-22;
    // Keep enough room to see and click fixed story actors on the same street.
    for(const actor of reserved){
     if(Math.abs(actor.y-y)>=24||actor.x+18<=from||actor.x-18>=to)continue;
     if(actor.x-18-from>=to-actor.x-18)to=actor.x-18;
     else from=actor.x+18;
    }
    const range=to-from;
    if(range<3)continue;
    const phase=distance%(2*range);
    const x=Math.round(from+Math.min(phase,2*range-phase));
    resident(i,x,y,distance,phase<range?1:-1);
   }
  });
  for(const [i,[x,y,vendor]] of (data.town?.vendors||[]).entries()){
   resident((locals?40:32)+i,x,y,0,0,false,false,vendor);
  }
  const store=window.liweiNeighborhood?.shopOpen()&&data.landmarks.find(mark=>mark.id==="store");
  if(store&&hour()>=8&&hour()<20){
   for(let i=0;i<3;i++){
    const east=i%2===0,side=east?1:-1,span=82+i*10;
    const walkingTime=span/12,wait=3+i*2;
    const phase=(state.streetTime+i*7)%(walkingTime*2+wait);
    const offset=phase<walkingTime?span-phase*12:phase<walkingTime+wait?0:(phase-walkingTime-wait)*12;
    resident(people.length+i,Math.round(store.x+side*(14+offset)),store.y+12+i*8,
      state.streetTime*12,phase<walkingTime?-side:side,offset>0,false,null,true);
   }
  }
  const path=data.town?.parkWalk;
  if(path){
   const [west,north]=path[0], [east,south]=path[2];
   const route=[[west,north],[east,north],[east,south],[576,south],[481,south],[west,south],[west,north]];
   const waits=[0,1.5,0,8,6,0];
   const speed=13;
   const durations=route.slice(0,-1).map(([x,y],i)=>Math.hypot(route[i+1][0]-x,route[i+1][1]-y)/speed+waits[i]);
   const loop=durations.reduce((sum,step)=>sum+step,0);
   for(let i=0;i<(moved?2:4);i++){
    let t=(state.streetTime+i*loop/4)%loop,j=0;
    while(t>=durations[j])t-=durations[j++];
    const [x,y]=route[j], [toX,toY]=route[j+1];
    const walking=t<durations[j]-waits[j], fraction=Math.min(1,t/(durations[j]-waits[j]));
    resident((locals?44:38)+i,Math.round(x+(toX-x)*fraction),Math.round(y+(toY-y)*fraction),
             state.streetTime*speed,Math.sign(toX-x),walking,!walking&&(j===2||j===3||j===4));
   }
  }
  return sprites;
 };
}
