// 草帽湾 hover glow (owner 2026-11-05: "does the moving gold outline show on things, like at home?"). Game-shell test page.
// Every frame the bay records the people it drew (summerLife.drawnPeople) and where each fish is (viewer: c.im/px/py);
// the one under the pointer gets the house's own marching pixel outline (drawObjectHover), drawn after the night pass.
// The lodge door, cabana, beach chairs and the sparkling spots get their box, like the 茵菲谷 farmhouse.
const summerHover=(function(){
 const L=summerLife,C=()=>seasonMapTest.state.summer,inBay=()=>sim.place==='summer_test';
 let ptr=null;const flips=new Map(),boxes=new Map();
 const flipped=im=>{if(!flips.has(im)){const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const g=c.getContext('2d');g.translate(im.width,0);g.scale(-1,1);g.drawImage(im,0,0);flips.set(im,c);}return flips.get(im);};
 const box=(w,h)=>{const k=w+'x'+h;if(!boxes.has(k)){const c=document.createElement('canvas');c.width=w;c.height=h;c.getContext('2d').fillRect(0,0,w,h);boxes.set(k,c);}return boxes.get(k);};
 // an opaque pixel of the picture near (x,y)? (1px slack so thin limbs are easy to hit)
 const alpha=new Map();function solid(pic,x,y){let a=alpha.get(pic);if(!a){try{a=pic.getContext?pic.getContext('2d').getImageData(0,0,pic.width,pic.height).data:null;}catch(e){a=null;}if(!a){const c=document.createElement('canvas');c.width=pic.width;c.height=pic.height;const g=c.getContext('2d');g.drawImage(pic,0,0);a=g.getImageData(0,0,pic.width,pic.height).data;}alpha.set(pic,a);}
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const xx=Math.floor(x)+dx,yy=Math.floor(y)+dy;if(xx>=0&&yy>=0&&xx<pic.width&&yy<pic.height&&a[(yy*pic.width+xx)*4+3]>0)return true;}return false;}
 function target(x,y){const c=C(),s=c.state;if(s.inside||s.door||L.isBusy()||storyLocked()||cardHolds()||wiping)return null;
  if(Math.abs(x-s.x)<10&&y<s.y&&y>s.y-28)return null;   // Buddy herself: her ring
  const people=L.drawnPeople;for(let i=people.length-1;i>=0;i--){const p=people[i];if(solid(p.pic,x-p.x,y-p.y))return {img:p.pic,x:p.x,y:p.y};}
  if(s.market)return null;
  for(const f of c.seaLife)if(f.im&&f.lane&&f.cx&&x>=f.px-3&&x<f.px+f.im.width+3&&y>=f.py-3&&y<f.py+f.im.height+3)return {img:f.flip?flipped(f.im):f.im,x:f.px,y:f.py};
  const D=c.data||{},g=c.gr(x);
  if(D.lodgeDoor!==undefined&&Math.abs(x-D.lodgeDoor)<16&&y>g-42&&y<g+5)return {img:box(28,42),x:D.lodgeDoor-14,y:c.gr(D.lodgeDoor)-40};
  for(const [lx,ly]of D.chairs||[])if(Math.abs(x-lx)<14&&y>ly-32&&y<ly+3)return {img:box(26,18),x:lx-13,y:ly-16};
  for(const h of D.hotspots||[])if(!s.found.has(h.id)&&Math.abs(x-h.x)<14&&Math.abs(y-h.y)<14)return {img:box(20,20),x:h.x-10,y:h.y-10};
  return null;}
 view.parentElement.addEventListener('pointermove',e=>{if(e.target!==view||!inBay()||e.pointerType!=='mouse'){ptr=null;return;}const c=C(),r=view.getBoundingClientRect();
  ptr={x:(e.clientX-r.left)*c.canvas.width/r.width,y:(e.clientY-r.top)*c.canvas.height/r.height};},true);
 view.addEventListener('pointerleave',()=>{ptr=null;});
 function draw(vctx,sx,sy){const list=L.drawnPeople;try{if(!ptr||!inBay())return;const s=C().state,cx=s.camX||0,cy=s.camY||0,t=target(ptr.x+cx,ptr.y+cy);view.style.cursor=t?'pointer':'';if(!t)return;
  vctx.save();vctx.scale(sx,sy);drawObjectHover(vctx,t.img,t.x-cx,t.y-cy);vctx.restore();}finally{list.length=0;}}
 return {draw,target};
})();
window.summerHover=summerHover;
