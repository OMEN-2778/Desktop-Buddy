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
