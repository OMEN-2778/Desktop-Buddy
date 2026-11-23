// The seasonal farm shares its object hit masks with the home furniture.
const infeiHover=(function(){
 const X=springFarm.X,T=seasonMapTest,C=()=>T.state.spring,F=()=>X.F,inSpring=()=>sim.place==='spring_test';
 const boxes=new Map();
 function box(w,h){const k=w+'x'+h;if(!boxes.has(k)){const c=document.createElement('canvas');c.width=Math.max(1,Math.round(w));c.height=Math.max(1,Math.round(h));const g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,c.width,c.height);boxes.set(k,c);}return boxes.get(k);}
 const rect=(x,y,w,h)=>({x,y,img:box(w,h)});
 let pointer=null;
 // what is under the pointer, in scene coordinates (mirrors the click handlers)
 function hit(x,y){const s=C().state,f=F();
  if(springFarm.speech.open||window.infeiQuests?.busy||storyLocked()||cardHolds()||wiping||sim.mode==='down'||s.door)return null;
  if(Math.abs(x-s.x)<10&&y<s.y&&y>s.y-28)return null;   // Buddy: her own ring
  if(f.phase==='meet'&&!s.inside&&s.scene===springFarm.mom.scene&&springFarm.momAt(x,y))return {mom:true};   // 妈妈 waiting with her "!"
  if(s.inside)return window.infeiHome?.hit(x,y);
  const sc=s.scene;
  const Q=window.infeiQuests,v=Q?.villagerAt(x,y,sc);
  if(v&&!Q.busy)return v;
  if(sc===4&&['sow','water','done'].includes(f.phase)){
   const i=X.bedAt(x,y);if(i!=null){const [bx,top,w,h]=X.D.plots[i];return rect(bx-1,top-1,w+2,h+2);}}
  if(f.phase!=='done')return sc===3?infeiFarm.yardHit(x,y,sc):null;
  if(Q){const g=Q.spotAt(sc,x,y);if(g)return rect(...Q.spots[g.spot].rect);}
  if(sc===3)return infeiFarm.yardHit(x,y,sc);
  if(sc===5){
   const exact=infeiFarm.yardHit(x,y,sc);
   if(exact)return exact;
   for(const [i,[px,py]]of X.D.pits.entries())if(!f.trees?.[i]&&Math.abs(x-px)<=9&&y>=py-5&&y<=py+2)return rect(px-9,py-5,19,8);
  }
  return null;
 }
 function hitPointer(){
  if(!pointer||!inSpring())return null;
  const project=T.viewport(C()),p=project.point(pointer);
  return project.onCanvas(p)?hit(p.worldX,p.worldY):null;
 }
 view.parentElement.addEventListener('pointermove',e=>{
  pointer=e.target===view&&inSpring()&&e.pointerType==='mouse'?{clientX:e.clientX,clientY:e.clientY}:null;
 },true);
 view.addEventListener('pointerleave',()=>{pointer=null;});
 X.hooks.draw.push(ctx=>{
  const hv=hitPointer();
  if(!hv||hv.animal)return;  // animals get their outline underneath the pasture fence
  if(hv.mom){const m=springFarm.mom;drawObjectHover(ctx,npcCanvas(springFarm.momNpc(),{expr:'happy',look:m.facing,bob:0,sway:0,wave:null},'stand'),Math.round(m.x)-10,Math.round(m.y)-27);return;}
  if(hv.img)drawObjectHover(ctx,hv.img,hv.x,hv.y);
 });
 return {get hv(){return hitPointer();},hit,hitPointer};
})();
window.infeiHoverApi=infeiHover;
