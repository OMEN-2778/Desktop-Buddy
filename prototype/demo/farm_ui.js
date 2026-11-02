// ================================================================ 农庄 / 丢丢币 UI (2026-11-02)
// Owner: draw game-ready UI for the twelve farm screens, not generated
// pictures. Everything here reuses the game's own pieces: ring menus for
// actions on a thing (航班, 菜地, 果树), the pick-a-thing panel for shops,
// the house-sized social sheet for details and the 丢丢平板电脑. Icons are
// pixelkit art (art/src/concept/farm_icons.py); crop/tree stages and animals
// are the farm map's own sprites. State comes in as plain data: this module
// only draws; the farm rules (DIDI_CURRENCY.md) live elsewhere.
const FarmUI = (() => {
  const IC = (typeof FARM_UI_ART !== "undefined" && FARM_UI_ART) || { icons: {}, stages: {}, animals: {} };
  const coins = v => (Math.round(v * 10) / 10).toFixed(Number.isInteger(Math.round(v * 10) / 10) ? 0 : 1);
  const signed = v => (v > 0 ? "+" : v < 0 ? "−" : "±") + Math.abs(v).toFixed(1);
  const k2 = () => (scale >= 3 ? 2 : 1);                                   // icon pixels per art pixel
  const houseK = () => Math.max(1, Math.round(scale));
  // icons at a whole 1x/2x; farm-map art (stages, animals) at one art pixel per house pixel
  function img(src, cls = "fu-ic", k = k2) {
    const i = new Image(); i.alt = ""; i.className = cls; i.src = src || "";
    i.onload = () => { const m = k(); i.style.width = i.naturalWidth * m + "px"; i.style.height = i.naturalHeight * m + "px"; };
    return i;
  }
  const icon = name => img(IC.icons[name]);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  function coinPill(balance) {
    const p = el("span", "fu-coin"); p.append(icon("coin"), el("b", null, coins(balance)), el("small", null, "丢丢币"));
    p.setAttribute("aria-label", `丢丢币 ${coins(balance)}`); return p;
  }

  // ---------------------------------------------------------------- rings
  // items: [{id, label, icon, off: "why not now"}]; at: {x, y} in house px.
  let anchor = null;
  function ring(title, items, at) {
    anchor = at;
    RINGS.farm = [["name", null, "label"], ...items.map(it => [it.id, it.label])];
    openRing("farm", "farm");
    const [label, ...buttons] = ringEl.children;
    label.textContent = title;
    buttons.forEach((b, i) => {
      const it = items[i];
      if (it.icon) b.prepend(img(IC.icons[it.icon], "fu-ring-ic"));
      if (it.off) { b.classList.add("fu-off"); b.setAttribute("aria-disabled", "true"); b.title = it.off;
        b.append(el("small", "fu-why", it.off)); }
    });
    ringEl.classList.add("fu-ring");
    const settle = () => { layoutRing(); placeRing(); };
    settle(); requestAnimationFrame(settle);
  }
  const oldCenter = ringCenter;
  ringCenter = function () { return ringAt === "farm" && anchor ? anchor : oldCenter(); };
  const oldClose = closeRing;
  closeRing = function () { ringEl.classList.remove("fu-ring"); return oldClose(); };

  // ---------------------------------------------------------------- shops (the pick-a-thing panel)
  // goods: [{group, items: [{id, name, icon|pic, cost, info, line, off}]}]
  function shop(act, title, balance, goods, from) {
    PICK[act] = { title, groups: () => goods.map(g => ({ name: g.group, note: g.note, items: g.items.map(it => ({
      title: it.name, icon: it.pic || IC.icons[it.icon], info: `${coins(it.cost)} 丢丢币${it.info ? " · " + it.info : ""}`, line: it.line || "", item: it })) })) };
    openPicker(act, from);
    const head = pickerEl.querySelector(".pk-head");
    head.querySelector(".fu-coin")?.remove();
    head.insertBefore(coinPill(balance), head.querySelector(".rand"));
    pickerEl.querySelector(".rand").hidden = true;                      // buying is never random
    pickerEl.classList.add("fu-shop");
    const all = goods.flatMap(g => g.items), btns = [...pickerEl.querySelectorAll(".pk-item")];
    btns.forEach((b, i) => {
      const it = all[i], why = it.off || (it.cost > balance ? `还差 ${coins(it.cost - balance)} 币` : "");
      b.querySelector("img").classList.add("fu-pic");
      if (why) { b.classList.add("fu-off"); b.setAttribute("aria-disabled", "true"); b.append(el("em", "fu-why", why)); }
    });
  }
  const oldClosePicker = closePicker;
  closePicker = function () { pickerEl.classList.remove("fu-shop"); pickerEl.querySelector(".rand").hidden = false;
    pickerEl.querySelector(".fu-coin")?.remove(); return oldClosePicker(); };

  // ---------------------------------------------------------------- house-sized sheets
  function sheet(title, cls) {
    const s = openSocialSheet(title);
    s.classList.add("fu-sheet", ...(cls ? [cls] : []));
    s.style.setProperty("--fu-k", k2());
    return s;
  }
  function meter(name, iconName, value, max = 4) {   // a row of whole pixel icons, empty ones faded
    const row = el("div", "fu-meter"); row.append(el("span", "fu-label", name));
    const cells = el("span", "fu-cells");
    for (let i = 0; i < max; i++) { const c = icon(iconName); if (i >= value) c.classList.add("fu-empty"); cells.append(c); }
    row.append(cells); row.setAttribute("role", "meter"); row.setAttribute("aria-valuenow", value); row.setAttribute("aria-valuemax", max);
    return row;
  }
  function bar(p, label) {
    const b = el("div", "fu-bar"); b.setAttribute("role", "progressbar"); b.setAttribute("aria-valuenow", Math.round(p * 100));
    const f = el("i"); f.style.width = Math.round(p * 100) + "%"; b.append(f, el("span", null, label)); return b;
  }
  function actions(list) {   // [{label, icon, off, primary}]
    const row = el("div", "fu-actions");
    for (const a of list) {
      const b = el("button", a.primary ? "fu-btn fu-primary" : "fu-btn"); b.type = "button";
      if (a.icon) b.append(icon(a.icon));
      b.append(el("span", null, a.label));
      if (a.off) { b.disabled = true; b.title = a.off; b.append(el("small", "fu-why", a.off)); }
      if (a.on) b.onclick = a.on;
      row.append(b);
    }
    return row;
  }

  // 作物 / 果树 details: {kind: "crop"|"tree", name, produce, stages: [src...], stage, days, total, watered, sell, plot}
  function plant(p) {
    const s = sheet(p.plot, "fu-plant"), c = socialContent(s);
    const top = el("div", "fu-plant-top"), pic = el("div", "fu-hero"); pic.append(img(IC.icons[p.produce], "fu-ic", () => Math.min(2, Math.max(1, Math.round(scale)))));
    const facts = el("div", "fu-facts");
    facts.append(el("h4", null, p.name), el("p", "fu-sub", p.kind === "tree" ? p.cycle : `种下 ${p.total} 天成熟`));
    const stages = el("ol", "fu-stages");
    top.append(pic, facts, stages);
    p.stages.forEach((src, i) => { const li = el("li", i === p.stage ? "now" : i < p.stage ? "done" : ""); li.append(img(src, "fu-stage", houseK));
      li.append(el("span", null, p.stageNames[i])); stages.append(li); });
    const info = el("div", "fu-lines");
    const water = el("p"); water.append(icon("drop"), el("span", null, p.watered ? "今天浇过水了" : "今天还没浇水"));
    if (!p.watered) water.classList.add("fu-warn");
    const sell = el("p"); sell.append(icon("coin"), el("span", null, `全部卖掉约 ${coins(p.sell)} 丢丢币`));
    info.append(water, sell);
    c.append(top, info, bar(p.days / p.total, `第 ${p.days} 天 · 共 ${p.total} 天`));
    s.append(actions(p.actions));
    return s;
  }

  // 牧场: {tab, animals: {chicken: {...}, sheep, cow}}
  const ANIMAL_TABS = [["chicken", "鸡"], ["sheep", "羊"], ["cow", "牛"]];
  function ranch(st) {
    const s = sheet("牧场", "fu-ranch"), c = socialContent(s);
    const tabs = el("div", "fu-tabs"); tabs.setAttribute("role", "tablist");
    for (const [id, name] of ANIMAL_TABS) {
      const a = st.animals[id], b = el("button", id === st.tab ? "on" : "", null); b.type = "button"; b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", id === st.tab); b.append(el("span", null, `${name} ${a ? a.count : 0}`));
      if (!a || !a.count) b.classList.add("fu-none");
      b.onclick = () => ranch({ ...st, tab: id });
      tabs.append(b);
    }
    const a = st.animals[st.tab];
    const body = el("div", "fu-ranch-body"), pen = el("div", "fu-pen"); pen.append(img(IC.animals[st.tab], "fu-animal", houseK));
    const facts = el("div", "fu-facts");
    facts.append(el("h4", null, a.title), meter("饮水", "drop", a.water), meter("饲料", "hay", a.feed));
    const prod = el("p", "fu-sub"); prod.append(icon(a.product), el("span", null, a.next)); facts.append(prod);
    body.append(pen, facts);
    c.append(tabs, body, el("p", "fu-note", "基础草料和清水都是免费的。"));
    s.append(actions([{ label: "添水", icon: "drop", off: a.water >= 4 ? "水槽是满的" : "" },
      { label: "喂草", icon: "hay", off: a.feed >= 4 ? "还吃不下" : "" },
      { label: "收取", icon: "basket", off: a.ready ? "" : "还没有", primary: true }]));
    return s;
  }

  // ---------------------------------------------------------------- 丢丢平板电脑
  const PC_TABS = [["farm", "农庄", "farm"], ["coin", "丢丢币", "coin"], ["fund", "每日操盘", "chart"], ["gift", "礼物与藏品", "gift"]];
  function computer(tab, st) {
    const s = sheet("丢丢平板电脑", "fu-pc"), c = socialContent(s);
    const nav = el("nav", "fu-nav"); nav.setAttribute("role", "tablist");
    for (const [id, name, ic] of PC_TABS) {
      const b = el("button", id === tab ? "on" : ""); b.type = "button"; b.setAttribute("role", "tab"); b.setAttribute("aria-selected", id === tab);
      b.append(icon(ic), el("span", null, name)); b.onclick = () => computer(id, st); nav.append(b);
    }
    const main = el("div", "fu-main");
    ({ farm: pcFarm, coin: pcCoin, fund: pcFund, gift: pcGift })[tab](main, st);
    c.append(nav, main);
    return s;
  }
  function pcFarm(m, st) {
    const f = st.farm;
    m.append(el("h4", null, "农庄"));
    const grid = el("div", "fu-stats");
    for (const [name, v, sub] of [["田地", `${f.fields} / 4 块`, f.nextField], ["果树", `${f.trees} / 2 棵`, ""],
      ["牲畜", f.animals, ""], ["家当", `约 ${f.assets} 币`, "田地、果树、牲畜"]]) {
      const d = el("div"); d.append(el("small", null, name), el("b", null, v)); if (sub) d.append(el("span", null, sub)); grid.append(d);
    }
    m.append(grid);
  }
  function pcCoin(m, st) {
    const a = st.account, big = el("div", "fu-balance");
    big.append(img(IC.icons.coin, "fu-ic fu-big"), el("b", null, coins(a.balance)), el("span", null, "丢丢币"));
    const today = el("p", "fu-sub", `今天 ${signed(a.today)}`); today.classList.add(a.today >= 0 ? "fu-up" : "fu-down");
    const list = el("ol", "fu-ledger"); list.setAttribute("aria-label", "最近记录");
    for (const r of a.ledger) {
      const li = el("li"); li.append(icon(r.icon), el("span", null, r.text), el("time", null, r.when),
        el("b", r.v >= 0 ? "fu-up" : "fu-down", signed(r.v)));
      list.append(li);
    }
    m.append(big, today, el("h5", null, "最近记录"), list);
  }
  function pcFund(m, st) {
    const f = st.fund;
    const head = el("div", "fu-stats fu-mini");
    for (const [name, v] of [["持有", `${coins(f.held)} 币`], ["今天", `${f.pct > 0 ? "+" : ""}${f.pct}%`], ["还可投入", `${f.inLeft} 币`], ["还可赎回", `${f.outLeft} 币`]]) {
      const d = el("div"); d.append(el("small", null, name), el("b", null, v)); if (name === "今天") d.classList.add(f.pct >= 0 ? "fu-up" : "fu-down"); head.append(d);
    }
    const chart = el("canvas", "fu-chart"); chart.setAttribute("role", "img"); chart.setAttribute("aria-label", "最近 14 天的走势");
    const step = el("div", "fu-step");
    const minus = el("button", "fu-btn", "−"), plus = el("button", "fu-btn", "+"), amt = el("b", null, `${f.amount} 币`);
    minus.type = plus.type = "button"; minus.setAttribute("aria-label", "少一点"); plus.setAttribute("aria-label", "多一点");
    step.append(minus, amt, plus);
    const row = el("div", "fu-trade"); row.append(step, actions([{ label: "投入", primary: true, off: f.inLeft ? "" : "今天投满了" },
      { label: "赎回", off: f.outLeft ? "" : "今天赎满了" }]));
    m.append(head, chart, row, el("p", "fu-note", "满仓一天最多涨跌 3 币。今天投入的部分明天才能赎回。"));
    requestAnimationFrame(() => drawChart(chart, f.history));
  }
  // The trend on the house pixel grid: integer points, stair-step joins,
  // drawn in house pixels and scaled by whole numbers (no smooth lines).
  function drawChart(cv, hist) {
    const k = Math.max(1, Math.round(scale)), w = Math.max(60, Math.floor(cv.parentElement.clientWidth / k)), h = Math.max(24, Math.min(40, Math.round(w * .13)));
    cv.width = w; cv.height = h; cv.style.width = w * k + "px"; cv.style.height = h * k + "px";
    const x = cv.getContext("2d"), lo = Math.min(...hist), hi = Math.max(...hist), pad = 3;
    const py = v => Math.round(h - pad - (v - lo) / Math.max(.01, hi - lo) * (h - pad * 2));
    const px = i => Math.round(pad + i * (w - pad * 2 - 1) / (hist.length - 1));
    x.fillStyle = "#eceaf2"; x.fillRect(0, 0, w, h);
    x.fillStyle = "#dedce7"; for (let gy = pad; gy < h; gy += 6) x.fillRect(0, gy, w, 1);
    for (let i = 1; i < hist.length; i++) {
      const a = [px(i - 1), py(hist[i - 1])], b = [px(i), py(hist[i])], up = hist[i] >= hist[i - 1];
      x.fillStyle = up ? "#337a78" : "#b94b4b";
      const mid = Math.round((a[0] + b[0]) / 2);
      x.fillRect(a[0], a[1], mid - a[0] + 1, 1);
      x.fillRect(mid, Math.min(a[1], b[1]), 1, Math.abs(b[1] - a[1]) + 1);
      x.fillRect(mid, b[1], b[0] - mid + 1, 1);
    }
    const last = [px(hist.length - 1), py(hist.at(-1))];
    x.fillStyle = "#22182a"; x.fillRect(last[0] - 1, last[1] - 1, 3, 3); x.fillStyle = "#f7f6fb"; x.fillRect(last[0], last[1], 1, 1);
  }
  function pcGift(m, st) {
    const g = st.gifts, tabs = el("div", "fu-tabs"); tabs.setAttribute("role", "tablist");
    for (const [id, name] of [["gift", "礼物"], ["keep", "藏品"]]) {
      const b = el("button", id === g.tab ? "on" : "", name); b.type = "button"; b.setAttribute("role", "tab");
      b.onclick = () => computer("gift", { ...st, gifts: { ...g, tab: id } }); tabs.append(b);
    }
    const body = el("div", "fu-gifts"), grid = el("div", "fu-grid"), list = g.tab === "keep" ? g.keep : g.items;
    list.forEach((it, i) => {
      const b = el("button", "fu-cell" + (i === g.sel ? " on" : "") + (it.locked ? " fu-locked" : "")); b.type = "button";
      b.append(it.locked ? el("span", "fu-q", "？") : icon(it.icon)); if (it.n > 1) b.append(el("small", null, "×" + it.n));
      b.title = it.locked ? "还没得到" : it.name; b.onclick = () => computer("gift", { ...st, gifts: { ...g, sel: i } }); grid.append(b);
    });
    const it = list[g.sel] || list[0], side = el("div", "fu-detail");
    if (it && !it.locked) side.append(icon(it.icon), el("h4", null, it.name), el("p", null, it.line),
      actions([{ label: g.tab === "keep" ? "摆到家里" : "送给…", primary: true }]));
    body.append(grid, side);
    m.append(tabs, body);
  }

  return { ring, shop, plant, ranch, computer, icon, coinPill };
})();
