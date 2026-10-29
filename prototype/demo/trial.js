// ================================================================ 试玩版 (trial build only)
// tools/make_demo.py --trial pastes this just before boot, into prototype/demo/trial.html (the
// full game stays as it is). The trial is a day-to-day life at home and nothing else (user):
// no festivals, no contacts (calls, visits, video chats, messages), no pets, no going out, no
// saving, no updates, no tutorial. Everything is switched off here by replacing the entry points,
// so the rest of the game code is shared with the full version.
const TRIAL = true;
festToday = () => null;                                  // no festivals (festName() follows)
outingDest = () => null;                                 // she never decides to go out
// contacts: nobody calls, visits or is called
tickSocial = () => {}; tickSocialLife = () => {}; tickFriendVisitTravel = () => {};
requestIncomingCall = () => false;
socialState.nextCall = socialState.nextVisit = Infinity;
// pets: none to adopt, none at home
petChoiceScores = () => {};
PetRules.weekly = () => [];
// cards of places, visits, friends and pets never come (tools/make_demo.py also drops most of them from the page)
for (let i = CARDS.length - 1; i >= 0; i--) { const c = CARDS[i]; if ((c.at || "home") !== "home" || c.service || /has(Pet|Cat|Dog)/.test(c.when || "")) CARDS.splice(i, 1); }
const TRIAL_OFF = new Set(["go_out", "phone_call", "phone_video", "phone_text", "pc_video", "host"]);
{
  const start = startAct;
  startAct = function (name, quiet) {                    // whatever still asks for them gets a book instead
    if (TRIAL_OFF.has(name) || OUT_ACTS.has(name) || name.startsWith("pet_")) name = "read";
    return start(name, quiet);
  };
  const open = openRing;
  openRing = function (what, at) {
    if (what === "door") { showHint("试玩版只能在家里生活哦，完整版可以出门逛街、过节、交朋友、养宠物。"); return; }
    return open(what, at);
  };
}
RINGS.phone = RINGS.phone.filter(([id]) => !["call", "phone_video", "phone_text"].includes(id));
RINGS.computer = RINGS.computer.filter(([id]) => id !== "video");
// chance cards: only the ones that happen at home and need nobody else
{
  const away = /朋友|爸|妈|父母|邻居|同事|宠物|猫|狗|公园|商场|海边|码头|酒吧|迪厅|出门|节/;
  const out = new Set(["front", "park", "mall", "beach", "bar", "disco", "friend_home", "visit", "food"]);
  for (let i = CARDS.length - 1; i >= 0; i--) if (out.has(CARDS[i].on) || CARDS[i].service || away.test(JSON.stringify(CARDS[i]))) CARDS.splice(i, 1);
}
// no saving: every start is a fresh day one
store.load = async () => null;
store.save = async () => {};
// no updates, no tutorial
startUpdateChecks = () => {};
openGuide = () => {};
{
  const apply = applySettings;
  applySettings = function (st) { apply(st); prefs.guided = true; prefs.autosave = false; };
}
for (let i = SETTINGS.length - 1; i >= 0; i--) if (["存档", "更新"].includes(SETTINGS[i].label)) SETTINGS.splice(i, 1);
document.head.insertAdjacentHTML("beforeend", `<style>#networkTrigger,#contactsPanel,#contactActions,#petHud{display:none!important}</style>`);
document.title = "Desktop Buddy 试玩版";
