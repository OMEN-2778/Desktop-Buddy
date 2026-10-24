// Dialogue has explicit context; selection never relaxes these conditions to
// fill a random slot. Historical anecdotes need no current-time restriction.
function socialTalkFits(talk){
  const title=Array.isArray(talk)?talk[0]:talk.title;
  const when=(!Array.isArray(talk)&&talk.when)||SOCIAL_DIALOGUE.legacyWhen[title]||{};
  const h=hour();
  if(when.hours){const [a,b]=when.hours;if(a<b?!(h>=a&&h<b):!(h>=a||h<b))return false;}
  if(when.days&&!when.days.includes(Math.floor(sim.t/1440)%7))return false;
  if(when.seasons&&!when.seasons.includes(seasonOf(sim.t).i))return false;
  if(when.weather&&!when.weather.includes(weather.kind))return false;
  if(when.acts&&!when.acts.includes(sim.act))return false;
  return true;
}
for(const [kind,entries]of Object.entries(SOCIAL_DIALOGUE.phone)){
  for(const [i,talk]of entries.entries()){
    talk.id=`social_extra_${kind}_${i}`;
    ML[talk.id]={name:talk.moodName||'聊到心里',emo:talk.emo||'happy',pts:2,min:120};
    CHATS[kind].friend.talks.push(talk);
  }
}
for(const [level,entries]of Object.entries(SOCIAL_DIALOGUE.relationship)){
  for(const [i,row]of entries.entries()){
    SOCIAL_TEXT.conversations[level].push(row);
  }
}

function homeGuestCanTalk(g){
  return sim.place==='home'&&g.phase==='visiting'&&!g.sleeping&&!asleep()&&sim.mode!=='down'
    &&!['bath','toilet','sleep'].includes(sim.act)&&!remoteSocial&&!sim.talk
    &&roomAt(here())===roomAt(homeGuestPoint(g))&&roomAt(here())!=='stairs';
}
function homeGuestTalkPool(g,c){
  const groups=SOCIAL_DIALOGUE.visit,context=[];
  if(sim.act==='tv')context.push(...groups.tv);
  if(sim.act==='eat')context.push(...groups.meal);
  if(isRain(weather.kind))context.push(...groups.rain);
  if(weather.kind==='snow')context.push(...groups.snow);
  context.push(...groups[['spring','summer','autumn','winter'][seasonOf(sim.t).i]]);
  const h=hour(),period=h<6?'night':h<11?'morning':h<14?'noon':h<18?'afternoon':h<22?'evening':'night';
  context.push(...groups[period]);
  // Half the conversations come from the current setting, half from everyday
  // stories. No repeated title until that pool's fresh entries are exhausted.
  const persona=personalityConversationPool(c,'visit').map(t=>[t.title,...t.lines]);
  const common=[...persona,...groups.common,...SOCIAL_TEXT.visitTalks,...(c.family?[]:SOCIAL_TEXT.conversations[socialLevel(c)])].filter(row=>socialTalkFits(row)&&(!(SOCIAL_DIALOGUE.visitCloseOnly||[]).includes(row[0])||!c.family&&c.affinity>=60));
  return Math.random()<.5?context.filter(socialTalkFits):common;
}

function moveHomeGuest(g,dt){
  if(g.phase!=='visiting'||g.sleeping)return;
  const target=homeGuestDestination(g),current=homeGuestPoint(g);
  if(!g.destination||g.destination.x!==target.x||g.destination.y!==target.y){
    g.destination=target;g.walkRoute=planRoute(current.x,current.y,target.x,target.y);g.walkS=0;g.walkLength=routeLength(g.walkRoute);
    if(roomAt(current)!==roomAt(target))g.talk=null;
  }
  if(g.walkS<g.walkLength){g.walkS=Math.min(g.walkLength,g.walkS+WALK*.85*Math.min(speed,4)*dt);g.position=routePos(g.walkRoute,g.walkS);}
  else g.position={...target,dy:0};
  if(g.roamRoom&&g.roamStage==='walking'&&g.walkS>=g.walkLength){g.roamStage='resting';g.roamUntil=sim.t+5+Math.random()*5;}
}

for(const [kind,entries]of Object.entries(SOCIAL_DIALOGUE.early))entries.forEach((t,i)=>{ML['social_early_'+kind+'_'+i]={name:'慢慢认识',emo:'happy',pts:1,min:60};});

for(const [kind,stages]of Object.entries(SOCIAL_DIALOGUE.everydayPersonality))for(const [stage,talks]of stages.entries())for(const [i,talk]of talks.entries())for(const context of ['call','text','video','meet','visit'])ML[`persona_${context}_${kind}_${stage}_${i}`]={name:'随口聊聊',emo:'happy',pts:1,min:90};
