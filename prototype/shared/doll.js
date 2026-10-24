// ================================================================ Buddy paper doll
// Shared by the dressing room page (prototype/creator) and the house demo
// (prototype/demo); tools/make_creator.py pastes it into both. DATA comes from
// make_creator.doll_data(): role maps per layer key + option tables.
//
// A look is plain data:
//   { name, gender, style, eyes, topStyle, bottomStyle, socks, acc: [..],
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

  // ---------------------------------------------------------- names
  // Up to NAME_MAX characters, no control characters or angle brackets;
  // an empty name falls back to the default.
  const NAME_DEFAULT = "Buddy", NAME_MAX = 8;
  function cleanName(s) {
    const t = String(s ?? "").replace(/[\u0000-\u001f\u007f<>]/g, "").replace(/\s+/g, " ").trim();
    return Array.from(t).slice(0, NAME_MAX).join("").trim();
  }
  // 200 names per gender: nicknames, Chinese, Japanese and Western transliterations.
  const NAME_GROUPS = {
  "f": [
    [
      "小桃",
      "糯米",
      "栗子",
      "小满",
      "阿梨",
      "七七",
      "柚子",
      "年糕",
      "芝麻",
      "汤圆",
      "布丁",
      "小鹿",
      "月月",
      "甜橙",
      "棉花",
      "小樱",
      "小雨",
      "糖糖",
      "小葵",
      "木子",
      "宁宁",
      "小圆",
      "奶糖",
      "杏子",
      "桃酥",
      "小麦",
      "朵朵",
      "贝贝",
      "小夏",
      "橙子",
      "豆沙",
      "小月",
      "阿茶",
      "小雪",
      "泡芙",
      "果果",
      "小芋",
      "椰椰",
      "桃子",
      "小杏",
      "糖糕",
      "泡泡",
      "奶芙",
      "软糖",
      "团子",
      "小椰",
      "小铃",
      "莓莓",
      "小饼",
      "布蕾",
      "花卷",
      "奶泡",
      "橘子",
      "小柚糖",
      "小云朵",
      "阿棉",
      "芋圆"
    ],
    [
      "林知夏",
      "林语桐",
      "林书宁",
      "林晚晴",
      "林予安",
      "林星禾",
      "陈知夏",
      "陈语桐",
      "陈书宁",
      "陈晚晴",
      "陈予安",
      "陈星禾",
      "周知夏",
      "周语桐",
      "周书宁",
      "周晚晴",
      "周予安",
      "周星禾",
      "许知夏",
      "许语桐",
      "许书宁",
      "许晚晴",
      "许予安",
      "许星禾",
      "沈知夏",
      "沈语桐",
      "沈书宁",
      "沈晚晴",
      "沈予安",
      "沈星禾",
      "江知夏",
      "江语桐",
      "江书宁",
      "江晚晴",
      "江予安",
      "江星禾",
      "顾知夏",
      "顾语桐",
      "顾书宁",
      "顾晚晴",
      "顾予安",
      "顾星禾",
      "叶知夏",
      "叶语桐",
      "叶书宁",
      "叶晚晴",
      "叶予安",
      "叶星禾",
      "宋知夏",
      "宋语桐",
      "宋书宁",
      "宋晚晴",
      "宋予安",
      "宋星禾",
      "苏知夏",
      "苏语桐",
      "苏书宁",
      "苏晚晴",
      "苏予安",
      "苏星禾"
    ],
    [
      "佐藤美咲",
      "铃木优奈",
      "高桥千鹤",
      "田中绘里",
      "渡边琴音",
      "伊藤爱",
      "山本纱织",
      "中村真央",
      "小林遥",
      "加藤杏",
      "吉田凛",
      "山田由衣",
      "佐佐木枫",
      "山口葵",
      "松本奈奈",
      "井上诗织",
      "木村玲",
      "林明日香",
      "清水雪乃",
      "山崎惠",
      "森彩夏",
      "池田茜",
      "桥本花音",
      "石川沙纪",
      "中岛咲良",
      "前田理香",
      "藤田美绪",
      "小川奈央",
      "冈田奏",
      "长谷川菫",
      "村上结月",
      "近藤萌",
      "石井穗香"
    ],
    [
      "艾米",
      "艾玛",
      "奥莉维亚",
      "索菲亚",
      "伊莎贝拉",
      "米娅",
      "夏洛特",
      "阿米莉亚",
      "哈珀",
      "伊芙琳",
      "阿比盖尔",
      "艾米莉",
      "伊丽莎白",
      "艾弗里",
      "艾拉",
      "斯嘉丽",
      "格蕾丝",
      "克洛伊",
      "维多利亚",
      "莱莉",
      "阿丽娅",
      "莉莉",
      "埃莉诺",
      "汉娜",
      "诺拉",
      "佐伊",
      "黑兹尔",
      "奥罗拉",
      "萨凡娜",
      "奥黛丽",
      "布鲁克琳",
      "贝拉",
      "克莱尔",
      "露西",
      "安娜",
      "卡罗琳",
      "娜塔莉",
      "爱丽丝",
      "莎拉",
      "伊娃",
      "玛雅",
      "艾琳",
      "娜奥米",
      "露比",
      "艾薇",
      "斯特拉",
      "薇拉",
      "西尔维娅",
      "阿黛尔",
      "罗丝"
    ]
  ],
  "m": [
    [
      "阿布",
      "土豆",
      "小树",
      "石头",
      "包子",
      "阿福",
      "冬瓜",
      "小虎",
      "卷卷",
      "毛毛",
      "大橙",
      "阿柴",
      "豆丁",
      "饭团",
      "小舟",
      "阿星",
      "阿辰",
      "林舟",
      "大可",
      "小野",
      "阿川",
      "小松",
      "阿森",
      "小北",
      "阿哲",
      "阿远",
      "小岩",
      "南瓜",
      "阿吉",
      "小谷",
      "山竹",
      "阿木",
      "小河",
      "阿朗",
      "阿洛",
      "小柏",
      "阿良",
      "小原",
      "阿青",
      "阿灿",
      "豆包",
      "小麦",
      "阿乐",
      "饼干",
      "阿圆",
      "毛豆",
      "小可",
      "栗栗",
      "小熊",
      "汤圆",
      "阿冬",
      "可乐",
      "小豆",
      "阿栗",
      "大福",
      "阿团",
      "小年糕"
    ],
    [
      "林知远",
      "林景行",
      "林亦辰",
      "林予川",
      "林明轩",
      "林书衡",
      "陈知远",
      "陈景行",
      "陈亦辰",
      "陈予川",
      "陈明轩",
      "陈书衡",
      "周知远",
      "周景行",
      "周亦辰",
      "周予川",
      "周明轩",
      "周书衡",
      "许知远",
      "许景行",
      "许亦辰",
      "许予川",
      "许明轩",
      "许书衡",
      "沈知远",
      "沈景行",
      "沈亦辰",
      "沈予川",
      "沈明轩",
      "沈书衡",
      "江知远",
      "江景行",
      "江亦辰",
      "江予川",
      "江明轩",
      "江书衡",
      "顾知远",
      "顾景行",
      "顾亦辰",
      "顾予川",
      "顾明轩",
      "顾书衡",
      "叶知远",
      "叶景行",
      "叶亦辰",
      "叶予川",
      "叶明轩",
      "叶书衡",
      "宋知远",
      "宋景行",
      "宋亦辰",
      "宋予川",
      "宋明轩",
      "宋书衡",
      "苏知远",
      "苏景行",
      "苏亦辰",
      "苏予川",
      "苏明轩",
      "苏书衡"
    ],
    [
      "佐藤健",
      "铃木大辅",
      "高桥悠真",
      "田中直树",
      "渡边翔",
      "伊藤隼人",
      "山本诚",
      "中村武",
      "小林拓海",
      "加藤润",
      "吉田雄介",
      "山田律",
      "佐佐木亮",
      "山口和也",
      "松本勇",
      "井上哲",
      "木村光",
      "林一郎",
      "清水莲",
      "山崎阳介",
      "森龙二",
      "池田宽",
      "桥本启",
      "石川聪",
      "中岛司",
      "前田正人",
      "藤田悠斗",
      "小川航",
      "冈田博",
      "长谷川彻",
      "村上修",
      "近藤彰",
      "石井谦"
    ],
    [
      "查尔斯",
      "亚瑟",
      "奥利弗",
      "诺亚",
      "利亚姆",
      "伊桑",
      "詹姆斯",
      "本杰明",
      "卢卡斯",
      "梅森",
      "亚历山大",
      "亨利",
      "杰克逊",
      "塞巴斯蒂安",
      "艾登",
      "马修",
      "塞缪尔",
      "大卫",
      "约瑟夫",
      "卡特",
      "欧文",
      "怀亚特",
      "约翰",
      "杰克",
      "卢克",
      "杰登",
      "迪伦",
      "格雷森",
      "莱维",
      "艾萨克",
      "加布里埃尔",
      "朱利安",
      "马特奥",
      "安东尼",
      "里奥",
      "林肯",
      "约书亚",
      "克里斯托弗",
      "安德鲁",
      "西奥多",
      "卡莱布",
      "瑞安",
      "阿舍",
      "内森",
      "托马斯",
      "里昂",
      "阿德里安",
      "埃里克",
      "马丁",
      "维克托"
    ]
  ]
};
  const NAMES = {f:NAME_GROUPS.f.flat(),m:NAME_GROUPS.m.flat()};
  function randomName(gender, not) {
    const pool = NAMES[gender === "m" ? "m" : "f"].filter(n => n !== not);
    return pool[Math.floor(Math.random() * pool.length)];
  }
  const pronoun = look => (look && look.gender === "m" ? "他" : "她");
  function normalize(l) {   // fill gaps / drop unknown values (old saves, hand edits)
    const p = PRESETS[l && l.gender === "m" ? "m" : "f"], o = DATA.options;
    const out = { ...p, ...(l || {}) };
    out.name = cleanName(out.name) || NAME_DEFAULT;
    if (!has(o.style, out.style)) out.style = p.style;
    if (!has(o.eyes, out.eyes)) out.eyes = p.eyes;
    if (!has(o.top, out.topStyle)) out.topStyle = p.topStyle;
    if (!has(o.bottom, out.bottomStyle)) out.bottomStyle = p.bottomStyle;
    if (!has(o.socks, out.socks)) out.socks = p.socks;
    out.acc = [];
    for(const a of Array.isArray(l?.acc)?l.acc:p.acc){if(!has(o.acc,a)||out.acc.includes(a))continue;out.acc=toggleAcc(out.acc,a);}
    for (const r of ROLES) if (!/^#[0-9a-f]{6}$/i.test(out[r] || "")) out[r] = p[r];
    for (const r of ROLES) out[r] = out[r].toLowerCase();
    return out;
  }
  // Wear / take off an accessory. Only one pair of eyewear at a time.
  function toggleAcc(list, a) {
    if (list.includes(a)) return list.filter(x => x !== a);
    const ew = DATA.eyewear;
    return [...list.filter(x => !(ew.includes(a) && ew.includes(x)) && !((DATA.hats||[]).includes(a) && DATA.hats.includes(x))), a];
  }

  // ---------------------------------------------------------- layers
  function layerKeys(look, f) {
    const arm = f.wave !== null && f.wave !== undefined;
    const acc = new Set(look.acc);
    const keys = [];
    const add = k => { if (DATA.layers[k]) keys.push(k); };
    const pose = DATA.pose[look.bottomStyle];
    const hat = DATA.hats.some(a => acc.has(a)) ? 1 : 0;      // hair above the beanie's cuff is clipped away
    add(`back/${look.style}/${f.bob}/${f.sway % 2}/${hat}`);
    add(`base/${arm ? 1 : 0}`);
    if (look.socks !== "none") add(`socks/${look.socks}`);
    add(`shoes/${pose.shoes}`);
    add(`bottom/${look.bottomStyle}`);
    add(`top/${look.topStyle}/${arm ? 1 : 0}`);
    add(`bib/${look.bottomStyle}`);
    if (acc.has("scarf")) add("acc/scarf/0");
    add(`head/${look.style}/${f.bob}/${hat}`);
    if (!hat) add(`ahoge/${look.style}/${f.sway % 2}/${f.bob}`);
    const eyes = f.expr === "neutral" ? look.eyes : "-";
    const brows = look.gender === "m" && DATA.eyewear.some(a => acc.has(a)) ? 1 : 0;
    add(`face/${look.gender}/${eyes}/${f.expr}/${f.look}/${f.bob}/${brows}`);
    for (const a of DATA.headAcc) {
      if (!acc.has(a)) continue;
      // the headphone band is fitted to the hairstyle's outline (or the hat's)
      add(a === "headphones" ? `acc/headphones/${hat ? "hat" : look.style}/${f.bob}` : `acc/${a}/${f.bob}`);
    }
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
  function sitPixels(buf, look, ramps = rampsOf(look)) {
    const out = new Uint8ClampedArray(buf.length);
    out.set(buf.subarray(0, DW * 22 * 4), DW * 2 * 4);
    paintLayer(out, DW, DH, DATA.layers[`pose/sit/${look.bottomStyle}/${look.socks}`], 0, 0, ramps);
    return out;
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

  // ---------------------------------------------------------- back view
  // Buddy seen from behind (climbing the stairs): the same layers without the
  // face, eyewear or a raised arm. The face's skin turns into the back of the
  // head (ears and the nape stay skin), prints on the top become plain cloth,
  // and long hair hangs in front of the head and shoulders instead of behind.
  const tokenOf = {};                       // "role/shade" -> the token that paints it
  for (const [t, c] of Object.entries(DATA.colors)) if (typeof c !== "string") tokenOf[c.join("/")] = t;
  const SKIN_TO_HAIR = [0, 2, 2, 2];        // skin shade -> hair shade
  const backCache = new Map();
  function backLayer(k, bob) {
    const key = k + "|" + bob;
    if (backCache.has(key)) return backCache.get(key);
    const L = DATA.layers[k];
    const swap = (row, fn) => [...row].map((t, i) => (t === "." ? t : fn(DATA.colors[t], i) || t)).join("");
    let out = L;
    if (k.startsWith("head/")) {
      const y0 = L.y || 0;
      out = { ...L, rows: L.rows.map((row, j) => y0 + j >= 14 + bob ? row
        : swap(row, (c, i) => c[0] === "skin" && i > 2 && i < DW - 3 && tokenOf["hair/" + SKIN_TO_HAIR[c[1]]])) };
    } else if (k.startsWith("back/")) {
      // hair that hung behind her is now the surface we look at: mid shade,
      // a few darker strands below the crown, dark outline kept on the edge
      const y0 = L.y || 0, at = (x, y) => (L.rows[y] && L.rows[y][x]) || ".";
      out = { ...L, rows: L.rows.map((row, j) => swap(row, (c, i) => {
        if (c[0] !== "hair") return null;
        // (a top edge that starts below the crown lies on the head: no seam there)
        const dirs = y0 + j > 4 + bob ? [[1, 0], [-1, 0], [0, 1]] : [[1, 0], [-1, 0], [0, 1], [0, -1]];
        if (dirs.some(([dx, dy]) => at(i + dx, j + dy) === ".")) return c[1] === 0 ? null : tokenOf["hair/1"];
        return tokenOf["hair/" + (y0 + j > 12 + bob && i % 4 === 1 ? 1 : 2)];
      })) };
    } else if (k.startsWith("top/")) {
      out = { ...L, rows: L.rows.map(row => swap(row, c => typeof c === "string" && tokenOf["top/2"])) };
    }
    backCache.set(key, out);
    return out;
  }
  function backKeys(look, f) {
    const eyewear = DATA.eyewear.map(a => `acc/${a}/`);
    const keys = layerKeys(look, { ...f, wave: null, expr: "neutral" })
      .filter(k => !k.startsWith("face/") && !eyewear.some(e => k.startsWith(e)));
    const hair = keys.filter(k => k.startsWith("back/")), rest = keys.filter(k => !k.startsWith("back/"));
    let at = rest.findIndex(k => k.startsWith("head/")) + 1;
    if (rest[at] && rest[at].startsWith("ahoge/")) at++;
    rest.splice(at, 0, ...hair);
    return rest;
  }
  function pixelsBack(look, f, ramps = rampsOf(look)) {
    const buf = new Uint8ClampedArray(DW * DH * 4);
    const fr = { ...FRAME, ...f };
    for (const k of backKeys(look, fr)) paintLayer(buf, DW, DH, backLayer(k, fr.bob), 0, 0, ramps);
    return buf;
  }

  return { W: DW, H: DH, ROLES, PRESETS, NAME_DEFAULT, NAME_MAX, cleanName, randomName, NAMES, NAME_GROUPS, pronoun, rampFrom, rampsOf, normalize, toggleAcc, layerKeys, paintLayer,
           pixels, pixelsBack, sitPixels, emotePixels, toCanvas, hexToRgb, cheer };
}
