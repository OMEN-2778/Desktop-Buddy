const LIWEI_REPAIR_TYPES = {
  bike: "修车试跑", defense: "分路塔防", mines: "线路扫雷", gomoku: "五子棋", pipes: "洗衣铺止漏", tape: "磁带抢救",
};

// Older orders keep their item type for delivery dialogue and rewards.
function liweiRepairMode(type) {
  return type==="clock" || type==="radio" ? "defense" : type;
}

function liweiRepairRandom(seed) {
  let value = seed >>> 0;
  return limit => {
    value = (Math.imul(value, 1664525) + 1013904223) >>> 0;
    return Math.floor(value / 4294967296 * limit);
  };
}

function runLiweiRepair(order, ui, complete) {
  const {element, button, setBody, sound, alive} = ui;
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
  function fail(words, icon = "fault") {
    sound("fault");
    setBody(row("rw-result", [liweiRepairIcon(icon), title("测试中断"), note(words), button("重新试一次", () => { if (!ui.retry || ui.retry()) restart(); })]));
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
  const boards=liweiRepairBoardGames({order,button,row,note,setBody,sound,later,win,fail});
  restart = {bike,pipes,tape,...boards}[liweiRepairMode(order.type)];
  restart();
  return () => clearTimeout(timer);
}
