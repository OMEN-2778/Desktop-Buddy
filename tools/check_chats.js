// Checks a conversation file from prototype/demo/chats/ (a JS array of talks):
//   node tools/check_chats.js prototype/demo/chats/call_dad.js call 50
// kind: call (phone, voice only) or forum. Prints problems, exits 1 if any.
const fs = require("fs"), path = require("path");
const [file, kind, want] = process.argv.slice(2);
const read = f => fs.readFileSync(f, "utf8");
const EMO = "playful happy dazed energized embarrassed tense sad focused scared inspired confident uncomfortable flirty bored angry".split(" ");
const talks = (0, eval)(read(file));
const CHATS = (0, eval)(read(path.join(__dirname, "../prototype/demo/chats_text.js")) + "\nCHATS");
const used = new Set();
for (const g of [...Object.values(CHATS.video), ...Object.values(CHATS.forum)]) for (const t of g.talks) used.add(t.title);
for (const f of fs.readdirSync(path.join(__dirname, "../prototype/demo/chats"))) {
  const p = path.join(__dirname, "../prototype/demo/chats", f);
  if (path.resolve(p) !== path.resolve(file)) for (const t of (0, eval)(read(p))) used.add(t.title);
}
const bad = [], own = new Set(), emos = {};
if (!Array.isArray(talks)) { console.log("not an array"); process.exit(1); }
if (want && talks.length !== +want) bad.push(`expected ${want} talks, got ${talks.length}`);
talks.forEach((t, i) => {
  const at = `#${i + 1} ${t.title}`;
  if (!t.title || t.title.length > 14) bad.push(`${at}: title missing or over 14 chars`);
  if (used.has(t.title) || own.has(t.title)) bad.push(`${at}: title already used`);
  own.add(t.title);
  if (!Array.isArray(t.lines) || t.lines.length < 4 || t.lines.length > 9) bad.push(`${at}: needs 4-9 lines`);
  const m = t.mood;
  if (!m) bad.push(`${at}: no mood`);
  else {
    if (!EMO.includes(m.emo)) bad.push(`${at}: emo ${m.emo}`);
    if (!m.name || m.name.length < 2 || m.name.length > 6) bad.push(`${at}: mood name 2-6 chars`);
    if (![1, 2, 3].includes(m.pts)) bad.push(`${at}: pts 1-3`);
    if (!(m.min >= 60 && m.min <= 300)) bad.push(`${at}: min 60-300`);
    emos[m.emo] = (emos[m.emo] || 0) + 1;
  }
  (t.lines || []).forEach((l, j) => {
    if (typeof l !== "string" || !l.trim()) bad.push(`${at}: line ${j + 1} empty`);
    else if (l.replace(/^[>#]\s*/, "").length > 34) bad.push(`${at}: line ${j + 1} over 34 chars`);
    if (kind === "call" && /[#]/.test(l[0])) bad.push(`${at}: calls have no "#" lines`);
    if (kind === "call" && /镜头|画面|屏幕|摄像|看你|看看你|视频|看见|看到你/.test(l)) bad.push(`${at}: line ${j + 1} is visual, but it is a phone call`);
  });
  if (kind === "call" && !(t.lines || []).some(l => l[0] === ">")) bad.push(`${at}: no ">" line`);
  if (kind === "forum" && !((t.lines || [])[0] || "").startsWith("#")) bad.push(`${at}: a forum talk starts with a "#" post`);
  if (kind === "forum" && !(t.lines || []).some(l => l[0] === ">")) bad.push(`${at}: no ">" comment`);
});
console.log(`${talks.length} talks, emotions:`, JSON.stringify(emos));
if (bad.length) { console.log(bad.join("\n")); process.exit(1); }
console.log("ok");
