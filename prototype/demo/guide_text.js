// 新手教程 (the in-game guide), pasted into the page by tools/make_demo.py.
// Short on purpose (user: concise). One entry per page: title, shot (a
// picture from tools/make_guide_shots.js, or null), lead, points, tip. In the
// text: [3] is the picture's mark 3 (marks are numbered in the order the shot
// lists them), **x** is bold, {名字} / {她} are her name and 她 / 他.
const GUIDE = [
  { title: "欢迎", shot: "overview",
    lead: "{名字}会自己过日子，你偶尔搭把手就好。",
    points: ["[1] 小屋", "[2] 需求", "[3] 心情", "[4] {她}说的话", "[5] 日记", "[6] 时间和天气", "[7] 设置"],
    tip: "← → 翻页，Esc 关闭。" },

  { title: "点家具", shot: "furniture",
    lead: "家具亮起金边就能点，{她}会去用。",
    points: ["[1] 床", "[2] 衣柜：换造型", "[3] 电脑", "[4] 书架、电视", "[5] 厨房", "[6] 大门：出门"],
    tip: null },

  { title: "点{她}", shot: "ring",
    lead: "点{她}，聊天、摸头、玩手机都在这儿。",
    points: ["[1] 名字", "[2] 玩手机", "[3] 改名字"],
    tip: null },

  { title: "需求", shot: "needs",
    lead: "鼠标移上去展开。绿色够，红色缺。",
    points: ["[1] 饱腹", "[2] 精力", "[3] 清洁", "[4] 如厕", "[5] 社交", "[6] 开心"],
    tip: "见底会晕倒，长按{她}叫醒。" },

  { title: "心情", shot: "mood",
    lead: "表情就是{她}现在的心情。",
    points: ["[1] 移上去看看", "[2] 心情", "[3] 原因"],
    tip: null },

  { title: "人脉", shot: "contacts",
    lead: "鼠标移到表情，左边会出现人脉图标。",
    points: ["[1] 人脉", "[2] 家人和朋友", "[3] 点卡片联系"],
    tip: null },

  { title: "机会卡", shot: "card",
    lead: "偶尔蹦出一张卡，替{她}二选一。",
    points: ["[1] 发生了什么", "[2] [3] 两个选择"],
    tip: null },

  { title: "出门", shot: "door",
    lead: "点大门，选个地方。",
    points: ["[1] 大门", "[2] 门口", "[3] 公园", "[4] 商场", "[5] 海边"],
    tip: "在外面点哪儿就去哪儿，也能找路人聊天。" },

  { title: "设置", shot: "settings",
    lead: "点齿轮。",
    points: ["[1] 时间流速", "[2] 界面大小", "[3] 置顶", "[4] 存档", "[5] 教程", "[6] 更新"],
    tip: "音乐和音效默认关闭，在这里打开。" },
];
