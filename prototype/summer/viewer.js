'use strict';
// Summer bay walk-through: one seamless map 旅舍 -> 更衣室 -> 沙滩 -> 水底.
// Walk on land, swim at the surface, click under water to dive; the view grows
// to twice the height while Buddy is in the sea and the camera eases after her.
const DATA=/*__DATA__*/null;
const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d'),images=new Map();
const {W,H,WL,ground}=DATA,VW=342,LAND_H=118,SEA_H=236,SURF_Y=WL+12;
const state={x:120,y:0,target:null,after:null,facing:1,camX:0,camY:0,viewH:LAND_H,time:0,paused:false,inside:false,walk:false,loaded:false,suit:null};
const keys=new Set(),maps=document.getElementById('maps'),status=document.getElementById('status');
const reduced=matchMedia('(prefers-reduced-motion:reduce)').matches;
function load(o){if(typeof o==='string'&&o.startsWith('data:image/')){if(!images.has(o)){const im=new Image();images.set(o,im);im.src=o;}return;}if(o&&typeof o==='object')Object.values(o).forEach(load);}
const img=s=>images.get(s);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const gr=x=>ground[clamp(Math.round(x),0,W-1)];
const deep=x=>gr(x)>WL+24;                    // deep enough to dive
const standY=x=>gr(x)<WL+8?gr(x):SURF_Y;      // feet on sand while wading, then float
const inSea=()=>state.y>WL+2;
const under=()=>state.y>SURF_Y+3;
function shoreX(){for(let x=0;x<W;x++)if(gr(x)>=WL+8)return x;return W;}
const SHORE=shoreX();
state.y=standY(state.x);
function zoneName(){if(state.inside)return '旅舍里';let n=DATA.zones[0][1];for(const [x,name]of DATA.zones)if(state.x>=x)n=name;return n+(under()?' · 潜水中':inSea()?' · 水面':'');}
function goTo(x,kind='walk',y=0,after=null){state.target={x:clamp(x,10,W-24),y,kind};state.after=after;}
function enterLodge(){goTo(DATA.lodgeDoor,'walk',0,()=>{state.inside=true;state.x=150;updateUI();});}
function leaveLodge(){state.inside=false;state.x=DATA.lodgeDoor;state.y=standY(state.x);updateUI();}
function updateUI(){status.textContent=zoneName()+(state.suit?' · '+state.suit:'');document.getElementById('exit').hidden=!state.inside;
 [...maps.children].forEach((b,i)=>{const z=DATA.zones[i],nx=DATA.zones[i+1];b.setAttribute('aria-current',String(!state.inside&&state.x>=z[0]&&(!nx||state.x<nx[0])));});}
function step(px,py,tx,ty,sp){const dx=tx-px,dy=ty-py,d=Math.hypot(dx,dy);if(d<=sp)return [tx,ty,true];return [px+dx/d*sp,py+dy/d*sp,false];}
function move(dt){state.walk=false;if(state.paused||!state.loaded)return;
 if(state.inside){if(state.target){const [x,,done]=step(state.x,0,state.target.x,0,dt*42);state.walk=!done;if(Math.abs(state.target.x-state.x)>.1)state.facing=Math.sign(state.target.x-state.x);state.x=x;if(done)state.target=null;}return;}
 const dir=(keys.has('ArrowRight')||keys.has('d')||keys.has('D')?1:0)-(keys.has('ArrowLeft')||keys.has('a')||keys.has('A')?1:0);
 const vdir=(keys.has('ArrowDown')||keys.has('s')||keys.has('S')?1:0)-(keys.has('ArrowUp')||keys.has('w')||keys.has('W')?1:0);
 if(dir||vdir){state.after=null;if((vdir>0||under())&&deep(state.x+dir*20))goTo(state.x+dir*30,'dive',clamp(state.y+vdir*30,SURF_Y,gr(state.x)-4));else goTo(state.x+dir*40);}
 const t=state.target;if(!t)return;
 if(Math.abs(t.x-state.x)>.5)state.facing=Math.sign(t.x-state.x);
 let done=false;
 if(t.kind==='dive'){
  if(!deep(state.x)&&!under()){                                  // still on land / in the shallows: head out along the surface
   const [x]=step(state.x,0,t.x,0,dt*(inSea()?30:42));state.x=x;state.y+=(standY(state.x)-state.y)*Math.min(1,dt*10);
  }else{const ty=clamp(t.y,SURF_Y,gr(t.x)-4);let [x,y,ok]=step(state.x,state.y,t.x,ty,dt*30);y=clamp(y,SURF_Y,gr(x)-4);state.x=x;state.y=y;done=ok;}
 }else if(under()){                                              // surface first, heading for the target (or the shore)
  const tx=gr(t.x)<WL+8?Math.max(SHORE,Math.min(state.x,t.x)):t.x;const [x,y]=step(state.x,state.y,tx,SURF_Y,dt*30);state.x=x;state.y=Math.min(y,gr(x)-4);
 }else{const [x,,ok]=step(state.x,0,t.x,0,dt*(inSea()?30:42));state.x=x;state.y+=(standY(state.x)-state.y)*Math.min(1,dt*10);done=ok&&Math.abs(state.y-standY(state.x))<1;}
 state.walk=true;
 if(done){state.target=null;state.walk=false;if(state.after){const f=state.after;state.after=null;f();}}
}
function camera(dt){const k=Math.min(1,dt*3);                     // slow, smooth follow
 const wantH=inSea()&&gr(state.x)>WL+8?SEA_H:LAND_H;state.viewH+=(wantH-state.viewH)*Math.min(1,dt*4);
 const vh=Math.round(state.viewH);if(canvas.height!==vh){canvas.height=vh;ctx.imageSmoothingEnabled=false;}
 state.camX+=(clamp(state.x-VW/2,0,W-VW)-state.camX)*k;
 const wantY=wantH===LAND_H?clamp(gr(state.x)-104,0,H-vh):clamp(state.y-vh/2,0,H-vh);
 state.camY+=(wantY-state.camY)*k;state.camY=clamp(state.camY,0,H-vh);}
function hero(x,y){const t=state.time,f=state.walk&&!inSea()?Math.floor(t*7)%4:0;ctx.save();ctx.translate(Math.round(x),Math.round(y));
 if(under()){ctx.translate(0,-10);ctx.rotate(state.facing*1.35+Math.sin(t*4)*.06);ctx.scale(state.facing,1);ctx.drawImage(img(DATA.hero),0,0,20,28,-10,-14,20,28);}
 else{ctx.scale(state.facing,1);ctx.drawImage(img(DATA.hero),f*20,0,20,28,-10,-28+(inSea()&&gr(state.x)>=WL+8?Math.round(Math.sin(t*3)):0),20,28);}
 ctx.restore();}
function draw(){const vh=canvas.height;ctx.fillStyle='#eee8dd';ctx.fillRect(0,0,VW,vh);if(!state.loaded)return;
 const t=reduced?0:state.time;
 if(state.inside){ctx.fillStyle='#2f2a33';ctx.fillRect(0,0,VW,vh);ctx.drawImage(img(DATA.inside),40,28);hero(clamp(state.x,46,296),78);return;}
 const cx=Math.round(state.camX),cy=Math.round(state.camY);
 ctx.drawImage(img(DATA.bg),cx,cy,VW,vh,0,0,VW,vh);
 ctx.save();ctx.translate(-cx,-cy);
 for(let i=0;i<20;i++){const c=img(DATA.clouds[i%3]),x=((i*113+t*(1.2+i%4*.5))%(W+60))-40,y=4+(i*17)%36;if(y+c.height<WL-8)ctx.drawImage(c,Math.round(x),y);}
 for(const c of DATA.life){const ph=t*c.v/Math.max(1,c.r),x=c.x+Math.sin(ph)*c.r,goingLeft=Math.cos(ph)<0,im=img(c.f[Math.floor(t*3+c.x)%2]);
  ctx.save();ctx.translate(Math.round(x),Math.round(c.y+Math.sin(t*.7+c.x)*2));if(goingLeft){ctx.scale(-1,1);ctx.drawImage(im,-im.width,0);}else ctx.drawImage(im,0,0);ctx.restore();}
 hero(state.x,state.y);
 if(inSea()&&!under()){ctx.fillStyle='rgba(120,190,215,.45)';ctx.fillRect(Math.round(state.x)-11,WL+1,22,Math.round(state.y)-WL);}  // body under the surface
 if(under()&&!reduced){ctx.fillStyle='#e8f6fb';for(let k=0;k<3;k++){const p=(t*.8+k/3)%1;ctx.fillRect(Math.round(state.x+state.facing*6+Math.sin(p*9)*2),Math.round(state.y-14-p*26),1+(k===0),1+(k===0));}}
 ctx.restore();}
DATA.zones.forEach(([x,name])=>{const b=document.createElement('button');b.textContent=name;b.onclick=()=>{state.inside=false;state.target=null;state.x=x+60;state.y=standY(state.x);state.camX=clamp(state.x-VW/2,0,W-VW);canvas.focus();};maps.append(b);});
document.getElementById('exit').onclick=leaveLodge;
document.getElementById('pause').onclick=e=>{state.paused=!state.paused;e.target.textContent=state.paused?'继续':'暂停';e.target.setAttribute('aria-pressed',String(state.paused));};
canvas.addEventListener('pointerdown',e=>{canvas.focus();const r=canvas.getBoundingClientRect(),sx=(e.clientX-r.left)*VW/r.width,sy=(e.clientY-r.top)*canvas.height/r.height;
 if(state.inside){goTo(clamp(sx,46,296));return;}
 const x=sx+state.camX,y=sy+state.camY,g=gr(x);
 if(Math.abs(x-DATA.lodgeDoor)<12&&y>g-36&&y<g+2){enterLodge();return;}
 for(const [k,dx]of Object.entries(DATA.cabana))if(Math.abs(x-dx)<10&&y>g-34&&y<g+2){goTo(dx,'walk',0,()=>{state.suit=k==='bikini'?'换上了比基尼':'换上了潜水服';updateUI();});return;}
 if(y>WL+16&&deep(x))goTo(x,'dive',Math.min(y,g-4));else goTo(x);});
window.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','a','d','w','s','A','D','W','S'].includes(e.key)&&!['BUTTON','INPUT'].includes(document.activeElement.tagName)){e.preventDefault();keys.add(e.key);}});
window.addEventListener('keyup',e=>keys.delete(e.key));window.addEventListener('blur',()=>keys.clear());
load(DATA);Promise.all([...images.values()].map(im=>im.decode())).then(()=>{state.loaded=true;ctx.imageSmoothingEnabled=false;updateUI();let last=performance.now();
 function frame(now){const dt=document.hidden?0:Math.min(.05,(now-last)/1000);last=now;if(!state.paused)state.time+=dt;move(dt);camera(dt);draw();updateUI();requestAnimationFrame(frame);}requestAnimationFrame(frame);})
 .catch(e=>{const el=document.getElementById('error');el.hidden=false;el.textContent='地图加载失败，请刷新重试';console.error(e);});
window.summerPreview={state,goTo,move,camera,draw,gr,deep,SHORE};
