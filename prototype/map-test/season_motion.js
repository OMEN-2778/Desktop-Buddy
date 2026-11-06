// UI 动效对标 iOS（owner 2026-11-06：“所有 UI 动效更丝滑，对标苹果 iOS”；丢丢平板要看得出是平板，和任务面板一样大）。
//  - 面板（social sheet：小摊、图鉴、茵菲谷的田地/牧场/商店、平板……）：打开用 iOS 的弹簧曲线上浮放大，关闭先淡出缩小再收起；
//  - 面板里切换分页（平板的 App、图鉴分类、小摊……）：只换内容，内容淡入上移，卡片依次落位，面板本身不再重新弹出；
//  - 按钮、卡片按下去缩一点，松手弹回（style.css → “iOS motion”）；
//  - 丢丢平板电脑：深色圆角边框、前置摄像头、状态栏（时间 / 信号 / 电量），App 图标式的导航；位置大小和任务面板一样（日记顶到房子底）。
(function(){
 const reduced=()=>matchMedia('(prefers-reduced-motion:reduce)').matches;
 let tok=0,lastTitle=null;
 // ---------------------------------------------------------------- open / switch
 const oOpen=openSocialSheet;openSocialSheet=function(title){
  const same=!socialSheet.hidden&&!socialSheet.classList.contains('ios-out')&&title===lastTitle;tok++;lastTitle=title;
  if(!same)for(const k of ['left','top','right','bottom','width','height'])socialSheet.style.removeProperty(k);   // the tablet's own box must not stay on the next panel
  const s=oOpen.apply(this,arguments);
  s.classList.toggle('ios-keep',same);   // a page change inside the same panel: no second pop
  requestAnimationFrame(()=>{if(s.hidden)return;
   const c=s.querySelector('.social-sheet-content');
   if(c&&same){const tgt=s.classList.contains('fu-pc')?c.querySelector('.fu-main'):c;tgt?.classList.remove('ios-swap');void tgt?.offsetWidth;tgt?.classList.add('ios-swap');}
   stagger(s);if(s.classList.contains('fu-pc'))tablet(s);});
  return s;};
 // cards and tiles settle one after another (capped, so a long list is not slow)
 function stagger(s){let k=0;for(const el of s.querySelectorAll('.st-card,.st-slot,.dex-tile,.fu-stats>div,.fu-ledger li,.fu-stages li,.fu-cell,.st-banner,.fu-plant-top,.fu-ranch-body,.fu-balance'))el.style.setProperty('--k',Math.min(12,k++));}
 // ---------------------------------------------------------------- close: fade and shrink, then hide
 const oClose=closeSocialSheet;closeSocialSheet=function(){
  if(socialSheet.hidden||reduced()||socialSheet.classList.contains('ios-out'))return oClose.apply(this,arguments);
  const t=++tok,args=arguments,pc=socialSheet.classList.contains('fu-pc');if(pc)fromHero(socialSheet);socialSheet.classList.add('ios-out');socialSheet.inert=true;
  setTimeout(()=>{socialSheet.inert=false;if(t!==tok){socialSheet.classList.remove('ios-out');return;}socialSheet.classList.remove('ios-out');oClose.apply(this,args);},pc?280:240);};
 // ---------------------------------------------------------------- 丢丢平板电脑
 const APP={farm:'#7fcf8a',coin:'#f4c95d',fund:'#7fb8ee',gift:'#f2a0c2'};
 function tablet(s){
  if(!s.querySelector('.pc-screen')){const scr=document.createElement('div');scr.className='pc-screen';
   const bar=document.createElement('div');bar.className='pc-status';bar.innerHTML='<time></time><b>丢丢平板</b><span class="pc-sig"><i></i><i></i><i></i></span><span class="pc-bat"><i></i></span>';
   const c=s.querySelector('.social-sheet-content');if(!c)return;s.insertBefore(scr,c);scr.append(bar,c);
   const cam=document.createElement('i');cam.className='pc-cam';s.append(cam);}
  s.querySelectorAll('.fu-nav button').forEach((b,i)=>{b.style.setProperty('--app',Object.values(APP)[i]||'#ccc');});
  clock();placeTablet(s);fromHero(s);}
 // owner 2026-11-06: 平板从小人身上弹出来，关上时缩回她身上
 function fromHero(s){try{const v=document.getElementById('view'),c=ringCenter(),vr=v.getBoundingClientRect(),r=s.getBoundingClientRect();if(!vr.width||!r.width)return;
  const x=vr.left+c.x*vr.width/342,y=vr.top+c.y*vr.height/v.height;s.style.transformOrigin=`${Math.round(x-r.left)}px ${Math.round(y-r.top)}px`;}catch(e){}}
 const clock=()=>{const t=socialSheet.querySelector('.pc-status time');if(t)t.textContent=fmt(sim.t);};
 setInterval(()=>{if(!socialSheet.hidden&&socialSheet.classList.contains('fu-pc'))clock();},500);
 // the quest panel's box: from the diary's top to the house's bottom, right of the diary circle
 function placeTablet(s){const diary=document.getElementById('diaryBox')||document.querySelector('.diary'),v=document.getElementById('view'),par=s.offsetParent;
  if(!diary||!v||!par)return;const dr=diary.getBoundingClientRect(),vr=v.getBoundingClientRect(),pr=par.getBoundingClientRect();if(!dr.width||!vr.width)return;
  const left=dr.left-6-pr.left,top=dr.top-6-pr.top;
  Object.assign(s.style,{left:left+'px',top:top+'px',right:'auto',bottom:'auto',width:(vr.right-pr.left-left)+'px',height:(vr.bottom-pr.top-top+6)+'px'});}
 addEventListener('resize',()=>{if(!socialSheet.hidden&&socialSheet.classList.contains('fu-pc'))placeTablet(socialSheet);});
 // ---------------------------------------------------------------- the pick-a-thing panel and quest cards: same press feel (CSS)
})();
// ---------------------------------------------------------------- sounds (owner 2026-11-06: 春天、夏天的新 UI 都要有音效)
// The game's UI sounds (ui-open / ui-close / ui-click, audio.js) are looked up through RECORDED_FOLEY: in the season maps
// they become the map's own (AUDIO_LIBRARY/tools/build_season_ui_sfx.py): 茵菲谷 wood, 丢丢平板 glass, 草帽湾 ukulele / steel drum / bubble.
(function(){
 if(typeof RECORDED_FOLEY==='undefined')return;
 let lastDown=null;addEventListener('pointerdown',e=>{lastDown=e.target;},true);
 const where=()=>sim.place==='spring_test'?'infei':sim.place==='summer_test'?'bay':null;
 const pad=()=>!socialSheet.hidden&&socialSheet.classList.contains('fu-pc');
 let padClosing=0;const oc=closeSocialSheet;closeSocialSheet=function(){if(!socialSheet.hidden&&socialSheet.classList.contains('fu-pc'))padClosing=performance.now();return oc.apply(this,arguments);};
 const tab=()=>!!lastDown?.closest?.('.fu-nav button,.fu-tabs button,.dex-tab,[role=tab]');
 const pick={
  'ui-open':()=>{const w=where();return !w?null:pad()?'pad-on':w+'-ui-open';},
  'ui-close':()=>{const w=where();return !w?null:performance.now()-padClosing<800?'pad-off':w+'-ui-close';},
  'ui-click':()=>{const w=where();if(!w)return null;if(lastDown?.closest?.('.fu-pc'))return 'pad-tab';return w+(tab()?'-ui-tab':'-ui-click');}};
 for(const [id,f]of Object.entries(pick)){const keep=RECORDED_FOLEY[id];Object.defineProperty(RECORDED_FOLEY,id,{configurable:true,enumerable:true,get(){try{return f()||keep;}catch(e){return keep;}}});}
})();
