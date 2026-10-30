// Deterministic boundary tests for adoption, neglect, returns and save continuity.
const assert=require('node:assert/strict'),P=require('../prototype/demo/pets_state.js');
const breeds=[...Array.from({length:12},(_,i)=>({id:'cat'+i,species:'cat'})),...Array.from({length:12},(_,i)=>({id:'dog'+i,species:'dog'}))];
const copy=x=>JSON.parse(JSON.stringify(x));
const create=(seed=12)=>{const s=P.fresh(seed);P.weekly(s,0,breeds);assert(P.adopt(s,s.offers[0],'团子',0));return s;};
const near=(a,b)=>assert(Math.abs(a-b)<1e-6,`${a} != ${b}`);
let s=P.fresh(12),list=copy(P.weekly(s,0,breeds));assert.equal(list.length,12);assert.equal(list.filter(o=>o.breed.startsWith('cat')).length,6);assert.equal(list.filter(o=>o.breed.startsWith('dog')).length,6);assert.deepEqual(P.weekly(s,10079,breeds),list);s=P.restore(copy(s),breeds);assert.deepEqual(P.weekly(s,3000,breeds),list);assert.notDeepEqual(P.weekly(s,10080,breeds),list);
assert(!P.adopt(s,s.offers[0],' ',10080));assert(P.adopt(s,s.offers[0],'豆豆',10080));assert(!P.adopt(s,s.offers[1],'第二只',10080));assert.equal(s.feeder,900);assert(s.installed);let events=[];
P.tick(s,10080,11519,{},x=>events.push(x));assert.equal(s.pet.status,'pending');P.tick(s,11519,11520,{},x=>events.push(x));assert.equal(s.pet.status,'home');assert.deepEqual(events,['arrival']);
s.pet.activityNow='idle';s.pet.needs.hunger=100;s.feeder=0;P.tick(s,11520,13320,{nearby:true},()=>{});near(s.pet.needs.hunger,0);assert.equal(s.pet.status,'home');
s=create();P.tick(s,0,1440,{});s.pet.needs={hunger:55,energy:80,company:80};s.pet.activityNow='eat';P.tick(s,1440,1450,{atFeeder:true,nearby:true});near(s.pet.needs.hunger,55-10/18+40);near(s.feeder,860);
s.feeder=1;s.pet.needs.hunger=30;P.tick(s,1450,1451,{atFeeder:true});near(s.feeder,0);near(s.pet.needs.hunger,30-1/18+1);
s.pet.activityNow='sleep';s.pet.needs.energy=5;P.tick(s,1451,1751,{nearby:true});assert(s.pet.needs.energy>88);
for(const key of ['hunger','energy','company']){s=create(100);s.pet.status='home';s.pet.needs={hunger:100,energy:100,company:100};s.pet.needs[key]=0;s.pet.activityNow='sleep';s.feeder=0;
 // Energy neglect requires no rest; other needs are kept safe through independent checks.
 if(key==='energy')s.pet.activityNow='idle';
 let t=0;for(;t<1439;t++){for(const k of ['hunger','energy','company'])if(k!==key)s.pet.needs[k]=100;P.tick(s,t,t+1,{},()=>{});}assert.equal(s.pet.status,'home');P.tick(s,1439,1440,{},()=>{});if(key==='energy')assert.equal(s.pet.status,'away');else if(key==='hunger'||key==='company')assert.equal(s.pet.status,'away');
 assert.equal(s.sadUntil,4320);assert.equal(s.banUntil,11520);const saved=copy(s),roll=s.pet.willReturn;s=P.restore(saved,breeds);assert.equal(s.pet.willReturn,roll);assert.equal(s.pet.returnAt,4320);assert.equal(P.refusal(s,4320),'ban');P.tick(s,1440,4319,{},()=>{});assert.equal(s.pet.status,'away');P.tick(s,4319,4320,{},()=>{});assert.equal(s.pet.status,roll?'home':'lost');assert.equal(P.refusal(s,11519),'ban');assert.equal(P.refusal(s,11520),null);   // one pet home: room for a second
}
// Restoring without advancing the simulation must never advance any timer.
s=create();s.pet.status='home';s.pet.needs.hunger=0;P.tick(s,0,120,{});s.pet.needs.hunger=40;P.tick(s,120,121,{});assert.equal(s.pet.low.hunger,0);
const saved=copy(s),restored=P.restore(saved,breeds);assert.equal(restored.pet.arrivalAt,saved.pets[0].arrivalAt);assert.equal(restored.pet.low.hunger,saved.pets[0].low.hunger);assert.equal(restored.sadUntil,saved.sadUntil);
// Fixed rolls exercise both return outcomes, rather than relying on statistical luck.
const outcomes=new Set();for(let seed=1;seed<100;seed++){s=create(seed);P.escape(s,2000,()=>{});const yes=s.pet.willReturn;outcomes.add(yes);s=P.restore(copy(s),breeds);P.tick(s,2000,4880,{},()=>{});assert.equal(s.pet.status,yes?'home':'lost');}assert.equal(outcomes.size,2);
s.pet.affinity=77;assert.equal(P.restore(copy(s),breeds).pet.affinity,77);const old=copy(s);delete old.pets[0].affinity;assert.equal(P.restore(old,breeds).pet.affinity,30);
s.matColor='rose';assert.equal(P.restore(copy(s),breeds).matColor,'rose');assert.equal(P.restore({...copy(s),matColor:'bad'},breeds).matColor,'sage');
// Two pets: a second one while the first is home, never a third; 放弃领养 after 3 days, 7-day ban, kit back with the last one.
s=create(7);P.tick(s,0,1440,{});assert.equal(P.refusal(s,1440),null);assert(P.adopt(s,s.offers[7],'二号',1440));assert.equal(s.pets.length,2);assert.equal(P.refusal(s,1440),'pending');
s.sel=1;P.tick(s,1440,2880,{});assert.equal(s.pets[1].status,'home');assert.equal(P.refusal(s,2880),'occupied');assert(!P.adopt(s,s.offers[8],'三号',2880));
let r2=P.restore(copy(s),breeds);assert.equal(r2.pets.length,2);assert.equal(r2.pets[1].name,'二号');assert.equal(r2.sel,1);assert.equal(r2.pet.name,'二号');assert(!('pet' in JSON.parse(JSON.stringify(s))));
assert.deepEqual(P.abandonable(s,1440+3*1440-1).map(p=>p.name),[]);assert.deepEqual(P.abandonable(s,1440+3*1440).map(p=>p.name),['团子']);assert(!P.abandon(s,s.pets[1],5760));
assert(P.abandon(s,s.pets[0],5760));assert.equal(s.pets.length,1);assert.equal(s.pet.name,'二号');assert(s.installed);assert.equal(P.refusal(s,5760),'ban');assert.equal(P.refusal(s,5760+7*1440),null);assert.equal(P.restore(copy(s),breeds).banWhy,'abandon');
assert(P.abandon(s,s.pets[0],2880+3*1440));assert.equal(s.pets.length,0);assert(!s.installed);assert.equal(s.feeder,0);assert.equal(s.pet,null);
const v1=P.restore({version:1,seed:3,pet:{breed:'cat1',status:'home',name:'旧存档',needs:{hunger:50}}},breeds);assert.equal(v1.pets.length,1);assert.equal(v1.pet.name,'旧存档');
console.log('PASS 12 weekly offers; singleton adoption; 24h delivery; 30h fullness; exact feeder accounting; sleep recovery; each neglect cause; 24h threshold; 48h fixed return; 7d ban; offline freeze; saved roll; both outcomes; two pets max; 放弃领养 after 3 days with 7-day ban; kit returned; v1 saves');
