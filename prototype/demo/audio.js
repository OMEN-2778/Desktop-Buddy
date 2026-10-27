// Audio is separate from simulation time. No sound or downloads until enabled
// and unlocked by a real user gesture. Both preference bits also travel in saves.
const GAME_AUDIO_FILES = /*__AUDIO_FILES__*/null;
const GAME_AUDIO_VERSION = /*__AUDIO_VERSION__*/null;
const GAME_AUDIO_INLINE = /*__AUDIO_INLINE__*/null;
const RECORDED_FOLEY={door:'real-door-cc0',fabric:'real-fabric-cc0',seat:'real-chair-cc0',drawer:'real-fridge-cc0',water:'real-water-running-cc0',pour:'real-pour-water-cc0',watering:'real-pour-water-cc0',page:'real-page-turn-cc0',keyboard:'real-keyboard-typing-cc0',cutlery:'real-cutlery-cc0',drink:'real-drink-cc0',flush:'real-toilet-flush-cc0',cook:'real-cooking-stir-cc0'};
const gameAudio = (() => {
  let ctx=null, musicBus=null, effectsBus=null, effectsGate=null, effectsMeter=null, meter=null, ambientBus=null, actionBus=null, unlocked=false;
  let muted=false, epoch=0, musicKey='', nextMusicRetry=0, currentMusic=null, requestedMusic=null, retryMusicKey='', lastTick=-Infinity;
  let sceneMixKey='', actionKey='', previousPlace='', nextFoley=0, nextAccent=0;
  const cache=new Map(), pending=new Map(), loops=new Map(), voices=new Set(), tracks=new Set(), cooldown=new Map(), failed=new Map();
  const emotionCue={current:null,candidate:null,at:0,until:0};
  const stats={played:0,loads:0,errors:[],last:[],music:''};
  // Both raw demo and packaged app use their own sibling audio directory.
  const url=path=>new URL('audio/'+path+'?v='+GAME_AUDIO_VERSION,document.baseURI).href;
  const sfx=id=>{id=RECORDED_FOLEY[id]||id;return id.endsWith('-cc0')?'SFX/processed/'+id+'.mp3':'SFX/game/'+id+'.mp3';};
  const ready=()=>unlocked&&ctx?.state==='running'&&!muted;
  const now=()=>performance.now()/1000;
  function ramp(node,value,seconds=.15){const at=ctx.currentTime;if(node.gain.cancelAndHoldAtTime)node.gain.cancelAndHoldAtTime(at);else{const value=node.gain.value;node.gain.cancelScheduledValues(at);node.gain.setValueAtTime(value,at);}node.gain.linearRampToValueAtTime(value,at+seconds);}
  function report(path,error){if(stats.errors.length<20)stats.errors.push({path,error:String(error)});failed.set(path,now()+30);}
  function wake(){
    if(!prefs.bgm&&!prefs.sfx)return;
    try{
      if(!ctx){
        const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
        ctx=new AC();musicBus=ctx.createGain();effectsBus=ctx.createGain();effectsGate=ctx.createGain();effectsMeter=ctx.createAnalyser();effectsMeter.fftSize=512;
        ambientBus=ctx.createGain();actionBus=ctx.createGain();actionBus.gain.value=.4;ambientBus.gain.value=.55;ambientBus.connect(effectsBus);actionBus.connect(effectsBus);effectsBus.connect(effectsGate);effectsGate.connect(effectsMeter);meter=ctx.createAnalyser();meter.fftSize=512;musicBus.connect(meter);effectsMeter.connect(meter);meter.connect(ctx.destination);
        musicBus.gain.value=prefs.bgm?prefs.bgmVolume/100*.53:0;effectsBus.gain.value=prefs.sfx?prefs.sfxVolume/100:0;effectsGate.gain.value=prefs.sfx?1:0;
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
  function voice(b,volume,loop=false,rate=1,options={}){
    const source=ctx.createBufferSource(),gain=ctx.createGain();source.buffer=b;source.loop=loop;source.playbackRate.value=rate;
    const filter=ctx.createBiquadFilter(),pan=ctx.createStereoPanner();filter.type='lowpass';filter.Q.value=.3;
    source.connect(filter);filter.connect(pan);pan.connect(gain);gain.connect(options.ambient?ambientBus:options.action?actionBus:effectsBus);gain.gain.value=0;
    const v={source,gain,filter,pan,stopped:false,volume,spatial:options.spatial||{}};
    placeVoice(v,loop?.65:.018);voices.add(v);
    source.onended=()=>{voices.delete(v);source.disconnect();filter.disconnect();pan.disconnect();gain.disconnect();};
    source.start(0,loop&&options.ambient?Math.random()*Math.max(.1,b.duration-1):0);if(!loop&&b.duration>8)source.stop(ctx.currentTime+6);return v;
  }
  function sound(id,volume=1,options={}){
    if(!prefs.sfx||!ready())return;
    const time=now(),tag=options.tag||id;
    if(time-(cooldown.get(tag)??-Infinity)<(options.gap??.12))return;
    cooldown.set(tag,time);const token=epoch;
    buffer(sfx(id)).then(b=>{
      if(!b||token!==epoch||!prefs.sfx||!ready()||now()-time>(options.maxAge??.8)||options.valid&&!options.valid())return;
      if([...voices].filter(v=>!v.stopped&&!v.source.loop).length>=10)return;
      if(tag==='emotion')emotionCue.until=now()+b.duration;
      const v=voice(b,volume,false,options.vary?(.95+Math.random()*.1):1,{...options,action:!!RECORDED_FOLEY[id]||!!options.spatial});v.tag=tag;
      stats.played++;stats.last.push(id);if(stats.last.length>24)stats.last.shift();
    });
  }
  function stopTag(tag){for(const v of voices)if(v.tag===tag)stopVoice(v,.025);}
  function setLoop(key,id,volume,spatial={}){
    const path=sfx(id),old=loops.get(key);
    if(old?.path===path){old.volume=volume;old.spatial=spatial;if(old.voice){old.voice.volume=volume;old.voice.spatial=spatial;placeVoice(old.voice,.35);}return;}
    if(old){loops.delete(key);stopVoice(old.voice,.4);}
    const entry={path,voice:null,volume,spatial};loops.set(key,entry);const token=epoch;
    buffer(path).then(b=>{
      if(loops.get(key)!==entry||token!==epoch)return;
      if(!b){loops.delete(key);return;}
      if(!prefs.sfx||!ready()){loops.delete(key);return;}
      entry.voice=voice(b,entry.volume,true,1,{ambient:key!=='ring'&&key!=='action',action:key==='action',spatial:entry.spatial});
    });
  }
  function stopEffects(){epoch++;for(const v of voices)stopVoice(v,.035);loops.clear();cooldown.clear();actionKey='';emotionCue.until=0;}
  function disposeTrack(t,fade=1.2){
    if(!t||t.retiring)return;t.retiring=true;clearTimeout(t.loadTimer);ramp(t.gain,0,fade);
    t.timer=setTimeout(()=>{t.el.pause();t.el.removeAttribute('src');t.el.load();t.node.disconnect();t.gain.disconnect();tracks.delete(t);},fade*1000+50);
  }
  function stopMusic(){musicKey='';stats.music='';nextMusicRetry=0;retryMusicKey='';currentMusic=requestedMusic=null;for(const t of tracks)disposeTrack(t,.08);}
  function chooseMusic(){
    const place=sim.place,season=SEASON_KEYS[seasonOf(sim.t).i],night=hour()<6||hour()>=18;
    if(place==='park')return 'BGM/park/park-'+season+'.mp3';
    if(place==='mall')return 'BGM/mall/mall-crowd-rush.mp3';
    if(place==='bar')return 'BGM/bar/'+(night?'bar-amber-bass':'bar-daylight-cup')+'.mp3';
    if(place==='beach')return 'BGM/harbor/harbor-mist-return.mp3';
    if(place==='disco')return 'BGM/disco/disco-mirror.mp3';
    return 'BGM/home/'+season+'-'+(night?'night':'day')+'.mp3';
  }
  function updateMusic(){
    if(!prefs.bgm||!ready())return;
    const path=chooseMusic();
    if(path===musicKey&&requestedMusic&&!requestedMusic.retiring)return;
    if(!GAME_AUDIO_FILES.includes(path))return;
    // Leave the old scene now, even when the next file is slow or unavailable.
    // Only scene changes touch these gains; dialogs and effects never duck BGM.
    for(const other of tracks)disposeTrack(other,.18);
    currentMusic=null;stats.music='';
    if(path===retryMusicKey&&now()<nextMusicRetry)return;
    musicKey=path;
    const el=new Audio();el.preload='auto';el.loop=true;
    const gain=ctx.createGain(),node=ctx.createMediaElementSource(el);gain.gain.value=0;node.connect(gain);gain.connect(musicBus);
    const t={el,node,gain,path,retiring:false};tracks.add(t);requestedMusic=t;
    const fail=e=>{
      if(t.retiring||requestedMusic!==t)return;
      report(path,e);musicKey='';retryMusicKey=path;nextMusicRetry=now()+30;
      requestedMusic=null;if(currentMusic===t)currentMusic=null;stats.music='';disposeTrack(t,.05);
    };
    el.addEventListener('error',()=>fail(el.error?.message||'audio loading failed'),{once:true});
    t.loadTimer=setTimeout(()=>fail('audio loading timed out'),12000);
    el.src=url(path);
    el.play().then(()=>{
      clearTimeout(t.loadTimer);
      // Identity matters for rapid A → B → A trips, not just the filename.
      if(!prefs.bgm||!ready()||requestedMusic!==t||chooseMusic()!==path||t.retiring){disposeTrack(t,.05);return;}
      retryMusicKey='';nextMusicRetry=0;currentMusic=t;stats.music=path;ramp(gain,1,.35);
    }).catch(fail);
  }

  function setVolume(channel,value){
    if(!['bgm','sfx'].includes(channel)||!Number.isFinite(value))return;
    prefs[channel+'Volume']=Math.round(Math.max(0,Math.min(100,value)));
    prefs[channel]=prefs[channel+'Volume']>0;
    if(prefs[channel])wake();sync();saveSettings();
  }
  function setEnabled(channel,value){setVolume(channel,value?(prefs[channel+'Volume']||60):0);buildSettings();}
  function sync(){
    if(!ctx)return;
    // A final binary gate makes zero absolute, even with delayed loads or
    // previously scheduled fades. No compressor or event-driven ducking.
    effectsGate.gain.cancelScheduledValues(ctx.currentTime);
    effectsGate.gain.setValueAtTime(prefs.sfx&&!muted?1:0,ctx.currentTime);
    if(!prefs.sfx||muted){effectsBus.gain.cancelScheduledValues(ctx.currentTime);effectsBus.gain.setValueAtTime(0,ctx.currentTime);}
    ramp(musicBus,prefs.bgm&&!muted?prefs.bgmVolume/100*.53:0,.08);if(prefs.sfx&&!muted)ramp(effectsBus,prefs.sfxVolume/100,.05);
    if(!prefs.bgm||muted)stopMusic();if(!prefs.sfx||muted)stopEffects();
    if(ready()){
      if(prefs.sfx)for(const id of ['ui-click','ui-open','ui-close','ui-card','ui-result','ui-message','phone-ring','phone-answer','phone-decline'])buffer(sfx(id));
      if(prefs.sfx){for(const id of new Set(Object.values(RECORDED_FOLEY)))buffer(sfx(id));for(const key of Object.keys(MOOD))buffer(sfx('emotion-'+key));}
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
  const ACTION_LOOP={bath:['water',.24],wash:['water',.20],cook:['cook',.20],laundry:['washer',.35],tv:['tv',.25],pc_video:['tv',.2],dance:['music',.3],cinema:['cinema',.35]};
  const ACTION_REPEAT={computer:['keyboard',3],pc_code:['keyboard',2.3],pc_forum:['keyboard',4],read:['page',12],eat:['cutlery',6],park_eat:['cutlery',6],drink:['drink',9],water:['watering',5],water_living:['watering',5],water_study:['watering',5],music:['music',5]};
  function placeVoice(v,fade=.3){
    const pos=audioSpatial(v.spatial),value=v.volume*pos.gain;
    if(v.target===undefined||Math.abs(value-v.target)>.001){ramp(v.gain,value,fade);v.target=value;}
    v.pan.pan.setTargetAtTime(pos.pan,ctx.currentTime,.12);v.filter.frequency.setTargetAtTime(pos.cutoff,ctx.currentTime,.15);
  }
  function updateSceneMix(){
    const key=sim.place==='home'||atFriendHome()?'home':'outside';
    if(key===sceneMixKey)return;sceneMixKey=key;
    // Stable scene balance: UI stays crisp above quiet household activity.
    // No calls, emotions or dialogs change these levels or the music bus.
    ramp(actionBus,key==='home'?.4:.7,.15);
    ramp(ambientBus,key==='home'?.55:1,.15);
  }
  function ambience(){return Object.fromEntries(Object.entries(audioSceneBeds()).filter(([,v])=>v));}
  function trackEmotion(time){
    const key=asleep()?'asleep':emotion().key;
    if(phoneHolds()&&ready()){stopTag('emotion');emotionCue.until=0;}
    if(emotionCue.current===null||!prefs.sfx||!ready()||friendHousePreview||visitSleepPreview){emotionCue.current=emotionCue.candidate=key;emotionCue.at=time;return;}
    if(key!==emotionCue.candidate){emotionCue.candidate=key;emotionCue.at=time;return;}
    if(phoneHolds()){stopTag('emotion');emotionCue.until=0;return;}
    if(key!==emotionCue.current&&time-emotionCue.at>=.35&&!wiping&&!wardrobeOpen){
      emotionCue.current=key;stopTag('emotion');
      sound('emotion-'+key,key==='asleep'?.30:.45,{tag:'emotion',gap:0,valid:()=>!phoneHolds()&&(asleep()?'asleep':emotion().key)===key});
    }
  }
  function tick(force=false){
    const time=now();if(!force&&time-lastTick<.10)return;lastTick=time;trackEmotion(time);
    if(!ready())return;updateMusic();updateSceneMix();if(!prefs.sfx)return;
    if(weather.kind==='storm'&&stormExposed())buffer(sfx('thunder-heavy-no-rain-cc0'));
    const desired=ambience(),act=activity(),playing=speed>0&&!cardHolds()&&!wiping;
    if(phoneCall.phase==='ringing')desired.ring=['phone-ring',.30];
    if((playing||act==='tv')&&ACTION_LOOP[act])desired.action=[...(act==='tv'?audioTvBed():ACTION_LOOP[act]),audioActionSource()];
    for(const [key,[id,volume,spatial]]of Object.entries(desired))setLoop(key,id,volume,spatial);
    for(const [key,entry]of loops)if(!desired[key]){loops.delete(key);stopVoice(entry.voice,key==='ring'?.025:.45);}
    // Keep state current while paused so opening a dialog doesn't restart Foley.
    const key=sim.place+':'+act;
    if(playing&&key!==actionKey){
      const old=actionKey.split(':').at(-1);
      if((old==='toilet'||old==='park_toilet')&&previousPlace===sim.place)sound('flush',.12,{gap:3});
      if(ACTION_SOUND[act])sound(ACTION_SOUND[act],.35,{vary:true,spatial:audioActionSource(),valid:()=>activity()===act});
      actionKey=key;nextFoley=time+3;
    }
    previousPlace=sim.place;
    if(playing&&time>=nextAccent){
      nextAccent=time+30+Math.random()*30;audioSceneAccent();
      if(sim.place==='front'&&weather.kind==='clear'&&hour()>=7&&hour()<20)sound('cat-meow-cc0',.15,{gap:30});
      else if((sim.place==='bar'&&!sim.bar?.toilet||sim.place==='mall'&&!mallInside())&&life.npcs?.length>1)sound('crowd-small-laugh-cc0',.12,{gap:30});
    }
    if(playing&&ACTION_REPEAT[act]&&time>=nextFoley){const [id,interval]=ACTION_REPEAT[act];sound(id,.25,{vary:true,spatial:audioActionSource(),valid:()=>activity()===act});nextFoley=time+interval+Math.random()*2;}
  }
  // Observe logical expansion, not every animation frame. One opening gets one
  // sound; filling a list or moving the pointer inside an open panel is silent.
  function installUI(){
    const hiddenIds=['picker','card','cardRes','ring','diaryPop','moodTip','skyTip','studio','guide','update','petPanel','petMini','petHud'];
    const roots=hiddenIds.map(id=>({el:document.getElementById(id),active:el=>!el.hidden}));
    for(const id of ['needs','setGear','networkTrigger'])roots.push({el:document.getElementById(id),active:el=>el.getAttribute('aria-expanded')==='true'});
    for(const id of ['contactsPanel','contactActions'])roots.push({el:document.getElementById(id),active:el=>el.getAttribute('aria-hidden')==='false'});
    roots.push({el:socialSheet,active:el=>!el.hidden},{el:moodrow,active:el=>el.classList.contains('network-ready')});
    for(const entry of roots){if(!entry.el)continue;entry.was=entry.active(entry.el);}
    const observer=new MutationObserver(records=>{
      const changed=new Set(records.map(r=>r.target));let opening=null,closing=false;
      for(const entry of roots){if(!changed.has(entry.el))continue;const active=entry.active(entry.el);if(active!==entry.was){entry.was=active;if(active)opening=entry.el.id||'panel';else closing=true;}}
      if(opening)sound(opening==='card'?'ui-card':opening==='cardRes'?'ui-result':'ui-open',.65,{tag:'ui-panel',gap:.1});
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
  function thunder(){if(stormExposed()){const exposed=stormOutside(),w=audioWindowExposure();sound('thunder-heavy-no-rain-cc0',exposed?.40:.30*w.gain,{gap:2,maxAge:1.5,spatial:{cutoff:exposed?16000:w.cutoff},ambient:true});}}
  function phoneEnd(accepted){const ring=loops.get('ring');if(ring){loops.delete('ring');stopVoice(ring.voice,.015);}sound(accepted?'phone-answer':'phone-decline',.35);}
  function outputLevel(node=meter){if(!node)return 0;const a=new Float32Array(512);node.getFloatTimeDomainData(a);return Math.sqrt(a.reduce((sum,v)=>sum+v*v,0)/a.length);}
  function resetEmotion(){stopTag('emotion');emotionCue.current=emotionCue.candidate=null;emotionCue.until=0;}
  installUI();
  return {setVolume,setEnabled,resetEmotion,wake,sync,tick,sound,thunder,phoneEnd,activity,ambience,chooseMusic,
    debug:()=>({unlocked,level:outputLevel(),effectsLevel:outputLevel(effectsMeter),effectsGate:effectsGate?.gain.value||0,state:ctx?.state||'locked',music:stats.music,desiredMusic:chooseMusic(),pendingMusic:requestedMusic&&!requestedMusic.retiring&&currentMusic!==requestedMusic?requestedMusic.path:'',musicTracks:[...tracks].map(t=>({path:t.path,retiring:t.retiring,paused:t.el.paused,gain:t.gain.gain.value})),loops:[...loops.keys()],voices:voices.size,tracks:tracks.size,cache:cache.size,musicTime:currentMusic?.el.currentTime||0,musicRate:currentMusic?.el.playbackRate||1,musicPath:"independent",musicTrackGain:currentMusic?.gain.gain.value||0,musicVolume:musicBus?.gain.value||0,effectsVolume:effectsBus?.gain.value||0,actionVolume:actionBus?.gain.value||0,ambientVolume:ambientBus?.gain.value||0,loopPaths:[...loops.values()].map(e=>e.path),focus:audioFocus(),emotion:emotionCue.current,emotionVoices:[...voices].filter(v=>v.tag==='emotion'&&!v.stopped).length,loopDetails:[...loops.entries()].map(([key,e])=>({key,path:e.path,volume:e.volume,spatial:e.spatial,filter:e.voice?.filter.frequency.value,pan:e.voice?.pan.pan.value})),stats:JSON.parse(JSON.stringify(stats))})};
})();
