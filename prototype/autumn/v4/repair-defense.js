function liweiRepairDefense({order, button, cell, row, note, setBody, sound, later, win, fail, position}) {
  const width = 6, lanes = 3, dt = .05, fuseLimit = 4;
  const tools = [
    {icon:"coil",name:"线圈",cost:3,damage:2,cooldown:.72,info:"连发"},
    {icon:"guard",name:"挡片",cost:2,integrity:9,info:"拦住杂讯"},
    {icon:"chill",name:"冷凝器",cost:4,damage:1,cooldown:.85,info:"减速"},
    {icon:"piercer",name:"穿甲管",cost:5,damage:4,cooldown:1.55,info:"穿透两个目标"},
    {icon:"battery",name:"蓄电盒",cost:3,info:"每 3 秒供电"},
  ];
  const opponents = {
    fault:{hp:5,speed:.7,armor:0},
    runner:{hp:4,speed:1.17,armor:0},
    armored:{hp:13,speed:.52,armor:1},
  };
  const draw=liweiRepairRandom(order.seed);
  const intro=order.id==="tutorial";
  const pattern=intro || order.seed%3===0 ? ["fault","runner","armored"] :
    order.seed%3===1 ? ["runner","fault","armored"] : ["fault","armored","runner"];
  const waveCount=intro?2:3;
  const arrivals=[];
  for (let wave=0;wave<waveCount;wave++) {
    const shift=draw(lanes);
    const count=intro?5+wave:5+wave*2;
    for (let j=0;j<count;j++) {
      const kind=wave===0 || intro ? j<3?"fault":"runner" :
        j%3===0?"fault":pattern[wave];
      const lane=j<3?(shift+j)%lanes:draw(lanes);
      arrivals.push({tick:12+wave*214+j*(wave===2?17:23), wave:wave+1, lane, kind});
    }
  }
  const field=Array(width*lanes).fill(null);
  const enemies=[], shots=[], impacts=[];
  let charge=order.shopTool==="coil"?11:9;
  let tool=0, frame=0, wave=1, leaks=0, sent=0, running=false;

  const amount=note(""), waves=note(""), fuses=note("");
  const label=note("");
  const tiles=field.map((_,i)=>cell(position(i,width),()=>place(i)));
  tiles.forEach((tile,i)=>tile.classList.toggle("rw-entry",i%width===width-1));
  const effects=row("rw-defense-effects",[]);
  effects.setAttribute("aria-hidden","true");
  const toolbar=tools.map(({icon,name,cost},i)=>cell(name+" "+cost+" 格电",()=>{
    tool=i;
    drawHud();
  },icon,name+" "+cost));
  const start=button("接通电源",()=>{
    if (running) return;
    running=true;
    start.hidden=true;
    drawHud();
    later(advance,50);
  });
  start.classList.add("rw-defense-start");
  const board=row("rw-defense-field",[row("rw-board rw-board-defense",tiles),effects]);
  const part=element=>row("rw-defense-stat",[element]);
  setBody(row("rw-game rw-board-game rw-defense",[
    row("rw-defense-hud",[
      row("rw-defense-stat",[liweiRepairIcon("bolt"),amount]),part(waves),
      row("rw-defense-stat",[liweiRepairIcon("guard"),fuses]),
    ]),
    board,row("rw-defense-tools",toolbar),row("rw-defense-controls",[label,start]),
  ]));

  function showAt(node,x,lane) {
    node.style.left=(100*x/width)+"%";
    node.style.top=(100*(lane+.5)/lanes)+"%";
  }
  function drawHud() {
    amount.textContent="电量 "+charge;
    waves.textContent="波次 "+wave+"/"+waveCount;
    fuses.textContent="保险丝 "+(fuseLimit-leaks)+"/"+fuseLimit;
    const chosen=tools[tool];
    label.textContent=running ? chosen.info : chosen.info+" · 点格安装";
    toolbar.forEach((b,i)=>{
      b.classList.toggle("rw-picked",i===tool);
      b.setAttribute("aria-pressed",String(i===tool));
    });
    tiles.forEach((b,i)=>{
      const tower=field[i];
      const entry=i%width===width-1;
      const occupied=enemies.some(e=>e.lane===Math.floor(i/width) && Math.floor(e.x)===i%width);
      b.disabled=entry||!!tower||occupied||charge<chosen.cost;
      b.setAttribute("aria-label",position(i,width)+(tower?" "+tower.name:entry?" 入口":" 空位"));
    });
  }
  function place(i) {
    const chosen=tools[tool];
    field[i]={...chosen,hp:chosen.integrity||3,next:frame+1};
    if (chosen.icon==="battery") field[i].next=frame+60;
    charge-=chosen.cost;
    tiles[i].append(liweiRepairIcon(chosen.icon));
    tiles[i].classList.add("rw-installed");
    sound("select");
    drawHud();
  }
  function spawn({kind,lane}) {
    const icon=liweiRepairIcon(kind);
    const life=row("rw-defense-life",[]);
    const node=row("rw-defense-unit",[icon,life]);
    node.classList.add("rw-defense-"+kind);
    effects.append(node);
    enemies.push({...opponents[kind],max:opponents[kind].hp,x:5.94,lane,node,life,slowUntil:0});
  }
  function burst(x,lane,kind) {
    const node=row("rw-defense-burst rw-defense-"+kind,[]);
    showAt(node,x,lane);
    effects.append(node);
    impacts.push({node,expires:frame+6});
  }
  function shoot(tower,x,lane) {
    const node=row("rw-defense-shot rw-defense-"+tower.icon,[]);
    effects.append(node);
    showAt(node,x,lane);
    shots.push({node,x,lane,damage:tower.damage,kind:tower.icon,hit:new Set()});
    burst(x,lane,"muzzle");
    tower.next=frame+Math.round(tower.cooldown/dt);
    sound("tick",.17);
  }
  function runTowers() {
    field.forEach((tower,i)=>{
      if (!tower || frame<tower.next) return;
      if (tower.icon==="battery") {
        charge++;
        tower.next=frame+60;
        burst(i%width+.5,Math.floor(i/width),"power");
      } else if (tower.damage) {
        const x=i%width+.5, lane=Math.floor(i/width);
        if (enemies.some(e=>e.lane===lane && e.x>x)) shoot(tower,x,lane);
      }
    });
  }
  function flyShots() {
    for (let i=shots.length-1;i>=0;i--) {
      const shot=shots[i], left=shot.x;
      shot.x+=dt*(shot.kind==="chill"?6.7:9.5);
      const targets=enemies.filter(e=>e.hp>0&&e.lane===shot.lane&&!shot.hit.has(e)&&e.x>=left-.27&&e.x<=shot.x+.27)
        .sort((a,b)=>a.x-b.x);
      for (const target of targets) {
        const piercing=shot.kind==="piercer";
        target.hp-=piercing?shot.damage:Math.max(1,shot.damage-target.armor);
        if (shot.kind==="chill") target.slowUntil=frame+34;
        shot.hit.add(target);
        burst(target.x,target.lane,shot.kind);
        if (!piercing || shot.hit.size===2) {shot.x=width;break;}
      }
      if (shot.x>=width) {shot.node.remove();shots.splice(i,1);}
      else showAt(shot.node,shot.x,shot.lane);
    }
  }
  function walkEnemies() {
    for(let i=enemies.length-1;i>=0;i--) {
      const enemy=enemies[i];
      if (enemy.hp<=0 || enemy.x<.02) {
        enemy.node.remove();
        enemies.splice(i,1);
        if (enemy.hp<=0) charge++;
        else leaks++;
        continue;
      }
      const tile=Math.floor(enemy.x-.30);
      const index=enemy.lane*width+tile;
      const tower=tile>=0?field[index]:null;
      if (tower && enemy.x<=tile+.88) {
        tower.hp-=dt*(enemy.armor?2.2:1.3);
        if (tower.hp<=0) {
          burst(tile+.5,enemy.lane,"muzzle");
          field[index]=null;
          tiles[index].replaceChildren();
          tiles[index].classList.remove("rw-installed");
        }
      } else {
        enemy.x-=dt*enemy.speed*(enemy.slowUntil>frame?.54:1);
      }
      showAt(enemy.node,enemy.x,enemy.lane);
      enemy.life.style.setProperty("--hp",Math.max(0,enemy.hp/enemy.max)*100+"%");
      enemy.node.classList.toggle("rw-chilled",enemy.slowUntil>frame);
    }
  }
  function advance() {
    if (document.hidden) {later(advance,250);return;}
    frame++;
    if (frame%44===0) charge++;
    while (arrivals[sent]?.tick===frame) {
      const entry=arrivals[sent++];
      wave=entry.wave;
      spawn(entry);
    }
    runTowers();
    flyShots();
    walkEnemies();
    while (impacts[0]?.expires<=frame) impacts.shift().node.remove();
    if (leaks>=fuseLimit) {fail("保险丝烧断了。");return;}
    if (sent===arrivals.length && !enemies.length) {win();return;}
    drawHud();
    later(advance,50);
  }
  drawHud();
}
