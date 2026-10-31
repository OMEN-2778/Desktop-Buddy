// Real native identities, avatar rendering and social dialogue on test-only terrain.
function installSeasonPeople(active,ctl){
 const cache=new Map();let region='',hover=null,approaching=null;
 const bubble=document.createElement('div');bubble.id='seasonNpcBubble';bubble.hidden=true;widget.append(bubble);
 const lines={
 spring_test:[['花田','>你也是顺着花香走来的？','差不多，走着走着就到这儿了','>我绕了两圈，鞋上都沾花粉了'],['风车','>刚才那阵风，把我帽子都吹跑了','追回来了吗？','>追到了，差点比帽子先起飞'],['拍照','>能帮我看看头发乱没？','有一点，风还挺大的','>算了，拍出来就当很有动感'],['散步','>今天这天气，不出来走走亏了','是啊，在家坐着也没什么事','>我本来只想走十分钟……现在都走饿了'],['花粉','>阿嚏！花是好看，鼻子不太同意','要不要往风车那边走？','>行，先给鼻子放个假']],
 summer_test:[['海风','>这海风吹得，头发都不用做造型了','免费的造型师，就是有点随意','>哈哈，回去估计梳不开'],['沙子','>鞋里全是沙，走一步响一下','你这是把沙滩打包带走了','>还没收我行李超重费呢'],['游泳','>看着岸挺近，游起来真不是一回事','慢慢来，别急','>嗯，我先在这儿漂会儿'],['浪花','>刚才一个浪过来，我喝了一口','味道怎么样？','>不推荐，也没得退'],['海底','>那边的鱼一转弯就不见了','我刚也看见了，颜色好亮','>它们这拐弯技术，比我好多了'],['晒太阳','>我带了防晒，结果忘了带毛巾','各有各的忘法，我忘了拖鞋','>咱俩凑一凑，刚好都不齐全'],['漂浮','>我就想安静漂着，什么也不干','这也挺好啊','>对，今天不努力了，努力也游不快'],['潜水','>那边珊瑚缝里有只小家伙','我等会儿绕过去看看','>别追它哈，它胆子可小了']]
 };
 for(const [key,adult]of Object.entries(lines))NPC_TALK_TEXT[key]={adult,kid:adult};
 function key(){const c=ctl();return sim.place+':'+(sim.place==='spring_test'?c.state.inside?'inside':c.state.scene:c.state.inside?'inside':'bay');}
 function make(x,kind,range=38){const n=makeNpc('adult',{x,feet:103,seasonKind:kind,origin:x,range,v:6,dir:Math.random()<.5?-1:1});n.phase=Math.random()*6;return n;}
 function sync(force=false){
  if(force)region='';
  if(!active()){if(region){stopNpcTalk();life.npcs=[];region='';}bubble.hidden=true;return;}
  const k=key();if(region===k)return;stopNpcTalk();approaching=null;hover=null;region=k;
  if(!cache.has(k)){
   const c=ctl(),s=c.state;let rows=[];
   if(!s.inside&&sim.place==='spring_test'&&s.scene<3)rows=[make(112,'walk'),make(245,'walk',45)];
   if(!s.inside&&sim.place==='summer_test')rows=[make(165,'walk'),make(510,'walk'),make(855,'walk'),...Array.from({length:4},(_,i)=>make(1230+i*88,'swim',26)),make(1510,'dive',45),make(1970,'dive',60)];
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
  if(n&&(n.sayUntil>realClock||q?.lastOther)){
   const text=q?.lastOther?q.lastText:n.sayText;if(text){if(bubble.textContent!==text)bubble.textContent=text;bubble.hidden=false;const s=c.state,x=n.x-(s.camera??s.camX??0),y=n.feet-(s.camY||0)-30;const scale=Number(view.style.width.replace('px',''))/342||view.width/342;bubble.style.left=Math.max(8,Math.min(342*scale-8,x*scale))+'px';bubble.style.top=(y*scale)+'px';}
  }else bubble.hidden=true;
 }
 function draw(ctx){sync();const c=ctl(),s=c.state;for(const n of life.npcs){const cx=s.camera??s.camX??0,cy=s.camY||0;if(n.x<cx-60||n.x>cx+400||n.feet<cy-5||n.feet>cy+c.canvas.height+40)continue;const [f,pose]=npcFrame(n),pic=npcCanvas(n,f,pose,false);
  if(n.seasonKind!=='walk'){const diving=n.seasonKind==='dive';c.fx.swimmer(ctx,{head:pic,skin:n.look.skin,sheet:c.personSheet(n.look.gender,diving?'wetsuit':'swim'),x:n.x,y:n.feet,time:s.time,facing:n.dir,diving,moving:!n.paused,wetsuit:diving,waterline:116,phase:n.phase});}
  else{if(hover===n)drawObjectHover(ctx,pic,n.x-10,n.feet-27);ctx.drawImage(pic,n.x-10,n.feet-27);}
 }}
 function hit(x,y){return [...life.npcs].reverse().find(n=>Math.abs(n.x-x)<(n.seasonKind==='walk'?12:33)&&Math.abs(n.feet-y-(n.seasonKind==='dive'?0:13))<18);}
 function click(x,y){const n=hit(x,y);if(!n)return false;if(!canClickNpc(n)||npcRefusesDirty(n,true))return true;
  const c=ctl(),s=c.state;if(n.seasonKind!=='walk'&&s.suit==='clothes'){showHint('先换上泳装再游过去吧');return true;}
  stopNpcTalk();if(approaching)approaching.paused=false;approaching=n;n.paused=true;
  const tx=n.x+(s.x<n.x?-15:15),done=()=>{if(active()&&life.npcs.includes(n)){s.facing=Math.sign(n.x-s.x)||1;n.dir=-s.facing;if(!startNpcTalk(n,true))n.paused=false;}approaching=null;};
  if(sim.place==='spring_test')c.target(tx,103,done);else c.goTo(tx,n.seasonKind==='dive'?'dive':'walk',n.feet,done);return true;
 }
 function cancel(){if(approaching)approaching.paused=false;approaching=null;stopNpcTalk();bubble.hidden=true;}
 return {sync,tick,draw,click,cancel,hover:(x,y)=>hover=hit(x,y),cache};
}
