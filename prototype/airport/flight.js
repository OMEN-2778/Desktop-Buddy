// Shared by art review and game-shell adapter. Timings are real visible milliseconds.
function createCabinFlight({canvas,images,drawHero,onFrame=()=>{},paused=()=>false}){
 const ctx=canvas.getContext('2d');let run=null,last=0;const history=[];
 function cabin(t){ctx.fillStyle='#e7e5e9';ctx.fillRect(0,0,canvas.width,canvas.height);const k=canvas.width/342,oy=Math.round((canvas.height-118*k)/2);ctx.drawImage(images.airport_cabin,0,oy,canvas.width,118*k);ctx.save();ctx.translate(0,oy);ctx.scale(k,k);
  // Window clouds rasterized on the native pixel grid.
  for(const x of [30,88,146,204,262]){ctx.save();ctx.beginPath();for(let y=0;y<15;y++){const inset=y<2?5:y<4?3:y<6?1:0;ctx.rect(x+5+inset,44+y,17-inset*2,1)}ctx.clip();ctx.fillStyle='#b4d7f3';ctx.fillRect(x+5,44,17,15);const drift=Math.floor(t/140+x/3)%39;for(let q=-1;q<2;q++){let xx=x+5+q*39+drift;ctx.fillStyle='#f6f9fd';ctx.fillRect(xx,52,15,3);ctx.fillRect(xx+4,49,7,3);ctx.fillStyle='#dfe7f2';ctx.fillRect(xx+2,55,12,1)}ctx.restore()}
  drawHero(ctx,153,62);ctx.drawImage(images.airport_cabin_front,0,0);ctx.restore();
 }
 function ease(t){t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)}
 function reveal(pic,t){for(let i=0;i<6;i++){const w=Math.round(canvas.width*ease((t-i*45)/475)),y=Math.floor(i*canvas.height/6),h=Math.ceil(canvas.height/6);ctx.save();ctx.beginPath();ctx.rect(0,y,w,h);ctx.clip();if(typeof pic==='function')pic();else ctx.drawImage(pic,0,0,canvas.width,canvas.height);ctx.restore()}}
 function tick(now){if(!run)return;const dt=last&&!paused()&&!document.hidden?Math.min(100,now-last):0;last=now;run.elapsed+=dt;run.total+=dt;ctx.imageSmoothingEnabled=false;
  if(run.phase==='enter'){ctx.drawImage(run.from,0,0,canvas.width,canvas.height);reveal(()=>cabin(run.total),run.elapsed);if(run.elapsed>=700){cabin(run.total);run.phase='hold';run.elapsed=0;history.push({phase:'hold',at:now})}}
  else if(run.phase==='hold'){cabin(run.total);if(run.elapsed>=2000){run.target=run.arrive();run.phase='exit';run.elapsed=0;history.push({phase:'exit',at:now})}}
  else{cabin(run.total);reveal(run.target,run.elapsed);if(run.elapsed>=700){ctx.drawImage(run.target,0,0,canvas.width,canvas.height);const done=run.done;run=null;history.push({phase:'done',at:now});onFrame();done?.();return}}
  onFrame();requestAnimationFrame(tick);
 }
 return {history,get phase(){return run?.phase||'idle'},get busy(){return !!run},start(from,arrive,done){if(run)return false;run={from,arrive,done,phase:'enter',elapsed:0,total:0};last=0;history.length=0;history.push({phase:'enter',at:performance.now()});requestAnimationFrame(tick);return true}};
}
