// Thunderstorms only affect home and exposed outdoor maps; never mall/bar interiors.
function isRain(kind=weather.kind){return kind==='rain'||kind==='storm';}
const stormOutside=()=>weather.kind==='storm'&&['front','park','beach'].includes(sim.place);
const stormExposed=()=>weather.kind==='storm'&&(sim.place==='home'||stormOutside());
const stormFX={left:0,duration:.22,bolt:0};
for(const group of ['negative','positive','outdoor'])STORM_TEXT[group].forEach((t,i)=>ML[`storm_${group}_${i}`]={name:t[0],emo:t[1],pts:group==='positive'?2:1,min:75});
function stormReaction(outdoor=false){
  if(!stormExposed()||asleep()||sim.mode==='down')return;
  const positive=Math.random()<.25;
  const group=outdoor?'outdoor':positive?'positive':'negative';
  const pool=STORM_TEXT[group].map((t,i)=>({t,i})).filter(({t})=>!outdoor||positive===['happy','inspired','energized','focused','confident','flirty','playful'].includes(t[1]));
  const seen=(lifeFlags.stormSeen||=[]);let fresh=pool.filter(({i})=>!seen.includes(group+i));
  if(!fresh.length){for(const {i}of pool){const at=seen.indexOf(group+i);if(at>=0)seen.splice(at,1);}fresh=pool;}
  const {t,i}=pick(fresh);seen.push(group+i);
  // Weather alone must not stack several reactions into an extreme emotion.
  for(const id of moods.keys())if(id.startsWith('storm_'))moods.delete(id);
  log(t[2]);speak(t[3],true);addMood(`storm_${group}_${i}`,{diary:false,words:false});
  if(positive)sim.needs.fun=clamp(sim.needs.fun+3);
}
function lightningStrike(){
  stormFX.duration=reduceMotionUI?.35:.22;stormFX.left=stormFX.duration;stormFX.bolt=Math.floor(Math.random()*3);
  weather.nextLightning=sim.t+50+Math.random()*45;
  if(stormExposed()&&sim.t-(weather.lastStormReaction??-1e9)>=90){stormReaction(stormOutside());weather.lastStormReaction=sim.t;}
}
function tickStorm(dt){
  if(weather.kind!=='storm'){stormFX.left=0;return;}
  if(!(dt>0))return;
  stormFX.left=Math.max(0,stormFX.left-dt);
  if(!Number.isFinite(weather.nextLightning))weather.nextLightning=sim.t+8;
  if(sim.t>=weather.nextLightning&&stormFX.left<=0)lightningStrike();
  if(stormOutside()){
    if(life.npcs?.length){life.npcs=[];life.talkQ=null;clearNpcPills();}
    if(sim.t-(weather.lastStormEvent??-1e9)>=75&&!cardHolds()&&sim.mode!=='down'){
      weather.lastStormEvent=sim.t;
      if(sim.t-(weather.lastStormReaction??-1e9)>=35){stormReaction(true);weather.lastStormReaction=sim.t;}
    }
  }
}
function stormFlash(){
  if(!stormExposed()||stormFX.left<=0)return 0;
  const elapsed=stormFX.duration-stormFX.left;
  return reduceMotionUI ? .35 : elapsed<.10 ? 1 : 0;
}
function stormWindowFlash(ctx,win,m){
  const flash=stormFlash();if(!flash)return;
  masked(ctx,m,m.glass,win.x,win.y,g=>{g.fillStyle=`rgba(247,250,255,${flash})`;g.fillRect(0,0,m.w,m.h);});
}
function drawStorm(ctx){
  if(!stormExposed())return;
  const home=sim.place==='home',flash=stormFlash();
  ctx.save();ctx.globalCompositeOperation='source-atop';ctx.fillStyle=`rgba(22,38,65,${home ? .12 : .28})`;ctx.fillRect(0,0,W,H);
  if(flash){
    // Hard cut to white, hold 100 ms, hard cut back: no ramp or spatial gradient.
    ctx.fillStyle=`rgba(255,255,255,${flash})`;ctx.fillRect(0,0,W,H);
  }else if(!home&&stormFX.left>0&&!reduceMotionUI){
    const se=SEASON_KEYS[seasonOf(sim.t).i];
    const mask=sim.place==='park'?parkImages().seasons[se]?.skyMask:IMG.out[sim.place].seasons[se]?.skyMask;
    if(mask){
      const c=duskBuffer(W);c.drawImage(IMG.storm.bolts[stormFX.bolt],0,0);
      c.globalCompositeOperation='destination-in';c.drawImage(mask,0,0);c.globalCompositeOperation='source-over';ctx.drawImage(duskCanvas,0,0);
    }
  }
  ctx.restore();
}
