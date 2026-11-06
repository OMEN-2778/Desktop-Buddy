// 茵菲谷 panels in the 海棠集市 stall's look (owner 2026-11-05: "the summer stall UI is great, polish 茵菲谷's
// panels after it"). Same FarmUI panels and contents; while she is in 茵菲谷 they get class infei-ui and the stall's
// big-sheet frame (fitBig: from the diary row down to the house, scroll bar on the right). Styles: style.css .infei-ui.
(function(){
 const inSpring=()=>sim.place==='spring_test';
 const dress=s=>{if(!inSpring()||!s)return s;s.classList.add('infei-ui','fu-big-sheet');
  requestAnimationFrame(()=>{const L=window.summerLife,c=s.querySelector('.social-sheet-content');try{L?.fitBig(s);if(c&&!s.querySelector('.st-scroll'))L?.scrollBar(s,c);}catch(e){}});return s;};
 // every FarmUI panel (also a tab re-render inside one) goes through the one social sheet: watch its class
 const sh=document.querySelector('.social-sheet');if(sh)new MutationObserver(()=>{if(sh.classList.contains('fu-sheet')&&!sh.classList.contains('infei-ui'))dress(sh);}).observe(sh,{attributes:true,attributeFilter:['class']});
 const oShop=FarmUI.shop;FarmUI.shop=function(){const r=oShop.apply(this,arguments);document.getElementById('picker')?.classList.toggle('infei-ui',inSpring());return r;};
 const oClose=closePicker;closePicker=function(){document.getElementById('picker')?.classList.remove('infei-ui');return oClose.apply(this,arguments);};
})();
// 种子铺 cards in the 草帽湾 stall look (owner 2026-11-06: 播种界面的 UI): the crop's picture on a cream tile, its name and a
// gold price tag, chips for growing days / regrowth / seasons, and what a basket sells for.
(function(){
 const SN=['春','夏','秋','冬'],SC=['st-spring','st-summer','st-autumn','st-winter'];
 const chip=(text,cls='')=>Object.assign(document.createElement('span'),{className:'seed-chip '+cls,textContent:text});
 const oShop=FarmUI.shop;FarmUI.shop=function(act,title,balance,goods){const r=oShop.apply(this,arguments);
  if(act!=='sf_seed')return r;const picker=document.getElementById('picker');picker.classList.add('seed-shop');
  const items=goods.flatMap(g=>g.items),CROP=springFarm.X.CROP||{};
  [...picker.querySelectorAll('.pk-item')].forEach((b,i)=>{const it=items[i],c=CROP[it?.crop];if(!it)return;
   const txt=b.querySelector('div');if(!txt)return;txt.className='seed-card';
   const top=document.createElement('div');top.className='seed-top';top.append(Object.assign(document.createElement('b'),{textContent:it.name}),chip(it.cost?`${it.cost} 币`:'免费','seed-price'));
   const chips=document.createElement('div');chips.className='seed-chips';
   if(c){chips.append(chip(`${c.days} 天成熟`,'seed-days'));if(c.regrow)chips.append(chip(`之后每 ${c.regrow} 天再收`,'seed-days'));for(const n of c.seasons)chips.append(chip(SN[n],SC[n]));}
   else if(it.info)chips.append(chip(it.info,'seed-days'));
   const line=Object.assign(document.createElement('small'),{textContent:c?`${c.regrow?'每收一次':'一筐'}约卖 ${c.sell} 币`:it.line||''});
   txt.replaceChildren(top,chips,line);b.style.setProperty('--k',i);});
  return r;};
 const oClose=closePicker;closePicker=function(){document.getElementById('picker')?.classList.remove('seed-shop');return oClose.apply(this,arguments);};
})();

