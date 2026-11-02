// Review harness for farm_ui.js (tools/make_farm_ui_preview.py only; never in the game).
// farmPreview.show(1..12) opens one screen over a still backdrop of the place it belongs to.
const farmPreview = (() => {
  const A = FARM_UI_ART, pics = {};
  for (const [k, src] of Object.entries(A.backs)) { const i = new Image(); i.src = src; pics[k] = i; }
  let stage = null;   // {back, crop, hero: [x, feet], mom: [x, feet]}
  const momLook = (socialState.contacts.find(c => c.id === "mom") || {}).look || doll.PRESETS.f;
  const mom = { look: momLook, ramps: doll.rampsOf(momLook), cache: new Map() };
  const oldRender = render;
  render = function () {
    if (!stage) return oldRender();
    const k = view.width / W, p = pics[stage.back], [sx, sw] = stage.crop || [0, W];
    vctx.setTransform(k, 0, 0, k, 0, 0); vctx.imageSmoothingEnabled = false; vctx.clearRect(0, 0, W, H);
    if (p.complete) vctx.drawImage(p, sx, 0, sw, 118, 0, 0, W, 118);
    const f = { expr: "happy", look: 0, bob: 0, sway: 0, wave: null };
    if (stage.hero) vctx.drawImage(dollCanvas(f), stage.hero[0] - 10, stage.hero[1] - DH + 1);
    if (stage.mom) { const c = npcCanvas(mom, { ...f, look: -1 }, "stand"); vctx.save(); vctx.translate(stage.mom[0] + 10, 0); vctx.scale(-1, 1); vctx.drawImage(c, 0, stage.mom[1] - DH + 1); vctx.restore(); }
    vctx.setTransform(1, 0, 0, 1, 0, 0);
  };
  showCard = () => {};   // no chance card over the review shots
  let speech = null;
  function reset() {
    speed = 0; closeRing(); closePicker(); closeSocialSheet(); setDiaryOpen(false); speech?.hide();
    if (typeof guideOn !== "undefined" && guideOn) closeGuide();
    stage = null;
  }
  const S = A.stages, NAMES = ["种子", "发芽", "长大", "成熟"], TREE = ["树苗", "小树", "开花", "结果"];
  const pcState = {
    farm: { fields: 2, nextField: "再经营 5 天可整理第 3 块（6 币）", trees: 1, animals: "鸡 1", assets: 18 },
    account: { balance: 8.5, today: 2, ledger: [
      { icon: "carrot", text: "卖掉一田胡萝卜", when: "第 6 天 16:20", v: 2 },
      { icon: "seeds", text: "买胡萝卜种子", when: "第 6 天 07:40", v: -1 },
      { icon: "egg", text: "卖掉一篮鸡蛋", when: "第 5 天 18:05", v: 1 },
      { icon: "chart", text: "操盘赎回", when: "第 5 天 10:12", v: 4.6 },
      { icon: "cabbage", text: "买白菜种子", when: "第 4 天 08:31", v: -2 } ] },
    fund: { held: 24.6, pct: 1.2, inLeft: 10, outLeft: 6, amount: 5, history: [20, 20.2, 19.8, 20.4, 21, 20.7, 21.3, 22, 21.6, 22.8, 23.1, 22.6, 24.3, 24.6] },
    gifts: { tab: "gift", sel: 0, items: [
      { icon: "carrot", name: "自家胡萝卜", n: 3, line: "刚从地里拔的，还带着泥。送朋友正合适。" },
      { icon: "egg", name: "一篮鸡蛋", n: 1, line: "自家母鸡下的。" },
      { icon: "peach", name: "水蜜桃", n: 2, line: "软软的，很甜。" },
      { icon: "gift", name: "节日礼盒", n: 1, line: "节日买的小礼物。" },
      { icon: "wool", name: "一团羊毛", n: 1, line: "可以织条围巾。" } ],
      keep: [{ icon: "pumpkin", name: "第一个南瓜", line: "农庄收获的第一个南瓜，舍不得卖。" }, { locked: 1 }, { locked: 1 }, { locked: 1 }, { locked: 1 }, { locked: 1 }] },
  };
  const SHOWS = {
    1() { stage = { back: "airport", hero: [171, 103] };
      FarmUI.ring("选航班", [{ id: "fly:spring", label: "春季农庄 · 免费" }, { id: "fly:x1", label: "？", off: "还没开放" },
        { id: "fly:x2", label: "？", off: "还没开放" }, { id: "fly:x3", label: "？", off: "还没开放" }], { x: 171, y: 80 }); },
    2() { stage = { back: "home", hero: [150, 103], mom: [196, 103] };
      speech ||= createStorySpeech({ view, anchor: who => who === "妈妈" ? { x: 196, y: 103 } : { x: 150, y: 103 } });
      speech.show("妈妈", "来啦！路上累不累？爸爸去镇上买化肥了，先带你看看你的房间。", { special: true, advance: () => {} }); },
    3() { log("妈妈寄来一封信", null, [["@letter", "妈妈"], ["", `${nameOf()}：`], ["", "我和你爸在山谷里承包了一小片农庄，地方不大，有菜地、果园，还有几只鸡。"],
        ["", "春天正是播种的时候，想请你来帮帮忙。机场有去农庄的航班，票我们已经买好了。"], ["", "你的房间收拾好了，被子也晒过了。等你来！"], ["", "—— 妈妈"]]);
      setDiaryOpen(true); setTimeout(() => document.querySelector("#diaryList .talk-btn")?.click(), 100); },
    4() { stage = { back: "farm", hero: [118, 103] };
      FarmUI.ring("菜地 · 第 2 块", [{ id: "sow", label: "播种", icon: "seeds", off: "已种着胡萝卜" }, { id: "water", label: "浇水", icon: "can" },
        { id: "harvest", label: "收获", icon: "basket", off: "还没熟" }, { id: "look", label: "查看", icon: "lens" }], { x: 120, y: 62 }); },
    5() { stage = { back: "farm", hero: [118, 103] };
      FarmUI.shop("farm_seed", "种子铺 · 这块田种什么", 2.5, [{ group: "种子", note: "一包种满一块田", items: [
        { name: "胡萝卜", icon: "carrot", cost: 1, info: "2 天", line: "长得最快，全部卖掉约 2 币。" },
        { name: "白菜", icon: "cabbage", cost: 2, info: "4 天", line: "全部卖掉约 4 币。" },
        { name: "玉米", icon: "corn", cost: 2, info: "6 天", line: "全部卖掉约 5 币。" },
        { name: "南瓜", icon: "pumpkin", cost: 3, info: "8 天", line: "最慢，全部卖掉约 7 币。" } ] }]); },
    6() { stage = { back: "farm", hero: [118, 103] };
      FarmUI.plant({ kind: "crop", plot: "菜地 · 第 2 块", name: "胡萝卜", produce: "carrot", stages: S.carrot, stageNames: NAMES, stage: 1,
        days: 1, total: 2, watered: true, sell: 2, actions: [{ label: "浇水", icon: "can", off: "今天浇过了" }, { label: "收获", icon: "basket", off: "还没熟", primary: true }] }); },
    7() { stage = { back: "ranch", crop: [0, 342], hero: [150, 103] };
      FarmUI.ring("桃树", [{ id: "water", label: "浇水", icon: "can" }, { id: "pick", label: "采摘", icon: "basket", off: "正在开花" },
        { id: "look", label: "查看", icon: "lens" }], { x: 152, y: 66 }); },
    8() { stage = { back: "ranch", crop: [342, 342], hero: [190, 103] };
      FarmUI.ranch({ tab: "chicken", animals: {
        chicken: { count: 1, title: "母鸡 · 来了 3 天", water: 3, feed: 1, product: "egg", next: "明天能捡一篮鸡蛋", ready: false },
        sheep: { count: 0, title: "还没有羊", water: 0, feed: 0, product: "wool", next: "", ready: false },
        cow: { count: 0, title: "还没有牛", water: 0, feed: 0, product: "milk", next: "", ready: false } } }); },
    9() { stage = { back: "ranch", crop: [342, 342], hero: [190, 103] };
      FarmUI.shop("farm_animal", "牲畜铺 · 添点什么", 8.5, [{ group: "牲畜", note: "清水和草料免费", items: [
        { name: "鸡", pic: A.animals.chicken, cost: 8, info: "每 4 天产 1 币", line: "已有 1 只，今年还能再养 1 只。" },
        { name: "羊", pic: A.animals.sheep, cost: 24, info: "每 6 天产 3 币", line: "羊毛能卖，也能当礼物。" },
        { name: "牛", pic: A.animals.cow, cost: 36, info: "每 4 天产 2 币", line: "每天有新鲜牛奶。" } ] },
        { group: "果苗", items: [{ name: "桃树苗", icon: "sapling", cost: 8, info: "8 天后结果", line: "之后每 6 天能摘一次。", off: "今年两棵都种满了" }] }]); },
    10() { FarmUI.computer("coin", pcState); },
    11() { FarmUI.computer("fund", pcState); },
    12() { FarmUI.computer("gift", pcState); },
  };
  return { show(n) { reset(); SHOWS[n](); render(); }, reset };
})();
window.farmPreview = farmPreview;
