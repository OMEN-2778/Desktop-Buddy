// Thunderstorms only affect home and exposed outdoor maps; never mall/bar interiors.
function isRain(kind=weather.kind){return kind==='rain'||kind==='storm';}
const stormOutside=()=>weather.kind==='storm'&&['front','park','beach'].includes(sim.place);
const stormExposed=()=>weather.kind==='storm'&&(sim.place==='home'||stormOutside());
const stormFX={left:0,duration:0,bolt:0,x:0};
for(const group of ['negative','positive','outdoor'])STORM_TEXT[group].forEach((t,i)=>ML[`storm_${group}_${i}`]={name:t[0],emo:t[1],pts:group==='positive'?2:1,min:75});
function stormReaction(outdoor=false){
  if(!stormExposed()||asleep()||sim.mode==='down')return;
  const positive=Math.random()<(.25-heroPersonality.sensitivity*.001);
  const group=outdoor?'outdoor':positive?'positive':'negative';
  const pool=STORM_TEXT[group].map((t,i)=>({t,i})).filter(({t})=>!outdoor||positive===['happy','inspired','energized','focused','confident','flirty','playful'].includes(t[1]));
  const seen=(lifeFlags.stormSeen||=[]);let fresh=pool.filter(({i})=>!seen.includes(group+i));
  if(!fresh.length){for(const {i}of pool){const at=seen.indexOf(group+i);if(at>=0)seen.splice(at,1);}fresh=pool;}
  const {t,i}=pick(fresh);seen.push(group+i);
  // Weather alone must not stack several reactions into an extreme emotion.
  for(const id of moods.keys())if(id.startsWith('storm_'))moods.delete(id);
  const reason=heroPersonality.sensitivity>25?(positive?'平时容易留意细节，这次反而被雨中的光打动了。':'自己对突如其来的声光比较敏感，想先缓一缓。'):heroPersonality.sensitivity< -25?(positive?'习惯先稳住心情，听着雨声反而觉得踏实。':'平时虽沉得住气，突来的雷声还是让人停顿了一下。'):'先感受一下心情，等这阵雷声过去。';
  log(t[2]+' '+reason);speak(t[3],true);addMood(`storm_${group}_${i}`,{diary:false,words:false});
  if(positive)sim.needs.fun=clamp(sim.needs.fun+3);
}
function lightningStrike(){
  stormFX.duration=reduceMotionUI ? 1.4 : .8;
  stormFX.left=stormFX.duration;stormFX.bolt=Math.floor(Math.random()*3);
  stormFX.x=24+Math.random()*(W-48);
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
  const t=1-stormFX.left/stormFX.duration;
  if(sim.place==='home'||reduceMotionUI)return Math.pow(Math.sin(Math.PI*t),reduceMotionUI?2:.6)*(reduceMotionUI?.32:1);
  const elapsed=stormFX.duration-stormFX.left;
  return elapsed>=.09&&elapsed<.18 ? .8 : 0;
}
function stormBolt(){
  if(!stormOutside()||stormFX.left<=0||reduceMotionUI)return {growth:0,alpha:0};
  const elapsed=stormFX.duration-stormFX.left;
  return {growth:Math.min(1,elapsed/.09),alpha:elapsed<.18?1:Math.pow(Math.max(0,1-(elapsed-.18)/.62),1.5)*.7};
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
    // At home, light comes through windows instead of whitening the whole room.
    if(!home){ctx.fillStyle=`rgba(255,255,255,${flash})`;ctx.fillRect(0,0,W,H);}
    if(home)for(const[id,win]of Object.entries(WMASK)){
      if(windowState[id]==='drawn')continue;
      const m=windowState[id]==='open'&&win.open?win.open:win.closed;
      if(!m)continue;
      const x=win.x+m.w/2,y=win.y+m.h/2;
      const room=Object.values(D.rooms).find(([rx,ry,rw,rh])=>x>=rx&&x<rx+rw&&y>=ry&&y<ry+rh);
      if(!room)continue;
      ctx.save();ctx.beginPath();ctx.rect(...room);ctx.clip();
      const light=ctx.createRadialGradient(x,y,2,x,y,Math.max(45,m.w*1.6));
      light.addColorStop(0,`rgba(240,247,255,${flash*.65})`);
      light.addColorStop(.4,`rgba(240,247,255,${flash*.32})`);
      light.addColorStop(1,'rgba(240,247,255,0)');
      ctx.fillStyle=light;ctx.fillRect(...room);ctx.restore();
    }
  }
  const bolt=stormBolt();
  if(bolt.alpha>0&&bolt.growth>0){
    const se=SEASON_KEYS[seasonOf(sim.t).i];
    const mask=sim.place==='park'?parkImages().seasons[se]?.skyMask:IMG.out[sim.place].seasons[se]?.skyMask;
    if(mask){
      const c=duskBuffer(W),image=IMG.storm.bolts[stormFX.bolt],height=Math.max(1,Math.ceil(image.height*bolt.growth));
      c.drawImage(image,0,0,image.width,height,Math.round(stormFX.x-image.width/2),0,image.width,height);
      c.globalCompositeOperation='destination-in';c.drawImage(mask,0,0);c.globalCompositeOperation='source-over';
      ctx.globalAlpha=bolt.alpha;ctx.drawImage(duskCanvas,0,0);
    }
  }
  ctx.restore();
}
