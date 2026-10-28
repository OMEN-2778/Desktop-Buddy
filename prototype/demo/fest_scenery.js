// ================================================================ festival dressing for the front yard, the dock and the mall
// User: the festivals felt bare outside the park, and not every festival should mean more stalls.
// Each festival dresses each place its own way: strings across the top (pennants, lanterns, hearts,
// bulbs, little flags, envelopes...), things hung on the door or the dock railing, lanterns drifting
// on the sea, kites / paper planes / petals / confetti / bubbles in the air, and fireworks at night.
// Everything moves with realClock alone (no saved state). Drawn before the night grade; whatever
// glows (lanterns, bulbs, fireworks) gets a second pass after it.
const SCENERY = {
  春节: { front: [["string", "lantern", 22], ["doorLanterns"], ["couplets"], ["bits", ["#d8383a", "#f2b33d"]], ["fireworks"]],
          beach: [["rail", "lantern"], ["string", "pennant", 9, ["#d8383a", "#f2b33d"]], ["fireworks"]],
          mall: [["ceil", "lantern"], ["ceil", "fu", 30]], park: [["fireworks"]] },
  元宵节: { front: [["doorLanterns"], ["string", "lantern", 20], ["skyLanterns"]], beach: [["water", "lotus"], ["skyLanterns"], ["rail", "lantern"]], mall: [["ceil", "riddle"]] },
  端午节: { front: [["door", "mugwort"], ["string", "pennant", 9, ["#e1725b", "#6ba14c", "#efc452", "#4f9fd0"]]], beach: [["rail", "flag"]], mall: [["ceil", "zongzi"]] },
  中秋节: { front: [["stoop", "rabbit"], ["string", "osmanthus", 9]], beach: [["water", "lotus"], ["moonPath"], ["rail", "lantern"]], mall: [["ceil", "lantern"], ["ceil", "osmanthus", 20]] },
  七夕: { front: [["string", "heart", 11]], beach: [["rail", "heartBulb"], ["string", "heart", 11]], mall: [["ceil", "heart"]] },
  怪兽夜: { front: [["stoop", "pumpkin"], ["cobwebs"], ["bats"]], beach: [["string", "ghost", 12], ["bats"]], mall: [["ceil", "ghost"]] },
  甜品节: { front: [["string", "pennant", 9, ["#f5c3d4", "#fae59c", "#a9d6bd", "#dccbf2"]]], beach: [["string", "candy", 9]], mall: [["ceil", "candy"]] },
  读书日: { front: [["planes"], ["string", "pennant", 9, ["#4f9f97", "#f3ede3", "#e1725b"]]], beach: [["planes"]], mall: [["ceil", "book"]] },
  跳舞日: { front: [["string", "bulb", 8]], beach: [["string", "bulb", 8], ["notes"]], mall: [["ceil", "discoBall"]] },
  春分: { front: [["kites"], ["petals"]], beach: [["kites"]], mall: [["ceil", "flower"]], park: [["kites"], ["petals"]] },
  写信日: { front: [["planes"], ["string", "envelope", 12]], beach: [["planes"]], mall: [["ceil", "envelope"]] },
  彩票日: { front: [["confetti"], ["string", "pennant", 9, ["#efc452", "#e1725b", "#f7f6fb"]]], beach: [["confetti"]], mall: [["ceil", "pennant"], ["confetti"]] },
  大扫除日: { front: [["bubbles"]], beach: [["bubbles"]], mall: [["bubbles"]] },
  马拉松日: { beach: [["string", "pennant", 9, ["#33303f", "#f7f6fb"]]], mall: [["ceil", "pennant"]] },
  冬至: { front: [["doorLanterns"]], beach: [["rail", "lantern"]], mall: [["ceil", "snowflake"]] },
  雪人日: { front: [["string", "snowflake", 10]], beach: [["string", "snowflake", 10]], mall: [["ceil", "snowflake"]] },
};
const sceneryHere = () => !stormOutside() && SCENERY[festName()]?.[sim.place];
const SC_TOP = { front: 9, beach: 2, park: 2 };
const scH = (i, k = 0) => hash(i * 12.9898 + k * 78.233);
function scPx(ctx, c, x, y, w = 1, h = 1) { ctx.fillStyle = c; ctx.fillRect(Math.round(x), Math.round(y), w, h); }

// ---- one hanging thing, drawn at (x, y) = where its string ends
function scHang(ctx, kind, x, y, k, colors) {
  const sw = Math.round(Math.sin(realClock * 1.2 + x * 0.3) * 0.6);
  x += sw;
  switch (kind) {
    case "pennant": { const c = colors[k % colors.length]; for (let r = 0; r < 6; r++) scPx(ctx, c, x - 3 + (r >> 1), y + 1 + r, 7 - (r >> 1) * 2); scPx(ctx, "rgba(255,255,255,.35)", x - 3, y + 1, 7); break; }
    case "lantern": ctx.drawImage(festImg(DECO.lantern), x - 3, y + 1); break;
    case "riddle": ctx.drawImage(festImg(DECO.lantern), x - 3, y + 1); scPx(ctx, "#f7f1de", x - 1, y + 11, 3, 5); scPx(ctx, "#b5a98c", x, y + 12, 1, 3); break;
    case "heart": { const c = k % 2 ? "#f28fb0" : "#e1525b"; scPx(ctx, c, x - 3, y + 1, 3); scPx(ctx, c, x + 1, y + 1, 3); scPx(ctx, c, x - 4, y + 2, 9, 2); scPx(ctx, c, x - 3, y + 4, 7); scPx(ctx, c, x - 2, y + 5, 5); scPx(ctx, c, x - 1, y + 6, 3); scPx(ctx, c, x, y + 7); scPx(ctx, "#ffd9e4", x - 2, y + 2); break; }
    case "bulb": case "heartBulb": scPx(ctx, "#5e5b71", x, y + 1); scPx(ctx, ["#ffd36b", "#ff7fa8", "#7fd6ff", "#a8f08a", "#c9a0ff"][k % 5], x - 1, y + 2, 3, 2); break;
    case "osmanthus": scPx(ctx, "#6b8f4e", x - 2, y + 1, 5, 2); for (const [dx, dy] of [[-2, 3], [0, 3], [2, 3], [-1, 4], [1, 4], [-2, 5], [0, 5], [2, 5], [0, 6]]) scPx(ctx, (dx + dy) % 2 ? "#f6c64a" : "#ffde7a", x + dx, y + dy, 2, 1); break;
    case "ghost": ctx.drawImage(festImg(DECO.ghost), x - 4, y + 1); break;
    case "candy": { const c = ["#f58fb0", "#7fd0c0", "#f6c64a"][k % 3]; scPx(ctx, "#f7f6fb", x, y + 1, 1, 4); scPx(ctx, c, x - 2, y + 5, 5, 4); scPx(ctx, "#ffffff", x - 1, y + 6); break; }
    case "envelope": scPx(ctx, "#f7f1de", x - 4, y + 1, 9, 6); scPx(ctx, "#e1725b", x, y + 4, 1, 1); scPx(ctx, "#c9b994", x - 2, y + 2, 1); scPx(ctx, "#c9b994", x + 2, y + 2); scPx(ctx, "#c9b994", x - 1, y + 3, 3); scPx(ctx, k % 2 ? "#e1725b" : "#4f9fd0", x - 1, y + 4, 2); break;
    case "snowflake": { const c = "#f4f8ff"; scPx(ctx, c, x, y + 1, 1, 5); scPx(ctx, c, x - 2, y + 3, 5); scPx(ctx, c, x - 1, y + 2); scPx(ctx, c, x + 1, y + 4); scPx(ctx, c, x + 1, y + 2); scPx(ctx, c, x - 1, y + 4); break; }
    case "zongzi": scPx(ctx, "#6ba14c", x - 2, y + 2, 5, 1); scPx(ctx, "#6ba14c", x - 2, y + 3, 4, 1); scPx(ctx, "#5c8a3e", x - 1, y + 4, 3, 1); scPx(ctx, "#5c8a3e", x - 1, y + 5, 2, 1); scPx(ctx, "#c9a46a", x - 2, y + 3, 1, 1); break;
    case "book": { const c = ["#e1725b", "#4f9f97", "#efc452", "#8b7bd1"][k % 4]; scPx(ctx, c, x - 2, y + 1, 5, 6); scPx(ctx, "#f3ede3", x + 2, y + 2, 1, 4); break; }
    case "discoBall": scPx(ctx, "#5e5b71", x, y + 1, 1, 3); scPx(ctx, "#d7dbe6", x - 2, y + 4, 5, 5); scPx(ctx, "#ffffff", x - 1, y + 5); scPx(ctx, "#9aa0b4", x + 1, y + 7, 1, 1); break;
    case "flower": { const c = ["#f5c3d4", "#fae59c", "#dccbf2", "#a9d6bd"][k % 4]; scPx(ctx, c, x - 1, y + 1, 3); scPx(ctx, c, x - 2, y + 2, 5); scPx(ctx, c, x - 1, y + 3, 3); scPx(ctx, "#f2b33d", x, y + 2); break; }
    case "fu": scPx(ctx, "#5e5b71", x, y + 1, 1, 2); for (let r = 0; r < 7; r++) { const w = r < 4 ? r * 2 + 1 : (6 - r) * 2 + 1; scPx(ctx, "#d8383a", x - (w >> 1), y + 3 + r, w); } scPx(ctx, "#f2b33d", x - 1, y + 5, 3, 3); scPx(ctx, "#d8383a", x, y + 6); break;
  }
}

// ---- strings across the top of the view
function scString(ctx, kind, every, colors, top, x0 = -8, x1 = W + 8) {
  drawString(ctx, x0, x1, top, 7, every, (x, y) => scHang(ctx, kind, x, y, (x / every) | 0, colors || []));
}

// ---- night glow for what lights up
function scGlowString(ctx, kind, every, top, f) {
  if (!["lantern", "riddle", "bulb", "heartBulb"].includes(kind)) return;
  drawString(ctx, -8, W + 8, top, 7, every, (x, y) => {
    const bulb = kind === "bulb" || kind === "heartBulb", c = bulb ? ["255, 211, 107", "255, 127, 168", "127, 214, 255", "168, 240, 138", "201, 160, 255"][((x / every) | 0) % 5] : "255, 150, 90";
    decoGlow(ctx, x, y + (bulb ? 3 : 6), bulb ? 5 : 9, c, (bulb ? 0.5 + 0.2 * Math.sin(realClock * 3 + x) : 0.45) * f);
  });
}

// ---- the dock railing: things on the posts
const RAIL = () => ({ y: OUT.beach.deck - 13, xs: Array.from({ length: 9 }, (_, i) => 18 + i * 38) });
function scRail(ctx, kind) {
  const R = RAIL();
  R.xs.forEach((x, i) => {
    if (kind === "flag") {                               // a little pole with a fluttering flag
      scPx(ctx, "#6b5a4a", x, R.y - 16, 1, 17);
      const c = ["#e1725b", "#6ba14c", "#efc452", "#4f9fd0", "#c9a0ff"][i % 5], fl = Math.floor(realClock * 4 + i) % 2;
      for (let r = 0; r < 5; r++) scPx(ctx, c, x + 1, R.y - 16 + r, 6 - Math.abs(r - 2) - fl);
    } else scHang(ctx, kind === "heartBulb" ? "heart" : kind, x, R.y - 8, i, []);
  });
  if (kind === "heartBulb") drawString(ctx, 0, W, R.y - 3, 2, 9, (x, y) => scHang(ctx, "bulb", x, y, (x / 9) | 0, []));
}
function scRailGlow(ctx, kind, f) {
  const R = RAIL();
  if (kind === "lantern") R.xs.forEach(x => decoGlow(ctx, x, R.y - 2, 9, "255, 150, 90", 0.5 * f));
  if (kind === "heartBulb") drawString(ctx, 0, W, R.y - 3, 2, 9, (x, y) => decoGlow(ctx, x, y + 3, 5, "255, 140, 180", 0.5 * f));
}

// ---- lanterns drifting on the sea
function scWater(ctx, f) {
  const B = OUT.beach, y0 = B.horizon + 6, y1 = B.deck - 16;
  for (let i = 0; i < 9; i++) {
    const y = Math.round(y0 + scH(i, 1) * (y1 - y0)), x = ((scH(i, 2) * (W + 40) + realClock * (2 + scH(i, 3) * 2)) % (W + 40)) - 20, bob = Math.round(Math.sin(realClock * 1.4 + i) * 0.6);
    scPx(ctx, "#f2a7b8", x - 2, y + bob, 5, 1); scPx(ctx, "#e46e8a", x - 3, y + 1 + bob, 7, 1); scPx(ctx, "#ffd36b", x, y - 1 + bob);
    if (f > 0.1) { decoGlow(ctx, x, y + bob, 6, "255, 190, 110", 0.5 * f); scPx(ctx, `rgba(255, 200, 120, ${(0.35 * f).toFixed(2)})`, x - 1, y + 3 + bob, 3, 1); }
  }
}
function scMoonPath(ctx, f) {                            // the full moon's road of light on the sea
  if (f < 0.3) return;
  const B = OUT.beach, cx = W * 0.62;
  for (let y = B.horizon + 3; y < B.deck - 12; y += 2) {
    const w = 2 + (y - B.horizon) * 0.25, j = Math.sin(realClock * 2 + y) * 1.5;
    ctx.fillStyle = `rgba(255, 236, 170, ${(0.35 * f).toFixed(2)})`; ctx.fillRect(Math.round(cx - w / 2 + j), y, Math.round(w), 1);
  }
}

// ---- the front door and the stoop (D.outside.front.door = [x, y, w, h])
function scDoor(ctx, kind) {
  const [x, y, w, h] = OUT.front.door;
  if (kind === "doorLanterns") for (const lx of [x - 5, x + w + 5]) { scPx(ctx, "#5e5b71", lx, y - 2, 1, 4); ctx.drawImage(festImg(DECO.lantern), lx - 3, y + 2); }
  if (kind === "couplets") {                             // red couplets either side, a banner across the top, 福 on the door
    for (const cx of [x - 4, x + w + 1]) { scPx(ctx, "#c8312f", cx, y + 6, 3, 30); for (let k = 0; k < 6; k++) scPx(ctx, "#f2b33d", cx + 1, y + 9 + k * 5); }
    scPx(ctx, "#c8312f", x + 2, y - 4, w - 4, 3); for (let k = 0; k < 4; k++) scPx(ctx, "#f2b33d", x + 5 + k * ((w - 10) / 3), y - 3);
    scHang(ctx, "fu", x + w / 2, y + 8, 0);
  }
  if (kind === "mugwort") for (const cx of [x - 5, x + w + 4]) { scPx(ctx, "#d8383a", cx - 2, y + 4, 5, 2); for (let k = 0; k < 16; k++) scPx(ctx, k % 2 ? "#6ba14c" : "#557f3c", cx - 2 + (k % 5), y + 6 + (k >> 1), 1, 3); }
}
function scStoop(ctx, kind) {
  const [x, y, w, h] = OUT.front.door, gy = y + h;
  if (kind === "pumpkin") for (const [px, py] of [[x - 14, gy - 10], [x - 24, gy - 10], [x - 19, gy - 19], [x + w + 3, gy - 10], [x + w + 14, gy - 10]]) ctx.drawImage(festImg(DECO.pumpkin[0]), px, py);
  if (kind === "rabbit") {                               // a white rabbit lantern by the door
    for (const [px, d] of [[x + w + 6, 1], [x - 18, -1]]) {
      scPx(ctx, "#f7f6fb", px, gy - 10, 12, 8); scPx(ctx, "#f7f6fb", px + 1, gy - 11, 10, 1); scPx(ctx, "#f7f6fb", px + (d > 0 ? 8 : 2), gy - 17, 2, 7); scPx(ctx, "#f7f6fb", px + (d > 0 ? 5 : 5), gy - 16, 2, 6);
      scPx(ctx, "#f2b6c8", px + (d > 0 ? 8 : 2), gy - 15, 1, 4); scPx(ctx, "#e1725b", px + (d > 0 ? 9 : 2), gy - 8, 1, 1); scPx(ctx, "#c8c4d6", px, gy - 3, 12, 1); scPx(ctx, "#5e8f4e", px + 1, gy - 2, 10, 1);
    }
  }
}
function scStoopGlow(ctx, kind, f) {
  const [x, y, w, h] = OUT.front.door, gy = y + h;
  if (kind === "pumpkin") for (const px of [x - 14, x - 24, x + w + 3, x + w + 14]) decoGlow(ctx, px + 6, gy - 5, 10, "255, 170, 70", (0.3 + 0.08 * Math.sin(realClock * 9 + px)) * f);
  if (kind === "rabbit") for (const px of [x + w + 12, x - 12]) decoGlow(ctx, px, gy - 6, 12, "255, 220, 160", 0.5 * f);
}
function scCobwebs(ctx) {                                // cobwebs in the corners of the front windows
  const [x, y, w] = OUT.front.door;
  for (const [cx, cy, d] of [[x - 30, y + 2, 1], [x + w + 30, y + 2, -1]]) {
    ctx.fillStyle = "rgba(240, 240, 248, .7)";
    for (let i = 0; i < 14; i++) { ctx.fillRect(cx + d * i, cy, 1, 1); ctx.fillRect(cx, cy + i, 1, 1); ctx.fillRect(cx + d * i, cy + 13 - i, 1, 1); ctx.fillRect(cx + d * Math.round(i * .5), cy + i, 1, 1); ctx.fillRect(cx + d * i, cy + Math.round(i * .5), 1, 1); }
    for (const r of [4, 8]) for (let i = 0; i <= r; i++) ctx.fillRect(cx + d * i, cy + r - i, 1, 1);
  }
}

// ---- the air: kites, paper planes, petals, confetti, bubbles, notes, bats, sky lanterns, scraps on the ground
function scAir(ctx, kind, colors) {
  if (kind === "kites") for (let i = 0; i < 3; i++) {
    const x = 40 + i * 120 + Math.sin(realClock * 0.4 + i * 2) * 14, y = 18 + i % 2 * 9 + Math.sin(realClock * 0.9 + i) * 3, c = ["#e1725b", "#4f9fd0", "#efc452"][i], c2 = ["#f7d0c8", "#cfe6f6", "#fbefc4"][i];
    for (let r = -5; r <= 5; r++) { const w = 6 - Math.abs(r); scPx(ctx, r < 0 ? c : c2, x - w, y + r, w); scPx(ctx, r < 0 ? c2 : c, x, y + r, w); }
    scPx(ctx, "#5e5b71", x, y - 5, 1, 11); scPx(ctx, "#5e5b71", x - 5, y, 11, 1);
    for (let k = 1; k < 14; k++) { const tx = x + Math.sin(realClock * 2 + k * 0.6 + i) * 2.5, ty = y + 5 + k; scPx(ctx, "#5e5b71", tx, ty); if (k % 4 === 2) scPx(ctx, c, tx - 1, ty, 3, 1); }
  }
  if (kind === "planes") for (let i = 0; i < 3; i++) {
    const p = (realClock * 0.05 + scH(i, 4)) % 1, x = -10 + p * (W + 20), y = 20 + i * 12 + Math.sin(p * 9 + i) * 6;
    scPx(ctx, "#f7f6fb", x - 5, y, 11, 1); scPx(ctx, "#f7f6fb", x - 3, y - 1, 6, 1); scPx(ctx, "#ffffff", x - 1, y - 2, 3, 1); scPx(ctx, "#c9c6d6", x - 5, y + 1, 7, 1); scPx(ctx, "#b5b1c4", x - 4, y + 2, 3, 1);
  }
  const fall = (n, v, draw) => { for (let i = 0; i < n; i++) { const y = (scH(i, 5) * H + realClock * v * (0.7 + scH(i, 6) * 0.6)) % (H + 6) - 6, x = scH(i, 7) * W + Math.sin(realClock * 1.3 + i) * 6; draw(x, y, i); } };
  if (kind === "petals") fall(30, 8, (x, y, i) => { scPx(ctx, i % 2 ? "#f5c3d4" : "#fbe3ea", x, y, 2, 2); scPx(ctx, "#f29bb8", x + 1, y + 1); });
  if (kind === "confetti") fall(44, 14, (x, y, i) => scPx(ctx, ["#efc452", "#e1725b", "#4f9fd0", "#a8d68a", "#c9a0ff"][i % 5], x, y, Math.sin(realClock * 6 + i) > 0 ? 3 : 1, 2));
  if (kind === "bubbles") for (let i = 0; i < 12; i++) {
    const y = H - ((scH(i, 8) * H + realClock * 6 * (0.6 + scH(i, 9))) % (H + 8)), x = scH(i, 10) * W + Math.sin(realClock + i) * 4, r = 1 + (i % 3);
    ctx.strokeStyle = "rgba(220, 236, 255, .8)"; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(Math.round(x) + .5, Math.round(y) + .5, r, 0, 6.3); ctx.stroke(); scPx(ctx, "#ffffff", x - r / 2, y - r / 2);
  }
  if (kind === "notes") for (let i = 0; i < 6; i++) {
    const t = (realClock * 0.25 + scH(i, 11)) % 1, x = 40 + scH(i, 12) * (W - 80) + Math.sin(t * 6) * 5, y = 70 - t * 50, c = ["#ff7fa8", "#7fd6ff", "#ffd36b"][i % 3];
    ctx.globalAlpha = Math.sin(t * Math.PI); scPx(ctx, c, x, y, 2, 2); scPx(ctx, c, x + 1, y - 4, 1, 4); scPx(ctx, c, x + 2, y - 4); ctx.globalAlpha = 1;
  }
  if (kind === "bats") for (let i = 0; i < 2; i++) {
    const p = (realClock * 0.06 + i * 0.5) % 1, x = (i ? W + 10 - p * (W + 20) : -10 + p * (W + 20)), y = 14 + i * 14 + Math.sin(realClock * 3 + i) * 4;
    ctx.drawImage(festImg(DECO.bat[Math.floor(realClock * 8 + i) % 2]), Math.round(x), Math.round(y));
  }
  if (kind === "bits") {                                 // red firecracker scraps on the ground
    const base = sim.place === "front" ? OUT.front.base + 2 : OUT.beach.deck + 6;
    for (let i = 0; i < 40; i++) scPx(ctx, colors[i % colors.length], scH(i, 13) * W, base + scH(i, 14) * 6);
  }
}
function scSkyLanterns(ctx, f) {
  if (f < 0.3) return;
  for (let i = 0; i < 7; i++) {
    const p = (realClock * 0.02 + scH(i, 15)) % 1, x = 20 + scH(i, 16) * (W - 40) + Math.sin(realClock * 0.5 + i) * 4, y = H - 10 - p * (H + 10);
    ctx.globalAlpha = Math.min(1, f * Math.min(1, (1 - p) * 4)); ctx.drawImage(festImg(DECO.skyLantern), Math.round(x), Math.round(y));
    decoGlow(ctx, x + 2.5, y + 4, 7, "255, 190, 110", 0.4 * f); ctx.globalAlpha = 1;
  }
}
function scFireworks(ctx, f) {                           // bursts across the night sky, every couple of seconds
  if (f < 0.35) return;
  const sky = sim.place === "beach" ? OUT.beach.horizon - 4 : 46;
  for (let k = 0; k < 4; k++) {
    const per = 2.6 + k * 0.7, n = Math.floor((realClock + k * 1.3) / per), t = ((realClock + k * 1.3) % per) / per;
    const cx = 24 + scH(n, k + 20) * (W - 48), cy = 8 + scH(n, k + 30) * (sky - 14), col = ["255, 120, 120", "255, 214, 110", "140, 220, 255", "200, 150, 255", "150, 255, 170"][(n + k) % 5];
    if (t < 0.2) { const y = sky + 10 - (sky + 10 - cy) * (t / 0.2); scPx(ctx, `rgba(${col}, ${f.toFixed(2)})`, cx, y, 1, 2); continue; }
    const u = (t - 0.2) / 0.8, r = 4 + u * 17, a = Math.min(1, (1 - u) * f * 1.4);
    for (let i = 0; i < 18; i++) {
      const th = i / 18 * Math.PI * 2, x = cx + Math.cos(th) * r, y = cy + Math.sin(th) * r + u * u * 6;
      scPx(ctx, `rgba(${col}, ${a.toFixed(2)})`, x, y, u < 0.5 ? 2 : 1, u < 0.5 ? 2 : 1); if (u < 0.6) scPx(ctx, `rgba(255, 255, 255, ${(a * 0.6).toFixed(2)})`, cx + Math.cos(th) * r * 0.6, cy + Math.sin(th) * r * 0.6 + u * u * 4);
    }
    decoGlow(ctx, cx, cy, 16 + r, col, 0.22 * a);
    if (sim.place === "beach") for (let i = 0; i < 4; i++) scPx(ctx, `rgba(${col}, ${(a * 0.35).toFixed(2)})`, cx - 2 + i, OUT.beach.horizon + 4 + i * 3 + Math.sin(realClock * 3 + i) * 1, 3, 1);   // its reflection
  }
}

// ---- the mall: things hanging from under the upstairs fascia, scrolling with the near layer
function scCeil(ctx, kind, every = 26, offN) {
  const L = MALL, top = L.fascia + 1;
  for (let x = mod(offN, every) - every; x < W + every; x += every) {
    const k = Math.round((x - offN) / every), drop = 3 + (k % 2) * 4;
    scPx(ctx, "#8a8798", x, top, 1, drop);
    scHang(ctx, kind === "ghost" ? "ghost" : kind, x, top + drop - 1, ((k % 7) + 7) % 7, ["#efc452", "#e1725b", "#4f9fd0"]);
  }
}

// ---- hooks called from the place renderers
function drawFestScenery(ctx, offN = 0) {
  const C = sceneryHere();
  if (!C) return;
  const top = SC_TOP[sim.place] ?? 3;
  for (const [kind, a, b, c] of C) {
    if (kind === "string") { scString(ctx, a, b, c, top); if (!["lantern", "ghost", "candy"].includes(a)) scString(ctx, a, b, c, top + 11, -8 + b / 2, W + 8); }
    else if (kind === "rail") scRail(ctx, a);
    else if (kind === "ceil") scCeil(ctx, a, b, offN);
    else if (kind === "doorLanterns" || kind === "couplets") scDoor(ctx, kind);
    else if (kind === "door") scDoor(ctx, a);
    else if (kind === "stoop") scStoop(ctx, a);
    else if (kind === "cobwebs") scCobwebs(ctx);
    else if (["kites", "planes", "petals", "confetti", "bubbles", "notes", "bats", "bits"].includes(kind)) scAir(ctx, kind, a);
    else if (kind === "water") scWater(ctx, 0);
  }
}
function drawFestSceneryNight(ctx, f) {
  const C = sceneryHere();
  if (!C) return;
  const top = SC_TOP[sim.place] ?? 3;
  for (const [kind, a, b] of C) {
    if (f > 0.05 && kind === "string") scGlowString(ctx, a, b, top, f);
    else if (f > 0.05 && kind === "rail") scRailGlow(ctx, a, f);
    else if (f > 0.05 && kind === "doorLanterns") { const [x, y, w] = OUT.front.door; for (const lx of [x - 5, x + w + 5]) decoGlow(ctx, lx, y + 8, 9, "255, 150, 90", 0.5 * f); }
    else if (f > 0.05 && kind === "stoop") scStoopGlow(ctx, a, f);
    else if (kind === "water") scWater(ctx, f);
    else if (kind === "moonPath") scMoonPath(ctx, f);
    else if (kind === "fireworks") scFireworks(ctx, f);
    else if (kind === "skyLanterns") scSkyLanterns(ctx, f);
  }
}
