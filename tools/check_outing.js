// Checks the outing text files in prototype/demo/outing/:
//   node tools/check_outing.js <file> go-a|go-b|say-pb|say-fm
const fs = require("fs");
const [file, kind] = process.argv.slice(2);
const d = (0, eval)("(" + fs.readFileSync(file, "utf8").replace(/^\s*\/\/.*$/gm, "") + ")");
const bad = [];
const strs = (a, where, min, max) => {
  if (!Array.isArray(a) || a.length < min) { bad.push(`${where}: needs >= ${min} strings, has ${Array.isArray(a) ? a.length : "none"}`); return; }
  const seen = new Set();
  a.forEach((s, i) => {
    if (typeof s !== "string" || !s.trim()) bad.push(`${where}[${i}] empty`);
    else if (s.length > max) bad.push(`${where}[${i}] over ${max} chars: ${s}`);
    if (seen.has(s)) bad.push(`${where}[${i}] duplicate: ${s}`);
    seen.add(s);
  });
};
const SPEC = {
  "go-a": { reasons: { bored: ["park", "mall", "beach", "front"], happy: ["park", "mall", "beach", "front"] } },
  "go-b": { reasons: { low: ["park", "beach", "front"], lonely: ["park", "mall", "beach", "front"] }, back: ["bored", "happy", "low", "lonely"] },
};
if (SPEC[kind]) {
  const S = SPEC[kind];
  for (const [why, places] of Object.entries(S.reasons)) {
    if (!d[why]) { bad.push(`missing ${why}`); continue; }
    for (const pl of places) {
      if (!d[why][pl]) { bad.push(`missing ${why}.${pl}`); continue; }
      strs(d[why][pl].say, `${why}.${pl}.say`, 10, 22);
      strs(d[why][pl].log, `${why}.${pl}.log`, 8, 32);
    }
  }
  for (const why of S.back || []) strs((d.back || {})[why], `back.${why}`, 14, 22);
} else {
  const need = { "say-pb": { park: [25, 25, 20], beach: [25, 25, 20] }, "say-fm": { front: [15, 20, 20], mall: [0, 20, 25] } }[kind];
  const WHEN = ["low+night", "low", "high"];
  for (const [pl, counts] of Object.entries(need)) {
    const list = d[pl] || [], seen = new Set();
    WHEN.forEach((w, i) => { const n = list.filter(l => l.when === w).length; if (n < counts[i]) bad.push(`${pl}: ${w} needs >= ${counts[i]}, has ${n}`); });
    list.forEach((l, i) => {
      if (!l || typeof l.t !== "string" || !l.t.trim()) bad.push(`${pl}[${i}] no text`);
      else if (l.t.length > 24) bad.push(`${pl}[${i}] over 24 chars: ${l.t}`);
      if (!WHEN.includes(l.when)) bad.push(`${pl}[${i}] when ${l.when}`);
      if (seen.has(l.t)) bad.push(`${pl}[${i}] duplicate: ${l.t}`);
      seen.add(l.t);
    });
  }
}
if (bad.length) { console.log(bad.slice(0, 40).join("\n")); process.exit(1); }
console.log("ok");
