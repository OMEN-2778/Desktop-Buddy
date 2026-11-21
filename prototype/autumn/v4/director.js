// V4 runs on the actual map, with its own beta save namespace.
(function installLiweiStory() {
  const toolbar = seasonMapTest.root.querySelector("header");
  if (!new URLSearchParams(location.search).has("liwei")) {
    const link = document.createElement("a");
    link.href = "?liwei=4";
    link.textContent = "栗尾市剧情内测";
    toolbar.append(link);
    return;
  }
  const city = seasonMapTest.state.autumn,
    world = city.state,
    data = city.DATA;
  const scenes = LIWEI_SCRIPT,
    where = (id) => data.landmarks.find((p) => p.id === id);
  const expressions = {
    note: "happy",
    heart: "happy",
    friend: "happy",
    sweat: "embarrassed",
    anger: "angry",
    bang: "surprised",
    question: "confused",
    swirl: "dazed",
    focus: "focused",
    dots: "sleepy",
    idea: "focused",
  };
  const models = new Map(data.npcNames.map((name, i) => {
    const look = doll.normalize(LIWEI_LOOKS[name]);
    return [name, { look, ramps: doll.rampsOf(look), cache: new Map(),
      kid: name === "老郑的孙子", ph: 791 * (i + 1), dist: 0, dir: 0 }];
  }));
  function frameFor(name, actor) {
    const model = models.get(name);
    if (!model) return null;
    if (actor) {
      const last = model.position;
      const dx = last ? actor.x - last.x : 0, dy = last ? actor.y - last.y : 0;
      const distance = Math.hypot(dx, dy);
      model.v = last?.loc === actor.loc && distance > 0 && distance < 8;
      if (model.v) {
        model.dist += distance;
        if (dx) model.dir = Math.sign(dx);
        model.walkUntil = realClock + 0.09;
      } else if (!distance && model.walkUntil > realClock) model.v = true;
      model.position = actor;
    }
    const [frame, pose] = npcFrame(model);
    if (active && name === speaker && expressions[face]) frame.expr = expressions[face];
    return npcCanvas(model, frame, pose, false);
  }
  const colors = {
    阿简: "#1c426d",
    程青: "#08746e",
    程铁山: "#98462b",
    老郑: "#725228",
    苏医生: "#745481",
    工人代表: "#495c89",
    楼上住户: "#a23e63",
    老郑的孙子: "#46713a",
    纸条: "#695c4e",
  };
  const ids = [
    "jian",
    "qing",
    "zhou",
    "doctor",
    "father",
    "mechanic",
    "child",
    "worker",
    "neighbor",
  ];
  const groups = [
    ["S00"],
    ["S01"],
    ["S02"],
    ["S03"],
    ["S04", "S05"],
    ["S06"],
    ["S07"],
    ["S08A", "S08B", "S08C"],
    ["S09"],
    ["S10"],
    ["S11"],
    ["S12"],
    ["visits"],
    ["note"],
    ["S14"],
  ];
  const fresh = () => ({
    done: [],
    choices: {},
    ending: "",
    chapter: null,
    index: 0,
    evidence: [],
    departed: [],
    enrolled: false,
  });
  let p = fresh(),
    active = false,
    speaker = "",
    face = "",
    cue = "",
    since = 0,
    timer = 0,
    preview = false,
    flyNext = false,
    approaching = false,
    routeTo = null;
  const inCity = () => sim.place === "autumn_test";
  const unlocked = () => p.done.includes("S01");
  const locked = () =>
    active || !!p.chapter ||
    approaching ||
    (sim.place === "front" && !city.modal.hidden) ||
    (inCity() && (!!world.goal?.storyChapter || world.goal?.storyWalk || !!routeTo));
  function next() {
    for (let keys of groups) {
      if (keys[0] === "S12") keys = ["S12" + p.ending];
      if (keys[0] === "visits") keys = [p.ending + "1", p.ending + "2"];
      const left = keys.filter((k) => !p.done.includes(k));
      if (left.length) return left;
    }
    return [];
  }
  const placeName = (k) => where(scenes[k].loc)?.name || "家门口";
  const objective = () =>
    next()
      .map((k) => scenes[k].title + " · " + placeName(k))
      .join(" / ") || "栗尾市主线完结";
  const display = document.createElement("div");
  display.className = "liwei-controls";
  toolbar.after(display);
  const sceneText = document.createElement("div");
  sceneText.className = "liwei-caption";
  sceneText.hidden = true;
  view.parentElement.append(sceneText);
  const frontBtn = document.createElement("button");
  frontBtn.className = "liwei-jian";
  frontBtn.setAttribute("aria-label", "与阿简交谈");
  frontBtn.innerHTML = "<b>!</b>";
  frontBtn.hidden = true;
  view.parentElement.append(frontBtn);
  const style = document.createElement("style");
  style.textContent = `
 .liwei-controls{display:flex;flex-wrap:wrap;gap:5px;align-items:center}.liwei-controls:empty{display:none}.liwei-jian{position:absolute;z-index:10;background:transparent!important;border:none!important;box-shadow:none!important;padding:0}.liwei-jian b{position:absolute;left:50%;transform:translateX(-50%);bottom:100%;color:#ffe66e;text-shadow:1px 1px #302735}.liwei-caption{position:absolute;inset:0;z-index:16;display:grid;place-content:center;text-align:center;color:white;text-shadow:1px 1px 2px #171322;background:#201d3380;font-weight:bold;animation:liweiFade .3s ease-out}.liwei-caption[hidden],.liwei-jian[hidden]{display:none}.liwei-caption button{font:inherit;padding:.5em 1em}.liwei-caption.dust{background:repeating-linear-gradient(162deg,#936e446b 0 5px,#c1a06f88 6px 11px);background-size:130% 150%;animation:dustBlow .7s linear infinite}@keyframes dustBlow{to{background-position:40px 28px}}@keyframes liweiFade{from{opacity:0}to{opacity:1}}#peerHud.quest .who{color:var(--liwei-who)}
 `;
  document.head.append(style);
  function portrait(label) {
    const name = label.split("（")[0],
      index = data.npcNames.indexOf(name);
    return {
      id: "liwei-" + label + "-" + face,
      name: label.includes("头像") ? "程青（电话）" : label,
      anonymous: index < 0 || label.includes("头像"),
      portrait: () =>
        label.includes("头像") ? null : frameFor(name),
    };
  }
  const speech = createStorySpeech({
    view,
    speakerFor: portrait,
    onClose: () => {
      if (active) show();
    },
  });
  const saved = snapshot;
  snapshot = function () {
    const s = saved();
    s.liweiV4 = JSON.parse(JSON.stringify(p));
    return s;
  };
  function syncCastContacts() {
    if (!p.done.includes("S14")) return;
    for (const [i, name] of data.npcNames.entries()) {
      const id = "autumn_" + ids[i], model = models.get(name);
      let c = socialState.contacts.find(entry => entry.id === id);
      if (!c && !p.castContactsAdded) {
        c = { id, name, family: null, affinity: i === 0 ? 50 : 20, metAt: sim.t, memories: [] };
        socialState.contacts.push(c);
      }
      if (c) {
        c.look = model.look;
        c.child = model.kid;
      }
    }
    p.castContactsAdded = true;
    contactsSig = "";
  }
  const restored = restore;
  restore = function (s) {
    stop();
    routeTo = null;
    approaching = false;
    p = Object.assign(fresh(), s?.liweiV4 || {});
    const result = restored(s);
    syncCastContacts();
    preview = !!p.enrolled;
    refresh();
    return result;
  };
  STORY_HOLDS.push(locked);
  const oldStep = step;
  step = function (...args) {
    if (!locked()) return oldStep(...args);
  };
  const oldSocial = tickSocial;
  tickSocial = function (...args) {
    if (!locked()) return oldSocial(...args);
  };
  const oldLife = tickSocialLife;
  tickSocialLife = function (...args) {
    if (!locked()) return oldLife(...args);
  };
  const oldCall = canReceiveCall;
  canReceiveCall = function () {
    return !locked() && oldCall();
  };
  function checkpoint() {
    if (typeof booted !== "undefined" && booted) autoSave();
  }
  function available() {
    return preview || seasonOf(sim.t).i === 2 || p.enrolled;
  }
  function button(parent, label, fn) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    b.onclick = fn;
    parent.append(b);
    return b;
  }
  function refresh() {
    frontBtn.hidden =
      sim.place !== "front" || !available() || unlocked() || wiping;
    frontBtn.disabled = active;
    frontBtn.lastChild.hidden = active;
    display.replaceChildren();
    if (active) return;
    if (p.chapter) {
      button(display, "继续 · " + scenes[p.chapter].title, () =>
        begin(p.chapter, true),
      );
      return;
    }
    if (inCity()) {
      for (const k of next())
        if (where(scenes[k].loc))
          button(display, scenes[k].title + " · " + placeName(k), () =>
            guide(k),
          );
      if (p.ending === "A" && p.done.includes("S12A"))
        button(display, "食堂公示", () => city.visit("canteen"));
    } else if (unlocked() && !wiping)
      button(
        display,
        sim.place === "airport_test" ? "乘机前往栗尾市" : "去机场 · 栗尾市",
        () =>
          throughDoor(
            sim.place === "airport_test" ? "autumn_test" : "airport_test",
          ),
      );
    else if (sim.place === "front" && available())
      button(display, "与门外的阿简交谈", frontStart);
    if (unlocked()) RINGS.airportFlights[2] = ["airport:liwei", "栗尾市"];
  }
  function approachJian() {
    approaching = true;
    const feet = buddyFeet();
    sim.route = [
      [feet.x, feet.y],
      [185, feet.y],
    ];
    sim.s = 0;
    sim.target = Math.abs(185 - feet.x);
    sim.facing = 185 >= feet.x ? 1 : -1;
    const distance = sim.target,
      start = performance.now();
    frontBtn.disabled = true;
    const walk = (now) => {
      sim.s = distance * Math.min(1, (now - start) / 420);
      if (sim.s < distance) {
        requestAnimationFrame(walk);
        return;
      }
      sim.target = sim.s;
      approaching = false;
      begin("S00");
    };
    requestAnimationFrame(walk);
  }
  function frontStart() {
    if (!available() || unlocked() || wiping || storyWaitsForPhone()) return;
    if (!p.done.includes("S00") && !p.enrolled) {
      city.panel(
        "秋季长篇任务",
        "开始后可以随时回家，换季后也能回来继续。现在开始吗？",
        [
          [
            "开始",
            () => {
              p.enrolled = true;
              approachJian();
            },
          ],
          [
            "再等等",
            () => {
              preview = false;
              refresh();
            },
          ],
        ],
      );
    } else begin(next()[0], !!p.chapter);
  }
  frontBtn.onclick = frontStart;
  const entry = toolbar.querySelector('[data-dest="autumn_test"]');
  entry.textContent = "栗尾市剧情内测";
  entry.onclick = () => {
    if (active || wiping) return;
    preview = true;
    if (unlocked()) {
      if (!inCity())
        throughDoor(
          sim.place === "airport_test" ? "autumn_test" : "airport_test",
        );
      else refresh();
    } else if (sim.place === "front") frontStart();
    else throughDoor("front");
  };
  const pickFlight = ringPick;
  ringPick = function (id) {
    if (id === "airport:liwei" && unlocked()) {
      closeRing();
      throughDoor("autumn_test");
      return;
    }
    return pickFlight(id);
  };
  const reach = arriveAt;
  arriveAt = function (place) {
    const r = reach(place);
    if (place === "autumn_test") {
      world.stage = environment();
      if (p.returning) p.returning = "arrived";
    }
    refresh();
    return r;
  };
  let lastPlace = "";
  setInterval(() => {
    if (typeof booted === "undefined" || !booted) return;
    if (flyNext && sim.place === "airport_test" && !wiping) {
      flyNext = false;
      throughDoor("autumn_test");
    }
    const key = [sim.place, wiping, available(), p.chapter, active].join("/");
    if (key !== lastPlace) {
      refresh();
      lastPlace = key;
    }
  }, 180);
  function environment() {
    if (p.done.includes("S11")) return p.ending === "B" ? 4 : 3;
    if (p.done.includes("S09")) return 3;
    if (p.done.includes("S08A")) return 2;
    return p.done.includes("S03") ? 1 : 0;
  }
  function guide(k) {
    if (active || wiping) return;
    if (!inCity()) {
      if (unlocked())
        throughDoor(
          sim.place === "airport_test" ? "autumn_test" : "airport_test",
        );
      else if (sim.place === "front") frontStart();
      else throughDoor("front");
      return;
    }
    window.autumnHome?.cancelActivity();
    const loc = scenes[k].loc;
    if (world.inside) {
      if (loc === "detective_home") return begin(k);
      routeTo = k;
      city.leave();
      return;
    }
    world.mapOpen = false;
    city.close();
    const spot = where(loc);
    city.goTo(spot.x, spot.y, { id: loc, storyChapter: k });
  }
  function meet(id) {
    const n = actors().find((v) => v.id === id);
    if (n) {
      const k = next().find(k => scenes[k].loc === n.loc);
      if (k) return begin(k);
      if (!["detective_home", "plaza", "canteen"].includes(n.loc) && site(n.loc)) return;
    }
    const fallback = {
      jian: next().includes("S09")
        ? "R02"
        : next().includes("S11")
          ? "R03"
          : next()[0]?.startsWith("S12")
            ? "R12"
            : "R01",
      qing: "R05",
      zhou: "R04",
      doctor: "R07",
      father: "R06",
      neighbor: "R11",
    }[id];
    if (fallback) begin(fallback);
  }
  function proximity() {
    if (
      !inCity() ||
      active ||
      world.inside ||
      world.door ||
      wiping ||
      world.mapOpen ||
      p.chapter ||
      city.modalOpen
    )
      return;
    const k = next().find((id) => id === "S09" || id === "S08A");
    if (!k) return;
    const spot = where(k === "S09" ? "canteen" : "reeds");
    if (Math.hypot(world.x - spot.x, world.y - spot.y) < 8) begin(k);
  }
  function facilityChoices(id) {
    const options = [];
    const k = next().find(k => scenes[k].loc === id || (id === "reeds" && k === "S08A"));
    if (k) options.push([scenes[k].title, () => begin(k)]);
    if (id === "canteen" && p.ending === "A" && p.done.includes("A1"))
      options.push(["查看当月公示", showAccounts]);
    if (id === "plaza" && p.done.includes("S03") && !p.done.includes("S11"))
      options.push(["和楼上住户聊聊", () => begin("R11")]);
    return options;
  }
  function showAccounts() {
    city.panel("工人食堂 · 当月公示","旧炉已封。本月工资已发，除尘支出已列账，居民可向程青核对。",[["收起", null]]);
  }
  function site(id) {
    if (active) return true;
    if (["canteen","plaza","detective_home","lookout","reeds"].includes(id)) return false;
    const key = next().find(
      (k) =>
        scenes[k].loc === id ||
        (k === "S08A" && id === "reeds") ||
        (k === "S11" && id === "mine_office"),
    );
    if (key) {
      begin(key);
      return true;
    }
    if (id === "airstrip" && p.done.includes("S14")) {
      city.panel("山顶停机坪", "航班已开放。", [
        ["返回小屋", () => throughDoor("home")],
        ["再逛逛", null],
      ]);
      return true;
    }
    if (id === "airstrip") {
      city.panel("山顶停机坪", "往返航班已开放。", [
        ["返回小屋", () => begin("R09")],
        ["再逛逛", null],
      ]);
      return true;
    }
    if (
      id === "notice" &&
      p.ending === "A" &&
      p.done.includes("A1")
    ) {
      showAccounts();
      return true;
    }
    const ambient = {
      hut: p.done.includes("S06") ? "R06" : "R08",
      mine_office: "R05",
      clinic: "R07",
    };
    if (ambient[id]) {
      const gate = {
        R05: "S03",
        R04: "S04",
        R07: "S08C",
        R06: "S06",
        R11: "S03",
      }[ambient[id]];
      if (
        (gate && !p.done.includes(gate)) ||
        (ambient[id] === "R06" && p.done.includes("S09")) ||
        (ambient[id] === "R11" && p.done.includes("S11"))
      ) {
        city.panel(where(id).name, objective(), [["收起", null]]);
        return true;
      }
      begin(ambient[id]);
      return true;
    }
    if (["townhall", "notice"].includes(id)) {
      city.panel(where(id).name, objective(), [["知道了", null]]);
      return true;
    }
    return false;
  }
  const nav = city.root.querySelector("[data-goal]");
  nav.onclick = () => {
    if (active) return;
    city.panel(
      "当前线索",
      objective(),
      next().map((k) => [placeName(k), () => guide(k)]),
    );
  };
  city.root.querySelector("[data-exit]").onclick = () => {
    if (!active) begin("R09");
  };
  function stop() {
    active = false;
    clearTimeout(timer);
    speech.hide();
    sceneText.hidden = true;
    sceneText.replaceChildren();
    face = speaker = cue = "";
  }
  function begin(k, resume = false) {
    if (active || !scenes[k] || wiping || storyWaitsForPhone()) return;
    if (inCity()) window.autumnHome?.cancelActivity();
    city.close();
    city.clearKeys();
    city.clearRoute();
    world.service = world.pose = null;
    if (!resume) {
      p.chapter = k;
      p.index = 0;
      p.departed = [];
      p.cueLoc = null;
      delete p.choices[k];
    }
    if (inCity() && (k === "note" || k === "S07") && !world.inside)
      relocate("detective_home", true);
    active = true;
    refresh();
    checkpoint();
    show();
  }
  function rows() {
    const k = p.chapter,
      out = [];
    for (const row of scenes[k].rows) {
      if (typeof row === "string") out.push(row);
      else if (row.choices) {
        out.push(row);
        if (p.choices[k] != null) out.push(...row.paths[p.choices[k]]);
      } else if (row.ending) out.push(...row.ending[p.ending === "B" ? 1 : 0]);
      else if (row.arrival) out.push(...row.arrival[p.choices.S01 || 0]);
    }
    return out;
  }
  function advance() {
    if (!active) return;
    p.index++;
    show();
  }
  function choose(row, i) {
    const commit = () => {
      p.choices[p.chapter] = i;
      if (p.chapter === "S11") p.ending = i ? "B" : "A";
      checkpoint();
      advance();
    };
    if (p.chapter === "S11") {
      speech.show("广场", "确定" + row.choices[i] + "？", {
        choices: [
          { label: "确认", on: commit },
          { label: "再想想", on: show },
        ],
      });
      return;
    }
    commit();
  }
  function show() {
    clearTimeout(timer);
    sceneText.hidden = true;
    cue = "";
    const row = rows()[p.index];
    if (!row) {
      finish();
      return;
    }
    if (row.choices) {
      face = "";
      speech.show("选择", "你怎么说？", {
        choices: row.choices.map((label, i) => ({
          label,
          on: () => choose(row, i),
        })),
      });
      return;
    }
    if (row.startsWith("!")) {
      perform(row.slice(1));
      return;
    }
    const at = row.indexOf(
        "：",
        row.includes("）") && row.indexOf("（") < row.indexOf("：")
          ? row.indexOf("）") + 1
          : 0,
      ),
      label = row.slice(0, at),
      words = row.slice(at + 1);
    speaker = label.split("（")[0];
    face = emotionFor(words);
    peerHud.style.setProperty("--liwei-who", colors[speaker] || "#54465c");
    speech.show(speaker === "我" ? nameOf() : label, words, {
      advance,
      last: p.index === rows().length - 1,
    });
  }
  const accents = {
    "您好，找这房子的主人。": "focus",
    "……？！": "bang",
    "你银行的还是法院的？你别往里迈！": "anger",
    "先说清楚，这套房没通过产权核查，抵押没生效。": "dots",
    "女儿查亲爹……拿我房子助兴呢？": "swirl",
    "飞机上挺好。你们这儿的空气……咳，咳咳！": "sweat",
    "我需要防毒面具！": "bang",
    小时候住隔壁呢: "friend",
    "打扰一下。两位叙旧能先等等吗，打印机都卡纸了": "swirl",
    "……简家那小子？": "idea",
    "我可还没说这是哪儿呢。": "focus",
    "别跑，口罩戴好。": "sweat",
    "是我填的。": "dots",
    "……挑哪家都一样。": "dots",
    "我给程青打电话（掏出手机）。": "focus",
    "第一个看不清，第二个……姓简？": "bang",
    "……先别翻了。说正事吧。": "dots",
    "爷爷，我渴了。这回的药还是上次那个甜的吗？": "question",
    "坏了，我孙子去外头买冰棍呢！": "bang",
    "……或者说我赌你会来问。": "dots",
    "真会算账啊。": "anger",
    "关了吧。": "focus",
    "留着吧。": "focus",
    "有存款。降压药记得吃。": "heart",
    "今天炖了排骨。": "note",
    "回见。": "dots",
    "我知道你想说什么。": "dots",
    "……也挺好的。现在住在这儿的人是你。": "heart",
    "我再吹会儿风。": "leaf",
    "你还真会找话题。": "note",
  };
  function emotionFor(line) {
    if (accents[line]) return accents[line];
    if (/节哀|抢救无效|对不起|……回见|一路顺风|没什么不能说/.test(line))
      return "sweat";
    if (/别往里迈|风凉话|别喊了|胡来|全赖|谁填的/.test(line)) return "anger";
    if (/……？！|吓得|房东让我|坏了|漏气|怎么还通着/.test(line)) return "bang";
    if (/？$/.test(line) && line.length < 18) return "question";
    if (/哈哈|大气呀|工资刚发|回来了|墙刷得挺白/.test(line)) return "note";
    if (/连饭都|撬不出|看花眼|谁也不接谁/.test(line)) return "swirl";
    if (/先别翻了|没什么为什么|两清了|把话说完整/.test(line)) return "dots";
    if (/签字|写清楚|算账|对过了/.test(line)) return "focus";
    if (/认出来|总算|难怪/.test(line)) return "idea";
    return "";
  }
  function relocate(loc, inside = false) {
    const pos = where(loc);
    world.inside = inside;
    world.x = inside ? 172 : pos.x;
    world.y = inside ? 108 : pos.y;
    city.clearRoute();
    world.camX = inside
      ? 0
      : Math.max(0, Math.min(data.width - 342, world.x - 171));
    world.camY = inside
      ? 0
      : Math.max(0, Math.min(data.height - 236, world.y - 118));
    p.cueLoc = loc;
  }
  function perform(action) {
    speech.hide();
    face = "";
    cue = action;
    since = performance.now();
    sceneText.replaceChildren();
    sceneText.hidden = false;
    sceneText.classList.toggle("dust", action.includes("黄灰"));
    if (action.startsWith("调查栈桥")) {
      button(sceneText, "查看木板下的管口", () => {
        sceneText.textContent = "木板下藏着一根粗管，暗通矿池。";
        timer = setTimeout(advance, 1000);
      });
      return;
    }
    sceneText.textContent = action;
    if (["人群安静下来", "广场抉择"].includes(action))
      view.animate(
        [
          { filter: "brightness(.82)", transform: "scale(1.018)" },
          { filter: "brightness(1)", transform: "scale(1)" },
        ],
        { duration: 800 },
      );
    if (action === "进入事务所") relocate("detective_home", true);
    if (action === "送孩子去诊所") relocate("clinic");
    if (action === "维修队封住了尾矿管") p.cueLoc = "pier";
    if (action === "河水渐清") world.stage = 2;
    if (action === "旧炉停运") world.stage = 3;
    if (action.startsWith("取得") || action.includes("已归档")) {
      if (!p.evidence.includes(action)) p.evidence.push(action);
    }
    const duration = action.includes("主线剧情完结")
      ? 3000
      : action.startsWith("取得")
        ? 1200
        : 850;
    timer = setTimeout(() => {
      const leaving = {
        工人代表离场: "工人代表",
        老郑离场: "老郑",
        阿简离场: "阿简",
        程铁山进屋: "程铁山",
        程铁山登机: "程铁山",
        程青登机: "程青",
        父女道别: "程青",
      }[action];
      if (leaving) p.departed.push(leaving);
      advance();
    }, duration);
  }
  function finish() {
    const k = p.chapter;
    stop();
    p.chapter = null;
    p.index = 0;
    p.departed = [];
    p.cueLoc = null;
    if (!k.startsWith("R") && !p.done.includes(k)) {
      p.done.push(k);
      log("栗尾市 · " + scenes[k].title);
      world.stage = environment();
    }
    if (k === "S14") {
      world.quest = 6;
      syncCastContacts();
      const jian = socialState.contacts.find(c => c.id === "autumn_jian");
      if (jian) {
        jian.affinity = Math.max(jian.affinity, 50);
        addSocialMemory(jian, "漫长的告别", "一起走过了栗尾市。");
      }
      showHint("与阿简的好感度达到 50 · 已解锁侦探条纹大衣");
    }
    refresh();
    checkpoint();
    if (k === "S01" && !p.choices.S01) {
      flyNext = true;
      throughDoor("airport_test");
    }
    if (k === "R09" || (k === "S07" && p.choices.S07 === 1)) {
      p.returning = !p.done.includes("S14");
      throughDoor("home");
    }
  }
  const casting = {
    S02: [0],
    S03: [0, 1],
    S04: [0, 2, 7],
    S05: [0, 3, 6],
    S06: [0, 4],
    S07: [0],
    S08A: [0, 2],
    S08B: [0, 2],
    S08C: [0, 3, 2, 6],
    S09: [0, 2, 8, 3, 1],
    S10: [0, 4],
    S11: [0, 1, 4, 2, 3, 7, 8, 6, 5],
    S12A: [0, 4, 1],
    S12B: [0, 1, 4],
    A1: [2],
    A2: [3],
    B1: [3, 6],
    B2: [2],
    note: [],
    S14: [0],
  };
  function actors() {
    const result = [],
      used = new Set(),
      offsets = [-27, 26, -56, 55, -82, 79, -105, 105, -127];
    function actor(seed, loc, slot, mark, staged) {
      if (used.has(seed) || p.departed.includes(data.npcNames[seed])) return;
      if (
        (p.done.includes("S12A") && seed === 4) ||
        (p.done.includes("S12B") && seed === 1) ||
        (p.done.includes("S14") && seed === 0)
      )
        return;
      used.add(seed);
      const spot = where(loc);
      if (!spot) return;
      let x = (staged ? world.x : spot.x) + offsets[slot],
        y = (staged ? world.y : spot.y) + (slot % 3 === 2 ? 2 : 0);
      const progress = Math.min(1, (performance.now() - since) / 780);
      if (staged && cue) {
        if (
          (cue.includes("离场") && cue.startsWith(data.npcNames[seed])) ||
          (cue.includes("登机") && cue.startsWith(data.npcNames[seed])) ||
          cue === "散场"
        )
          x += Math.round(progress * 38);
        if (cue === "走上栈桥" || cue === "居民来到广场")
          x += Math.round((1 - progress) * (slot % 2 ? 32 : -32));
        if (cue === "程青走近阿简" && seed === 1)
          x -= Math.round(progress * 32);
        if (
          (cue === "父女道别" && seed === 4) ||
          (cue === "程青走近主角" && seed === 1)
        )
          x -= Math.round(progress * 12);
      }
      result.push({
        id: ids[seed],
        name: data.npcNames[seed],
        seed,
        x,
        y,
        loc,
        mark,
      });
    }
    if (active && scenes[p.chapter]) {
      const loc = p.cueLoc || scenes[p.chapter].loc || "plaza",
        cast = casting[p.chapter] || [0, 1, 2, 3, 4];
      cast.forEach((seed, i) => actor(seed, loc, i, false, true));
      if (p.chapter === "S08A" && p.cueLoc === "pier")
        actor(1, "pier", 2, false, true);
      return result;
    }
    for (const k of next()) {
      const loc = scenes[k]?.loc;
      if (!where(loc)) continue;
      const seed = {
        S02: 0,
        S03: 1,
        S04: 2,
        S05: 3,
        S06: 4,
        S07: 0,
        S08A: 2,
        S08B: 2,
        S08C: 3,
        S09: 2,
        S10: 4,
        S11: 1,
        S12A: 4,
        S12B: 1,
        A1: 2,
        A2: 3,
        B1: 3,
        B2: 2,
        S14: 0,
      }[k];
      if (seed != null) actor(seed, loc, 0, true, false);
    }
    ["detective_home", "mine_office", "canteen", "clinic", "hut"].forEach(
      (loc, seed) => actor(seed, loc, 0, false, false),
    );
    return result;
  }
  function draw(ctx, images) {
    const cast = actors();
    if (world.inside && active)
      for (const n of cast)
        ctx.drawImage(
          frameFor(n.name, n) || images.get(data.npcs[n.seed][0]),
          n.x - 10,
          n.y - 28,
        );
    if (active && face) {
      const target =
        speaker === "我" ? world : cast.find((a) => a.name === speaker);
      if (target) ctx.drawImage(emoteCanvas(face), target.x + 4, target.y - 43);
    }
  }
  // Draw on the same pavement layer and pixel grid as other pedestrians.
  const doorX = 209, doorFeet = 107;
  const drawStreetNpcs = drawNpcs;
  drawNpcs = function (ctx, layer) {
    drawStreetNpcs(ctx, layer);
    if (sim.place !== "front" || !available() || unlocked() || wiping) return;
    const lane = heroGround != null && doorFeet > heroGround ? "backAhead" : "back";
    if (layer !== lane) return;
    ctx.drawImage(frameFor("阿简"), doorX - DW / 2, doorFeet - DH + 1);
    const sx = view.clientWidth / W, sy = view.clientHeight / H;
    Object.assign(frontBtn.style, {
      left: (view.offsetLeft + (doorX - DW / 2) * sx) + "px",
      top: (view.offsetTop + (doorFeet - DH + 1) * sy) + "px",
      width: DW * sx + "px", height: DH * sy + "px",
    });
  };
  const oldRender = renderOutside;
  renderOutside = function () {
    oldRender();
    if (sim.place === "front" && active && face) {
      const scale = view.width / 342,
        pt = buddyFeet();
      vctx.save();
      vctx.scale(scale, scale);
      vctx.drawImage(
        emoteCanvas(face),
        speaker === "我" ? pt.x + 4 : doorX + 4,
        speaker === "我" ? pt.y - 43 : doorFeet - 43,
      );
      vctx.restore();
    }
    proximity();
    if (routeTo && (!inCity() || (world.inside && !world.door && world.goal?.id !== "exit_inside"))) routeTo = null;
    if (routeTo && !world.inside && !world.door) {
      const target = routeTo;
      routeTo = null;
      guide(target);
    }
    if (inCity() && p.returning === "arrived" && !wiping && !active) {
      p.returning = false;
      begin("R10");
    }
  };
  const prevThrough = throughDoor;
  throughDoor = function (dest) {
    if (active) return;
    if (dest === "autumn_test" && !unlocked()) {
      showHint("先去家门口见阿简");
      return;
    }
    return prevThrough(dest);
  };
  // Staging owns pointer input until the current cue finishes.
  view.parentElement.addEventListener(
    "pointerdown",
    (e) => {
      if (active && e.target === view) {
        e.stopImmediatePropagation();
        e.preventDefault();
      }
    },
    true,
  );
  toolbar.addEventListener(
    "click",
    (e) => {
      if (active) {
        e.preventDefault();
        e.stopImmediatePropagation();
      }
    },
    true,
  );
  city.root.addEventListener(
    "click",
    (e) => {
      if (active) {
        e.preventDefault();
        e.stopImmediatePropagation();
      }
    },
    true,
  );
  document.addEventListener(
    "keydown",
    (e) => {
      if (
        active &&
        [
          "ArrowLeft",
          "ArrowRight",
          "ArrowUp",
          "ArrowDown",
          "a",
          "w",
          "s",
          "d",
        ].includes(e.key)
      ) {
        e.stopImmediatePropagation();
        e.preventDefault();
      }
    },
    true,
  );
  questBoard.add(() =>
    p.enrolled
      ? next().map((k) => ({
          title: scenes[k].title,
          step: "前往" + placeName(k),
          place: "栗尾市",
          log: p.evidence.map((title) => ({
            day: Math.floor(sim.t / 1440),
            title,
            lines: [],
          })),
          go: () => {
            if (active) return "正在对话";
            guide(k);
            return true;
          },
        }))
      : [],
  );
  window.liweiStory = {
    locked,
    facilityChoices,
    objective,
    unlocked,
    actors,
    frameFor,
    heroExpression: () =>
      active && speaker === "我" ? expressions[face] : null,
    site,
    meet,
    draw,
    guide,
    begin,
    show,
    next,
    get progress() {
      return p;
    },
    get active() {
      return active;
    },
  };
  refresh();
})();
