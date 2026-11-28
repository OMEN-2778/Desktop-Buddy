(function installLiweiNeighborhood() {
  if (!window.liweiStory) return;
  const story = window.liweiStory;
  const city = seasonMapTest.state.autumn;
  const X = springFarm.X;
  const shopTitle = "栗尾维修记";
  const special = {id:"shop",title:shopTitle,kind:"repair",day:0,steps:LIWEI_SHOP_STORY};
  const placeLabels = {bay_market:"草帽湾 · 海棠集市",farm_yard:"茵菲谷 · 农舍"};
  const travelers = {bay_market:"summer_test",farm_yard:"spring_test"};
  const products = {pumpkin:"南瓜",carrot:"胡萝卜"};
  const equipment = [
    ["coil","回收线圈",4,"自动扫频多一个起手回收线圈"],
    ["display","修理铺的灯牌",3,"柜台点亮一盏店灯"],
    ["record","刻纹唱片",4,"把维修铺的音乐收进收藏"],
  ];
  const blank = () => ({since:null,jobs:{},shopOpen:false,orders:{},paidDay:-1,owned:[],effects:[],investment:null,investDay:-1,partners:[]});
  let state = blank(), run = null, cancelGame = null, taskWalk = null, talking = false, broadcastNear = false;
  const inTown = () => sim.place === "autumn_test";
  const enabled = () => story.progress.done.includes("S14");
  const day = () => X.today();
  const randomSeed = (id, number) => hashOf(id + ":" + number + ":" + nameOf()) >>> 0;
  const sound = (id, gain=.38) => gameAudio.sound("liwei-repair-"+id,gain,{gap:.12});
  const persist = () => { if (typeof booted !== "undefined" && booted) autoSave(); };
  const pay = (text,amount) => X.record("coin",text,amount);
  const landmark = id => city.DATA.landmarks.find(item=>item.id===id);
  const all = [special,...LIWEI_SIDE_STORIES];
  const status = q => state.jobs[q.id];
  const current = q => q.steps[status(q)?.step || 0];
  const taskDay = q => q.steps[status(q)?.step || 0]?.[5] ? (status(q)?.day ?? day())+q.steps[status(q).step][5] : -1;
  const titleAt = id => placeLabels[id] || landmark(id)?.name || "栗尾市";
  function offers() {
    if (!enabled() || state.since == null) return [];
    return all.filter(q=>day()>=state.since+q.day || status(q));
  }
  function activeAt(id) {
    return offers().filter(q => current(q)?.[0]===id && day()>=taskDay(q));
  }
  function safeToPlay() {
    if (sim.mode==="down") return "先长按叫醒小人";
    if (wiping || story.active || storySpeechOpen() || phoneHolds() || talking) return "等眼前这段结束";
    return null;
  }
  function element(tag, className="", text="") {
    const el = document.createElement(tag);
    if (className) el.className=className;
    if (text) el.textContent=text;
    return el;
  }
  function button(text, action, {info,label,disabled=false}={}) {
    const b=element("button","rw-btn",text);
    b.type="button";
    b.disabled=disabled;
    if (info) b.append(element("small","",info));
    if (label) b.setAttribute("aria-label",label);
    b.onclick=action;
    return b;
  }
  const overlay=element("section","liwei-repair");
  overlay.hidden=true;
  overlay.setAttribute("aria-label","栗尾维修铺");
  overlay.setAttribute("role","dialog");
  overlay.setAttribute("aria-modal","true");
  const head=element("header","rw-head");
  const headText=element("h2","");
  const body=element("div","rw-body");
  const closeButton=button("×",closeRoom,{label:"关上维修台"});
  const icon=new Image();
  icon.className="rw-tool-icon";
  icon.alt="";
  icon.draggable=false;
  icon.src=QUEST_ICONS.repair;
  head.append(icon,element("i","rw-indicator"),headText,closeButton);
  overlay.append(head,body);
  view.parentElement.append(overlay);
  const benchArt=element("figure","rw-bench-art");
  benchArt.setAttribute("aria-hidden","true");
  const picture=new Image();
  picture.src=LIWEI_REPAIR_BENCH;
  picture.alt="";
  picture.draggable=false;
  benchArt.append(picture,element("b","rw-bench-light"));
  const workbench=element("div","rw-console");
  workbench.append(benchArt);
  function setBody(el) {
    if (!el.classList.contains("rw-game")) {body.replaceChildren(el);return;}
    if (workbench.firstElementChild===benchArt) workbench.prepend(el);
    else workbench.firstElementChild.replaceWith(el);
    if (workbench.parentElement!==body) body.replaceChildren(workbench);
  }
  let priorFocus=null;
  function position() {
    const rect=view.getBoundingClientRect();
    const host=view.parentElement.getBoundingClientRect();
    Object.assign(overlay.style,{left:rect.left-host.left+"px",top:rect.top-host.top+"px",width:rect.width+"px",height:rect.height+"px"});
  }
  function openRoom(title) {
    cancelGame?.();
    cancelGame=null;
    if (overlay.hidden) priorFocus=document.activeElement;
    city.close();
    city.clearKeys();
    city.clearRoute();
    city.playerInput();
    closeRing();
    questBoard.close();
    headText.textContent=title;
    overlay.hidden=false;
    position();
    closeButton.focus({preventScroll:true});
    sound("open");
  }
  function closeRoom() {
    if (overlay.hidden) return;
    overlay.hidden=true;
    cancelGame?.();
    cancelGame=null;
    run=null;
    sound("switch",.25);
    if (priorFocus?.isConnected) priorFocus.focus({preventScroll:true});
    priorFocus=null;
  }
  addEventListener("resize",()=>{if(!overlay.hidden)position();});
  overlay.addEventListener("keydown",e=>{
    if (e.key==="Escape") {e.stopImmediatePropagation(); e.preventDefault(); closeRoom();}
  });
  STORY_HOLDS.push(()=>talking||!overlay.hidden);
  const previousHolds=cardHolds;
  cardHolds=()=>previousHolds()||talking||!overlay.hidden;
  const speech=createStorySpeech({
    view,
    speakerFor:name=>({name,id:"liwei-neighborhood:"+name,anonymous:true,portrait:()=>story.frameFor(name)}),
    onClose:()=>{talking=false;speech.hide();},
  });
  function tell(rows, done) {
    if (safeToPlay()) return;
    questBoard.close();
    if (inTown()) city.close();
    talking=true;
    let index=0;
    function next() {
      if (index===rows.length) {
        talking=false;
        speech.hide();
        done?.();
        return;
      }
      const [who,line]=rows[index++];
      speech.show(who==="我"?nameOf():who,line,{asNpc:who!=="我",last:index===rows.length,advance:next});
    }
    next();
  }
  function completeStep(q, rows, step) {
    const job=state.jobs[q.id] ||= {step:0, day:day(),log:[]};
    if (job.step!==step) return;
    job.log.push({day:day(),title:q.steps[step][1],lines:rows.map(([who,text])=>[who==="我"?nameOf():who,text])});
    job.day=day();
    job.step++;
    if (!current(q)) {
      if (q===special) state.shopOpen=true;
      const journal="任务完成 · "+q.title;
      log(journal);
      if (q.coin) pay(q.title,q.coin);
      if (q.item) X.addItem(q.item);
      sound("success",.45);
      const item=X.ITEMS[q.item]?.name || products[q.item];
      showHint(journal+(q.coin?"　+"+q.coin+" 丢丢币":item?"　获得 "+item:""));
    }
    persist();
  }
  function doStep(q) {
    const step=status(q)?.step||0;
    const s=current(q);
    if (!s || day()<taskDay(q) || safeToPlay()) return;
    if (q===special) {
      if (step===4 && status(q)?.briefed) return play(tutorial());
      const rows=s[2];
      return tell(rows,()=>{
        if (step===4) {
          state.jobs.shop.briefed=true;
          persist();
          play(tutorial());
        } else completeStep(q,rows,step);
      });
    }
    const rows=[[s[2],s[3]],["我",s[4]]];
    tell(rows,()=>completeStep(q,rows,step));
  }
  function tutorial() {
    return {id:"tutorial",type:"radio",title:"许师傅的旧收音机",client:"许师傅",detail:"让它重新收到晚间广播。",seed:912,coin:0};
  }
  function feed() {
    state.since ??= day();
    const cur=day();
    const candidates=LIWEI_REPAIR_ORDERS.filter(row=>!(story.progress.ending==="B" && row[1]==="工人代表"));
    const rng=liweiRepairRandom(randomSeed("work-orders",cur));
    const byType=Object.keys(LIWEI_REPAIR_TYPES).map(type=>{
      const pool=candidates.filter(row=>row[0]===type);
      return pool[rng(pool.length)];
    });
    const featured = [
      ["pipes","漏水的控制盒",0], ["bike","蓝绳小童车",1],
      ["radio","广场的旧广播",2], ["tape","夜班开饭的录音",3],
    ].find(([type,title,offset])=>cur>=(state.jobs.shop?.day??cur)+offset &&
      !Object.values(state.orders).some(order=>order.title===title));
    if (featured) {
      const [type,title] = featured;
      const index = byType.findIndex(item=>item[0]===type);
      byType[index] = LIWEI_REPAIR_ORDERS.find(item=>item[2]===title);
    }
    const paid = featured ? byType.findIndex(item=>item[2]===featured[1]) : rng(byType.length);
    const newOrders=byType.map(([type,client,title,detail],i)=>({
      id:cur+"-"+type,day:cur,type,client,title,detail,seed:rng(0x7fffffff),coin:i===paid ? (title==="广场的旧广播"?3:cur%4===0?2:1):0,
    }));
    return [...Object.values(state.orders).filter(order=>!order.delivered && order.day<cur),...newOrders.map(order=>state.orders[order.id]||order)];
  }
  function orderInfo(order) {
    return LIWEI_REPAIR_TYPES[order.type]+" · "+(order.coin?order.coin+" 丢丢币":"人情单");
  }
  function play(order, practice = false) {
    if (order.delivered) return;
    if (order.completed) return deliver(order);
    if (!practice && order.id!=="tutorial") {
      state.orders[order.id]=order;
      persist();
    }
    openRoom(order.title);
    run=order.id;
    cancelGame=runLiweiRepair({...order,shopTool:state.owned.includes("coil")?"coil":null},{
      element,button,setBody,sound,alive:()=>run===order.id&&!overlay.hidden
    },()=>{
      run=null;
      if (practice) {
        setBody(result("测试通过","可以换一个玩法，或者用同一张样单再试。",practiceMenu,"回维修测试"));
        return;
      }
      if (order.id==="tutorial") {
        completeStep(special,LIWEI_SHOP_STORY[4][2],4);
        setBody(result("收音机响了", "把它拿回给许师傅。",()=>{closeRoom();doStep(special);}, "交还收音机"));
        return;
      }
      order.completed=true;
      persist();
      setBody(result("测试通过",order.client+"还等着拿东西。",()=>deliver(order),"交货"));
    });
  }
  function result(title,text,action,label) {
    const node=element("div","rw-result");
    node.append(element("i","rw-result-glint"),element("h3","",title),element("p","rw-note",text),button(label,action));
    return node;
  }
  const customerLines = {
    radio:["接上了！刚才那句报的是晚上吃什么？","听着像豆腐。我拧回去再听一遍。"],
    bike:["这圈终于安静了。以前我骑到半街，人家光听声就知道是我。","那下次就记得摁铃。"],
    clock:["它上回走得这么正，还是我搬来那天。","行，明早可以用它准点起床了。"],
    pipes:["桶底干着呢！我先把地上的旧毛巾收了。","那条别急着扔，擦工作台挺好。"],
    tape:["录着呢，后头还真有声。我以为那截早磨没了。","找个安静地方再听一遍吧。"],
  };
  const specialTapes = {
    "夜班开饭的录音":["老郑，你先别把门锁了！后头还有人下班。","记起来了。那天我多留了一把面，糊锅里了。还以为他们没听见我喊。"],
    "店门口的旧录音":["门铃响两下，许师傅在屋里说，今天风挺大。","我当时录它干嘛呢？还好录了。留这里吧，回头你开门也响两下。"],
    "换班留声带":["你先出去，我把灯关了。明儿还是这点见。","后来就散了，谁也没想到那天是最后一回。你给我留这半段就行。"],
  };
  function deliver(order) {
    if (!order.completed || order.delivered) return;
    if (order.coin && state.paidDay===day()) return showHint("今天已经结过一张付费单，这张明天还能交。");
    closeRoom();
    const [clientLine, reply]=customerLines[order.type];
    const archive=specialTapes[order.title];
    const rows=archive?[[order.client,"先放一下后半截，听听还能不能接上。"],["录音",archive[0]],[order.client,archive[1]]]:
      [[order.client,clientLine],["我",reply]];
    tell(rows,()=>{
      if (order.delivered) return;
      order.delivered=true;
      const reward=order.coin;
      if (reward) {state.paidDay=day();pay("修理 · "+order.title,reward);}
      if (!state.effects.includes(order.type)) state.effects.push(order.type);
      if (order.type==="radio" && order.title.includes("广播") && !state.effects.includes("broadcast")) state.effects.push("broadcast");
      log("修好了"+order.client+"的"+order.title+"。"+(reward?" 收到 "+reward+" 枚丢丢币。":""));
      persist();
      sound("success",.5);
      openRoom("栗尾维修铺");
      setBody(result("交货完成",reward?"收到 "+reward+" 枚丢丢币":"街坊把修好的东西带走了。",board,"回委托板"));
    });
  }
  function tab(text,fn) {return button(text,()=>{sound("select");fn();});}
  function makeList(heading,controls,items) {
    const wrap=element("div","rw-list");
    const top=element("nav","rw-actions");
    top.append(...controls);
    wrap.append(top,element("p","rw-note",heading),...items);
    return wrap;
  }
  function board() {
    openRoom("栗尾维修铺");
    const retained=feed().filter(order=>!order.delivered);
    const orders=retained.map(order=>{
      const waitPay=order.completed&&order.coin&&state.paidDay===day();
      const action=order.completed?(waitPay?"明天交货":"交货"):"上工作台";
      const card=element("article","rw-order");
      const heading=element("div","");
      heading.append(element("h3","",order.title),element("p","",order.client+"　"+orderInfo(order)),element("p","rw-quote",order.detail));
      card.append(heading,button(action,()=>play(order),{disabled:!!waitPay}));
      return card;
    });
    setBody(makeList("余额 "+X.F.coins+" 丢丢币 · 每天结算一张付费修理单",[
      tab("街坊合伙",partners),tab("工具和摆件",supplies)
    ],orders.length?orders:[element("p","rw-note","今天都取走了。明天再开门看看。")]));
  }
  function supplies() {
    openRoom("工具和摆件");
    const items=equipment.map(([id,name,price,detail])=>{
      const owned=state.owned.includes(id);
      return button(name+(owned?" · 已拥有":" · "+price+" 币"),()=>{
        if (state.owned.includes(id)||X.F.coins<price) return;
        state.owned.push(id);
        pay("添置 · "+name,-price);
        persist();
        sound("success");supplies();
      },{info:detail,disabled:owned||X.F.coins<price});
    });
    if (state.owned.includes("record")) items.push(button("听唱片的开头",()=>sound("broadcast",.5)));
    setBody(makeList("余额 "+X.F.coins+" 丢丢币",[tab("回委托板",board)],items));
  }
  function partners() {
    openRoom("街坊合伙");
    const cur=day();
    if (state.investment) {
      const stake=state.investment;
      const offer=LIWEI_PARTNERS.find(item=>item.id===stake.id);
      const due=cur>=stake.due;
      setBody(makeList(offer.host+"正在做「"+offer.name+"」",[tab("回委托板",board)],[
        element("p","rw-note",due?"已经捎话来，可以看结果了。":"还要等 "+(stake.due-cur)+" 天。"),
        button("听听做得怎样",()=>settle(stake,offer),{disabled:!due}),
      ]));
      return;
    }
    const start=Math.floor(cur/3)%LIWEI_PARTNERS.length;
    const options=[LIWEI_PARTNERS[start],LIWEI_PARTNERS[(start+2)%LIWEI_PARTNERS.length]];
    setBody(makeList("余额 "+X.F.coins+" 丢丢币 · 同时挑一个项目",[tab("回委托板",board)],options.map(offer=>{
      const card=element("article","rw-order");
      const copy=element("div","");
      copy.append(element("h3","",offer.host+" · "+offer.name),element("p","",offer.brief),element("p","rw-quote",offer.hope+" "+offer.risk));
      card.append(copy,button("考虑出 "+offer.cost+" 币",()=>consider(offer),{disabled:X.F.coins<offer.cost||cur<=state.investDay}));
      return card;
    })));
  }
  function consider(offer) {
    const options=element("div","rw-actions");
    const wrap=result("给「"+offer.name+"」投 "+offer.cost+" 币？","要等 "+offer.days+" 天。"+offer.risk,()=>{
      if (state.investment||day()<=state.investDay||X.F.coins<offer.cost) return;
      const started=day();
      const roll=liweiRepairRandom(randomSeed(offer.id,started))(100);
      state.investment={id:offer.id,due:started+offer.days,roll};
      state.investDay=started;
      pay("合伙投入 · "+offer.name,-offer.cost);
      log("答应和"+offer.host+"试做「"+offer.name+"」。");
      persist();
      partners();
    },"确定投入");
    options.append(button("我再看看",partners));
    wrap.append(options);
    setBody(wrap);
  }
  function settle(stake,offer) {
    if (state.investment!==stake || day()<stake.due) return;
    closeRoom();
    const win=stake.roll<45, even=stake.roll>=45&&stake.roll<70;
    const first=!state.partners.some(item=>item.id===offer.id&&item.win);
    const returned=win?offer.cost+(first?1:0):even?offer.cost:Math.max(1,offer.cost-2);
    tell([[offer.host,win?offer.win:even?"忙了一圈，钱刚好都回来。下回我想先少做几份，看看哪样卖得快。":offer.lose],["我",win?"那下回开门，记得叫我。":"行，你慢慢来。账我记下了。"]],()=>{
      if(state.investment!==stake) return;
      state.investment=null;
      state.partners.push({id:offer.id,win,day:day()});
      pay("合伙回款 · "+offer.name,returned);
      if(win&&offer.item)X.addItem(offer.item);
      log(offer.host+"做完了「"+offer.name+"」这一轮。收回 "+returned+" 枚丢丢币。");
      persist();
      openRoom("街坊合伙");
      setBody(result(win?"开张顺利":even?"这次打平":"这一回没回本","收回 "+returned+" 枚丢丢币。",partners,"回合伙板"));
    });
  }
  function site(id) {
    if (!enabled()) return false;
    const tasks=activeAt(id);
    if (!tasks.length && (id!=="store"||!state.shopOpen)) return false;
    if(id==="detective_home"&&!tasks.includes(taskWalk?.quest))return false;
    if(taskWalk?.id===id&&tasks.includes(taskWalk.quest)){
      const quest=taskWalk.quest;
      taskWalk=null;
      doStep(quest);
    } else if(tasks.length===1 && (id==="store"&&!state.shopOpen || travelers[id])) {
      doStep(tasks[0]);
    } else {
      city.panel(id==="store"&&state.shopOpen?"栗尾维修铺":titleAt(id),"",[
        ...tasks.map(q=>[q.title,()=>doStep(q)]),
        ...(id==="store"&&state.shopOpen?[["打开委托板",board]]:[]),
        ...(id!=="store"&&!travelers[id]?[["继续原本的活动",()=>{ignoreSite=true;try{city.interact(id);}finally{ignoreSite=false;}}]]:[]),
        ["先离开"],
      ]);
    }
    return true;
  }
  let ignoreSite=false;
  function go(q) {
    const wait=safeToPlay();
    if (wait) return wait;
    const step=current(q);
    if (!step) return "这件事已经做完";
    if(day()<taskDay(q)) return "请等到明天再去";
    const id=step[0], dest=travelers[id] || "autumn_test";
    questBoard.close();
    if(sim.place!==dest){
      if(sim.place==="airport_test") {
        if(dest==="summer_test" && ![1,2].includes(seasonOf(sim.t).i)) return "草帽湾航班在夏、秋两季开放";
        throughDoor(dest);
        return {say:"搭航班去"+titleAt(id)};
      }
      if(seasonMapTest.active()) return "请先从本地机场或返程入口回家";
      throughDoor("airport_test");
      return {say:"先去机场"};
    }
    taskWalk={quest:q,id};
    if(dest!=="autumn_test") {
      if(atHandoff(id)){taskWalk=null;doStep(q);return {say:"找到"+step[2]};}
      if(goElsewhere(id))return {say:"去找"+step[2]};
      taskWalk=null;
      return "等转场和眼前的动作结束";
    }
    window.autumnHome?.cancelActivity();
    city.playerInput();
    city.state.mapOpen=false;
    if (city.state.inside) {
      taskWalk.leaving=true;
      city.leave();
      return {say:"先出门"};
    }
    if(!city.visit(id)){taskWalk=null;return "这会儿过不去";}
    return {say:"前往"+titleAt(id)};
  }
  function goElsewhere(id) {
    seasonMapTest.state.autoAt=sim.t+90;
    if(id==="farm_yard") {
      const farm=seasonMapTest.state.spring, s=farm.state;
      if(s.edge||s.door)return true;
      if(s.inside){farm.leave();return true;}
      if(farm.current().id!=="home"){farm.travel(-1);return true;}
      const x=93;
      farm.target(x);
      return true;
    }
    const bay=seasonMapTest.state.summer, s=bay.state;
    if(s.door) return true;
    if(s.inside){bay.leave();return true;}
    if(!s.market) {
      if(s.y>132){bay.goTo(1050,"dive",128);return true;}
      return bay.goTo(50,"walk",0,()=>bay.beginDoor("market"));
    }
    return bay.goTo(548,"walk",0);
  }
  function atHandoff(id) {
    const c=id==="farm_yard"?seasonMapTest.state.spring:seasonMapTest.state.summer, s=c.state;
    if(s.inside||s.door||s.edge)return false;
    return id==="farm_yard"?c.current().id==="home"&&Math.abs(s.x-93)<6 : s.market&&Math.abs(s.x-548)<9;
  }
  function trackTravel() {
    if (!taskWalk || wiping || talking || !speed) return;
    const {id,quest}=taskWalk;
    const step=current(quest);
    if(step?.[0]!==id || (travelers[id]||"autumn_test")!==sim.place) {taskWalk=null;return;}
    if (inTown()) {
      if(city.state.door||city.state.inside||city.state.target) return;
      if (taskWalk.leaving) {
        taskWalk.leaving=false;
        if(!city.visit(id))taskWalk=null;
      } else taskWalk=null;
      return;
    }
    const c=id==="farm_yard"?seasonMapTest.state.spring:seasonMapTest.state.summer;
    if(c.state.door||c.state.target||c.state.edge) return;
    if(atHandoff(id)){taskWalk=null;doStep(quest);}else goElsewhere(id);
  }
  setInterval(()=>{
    if(!enabled())return;
    if(state.since==null){state.since=day();persist();}
    trackTravel();
    const near=nearBroadcast();
    if(near&&!broadcastNear&&!cardHolds())sound("broadcast",.32);
    broadcastNear=near;
    if(!overlay.hidden){
      if(!inTown())closeRoom();
      else position();
    }
  },220);
  function nearBroadcast() {
    if (!inTown() || city.state.inside || !state.effects.includes("broadcast") || hour()<17 || hour()>=20) return false;
    const canteen=landmark("canteen");
    return Math.hypot(city.state.x-canteen.x,city.state.y-canteen.y)<75;
  }
  function drawAway(c) {
    const id=sim.place==="summer_test"&&c.state.market?"bay_market":
      sim.place==="spring_test"&&c.current().id==="home"?"farm_yard":null;
    if(!id||c.state.inside)return;
    const q=activeAt(id)[0];
    if(!q)return;
    const ctx=c.renderCanvas.getContext("2d"), s=c.state;
    ctx.save();
    const res=c.renderCanvas.width/342;
    ctx.setTransform(res,0,0,res,0,0);
    drawQuestMarker(ctx,id==="bay_market"?548-Math.round(s.camX):93-s.camera,73,"?",()=>go(q));
    ctx.restore();
  }
  function drawOutdoor(ctx) {
    if(!enabled() || !inTown() || city.state.inside || city.state.mapOpen) return;
    const store=landmark("store"), notice=landmark("notice");
    if(state.shopOpen&&store){
      const x=store.x-16,y=store.y-28;
      ctx.fillStyle="#342331";ctx.fillRect(x,y,32,10);
      ctx.fillStyle=state.owned.includes("display")?"#f7b85e":"#a76542";ctx.fillRect(x+1,y+1,30,8);
      ctx.font="7px sans-serif";ctx.textAlign="center";ctx.fillStyle="#fff1c5";ctx.fillText("修理铺",x+16,y+7);
    }
    for(const id of new Set(offers().map(q=>current(q)?.[0]).filter(id=>id&&!travelers[id]))){
      const loc=landmark(id);
      if(!loc||!activeAt(id).length)continue;
      drawQuestMarker(ctx,loc.x,loc.y-22,activeAt(id).some(q=>status(q)?.step)?"?":"!",()=>{
        const list=activeAt(id);
        if(list.length===1)go(list[0]);
        else city.visit(id);
      });
    }
    const canteen=landmark("canteen");
    if(canteen&&state.effects.includes("broadcast")&&hour()>=17&&hour()<20){
      const x=canteen.x+21,y=canteen.y-24;
      const beat=reduceMotionUI?0:Math.floor(realClock*5)%4;
      ctx.fillStyle="#493544";ctx.fillRect(x,y,8,9);
      ctx.fillStyle="#ffd67d";ctx.fillRect(x+1,y+1,6,3);
      ctx.fillRect(x+10+beat,y-2-beat,2,4);
      ctx.fillRect(x+8+beat,y+1-beat,3,2);
    }
    if (notice&&state.partners.some(p=>p.win)) {
      ctx.fillStyle="#bd8052";ctx.fillRect(notice.x+10,notice.y-20,9,10);
      ctx.fillStyle="#eed68a";ctx.fillRect(notice.x+11,notice.y-19,7,7);
    }
  }
  questBoard.add(()=>offers().map(q=>{
    const job=status(q), done=!current(q), loc=current(q)?.[0];
    return {id:"liwei-neighborhood-"+q.id,group:q===special?"liwei-special":"side",title:q.title,kind:q.kind,theme:q===special?"liwei-repair":null,
      isNew:!job,offer:q!==special&&!job,done,place:loc?titleAt(loc):"栗尾市",
      end:q===special?"拿到了维修铺的钥匙":q.coin?"收到 "+q.coin+" 枚丢丢币":q.item?"获得街坊送的小礼物":"完成了",
      step:current(q)?.[1],log:job?.log,go:()=>go(q)};
  }));
  const previousSnapshot=snapshot;
  snapshot=function(){const save=previousSnapshot();save.liweiNeighborhood=JSON.parse(JSON.stringify(state));return save;};
  const previousRestore=restore;
  restore=function(save){
    closeRoom();
    speech.hide();
    taskWalk=null;
    talking=false;
    broadcastNear=false;
    const out=previousRestore(save);
    state=Object.assign(blank(),save?.liweiNeighborhood);
    return out;
  };
  const control=element("button","liwei-repair-entry","栗尾维修铺");
  control.type="button";
  control.hidden=true;
  control.onclick=()=>{const wait=safeToPlay();if(wait)return showHint(wait);go(shopAccess);};
  const shopAccess={id:"shopAccess",steps:[["store","回栗尾维修铺"]]};
  seasonMapTest.root.querySelector("header").append(control);
  setInterval(()=>{control.hidden=!(inTown()&&state.shopOpen);},350);
  function practiceMenu() {
    openRoom("直接测试维修台");
    const samples=Object.entries(LIWEI_REPAIR_TYPES).map(([type,label])=>{
      const [,client,title,detail]=LIWEI_REPAIR_ORDERS.find(order=>order[0]===type);
      return button(label,()=>play({
        id:"practice-"+type,type,client,title,detail,seed:randomSeed("practice-"+type,day()),coin:0,
      },true),{info:title});
    });
    setBody(makeList("选择一个玩法。练习样单不结算工钱。",[],samples));
  }

  const testUrl=new URL(location.href);
  const repairTest=testUrl.searchParams.get("repair-test")==="1";
  if (repairTest) {
    const controls=element("span","");
    controls.id="liweiRepairTest";
    const stepLabel=element("span","");
    const skip=button("完成当前阶段",()=>startTest(()=>{
      const index=status(special)?.step||0;
      const part=current(special);
      if (!part) {board();return;}
      completeStep(special,part[2],index);
      updateTest();
      if (state.shopOpen) board();
      else {
        placeAt(current(special)[0]);
        showHint("已完成第 "+(index+1)+" 段 · "+current(special)[1]);
      }
    }));
    const direct=button("直接测试维修台",()=>startTest(practiceMenu));
    controls.append(stepLabel,skip,direct);
    seasonMapTest.root.querySelector("header").append(controls);
    function placeAt(id) {
      const spot=landmark(id);
      city.clearRoute();
      Object.assign(city.state,{inside:false,door:null,mapOpen:false,x:spot.x,y:spot.y});
      city.syncHeight();
      city.snapCamera();
      seasonMapTest.sync();
    }
    function updateTest() {
      const part=current(special);
      stepLabel.textContent=part?"独立测试档 · 第 "+((status(special)?.step||0)+1)+" / "+special.steps.length+" 阶段":"独立测试档 · 修理铺已开张";
      skip.disabled=!part;
    }
    function startTest(action) {
      if (!booted || !city.state.loaded) {showHint("栗尾市正在载入");return;}
      if (wiping || story.active || phoneHolds()) {showHint("等这段转场或对白结束");return;}
      closeGuide();
      closeRoom();
      if (talking) {talking=false;speech.hide();}
      if (!inTown()) {
        sim.place="autumn_test";
        sim.dest=null;
        sim.mode="idle";
        sim.act=null;
        arriveAt("autumn_test");
      }
      if (!enabled()) {
        Object.assign(story.progress,{
          done:Object.keys(LIWEI_SCRIPT).filter(id=>!id.startsWith("R")&&!["S12A","A1","A2"].includes(id)),
          ending:"B",enrolled:true,visitTimePassed:true,
        });
        Object.assign(story.progress.choices,{S02:0,S11:1});
        city.state.stage=4;
        city.state.quest=6;
      }
      state.since ??= day();
      placeAt(current(special)?.[0]||"store");
      action();
      updateTest();
    }
    setInterval(updateTest,500);
    updateTest();
  } else {
    testUrl.searchParams.set("repair-test","1");
    const testLink=element("a","","维修测试（独立存档）");
    testLink.href=testUrl.href;
    seasonMapTest.root.querySelector("header").append(testLink);
  }

  window.liweiNeighborhood={
    shopOpen:()=>enabled()&&state.shopOpen,
    talkCustomer(person){
      if(!enabled()||!state.shopOpen||!inTown())return false;
      const lines=["我先等前面那位。我的车再响两声也还能骑。","我怀里这个是好钟。我是说，它没坏的时候挺好。","我还没想好修不修，先看看摆的是什么价。"];
      tell([[person.name,lines[(person.local+day())%lines.length]]]);
      return true;
    },
    site:id=>!ignoreSite&&site(id),
    choices:id=>ignoreSite?[]:activeAt(id).map(q=>[q.title,()=>doStep(q)]),
    drawOutdoor,drawAway,
    music:()=>!overlay.hidden?"BGM/liwei/repair-after-hours.mp3":null,
  };
})();
