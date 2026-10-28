// ================================================================ the park dressed up for festivals (user: 装饰感做足)
// Bunting across the top, strings of red lanterns, balloon bunches tied to the
// stalls and sign boards (with the festival's own icon), props on the lawn
// (giant lollipops, book stacks, rose pots, jack-o'-lanterns, tombstones), and
// moving things: bats, sky lanterns rising at night, fog on 怪兽夜.
const DECO = D.deco;
const PARK_DECO = {
  甜品节: { bunting: ["#f5c3d4", "#fae59c", "#a9d6bd", "#dccbf2"], balloons: "round", props: ["lollipop", "board", "lollipop", "lollipop"], icon: () => D.items.dish.cake?.[0] },
  端午节: { bunting: ["#e1725b", "#6ba14c", "#efc452"], lanterns: true, balloons: "round", props: ["board"], icon: () => D.items.dish.zongzi?.[0] },
  中秋节: { bunting: ["#efc452", "#e1725b", "#fae59c"], lanterns: true, sky: true, balloons: "round", props: ["board"], icon: () => D.items.dish.mooncake?.[0] },
  读书日: { bunting: ["#4f9f97", "#f3ede3", "#e1725b", "#efc452"], balloons: "round", props: ["books", "board", "books", "books"], icon: () => D.items.dish.book?.[0] },
  彩票日: { bunting: ["#e1725b", "#efc452", "#f7f6fb"], balloons: "round", props: [] },
  七夕: { hearts: true, balloons: "heart", sky: true, props: ["roses", "board", "roses", "roses"], icon: () => DECO.heart[1] },
  元宵节: { lanterns: true, sky: true, props: [] },
  怪兽夜: { bunting: ["#e0782f", "#5b3c8f", "#33253b"], balloons: "ghost", bats: true, fog: true,
    props: ["pumpkin", "tomb", "pumpkin", "board", "tomb", "pumpkin"], icon: () => D.festival2.masks[0] },
  春分: { bunting: ["#a7d47a", "#f5c3d4", "#fae59c"], props: [] },
  春节: { bunting: ["#d8383a", "#f2b33d", "#d8383a", "#f7e2b0"], lanterns: true, props: [] },
  冬至: { lanterns: true, props: [] },
};
const decoHere = () => sim.place === "park" && !stormOutside() && PARK_DECO[festName()];
const decoLife = { bats: [], sky: [], seed: 0 };
// spots on the lawn behind the path, clear of stalls, benches, the toilet, the pond, the riddle tree, the arch
function decoSpots(n) {
  const L = parkLayout(), avoid = festStallsHere().map(s => [s.x, 26]);
  if (L.bench) avoid.push([L.bench.x, 24]);
  if (L.facility) avoid.push([L.facility.x, 56]);
  if (L.pond) avoid.push([L.pond[0], L.pond[2] + 10]);
  if (riddleHere()) avoid.push([RIDDLE_TREE.x, 62]);
  if (festName() === "七夕" && QIXI_ARCH[L.id] != null) avoid.push([QIXI_ARCH[L.id], 26]);
  const seed = [...L.id].reduce((a, c) => a + c.charCodeAt(0), 0), xs = [];
  for (let x = 14; x < W - 12; x += 7) xs.push(x);
  xs.sort((a, b) => hash(a * 1.7 + seed) - hash(b * 1.7 + seed));
  const out = [];
  for (const x of xs) if (out.length < n && avoid.every(([a, r]) => Math.abs(x - a) > r) && out.every(o => Math.abs(o - x) > 30)) out.push(x);
  return out.sort((a, b) => a - b);
}
function drawString(ctx, x0, x1, top, sag, every, each) {
  for (let x = Math.floor(x0); x <= x1; x++) {
    const u = (x - x0) / (x1 - x0), y = Math.round(top + Math.sin(u * Math.PI) * sag);
    if (x >= 0 && x < W) { ctx.fillStyle = "#5e5b71"; ctx.fillRect(x, y, 1, 1); }
    if ((x - Math.floor(x0)) % every === Math.floor(every / 2)) each(x, y);
  }
}
function drawBalloonBunch(ctx, tx, ty, n, kind, k0) {
  for (let i = 0; i < n; i++) {
    const ph = tx * 0.13 + i * 1.9, hx = Math.round(tx - 6 + i * 6 + Math.sin(realClock * 0.9 + ph) * 1.5), hy = Math.round(ty - 24 - (i % 2) * 6 + Math.sin(realClock * 1.3 + ph) * 1.2);
    ctx.fillStyle = "rgba(247, 246, 251, .85)";
    for (let s = 0; s <= 10; s++) {                  // the string, a gentle curve
      const u = s / 10, x = tx + (hx + 4 - tx) * u + Math.sin(u * Math.PI) * 1.5, y = ty + (hy + 10 - ty) * u;
      ctx.fillRect(Math.round(x), Math.round(y), 1, 1);
    }
    const img = kind === "heart" ? DECO.heart[(k0 + i) % 2] : kind === "ghost" ? DECO.ghost : DECO.balloons[(k0 + i) % DECO.balloons.length];
    ctx.drawImage(festImg(img), hx, hy);
  }
}
function drawParkDeco(ctx, dt, run) {
  const C = decoHere();
  if (!C) return;
  const ground = OUT.park.side - 1, sway = Math.sin(realClock * 0.8);
  if (C.bunting) for (const [k, top] of [[0, 3], [1, 8]]) {   // two strands of pennants across the top
    for (let a = -10 + k * 40; a < W; a += 130)
      drawString(ctx, a, a + 130, top, 7, 7, (x, y) => {
        const c = C.bunting[((x / 7) | 0) % C.bunting.length], d = Math.round(sway * ((x % 3) - 1) * 0.5);
        ctx.fillStyle = c; ctx.fillRect(x - 2, y + 1, 5, 1); ctx.fillRect(x - 1 + d, y + 2, 3, 1); ctx.fillRect(x + d, y + 3, 2, 1); ctx.fillRect(x + d, y + 4, 1, 1);
      });
  }
  if (C.hearts) drawString(ctx, -6, W + 6, 4, 9, 11, (x, y) => {   // 七夕: a garland of paper hearts
    ctx.fillStyle = (x / 11 | 0) % 2 ? "#f2b6c8" : "#e1725b";
    ctx.fillRect(x - 2, y + 1, 2, 1); ctx.fillRect(x + 1, y + 1, 2, 1); ctx.fillRect(x - 2, y + 2, 5, 1); ctx.fillRect(x - 1, y + 3, 3, 1); ctx.fillRect(x, y + 4, 1, 1);
  });
  if (C.lanterns) drawString(ctx, -8, W + 8, 12, 8, 24, (x, y) =>   // a string of red lanterns
    ctx.drawImage(festImg(DECO.lantern), x - 3 + Math.round(Math.sin(realClock * 1.1 + x) * 0.6), y + 1));
  // props on the lawn, a sign board with the festival's icon among them
  const spots = decoSpots(C.props.length);
  C.props.forEach((p, i) => {
    const x = spots[i];
    if (x == null) return;
    if (p === "board") {
      const b = DECO.boards[(i + festDay()) % DECO.boards.length];
      ctx.drawImage(festImg(b), x - 12, ground - 31);
      const icon = C.icon && C.icon();
      if (icon) { const im = festImg(icon), w = im.width || 14, h = im.height || 14, k = Math.min(1, 14 / Math.max(w, h)); ctx.drawImage(im, Math.round(x - w * k / 2), Math.round(ground - 31 + 11 - h * k / 2), Math.round(w * k), Math.round(h * k)); }
      if (C.balloons) drawBalloonBunch(ctx, x + 9, ground - 30, 2, C.balloons, i);
    } else if (p === "lollipop") ctx.drawImage(festImg(DECO.lollipops[i % 3]), x - 5, ground - 27);
    else if (p === "books") ctx.drawImage(festImg(DECO.books), x - 9, ground - 21);
    else if (p === "roses") ctx.drawImage(festImg(DECO.roses), x - 6, ground - 11);
    else if (p === "pumpkin") ctx.drawImage(festImg(DECO.pumpkin[0]), x - 6, ground - 10);
    else if (p === "tomb") ctx.drawImage(festImg(DECO.tomb[i % 2]), x - 5, ground - 12);
  });
  if (C.balloons) for (const s of festStallsHere()) drawBalloonBunch(ctx, s.x + 16, FEST_STALL_TOP + 18, 3, C.balloons, s.k);   // tied to the stalls
  if (C.bats) {                                    // bats flapping across
    if (run && decoLife.bats.length < 3 && Math.random() < dt * 0.25) { const d = Math.random() < 0.5 ? 1 : -1; decoLife.bats.push({ x: d > 0 ? -10 : W + 10, y: 10 + Math.random() * 30, d, v: 18 + Math.random() * 14, ph: Math.random() * 6 }); }
    for (const b of decoLife.bats) {
      if (run) b.x += b.d * b.v * dt;
      ctx.drawImage(festImg(DECO.bat[Math.floor(realClock * 8 + b.ph) % 2]), Math.round(b.x), Math.round(b.y + Math.sin(realClock * 3 + b.ph) * 4));
    }
    decoLife.bats = decoLife.bats.filter(b => b.x > -20 && b.x < W + 20);
  }
}
function decoGlow(ctx, x, y, r, rgb, a) {            // a soft round pool of light
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(${rgb}, ${a.toFixed(3)})`); g.addColorStop(1, `rgba(${rgb}, 0)`);
  ctx.save(); ctx.globalCompositeOperation = "lighter"; ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.restore();
}
// after the night pass: things that glow
function drawParkDecoNight(ctx, f, dt, run) {
  const C = decoHere();
  if (!C) return;
  const ground = OUT.park.side - 1;
  if (C.props.includes("pumpkin") && f > 0.2) {   // jack-o'-lanterns glowing
    const spots = decoSpots(C.props.length);
    C.props.forEach((p, i) => {
      if (p !== "pumpkin" || spots[i] == null) return;
      const flick = 0.22 + 0.06 * Math.sin(realClock * 9 + i * 2);
      decoGlow(ctx, spots[i], ground - 5, 11, "255, 170, 70", flick * 1.6 * f);
    });
  }
  if (C.lanterns && f > 0.2) drawString(ctx, -8, W + 8, 12, 8, 24, (x, y) => decoGlow(ctx, x, y + 6, 9, "255, 150, 90", 0.45 * f));
  if (C.sky && f > 0.4) {                          // sky lanterns rising
    if (run && decoLife.sky.length < 9 && Math.random() < dt * 0.4) decoLife.sky.push({ x: 20 + Math.random() * (W - 40), y: H - 20, v: 3 + Math.random() * 3, ph: Math.random() * 6 });
    for (const s of decoLife.sky) {
      if (run) { s.y -= s.v * dt; s.x += Math.sin(realClock * 0.5 + s.ph) * 2 * dt; }
      ctx.globalAlpha = Math.min(1, f * Math.min(1, s.y / 20));
      ctx.drawImage(festImg(DECO.skyLantern), Math.round(s.x), Math.round(s.y));
      decoGlow(ctx, s.x + 2.5, s.y + 4, 7, "255, 190, 110", 0.4 * f);
    }
    ctx.globalAlpha = 1;
    decoLife.sky = decoLife.sky.filter(s => s.y > -10);
  }
  if (C.fog && f > 0.2) {                          // 怪兽夜: purple fog creeping over the lawn
    for (let x = 0; x < W; x += 4) {
      const h = 6 + Math.sin(x * 0.07 + realClock * 0.4) * 3 + Math.sin(x * 0.03 - realClock * 0.25) * 3;
      ctx.fillStyle = `rgba(150, 110, 190, ${(0.16 * f).toFixed(3)})`;
      ctx.fillRect(x, Math.round(ground + 4 - h), 4, Math.round(h) + 8);
    }
  }
}
