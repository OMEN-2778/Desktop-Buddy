// 季节地图的夜晚（owner 2026-11-06：“旅社晚上竟然不按房间开灯？茵菲谷再检查检查”）。茵菲谷 had no night at all and the
// 草帽湾 lodge darkened as one block. Same rules as the main world's house:
//  - outdoors (茵菲谷): the main world's evening (duskState: the day's warm or rose sky) and night (outdoorNightness);
//  - indoors (农舍 / 旅社): at night only the room she is in has its light on (it fades up, rooms she left fade down),
//    the other rooms take the main house's night colours; when she goes to bed the light goes out.
// adapter.js calls draw() on the scaled view after the scene; 草帽湾 outdoors keeps summer_more's own night and 晚霞.
const seasonNight=(function(){
 const NIGHT=[.40,.42,.62];   // the main house's dark-room multiply (grade())
 // rooms in scene coordinates [x0,y0,x1,y1]
 const ROOMS={
  spring:{stairs:[30,5,77,111],mine:[77,5,167,53],bath:[171,5,211,53],parents:[215,5,309,53],living:[77,63,309,111]},
  summer:{bed:[46,33,118,81],living:[122,33,204,81],kitchen:[208,33,274,81],bath:[278,33,312,81]}};
 const glow={};let last=0;
 const roomOf=(rooms,x,y)=>{for(const [k,[x0,y0,x1,y1]] of Object.entries(rooms))if(x>=x0&&x<x1&&y>=y0-30&&y<=y1+2)return k;return null;};
 const mul=(f,k=1)=>{const a=f*k;return `rgb(${Math.round(255*(1-a*(1-NIGHT[0])))},${Math.round(255*(1-a*(1-NIGHT[1])))},${Math.round(255*(1-a*(1-NIGHT[2])))})`;};
 function draw(v,W,H,c,which){
  const s=c.state,h=hour(),now=performance.now(),dt=Math.min(.2,(now-last)/1000);last=now;
  if(!s.inside){
   if(which!=='spring')return;
   const d=typeof duskState==='function'?duskState():{strength:0},f=outdoorNightness(h);
   v.save();
   if(d.strength){v.globalCompositeOperation='soft-light';v.fillStyle=d.mode==='rose'?`rgba(214,120,200,${(d.strength*.55).toFixed(3)})`:`rgba(255,150,80,${(d.strength*.55).toFixed(3)})`;v.fillRect(0,0,W,H);}
   if(f>0){v.globalCompositeOperation='multiply';v.fillStyle=mul(f);v.fillRect(0,0,W,H);}
   v.restore();return;}
  const f=nightness(h),rooms=ROOMS[which],kx=W/342,ky=H/c.canvas.height;
  const asleep=which==='spring'?window.infeiHome?.svc?.id==='bed':window.summerLodge?.svc?.id==='bed';
  const here=asleep?null:roomOf(rooms,s.x,s.y??(which==='summer'?84:108));
  for(const k of Object.keys(rooms)){const want=k===here?1:0;glow[which+k]=(glow[which+k]??want)+(want-(glow[which+k]??want))*Math.min(1,dt*7);}
  if(f<=0)return;
  v.save();v.globalCompositeOperation='multiply';
  // everything outside the rooms (walls, roof, the page around) at full night; each room by its light
  v.fillStyle=mul(f);v.beginPath();v.rect(0,0,W,H);for(const [x0,y0,x1,y1] of Object.values(rooms))v.rect(x1*kx,y0*ky,-(x1-x0)*kx,(y1-y0)*ky);v.fill('evenodd');
  for(const [k,[x0,y0,x1,y1]] of Object.entries(rooms)){const g=glow[which+k]||0;v.fillStyle=mul(f,1-g);v.fillRect(x0*kx,y0*ky,(x1-x0)*kx,(y1-y0)*ky);}
  v.restore();}
 return {draw,ROOMS};
})();
window.seasonNight=seasonNight;
