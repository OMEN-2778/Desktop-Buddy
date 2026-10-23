// One saved seed picks the same evening palette in every scene and after reload.
function duskState(t = sim.t, kind = weather.kind) {
  const day=Math.floor(t/1440),h=((t%1440)+1440)%1440/60;
  let n=(weather.skySeed ^ (day+1))>>>0;
  n=Math.imul(n^(n>>>16),0x45d9f3b);n=Math.imul(n^(n>>>16),0x45d9f3b);n=(n^(n>>>16))>>>0;
  const smooth=(a,b,x)=>{const k=Math.max(0,Math.min(1,(x-a)/(b-a)));return k*k*(3-2*k);};
  return {mode:n/4294967296<.3?'rose':'warm',h,
    strength:kind==='clear'?smooth(16.5,17.8,h)*(1-smooth(19,20.25,h)):0,
    sunY:52-18+(h-16.5)*10};
}
function outdoorNightness(h) {
  if(h>=17&&h<20.25){const k=Math.max(0,Math.min(1,(h-18)/2.25));return k*k*(3-2*k);}
  return nightness(h);
}
const duskCanvas=document.createElement('canvas'),duskCtx=duskCanvas.getContext('2d');
function duskBuffer(width) {
  if(duskCanvas.width!==width||duskCanvas.height!==H){duskCanvas.width=width;duskCanvas.height=H;}
  duskCtx.imageSmoothingEnabled=false;
  duskCtx.clearRect(0,0,width,H);return duskCtx;
}
function drawDuskSky(ctx,mask,horizon,x=0,dock=false) {
  const s=duskState();if(!s.strength||!mask)return;
  const c=duskBuffer(mask.width);
  c.drawImage(IMG.dusk[s.mode],0,0,mask.width,horizon);
  if(dock){
    const y=Math.round(s.sunY);
    c.save();c.beginPath();c.rect(0,0,W,horizon);c.clip();
    c.globalAlpha=.07;c.fillStyle='#f7d4a3';
    for(const r of [17,14]){c.beginPath();c.ellipse(204,y,r,r*.85,0,0,Math.PI*2);c.fill();}
    c.globalAlpha=1;c.drawImage(IMG.dusk.sun,192,y-12);c.restore();
  }
  c.globalCompositeOperation='destination-in';c.drawImage(mask,0,0);c.globalCompositeOperation='source-over';
  ctx.save();ctx.globalAlpha=s.strength;ctx.drawImage(duskCanvas,Math.round(x),0);ctx.restore();
}
function drawDuskSea(ctx,mask) {
  const s=duskState();if(!s.strength||!mask||s.sunY>62)return;
  const c=duskBuffer(W),phase=reduceMotionUI?0:realClock*.6;
  // Broken horizontal glints widen towards the viewer; the mask protects rails/planks.
  for(let y=54;y<87;y+=2){
    const depth=(y-52)/36,w=Math.round(3+depth*15),drift=Math.round(Math.sin(y*1.7+phase)*3);
    c.globalAlpha=(.55-depth*.28)*s.strength;
    c.fillStyle=s.mode==='rose'?'#f5c9c4':'#f7d4a3';
    c.fillRect(204-w+drift,y,w*2+1,1);
    if(y%6===0)c.fillRect(204+w+5+drift,y,3,1);
  }
  c.globalAlpha=1;c.globalCompositeOperation='destination-in';c.drawImage(mask,0,0);c.globalCompositeOperation='source-over';
  ctx.drawImage(duskCanvas,0,0);
}
