// Shared, scene-local pixel effects. One main game RAF; no DOM work in draw paths.
function makeSeasonEffects(){
 const trails=new Map(),bubbles=[],ripples=[];
 const actorCanvas=document.createElement('canvas');actorCanvas.width=64;actorCanvas.height=48;const ac=actorCanvas.getContext('2d');
 const samples=new WeakMap();
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 function colors(sheet){if(samples.has(sheet))return samples.get(sheet);const c=document.createElement('canvas');c.width=28;c.height=28;const g=c.getContext('2d');g.drawImage(sheet,0,0,28,28);const p=(x,y)=>{const d=g.getImageData(x,y,1,1).data;return d[3]?`rgb(${d[0]},${d[1]},${d[2]})`:'#e6b993';};const out={skin:p(10,12),cloth:p(14,18),dark:p(11,18),leg:p(11,24)};samples.set(sheet,out);return out;}
 function limb(points,color,width=3){ac.strokeStyle=color;ac.lineWidth=width;ac.lineCap='butt';ac.lineJoin='bevel';ac.beginPath();points.forEach(([x,y],i)=>i?ac.lineTo(Math.round(x),Math.round(y)):ac.moveTo(Math.round(x),Math.round(y)));ac.stroke();}
 function swimmer(ctx,{head,sheet,x,y,time,facing=1,diving=false,moving=true,wetsuit=false,waterline=116,phase=0,skin=null}){
  const p=colors(sheet),skinTone=skin||p.skin,t=time*(moving?8:3.2)+phase,beat=Math.sin(t),back=Math.sin(t+Math.PI);
  ac.clearRect(0,0,64,48);ac.save();ac.translate(32,31);
  // Connected shoulder/hip joints; the two knees alternate flexion and extension.
  const legs=[{f:(back+1)/2,c:p.dark},{f:(beat+1)/2,c:wetsuit?p.leg:skinTone}];
  for(const leg of legs){const k=leg.f,foot=[-24+k*8,-10+k*2];limb([[-6,-11],[-14+k*5,-11+k*7],foot],leg.c,3);if(wetsuit)limb([foot,[foot[0]-4,foot[1]+1]],'#354e67',3);else limb([foot,[foot[0]-2,foot[1]+1]],skinTone,2);}
  limb([[1,-17],[4+Math.cos(t)*5,-7],[12+Math.cos(t)*4,-9+beat*3]],wetsuit?p.cloth:skinTone,3);
  ac.save();ac.translate(1,-16);ac.rotate(Math.PI/2);ac.drawImage(sheet,10,15,8,8,0,0,8,8);ac.restore();
  limb([[1,-17],[-4+Math.cos(t+2)*4,-6],[-10+Math.cos(t)*6,-5+back*2]],wetsuit?p.dark:skinTone,3);
  // Actual player's/NPC's own head; keep it upright, never rotate the face sideways.
  ac.drawImage(head,0,0,20,15,0,-28,20,15);ac.restore();
  const depth=Math.max(0,y-waterline-14),tint=diving?clamp(.15+depth/850,.15,.55):.07;
  ac.globalCompositeOperation='source-atop';ac.fillStyle=`rgba(95,180,213,${tint})`;ac.fillRect(0,0,64,48);ac.globalCompositeOperation='source-over';
  ctx.save();ctx.translate(x,y+Math.sin(time*2.4+phase)*.45);ctx.scale(facing,1);ctx.rotate(diving?Math.sin(time*1.2+phase)*.035:.035);ctx.drawImage(actorCanvas,-42,-31);ctx.restore();
 }
 function waterActor(id,x,y,face,moving,diving,dt,wl){
  let a=trails.get(id);if(!a){a={x,y,emission:0,ripple:0};trails.set(id,a);}const distance=Math.hypot(x-a.x,y-a.y);a.x=x;a.y=y;
  if(dt<=0)return;a.emission+=dt*(moving?20:4);a.ripple+=dt;
  while(a.emission>=1){a.emission--;if(bubbles.length>=300)bubbles.shift();bubbles.push({x:x-face*(27+Math.random()*10),y:diving?y-10+(Math.random()-.5)*8:wl+3+Math.random()*8,life:1.3+Math.random(),age:0,r:.6+Math.random()*.9,dx:-face*(2+Math.random()*3)});}
  if(!diving&&a.ripple>(moving?.25:.9)){a.ripple=0;ripples.push({x,y:wl,age:0,life:1.6,force:moving?1:.5});}
 }
 function tickWater(dt){for(const p of bubbles){p.age+=dt;p.x+=p.dx*dt;p.y-=dt*9;}for(const p of ripples)p.age+=dt;for(const list of [bubbles,ripples])for(let i=list.length-1;i>=0;i--)if(list[i].age>=list[i].life)list.splice(i,1);}
 function drawWater(ctx,wl){ctx.save();ctx.strokeStyle='#d3f1f6';ctx.lineWidth=.65;for(const p of bubbles){ctx.globalAlpha=(1-p.age/p.life)*.65;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.stroke();}for(const p of ripples){const t=p.age/p.life;ctx.globalAlpha=(1-t)*.65*p.force;ctx.beginPath();ctx.ellipse(p.x,p.y,4+t*20,.7+t*2,0,0,Math.PI*2);ctx.stroke();}ctx.restore();}
 function waves(ctx,t,cx,w,wl,shore,seaEnd){
  ctx.save();ctx.lineWidth=.8;
  ctx.fillStyle='rgba(136,202,216,.78)';ctx.beginPath();const start=Math.max(shore-12,cx-3),end=Math.min(seaEnd,cx+w+3);ctx.moveTo(start,wl+3);for(let x=start;x<end;x+=2)ctx.lineTo(x,wl+Math.sin(x*.065-t*1.65)*1.9+Math.sin(x*.027-t*.8)*.9);ctx.lineTo(end,wl+3);ctx.closePath();ctx.fill();
  for(let row=0;row<4;row++){ctx.strokeStyle=row===0?'#e7f7f3':'#aedfdf';ctx.globalAlpha=row===0?.8:.35;ctx.beginPath();let begun=false;for(let x=Math.max(shore-14,cx-3);x<Math.min(seaEnd,cx+w+3);x+=2){const y=wl-row*1.65+Math.sin(x*.065-t*1.65+row)*1.9+Math.sin(x*.027-t*.8)*.9;if(!begun){ctx.moveTo(x,y);begun=true;}else ctx.lineTo(x,y);}ctx.stroke();}
  // A rolling, retreating foamy wash follows the sloping shoreline.
  for(let i=0;i<3;i++){const phase=(t*.19+i/3)%1,edge=shore-12+phase*28;ctx.globalAlpha=Math.sin(phase*Math.PI)*.65;ctx.fillStyle='#f0f8ef';ctx.fillRect(edge,wl-2+Math.sin(t+i)*.5,7+phase*11,1.4);}
  ctx.restore();
 }
 function sunlight(ctx,t,cx,cy,w,h,wl,ground,cloudy){
  if(cloudy||cy>wl+220||cx+w<1020)return;ctx.save();ctx.beginPath();ctx.moveTo(cx,wl);ctx.lineTo(cx+w,wl);for(let x=cx+w;x>=cx;x-=3)ctx.lineTo(x,Math.max(wl,Math.min(wl+240,ground[clamp(Math.round(x),0,ground.length-1)])));ctx.closePath();ctx.clip();
  for(let i=Math.floor(cx/64)-1;i<(cx+w)/64+1;i++){const x=i*64+Math.sin(t*.35+i)*7,reach=110+25*Math.sin(i);const grad=ctx.createLinearGradient(x,wl,x+30,wl+reach);grad.addColorStop(0,'rgba(234,250,212,.20)');grad.addColorStop(1,'rgba(234,250,212,0)');ctx.fillStyle=grad;ctx.beginPath();ctx.moveTo(x,wl);ctx.lineTo(x+7,wl);ctx.lineTo(x+55,wl+reach);ctx.lineTo(x+19,wl+reach);ctx.fill();}
  ctx.strokeStyle='#e6f6d7';ctx.lineWidth=.6;
  for(let x=Math.max(1020,Math.floor(cx/14)*14);x<cx+w+14;x+=14){const g=ground[Math.min(ground.length-1,Math.round(x))];if(g>wl+135)continue;ctx.globalAlpha=.12+.1*Math.sin(t*1.4+x*.1);const yy=g-2;ctx.beginPath();for(let j=0;j<5;j++){const px=x+j*4,py=yy+Math.sin(t*1.8+j+x)*2-j%2*2;j?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.stroke();}ctx.restore();
 }
 function plant(ctx,im,p,t){const amp=p.kind==='palm'?2.7:p.kind.startsWith('shrub')?.32:1.1,phase=p.x*.071+p.y*.13;for(let y=0;y<im.height;y+=3){const h=Math.min(3,im.height-y),root=1-y/im.height,dx=(Math.sin(t*(p.kind==='palm'?.9:1.3)+phase)+.27*Math.sin(t*2.3+phase*2))*amp*root**1.8;ctx.drawImage(im,0,y,im.width,h,p.x+dx,p.y+y,im.width,h);}}
 function kelp(ctx,t,items,cx,cy,w,h){ctx.save();for(const p of items){if(p.x<cx-30||p.x>cx+w+30||p.y<cy||p.y-p.h>cy+h)continue;for(let k=0;k<4;k++){ctx.strokeStyle=['#244e51','#326b65','#44847b','#659789'][k];ctx.lineWidth=2-(k%2)*.5;ctx.beginPath();for(let j=0;j<=20;j++){const u=j/20,x=p.x+(k-1.5)*3+Math.sin(t*.9+p.x*.13-u*3+k*.8)*(u*u*8),y=p.y-p.h*u;j?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();}}ctx.restore();}
 function weather(ctx,kind,t,w,h,{waterline=Infinity,inside=false,roof=null}={}){
  if(inside||kind==='clear'||waterline<0)return;const snow=kind==='snow'||kind==='blizzard',heavy=kind==='storm'||kind==='blizzard',limit=Math.min(h,waterline+3),n=snow?(heavy?220:45):(heavy?180:45);ctx.save();if(roof){ctx.beginPath();ctx.rect(0,0,w,h);ctx.rect(roof.x,roof.y,roof.w,roof.h);ctx.clip('evenodd');}ctx.fillStyle=snow?'#f3f7fd':'#c2dbea';ctx.strokeStyle='#b6d5e5';ctx.lineWidth=heavy?.75:.55;
  if(!snow){ctx.fillStyle=heavy?'rgba(50,66,86,.20)':'rgba(50,66,86,.11)';ctx.fillRect(0,0,w,limit);}
  if(snow&&heavy){ctx.fillStyle='rgba(224,237,246,.09)';ctx.fillRect(0,0,w,limit);}
  for(let i=0;i<n;i++){let x=(i*71.31+t*(snow?5:heavy?32:15))%(w+25)-12,y=(i*43.73+t*(snow?heavy?26:13:heavy?155:95))%(limit+20)-10;if(snow){x+=Math.sin(t+i)*2;const r=heavy&&i%4===0?2:heavy?1:.8;ctx.globalAlpha=.55+(i%3)*.2;ctx.fillStyle='#f3f7fd';ctx.fillRect(x,y,r,r);if(r>1){ctx.fillRect(x-.7,y+.5,2.5,.5);}}else{ctx.globalAlpha=heavy?.55:.5;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x-1.5,y+(heavy?8:5));ctx.stroke();if(y>limit-7){ctx.globalAlpha=.3;ctx.beginPath();ctx.ellipse(x,limit-1,2+(i%3),.6,0,0,Math.PI*2);ctx.stroke();}}}ctx.restore();
 }
 function transition(ctx,door,w,h){if(!door)return;const p=door.elapsed/door.duration,alpha=Math.sin(Math.min(1,p)*Math.PI);ctx.save();ctx.fillStyle=`rgba(40,35,49,${alpha})`;ctx.fillRect(0,0,w,h);ctx.restore();}
 return {swimmer,waterActor,tickWater,drawWater,waves,sunlight,plant,kelp,weather,transition,bubbles,ripples,trails};
}
