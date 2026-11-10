// 草帽湾 lodge furniture (game-shell test page only). Owner 2026-11-05: "the lodge must work like her own home":
// click the bed, sofa, stove, shower, toilet... and she walks over and uses it; hovering shows the house's glow.
// Canvas coords inside the lodge (the picture is drawn at 40,28; her feet at y 84). rect [x,y,w,h].
const summerLodge=(function(){
 const C=()=>seasonMapTest.state.summer,inBay=()=>sim.place==='summer_test';
 const SPOTS={
  bed:{rect:[49,52,46,26],x:72,need:'energy',act:'sleep',hide:true,line:['被子上有扶桑花，好看','海风吹着睡，真香'],zz:[66,50]},
  lamp:{rect:[95,48,13,30],x:100,look:['藤编的小台灯','床头放着一个贝壳，是谁捡的？']},
  print:{rect:[83,36,13,11],x:88,look:['画里是一道浪','这幅画看着就凉快']},
  board:{rect:[123,32,9,30],x:128,look:['阿洛的旧冲浪板，全是划痕','这块板子比我还高']},
  table:{rect:[136,67,19,11],x:146,need:'hunger',act:'snack',log:'吃了几块菠萝。',line:['吃块菠萝','青柠酸得眯眼睛']},
  sofa:{rect:[127,50,38,28],x:146,need:'fun',act:'season_sofa',iy:-8,line:['藤沙发吱呀一声','坐着听外面的海浪']},
  uke:{rect:[187,31,9,20],x:190,need:'fun',act:'season_uke',line:['借阿洛的尤克里里弹一首','叮叮咚咚～']},
  tv:{rect:[171,52,30,26],x:146,need:'fun',act:'tv',iy:-8,face:1,line:['看会儿电视','岛上的台也挺好看']},   // owner 2026-11-07: 客厅改沙发电视 (the home's TV act, watched from the sofa)
  dine:{rect:[210,52,34,26],x:216,need:'hunger',act:'eat',iy:-7,face:1,line:['开饭咯','真香']},   // owner 2026-11-06: the kitchen's own dining table
  sink:{rect:[246,55,12,23],x:252,need:'hunger',act:'snack',log:'接了杯凉水喝。',line:['接杯凉水喝','咕咚咕咚']},
  stove:{rect:[258,52,14,26],x:248,face:1,need:'hunger',act:'cook',line:['烧水、煮面……','自己做的就是香']},
  shower:{rect:[278,35,15,43],x:284,need:'hygiene',act:'season_shower',hide:true,line:['冲掉一身沙子','凉水澡真舒服']},
  basin:{rect:[297,44,14,18],x:304,need:'hygiene',act:'wash',line:['洗把脸，清醒了']},
  toilet:{rect:[292,62,14,16],x:299,need:'bladder',act:'toilet',iy:-6,line:['马上出来']}
 };
 const NEED_SPOT={energy:'bed',hygiene:'shower',bladder:'toilet',hunger:'stove',fun:'tv'};
 let svc=null,lastT=sim.t,hv=null,hinted=false;
 const inRect=(x,y,[rx,ry,w,h])=>x>=rx&&x<rx+w&&y>=ry&&y<ry+h;
 const hitSpot=(x,y)=>{for(const [id,p]of Object.entries(SPOTS))if(inRect(x,y,p.rect))return id;return null;};
 function stop(){if(!svc)return;const s=C().state;s.pose=null;s.hideHero=false;s.iy=0;seasonHouse.drop(svc.act);svc=null;}
 const ALIAS={bath:'shower',eat:'dine'};   // the home's act → this lodge's furniture
 // from anywhere on the island (the sea, the market): ashore, in through the door, then the furniture
 let goGen=0;function goUse(id,auto=true){if(id==='stove'&&auto&&sim.needs.hunger<25&&!homeMeal()){sim.quickMeal=true;id='sink';}   // owner 2026-11-10: red hunger → a ready meal, no cooking
const g=++goGen,t0=Date.now(),c=C();
  const step=()=>{if(g!==goGen||!inBay()||Date.now()-t0>60000)return;const s=c.state;
   if(s.inside&&!s.door){if(!s.target)use(id,auto);else setTimeout(step,300);return;}
   if(!s.door&&!s.target&&!s.inCabana&&!summerLife.isBusy()){if(s.market)c.beginDoor('bay');else if(s.y>131)c.goTo(1050,'dive',128);else c.enter();}
   setTimeout(step,400);};step();}
 function useAct(name){if(!inBay()||!C().state.inside)return false;const id=ALIAS[name]||Object.keys(SPOTS).find(k=>SPOTS[k].act===name);if(!id)return false;use(id,true);return true;}
 function use(id,auto){if(id==='dine'&&!homeMeal())id='stove';   // nothing on the table: cook first, then eat (as at home)
  if(id==='stove'&&!auto){closeRing();seasonHouse.menu('summer');return;}   // the player clicked the stove (or an empty table): the menu
  const p=SPOTS[id],c=C();if(!p)return;stop();closeRing();
  if(p.look){c.goTo(p.x,'walk',0,()=>speak(pick(p.look),true));return;}
  c.goTo(p.x,'walk',0,()=>{const s=c.state;s.facing=p.face||(p.x>170?1:-1);svc={id,act:p.act,need:p.need};s.pose=null;s.hideHero=!!p.hide;s.iy=p.iy||0;speak(pick(p.line),true);seasonHouse.start(p.act,{auto,log:p.log});});}
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
  if(s.inside&&seasonHouse.running('tv')){const f=nextTvFrame();if(f)ctx.drawImage(f,TV_AT[0],TV_AT[1]);}else if(typeof tvPlayback!=='undefined'&&inBay())tvPlayback.playing=false;   // the home's programmes on the lodge TV
  if(s.inside){seasonHouse.cookFx(ctx,COOK_FX[0],COOK_FX[1]);seasonHouse.meal(ctx,MEAL_AT[0],MEAL_AT[1]);}   // the home's pan and dish
  if(!svc)return;
  if(s.target||!s.inside||s.door){stop();return;}
  if(!seasonHouse.running(svc.act)){s.pose=null;s.hideHero=false;s.iy=0;svc=null;return;}   // the home's act is over
  const p=SPOTS[svc.id],t=s.time;
  if(svc.id==='bed'){const h=lyingHead(SLEEPY);ctx.drawImage(h,52,66-h.height);if(!coverImg){coverImg=new Image();coverImg.src=SUMMER_LIFE_ART.cover;}if(coverImg.complete)ctx.drawImage(coverImg,40,28);seasonHouse.sleepFx(ctx,62,52);}
  if(svc.id==='shower'){showerShadow(ctx,t);ctx.fillStyle='#bfe3f2';for(let i=0;i<6;i++){const y=38+((t*40+i*7)%36);ctx.fillRect(280+(i*5)%10,Math.round(y),1,2);}seasonHouse.emote(ctx,p.x+3,40);}}
 // owner 2026-11-09: in the shower a dark figure behind the steam (no plain empty stall)
 const shade=document.createElement('canvas');shade.width=20;shade.height=28;const shadeCtx=shade.getContext('2d');
 function showerShadow(ctx,t){
  shadeCtx.globalCompositeOperation='source-over';shadeCtx.clearRect(0,0,20,28);shadeCtx.drawImage(dollCanvas({expr:'happy',look:1,bob:0,sway:Math.floor(t*1.5)%2,wave:null},'stand'),0,0);
  shadeCtx.globalCompositeOperation='source-in';shadeCtx.fillStyle='#2b3550';shadeCtx.fillRect(0,0,20,28);
  ctx.save();ctx.beginPath();ctx.rect(278,35,15,43);ctx.clip();ctx.globalAlpha=.55;ctx.drawImage(shade,275,50);ctx.restore();   // kept inside the stall
  // steam: soft puffs rising out of the stall and fading at the top
  for(let i=0;i<9;i++){const k=(t*.35+i/9)%1,x=Math.round(276+((i*7)%12)+Math.sin(t*1.3+i)*2),y=Math.round(76-k*44);
   ctx.fillStyle=`rgba(255,255,255,${(.85*(1-k)*Math.min(1,k*4)).toFixed(2)})`;const w=2+(i%3);ctx.fillRect(x,y,w,w-1||1);}}
 const COOK_FX=[258,39],MEAL_AT=[227,53],TV_AT=[174,55];   // TV_AT: the screen of the home's TV on its cabinet (24×12)   // the home's pan steam over the burners, the dish on the dining table
 const oArrive=arriveAt;arriveAt=function(pl){stop();hinted=false;return oArrive(pl);};
 return {SPOTS,NEED_SPOT,use,useAct,goUse,stop,draw,get svc(){return svc;}};
})();
window.summerLodge=summerLodge;
