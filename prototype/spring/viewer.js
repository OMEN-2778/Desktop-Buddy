'use strict';
const DATA=/*__DATA__*/null;
const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d'),images=new Map();ctx.imageSmoothingEnabled=false;
const state={scene:0,x:80,y:103,target:null,route:[],camera:0,facing:1,time:0,paused:false,inside:false,walk:false,loaded:false,after:null};
let peopleRenderer=null;const fx=makeSeasonEffects();let wetKind='clear',weatherOverride=null;
const wxLabel=document.createElement('label');wxLabel.className='season-weather';wxLabel.innerHTML='天气 <select aria-label="地图测试天气"><option value="">跟随游戏</option><option value="clear">晴天</option><option value="rain">小雨</option><option value="storm">大雨</option><option value="snow">小雪</option><option value="blizzard">大雪</option></select>';canvas.parentElement.parentElement.querySelector('.controls').append(wxLabel);wxLabel.querySelector('select').onchange=e=>{weatherOverride=e.target.value||null;wetKind=weatherOverride||'clear';};
const keys=new Set(),maps=document.getElementById('maps'),status=document.getElementById('status');
const reduced=matchMedia('(prefers-reduced-motion:reduce)').matches;
function load(o){if(typeof o==='string'&&o.startsWith('data:image/')){if(!images.has(o)){const im=new Image();images.set(o,im);im.src=o;}return;}if(o&&typeof o==='object')Object.values(o).forEach(load);}
function image(src){return images.get(src);}function paint(src,x=0,y=0){if(src)ctx.drawImage(image(src),Math.round(x),Math.round(y));}
function current(){return DATA.scenes[state.scene];}
function go(index,entry=80){state.scene=Math.max(0,Math.min(DATA.scenes.length-1,index));state.inside=false;state.door=null;state.x=entry;state.y=103;state.target=null;state.route=[];state.after=null;state.camera=Math.max(0,Math.min(current().width-342,state.x-171));updateUI();}
function updateUI(){[...maps.children].forEach((b,i)=>b.setAttribute('aria-current',String(i===state.scene&&!state.inside)));status.textContent=state.inside?'农舍内部':current().id==='ranch'?(state.x<342?'果园':'牧场'):current().name;document.getElementById('prev').disabled=state.inside||state.scene===0;document.getElementById('next').disabled=state.inside||state.scene===DATA.scenes.length-1;document.getElementById('enter').hidden=state.inside||current().id!=='home';document.getElementById('exit').hidden=!state.inside;}
function target(x,y=103,after=null){state.route=[];state.after=after;if(state.inside&&Math.abs(y-state.y)>10)state.route=[{x:51,y:state.y},{x:51,y},{x,y}];else state.route=[{x,y}];state.target=state.route.shift();}
function enter(){target(182,103,()=>beginDoor(true));}
function leave(){if(state.inside)target(51,108,()=>beginDoor(false));}
function beginDoor(to){if(state.door)return;keys.clear();state.target=null;state.after=null;state.door={to,elapsed:0,duration:.65,mid:false};}
function advanceDoor(dt){const d=state.door;if(!d)return;d.elapsed+=dt;if(!d.mid&&d.elapsed>=d.duration/2){d.mid=true;state.inside=d.to;state.x=d.to?51:182;state.y=d.to?108:103;state.camera=0;updateUI();}if(d.elapsed>=d.duration)state.door=null;}
function exitArrow(){ctx.fillStyle='#e9eee2';ctx.fillRect(7,88,22,22);ctx.strokeStyle='#526578';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(22,93);ctx.lineTo(14,99);ctx.lineTo(22,105);ctx.stroke();}
function move(dt){state.walk=false;if(state.paused||!state.loaded||state.door)return;
 const dir=(keys.has('ArrowRight')||keys.has('d')||keys.has('D')?1:0)-(keys.has('ArrowLeft')||keys.has('a')||keys.has('A')?1:0);
 if(dir){state.after=null;state.route=[];state.target={x:state.x+dir*40,y:state.y};}
 const intentX=state.target?.x;
 if(state.target){const dx=state.target.x-state.x,dy=state.target.y-state.y,dist=Math.hypot(dx,dy),step=dt*(Math.abs(dy)>0?27:42);state.walk=dist>.1;if(Math.abs(dx)>.1)state.facing=Math.sign(dx);
 if(dist<=step){state.x=state.target.x;state.y=state.target.y;state.target=state.route.shift()||null;if(!state.target&&state.after){const f=state.after;state.after=null;f();}}
 else{state.x+=dx/dist*step;state.y+=dy/dist*step;}}
 if(!state.inside){const width=current().width;if(state.x>=width-14&&intentX>=width-14&&state.scene<DATA.scenes.length-1){go(state.scene+1,0);target(35);}else if(state.x<=14&&intentX<=14&&state.scene>0){const i=state.scene-1;go(i,DATA.scenes[i].width);target(state.x-35);}else state.x=Math.max(state.scene===0?10:-10,Math.min(width+(state.scene===DATA.scenes.length-1?-10:10),state.x));
 state.camera+= (Math.max(0,Math.min(width-342,state.x-171))-state.camera)*Math.min(1,dt*7);
 }else state.x=Math.max(37,Math.min(303,state.x));
 if(state.target&&((!state.inside&&((state.scene===0&&state.x<=10&&state.target.x<10)||(state.scene===DATA.scenes.length-1&&state.x>=current().width-10&&state.target.x>current().width-10)))||(state.inside&&((state.x<=37&&state.target.x<37)||(state.x>=303&&state.target.x>303))))){state.target=null;state.walk=false;}updateUI();}
function actor(){const frame=state.walk?Math.floor(state.time*7)%4:0;ctx.save();ctx.translate(Math.round(state.x),Math.round(state.y));ctx.scale(state.facing,1);ctx.drawImage(image(DATA.hero),frame*20,0,20,28,-10,-28,20,28);ctx.restore();}
function draw(){ctx.clearRect(0,0,342,120);ctx.fillStyle='#eee8dd';ctx.fillRect(0,0,342,120);if(!state.loaded)return;
 if(state.inside){paint(DATA.inside,27,0);actor();exitArrow();fx.transition(ctx,state.door,342,120);return;}
 const s=current(),t=reduced?0:state.time,w=s.width;ctx.save();ctx.translate(-state.camera,0);
 paint(s.sky);
 // Sky -> drifting clouds -> mountains/fields -> trees/buildings -> people.
 for(const offset of [0,-w,w])paint(s.clouds,(t*1.5)%w+offset,0);
 if(s.wind){const f=reduced?0:Math.floor(t/.04)%72;ctx.drawImage(image(s.wind),f*342,0,342,118,0,0,342,118);ctx.drawImage(image(s.cleanTop),0,0,342,58,0,0,342,58);}else paint(s.bg);
 if(s.id==='tulip'){const f=Math.floor(t/.04)%144;ctx.drawImage(image(DATA.sails),f*50,0,50,50,211,2,50,50);}
 if(s.id==='home')for(const [x,y,f,r]of DATA.coop)paint(DATA.chickens[(r?2:0)+(Math.floor(t*3+f)%2)],x+Math.sin(t*.6+x)*2,y-11);
 if(s.id==='ranch')for(const [kind,x,y,f]of DATA.herd){const im=DATA.animals[kind][Math.floor(t*1.4+f)%4];paint(im,342+x+Math.sin(t*.5+x)*2,y-image(im).height);}
 if(s.id==='tulip'&&!reduced){const a=Math.max(0,Math.sin((t%18)/18*Math.PI*2))**12;if(a>.01){ctx.globalAlpha=a*.12;paint(DATA.beam,90+(t%18)*6,0);ctx.globalAlpha=1;}}
 paint(s.trees[reduced?0:Math.sin(t*1.1)>0?1:0]);
 for(let i=0;i<(w>342?4:3);i++){const x=((70+i*116+t*(5+i))%(w+30))-15,y=12+i%3*6+Math.sin(t*.8+i)*2;paint(DATA.birds[Math.floor(t*6+i)%3],x,y);}
 for(let i=0;i<(w>342?5:3);i++)paint(DATA.butterflies[(i%2)*2+Math.floor(t*7+i)%2],65+i*100+Math.sin(t+i)*9,78+Math.sin(t*1.5+i)*4);
 paint(s.front);peopleRenderer?.(ctx,{region:state.scene,inside:state.inside,time:t});actor();ctx.restore();fx.weather(ctx,wetKind,t,342,120);drawTravelArrows();fx.transition(ctx,state.door,342,120);}
function drawTravelArrows(){if(state.inside)return;for(const [x,d,allowed]of [[12,-1,state.scene>0],[330,1,state.scene<5]]){if(!allowed)continue;ctx.fillStyle='rgba(247,246,251,.9)';ctx.fillRect(x-8,87,16,18);ctx.fillStyle='#5d6176';for(let i=0;i<5;i++){ctx.fillRect(x+d*(i-2),90+i,2,2);ctx.fillRect(x+d*(i-2),98-i,2,2);}}}
function travel(d){if(!state.inside&&((d<0&&state.scene>0)||(d>0&&state.scene<5)))target(d<0?0:current().width);}
for(const [i,s]of DATA.scenes.entries()){const b=document.createElement('button');b.textContent=s.name;b.onclick=()=>{go(i);canvas.focus();};maps.append(b);}
document.getElementById('prev').onclick=()=>{target(-12);canvas.focus();};document.getElementById('next').onclick=()=>{target(current().width+12);canvas.focus();};document.getElementById('enter').onclick=enter;document.getElementById('exit').onclick=leave;
document.getElementById('pause').onclick=e=>{state.paused=!state.paused;e.target.textContent=state.paused?'继续':'暂停';e.target.setAttribute('aria-pressed',String(state.paused));};
canvas.addEventListener('pointerdown',e=>{canvas.focus();const r=canvas.getBoundingClientRect(),x=(e.clientX-r.left)*342/r.width+state.camera,y=(e.clientY-r.top)*120/r.height;if(state.door)return;if(!state.inside&&y>83&&y<110&&(x-state.camera<25||x-state.camera>317)){travel(x-state.camera<25?-1:1);return;}if(state.inside){if(x<39&&y>80)return leave();target(Math.max(39,Math.min(300,x)),y<65?50:108);return;}if(current().id==='home'&&Math.abs(x-182)<14&&y>62&&y<102){enter();return;}target(Math.max(-12,Math.min(current().width+12,x)));});
window.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','a','d','A','D'].includes(e.key)&&!['BUTTON','INPUT'].includes(document.activeElement.tagName)){e.preventDefault();keys.add(e.key);}});window.addEventListener('keyup',e=>keys.delete(e.key));window.addEventListener('blur',()=>keys.clear());document.addEventListener('visibilitychange',()=>{if(document.hidden)keys.clear();});
load(DATA);Promise.all([...images.values()].map(im=>im.decode())).then(()=>{state.loaded=true;updateUI();let last=performance.now();function frame(now){const dt=document.hidden?0:Math.min(.05,(now-last)/1000);last=now;if(!state.paused)state.time+=dt;advanceDoor(state.paused?0:dt);move(dt);draw();requestAnimationFrame(frame);}requestAnimationFrame(frame);}).catch(e=>{const el=document.getElementById('error');el.hidden=false;el.textContent='地图加载失败，请刷新重试';console.error(e);});
window.springPreview={state,go,target,enter,leave,draw,move,travel,advanceDoor,fx,setWeather:kind=>wetKind=weatherOverride||kind,getWeather:()=>wetKind,setPeopleRenderer:fn=>peopleRenderer=fn};
