// V4 runs on the actual map, with its own beta save namespace.
(function installLiweiStory() {
  const toolbar = seasonMapTest.root.querySelector("header");
  if (!new URLSearchParams(location.search).has("liwei")) {
    const link = document.createElement("a");
    link.href = "?liwei=6";
    link.textContent = "栗尾市剧情内测 V6";
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
    dots: "neutral",
    idea: "focused",
  };
  const models = new Map(data.npcNames.map((name, i) => {
    const look = doll.normalize(LIWEI_LOOKS[name]);
    return [name, { look, ramps: doll.rampsOf(look), cache: new Map(),
      kid: name === "老郑的孙子", ph: 791 * (i + 1), dist: 0, dir: 0 }];
  }));
  const glassesCue = "我：你银行的还是法院的？你别往里迈！";
  const glassesStep = scenes.S00.rows.indexOf(glassesCue);
  const ajianWardrobe = new Map(
    ["sunglasses", "flat_glasses", "scarf"].map(accessory => {
      const look = doll.normalize({ ...models.get("阿简").look, acc: [accessory] });
      return [accessory, { look, ramps: doll.rampsOf(look), cache: new Map() }];
    })
  );
  let glassesGestureAt = -Infinity;

  function ajianAccessory() {
    if (sim.place === "front" && !p.done.includes("S00")) {
      const step = p.chapter === "S00" ? p.index : 0;
      if (step < glassesStep || step === glassesStep && performance.now() - glassesGestureAt < 180)
        return "sunglasses";
    }
    if (p.chapter === "S03") return "flat_glasses";
    if (p.chapter === "S14") return "scarf";
    return null;
  }

  function frameFor(name, actor, restingPose) {
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
    if (actor?.lookAt && !model.v) frame.look = actor.lookAt;
    if (active && name === speaker && expressions[face]) frame.expr = expressions[face];
    if (restingPose === "sleep") frame.expr = "sleepy";
    const accessory = name === "阿简" ? ajianAccessory() : null;
    if (name === "阿简" && active && p.chapter === "S00" && p.index === glassesStep &&
      performance.now() - glassesGestureAt < 360 && !reduceMotionUI) frame.wave = 1;
    return npcCanvas(ajianWardrobe.get(accessory) || model, frame, restingPose === "sit" ? "sit" : pose, false);
  }
  const heroReactions = {
    calm: ["fine", "平静"],
    curious: ["focused", "好奇"],
    eager: ["energized", "期待"],
    focused: ["focused", "专注"],
    determined: ["confident", "下定决心"],
    firm: ["focused", "态度坚定"],
    pensive: ["focused", "若有所思"],
    fascinated: ["focused", "惊讶地细看"],
    realized: ["inspired", "恍然大悟"],
    puzzled: ["dazed", "困惑"],
    surprised: ["dazed", "意外"],
    shocked: ["dazed", "震惊"],
    worried: ["tense", "担心"],
    wary: ["tense", "戒备"],
    alert: ["tense", "警觉"],
    tense: ["tense", "紧张"],
    concerned: ["tense", "担忧"],
    torn: ["tense", "犹豫"],
    uncertain: ["dazed", "没把握"],
    alarmed: ["scared", "惊慌"],
    scared: ["scared", "惊恐"],
    impatient: ["angry", "不耐烦"],
    frustrated: ["angry", "烦躁"],
    angry: ["angry", "生气"],
    wry: ["playful", "打趣"],
    playful: ["playful", "调侃"],
    unwell: ["uncomfortable", "不舒服"],
    weary: ["uncomfortable", "疲惫"],
    awkward: ["embarrassed", "有些难为情"],
    sad: ["sad", "难过"],
    disappointed: ["sad", "失落"],
    wistful: ["sad", "不舍"],
    hopeful: ["inspired", "抱有希望"],
    joyful: ["happy", "高兴"],
    relieved: ["happy", "松了一口气"],
    comforted: ["happy", "感到宽慰"],
    touched: ["happy", "被触动"],
  };
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
    scriptRevision: 6,
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
    entrance = null,
    speaker = "",
    face = "",
    heroMood = null,
    cue = "",
    since = 0,
    pastActions = new Set(),
    timer = 0,
    preview = false,
    flyNext = false,
    approaching = false,
    routeTo = null;
  const inCity = () => sim.place === "autumn_test";
  const unlocked = () => p.done.includes("S01");
  const lodging = () => where("hotel") && p.choices.S02 === 1 ? "hotel" : "detective_home";
  const firstLanding = () => inCity() && unlocked() && !p.done.includes("S02") && !p.chapter;
  const locked = () => firstLanding() || (inCity() && p.returning === "arrived") ||
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
  frontBtn.type = "button";
  frontBtn.className = "liwei-jian";
  frontBtn.setAttribute("aria-label", "与阿简交谈");
  frontBtn.hidden = true;
  view.parentElement.append(frontBtn);
  const style = document.createElement("style");
  style.textContent = `
 .liwei-controls{display:flex;flex-wrap:wrap;gap:5px;align-items:center}.liwei-controls:empty{display:none}.liwei-jian{position:absolute;z-index:10;background:transparent!important;border:none!important;box-shadow:none!important;padding:0}.liwei-caption{position:absolute;top:4%;left:50%;transform:translateX(-50%);max-width:92%;width:max-content;box-sizing:border-box;padding:.2em .7em;border-radius:5px;z-index:16;text-align:center;color:#fff6dd;background:#302d38e8;font-weight:bold;pointer-events:none}.liwei-caption[hidden],.liwei-jian[hidden]{display:none}.liwei-caption.liwei-finale{top:50%;transform:translate(-50%,-50%);padding:.6em .85em;letter-spacing:.12em;background:linear-gradient(110deg,#271d35,#55415f,#302239);border:2px solid #ffe0a2;text-shadow:0 1px #43233b;box-shadow:0 0 14px #ffdc9a8a;color:#fff2cf}.liwei-caption.liwei-evidence{display:flex;gap:5px;background:#433638}.liwei-caption.liwei-evidence[hidden]{display:none}.liwei-evidence span{max-width:12em;padding:.35em;background:#f5ead1;color:#403b37;border:1px solid #b2976c}.liwei-caption button{font:inherit;pointer-events:auto;padding:.4em .7em}
 `;
  document.head.append(style);
  function portrait(label) {
    const name = label.split("（")[0],
      index = data.npcNames.indexOf(name);
    return {
      color: colors[name],
      id: "liwei-" + label + "-" + face,
      name: label.includes("头像") ? "程青（电话）" : label,
      anonymous: index < 0 || label.includes("头像"),
      portrait: () =>
        label.includes("头像") ? null : frameFor(name),
    };
  }
  let confirmChoice = null;
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
    const introduced=["S00","S03","S04","S05","S06","S11","S05","S04","S09"];
    const complete=p.done.includes("S14");
    p.metContacts ||= {};
    for (const [i, name] of data.npcNames.entries()) {
      if (!complete && !p.done.includes(introduced[i])) continue;
      const id="autumn_"+ids[i],model=models.get(name);
      let c=socialState.contacts.find(entry=>entry.id===id);
      if (!c&&!p.metContacts[id]&&!p.castContactsAdded) {
        c={id,name,family:null,affinity:complete&&i===0?50:20,metAt:sim.t,memories:[]};
        socialState.contacts.push(c);
      }
      p.metContacts[id]=true;
      if(c){c.look=model.look;c.child=model.kid;}
    }
    if(complete)p.castContactsAdded=true;
    contactsSig = "";
  }
  const restored = restore;
  restore = function (s) {
    stop();
    routeTo = null;
    approaching = false;
    p = Object.assign(fresh(), s?.liweiV4 || {});
    if (p.chapter || p.done.length) p.enrolled = true;
    const result = restored(s);
    if (s?.liweiV4 && s.liweiV4.scriptRevision !== 6 && scenes[p.chapter]) {
      const k = p.chapter;
      p.index = 0;
      p.departed = [];
      p.cueLoc = null;
      if (k === "S02" && world.inside && ["hotel", "detective_home"].includes(world.indoorSite)) {
        p.choices = {...p.choices, S02: world.indoorSite === "hotel" ? 1 : 0};
        p.index = rows().findIndex(row => row === "!进入事务所" || row === "!进入旅馆") + 1;
      } else if (k === "S11" && p.ending && p.choices.S11 != null) {
        p.index = rows().findIndex(row => row?.choices) + 1;
      } else {
        delete p.choices[k];
        if (k === "S09" && inCity()) relocate(scenes[k].loc);
      }
      if (k === "S02") p.lodgingPrompt = true;
    }
    const savedCity = s?.seasonMapTest?.place === "autumn_test" ? s.seasonMapTest.state : s?.testAutumn;
    if (data.town && savedCity?.layoutVersion !== data.layoutVersion && inCity() && p.chapter && !world.inside) {
      const loc = p.cueLoc || scenes[p.chapter]?.loc;
      if (where(loc)) relocate(loc);
    }
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
        "这会是一个比较长的故事，确定继续吗？",
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
        {sceneConfirm:true},
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
    if (p.chapter && !active && !wiping && (inCity() || sim.place === "front")) begin(p.chapter, true);
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
    if (p.done.includes("S11")) return p.ending === "B" && (p.visitTimePassed || p.done.includes("B1") || p.done.includes("B2")) ? 4 : 3;
    if (p.done.includes("S09")) return 3;
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
      if (loc === world.indoorSite) return begin(k);
      routeTo = k;
      city.leave();
      return;
    }
    world.mapOpen = false;
    city.close();
    const spot = where(loc);
    city.goTo(spot.x, spot.y, { id: loc, storyChapter: k });
  }
  function exchange(id,channel) {
    const phase=p.done.includes("S14")?"after":"during", bank=LIWEI_CHATS[id][phase];
    const entries=bank[channel].slice();
    if(channel==="visit")entries.push(...bank.out);
    for(const row of bank.milestones||[]){
      if(row.channel===channel&&p.done.includes(row.done))entries.push(row.lines);
    }
    if(phase==="after"&&["in","out","meet"].includes(channel))
      entries.push(...(bank[p.ending+(channel==="in"?"In":"")]||[]));
    const key=[id,phase,channel].join("/"),history=p.chatHistory||={};
    let seen=history[key]||[],available=entries.filter(lines=>!seen.includes(lines[0]));
    if(!available.length){
      available=entries.filter(lines=>lines[0]!==seen.at(-1));seen=[];
    }
    const lines=pick(available);
    history[key]=[...seen,lines[0]];
    return lines.map((line,i)=>((i%2===0)===(channel==="in")?">":"")+line);
  }
  function phoneExchange(c,kind,incoming){
    if(!["call","text","video"].includes(kind)||!c?.id.startsWith("autumn_"))return null;
    const id=c.id.slice(7);
    if(!LIWEI_CHATS[id])return null;
    const lines=exchange(id,incoming?"in":kind==="text"?"text":"out");
    return {title:lines[0].replace(/^>/,""),lines,early:true,liwei:true};
  }
  function smallTalk(id){
    const name=data.npcNames[ids.indexOf(id)];
    const lines=exchange(id,"meet").map(line=>line.startsWith(">")?[name,line.slice(1)]:["我",line]);
    city.talk(lines,null,false);
  }
  function meet(id,indoors=false) {
    if(active||!LIWEI_CHATS[id])return;
    const n=actors().find(v=>v.id===id);
    const loc=indoors?"detective_home":n?.loc;
    const quest=next().find(k=>scenes[k].loc===loc);
    if(quest&&(indoors||n?.mark))return begin(quest);
    if(!p.done.includes("S14")){
      const clue={jian:next().includes("S09")?"R02":next().includes("S11")?"R03":next()[0]?.startsWith("S12")?"R12":"R01",
        qing:"R05",zhou:"R04",doctor:"R07",father:"R06",neighbor:"R11"}[id];
      const gate={R01:"S07",R05:"S03",R04:"S04",R07:"S08C",R06:"S06",R11:"S03"}[clue];
      if(clue&&(!gate||p.done.includes(gate))&&!(clue==="R06"&&p.done.includes("S09")||clue==="R11"&&p.done.includes("S11")))return begin(clue);
    }
    smallTalk(id);
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
  function jianAtOffice() {
    return p.done.includes("S02") && p.done.includes("S03") && !p.done.includes("note") &&
      !next().some(k=>k==="S11"||k==="S12A"||k==="S12B"||k==="note");
  }
  function eventNotice(words) {
    if(active)return;
    speech.show("",words,{asNpc:true,variant:"event",last:true,advance:()=>speech.hide()});
  }
  function facilityChoices(id) {
    const options = [];
    const k = next().find(k => scenes[k].loc === id || (id === "reeds" && k === "S08A"));
    if (k) options.push([scenes[k].title, () => begin(k)]);
    if (id === "canteen" && p.ending === "A" && p.done.includes("A1"))
      options.push(["查看当月公示", showAccounts]);
    return options;
  }
  function showAccounts() {
    city.panel("工人食堂 · 当月公示","旧炉已封。本月工资已发，除尘支出已列账，居民可向程青核对。",[["收起", null]]);
  }
  function siteChapter(id) {
    return next().find(k => scenes[k].loc === id ||
      k === "S11" && id === "mine_office" ||
      k === "S08A" && id === "reeds");
  }
  function site(id) {
    if (active) return true;
    const key = siteChapter(id);
    if (key) {
      begin(key);
      return true;
    }
    if (["canteen","plaza","detective_home","lookout","reeds"].includes(id)) return false;
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
  function applyHeroMood(reaction) {
    heroMood = reaction ? heroReactions[reaction] : null;
    showFace(true);
  }
  function stop() {
    active = false;
    if (heroMood) applyHeroMood(null);
    confirmChoice = null;
    entrance?.cancel();
    entrance = null;
    clearTimeout(timer);
    speech.hide();
    sceneText.hidden = true;
    sceneText.replaceChildren();
    face = speaker = cue = "";
  }
  function putPhoneAway(message) {
    if (!remoteSocial) return;
    log(message, null, remoteSocial.said);
    remoteSocial = null;
    hidePeerSay(true);
  }
  function begin(k, resume = false) {
    if (active || !scenes[k] || wiping || phoneHolds()) return;
    if (inCity()) putPhoneAway("先收起手机，等办完事再聊。");
    if (storyWaitsForPhone()) return;
    // Cover the scene before changing its occupants. Dialogue and cue timers
    // start only after the reveal, including when resuming a saved chapter.
    const reveal = view.animate([
      {filter:"brightness(0)", offset:0},
      {filter:"brightness(0)", offset:0.52},
      {filter:"brightness(1)", offset:1},
    ], {duration:reduceMotionUI ? 240 : 520, fill:"both"});
    entrance = reveal;
    active = true;
    sayQueue.length = 0;
    clearTimeout(popSay._t);
    clearTimeout(popSay._t2);
    popSay.hidden = true;
    closeRing();
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
      if (k === "S02") p.lodgingPrompt = true;
    }
    pastActions = completedActions(rows());
    applyHeroMood(LIWEI_HERO_MOODS[k].opening);
    if (inCity() && (k === "note" || k === "S07") && (!world.inside || world.indoorSite !== "detective_home"))
      relocate("detective_home", true);
    refresh();
    checkpoint();
    reveal.onfinish = () => {
      if (entrance !== reveal) return;
      entrance = null;
      reveal.cancel();
      show();
    };
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
    checkpoint();
    show();
  }
  function choose(row, i) {
    if (!active || confirmChoice) return;
    const chapter = p.chapter;
    const commit = () => {
      p.choices[chapter] = i;
      if (chapter === "S11") p.ending = i ? "B" : "A";
      advance();
    };
    if (!row.confirm && chapter !== "S11") {
      commit();
      return;
    }
    const speaker = row.speaker || "广场";
    const shownAt = performance.now();
    const confirm = () => {
      // A double-click on the first menu can land on the confirmation button.
      if (confirmChoice !== confirm || performance.now() - shownAt < 300) return;
      confirmChoice = null;
      commit();
    };
    confirmChoice = confirm;
    applyHeroMood("focused");
    speech.show(speaker, row.confirm?.[i] || "确定" + row.choices[i] + "？", {
      asNpc: true,
      choices: [
        { label: row.confirm ? "是的" : "确认", on: confirm },
        { label: row.confirm ? "我再想想" : "再想想", on: () => {
          if (confirmChoice === confirm) show();
        }},
      ],
    });
  }
  function completedActions(sequence) {
    return new Set(sequence.slice(0,p.index).filter(row => typeof row === "string" && row.startsWith("!")));
  }
  function show() {
    if (entrance) return;
    confirmChoice = null;
    clearTimeout(timer);
    sceneText.hidden = true;
    sceneText.classList.remove("liwei-finale", "liwei-evidence");
    cue = "";
    const sequence = rows();
    pastActions = completedActions(sequence);
    const row = sequence[p.index];
    if (p.chapter === "S00" && row === glassesCue)
      glassesGestureAt = reduceMotionUI ? -Infinity : performance.now();
    if (!row) {
      finish();
      return;
    }
    // Rebuild from the selected path, so returning to a choice or reloading a
    // chapter lands on the same reaction even in a run of NPC dialogue.
    const {opening, cues} = LIWEI_HERO_MOODS[p.chapter];
    let reaction = opening;
    for (let i = p.index; i >= 0; i--) {
      const beat = sequence[i];
      const key = typeof beat === "string" ? beat : beat.choices[0];
      if (!Object.hasOwn(cues, key)) continue;
      reaction = cues[key];
      break;
    }
    applyHeroMood(reaction);
    if (row.choices) {
      speaker = row.speaker || "";
      face = "";
      speech.show(row.speaker || "选择", row.prompt || "你怎么说？", {
        asNpc: true,
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
      words = row.slice(at + 1).replace(/「玩家名字」|【玩家名字】/g, () => nameOf());
    speaker = label.split("（")[0];
    face = emotionFor(words);
    speech.show(speaker === "我" ? nameOf() : label, words, {
      asNpc: speaker !== "我",
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
    if (inside) world.indoorSite = loc;
    city.syncHeight();
    world.x = inside ? 222 : pos.x;
    world.y = inside ? 108 : pos.y;
    city.clearRoute();
    city.snapCamera();
    p.cueLoc = loc;
  }
  const movementCues = /离开|进屋|登机|散场|走近|道别|栈桥|来到广场|跑进矿道/;
  function showEvent(words) {
    sceneText.hidden = true;
    speech.show("", words, {asNpc:true, variant:"event"});
  }
  function perform(action) {
    speech.hide();
    speaker = face = "";
    cue = action;
    since = performance.now();
    sceneText.replaceChildren();
    sceneText.hidden = false;

    if (action.startsWith("调查栈桥")) {
      button(sceneText, "查看木板下的管口", () => {
        showEvent("木板下藏着一根粗管，暗通矿池。");
        timer = setTimeout(advance, 1600);
      });
      return;
    }
    sceneText.textContent = action;
    if (["进入事务所", "进入旅馆", "送孩子去诊所", "矿道落石"].includes(action)) {
      sceneText.hidden = true;
      const fadeOut = view.animate([{filter:"brightness(1)"},{filter:"brightness(0)"}],
        {duration:reduceMotionUI ? 120 : 420, easing:"ease-in", fill:"forwards"});
      entrance = fadeOut;
      fadeOut.onfinish = () => {
        if (entrance !== fadeOut) return;
        if (action === "送孩子去诊所") relocate("clinic");
        else if (action !== "矿道落石") relocate(action === "进入旅馆" ? "hotel" : "detective_home", true);
        const falls = action === "矿道落石";
        const fadeIn = view.animate([{filter:"brightness(0)"},{filter:"brightness(1)"}],
          {delay:falls ? 390 : 160, duration:reduceMotionUI ? 160 : 560, easing:"ease-out", fill:"both"});
        entrance = fadeIn;
        fadeOut.cancel();
        fadeIn.onfinish = () => {
          if (entrance !== fadeIn) return;
          entrance = null;
          fadeIn.cancel();
          if (falls) {
            showEvent("把孩子扑开，石头砸在他刚才站的地方。");
            timer = setTimeout(advance, 1750);
          } else advance();
        };
      };
      return;
    }
    if (action === "数周后") {
      if (p.visitTimePassed) { advance(); return; }
      showEvent(action);
      timer = setTimeout(() => {
        p.visitTimePassed = true;
        world.stage = environment();
        advance();
      }, 1550);
      return;
    }
    if (action === "核对锅炉批号") {
      sceneText.classList.add("liwei-evidence");
      for (const label of ["旧领料单", "现役旧炉设备登记照片"]) {
        const paper = document.createElement("span");
        paper.textContent = label + " · 炉体批号一致";
        sceneText.append(paper);
      }
      sceneText.firstChild.remove();
      timer = setTimeout(advance, 2000);
      return;
    }
    if (action === "栗尾市主线剧情完结") {
      sceneText.classList.add("liwei-finale");
      sceneText.innerHTML='<i class="liwei-roll left" aria-hidden="true"></i><i class="liwei-roll right" aria-hidden="true"></i><span></span>';
      sceneText.querySelector("span").textContent=action;
      if (!reduceMotionUI) sceneText.animate([
        {"--unroll":".02",opacity:0},
        {"--unroll":".28",opacity:1,offset:.13,easing:"cubic-bezier(.3,.07,.3,1)"},
        {"--unroll":"1.04",opacity:1,offset:.41},
        {"--unroll":"1",opacity:1,offset:.49},
        {"--unroll":"1",opacity:1,offset:.86},
        {"--unroll":"1",opacity:0}
      ], {duration:4400,fill:"both"});
    }
    if (action === "维修队封住了尾矿管") p.cueLoc = "pier";
    if (action === "旧炉停运") world.stage = 3;
    if (action.startsWith("取得") || action.includes("已归档")) {
      if (!p.evidence.includes(action)) p.evidence.push(action);
    }
    if (action !== "栗尾市主线剧情完结") showEvent(action);
    const duration = action.includes("主线剧情完结")
      ? 4400
      : action.startsWith("取得")
        ? 1600
        : movementCues.test(action) ? 1850 : 1450;
    timer = setTimeout(() => {
      const leaving = {
        工人代表离开: "工人代表",
        老郑离开: "老郑",
        阿简离开: "阿简",
        程铁山进屋: "程铁山",
        程铁山登机: "程铁山",
        程青登机: "程青",
      }[action];
      if (leaving) p.departed.push(leaving);
      if (action === "诊所交接材料") p.departed.push("老郑", "老郑的孙子");
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
      log("任务完成 · " + scenes[k].title);
      gameAudio.sound("ui-result",.4,{tag:"liwei-complete"});
      world.stage = environment();
    }
    if (k === "R10" || k === "R13") p.returning = false;
    if (k === "R13") p.needsInvestigationBrief = false;
    syncCastContacts();
    if (k === "S14") {
      world.quest = 6;
      const jian = socialState.contacts.find(c => c.id === "autumn_jian");
      if (jian) {
        jian.affinity = Math.max(jian.affinity, 50);
        addSocialMemory(jian, "漫长的告别", "一起走过了栗尾市。");
      }
      showHint("与阿简的好感度达到 50 · 已解锁侦探条纹大衣");
    }
    sayQueue.length = 0;
    sayBusy = Math.max(sayBusy, realClock + 3);
    nextSay = Math.max(nextSay, realClock + 5);
    refresh();
    checkpoint();
    if (k === "S01" && !p.choices.S01) {
      flyNext = true;
      throughDoor("airport_test");
    }
    if (k === "S07" && p.choices.S07 === 1) p.needsInvestigationBrief = true;
    if (k === "R09" || (k === "S07" && p.choices.S07 === 1)) {
      p.returning = !p.done.includes("S14");
      throughDoor("home");
    }
  }
  const casting = {
    R01: [0], R02: [0], R03: [0], R04: [2], R05: [1], R06: [4],
    R07: [3], R08: [0], R09: [0], R10: [0], R11: [8], R12: [0], R13: [0],
    S02: [0],
    S03: [0, 1],
    S04: [0, 2, 7],
    S05: [0, 3, 6],
    S06: [0, 4],
    S07: [0],
    S08A: [0, 2],
    S08B: [0, 2, 6],
    S08C: [0, 3, 2, 6],
    S09: [0, 2, 8],
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
  const plazaCrowd = (data.town?.residents || []).slice(0,10).map((look,i)=>{
    const name = "广场居民"+i;
    const normalized = doll.normalize(look);
    models.set(name,{look:normalized,ramps:doll.rampsOf(normalized),cache:new Map(),ph:i*791,dist:0,dir:0});
    return name;
  });
  function addPlazaCrowd(result,loc) {
    const occupied=[world,...result];
    const spots=[];
    for(const dy of [-18,14,-10,8,34])for(const dx of [-145,-112,-85,-59,-32,1,35,61,87,114,145]){
      const x=world.x+dx,y=world.y+dy,ground=city.nearest(x,y);
      if(!ground||ground.d>4 || occupied.some(a=>Math.abs(a.x-ground.x)<23&&Math.abs(a.y-ground.y)<22))continue;
      spots.push(ground);occupied.push(ground);
    }
    const started = cue==="居民来到广场" || pastActions.has("!居民来到广场");
    if(!started)return;
    const elapsed=performance.now()-since;
    for(const [i,point] of spots.slice(0,plazaCrowd.length).entries()){
      if(!reduceMotionUI&&cue==="居民来到广场"&&elapsed<130+i*95)continue;
      result.push({id:plazaCrowd[i],name:plazaCrowd[i],loc,x:point.x,y:point.y,lookAt:Math.sign(world.x-point.x)});
    }
  }
  function actors() {
    const result = [],
      used = new Set(),
      offsets = [-27, 26, -56, 55, -82, 79, -105, 105, -127];
    function actor(seed, loc, slot, mark, staged) {
      if (used.has(seed) || p.departed.includes(data.npcNames[seed])) return;
      if (!staged && (
        (p.done.includes("S12A") && seed === 4) ||
        (p.done.includes("S12B") && seed === 1) ||
        (p.done.includes("S14") && seed === 0)
      ))
        return;
      used.add(seed);
      const spot = where(loc);
      if (!spot) return;
      let x = (staged ? world.x : spot.x) + offsets[slot],
        y = (staged ? world.y : spot.y) + (slot % 3 === 2 ? 2 : 0);
      if (staged) {
        const elapsed = reduceMotionUI ? 2000 : Math.max(0,performance.now()-since);
        const progress = (action, delay=0) => {
          if (cue !== action) return pastActions.has("!"+action) ? 1 : 0;
          const t=Math.max(0,Math.min(1,(elapsed-delay)/1460));
          return t*t*(3-2*t);
        };
        const side = Math.sign(offsets[slot]);
        if (p.chapter === "S11") {
          if (slot >= 3) y -= slot % 2 ? 5 : 9;
          x += side * Math.round(34*(1-progress("居民来到广场",slot%3*90)));
          x += side * Math.round(58*progress("散场",slot%3*75));
        }
        if (p.chapter === "S08B" && seed === 6) {
          if (cue !== "孙子跑进矿道" && !pastActions.has("!孙子跑进矿道")) return;
          x += 48 * (1-progress("孙子跑进矿道"));
          if (cue === "矿道落石" || pastActions.has("!矿道落石")) x -= 18;
        }
        if (p.chapter === "S08A") x += side*Math.round(20*(1-progress("走上栈桥")));
        if (p.chapter === "S12B") {
          if (seed === 0) x = world.x - 43;
          if (seed === 1) x += 8 - Math.round(14*progress("程青走近主角")+41*progress("程青走近阿简"));
        }
        if (p.chapter === "S12A") {
          if (seed === 4) x = world.x + 54;
          if (seed === 1) x = world.x + 22 + Math.round(12*progress("父女道别"));
        }
        const name=data.npcNames[seed];
        if (cue === name+"登机" || cue === name+"离开" || cue === name+"进屋") {
          const direction = cue.endsWith("登机") ? 1 : side;
          const destination = cue === "程铁山进屋" ? where("hut").x : x+direction*42;
          const stride = x+(destination-x)*progress(cue);
          const end = Math.max(world.camX+12,Math.min(world.camX+330,stride));
          if (world.inside) x = end;
          else while(Math.abs(end-x)>.1){
            const candidate=x+Math.sign(end-x)*Math.min(4,Math.abs(end-x));
            if(city.nearest(candidate,y)?.d>3) break;
            x=candidate;
          }
        }
      }
      if (staged && !world.inside) x = Math.max(world.camX+12,Math.min(world.camX+330,x));
      if (data.town && !world.inside) {
        const footing=city.nearest(x,y);
        if (footing && footing.d>2) {
          x=footing.x;
          y=footing.y;
        }
      }
      result.push({
        id: ids[seed],
        name: data.npcNames[seed],
        seed,
        x,
        y,
        loc,
        mark,
        sitting: !staged && (Math.floor(world.streetTime / 26) + seed * 3) % 5 === 1,
      });
    }
    if (active && scenes[p.chapter]) {
      const loc = p.cueLoc || scenes[p.chapter].loc || "plaza",
        cast = p.chapter === "S09" && loc === "clinic" ? [0,2,6,3,1] : casting[p.chapter] || [];
      cast.forEach((seed, i) => actor(seed, loc, i, false, true));
      if (p.chapter === "S08A" && p.cueLoc === "pier") {
        actor(5, "pier", 2, false, true);
        actor(1, "pier", 3, false, true);
      }
      if (p.chapter === "S11") addPlazaCrowd(result,loc);
      const target = speaker === "我" ? world : result.find(n => n.name === speaker);
      for (const n of result) {
        if (target) n.lookAt = Math.sign((n === target ? world : target).x - n.x);
        else if (p.chapter === "S12A" && cue === "父女道别" && [1,4].includes(n.seed))
          n.lookAt = n.seed === 1 ? 1 : -1;
      }
      return result.sort((a,b) => a.y-b.y);
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
      if (seed != null) actor(seed, loc, 0, p.enrolled ? "?" : "!", false);
    }
    ["detective_home", "mine_office", "canteen", "clinic", "hut"].forEach(
      (loc, seed) => {if(seed!==0 || jianAtOffice())actor(seed, loc, 0, false, false);},
    );
    for(const [seed,loc,slot] of [[5,"notice",0],[6,"canteen",1],[7,"mine_office",1],[8,"plaza",0]]){
      if(!p.metContacts?.["autumn_"+ids[seed]]||(seed===7&&p.ending==="B"&&p.done.includes("B2")))continue;
      actor(seed,loc,slot,false,false);
    }
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
  const streetPills = placeNpcPills;
  placeNpcPills = function () {
    if (active && sim.place === "front") clearNpcPills();
    else streetPills();
  };
  const drawStreetRace = drawMarathon;
  drawMarathon = function (ctx) {
    if (!(active && sim.place === "front")) drawStreetRace(ctx);
  };
  const drawStreetNpcs = drawNpcs;
  drawNpcs = function (ctx, layer) {
    if (!(active && sim.place === "front")) drawStreetNpcs(ctx, layer);
    if (sim.place !== "front" || !available() || unlocked() || wiping) return;
    const lane = heroGround != null && doorFeet > heroGround ? "backAhead" : "back";
    if (layer !== lane) return;
    const headY = doorFeet - DH + 1;
    ctx.drawImage(frameFor("阿简"), doorX - DW / 2, headY);
    if (!active) drawQuestMarker(ctx, doorX, headY, p.enrolled ? "?" : "!");
    const sx = view.clientWidth / W, sy = view.clientHeight / H;
    const buttonTop = active ? headY : headY - IMG.questMarker["!"].height - 4;
    Object.assign(frontBtn.style, {
      left: (view.offsetLeft + (doorX - DW / 2) * sx) + "px",
      top: (view.offsetTop + buttonTop * sy) + "px",
      width: DW * sx + "px", height: (doorFeet + 1 - buttonTop) * sy + "px",
    });
  };
  function drawSceneWeather(ctx) {
    if (!active || world.inside) return;
    const dust = p.chapter === "S09" && p.cueLoc !== "clinic" &&
      (cue === "旧炉喷出大量黄灰！" || pastActions.has("!旧炉喷出大量黄灰！"));
    const wind = p.chapter === "S14";
    if (!dust && !wind) return;
    const t = performance.now() / 1000, w = view.width, h = view.height;
    ctx.save();
    if (dust) {
      const alpha = cue === "旧炉喷出大量黄灰！" && !reduceMotionUI ?
        Math.min(1, (performance.now()-since)/600) : 1;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = "#b4924e70";
      ctx.fillRect(0, 0, w, h);
    }
    if (!reduceMotionUI) {
      ctx.fillStyle = dust ? "#e4bc7078" : "#e9dfbb8c";
      for (let i = 0; i < (dust ? 40 : 13); i++) {
        const x = (i * .618 + t * (dust ? .43 : .32)) % 1;
        const y = (i * .381 + .012 * Math.sin(t * 2 + i)) % 1;
        ctx.fillRect(Math.floor(x*w), Math.floor(y*h), Math.max(2,w/110)*(1+i%3), Math.max(1,h/145));
      }
    }
    ctx.restore();
  }
  const oldRender = renderOutside;
  renderOutside = function () {
    // A conversation begun before boarding cannot finish while the landing owns the clock.
    if (inCity() && (firstLanding() || p.returning === "arrived"))
      putPhoneAway("到栗尾市了，先收起手机。");
    if (firstLanding() && !wiping && world.loaded) {
      const strip = where("airstrip");
      if (world.inside || world.door || world.x !== strip.x || world.y !== strip.y) city.reset();
      begin("S02");
    }
    oldRender();
    if (inCity()) drawSceneWeather(vctx);
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
      begin(p.needsInvestigationBrief ? "R13" : "R10");
      if (active) p.returning = false;
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
      if (confirmChoice && e.repeat && (e.key === "Enter" || e.key === " ")) {
        e.stopImmediatePropagation();
        e.preventDefault();
        return;
      }
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
  questBoard.add(() => {
    if (!p.enrolled) return [];
    const completed = p.done.filter(k => scenes[k]).map(k => ({
      id: "liwei-" + k, group: "liwei", title: scenes[k].title,
      place: "栗尾市", done: true, end: "已完成",
    }));
    const current = p.done.includes("S14") ? [] : next();
    return current.map((k) => ({
          id: "liwei-" + k,
          group: "liwei",
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
        })).concat(completed);
  });
  window.liweiStory = {
    locked,
    facilityChoices,
    eventNotice,
    jianAtOffice,
    lodging,
    objective,
    unlocked,
    actors,
    frameFor,
    phoneExchange,
    visitExchange(c){
      const id=c.id.slice(7);
      if(!c.id.startsWith("autumn_")||!LIWEI_CHATS[id])return null;
      const lines=exchange(id,"visit");
      return {title:lines[0],lines};
    },
    heroMood: () => active ? heroMood : null,
    heroExpression: () =>
      active && speaker === "我" ? expressions[face] : null,
    site,
    siteChapter,
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
