// 草帽湾 lodge furniture (game-shell test page only). Owner 2026-11-05: "the lodge must work like her own home":
// click the bed, sofa, stove, shower, toilet... and she walks over and uses it; hovering shows the house's glow.
// Canvas coords inside the lodge (the picture is drawn at 40,28; her feet at y 84). rect [x,y,w,h].
const summerLodge=(function(){
 const C=()=>seasonMapTest.state.summer,inBay=()=>sim.place==='summer_test';
 const SPOTS={
  bed:{rect:[49,52,46,26],x:72,need:'energy',hide:true,line:['被子上有扶桑花，好看','海风吹着睡，真香'],zz:[66,50]},
  lamp:{rect:[95,48,13,30],x:100,look:['藤编的小台灯','床头放着一个贝壳，是谁捡的？']},
  print:{rect:[83,36,13,11],x:88,look:['画里是一道浪','这幅画看着就凉快']},
  board:{rect:[123,32,9,30],x:128,look:['阿洛的旧冲浪板，全是划痕','这块板子比我还高']},
  table:{rect:[140,66,26,12],x:153,need:'hunger',max:70,rate:2,line:['吃块菠萝','青柠酸得眯眼睛']},
  sofa:{rect:[126,48,58,30],x:160,need:'fun',max:90,pose:'sit',iy:-8,line:['藤沙发吱呀一声','坐着听外面的海浪']},
  uke:{rect:[183,33,9,23],x:186,need:'fun',max:95,line:['借阿洛的尤克里里弹一首','叮叮咚咚～']},
  plant:{rect:[190,57,11,21],x:195,look:['龟背竹长得比我胖','叶子上有水珠']},
  sink:{rect:[217,55,17,23],x:226,need:'hunger',max:60,line:['接杯凉水喝','咕咚咕咚']},
  stove:{rect:[237,52,19,26],x:246,need:'hunger',rate:3,line:['烧水、煮面……','自己做的就是香']},
  shower:{rect:[262,35,15,43],x:268,need:'hygiene',hide:true,line:['冲掉一身沙子','凉水澡真舒服']},
  basin:{rect:[281,44,14,18],x:288,need:'hygiene',max:70,line:['洗把脸，清醒了']},
  toilet:{rect:[276,62,14,16],x:283,need:'bladder',pose:'sit',iy:-6,line:['马上出来']}
 };
 const RATE={hunger:2.4,energy:.45,hygiene:3,bladder:8,fun:1.3};
 const NEED_SPOT={energy:'bed',hygiene:'shower',bladder:'toilet',hunger:'stove',fun:'sofa'};
 let svc=null,lastT=sim.t,hv=null,hinted=false;
 const inRect=(x,y,[rx,ry,w,h])=>x>=rx&&x<rx+w&&y>=ry&&y<ry+h;
 const hitSpot=(x,y)=>{for(const [id,p]of Object.entries(SPOTS))if(inRect(x,y,p.rect))return id;return null;};
 function stop(){if(!svc)return;const s=C().state;s.pose=null;s.hideHero=false;s.iy=0;svc=null;}
 function use(id,auto){const p=SPOTS[id],c=C();if(!p)return;stop();closeRing();
  if(p.look){c.goTo(p.x,'walk',0,()=>speak(pick(p.look),true));return;}
  c.goTo(p.x,'walk',0,()=>{const s=c.state;s.facing=p.x>170?1:-1;svc={id,need:p.need,until:sim.t+20};s.pose=p.pose||null;s.hideHero=!!p.hide;s.iy=p.iy||0;speak(pick(p.line),true);});}
 // clicks: the adapter asks summerLife first; inside the lodge that is us
 const oClick=summerLife.click;summerLife.click=function(x,y){
  const s=C().state;if(inBay()&&s.inside&&!s.door){const id=hitSpot(x,y);if(id){use(id);return true;}stop();return false;}
  return oClick.apply(this,arguments);};
 // hover glow, like the furniture at home
 const boxes=new Map();function box(w,h){const k=w+'x'+h;if(!boxes.has(k)){const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,w,h);boxes.set(k,c);}return boxes.get(k);}
 view.parentElement.addEventListener('pointermove',e=>{if(e.target!==view||!inBay()||!C().state.inside){hv=null;return;}
  const r=view.getBoundingClientRect(),id=hitSpot((e.clientX-r.left)*342/r.width,(e.clientY-r.top)*C().canvas.height/r.height);hv=id&&SPOTS[id].rect;},true);
 view.addEventListener('pointerleave',()=>{hv=null;});
 let coverImg=null;   // art/src/concept/summer_lodge_cover.py: the quilt bulging over her, in lodge-picture coords
 const SLEEPY={expr:'sleepy',look:0,bob:0,sway:0,wave:null};
 // drawn by the summer viewer every frame she is inside (after her)
 function draw(ctx){if(!inBay())return;const c=C(),s=c.state,dt=Math.max(0,Math.min(30,sim.t-lastT));lastT=sim.t;
  if(!hinted&&!storyLocked()){hinted=true;setTimeout(()=>showHint('点家具能睡觉、洗澡、做饭'),700);}
  if(hv)drawObjectHover(ctx,box(hv[2],hv[3]),hv[0],hv[1]);
  if(!svc)return;
  if(s.target||!s.inside||s.door){stop();return;}
  const p=SPOTS[svc.id],t=s.time;
  if(svc.id==='bed'){const h=lyingHead(SLEEPY);ctx.drawImage(h,52,66-h.height);if(!coverImg){coverImg=new Image();coverImg.src=SUMMER_LIFE_ART.cover;}if(coverImg.complete)ctx.drawImage(coverImg,40,28);ctx.fillStyle='#5d6176';ctx.font='8px monospace';const k=Math.floor(t*1.5)%3;ctx.fillText('z'.repeat(k+1),p.zz[0],p.zz[1]-k*2);}
  if(svc.id==='shower'){ctx.fillStyle='#bfe3f2';for(let i=0;i<6;i++){const y=38+((t*40+i*7)%36);ctx.fillRect(264+(i*5)%10,Math.round(y),1,2);}}
  const n=sim.needs;n[svc.need]=Math.min(100,n[svc.need]+(p.rate||RATE[svc.need])*dt);
  if(n[svc.need]>=(p.max||97)&&sim.t>=svc.until){stop();log(pick(['歇好了。','舒服多了。']));}}
 const oArrive=arriveAt;arriveAt=function(pl){stop();hinted=false;return oArrive(pl);};
 return {SPOTS,NEED_SPOT,use,stop,draw,get svc(){return svc;}};
})();
window.summerLodge=summerLodge;
