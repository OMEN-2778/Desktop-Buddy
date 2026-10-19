// ================================================================ Buddy 造型室 (dressing room)
// One panel, used as the whole page in prototype/creator and as the pop-up
// above the house in prototype/demo. Tabs: hair / face / top / bottom / socks /
// accessories; every option is a live thumbnail of Buddy in the current colors.
//
//   const studio = BuddyStudio(rootEl, doll, DATA, {
//     look, onChange(look), onClose?, modes?: true, previewScale?: 4, thumbH?: 44 })
//   studio.setLook(look) · studio.start() · studio.stop() · studio.look
function BuddyStudio(root, doll, DATA, opts = {}) {
  const O = DATA.options;
  let look = doll.normalize(opts.look);
  let tab = "hair", mode = "idle";
  const COVERS_SOCKS = ["trousers", "jeans", "maxi"];
  const HIDES_HAIR = ["beanie", "headphones"];

  const TABS = [
    { id: "hair", name: "发型", groups: [{ kind: "thumbs", key: "style", opt: "style", label: "发型" }, { kind: "colors", key: "hair", label: "发色" }] },
    { id: "face", name: "五官", groups: [{ kind: "gender", label: "性别" }, { kind: "thumbs", key: "eyes", opt: "eyes", label: "眼型" },
                                        { kind: "colors", key: "eye", label: "瞳色" }, { kind: "colors", key: "skin", label: "肤色" }] },
    { id: "top", name: "上装", groups: [{ kind: "thumbs", key: "topStyle", opt: "top", label: "款式" }, { kind: "colors", key: "top", label: "颜色" }] },
    { id: "bottom", name: "下装", groups: [{ kind: "thumbs", key: "bottomStyle", opt: "bottom", label: "款式" }, { kind: "colors", key: "bottom", label: "颜色" }] },
    { id: "socks", name: "袜子", groups: [{ kind: "thumbs", key: "socks", opt: "socks", label: "款式" }, { kind: "colors", key: "sock", label: "颜色" },
                                         { kind: "note", id: "socksNote" }] },
    { id: "acc", name: "饰品", groups: [{ kind: "thumbs", key: "acc", opt: "acc", label: "佩戴", multi: true },
                                       { kind: "note", text: "可以同时戴好几件，再点一次就取下来。眼镜和墨镜只能二选一。" }] },
  ];
  // thumbnail crop per option kind: x, y, w, h in doll pixels
  const CROP = { style: [0, 0, 20, 16], eyes: [3, 8, 14, 7], topStyle: [1, 14, 18, 9], bottomStyle: [3, 21, 14, 7],
                 socks: [4, 22, 12, 6], acc: [1, 0, 18, 16], scarf: [1, 6, 18, 16] };
  const cropOf = (key, v) => CROP[key === "acc" && v === "scarf" ? "scarf" : key];
  const SWATCH = { hair: DATA.swatches.hair, skin: DATA.swatches.skin, top: DATA.swatches.cloth, bottom: DATA.swatches.cloth,
                   sock: DATA.swatches.cloth, eye: DATA.swatches.eye };

  // a look that shows option v of a kind clearly (nothing covering it)
  function variant(key, v) {
    switch (key) {
      case "style": return { ...look, style: v, acc: look.acc.filter(a => !HIDES_HAIR.includes(a)) };
      case "eyes": return { ...look, eyes: v, acc: look.acc.filter(a => !DATA.eyewear.includes(a)) };
      case "topStyle": return { ...look, topStyle: v, acc: look.acc.filter(a => a !== "scarf") };
      case "socks": return { ...look, socks: v, bottomStyle: "shorts" };   // the legs show best in shorts
      case "acc": return { ...look, acc: [v] };
      default: return { ...look, [key]: v };
    }
  }

  // ---------------------------------------------------------- markup
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  root.classList.add("studio");
  root.setAttribute("aria-label", "Buddy 造型室");
  root.innerHTML = `
    <div class="st-title">
      <span class="st-name">Buddy 造型室</span>
      <span class="st-tools">
        <button type="button" class="st-random">随机搭配</button>
        ${opts.onClose ? `<button type="button" class="st-close" aria-label="关闭造型室">✕</button>` : ""}
      </span>
    </div>
    <div class="st-body">
      <div class="st-stage">
        <div class="st-screen"><canvas class="st-preview" aria-label="Buddy 预览"></canvas></div>
        ${opts.modes ? `<div class="st-modes" role="group" aria-label="表情">${[["idle", "日常"], ["happy", "开心"], ["surprised", "惊讶"],
          ["sleepy", "犯困"], ["flustered", "慌张"]].map(([m, n]) => `<button type="button" data-mode="${m}">${n}</button>`).join("")}</div>` : ""}
      </div>
      <div class="st-main">
        <div class="st-tabs" role="tablist">${TABS.map(t =>
          `<button type="button" role="tab" data-tab="${t.id}" id="st-tab-${t.id}" aria-controls="st-panel-${t.id}">${t.name}</button>`).join("")}</div>
        <div class="st-panels">${TABS.map(t => `
          <div class="st-panel" role="tabpanel" data-tab="${t.id}" id="st-panel-${t.id}" aria-labelledby="st-tab-${t.id}">
            ${t.groups.map(g => groupHTML(g)).join("")}
          </div>`).join("")}</div>
      </div>
    </div>`;

  function groupHTML(g) {
    if (g.kind === "note") return `<p class="st-note"${g.id ? ` data-note="${g.id}"` : ""}>${g.text ? esc(g.text) : ""}</p>`;
    const head = `<span class="st-label">${g.label}</span>`;
    if (g.kind === "gender") {
      return `<div class="st-group">${head}<div class="st-chips" role="group" aria-label="性别">
        <button type="button" data-gender="f">女生</button><button type="button" data-gender="m">男生</button></div></div>`;
    }
    if (g.kind === "thumbs") {
      return `<div class="st-group">${head}<div class="st-thumbs" role="group" aria-label="${g.label}">${O[g.opt].map(([v, name]) => {
        const [, , w, h] = cropOf(g.key, v);
        return `<button type="button" class="st-thumb" data-key="${g.key}" data-v="${v}" title="${esc(name)}">
          <canvas width="${w}" height="${h}" aria-hidden="true"></canvas><span>${esc(name)}</span></button>`;
      }).join("")}</div></div>`;
    }
    // colors: preset swatches + a custom picker that makes the same 5-shade ramp
    const skin = g.key === "skin";
    return `<div class="st-group">${head}<div class="st-swatches" role="group" aria-label="${g.label}" data-color="${g.key}">${SWATCH[g.key].map(([name, hex]) =>
      `<button type="button" class="st-swatch" data-color="${g.key}" data-v="${hex.toLowerCase()}" title="${esc(name)}" aria-label="${esc(name)}"
        style="--c:${hex};--c2:${doll.rampFrom(hex, skin)[1]}"></button>`).join("")}
      <label class="st-swatch st-custom" title="自定义颜色">+<input type="color" data-color="${g.key}" aria-label="${g.label}：自定义颜色"></label>
    </div></div>`;
  }

  const $ = s => root.querySelector(s), $$ = s => [...root.querySelectorAll(s)];
  const preview = $(".st-preview"), pctx = preview.getContext("2d");

  // ---------------------------------------------------------- thumbnails
  const scratch = document.createElement("canvas");
  scratch.width = doll.W; scratch.height = doll.H;
  const sctx = scratch.getContext("2d");
  function paintThumb(btn) {
    const key = btn.dataset.key, v = btn.dataset.v, c = btn.querySelector("canvas");
    const [x, y, w, h] = cropOf(key, v);
    sctx.putImageData(new ImageData(doll.pixels(variant(key, v), {}), doll.W, doll.H), 0, 0);
    const g = c.getContext("2d");
    g.clearRect(0, 0, w, h);
    g.drawImage(scratch, x, y, w, h, 0, 0, w, h);
  }
  function sizeThumbs() {
    const th = opts.thumbH || 44;
    for (const btn of $$(".st-thumb")) {
      const [, , w, h] = cropOf(btn.dataset.key, btn.dataset.v);
      const s = Math.max(1, Math.round(th / h));
      const c = btn.querySelector("canvas");
      c.style.width = w * s + "px"; c.style.height = h * s + "px";
    }
  }

  // ---------------------------------------------------------- sync
  function sync() {
    $$(".st-tabs [data-tab]").forEach(b => {
      const on = b.dataset.tab === tab;
      b.setAttribute("aria-selected", String(on));
      b.tabIndex = on ? 0 : -1;
    });
    $$(".st-panel").forEach(p => p.classList.toggle("on", p.dataset.tab === tab));
    $$("[data-gender]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.gender === look.gender)));
    $$(".st-thumb").forEach(b => {
      const k = b.dataset.key, v = b.dataset.v;
      b.setAttribute("aria-pressed", String(k === "acc" ? look.acc.includes(v) : look[k] === v));
    });
    $$(`.st-panel[data-tab="${tab}"] .st-thumb`).forEach(paintThumb);
    for (const box of $$(".st-swatches")) {
      const key = box.dataset.color, cur = look[key];
      let matched = false;
      box.querySelectorAll(".st-swatch:not(.st-custom)").forEach(b => {
        const on = b.dataset.v === cur; matched ||= on;
        b.setAttribute("aria-pressed", String(on));
      });
      const custom = box.querySelector(".st-custom");
      custom.classList.toggle("has-color", !matched);
      custom.setAttribute("aria-pressed", String(!matched));
      if (!matched) { custom.style.setProperty("--c", cur); custom.style.setProperty("--c2", doll.rampFrom(cur, key === "skin")[1]); }
      custom.querySelector("input").value = cur;
    }
    const note = $('[data-note="socksNote"]');
    if (note) {
      const bottomName = O.bottom.find(o => o[0] === look.bottomStyle)[1];
      note.textContent = COVERS_SOCKS.includes(look.bottomStyle) ? `现在穿的${bottomName}会盖住袜子，换成短裤或短裙就看得到啦。`
        : look.bottomStyle === "pleated" ? "百褶裙会挡住大半截，长袜只从裙摆缝里露出一点。配短裤或短裙更明显。"
        : "短袜只露出脚踝一圈，长袜一直拉到膝盖。";
    }
    $$(".st-modes [data-mode]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.mode === mode)));
  }

  function change(patch) {
    look = doll.normalize({ ...look, ...patch });
    sync();
    redraw();
    if (opts.onChange) opts.onChange(look);
  }

  // ---------------------------------------------------------- preview stage
  // a slice of the bedroom from the house: plaster wall, white skirting, oak floor
  const SW = 48, SH = 52, STAGE_X = 14, FLOOR_TOP = 41, FEET_Y = 47;
  const off = document.createElement("canvas");
  off.width = SW; off.height = SH;
  const octx = off.getContext("2d");
  function rect(img, x, y, w, h, hex) {
    const [r, g, b] = doll.hexToRgb(hex);
    for (let j = y; j < y + h; j++) for (let i = x; i < x + w; i++) {
      if (i < 0 || j < 0 || i >= SW || j >= SH) continue;
      const p = (j * SW + i) * 4;
      img.data[p] = r * 255; img.data[p + 1] = g * 255; img.data[p + 2] = b * 255; img.data[p + 3] = 255;
    }
  }
  function paintRoom(img) {
    rect(img, 0, 0, SW, FLOOR_TOP, "#ece2d9");
    rect(img, 0, 0, SW, 1, "#cdbfb4");
    rect(img, 0, 1, SW, 1, "#dccfc5");
    rect(img, 0, FLOOR_TOP - 3, SW, 3, "#f4f2ee");
    rect(img, 0, FLOOR_TOP - 1, SW, 1, "#c4c1bc");
    rect(img, 0, FLOOR_TOP, SW, SH - FLOOR_TOP, "#b48a62");
    rect(img, 0, FLOOR_TOP, SW, 1, "#5b4232");
    rect(img, 0, FLOOR_TOP + 1, SW, 1, "#d1ab80");
    for (let r = 0, y = FLOOR_TOP + 2; y < SH; r++, y += 3) {
      rect(img, 0, y + 2, SW, 1, "#8a6446");
      for (let x = (r * 11) % 23; x < SW; x += 23) rect(img, x, y, 1, 2, "#8a6446");
    }
  }
  function paintStage(f) {
    const ramps = doll.rampsOf(look);
    const img = octx.createImageData(SW, SH);
    paintRoom(img);
    const top = FEET_Y - doll.H + 1;
    rect(img, STAGE_X + 5, FEET_Y + 1, 11, 1, "#8a6446");   // contact shadow under the shoes
    const px = doll.pixels(look, f, ramps);
    for (let j = 0; j < doll.H; j++) for (let i = 0; i < doll.W; i++) {
      const s = (j * doll.W + i) * 4;
      if (!px[s + 3]) continue;
      const d = ((top + j) * SW + STAGE_X + i) * 4;
      img.data[d] = px[s]; img.data[d + 1] = px[s + 1]; img.data[d + 2] = px[s + 2]; img.data[d + 3] = 255;
    }
    if (f.emote) {
      const name = f.emote === "cheer" ? doll.cheer(look) : f.emote;
      const e = doll.emotePixels(name, ramps);
      for (let j = 0; j < e.h; j++) for (let i = 0; i < e.w; i++) {
        const s = (j * e.w + i) * 4, x = STAGE_X + 13 + i, y = top - 15 + j;
        if (!e.buf[s + 3] || x >= SW || y < 0) continue;
        const d = (y * SW + x) * 4;
        img.data[d] = e.buf[s]; img.data[d + 1] = e.buf[s + 1]; img.data[d + 2] = e.buf[s + 2]; img.data[d + 3] = 255;
      }
    }
    octx.putImageData(img, 0, 0);
    pctx.imageSmoothingEnabled = false;
    pctx.clearRect(0, 0, preview.width, preview.height);
    pctx.drawImage(off, 0, 0, preview.width, preview.height);
  }
  function sizePreview(scale) {
    preview.width = SW * scale; preview.height = SH * scale;
    preview.style.width = preview.width + "px"; preview.style.height = preview.height + "px";
  }

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const MODE_SEQ = {
    happy: [{ expr: "happy", emote: "note", ms: 700 }, { expr: "happy", bob: 1, sway: 1, emote: "note", ms: 400 }],
    surprised: [{ expr: "surprised", emote: "bang", ms: 900 }, { expr: "surprised", bob: 1, sway: 1, emote: "bang", ms: 300 }],
    sleepy: [{ expr: "sleepy", ms: 900 }, { expr: "sleepy", bob: 1, sway: 1, ms: 700 }],
    flustered: [{ expr: "flustered", ms: 500 }, { expr: "flustered", bob: 1, sway: 1, ms: 250 }, { expr: "flustered", ms: 400 }],
  };
  let timer = null, step = 0, running = false;
  function tick() {
    const seq = mode === "idle" ? DATA.seq : MODE_SEQ[mode];
    const f = { expr: "neutral", look: 0, bob: 0, sway: 0, wave: null, emote: null, ...seq[step % seq.length] };
    paintStage(f);
    if (reduceMotion || !running) return;
    timer = setTimeout(() => { step++; tick(); }, f.ms);
  }
  function redraw() { clearTimeout(timer); tick(); }

  // ---------------------------------------------------------- input
  root.addEventListener("click", e => {
    const b = e.target.closest("button");
    if (!b || !root.contains(b)) return;
    if (b.dataset.tab) { tab = b.dataset.tab; sync(); return; }
    if (b.dataset.mode) { mode = b.dataset.mode; step = 0; sync(); redraw(); return; }
    if (b.dataset.gender) { if (b.dataset.gender !== look.gender) change(pickPreset(b.dataset.gender)); return; }
    if (b.classList.contains("st-thumb")) {
      const k = b.dataset.key, v = b.dataset.v;
      change(k === "acc" ? { acc: doll.toggleAcc(look.acc, v) } : { [k]: v });
      return;
    }
    if (b.classList.contains("st-swatch")) { change({ [b.dataset.color]: b.dataset.v }); return; }
    if (b.classList.contains("st-random")) { change(randomLook()); return; }
    if (b.classList.contains("st-close") && opts.onClose) opts.onClose();
  });
  root.addEventListener("input", e => {
    const inp = e.target.closest("input[type=color]");
    if (inp) change({ [inp.dataset.color]: inp.value });
  });
  root.querySelector(".st-tabs").addEventListener("keydown", e => {   // arrow keys move between tabs
    const i = TABS.findIndex(t => t.id === tab);
    const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
    if (!d) return;
    e.preventDefault();
    tab = TABS[(i + d + TABS.length) % TABS.length].id;
    sync();
    root.querySelector(`[data-tab="${tab}"]`).focus();
  });
  root.addEventListener("keydown", e => { if (e.key === "Escape" && opts.onClose) opts.onClose(); });

  // switching gender puts on that gender's default styles; colors stay
  function pickPreset(g) {
    const p = doll.PRESETS[g];
    return { gender: g, style: p.style, eyes: p.eyes, topStyle: p.topStyle, bottomStyle: p.bottomStyle, socks: p.socks, acc: p.acc };
  }
  const pick = a => a[Math.floor(Math.random() * a.length)];
  function randomLook() {
    const g = pick(["f", "m"]);
    const short = O.style.filter(o => DATA.shortStyles.includes(o[0])), long = O.style.filter(o => !DATA.shortStyles.includes(o[0]));
    const styles = Math.random() < 0.8 ? (g === "m" ? short : long) : O.style;
    const cloth = DATA.swatches.cloth.map(c => c[1].toLowerCase());
    const top = pick(cloth);
    let acc = [];
    for (const [a] of O.acc) if (Math.random() < 0.18) acc = doll.toggleAcc(acc, a);
    const skirts = ["pleated", "maxi"];
    return {
      gender: g, style: pick(styles)[0], eyes: pick(O.eyes)[0], topStyle: pick(O.top)[0],
      bottomStyle: pick(O.bottom.filter(o => g === "f" || !skirts.includes(o[0])))[0], socks: pick(O.socks)[0], acc,
      hair: pick(DATA.swatches.hair)[1].toLowerCase(), skin: pick(DATA.swatches.skin)[1].toLowerCase(),
      top, bottom: pick(cloth.filter(c => c !== top)), sock: pick(cloth), eye: pick(DATA.swatches.eye)[1].toLowerCase(),
    };
  }

  // narrow hosts (phones): stage above the tabs, smaller preview and thumbnails
  let narrow = null;
  function fitWidth() {
    const w = root.clientWidth;
    if (!w || (w < 600) === narrow) return;
    narrow = w < 600;
    root.classList.toggle("narrow", narrow);
    opts.thumbH = narrow ? 34 : wideThumbH;
    sizeThumbs();
    sizePreview(narrow ? (opts.modes ? 3 : 2) : (opts.previewScale || 4));
    redraw();
  }
  const wideThumbH = opts.thumbH || 44;
  if (window.ResizeObserver) new ResizeObserver(fitWidth).observe(root);

  sizeThumbs();
  sizePreview(opts.previewScale || 4);
  sync();
  tick();
  fitWidth();

  return {
    get look() { return look; },
    setLook(l) { look = doll.normalize(l); sync(); redraw(); },
    start() { if (running) return; running = true; step = 0; redraw(); },
    stop() { running = false; clearTimeout(timer); },
    refit() { narrow = null; fitWidth(); },
  };
}
