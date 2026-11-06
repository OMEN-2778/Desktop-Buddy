// 草帽湾, part 2 (owner 2026-11-05: "do all the rest"), test page only. Built on summerLife (summer_life.js hooks).
//   1. Underwater camera + 图鉴: click a creature while diving, she swims over and takes a photo (flash, photo card).
//      Four pages (浅滩 / 珊瑚花园 / 沉船与拱门 / 深沟) + 地点 (the old hotspots); rare ones need a moment: night
//      (发光水母, 萤光虾), rain (雨中的蝠鲼), the trench (灯笼鱼, 深海章鱼), calendar autumn (座头鲸). A full page gives
//      a mood and 3 coins. Opened from her ring: 草帽湾图鉴. Photos are tiny PNGs kept in the save (F.bay.album).
//   2. Beach life: sun loungers (energy, sunburn after long noon sun), the open-air shower (hygiene), the evening
//      bonfire (social), surfing (falls first, stands from the third time), sand castles (washed away at high tide),
//      night dives in a glowing sea.
//   3. Ten commissions (委托): each person shows up on some days only; once taken, they are there every day.
//   4. Island festivals: five of its own (3 in calendar summer, 2 in calendar autumn (the bay is only reachable in summer and autumn), never on a city festival day).
//      On the island city festivals neither apply nor show; the festival bar shows the island's.
// Everything lasting lives in F.bay (save rule).
(function(){
 const L=window.summerLife;if(!L)return;
 const {hooks,say,ask,walk,scene,speakBay,drawPerson,person,pose,ML_,hour,night,today,under,inBay,inMarket,C,S,X,img,fitBig,scrollBar}=L;
 const el=FarmUI.el,WL=116,SURF=WL+12;
 const rain=()=>typeof weather!=='undefined'&&weather.kind!=='clear';
 const cal=()=>seasonOf(sim.t);
 const need=(k,v)=>{if(sim.needs[k]!=null)sim.needs[k]=Math.max(0,Math.min(100,sim.needs[k]+v));};
 const M=()=>{const b=L.B();b.dex??={};b.album??={};b.pages??={};b.act??={};b.cq??={};b.fest??={};return b;};
 const once=(key)=>{const b=M();b.act.once??={};const k=key+'@'+today();if(b.act.once[k])return false;b.act.once[k]=1;
  for(const o of Object.keys(b.act.once))if(+o.split('@')[1]<today()-2)delete b.act.once[o];return true;};
 const coins=(v,text)=>X.record('coin',text,v);
 const swim=()=>C().state.suit&&C().state.suit!=='clothes';
 const toast=t=>C().toast?.(t);
 const MOOD={snap:ML_('snap','第一张照片','happy'),page:ML_('page','图鉴集满一页','confident',3),sun:ML_('sun','晒得暖洋洋','happy',1),burn:ML_('burn','晒红了','embarrassed',1),
  shower:ML_('shower','冲掉一身海盐','happy',1),fire:ML_('fire','篝火旁的晚上','happy',2),surf_fall:ML_('surf_fall','喝了一大口海水','embarrassed',1),surf_up:ML_('surf_up','站上浪了！','confident',3),
  castle:ML_('castle','沙堡','happy',1),glow:ML_('glow','荧光海','dazed',3),quest:ML_('quest','帮上忙了','happy',2),letter:ML_('letter','四十年前的信','sad',2),
  fest:ML_('fest','草帽湾过节','happy',3),lantern:ML_('lantern','一盏椰灯','dazed',2),whale:ML_('whale','鲸歌','dazed',3),wave:ML_('wave','冲浪日','confident',2)};
 const mood=(id)=>{try{addMood(id);}catch(e){}};

 // ================================================================ 1. camera + 图鉴
 const NAMES={turtle:'绿海龟',manta:'蝠鲼',jelly:'小水母',eagleray:'斑点鹞鲼',school:'银色鱼群',tang:'刺尾鲷',butterflyfish:'蝴蝶鱼',shark:'白鳍礁鲨',grouper:'大石斑鱼',ulua:'浪人鲹'};
 const RARE={glow_jelly:['发光水母','夜里才有','一碰就亮的水母，像一盏会游泳的小灯。'],glow_shrimp:['萤光虾','夜里才有','一群小虾在珊瑚里一闪一闪，像有人撒了把星星。'],
  rain_manta:['雨中的蝠鲼','下雨天才有','雨点打在海面上，蝠鲼在下面慢慢翻了个身。'],lanternfish:['灯笼鱼','只在最深的海沟','头顶挂着小灯的鱼，在漆黑的海沟里一晃一晃。'],
  deep_octopus:['深海章鱼','只在最深的海沟','红色的章鱼缩在石缝里，八条腿慢慢地卷。'],humpback:['座头鲸','秋天才会远远游过','远处的海面喷出一道水柱，巨大的尾巴抬起来又落下。']};
 // 图鉴 second batch (owner 2026-11-05): 33 more, only at some times. When text shows on the empty card.
 const WHEN2={day:'白天',night:'夜里才有',rain:'下雨天才有',dawn:'清晨才有',dusk:'傍晚才有',rare:'偶尔出现',vrare:'极其罕见'};
 const NEW2=k=>(C()?.data?.life||[]).find(c=>c.k===k)?.when;
 const nameK=k=>RARE[k]?.[0]||NAMES[k]||((C().lifeText?.[k]||'').match(/遇到了(.+?)，/)||[])[1]||k;
 const lineK=k=>RARE[k]?.[2]||C().lifeText?.[k]||'';
 const PAGES=[['浅滩',['turtle','jelly','school','clownfish','yellow_tang','anthias','convict','bait_ball','eagleray','glow_jelly','glow_shrimp']],
  ['珊瑚花园',['butterflyfish','tang','regal_tang','flame_angel','moorish_idol','lionfish','boxfish','triggerfish']],
  ['沉船与拱门',['manta','rain_manta','ulua','bluestripe','grouper','shark','pufferfish','saddle_wrasse']],
  ['深沟',['parrotfish','barracuda','trevally','lanternfish','deep_octopus','humpback']]];
 // the batch-2 species join their pages (reef2.py SPECIES: page index) and swim only at their times
 (function addBatch2(){const life=C()?.data?.life;if(!life){setTimeout(addBatch2,300);return;}const seen=new Set();
  for(const c of life)if(c.when&&!seen.has(c.k)){seen.add(c.k);const pg=PAGES[c.page??0]||PAGES[0];if(!pg[1].includes(c.k))pg[1].push(c.k);}})();
 const roll=(k,p)=>{let h=Math.imul(today()+7,2654435761)^[...k].reduce((a,ch)=>Math.imul(a,31)+ch.charCodeAt(0)|0,11);h=Math.imul(h^h>>>15,2246822507)>>>0;return h%1000<p*1000;};
 globalThis.summerLifeOn=(w,k)=>{const h=hour();
  if(w==='day')return h>=6&&h<19;if(w==='night')return h>=19||h<5;if(w==='rain')return rain();
  if(w==='dawn')return h>=5&&h<8;if(w==='dusk')return h>=17&&h<20;
  if(w==='rare')return roll(k,.25);if(w==='vrare')return roll(k,.06)&&(h<6||h>=16);return true;};
 const photoHooks=[];
 function crop(cx,cy){try{const c=C(),v=document.getElementById('view'),k=v.width/342,ky=v.height/c.canvas.height,s=c.state,cv=document.createElement('canvas');cv.width=60;cv.height=42;   // what is on screen right now
  const g=cv.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(v,(cx-(s.camX||0)-30)*k,(cy-(s.camY||0)-21)*ky,60*k,42*ky,0,0,60,42);return cv.toDataURL('image/png');}catch(e){return '';}}
 function flash(){const v=document.getElementById('view');const f=el('div','bay-flash');f.style.cssText=`left:${v.offsetLeft}px;top:${v.offsetTop}px;width:${v.offsetWidth}px;height:${v.offsetHeight}px`;v.parentElement.append(f);setTimeout(()=>f.remove(),500);}
 let cardT=0;
 function card(k,shot,first,n){document.querySelector('.bay-photo')?.remove();const v=document.getElementById('view'),c=el('button','bay-photo');c.type='button';
  const im=new Image();im.src=shot;c.append(im,el('b',null,(first?'新发现 · ':'')+nameK(k)),el('small',null,first?lineK(k):`拍了第 ${n} 张`));c.onclick=()=>{c.remove();openDex(pageOf(k));};
  c.style.left=(v.offsetLeft+v.offsetWidth-196)+'px';c.style.top=(v.offsetTop+v.offsetHeight-118)+'px';v.parentElement.append(c);clearTimeout(cardT);cardT=setTimeout(()=>c.remove(),4200);}
 const pageOf=k=>Math.max(0,PAGES.findIndex(p=>p[1].includes(k)));
 function snap(k,cx,cy){const b=M();flash();const shot=crop(cx,cy),first=!b.dex[k];b.dex[k]=(b.dex[k]||0)+1;if(first||!b.album[k])b.album[k]=shot;
  card(k,shot,first,b.dex[k]);
  if(first){if(Object.keys(b.dex).length===1)mood(MOOD.snap);log(`在海里拍到了${nameK(k)}，记进了图鉴。`);}
  for(const [i,[name,ks]]of PAGES.entries())if(!b.pages[i]&&ks.every(x=>b.dex[x])){b.pages[i]=1;mood(MOOD.page);coins(3,`图鉴「${name}」集满了`);setTimeout(()=>showHint(`图鉴「${name}」集满了！奖励 3 丢丢币`),1500);}
  for(const f of photoHooks)try{f(k);}catch(e){}}
 (function hook(){const c=C();if(c?.setPhoto){c.setPhoto(o=>{const k=o.k==='manta'&&rain()?'rain_manta':o.k;if(k==='rain_manta'&&!M().dex.manta)M().dex.manta=1;snap(k,o.cx,o.cy);});return;}setTimeout(hook,300);})();
 // the rare ones the base sea doesn't have: drawn here, clicked here
 const RARE_AT={glow_jelly:[[1330,172],[1490,192],[1705,160]],glow_shrimp:[[1420,252],[2120,330]],lanternfish:[[2870,722],[2955,758],[3045,736]],deep_octopus:[[2992,792]]};
 const rareOn=k=>k.startsWith('glow')?night():k==='humpback'?cal().i===2||fest()?.n==='鲸歌节':true;
 function rarePos(k,i,t){const [x,y]=RARE_AT[k][i];return k==='lanternfish'?[x+Math.sin(t*.5+i)*14,y+Math.sin(t*.8+i*2)*5]:k==='glow_jelly'?[x+Math.sin(t*.3+i)*6,y+Math.sin(t*.9+i)*7]:[x,y];}
 function whalePos(t){const p=(t/90)%1;return [1300+p*2600,WL+1];}
 function drawRare(ctx,t){const gl=G(ctx);
  if(night()){for(let i=0;i<3;i++){const [x,y]=rarePos('glow_jelly',i,t);const a=.35+.25*Math.sin(t*2+i);gl.fillStyle=`rgba(120,255,240,${a*.35})`;gl.fillRect(x-6,y-6,13,12);
    gl.fillStyle='#bafff4';gl.fillRect(x-3,y-3,7,3);gl.fillRect(x-2,y-4,5,1);gl.fillStyle='#7ff0e0';for(let k=0;k<3;k++)gl.fillRect(x-2+k*2,y,1,3+((t*3+k)|0)%2);}
   for(let i=0;i<2;i++){const [x,y]=RARE_AT.glow_shrimp[i];for(let k=0;k<7;k++){if(Math.sin(t*4+k*1.7+i)>.2){gl.fillStyle='#d6ffb0';gl.fillRect(x+(k*5%13)-6,y+(k*3%7)-3,1,1);}}}}
  for(let i=0;i<3;i++){const [x,y]=rarePos('lanternfish',i,t),d=Math.cos(t*.5+i)>0?1:-1;ctx.fillStyle='#2a2140';ctx.fillRect(x-3,y-1,6,3);ctx.fillRect(x-3*d-1*d,y,1,1);ctx.fillStyle='#4a3a66';ctx.fillRect(x-2,y-1,4,1);
   ctx.fillStyle='#3a2a52';ctx.fillRect(x+2*d,y-3,1,2);gl.fillStyle=`rgba(255,230,120,${.6+.4*Math.sin(t*3+i)})`;gl.fillRect(x+3*d,y-4,2,2);gl.fillStyle='rgba(255,230,120,.18)';gl.fillRect(x+3*d-3,y-7,8,8);}
  {const [x,y]=RARE_AT.deep_octopus[0];ctx.fillStyle='#8a2f2f';ctx.fillRect(x-4,y-6,8,5);ctx.fillStyle='#b4483a';ctx.fillRect(x-3,y-7,6,2);ctx.fillStyle='#fff';ctx.fillRect(x-2,y-4,1,1);ctx.fillRect(x+1,y-4,1,1);
   ctx.fillStyle='#8a2f2f';for(let k=0;k<4;k++)ctx.fillRect(x-4+k*2+Math.round(Math.sin(t*1.5+k)),y-1,1,3);}
  if(rareOn('humpback')){const [x,y]=whalePos(t),ph=(t%12)/12;ctx.fillStyle='#3c4a63';ctx.fillRect(x-14,y-2,28,3);ctx.fillRect(x-10,y-3,18,1);ctx.fillStyle='#53627e';ctx.fillRect(x-12,y-2,20,1);
   if(ph<.25){ctx.fillStyle='rgba(235,248,255,.9)';const hgt=Math.round(10*Math.sin(ph/.25*Math.PI));ctx.fillRect(x+6,y-3-hgt,1,hgt);ctx.fillRect(x+4,y-3-hgt,5,1);}
   if(ph>.6&&ph<.8){ctx.fillStyle='#3c4a63';ctx.fillRect(x-20,y-7,2,5);ctx.fillRect(x-24,y-8,10,2);}}}
 function rareHit(x,y,t){
  if(night())for(let i=0;i<3;i++){const [rx,ry]=rarePos('glow_jelly',i,t);if(Math.hypot(x-rx,y-ry)<9)return ['glow_jelly',rx,ry];}
  if(night())for(let i=0;i<2;i++){const [rx,ry]=RARE_AT.glow_shrimp[i];if(Math.hypot(x-rx,y-ry)<9)return ['glow_shrimp',rx,ry];}
  for(let i=0;i<3;i++){const [rx,ry]=rarePos('lanternfish',i,t);if(Math.hypot(x-rx,y-ry)<8)return ['lanternfish',rx,ry];}
  {const [rx,ry]=RARE_AT.deep_octopus[0];if(Math.hypot(x-rx,y-ry+3)<9)return ['deep_octopus',rx,ry-3];}
  if(rareOn('humpback')){const [rx,ry]=whalePos(t);if(Math.abs(x-rx)<20&&Math.abs(y-ry)<10)return ['humpback',rx,ry];}
  return null;}
 hooks.click.push((x,y)=>{const t=C().state.time||realClock,h=rareHit(x,y,t);if(!h)return false;const [k]=h;
  if(k==='humpback'){walk(Math.min(1015,C().state.x+200)).then(()=>{const [wx,wy]=whalePos(C().state.time||realClock);snap(k,wx,wy);});return true;}
  if(!swim()){toast('那是'+nameK(k)+'，换上泳装才能游过去拍。');return true;}
  C().goTo(h[1],'dive',h[2]+8,()=>{const [k2,rx,ry]=rareHit(C().state.x,C().state.y-8,C().state.time||realClock)||h;snap(k2,rx,ry);});return true;});

 function openDex(page=0){const b=M(),s=FarmUI.sheet('草帽湾图鉴','fu-stall');s.classList.add('fu-big-sheet','bay-dex');const c=socialContent(s);
  const tabs=el('div','dex-tabs'),body=el('div','dex-body');
  const total=PAGES.reduce((a,p)=>a+p[1].length,0),got=PAGES.reduce((a,p)=>a+p[1].filter(k=>b.dex[k]).length,0);
  const names=[...PAGES.map(p=>p[0]),'地点'];
  const show=i=>{[...tabs.children].forEach((x,j)=>x.classList.toggle('on',j===i));body.replaceChildren();
   if(i<PAGES.length){const [name,ks]=PAGES[i],n=ks.filter(k=>b.dex[k]).length;body.append(el('p','dex-sum',`${name} · 拍到 ${n}/${ks.length}${b.pages[i]?' · 已集满 ✦':' · 集满奖励 3 丢丢币'}`));
    const g=el('div','dex-grid');for(const k of ks){const t=el('div','dex-tile'+(b.dex[k]?'':' dex-no'));
     if(b.dex[k]&&b.album[k]){const im=new Image();im.src=b.album[k];t.append(im);}else t.append(el('span','dex-q','?'));
     t.append(el('b',null,b.dex[k]?nameK(k):'？？？'),el('small',null,b.dex[k]?`拍了 ${b.dex[k]} 张`:(RARE[k]?.[1]||WHEN2[NEW2(k)]||'在这片海里')));if(b.dex[k])t.title=lineK(k);g.append(t);}body.append(g);}
   else{const hs=C().hotspots||[],found=C().state.found||new Set(),n=hs.filter(h=>found.has(h.id)).length;body.append(el('p','dex-sum',`地点 · 去过 ${n}/${hs.length}`));
    const g=el('div','dex-grid dex-places');for(const h of hs){const ok=found.has(h.id),t=el('div','dex-tile dex-place'+(ok?'':' dex-no'));t.append(el('b',null,ok?h.name:'？？？'),el('small',null,ok?h.text:'还没去过'));g.append(t);}body.append(g);}
   body.scrollTop=0;};
  names.forEach((n,i)=>{const t=el('button','dex-tab',n);t.type='button';t.onclick=()=>show(i);tabs.append(t);});
  c.append(el('p','dex-head',`已经拍到 ${got}/${total} 种`),tabs,body);show(page);requestAnimationFrame(()=>{fitBig(s);scrollBar(s,c);});}
 const oldOpen=openRing;openRing=function(which,at){
  if(which==='away'&&inBay()){const keep=RINGS.away;RINGS.away=[keep[0],['bay:dex','草帽湾图鉴'],...keep.slice(1)];try{return oldOpen(which,at);}finally{RINGS.away=keep;}}
  return oldOpen(which,at);};
 const oldPick=ringPick;ringPick=function(id){if(id==='bay:dex'){closeRing();openDex();return;}return oldPick(id);};

 // ---- night (the summer map had no night at all): a blue multiply pass over the frame, then a glow layer on top
 //      (bonfire, glowing sea, glow jellies, lanterns) so lights really shine in the dark
 const glowC=document.createElement('canvas');let glowUsed=false;
 function dark(){const h=hour();return h>=20.5||h<4.5?1:h>=18&&h<20.5?(h-18)/2.5:h>=4.5&&h<6.5?1-(h-4.5)/2:0;}
 function G(ctx){if(dark()<.12)return ctx;if(glowC.width!==ctx.canvas.width||glowC.height!==ctx.canvas.height){glowC.width=ctx.canvas.width;glowC.height=ctx.canvas.height;}
  const g=glowC.getContext('2d');if(!glowUsed){g.setTransform(1,0,0,1,0,0);g.clearRect(0,0,glowC.width,glowC.height);glowUsed=true;}g.setTransform(ctx.getTransform());g.imageSmoothingEnabled=false;return g;}
 function nightPass(v,W,H){const a=dark()*(rain()?.9:.82);if(a>0){v.save();v.globalCompositeOperation='multiply';v.fillStyle=`rgb(${255-a*190|0},${255-a*170|0},${255-a*100|0})`;v.fillRect(0,0,W,H);v.restore();}
  if(glowUsed){v.save();v.imageSmoothingEnabled=false;v.drawImage(glowC,0,0,W,H);v.restore();glowUsed=false;}}
 // ================================================================ 2. beach life
 const SHOWER_X=650,FIRE_X=830,RACK_X=1010,CASTLE_X=784;   // castle bucket at 800, clear of the fire
 const fireOn=()=>{const h=hour();return (h>=18.5||h<0.5)&&!rain();};
 let lastT=0,showerUntil=0,surfFx=null,trail=[],castleFx=0;
 hooks.tick.push(dt=>{if(!inBay())return;const s=C().state,b=M(),gm=lastT?Math.max(0,Math.min(30,sim.t-lastT)):0;lastT=sim.t;
  if(s.lying!=null&&!night()&&!rain()){need('energy',gm*.12);need('fun',gm*.04);b.act.sunMin=(b.act.sunDay===today()?b.act.sunMin||0:0)+gm;b.act.sunDay=today();
   if(b.act.sunMin>20&&once('sun'))mood(MOOD.sun);
   if(b.act.sunMin>90&&hour()>=11&&hour()<15&&once('burn')){mood(MOOD.burn);speakBay('嘶……好像晒红了');}}
  if(night()&&under()){if(Math.random()<.6)trail.push({x:s.x+(Math.random()-.5)*10,y:s.y-8+(Math.random()-.5)*10,a:1});if(once('glowsea')&&!b.act.glowSeen){b.act.glowSeen=1;mood(MOOD.glow);log('夜里下海，海水一碰就发出蓝光。');setTimeout(()=>speakBay('海……在发光！'),400);}}
  for(const p of trail)p.a-=dt*.8;trail=trail.filter(p=>p.a>0).slice(-80);});
 function drawBeach(ctx,info){const c=C(),s=c.state,t=s.time||realClock,b=M(),g=x=>c.gr(x);
  // shower: a pole, a head, a little tiled tray
  {const x=SHOWER_X,y=g(x);ctx.fillStyle='#8f969e';ctx.fillRect(x,y-30,2,30);ctx.fillRect(x,y-31,8,2);ctx.fillStyle='#c7ccd2';ctx.fillRect(x+1,y-30,1,29);ctx.fillStyle='#6b7178';ctx.fillRect(x+6,y-29,4,2);
   ctx.fillStyle='#d9d3c7';ctx.fillRect(x-3,y-1,16,2);ctx.fillStyle='#b9b2a5';ctx.fillRect(x-3,y,16,1);
   if(realClock<showerUntil){ctx.fillStyle='rgba(170,220,255,.85)';for(let k=0;k<12;k++){const yy=(t*60+k*7)%26;ctx.fillRect(x+6+(k%4),y-27+yy,1,2);}}}
  // bonfire, evenings
  {const x=FIRE_X,y=g(x);ctx.fillStyle='#6e4a2c';ctx.fillRect(x-6,y-2,12,2);ctx.fillStyle='#8c6238';ctx.fillRect(x-5,y-3,4,1);ctx.fillRect(x+1,y-3,4,1);
   ctx.fillStyle='#7a7266';for(let k=-7;k<=7;k+=3)ctx.fillRect(x+k,y-1,2,2);
   if(fireOn()){const gl=G(ctx);gl.fillStyle=`rgba(255,170,80,${.1+dark()*.12})`;gl.fillRect(x-30,y-34,60,36);gl.fillStyle='rgba(255,190,90,.14)';gl.fillRect(x-18,y-22,36,24);gl.fillStyle='rgba(255,200,110,.12)';gl.fillRect(x-10,y-14,20,16);
    for(let k=0;k<6;k++){const hgt=6+((Math.sin(t*9+k*2)+1)*3)|0,xx=x-4+k*1.6|0;gl.fillStyle=k%2?'#ffb43a':'#ff7b2e';gl.fillRect(xx,y-2-hgt,2,hgt);gl.fillStyle='#ffe28a';gl.fillRect(xx,y-3-Math.max(1,hgt/3|0),1,Math.max(1,hgt/3|0));}
    for(let k=0;k<4;k++){const p=(t*.7+k*.25)%1;gl.fillStyle=`rgba(255,220,140,${1-p})`;gl.fillRect(x-2+Math.sin(t*3+k)*4|0,y-12-p*26|0,1,1);}
    drawPerson(ctx,BON[0],x-18,g(x-18));drawPerson(ctx,BON[1],x+18,g(x+18));}}
  // surfboards leaning on a rack by the water
  {const x=RACK_X,y=g(x);ctx.fillStyle='#7a5636';ctx.fillRect(x-1,y-14,1,14);ctx.fillRect(x+9,y-14,1,14);ctx.fillRect(x-1,y-13,11,1);
   for(const [ox,c1,c2]of [[0,'#f2d36b','#e35b4f'],[4,'#7fc4e8','#ffffff']]){ctx.fillStyle=c1;ctx.fillRect(x+ox,y-22,3,22);ctx.fillStyle=c2;ctx.fillRect(x+ox+1,y-20,1,18);}}
  // the sand castle, until the tide takes it
  if(b.castle&&sim.t<b.castle.wash){const x=b.castle.x,y=g(x),big=b.castle.big?1:0;ctx.fillStyle='#d9b77e';ctx.fillRect(x-7-big*2,y-5,14+big*4,5);ctx.fillRect(x-6-big*2,y-10-big*2,4,6+big*2);ctx.fillRect(x+2+big*2,y-10-big*2,4,6+big*2);ctx.fillRect(x-2,y-13-big*3,4,9+big*3);
   ctx.fillStyle='#ecd5a0';ctx.fillRect(x-6-big*2,y-10-big*2,1,6);ctx.fillRect(x-2,y-13-big*3,1,9);ctx.fillStyle='#b8925c';ctx.fillRect(x-1,y-3,2,3);ctx.fillStyle='#e35b4f';ctx.fillRect(x,y-18-big*3,1,5);ctx.fillRect(x+1,y-18-big*3,3,2);}
  {const x=CASTLE_X+16,y=g(x);ctx.fillStyle='#e35b4f';ctx.fillRect(x-2,y-5,5,5);ctx.fillStyle='#b9473d';ctx.fillRect(x-2,y-5,5,1);ctx.fillStyle='#8c6238';ctx.fillRect(x+4,y-8,1,8);ctx.fillStyle='#9aa3ad';ctx.fillRect(x+3,y-9,3,2);}
  if(realClock<castleFx){ctx.fillStyle='#e8cf98';for(let k=0;k<6;k++)ctx.fillRect(CASTLE_X-8+((t*40+k*5)%16|0),g(CASTLE_X)-4-((t*30+k*3)%8|0),1,1);}
  // the surf ride
  // owner 2026-11-06: the swimming pose standing on the board; soles, board and the water surface on one line
  if(surfFx){const p=(realClock-surfFx.t0)/surfFx.dur,x=Math.round(s.x),fell=surfFx.fall&&p>.6,bob=Math.round(Math.sin(p*9)),top=WL-2+bob;
   window.__surfHero=fell?null:(window.__surfHero||{});
   if(!fell){ctx.fillStyle='#e35b4f';ctx.fillRect(x-10,top,20,1);ctx.fillStyle='#f2d36b';ctx.fillRect(x-11,top+1,22,1);ctx.fillRect(x+10*(s.facing||1),top,1,1);   // the board, its top at the waterline
    const a=window.__surfHero.args;if(a)seasonMapTest.state.summer.fx.swimmer(ctx,{head:a.dc,skinRamp:a.skin,sheet:a.sheet,x,y:top,time:s.time,facing:s.facing,diving:false,moving:true,waterline:WL});}
   ctx.fillStyle='rgba(255,255,255,.85)';for(let k=0;k<10;k++)ctx.fillRect(x-12-k*2*(s.facing||1),WL-Math.round(3*Math.abs(Math.sin(k/3+p*6))),2,1);   // spray behind the board
   if(fell){ctx.fillStyle='rgba(235,250,255,.9)';for(let k=0;k<8;k++)ctx.fillRect(x-6+k*2,WL-4-((k*7+p*30)%9|0),1,2);}}
  else if(window.__surfHero)window.__surfHero=null;
  // glowing sea at night
  if(night()){const gl=G(ctx);for(const p of trail){gl.fillStyle=`rgba(110,255,230,${p.a*.9})`;gl.fillRect(p.x|0,p.y|0,1,1);}
   for(let k=0;k<26;k++){const x=1030+((k*97)%900),on=Math.sin(t*2.2+k*1.3)>.5;if(on){gl.fillStyle='rgba(120,255,235,.7)';gl.fillRect(x+((t*4+k)%6|0),WL+1+(k%3),2,1);}}}
  drawRare(ctx,t);}
 const BON=[person('篝火边的游客','f',1201),person('篝火边的大叔','m',1303)];
 hooks.draw.push(drawBeach);
 const near=(x,X,w=12)=>Math.abs(x-X)<w;
 hooks.click.push((x,y)=>{const c=C(),g=c.gr(x),busy=L.isBusy();if(busy||y>g+6||y<g-40)return false;
  if(near(x,SHOWER_X+4,10)){scene(async()=>{await walk(SHOWER_X+6);showerUntil=realClock+3.5;need('hygiene',45);speakBay(swim()?'冲掉一身海盐，清清爽爽':'凉水一冲，人都精神了');if(once('shower'))mood(MOOD.shower);await new Promise(r=>setTimeout(r,3200));});return true;}
  if(near(x,FIRE_X,12)){if(!fireOn()){toast(rain()?'下雨了，今晚不生火。':'太阳落山以后，这里会点起篝火。');return true;}
   scene(async()=>{await walk(FIRE_X-6);await say(BON[0].name,['晚上好呀！坐过来烤烤火，海风有点凉。','来来，坐。今晚有人要弹琴。','火边的位置给你留着呢。'][today()%3]);
    await say(nameOf(),['好暖和……','听着海浪声烤火，太舒服了。','来了来了～'][today()%3]);need('social',30);need('fun',12);if(once('fire'))mood(MOOD.fire);});return true;}
  if(near(x,RACK_X+4,10)){surf();return true;}
  if(near(x,CASTLE_X+16,8)||(M().castle&&sim.t<M().castle.wash&&near(x,M().castle.x,9))){buildCastle(false);return true;}
  return false;});
 function surf(){if(!swim()){toast('先去更衣室换上泳装，才能下水冲浪。');return;}
  scene(async()=>{const b=M(),lesson=cqOn('surf')&&present('surf');await walk(RACK_X);C().goTo(1095,'dive',SURF-2);await new Promise(r=>setTimeout(r,2600));
   const sk=b.act.surf||0,ok=sk>=2||(lesson&&b.cq.surf.lessons>=2);surfFx={t0:realClock,dur:3.4,fall:!ok};C().goTo(1036,'dive',SURF-2);await new Promise(r=>setTimeout(r,3400));surfFx=null;
   b.act.surf=sk+1;if(lesson){b.cq.surf.lessons=(b.cq.surf.lessons||0)+1;}
   if(ok){mood(MOOD.surf_up);speakBay(sk>=4?'这道浪刚刚好～':'站起来了！我站起来了！');if(sk<3)log('第一次在浪上站了起来。');}
   else{mood(MOOD.surf_fall);speakBay(['扑通——喝了一大口海水','又摔了……再来！','差一点点就站起来了'][Math.min(2,sk)]);}});}
 function nextTide(t){const d=Math.floor(t/1440)*1440;for(const m of [6*60,17*60,1440+6*60])if(d+m>t)return d+m;return d+1440+6*60;}
 function buildCastle(withKid){const b=M();if(b.castle&&sim.t<b.castle.wash&&!withKid){toast('沙堡还立着呢，等涨潮再堆新的。');return Promise.resolve();}
  return scene(async()=>{await walk(CASTLE_X-10);castleFx=realClock+3;speakBay(withKid?'看谁堆得高！':'堆个沙堡～');await new Promise(r=>setTimeout(r,3000));
   b.castle={x:CASTLE_X,wash:nextTide(sim.t),big:withKid?1:0,day:today()};need('fun',15);if(once('castle'))mood(MOOD.castle);speakBay('涨潮之前，它都会一直在这儿。');});}

 // ================================================================ 3. commissions (委托)
 const NPC={hai:person('救生员阿海','m',1409),mai:person('冲浪教练小麦','f',1511),noa:person('潜水教练诺亚','m',1613),mom:person('带孩子的妈妈','f',1709),
  le:person('阿乐','m',1801),art:person('画画的姐姐','f',1907),inn:person('旅舍老板','m',2003),sci:person('海洋研究员','f',2111)};
 const Q={
  whistle:{who:'hai',x:960,title:'丢了的哨子',off:0},
  surf:{who:'mai',x:990,title:'第一次站上板',off:1},
  coco:{who:'cafe',market:true,title:'椰子不够了',off:2},
  turtle:{who:'noa',x:575,title:'看见海龟了吗',off:0},
  bucket:{who:'mom',x:712,title:'小桶不见了',off:1},
  bottle:{who:'fish',market:true,title:'漂流瓶',off:2},
  paint:{who:'art',x:742,title:'画一条鱼',off:0},
  lamp:{who:'inn',x:212,title:'晚上的灯',off:1,late:true},
  castle:{who:'le',x:768,title:'沙堡比赛',off:2,kid:true},
  deep:{who:'sci',x:935,title:'最深的地方',off:1}};
 const st=id=>{const b=M();b.cq[id]??={step:0};return b.cq[id];};
 const cqOn=id=>st(id).step>0&&!st(id).done;
 const awake=q=>{const h=hour();return q.late?h>=7&&h<23.5:h>=8&&h<19;};
 function present(id){const q=Q[id];if(q.market)return true;if(!awake(q))return false;return cqOn(id)||(today()+q.off)%3===0;}
 const whoP=id=>{const q=Q[id];return q.market?L.V[q.who]:NPC[q.who];};
 const ready={whistle:()=>st('whistle').got,surf:()=>(st('surf').lessons||0)>=3,coco:()=>(S().inv.coconut||0)>=3,turtle:()=>(st('turtle').n||0)>=3,bucket:()=>st('bucket').got,
  bottle:()=>st('bottle').step===3,paint:()=>st('paint').shot,lamp:()=>st('lamp').shot,castle:()=>st('castle').step===2&&today()>st('castle').day,deep:()=>st('deep').shot};
 photoHooks.push(k=>{if(cqOn('turtle')&&k==='turtle')st('turtle').n=(st('turtle').n||0)+1;
  if(cqOn('paint')&&PAGES[1][1].includes(k))st('paint').shot=1;if(cqOn('lamp')&&k==='glow_jelly')st('lamp').shot=1;if(cqOn('deep')&&k==='lanternfish')st('deep').shot=1;});
 function finish(id,text,{coins:v=0}={}){const s=st(id);s.done=1;s.doneDay=today();mood(MOOD.quest);log(text);if(v)coins(v,`委托「${Q[id].title}」的谢礼`);showHint(`委托「${Q[id].title}」完成${v?`，得到 ${v} 丢丢币`:''}`);}
 const IDLE={whistle:['今天浪不大，适合下水。','别游出黄色浮标外面哦。'],surf:['看浪要看第三道。','站起来那一下，膝盖别硬。'],coco:['今天的冰咖啡加了椰奶。','坐会儿吧，不急。'],
  turtle:['海龟不喜欢被追，等它游过来。','潜水别憋气，慢慢吐。'],bucket:['孩子玩疯了，喊都喊不回来。','这里的沙子真细。'],bottle:['今天的鱼还行。','年轻时我也天天下海。'],
  paint:['海的颜色每个钟头都不一样。','我在调一种蓝，还没调出来。'],lamp:['房间都收拾好了，随时回来住。','晚上门口的灯我一直留着。'],castle:['我的沙堡最高！','你看我挖的护城河！'],deep:['海沟底下的温度只有几度。','我又多了一页数据。']};
 // the goal in one line, shown when a commission is taken and whenever its giver is asked again (owner 2026-11-05:
 // 旅舍老板 repeating his reminder looked like a stuck talk)
 const GOAL={whistle:'退潮时（6–9 点、17–19 点）去浅滩找红绳子的哨子',surf:'在沙滩的冲浪板架冲三次浪（教练在场时算一节课）',coco:'在椰子树下捡 3 个椰子交给米娅',
  turtle:'潜水时点海龟，拍 3 张照片',bucket:'在浅水里找到小红桶',bottle:'去沉船谷的沉船宝箱找漂流瓶，再交给旅舍老板',paint:'拍一张珊瑚花园页里的鱼',
  lamp:'晚上 8 点后下水，在浅滩给发光水母拍照',castle:'和阿乐堆沙堡，第二天再来看',deep:'潜到深蓝海沟底，给灯笼鱼拍照'};
 // owner 2026-11-05: "use what exists": taken commissions show in the same 任务 panel as 茵菲谷's quests
 const QICON={whistle:'note',surf:'star',coco:'basket',turtle:'lens',bucket:'gift',bottle:'letter',paint:'fish',lamp:'lantern',castle:'house',deep:'map'};
 const zoneAt=x=>{let n='草帽湾';for(const [zx,name]of C()?.data?.zones||[])if(x>=zx)n=name;return n;};
 if(typeof questBoard!=='undefined')questBoard.add(()=>Object.entries(Q).filter(([id])=>st(id).step>0).map(([id,q])=>{const s=st(id);
  return {id:'bay_'+id,title:q.title,kind:QICON[id]||'scroll',place:q.market?'海棠集市':zoneAt(q.x),done:!!s.done,step:s.done?'':(GOAL[id]||''),end:'委托完成了',isNew:false,log:s.log||[]};}));
 const goalHint=id=>{const s=st(id);if(s.step&&!s.done&&GOAL[id])showHint(`委托「${Q[id].title}」：${GOAL[id]}`);};
 async function talk(id){const q=Q[id],s=st(id),P_=whoP(id),N=P_.name,me=nameOf();
  if(s.done){await say(N,IDLE[id][today()%2]);return;}
  if(id==='whistle'){if(!s.step){if(await ask(N,'哎，你会潜水吧？我的哨子早上掉海里了，退潮的时候浅滩那边能看见。帮我捞一下？',['我去找找','下次吧'])===0){s.step=1;await say(me,'退潮是早上和傍晚吧，我留意着。');}return;}
   if(!s.got){await say(N,'退潮的时候（早上 6 到 9 点、傍晚 5 到 7 点）浅滩那边能看见，红绳子的。');return;}
   await say(N,'就是它！没它我上班都不踏实。');await say(N,'这个你拿着，算我请你喝饮料。');finish(id,'帮救生员阿海从浅滩捞回了哨子。',{coins:2});return;}
  if(id==='surf'){if(!s.step){if(await ask(N,'想学冲浪吗？三节课，包你站起来。第一节先学摔。',['好，学！','我再想想'])===0){s.step=1;s.lessons=0;await say(N,'去架子上拿块板，我就在这儿看着。');}return;}
   if(!ready.surf()){await say(N,`还差 ${3-(s.lessons||0)} 节。摔几次就会了，谁不是喝着海水学会的。`);return;}
   await say(N,'我就说吧！站起来那一下，是不是整片海都是你的？');await say(me,'是！我还想再来一次！');finish(id,'跟冲浪教练小麦上完三节课，在浪上站起来了。');return;}
  if(id==='coco'){if(!s.step){if(await ask(N,'糟了，椰子用完了……旅舍后面那棵树每天会掉两个，能帮我捡三个来吗？',['好，我去捡','今天没空'])===0){s.step=1;await say(me,'椰子树下，我记住了。');}return;}
   if(!ready.coco()){await say(N,`还差 ${3-(S().inv.coconut||0)} 个，不急哦。`);return;}
   X.addItem('coconut',-3);need('fun',15);await say(N,'太好了！今天的椰子拿铁有着落了。这杯请你。');finish(id,'帮咖啡店的米娅捡了三个椰子，喝到一杯椰子拿铁。',{coins:3});return;}
  if(id==='turtle'){if(!s.step){if(await ask(N,'这片海的海龟脾气都好。我在做个记录，你能帮我拍三张海龟的照片吗？',['包在我身上','下次吧'])===0){s.step=1;s.n=0;await say(N,'海龟清洁站那边最多，慢慢靠近，别追。');}return;}
   if(!ready.turtle()){await say(N,`拍到 ${s.n||0} 张了，再来 ${3-(s.n||0)} 张。`);return;}
   await say(N,'这只左鳍上有道疤，我认识它！叫它“老船长”。');finish(id,'帮潜水教练诺亚拍了三张海龟。',{coins:3});return;}
  if(id==='bucket'){if(!s.step){if(await ask(N,'不好意思……孩子的红桶被浪卷走了，哭了一上午。你会游泳的话，能帮忙看看吗？',['我去找','这个我帮不上'])===0){s.step=1;await say(me,'浪往东边推的，应该在浅水那边。');}return;}
   if(!s.got){await say(N,'红色的小桶，上面有只鸭子。');return;}
   await say(N,'找到了！快谢谢姐姐。');await say('小朋友','谢谢！！');need('fun',10);finish(id,'在海里找回了小朋友的红桶。',{coins:1});return;}
  if(id==='bottle'){if(!s.step){if(await ask(N,'沉船那边的宝箱你见过吗？我年轻时往里塞过一个瓶子，里面有封信……要是还在，帮我送给旅舍老板。',['我去看看','今天不下海'])===0){s.step=1;await say(N,'别问写的什么。');}return;}
   if(s.step===1){await say(N,'沉船宝箱，在沉船谷那边。');return;}
   if(s.step===2){await say(N,'送到了没？……还没就先别跟我说。');return;}
   await say(N,'他……他说什么了？');await say(me,'他说，旅舍的招牌上，一直留着你的名字。');await say(N,'……这个老东西。');mood(MOOD.letter);finish(id,'把老渔夫四十年前的信送到了旅舍老板手里。',{coins:2});return;}
  if(id==='paint'){if(!s.step){if(await ask(N,'我想画一条鱼，可我不会潜水。你能拍张珊瑚花园里的照片给我当参考吗？',['好呀','我还不太会拍'])===0){s.step=1;await say(N,'越亮的颜色越好！');}return;}
   if(!s.shot){await say(N,'珊瑚花园那一页里的鱼都可以。');return;}
   await say(N,'就是这个颜色！你等我一下……');await say(N,'送你，画得不像别笑我。');X.addItem('painting',1);finish(id,'画画的姐姐照着照片画了一条鱼，送了一幅给我。');return;}
  if(id==='lamp'){if(s.step===0&&st('bottle').step===2){await say(N,'这是……老周的字。');await say(N,'四十年前我们说好一起开旅舍，他后来去打鱼了。招牌上的“周”字，我一直没摘。');await say(N,'你帮我告诉他吧，就说……旅舍还缺个钓鱼的。');st('bottle').step=3;return;}
   if(!s.step){if(await ask(N,'晚上海里有会发光的水母，你见过没？我年纪大了下不去了，你帮我拍张照片回来给我看看。',['好，晚上去','我怕黑'])===0){s.step=1;await say(N,'晚上八点以后，换上泳衣下水，浅滩那边一亮一亮的就是。');}return;}
   if(st('bottle').step===2){await say(N,'这是……老周的字。');await say(N,'四十年前我们说好一起开旅舍，他后来去打鱼了。招牌上的“周”字，我一直没摘。');await say(N,'你帮我告诉他吧，就说……旅舍还缺个钓鱼的。');st('bottle').step=3;return;}
   if(!s.shot){await say(N,'晚上八点以后去浅滩，看到一亮一亮的水母，点它给它拍张照片，再回来给我看。');return;}
   await say(me,'像一盏会游泳的小灯，一碰它就亮。');await say(N,'对对对，跟我年轻时看到的一模一样。');finish(id,'给旅舍老板讲了夜里的发光水母。');return;}
  if(id==='castle'){if(!s.step){if(await ask(N,'一起堆沙堡吗！比谁的高！',['来！','下次吧'])===0){s.step=1;await buildCastle(true);s.step=2;s.day=today();await say(N,'明天来看看，它还在不在！');}return;}
   if(!ready.castle()){await say(N,'明天再来看哦！');return;}
   await say(N,'沙堡被海吃掉了！！');await say(me,'涨潮的时候海水把它带走啦。');await say(N,'那……明天堆一个更大的！');finish(id,'和阿乐堆的沙堡被潮水带走了，约好明天再堆一个更大的。');return;}
  if(id==='deep'){if(!s.step){if(await ask(N,'我在做深海调查。最深的海沟底有灯笼鱼，头上挂着小灯——能帮我拍一张吗？',['我试试','太深了'])===0){s.step=1;await say(N,'换上潜水服再下去，海沟在深蓝海沟那边。');}return;}
   if(!s.shot){await say(N,'深蓝海沟最底下，黑漆漆的地方找一点黄光。');return;}
   await say(N,'清楚！这张能放进报告封面了。');finish(id,'帮海洋研究员拍到了海沟底的灯笼鱼。',{coins:5});return;}}
 Object.assign(X.ITEMS,{painting:{name:'一幅小鱼画',icon:'shell',price:0,line:'画画的姐姐照着照片画的，颜色比照片还亮。'}});
 // things to fetch in the sea
 const THINGS={whistle:[1112,150,()=>cqOn('whistle')&&!st('whistle').got&&((hour()>=6&&hour()<9)||(hour()>=17&&hour()<19))],bucket:[1236,206,()=>cqOn('bucket')&&!st('bucket').got],
  bottle:[1552,343,()=>cqOn('bottle')&&st('bottle').step===1]};
 function drawThings(ctx,t){for(const [id,[x,y,on]]of Object.entries(THINGS)){if(!on())continue;const yy=y+Math.round(Math.sin(t*1.5)*1);
  if(id==='whistle'){ctx.fillStyle='#d23b30';ctx.fillRect(x-4,yy,8,1);ctx.fillStyle='#c0c6cc';ctx.fillRect(x+3,yy-1,4,3);ctx.fillStyle='#8e959c';ctx.fillRect(x+3,yy+1,4,1);}
  if(id==='bucket'){ctx.fillStyle='#e35b4f';ctx.fillRect(x-3,yy-4,7,6);ctx.fillStyle='#b9473d';ctx.fillRect(x-3,yy-4,7,1);ctx.fillStyle='#f2d36b';ctx.fillRect(x-1,yy-2,3,2);ctx.fillStyle='#6b7178';ctx.fillRect(x-3,yy-6,7,1);}
  if(id==='bottle'){ctx.fillStyle='rgba(150,220,200,.85)';ctx.fillRect(x-2,yy-6,4,7);ctx.fillRect(x-1,yy-8,2,2);ctx.fillStyle='#f6ecd2';ctx.fillRect(x-1,yy-4,2,3);ctx.fillStyle='#8c6238';ctx.fillRect(x-1,yy-9,2,1);}
  if(Math.sin(t*3)>.5){ctx.fillStyle='#fffbe6';ctx.fillRect(x,yy-10,1,3);ctx.fillRect(x-1,yy-9,3,1);}}}
 hooks.click.push((x,y)=>{for(const [id,[tx,ty,on]]of Object.entries(THINGS)){if(!on()||Math.hypot(x-tx,y-ty)>10)continue;
  if(!swim()){toast('换上泳装才能游过去。');return true;}
  C().goTo(tx,'dive',ty+6,()=>{const s=st(id);if(id==='bottle'){s.step=2;speakBay('瓶子里有封信，信封上写着「给旅舍老板」。');log('在沉船宝箱里找到一个漂流瓶。');}else{s.got=1;speakBay(id==='whistle'?'找到了！红绳子的哨子。':'找到小红桶了！');}});return true;}return false;});
 // the people: drawn where they stand, a ! when they have something to ask, a ? when it can be handed in
 function markAt(ctx,x,y,ch){const by=Math.round(y+Math.sin(realClock*4)*1.5);ctx.fillStyle='#2b2236';ctx.fillRect(x-3,by-1,7,9);ctx.fillStyle=ch==='?'?'#7fd0f0':'#f6c45a';ctx.fillRect(x-2,by,5,7);ctx.fillStyle='#2b2236';
  if(ch==='!'){ctx.fillRect(x,by+1,1,3);ctx.fillRect(x,by+5,1,1);}else{ctx.fillRect(x-1,by+1,3,1);ctx.fillRect(x+1,by+2,1,1);ctx.fillRect(x,by+3,1,1);ctx.fillRect(x,by+5,1,1);}}
 const markOf=id=>{const s=st(id);if(s.done)return null;if(!s.step)return '!';return ready[id]()||(id==='bottle'&&s.step===3)?'?':null;};
 function drawPeople(ctx){const c=C(),t=c.state.time||realClock;drawThings(ctx,t);
  for(const [id,q]of Object.entries(Q)){if(q.market||!present(id))continue;const p=NPC[q.who],x=q.x,y=c.gr(x);
   if(q.kid){const pic=pose(p,realClock*1000);ctx.drawImage(pic,Math.round(x-7),Math.round(y-20),15,21);}else drawPerson(ctx,p,x,y);
   if(id==='paint'){ctx.fillStyle='#8c6238';ctx.fillRect(x+9,y-18,1,18);ctx.fillRect(x+15,y-18,1,18);ctx.fillStyle='#f6ecd2';ctx.fillRect(x+8,y-20,9,8);ctx.fillStyle='#7fc4e8';ctx.fillRect(x+9,y-17,7,3);ctx.fillStyle='#f2a65a';ctx.fillRect(x+11,y-16,3,1);}
   if(id==='whistle'){ctx.fillStyle='#e35b4f';ctx.fillRect(x+10,y-30,10,2);ctx.fillStyle='#f6f2ea';ctx.fillRect(x+12,y-28,1,28);ctx.fillRect(x+18,y-28,1,28);ctx.fillRect(x+12,y-16,7,1);}
   const m=markOf(id);if(m)markAt(ctx,x,y-(q.kid?28:36),m);}
  if(fest())drawFest(ctx);}
 hooks.draw.push(drawPeople);
 hooks.mdraw.push(ctx=>{for(const [id,q]of Object.entries(Q)){if(!q.market)continue;const m=markOf(id);if(!m)continue;const x=id==='coco'?L.CAFE_X-30:L.FISH_X+4;markAt(ctx,x,L.FEET-(id==='coco'?36:45),m);}if(fest())drawFestMarket(ctx);});
 hooks.click.push((x,y)=>{const c=C();for(const [id,q]of Object.entries(Q)){if(q.market||!present(id))continue;const g=c.gr(q.x);if(Math.abs(x-q.x)<9&&y>g-(q.kid?32:40)&&y<g+3){   /* includes the !/? mark above the head */
  scene(async()=>{await walk(q.x+(c.state.x<q.x?-14:14));await talk(id);goalHint(id);});return true;}}return false;});
 hooks.mclick.push((x,y)=>{for(const [id,q]of Object.entries(Q)){if(!q.market)continue;const px=id==='coco'?L.CAFE_X-30:L.FISH_X+4,m=markOf(id);if(!m)continue;
  if(Math.abs(x-px)<10&&y>L.FEET-34&&y<L.FEET+3){scene(async()=>{await walk(px+14);await talk(id);goalHint(id);});return true;}}return false;});

 // ================================================================ 4. island festivals
 const FESTS=[{n:'草帽节',se:1,day:4,c:['#d9a441','#f6dc8a'],line:'满天飞着草帽，风越大越热闹',flags:['#e35b4f','#f2d36b','#7fc4e8']},
  {n:'椰灯夜',se:1,day:9,c:['#3a3f7a','#f0a95b'],line:'椰壳里点上小灯，晚上放进海里许个愿',flags:['#f0a95b','#f6dc8a','#e57a5a']},
  {n:'花环节',se:1,day:12,c:['#d0577f','#f6b3cb'],line:'人人戴花环，广场上跳草裙舞',flags:['#f28fb0','#f6dc8a','#9fdc8a']},
  {n:'鲸歌节',se:2,day:5,c:['#36557a','#9bd3df'],line:'座头鲸经过海湾，海里能听到它们唱歌',flags:['#5d84b8','#e8f2fa','#9bd3df']},
  {n:'冲浪日',se:2,day:12,c:['#2f7aa0','#f2d36b'],line:'一年最大的浪，冲浪手都来了',flags:['#2f7aa0','#f2d36b','#ffffff']}];
 const fest=()=>{const se=cal();return FESTS.find(f=>f.se===se.i&&f.day===se.day)||null;};
 // city festivals stay in the city: on the island the bar and the time-bar tag show only the island's own
 const oldFT=festToday;festToday=function(){if(sim.place==='summer_test'){const f=fest();return f?{name:f.n,season:f.se,day:f.day,island:true,announce:()=>announce(f)}:null;}return oldFT();};
 // the day's start, the same way a city festival starts it: a diary line, her own words, the festival mood
 const FEST_SAY={草帽节:['帽子要抓紧！','今天风好大，好热闹'],椰灯夜:['晚上要放椰灯！','先想好许什么愿'],花环节:['好香的花环','今天要学草裙舞'],鲸歌节:['今天能听到鲸鱼唱歌吗','去岸边等着'],冲浪日:['浪好大！','今天有冲浪比赛']};
 function announce(f){log(`今天是草帽湾的${f.n}。${f.line}。`);speak(pick(FEST_SAY[f.n]||['过节啦']));mood(MOOD.fest);}
 const oldFT2=festivalToday;festivalToday=function(){if(sim.place==='summer_test'){const f=fest();if(f)return f.n;const d=Math.floor(sim.t/1440)+1;return d===30?'生日':d===14||d===56?'纪念日':null;}return oldFT2();};
 const festDone=k=>{const b=M();return b.fest[k+'@'+today()];},festMark=k=>{const b=M();b.fest[k+'@'+today()]=1;for(const o of Object.keys(b.fest))if(+o.split('@')[1]<today()-30)delete b.fest[o];};
 const goBay=async x=>{if(C().state.market){C().beginDoor('bay');await new Promise(r=>setTimeout(r,1400));}await walk(x);};
 const A={
  hat:()=>scene(async()=>{await goBay(C().state.x<700?C().state.x:880);hatFx.push({x:C().state.x,y:C().gr(C().state.x)-24,t0:realClock,me:1});speakBay('飞吧——！');
   if(!festDone('hat')){festMark('hat');mood(MOOD.fest);log('草帽节：把草帽抛向风里，看它飞过了整片海湾。');}}),
  freehat:()=>{if(festDone('freehat'))return showHint('今天已经领过草帽了');festMark('freehat');X.addItem('strawhat',1);showHint('草帽爷爷送了一顶草帽，放进仓库了');},
  lantern:()=>{if(hour()<18&&hour()>=5)return showHint('椰灯要等太阳落山以后才放');scene(async()=>{await goBay(1012);myLantern={t0:sim.t};speakBay('希望明天也是好天气……');
   if(!festDone('lantern')){festMark('lantern');mood(MOOD.lantern);log('椰灯夜：把一盏椰壳小灯放进海里，看它漂远了。');}});},
  hula:()=>scene(async()=>{await goBay(860);await say(L.P.lei.name,'手像海浪一样，左边——右边——');await say(nameOf(),'左边……右边……哈哈，我同手同脚了！');need('fun',20);need('social',15);
   if(!festDone('hula')){festMark('hula');mood(MOOD.fest);log('花环节：戴着花环跟蕾拉妮学了草裙舞。');}}),
  lei:()=>{if(festDone('lei'))return showHint('花环已经戴上啦');festMark('lei');need('fun',8);showHint('戴上了一串鸡蛋花花环');log('花环节：戴上了一串鸡蛋花花环，香了一整天。');},
  whale:()=>scene(async()=>{await goBay(1012);await say(nameOf(),'嘘……');await say('海里传来的声音','呜——————嗯——————');await say(nameOf(),'它们在聊天吗？');need('fun',15);
   if(!festDone('whale')){festMark('whale');mood(MOOD.whale);log('鲸歌节：坐在岸边听了很久的鲸歌。');}}),
  watch:()=>scene(async()=>{await goBay(960);await say('解说员','第三号选手上浪了！——完美的转身！');await say(nameOf(),'好厉害！！');need('fun',20);if(!festDone('watch')){festMark('watch');mood(MOOD.wave);}}),
  contest:()=>{if((M().act.surf||0)<3)return showHint('先多冲几次浪，能站起来了再来报名');if(festDone('contest'))return showHint('今天已经比过了');
   scene(async()=>{festMark('contest');await say('解说员','下一位选手——来自草帽湾的新人！');surf();await new Promise(r=>setTimeout(r,9500));await say('解说员','漂亮！新人奖！');coins(5,'冲浪日新人奖');mood(MOOD.wave);log('冲浪日：参加冲浪比赛，拿了新人奖。');});}};
 if(typeof FB_MOTIFS!=='undefined')Object.assign(FB_MOTIFS,{草帽节:['star','flower','heart'],椰灯夜:['lantern','moon','star'],花环节:['flower','heart','note'],鲸歌节:['wave','note','star'],冲浪日:['wave','star','ball']});   // the festival bar's own drifting motifs
 Object.assign(FEST_BAR,{
  草帽节:['#d9a441','#f6dc8a','满天飞着草帽，风越大越热闹',['抛草帽','fn',A.hat],['领一顶草帽','fn',A.freehat]],
  椰灯夜:['#3a3f7a','#f0a95b','椰壳里点上小灯，晚上放进海里许个愿',['放一盏椰灯','fn',A.lantern]],
  花环节:['#d0577f','#f6b3cb','人人戴花环，广场上跳草裙舞',['戴花环','fn',A.lei],['学草裙舞','fn',A.hula]],
  鲸歌节:['#36557a','#9bd3df','座头鲸经过海湾，海里能听到它们唱歌',['岸边听鲸歌','fn',A.whale]],
  冲浪日:['#2f7aa0','#f2d36b','一年最大的浪，冲浪手都来了',['看冲浪比赛','fn',A.watch],['报名比赛','fn',A.contest]]});
 let hatFx=[],myLantern=null,festHello=-1;
 hooks.tick.push(()=>{if(!inBay())return;const f=fest();
  if(f?.n==='草帽节'&&Math.random()<.02&&hatFx.length<14)hatFx.push({x:C().state.x-200+Math.random()*120,y:20+Math.random()*50,t0:realClock});});
 function bunting(ctx,x0,x1,y,f,t){const sag=6;for(let x=x0;x<=x1;x++){const u=(x-x0)/(x1-x0),yy=Math.round(y+sag*4*u*(1-u));ctx.fillStyle='#6b5a4a';ctx.fillRect(x,yy,1,1);
  if((x-x0)%7===0&&x+5<=x1){ctx.fillStyle=f.flags[((x-x0)/7|0)%f.flags.length];const sway=Math.round(Math.sin(t*2+x)*.6);for(let k=0;k<5;k++)ctx.fillRect(x+Math.floor(k/2)+sway*(k>2?1:0),yy+1+k,Math.max(1,5-k-Math.floor(k/2)),1);}}}
 function drawHats(ctx,t){for(const h of hatFx){const p=realClock-h.t0;const x=h.x+p*38,y=h.y-p*(h.me?10:2)+Math.sin(p*3)*6;ctx.fillStyle='#e9c46a';ctx.fillRect(x-3,y,7,1);ctx.fillRect(x-1,y-2,3,2);ctx.fillStyle='#c98b3a';ctx.fillRect(x-1,y-1,3,1);ctx.fillStyle='#e35b4f';ctx.fillRect(x-1,y-1,3,1);}
  hatFx=hatFx.filter(h=>realClock-h.t0<14);}
 function drawFest(ctx){const f=fest(),c=C(),t=c.state.time||realClock;
  bunting(ctx,560,760,34,f,t);bunting(ctx,770,1000,30,f,t);bunting(ctx,140,330,38,f,t);
  for(const x of [560,760,770,1000,140,330]){ctx.fillStyle='#7a5636';ctx.fillRect(x,30,1,c.gr(x)-30);}
  if(f.n==='草帽节')drawHats(ctx,t);
  if(f.n==='椰灯夜'){const ev=hour()>=18||hour()<2;if(ev){const ctx_=ctx;{const ctx=G(ctx_);for(let k=0;k<16;k++){const x=1030+((k*67+t*3)%700),y=WL+Math.round(Math.sin(t*1.3+k)*1);ctx.fillStyle='rgba(255,190,90,.25)';ctx.fillRect(x-3,y-5,7,6);ctx.fillStyle='#f6c45a';ctx.fillRect(x-1,y-3,3,3);ctx.fillStyle='#fff1c0';ctx.fillRect(x,y-2,1,1);}
    for(let k=0;k<6;k++){const x=900+k*90+Math.sin(t*.3+k)*10,y=110-((t*4+k*30)%110);ctx.fillStyle='rgba(255,200,110,.3)';ctx.fillRect(x-2,y-3,5,6);ctx.fillStyle='#f0a95b';ctx.fillRect(x-1,y-2,3,4);}
    if(myLantern){const age=(sim.t-myLantern.t0),x=1020+age*1.2,y=WL+Math.round(Math.sin(t*1.5));if(age<240){ctx.fillStyle='rgba(255,140,180,.3)';ctx.fillRect(x-4,y-6,9,7);ctx.fillStyle='#f28fb0';ctx.fillRect(x-1,y-3,3,3);}}}}}
  if(f.n==='花环节'){for(const [i,x]of [[0,846],[1,874]]){const p=i?L.P.lei:L.P.alo,bob=Math.round(Math.sin(t*4+i)*1.5);drawPerson(ctx,p,x+Math.round(Math.sin(t*2+i)*2),c.gr(x)+bob,{wave:true});}
   for(let x=600;x<1000;x+=9){ctx.fillStyle=['#f28fb0','#f6dc8a','#ffffff'][(x/9|0)%3];ctx.fillRect(x,40+Math.round(Math.sin(x)*2),2,2);}}
  if(f.n==='鲸歌节'){const n=Math.floor(t)%6;if(n<2){ctx.fillStyle='rgba(255,255,255,.7)';for(let k=0;k<3;k++)ctx.fillRect(1040+k*6,WL-8-k*3-(t*4%4|0),3,1);}}
  if(f.n==='冲浪日'){for(let k=0;k<3;k++){const p=((t*.12+k/3)%1),x=1400-p*370,h=Math.round(10*(1-p)+3);ctx.fillStyle='rgba(255,255,255,.9)';ctx.fillRect(x-20,WL-h,40,2);ctx.fillStyle='rgba(180,230,245,.8)';ctx.fillRect(x-24,WL-h+2,48,h);
    if(k===0){const sp=WAVE[0];drawPerson(ctx,sp,x,WL-h-1);ctx.fillStyle='#f2d36b';ctx.fillRect(x-7,WL-h-1,14,2);}}
   for(let i=0;i<3;i++)drawPerson(ctx,WAVE[i+1],930+i*16,c.gr(930+i*16),{wave:Math.sin(t*3+i)>.3});}}
 const WAVE=[person('冲浪选手','m',2203),person('观众','f',2309),person('观众','m',2411),person('观众','f',2503)];
 function drawFestMarket(ctx){const f=fest(),t=realClock;bunting(ctx,40,300,26,f,t);bunting(ctx,300,560,22,f,t);bunting(ctx,560,680,28,f,t);
  if(f.n==='草帽节')drawHats(ctx,t);if(f.n==='花环节')for(let x=60;x<660;x+=11){ctx.fillStyle=['#f28fb0','#f6dc8a','#ffffff'][(x/11|0)%3];ctx.fillRect(x,30+Math.round(Math.sin(x*.7)*2),2,2);}
  if(f.n==='椰灯夜'&&(hour()>=18||hour()<2)){const ctx_=ctx;const ctx2=G(ctx_);for(let x=50;x<680;x+=40){const ctx=ctx2;ctx.fillStyle='rgba(255,190,90,.25)';ctx.fillRect(x-3,26,7,9);ctx.fillStyle='#f0a95b';ctx.fillRect(x-1,28,3,5);}}}
 // ================================================================ 5. needs are met in the lodge
 // Owner rule (AGENTS.md → Season maps): she never decides to go home from a season map. Low needs send her into
 // 阿洛's lodge, where she rests until the lowest need is back up. Only the player's own 回家 flies her home.
 let leavingBay=false,care=null;
 const oCmd=command;command=function(act,item){if(sim.place==='summer_test'&&act==='go_home')leavingBay=true;return oCmd(act,item);};
 function lodgeCare(){if(care)return;const low=Object.entries(sim.needs).sort((a,b)=>a[1]-b[1])[0];care={need:low[0]};
  speakBay(pick({hunger:['回旅舍吃点东西','肚子饿了，回旅舍'],energy:['回旅舍睡一会儿','好困，回旅舍歇歇'],hygiene:['回旅舍洗个澡','一身沙子，回旅舍冲冲'],bladder:['去旅舍上个厕所'],social:['回旅舍和阿洛聊聊天'],fun:['回旅舍歇一会儿']}[care.need]||['回旅舍歇一会儿']));
  sim.mode='act';sim.act='season_explore';sim.actEnd=Infinity;const c=C();
  c.state.target=null;}   /* the timer below walks her there, swimming ashore first */
 const oHome=homeFor;homeFor=function(k){if(sim.place==='summer_test'&&!leavingBay){lodgeCare();return;}return oHome(k);};
 const oStart=startAct;startAct=function(name,quiet){if(sim.place==='summer_test'&&name==='go_home'&&!leavingBay){lodgeCare();return;}return oStart(name,quiet);};
 const oArrive=arriveAt;arriveAt=function(p){leavingBay=false;care=null;if(p==='summer_test'){sim.outBack=null;sim.outWhy=null;}return oArrive(p);};   /* the city outing's "home by …" timer (set when she walked to the airport) must not follow her onto the island */
 setInterval(()=>{if(sim.place==='summer_test'&&!leavingBay&&sim.outBack!=null){sim.outBack=null;sim.outWhy=null;}},1000);
 let careT=0,careStuck=0;setInterval(()=>{if(!care||sim.place!=='summer_test'||wiping)return;   // a timer: the bay's draw hooks stop while she is inside
  const s=C().state;if(!s.inside){if(!s.target&&!s.door&&!L.isBusy()&&!storyLocked()){if(s.market)C().beginDoor('bay');else if(s.y>SURF+3)C().goTo(1050,'dive',SURF);else C().enter();careStuck=Date.now();}else if(s.target&&Date.now()-careStuck>15000){s.target=null;careStuck=Date.now();}return;}   /* from the sea she swims ashore first */
  if(sim.needs[care.need]<90&&window.summerLodge){const sl=summerLodge,id=sl.NEED_SPOT[care.need];if(id){careT=0;if(!sl.svc&&!s.target)sl.use(id,true);return;}}   /* the lodge's own furniture: bed, shower, stove... */
  const gm=careT?Math.max(0,Math.min(30,sim.t-careT)):0;careT=sim.t;need(care.need,gm*.6);for(const k of Object.keys(sim.needs))if(k!==care.need)need(k,gm*.05);
  if(sim.needs[care.need]>=90){care=null;careT=0;sim.actEnd=sim.t;speakBay('歇好了，出去玩～');setTimeout(()=>{try{C().leave();}catch(e){}},900);}},500);
 window.summerMore={nightPass,dark,snap,openDex,M,fest,FESTS,Q,st,talk,surf,buildCastle,PAGES,A,present};
})();
