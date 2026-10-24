// Three independent, stable traits. Appearance and gender never determine them.
const PERSONALITY_AXES=[['social','社交方式','慢热','外向','先熟悉，再慢慢打开话匣子。','愿意主动认识人、分享身边的新鲜事。'],['care','处事方式','随性','周到','喜欢留点空白，偶尔临时起意。','喜欢提前商量，留意彼此是否方便。'],['sensitivity','情绪反应','沉稳','敏感','情绪起伏较小，愿意慢慢消化。','容易察觉细微变化，也更容易被小事打动。']];
function seededPersonality(id){let h=2166136261;for(const ch of String(id))h=Math.imul(h^ch.charCodeAt(0),16777619)>>>0;const p={};for(const [key]of PERSONALITY_AXES){h=(Math.imul(h,1664525)+1013904223)>>>0;p[key]=Math.round(h/4294967295*200-100);}return p;}
function normalizePersonality(value,id='hero'){const fallback=seededPersonality(id),p={};for(const [key]of PERSONALITY_AXES)p[key]=Number.isFinite(value?.[key])?Math.max(-100,Math.min(100,Math.round(value[key]))):fallback[key];return p;}
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
 for(const c of socialState.contacts){const old=(data?.contacts||[]).find?.(p=>p?.id===c.id);c.personality=normalizePersonality(old?.personality||socialState.world.find(p=>p.id===c.id)?.personality,c.id);c.personalityTalks=Number.isFinite(old?.personalityTalks)?Math.max(0,Math.min(1000,Math.floor(old.personalityTalks))):0;c.personalityTextSeen={};for(const [key,indices]of Object.entries(old?.personalityTextSeen||{}))if(Array.isArray(indices))c.personalityTextSeen[key]=indices.filter(i=>Number.isInteger(i)&&i>=0&&i<2).slice(-2);c.personalitySeen=Array.isArray(old?.personalitySeen)?[...new Set(old.personalitySeen.filter(k=>PERSONALITY_AXES.some(a=>a[0]===k)))]:[];}
}
function discoverPersonality(c){
 if(!c)return;c.personalityTalks=Math.min(1000,(c.personalityTalks||0)+1);c.personalitySeen||=[];
 const count=c.family?3:Math.min(3,Math.floor(c.personalityTalks/2));
 const axes=[...PERSONALITY_AXES].sort((a,b)=>Math.abs(personalityOf(c)[b[0]])-Math.abs(personalityOf(c)[a[0]]));
 for(const axis of axes.slice(0,count))if(!c.personalitySeen.includes(axis[0])){c.personalitySeen.push(axis[0]);const label=personalityLabel(axis,personalityOf(c)[axis[0]]),text=`相处下来，发现${contactName(c)}${({慢热:'需要一点熟悉的时间，话少也会认真听',外向:'总能主动找到话题',随性:'喜欢临时起意，也愿意留点空白',周到:'会提前商量，留意别人的方便',沉稳:'习惯先稳住心情，再慢慢处理',敏感:'会留意细微变化，也容易被小事打动',随和:'会在热闹和安静之间找自己的节奏',灵活:'既能提前安排，也能顺势而为',平和:'能感受情绪，也愿意慢慢消化'})[label]}。`;log(text);addSocialMemory(c,'更了解彼此 · '+label,text);}
}
function personalityCallFactor(c){return 1-personalityOf(c).social*.004;}
function personalityDecay(c){return 1+personalityOf(c).social*.0025;}
function personalityMoodDuration(m){const s=heroPersonality.sensitivity/100;return Math.round(m.min*(1+s*(LOW_EMO.has(m.emo)?.2:.1)));}
function personalityChoices(score){const p=heroPersonality;for(const key of ['phone_text','phone_call','phone_video','pc_video'])score[key]*=1+p.social*.002;score.read*=1-p.social*.0015;score.go_out*=1+p.social*.0015;for(const key of ['wash','water_living','water_study'])score[key]*=1+p.care*.002;}
function personalityLines(c,context='meet'){
 const p=personalityOf(c),weights=PERSONALITY_AXES.map(([key])=>[key,25+Math.abs(p[key])]),total=weights.reduce((sum,[,w])=>sum+w,0);let roll=Math.random()*total,axis=weights.at(-1)[0];for(const [key,w]of weights){roll-=w;if(roll<=0){axis=key;break;}}
 const kind=personalityKind(c,axis),pool=PERSONALITY_TEXT[kind][context]||PERSONALITY_TEXT[kind].meet;
 const seen=(c.personalityTextSeen||={}),key=kind+'_'+context,indices=Array.isArray(seen[key])?seen[key]:[],fresh=pool.map((_,i)=>i).filter(i=>!indices.includes(i)),i=pick(fresh.length?fresh:pool.map((_,i)=>i));seen[key]=[...indices.slice(-1),i];
 const level=c.family?'close':socialLevel(c),familiar=level==='familiar';
 const other=pool[i][familiar?0:1];
 const reply=pick(PERSONALITY_REPLIES[personalityKind(null)]);
 return ['>'+other,reply];
}
function personalityTalk(lines,c,context){return [...personalityLines(c,context),...lines];}
function personalityVisitReason(c){const k=personalityKind(c,'care');if(k==='balanced')return ['想找你坐坐','今天有空吗？想去你家聊聊天，方便的话我就过来。','欢迎来坐坐','今天有点忙，改天再聚'];return k==='thoughtful'?['想先约个方便的时间','我想来坐一会儿，先问问你现在方便吗？不方便我们就改天，不着急。','茶杯准备好了，欢迎来坐','今天有点忙，咱们另约时间']:['临时起意的散步终点','本来只打算出门走走，走着走着想找你聊聊。我能把终点改成你家沙发吗？','沙发批准了，过来吧','沙发今天休假，改天吧'];}
function showPersonality(id=null,selection=null){
 const c=id?socialState.contacts.find(c=>c.id===id):null;if(id&&!c)return;
 if(!c&&!wardrobeOpen){showHint('请在更衣室里修改性格。');return;}
 if(phoneHolds()||socialBusy()||card||wiping){showHint('先忙完眼前的事，再看看性格吧。');return;}
 const sheet=c?openSocialSheet(`${contactName(c)} · 性格`):openWardrobePersonality();sheet.classList.add('personality-sheet');const content=c?socialContent(sheet):sheet;
 const intro=document.createElement('p');intro.className='personality-intro';intro.textContent=c?'性格会在相处中慢慢显露。话少不等于疏远，热情也有安静的时候。':'性格影响自主行为和表达；你手动安排的事始终优先。可以以后再调整。';content.append(intro);
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

const PERSONALITY_TEXT={
  "slow": {
    "meet": [
      [
        "我不太会开场，不过这里挺舒服的。",
        "又碰到你啦，这次不用在心里排练开场白了。"
      ],
      [
        "我有时候话接得慢，不是没在听。",
        "跟你说话不用急着找话题，停一会儿也舒服。"
      ]
    ],
    "text": [
      [
        "消息我看到了，刚才在想怎么说清楚。",
        "刚才把回复删了两遍，后来想，你应该懂我的意思。"
      ],
      [
        "文字聊天挺好的，可以慢慢组织语言。",
        "有些当面不好意思说的事，想先悄悄发给你。"
      ]
    ],
    "call": [
      [
        "我先听你说，电话里我有时会紧张。",
        "听到你的声音就放松了，刚才还练了一遍喂。"
      ],
      [
        "如果我安静一会儿，是在认真听。",
        "你慢慢讲，我没打算赶着挂电话。"
      ]
    ],
    "video": [
      [
        "镜头这样可以吗？我还不太习惯看镜头。",
        "看见你就没那么拘谨了，我把镜头摆正一点。"
      ],
      [
        "视频时不知道该看屏幕还是看镜头呢。",
        "跟你视频可以不一直找话题，做自己的事也行。"
      ]
    ],
    "visit": [
      [
        "第一次来有点拘谨，我坐这里可以吗？",
        "还是你家这个位置自在，我已经不用端坐了。"
      ],
      [
        "我先听你说说最近的事吧。",
        "今天想把那件没好意思说的小事讲给你听。"
      ]
    ]
  },
  "outgoing": {
    "meet": [
      [
        "你好！刚才路过，忽然想找人聊两句。",
        "远远就看见你啦，我这声招呼没白练！"
      ],
      [
        "今天遇见一件小事，正愁没人分享。",
        "有你在，我今天攒的话终于有地方放了。"
      ]
    ],
    "text": [
      [
        "看到个有趣的东西，想顺手分享给你。",
        "今日份新鲜事送达！你忙完再拆。"
      ],
      [
        "我发消息比较积极，你有空再回就好。",
        "又来投递生活碎片啦，不用每条都回复。"
      ]
    ],
    "call": [
      [
        "想打个电话问声好，没有急事。",
        "听筒接通，今日闲聊频道正式开播！"
      ],
      [
        "今天路上发生的事有点好笑，想说给你听。",
        "有个笑话憋了一路，得先讲给你。"
      ]
    ],
    "video": [
      [
        "视频接通啦！这样比文字打招呼热闹。",
        "让我看看你！今天也来一场隔空碰面。"
      ],
      [
        "我把镜头转一下，给你看看窗外。",
        "给你直播一下我的窗台，小植物也算出镜嘉宾。"
      ]
    ],
    "visit": [
      [
        "谢谢让我来坐坐，路上攒了几个新话题。",
        "我带着一肚子话来了，先别嫌我占用沙发。"
      ],
      [
        "如果聊得太起劲，你随时提醒我喝口水。",
        "今天的聊天库存很足，咱们慢慢挑着聊。"
      ]
    ]
  },
  "casual": {
    "meet": [
      [
        "本来没想走到这里，随便逛逛也挺好。",
        "散步没定路线，倒正好把你随到了。"
      ],
      [
        "今天没排满计划，想看看会遇见什么。",
        "计划表空着，碰到你就多了一件好事。"
      ]
    ],
    "text": [
      [
        "突然想到个话题，就先给你发来了。",
        "刚刚灵机一动，想法还热着就发给你了。"
      ],
      [
        "不是什么重要消息，路过问声好。",
        "今天没什么大事，但想跟你分享一点小事。"
      ]
    ],
    "call": [
      [
        "临时想打个招呼，方便聊一会儿吗？",
        "刚才突然想起你，手比脑子先拨了电话。"
      ],
      [
        "没有准备话题，随便聊聊也可以。",
        "今天就聊到哪儿算哪儿，跑题也归咱们管。"
      ]
    ],
    "video": [
      [
        "背景有点随意，希望不影响聊天。",
        "先别笑我的背景，它今天走自由摆放路线。"
      ],
      [
        "我临时接的视频，还没找好位置。",
        "镜头先放这儿，咱们边试边找个舒服角度。"
      ]
    ],
    "visit": [
      [
        "临时来打扰了，坐一会儿就好。",
        "散步的终点改成你家沙发，路线升级成功。"
      ],
      [
        "不用特意招待，白水就很好。",
        "别忙啦，我是来找你玩的，不是来验收茶点的。"
      ]
    ]
  },
  "thoughtful": {
    "meet": [
      [
        "现在方便说话吗？不方便也没关系。",
        "看你没在忙才过来，正好问问最近怎么样。"
      ],
      [
        "我站这边吧，留出一点过路的位置。",
        "咱们靠旁边聊，别把路人的路堵成收费站了。"
      ]
    ],
    "text": [
      [
        "你有空再回复，不用急着看手机。",
        "先把消息放这里，等你忙完我们再慢慢说。"
      ],
      [
        "我把要说的事整理了一下，应该不长。",
        "今天的消息已整理成不费脑版本，请放心查收。"
      ]
    ],
    "call": [
      [
        "现在接电话方便吗？我可以晚一点再打。",
        "先问问你有没有空，别耽误你吃饭或休息。"
      ],
      [
        "没有急事，我们按方便的时间聊。",
        "放心，今天没有紧急任务，只有问候。"
      ]
    ],
    "video": [
      [
        "声音清楚吗？我先把旁边的声音关小。",
        "我把背景声音关了，今天认真听你讲。"
      ],
      [
        "我调整一下光线，免得你看着费劲。",
        "等一下，挪好灯就能看清，不能让你跟剪影聊天。"
      ]
    ],
    "visit": [
      [
        "提前问好了时间，应该没打乱你的安排吧？",
        "我照约好的时间来啦，今天不用你临时忙活。"
      ],
      [
        "杯子用完放哪里？我顺手收好。",
        "不用急着收拾，我走前会把这一小块恢复原样。"
      ]
    ]
  },
  "steady": {
    "meet": [
      [
        "刚才有点小插曲，不过现在已经没事了。",
        "绕了一点路也不碍事，慢慢走总能碰到你。"
      ],
      [
        "偶尔停一停，看看周围挺好的。",
        "今天不赶，咱们把这阵风吹完再走。"
      ]
    ],
    "text": [
      [
        "刚才遇到一点麻烦，处理完就轻松了。",
        "今天的小麻烦解决了，来跟你报个平安。"
      ],
      [
        "不用急着给我建议，我已经慢慢理顺了。",
        "跟你说说就行，不用替我着急。"
      ]
    ],
    "call": [
      [
        "我没着急，想慢慢把事情说清楚。",
        "别急，听你声音有点累，咱们慢慢说。"
      ],
      [
        "今天有点波折，好在都过去了。",
        "坏事没有占满今天，剩下的时间用来聊天正好。"
      ]
    ],
    "video": [
      [
        "画面卡了一下，没事，等它缓过来。",
        "镜头卡住也不要紧，听到声音就当电话聊。"
      ],
      [
        "今天想安静聊会儿，不需要特别的话题。",
        "看你在那边安心待着，我这边也跟着松口气。"
      ]
    ],
    "visit": [
      [
        "路上耽搁了一点，进门坐下就不赶了。",
        "一坐到你家沙发上，路上那点烦心事就放下了。"
      ],
      [
        "我陪你坐会儿，安静一点也很好。",
        "今天咱们不用把日子过成节目，歇会儿就好。"
      ]
    ]
  },
  "sensitive": {
    "meet": [
      [
        "这里一点小变化，我就忍不住多看两眼。",
        "今天跟上次有点不一样，跟你说才觉得有意思。"
      ],
      [
        "刚才那阵风让我想起以前的一天。",
        "有时一个小细节就能勾起回忆，还好能说给你听。"
      ]
    ],
    "text": [
      [
        "收到认真回复会觉得很温暖，谢谢。",
        "看到你的消息，今天的疲惫像被轻轻接住了。"
      ],
      [
        "我有时会把一句话想很久，正在学着放松。",
        "刚才差点又多想了，后来记起我们可以直接说。"
      ]
    ],
    "call": [
      [
        "听见熟悉的声音会安心一点。",
        "本来有点乱，接通你这边以后就安稳多了。"
      ],
      [
        "今天被一件小事打动，想找个人讲讲。",
        "今天有人替我留了门，这点小善意够暖一整天。"
      ]
    ],
    "video": [
      [
        "视频里能看见表情，感觉更容易聊清楚。",
        "看见你点头，我就知道自己不是在对空气讲话。"
      ],
      [
        "我注意到那边光线挺柔和，看着很舒服。",
        "你那边的灯还是这个颜色，好像隔着屏幕回了趟熟悉的地方。"
      ]
    ],
    "visit": [
      [
        "谢谢愿意让我来，这样面对面聊挺安心的。",
        "你记得我坐哪儿舒服，这种小事我会记很久。"
      ],
      [
        "房间里的灯很温暖，我一下放松了。",
        "来之前有点烦，坐在这里喝口水就觉得被照顾到了。"
      ]
    ]
  }
};
const PERSONALITY_REPLIES={
  "slow": [
    "我可能接话慢一点，不过我在认真听。",
    "能这样慢慢聊，我觉得挺自在的。",
    "刚认识时我话不多，熟悉以后会慢慢讲给你听。"
  ],
  "outgoing": [
    "我也有件小事想说，等你讲完轮到我。",
    "你这么一说，我的话匣子也打开了。",
    "收到！今天又多了一件能一起聊的事。"
  ],
  "casual": [
    "那就随便聊聊，话题走到哪儿算哪儿。",
    "不用准备得太完整，这样就挺好。",
    "临时起意也会碰到好事嘛。"
  ],
  "thoughtful": [
    "你慢慢说，我把手边的事放一下。",
    "有什么不方便的就直说，我们可以另约。",
    "先确认你舒服，咱们再接着聊。"
  ],
  "steady": [
    "没关系，咱们一件一件慢慢说。",
    "先坐稳心情，不急着把一切想明白。",
    "好的，今天就按舒服的节奏来。"
  ],
  "sensitive": [
    "这种小细节我也会记在心里。",
    "谢谢你愿意讲，我听着也觉得暖了一点。",
    "有时说出来就安心了，我懂这种感觉。"
  ]
};

PERSONALITY_TEXT.balanced={
 meet:[['你好，正好在这里歇一会儿。','又碰到你了，今天也来走走呀。'],['走走停停挺好的，不急着赶路。','今天不赶时间，聊两句再继续走。']],
 text:[['有件小事想跟你聊聊，方便时回就好。','今天的生活碎片来啦，有空一起聊。'],['刚好拿起手机，顺便问候一下。','忙完一阵，想起来还没跟你说今天的事。']],
 call:[['你好，现在方便聊一会儿吗？','听到你声音啦，今天过得怎么样？'],['没什么急事，打个电话问候一下。','就想聊点最近的小事，不用特意准备话题。']],
 video:[['画面清楚吧？我们随便聊聊。','看见你啦，今天状态怎么样？'],['我找个合适的位置放手机。','这个角度正好，咱们慢慢聊。']],
 visit:[['谢谢招待，坐一会儿聊聊就好。','又来你家坐坐啦，今天不聊什么大道理。'],['我把东西放这里可以吗？','你忙的话我就先歇一会儿，咱们不用一直说话。']]
};
PERSONALITY_REPLIES.balanced=['好的，咱们慢慢聊。','我在听，你接着说。','今天能聊一会儿就挺好。'];
