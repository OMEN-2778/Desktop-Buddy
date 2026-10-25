// Furniture in a friend's house owns its hit mask, destination, pose and
// foreground. No interaction borrows coordinates from the hero's house.
const FRIEND_HOME_EFFECTS={eat:{hunger:2.5,fun:.08},toilet:{bladder:8},bath:{hygiene:3},wash:{hygiene:1.5},towel:{hygiene:.4},sit:{energy:.16,fun:.15,social:.1},tv:{fun:.5,social:.12,energy:.08},read:{fun:.3,energy:.08},computer:{fun:.45},water:{fun:.18},music:{fun:.4},art:{fun:.2},laundry:{hygiene:.35},cook:{fun:.12},chat:{social:.4,fun:.16},sleep:{energy:.16}};
const FRIEND_OBJECT_ACTION={entry:'leave',bed:'sleep',sofa:'tv',reading_sofa:'sit',chair:'sit',tv:'tv',media:'tv',monitor:'computer',desk:'computer',bookcase:'read',coffee_table:'eat',tea_table:'eat',table:'eat',toilet:'toilet',tub:'bath',shower:'bath',basin:'wash',towel:'towel',plant:'water',planter:'water',desktop_plant:'water',guitar:'music',keyboard:'music',washer:'laundry',art:'art',scroll:'art',easel:'art',window:'window',glass:'window',lamp:'lamp',floor_lamp:'lamp',fridge:'snack',kitchen:'cook',cabinets:'cook',wardrobe:'inspect',nightstand:'inspect'};
Object.assign(FRIEND_VISIT_ACTS,{tv:'坐在沙发上看电视',computer:'借用电脑',read:'坐着看书',wash:'洗手洗脸',towel:'擦干手',water:'帮忙浇花',music:'试着弹奏',laundry:'帮忙洗衣',cook:'准备饭菜',art:'欣赏摆设',window:'看看窗外',inspect:'看看家具'});
ACTS.friend_snack={...ACTS.snack,label:'拿点吃的'};
PICK.friend_snack={title:'朋友家的冰箱 · 拿点什么',groups:()=>[{name:'吃点小零食',items:T.snacks.map(name=>({title:name,icon:(D.items.dish.fruit||D.items.dish.rice)[0],item:{vars:{零食:name,食物:name}}}))}]};
function friendHouseObject(id){return visitingHouse()?.furniture.find(f=>f.id===id)||null;}
function friendObjectRoom(f){const h=visitingHouse();return h.rooms.find(r=>r.id===f.room)||friendVisitRoom(h,f.x+f.w/2,f.y+f.h);}
function friendObjects(kinds,near=null){
 const list=visitingHouse().furniture.filter(f=>kinds.includes(f.kind));
 if(!near)return list;
 return list.sort((a,b)=>((a.room===near.room?0:1000)+Math.abs(a.y-near.y)*4+Math.abs(a.x-near.x))-((b.room===near.room?0:1000)+Math.abs(b.y-near.y)*4+Math.abs(b.x-near.x)));
}
function friendSeat(f){
 const r=friendObjectRoom(f),v=friendVisit,off=(W-visitingHouse().w)/2;
 if(['sofa','reading_sofa'].includes(f.kind)){
  const left=f.x+12,right=f.x+29;return {x:off+(Math.abs(v.host.x-off-left)<12&&Math.abs(v.host.y-r.floor)<5?right:left),y:r.floor-3};
 }
 if(f.kind==='bed')return {x:off+f.x+f.w-12,y:r.floor-3};
 return {x:off+f.x+f.w/2,y:r.floor-(f.h>=20?5:4)};
}
function startFriendHouseAction(action,selected=null,item=null){
 if(!atFriendHome()||sim.mode==='down')return false;
 const h=visitingHouse(),v=friendVisit,off=(W-h.w)/2,choose=k=>friendObjects(k,selected)[0];
 if(action==='leave')return leaveFriendHome();
 if(action==='chat'){friendVisitWalk({x:Math.min(W-12,v.host.x+17),y:v.host.y},action,40);v.objectId=v.seatId=null;return true;}
 let object=selected,seat=null,duration=25,target=null;
 if(action==='sleep'){
  if(!v.stay){showHint('先点击朋友，问问今晚能不能借住吧。');return false;}
  const bed=choose(['bed']);
  if(selected?.kind==='bed'&&selected.id!==bed?.id){showSay('那间是家里人住的，我给你安排这边吧。',contactName(visitingFriend())+'：',visitingFriend());object=choose(['sofa'])||bed;}
  else object=selected&&['sofa','reading_sofa','bed'].includes(selected.kind)?selected:choose(['sofa'])||bed;
  duration=720;
 }else if(action==='tv'){
  object=selected?.kind==='tv'?selected:choose(['tv']);
  if(!object||selected&&['sofa','reading_sofa'].includes(selected.kind)&&object.room!==selected.room)return startFriendHouseAction('sit',selected);
  else{seat=selected&&['sofa','reading_sofa'].includes(selected.kind)?selected:friendObjects(['sofa','reading_sofa','chair'],object).find(f=>f.room===object.room);duration=55;}
 }else if(action==='computer'){
  object=selected?.kind==='monitor'?selected:choose(['monitor']);
  seat=object&&friendObjects(['chair'],object).find(f=>f.room===object.room);duration=45;
 }else if(action==='toilet'){object=selected?.kind==='toilet'?selected:choose(['toilet']);duration=12;}
 else if(action==='bath'){object=selected&&['tub','shower'].includes(selected.kind)?selected:choose(['tub','shower']);duration=25;}
 else if(action==='wash'){object=selected?.kind==='basin'?selected:choose(['basin']);duration=10;}
 else if(action==='towel'){duration=8;}
 else if(action==='cook'){object=selected?.kind==='kitchen'?selected:choose(['kitchen']);duration=40;}
 else if(action==='eat'){
  object=selected&&['table','coffee_table','tea_table'].includes(selected.kind)?selected:choose(['table','coffee_table','tea_table']);
  if(object)seat=friendObjects(['chair','sofa','reading_sofa'],object).find(f=>f.room===object.room);
  if(!object)object=choose(['fridge'])||choose(['bed']);
 }else if(action==='read'){
  object=selected?.kind==='bookcase'?selected:choose(['bookcase']);
  if(object)seat=friendObjects(['reading_sofa','chair','sofa','bed'],object).find(f=>f.room===object.room);duration=45;
 }else if(action==='sit'){
  object=selected&&['sofa','reading_sofa','chair','bed'].includes(selected.kind)?selected:choose(['sofa','reading_sofa','chair','bed']);seat=object;duration=30;
 }else if(action==='window'){duration=14;}
 else if(['water','music','art','inspect','laundry'].includes(action)){duration=action==='water'?12:action==='music'?35:20;}
 if(!object){showHint('这间屋里暂时没有能这样使用的家具。');return false;}
 const room=friendObjectRoom(object);
 target=seat?friendSeat(seat):{x:off+object.x+object.w/2,y:room.floor};
 if(action==='toilet')target.y=room.floor-7;
 friendVisitWalk(target,action,duration,!!seat||action==='toilet');
 v.objectId=object.id;v.seatId=seat?.id||null;v.mealItem=action==='eat'||action==='cook'?item||v.mealItem||null:null;
 v.sleepFurniture=action==='sleep'?object:null;v.bedIndex=action==='sleep'?h.furniture.indexOf(object):null;
 v.hover=null;return true;
}
function onFriendHouseActionStart(){
 const v=friendVisit,c=visitingFriend(),o=friendHouseObject(v.objectId);if(!o)return;
 const food=v.mealItem?.vars?.食物||v.mealItem?.vars?.零食||'朋友准备的小点心';
 const texts={tv:'在朋友家的沙发上坐好，一起看电视。',computer:'借用了一会儿朋友的电脑。',read:'挑了本书，找个位置坐下慢慢看。',eat:'在朋友家吃了'+food+'。',cook:'借用朋友家的厨房，准备'+food+'。',toilet:'借用了朋友家的卫生间。',bath:'在朋友家洗了个澡。',wash:'在洗手台洗了洗手和脸。',towel:'拿干净的小毛巾擦了擦手。',water:'帮朋友照看了一下绿植。',music:'在朋友家试着弹了一小段。',art:'看了看朋友挑选的画和摆设。',laundry:'帮朋友把洗衣机里的衣服转起来。',inspect:o.kind==='wardrobe'?'看了看朋友的衣柜，没有翻动里面的衣服。':'看了看朋友屋里的小物件。'};
 if(texts[v.action])log(texts[v.action]);
 if(v.action==='window'){
  const line=weather.kind==='snow'?'外头的雪还在下，窗边看得特别清楚。':weather.kind==='storm'?'外头雨可真大，先在屋里待着吧。':weather.kind==='rain'?'雨还没停呢，先坐着，别急着走。':duskState().strength?'你看窗外，这会儿的天还挺好看。':'从这儿能看见外面，站窗边透透气也不错。';showSay(line,contactName(c)+'：',c);
 }
}
function finishFriendHouseAction(){
 const v=friendVisit;
 if(v.action==='cook'){const item=v.mealItem;startFriendHouseAction('eat',null,item);return true;}
 if(v.action==='eat'){v.mealItem=null;applyNeedConsequences();}
 if(['water','music','laundry'].includes(v.action)){
  const c=visitingFriend();if(c)finishContactTalk(c.id,'visit-chat');
 }
 v.objectId=v.seatId=null;return false;
}
function interactFriendFurniture(f){
 const v=friendVisit,kind=f.kind,action=FRIEND_OBJECT_ACTION[kind]||'inspect';
 if(action==='lamp'){
  v.lamps||={};v.lamps[f.id]=!v.lamps[f.id];showSay(v.lamps[f.id]?'把灯打开了，窗边暖和了点。':'把这盏灯关上了。');return true;
 }
 if(['snack','cook','read'].includes(action)){
  v.pendingFurnitureId=f.id;openPicker(action==='snack'?'friend_snack':action,{x:(W-visitingHouse().w)/2+f.x+f.w/2,y:f.y+f.h/2});return true;
 }
 return startFriendHouseAction(action,f);
}
function friendFurnitureAt(x,y,foregroundOnly=false){
 const h=visitingHouse(),off=(W-h.w)/2,images=IMG.friendHouses[friendVisit.houseId].objects;
 const objects=h.furniture.filter(f=>images[f.id]&&(!foregroundOnly||f.front)).reverse();
 for(const f of objects){
  const image=images[f.id];if(!outlineCache.has(image))outlineCache.set(image,outlineShape(image));
  const shape=outlineCache.get(image);if(shape.near.has(Math.floor(x-off-f.x)+','+Math.floor(y-f.y)))return {kind:'furniture',f};
 }
 return null;
}
function drawFriendFurnitureHover(ctx){
 const hit=friendVisit.hover;if(hit?.kind!=='furniture')return;
 const f=hit.f,image=IMG.friendHouses[friendVisit.houseId].objects[f.id];if(image)drawObjectHover(ctx,image,(W-visitingHouse().w)/2+f.x,f.y);
}
function drawFriendHomeScreens(ctx){
 const v=friendVisit;if(sim.mode!=='act')return;const o=friendHouseObject(v.objectId),off=(W-visitingHouse().w)/2;
 if(!o)return;
 if(v.action==='tv'){
  const image=nextTvFrame();if(image)ctx.drawImage(image,off+o.x+1,o.y+1);
 }else if(v.action==='computer'){
  const frames=IMG.mon[Object.keys(IMG.mon)[Math.floor(realClock/12)%Object.keys(IMG.mon).length]];
  if(frames)ctx.drawImage(frameOf(frames,5),off+o.x+1,o.y+1);
 }
}
function drawFriendHomeLamps(ctx){
 const v=friendVisit,h=visitingHouse(),off=(W-h.w)/2;
 for(const [id,on]of Object.entries(v.lamps||{})){
  const o=friendHouseObject(id);if(!on||!o)continue;const r=friendObjectRoom(o),x=off+o.x+o.w/2,y=o.y+4;
  ctx.save();ctx.beginPath();ctx.rect(off+r.x,r.y,r.w,r.floor-r.y+6);ctx.clip();ctx.globalCompositeOperation='source-atop';
  const light=ctx.createRadialGradient(x,y,1,x,y,28);light.addColorStop(0,'rgba(255,236,179,.52)');light.addColorStop(1,'rgba(255,224,169,0)');ctx.fillStyle=light;ctx.fillRect(off+r.x,r.y,r.w,r.floor-r.y+6);ctx.restore();
 }
}
function drawFriendFixtureUser(ctx,f){
 const v=friendVisit,o=friendHouseObject(v.objectId);if(sim.mode!=='act'||!o||!['toilet','bath'].includes(v.action))return false;
 const off=(W-visitingHouse().w)/2,room=friendObjectRoom(o),image=IMG.friendHouses[v.houseId].objects[o.id];
 ctx.save();ctx.beginPath();ctx.rect(off+room.x,room.y,room.w,room.floor-room.y+6);ctx.clip();
 if(o.kind==='tub'){
  ctx.drawImage(dollCanvas({...f,expr:'neutral'},'stand',14),off+o.x+5,o.y+6);
  ctx.drawImage(IMG.ov.bubbles,off+o.x,o.y+18);
  ctx.drawImage(image,0,21,o.w,o.h-21,off+o.x,o.y+21,o.w,o.h-21);
 }else if(o.kind==='shower'){
  ctx.drawImage(dollCanvas({...f,expr:'neutral'},'stand',14),off+o.x-3,o.y+4);
  ctx.fillStyle='rgba(176,211,218,.2)';ctx.fillRect(off+o.x+1,o.y+2,o.w-2,o.h-5);
  ctx.fillStyle='#d9eaf0';for(let i=0;i<4;i++)ctx.fillRect(off+o.x+3+i*4,o.y+10+(Math.floor(realClock*15)+i*5)%16,1,2);
 }else{
  const p=here();ctx.drawImage(dollCanvas(f,'sit'),Math.round(p.x-DW/2),Math.round(p.y-DH+1));
  ctx.drawImage(image,0,9,o.w,o.h-9,off+o.x,o.y+9,o.w,o.h-9);
 }
 ctx.restore();return true;
}
function drawFriendActionForeground(ctx,f){
 const v=friendVisit;if(sim.mode!=='act')return;const o=friendHouseObject(v.objectId),off=(W-visitingHouse().w)/2;if(!o)return;
 if(v.action==='computer'){
  const desk=friendObjects(['desk'],o).find(d=>d.room===o.room),image=desk&&IMG.friendHouses[v.houseId].objects[desk.id];if(image)ctx.drawImage(image,off+desk.x,desk.y);
 }
 if(v.action==='eat'){
  const dish=v.mealItem?.dish?.look&&dishIcon(v.mealItem.dish),pic=dish&&dishPic(dish);
  if(pic?.complete)ctx.drawImage(pic,off+o.x+o.w/2-pic.width/2,o.y-pic.height+2);
  else{ctx.fillStyle='#f4eddb';ctx.fillRect(off+o.x+o.w/2-3,o.y-1,7,2);ctx.fillStyle='#c9975c';ctx.fillRect(off+o.x+o.w/2-2,o.y-2,5,2);}
 }
 if(v.action==='water'||v.action==='wash'){
  ctx.fillStyle='#c6e6ed';for(let i=0;i<3;i++)ctx.fillRect(Math.round(off+o.x+o.w/2+i*2-2),o.y+5+(Math.floor(realClock*14)+i*4)%Math.max(6,o.h-10),1,2);
 }
 if(v.action==='music')ctx.drawImage(emoteCanvas('note'),Math.round(here().x+6),Math.round(here().y-DH-4));
 if(v.action==='laundry'){
  ctx.fillStyle=Math.floor(realClock*5)%2?'#b6cdd2':'#60818e';ctx.fillRect(off+o.x+8,o.y+12,5,3);
 }
}
