// The market, lodge and coast resolve the same visible target for a hover and a click.
const summerHover=(()=>{
 const C=()=>seasonMapTest.state.summer;
 let pointer=null;
 function target(x,y){
  const c=C(),s=c.state;
  if(s.door||s.inCabana||summerLife.isBusy()||storyLocked()||cardHolds()||wiping||sim.mode==='down')return null;
  if(Math.abs(x-s.x)<10&&y<s.y&&y>s.y-28)return null;
  if(s.inside)return window.summerLodge?.hit(x,y);
  if(s.market){const p=summerLife.marketHit(x,y);return p?.id?p:null;}
  return summerLife.beachHit(x,y)||c.targetAt(x,y);
 }
 view.parentElement.addEventListener('pointermove',e=>{
  pointer=e.target===view&&sim.place==='summer_test'&&e.pointerType==='mouse'?{clientX:e.clientX,clientY:e.clientY}:null;
 },true);
 view.addEventListener('pointerleave',()=>{pointer=null;});
 function draw(ctx,projection){
  if(!pointer||sim.place!=='summer_test')return;
  const p=projection.point(pointer);
  if(questMarkerAt(p.x,p.y+projection.top)?.activate){view.style.cursor='pointer';return;}
  const visible=projection.onCanvas(p)?target(p.worldX,p.worldY):null;
  view.style.cursor=visible?'pointer':'';
  if(!visible?.img)return;
  const anchor=projection.scene(visible.x,visible.y);
  ctx.save();
  ctx.scale(view.width/W,view.height/projection.height);
  if(C().state.market)drawHoverOutline(ctx,summerLife.marketOutline(visible),Math.round(anchor.x),Math.round(anchor.y));
  else drawObjectHover(ctx,visible.img,anchor.x,anchor.y);
  ctx.restore();
 }
 return {draw,target};
})();
window.summerHover=summerHover;
