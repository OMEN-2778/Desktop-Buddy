// Pure, game-minute pet state. No wall-clock catch-up and no save-file side effects.
const PetRules = (()=>{
 const DAY=1440,MAX=100,clamp=n=>Math.max(0,Math.min(MAX,n));
 const fresh=(seed=Date.now())=>({version:1,seed:seed>>>0,week:-1,offers:[],pet:null,feeder:0,installed:false,banUntil:0,sadUntil:0});
 function random(s){s.seed=(Math.imul(s.seed,1664525)+1013904223)>>>0;return s.seed/4294967296;}
 function weekly(s,t,breeds){const week=Math.floor(t/(7*DAY));if(s.week===week&&s.offers.length===12)return s.offers;s.week=week;s.offers=[];
  for(const species of ['cat','dog']){const list=breeds.filter(b=>b.species===species);for(let i=0;i<6;i++){const breed=list[Math.floor(random(s)*list.length)];s.offers.push({id:`${week}-${species}-${i}`,breed:breed.id,activity:random(s)<.5?'lazy':'active',attachment:random(s)<.5?'independent':'clingy'});}}return s.offers;
 }
 function refusal(s,t){if(s.banUntil>t)return 'ban';if(s.pet&&s.pet.status!=='lost')return 'occupied';return null;}
 function adopt(s,offer,name,t){if(refusal(s,t)||!s.offers.some(o=>o.id===offer?.id))return false;name=[...String(name).trim()].slice(0,8).join('');if(!name)return false;
  const o=s.offers.find(o=>o.id===offer.id);s.pet={...o,name,status:'pending',arrivalAt:t+DAY,needs:{hunger:100,energy:100,company:100},low:{hunger:0,energy:0,company:0},warned:{},motion:null,activityNow:'idle',nextEvent:t+DAY+120};s.installed=true;s.feeder=900;return true;
 }
 function restore(raw,breeds){const s=fresh();if(!raw||raw.version!==1)return s;const ids=new Set(breeds.map(b=>b.id)),number=(n,d=0)=>Number.isFinite(n)?Math.max(0,n):d;
  s.seed=Number.isInteger(raw.seed)?raw.seed>>>0:s.seed;s.week=Number.isInteger(raw.week)?raw.week:-1;s.offers=(Array.isArray(raw.offers)?raw.offers:[]).filter(o=>ids.has(o?.breed)&&['lazy','active'].includes(o.activity)&&['independent','clingy'].includes(o.attachment)).slice(0,12);if(s.offers.length!==12)s.week=-1;
  for(const k of ['feeder','banUntil','sadUntil'])s[k]=number(raw[k]);s.feeder=Math.min(900,s.feeder);s.installed=!!raw.installed;
  const p=raw.pet;if(p&&ids.has(p.breed)&&['pending','home','away','lost'].includes(p.status)){
   s.pet={...p,name:[...String(p.name||'团子')].slice(0,8).join(''),needs:{},low:{},warned:p.warned&&typeof p.warned==='object'?p.warned:{},motion:null,activityNow:'idle',nextEvent:number(p.nextEvent)};
   for(const k of ['hunger','energy','company']){s.pet.needs[k]=clamp(number(p.needs?.[k],100));s.pet.low[k]=number(p.low?.[k]);}
   for(const k of ['arrivalAt','returnAt','escapedAt'])s.pet[k]=number(p[k]);s.pet.position=p.position&&Number.isFinite(p.position.x)&&Number.isFinite(p.position.y)?{x:p.position.x,y:p.position.y}:null;s.pet.interaction=null;s.pet.reservedUntil=0;s.pet.willReturn=p.willReturn===true;s.pet.activity=p.activity==='active'?'active':'lazy';s.pet.attachment=p.attachment==='clingy'?'clingy':'independent';
  }return s;
 }
 function escape(s,t,emit){const p=s.pet;p.status='away';p.escapedAt=t;p.returnAt=t+2*DAY;p.willReturn=random(s)<.5;p.motion=null;s.banUntil=t+7*DAY;s.sadUntil=t+2*DAY;emit('escape',p);}
 function tick(s,from,to,context,emit=()=>{}){if(!(to>from)||!s.pet)return;
  // One-minute integration keeps fast sleep and ordinary speed equivalent.
  for(let t=from;t<to;){const end=Math.min(to,t+1),dt=end-t,p=s.pet;t=end;
   if(p.status==='pending'){if(t>=p.arrivalAt){p.status='home';p.nextEvent=t+90;emit('arrival',p);}continue;}
   if(p.status==='away'){if(t>=p.returnAt){p.status=p.willReturn?'home':'lost';p.motion=null;p.activityNow='idle';if(p.willReturn){p.needs={hunger:45,energy:45,company:45};p.low={hunger:0,energy:0,company:0};p.warned={};}emit(p.willReturn?'return':'lost',p);}continue;}
   if(p.status!=='home')continue;
   const n=p.needs;n.hunger=clamp(n.hunger-dt/18);const sleeping=['sleep','rest','lie_down'].includes(p.activityNow);
   n.energy=clamp(n.energy+dt*(sleeping?.28:-(p.activity==='active'?.055:.04)));
   n.company=clamp(n.company+dt*(context.nearby?.085:-(p.attachment==='clingy'?.045:.026)));
   if(p.activityNow==='eat'&&context.atFeeder&&s.feeder>0){const food=Math.min(s.feeder,dt*4,100-n.hunger);s.feeder-=food;n.hunger=clamp(n.hunger+food);}
   for(const k of Object.keys(n)){
    if(n[k]<10)p.low[k]+=dt;else p.low[k]=0;
    if(n[k]<20&&!p.warned[k]){p.warned[k]=true;emit('warning:'+k,p);}if(n[k]>=25)delete p.warned[k];
    if(p.low[k]>=DAY){escape(s,t,emit);break;}
   }
  }
 }
 return {DAY,fresh,random,weekly,refusal,adopt,restore,tick,escape};
})();
if(typeof module!=='undefined')module.exports=PetRules;
