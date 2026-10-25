// A reversible art-preview workspace; no visit, relationship or save progress.
const friendHouseControls=document.getElementById('friendHousePreviewControls');
const friendHouseSelect=document.getElementById('friendHouseSelect');
const friendHouseNote=document.getElementById('friendHouseNote');
const friendHouseAnchor=document.createComment('friend house preview controls');friendHouseControls.before(friendHouseAnchor);
const friendHouseKeys=Object.keys(D.friendHouses);
let friendHouseAnimations=[];
for(const [i,id]of friendHouseKeys.entries()){
 const h=D.friendHouses[id],o=document.createElement('option');o.value=id;o.textContent=`${String(i+1).padStart(2,'0')} · ${h.name} · ${Math.round((h.h-4)/58)}层`;friendHouseSelect.append(o);
}
function housePreviewRects(){return [moodrow,document.querySelector('.status-row')].map(el=>[el,el.getBoundingClientRect().top]);}
function animateHousePreviewLayout(old,oldBottom,oldHeight){
 const timing={duration:620,easing:'cubic-bezier(.22,.8,.24,1)',fill:'none'};
 if(!reduceMotionUI){
  for(const [el,top]of old){const delta=top-el.getBoundingClientRect().top;if(Math.abs(delta)>1)friendHouseAnimations.push(el.animate([{transform:`translateY(${delta}px)`},{transform:'translateY(0px)'}],timing));}
  const r=view.getBoundingClientRect(),dy=oldBottom-r.bottom,cut=Math.max(0,r.height-oldHeight);
  friendHouseAnimations.push(view.animate([{transform:`translateY(${dy}px)`,clipPath:`inset(${cut}px 0px 0px 0px)`},{transform:'translateY(0px)',clipPath:'inset(0px 0px 0px 0px)'}],timing));
 }
}
function openFriendHousePreview(id){
 if(!Object.hasOwn(D.friendHouses,id))return false;
 if(friendVisit){showHint('先结束拜访，再查看房屋预览吧。');return false;}
 if(wiping||phoneHolds()||card){showHint('先处理完眼前的事情，再看看房屋吧。');return false;}
 const old=housePreviewRects(),r=view.getBoundingClientRect();
 friendHouseAnimations.forEach(a=>a.cancel());friendHouseAnimations=[];
 closeGuide();closePicker();closeRing();closeWardrobe();closeSocialSheet();setContactsOpen(false);setNeedsOpen(false);showMoodTip(false);setDiaryOpen(false);setSettingsOpen(false);
 const wasConsole=friendHousePreview?.wasConsole??document.querySelector('.console').open;
 const previous=friendHousePreview;
 friendHousePreview={id,night:previous?.night??hour()>=18,figures:previous?.figures??true,wasConsole};
 document.querySelector('.console').open=false;document.querySelector('.house-col').append(friendHouseControls);friendHouseControls.classList.add('friend-house-active');
 document.getElementById('widget').classList.add('house-preview');view.style.pointerEvents='none';
 friendHouseSelect.value=id;syncFriendHousePreview();fit();makeRoom();render();
 animateHousePreviewLayout(old,r.bottom,r.height);fitWindow();return true;
}
function syncFriendHousePreview(){
 const p=friendHousePreview;if(!p)return;const h=D.friendHouses[p.id];
 document.getElementById('friendHouseNight').checked=p.night;document.getElementById('friendHouseFigures').checked=p.figures;
 friendHouseNote.textContent=`${h.name} · ${h.w}×${h.h}像素｜${h.description} ${p.night?'夜景，室内开灯。':''}仅预览样式，时间暂停，不写入存档。`;
}
function closeFriendHousePreview(){
 if(!friendHousePreview)return;
 const old=housePreviewRects(),r=view.getBoundingClientRect(),wasConsole=friendHousePreview.wasConsole;
 friendHouseAnimations.forEach(a=>a.cancel());friendHouseAnimations=[];
 friendHousePreview=null;friendHouseAnchor.after(friendHouseControls);friendHouseControls.classList.remove('friend-house-active');
 document.getElementById('widget').classList.remove('house-preview');view.style.pointerEvents='';friendHouseSelect.value='';friendHouseNote.textContent='预览不会启动做客、改变进度或写入存档。';
 document.querySelector('.console').open=wasConsole;fit();makeRoom();render();animateHousePreviewLayout(old,r.bottom,r.height);fitWindow();
}
function renderFriendHousePreview(){
 const p=friendHousePreview;if(!p)return false;
 const h=D.friendHouses[p.id],imgs=IMG.friendHouses[p.id],x=(W-h.w)/2;
 vctx.save();vctx.setTransform(1,0,0,1,0,0);vctx.clearRect(0,0,view.width,view.height);vctx.scale(devPx,devPx);vctx.imageSmoothingEnabled=false;
 vctx.drawImage(p.night?imgs.night:imgs.day,x,0);
 if(p.figures){
  const c=contactFor('friend','abu')||contactFor('mom'),[hx,hy]=h.host;
  const n=p.npc||={look:c.look,ramps:doll.rampsOf(c.look),cache:new Map(),kid:false};
  const f={expr:Math.floor(realClock/3)%5===0?'blink':'neutral',look:0,bob:0,sway:0,wave:null};
  vctx.drawImage(npcCanvas(n,f,h.hostSeated?'sit':'stand'),Math.round(x+hx-DW/2),hy-DH+1);
  vctx.drawImage(dollCanvas(f,'stand'),Math.round(x+h.entry[0]-DW/2),h.entry[1]-DH+1);
 }
 vctx.drawImage(imgs.front,x,0);vctx.restore();return true;
}
friendHouseSelect.onchange=()=>{if(friendHouseSelect.value)openFriendHousePreview(friendHouseSelect.value);};
for(const [id,dir]of [['friendHousePrev',-1],['friendHouseNext',1]])document.getElementById(id).onclick=()=>{
 const i=friendHousePreview?friendHouseKeys.indexOf(friendHousePreview.id):(dir>0?-1:0);openFriendHousePreview(friendHouseKeys[(i+dir+friendHouseKeys.length)%friendHouseKeys.length]);
};
document.getElementById('friendHouseExit').onclick=closeFriendHousePreview;
for(const [id,key]of [['friendHouseNight','night'],['friendHouseFigures','figures']])document.getElementById(id).onchange=e=>{if(friendHousePreview){friendHousePreview[key]=e.target.checked;syncFriendHousePreview();render();}};
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&friendHousePreview){e.preventDefault();closeFriendHousePreview();}});
