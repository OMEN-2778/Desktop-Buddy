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

  const defense=()=>liweiRepairDefense({order,button,cell,row,note,setBody,sound,later,win,fail,position});

  function mines() {
    const draw=liweiRepairRandom(order.seed), width=6, count=[4,6,9][(order.difficulty ?? 2)-1];
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
        row("rw-mines-layout",[grid("mines",slots.map(i=>{
          const revealed=opened.has(i);
          const number=neighbors[i].filter(j=>faults.has(j)).length;
          const b=cell(position(i,width)+(revealed?" 已探明 "+number:flags.has(i)?" 已标记":" 未探明"),
            ()=>probe(i),flags.has(i)?"flag":null,revealed&&number?String(number):"",revealed);
          if (revealed) b.classList.add("rw-revealed");
          return b;
        })),flag]),
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
        const difficulty=order.difficulty ?? 2;
        const attack=score(i,2), block=score(i,1);
        const value=attack*(difficulty===1?1.6:1.2)+block*(difficulty===3?1.18:.8)+draw(difficulty===1?27:6);
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
