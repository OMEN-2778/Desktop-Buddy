// ================================================================ festival activities (batch 3): 写信日
// On 写信日 the phone and computer rings get 写信: pick who (爸爸 / 妈妈 /
// friends / 未来的自己), pick what about, and the letter goes out (kept in
// the diary, folded like a chat). Replies come back a few hours later, and
// others write too, now and then through the day. A letter that comes shows
// as a little bubble with an envelope over the front door (at home and on
// the street); click it and she reads it: it opens in the diary. Unread
// letters wait in lifeFlags.mail (saved). Texts: festival_text3.json.
ML.fest_letter_sent = { name: "寄出一封信", emo: "happy", pts: 1, min: 240 };
ML.fest_letter_read = { name: "收到一封信", emo: "happy", pts: 2, min: 360 };
const LETTER_MAX = 6;   // letters she writes a day
const mailState = () => (lifeFlags.mail ||= { queue: [], box: [], day: -1, sent: 0, planned: -1 });
const letterFill = (t, who) => fill(t, { 收信人: who, 寄信人: who, 名字: nameOf() });
function letterContacts() {
  return sortedContacts().filter(c => c.family || c.affinity > 0).slice(0, 10);
}
function openLetterTo() {
  if (festName() !== "写信日") return;
  const icon = D.festival.envelope, cs = letterContacts();
  PICK.fest_letter_to = { title: "写信 · 寄给谁",
    groups: () => [
      { name: "家人", items: cs.filter(c => c.family).map(c => ({ title: contactName(c), icon, item: { id: c.id } })) },
      { name: "朋友", items: cs.filter(c => !c.family).map(c => ({ title: contactName(c), info: contactRelation(c), icon, item: { id: c.id } })) },
      { name: "其他", items: [{ title: "未来的自己", line: "封好，过几年再拆", icon, item: { id: "@self" } }] },
    ].filter(g => g.items.length) };
  openPicker("fest_letter_to", pickFrom("buddy"));
}
function openLetterTheme(item) {
  if (item.id === "@self") { writeLetter({ id: "@self" }); return; }
  const c = socialState.contacts.find(c => c.id === item.id);
  if (!c) return;
  PICK.fest_letter = { title: `写给${contactName(c)} · 写点什么`,
    groups: () => [{ name: "信的主题", items: FEST_TEXT3.themes.map(t => ({ title: t.name, line: t.desc, icon: D.festival.envelope, item: { id: c.id, theme: t.id } })) }] };
  openPicker("fest_letter", pickFrom("buddy"));
}
function writeLetter(item) {
  const m = mailState();
  if (m.day !== festDay()) { m.day = festDay(); m.sent = 0; }
  if (m.sent >= LETTER_MAX) { speak("今天写得手都酸了，明天再写吧"); return; }
  m.sent++;
  const self = item.id === "@self", c = self ? null : socialState.contacts.find(c => c.id === item.id);
  if (!self && !c) return;
  const who = self ? "未来的自己" : contactName(c), theme = FEST_TEXT3.themes.find(t => t.id === item.theme);
  const body = self ? pick(FEST_TEXT3.self) : pick(FEST_TEXT3.mine[item.theme] || []);
  if (!body) return;
  const lines = [...body.lines.map(l => letterFill(l, who)), `—— ${nameOf()}`];
  log(self ? "给未来的自己写了一封信，封好藏进了抽屉。" : `给${who}写了一封信：「${theme?.name || "近况"}」。`, null, [["@letter", ""], ...lines.map(l => ["", l])]);
  speak(pick(FEST_TEXT3.sent));
  addMood("fest_letter_sent", { diary: false, words: false });
  sim.needs.social = clamp(sim.needs.social + 6);
  if (!self) {   // the reply, a few hours later
    const kind = c.family ? "family" : "friend", r = pick(FEST_TEXT3.replies[item.theme]?.[kind] || []);
    if (r) m.queue.push({ at: sim.t + 60 + Math.random() * 300, from: c.id, title: `${who}回信了`, lines: r.lines });
  }
}
// others write on the day too: a parent, a friend or two, someone unexpected
function planLetters() {
  const m = mailState();
  if (festName() !== "写信日" || m.planned === festDay()) return;
  m.planned = festDay();
  const day0 = festDay() * 1440, at = () => day0 + (9 + Math.random() * 12) * 60;
  const fam = sortedContacts().filter(c => c.family), fr = sortedContacts().filter(c => !c.family && c.affinity > 10);
  if (fam.length) { const l = pick(FEST_TEXT3.incoming.family); m.queue.push({ at: at(), from: pick(fam).id, title: l.title, lines: l.lines }); }
  for (const c of fr.sort(() => Math.random() - 0.5).slice(0, 2)) { const l = pick(FEST_TEXT3.incoming.friend); m.queue.push({ at: at(), from: c.id, title: l.title, lines: l.lines }); }
  const o = pick(FEST_TEXT3.incoming.other); m.queue.push({ at: at(), from: null, name: o.from, title: o.title, lines: o.lines });
}
function mailTick() {
  planLetters();
  const m = lifeFlags.mail;
  if (!m || !m.queue.length) return;
  const due = m.queue.filter(l => sim.t >= l.at);
  if (!due.length) return;
  m.queue = m.queue.filter(l => sim.t < l.at);
  m.box.push(...due);
  if (["home", "front"].includes(sim.place) && !asleep()) { gameAudio.sound("bell", .2, { gap: 4 }); speak(pick(["好像有信来了", "门口有封信！", "是信吗？"])); }
}
const mailWaiting = () => !!lifeFlags.mail?.box?.length && ["home", "front"].includes(sim.place);
function mailBubblePos() {
  if (sim.place === "front") { const O = OUT.front; return { x: O.doorX, y: O.door[1] - 14 }; }
  const c = CLICK.front_door; return { x: c.x - 9, y: c.y + 11 };   // beside the door: above it is the ceiling slab
}
function drawMailBubble(ctx) {
  if (!mailWaiting()) return;
  const p = mailBubblePos(), bob = Math.round(Math.sin(realClock * 3) * 1.5);
  ctx.drawImage(festImg(D.festival.mail), Math.round(p.x) - 10, Math.round(p.y) - 9 + bob);
  if (lifeFlags.mail.box.length > 1) { ctx.fillStyle = "#b94b4b"; ctx.fillRect(Math.round(p.x) + 6, Math.round(p.y) - 9 + bob, 5, 5); ctx.fillStyle = "#f4f2ee"; ctx.fillRect(Math.round(p.x) + 8, Math.round(p.y) - 8 + bob, 1, 3); }
}
function mailBubbleHit(x, y) {
  if (!mailWaiting()) return false;
  const p = mailBubblePos();
  return Math.abs(x - p.x) <= 11 && y >= p.y - 10 && y <= p.y + 9;
}
function readMail() {
  const m = lifeFlags.mail, l = m?.box.shift();
  if (!l) return;
  const c = l.from ? socialState.contacts.find(c => c.id === l.from) : null, who = c ? contactName(c) : l.name || "一位朋友";
  const lines = [...l.lines.map(t => letterFill(t, who)), `—— ${who}`];
  log(l.title.includes(who) || !c ? l.title : `${who}寄来一封信`, null, [["@letter", who], ...lines.map(t => ["", t])]);
  const li = logEl.firstChild;
  if (li) talkOpen.add(li);
  setDiaryOpen(true);
  speak(pick(FEST_TEXT3.react), true);
  addMood("fest_letter_read", { diary: false, words: false });
  sim.needs.social = clamp(sim.needs.social + 8);
  if (c) { c.lastContact = sim.t; c.affinity = Math.min(100, (c.affinity || 0) + 2); contactsSig = ""; }
}
function festLetterRing(which, items) {
  if (festName() !== "写信日" || !["phone", "computer"].includes(which)) return items;
  const out = items.slice(), back = out.findIndex(([id]) => id === "back");
  out.splice(back < 0 ? out.length : back, 0, ["write_letter", "写信 ▸"]);
  return out;
}
FEST_TEXT.chatter["写信日"] = FEST_TEXT3.chatter;
