'use strict';
// Summer bay walk-through: one seamless map 旅舍 -> 更衣室 -> 沙滩 -> 水底.
// Walk on land; change at the cabana (clothes can only wade); swim at the
// surface; click under water to dive without an oxygen timer. Rocks are solid;
// the arch has a hole. Discover habitats and sea life at your own pace.
const DATA=/*__DATA__*/null;
const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d'),images=new Map();
const say=document.getElementById('say'),status=document.getElementById('status'),maps=document.getElementById('maps');
const {W,H,WL,ground}=DATA,VW=342,LAND_H=118,SEA_H=236,SURF_Y=WL+12,CELL=28;
const SUIT_NAME={clothes:'便装',swim:'泳衣',wetsuit:'潜水服'};
const TOTAL=DATA.hotspots.length+new Set(DATA.life.map(c=>c.k)).size;
const state={x:120,y:0,vy:0,target:null,after:null,facing:1,camX:0,camY:0,viewH:LAND_H,time:0,paused:false,inside:false,walk:false,loaded:false,
 suit:'clothes',gender:'f',moveSpeed:0,camVX:0,camVY:0,diveBlend:0,inCabana:false,lying:null,changing:0,found:new Set(),wasSea:false,warned:0,market:false};
// 市集 (owner 2026-11-05): an optional district left of the lodge, drawn and clicked by a hook (setMarket).
let market=null,photo=null;/* photo: the underwater camera (summer_more.js) takes over a creature click */const MARKET_FEET=104;
const fx=makeSeasonEffects(DATA.skinRamp);let wetKind='clear',weatherOverride=null;
const wxLabel=document.createElement('label');wxLabel.className='season-weather';wxLabel.innerHTML='天气 <select aria-label="地图测试天气"><option value="">跟随游戏</option><option value="clear">晴天</option><option value="rain">小雨</option><option value="storm">大雨</option><option value="snow">小雪</option><option value="blizzard">大雪</option></select>';canvas.parentElement.parentElement.querySelector('.controls').append(wxLabel);wxLabel.querySelector('select').onchange=e=>{weatherOverride=e.target.value||null;wetKind=weatherOverride||'clear';};
const keys=new Set(),parts=[];let peopleRenderer=null;
const reduced=matchMedia('(prefers-reduced-motion:reduce)').matches;
let solid=null,solidSum=null;
function load(o){if(typeof o==='string'&&o.startsWith('data:image/')){if(!images.has(o)){const im=new Image();images.set(o,im);im.src=o;}return;}if(o&&typeof o==='object')Object.values(o).forEach(load);}
const img=s=>images.get(s);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const gr=x=>ground[clamp(Math.round(x),0,W-1)];
const isSolid=(x,y)=>{x=Math.round(x);y=Math.round(y);if(x<0||x>=W||y>=H)return true;if(y<0)return false;return solid[y*W+x]>0;};
const deep=x=>gr(x)>WL+24;
const wadeLimit=()=>state.suit==='clothes'?WL+5:Infinity;
const standY=x=>gr(x)<WL+8?gr(x):SURF_Y;            // feet on the sand while wading, then float
const inSea=()=>state.y>WL+2;
const under=()=>state.y>SURF_Y+3;
const floating=()=>inSea()&&!under()&&gr(state.x)>=WL+8;
const LEFT=44,RIGHT=DATA.seaEnd;
let sayTimer=0;
function toast(text,sec=3.2){say.textContent=text;say.hidden=false;sayTimer=sec;}
function zoneName(){if(state.inside)return '旅舍里';if(state.market)return '市集';let n=DATA.zones[0][1];for(const [x,name]of DATA.zones)if(state.x>=x)n=name;return n+(under()?' · 潜水中':inSea()?' · 水里':'');}
function updateUI(){const label=`${zoneName()} · ${SUIT_NAME[state.suit]} · 发现 ${state.found.size}/${TOTAL}`;if(status.textContent!==label)status.textContent=label;document.getElementById('exit').hidden=!state.inside;
 [...maps.children].forEach((b,i)=>{const z=DATA.zones[i],nx=DATA.zones[i+1];const value=String(!state.inside&&state.x>=z[0]&&(!nx||state.x<nx[0]));if(b.getAttribute('aria-current')!==value)b.setAttribute('aria-current',value);});}
function goTo(x,kind='walk',y=0,after=null){state.lying=null;state.target={x:clamp(x,LEFT,RIGHT),y,kind};state.after=after;}
function discover(id,text){const first=!state.found.has(id);state.found.add(id);toast((first?'✦ 新发现：':'')+text,4.2);}
function splash(x,y,n=10){for(let i=0;i<n;i++)parts.push({x:x+(Math.random()-.5)*8,y,vx:(Math.random()-.5)*30,vy:-20-Math.random()*30,life:.7,c:'#f4fbff',g:80});}
// ------------------------------------------------------------- movement
function step(px,py,tx,ty,sp){const dx=tx-px,dy=ty-py,d=Math.hypot(dx,dy);if(d<=sp)return [tx,ty,true];return [px+dx/d*sp,py+dy/d*sp,false];}
function walkTo(tx,dt){const sp=dt*(inSea()?30:42)*(state.rush?2:1);let [x,,ok]=step(state.x,0,tx,0,sp);
 if(gr(x)>wadeLimit()){if(state.warned<=0){toast('穿着便装只能在浅水边踩踩水，先去更衣室换上泳装吧～');state.warned=6;}return true;}
 state.x=x;state.y+=(standY(state.x)-state.y)*Math.min(1,dt*10);return ok&&Math.abs(state.y-standY(state.x))<1;}
function swimTo(tx,ty,dt){                               // free swimming with rock collision (slides along walls)
 const distance=Math.hypot(tx-state.x,ty-state.y),limit=state.target?.kind==='up'?18:12;state.moveSpeed+=(Math.min(limit,Math.sqrt(distance*28))-state.moveSpeed)*(1-Math.exp(-9*dt));const [nx,ny,ok]=step(state.x,state.y,tx,ty,dt*state.moveSpeed*(state.rush?2:1));let x=state.x,y=state.y;
 const free=(a,b)=>!isSolid(a,b)&&!isSolid(a,b-10)&&b>=SURF_Y&&a<=RIGHT;
 if(free(nx,ny)){x=nx;y=ny;}else if(free(nx,state.y)){x=nx;}else if(free(state.x,ny)){y=ny;}else return true;
 state.vy=(y-state.y)/Math.max(dt,1e-3);state.x=x;state.y=y;return ok;}
function move(dt){state.walk=false;if(state.paused||!state.loaded)return;if(state.target)state.rushWalk=1;else if(state.rushWalk||state.rush&&performance.now()-state.rush>3000){state.rush=0;state.rushWalk=0;}/* player-sent walks go 2x (owner 2026-11-05) */
 state.warned-=dt;if(sayTimer>0&&(sayTimer-=dt)<=0)say.hidden=true;
 if(state.door)return;
 if(state.changing>0){state.changing-=dt;return;}
 if(state.market){if(state.target){const [x,,done]=step(state.x,0,clamp(state.target.x,14,(market?.w||684)-14),0,dt*42*(state.rush?2:1));state.walk=!done;if(Math.abs(state.target.x-state.x)>.1)state.facing=Math.sign(state.target.x-state.x);state.x=x;state.y=MARKET_FEET;if(done){state.target=null;if(state.after){const f=state.after;state.after=null;f();}}}return;}
 if(state.inside){if(state.target){const [x,,done]=step(state.x,0,state.target.x,0,dt*42*(state.rush?2:1));state.walk=!done;if(Math.abs(state.target.x-state.x)>.1)state.facing=Math.sign(state.target.x-state.x);state.x=x;if(done){state.target=null;if(state.after){const f=state.after;state.after=null;f();}}}return;}
 const dir=(keys.has('ArrowRight')||keys.has('d')||keys.has('D')?1:0)-(keys.has('ArrowLeft')||keys.has('a')||keys.has('A')?1:0);
 const vdir=(keys.has('ArrowDown')||keys.has('s')||keys.has('S')?1:0)-(keys.has('ArrowUp')||keys.has('w')||keys.has('W')?1:0);
 if(dir||vdir){state.after=null;if(state.suit!=='clothes'&&(under()||(vdir>0&&deep(state.x))))goTo(state.x+dir*30,'dive',state.y+vdir*30);else if(dir)goTo(state.x+dir*40);}
 const t=state.target;
 if(t){if(Math.abs(t.x-state.x)>.5)state.facing=Math.sign(t.x-state.x);let done=false;
  if(t.kind==='up'){done=swimTo(state.x,SURF_Y,dt);}
  else if(t.kind==='dive'&&state.suit!=='clothes'){
   if(!under()&&!deep(state.x))walkTo(t.x,dt);                // head out along the surface first
   else done=swimTo(t.x,clamp(t.y,SURF_Y,gr(t.x)-4),dt);
  }else if(under()){const tx=gr(t.x)<WL+8?Math.max(state.x-40,Math.min(state.x+40,t.x)):t.x;swimTo(tx,SURF_Y,dt);}
  else done=walkTo(t.x,dt);
  state.walk=true;
  if(done){state.target=null;state.walk=false;if(state.after){const f=state.after;state.after=null;f();}}}
 const sea=floating();if(sea&&!state.wasSea)splash(state.x,WL,12);state.wasSea=sea;
 // fish shy away from Buddy
 for(const c of DATA.life)if(c.k==='school'||c.k==='tang'){const dx=(c.cx||0)-state.x,dy=(c.cy||0)-(state.y-10),d=Math.hypot(dx,dy);if(d>0.01&&d<28&&under()){c.ox=(c.ox||0)+dx/d*dt*60;c.oy=(c.oy||0)+dy/d*dt*40;}c.ox=(c.ox||0)*.985;c.oy=(c.oy||0)*.985;}
 for(const p of parts){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=p.g*dt;p.life-=dt;}for(let i=parts.length-1;i>=0;i--)if(parts[i].life<=0)parts.splice(i,1);
 if(inSea()&&!state.inside)fx.waterActor('hero',state.x,state.y,state.facing,state.walk,under(),dt,WL);}
function follow(value,velocity,target,omega,dt){const delta=value-target,e=Math.exp(-omega*dt),temp=(velocity+omega*delta)*dt;return [target+(delta+temp)*e,(velocity-omega*temp)*e];}
function camera(dt){
 if(state.market){if(canvas.height!==LAND_H){canvas.height=LAND_H;ctx.imageSmoothingEnabled=false;}state.viewH=LAND_H;const lead=state.walk?state.facing*14:0;[state.camX,state.camVX]=follow(state.camX,state.camVX,clamp(state.x-VW/2+lead,0,(market?.w||684)-VW),7,dt);state.camX=clamp(state.camX,0,(market?.w||684)-VW);state.camY=0;state.diveBlend=0;return;}
 const sea=!state.inside&&((inSea()&&gr(state.x)>WL+8)||under()),wantH=sea?SEA_H:LAND_H;
 // Resize once per mode switch, not once per animated height pixel.
 if(canvas.height!==wantH){canvas.height=wantH;ctx.imageSmoothingEnabled=false;}
 state.viewH+=(wantH-state.viewH)*(1-Math.exp(-6*dt));
 const lead=state.walk?state.facing*14:0,tx=clamp(state.x-VW/2+lead,0,W-VW);
 [state.camX,state.camVX]=follow(state.camX,state.camVX,tx,7,dt);
 const ty=sea?clamp(state.y-state.viewH*.48,0,H-wantH):clamp(gr(state.x)-104,0,H-wantH);
 [state.camY,state.camVY]=follow(state.camY,state.camVY,ty,6,dt);
 state.camX=clamp(state.camX,0,W-VW);state.camY=clamp(state.camY,0,H-wantH);
 state.diveBlend+=(Number(under())-state.diveBlend)*(1-Math.exp(-8*dt));
}
// ------------------------------------------------------------- drawing
function cell(){const t=state.time;if(state.lying!==null)return 8;
 if(under())return 6+(state.walk?Math.floor(t*5)%2:Math.floor(t*1.5)%2);
 if(floating())return 4+(state.walk?Math.floor(t*4)%2:0);
 return state.walk?Math.floor(t*7)%4:0;}
function hero(x,y){if(state.inCabana||state.changing>0)return;const sheet=img(DATA.heroes[state.gender][state.suit]);
 if(inSea()&&!state.inside){fx.swimmer(ctx,{head:headImage(sheet),sheet,x,y,time:state.time,facing:state.facing,diving:under(),moving:state.walk,wetsuit:state.suit==='wetsuit',waterline:WL});return;}
 const c=cell();ctx.save();ctx.translate(x,y);if(c!==8)ctx.scale(state.facing,1);ctx.drawImage(sheet,c*CELL,0,CELL,CELL,-14,-28,CELL,CELL);ctx.restore();}
const headCache=new Map();function headImage(sheet){if(!headCache.has(sheet)){const c=document.createElement('canvas');c.width=20;c.height=28;c.getContext('2d').drawImage(sheet,4,0,20,15,0,0,20,15);headCache.set(sheet,c);}return headCache.get(sheet);}
function beginDoor(to){if(state.door)return;keys.clear();state.target=null;state.after=null;state.door={to,elapsed:0,duration:.65,mid:false};}
function advanceDoor(dt){const d=state.door;if(!d)return;d.elapsed+=dt;if(!d.mid&&d.elapsed>=d.duration/2&&(d.to==='market'||d.to==='bay')){d.mid=true;state.inside=false;state.market=d.to==='market';state.x=d.to==='market'?(market?.w||684)-40:58;state.y=d.to==='market'?MARKET_FEET:standY(58);state.camX=d.to==='market'?clamp(state.x-VW/2,0,(market?.w||684)-VW):0;state.camY=0;state.camVX=state.camVY=0;state.facing=-1;updateUI();}
 if(!d.mid&&d.elapsed>=d.duration/2){d.mid=true;state.inside=d.to;state.x=d.to?64:DATA.lodgeDoor;state.y=d.to?84:standY(state.x);state.camX=d.to?0:clamp(state.x-VW/2,0,W-VW);state.camY=0;state.camVX=state.camVY=0;updateUI();}if(d.elapsed>=d.duration)state.door=null;}
function enter(){goTo(DATA.lodgeDoor,'walk',0,()=>beginDoor(true));}
function leave(){if(state.inside)goTo(48,'walk',0,()=>beginDoor(false));}
function exitArrow(){ctx.fillStyle='#e9eee2';ctx.fillRect(12,64,22,24);ctx.strokeStyle='#526578';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(27,69);ctx.lineTo(19,76);ctx.lineTo(27,83);ctx.stroke();}

function sparkle(x,y,t){const a=(Math.sin(t*3+x)+1)/2;if(a<.3)return;ctx.fillStyle=`rgba(255,250,220,${a})`;ctx.fillRect(x,y-2,1,5);ctx.fillRect(x-2,y,5,1);}
function draw(){const vh=canvas.height;ctx.fillStyle='#eee8dd';ctx.fillRect(0,0,VW,vh);if(!state.loaded)return;
 const t=reduced?0:state.time;
 if(state.market&&market){market.draw(ctx,{time:t,camX:state.camX,hero:()=>hero(state.x,MARKET_FEET)});drawTravelArrows();fx.transition(ctx,state.door,VW,vh);return;}
 if(state.inside){ctx.fillStyle='#eee8dd';ctx.fillRect(0,0,VW,vh);ctx.drawImage(img(DATA.inside),40,28);if(!state.hideHero)hero(state.x,84+(state.iy||0));globalThis.summerLodge?.draw(ctx);exitArrow();fx.transition(ctx,state.door,VW,vh);return;}
 const cx=state.camX,cy=state.camY;
 ctx.drawImage(img(DATA.sky),cx,cy,VW,vh,0,0,VW,vh);
 ctx.save();ctx.translate(-cx,-cy);
 // Clouds belong behind mountains, trees, buildings and every actor.
 for(let i=0;i<42;i++){const c=img(DATA.clouds[i%3]),x=((i*113+t*(1.2+i%4*.5))%(W+60))-40,y=4+(i*17)%36;if(x+c.width>cx&&x<cx+VW)ctx.drawImage(c,x,y);}
 // 远景 / 中景 scroll slower than the land and water (owner 2026-11-06): drawn shifted by part of the camera move
 for(const [k,key] of [[.35,'far'],[.65,'mid']])if(DATA[key])ctx.drawImage(img(DATA[key]),Math.round(cx*(1-k)),0);
 ctx.drawImage(img(DATA.bg),0,0);
 for(const p of DATA.plants){const im=img(p.img);if(!p.kind.endsWith('-front')&&p.x+im.width>cx-4&&p.x<cx+VW+4&&p.y+im.height>cy&&p.y<cy+vh)fx.plant(ctx,im,p,t);}
 ctx.drawImage(img(DATA.structures),0,0);
 for(const p of DATA.plants)if(p.kind.endsWith('-front')){const im=img(p.img);if(p.x+im.width>cx-4&&p.x<cx+VW+4&&p.y+im.height>cy&&p.y<cy+vh)fx.plant(ctx,im,p,t);}
 fx.sunlight(ctx,t,cx,cy,VW,vh,WL,ground,wetKind!=='clear');
 fx.kelp(ctx,t,DATA.kelp,cx,cy,VW,vh);
 fx.waves(ctx,t,cx,VW,WL,DATA.shore,DATA.seaEnd);
 const sim=img(DATA.seal[Math.floor(t*.7)%2]);ctx.drawImage(sim,DATA.sealAt[0],DATA.sealAt[1]-sim.height);
 for(const h of DATA.hotspots)if(!state.found.has(h.id))sparkle(h.x,h.y,t);
 // Fish swim back and forth inside a lane worked out ONCE from open water (owner 2026-11-05: fish popped in/out and
 // jerked when the old per-frame test met rock: frozen, snapped back, or skipped). The lane fits the largest frame
 // plus the 2px bob, so the whole sprite always stays in water and the motion is one smooth sine.
 const free=(xx,yy,w,h)=>{const x0=Math.floor(xx),y0=Math.floor(yy),x1=Math.ceil(xx+w),y1=Math.ceil(yy+h),stride=W+1;if(x0<0||x1>W||y0<=WL+3||y1>H)return false;return solidSum[y1*stride+x1]-solidSum[y0*stride+x1]-solidSum[y1*stride+x0]+solidSum[y0*stride+x0]===0;};
 for(const c of DATA.life){
  if(c.when&&!(globalThis.summerLifeOn?.(c.when,c.k)??true)){c.cx=0;continue;}   /* 图鉴 batch 2: night / rain / dawn / dusk / rare ones */
  if(c.lane===undefined){const ims=c.f.map(img);if(ims.some(m=>!m.width))continue;
   const w=Math.max(...ims.map(m=>m.width)),h=Math.max(...ims.map(m=>m.height)),ok=(x,y)=>free(x,y-2,w,h+4);
   let y=c.y+(c.oy||0),x0=c.x+(c.ox||0);
   if(!ok(x0,y)){let hit=null;for(let d=1;d<120&&!hit;d++)for(const [dx,dy]of [[0,-d],[0,d],[-d,0],[d,0],[-d,-d],[d,-d],[-d,d],[d,d]])if(ok(x0+dx,y+dy)){hit=[x0+dx,y+dy];break;}if(hit)[x0,y]=hit;else y=null;}   /* nearest open water around its spot */
   if(y===null)c.lane=null;
   else{let lo=0,hi=0;while(lo<c.r&&ok(x0-lo-1,y))lo++;while(hi<c.r&&ok(x0+hi+1,y))hi++;c.lane={mid:x0+(hi-lo)/2,half:(hi+lo)/2,y};}}
  if(!c.lane)continue;const L=c.lane;
  const ph=t*c.v/Math.max(1,L.half)+c.x*.031,x=L.mid+Math.sin(ph)*L.half,y=L.y+Math.sin(t*.7+c.x)*2,left=Math.cos(ph)<0&&L.half>1,im=img(c.f[Math.floor(t*10+c.x)%c.f.length]);
  c.cx=x+im.width/2;c.cy=y+im.height/2;c.w=im.width;c.h=im.height;c.im=im;c.px=Math.round(x+im.width/2)-Math.round(im.width/2);c.py=Math.round(y+im.height/2)-Math.round(im.height/2);c.flip=left;
  if(x+im.width<cx||x>cx+VW||y+im.height<cy||y>cy+vh)continue;
  ctx.save();ctx.translate(Math.round(x+im.width/2),Math.round(y+im.height/2));ctx.scale(left?-1:1,1);ctx.drawImage(im,-Math.round(im.width/2),-Math.round(im.height/2));ctx.restore();}
 peopleRenderer?.(ctx,{time:t,inside:state.inside,under:under()});
 if(state.lying!==null){const [lx,ly]=DATA.chairs[state.lying];state.facing=1;hero(lx,ly);}else hero(state.x,state.y);
 fx.drawWater(ctx,WL,{x:cx,y:cy,w:VW,h:vh});
 for(const p of parts){ctx.fillStyle=p.c;ctx.globalAlpha=clamp(p.life*1.5,0,1);ctx.fillRect(Math.round(p.x),Math.round(p.y),1,1);}ctx.globalAlpha=1;
 ctx.restore();
 fx.weather(ctx,wetKind,t,VW,vh,{waterline:WL-cy});
 drawTravelArrows();fx.transition(ctx,state.door,VW,vh);
}
function drawTravelArrows(){if(state.inside||state.inCabana)return;const y=canvas.height*.56;
 for(const [x,dir]of [[12,-1],[VW-12,1]]){ctx.fillStyle='rgba(247,246,251,.88)';ctx.fillRect(x-8,y-9,16,18);ctx.fillStyle='#5d6176';for(let i=0;i<5;i++){ctx.fillRect(x+dir*(i-2),y-5+i,2,2);ctx.fillRect(x+dir*(i-2),y+3-i,2,2);}}}
function travel(dir){if(state.inside||state.inCabana)return;
 if(state.market){if(dir>0&&state.x>(market?.w||684)-150)return beginDoor('bay');return goTo(clamp(state.x+dir*170,14,(market?.w||684)-14));}
 if(market&&dir<0&&state.x<150&&!under())return beginDoor('market');const next=DATA.zones.filter(z=>dir>0?z[0]>state.x+24:z[0]<state.x-24);const x=next.length?(dir>0?next[0][0]+35:next[next.length-1][0]+35):state.x+dir*180;goTo(x,under()?'dive':'walk',state.y);}
const wardrobe=document.createElement('section');wardrobe.className='bay-wardrobe';wardrobe.hidden=true;wardrobe.setAttribute('role','dialog');wardrobe.setAttribute('aria-modal','true');wardrobe.setAttribute('aria-label','更衣室');wardrobe.innerHTML='<h2>换好衣服，再去海里玩</h2><div><button data-suit="swim">穿泳衣</button><button data-suit="wetsuit">穿潜水服</button><button data-suit="clothes">换回便装</button><button data-cancel>先不换</button></div>';
canvas.parentElement.append(wardrobe);
function leaveCabana(kind){if(kind){state.suit=kind;toast('换上了'+SUIT_NAME[kind]+'～');}state.inCabana=false;wardrobe.hidden=true;state.x=DATA.cabana.wetsuit;state.y=standY(state.x);goTo(DATA.cabana.wetsuit+16,'walk');canvas.focus();}
wardrobe.querySelectorAll('[data-suit]').forEach(b=>b.onclick=()=>leaveCabana(b.dataset.suit));wardrobe.querySelector('[data-cancel]').onclick=()=>leaveCabana(null);
function enterCabana(){goTo(DATA.cabana.swim,'walk',0,()=>{state.inCabana=true;state.target=null;wardrobe.hidden=false;wardrobe.querySelector('button').focus();});}
// ------------------------------------------------------------- input
function pick(x,y){
 if(state.market){if(market?.pick(x,y))return;return goTo(x);}
 if(state.lying!==null){state.lying=null;toast('站起来活动活动～',1.5);}
 const g=gr(x);
 if(Math.abs(x-DATA.lodgeDoor)<16&&y>g-42&&y<g+5)return enter();
 if(x>=DATA.cabanaBounds[0]&&x<=DATA.cabanaBounds[1]&&y>g-77&&y<g+12)return enterCabana();
 for(const [i,[lx,ly]]of DATA.chairs.entries())if(Math.abs(x-lx)<14&&y>ly-32&&y<ly+3)return goTo(lx,'walk',0,()=>{state.lying=i;toast('坐在沙滩椅上吹海风，好惬意～');});
 for(const c of DATA.life)if(c.cx&&Math.abs(x-c.cx)<c.w/2+5&&Math.abs(y-c.cy)<c.h/2+5){
  if(state.suit==='clothes')return toast('先去更衣室换上泳装，才能游过去看看。');
  return goTo(c.cx,'dive',c.cy,()=>{if(Math.hypot(c.cx-state.x,c.cy-state.y+10)<40){if(photo)photo(c);else discover('life:'+c.k,DATA.lifeText[c.k]);}else toast('它游走了……');});}
 for(const h of DATA.hotspots)if(Math.abs(x-h.x)<14&&Math.abs(y-h.y)<14){
  if(state.suit==='clothes')return toast('那是「'+h.name+'」，换上泳装就能去看看。');
  const surf=h.id==='seal_rock';return goTo(h.x-(surf?14:0),surf?'walk':'dive',h.y,()=>discover(h.id,'「'+h.name+'」'+h.text));}
 if(y>WL+16&&deep(x)&&state.suit!=='clothes')return goTo(x,'dive',Math.min(y,g-4));
 goTo(x);}
DATA.zones.forEach(([x,name])=>{const b=document.createElement('button');b.textContent=name;b.onclick=()=>{state.door=null;state.market=false;state.inCabana=false;wardrobe.hidden=true;state.inside=false;state.target=null;state.lying=null;
 let nx=x+60;if(state.suit==='clothes'&&gr(nx)>WL+5){nx=x;toast('换上泳装才能下水哦。');}state.x=nx;state.y=standY(nx)>SURF_Y?SURF_Y:standY(nx);state.camX=clamp(state.x-VW/2,0,W-VW);canvas.focus();};maps.append(b);});
document.getElementById('gender').onclick=e=>{state.gender=state.gender==='f'?'m':'f';e.target.textContent=state.gender==='f'?'换成男生':'换成女生';canvas.focus();};
document.getElementById('exit').onclick=leave;
document.getElementById('pause').onclick=e=>{state.paused=!state.paused;e.target.textContent=state.paused?'继续':'暂停';e.target.setAttribute('aria-pressed',String(state.paused));};
canvas.addEventListener('pointerdown',e=>{canvas.focus();const r=canvas.getBoundingClientRect(),sx=(e.clientX-r.left)*VW/r.width,sy=(e.clientY-r.top)*canvas.height/r.height;
 if(state.changing>0||state.inCabana||state.door)return;if(!state.inside&&sy>canvas.height*.56-20&&sy<canvas.height*.56+20&&(sx<25||sx>VW-25)){travel(sx<25?-1:1);return;}if(state.inside){if(sx<43&&sy>55)return leave();goTo(clamp(sx,46,312));return;}pick(sx+state.camX,sy+state.camY);});
window.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','a','d','w','s','A','D','W','S'].includes(e.key)&&!['BUTTON','INPUT'].includes(document.activeElement.tagName)){e.preventDefault();keys.add(e.key);state.lying=null;}});
window.addEventListener('keyup',e=>keys.delete(e.key));window.addEventListener('blur',()=>keys.clear());
load(DATA);Promise.all([...images.values()].map(im=>im.decode())).then(()=>{
 const mc=document.createElement('canvas');mc.width=W;mc.height=H;const m=mc.getContext('2d');m.drawImage(img(DATA.solid),0,0);
 const d=m.getImageData(0,0,W,H).data;solid=new Uint8Array(W*H);for(let i=0;i<W*H;i++)solid[i]=d[i*4+3];
 solidSum=new Uint32Array((W+1)*(H+1));for(let y=0;y<H;y++){let row=0;for(let x=0;x<W;x++){row+=solid[y*W+x]>0?1:0;solidSum[(y+1)*(W+1)+x+1]=solidSum[y*(W+1)+x+1]+row;}}
 state.y=standY(state.x);state.loaded=true;ctx.imageSmoothingEnabled=false;toast('先去更衣室换上泳装，再去海里玩吧～ 发光的小星星是可以探索的地方。',5);
 let last=performance.now();function frame(now){const dt=document.hidden?0:clamp((now-last)/1000,0,.05);last=now;if(!state.paused)state.time+=dt;advanceDoor(dt);fx.tickWater(state.paused?0:dt);move(dt);camera(dt);draw();updateUI();requestAnimationFrame(frame);}requestAnimationFrame(frame);})
 .catch(e=>{const el=document.getElementById('error');el.hidden=false;el.textContent='地图加载失败，请刷新重试';console.error(e);});
window.summerPreview={state,seaLife:DATA.life,plants:DATA.plants,kelp:DATA.kelp,goTo,pick,move,camera,draw,gr,deep,isSolid,enterCabana,leaveCabana,travel,wardrobe,enter,leave,advanceDoor,fx,setWeather:kind=>wetKind=weatherOverride||kind,getWeather:()=>wetKind,setPeopleRenderer:fn=>peopleRenderer=fn,setMarket:m=>market=m,beginDoor,setPhoto:f=>photo=f,discover,hotspots:DATA.hotspots,data:DATA,lifeText:DATA.lifeText,toast};
