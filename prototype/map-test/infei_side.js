// 茵菲谷: more side quests (owner 2026-11-03: "各个地图里都随机增加点支线任务"), one per scene. Who offers one
// shows up on some days only (a seeded daily roll), so they turn up at random; once taken they are there every day.
//   小溪边   林老师的速写   stand still for a sketch, see it the next day
//   油菜花田 老蔡的蜂       a swarm got away, find it in the orchard
//   郁金香田 小吴的包裹     the postman's chain broke: take a parcel to 林老师
//   农舍门口 门口的小狗     a dog with a bell: whose is it?
//   菜地     刘婶借菜       lend a crop, get dumplings back
//   牧场     阿木的口琴     a lost harmonica in the orchard grass
(function(){
 const Q0=infeiQuests,K=Q0.kit,{say,ask,walkTo,finish,crops,take,note,me,today,hour,X,S,C}=K;
 const Q=()=>Q0.Q(),done=()=>S().phase==='done';
 const roll=(id,p)=>{let h=Math.imul(today()+1,2654435761)^[...id].reduce((a,c)=>Math.imul(a,31)+c.charCodeAt(0)|0,7);h=Math.imul(h^h>>>15,2246822507)>>>0;return h%1000<p*1000;};
 const hours=(a,b)=>hour()>=a&&hour()<b;
 // a giver: there while their quest runs, on some days before (to offer it) and after (to chat)
 const giver=(id,a,b,more=()=>false)=>q=>{const st=q[id].step;if(!hours(a,b))return false;if(more(q))return true;return st===0?roll(id,.55):st===9?roll(id+'~',.35):true;};
 const nextDay=id=>today()>(Q()[id].day??1e9);
 const eat=n=>{sim.needs.hunger=Math.min(100,sim.needs.hunger+n);};
 const vl=(name,g,seed,o,vis)=>{const v=K.villager(name,g,seed,o);v.vis=vis;return v;};
 const V={
  lin:vl('林老师','f',71,{scene:0,x:285},giver('sketch',8,17,q=>q.parcel.step===1)),
  cai:vl('老蔡','m',83,{scene:1,x:95},giver('bees',6,18)),
  wu:vl('小吴','m',97,{scene:2,x:175},giver('parcel',9,16,q=>q.dog.step===1)),
  liu:vl('刘婶','f',109,{scene:4,x:296},giver('borrow',7,18)),
  amu:vl('阿木','m',127,{scene:5,x:290,kid:true},giver('harp',8,18))};
 Object.assign(V.lin,{hours:[8,17]});Object.assign(V.cai,{hours:[6,18]});Object.assign(V.wu,{hours:[9,16]});Object.assign(V.liu,{hours:[7,18]});Object.assign(V.amu,{hours:[8,18]});   // for the 任务 panel's "not here now" bubble
 const reg=(o)=>Q0.register(o);
 // ---------------------------------------------------------------- 小吴的包裹 (first: its goal on 林老师 comes before hers)
 reg({id:'parcel',title:'小吴的包裹',kind:'gift',end:'把颜料送到了林老师手里',home:'郁金香田',place:['郁金香田','小溪边'],scenes:['链子掉了','送包裹'],icons:['gift','gift'],
  mood:['帮小吴送包裹','happy'],villagers:{wu:V.wu},
  idle:{wu:[['小吴','今天信少，下午能早点回去。'],['小吴','这车该换了，一天掉三回链子。']]},
  goals:q=>{const st=q.parcel.step;return st===0?[{id:'parcel',v:V.wu,mark:'!'}]:st===1?[{id:'parcel',v:V.lin,mark:'?',hint:'把包裹送去小溪边给林老师'}]:[];},
  run:[async()=>{
   await say('小吴','哎，你等等！');
   await say('小吴','链子又掉了，我这一手油。');
   await say(me(),'要帮忙吗？');
   await say('小吴','不用不用，我自己弄。就是这个包裹……');
   await say('小吴','小溪边画画的林老师的，她等好些天了。');
   if(await ask('小吴','你要是顺路，帮我捎过去？',['行，我送过去','您这车多少年了？'])===1){
    await say('小吴','跟我差不多大。');await say(me(),'……那我帮您送包裹吧。');}
   await say('小吴','谢了啊。轻拿轻放，里头可能是瓶子。');
   Q().parcel.step=1;showHint('把包裹送去小溪边给林老师');},
  async()=>{
   await say(me(),'林老师，小吴让我带的包裹。');
   await say('林老师','我的颜料！');
   await say('林老师','城里订的，等了半个月，还以为寄丢了。');
   await say(me(),'他车链子掉了，走不过来。');
   await say('林老师','又掉了？上礼拜也是。');
   await say('林老师','替我谢谢他。');
   finish('parcel','替小吴把包裹送给了林老师，是一盒颜料。');}]});
 // ---------------------------------------------------------------- 林老师的速写
 reg({id:'sketch',title:'林老师的速写',kind:'scroll',end:'林老师把画送给了你',home:'小溪边',place:['小溪边','小溪边'],scenes:['别动','看画'],icons:['scroll','scroll'],
  mood:['被画进了画里','happy'],villagers:{lin:V.lin},
  idle:{lin:[['林老师','这儿的水，一天一个颜色。'],['林老师','今天光不好，随便画画。']]},
  goals:q=>{const st=q.sketch.step;return st===0?[{id:'sketch',v:V.lin,mark:'!'}]:st===1?[{id:'sketch',v:V.lin,mark:'?',hint:nextDay('sketch')?'去小溪边看林老师的画':'明天再去小溪边找林老师'}]:[];},
  run:[async()=>{
   await say('林老师','哎，你先别动。');
   await say(me(),'啊？');
   await say('林老师','就这么站着。你站的地方，正好是我画里缺的那一块。');
   if(await ask('林老师','一会儿就好。',['行，站多久？','我是不是挡着您了？'])===0){
    await say('林老师','十分钟。手别乱放。');await say(me(),'……手该放哪儿？');await say('林老师','就刚才那样。');}
   else{await say('林老师','没挡，你就是那块要画的。');await say(me(),'哦。');}
   await say(me(),'……');
   await say('林老师','好了，样子有了。');
   await say('林老师','明天上完色给你看。');
   Object.assign(Q().sketch,{step:1,day:today()});},
  async()=>{
   if(!nextDay('sketch')){await say('林老师','还没画完，水彩干得慢。');return;}
   await say('林老师','来，看看。');
   await say(me(),'这个小人是我？');
   await say('林老师','嗯，就这么大。离得远嘛。');
   note({letter:'林老师的速写',text:'小溪、木桥、两棵柳树。\n桥头站着一个很小的人，手不知道往哪儿放。'});
   const i=await ask('林老师','送你了。',['谢谢，我挂家里','我脸上就一个点？']);
   await say('林老师',['挂门口那面墙，光好。','离那么远，画上鼻子就吓人了。'][i]);
   finish('sketch','溪边的林老师画了一张速写，桥头那个小人是你。');}]});
 // ---------------------------------------------------------------- 老蔡的蜂
 const swarm={scene:5,rect:[60,14,80,62],x:100};
 reg({id:'bees',title:'老蔡的蜂',kind:'flower',end:'跑掉的蜂落在了你家果园',home:'油菜花田',place:['油菜花田','果园','油菜花田'],scenes:['蜂跑了','果园里','告诉老蔡'],icons:['flower','lens','flower'],
  mood:['尝到了油菜花蜜','happy'],villagers:{cai:V.cai},spots:{swarm},
  idle:{cai:[['老蔡','花开得好，蜂就不闹。'],['老蔡','别穿黑衣服往蜂箱边上凑。']]},
  goals:q=>{const st=q.bees.step;return st===0?[{id:'bees',v:V.cai,mark:'!'}]:st===1?[{id:'bees',spot:'swarm',mark:'?',hint:'去果园的树上找找'}]:st===2?[{id:'bees',v:V.cai,mark:'?',hint:'回油菜花田告诉老蔡'}]:[];},
  run:[async()=>{
   await say('老蔡','你看见我的蜂没？');
   await say(me(),'蜂？');
   await say('老蔡','跑了一窝。早上一开箱，呼啦一下全飞了。');
   await say('老蔡','往东边去的。东边果树多，八成落哪棵树上了。');
   if(await ask('老蔡','你帮我留个心。',['我回去看看','蜂还会自己跑？'])===1){
    await say('老蔡','嫌箱子挤，就分家。');await say('老蔡','跟人一样。');}
   Q().bees.step=1;showHint('去果园的树上找找');},
  async()=>{
   await walkTo(swarm.x);C().state.facing=-1;
   await say(me(),'树杈上挂着一大团……');
   await say(me(),'嗡嗡的，还在动。');
   await say(me(),'还是别碰了，回去叫老蔡。');
   Q().bees.step=2;showHint('回油菜花田告诉老蔡');},
  async()=>{
   await say(me(),'蔡叔，蜂在我家果园，挂在树上。');
   await say('老蔡','果园？那是看上你家果树了。');
   await say('老蔡','我傍晚拿箱子去收，天一凉它们就不爱动。');
   await say('老蔡','这罐你拿着，去年的油菜花蜜。');
   const i=await ask('老蔡','冲水喝，别兑太多。',['谢谢蔡叔','它们收回去还会跑吗？']);
   await say('老蔡',['客气啥。','那得看它们乐不乐意了。'][i]);
   eat(15);
   finish('bees','老蔡跑掉的蜂落在了果园的树上。得了一罐油菜花蜜。');}]});
 // ---------------------------------------------------------------- 门口的小狗
 const DOG={scene:3,rect:[256,70,26,34],x:262};
 reg({id:'dog',title:'门口的小狗',kind:'heart',end:'馒头回老周的饭馆了',home:'农舍门口',place:['农舍门口','郁金香田'],scenes:['门口的小狗','问小吴'],icons:['heart','heart'],
  mood:['馒头找到家了','happy'],spots:{dog:DOG},
  goals:q=>{const st=q.dog.step;return st===0&&hours(7,19)&&roll('dog',.4)?[{id:'dog',spot:'dog',mark:'!'}]:st===1?[{id:'dog',v:V.wu,mark:'?',hint:'问问送信的小吴，他认得各家'}]:[];},
  run:[async()=>{
   await walkTo(DOG.x-14);C().state.facing=1;
   await say(me(),'哪来的小狗？');
   await say(me(),'脖子上挂了个铃铛，刻着字……“馒头”。');
   const have=crops();
   await say(me(),'饿了吧？');
   if(have.length&&await ask('小狗','（尾巴摇个不停）',['从仓库拿点菜给它','先摸摸它'])===0){
    const i=await ask('小狗','（盯着你的手）',have.map(k=>X.CROP[k].name));take(have[i]);
    await say(me(),'……它闻了闻，只吃了一口。');await say(me(),'挑食。');}
   else{await say(me(),'它把肚子翻过来了。');}
   await say(me(),'送信的小吴走得远，问问他认不认得。');
   Q().dog.step=1;showHint('问问送信的小吴，他认得各家');},
  async()=>{
   await say(me(),'小吴，你认得一只叫馒头的狗吗？脖子上挂铃铛的。');
   await say('小吴','馒头？镇上老周饭馆的。');
   await say('小吴','老跟着我的车跑，跑着跑着就不见了。');
   await say(me(),'它在我家门口趴着呢。');
   await say('小吴','我下午顺路给它带回去。');
   await say('小吴','老周找它一上午了，骂了我两回。');
   finish('dog','门口的小狗叫馒头，是老周饭馆的。小吴给带回去了。');}]});
 // ---------------------------------------------------------------- 刘婶借菜
 reg({id:'borrow',title:'刘婶借菜',kind:'basket',end:'借出去的菜换回了一盘饺子',home:'菜地',place:['菜地','菜地'],scenes:['借菜','还饺子'],icons:['basket','cake'],
  mood:['刘婶的饺子','happy'],villagers:{liu:V.liu},
  idle:{liu:[['刘婶','你这地收拾得比我家的齐整。'],['刘婶','你王叔又不知道上哪去了。']]},
  goals:q=>{const st=q.borrow.step;return st===0?[{id:'borrow',v:V.liu,mark:'!'}]:st===1?[{id:'borrow',v:V.liu,mark:'?',hint:nextDay('borrow')?'去菜地边找刘婶':'明天刘婶来还'}]:[];},
  run:[async()=>{
   await say('刘婶','你就是新来那家的吧？我是你王叔家的。');
   await say('刘婶','家里来客人了，我地里的菜还没长好。');
   const have=crops();
   if(!have.length){await say('刘婶','你也还没收啊？');await say('刘婶','那我上别家问问。');return;}
   const i=await ask('刘婶','能借我点不？明天还你。',have.map(k=>X.CROP[k].name).concat('现在不太方便'));
   if(i===have.length){await say('刘婶','没事没事，我再问问。');return;}
   take(have[i]);
   await say('刘婶',`这${X.CROP[have[i]].name}长得真好。`);
   await say('刘婶','明天我拿点东西过来。');
   Object.assign(Q().borrow,{step:1,day:today()});},
  async()=>{
   if(!nextDay('borrow')){await say('刘婶','客人还没走呢，明天啊。');return;}
   await say('刘婶','来，饺子，还热乎。');
   await say(me(),'这么多？');
   await say('刘婶','包多了，客人吃不完。');
   const i=await ask('刘婶','哎，你晚上听见风车那边有声没？',['好像听见了','没听见']);
   if(i===0){await say('刘婶','肯定是你王叔又躲那儿吹唢呐。');await say('刘婶','我就说他天天晚上出去干啥。');}
   else{await say('刘婶','那就好。');await say('刘婶','我还当他又出去吹了。');}
   eat(25);
   finish('borrow','借了刘婶一筐菜，换回来一盘饺子。');}]});
 // ---------------------------------------------------------------- 阿木的口琴
 const grass={scene:5,rect:[180,82,70,22],x:214};
 reg({id:'harp',title:'阿木的口琴',kind:'note',end:'口琴找回来了，阿木就会吹一首',home:'牧场',place:['牧场','果园','牧场'],scenes:['口琴丢了','草里','还口琴'],icons:['note','lens','note'],
  mood:['听阿木吹口琴','playful'],villagers:{amu:V.amu},spots:{grass},
  idle:{amu:[['阿木','我数羊呢，你别跟我说话。'],['阿木','那只花脸的最不听话。']]},
  goals:q=>{const st=q.harp.step;return st===0?[{id:'harp',v:V.amu,mark:'!'}]:st===1?[{id:'harp',spot:'grass',mark:'?',hint:'去果园的草里找找口琴'}]:st===2?[{id:'harp',v:V.amu,mark:'?',hint:'把口琴还给牧场的阿木'}]:[];},
  run:[async()=>{
   await say('阿木','你踩着我口琴没？');
   await say(me(),'没有吧……你丢哪儿了？');
   await say('阿木','早上在果园那边躺了一会儿，回来就没了。');
   if(await ask('阿木','不会让羊吃了吧？',['我帮你去找找','羊不吃口琴'])===1){
    await say('阿木','你又不是羊。');await say(me(),'……行，我去找找。');}
   Q().harp.step=1;showHint('去果园的草里找找口琴');},
  async()=>{
   await walkTo(grass.x);
   await say(me(),'草里有个亮亮的东西。');
   await say(me(),'口琴，上面全是草汁。');
   Q().harp.step=2;showHint('把口琴还给牧场的阿木');},
  async()=>{
   await say('阿木','就是它！');
   await say('阿木','我吹一个给你听。');
   await say('口琴','嘟——嘟嘟——嘟——');
   const i=await ask('阿木','怎么样？',['吹的什么呀？','挺好听的']);
   if(i===0){await say('阿木','小星星。');await say('阿木','我就会这一首。');}
   else{await say('阿木','你骗人，我自己都听出来跑调了。');}
   finish('harp','在果园草里找到了阿木的口琴。他就会吹小星星。');}]});
 // ---------------------------------------------------------------- drawing: the dog, the swarm
 function dog(ctx,x,y,t){const b='#c8925a',d='#8a5a34';ctx.fillStyle=b;ctx.fillRect(x-6,y-6,11,5);ctx.fillRect(x+3,y-10,5,5);ctx.fillRect(x-6,y-1,2,1);ctx.fillRect(x+3,y-1,2,1);
  ctx.fillStyle=d;ctx.fillRect(x+3,y-10,1,3);ctx.fillRect(x+7,y-10,1,3);ctx.fillRect(x-7,y-8+(Math.floor(t*4)%2),1,3);ctx.fillStyle='#3a2a2e';ctx.fillRect(x+6,y-8,1,1);ctx.fillRect(x+8,y-7,1,1);ctx.fillStyle='#f6d36b';ctx.fillRect(x+3,y-5,1,1);}
 function bees(ctx,x,y,t){ctx.fillStyle='#6b4a2a';for(const [dx,dy,w]of [[-3,0,7],[-4,1,9],[-4,2,9],[-3,3,7],[-2,4,5],[-1,5,3]])ctx.fillRect(x+dx,y+dy,w,1);
  ctx.fillStyle='#f6d36b';for(let i=0;i<5;i++){const a=t*3+i*1.3;ctx.fillRect(Math.round(x+Math.cos(a)*7),Math.round(y+3+Math.sin(a*1.7)*5),1,1);}}
 X.hooks.draw.push((ctx,info)=>{if(info.inside||!done())return;const q=Q(),t=info.time;
  if(info.region===3&&(q.dog.step===1||Q0.goals().some(g=>g.spot==='dog')))dog(ctx,DOG.x+Math.round(Math.sin(t*.7)),103,t);
  if(info.region===5&&q.bees.step>=1&&q.bees.step<9)bees(ctx,swarm.x,swarm.rect[1]+26,t);});
})();
