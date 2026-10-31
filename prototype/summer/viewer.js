'use strict';
// Summer bay walk-through: one seamless map 旅舍 -> 更衣室 -> 沙滩 -> 水底.
// Walk on land; change at the cabana (clothes can only wade); swim at the
// surface; click under water to dive (snorkel breath in swimwear, a tank in a
// wetsuit); rocks are solid, the arch has a hole; discover hotspots and sea life.
const DATA=/*__DATA__*/null;
const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d'),images=new Map();
const say=document.getElementById('say'),status=document.getElementById('status'),maps=document.getElementById('maps');
const {W,H,WL,ground}=DATA,VW=342,LAND_H=118,SEA_H=236,SURF_Y=WL+12,CELL=28;
const BREATH={clothes:0,swim:20,wetsuit:90},SUIT_NAME={clothes:'便装',swim:'泳衣',wetsuit:'潜水服'};
const TOTAL=DATA.hotspots.length+Object.keys(DATA.lifeText).length;
const state={x:120,y:0,vy:0,target:null,after:null,facing:1,camX:0,camY:0,viewH:LAND_H,time:0,paused:false,inside:false,walk:false,loaded:false,
 suit:'clothes',gender:'f',breath:0,lying:null,changing:0,found:new Set(),wasSea:false,warned:0};
const keys=new Set(),parts=[];
const reduced=matchMedia('(prefers-reduced-motion:reduce)').matches;
let solid=null;
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
function zoneName(){if(state.inside)return '旅舍里';let n=DATA.zones[0][1];for(const [x,name]of DATA.zones)if(state.x>=x)n=name;return n+(under()?' · 潜水中':inSea()?' · 水里':'');}
function updateUI(){status.textContent=`${zoneName()} · ${SUIT_NAME[state.suit]} · 发现 ${state.found.size}/${TOTAL}`;document.getElementById('exit').hidden=!state.inside;
 [...maps.children].forEach((b,i)=>{const z=DATA.zones[i],nx=DATA.zones[i+1];b.setAttribute('aria-current',String(!state.inside&&state.x>=z[0]&&(!nx||state.x<nx[0])));});}
function goTo(x,kind='walk',y=0,after=null){state.lying=null;state.target={x:clamp(x,LEFT,RIGHT),y,kind};state.after=after;}
function discover(id,text){const first=!state.found.has(id);state.found.add(id);toast((first?'✦ 新发现：':'')+text,4.2);}
function splash(x,y,n=10){for(let i=0;i<n;i++)parts.push({x:x+(Math.random()-.5)*8,y,vx:(Math.random()-.5)*30,vy:-20-Math.random()*30,life:.7,c:'#f4fbff',g:80});}
// ------------------------------------------------------------- movement
function step(px,py,tx,ty,sp){const dx=tx-px,dy=ty-py,d=Math.hypot(dx,dy);if(d<=sp)return [tx,ty,true];return [px+dx/d*sp,py+dy/d*sp,false];}
function walkTo(tx,dt){const sp=dt*(inSea()?30:42);let [x,,ok]=step(state.x,0,tx,0,sp);
 if(gr(x)>wadeLimit()){if(state.warned<=0){toast('穿着便装只能在浅水边踩踩水，先去更衣室换上泳装吧～');state.warned=6;}return true;}
 state.x=x;state.y+=(standY(state.x)-state.y)*Math.min(1,dt*10);return ok&&Math.abs(state.y-standY(state.x))<1;}
function swimTo(tx,ty,dt){                               // free swimming with rock collision (slides along walls)
 const [nx,ny,ok]=step(state.x,state.y,tx,ty,dt*30);let x=state.x,y=state.y;
 const free=(a,b)=>!isSolid(a,b)&&!isSolid(a,b-10)&&b>=SURF_Y&&a<=RIGHT;
 if(free(nx,ny)){x=nx;y=ny;}else if(free(nx,state.y)){x=nx;}else if(free(state.x,ny)){y=ny;}else return true;
 state.vy=(y-state.y)/Math.max(dt,1e-3);state.x=x;state.y=y;return ok;}
function move(dt){state.walk=false;if(state.paused||!state.loaded)return;
 state.warned-=dt;if(sayTimer>0&&(sayTimer-=dt)<=0)say.hidden=true;
 if(state.changing>0){state.changing-=dt;return;}
 if(state.inside){if(state.target){const [x,,done]=step(state.x,0,state.target.x,0,dt*42);state.walk=!done;if(Math.abs(state.target.x-state.x)>.1)state.facing=Math.sign(state.target.x-state.x);state.x=x;if(done)state.target=null;}return;}
 const dir=(keys.has('ArrowRight')||keys.has('d')||keys.has('D')?1:0)-(keys.has('ArrowLeft')||keys.has('a')||keys.has('A')?1:0);
 const vdir=(keys.has('ArrowDown')||keys.has('s')||keys.has('S')?1:0)-(keys.has('ArrowUp')||keys.has('w')||keys.has('W')?1:0);
 if(dir||vdir){state.after=null;if(state.suit!=='clothes'&&(under()||(vdir>0&&deep(state.x))))goTo(state.x+dir*30,'dive',state.y+vdir*30);else if(dir)goTo(state.x+dir*40);}
 // breath: a snorkel in swimwear, a tank in a wetsuit; refills at the surface
 const max=BREATH[state.suit];
 if(under()){state.breath-=dt;if(state.breath<=0&&state.target?.kind!=='up'){toast(state.suit==='swim'?'憋不住气了，先浮上去换口气！':'气瓶快空了，先浮上去！');state.target={x:state.x,y:SURF_Y,kind:'up'};state.after=null;}}
 else state.breath=Math.min(max,state.breath+dt*max/2);
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
 for(const c of DATA.life)if(c.k==='school'||c.k==='tang'){const dx=(c.cx||0)-state.x,dy=(c.cy||0)-(state.y-10),d=Math.hypot(dx,dy);if(d<28&&under()){c.ox=(c.ox||0)+dx/d*dt*60;c.oy=(c.oy||0)+dy/d*dt*40;}c.ox=(c.ox||0)*.985;c.oy=(c.oy||0)*.985;}
 for(const p of parts){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=p.g*dt;p.life-=dt;}for(let i=parts.length-1;i>=0;i--)if(parts[i].life<=0)parts.splice(i,1);
 if(under()&&!reduced&&Math.random()<dt*3)parts.push({x:state.x+state.facing*7,y:state.y-12,vx:(Math.random()-.5)*4,vy:-14,life:1.6,c:'#e8f6fb',g:-2});}
function camera(dt){const k=Math.min(1,dt*3);
 const wantH=(inSea()&&gr(state.x)>WL+8)||under()?SEA_H:LAND_H;state.viewH+=(wantH-state.viewH)*Math.min(1,dt*4);
 const vh=Math.round(state.viewH);if(canvas.height!==vh){canvas.height=vh;ctx.imageSmoothingEnabled=false;}
 state.camX+=(clamp(state.x-VW/2,0,W-VW)-state.camX)*k;
 const wantY=wantH===LAND_H?clamp(gr(clamp(state.x,0,W-1))-104,0,H-vh):clamp(state.y-vh/2,0,H-vh);
 state.camY=clamp(state.camY+(wantY-state.camY)*k,0,H-vh);}
// ------------------------------------------------------------- drawing
function cell(){const t=state.time;if(state.lying!==null)return 8;
 if(under())return 6+(state.walk?Math.floor(t*5)%2:Math.floor(t*1.5)%2);
 if(floating())return 4+(state.walk?Math.floor(t*4)%2:0);
 return state.walk?Math.floor(t*7)%4:0;}
function hero(x,y){if(state.changing>0)return;const sheet=img(DATA.heroes[state.gender][state.suit]),c=cell();ctx.save();ctx.translate(Math.round(x),Math.round(y));
 if(under()){ctx.translate(0,-14);ctx.rotate(clamp(state.vy/60,-.6,.6)*state.facing);ctx.translate(0,14);}
 if(c!==8)ctx.scale(state.facing,1);
 ctx.drawImage(sheet,c*CELL,0,CELL,CELL,-14,-28+(floating()?Math.round(Math.sin(state.time*3)):0),CELL,CELL);ctx.restore();}
function sparkle(x,y,t){const a=(Math.sin(t*3+x)+1)/2;if(a<.3)return;ctx.fillStyle=`rgba(255,250,220,${a})`;ctx.fillRect(x,y-2,1,5);ctx.fillRect(x-2,y,5,1);}
function draw(){const vh=canvas.height;ctx.fillStyle='#eee8dd';ctx.fillRect(0,0,VW,vh);if(!state.loaded)return;
 const t=reduced?0:state.time;
 if(state.inside){ctx.fillStyle='#2f2a33';ctx.fillRect(0,0,VW,vh);ctx.drawImage(img(DATA.inside),40,28);const sheet=img(DATA.heroes[state.gender][state.suit]),c=state.walk?Math.floor(state.time*7)%4:0;
  ctx.save();ctx.translate(Math.round(clamp(state.x,46,296)),78);ctx.scale(state.facing,1);ctx.drawImage(sheet,c*CELL,0,CELL,CELL,-14,-28,CELL,CELL);ctx.restore();return;}
 const cx=Math.round(state.camX),cy=Math.round(state.camY);
 ctx.drawImage(img(DATA.bg),cx,cy,VW,vh,0,0,VW,vh);
 ctx.save();ctx.translate(-cx,-cy);
 for(let i=0;i<20;i++){const c=img(DATA.clouds[i%3]),x=((i*113+t*(1.2+i%4*.5))%(W+60))-40,y=4+(i*17)%36;if(y+c.height<WL-8)ctx.drawImage(c,Math.round(x),y);}
 const sim=img(DATA.seal[Math.floor(t*.7)%2]);ctx.drawImage(sim,DATA.sealAt[0],DATA.sealAt[1]-sim.height);
 for(const h of DATA.hotspots)if(!state.found.has(h.id))sparkle(h.x,h.y,t);
 for(const c of DATA.life){const ph=t*c.v/Math.max(1,c.r),x=c.x+Math.sin(ph)*c.r+(c.ox||0),y=c.y+Math.sin(t*.7+c.x)*2+(c.oy||0),left=Math.cos(ph)<0,im=img(c.f[Math.floor(t*3+c.x)%2]);
  c.cx=x+im.width/2;c.cy=y+im.height/2;c.w=im.width;c.h=im.height;
  ctx.save();ctx.translate(Math.round(x),Math.round(y));if(left){ctx.scale(-1,1);ctx.drawImage(im,-im.width,0);}else ctx.drawImage(im,0,0);ctx.restore();}
 if(state.lying!==null){const [lx,ly]=DATA.chairs[state.lying];state.facing=1;hero(lx,ly);}else hero(state.x,state.y);
 if(floating()){ctx.fillStyle='rgba(120,190,215,.5)';ctx.fillRect(Math.round(state.x)-12,WL+1,24,Math.round(state.y)-WL);
  ctx.fillStyle='#f4fbff';const r=4+Math.round((t*6)%6);ctx.fillRect(Math.round(state.x)-r-4,WL,3,1);ctx.fillRect(Math.round(state.x)+r+2,WL,3,1);}   // ripples
 for(const p of parts){ctx.fillStyle=p.c;ctx.globalAlpha=clamp(p.life*1.5,0,1);ctx.fillRect(Math.round(p.x),Math.round(p.y),1,1);}ctx.globalAlpha=1;
 ctx.restore();
 if(under()&&BREATH[state.suit]){const f=clamp(state.breath/BREATH[state.suit],0,1);                 // breath / air
  ctx.fillStyle='rgba(30,50,70,.55)';ctx.fillRect(6,6,46,7);ctx.fillStyle=f<.25?'#e86b5a':'#bfe9f5';ctx.fillRect(8,8,Math.round(42*f),3);}}
// ------------------------------------------------------------- input
function pick(x,y){
 if(state.lying!==null){state.lying=null;toast('站起来活动活动～',1.5);}
 const g=gr(x);
 if(Math.abs(x-DATA.lodgeDoor)<12&&y>g-36&&y<g+2)return goTo(DATA.lodgeDoor,'walk',0,()=>{state.inside=true;state.x=150;toast('旅舍里：卧室、客厅、厨房和浴室。',2.5);});
 for(const [k,dx]of Object.entries(DATA.cabana))if(Math.abs(x-dx)<10&&y>g-34&&y<g+2)return goTo(dx,'walk',0,()=>{state.changing=1.1;const next=state.suit===k?'clothes':k;
  setTimeout(()=>{state.suit=next;state.breath=BREATH[next];toast(next==='clothes'?'换回了便装。':next==='swim'?'换上了泳衣！戴着浮潜面罩，能潜一小会儿。':'换上了潜水服！背着气瓶，可以下到深海沟。');},reduced?0:1000);});
 for(const [i,[lx,ly]]of DATA.chairs.entries())if(Math.abs(x-lx)<14&&y>ly-32&&y<ly+3)return goTo(lx,'walk',0,()=>{state.lying=i;toast('坐在沙滩椅上吹海风，好惬意～');});
 for(const c of DATA.life)if(c.cx&&Math.abs(x-c.cx)<c.w/2+5&&Math.abs(y-c.cy)<c.h/2+5){
  if(state.suit==='clothes')return toast('先去更衣室换上泳装，才能游过去看看。');
  return goTo(c.cx,'dive',c.cy,()=>{if(Math.hypot(c.cx-state.x,c.cy-state.y+10)<40)discover('life:'+c.k,DATA.lifeText[c.k]);else toast('它游走了……');});}
 for(const h of DATA.hotspots)if(Math.abs(x-h.x)<14&&Math.abs(y-h.y)<14){
  if(state.suit==='clothes')return toast('那是「'+h.name+'」，换上泳装就能去看看。');
  const surf=h.id==='seal_rock';return goTo(h.x-(surf?14:0),surf?'walk':'dive',h.y,()=>discover(h.id,'「'+h.name+'」'+h.text));}
 if(y>WL+16&&deep(x)&&state.suit!=='clothes')return goTo(x,'dive',Math.min(y,g-4));
 goTo(x);}
DATA.zones.forEach(([x,name])=>{const b=document.createElement('button');b.textContent=name;b.onclick=()=>{state.inside=false;state.target=null;state.lying=null;
 let nx=x+60;if(state.suit==='clothes'&&gr(nx)>WL+5){nx=x;toast('换上泳装才能下水哦。');}state.x=nx;state.y=standY(nx)>SURF_Y?SURF_Y:standY(nx);state.camX=clamp(state.x-VW/2,0,W-VW);canvas.focus();};maps.append(b);});
document.getElementById('gender').onclick=e=>{state.gender=state.gender==='f'?'m':'f';e.target.textContent=state.gender==='f'?'换成男生':'换成女生';canvas.focus();};
document.getElementById('exit').onclick=()=>{state.inside=false;state.x=DATA.lodgeDoor;state.y=standY(state.x);};
document.getElementById('pause').onclick=e=>{state.paused=!state.paused;e.target.textContent=state.paused?'继续':'暂停';e.target.setAttribute('aria-pressed',String(state.paused));};
canvas.addEventListener('pointerdown',e=>{canvas.focus();const r=canvas.getBoundingClientRect(),sx=(e.clientX-r.left)*VW/r.width,sy=(e.clientY-r.top)*canvas.height/r.height;
 if(state.changing>0)return;if(state.inside){state.target={x:clamp(sx,46,296)};return;}pick(sx+state.camX,sy+state.camY);});
window.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','a','d','w','s','A','D','W','S'].includes(e.key)&&!['BUTTON','INPUT'].includes(document.activeElement.tagName)){e.preventDefault();keys.add(e.key);state.lying=null;}});
window.addEventListener('keyup',e=>keys.delete(e.key));window.addEventListener('blur',()=>keys.clear());
load(DATA);Promise.all([...images.values()].map(im=>im.decode())).then(()=>{
 const mc=document.createElement('canvas');mc.width=W;mc.height=H;const m=mc.getContext('2d');m.drawImage(img(DATA.solid),0,0);
 const d=m.getImageData(0,0,W,H).data;solid=new Uint8Array(W*H);for(let i=0;i<W*H;i++)solid[i]=d[i*4+3];
 state.y=standY(state.x);state.loaded=true;ctx.imageSmoothingEnabled=false;toast('先去更衣室换上泳装，再去海里玩吧～ 发光的小星星是可以探索的地方。',5);
 let last=performance.now();function frame(now){const dt=document.hidden?0:clamp((now-last)/1000,0,.05);last=now;if(!state.paused)state.time+=dt;move(dt);camera(dt);draw();updateUI();requestAnimationFrame(frame);}requestAnimationFrame(frame);})
 .catch(e=>{const el=document.getElementById('error');el.hidden=false;el.textContent='地图加载失败，请刷新重试';console.error(e);});
window.summerPreview={state,goTo,pick,move,camera,draw,gr,deep,isSolid};
