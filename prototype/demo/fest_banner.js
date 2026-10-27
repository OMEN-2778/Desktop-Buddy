// ================================================================ the festival banner (user)
// On a festival a banner rides above the diary, left-aligned with the house
// (the update pill keeps the right side): the festival's own pixel icon, its
// name and what there is to do today. It drops in with a bounce and a burst
// of confetti, then idles (the icon bobs, a shine sweeps across, sparkles
// twinkle) and leaves with a little hop when the day is over. Clicking it
// throws the confetti again.
const fbEl = document.getElementById("festBanner");
const FEST_BANNER = {
  元宵节: ["#d9534a", "#f2a65a", "公园里有灯谜树，去猜猜看"], 赖床节: ["#6c7fc4", "#a8b8ea", "今天多睡会儿，有额外好心情"],
  春分: ["#5fa565", "#a7d47a", "春天来了，出门走走吧"], 写信日: ["#c0675a", "#e9b08a", "用手机或电脑给人写封信"],
  彩票日: ["#d1912c", "#f3cf5b", "买张彩票，试试手气"], 晒被子日: ["#4f9fb0", "#9bd3df", "门口晒满了被子"],
  甜品节: ["#d16a94", "#f5b3cb", "公园里摆满了甜品摊"], 端午节: ["#3f8f5a", "#9fcf6e", "码头有龙舟赛，去加油吧"],
  跳舞日: ["#7c4fd0", "#e06ab5", "迪厅开张啦，去跳一曲"], 七夕: ["#d0577f", "#f2a3bf", "公园挂满了浪漫灯串"],
  读书日: ["#3c7a8a", "#7fc4b6", "今天读书有额外好心情"], 中秋节: ["#c47a2c", "#f0c766", "做月饼，逛逛公园的月饼摊"],
  怪兽夜: ["#5b3c8f", "#e0782f", "戴上面具，街上有百鬼夜行"], 大扫除日: ["#4b8fb8", "#a6d3ea", "一起来大扫除吧"],
  马拉松日: ["#d4553f", "#f39a6a", "家门口在跑马拉松"], 冬至: ["#4b6aa8", "#a6c5e7", "大雪下了一整天"],
  雪人日: ["#5a86b8", "#cfe3f5", "到处都是雪人，也去堆一个"], 春节: ["#c8312f", "#f2b33d", "新年快乐，万事如意"],
};
function fbIcon(name) {
  const F = D.festival, F2 = D.festival2, dish = k => (D.items.dish[k] || [])[0];
  return ({ 元宵节: F.lantern, 端午节: dish("zongzi"), 中秋节: dish("mooncake"), 写信日: F.envelope, 彩票日: F.stalls.lottery,
    晒被子日: F.quilts[0], 甜品节: dish("cake"), 跳舞日: F2.mirrorBall[0], 七夕: F.heartArch, 读书日: dish("book"),
    怪兽夜: F2.masks[0], 马拉松日: F2.fence, 冬至: dish("tangyuan"), 雪人日: F2.snowmen[1], 春节: F.lantern })[name] || F.lantern;
}
function fbDrawIcon(src) {                         // the icon at whole house pixels, never smoothed
  const c = fbEl.querySelector(".fb-icon"), img = festImg(src);
  const go = () => {
    c.width = img.width; c.height = img.height;
    const k = Math.max(1, Math.floor(scale * Math.min(1, 20 / Math.max(img.width, img.height))));
    c.style.width = img.width * k + "px"; c.style.height = img.height * k + "px";
    const x = c.getContext("2d"); x.imageSmoothingEnabled = false; x.clearRect(0, 0, c.width, c.height); x.drawImage(img, 0, 0);
  };
  if (img.complete && img.naturalWidth) go(); else img.addEventListener("load", go, { once: true });
}
function fbConfetti() {
  if (reduceMotionUI) return;
  const box = fbEl.querySelector(".fb-confetti"), cols = ["#ffd84a", "#ff5fa2", "#4fd2ff", "#6dff9c", "#ffffff", "#ff8a3d"];
  box.innerHTML = "";
  for (let i = 0; i < 14; i++) {
    const s = document.createElement("i"), a = (i / 14) * Math.PI * 2 + Math.random() * 0.4, r = 26 + Math.random() * 30;
    s.style.cssText = `--dx:${Math.round(Math.cos(a) * r)}px;--dy:${Math.round(Math.sin(a) * r * 0.7 - 8)}px;--c:${cols[i % cols.length]};--d:${Math.round(Math.random() * 120)}ms`;
    box.appendChild(s);
  }
}
let fbName = null, fbTimer = 0;
function fbPlace() {
  const box = fbEl.parentElement.getBoundingClientRect(), d = diaryBox.getBoundingClientRect();
  fbEl.style.top = Math.round(d.top - box.top - fbEl.offsetHeight - 14) + "px";
  fbEl.style.left = view.offsetLeft + "px";
}
function fbShow(f) {
  const [a, b, tip] = FEST_BANNER[f.name] || ["#e1725b", "#f6a487", pick(f.say || ["节日快乐"])];
  fbEl.style.setProperty("--fb-a", a); fbEl.style.setProperty("--fb-b", b);
  fbEl.querySelector("b").textContent = f.chip || f.name;
  fbEl.querySelector(".fb-tip").textContent = tip;
  fbEl.title = `${f.name}：${tip}`;
  fbDrawIcon(fbIcon(f.name));
  clearTimeout(fbTimer);
  fbEl.hidden = false; fbEl.className = "fest-banner"; void fbEl.offsetWidth;
  makeRoom(); fbPlace();
  fbEl.classList.add("in"); fbConfetti();
  fbTimer = setTimeout(() => fbEl.classList.add("idle"), 650);
}
function fbHide() {
  clearTimeout(fbTimer);
  fbEl.classList.remove("in", "idle"); fbEl.classList.add("out");
  fbTimer = setTimeout(() => { fbEl.hidden = true; fbEl.classList.remove("out"); makeRoom(); }, 300);
}
function fbTick() {
  if (typeof booted === "undefined" || !booted) return;
  const f = friendHousePreview ? null : festToday(), name = f?.name || null;
  if (name !== fbName) {
    const was = fbName; fbName = name;
    if (was) fbHide();
    if (f) setTimeout(() => { if (fbName === f.name) fbShow(f); }, was ? 340 : 0);
  }
  if (!fbEl.hidden && fbEl.offsetHeight !== fbEl._h) { fbEl._h = fbEl.offsetHeight; makeRoom(); }   // (the icon loads a moment later)
  if (!fbEl.hidden) fbPlace();
}
fbEl.addEventListener("click", () => { fbConfetti(); fbEl.classList.remove("pop"); void fbEl.offsetWidth; fbEl.classList.add("pop"); });
setInterval(fbTick, 500);
