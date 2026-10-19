// ================================================================ Buddy paper doll
// Shared by the dressing room page (prototype/creator) and the house demo
// (prototype/demo); tools/make_creator.py pastes it into both. DATA comes from
// make_creator.doll_data(): role maps per layer key + option tables.
//
// A look is plain data:
//   { gender, style, eyes, topStyle, bottomStyle, socks, acc: [..],
//     hair, skin, top, bottom, sock, eye }        <- the last six are colors
// layerKeys() must build the same keys as Doll.layers() in art/src/concept/doll.py.
function BuddyDoll(DATA) {
  const ROLES = ["hair", "skin", "top", "bottom", "eye", "sock"];
  const DW = DATA.W, DH = DATA.H;

  // ---------------------------------------------------------- color ramps
  // Mirror of tools/pixelkit/palette.py ramp_from(): one picked color -> 5 shades,
  // shadows drift cool (skin: toward red), highlights drift warm.
  function hexToRgb(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255]; }
  function rgbToHex(r, g, b) { return "#" + [r, g, b].map(v => Math.round(v * 255).toString(16).padStart(2, "0")).join(""); }
  function rgbToHsv(r, g, b) {
    const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
    let h = 0;
    if (d) { if (max === r) h = ((g - b) / d) % 6; else if (max === g) h = (b - r) / d + 2; else h = (r - g) / d + 4; h *= 60; if (h < 0) h += 360; }
    return [h, max ? d / max : 0, max];
  }
  function hsvToRgb(h, s, v) {
    const c = v * s, x = c * (1 - Math.abs((h / 60) % 2 - 1)), m = v - c;
    const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
    return [r + m, g + m, b + m];
  }
  function toward(h, t, a) { const d = (((t - h + 180) % 360) + 360) % 360 - 180; return (h + Math.max(-a, Math.min(a, d)) + 360) % 360; }
  const rampCache = new Map();
  function rampFrom(base, skin = false) {
    const key = base + (skin ? "s" : "c");
    if (rampCache.has(key)) return rampCache.get(key);
    const R = DATA.ramp, steps = skin ? R.skin : R.cloth, sh = skin ? R.skinShadowHue : R.shadowHue;
    const [h, s, v] = rgbToHsv(...hexToRgb(base));
    const out = steps.map(([dv, fs, dh]) => {
      let hh = h, ss = s, vv = v;
      if (dv < 0) { hh = toward(h, sh, dh); ss = Math.min(1, s * fs + 0.06); vv = v * (1 + dv); }
      else if (dv > 0) { hh = toward(h, R.lightHue, dh); ss = s * fs; vv = Math.min(1, v + (1 - v) * dv * (0.4 + 0.6 * v)); }
      return rgbToHex(...hsvToRgb(hh, ss, vv));
    });
    rampCache.set(key, out);
    return out;
  }
  function rampsOf(look) {
    const r = {};
    for (const role of ROLES) r[role] = rampFrom(look[role], role === "skin");
    return r;
  }

  // ---------------------------------------------------------- looks
  const PRESETS = {
    f: { gender: "f", style: "long", eyes: "round", topStyle: "sweater", bottomStyle: "pleated", socks: "short", acc: ["bow"],
         hair: "#433a54", skin: "#f6c39c", top: "#b94b4b", bottom: "#46619e", sock: "#e8e6ef", eye: "#46619e" },
    m: { gender: "m", style: "messy", eyes: "bean", topStyle: "jacket", bottomStyle: "jeans", socks: "short", acc: [],
         hair: "#7c4734", skin: "#f6c39c", top: "#447840", bottom: "#46619e", sock: "#e8e6ef", eye: "#7c4734" },
  };
  const has = (list, v) => list.some(o => o[0] === v);
  function normalize(l) {   // fill gaps / drop unknown values (old saves, hand edits)
    const p = PRESETS[l && l.gender === "m" ? "m" : "f"], o = DATA.options;
    const out = { ...p, ...(l || {}) };
    if (!has(o.style, out.style)) out.style = p.style;
    if (!has(o.eyes, out.eyes)) out.eyes = p.eyes;
    if (!has(o.top, out.topStyle)) out.topStyle = p.topStyle;
    if (!has(o.bottom, out.bottomStyle)) out.bottomStyle = p.bottomStyle;
    if (!has(o.socks, out.socks)) out.socks = p.socks;
    out.acc = Array.isArray(out.acc) ? out.acc.filter(a => has(o.acc, a)) : [];
    for (const r of ROLES) if (!/^#[0-9a-f]{6}$/i.test(out[r] || "")) out[r] = p[r];
    for (const r of ROLES) out[r] = out[r].toLowerCase();
    return out;
  }
  // Wear / take off an accessory. Only one pair of eyewear at a time.
  function toggleAcc(list, a) {
    if (list.includes(a)) return list.filter(x => x !== a);
    const ew = DATA.eyewear;
    return [...list.filter(x => !(ew.includes(a) && ew.includes(x))), a];
  }

  // ---------------------------------------------------------- layers
  function layerKeys(look, f) {
    const arm = f.wave !== null && f.wave !== undefined;
    const acc = new Set(look.acc);
    const keys = [];
    const add = k => { if (DATA.layers[k]) keys.push(k); };
    const pose = DATA.pose[look.bottomStyle];
    add(`back/${look.style}/${f.bob}/${f.sway % 2}`);
    add(`base/${arm ? 1 : 0}`);
    if (look.socks !== "none") add(`socks/${look.socks}`);
    add(`shoes/${pose.shoes}`);
    add(`bottom/${look.bottomStyle}`);
    add(`top/${look.topStyle}/${arm ? 1 : 0}`);
    add(`bib/${look.bottomStyle}`);
    if (acc.has("scarf")) add("acc/scarf/0");
    add(`head/${look.style}/${f.bob}`);
    if (!acc.has("beanie")) add(`ahoge/${look.style}/${f.sway % 2}/${f.bob}`);
    const eyes = f.expr === "neutral" ? look.eyes : "-";
    const brows = look.gender === "m" && DATA.eyewear.some(a => acc.has(a)) ? 1 : 0;
    add(`face/${look.gender}/${eyes}/${f.expr}/${f.look}/${f.bob}/${brows}`);
    for (const a of DATA.headAcc) if (acc.has(a)) add(`acc/${a}/${f.bob}`);
    if (arm) add(`arm/${DATA.sleeves[look.topStyle]}/${f.wave}`);
    return keys;
  }

  const rgbCache = new Map();
  function rgb255(hex) {
    let v = rgbCache.get(hex);
    if (!v) { v = hexToRgb(hex).map(c => Math.round(c * 255)); rgbCache.set(hex, v); }
    return v;
  }
  // Paint one role map into an RGBA buffer (w x h) at (ox, oy).
  function paintLayer(buf, w, h, layer, ox, oy, ramps) {
    if (!layer) return;
    const y0 = layer.y || 0;
    layer.rows.forEach((row, j) => {
      for (let i = 0; i < row.length; i++) {
        const t = row[i];
        if (t === ".") continue;
        const c = DATA.colors[t];
        const hex = typeof c === "string" ? c : ramps[c[0]][c[1]];
        const x = ox + i, y = oy + y0 + j;
        if (x < 0 || y < 0 || x >= w || y >= h) continue;
        const [r, g, b] = rgb255(hex), p = (y * w + x) * 4;
        buf[p] = r; buf[p + 1] = g; buf[p + 2] = b; buf[p + 3] = 255;
      }
    });
  }
  const FRAME = { expr: "neutral", look: 0, bob: 0, sway: 0, wave: null };
  // Buddy's 20x28 RGBA pixels for a look and an animation frame.
  function pixels(look, f, ramps = rampsOf(look)) {
    const buf = new Uint8ClampedArray(DW * DH * 4);
    const fr = { ...FRAME, ...f };
    for (const k of layerKeys(look, fr)) paintLayer(buf, DW, DH, DATA.layers[k], 0, 0, ramps);
    return buf;
  }
  function emotePixels(name, ramps) {
    const L = DATA.layers["emote/" + name];
    const buf = new Uint8ClampedArray(L.w * L.h * 4);
    paintLayer(buf, L.w, L.h, L, 0, 0, ramps);
    return { buf, w: L.w, h: L.h };
  }
  function toCanvas(buf, w, h, rows = h) {
    const c = document.createElement("canvas");
    c.width = w; c.height = rows;
    c.getContext("2d").putImageData(new ImageData(buf.slice(0, w * rows * 4), w, rows), 0, 0);
    return c;
  }
  const cheer = look => (look.gender === "f" ? "heart" : "star");

  return { W: DW, H: DH, ROLES, PRESETS, rampFrom, rampsOf, normalize, toggleAcc, layerKeys, paintLayer,
           pixels, emotePixels, toCanvas, hexToRgb, cheer };
}
