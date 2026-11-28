const LIWEI_REPAIR_TYPES = {
  radio: "自动扫频", bike: "修车试跑", clock: "挂钟排故", pipes: "洗衣铺止漏", tape: "磁带抢救",
};

function liweiRepairRandom(seed) {
  let value = seed >>> 0;
  return limit => {
    value = (Math.imul(value, 1664525) + 1013904223) >>> 0;
    return Math.floor(value / 4294967296 * limit);
  };
}

function runLiweiRepair(order, ui, complete) {
  const {element, button, setBody, sound, alive} = ui;
  const random = liweiRepairRandom(order.seed);
  let timer = 0;
  const later = (fn, ms) => { timer = setTimeout(() => { if (alive()) fn(); }, ms); };
  const note = text => element("p", "rw-note", text);
  const title = text => element("h3", "", text);
  const row = (className, children) => {
    const node = element("div", className);
    node.append(...children);
    return node;
  };
  function win() {
    clearTimeout(timer);
    sound("success");
    complete();
  }
  let restart;
  function fail(words) {
    sound("fault");
    setBody(row("rw-result", [title("测试中断"), note(words), button("重新试一次", () => restart())]));
  }
  function radio() {
    const draw = liweiRepairRandom(order.seed);
    const lanes = Array.from({length:3}, () => []);
    const upgrades = [
      ["铜线探针","选中线路扫频 +1", l => l.power++],
      ["侧向风扇","扫掉杂波时，旁边线路也能扫到", l => l.chain++],
      ["蓄电盒","每隔三拍额外清理当前线路", l => l.reserve++],
      ["回收线圈","漏过的杂波会给本线路充电", l => l.recycle++],
      ["扩音模块","选中线路扫频 +2", l => l.power+=2],
      ["散热夹","还可承受 3 团漏过的杂波", () => allowance+=3],
    ];
    const profile = draw(3);
    const tutorial=order.id==="tutorial";
    const rigs = Array.from({length:3}, () => ({power:tutorial?2:1,chain:0,reserve:0,recycle:0,charge:0}));
    let wave = 1, tick = 0, leaking = 0, allowance = tutorial?16:12, score = 0, selected = draw(3);
    let phase = "ready", picks = [], pulse = [];
    rigs[selected].power++;
    if (order.shopTool === "coil") rigs[selected].recycle++;
    const waveLength = 10;
    function offer() {
      const pool = [...upgrades];
      picks = Array.from({length:3}, () => pool.splice(draw(pool.length),1)[0]);
    }
    function step() {
      if (document.hidden) { later(step, 360); return; }
      tick++;
      let idx = draw(3);
      for (let count = 0; count < wave + 1; count++) {
        if (profile === 0 || count % 2 === 0) idx = draw(3);
        if (profile === 2 && tick % 3 === 0) idx = 2;
        lanes[idx].push(0);
      }
      const hit = rigs.map(l => l.power + (tick % 3 === 0 ? l.reserve*3 : 0) + l.charge);
      for (let i = 0; i < 3; i++) {
        if (!lanes[i].length) continue;
        if (i > 0) hit[i-1] += rigs[i].chain;
        if (i < 2) hit[i+1] += rigs[i].chain;
      }
      pulse = hit;
      for (let i = 0; i < 3; i++) {
        const clear = Math.min(hit[i],lanes[i].length);
        score += clear;
        lanes[i].splice(0,clear);
        for (let j=0; j<lanes[i].length; j++) lanes[i][j]++;
        const escaped = lanes[i].filter(n => n >= 4).length;
        if (escaped) lanes[i].splice(0,escaped);
        leaking += escaped;
        rigs[i].charge = escaped*rigs[i].recycle;
      }
      sound("tick");
      if (leaking >= allowance) { fail("线路过载了。可以把升级留给容易堆杂波的线路。"); return; }
      if (tick === waveLength) {
        if (wave === 4) { win(); return; }
        phase = "upgrade";
        offer();
        sound("select");
      }
      render();
      if (phase === "test") later(step,550);
    }
    function start() {
      tick = 0;
      phase = "test";
      sound("switch");
      render();
      later(step,380);
    }
    function render() {
      const tracks = lanes.map((line,i) => {
        const rig = rigs[i];
        const rail = row("rw-rail", Array.from({length:4}, (_,pos) => {
          const cell = element("i","rw-slot");
          for (let j=0;j<Math.min(5,line.filter(n=>n===pos).length);j++) cell.append(element("b","rw-signal"));
          return cell;
        }));
        const device = button(["左路","中路","右路"][i] + " · " + rig.power, () => { selected=i; sound("select"); render(); }, {disabled:phase==="test"});
        device.classList.toggle("rw-picked",i===selected);
        const track = row("rw-track",[device,rail]);
        track.classList.toggle("rw-pulse",phase==="test"&&pulse[i]>0);
        return track;
      });
      let actions = [button("开始测试",start)];
      if (phase === "test") actions = [note("装置正在自动扫频"), element("progress","rw-meter")];
      if (phase === "upgrade") actions = picks.map(([name,info,apply]) => button(name,() => {
        apply(rigs[selected]); wave++; phase="ready"; sound("switch"); render();
      },{info}));
      const footer = row("rw-actions",actions);
      const progress = footer.querySelector("progress");
      if (progress) {progress.max=waveLength; progress.value=tick;}
      setBody(row("rw-game",[
        note("第 " + wave + " / 4 轮　已扫除 " + score + "　漏过 " + leaking + " / " + allowance),
        note(["宽频杂波 · 三路随机","脉冲杂波 · 同路连发","低频杂波 · 右路周期增强"][profile]),
        ...tracks, phase==="upgrade"?note("先点要加强的线路，再装一个工具。"):note("线路从左边进杂波。每轮结束可以选升级。"), footer
      ]));
    }
    render();
  }
  function bike() {
    const draw = liweiRepairRandom(order.seed);
    const parts = ["前轮","链条","后刹"];
    const problem = draw(parts.length);
    const wobble = 1+draw(2);
    let phase = "idle", position = 0, fixed = 0, picked = -1, attempts = 0, slots=[];
    function tick() {
      if (document.hidden) { later(tick,105); return; }
      position = (position+1)%12;
      if (position === 3 && picked === problem) sound("fault");
      if (position === 0 && ++attempts === 6) { phase="idle"; render(); return; }
      slots.forEach((slot,i)=>{
        if(i===position)slot.append(element("b","rw-signal"));
        else slot.replaceChildren();
      });
      later(tick,105);
    }
    function align() {
      if (picked !== problem) { sound("fault"); return; }
      const target = (fixed*3+wobble+2)%12;
      if (Math.abs(target-position)>1) { sound("fault"); return; }
      sound("switch");
      if (++fixed === 3) win();
      else render();
    }
    function render() {
      const target = (fixed*3+wobble+2)%12;
      slots = Array.from({length:12},(_,i) => {
        const slot = element("i","rw-slot");
        if (Math.abs(i-target)<=1) slot.classList.add("rw-align");
        if (phase==="spin" && position===i) slot.append(element("b","rw-signal"));
        return slot;
      });
      const visual = row("rw-bike",slots);
      setBody(row("rw-game",[
        note("校正进度 " + fixed + " / 3"),
        note(parts[problem] + "试转时有异响。选中零件，指针走到绿色区时点「校正」。"),
        row("rw-actions",parts.map((part,i) => {
          const b=button(part,()=>{ picked=i; sound("select"); render(); });
          b.classList.toggle("rw-picked",i===picked);
          return b;
        })),
        visual,
        phase==="idle"?button("开始试转",()=>{phase="spin";attempts=0;render();tick();}):button("校正",align)
      ]));
    }
    render();
  }
  function clock() {
    const draw=liweiRepairRandom(order.seed);
    const patterns=["长齿铜轮","短齿铜轮","长齿铁轮","短齿铁轮"];
    const pool=patterns.map((_,i)=>i);
    const target=Array.from({length:3},()=>pool.splice(draw(pool.length),1)[0]);
    let fitted=[0,1,2], history=[], hint="";
    function test() {
      const exact=fitted.filter((id,i)=>id===target[i]).length;
      if (exact===3) { win(); return; }
      const loose=new Set(fitted.filter(id=>target.includes(id))).size-exact;
      history.unshift(fitted.map(id=>patterns[id]).join(" / ")+"　响对 "+exact+" · 装错槽 "+loose);
      history=history.slice(0,4);
      sound(exact?"select":"fault");
      render();
    }
    function render() {
      setBody(row("rw-game",[
        note("点槽位换齿轮，三个轮子各有一个位置。每次试敲都会留下提示。"),
        row("rw-actions",fitted.map((part,i)=>button(["时针","半点","报时"][i]+" · "+patterns[part],()=>{
          fitted[i]=(part+1)%patterns.length;sound("tick");render();
        }))),
        row("rw-actions",[
          button("拨到整点试敲",test),
          button("听一遍低音齿",()=>{hint=target[0]<2?"时针齿轮敲起来清脆，是铜片。":"时针齿轮声音低，是铁片。";sound("tick");render();})
        ]),
        note(hint || "「响对」是轮子和槽位都对，「装错槽」是轮子对但位置不对。"),
        ...history.map(note)
      ]));
    }
    render();
  }
  function pipes() {
    const draw=liweiRepairRandom(order.seed);
    const path=[];
    const width=5, height=4, board=Array.from({length:width*height},()=>draw(4));
    const arrows=["→","↓","←","↑"];
    const turn=draw(3)+1, endRow=draw(2)+2;
    for(let x=0;x<turn;x++) path.push(x);
    for(let y=0;y<endRow;y++) path.push(y*width+turn);
    for(let x=turn;x<width;x++) path.push(endRow*width+x);
    const outlet=path.at(-1);
    let trace=[], successes=0, text="点格子顺时针转向。让水从左上角流到蓝桶。";
    function test() {
      trace=[];let at=0;
      for (let i=0;i<board.length;i++) {
        if (trace.includes(at)) break;
        trace.push(at);
        if (at===outlet) { win(); return; }
        const x=at%width, y=Math.floor(at/width), d=board[at];
        if (d===0 && x===width-1 || d===1 && y===height-1 || d===2 && x===0 || d===3 && y===0) break;
        at += [1,width,-1,-width][d];
      }
      successes++;
      text="水走到这里就断了。转动末端的管向后再试。";
      sound("fault");render();
    }
    let hint=-1;
    function render() {
      const boardNode=row("rw-grid",board.map((d,i)=>{
        const b=button(i===outlet?"桶":arrows[d],()=>{board[i]=(d+1)%4;trace=[];sound("tick");render();},{label:"第 "+(Math.floor(i/width)+1)+" 行第 "+(i%width+1)+" 格 "+(i===outlet?"出水桶":arrows[d]),disabled:i===outlet});
        if (trace.includes(i)) b.classList.add("rw-stream");
        if (i===hint || i===0 || i===outlet) b.classList.add("rw-picked");
        return b;
      }));
      setBody(row("rw-game",[note(text),boardNode,row("rw-actions",[
        button("开水试流",test),
        button("看看中段",()=>{hint=path[Math.floor(path.length/2)];sound("select");render();},{disabled:successes===0})
      ])]));
    }
    render();
  }
  function tape() {
    const draw=liweiRepairRandom(order.seed);
    const route = draw(2) ? [0,1,2,3,4,9,14,13,12,11,10,15,20,21,22,23,24]
      : [0,5,6,7,8,9,14,13,12,11,10,15,20,21,22,23,24];
    const obstacles=new Set(Array.from({length:24},(_,i)=>i).filter(i=>!route.includes(i)&&draw(3)===0));
    const reels=[route[1+draw(3)],9,20+draw(4)];
    reels.forEach(i=>obstacles.delete(i));
    let walked=[0], next=0, hint="依次经过号码导轮，最后绕到右下角。空格只绕一次。";
    function move(i) {
      const last=walked.at(-1);
      if (walked.length>1 && i===walked.at(-2)) {
        if (last===reels[next-1]) next--;
        walked.pop();sound("tick");render();return;
      }
      if (Math.abs(i%5-last%5)+Math.abs(Math.floor(i/5)-Math.floor(last/5))!==1 || walked.includes(i) || obstacles.has(i)) return;
      if (reels.includes(i) && i!==reels[next]) { hint="先绕到编号 " + (next+1) + " 的导轮。";sound("fault");render();return; }
      if (i===24 && next===reels.length) { win(); return; }
      walked.push(i);
      if (i===reels[next]) { next++; hint=["滋啦……","声音接上了。","放回收带盘就好了。"][next-1];sound("select"); }
      else sound("tick");
      render();
    }
    function render() {
      setBody(row("rw-game",[
        note(hint),row("rw-grid",Array.from({length:25},(_,i)=>{
          const reel=reels.indexOf(i);
          const b=button(obstacles.has(i)?"■":i===24?"盘":i===0?"起":reel>=0?String(reel+1):"·",()=>move(i),{disabled:obstacles.has(i),label:"磁带格 "+(i+1)});
          if (walked.includes(i)) b.classList.add("rw-stream");
          if (i===walked.at(-1)) b.classList.add("rw-picked");
          return b;
        })),button("从头绕",()=>{walked=[0];next=0;hint="依次经过三个导轮。";render();})
      ]));
    }
    render();
  }
  restart = {radio,bike,clock,pipes,tape}[order.type];
  restart();
  return () => clearTimeout(timer);
}
