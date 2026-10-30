// Pure, game-minute pet state. No wall-clock catch-up and no save-file side effects.
// Up to two pets (user): s.pets, and s.pet is the one being looked at (s.sel). The
// game runs each pet's routine with s.sel pointed at it (withPet in pets.js).
const PetRules = (()=>{
 const DAY=1440,MAX=100,clamp=n=>Math.max(0,Math.min(MAX,n));
 const MAX_PETS=2,KEEP_DAYS=3;
 const withPet=s=>Object.defineProperty(s,'pet',{enumerable:false,configurable:true,
  get(){return this.pets[this.sel]??this.pets[0]??null;},
  set(v){const i=this.pets.indexOf(this.pet);if(v==null){if(i>=0)this.pets.splice(i,1);this.sel=0;}else if(i>=0)this.pets[i]=v;else{this.pets.push(v);this.sel=this.pets.length-1;}}});
 const fresh=(seed=Date.now())=>withPet({version:2,seed:seed>>>0,week:-1,offers:[],pets:[],sel:0,feeder:0,installed:false,matColor:'sage',banUntil:0,banWhy:'',sadUntil:0});
 function random(s){s.seed=(Math.imul(s.seed,1664525)+1013904223)>>>0;return s.seed/4294967296;}
 function weekly(s,t,breeds){const week=Math.floor(t/(7*DAY));if(s.week===week&&s.offers.length===12)return s.offers;s.week=week;s.offers=[];
  for(const species of ['cat','dog']){const list=breeds.filter(b=>b.species===species);for(let i=0;i<6;i++){const breed=list[Math.floor(random(s)*list.length)];s.offers.push({id:`${week}-${species}-${i}`,breed:breed.id,activity:random(s)<.5?'lazy':'active',attachment:random(s)<.5?'independent':'clingy'});}}return s.offers;
 }
 function refusal(s,t){if(s.banUntil>t)return 'ban';const live=s.pets.filter(p=>p.status!=='lost');if(live.some(p=>p.status==='pending'))return 'pending';if(live.length>=MAX_PETS)return 'occupied';return null;}
 // 放弃领养 (user): a pet that has lived here 3 days can go back to the shelter; no new pet for 7 days.
 // Its mat goes with it; with no pet left, the feeder and the mat are taken back too.
 const abandonable=(s,t)=>s.pets.filter(p=>p.status==='home'&&t>=p.arrivalAt+KEEP_DAYS*DAY);
 function abandon(s,p,t){const i=s.pets.indexOf(p);if(i<0||!abandonable(s,t).includes(p))return false;s.pets.splice(i,1);s.sel=Math.min(s.sel,Math.max(0,s.pets.length-1));
  s.banUntil=Math.max(s.banUntil,t+7*DAY);s.banWhy='abandon';if(!s.pets.some(q=>q.status!=='lost')){s.pets=[];s.sel=0;s.installed=false;s.feeder=0;}return true;}
 function adopt(s,offer,name,t){if(refusal(s,t)||!s.offers.some(o=>o.id===offer?.id))return false;name=[...String(name).trim()].slice(0,8).join('');if(!name)return false;
  const o=s.offers.find(o=>o.id===offer.id);s.pets=s.pets.filter(p=>p.status!=='lost');s.sel=Math.min(s.sel,Math.max(0,s.pets.length-1));
  s.pets.push({...o,uid:o.id+'@'+t,name,status:'pending',arrivalAt:t+DAY,affinity:30,needs:{hunger:100,energy:100,company:100},low:{hunger:0,energy:0,company:0},warned:{},motion:null,activityNow:'idle',nextEvent:t+DAY+120});s.installed=true;s.feeder=900;return true;
 }
 function restore(raw,breeds){const s=fresh();if(!raw||![1,2].includes(raw.version))return s;const ids=new Set(breeds.map(b=>b.id)),number=(n,d=0)=>Number.isFinite(n)?Math.max(0,n):d;
  s.seed=Number.isInteger(raw.seed)?raw.seed>>>0:s.seed;s.week=Number.isInteger(raw.week)?raw.week:-1;s.offers=(Array.isArray(raw.offers)?raw.offers:[]).filter(o=>ids.has(o?.breed)&&['lazy','active'].includes(o.activity)&&['independent','clingy'].includes(o.attachment)).slice(0,12);if(s.offers.length!==12)s.week=-1;
  for(const k of ['feeder','banUntil','sadUntil'])s[k]=number(raw[k]);s.feeder=Math.min(900,s.feeder);s.installed=!!raw.installed;s.matColor=['sage','blue','rose','cream','lilac','clay'].includes(raw.matColor)?raw.matColor:'sage';
  s.banWhy=raw.banWhy==='abandon'?'abandon':'';
  for(const p of (raw.version===1?[raw.pet]:Array.isArray(raw.pets)?raw.pets:[]).slice(0,MAX_PETS))if(p&&ids.has(p.breed)&&['pending','home','away','lost'].includes(p.status)){
   const q={...p,uid:typeof p.uid==='string'&&p.uid?p.uid:String(p.id||'pet')+'@'+s.pets.length,name:[...String(p.name||'团子')].slice(0,8).join(''),needs:{},low:{},warned:p.warned&&typeof p.warned==='object'?p.warned:{},motion:null,activityNow:'idle',nextEvent:number(p.nextEvent)};s.pets.push(q);
   for(const k of ['hunger','energy','company']){q.needs[k]=clamp(number(p.needs?.[k],100));q.low[k]=number(p.low?.[k]);}
   for(const k of ['arrivalAt','returnAt','escapedAt'])q[k]=number(p[k]);q.position=p.position&&Number.isFinite(p.position.x)&&Number.isFinite(p.position.y)?{x:p.position.x,y:p.position.y}:null;q.interaction=null;q.reservedUntil=0;q.affinity=clamp(number(p.affinity,30));q.carried=p.carried===true;q.walk=p.walk&&['front','park','beach'].includes(p.walk.dest)&&['departing','active'].includes(p.walk.phase)?{dest:p.walk.dest,phase:p.walk.phase,startedAt:number(p.walk.startedAt),until:number(p.walk.until),position:null}:null;q.willReturn=p.willReturn===true;q.activity=p.activity==='active'?'active':'lazy';q.attachment=p.attachment==='clingy'?'clingy':'independent';
  }s.sel=Math.max(0,Math.min(s.pets.length-1,Number.isInteger(raw.sel)?raw.sel:0));return s;
 }
 function escape(s,t,emit,p=s.pet){p.status='away';p.walk=null;p.carried=false;p.escapedAt=t;p.returnAt=t+2*DAY;p.willReturn=random(s)<.5;p.motion=null;s.banUntil=t+7*DAY;s.sadUntil=t+2*DAY;emit('escape',p);}
 function tick(s,from,to,context,emit=()=>{}){if(!(to>from)||!s.pet)return;
  // One-minute integration keeps fast sleep and ordinary speed equivalent.
  for(let t=from;t<to;){const end=Math.min(to,t+1),dt=end-t,p=s.pet;t=end;
   if(p.status==='pending'){if(t>=p.arrivalAt){p.status='home';p.nextEvent=t+90;emit('arrival',p);}continue;}
   if(p.status==='away'){if(t>=p.returnAt){p.status=p.willReturn?'home':'lost';p.motion=null;p.activityNow='idle';if(p.willReturn){p.needs={hunger:45,energy:45,company:45};p.low={hunger:0,energy:0,company:0};p.warned={};}emit(p.willReturn?'return':'lost',p);}continue;}
   if(p.status!=='home')continue;
   const n=p.needs;n.hunger=clamp(n.hunger-dt/18);const sleeping=['sleep','rest','lie_down'].includes(p.activityNow);
   n.energy=clamp(n.energy+dt*(sleeping?.28:-(p.activity==='active'?.055:.04)));
   n.company=clamp(n.company+dt*(context.nearby?.085:-(p.attachment==='clingy'?.045:.026)*(context.pal?.6:1)));   // a second pet at home keeps it some company
   if(p.activityNow==='eat'&&context.atFeeder&&s.feeder>0){const food=Math.min(s.feeder,dt*4,100-n.hunger);s.feeder-=food;n.hunger=clamp(n.hunger+food);}
   for(const k of Object.keys(n)){
    if(n[k]<10)p.low[k]+=dt;else p.low[k]=0;
    if(n[k]<20&&!p.warned[k]){p.warned[k]=true;emit('warning:'+k,p);}if(n[k]>=25)delete p.warned[k];
    if(p.low[k]>=DAY){escape(s,t,emit,p);break;}
   }
  }
 }
 return {DAY,MAX_PETS,KEEP_DAYS,fresh,random,weekly,refusal,adopt,restore,tick,escape,abandonable,abandon};
})();
if(typeof module!=='undefined')module.exports=PetRules;
