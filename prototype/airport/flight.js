// Shared by art review and game-shell adapter. Timings are real visible milliseconds.
// Owner 2026-11-02: a finer transition with clouds rushing to the right. In and out, a wall of
// pixel clouds sweeps left -> right across the picture, its wake (puffs, wind lines) trailing behind; in the
// cabin, window clouds stream right in three layers (far, near, streaks), the cabin bumps 1px now and then.
function createCabinFlight({canvas,images,drawHero,onFrame=()=>{},paused=()=>false}){
 const ctx=canvas.getContext('2d');let run=null,last=0;const history=[];
 const WHITE='#f6f9fd',SHADE='#dfe7f2',DEEP='#c9d6e6',GLINT='#ffffff';
 function puff(x,y,r,c){x=Math.round(x);y=Math.round(y);for(let dy=-r;dy<=r;dy++){const h=Math.floor(Math.sqrt(r*r-dy*dy));ctx.fillStyle=c;ctx.fillRect(x-h,y+dy,h*2+1,1);}}
 function cloud(x,y,r){puff(x,y+2,r,SHADE);puff(x,y,r,WHITE);puff(x+r*.8,y+1,Math.max(2,Math.round(r*.7)),SHADE);puff(x+r*.8,y,Math.max(2,Math.round(r*.7)),WHITE);puff(x-r*.9,y+1,Math.max(2,Math.round(r*.6)),WHITE);ctx.fillStyle=GLINT;ctx.fillRect(Math.round(x-r*.4),Math.round(y-r*.7),Math.max(2,Math.round(r*.6)),1);}
 const wrap=(v,p)=>((v%p)+p)%p;
 function windowSky(x,t){   // one oval window: three layers moving right, world-continuous across the windows
  ctx.fillStyle='#9fc9ee';ctx.fillRect(x+5,44,17,21);ctx.fillStyle='#b4d7f3';ctx.fillRect(x+5,52,17,13);
  for(let k=0;k<8;k++){const cx=wrap(k*47+t*.045,376)-17;puff(cx,48+(k%3)*2,2,'#e4eef8');}
  for(let k=0;k<6;k++){const cx=wrap(k*63+t*.13,378)-18,cy=55+(k%2)*5;puff(cx,cy+1,4,SHADE);puff(cx,cy,4,WHITE);puff(cx+5,cy+1,3,WHITE);}
  ctx.fillStyle=GLINT;for(let k=0;k<5;k++){const sx=wrap(k*71+t*.26,400)-30;ctx.fillRect(Math.round(sx),46+k*4,9+k%3*4,1);}
 }
 function cabin(t){
  ctx.fillStyle='#e7e5e9';ctx.fillRect(0,0,canvas.width,canvas.height);const k=canvas.width/342,bump=(t%1700)<90?1:0,oy=Math.round((canvas.height-118*k)/2)+bump;
  ctx.save();ctx.translate(0,oy);ctx.scale(k,k);ctx.drawImage(images.airport_cabin,0,0);
  for(const x of [30,88,146,204,262]){ctx.save();ctx.beginPath();for(let y=0;y<21;y++){const inset=y<2?5:y<4?3:y<6?1:y>18?3:y>16?1:0;ctx.rect(x+5+inset,44+y,17-inset*2,1)}ctx.clip();windowSky(x,t);ctx.restore();
   ctx.fillStyle='#f6f9fd';ctx.fillRect(x+8,61,11,1);ctx.fillRect(x+6,62,15,1);}
  drawHero(ctx,153,62);ctx.drawImage(images.airport_cabin_front,0,0);ctx.restore();
 }
 function ease(t){t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)}
 // The wipe: new picture left of a ragged edge, a band of clouds riding the edge, wind streaks ahead.
 function sweep(pic,t,dur){
  const W=canvas.width,Hh=canvas.height,e=ease(t/dur),edge=Math.round(-90+(W+180)*e),rows=Math.ceil(Hh/8);
  ctx.save();ctx.beginPath();for(let i=0;i<rows;i++){const off=Math.round(Math.sin(i*1.9)*9+Math.sin(i*.7)*5);ctx.rect(0,i*8,Math.max(0,edge-24+off),8);}ctx.clip();
  if(typeof pic==='function')pic();else ctx.drawImage(pic,0,0,W,Hh);ctx.restore();
  for(let i=-1;i<=rows;i++){const off=Math.round(Math.sin(i*1.9)*9+Math.sin(i*.7)*5),r=9+(i*7%5);puff(edge-30+off,i*8+4,r+3,DEEP);}
  for(let i=-1;i<=rows;i++){const off=Math.round(Math.sin(i*1.9)*9+Math.sin(i*.7)*5),r=9+(i*7%5);cloud(edge-14+off,i*8+3,r);}
  // the wake trails BEHIND the wall (left): torn-off puffs shrinking away, then wind lines (owner: it must read as moving right)
  for(let i=0;i<rows;i++){const off=Math.round(Math.sin(i*1.9)*9+Math.sin(i*.7)*5);for(let j=0;j<3;j++){const r=4-j-(i%2),x=edge-40+off-j*(14+i*5%9);if(r>0)puff(x,i*8+4+(j%2)*2,r,j?SHADE:WHITE);}}
  for(let i=0;i<rows*2;i++){const len=14+(i*13%30),x=edge-64-(i*29%70)-len;ctx.fillStyle=i%3?GLINT:SHADE;ctx.fillRect(x,Math.round(i*4+(i%3)),len,1);ctx.fillRect(x+len,Math.round(i*4+(i%3)),3,1);}
 }
 function tick(now){if(!run)return;const dt=last&&!paused()&&!document.hidden?Math.min(100,now-last):0;last=now;run.elapsed+=dt;run.total+=dt;ctx.imageSmoothingEnabled=false;
  if(run.phase==='enter'){ctx.drawImage(run.from,0,0,canvas.width,canvas.height);sweep(()=>cabin(run.total),run.elapsed,700);if(run.elapsed>=700){cabin(run.total);run.phase='hold';run.elapsed=0;history.push({phase:'hold',at:now})}}
  else if(run.phase==='hold'){cabin(run.total);if(run.elapsed>=3000){run.target=run.arrive();run.phase='exit';run.elapsed=0;history.push({phase:'exit',at:now})}}
  else{cabin(run.total);sweep(run.target,run.elapsed,700);if(run.elapsed>=700){ctx.drawImage(run.target,0,0,canvas.width,canvas.height);const done=run.done;run=null;history.push({phase:'done',at:now});onFrame();done?.();return}}
  onFrame();requestAnimationFrame(tick);
 }
 return {history,cabin,sweep,get phase(){return run?.phase||'idle'},get busy(){return !!run},start(from,arrive,done){if(run)return false;run={from,arrive,done,phase:'enter',elapsed:0,total:0};last=0;history.length=0;history.push({phase:'enter',at:performance.now()});requestAnimationFrame(tick);return true}};
}
