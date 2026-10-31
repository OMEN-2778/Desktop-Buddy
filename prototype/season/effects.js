// Shared, scene-local pixel effects. One main game RAF; no DOM work in draw paths.
function makeSeasonEffects(skinBase=null){
 const trails=new Map(),bubbles=[],ripples=[];
 // Keep the original 20×28 doll intact. Only the bottom four leg rows shorten.
 const actorCanvas=document.createElement('canvas');actorCanvas.width=20;actorCanvas.height=28;const ac=actorCanvas.getContext('2d');
 const legs=document.createElement('canvas');legs.width=20;legs.height=4;const lc=legs.getContext('2d');
 ac.imageSmoothingEnabled=lc.imageSmoothingEnabled=false;
 const bodyCache=new WeakMap();
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 function outfitFrames(sheet,skinRamp){
  let variants=bodyCache.get(sheet);if(!variants){variants=new Map();bodyCache.set(sheet,variants);}
  const key=skinRamp?.join(',')||'';if(variants.has(key))return variants.get(key);
  const rgb=hex=>hex.slice(1).match(/../g).map(v=>parseInt(v,16)),map=new Map();
  if(skinBase&&skinRamp)skinBase.forEach((hex,i)=>map.set(rgb(hex).join(','),rgb(skinRamp[i])));
  const frames=[0,1].map(i=>{const c=document.createElement('canvas');c.width=20;c.height=28;const g=c.getContext('2d');g.drawImage(sheet,(4+i)*28+4,0,20,28,0,0,20,28);
   if(map.size){const pixels=g.getImageData(0,15,20,13);for(let j=0;j<pixels.data.length;j+=4){const d=pixels.data,replacement=map.get([d[j],d[j+1],d[j+2]].join(','));if(d[j+3]&&replacement){d[j]=replacement[0];d[j+1]=replacement[1];d[j+2]=replacement[2];}}g.putImageData(pixels,0,15);}return c;});
  variants.set(key,frames);return frames;
 }
 function swimmer(ctx,{head,sheet,x,y,time,facing=1,diving=false,moving=true,waterline=116,phase=0,skinRamp=null}){
  const beat=Math.floor(time/.28+phase)%4;
  ac.clearRect(0,0,20,28);ac.drawImage(outfitFrames(sheet,skinRamp)[beat%2],0,0);
  ac.drawImage(head,0,0,20,15,0,0,20,15);
  lc.clearRect(0,0,20,4);lc.drawImage(actorCanvas,0,24,20,4,0,0,20,4);ac.clearRect(0,24,20,4);
  for(let side=0;side<2;side++){const tuck=beat===(side===0?0:2)?1:0;ac.drawImage(legs,side*10,0,10,4,side*10,24,10,4-tuck);}
  const depth=Math.max(0,y-waterline-14),tint=diving?clamp(.15+depth/850,.15,.55):.07;
  ac.globalCompositeOperation='source-atop';ac.fillStyle=`rgba(95,180,213,${tint})`;ac.fillRect(0,0,20,28);ac.globalCompositeOperation='source-over';
  ctx.save();ctx.translate(x,y);if(diving){ctx.translate(0,-14);ctx.scale(facing,1);ctx.rotate(Math.PI/2);ctx.drawImage(actorCanvas,-10,-14);}else{ctx.scale(facing,1);ctx.drawImage(actorCanvas,-10,-28);}ctx.restore();
 }
 function waterActor(id,x,y,face,moving,diving,dt,wl){
  let a=trails.get(id);if(!a){a={x,y,emission:0,ripple:0,next:.3+Math.random()*.5,site:0};trails.set(id,a);}
  const oldX=a.x,oldY=a.y;a.x=x;a.y=y;
  if(dt<=0)return;a.emission+=dt;a.ripple+=dt;
  // Sparse, staggered releases from breath, hands and kicking feet; never a hose.
  if(a.emission>=a.next){a.emission=0;a.next=(moving?.35:.95)+Math.random()*(moving?.55:1.4);
   const site=a.site++%3,f=Math.random(),px=oldX+(x-oldX)*f,py=oldY+(y-oldY)*f;
   const bx=px+face*(diving?([11,-2,-14][site]):([-5,5,0][site]))+(Math.random()-.5)*4;
   const by=diving?py-14+([-3,5,0][site])+(Math.random()-.5)*4:wl+4+Math.random()*7;
   if(bubbles.length>=90)bubbles.shift();bubbles.push({x:bx,y:Math.max(wl+3,by),wl,life:1.1+Math.random()*1.5,age:0,r:.6+Math.random()*.9,dx:(Math.random()-.5)*3,vy:5+Math.random()*4,phase:Math.random()*6});
  }
  if(!diving&&a.ripple>(moving?.45:1.3)){a.ripple=0;ripples.push({x:x+(Math.random()-.5)*8,y:wl,age:0,life:1.4,force:moving?1:.5});}
 }
 function tickWater(dt){for(const p of bubbles){p.age+=dt;p.x+=(p.dx+Math.sin(p.age*3+p.phase))*dt;p.y-=dt*p.vy;}for(const p of ripples)p.age+=dt;for(const list of [bubbles,ripples])for(let i=list.length-1;i>=0;i--)if(list[i].age>=list[i].life||(list[i].wl!==undefined&&list[i].y<=list[i].wl+3))list.splice(i,1);}
 // All scenery FX paint onto logical 1x pixel canvases, then upscale nearest-neighbour.
 // No Canvas paths, smooth strokes, ellipses, gradients or subpixel FX geometry.
 const rasterLayers=new Map();
 function raster(ctx,key,x,y,w,h,paint){
  x=Math.floor(x);y=Math.floor(y);w=Math.max(1,Math.ceil(w));h=Math.max(1,Math.ceil(h));
  let c=rasterLayers.get(key);if(!c){c=document.createElement('canvas');rasterLayers.set(key,c);}if(c.width!==w||c.height!==h){c.width=w;c.height=h;}
  const g=c.getContext('2d');g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,w,h);g.imageSmoothingEnabled=false;g.save();g.translate(-x,-y);paint(g);g.restore();ctx.save();ctx.imageSmoothingEnabled=false;ctx.drawImage(c,x,y);ctx.restore();
 }
 function pxLine(g,x0,y0,x1,y1,width=1){x0=Math.round(x0);y0=Math.round(y0);x1=Math.round(x1);y1=Math.round(y1);const dx=Math.abs(x1-x0),sx=x0<x1?1:-1,dy=-Math.abs(y1-y0),sy=y0<y1?1:-1;let error=dx+dy;for(;;){g.fillRect(x0,y0,width,width);if(x0===x1&&y0===y1)break;const e=error*2;if(e>=dy){error+=dy;x0+=sx;}if(e<=dx){error+=dx;y0+=sy;}}}
 function pixelRing(g,cx,cy,rx,ry){cx=Math.round(cx);cy=Math.round(cy);rx=Math.max(1,Math.round(rx));ry=Math.max(1,Math.round(ry));for(let x=-rx;x<=rx;x++){const y=Math.round(ry*Math.sqrt(Math.max(0,1-x*x/(rx*rx))));g.fillRect(cx+x,cy-y,1,1);g.fillRect(cx+x,cy+y,1,1);}}
 function drawWater(ctx,wl,bounds={x:0,y:0,w:342,h:236}){raster(ctx,'water',bounds.x-1,bounds.y-1,bounds.w+2,bounds.h+2,g=>{
  for(const p of bubbles){const x=Math.round(p.x),y=Math.round(p.y);if(y-1<=wl||x<bounds.x-5||x>bounds.x+bounds.w+5||y<bounds.y-5||y>bounds.y+bounds.h+5)continue;g.globalAlpha=p.age/p.life<.4?.75:p.age/p.life<.75?.5:.25;g.fillStyle='#9bd3df';
   if(p.r<1.1){g.fillRect(x,y-1,1,1);g.fillRect(x-1,y,1,1);g.fillRect(x+1,y,1,1);g.fillRect(x,y+1,1,1);}else{g.fillRect(x,y-1,2,1);g.fillRect(x-1,y,1,2);g.fillRect(x+2,y,1,2);g.fillRect(x,y+2,2,1);}g.fillStyle='#f4f2ee';g.fillRect(x,y-1,1,1);
  }
  for(const p of ripples){const age=p.age/p.life;g.globalAlpha=age<.5?.5:.25;g.fillStyle='#9bd3df';pixelRing(g,p.x,p.y,4+Math.floor(age*18),1+Math.floor(age*2));}g.globalAlpha=1;
 });}
 function waves(ctx,t,cx,w,wl,shore,seaEnd){raster(ctx,'waves',cx-2,wl-12,w+4,23,g=>{
  const start=Math.ceil(Math.max(shore-12,cx-2)),end=Math.floor(Math.min(seaEnd,cx+w+2));
  for(let x=start;x<=end;x++){const crest=Math.round(wl+Math.sin(x*.065-t*1.65)*2+Math.sin(x*.027-t*.8));g.fillStyle='#9bd3df';g.fillRect(x,crest,1,Math.max(1,wl+4-crest));g.fillStyle='#f4f2ee';if((x+Math.floor(t*5))%27<20)g.fillRect(x,crest,1,1);}
  for(let row=1;row<4;row++){g.fillStyle=row%2?'#9bd3df':'#e5edf4';for(let x=start;x<=end;x++){if((x+Math.floor(t*7)+row*13)%37>12)continue;const y=Math.round(wl-row*2+Math.sin(x*.065-t*1.65+row)*2+Math.sin(x*.027-t*.8));g.fillRect(x,y,1,1);}}
  for(let i=0;i<3;i++){const phase=(t*.19+i/3)%1,edge=Math.round(shore-12+phase*28),width=Math.round(7+phase*11);g.globalAlpha=phase<.2||phase>.8?.25:.5;g.fillStyle='#f4f2ee';for(let j=0;j<width;j++)if((j+i)%5!==0)g.fillRect(edge+j,wl-2+(j%7===0?1:0),1,1);}g.globalAlpha=1;
 });}
 function sunlight(ctx,t,cx,cy,w,h,wl,ground,cloudy){if(cloudy||cy>wl+220||cx+w<1020)return;raster(ctx,'sunlight',cx-1,cy-1,w+2,h+2,g=>{
  const noise=n=>{const v=Math.sin(n*127.1+311.7)*43758.5453;return v-Math.floor(v);};
  // Broken surface openings: unequal spacing/width, broad at entry and fading narrower.
  for(let i=Math.floor((cx-80)/47);i<(cx+w+80)/47;i++){
   if(noise(i+9)<.3)continue;
   const top=i*47+noise(i)*35+Math.sin(t*.23+i)*4,reach=55+noise(i+2)*115,span=9+noise(i+3)*18,lean=-16+noise(i+4)*28;
   g.fillStyle='#f4f2ee';
   for(let dy=Math.max(0,Math.floor(cy-wl));dy<reach&&wl+dy<cy+h+2;dy++){
    const u=dy/reach,width=Math.max(1,Math.round(span*(1-u*.85))),left=Math.round(top+u*lean-width/2+Math.sin(dy*.07+t*.4+i)*1.5);
    g.globalAlpha=u<.25?.12:u<.6?.08:.04;
    for(let x=left;x<left+width;x++){if(x<Math.max(1020,cx-1)||x>cx+w+1||wl+dy>=ground[clamp(x,0,ground.length-1)])continue;
     if((x+dy*3+i)%5===0||u>.7&&(x*3+dy)%3===0)continue;g.fillRect(x,wl+dy,1,1);}
   }
  }
  g.fillStyle='#f4f2ee';g.globalAlpha=.18;
  for(let i=Math.floor(cx/23)-1;i<(cx+w)/23+1;i++){if(noise(i+42)<.35)continue;const x=Math.round(i*23+noise(i+18)*18+Math.sin(t*.6+i)*3),floor=ground[clamp(x,0,ground.length-1)];if(floor>wl+145||floor<wl||floor<cy||floor>cy+h+5)continue;
   const length=3+Math.floor(noise(i+31)*8);for(let j=0;j<length;j++){const xx=x+j,yy=Math.round(ground[clamp(xx,0,ground.length-1)]-2-Math.abs(Math.sin(j*.5+t*.8+i))*3);if((j+i)%4!==0)g.fillRect(xx,yy,1,1);}}
  g.globalAlpha=1;
 });}
 function plant(ctx,im,p,t){const amp=p.kind==='palm'?2.7:p.kind.startsWith('shrub')?.32:1.1,phase=p.x*.071+p.y*.13;for(let y=0;y<im.height;y+=3){const h=Math.min(3,im.height-y),root=1-y/im.height,dx=(Math.sin(t*(p.kind==='palm'?.9:1.3)+phase)+.27*Math.sin(t*2.3+phase*2))*amp*root**1.8;ctx.drawImage(im,0,y,im.width,h,p.x+dx,p.y+y,im.width,h);}}
 function kelp(ctx,t,items,cx,cy,w,h){raster(ctx,'kelp',cx-1,cy-1,w+2,h+2,g=>{
  for(const p of items){if(p.x<cx-30||p.x>cx+w+30||p.y<cy||p.y-p.h>cy+h)continue;for(let k=0;k<4;k++){const first=Math.max(0,Math.floor(p.y-cy-h-2)),last=Math.min(p.h,Math.ceil(p.y-cy+2));
   for(let j=first;j<=last;j++){const u=j/p.h,x=Math.round(p.x+(k-1.5)*3+Math.sin(t*.9+p.x*.13-u*3+k*.8)*(u*u*8)),y=Math.round(p.y-j);g.fillStyle='#22575b';g.fillRect(x-1,y,3,1);g.fillStyle=k%2?'#4f9f97':'#337a78';g.fillRect(x,y,1,1);
    if(j>8&&j%13===k*2){g.fillStyle='#337a78';pxLine(g,x,y,x+(j%26<13?-3:3),y-3);g.fillStyle='#7fc4b6';g.fillRect(x,y-1,1,1);}
   }
  }}
 });}
 function weather(ctx,kind,t,w,h,{waterline=Infinity,inside=false,roof=null}={}){
  if(inside||kind==='clear'||waterline<0)return;const snow=kind==='snow'||kind==='blizzard',heavy=kind==='storm'||kind==='blizzard',limit=Math.min(h,Math.floor(waterline+3)),n=snow?(heavy?220:45):(heavy?180:45);
  raster(ctx,'weather',0,0,w,h,g=>{if(!snow){g.globalAlpha=heavy?.20:.10;g.fillStyle='#163651';g.fillRect(0,0,w,limit);}else if(heavy){g.globalAlpha=.1;g.fillStyle='#e5edf4';g.fillRect(0,0,w,limit);}g.globalAlpha=1;
   for(let i=0;i<n;i++){let x=Math.round((i*71.31+t*(snow?5:heavy?32:15))%(w+25)-12),y=Math.round((i*43.73+t*(snow?heavy?26:13:heavy?155:95))%(limit+20)-10);if(roof&&x>=roof.x&&x<roof.x+roof.w&&y>=roof.y&&y<roof.y+roof.h)continue;if(y>=limit)continue;
    if(snow){x+=Math.round(Math.sin(t+i)*2);g.fillStyle=i%3?'#f4f2ee':'#c4d6e8';g.fillRect(x,y,1,1);if(heavy&&i%4===0){g.fillRect(x-1,y,3,1);g.fillRect(x,y-1,1,3);}}
    else{g.globalAlpha=heavy?.75:.5;g.fillStyle='#9bd3df';pxLine(g,x,y,x-2,Math.min(limit-1,y+(heavy?8:5)));if(y>limit-7){g.globalAlpha=.25;pixelRing(g,x,limit-1,2+i%3,1);}}
   }g.globalAlpha=1;
  });
 }
 function transition(ctx,door,w,h){if(!door)return;const p=door.elapsed/door.duration,alpha=Math.sin(Math.min(1,p)*Math.PI);ctx.save();ctx.fillStyle=`rgba(40,35,49,${alpha})`;ctx.fillRect(0,0,w,h);ctx.restore();}
 return {swimmer,waterActor,tickWater,drawWater,waves,sunlight,plant,kelp,weather,transition,bubbles,ripples,trails,rasterLayers};
}
