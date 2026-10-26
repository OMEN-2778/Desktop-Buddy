// Three independent, stable traits. Appearance and gender never determine them.
const PERSONALITY_AXES=[['social','社交方式','慢热','外向','先熟悉，再慢慢打开话匣子。','愿意主动认识人、分享身边的新鲜事。'],['care','处事方式','随性','周到','喜欢留点空白，偶尔临时起意。','喜欢提前商量，留意彼此是否方便。'],['sensitivity','情绪反应','沉稳','敏感','情绪起伏较小，愿意慢慢消化。','容易察觉细微变化，也更容易被小事打动。']];
const PARENT_PERSONALITIES={dad:{social:-60,care:-60,sensitivity:-60},mom:{social:60,care:60,sensitivity:0}};
function seededPersonality(id){let h=2166136261;for(const ch of String(id))h=Math.imul(h^ch.charCodeAt(0),16777619)>>>0;const p={};for(const [key]of PERSONALITY_AXES){h=(Math.imul(h,1664525)+1013904223)>>>0;p[key]=Math.round(h/4294967295*200-100);}return p;}
function normalizePersonality(value,id='hero'){if(Object.hasOwn(PARENT_PERSONALITIES,id))return {...PARENT_PERSONALITIES[id]};const fallback=seededPersonality(id),p={};for(const [key]of PERSONALITY_AXES)p[key]=Number.isFinite(value?.[key])?Math.max(-100,Math.min(100,Math.round(value[key]))):fallback[key];return p;}
let heroPersonality={social:0,care:0,sensitivity:0},heroPersonalityChosen=false;
function personalityOf(c){return c?normalizePersonality(c.personality,c.id||c.personId||'passerby'):heroPersonality;}
function personalityLabel(axis,value){return value< -25?axis[2]:value>25?axis[3]:{social:'随和',care:'灵活',sensitivity:'平和'}[axis[0]];}
function personalityTraits(c){const p=personalityOf(c);return PERSONALITY_AXES.map(a=>personalityLabel(a,p[a[0]]));}
function personalityKind(c,axis=null){const p=personalityOf(c),key=axis||[...PERSONALITY_AXES].sort((a,b)=>Math.abs(p[b[0]])-Math.abs(p[a[0]]))[0][0];if(Math.abs(p[key])<=25)return 'balanced';return key==='social'?(p.social<0?'slow':'outgoing'):key==='care'?(p.care<0?'casual':'thoughtful'):(p.sensitivity<0?'steady':'sensitive');}
function personalityContact(c){return socialState.contacts.find(p=>p.id===c?.personId)||socialState.world.find(p=>p.id===c?.personId)||c;}
function restorePersonalities(data){
 heroPersonality=normalizePersonality(data?.heroPersonality||{social:0,care:0,sensitivity:0});heroPersonalityChosen=data?.heroPersonalityChosen===true;
 const saved=new Map((Array.isArray(data?.world)?data.world:[]).filter(p=>p&&typeof p.id==='string').map(p=>[p.id,p]));
 for(const p of socialState.world)p.personality=normalizePersonality(saved.get(p.id)?.personality,p.id);
 for(const c of socialState.contacts){const old=(data?.contacts||[]).find?.(p=>p?.id===c.id);c.personality=normalizePersonality(old?.personality||socialState.world.find(p=>p.id===c.id)?.personality,c.id);c.personalityTalks=Number.isFinite(old?.personalityTalks)?Math.max(0,Math.min(1000,Math.floor(old.personalityTalks))):0;c.personalityBond={gain:Number.isFinite(old?.personalityBond?.gain)?Math.max(0,Math.min(1000,old.personalityBond.gain)):0,days:Array.isArray(old?.personalityBond?.days)?[...new Set(old.personalityBond.days.filter(Number.isInteger))].slice(-180):[]};c.personalityTextSeen={};for(const [key,indices]of Object.entries(old?.personalityTextSeen||{}))if(Array.isArray(indices))c.personalityTextSeen[key]=indices.filter(i=>Number.isInteger(i)&&i>=0&&i<1000).slice(-4);c.personalitySeen=Array.isArray(old?.personalitySeen)?[...new Set(old.personalitySeen.filter(k=>PERSONALITY_AXES.some(a=>a[0]===k)))]:[];}
}
const PERSONALITY_DISCOVERY=[{gain:6,days:2,affinity:30},{gain:14,days:4,affinity:60},{gain:24,days:7,affinity:80}];
function knownPersonalityTraits(c){return PERSONALITY_AXES.filter(a=>c.family||c.personalitySeen?.includes(a[0])).map(a=>personalityLabel(a,personalityOf(c)[a[0]]));}
function personalityUnderstanding(c,axis){
 if(c.family)return 2;if(!c.personalitySeen?.includes(axis))return 0;
 const bond=c.personalityBond;return bond?.gain>=30&&bond?.days?.length>=10?2:1;
}
function discoverPersonality(c,gain=0){
 if(!c)return;c.personalityTalks=Math.min(1000,(c.personalityTalks||0)+1);c.personalitySeen||=[];
 const bond=c.personalityBond||={gain:0,days:[]},day=Math.floor(sim.t/1440);
 bond.gain=Math.min(1000,bond.gain+Math.max(0,gain));if(!bond.days.includes(day))bond.days.push(day);bond.days=bond.days.slice(-180);
 const count=c.family?3:PERSONALITY_DISCOVERY.filter(step=>bond.gain>=step.gain&&bond.days.length>=step.days&&c.affinity>=step.affinity).length;
 const axes=[...PERSONALITY_AXES].sort((a,b)=>Math.abs(personalityOf(c)[b[0]])-Math.abs(personalityOf(c)[a[0]]));
 for(const axis of axes.slice(0,count))if(!c.personalitySeen.includes(axis[0])){
  c.personalitySeen.push(axis[0]);const label=personalityLabel(axis,personalityOf(c)[axis[0]]),examples=SOCIAL_DIALOGUE.discovery[label];
  const text=`相处下来，发现${contactName(c)}${pick(examples)}。`;log(text);addSocialMemory(c,'更了解彼此 · '+label,text);contactsSig='';
 }
}
function personalityCallFactor(c){return 1-personalityOf(c).social*.004;}
function personalityDecay(c){return 1+personalityOf(c).social*.0025;}
function personalityMoodDuration(m){const s=heroPersonality.sensitivity/100;return Math.round(m.min*(1+s*(LOW_EMO.has(m.emo)?.2:.1)));}
function personalityChoices(score){const p=heroPersonality;for(const key of ['phone_text','phone_call','phone_video','pc_video'])score[key]*=1+p.social*.002;score.read*=1-p.social*.0015;score.go_out*=1+p.social*.0015;for(const key of ['wash','water_living','water_study'])score[key]*=1+p.care*.002;}
function personalityConversationPool(c,context='call'){
 const axis=[...PERSONALITY_AXES].sort((a,b)=>Math.abs(personalityOf(c)[b[0]])-Math.abs(personalityOf(c)[a[0]]))[0][0];
 const kind=personalityKind(c,axis),stage=personalityUnderstanding(c,axis);
 return SOCIAL_DIALOGUE.everydayPersonality[kind][stage].map((t,i)=>({...t,id:`persona_${context}_${kind}_${stage}_${i}`,personalityTopic:true}));
}
function personalityLines(c,context='meet'){return pick(personalityConversationPool(c,context)).lines.slice(0,2);}
// Routine exchanges start with their own subject, not a personality biography.
function personalityTalk(lines){return [...lines];}
function personalityVisitReason(c){const k=personalityKind(c,'care');if(k==='balanced')return ['想找你坐坐','在家吗？我想过去待会儿，方便不？','来呗','今天有点忙，下回吧'];return k==='thoughtful'?['想先约个方便的时间','想过去坐坐，你现在忙不忙？不方便咱就改天。',"来吧，我给你倒水",'今天有点忙，咱们另约时间']:['临时起意的散步终点','我出来溜达，突然想去你家坐会儿。你在家吧？',"来吧，刚好有空","今天不方便，改天来吧"];}
function showPersonality(id=null,selection=null){
 const c=id?socialState.contacts.find(c=>c.id===id):null;if(id&&!c)return;
 if(!c&&!wardrobeOpen){showHint('请在更衣室里修改性格。');return;}
 if(phoneHolds()||socialBusy()||card||wiping){showHint('先忙完眼前的事，再看看性格吧。');return;}
 const sheet=c?openSocialSheet(`${contactName(c)} · 性格`):openWardrobePersonality();sheet.classList.add('personality-sheet');const content=c?socialContent(sheet):sheet;
 const intro=document.createElement('p');intro.className='personality-intro';intro.textContent=c?"再多相处一阵，才能知道对方平时是什么样的人。":'性格影响自主行为和表达；你手动安排的事始终优先。可以以后再调整。';content.append(intro);
 const draft={...(selection||heroPersonality)},form=document.createElement('div');form.className='personality-axes';
 for(const axis of PERSONALITY_AXES){
  if(c){const known=c.family||c.personalitySeen?.includes(axis[0]),fact=document.createElement('div'),label=document.createElement('strong'),value=document.createElement('span'),description=document.createElement('small');fact.className='personality-fact';label.textContent=axis[1];value.textContent=known?personalityLabel(axis,personalityOf(c)[axis[0]]):'还不太了解';description.textContent=known?(Math.abs(personalityOf(c)[axis[0]])<=25?'会依照当时的情境调整自己的节奏。':axis[personalityOf(c)[axis[0]]<0?4:5]):'再聊聊，或一起经历一些事吧。';value.title=description.textContent;fact.append(label,value,description);form.append(fact);continue;}
  const row=document.createElement('fieldset'),legend=document.createElement('legend');legend.textContent=axis[1];row.append(legend);
  for(const [value,label]of [[-75,axis[2]],[0,{social:'随和',care:'灵活',sensitivity:'平和'}[axis[0]]],[75,axis[3]]]){const labelEl=document.createElement('label'),input=document.createElement('input');input.type='radio';input.name='personality-'+axis[0];input.value=value;input.checked=value===(draft[axis[0]]< -25?-75:draft[axis[0]]>25?75:0);input.onchange=()=>draft[axis[0]]=value;labelEl.append(input,document.createTextNode(label));row.append(labelEl);}form.append(row);
 }if(c){content.prepend(form);}else content.append(form);
 if(!c){const actions=document.createElement('div');actions.className='personality-actions';sheet.append(actions);for(const [label,action]of [['随机一组',()=>{showPersonality(null,seededPersonality('hero-'+Math.random()));}],['确定性格',()=>{for(const [key]of PERSONALITY_AXES){const checked=sheet.querySelector(`input[name="personality-${key}"]:checked`);draft[key]=Number(checked.value);}heroPersonality=normalizePersonality(draft);heroPersonalityChosen=true;closeWardrobePersonality();log(`认识自己：${personalityTraits(null).join('、')}。这些倾向会影响生活，但每次选择仍握在自己手里。`);autoSave();}]]){const button=document.createElement('button');button.type='button';button.textContent=label;button.onclick=action;actions.append(button);}}
 if(!c)makeRoom();
}
let wardrobePersonality=null;
function closeWardrobePersonality(){
 if(!wardrobePersonality)return;wardrobePersonality.replaceChildren();wardrobePersonality.className='wardrobe-personality';wardrobePersonality.setAttribute('aria-label','当前性格');
 const title=document.createElement('h3');title.textContent='性格';wardrobePersonality.append(title);
 for(const trait of personalityTraits(null)){const p=document.createElement('p');p.textContent=trait;wardrobePersonality.append(p);}
 const hint=document.createElement('small');hint.textContent=heroPersonalityChosen?'点击上方「性格」调整':'点击上方「性格」选择';wardrobePersonality.append(hint);
 studioEl.querySelector('.st-personality')?.setAttribute('aria-expanded','false');
 if(wardrobeOpen)makeRoom();
}
function openWardrobePersonality(){
 wardrobePersonality.replaceChildren();wardrobePersonality.className='wardrobe-personality editing';wardrobePersonality.setAttribute('aria-label','选择性格');
 const heading=document.createElement('h3');heading.textContent='我的性格';const cancel=document.createElement('button');cancel.type='button';cancel.className='personality-cancel';cancel.textContent='取消';cancel.onclick=closeWardrobePersonality;wardrobePersonality.append(heading,cancel);
 studioEl.querySelector('.st-personality').setAttribute('aria-expanded','true');return wardrobePersonality;
}
function installWardrobePersonality(){
 studioEl.classList.add('has-personality');const button=document.createElement('button');button.type='button';button.className='st-personality';button.textContent='性格';button.setAttribute('aria-controls','wardrobePersonality');button.setAttribute('aria-expanded','false');button.onclick=()=>showPersonality();studioEl.querySelector('.st-tools').prepend(button);
 const stage=studioEl.querySelector('.st-stage'),summary=document.createElement('div');summary.className='st-summary';stage.before(summary);summary.append(stage);
 wardrobePersonality=document.createElement('aside');wardrobePersonality.id='wardrobePersonality';summary.append(wardrobePersonality);closeWardrobePersonality();
 wardrobePersonality.addEventListener('keydown',e=>{if(e.key==='Escape'){e.stopPropagation();closeWardrobePersonality();button.focus();}});
}
