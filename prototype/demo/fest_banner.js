// ================================================================ the festival bar (user)
// On a festival a long pill rides above the diary, as wide as the house, in
// the festival's colours: its name, one button per thing to do today (click
// and she goes there / does it by herself), and a line about the day. iOS-like
// spring in, idle drift, folds away when the day is over (ui.css .fest-bar).
const fbEl = document.getElementById("festBanner");
// [left colour, middle colour, line, [label, kind, what]...]; kind: place / act / fn
const FEST_BAR = {
  元宵节: ["#d9534a", "#f2a65a", "灯谜树挂满了红灯笼", ["公园猜灯谜", "place", "park"], ["煮元宵", "act", "cook"]],
  赖床节: ["#6c7fc4", "#a8b8ea", "今天睡觉有额外好心情", ["睡个懒觉", "act", "sleep"]],
  春分: ["#5fa565", "#a7d47a", "春天来了，花都开了", ["公园散步", "place", "park"]],
  写信日: ["#c0675a", "#e9b08a", "寄出去的信，会有回信", ["写信", "fn", () => openLetterTo()]],
  彩票日: ["#d1912c", "#f3cf5b", "中了奖，开心一整天", ["公园彩票站", "place", "park"], ["商场彩票车", "place", "mall"], ["网上买彩票", "fn", () => festLottoOnline()]],
  晒被子日: ["#4f9fb0", "#9bd3df", "被子晒得香喷喷", ["门口晒被子", "place", "front"]],
  甜品节: ["#d16a94", "#f5b3cb", "吃甜的有好心情", ["公园甜品摊", "place", "park"], ["做甜品", "act", "cook"]],
  端午节: ["#3f8f5a", "#9fcf6e", "端午安康", ["码头龙舟赛", "place", "beach"], ["公园粽子摊", "place", "park"], ["包粽子", "act", "cook"]],
  跳舞日: ["#7c4fd0", "#e06ab5", "迪厅只开这几天", ["迪厅开放", "place", "disco"], ["跳支舞", "act", "dance"]],
  七夕: ["#d0577f", "#f2a3bf", "公园挂满了浪漫灯串", ["公园装饰", "place", "park"]],
  读书日: ["#3c7a8a", "#7fc4b6", "读书有额外好心情", ["公园书摊", "place", "park"], ["商场旧书摊", "place", "mall"], ["读本书", "act", "read"]],
  中秋节: ["#c47a2c", "#f0c766", "月圆人团圆", ["公园月饼摊", "place", "park"], ["做月饼", "act", "cook"]],
  怪兽夜: ["#5b3c8f", "#e0782f", "街上有百鬼夜行", ["戴面具", "fn", () => wearMask()], ["公园游戏摊", "place", "park"], ["街头巡游", "place", "front"]],
  大扫除日: ["#4b8fb8", "#a6d3ea", "屋里屋外都扫一扫"],
  马拉松日: ["#d4553f", "#f39a6a", "跑者从门口经过", ["门口看马拉松", "place", "front"]],
  冬至: ["#4b6aa8", "#a6c5e7", "大雪下了一整天", ["吃汤圆", "act", "cook"]],
  雪人日: ["#5a86b8", "#b9d6f2", "到处都是雪人", ["门口堆雪人", "place", "front"], ["公园雪人", "place", "park"], ["码头雪人", "place", "beach"]],
  春节: ["#c8312f", "#f2b33d", "新年快乐，万事如意"],
};
const PLACE_NAME = { home: "家", front: "家门口", park: "公园", mall: "商场", beach: "码头", bar: "酒吧", disco: "迪厅" };
function fbGo(kind, what, btn) {
  btn.classList.remove("go"); void btn.offsetWidth; btn.classList.add("go");
  if (sim.mode === "down") { showHint(`先长按${ta()} 5 秒把${ta()}叫醒吧。`); return; }
  if (wiping || tripRun) { setTimeout(() => fbGo(kind, what, btn), 500); return; }   // mid-transition: as soon as it's done
  if (cardHolds()) return;
  closeRing(); closePicker();
  if (kind === "fn") { what(); return; }
  if (kind === "act") { command(what); return; }
  if (sim.place === what) { speak(pick(["就在这儿啦", "已经到啦", "就是这里！"])); return; }
  if (what === "disco" && !discoOpen()) { showHint("迪厅今天不开门"); return; }
  sim.dest = what; sim.outBack = null; sim.outWhy = null;      // sent by the player: she stays till she's had enough
  if (sim.place === "home") command("go_out");
  else { stopNpcTalk("该动身了"); throughDoor(what); }
}
// motifs drifting slowly behind the pills (user): simple shapes per festival, 24x24 SVG paths
const FB_SHAPES = {
  lantern: "M9 3h6v2h-6zM6 7c0-1 1-2 3-2h6c2 0 3 1 3 2v8c0 1-1 2-3 2H9c-2 0-3-1-3-2zM9 17h6v2H9zM11.2 19h1.6v3h-1.6z",
  zongzi: "M12 3 21 19H3zM8 13h8v2H8z",
  wave: "M2 14c3-4 5-4 8 0s5 4 8 0 3-3 4-2v4c-1-1-2-1-4 1-3 4-5 4-8 0s-5-4-8 0z",
  heart: "M12 21 4 13a5 5 0 0 1 8-6 5 5 0 0 1 8 6z",
  book: "M3 5c3-1 6-1 8 1v14c-2-2-5-2-8-1zM21 5c-3-1-6-1-8 1v14c2-2 5-2 8-1z",
  pumpkin: "M11 3h2v3h-2zM12 6c-2-1-6-1-8 2-2 4 0 10 4 11 1 1 3 1 4 0 1 1 3 1 4 0 4-1 6-7 4-11-2-3-6-3-8-2z",
  bat: "M12 9c1-2 2-2 2-2l1 2c2-1 5-1 7 2-2 0-3 1-3 3-1-1-3-1-4 1-1-1-2-1-3 0-1-1-2-1-3 0-1-2-3-2-4-1 0-2-1-3-3-3 2-3 5-3 7-2l1-2s1 0 2 2z",
  snow: "M11 2h2v20h-2zM2 11h20v2H2zM5 4l15 15-1.5 1.5L3.5 5.5zM19 4l1.5 1.5L5.5 20.5 4 19z",
  note: "M9 4h11v3H11v10a3 3 0 1 1-2-2.8zM18 7h2v8a3 3 0 1 1-2-2.8z",
  star: "M12 2l3 7 7 .6-5.3 4.6 1.7 7.3L12 17.6 5.6 21.5l1.7-7.3L2 9.6 9 9z",
  moon: "M15 3a9 9 0 1 0 6 15A8 8 0 0 1 15 3z",
  ticket: "M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4zM9 7v10h1V7z",
  mail: "M3 6h18v12H3zM3 6l9 7 9-7v2l-9 7-9-7z",
  candy: "M11 12h2v10h-2zM12 2a6 6 0 1 1 0 12 6 6 0 0 1 0-12z",
  shirt: "M8 4l4 2 4-2 5 4-3 3-1-1v10H7V10l-1 1-3-3z",
  medal: "M7 2h3l2 5 2-5h3l-3 7a6 6 0 1 1-4 0zM12 12a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
  flower: "M12 3a3 3 0 0 1 3 4 3 3 0 1 1 1 5 3 3 0 1 1-4 4 3 3 0 1 1-4-4 3 3 0 1 1 1-5 3 3 0 0 1 3-4zM12 9a2 2 0 1 0 0 4 2 2 0 0 0 0-4z",
  broom: "M15 2l2 1-4 9h2l3 9H6l3-9h2z",
  zz: "M4 5h7v2l-4 5h4v2H4v-2l4-5H4zM13 11h7v2l-4 5h4v2h-7v-2l4-5h-4z",
  bowl: "M3 11h18c0 5-4 9-9 9s-9-4-9-9zM8 6a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM13 5a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM17 7a2 2 0 1 1 0 4 2 2 0 0 1 0-4z",
  firecracker: "M8 8h8v13H8zM11 3h2v5h-2zM13 3l3-2 1 1-3 2z",
  snowman: "M12 3a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7zM12 10a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11z",
  ball: "M12 4a8 8 0 1 1 0 16 8 8 0 0 1 0-16zM11 0h2v4h-2z",
};
const FB_MOTIFS = {
  元宵节: ["lantern", "moon", "star"], 赖床节: ["zz", "moon", "star"], 春分: ["flower", "star"], 写信日: ["mail", "heart", "star"],
  彩票日: ["ticket", "star", "candy"], 晒被子日: ["shirt", "star", "flower"], 甜品节: ["candy", "heart", "star"], 端午节: ["zongzi", "wave", "lantern"],
  跳舞日: ["note", "ball", "star"], 七夕: ["heart", "star", "flower"], 读书日: ["book", "star", "note"], 中秋节: ["moon", "lantern", "star"],
  怪兽夜: ["pumpkin", "bat", "moon"], 大扫除日: ["broom", "star", "flower"], 马拉松日: ["medal", "star", "flower"], 冬至: ["snow", "bowl", "star"],
  雪人日: ["snowman", "snow", "star"], 春节: ["firecracker", "lantern", "star"],
};
function fbDeco(name) {
  const deco = fbEl.querySelector(".fb-deco"), kinds = FB_MOTIFS[name] || ["star", "heart"];
  const one = () => {
    let h = "";
    for (let i = 0; i < 18; i++) {
      const x = (i / 18) * 100 + Math.random() * 4, y = 8 + ((i * 37) % 70), sz = 18 + ((i * 7) % 4) * 4 + Math.random() * 4;
      const light = x > 55, k = kinds[i % kinds.length];
      h += `<svg viewBox="0 0 24 24" shape-rendering="crispEdges" style="left:${x.toFixed(1)}%;top:${y}%;width:${sz.toFixed(0)}px;height:${sz.toFixed(0)}px;--r:${(Math.random() * 30 - 15).toFixed(0)}deg;--d:${(Math.random() * -6).toFixed(1)}s;--t:${(4 + Math.random() * 3).toFixed(1)}s" class="${light ? "tint" : ""}"><path d="${FB_SHAPES[k]}"/></svg>`;
    }
    return `<span class="fb-deco-run">${h}</span>`;
  };
  deco.innerHTML = `<span class="fb-deco-strip">${one()}${one()}</span>`;   // two copies side by side: a seamless loop
}
let fbName = null, fbTimer = 0;
// the highest thing it must stay above: the diary row, its open list, the settings rows,
// a chat bubble with a friend, an incoming call
function fbUnderTop() {
  let top = diaryBox.getBoundingClientRect().top;
  for (const el of [diaryPop, setPop, document.getElementById("peerHud"), document.getElementById("incomingCall")]) {
    if (!el || el.hidden || !el.offsetHeight || getComputedStyle(el).visibility === "hidden") continue;
    const r = el.getBoundingClientRect();
    if (r.height && r.bottom > 0) top = Math.min(top, r.top);
  }
  return top;
}
function fbPlace() {
  const box = fbEl.parentElement.getBoundingClientRect(), above = fbUnderTop();
  let top = above - box.top - fbEl.offsetHeight - 6;
  if (!updEl.hidden) top -= updEl.offsetHeight + 6;              // the update pill keeps its own row
  fbEl.style.top = Math.round(top) + "px";
  fbEl.style.left = view.offsetLeft + "px";
  fbEl.style.width = view.offsetWidth + "px";
  const h = fbEl.offsetHeight;                                   // pixel-stepped round ends, sized to the bar and its pills
  if (h && h !== fbEl._clipH) {
    fbEl._clipH = h;
    fbEl.style.setProperty("--fb-clip", roundClip(Math.max(3, Math.floor(h / 4)), 2));
    fbEl.style.setProperty("--fb-pill-clip", roundClip(Math.max(3, Math.floor((h - 12) / 4)), 2));
  }
}
function fbFollow() {
  if (fbEl.hidden) return;
  fbPlace();
  if (fbEl.getBoundingClientRect().top < 4 && performance.now() - (fbEl._room || 0) > 250) { fbEl._room = performance.now(); makeRoom(); }   // pushed off the top: ask for room
  requestAnimationFrame(fbFollow);
}
function fbShow(f) {
  const [a, b, line, ...acts] = FEST_BAR[f.name] || ["#e1725b", "#f6a487", pick(f.say || ["节日快乐"])];
  fbEl.style.setProperty("--fb-a", a); fbEl.style.setProperty("--fb-b", b);
  fbEl.querySelector(".fb-name").textContent = f.chip || f.name;
  fbDeco(f.name);
  const box = fbEl.querySelector(".fb-acts"), n = acts.length + 1;
  box.innerHTML = "";
  acts.forEach(([label, kind, what], i) => {
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = "fb-pill"; btn.textContent = label; btn.style.setProperty("--i", i); btn.style.setProperty("--n", n);
    btn.title = kind === "place" ? `让${nameOf()}去${PLACE_NAME[what] || what}` : label;
    btn.addEventListener("click", e => { e.stopPropagation(); fbGo(kind, what, btn); });
    box.appendChild(btn);
  });
  const say = document.createElement("span");
  say.className = "fb-pill fb-say"; say.textContent = line; say.style.setProperty("--i", acts.length); say.style.setProperty("--n", n);
  box.appendChild(say);
  clearTimeout(fbTimer);
  fbEl.hidden = false; fbEl.className = "fest-bar"; void fbEl.offsetWidth;
  fbPlace(); makeRoom(); fbPlace();
  fbEl.classList.add("in");
  requestAnimationFrame(fbFollow);
  fbTimer = setTimeout(() => { fbEl.classList.remove("in"); fbEl.classList.add("idle"); }, 1100);
}
function fbHide() {
  clearTimeout(fbTimer);
  fbEl.classList.remove("in", "idle"); fbEl.classList.add("out");
  fbTimer = setTimeout(() => { fbEl.hidden = true; fbEl.classList.remove("out"); makeRoom(); }, 650);
}
function fbTick() {
  if (!booted) return;
  const f = friendHousePreview ? null : festToday(), name = f?.name || null;
  if (name !== fbName) {
    const was = fbName; fbName = name;
    if (was) fbHide();
    if (f) setTimeout(() => { if (fbName === f.name) fbShow(f); }, was ? 700 : 0);
  }
  if (!fbEl.hidden && fbEl.offsetHeight !== fbEl._h) { fbEl._h = fbEl.offsetHeight; makeRoom(); }
}
setInterval(fbTick, 400);
