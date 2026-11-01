// Full-game TEST controller, no independent RAF. One continuous orthogonal route graph.
function makeSeason_autumn(opts, DATA) {
    const canvas = document.createElement("canvas");
    canvas.width = 342;
    canvas.height = 236;
    const renderCanvas = document.createElement("canvas");
    let resolution = 1, ctx = renderCanvas.getContext("2d");
    const root = document.createElement("section");
    root.className = "season-controller";
    root.dataset.kind = "autumn";
    root.hidden = true;
    root.innerHTML = '<div class="controls"><strong>枫叶城</strong><button data-map>全城地图</button><button data-home>阿简的家</button><button data-goal>当前线索</button><button data-exit>返回小屋</button></div><p data-status></p>';
    const modal = document.createElement("section");
    modal.className = "autumn-panel";
    modal.hidden = true;
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    opts.view.parentElement.append(modal);
    const foregroundAlpha = new Map;
    let frameDt = 0;
    const headCanvas = document.createElement("canvas");
    headCanvas.width = 20;
    headCanvas.height = 28;
    const headCtx = headCanvas.getContext("2d");
    const keys = new Set, images = new Map, fx = makeSeasonEffects();
    let weatherKind = "clear";
    let hover = null, dialog = null, lastFocus = null;
    const state = {
        loaded: false,
        x: DATA.landmarks[0].x,
        y: DATA.landmarks[0].y,
        camX: DATA.landmarks[0].x - 171,
        camY: DATA.landmarks[0].y - 122,
        facing: -1,
        time: 0,
        paused: false,
        walk: false,
        inside: false,
        target: null,
        route: [],
        goal: null,
        service: null,
        door: null,
        quest: 0,
        stage: 0,
        flags: {},
        found: [],
        mapOpen: false,
        autoAt: 0,
        layoutVersion: DATA.layoutVersion,
        liftY: DATA.lift.bottom,
        riding: false,
        keyboard: false
    };
    const clamp = (v, a, b) => Math.max(a, Math.min(b, v)), dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
    const nodes = [], edges = [], nodeMap = new Map;
    function node(x, y) {
        const k = x + "," + y;
        if (!nodeMap.has(k)) {
            nodeMap.set(k, nodes.length);
            nodes.push({
                x: x,
                y: y,
                links: []
            });
        }
        return nodeMap.get(k);
    }
    for (const [, points] of DATA.routes) for (const [x, y] of points) node(x, y);
    for (const [name, points] of DATA.routes) for (let i = 1; i < points.length; i++) {
        const [ax, ay] = points[i - 1], [bx, by] = points[i];
        if (ax !== bx && ay !== by) throw Error("Autumn route must be orthogonal");
        const list = nodes.map((n, j) => ({
            n: n,
            j: j
        })).filter(({n: n}) => ax === bx ? n.x === ax && n.y >= Math.min(ay, by) && n.y <= Math.max(ay, by) : n.y === ay && n.x >= Math.min(ax, bx) && n.x <= Math.max(ax, bx)).sort((a, b) => ax === bx ? a.n.y - b.n.y : a.n.x - b.n.x);
        for (let j = 1; j < list.length; j++) {
            const a = list[j - 1].j, b = list[j].j;
            if (edges.some(e => e.a === a && e.b === b)) continue;
            const kind = name === "货运升降机" && ax === bx ? "lift" : ax === bx ? "stairs" : "street", id = edges.length;
            edges.push({
                a: a,
                b: b,
                kind: kind
            });
            nodes[a].links.push({
                to: b,
                id: id
            });
            nodes[b].links.push({
                to: a,
                id: id
            });
        }
    }
    const indoorNodes = [ {
        x: 29,
        y: 204
    }, {
        x: 67,
        y: 204
    }, {
        x: 154,
        y: 204
    }, {
        x: 180,
        y: 204
    }, {
        x: 250,
        y: 204
    }, {
        x: 154,
        y: 102
    }, {
        x: 75,
        y: 102
    }, {
        x: 110,
        y: 102
    }, {
        x: 269,
        y: 102
    } ];
    const indoorPairs = [ [ 0, 1 ], [ 1, 2 ], [ 2, 3 ], [ 3, 4 ], [ 2, 5 ], [ 5, 6 ], [ 6, 7 ], [ 5, 8 ] ];
    function graph() {
        if (!state.inside) return {
            nodes: nodes,
            edges: edges
        };
        return {
            nodes: indoorNodes,
            edges: indoorPairs.map(([a, b]) => ({
                a: a,
                b: b,
                kind: indoorNodes[a].y === indoorNodes[b].y ? "street" : "stairs"
            }))
        };
    }
    function nearest(x, y, g = graph()) {
        let best = null;
        for (let i = 0; i < g.edges.length; i++) {
            const e = g.edges[i], a = g.nodes[e.a], b = g.nodes[e.b], dx = b.x - a.x, dy = b.y - a.y, t = clamp(((x - a.x) * dx + (y - a.y) * dy) / (dx * dx + dy * dy), 0, 1), p = {
                x: a.x + t * dx,
                y: a.y + t * dy
            }, d = Math.hypot(x - p.x, y - p.y);
            if (!best || d < best.d) best = {
                ...p,
                d: d,
                id: i,
                e: e
            };
        }
        return best;
    }
    function plan(x, y) {
        const g = graph(), a = nearest(state.x, state.y, g), b = nearest(x, y, g), ns = [ ...g.nodes.map(n => ({
            x: n.x,
            y: n.y
        })), a, b ], start = ns.length - 2, end = ns.length - 1, adj = ns.map(() => []);
        const connect = (i, j, kind) => {
            const cost = dist(ns[i], ns[j]) * (kind === "stairs" ? 1.3 : kind === "lift" ? .55 : 1);
            adj[i].push({
                to: j,
                cost: cost,
                kind: kind
            });
            adj[j].push({
                to: i,
                cost: cost,
                kind: kind
            });
        };
        for (const e of g.edges) connect(e.a, e.b, e.kind);
        for (const [idx, p] of [ [ start, a ], [ end, b ] ]) for (const n of [ p.e.a, p.e.b ]) connect(idx, n, p.e.kind);
        if (a.id === b.id) connect(start, end, a.e.kind);
        const scores = ns.map(() => Infinity), previous = [], open = new Set(ns.map((_, i) => i));
        scores[start] = 0;
        while (open.size) {
            let k = -1;
            for (const i of open) if (k < 0 || scores[i] < scores[k]) k = i;
            if (k === end || !Number.isFinite(scores[k])) break;
            open.delete(k);
            for (const e of adj[k]) if (scores[k] + e.cost < scores[e.to]) {
                scores[e.to] = scores[k] + e.cost;
                previous[e.to] = {
                    from: k,
                    kind: e.kind
                };
            }
        }
        if (!Number.isFinite(scores[end])) return [];
        const route = [];
        for (let i = end; i !== start; ) {
            const prev = previous[i];
            if (!prev) return [];
            route.unshift({
                ...ns[i],
                kind: prev.kind
            });
            i = prev.from;
        }
        return route.filter((p, i) => i || dist(p, state) > .01);
    }
    function clearRoute() {
        state.target = null;
        state.route = [];
        state.goal = null;
        state.walk = false;
    }
    function goTo(x, y, goal = null) {
        if (state.door) return false;
        state.service = null;
        state.pose = null;
        state.mapOpen = false;
        const path = plan(x, y);
        if (!path.length) {
            clearRoute();
            if (Math.hypot(x - state.x, y - state.y) < 1) {
                state.goal = goal;
                arrive();
                return true;
            }
            return false;
        }
        state.route = path;
        state.target = state.route.shift();
        state.goal = goal;
        state.autoAt = opts.now() + 45;
        return true;
    }
    const landmark = id => DATA.landmarks.find(p => p.id === id);
    function visit(id, need = null, automatic = false) {
        const p = landmark(id);
        if (!p) return false;
        close();
        return goTo(p.x, p.y, {
            id: id,
            need: need,
            automatic: automatic
        });
    }
    function pauseModal() {
        lastFocus = document.activeElement;
        modal.hidden = false;
        modal.innerHTML = "";
        const dismiss = document.createElement("button");
        dismiss.className = "autumn-close";
        dismiss.type = "button";
        dismiss.textContent = "×";
        dismiss.setAttribute("aria-label", "关闭");
        dismiss.onclick = close;
        modal.append(dismiss);
        clearKeys();
    }
    function close() {
        dialog = null;
        modal.hidden = true;
        modal.replaceChildren();
        if (lastFocus?.isConnected) lastFocus.focus();
        lastFocus = null;
    }
    function panel(title, text, choices) {
        pauseModal();
        const h = document.createElement("h2");
        h.textContent = title;
        const body = document.createElement("div");
        body.className = "autumn-panel-body";
        const p = document.createElement("p");
        p.textContent = text;
        body.append(p);
        const actions = document.createElement("div");
        actions.className = "autumn-actions";
        for (const [label, fn] of choices) {
            const b = document.createElement("button");
            b.textContent = label;
            b.onclick = () => {
                close();
                fn?.();
            };
            actions.append(b);
        }
        modal.append(h, body, actions);
        actions.querySelector("button")?.focus();
    }
    function talk(lines, done) {
        pauseModal();
        let i = 0;
        dialog = {
            lines: lines,
            done: done
        };
        const h = document.createElement("h2"), body = document.createElement("div");
        body.className = "autumn-panel-body";
        const p = document.createElement("p");
        body.append(p);
        const actions = document.createElement("div");
        actions.className = "autumn-actions";
        const next = document.createElement("button");
        actions.append(next);
        modal.append(h, body, actions);
        const show = () => {
            const [who, text] = lines[i];
            h.textContent = who === "我" ? opts.heroName() : who;
            p.textContent = text;
            next.textContent = i === lines.length - 1 ? "说完了" : "继续";
        };
        next.onclick = () => {
            opts.record((lines[i][0] === "我" ? opts.heroName() : lines[i][0]) + "：" + lines[i][1]);
            i++;
            if (i >= lines.length) {
                close();
                done?.();
                updateStatus();
            } else show();
        };
        show();
        next.focus();
    }
    function chapter(q, stage, entry) {
        state.quest = q;
        state.stage = stage;
        opts.record(entry);
        state.autoAt = opts.now() + 25;
    }
    function npcRows() {
        return [ [ "jian", "阿简", state.quest === 0 ? "airstrip" : "plaza", "m", 0 ], [ "qing", "程青", "mine_office", "f", 1 ], [ "zhou", "老周", "canteen", "m", 2 ], [ "doctor", "苏医生", "clinic", "f", 3 ], ...state.quest >= 2 ? [ [ "father", "程铁山", "hut", "m", 4 ] ] : [] ].map(([id, name, loc, gender, seed]) => ({
            id: id,
            name: name,
            gender: gender,
            seed: seed,
            x: landmark(loc).x - 22,
            y: landmark(loc).y
        }));
    }
    const objective = () => [ "先和停机坪的阿简说说话", "去公司、食堂、诊所问问程铁山的下落", "到山上的小屋找程铁山", "再去诊所、食堂和公司看看", "去公司看账本，再到市政厅参加公开讨论", "把带来的枫树苗种到中城广场", "枫叶城已开放，想逛多久都行" ][state.quest] || "四处逛逛";
    function converse(id) {
        const q = state.quest, f = state.flags;
        if (q === 1 && [ "qing", "zhou", "doctor" ].every(n => f["heard_" + n])) return talk(AUTUMN_STORY.dust, () => chapter(2, 1, "运输车盖上了篷布，工人街开始洒水。山上的小屋也许有人。"));
        if (id === "jian" && q === 0) return talk(AUTUMN_STORY.intro, () => chapter(1, 0, "借住阿简的老房子，开始寻找程铁山。"));
        if (q === 1 && [ "qing", "zhou", "doctor" ].includes(id) && !f["heard_" + id]) return talk(AUTUMN_STORY[id === "qing" ? "qing1" : id === "zhou" ? "zhou1" : "su1"], () => {
            f["heard_" + id] = true;
            if ([ "qing", "zhou", "doctor" ].every(n => f["heard_" + n])) talk(AUTUMN_STORY.dust, () => chapter(2, 1, "运输车盖上了篷布，工人街开始洒水。山上的小屋也许有人。"));
        });
        if (id === "father" && q === 2) return talk(AUTUMN_STORY.father, () => chapter(3, 2, "找到程铁山；旧排水口封住了，河水开始变清。老周少了一班活。"));
        if (q === 3 && id === "doctor" && !f.letter) return talk(AUTUMN_STORY.doctor, () => {
            f.letter = true;
        });
        if (q === 3 && id === "zhou" && f.letter && !f.zhouLetter) return talk(AUTUMN_STORY.zhou3, () => {
            f.zhouLetter = true;
        });
        if (q === 3 && id === "qing" && f.zhouLetter) return talk(AUTUMN_STORY.qing3, () => chapter(4, 3, "旧炉停了。程青准备把账本公开，去公司看看。"));
        if (id === "qing" && q === 4 && !f.ledger) return talk(AUTUMN_STORY.ledger, () => {
            f.ledger = true;
            opts.record("账本和检测报告准备好了，去市政厅，再到广场公开讨论。");
        });
        return talk(AUTUMN_STORY.ambient[id]);
    }
    function beginService(need, location) {
        const names = {
            hunger: "吃点热饭",
            energy: "睡一会儿",
            hygiene: "洗个澡",
            bladder: "上厕所",
            social: "聊聊天",
            fun: "歇一歇，看看书"
        };
        state.service = {
            need: need,
            location: location,
            elapsed: 0
        };
        state.pose = [ "energy", "social", "fun" ].includes(need) || need === "hunger" && !state.inside ? "sit" : null;
        opts.record((state.inside ? "在阿简家里" : location) + "，" + names[need] + "。");
    }
    function enter(automaticNeed = null) {
        state.door = {
            elapsed: 0,
            to: true,
            need: automaticNeed
        };
        clearRoute();
    }
    function leave() {
        close();
        goTo(29, 204, {
            id: "exit_inside"
        });
    }
    function arrive() {
        const goal = state.goal;
        state.goal = null;
        if (!goal) return;
        if (goal.id === "exit_inside") {
            state.door = {
                elapsed: 0,
                to: false
            };
            return;
        }
        if (goal.id === "inside_service") {
            beginService(goal.need, "阿简的家");
            return;
        }
        if (goal.id === "detective_home" && goal.automatic) {
            enter(goal.need);
            return;
        }
        if (goal.id.startsWith("npc:")) {
            converse(goal.id.slice(4));
            return;
        }
        if (goal.need) {
            beginService(goal.need, landmark(goal.id).name);
            return;
        }
        interact(goal.id);
    }
    function interact(id) {
        const p = landmark(id);
        if (!p) return;
        if (id === "detective_home") return panel(p.name, "阿简留下了钥匙。床铺、厨房和洗漱间都能用。", [ [ "进屋", () => enter() ], [ "先不进去" ] ]);
        if (id === "hut") return state.quest >= 2 ? converse("father") : panel("山上的小屋", "门虚掩着。先把公司的消息和诊所那边的情况问清楚。", [ [ "好" ] ]);
        if (id === "mine_office") return state.quest >= 6 ? talk(AUTUMN_STORY.office) : converse("qing");
        if (id === "clinic") return converse("doctor");
        if (id === "townhall" && state.quest === 4 && state.flags.ledger) return talk(AUTUMN_STORY.meeting, () => chapter(5, 4, "公开讨论结束。矿区开始分步转型，烟囱停了；也有人准备离开。把那棵枫树种下来吧。"));
        if (id === "plaza" && state.quest === 5) return panel("广场上的空地", "带来的枫树苗可以种在这里。", [ [ "种下树苗", () => talk(AUTUMN_STORY.planting, () => {
            state.flags.tree = true;
            chapter(6, 4, "枫树苗种在中城广场。枫叶城从此全年开放；办公室想去就去，不去也没关系。");
        }) ], [ "等一会儿" ] ]);
        if (id === "notice") return panel(p.name, state.quest < 4 ? "墙上贴着运输安排，几张纸被灰盖住了。" : state.quest < 5 ? "公开讨论：工资、债务、河水检测。表上有日期，也有空着的项目。" : "新的河水与空气报告按月贴在这里。做完的和没做完的，都留着。", [ [ "记进日记", () => discover("notice", "看了广场的公告，日期和没完成的项目都还在。") ], [ "离开" ] ]);
        if (id === "airstrip") return panel(p.name, state.quest < 6 ? "雾霾还没散，阿简正在等能起飞的天气。测试时也可以随时返回小屋。" : "天清了，飞机随时可以出发。枫叶城以后全年都能来。", [ [ "返回小屋", opts.exit ], [ "再逛逛" ] ]);
        const services = {
            canteen: [ "吃碗热面", "hunger" ],
            market: [ "买点吃的", "hunger" ],
            laundry: [ "洗把脸", "hygiene" ],
            bath: [ "进去洗澡", "hygiene" ],
            toilet: [ "使用公厕", "bladder" ],
            lookout: [ "坐下看看远处", "fun" ],
            plaza: [ "坐一会儿，聊聊天", "social" ]
        };
        if (services[id]) {
            const [label, need] = services[id];
            return panel(p.name, id === "plaza" ? "长椅边有人歇脚，能坐下来聊几句。" : "走到地方了，先歇口气。", [ [ label, () => beginService(need, p.name) ], ...id === "canteen" ? [ [ "和老周聊聊", () => converse("zhou") ] ] : [], [ "离开" ] ]);
        }
        const discoveries = {
            nursery: "苗圃里的枫树苗，一片片叶子上都落着灰。",
            pier: "旧码头的缆绳还拴着船，木板上的锈水印已经洗不掉了。",
            mine: "旧矿道墙上留着工人的照片，最下面那排比上面的新。",
            townhall: "市政厅的告示里夹着旧矿区改造的申请，盖章的日期很早。"
        };
        panel(p.name, discoveries[id] || "这里可以停下来看看。", [ [ "仔细看看", () => discover(id, discoveries[id] || "在枫叶城走了一段路。") ], [ "离开" ] ]);
    }
    function discover(id, text) {
        if (state.found.includes(id)) {
            opts.hint("这处已经看过了");
            return;
        }
        state.found.push(id);
        opts.record(text);
        opts.needs().fun = Math.min(100, opts.needs().fun + 5);
        opts.hint(text);
    }
    const indoorSpots = [ {
        id: "bed",
        name: "床铺",
        x: 269,
        y: 102,
        rect: [ 243, 57, 66, 47 ],
        need: "energy"
    }, {
        id: "bath",
        name: "浴缸",
        x: 75,
        y: 102,
        rect: [ 28, 66, 58, 37 ],
        need: "hygiene"
    }, {
        id: "wc",
        name: "卫生间",
        x: 110,
        y: 102,
        rect: [ 90, 68, 30, 35 ],
        need: "bladder"
    }, {
        id: "kitchen",
        name: "厨房",
        x: 67,
        y: 204,
        rect: [ 28, 132, 86, 72 ],
        need: "hunger"
    }, {
        id: "sofa",
        name: "沙发",
        x: 180,
        y: 204,
        rect: [ 162, 167, 48, 37 ],
        need: "social"
    }, {
        id: "books",
        name: "书架",
        x: 250,
        y: 204,
        rect: [ 259, 149, 38, 51 ],
        need: "fun"
    }, {
        id: "exit",
        name: "出门",
        x: 29,
        y: 204,
        rect: [ 19, 181, 18, 35 ]
    } ];
    function insideVisit(need) {
        const p = indoorSpots.find(p => p.need === need);
        return p && goTo(p.x, p.y, {
            id: "inside_service",
            need: need
        });
    }
    function care(need) {
        if (state.service || state.goal?.automatic || state.goal?.id === "inside_service") return;
        close();
        if (state.inside) insideVisit(need); else visit("detective_home", need, true);
    }
    function stepNeeds(dt) {
        if (!(dt > 0) || state.paused || !opts.active()) return;
        const n = opts.needs();
        if (state.service) {
            const a = state.service, rate = {
                hunger: 2.4,
                energy: .4,
                hygiene: 3,
                bladder: 8,
                social: 1.6,
                fun: 1.3
            }[a.need];
            n[a.need] = Math.min(100, n[a.need] + rate * dt);
            a.elapsed += dt;
            if (n[a.need] >= 97) {
                opts.record("歇好了，接着在枫叶城走走。");
                state.service = null;
                state.pose = null;
                state.autoAt = opts.now() + 35;
            }
        }
    }
    function move(dt) {
        state.walk = false;
        if (state.paused || state.door || modal.hidden === false || state.service || state.mapOpen) return;
        if (!state.target && keys.size) {
            const dx = (keys.has("ArrowRight") || keys.has("d") ? 1 : 0) - (keys.has("ArrowLeft") || keys.has("a") ? 1 : 0), dy = (keys.has("ArrowDown") || keys.has("s") ? 1 : 0) - (keys.has("ArrowUp") || keys.has("w") ? 1 : 0), g = graph(), near = nearest(state.x, state.y, g);
            let best = null;
            for (const index of [ near.e.a, near.e.b ]) {
                const a = g.nodes[index], vx = a.x - state.x, vy = a.y - state.y, score = (vx * dx + vy * dy) / Math.max(.1, Math.hypot(vx, vy));
                if (Math.hypot(vx, vy) > .5 && score > .4 && (!best || score > best.score)) best = {
                    ...a,
                    score: score
                };
            }
            if (!best) {
                const k = g.nodes.findIndex(n => dist(n, state) < .5);
                if (k >= 0) for (const e of g.edges) {
                    const to = e.a === k ? e.b : e.b === k ? e.a : null;
                    if (to === null) continue;
                    const a = g.nodes[to], score = ((a.x - state.x) * dx + (a.y - state.y) * dy) / Math.max(.1, dist(a, state));
                    if (score > .4 && (!best || score > best.score)) best = {
                        ...a,
                        score: score
                    };
                }
            }
            if (best) goTo(best.x, best.y);
        }
        let remaining = opts.walkSpeed * dt;
        while (state.target && remaining > 0) {
            const p = state.target;
            if (p.kind === "lift" && !state.riding) {
                const diff = state.y - state.liftY;
                if (Math.abs(diff) > 1) {
                    state.liftY += Math.sign(diff) * Math.min(Math.abs(diff), remaining * 3);
                    break;
                }
                state.riding = true;
            }
            const dx = p.x - state.x, dy = p.y - state.y, d = Math.hypot(dx, dy), factor = p.kind === "stairs" ? .74 : p.kind === "lift" ? 1.5 : 1, step = remaining * factor;
            state.walk = true;
            if (Math.abs(dx) > .01) state.facing = Math.sign(dx);
            if (d <= step) {
                state.x = p.x;
                state.y = p.y;
                if (p.kind === "lift") {
                    state.liftY = state.y;
                    state.riding = false;
                }
                remaining -= d / factor;
                state.target = state.route.shift() || null;
                if (!state.target) {
                    arrive();
                    break;
                }
            } else {
                state.x += dx / d * step;
                state.y += dy / d * step;
                remaining = 0;
            }
            if (p.kind === "lift") state.liftY = state.y;
        }
    }
    function advanceDoor(dt) {
        const d = state.door;
        if (!d) return;
        d.elapsed += dt;
        if (!d.mid && d.elapsed >= .3) {
            d.mid = true;
            state.inside = d.to;
            state.x = d.to ? 29 : landmark("detective_home").x;
            state.y = d.to ? 204 : landmark("detective_home").y;
            state.camX = d.to ? 0 : state.x - 171;
            state.camY = d.to ? 0 : state.y - 118;
        }
        if (d.elapsed >= .65) {
            state.door = null;
            if (d.to && d.need) insideVisit(d.need);
        }
    }
    function camera(dt) {
        if (state.inside) {
            state.camX = state.camY = 0;
            return;
        }
        const x = clamp(state.x - 171, 0, DATA.width - 342), y = clamp(state.y - 130, 0, DATA.height - 236), t = 1 - Math.exp(-dt * 5);
        state.camX += (x - state.camX) * t;
        state.camY += (y - state.camY) * t;
    }
    function load(src) {
        if (images.has(src)) return;
        const im = new Image;
        images.set(src, im);
        im.src = src;
        return im.decode();
    }
    // Pixel-row bending: roots fixed, attached crown, independent phase/rate.
    // Cache warped native sprites; no per-frame rasterization once a wind shape exists.
    const windCache = new Map;
    function windAmount(p, time = state.time) {
        const phase = p.frame * 2.399963, rate = .9 + p.frame % 7 * .073;
        return Math.round((Math.sin(time * rate + phase) + .23 * Math.sin(time * .47 + phase * .7)) * (p.kind === "tree" ? 2.3 : .7) * 4) / 4;
    }
    function windSprite(p) {
        const wind = windAmount(p), key = state.stage + ":" + p.frame + ":" + wind;
        if (windCache.has(key)) return windCache.get(key);
        const c = document.createElement("canvas");c.width = 70;c.height = 96;
        const g = c.getContext("2d"), root = Math.max(1,p.base-p.y);
        g.imageSmoothingEnabled = false;
        for (let y=0;y<p.h;y++) {
            const height = Math.max(0,1-y/root), dx = Math.round(wind*height*height);
            g.drawImage(images.get(DATA.foliageSheets[state.stage]),p.frame*64,y,64,1,3+dx,y,64,1);
        }
        if (windCache.size >= 384) windCache.delete(windCache.keys().next().value);
        windCache.set(key,c);return c;
    }
    function drawSigns() {
        ctx.save();ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillStyle="#e6dfcf";
        for (const p of DATA.signs) {
            if(p.x+p.w<state.camX||p.x>state.camX+342||p.y+p.h<state.camY||p.y>state.camY+236)continue;
            ctx.font=p.size+'px "Buddy Autumn Signs"';
            ctx.fillText(p.text,p.x+p.w/2,p.y+p.h/2-1,p.w-6);
        }
        ctx.restore();
    }
    function drawFoliage(front) {
        for (const p of DATA.foliage) {
            if (p.base >= state.y - 3 !== front || p.x + p.w < state.camX || p.x > state.camX + 342 || p.y + p.h < state.camY || p.y > state.camY + 236) continue;
            const overlap = front && state.x + 12 > p.x && state.x - 12 < p.x + p.w && state.y > p.y && state.y - 29 < p.y + p.h, key = "tree" + p.frame, target = overlap ? .3 : 1, prev = foregroundAlpha.get(key) ?? 1, alpha = prev + (target - prev) * (1 - Math.exp(-frameDt * 14));
            foregroundAlpha.set(key, alpha);
            ctx.globalAlpha = alpha;
            ctx.drawImage(windSprite(p), p.x - 3, p.y);
        }
        ctx.globalAlpha = 1;
    }
    function draw() {
        const ratio = resolution;
        if (renderCanvas.width !== 342 * ratio || renderCanvas.height !== 236 * ratio) {
            renderCanvas.width = 342 * ratio;
            renderCanvas.height = 236 * ratio;
        }
        ctx = renderCanvas.getContext("2d");
        ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        ctx.imageSmoothingEnabled = false;
        ctx.clearRect(0, 0, 342, 236);
        if (!state.loaded) return;
        const bg = images.get(DATA.scenes[state.stage]);
        if (state.mapOpen) {
            const sc = Math.min(342 / DATA.width, 236 / DATA.height), ox = (342 - DATA.width * sc) / 2;
            ctx.drawImage(bg, ox, 0, DATA.width * sc, DATA.height * sc);
            ctx.save();ctx.translate(ox,0);ctx.scale(sc,sc);
            ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillStyle="#e6dfcf";
            for(const p of DATA.signs){ctx.font=p.size+'px "Buddy Autumn Signs"';ctx.fillText(p.text,p.x+p.w/2,p.y+p.h/2-1,p.w-6)}ctx.restore();
            for (const p of DATA.foliage) ctx.drawImage(images.get(DATA.foliageSheets[state.stage]), p.frame * 64, 0, 64, 96, ox + p.x * sc, p.y * sc, 64 * sc, 96 * sc);
            ctx.drawImage(images.get(DATA.front), ox, 0, DATA.width * sc, DATA.height * sc);
            ctx.fillStyle = "#efc452";
            ctx.fillRect(ox + state.x * sc - 2, state.y * sc - 2, 4, 4);
            return;
        }
        ctx.save();
        ctx.translate(-state.camX, -state.camY);
        ctx.drawImage(state.inside ? images.get(DATA.inside) : bg, 0, 0);
        if (!state.inside) {
            drawSigns();
            drawFoliage(false);
            for (const n of npcRows()) {
                if (Math.abs(n.x - state.x) > 240 || Math.abs(n.y - state.y) > 190) continue;
                ctx.drawImage(images.get(DATA.npcs[n.seed][(state.time + n.seed) % 4.7 < .16 ? 1 : 0]), n.x - 10, n.y - 28);
                if (state.quest === 0 && n.id === "jian" || state.quest === 2 && n.id === "father") {
                    ctx.fillStyle = "#efc452";
                    ctx.fillRect(n.x - 1, n.y - 39, 3, 7);
                    ctx.fillRect(n.x - 1, n.y - 30, 3, 2);
                }
            }
        }
        if (!state.inside) {
            const x = DATA.lift.x, y = state.liftY;
            ctx.fillStyle = "#262434";
            ctx.fillRect(x - 15, y - 31, 30, 33);
            ctx.fillStyle = "#87573e";
            ctx.fillRect(x - 12, y - 28, 24, 27);
        }
        if (!state.inside && state.service && [ "hunger", "social", "fun" ].includes(state.service.need)) {
            ctx.fillStyle = "#5d3831";
            ctx.fillRect(state.x - 9, state.y - 5, 18, 3);
            ctx.fillRect(state.x - 7, state.y - 2, 2, 5);
            ctx.fillRect(state.x + 5, state.y - 2, 2, 5);
            if (state.service.need === "hunger") {
                ctx.fillRect(state.x + 10, state.y - 10, 18, 3);
                ctx.fillRect(state.x + 13, state.y - 7, 2, 10);
                ctx.fillStyle = "#e0ddd8";
                ctx.fillRect(state.x + 15, state.y - 13, 9, 3);
                ctx.fillStyle = "#d29b30";
                ctx.fillRect(state.x + 17, state.y - 14, 5, 1);
            }
        }
        const privacy = state.service && [ "hygiene", "bladder" ].includes(state.service.need);
        if (state.inside && state.service?.need === "hygiene") {
            headCtx.clearRect(0, 0, 20, 28);
            opts.drawHero(headCtx, 10, 28, {
                ...state,
                pose: null,
                walk: false
            }, null);
            ctx.drawImage(headCanvas, 0, 0, 20, 15, 35, 77, 20, 15);
        } else if (state.inside && state.service?.need === "energy") {
            ctx.save();
            ctx.translate(275, 92);
            ctx.rotate(-Math.PI / 2);
            opts.drawHero(ctx, 0, 0, {
                ...state,
                pose: null,
                walk: false
            }, null);
            ctx.restore();
        } else if (!privacy) opts.drawHero(ctx, state.x, state.y, state, null);
        if (!state.inside) {
            const lx = DATA.lift.x, ly = state.liftY;
            ctx.globalAlpha = state.riding ? .3 : 1;
            ctx.fillStyle = "#8b8899";
            for (let i = 0; i < 5; i++) ctx.fillRect(lx - 12 + i * 6, ly - 29, 1, 27);
            ctx.fillRect(lx - 16, ly + 1, 32, 3);
            ctx.globalAlpha = 1;
            drawFoliage(true);
            for (const [index, p] of DATA.foreground.entries()) {
                if (p.x + p.w < state.camX || p.x > state.camX + 342 || p.y + p.h < state.camY || p.y > state.camY + 236) continue;
                const overlap = state.x + 12 > p.x && state.x - 12 < p.x + p.w && state.y > p.y && state.y - 30 < p.y + p.h;
                const key = "rail" + index, target = overlap ? .28 : 1, prev = foregroundAlpha.get(key) ?? 1, alpha = prev + (target - prev) * (1 - Math.exp(-frameDt * 14));
                foregroundAlpha.set(key, alpha);
                ctx.globalAlpha = alpha;
                ctx.drawImage(images.get(p.img), p.x, p.y);
            }
            ctx.globalAlpha = 1;
            if (state.flags.tree) {
                ctx.fillStyle = "#87573e";
                ctx.fillRect(landmark("plaza").x + 22, landmark("plaza").y - 33, 3, 26);
                for (const [x, y] of [ [ 18, -37 ], [ 25, -42 ], [ 29, -32 ] ]) {
                    ctx.fillStyle = "#e88a2f";
                    ctx.fillRect(landmark("plaza").x + x, landmark("plaza").y + y, 9, 7);
                }
            }
        }
        if (hover) {
            const p = hover;
            ctx.fillStyle = "#fae59c";
            for (let i = 0; i < 4; i++) ctx.fillRect(p.x - 3 + i, p.y + 5 + i, 7 - i * 2, 1);
        }
        ctx.restore();
        if (!state.inside) {
            if (state.stage < 3) {
                ctx.fillStyle = "#c4c1bc";
                for (let i = 0; i < 12; i++) {
                    const x = DATA.smoke[0] - state.camX + Math.round((state.time * 5 + i * 7) % 65), y = DATA.smoke[1] - state.camY - (state.time * 2 + i * 5) % 45;
                    if (x >= 0 && x < 342 && y >= 0 && y < 236) ctx.fillRect(x, y, 3 + i % 3, 1);
                }
            }
            if (state.stage >= 4) {
                ctx.fillStyle = "#e88a2f";
                for (let i = 0; i < 12; i++) {
                    const x = (i * 41 + Math.sin(state.time + i) * 7) % 342, y = (i * 71 + state.time * 6) % 236;
                    ctx.fillRect(Math.round(x), Math.round(y), 2, 1);
                }
            }
            fx.weather(ctx, weatherKind, state.time, 342, 236);
        }
        const h = opts.now() % 1440 / 60, night = h < 6 || h >= 20 ? .38 : h < 7 || h >= 18 ? .16 : 0;
        if (night) {
            ctx.fillStyle = `rgba(26,22,37,${night})`;
            ctx.fillRect(0, 0, 342, 236);
        }
        if (state.door) {
            const alpha = Math.sin(Math.min(1, state.door.elapsed / .65) * Math.PI);
            ctx.fillStyle = `rgba(38,42,54,${alpha})`;
            ctx.fillRect(0, 0, 342, 236);
        }
        if (state.service) {
            ctx.fillStyle = "#262a36";
            ctx.fillRect(99, 215, 144, 13);
            ctx.fillStyle = "#a7cd6b";
            const v = opts.needs()[state.service.need];
            ctx.fillRect(101, 217, Math.round(140 * v / 100), 9);
        }
    }
    function hit(x, y) {
        if (state.inside) return indoorSpots.find(p => x >= p.rect[0] && y >= p.rect[1] && x < p.rect[0] + p.rect[2] && y < p.rect[1] + p.rect[3]);
        const npc = npcRows().find(n => Math.abs(n.x - x) < 10 && y < n.y && y > n.y - 29);
        if (npc) return {
            ...npc,
            npc: true
        };
        return DATA.landmarks.find(p => x >= p.rect[0] && y >= p.rect[1] && x < p.rect[0] + p.rect[2] && y < p.rect[1] + p.rect[3]);
    }
    function pick(x, y) {
        clearKeys();
        if (state.mapOpen) {
            const sc = 236 / DATA.height, ox = (342 - DATA.width * sc) / 2;
            x = (x - ox) / sc;
            y /= sc;
            state.mapOpen = false;
            const p = nearest(x, y);
            goTo(p.x, p.y);
            return;
        }
        const p = hit(x, y);
        if (p) {
            if (state.inside) {
                if (p.id === "exit") leave(); else goTo(p.x, p.y, {
                    id: "inside_service",
                    need: p.need
                });
            } else if (p.npc) goTo(p.x + (state.x < p.x ? -18 : 18), p.y, {
                id: "npc:" + p.id
            }); else visit(p.id);
            return;
        }
        const dest = nearest(x, y);
        if (dest.d > 36) {
            opts.hint("沿石阶或街道走吧，楼梯口可以上下换层");
            return;
        }
        close();
        goTo(dest.x, dest.y);
    }
    function hoverAt(x, y) {
        hover = hit(x, y);
        canvas.title = hover?.name || "";
        return hover;
    }
    function updateStatus() {
        root.querySelector("[data-status]").textContent = state.service ? {
            hunger: "正在吃饭",
            energy: "正在睡觉",
            hygiene: "正在洗漱",
            bladder: "正在使用卫生间",
            social: "正在聊聊天",
            fun: "正在休息"
        }[state.service.need] + " · " + Math.round(opts.needs()[state.service.need]) + "%" : state.inside ? "阿简的家 · 点击床铺、浴缸、厨房或书架使用" : objective();
    }
    function tick(dt, realDt = dt) {
        if (!state.loaded) return;
        frameDt = state.paused ? 0 : realDt;
        if (!state.paused) {
            state.time += realDt;
            advanceDoor(realDt);
            move(dt);
            if (!state.target && !state.goal && !state.service && !state.door && !state.mapOpen && modal.hidden && !state.inside && !keys.size && opts.now() >= state.autoAt) {
                state.autoAt = opts.now() + 35 + Math.random() * 30;
                const nearby = nodes.filter(n => dist(n, state) > 25 && dist(n, state) < 130);
                if (nearby.length) {
                    const p = nearby[Math.floor(Math.random() * nearby.length)];
                    goTo(p.x, p.y);
                }
            }
            camera(realDt);
        }
        draw();
        updateStatus();
    }
    function clearKeys() {
        keys.clear();
        if (state.keyboard) {
            state.keyboard = false;
            clearRoute();
        }
    }
    function reset() {
        close();
        clearRoute();
        state.inside = false;
        state.door = null;
        state.service = null;
        state.pose = null;
        state.mapOpen = false;
        state.x = landmark("airstrip").x;
        state.y = landmark("airstrip").y;
        state.camX = state.x - 171;
        state.camY = state.y - 110;
        state.autoAt = opts.now() + 30;
    }
    function restore() {
        close();
        state.keyboard = false;
        state.door = null;
        state.mapOpen = false;
        state.quest = clamp(Math.floor(state.quest) || 0, 0, 6);
        state.stage = clamp(Math.floor(state.stage) || 0, 0, 4);
        state.flags ||= {};
        state.found = Array.from(state.found || []);
        if (state.layoutVersion !== DATA.layoutVersion) {
            // Preserve story/needs, discard travel coordinates from the retired large map.
            state.x = landmark("airstrip").x;
            state.y = landmark("airstrip").y;
            state.route = [];
            state.target = state.goal = state.service = state.pose = null;
            state.inside = false;
            state.layoutVersion = DATA.layoutVersion;
        }
        state.liftY = clamp(Number(state.liftY) || DATA.lift.bottom, DATA.lift.top, DATA.lift.bottom);
        state.riding = false;
        const p = nearest(state.x, state.y);
        state.x = p.x;
        state.y = p.y;
        if (state.target) {
            const target = state.route.at(-1) || state.target;
            const goal = state.goal;
            state.route = plan(target.x, target.y);
            state.target = state.route.shift() || null;
            state.goal = goal;
        }
        updateStatus();
    }
    canvas.getBoundingClientRect = () => opts.view.getBoundingClientRect();
    canvas.addEventListener("pointerdown", e => {
        const b = opts.view.getBoundingClientRect();
        pick((e.clientX - b.left) * 342 / b.width + state.camX, (e.clientY - b.top) * 236 / b.height + state.camY);
    });
    window.addEventListener("keydown", e => {
        if (opts.active() && e.key === "Escape" && !modal.hidden) {
            e.preventDefault();
            close();
            return;
        }
        if (!opts.active() || /INPUT|TEXTAREA|SELECT|BUTTON/.test(document.activeElement.tagName) || !modal.hidden) return;
        if ([ "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "w", "a", "s", "d" ].includes(e.key)) {
            e.preventDefault();
            if (!keys.has(e.key)) {
                clearRoute();
                state.service = null;
                state.pose = null;
                state.keyboard = true;
            }
            keys.add(e.key);
        }
    });
    window.addEventListener("keyup", e => {
        keys.delete(e.key);
        if (!keys.size && state.keyboard) {
            state.keyboard = false;
            clearRoute();
        }
    });
    window.addEventListener("blur", clearKeys);
    root.querySelector("[data-map]").onclick = () => {
        close();
        state.mapOpen = !state.mapOpen;
        clearRoute();
    };
    root.querySelector("[data-home]").onclick = () => visit("detective_home");
    root.querySelector("[data-goal]").onclick = () => panel("当前线索", objective(), [ [ "知道了" ] ]);
    root.querySelector("[data-exit]").onclick = opts.exit;
    const signFont = new FontFace("Buddy Autumn Signs", 'url("'+DATA.signFont+'")');
    const fontReady = signFont.load().then(face=>document.fonts.add(face));
    Promise.all([fontReady, ...[ ...DATA.scenes, DATA.front, DATA.inside, ...DATA.npcs.flat(), ...DATA.foreground.map(p => p.img), ...DATA.foliageSheets ].map(load)]).then(() => {
        state.loaded = true;
        draw();
        updateStatus();
    }).catch(e => {
        opts.hint("枫叶城加载失败，请刷新");
        console.error(e);
    });
    return {
        root: root,
        canvas: canvas,
        renderCanvas: renderCanvas,
        state: state,
        modal: modal,
        DATA: DATA,
        foregroundAlpha: foregroundAlpha,
        windAmount: windAmount,
        windSprite: windSprite,
        nodes: nodes,
        edges: edges,
        npcRows: npcRows,
        goTo: goTo,
        visit: visit,
        interact: interact,
        converse: converse,
        care: care,
        stepNeeds: stepNeeds,
        close: close,
        talk: talk,
        plan: plan,
        nearest: nearest,
        pick: pick,
        hit: hit,
        hover: hoverAt,
        tick: tick,
        draw: draw,
        reset: reset,
        restore: restore,
        leave: leave,
        clearKeys: clearKeys,
        setResolution: r => resolution = Math.max(1, r),
        setWeather: kind => weatherKind = kind,
        get modalOpen() {
            return !modal.hidden;
        },
        objective: objective
    };
}