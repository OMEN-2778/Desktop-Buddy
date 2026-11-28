(function installLiweiNeighborhood() {
  if (!window.liweiStory) return;
  const story = window.liweiStory;
  const city = seasonMapTest.state.autumn;
  const X = springFarm.X;
  const shopTitle = "栗尾维修记";
  const stallId = "repair_stall";
  const dailyLimit = 20, closedMessage = "今天好像没有顾客了";
  const special = {id:"shop",title:shopTitle,kind:"repair",day:0,steps:LIWEI_SHOP_STORY};
  const placeLabels = {bay_market:"草帽湾 · 海棠集市",farm_yard:"茵菲谷 · 农舍"};
  const travelers = {bay_market:"summer_test",farm_yard:"spring_test"};
  const products = {pumpkin:"南瓜",carrot:"胡萝卜"};
  const equipment = [
    ["coil","回收线圈",4,"自动扫频多一个起手回收线圈"],
    ["display","修理铺的灯牌",3,"柜台点亮一盏店灯"],
    ["record","刻纹唱片",4,"把维修铺的音乐收进收藏"],
  ];
  const blank = () => ({since:null,jobs:{},shopOpen:false,orders:{},counter:{sequence:0,pending:null,lastType:null},playDay:null,plays:0,paidDay:-1,owned:[],effects:[],investment:null,investDay:-1,partners:[]});
  let state = blank(), run = null, cancelGame = null, taskWalk = null, talking = false, broadcastNear = false;
  let service = null, departing = null, practiceIndex = 0;
  const stallArt = new Image();
  stallArt.src = LIWEI_REPAIR_STALL;
  const inTown = () => sim.place === "autumn_test";
  const enabled = () => story.progress.done.includes("S14");
  const day = () => X.today();
  const playsToday = () => state.playDay===day() ? state.plays : 0;
  function countPlay() {
    if (playsToday()>=dailyLimit) {showHint(closedMessage);return false;}
    state.plays=playsToday()+1;
    state.playDay=day();
    persist();
    return true;
  }
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
  const spark=liweiRepairIcon("spark");
  spark.classList.add("rw-spark");
  head.append(icon,element("i","rw-indicator"),headText,spark,closeButton);
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
    const board=el.classList.contains("rw-board-game");
    if (board!==overlay.classList.contains("rw-board-active")) {
      overlay.classList.toggle("rw-board-active",board);
      position();
    }
    if (!el.classList.contains("rw-game")) {body.replaceChildren(el);return;}
    if (workbench.firstElementChild===benchArt) workbench.prepend(el);
    else workbench.firstElementChild.replaceWith(el);
    if (workbench.parentElement!==body) body.replaceChildren(workbench);
  }
  let priorFocus=null;
  let counterLift=0;
  function position() {
    const rect=view.getBoundingClientRect();
    const host=view.parentElement.getBoundingClientRect();
    const counter=overlay.classList.contains("rw-counter");
    const padding=Math.min(14,rect.width*.035);
    const width=counter ? Math.min(520,rect.width-padding*2) : Math.min(780,rect.width-padding*2);
    const tall=overlay.classList.contains("rw-board-active") && rect.width<400 && !counter;
    const maxHeight=tall ? rect.height+Math.max(0,Math.min(140,rect.top-12)) : rect.height-padding*2;
    const height=counter ? Math.min(208,rect.height*.58) : Math.min(550,maxHeight);
    const top=tall ? rect.height-height : counter ? rect.height-padding : (rect.height-height)/2;
    Object.assign(overlay.style,{
      left:rect.left-host.left+(rect.width-width)/2+"px",
      top:rect.top-host.top+top+"px",
      width:width+"px",height:counter?"auto":height+"px",maxHeight:height+"px",
    });
    // On a narrow screen, keep the customer and table above the order card.
    const lift=counter && rect.width<400 ? 65 : 0;
    if (lift!==counterLift) city.snapCamera(counterLift=lift);
  }
  function openRoom(title, counter = false) {
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
    overlay.classList.toggle("rw-counter",counter);
    closeButton.setAttribute("aria-label",counter?"收摊":"关上维修台");
    closeButton.title=counter?"收摊":"关闭";
    overlay.hidden=false;
    position();
    closeButton.focus({preventScroll:true});
    sound("open");
  }
  function closeRoom() {
    service=null;
    departing=null;
    hideRoom();
  }
  function hideRoom() {
    if (overlay.hidden) return;
    overlay.hidden=true;
    if (counterLift) city.snapCamera(counterLift=0);
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
    onClose:()=>{talking=false;speech.hide();if(service&&inTown())board();},
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
  function nextOrder(practice) {
    const current=day();
    const counter=state.counter;
    if (!practice) {
      const eligible=order=>order&&!order.delivered&&(!order.coin||state.paidDay!==current);
      const held=state.orders[counter.pending];
      if (eligible(held)) return held;
      // Repair orders accepted before the move are still collected at the new stall.
      const outstanding=Object.values(state.orders).find(eligible);
      if (outstanding) {
        counter.pending=outstanding.id;
        return outstanding;
      }
    }
    const seq=practice ? ++practiceIndex : ++counter.sequence;
    const rng=liweiRepairRandom(randomSeed((practice?"practice":"walk-in")+"-"+seq,current));
    const candidates=LIWEI_REPAIR_ORDERS.filter(row=>story.progress.ending!=="B"||row[1]!=="工人代表");
    const lastType=practice ? service.lastType : counter.lastType;
    const pool=candidates.filter(row=>row[0]!==lastType);
    const [type,client,title,detail]=pool[rng(pool.length)];
    const coin=practice||state.paidDay===current ? 0 : title==="广场的旧广播" ? 3 : current%4===0 ? 2 : 1;
    const order={id:(practice?"practice-":"walk-in-")+current+"-"+seq,day:current,type,client,title,detail,seed:rng(0x7fffffff),coin};
    if (!practice) {
      state.orders[order.id]=order;
      counter.pending=order.id;
      counter.lastType=type;
      persist();
    }
    return order;
  }
  function queueCustomer(receipt = "") {
    const s=service;
    s.receipt=receipt;
    if (playsToday()>=dailyLimit) {
      s.order=null;
      s.closedDay=day();
      board();
      return;
    }
    const order=nextOrder(s.practice);
    s.closedDay=null;
    const now=performance.now();
    s.order=order;
    s.lastType=order.type;
    s.walkAt=now+(departing?1550:220);
    s.arriveAt=s.walkAt+(reduceMotionUI?250:1650);
    board();
  }
  function openStall(practice = false) {
    const stop=safeToPlay();
    if (stop) {showHint(stop);return;}
    service={practice,order:null};
    queueCustomer();
  }
  function customerPosition(visit, now) {
    const plot=landmark(stallId);
    const y=plot.y+8, servingX=plot.x+20;
    const farX=servingX+62;
    const left=visit.leaveAt!=null;
    const start=left?visit.leaveAt:visit.walkAt;
    const duration=left?(reduceMotionUI?260:1350):visit.arriveAt-visit.walkAt;
    const fraction=Math.max(0,Math.min(1,(now-start)/duration));
    const x=left?servingX+62*fraction:farX-62*fraction;
    return {x:Math.round(x),y,direction:left?1:-1,moving:fraction<1,distance:fraction*62,alpha:Math.min(1,left?(1-fraction)*7:fraction*7)};
  }
  function releaseCustomer() {
    departing={...service,leaveAt:performance.now()};
    state.counter.pending=null;
  }
  function play(order, practice = false) {
    if (order.delivered) return;
    if (order.completed) return deliver(order);
    if (!countPlay()) {if(service)queueCustomer();return;}
    if (!practice && order.id!=="tutorial") {
      state.orders[order.id]=order;
      persist();
    }
    openRoom(order.title);
    run=order.id;
    cancelGame=runLiweiRepair({...order,shopTool:state.owned.includes("coil")?"coil":null},{
      element,button,setBody,sound,alive:()=>run===order.id&&!overlay.hidden,
      retry:()=>{
        if (countPlay()) return true;
        if (service) queueCustomer();
        return false;
      }
    },()=>{
      run=null;
      if (practice) {
        setBody(result("修好了",order.client+"在摊前等着取件。",()=>{
          departing={...service,leaveAt:performance.now()};
          queueCustomer("刚刚交给"+order.client);
        },"交给客人"));
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
    defense:["哎，真安静了。它半夜多响一下，我还以为有人敲门！","您先听一晚。它要是又乱报点，明早再给我送来。"],
    mines:["亮了亮了！手别挪，让我看看是不是这几格在捣鬼。","我把烧坏的线换下来啦。先少开几分钟，摸摸外壳烫不烫。"],
    gomoku:["好嘛，桌子稳了，我这盘倒下歪了。","我看见您手里还攥着一颗呢。就搁这儿吧，下回接着下。"],
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
    hideRoom();
    const [clientLine, reply]=customerLines[order.type==="clock"?"defense":order.type];
    const archive=specialTapes[order.title];
    const after=LIWEI_REPAIR_COMMENTS[order.title];
    const rows=archive?[[order.client,"先放一下后半截，听听还能不能接上。"],["录音",archive[0]],[order.client,archive[1]]]:
      [[order.client,clientLine],["我",reply],...(after?[[order.client,after[0]],["我",after[1]]]:[])];
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
      releaseCustomer();
      queueCustomer(reward?"刚交货 · 收到 "+reward+" 枚丢丢币":"刚交货 · "+order.client+"把东西带走了");
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
    if (!service) return openStall();
    openRoom(service.practice?"试摆维修摊":"栗尾维修摊",true);
    paintCounter();
  }
  function paintCounter() {
    if (!service) return;
    const {order,receipt,practice,arriveAt}=service;
    const arrived=!!order && performance.now()>=arriveAt;
    overlay.dataset.customer=!order?"closed":arrived?"ready":"waiting";
    const card=element("article","rw-customer");
    const name=element("div","rw-customer-name",!order?closedMessage:arrived?order.client:"等下一位客人");
    name.prepend(liweiRepairIcon(!order?"seal":arrived?"bolt":"spark"));
    const stamp=element("span","rw-customer-stamp",arrived?(order.coin?order.coin+" 丢丢币":"人情单"):order?"营业中":"收工");
    stamp.prepend(liweiRepairIcon("seal"));
    name.append(stamp);
    card.append(name);
    const fault=element("p","rw-note",arrived?order.detail:"桌子支好了。街坊正往这边来。");
    if (!order) card.append(element("p","rw-note","今天的 20 局都玩完了，明天再来开摊吧。"));
    else if (arrived) {
      fault.classList.add("rw-fault");
      card.append(element("h3","",order.title),fault);
      fault.append(element("small","rw-order-mode",LIWEI_REPAIR_TYPES[order.type==="clock"?"defense":order.type]));
      card.append(button(order.completed?"交给客人":"接过来修",()=>play(order,practice)));
    } else {
      const steps=element("div","rw-customer-walk");
      steps.setAttribute("aria-hidden","true");
      steps.append(element("i"),element("i"),element("i"));
      card.append(fault,steps);
    }
    const footer=element("nav","rw-counter-tools");
    footer.append(element("small","rw-counter-balance",receipt||(practice?"练习摊位":"余额 "+X.F.coins+" 丢丢币")));
    footer.append(element("small","rw-counter-tally","今日 "+playsToday()+" / "+dailyLimit+" 局"));
    if (!practice) footer.append(tab("街坊合伙",partners),tab("工具和摆件",supplies));
    const wrap=element("div","rw-counter-content");
    wrap.append(card,footer);
    setBody(wrap);
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
    setBody(makeList("余额 "+X.F.coins+" 丢丢币",[tab("回摊位",board)],items));
  }
  function partners() {
    openRoom("街坊合伙");
    const cur=day();
    if (state.investment) {
      const stake=state.investment;
      const offer=LIWEI_PARTNERS.find(item=>item.id===stake.id);
      const due=cur>=stake.due;
      setBody(makeList(offer.host+"正在做「"+offer.name+"」",[tab("回摊位",board)],[
        element("p","rw-note",due?"已经捎话来，可以看结果了。":"还要等 "+(stake.due-cur)+" 天。"),
        button("听听做得怎样",()=>settle(stake,offer),{disabled:!due}),
      ]));
      return;
    }
    const start=Math.floor(cur/3)%LIWEI_PARTNERS.length;
    const options=[LIWEI_PARTNERS[start],LIWEI_PARTNERS[(start+2)%LIWEI_PARTNERS.length]];
    setBody(makeList("余额 "+X.F.coins+" 丢丢币 · 同时挑一个项目",[tab("回摊位",board)],options.map(offer=>{
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
    hideRoom();
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
    if (id===stallId && state.shopOpen) {
      taskWalk=null;
      openStall();
      return true;
    }
    const tasks=activeAt(id);
    if (!tasks.length) return false;
    if(taskWalk?.id===id&&tasks.includes(taskWalk.quest)){
      const quest=taskWalk.quest;
      taskWalk=null;
      doStep(quest);
    } else if(tasks.length===1 && (id===stallId || travelers[id])) {
      doStep(tasks[0]);
    } else {
      city.panel(titleAt(id),"",[
        ...tasks.map(q=>[q.title,()=>doStep(q)]),
        ["继续原本的活动",()=>{ignoreSite=true;try{city.interact(id);}finally{ignoreSite=false;}}],
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
    if (departing && customerPosition(departing,performance.now()).alpha<=0) departing=null;
    if (service?.closedDay!=null && service.closedDay!==day() && !overlay.hidden &&
        overlay.classList.contains("rw-counter")) queueCustomer();
    if (service && !overlay.hidden && overlay.classList.contains("rw-counter") &&
        overlay.dataset.customer==="waiting" && performance.now()>=service.arriveAt) {
      sound("select");
      paintCounter();
    }
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
    const store=landmark(stallId), notice=landmark("notice");
    if((state.shopOpen||service)&&store){
      const x=store.x-16,y=store.y-38;
      ctx.fillStyle="#342331";ctx.fillRect(x,y,32,10);
      ctx.fillStyle=state.owned.includes("display")?"#f7b85e":"#a76542";ctx.fillRect(x+1,y+1,30,8);
      ctx.font="7px sans-serif";ctx.textAlign="center";ctx.fillStyle="#fff1c5";ctx.fillText(service?.order?"营业中":"维修摊",x+16,y+7);
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
  const shopAccess={id:"shopAccess",steps:[[stallId,"去工人街西侧摆摊"]]};
  seasonMapTest.root.querySelector("header").append(control);
  setInterval(()=>{control.hidden=!(inTown()&&state.shopOpen);},350);
  const testUrl=new URL(location.href);
  const repairTest=testUrl.searchParams.get("repair-test")==="1";
  if (repairTest) {
    const controls=element("span","");
    controls.id="liweiRepairTest";
    const stepLabel=element("span","");
    const skip=button("完成当前阶段",()=>startTest(()=>{
      const index=status(special)?.step||0;
      const part=current(special);
      if (!part) return;
      completeStep(special,part[2],index);
      updateTest();
      if (state.shopOpen) {placeAt(stallId);showHint("走完了。点小屋门口就能摆摊。");}
      else {
        placeAt(current(special)[0]);
        showHint("已完成第 "+(index+1)+" 段 · "+current(special)[1]);
      }
    }));
    const direct=button("直接测试维修台",()=>startTest(()=>{placeAt(stallId);openStall(true);}));
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
      prefs.guided=true;
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
      placeAt(current(special)?.[0]||stallId);
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
    // The front table and guests share the street's depth sort, including
    // the same building masks and road coordinates as other residents.
    visitors(){
      if (!service) return [];
      const now=performance.now();
      return [departing,service].filter(v=>v?.order).map(v=>({
        ...customerPosition(v,now),name:v.order.client,seed:v.order.seed,
      })).filter(v=>v.alpha>0);
    },
    stallScenery(){
      if (!service?.order || !stallArt.complete || !stallArt.naturalWidth) return null;
      const plot=landmark(stallId), y=plot.y+4;
      return {img:stallArt,x:plot.x-26,y:y-stallArt.height+3,depth:y};
    },
    site:id=>!ignoreSite&&site(id),
    choices:id=>ignoreSite?[]:activeAt(id).map(q=>[q.title,()=>doStep(q)]),
    drawOutdoor,drawAway,
    music:()=>!overlay.hidden?"BGM/liwei/repair-after-hours.mp3":null,
  };
})();
