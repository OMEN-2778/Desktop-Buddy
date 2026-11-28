function liweiRepairIcon(key) {
  const image = new Image();
  image.src = LIWEI_REPAIR_ICONS[key];
  image.className = "rw-pixel-icon";
  image.alt = "";
  image.draggable = false;
  return image;
}

function liweiRepairBoardGames({order, button, row, note, setBody, sound, later, win, fail}) {
  const grid = (name, items) => row("rw-board rw-board-" + name, items);
  const position = (i, width) => (Math.floor(i / width) + 1) + " 行 " + (i % width + 1) + " 列";
  function cell(label, action, icon, text = "", disabled = false) {
    const b = button(text, action, {label, disabled});
    if (icon) b.append(liweiRepairIcon(icon));
    return b;
  }
  const status = (icon, text) => row("rw-board-status", [liweiRepairIcon(icon), note(text)]);

  function defense() {
    const draw = liweiRepairRandom(order.seed);
    const width = 6, height = 3;
    const fittings = Array(width * height).fill(null);
    const shift = draw(height);
    const waves = Array.from({length:height},(_,i)=>(i+shift)%height);
    const schedule = waves.flatMap((lane,i) => [[1+i*2,lane,3],[7+i*2,lane,4],[13+i*2,lane,5]]);
    for (let i=0; i<3; i++) schedule.push([19+i*2,draw(height),6]);
    const heavy = order.seed%3!==0;
    if (heavy) for (let i=0;i<4;i++) schedule.push([25+i*2,draw(height),14+draw(5)]);
    const lastArrival=schedule.at(-1)[0];
    let charge = 9, frame = 0, leaks = 0, cleared = 0, running = false, tool = 0;
    const enemies = [];
    const tools = [["coil","线圈",3],["guard","挡片",2]];
    function advance() {
      if (document.hidden) return later(advance, 650);
      frame++;
      if (frame%3===0) charge++;
      for (const [time,lane,hp] of schedule)
        if (time===frame) enemies.push({lane,hp,x:width-1});
      for (let i=enemies.length-1; i>=0; i--) {
        const e=enemies[i], front=e.lane*width, slot=front+e.x;
        const coils=fittings.slice(front,slot+1).filter(f=>f?.kind===0).length;
        if ((e.hp-=coils*2)<=0) {
          enemies.splice(i,1);
          cleared++; charge++;
          continue;
        }
        const guard=fittings[slot-1];
        if (e.x>0 && guard?.kind===1) {
          if (--guard.hp===0) fittings[slot-1]=null;
          continue;
        }
        if (--e.x<0) {enemies.splice(i,1);leaks++;}
      }
      if (leaks>=4) return fail("左边的保险丝断了。开打前，可以先给每路各摆一个线圈。");
      if (frame>=lastArrival && !enemies.length) return win();
      sound("tick",.20);
      render();
      later(advance, 850);
    }
    function render() {
      const tiles=fittings.map((fitting,i)=>{
        const lane=Math.floor(i/width), x=i%width;
        const enemy=enemies.find(e=>e.lane===lane && e.x===x);
        const label=position(i,width)+(enemy?" 杂讯 "+enemy.hp:fitting?" "+tools[fitting.kind][1]:" 空位");
        const b=cell(label,()=>{
          charge-=tools[tool][2];
          fittings[i]={kind:tool,hp:3};
          sound("select");
          render();
        },enemy?"fault":fitting?tools[fitting.kind][0]:null,enemy?String(enemy.hp):"",
        !!fitting||!!enemy||x===width-1||charge<tools[tool][2]);
        b.classList.toggle("rw-entry",x===width-1);
        b.classList.toggle("rw-enemy",!!enemy);
        b.classList.toggle("rw-installed",!!fitting);
        return b;
      });
      const toolsBar=tools.map(([icon,name,cost],i)=>{
        const b=cell(name+" "+cost+" 格电",()=>{tool=i;render();},icon,name+" "+cost);
        b.classList.toggle("rw-picked",tool===i);
        b.setAttribute("aria-pressed",String(tool===i));
        return b;
      });
      if (!running) toolsBar.push(button("接通电源",()=>{running=true;render();later(advance,700);}));
      setBody(row("rw-game rw-board-game",[
        status("bolt","电量 "+charge+"　拦下 "+cleared+" / "+schedule.length+"　保险丝 "+(4-leaks)+"/4"),
        note(running?"线圈会自动打本路的杂讯。还有电，就能继续摆。":"点线圈，再点棋盘左边的空格。三路各摆一个，点「接通电源」。"),
        grid("defense",tiles),row("rw-actions rw-board-tools",toolsBar),
        note(heavy?"后半轮有大团杂讯。攒到电后，可以在同一路再加线圈。":"杂讯从右边来。线圈自动清理，挡片可以拦几拍。"),
      ]));
    }
    render();
  }

  function mines() {
    const draw=liweiRepairRandom(order.seed), width=6, count=6;
    const slots=Array.from({length:width*width},(_,i)=>i);
    const neighbors=slots.map(i=>slots.filter(j=>i!==j &&
      Math.abs(i%width-j%width)<=1 && Math.abs(Math.floor(i/width)-Math.floor(j/width))<=1));
    const faults=new Set(), opened=new Set(), flags=new Set();
    let flagging=false;
    function probe(at) {
      if (opened.has(at)) return;
      if (flagging) {
        if (flags.has(at)) flags.delete(at);
        else if (flags.size<count) flags.add(at);
      } else {
        if (flags.has(at)) return;
        if (!faults.size) {
          const pool=slots.filter(i=>i!==at && !neighbors[at].includes(i));
          for (let i=0;i<count;i++) faults.add(pool.splice(draw(pool.length),1)[0]);
        }
        if (faults.has(at)) return fail("碰到短路点了。数字表示周围八格里有几个短路点。","mine");
        const frontier=[at];
        while (frontier.length) {
          const i=frontier.pop();
          if (opened.has(i)||flags.has(i)) continue;
          opened.add(i);
          if (!neighbors[i].some(j=>faults.has(j))) frontier.push(...neighbors[i]);
        }
        if (opened.size===slots.length-count) return win();
      }
      sound("select");
      render();
    }
    function render() {
      const flag=cell("切换插旗模式",()=>{flagging=!flagging;render();},"flag",flagging?"插旗中":"改用插旗");
      flag.classList.toggle("rw-picked",flagging);
      flag.setAttribute("aria-pressed",String(flagging));
      setBody(row("rw-game rw-board-game",[
        status("flag","标记 "+flags.size+" / "+count+"　安全格 "+opened.size+" / "+(slots.length-count)),
        note("点格子找出所有安全线路。数字是周围八格的短路数，第一下可以放心点。"),
        grid("mines",slots.map(i=>{
          const revealed=opened.has(i);
          const number=neighbors[i].filter(j=>faults.has(j)).length;
          const b=cell(position(i,width)+(revealed?" 已探明 "+number:flags.has(i)?" 已标记":" 未探明"),
            ()=>probe(i),flags.has(i)?"flag":null,revealed&&number?String(number):"",revealed);
          if (revealed) b.classList.add("rw-revealed");
          return b;
        })),
        row("rw-actions rw-board-tools",[flag,note(flagging?"再点一次已插旗的格子可拔掉。":"怀疑短路的格子，可以切换成插旗。")]),
      ]));
    }
    render();
  }

  function gomoku() {
    const draw=liweiRepairRandom(order.seed), width=9;
    const slots=Array(width*width).fill(0);
    const axes=[[1,0],[0,1],[1,1],[1,-1]];
    let thinking=false, stones=0;
    function scan(i,side,dx,dy) {
      let x=i%width+dx, y=Math.floor(i/width)+dy, steps=0;
      while (x>=0 && x<width && y>=0 && y<width && slots[y*width+x]===side) {
        steps++; x+=dx; y+=dy;
      }
      return [steps,x>=0&&x<width&&y>=0&&y<width&&!slots[y*width+x]];
    }
    function lines(i,side) {
      return axes.map(([dx,dy])=>{
        const [a,left]=scan(i,side,dx,dy), [b,right]=scan(i,side,-dx,-dy);
        return [1+a+b,Number(left)+Number(right)];
      });
    }
    function score(i,side) {
      return lines(i,side).reduce((sum,[length,open])=>sum+(length>=5?100000:open*9**(length-1)),0);
    }
    function place(i,side) {
      slots[i]=side;
      stones++;
      sound("select");
      if (lines(i,side).some(([length])=>length>=5)) {
        if (side===1) win();
        else fail("对手先连成了五颗。看到对方有四连，要先挡住空出来的那头。");
        return true;
      }
      if (stones===slots.length) {fail("这盘下满了，两边都没连成五颗。");return true;}
      return false;
    }
    function reply() {
      let at=-1, best=-1;
      slots.forEach((stone,i)=>{
        if (stone) return;
        const value=score(i,2)*1.2+score(i,1)+draw(6);
        if (value>best) {at=i;best=value;}
      });
      thinking=false;
      if (!place(at,2)) render();
    }
    function turn(i) {
      if (thinking || slots[i] || place(i,1)) return;
      thinking=true; render(); later(reply,340);
    }
    function render() {
      setBody(row("rw-game rw-board-game",[
        status(thinking?"dark":"light",thinking?"对手在想……":"轮到你落白子"),
        note("横、竖、斜连成五颗就赢。留心对手的四连。"),
        grid("gomoku",slots.map((stone,i)=>cell(position(i,width)+(stone===1?" 白子":stone===2?" 深色棋子":" 空位"),
          ()=>turn(i),stone===1?"light":stone===2?"dark":null,"",thinking||!!stone))),
      ]));
    }
    render();
  }
  return {defense,mines,gomoku};
}
