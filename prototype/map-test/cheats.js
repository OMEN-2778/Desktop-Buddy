// Deliberately injected only into /map-test/. No normal save or release hooks.
function installSeasonCheats(){
 const flags={hero:false,pets:false};
 function fillHero(){for(const k of Object.keys(sim.needs))sim.needs[k]=100;}
 function fillPets(){for(const p of petState.pets){for(const k of ['hunger','energy','company']){p.needs[k]=100;p.low[k]=0;}p.warned={};}}
 const box=document.createElement('div');box.className='season-cheats';box.innerHTML='<div class="label">季节地图测试 · 需求作弊</div><button type="button" data-fill>主角与宠物立即全满</button><label><input type="checkbox" data-lock="hero">主角需求全满且不掉</label><label><input type="checkbox" data-lock="pets">所有宠物需求全满且不掉</label>';
 document.querySelector('.console .box').prepend(box);
 box.querySelector('[data-fill]').onclick=()=>{fillHero();fillPets();};
 box.querySelectorAll('[data-lock]').forEach(el=>el.onchange=()=>{flags[el.dataset.lock]=el.checked;if(flags.hero)fillHero();if(flags.pets)fillPets();});
 const enforce=()=>{if(flags.hero)fillHero();if(flags.pets)fillPets();};
 const originalStep=step;step=function(...args){enforce();const r=originalStep(...args);enforce();return r;};
 const originalPets=tickPets;tickPets=function(...args){if(flags.pets)fillPets();const r=originalPets(...args);if(flags.pets)fillPets();return r;};
 return {flags,fillHero,fillPets,enforce};
}
