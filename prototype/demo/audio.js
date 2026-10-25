// Audio is separate from simulation time. No sound or downloads until enabled
// and unlocked by a real user gesture. Both preference bits also travel in saves.
const GAME_AUDIO_FILES = /*__AUDIO_FILES__*/null;
const GAME_AUDIO_VERSION = /*__AUDIO_VERSION__*/null;
const GAME_AUDIO_INLINE = /*__AUDIO_INLINE__*/null;
const gameAudio = (() => {
  let ctx=null, musicBus=null, effectsBus=null, limiter=null, meter=null, unlocked=false;
  let muted=false, epoch=0, musicKey='', nextMusicRetry=0, currentMusic=null, lastTick=-Infinity;
  let actionKey='', previousPlace='', nextFoley=0, nextAccent=0;
  const cache=new Map(), pending=new Map(), loops=new Map(), voices=new Set(), tracks=new Set(), cooldown=new Map(), failed=new Map();
  const stats={played:0,loads:0,errors:[],last:[],music:''};
  // Both raw demo and packaged app use their own sibling audio directory.
  const url=path=>new URL('audio/'+path+'?v='+GAME_AUDIO_VERSION,document.baseURI).href;
  const sfx=id=>id.endsWith('-cc0')?'SFX/processed/'+id+'.mp3':'SFX/game/'+id+'.mp3';
  const ready=()=>unlocked&&ctx?.state==='running'&&!muted;
  const now=()=>performance.now()/1000;
  function ramp(node,value,seconds=.15){const at=ctx.currentTime;node.gain.cancelScheduledValues(at);node.gain.setValueAtTime(node.gain.value,at);node.gain.linearRampToValueAtTime(value,at+seconds);}
  function report(path,error){if(stats.errors.length<20)stats.errors.push({path,error:String(error)});failed.set(path,now()+30);}
  function wake(){
    if(!prefs.bgm&&!prefs.sfx)return;
    try{
      if(!ctx){
        const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
        ctx=new AC();musicBus=ctx.createGain();effectsBus=ctx.createGain();limiter=ctx.createDynamicsCompressor();
        limiter.threshold.value=-12;limiter.knee.value=12;limiter.ratio.value=5;limiter.attack.value=.004;limiter.release.value=.2;
        musicBus.connect(limiter);effectsBus.connect(limiter);meter=ctx.createAnalyser();meter.fftSize=512;limiter.connect(meter);meter.connect(ctx.destination);
        musicBus.gain.value=prefs.bgm?.32:0;effectsBus.gain.value=prefs.sfx?.75:0;
      }
      unlocked=true;muted=document.hidden;ctx.resume().then(()=>{if(!muted)sync();}).catch(()=>{});
    }catch(e){report('AudioContext',e);}
  }
  async function buffer(path){
    if(cache.has(path))return cache.get(path);
    if(!GAME_AUDIO_FILES.includes(path)||(failed.get(path)||0)>now())return null;
    if(!pending.has(path)){
      stats.loads++;
      pending.set(path,(async()=>{
        try{
          let bytes;
          if(GAME_AUDIO_INLINE[path])bytes=Uint8Array.from(atob(GAME_AUDIO_INLINE[path]),c=>c.charCodeAt(0)).buffer;
          else{const response=await fetch(url(path));if(!response.ok)throw new Error('HTTP '+response.status);bytes=await response.arrayBuffer();}
          const b=await ctx.decodeAudioData(bytes);cache.set(path,b);return b;
        }catch(e){report(path,e);return null;}finally{pending.delete(path);}
      })());
    }
    return pending.get(path);
  }
  function stopVoice(v,fade=.07){
    if(!v||v.stopped)return;v.stopped=true;ramp(v.gain,0,fade);
    try{v.source.stop(ctx.currentTime+fade+.02);}catch{}
  }
  function voice(b,volume,loop=false,rate=1){
    const source=ctx.createBufferSource(),gain=ctx.createGain();source.buffer=b;source.loop=loop;source.playbackRate.value=rate;
    source.connect(gain);gain.connect(effectsBus);gain.gain.value=loop?0:volume;
    const v={source,gain,stopped:false};voices.add(v);
    source.onended=()=>{voices.delete(v);source.disconnect();gain.disconnect();};
    source.start();if(!loop&&b.duration>8)source.stop(ctx.currentTime+6);if(loop)ramp(gain,volume,.65);return v;
  }
  function sound(id,volume=1,options={}){
    if(!prefs.sfx||!ready())return;
    const time=now(),tag=options.tag||id;
    if(time-(cooldown.get(tag)??-Infinity)<(options.gap??.12))return;
    cooldown.set(tag,time);const token=epoch;
    buffer(sfx(id)).then(b=>{
      if(!b||token!==epoch||!prefs.sfx||!ready()||now()-time>(options.maxAge??.8))return;
      if([...voices].filter(v=>!v.stopped&&!v.source.loop).length>=10)return;
      const v=voice(b,volume,false,options.vary?(.95+Math.random()*.1):1);v.tag=tag;
      stats.played++;stats.last.push(id);if(stats.last.length>24)stats.last.shift();
    });
  }
  function stopTag(tag){for(const v of voices)if(v.tag===tag)stopVoice(v,.025);}
  function setLoop(key,id,volume){
    const path=sfx(id),old=loops.get(key);
    if(old?.path===path){old.volume=volume;if(old.voice)ramp(old.voice.gain,volume,.4);return;}
    if(old){loops.delete(key);stopVoice(old.voice,.4);}
    const entry={path,voice:null,volume};loops.set(key,entry);const token=epoch;
    buffer(path).then(b=>{
      if(loops.get(key)!==entry||token!==epoch)return;
      if(!b){loops.delete(key);return;}
      if(!prefs.sfx||!ready()){loops.delete(key);return;}
      entry.voice=voice(b,entry.volume,true);
    });
  }
  function stopEffects(){epoch++;for(const v of voices)stopVoice(v,.035);loops.clear();cooldown.clear();actionKey='';}
  function disposeTrack(t,fade=1.2){
    if(!t||t.retiring)return;t.retiring=true;ramp(t.gain,0,fade);
    t.timer=setTimeout(()=>{t.el.pause();t.el.removeAttribute('src');t.el.load();t.node.disconnect();t.gain.disconnect();tracks.delete(t);},fade*1000+50);
  }
  function stopMusic(){musicKey='';stats.music='';nextMusicRetry=0;currentMusic=null;for(const t of tracks)disposeTrack(t,.08);}
  function chooseMusic(){
    const place=sim.place,season=SEASON_KEYS[seasonOf(sim.t).i],night=hour()<6||hour()>=18;
    if(place==='park')return 'BGM/park/park-'+season+'.mp3';
    if(place==='mall')return 'BGM/mall/mall-crowd-rush.mp3';
    if(place==='bar')return 'BGM/bar/'+(night?'bar-amber-bass':'bar-daylight-cup')+'.mp3';
    if(place==='beach')return 'BGM/harbor/harbor-mist-return.mp3';
    return 'BGM/home/'+season+'-'+(night?'night':'day')+'.mp3';
  }
  function updateMusic(){
    if(!prefs.bgm||!ready())return;
    const path=chooseMusic();if(path===musicKey||now()<nextMusicRetry)return;
    if(!GAME_AUDIO_FILES.includes(path))return;
    musicKey=path;const el=new Audio();el.preload='none';el.loop=true;
    const gain=ctx.createGain(),node=ctx.createMediaElementSource(el);gain.gain.value=0;node.connect(gain);gain.connect(musicBus);
    const t={el,node,gain,retiring:false};tracks.add(t);el.src=url(path);
    const fail=e=>{if(t.retiring)return;report(path,e);if(musicKey===path){musicKey='';nextMusicRetry=now()+30;}if(currentMusic===t)currentMusic=null;disposeTrack(t,.05);};
    el.addEventListener('error',()=>fail(el.error?.message||'audio loading failed'),{once:true});
    el.play().then(()=>{
      if(!prefs.bgm||!ready()||musicKey!==path||t.retiring){disposeTrack(t,.05);return;}
      if(currentMusic)disposeTrack(currentMusic);currentMusic=t;stats.music=path;ramp(gain,1,1.2);
    }).catch(fail);
    // A slow previous request must not start playing after a later scene change.
    for(const other of tracks)if(other!==t&&other!==currentMusic)disposeTrack(other,.05);
  }
  function setEnabled(channel,value){
    if(!['bgm','sfx'].includes(channel))return;
    prefs[channel]=!!value;if(value)wake();sync();saveSettings();buildSettings();
    if(channel==='sfx'&&value)sound('ui-click',.75);
  }
  function sync(){
    if(!ctx)return;
    ramp(musicBus,prefs.bgm&&!muted?.32:0,.08);ramp(effectsBus,prefs.sfx&&!muted?.75:0,.05);
    if(!prefs.bgm||muted)stopMusic();if(!prefs.sfx||muted)stopEffects();
    if(ready()){
      if(prefs.sfx)for(const id of ['ui-click','ui-open','ui-close','ui-card','ui-result','ui-message','phone-ring','phone-answer','phone-decline'])buffer(sfx(id));
      updateMusic();tick(true);
    }
  }
  // One action adapter covers main house, park, public restrooms, bar, mall
  // interiors, and the 30 friend houses. Sounds begin on arrival, never en route.
  function activity(){
    if(sim.mode==='down'||wiping||wardrobeOpen)return '';
    if(atFriendHome())return sim.mode==='act'?friendVisit.action:'';
    if(sim.place==='bar')return sim.bar?.toilet?.phase==='inside'?'toilet':sim.mode==='walk'?'':sim.bar?.drink?'drink':sim.bar?.seat?'sit':'';
    if(sim.place==='mall'){
      if(mallToiletInside())return 'toilet';
      if(mallVisitInside())return mallS.visit.kind==='restaurant'?'eat':mallSleeping()?'sleep':'cinema';
      if(mallInside())return ({pets:'pet',arcade:'computer',books:'read',coffee:'drink',dessert:'eat',clothes:'dress',sneakers:'dress'})[mallS.stop?.it?.id]||'inspect';
    }
    return sim.mode==='act'?sim.act||'':'';
  }
  const ACTION_SOUND={pet:'cat-purr-meow-cc0',toilet:'seat',park_toilet:'seat',eat:'cutlery',park_eat:'cutlery',snack:'drawer',friend_snack:'drawer',tv:'switch',computer:'keyboard',pc_code:'keyboard',pc_forum:'keyboard',pc_video:'switch',read:'page',towel:'fabric',dress:'fabric',sleep:'fabric',nap:'fabric',bench:'seat',sit:'seat',drink:'drink',water:'watering',water_living:'watering',water_study:'watering',music:'music',laundry:'switch',art:'page',window:'fabric',inspect:'ui-click',fish:'splash',fishing:'splash',dance:'music',phone_game:'switch',phone_feed:'ui-message'};
  const ACTION_LOOP={bath:['water',.24],wash:['water',.20],cook:['cook',.23],laundry:['washer',.35],tv:['tv',.25],pc_video:['tv',.2],dance:['music',.3],cinema:['cinema',.35]};
  const ACTION_REPEAT={computer:['keyboard',3],pc_code:['keyboard',2.3],pc_forum:['keyboard',4],read:['page',12],eat:['cutlery',6],park_eat:['cutlery',6],drink:['drink',9],water:['watering',5],water_living:['watering',5],water_study:['watering',5],music:['music',5]};
  function ambience(){
    const a={},place=sim.place,outside=['front','park','beach'].includes(place),home=place==='home'||atFriendHome(),h=hour(),night=h<6||h>=19,se=SEASON_KEYS[seasonOf(sim.t).i];
    const wet=weather.kind==='rain'||weather.kind==='storm';
    if((outside||home)&&wet)a.rain=[weather.kind==='storm'?'rain-heavy-window-cc0':'rain-soft-loop-cc0',outside?.32:.10];
    if(outside){
      a.air=['wind',weather.kind==='storm'?.32:.12];
      if(place==='beach'){a.water=['waves',.30];if(!wet&&!night)a.birds=['gulls',.38];}
      else if(!wet&&weather.kind!=='snow'){
        if(!night)a.birds=['birds',place==='park'?.42:.22];
        else if(se!=='winter')a.birds=['insects',.30];
        if(place==='park')a.leaves=['leaves',.3];
      }
      if(!wet&&life.npcs?.length>1)a.people=['crowd-indoor-walla-cc0',.045];
    }
    if(place==='mall'){
      if(!mallToiletInside()&&(!mallVisitInside()||mallS.visit.kind!=='cinema'))a.people=['crowd-indoor-walla-cc0',mallVisitInside()?.11:.14];
    }else if(place==='bar'&&sim.bar?.toilet?.phase!=='inside')a.people=['crowd-indoor-walla-cc0',.12];
    return a;
  }
  function tick(force=false){
    const time=now();if(!force&&time-lastTick<.10)return;lastTick=time;
    if(!ready())return;updateMusic();if(!prefs.sfx)return;
    if(weather.kind==='storm'&&stormExposed())buffer(sfx('thunder-heavy-no-rain-cc0'));
    const desired=ambience(),act=activity(),playing=speed>0&&!cardHolds()&&!wiping;
    if(phoneCall.phase==='ringing')desired.ring=['phone-ring',.8];
    if(playing&&ACTION_LOOP[act])desired.action=ACTION_LOOP[act];
    for(const [key,[id,volume]]of Object.entries(desired))setLoop(key,id,volume);
    for(const [key,entry]of loops)if(!desired[key]){loops.delete(key);stopVoice(entry.voice,key==='ring'?.025:.45);}
    // Keep state current while paused so opening a dialog doesn't restart Foley.
    const key=sim.place+':'+act;
    if(playing&&key!==actionKey){
      const old=actionKey.split(':').at(-1);
      if((old==='toilet'||old==='park_toilet')&&previousPlace===sim.place)sound('flush',.12,{gap:3});
      if(ACTION_SOUND[act])sound(ACTION_SOUND[act],.5,{vary:true});
      actionKey=key;nextFoley=time+3;
    }
    previousPlace=sim.place;
    if(playing&&time>=nextAccent){
      nextAccent=time+30+Math.random()*30;
      if(sim.place==='front'&&weather.kind==='clear'&&hour()>=7&&hour()<20)sound('cat-meow-cc0',.15,{gap:30});
      else if((sim.place==='bar'&&!sim.bar?.toilet||sim.place==='mall'&&!mallInside())&&life.npcs?.length>1)sound('crowd-small-laugh-cc0',.12,{gap:30});
    }
    if(playing&&ACTION_REPEAT[act]&&time>=nextFoley){const [id,interval]=ACTION_REPEAT[act];sound(id,.35,{vary:true});nextFoley=time+interval+Math.random()*2;}
  }
  // Observe logical expansion, not every animation frame. One opening gets one
  // sound; filling a list or moving the pointer inside an open panel is silent.
  function installUI(){
    const hiddenIds=['picker','card','cardRes','ring','diaryPop','moodTip','skyTip','studio','guide','update','popSay'];
    const roots=hiddenIds.map(id=>({el:document.getElementById(id),active:el=>!el.hidden}));
    for(const id of ['needs','setGear','networkTrigger'])roots.push({el:document.getElementById(id),active:el=>el.getAttribute('aria-expanded')==='true'});
    for(const id of ['contactsPanel','contactActions'])roots.push({el:document.getElementById(id),active:el=>el.getAttribute('aria-hidden')==='false'});
    roots.push({el:socialSheet,active:el=>!el.hidden},{el:moodrow,active:el=>el.classList.contains('network-ready')});
    for(const entry of roots){if(!entry.el)continue;entry.was=entry.active(entry.el);}
    const observer=new MutationObserver(records=>{
      const changed=new Set(records.map(r=>r.target));let opening=null,closing=false;
      for(const entry of roots){if(!changed.has(entry.el))continue;const active=entry.active(entry.el);if(active!==entry.was){entry.was=active;if(active)opening=entry.el.id||'panel';else closing=true;}}
      if(opening)sound(opening==='card'?'ui-card':opening==='cardRes'?'ui-result':opening==='popSay'?'ui-message':'ui-open',.65,{tag:'ui-panel',gap:.1});
      else if(closing)sound('ui-close',.5,{tag:'ui-panel',gap:.1});
    });
    for(const {el}of roots)if(el)observer.observe(el,{attributes:true,attributeFilter:['hidden','class','aria-expanded','aria-hidden']});
    document.addEventListener('click',event=>{
      const button=event.target.closest('button,[role="button"],summary,input[type="checkbox"]');
      if(!button||button.disabled||button.getAttribute('aria-disabled')==='true'||button.closest('[inert]'))return;
      if(button.closest('[data-audio-channel]'))return; // enabling provides its own confirmation
      sound('ui-click',.65,{tag:'ui-click',gap:.055});
    },true);
    for(const event of ['pointerdown','keydown'])document.addEventListener(event,wake,{capture:true});
    document.addEventListener('visibilitychange',()=>{
      muted=document.hidden;sync();if(muted)ctx?.suspend().catch(()=>{});else if(unlocked)wake();
    });
    window.addEventListener('pagehide',()=>{muted=true;sync();ctx?.suspend().catch(()=>{});});
    window.addEventListener('pageshow',()=>{if(unlocked&&!document.hidden)wake();});
  }
  function thunder(){if(stormExposed())sound('thunder-heavy-no-rain-cc0',stormOutside()?.65:.25,{gap:2,maxAge:1.5});}
  function phoneEnd(accepted){const ring=loops.get('ring');if(ring){loops.delete('ring');stopVoice(ring.voice,.015);}sound(accepted?'phone-answer':'phone-decline',.65);}
  function outputLevel(){if(!meter)return 0;const a=new Float32Array(512);meter.getFloatTimeDomainData(a);return Math.sqrt(a.reduce((sum,v)=>sum+v*v,0)/a.length);}
  installUI();
  return {setEnabled,wake,sync,tick,sound,thunder,phoneEnd,activity,ambience,chooseMusic,
    debug:()=>({unlocked,level:outputLevel(),state:ctx?.state||'locked',music:stats.music,desiredMusic:chooseMusic(),loops:[...loops.keys()],voices:voices.size,tracks:tracks.size,cache:cache.size,musicTime:currentMusic?.el.currentTime||0,musicRate:currentMusic?.el.playbackRate||1,musicVolume:musicBus?.gain.value||0,effectsVolume:effectsBus?.gain.value||0,loopPaths:[...loops.values()].map(e=>e.path),stats:JSON.parse(JSON.stringify(stats))})};
})();
