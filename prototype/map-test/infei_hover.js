// Hover glow in 茵菲谷 (owner 2026-11-03: "does hovering over things show the outline like the rest of the game?").
// Game-shell test page only. Everything she can click gets the house's own pixel glow (drawObjectHover): villagers,
// fruit trees and animals by their sprite; beds, tree pits, the barn, the coop, the farmhouse door, quest spots and the
// furniture inside the farmhouse by their outline box (they are part of the painted scene, not separate sprites).
const infeiHover=(function(){
 const X=springFarm.X,T=seasonMapTest,C=()=>T.state.spring,F=()=>X.F,inSpring=()=>sim.place==='spring_test';
 const boxes=new Map();
 function box(w,h){const k=w+'x'+h;if(!boxes.has(k)){const c=document.createElement('canvas');c.width=Math.max(1,Math.round(w));c.height=Math.max(1,Math.round(h));const g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,c.width,c.height);boxes.set(k,c);}return boxes.get(k);}
 const rect=(x,y,w,h)=>({x,y,img:box(w,h)});
 const FARMDOOR=[168,62,28,40],INDOOR=[30,66,20,42];
 let hv=null,region=null;
 // what is under the pointer, in scene coordinates (mirrors the click handlers)
 function hit(x,y){const s=C().state,f=F();
  if(springFarm.speech.open||window.infeiQuests?.busy||storyLocked()||cardHolds()||wiping||sim.mode==='down'||s.door)return null;
  if(Math.abs(x-s.x)<10&&y<s.y&&y>s.y-28)return null;   // Buddy: her own ring
  if(f.phase==='meet'&&!s.inside&&s.scene===springFarm.mom.scene&&springFarm.momAt(x,y))return {mom:true};   // 妈妈 waiting with her "!"
  if(s.inside){
   for(const p of Object.values(window.infeiHome?.SPOTS||{})){const [rx,ry,w,h]=p.rect;if(x>=rx&&x<rx+w&&y>=ry&&y<ry+h)return rect(rx,ry,w,h);}
   const [dx,dy,dw,dh]=INDOOR;if(x<50&&y>64)return rect(dx,dy,dw,dh);
   return null;}
  const sc=s.scene;
  if(sc===4&&['sow','water','done'].includes(f.phase)){
   for(const i of f.open.concat([11,12])){const [bx,top,w,h]=X.D.plots[i];if(x>=bx-2&&x<=bx+w+2&&y>=top-12&&y<=top+h+3)return rect(bx-1,top-1,w+2,h+2);}}
  if(f.phase!=='done')return null;
  const Q=window.infeiQuests;
  if(Q)for(const v of Object.values(Q.V)){const p=Q.at(v);if(p&&p.scene===sc&&Math.abs(x-p.x)<10&&y>103-30&&y<104)return {npc:v,x:p.x};}
  if(Q){const q=Q.Q(),m=Q.spots.mill,r=Q.spots.reeds;
   if(sc===2&&q.mill.step===1&&x>=m.rect[0]&&x<m.rect[0]+m.rect[2]&&y>=m.rect[1]&&y<m.rect[1]+m.rect[3])return rect(...m.rect);
   if(sc===0&&q.prints.step===1&&x>=r.rect[0]&&x<r.rect[0]+r.rect[2]&&y>=r.rect[1]&&y<r.rect[1]+r.rect[3])return rect(...r.rect);}
  const winter=X.seasonAt(X.today?.()??Math.floor(sim.t/1440))===3,A=infeiFarm.ANIMAL;
  const animal=sce=>!winter&&[...(f.animals||[])].reverse().find(a=>a.x!=null&&5===sce&&Math.abs(x-a.x)<A[a.kind].size[0]/2+2&&y<=a.y+2&&y>=a.y-A[a.kind].size[1]-10);
  if(sc===5){
   for(const [i,[px,py]]of X.D.pits.entries()){if(Math.abs(x-px)<12&&y>py-34&&y<py+4){const t=f.trees?.[i];
     if(t){const SK=['spring','summer','autumn','winter'],st=t.grown<3?0:t.grown<8?1:t.ready?3:2,a=X.D.trees[t.kind]?.[SK[X.seasonAt(Math.floor(sim.t/1440))]]?.[st];if(a)return {x:px+a.dx,y:py+a.dy,img:X.imgOf(a.src)};}
     return rect(px-9,py-5,18,7);}}
   const a=animal(5);if(a)return {animal:a.id};
   if(x>=452&&x<=632&&y>=30&&y<=88)return rect(452,30,181,59);}
  if(sc===3){
   const [dx,dy,dw,dh]=FARMDOOR;if(Math.abs(x-182)<14&&y>62&&y<102)return rect(dx,dy,dw,dh);}
  return null;}
 view.parentElement.addEventListener('pointermove',e=>{
  if(e.target!==view||!inSpring()){hv=null;window.infeiHover=null;return;}
  const c=C(),s=c.state,r=view.getBoundingClientRect(),x=(e.clientX-r.left)*342/r.width+(s.inside?0:(s.camera||0)),y=(e.clientY-r.top)*c.canvas.height/r.height;
  hv=hit(x,y);region=s.inside?-1:s.scene;window.infeiHover=hv&&hv.animal?{animal:hv.animal}:null;
 },true);
 view.addEventListener('pointerleave',()=>{hv=null;window.infeiHover=null;});
 X.hooks.draw.push((ctx,info)=>{
  if(!hv||(info.inside?-1:info.region)!==region)return;
  if(hv.npc){const v=hv.npc;drawObjectHover(ctx,npcCanvas(v,{expr:'neutral',look:v.dir,bob:0,sway:0,wave:null},'stand'),Math.round(hv.x)-10,103-27);return;}
  if(hv.mom){const m=springFarm.mom;drawObjectHover(ctx,npcCanvas(springFarm.momNpc(),{expr:'happy',look:m.facing,bob:0,sway:0,wave:null},'stand'),Math.round(m.x)-10,Math.round(m.y)-27);return;}
  if(hv.img)drawObjectHover(ctx,hv.img,hv.x,hv.y);
 });
 return {get hv(){return hv;},hit};
})();
window.infeiHoverApi=infeiHover;
