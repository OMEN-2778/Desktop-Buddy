// ================================================================ chance cards (机会卡)
// The user's 100 chance cards, like The Sims': a little situation, two
// choices, and for each choice two possible results (one is picked at
// random). Written by the user; {名字} is her name. Per card:
//   when  - when it may come up: tags (WHEN in the demo) joined with "+" = and,
//           groups joined with "|" = or; "" = any time she's awake
//   mood  - the moodlet that result gives her (the pill above the result box):
//           emo = emotion, pts = 1-3, min = game minutes it lasts
//   need  - small changes to her needs that result implies
// tools/make_demo.py pastes this file into the demo.
const CARDS = [
  { n: 1, title: "冰箱灯的职业道德", when: "inKitchen|cooking|hungry|idle",
    text: "{名字}突然想到：冰箱门关上以后，灯真的会熄灭吗？",
    a: { label: "反复开关检查。", out: [
      { text: "每次开门灯都亮着。{名字}没有抓到任何证据，但认为自己的检查起到了震慑作用。", mood: { name: "震慑了冰箱灯", emo: "confident", pts: 1, min: 120 } },
      { text: "检查了十几次以后，{名字}开始怀疑：灯是不是比自己动作更快？", mood: { name: "冰箱灯可疑", emo: "dazed", pts: 1, min: 120 } } ] },
    b: { label: "决定信任自己的家电。", out: [
      { text: "{名字}关上冰箱，回去安心做自己的事。双方暂时保持着体面的合作关系。" },
      { text: "到了晚上，{名字}又想到：洗衣机不工作的时候，会不会也有自己的安排？", mood: { name: "洗衣机可疑", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 2, title: "经济复苏", when: "inLiving|idle|bored",
    text: "{名字}在沙发缝里摸到一枚硬币。再往里摸，好像还有。",
    a: { label: "展开全面搜查。", out: [
      { text: "找出几枚硬币和一张小面额钞票！", mood: { name: "沙发里捡到钱", emo: "happy", pts: 2, min: 180 } },
      { text: "摸出的东西越来越多，能花的却只有第一枚硬币，其余都是垃圾。", mood: { name: "摸出一堆垃圾", emo: "uncomfortable", pts: 1, min: 120 } } ] },
    b: { label: "见好就收。", out: [
      { text: "{名字}把硬币放进零钱盒，决定给沙发保留一点周转资金。", mood: { name: "给沙发留点钱", emo: "playful", pts: 1, min: 90 } },
      { text: "硬币从手里滑落，又掉回了缝里。这笔钱显然还没到可以支取的时候。", mood: { name: "钱又掉回去了", emo: "sad", pts: 1, min: 90 } } ] } },
  { n: 3, title: "煮多啦！", when: "inKitchen|cooking|hungry",
    text: "面条看起来不多。{名字}又加了一把。现在锅里好像要溢出来了。",
    a: { label: "全部煮完，分成几餐。", out: [
      { text: "接下来几顿饭都有了着落，也许做多了也是一种提前安排。", mood: { name: "饭有着落了", emo: "confident", pts: 1, min: 180 }, need: { hunger: 20 } },
      { text: "连吃几餐后，{名字}看见任何细长的东西都觉得应该加一点葱花。", mood: { name: "吃面吃到腻", emo: "bored", pts: 1, min: 180 }, need: { hunger: 15 } } ] },
    b: { label: "今晚努力吃完。", out: [
      { text: "{名字}终于放下碗，郑重地告诉自己下次一定记住这个分量。", mood: { name: "面条吃撑了", emo: "uncomfortable", pts: 1, min: 120 }, need: { hunger: 30 } },
      { text: "吃到最后，{名字}已经不想再看到面条了，只想以一个不会压到肚子的姿势坐着。", mood: { name: "撑到不想动", emo: "uncomfortable", pts: 2, min: 180 }, need: { hunger: 30 } } ] } },
  { n: 4, title: "失踪鞋员", when: "",
    text: "一只拖鞋不见了。另一只在原地，看起来没有提供线索的意愿。",
    a: { label: "沿着今天的活动路线寻找。", out: [
      { text: "拖鞋躲在床底，找到你了！", mood: { name: "找到拖鞋了", emo: "happy", pts: 1, min: 90 } },
      { text: "{名字}回忆了半天，发现今天几乎没走动过。", mood: { name: "今天没走动", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "先穿着一只过日子。", out: [
      { text: "路过椅子时，{名字}终于看见了另一只拖鞋。", mood: { name: "拖鞋自己现身", emo: "playful", pts: 1, min: 60 } },
      { text: "一只脚觉得地板很凉，另一只暂时没有意见......好难受！{名字}不得不尽快结束这种内部差异。", mood: { name: "一只脚冰凉", emo: "uncomfortable", pts: 1, min: 90 } } ] } },
  { n: 5, title: "热水壶的掌声", when: "inKitchen|cooking|morning|idle",
    text: "水已经烧开，{名字}却忘了自己为什么烧水。",
    a: { label: "泡杯茶。", out: [
      { text: "茶香慢慢散开。{名字}决定，不必每件事都追究最初的目的。", mood: { name: "一杯好茶", emo: "happy", pts: 1, min: 120 } },
      { text: "喝到一半，{名字}终于想起，自己原本是要泡面。好吧。", mood: { name: "原来要泡面", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "站着等记忆回来。", out: [
      { text: "看见旁边的杯子，{名字}突然想起来了，赶紧继续原本的事。", mood: { name: "终于想起来了", emo: "confident", pts: 1, min: 60 } },
      { text: "等到水都凉了，记忆没有回来。{名字}决定重新烧一壶，看看能不能重现当时的思路。", mood: { name: "记忆没回来", emo: "dazed", pts: 1, min: 120 } } ] } },
  { n: 6, title: "我的遥控器呢？", when: "tv|inLiving|idle",
    text: "遥控器不见了，该怎么办？",
    a: { label: "认真翻找。", out: [
      { text: "遥控器就在坐垫下面。{名字}拿到它后，先花了一点时间重新坐舒服。", mood: { name: "找到遥控器", emo: "happy", pts: 1, min: 90 } },
      { text: "只找到一只旧遥控器，按了半天电视也没反应。", mood: { name: "旧遥控器罢工", emo: "angry", pts: 1, min: 90 } } ] },
    b: { label: "直接用电视上的按钮。", out: [
      { text: "{名字}发现电视还有几个从没用过的功能，遥控器暂时失去了不可替代的地位。", mood: { name: "解锁新功能", emo: "inspired", pts: 1, min: 120 } },
      { text: "误入设置菜单后，{名字}把语言改成了不认识的文字。现在急需找到遥控器！", mood: { name: "电视变外语了", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 7, title: "摆盘尊严", when: "morning",
    text: "早餐只有一片面包，但今天的{名字}觉得生活需要仪式感。",
    a: { label: "认真摆盘。", out: [
      { text: "面包摆好后确实像样了很多。{名字}甚至换了个角度，才舍得吃第一口。", mood: { name: "早餐有仪式感", emo: "happy", pts: 2, min: 180 }, need: { hunger: 10 } },
      { text: "{名字}摆了又摆，最后拍到了满意的照片。面包也终于彻底凉了。", mood: { name: "面包拍凉了", emo: "embarrassed", pts: 1, min: 90 }, need: { hunger: 10 } } ] },
    b: { label: "拿起来就吃。", out: [
      { text: "早餐很快结束，{名字}可以从容地开始今天的事。", mood: { name: "从容开始一天", emo: "energized", pts: 1, min: 120 }, need: { hunger: 10 } },
      { text: "吃完才注意到旁边那只漂亮盘子。它今天唯一的工作，是见证自己没有被使用。", mood: { name: "盘子没出场", emo: "playful", pts: 1, min: 60 }, need: { hunger: 10 } } ] } },
  { n: 8, title: "漂浮物", when: "",
    text: "不看不知道，细看不得了。杯子里的水面上好像漂着一点东西。",
    a: { label: "倒掉，洗杯子。", out: [
      { text: "杯子洗干净了，{名字}终于放心喝上水。", mood: { name: "安心喝上水", emo: "happy", pts: 1, min: 60 } },
      { text: "洗完发现，那一点东西是杯底的图案。", mood: { name: "被杯底骗了", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "仔细辨认。", out: [
      { text: "确实只是一小片茶叶。" },
      { text: "看得越久，越觉得它像某种微型生物。{名字}最终还是决定换一杯水。", mood: { name: "水里有生物?", emo: "scared", pts: 1, min: 90 } } ] } },
  { n: 9, title: "气候差异", when: "inBedroom+evening|night|tired",
    text: "盖着太热，不盖太冷。{名字}的一条腿正在承担温度调节工作。",
    a: { label: "露一只脚。", out: [
      { text: "温度终于合适了。{名字}很快睡着。", mood: { name: "温度调好了", emo: "confident", pts: 1, min: 120 }, need: { energy: 10 } },
      { text: "{名字}越想越觉得床外可能有什么会碰脚。几分钟后，这条腿被紧急撤回。", mood: { name: "床外有东西?", emo: "scared", pts: 1, min: 90 } } ] },
    b: { label: "重新调整整条被子。", out: [
      { text: "折腾一阵后，{名字}终于找到舒服的位置，安静睡去。", mood: { name: "一夜好眠", emo: "happy", pts: 2, min: 240 }, need: { energy: 15 } },
      { text: "被子调整好了，{名字}也彻底清醒了，躺着研究起了明天的午饭。", mood: { name: "折腾醒了", emo: "dazed", pts: 1, min: 180 }, need: { energy: -10 } } ] } },
  { n: 10, title: "锅盖失踪", when: "inKitchen|cooking",
    text: "锅里的东西需要焖一会儿，锅盖却不在任何合理的位置。",
    a: { label: "找一个大小合适的替代盖子。", out: [
      { text: "临时找来的盖子刚好合适。饭做好后，{名字}决定暂时不追究原锅盖的缺勤。", mood: { name: "替代盖子真行", emo: "confident", pts: 1, min: 120 } },
      { text: "盖子没有完全盖住，汤汁还是溅了出来。{名字}吃完饭，又多了一片需要擦的地方。", mood: { name: "汤汁溅出来", emo: "uncomfortable", pts: 1, min: 90 } } ] },
    b: { label: "把所有柜子检查一遍。", out: [
      { text: "锅盖找到了，几件乱放的厨具也顺便回了原位。", mood: { name: "厨具归位了", emo: "happy", pts: 1, min: 120 } },
      { text: "最后发现锅盖一直盖在另一口锅上。其实{名字}看过它好几次，只是默认那就是锅的一部分。", mood: { name: "锅盖一直在", emo: "embarrassed", pts: 1, min: 120 } } ] } },
  { n: 11, title: "包装建议", when: "hungry|eating|idle|bored",
    text: "饼干包装写着：开封后请尽快食用，嗯......这句话很有责任感。",
    a: { label: "严格执行。", out: [
      { text: "最后一块饼干吃完，{名字}仔细折好包装，看好了，自己没有辜负厂家的叮嘱。", mood: { name: "没辜负厂家", emo: "playful", pts: 1, min: 90 }, need: { hunger: 15 } },
      { text: "吃得有些多。{名字}重新看了一遍包装，发现上面没有要求一次完成。", mood: { name: "饼干吃多了", emo: "uncomfortable", pts: 1, min: 120 }, need: { hunger: 20 } } ] },
    b: { label: "分装保存。", out: [
      { text: "饼干被装进几个小盒，未来几天都有零食可吃。", mood: { name: "囤好零食了", emo: "happy", pts: 1, min: 180 } },
      { text: "真的要这么麻烦吗？分装时需要不断确认口味，最后装好的只有两个盒子，另一个盒子暂时没有内容。", mood: { name: "边分边偷吃", emo: "embarrassed", pts: 1, min: 90 }, need: { hunger: 10 } } ] } },
  { n: 12, title: "一块顽强的污渍", when: "",
    text: "桌上的污渍擦不掉。{名字}换了角度，它也好像换了一个的位置。",
    a: { label: "继续清洁！", out: [
      { text: "污渍终于擦掉了。{名字}忍不住多看了几眼这块来之不易的干净桌面。", mood: { name: "桌面干净了", emo: "confident", pts: 2, min: 180 } },
      { text: "擦了半天才发现那是木头本来的纹路。桌子始终很配合，只是不可能长得不一样！", mood: { name: "擦了半天木纹", emo: "embarrassed", pts: 1, min: 120 } } ] },
    b: { label: "放个杯垫挡住。", out: [
      { text: "杯垫放得正好，桌面看起来顺眼多了。", mood: { name: "杯垫挡住了", emo: "happy", pts: 1, min: 90 } },
      { text: "之后每次看见杯垫，{名字}都会想起下面的污渍------为什么会这样？！", mood: { name: "杯垫下的污渍", emo: "tense", pts: 1, min: 120 } } ] } },
  { n: 13, title: "剩饭选举", when: "inKitchen|cooking|hungry|eating",
    text: "冰箱里有三份剩菜，每一份都已经到了今天最好吃掉的时候。",
    a: { label: "混在一起做炒饭。", out: [
      { text: "几种味道意外合拍！好美味呀。", mood: { name: "炒饭超好吃", emo: "happy", pts: 2, min: 180 }, need: { hunger: 25 } },
      { text: "{名字}无法判断这道饭是否成功，只能说内容丰富......", mood: { name: "炒饭很丰富", emo: "dazed", pts: 1, min: 120 }, need: { hunger: 25 } } ] },
    b: { label: "分别热好，郑重摆桌。", out: [
      { text: "剩菜也有了宴席的气势，是不是叫点朋友更好？", mood: { name: "剩菜也成宴", emo: "confident", pts: 1, min: 150 }, need: { hunger: 25 } },
      { text: "饭都吃完了，盘子还排着队。{名字}开始怀疑自己刚才是不是过于讲究。", mood: { name: "讲究过头了", emo: "embarrassed", pts: 1, min: 90 }, need: { hunger: 20 } } ] } },
  { n: 14, title: "缺纸，缺纸？缺纸！", when: "",
    text: "纸巾盒里只剩一张。{名字}抽得很小心，但还是整张掉进盒子里了。",
    a: { label: "把盒子拆开。", out: [
      { text: "最后一张下面居然还压着几张。虽然也于事无补吧。", mood: { name: "白拆一场", emo: "embarrassed", pts: 1, min: 60 } },
      { text: "纸巾拿到了，盒子也彻底拆散了。剩下的纸巾需要另找住处。", mood: { name: "纸巾无家可归", emo: "dazed", pts: 1, min: 60 } } ] },
    b: { label: "换一盒新的。", out: [
      { text: "新纸巾顺畅地抽了出来，生活继续。" },
      { text: "过会儿才发现旧盒还有纸。{名字}现在暂时拥有两个都没用完的纸巾盒。", mood: { name: "纸巾盒双开", emo: "playful", pts: 1, min: 60 } } ] } },
  { n: 15, title: "我不想干活", when: "",
    text: "{名字}终于处理了那件拖了很久的家务。实际做完，只花了几分钟。",
    a: { label: "乘胜追击，再做一件。", out: [
      { text: "越做越顺，几个积压的小问题一口气解决了。", mood: { name: "积压清空了", emo: "energized", pts: 2, min: 240 } },
      { text: "第二件远比第一件麻烦。{名字}做着做着开始怀念几分钟前那个轻松的自己。", mood: { name: "第二件好难", emo: "tense", pts: 1, min: 120 }, need: { energy: -5 } } ] },
    b: { label: "立刻奖励自己。", out: [
      { text: "{名字}舒舒服服地休息了一会儿，觉得以后或许也可以这样安排。", mood: { name: "奖励自己", emo: "happy", pts: 1, min: 180 }, need: { fun: 10 } },
      { text: "休息时间渐渐超过了干活时间，但这没事吧？放松，生活不是比赛。", mood: { name: "生活不是比赛", emo: "playful", pts: 1, min: 120 }, need: { fun: 10 } } ] } },
  { n: 16, title: "最后一点", when: "inBath|dirty",
    text: "洗发水的瓶子捏不出来，但摇一摇，里面分明还有声音。",
    a: { label: "加一点水，再用一次。", out: [
      { text: "剩下的洗发水终于出来了，刚好够用。", mood: { name: "刚好够用", emo: "confident", pts: 1, min: 90 }, need: { hygiene: 20 } },
      { text: "水加得有点多，{名字}洗了半天，也不确定自己到底用了多少洗发水。", mood: { name: "洗得稀里糊涂", emo: "dazed", pts: 1, min: 90 }, need: { hygiene: 15 } } ] },
    b: { label: "把瓶子倒放一会儿。", out: [
      { text: "等待起了作用，剩余的洗发水顺利流到了瓶口。", mood: { name: "最后一点挤出", emo: "happy", pts: 1, min: 90 }, need: { hygiene: 20 } },
      { text: "{名字}等待时顺手做了几件事，直到很久以后才想起，自己原本准备洗头。", mood: { name: "忘了要洗头", emo: "embarrassed", pts: 1, min: 120 } } ] } },
  { n: 17, title: "勺子掉进去了", when: "eating|inKitchen|hungry",
    text: "{名字}刚把勺子放进碗里，它就缓缓滑入食物深处。整个过程从容得像早有安排。",
    a: { label: "再拿一把勺子救援。", out: [
      { text: "第一把勺子被顺利捞出，很不错。", mood: { name: "勺子获救", emo: "confident", pts: 1, min: 60 } },
      { text: "第二把也滑了进去。{名字}看着碗，暂时不想再派出第三位。", mood: { name: "勺子又沉了", emo: "angry", pts: 1, min: 90 } } ] },
    b: { label: "把食物倒进大盘子。", out: [
      { text: "勺子露了出来，食物也凉到了刚好能吃的温度。", mood: { name: "温度刚好", emo: "happy", pts: 1, min: 90 }, need: { hunger: 15 } },
      { text: "饭吃完后，{名字}多洗了一个盘子，觉得这把勺子应该承担部分责任。", mood: { name: "多洗一个盘子", emo: "bored", pts: 1, min: 60 }, need: { hunger: 15 } } ] } },
  { n: 18, title: "新毛巾", when: "inBath|dirty|idle",
    text: "新毛巾很柔软，柔软到让{名字}觉得自己以前用的可能是某种建筑材料。",
    a: { label: "立刻换掉旧毛巾。", out: [
      { text: "洗漱变得舒服了很多。{名字}认真回想，自己为什么没早点换。", mood: { name: "新毛巾好软", emo: "happy", pts: 2, min: 180 }, need: { hygiene: 5 } },
      { text: "新毛巾有些掉毛。{名字}照镜子时发现，脸上多了一层均匀的细绒。", mood: { name: "脸上一层绒", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "把旧毛巾留下当抹布。", out: [
      { text: "旧毛巾擦起桌子很好用，顺利开始了第二份工作。", mood: { name: "旧毛巾再就业", emo: "confident", pts: 1, min: 90 } },
      { text: "收起来时才发现，同类抹布已经有一大叠，远超这个家的实际需求。" } ] } },
  { n: 19, title: "房间里的怪味", when: "",
    text: "{名字}闻到一点怪味。站起来闻不见，坐下又出现。",
    a: { label: "检查家具和角落。", out: [
      { text: "找到一个遗忘的食物包装。扔掉后，房间终于恢复正常。", mood: { name: "揪出怪味源", emo: "confident", pts: 1, min: 120 } },
      { text: "查了半天，发现味道来自自己的袜子。{名字}默默把搜索方向转向了洗衣区。", mood: { name: "原来是袜子", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "先开窗通风。", out: [
      { text: "空气慢慢清新起来，{名字}决定先享受眼前的成果。", mood: { name: "空气清新", emo: "energized", pts: 1, min: 120 } },
      { text: "味道暂时消失了，但{名字}坐下时还是会忍不住闻一闻。", mood: { name: "忍不住闻闻", emo: "uncomfortable", pts: 1, min: 90 } } ] } },
  { n: 20, title: "掉在床上的小东西", when: "inBedroom",
    text: "一个很小但很重要的零件掉进被褥里。{名字}刚才还看见它，现在整张床都拒绝作证。",
    a: { label: "逐层整理床铺。", out: [
      { text: "零件找到了，床也意外铺得十分整齐。", mood: { name: "零件找到了", emo: "happy", pts: 1, min: 120 } },
      { text: "没找到零件，却找到了另一件丢失物。{名字}原来已经压着它睡了好几晚。", mood: { name: "压着它睡了几晚", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "用手机灯慢慢照。", out: [
      { text: "一点反光暴露了零件的位置，事情很快解决。", mood: { name: "反光立功", emo: "confident", pts: 1, min: 90 } },
      { text: "零件没找到，床上的细小灰尘倒看得一清二楚。{名字}决定先换床单。", mood: { name: "床上全是灰", emo: "uncomfortable", pts: 1, min: 120 } } ] } },
  { n: 21, title: "椅子的可疑叫声", when: "",
    text: "{名字}坐下时，椅子发出一声很不体面的响动。房间里只有{名字}和椅子，但{名字}还是想解释。",
    a: { label: "检查并拧紧螺丝。", out: [
      { text: "椅子终于安静，{名字}坐下时不再需要提前做好心理准备。", mood: { name: "椅子安静了", emo: "happy", pts: 1, min: 90 } },
      { text: "原来的声音没了，又出现一种新的。椅子似乎只是换了种表达方式。", mood: { name: "椅子又响了", emo: "angry", pts: 1, min: 90 } } ] },
    b: { label: "换个坐姿。", out: [
      { text: "{名字}找到了一个安静又舒服的位置，双方相安无事。", mood: { name: "坐姿刚刚好", emo: "focused", pts: 1, min: 120 } },
      { text: "为了不让椅子响，{名字}坐得浑身僵硬。最后还是先站了起来。", mood: { name: "坐得浑身僵", emo: "uncomfortable", pts: 1, min: 90 } } ] } },
  { n: 22, title: "煮饭按钮的沉默", when: "inKitchen|cooking|hungry",
    text: "等了很久，饭还没好。{名字}走近一看，电饭锅从未收到开始工作的正式通知。",
    a: { label: "现在按下按钮，耐心等。", out: [
      { text: "米饭终于煮好。虽然晚了一点，{名字}还是认真吃完了这顿饭。", mood: { name: "认真吃完饭", emo: "happy", pts: 1, min: 120 }, need: { hunger: 25 } },
      { text: "等待时吃了太多零食，饭好以后已经不饿。电饭锅的努力需要延期验收。", mood: { name: "饭好不饿了", emo: "embarrassed", pts: 1, min: 90 }, need: { hunger: 20 } } ] },
    b: { label: "先做一道不用等的食物。", out: [
      { text: "眼前的饥饿解决了，煮好的米饭正好留给下一餐。", mood: { name: "先垫饱肚子", emo: "confident", pts: 1, min: 120 }, need: { hunger: 20 } },
      { text: "忙来忙去，{名字}把两份食物都做多了，厨房突然比食欲更有准备。", mood: { name: "饭做多了", emo: "dazed", pts: 1, min: 90 }, need: { hunger: 15 } } ] } },
  { n: 23, title: "口袋里的纸团", when: "",
    text: "洗衣机里出现了白色碎屑，一般来说这是种不好的预兆。果不其然，那张忘记掏出的纸巾终于平等地覆盖了所有衣物。",
    a: { label: "耐心逐件处理。", out: [
      { text: "衣服总算恢复原样。{名字}决定以后洗衣服前先认真摸一遍口袋。", mood: { name: "衣服复原了", emo: "happy", pts: 1, min: 120 } },
      { text: "清到最后，{名字}发现自己身上也粘了碎屑。这场清理还没有完全结束。", mood: { name: "身上也粘屑", emo: "uncomfortable", pts: 1, min: 90 } } ] },
    b: { label: "先晾干再处理。", out: [
      { text: "干掉的碎屑更容易去除，事情比想象中轻松。", mood: { name: "轻松搞定", emo: "confident", pts: 1, min: 90 } },
      { text: "晾着晾着就忘了。下次拿衣服时，{名字}再次见到了这场室内降雪。", mood: { name: "又见室内雪", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 24, title: "自制甜品", when: "inKitchen|cooking|hungry|idle",
    text: "食谱说冷藏两小时。{名字}已经查看冰箱四次，目前过去了十一分钟。",
    a: { label: "严格等够时间。", out: [
      { text: "成品口感很好，{名字}决定这两小时确实没有白等。", mood: { name: "甜品没白等", emo: "confident", pts: 2, min: 180 }, need: { hunger: 10 } },
      { text: "等着等着就忘了。第二天打开冰箱，{名字}收到一份自己提前准备的惊喜。", mood: { name: "昨日的惊喜", emo: "playful", pts: 1, min: 150 }, need: { hunger: 10 } } ] },
    b: { label: "先挖一小口看看。", out: [
      { text: "味道不错。{名字}盖好盒子，带着更明确的期待继续等。", mood: { name: "偷尝真好吃", emo: "happy", pts: 1, min: 120 }, need: { hunger: 5 } },
      { text: "一小口之后还有一小口，最后没有任何甜品坚持到规定时间。", mood: { name: "甜品全偷吃了", emo: "embarrassed", pts: 1, min: 120 }, need: { hunger: 15 } } ] } },
  { n: 25, title: "今天的背景音", when: "",
    text: "{名字}打开音乐准备做家务，选歌时发现自己对每一首都有意见。",
    a: { label: "随机播放，接受安排。", out: [
      { text: "意外听到几首喜欢的歌，家务不知不觉就做完了。", mood: { name: "听到喜欢的歌", emo: "happy", pts: 2, min: 180 }, need: { fun: 10 } },
      { text: "倒垃圾时响起极其悲壮的音乐，{名字}提着袋子站了一会儿，感觉应该说点什么。", mood: { name: "悲壮倒垃圾", emo: "playful", pts: 1, min: 90 } } ] },
    b: { label: "认真选一张合适的歌单。", out: [
      { text: "节奏刚好，{名字}做事也跟着利落起来。", mood: { name: "节奏刚刚好", emo: "energized", pts: 1, min: 120 }, need: { fun: 5 } },
      { text: "歌单选好了，原本预留的家务时间也差不多结束了。", mood: { name: "光顾着选歌", emo: "embarrassed", pts: 1, min: 90 }, need: { fun: 5 } } ] } },
  { n: 26, title: "酸得有态度", when: "eating|inKitchen|hungry|idle",
    text: "第一口水果酸得{名字}短暂失去了语言能力。盘里还有很多，个个长得很无辜。",
    a: { label: "加一点糖。", out: [
      { text: "味道终于合适，剩下的水果顺利吃完了。", mood: { name: "水果真好吃", emo: "happy", pts: 1, min: 120 }, need: { hunger: 8 } },
      { text: "糖和酸各有各的主张。{名字}每吃一口，都要重新适应一次。", mood: { name: "酸甜轮流上阵", emo: "dazed", pts: 1, min: 90 }, need: { hunger: 6 } } ] },
    b: { label: "尝尝下一块，也许会甜。", out: [
      { text: "下一块真的很甜，{名字}决定暂时原谅这一整盘。", mood: { name: "原谅这盘了", emo: "happy", pts: 1, min: 120 }, need: { hunger: 6 } },
      { text: "下一块同样酸。{名字}终于确认，这不是某一块水果的个人问题。", mood: { name: "整盘都很酸", emo: "uncomfortable", pts: 1, min: 90 }, need: { hunger: 4 } } ] } },
  { n: 27, title: "剪包装", when: "",
    text: "包装打开了，说明书也被整齐地切成两半。",
    a: { label: "把说明书拼回来。", out: [
      { text: "两半对得很齐，{名字}顺利读懂了操作方法。", mood: { name: "说明书拼好了", emo: "confident", pts: 1, min: 120 } },
      { text: "最关键的一行正好缺了几个字。{名字}手里的家电资料需要结合上下文推理。", mood: { name: "缺了关键字", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "上网查电子版。", out: [
      { text: "找到清晰的教程，很快学会了使用。", mood: { name: "教程很清楚", emo: "happy", pts: 1, min: 120 } },
      { text: "同系列有十几个型号长得几乎一样。{名字}开始翻看机器底部，重新确认它的身份。", mood: { name: "型号连连看", emo: "bored", pts: 1, min: 90 } } ] } },
  { n: 28, title: "今天适合重新布置？", when: "idle|morning|day",
    text: "{名字}觉得只要把桌子挪一下，人生可能就会顺一点。",
    a: { label: "动手调整。", out: [
      { text: "新位置确实更顺手，{名字}坐下后很满意。", mood: { name: "新布局真顺手", emo: "happy", pts: 2, min: 240 }, need: { energy: -5 } },
      { text: "桌子挪好了，电线却够不着。人生暂时被插座限制住了。", mood: { name: "被插座限制", emo: "angry", pts: 1, min: 120 }, need: { energy: -5 } } ] },
    b: { label: "先画个简单布局。", out: [
      { text: "提前发现几个问题，{名字}省下了一次无效搬运。", mood: { name: "省了次搬运", emo: "confident", pts: 1, min: 150 } },
      { text: "图越画越理想，最后多出一间现实里没有的房间。{名字}看着纸，久久没有动家具。", mood: { name: "纸上多间房", emo: "inspired", pts: 1, min: 120 } } ] } },
  { n: 29, title: "互不信任", when: "inKitchen|idle|morning",
    text: "手机、微波炉和墙上的钟显示三个不同时间。它们看起来都都非常坚定的样子。",
    a: { label: "全部校准。", out: [
      { text: "家里的时间终于一致，{名字}看哪一个都放心。", mood: { name: "全家对上表", emo: "confident", pts: 1, min: 120 } },
      { text: "调完最后一个，却忘记了最初参考的是哪个，哦对了，还有手机。", mood: { name: "忘了参考谁", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "以后只看手机。", out: [
      { text: "{名字}不再纠结，其他时钟暂时只负责装饰。", mood: { name: "只认手机了", emo: "happy", pts: 1, min: 90 } },
      { text: "手机没电以后，另外两种时间重新获得了发言权。", mood: { name: "手机没电了", emo: "tense", pts: 1, min: 120 } } ] } },
  { n: 30, title: "一根头发的胜利", when: "idle|inLiving|inBedroom|inBath",
    text: "{名字}刚打扫完，就在地上看见一根头发。",
    a: { label: "立刻捡起来。", out: [
      { text: "地面重新干净，{名字}满意地结束了今天的清洁。", mood: { name: "地板干净了", emo: "happy", pts: 1, min: 120 } },
      { text: "低头时又掉了一根。{名字}意识到，主要来源仍然站在现场。", mood: { name: "头发源头是我", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "允许房间留一点生活痕迹。", out: [
      { text: "{名字}坐下来休息，很快就把它忘了。", mood: { name: "安心歇会儿", emo: "happy", pts: 1, min: 60 }, need: { energy: 5 } },
      { text: "每次经过都忍不住看一眼。最后还是捡起来了，只是双方先僵持了很久------是不是有点太浪费时间了。", mood: { name: "和头发僵持", emo: "bored", pts: 1, min: 90 } } ] } },
  { n: 31, title: "句号。。。。", when: "phone|screen|idle",
    text: "朋友发来的消息只有一个句号。",
    a: { label: "回复问号？", out: [
      { text: "对方解释是误触，顺便聊起了今天发生的事。", mood: { name: "聊起了今天", emo: "happy", pts: 1, min: 120 }, need: { social: 10 } },
      { text: "对方又发来一个句号。{名字}盯着屏幕，开始考虑是否需要使用冒号。", mood: { name: "考虑用冒号", emo: "playful", pts: 1, min: 90 }, need: { social: 3 } } ] },
    b: { label: "回复收到。", out: [
      { text: "对方被逗笑，终于说出了原本想说的话。", mood: { name: "把朋友逗笑", emo: "playful", pts: 2, min: 150 }, need: { social: 10 } },
      { text: "对方以为{名字}明白了某种暗示。双方礼貌地聊了几句，谁也不知道对方懂了什么。", mood: { name: "懂了个啥", emo: "dazed", pts: 1, min: 90 }, need: { social: 5 } } ] } },
  { n: 32, title: "消息的长度", when: "phone|screen|idle",
    text: "朋友发来一段总计可能有五分钟语音。{名字}看着这些进度条，感觉收到了一部没有海报的电影。",
    a: { label: "认真听完。", out: [
      { text: "对方确实遇到了一些烦心事。{名字}耐心回应后，电话那边轻松了不少------乐善好施，人生的信条。", mood: { name: "帮朋友解忧", emo: "confident", pts: 2, min: 180 }, need: { social: 15 } },
      { text: "好吧，其实前四分半都是铺垫。最后的问题是：今晚到底吃什么？", mood: { name: "原来问吃啥", emo: "bored", pts: 1, min: 90 }, need: { social: 8 } } ] },
    b: { label: "请对方先概括重点。", out: [
      { text: "对方用一句话说明白了，{名字}很快给出了建议。", mood: { name: "一句话说清", emo: "happy", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "对方发来一段四分钟语音，并说明已经尽量精简。", mood: { name: "精简版四分钟", emo: "dazed", pts: 1, min: 90 }, need: { social: 5 } } ] } },
  { n: 33, title: "一张看不懂的照片", when: "phone|screen|idle",
    text: "朋友发来一张模糊照片，说太绝了。{名字}看不出绝在哪里，甚至看不出是什么。",
    a: { label: "问清楚拍的是什么。", out: [
      { text: "对方兴致勃勃地解释，两人因此聊了好一会儿。", mood: { name: "聊得很开心", emo: "happy", pts: 1, min: 150 }, need: { social: 12 } },
      { text: "对方重新发了一遍。{名字}才发现，刚才研究的是一张没加载出来的缩略图。", mood: { name: "研究缩略图", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "回复确实，太绝了。", out: [
      { text: "恰好接对了话，对方开心地继续分享。", mood: { name: "恰好接对了", emo: "playful", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "对方追问：你也觉得坏得没法修了？{名字}赶紧重新看了一眼图片。", mood: { name: "差点穿帮", emo: "tense", pts: 1, min: 90 } } ] } },
  { n: 34, title: "突然开始的语音通话", when: "phone|idle|lonely",
    text: "朋友直接打来语音电话。{名字}还没准备好聊天，但已经清了清嗓子。",
    a: { label: "接听。", out: [
      { text: "两人随意聊了些小事，时间过得很快。", mood: { name: "闲聊好时光", emo: "happy", pts: 2, min: 180 }, need: { social: 18 } },
      { text: "对方只是误拨。{名字}准备好的开场白，暂时没有使用机会。", mood: { name: "被误拨了", emo: "dazed", pts: 1, min: 60 } } ] },
    b: { label: "先发消息问什么事。", out: [
      { text: "对方简明说明了情况，几条消息就把事情解决了。", mood: { name: "几条就搞定", emo: "confident", pts: 1, min: 90 }, need: { social: 5 } },
      { text: "对方说没什么，只是想听听{名字}的声音。{名字}又清了一次嗓子。", mood: { name: "被想念了", emo: "flirty", pts: 2, min: 180 }, need: { social: 10 } } ] } },
  { n: 35, title: "管理员", when: "phone|computer|screen",
    text: "群提示：{名字}已成为管理员，但{名字}刚知道这事。",
    a: { label: "认真履行职责。", out: [
      { text: "清理了几条广告，群里有人专门道谢：\"谢谢管理员惹。\"", mood: { name: "被谢谢管理员", emo: "confident", pts: 2, min: 180 }, need: { social: 8 } },
      { text: "只是刚提醒大家文明聊天，就被回：\"妈呀大姐，这素在干什么。\"", mood: { name: "被叫大姐", emo: "angry", pts: 1, min: 120 } } ] },
    b: { label: "询问能不能卸任。", out: [
      { text: "群主爽快同意，{名字}恢复安静围观。", mood: { name: "卸任一身轻", emo: "happy", pts: 1, min: 90 } },
      { text: "群主说，只有{名字}会用管理员功能。{名字}一时不知道算不算夸奖。群主补了一句：\"真的，只有你。\"", mood: { name: "只有你会用", emo: "embarrassed", pts: 1, min: 120 } } ] } },
  { n: 36, title: "朋友更换了头像", when: "phone|screen|idle",
    text: "新头像是一颗很有心事的红色番茄。",
    a: { label: "夸一句很特别。", out: [
      { text: "对方很高兴，分享了最近迷上的插画。", mood: { name: "看了好插画", emo: "inspired", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "对方说，这就是自己现在的精神状态。{名字}把准备好的蔬菜笑话删掉了。", mood: { name: "删掉了笑话", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "问这是什么菜。", out: [
      { text: "两人聊着聊着开始交换菜谱，晚饭也有了思路。", mood: { name: "晚饭有思路", emo: "happy", pts: 1, min: 150 }, need: { social: 8 } },
      { text: "对方说那是莴苣。{名字}放大图片，又去搜了一遍莴苣。", mood: { name: "番茄是莴苣", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 37, title: "起一个名字", when: "phone|screen|idle",
    text: "朋友问，新买的扫地机器人叫什么好。",
    a: { label: "取个威风的名字。", out: [
      { text: "碎屑终结者顺利当选，对方立刻改好了设备名称。", mood: { name: "起名被采纳", emo: "confident", pts: 1, min: 150 }, need: { social: 5 } },
      { text: "没过多久，对方发来消息：终结者被地毯扣住了，请求支援。", mood: { name: "终结者被困", emo: "playful", pts: 1, min: 120 } } ] },
    b: { label: "取个亲切的名字。", out: [
      { text: "名字很贴切，对方每次提起都忍不住笑。", mood: { name: "名字很贴切", emo: "happy", pts: 1, min: 120 }, need: { social: 5 } },
      { text: "名字恰好和对方一位亲戚重名。朋友在家庭群里解释了好几句。", mood: { name: "撞名亲戚了", emo: "embarrassed", pts: 1, min: 120 } } ] } },
  { n: 38, title: "正在输入中......", when: "phone|screen",
    text: "对方正在输入。怎么停了。又开始输入。......{名字}逐渐坐直。",
    a: { label: "耐心等。", out: [
      { text: "一段认真组织过的话发了过来。{名字}也仔细想了想才开始回复。", mood: { name: "认真的对话", emo: "focused", pts: 1, min: 120 }, need: { social: 10 } },
      { text: "最后只收到两个字：哈哈。{名字}觉得，前面的准备时间有够充分。", mood: { name: "只等来哈哈", emo: "bored", pts: 1, min: 90 } } ] },
    b: { label: "主动发个轻松的话题。", out: [
      { text: "对方顺势聊起来，原本的犹豫慢慢消散。", mood: { name: "顺利聊开了", emo: "happy", pts: 1, min: 120 }, need: { social: 10 } },
      { text: "对方说刚才打了很长一段，又被新消息打断思路。窗口重新开始显示正在输入。", mood: { name: "又在输入中", emo: "tense", pts: 1, min: 90 } } ] } },
  { n: 39, title: "宣布早睡", when: "evening|night",
    text: "朋友发消息：从今天开始，十点以后绝不上网。问题是现在几点了？",
    a: { label: "善意指出时间。", out: [
      { text: "对方笑着道了晚安，终于放下手机。", mood: { name: "朋友去睡了", emo: "happy", pts: 1, min: 90 }, need: { social: 5 } },
      { text: "对方解释，今天只是宣布，正式执行从下一个今天开始。", mood: { name: "下一个今天", emo: "playful", pts: 1, min: 90 } } ] },
    b: { label: "表示支持。", out: [
      { text: "对方很受鼓舞，决定现在就去睡。", mood: { name: "鼓励了朋友", emo: "confident", pts: 1, min: 120 }, need: { social: 5 } },
      { text: "两人认真讨论早睡的好处，等聊完，时间又晚了不少。", mood: { name: "又聊晚了", emo: "uncomfortable", pts: 1, min: 120 }, need: { energy: -8, social: 8 } } ] } },
  { n: 40, title: "版本差异", when: "phone|screen|idle",
    text: "{名字}和朋友回忆一件旧事。两人的版本里，丢脸的都是对方。",
    a: { label: "翻旧聊天记录查证。", out: [
      { text: "记录证明{名字}没记错，{名字}终于可以心平气和地继续笑了。", mood: { name: "我没记错", emo: "confident", pts: 2, min: 180 }, need: { social: 8 } },
      { text: "两个人都记错了，而且当时的实际情况比现在说的更丢脸。", mood: { name: "都记错了", emo: "embarrassed", pts: 2, min: 150 }, need: { social: 8 } } ] },
    b: { label: "同意这是一次集体失误。", out: [
      { text: "双方笑着接受了这个说法，不再追究细节。", mood: { name: "笑着和解", emo: "happy", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "对方回复：你终于承认了。{名字}开始重新审视这份口头和解。", mood: { name: "和解有诈", emo: "angry", pts: 1, min: 90 } } ] } },
  { n: 41, title: "行", when: "phone|screen",
    text: "{名字}发了很长一段话，对方只回复一个行字。",
    a: { label: "继续确认对方的想法。", out: [
      { text: "对方只是手头忙，解释清楚后，{名字}终于不再多想。", mood: { name: "不再多想", emo: "happy", pts: 1, min: 90 }, need: { social: 5 } },
      { text: "对方开始逐条回复，内容比{名字}原来的消息还长。{名字}坐稳，准备认真阅读。", mood: { name: "回复超长", emo: "focused", pts: 1, min: 120 }, need: { social: 5 } } ] },
    b: { label: "接受这个回复。", out: [
      { text: "事情顺利定下来了，{名字}很快去忙别的。" },
      { text: "{名字}忍不住反复点开消息，试图从同一个字里看出语气变化。", mood: { name: "一个字反复看", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 42, title: "一部神作", when: "phone|screen|tv",
    text: "朋友推荐了一部据说很棒的片子，并强调千万别看剧透，接着连续发来十几条介绍。",
    a: { label: "提醒对方先停一下。", out: [
      { text: "对方及时收住，{名字}保住了自己观看的机会。", mood: { name: "躲过剧透", emo: "happy", pts: 1, min: 120 } },
      { text: "对方回复：放心，真正重要的是最后那个......{名字}看见剧透的时候已经晚了。", mood: { name: "被剧透了", emo: "sad", pts: 1, min: 150 } } ] },
    b: { label: "让对方说尽兴。", out: [
      { text: "对方讲得很开心，{名字}也因此对作品更有兴趣。", mood: { name: "想看这部了", emo: "energized", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "被剧透得一败涂地！{名字}还没看第一集就已经能够评价最后一集的处理方式了。", mood: { name: "被剧透全集", emo: "angry", pts: 2, min: 180 }, need: { social: 5 } } ] } },
  { n: 43, title: "发错窗口", when: "phone|screen",
    text: "{名字}原本想向另一个人解释自己为什么准备结束聊天，却把不太想聊了发给了正在聊天的人。",
    a: { label: "直接解释自己需要休息。", out: [
      { text: "对方表示理解，约好以后再聊。", mood: { name: "对方很理解", emo: "happy", pts: 1, min: 90 }, need: { social: 5 } },
      { text: "对方有点失落，回了句好吧。怎么会有这么尴尬的事！", mood: { name: "尴尬到想逃", emo: "embarrassed", pts: 2, min: 180 } } ] },
    b: { label: "委婉表示不太想聊这个话题。", out: [
      { text: "对方自然地换了话题，气氛很快恢复。", mood: { name: "化险为夷", emo: "confident", pts: 1, min: 90 } },
      { text: "对方问：我们刚才不是在互道晚安吗？看来还是坦白比较省事。", mood: { name: "还是坦白吧", emo: "embarrassed", pts: 1, min: 120 } } ] } },
  { n: 44, title: "开始记账", when: "phone|screen|idle",
    text: "朋友展示本月账单，表示要严格控制非必要开支。截图底部还有一笔高级记账软件会员费。",
    a: { label: "温和提醒这笔支出。", out: [
      { text: "对方愣了一下，决定先用免费功能试试。", mood: { name: "劝住了朋友", emo: "confident", pts: 1, min: 120 } },
      { text: "对方认真解释这是为了省钱的必要投资，并发来了购买链接。", mood: { name: "收到购买链接", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "夸奖对方开始行动。", out: [
      { text: "对方受到鼓励，两人交换了几个简单的省钱办法。", mood: { name: "交换省钱招", emo: "happy", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "对方邀请{名字}一起参加付费省钱课程，说两个人报名更划算。", mood: { name: "被拉去报课", emo: "uncomfortable", pts: 1, min: 90 } } ] } },
  { n: 45, title: "客观评价", when: "phone|screen|idle",
    text: "朋友问：你觉得我是个容易纠结的人吗？",
    a: { label: "\"有一点\"", out: [
      { text: "对方想了想，承认自己确实经常拿不定主意。", mood: { name: "坦诚被接受", emo: "happy", pts: 1, min: 90 }, need: { social: 5 } },
      { text: "对方追问这一点到底是多少，两人的聊天开始出现百分比。", mood: { name: "聊出百分比", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "问对方自己怎么想。", out: [
      { text: "对方说着说着理清了思路，最后认真感谢了{名字}。", mood: { name: "被认真感谢", emo: "confident", pts: 2, min: 150 }, need: { social: 10 } },
      { text: "对方表示自己也不确定。问题又原封不动地回到了{名字}面前。", mood: { name: "问题又回来", emo: "bored", pts: 1, min: 60 } } ] } },
  { n: 46, title: "被推荐给陌生人", when: "phone|screen|idle",
    text: "朋友说，自己把{名字}推荐给别人了，因为{名字}很会聊天。",
    a: { label: "问清是什么情况。", out: [
      { text: "原来是介绍一位兴趣相近的网友，几个人很快聊到了一起。", mood: { name: "认识新网友", emo: "happy", pts: 2, min: 180 }, need: { social: 15 } },
      { text: "对方正在找能长期听自己倾诉的人。{名字}提前说明了自己能陪聊的时间。", mood: { name: "先说好时间", emo: "tense", pts: 1, min: 90 } } ] },
    b: { label: "坦白自己其实比较慢热。", out: [
      { text: "朋友表示理解，以后会先问{名字}的意见。", mood: { name: "朋友很体贴", emo: "happy", pts: 1, min: 90 }, need: { social: 5 } },
      { text: "朋友回复：我就是这么介绍的，神秘，而且有深度。", mood: { name: "神秘有深度", emo: "confident", pts: 1, min: 120 } } ] } },
  { n: 47, title: "深夜重大问题", when: "night",
    text: "凌晨，朋友问：如果抹了黄油的面包总是黄油朝下，猫又总能脚朝下，那么把它们......",
    a: { label: "认真讨论。", out: [
      { text: "两人胡扯了很久，最后一致决定让猫远离早餐。", mood: { name: "猫远离早餐", emo: "playful", pts: 2, min: 150 }, need: { social: 10 } },
      { text: "等终于停下来，两个人都该睡觉了，好困啊！", mood: { name: "聊到好困", emo: "dazed", pts: 1, min: 120 }, need: { energy: -10, social: 8 } } ] },
    b: { label: "回复先让猫睡觉。", out: [
      { text: "对方笑着道了晚安，这场理论研究暂时结束。", mood: { name: "晚安收工", emo: "happy", pts: 1, min: 90 }, need: { social: 5 } },
      { text: "对方开始搜索猫每天睡多久，又发来一段新发现。", mood: { name: "猫睡多久", emo: "bored", pts: 1, min: 60 } } ] } },
  { n: 48, title: "一笔数字奇怪的转账", when: "phone|screen",
    text: "朋友转来一小笔钱，备注：上次的。{名字}不记得上次发生过什么。",
    a: { label: "问清楚再收。", out: [
      { text: "原来是很久以前的一笔小借款，{名字}已经忘了，对方却一直记着。", mood: { name: "朋友真靠谱", emo: "happy", pts: 1, min: 150 } },
      { text: "对方发错了人，连忙道谢，{名字}也省去了一场后续误会。", mood: { name: "避免了误会", emo: "confident", pts: 1, min: 60 } } ] },
    b: { label: "先查自己的聊天记录。", out: [
      { text: "找到了来由，{名字}顺便重看了一段以前的有趣对话。", mood: { name: "重看旧对话", emo: "happy", pts: 1, min: 120 } },
      { text: "这笔没查清，却发现自己也有一笔钱忘了还给对方（好像更多）。", mood: { name: "我也欠钱了", emo: "embarrassed", pts: 2, min: 150 } } ] } },
  { n: 49, title: "被拉进了兴趣群", when: "phone|screen|idle",
    text: "群名是轻松生活交流。群公告足足有二十条。",
    a: { label: "先看看大家聊什么。", out: [
      { text: "群里分享了一个很实用的小技巧，{名字}马上记了下来。", mood: { name: "学到小技巧", emo: "inspired", pts: 1, min: 120 } },
      { text: "大家正在认真讨论如何收纳暂时不用的收纳盒，{名字}决定先潜水。", mood: { name: "收纳盒的收纳", emo: "bored", pts: 1, min: 90 } } ] },
    b: { label: "礼貌退群。", out: [
      { text: "朋友表示理解，{名字}的消息列表重新安静了。" },
      { text: "朋友发现自己拉错群了，真正用来闲聊的那个群没有公告，只有很多表情包。", mood: { name: "拉错群了", emo: "playful", pts: 1, min: 90 } } ] } },
  { n: 50, title: "请您假装懂行", when: "phone|screen",
    text: "朋友想发一张精致晚餐照片，请{名字}留一句听起来很专业的评论。",
    a: { label: "\"层次很丰富\"", out: [
      { text: "对方满意地回复，两人默契地完成了这次配合。", mood: { name: "默契配合", emo: "playful", pts: 1, min: 120 }, need: { social: 5 } },
      { text: "有人认真追问具体是哪种层次。{名字}把图片重新放大，看了很久，表示我哪知道，还是删评吧。", mood: { name: "被追问层次", emo: "embarrassed", pts: 2, min: 150 } } ] },
    b: { label: "\"这个擦桌布我家也有，确实不错\"。", out: [
      { text: "评论区因此聊起了各自的餐具，照片下面热闹起来。", mood: { name: "评论区热闹", emo: "happy", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "对方私信发来一串省略号，原本计划好的高级感没有顺利建立。", mood: { name: "高级感崩了", emo: "uncomfortable", pts: 1, min: 90 } } ] } },
  { n: 51, title: "忘了回复的消息", when: "phone|screen|idle|lonely",
    text: "{名字}发现一条三天前的消息。脑海里明明已经回复过，怎么回事呢？",
    a: { label: "道歉并补上回复。", out: [
      { text: "对方完全不介意，聊天很自然地继续了。", mood: { name: "对方不介意", emo: "happy", pts: 1, min: 120 }, need: { social: 10 } },
      { text: "对方也忘了原本想说什么，两个人一起向上翻记录。", mood: { name: "一起翻记录", emo: "playful", pts: 1, min: 90 }, need: { social: 8 } } ] },
    b: { label: "用新话题自然开场。", out: [
      { text: "新话题很合适，双方很快聊得热闹。", mood: { name: "新话题聊嗨了", emo: "happy", pts: 2, min: 180 }, need: { social: 12 } },
      { text: "对方先问：所以我上次那个问题呢？{名字}还是补上了迟到的回复。", mood: { name: "迟到回复被抓", emo: "embarrassed", pts: 1, min: 90 }, need: { social: 5 } } ] } },
  { n: 52, title: "冷战", when: "phone|screen|idle|lonely",
    text: "朋友问{名字}是不是生气了。{名字}一直以为两人的关系很正常。",
    a: { label: "解释最近只是比较安静。", out: [
      { text: "对方松了口气，误会很快解开。", mood: { name: "误会解开了", emo: "happy", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "对方列出了好几项证据。{名字}第一次知道自己少发一个表情也会被留意。", mood: { name: "被列了证据", emo: "embarrassed", pts: 2, min: 180 }, need: { social: 3 } } ] },
    b: { label: "问对方为什么这么想。", out: [
      { text: "原来只是一句话理解错了，解释之后，两个人都笑了。", mood: { name: "一起笑了", emo: "happy", pts: 1, min: 120 }, need: { social: 10 } },
      { text: "对方说，因为{名字}昨天没给自己的动态点赞。{名字}重新打开了那个几乎没看的应用。", mood: { name: "为点赞赔罪", emo: "dazed", pts: 1, min: 120 }, need: { social: 5 } } ] } },
  { n: 53, title: "梦里有你", when: "phone|screen|idle|lonely",
    text: "对方说，梦见{名字}变成了一个电饭锅，而且不肯煮饭。",
    a: { label: "问自己最后有没有煮。", out: [
      { text: "对方详细讲起梦里的情节，两人聊得很开心。", mood: { name: "梦话聊得开心", emo: "playful", pts: 2, min: 150 }, need: { social: 10 } },
      { text: "对方说{名字}后来只肯煮粥。{名字}莫名觉得，梦里的自己还可以更有追求。", mood: { name: "梦里只肯煮粥", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "声明梦里的行为与本人无关。", out: [
      { text: "对方被逗笑，表示会去追究梦里的电饭锅。", mood: { name: "逗笑了对方", emo: "confident", pts: 1, min: 120 }, need: { social: 8 } },
      { text: "对方要求{名字}证明现实中会做饭，聊天逐渐变成了一场菜谱交流。", mood: { name: "聊成菜谱交流", emo: "inspired", pts: 1, min: 120 }, need: { social: 10 } } ] } },
  { n: 54, title: "分享欲的时差", when: "phone|screen|idle|lonely",
    text: "{名字}刚想讲今天的趣事，朋友正好发来一句我跟你说个事。两条消息撞在了一起。",
    a: { label: "让对方先说。", out: [
      { text: "对方说完后也认真听了{名字}的故事，两个人都有话可讲。", mood: { name: "互相听故事", emo: "happy", pts: 2, min: 180 }, need: { social: 12 } },
      { text: "对方讲得太投入，{名字}等到最后已经忘了自己原本准备怎样开头。", mood: { name: "忘了怎么开头", emo: "dazed", pts: 1, min: 90 }, need: { social: 5 } } ] },
    b: { label: "提议一人一段轮流讲。", out: [
      { text: "两个故事交替进行，聊天比平时还热闹。", mood: { name: "轮流讲故事", emo: "playful", pts: 2, min: 180 }, need: { social: 12, fun: 5 } },
      { text: "讲着讲着，双方都混淆了情节，不确定到底是谁把盐加进了咖啡。", mood: { name: "谁加的盐", emo: "dazed", pts: 1, min: 90 }, need: { social: 8 } } ] } },
  { n: 55, title: "小众忧郁款", when: "phone|screen|idle|bored|lonely",
    text: "{名字}想发一句有深度的朋友圈，却暂时没有深度可用。",
    a: { label: "\"有些事，懂的都懂\"", out: [
      { text: "朋友纷纷来问近况，{名字}顺势和几位久没联系的人聊了起来。", mood: { name: "和老友叙旧", emo: "happy", pts: 2, min: 240 }, need: { social: 15 } },
      { text: "大家追问究竟发生了什么，{名字}只好解释，今天其实挺普通的。", mood: { name: "其实挺普通", emo: "embarrassed", pts: 1, min: 120 }, need: { social: 5 } } ] },
    b: { label: "\"今天的饭很好吃\"", out: [
      { text: "评论区聊起了各自的晚饭，简单又热闹。", mood: { name: "晚饭话题热闹", emo: "happy", pts: 1, min: 150 }, need: { social: 10 } },
      { text: "大家都在求做法。{名字}看着垃圾桶里的速食包装，思考该从哪一步开始介绍。", mood: { name: "速食包装露馅", emo: "embarrassed", pts: 1, min: 120 }, need: { social: 5 } } ] } },
  { n: 56, title: "练习夸人", when: "phone|screen|idle|lonely",
    text: "朋友说最近在练习真诚表达，并夸{名字}是一个很有自己作息的人。",
    a: { label: "接受这份努力。", out: [
      { text: "对方放松下来，后面的夸奖终于自然了许多。", mood: { name: "收到真诚夸奖", emo: "happy", pts: 1, min: 150 }, need: { social: 8 } },
      { text: "{名字}客气地道完谢，开始认真回忆自己最近到底几点睡觉。", mood: { name: "回想作息", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "回赠一句夸奖。", out: [
      { text: "两人开始比赛谁能把普通特点说得更郑重，聊得停不下来。", mood: { name: "郑重互夸", emo: "playful", pts: 2, min: 180 }, need: { social: 12 } },
      { text: "对方认真记下了{名字}的措辞准备下次拿去夸别人。", mood: { name: "措辞被借走", emo: "confident", pts: 1, min: 120 }, need: { social: 5 } } ] } },
  { n: 57, title: "撤回的诱惑", when: "phone|screen|idle",
    text: "朋友撤回了一条消息。{名字}只瞥见开头：其实我一直觉得你......",
    a: { label: "\"觉得我什么？\"", out: [
      { text: "对方重新发来一句真心夸奖，只是刚才觉得有点不好意思。", mood: { name: "被真心夸了", emo: "flirty", pts: 2, min: 240 }, need: { social: 10 } },
      { text: "对方只有沉默。{名字}不知为何变得很烦单燥。", mood: { name: "撤回的沉默", emo: "tense", pts: 2, min: 180 } } ] },
    b: { label: "假装没看见。", out: [
      { text: "对方稍后重新组织了语言，把想说的话完整发了过来。", mood: { name: "话说完整了", emo: "happy", pts: 1, min: 150 }, need: { social: 8 } },
      { text: "{名字}想了很多种可能，最后忍不住再次打开对话框。怎么还是没发。", mood: { name: "还是没发", emo: "tense", pts: 1, min: 120 } } ] } },
  { n: 58, title: "群里的免费专家", when: "phone|computer|screen|idle",
    text: "群里有人问一个生活问题。{名字}刚好懂一点，但也只懂一点点。",
    a: { label: "说明自己知道多少，再分享经验。", out: [
      { text: "建议正好派上用场，对方专门回来道了谢。", mood: { name: "被专门道谢", emo: "confident", pts: 2, min: 180 }, need: { social: 10 } },
      { text: "对方接着问了更复杂的问题，{名字}坦白不会，帮忙找了一份可靠资料。", mood: { name: "坦白不会", emo: "embarrassed", pts: 1, min: 90 }, need: { social: 5 } } ] },
    b: { label: "保持沉默。", out: [
      { text: "很快有人给出了准确答案，{名字}放心继续做自己的事。", mood: { name: "放心了", emo: "happy", pts: 1, min: 60 } },
      { text: "另一个人说得非常肯定，内容却明显不对。{名字}的手指在输入框上停了很久。", mood: { name: "忍住没纠错", emo: "uncomfortable", pts: 1, min: 120 } } ] } },
  { n: 59, title: "给朋友当闹钟", when: "evening|night|phone",
    text: "朋友请{名字}明早发消息叫醒自己，强调{名字}不叫自己肯定起不来。",
    a: { label: "答应，并设好提醒。", out: [
      { text: "消息发出后，对方很快醒了，连着发来几句感谢。", mood: { name: "成功叫醒朋友", emo: "confident", pts: 2, min: 180 }, need: { social: 10 } },
      { text: "{名字}发了很多条消息，对方醒后才说，手机开着免打扰。", mood: { name: "白发一堆消息", emo: "angry", pts: 1, min: 120 }, need: { social: 3 } } ] },
    b: { label: "建议对方多设几个闹钟。", out: [
      { text: "对方照做，第二天准时起床，还把经验分享给{名字}。", mood: { name: "朋友学会了", emo: "happy", pts: 1, min: 120 }, need: { social: 5 } },
      { text: "对方把所有闹钟都改成{名字}的名字，截图发来，表示现在有六个{名字}负责叫醒自己。", mood: { name: "六个我叫醒你", emo: "playful", pts: 1, min: 150 }, need: { social: 8 } } ] } },
  { n: 60, title: "一个过于准确的推荐", when: "phone|screen|idle|tired",
    text: "朋友发来一件商品，说看到就想到了{名字}。商品是一条能从头裹到脚的毯子。",
    a: { label: "承认对方很了解自己。", out: [
      { text: "两人认真讨论了一会儿毯子的优点，{名字}觉得这份推荐确实很贴心。", mood: { name: "推荐很贴心", emo: "happy", pts: 1, min: 150 }, need: { social: 8 } },
      { text: "对方继续发来一整套适合躺着使用的东西，连水杯支架都考虑到了。", mood: { name: "躺平全家桶", emo: "playful", pts: 1, min: 120 }, need: { social: 5 } } ] },
    b: { label: "抗议自己没有那么懒。", out: [
      { text: "对方笑着改口，说只是觉得{名字}会喜欢柔软的东西。", mood: { name: "对方改口了", emo: "confident", pts: 1, min: 90 }, need: { social: 5 } },
      { text: "{名字}刚说完就继续躺着，用脚去够桌边的遥控器。", mood: { name: "用脚够遥控器", emo: "embarrassed", pts: 1, min: 90 } } ] } },
  { n: 61, title: "自动续费的纪念日", when: "phone|computer|screen|idle",
    text: "一个几乎没用过的软件扣了费，并感谢{名字}长期以来的支持。",
    a: { label: "取消续费再申请退款。", out: [
      { text: "退款顺利到账，这段{名字}几乎不记得的关系终于结束了。", mood: { name: "退款到账", emo: "happy", pts: 2, min: 180 } },
      { text: "退款没有通过，但续费关掉了。{名字}把软件的感谢信也一起删了。", mood: { name: "删了感谢信", emo: "angry", pts: 1, min: 120 } } ] },
    b: { label: "既然付了钱就认真用起来啊！", out: [
      { text: "{名字}发现了几个实用功能，觉得这笔钱总算有了去处。", mood: { name: "钱有了去处", emo: "confident", pts: 1, min: 150 } },
      { text: "{名字}花了一小时学习如何使用一款号称节省时间的软件，暂时还没开始节省。", mood: { name: "还没开始省时", emo: "bored", pts: 1, min: 120 }, need: { energy: -5 } } ] } },
  { n: 62, title: "验证码的审美门槛", when: "computer|phone|screen",
    text: "网页要求选出所有包含楼梯的图片。{名字}怀疑其中一张到底算台阶还是坡。",
    a: { label: "认真辨认。", out: [
      { text: "一次通过，{名字}终于顺利进入网页。", mood: { name: "一次通过", emo: "confident", pts: 1, min: 60 } },
      { text: "连续失败后，{名字}觉得自己需要证明一些很基本的事实。", mood: { name: "自证是人类", emo: "angry", pts: 1, min: 120 } } ] },
    b: { label: "刷新一组。", out: [
      { text: "新题简单得多，很快就通过了。", mood: { name: "刷到简单题", emo: "happy", pts: 1, min: 60 } },
      { text: "新题要求辨认两个长得很相近的邪恶字母。{名字}暂时告别了建筑问题，进入另一个专业领域。", mood: { name: "邪恶字母", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 63, title: "过于私人", when: "computer|phone|screen",
    text: "密码提示写着：那个你绝对不会忘的东西。",
    a: { label: "逐个尝试重要回忆。", out: [
      { text: "终于试对，{名字}看着旧账户，顺便想起了当年设置密码时的自己。", mood: { name: "想起当年的我", emo: "inspired", pts: 1, min: 180 } },
      { text: "尝试次数用完，账户暂时锁定。{名字}只能承认自己绝对不会忘的东西还挺多。", mood: { name: "账户被锁", emo: "sad", pts: 1, min: 150 } } ] },
    b: { label: "直接重置密码。", out: [
      { text: "重置顺利完成，{名字}重新登录，并认真保存了新密码。", mood: { name: "新密码存好了", emo: "focused", pts: 1, min: 90 } },
      { text: "系统提示新密码不能与旧密码相同。{名字}盯着提示沉默了一会儿。", mood: { name: "不能和旧的同", emo: "uncomfortable", pts: 1, min: 90 } } ] } },
  { n: 64, title: "愿望博物馆", when: "phone|computer|screen|idle|bored",
    text: "{名字}打开购物车，发现里面躺着许多过去的自己想要的东西。",
    a: { label: "认真清理。", out: [
      { text: "一批已经不需要的商品被删掉，购物车终于清爽了。", mood: { name: "购物车清爽了", emo: "energized", pts: 1, min: 120 } },
      { text: "重新点开介绍后，{名字}又理解了当时的自己，还顺手加了几件配套商品。", mood: { name: "理解当时的我", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "挑一件最实用的购买。", out: [
      { text: "买到的东西确实能解决眼前的小麻烦，{名字}很满意。", mood: { name: "买到实用货", emo: "happy", pts: 1, min: 150 } },
      { text: "为了凑免邮，{名字}又加了几样东西，最后花的钱远超最初那一件。", mood: { name: "凑单凑超支", emo: "uncomfortable", pts: 2, min: 180 } } ] } },
  { n: 65, title: "差评里的文学天赋", when: "phone|computer|screen|idle|bored",
    text: "{名字}只是想买个普通水杯，却在评论区读到一篇跌宕起伏的家庭故事。",
    a: { label: "继续读下去。", out: [
      { text: "故事写得实在精彩，{名字}甚至忘了自己原本要买什么。", mood: { name: "评论区追剧", emo: "inspired", pts: 1, min: 150 }, need: { fun: 10 } },
      { text: "故事在最关键的地方结束了，发布者也没有后续更新。{名字}惦记了一整晚。", mood: { name: "故事没后续", emo: "sad", pts: 1, min: 240 }, need: { fun: 5 } } ] },
    b: { label: "回到商品参数。", out: [
      { text: "{名字}很快找齐需要的信息，选好了合适的杯子。", mood: { name: "选好杯子", emo: "focused", pts: 1, min: 90 } },
      { text: "参数里写满了漂亮、好用、值得拥有。{名字}翻回评论区，发现故事至少提到了杯子有多大。", mood: { name: "参数全是废话", emo: "bored", pts: 1, min: 90 } } ] } },
  { n: 66, title: "一分钱的胜利", when: "phone|computer|screen",
    text: "优惠券领取成功，预计可节省一分钱。",
    a: { label: "坚持使用。", out: [
      { text: "付款金额真的少了一分钱。{名字}看着订单，认为原则得到了落实。", mood: { name: "原则落实了", emo: "confident", pts: 1, min: 120 } },
      { text: "为满足使用门槛，{名字}又买了点东西。这一分钱省得相当隆重。", mood: { name: "隆重的一分钱", emo: "embarrassed", pts: 1, min: 120 } } ] },
    b: { label: "放弃复杂优惠。", out: [
      { text: "{名字}直接完成购买，省去了反复比较的时间。", mood: { name: "干脆利落", emo: "happy", pts: 1, min: 90 } },
      { text: "页面不断提醒还有优惠没有使用，这到底是什么重要财产......", mood: { name: "优惠在催我", emo: "uncomfortable", pts: 1, min: 90 } } ] } },
  { n: 67, title: "健康应用", when: "phone|idle|day|morning",
    text: "手机提醒，{名字}已经连续三天没有完成健身目标，态度明显。",
    a: { label: "现在做一组室内伸展。", out: [
      { text: "活动完身体舒服了一些，{名字}决定明天也可以做一点。", mood: { name: "伸展真舒服", emo: "energized", pts: 2, min: 180 }, need: { energy: 5 } },
      { text: "软件没有识别到动作，只弹出一句继续加油。{名字}对着手机又伸了一次胳膊。", mood: { name: "对着手机伸臂", emo: "embarrassed", pts: 1, min: 90 }, need: { energy: 3 } } ] },
    b: { label: "关闭提醒。", out: [
      { text: "手机终于安静，{名字}可以按自己的安排休息。", mood: { name: "手机安静了", emo: "happy", pts: 1, min: 120 } },
      { text: "进入设置时，又看到了其他几项未完成的目标。这次提醒比平时更加集中。", mood: { name: "目标集中轰炸", emo: "tense", pts: 1, min: 150 } } ] } },
  { n: 68, title: "替你交朋友", when: "phone|screen|idle",
    text: "{名字}想输入好的，输入法却补成了好的宝贝。",
    a: { label: "快撤回呀！", out: [
      { text: "多余的两个字被及时撤回，对话平稳继续------别想太多。" },
      { text: "检查完忘了发送，对方等了一阵，又问{名字}是不是现在讲不太方便。", mood: { name: "忘了发送", emo: "embarrassed", pts: 1, min: 90 }, need: { social: 3 } } ] },
    b: { label: "已经发了，就当一次亲切尝试。", out: [
      { text: "对方愉快地接住了这个称呼，聊天比平时更轻松。", mood: { name: "宝贝被接住", emo: "flirty", pts: 2, min: 180 }, need: { social: 10 } },
      { text: "对方回复了一句非常正式的不用。{名字}决定暂时让输入法安静一点。", mood: { name: "正式的不用", emo: "embarrassed", pts: 2, min: 150 } } ] } },
  { n: 69, title: "神秘截图", when: "phone|idle|bored",
    text: "相册里有一张半年前的截图。{名字}当时显然觉得它很重要。",
    a: { label: "研究里面的信息。", out: [
      { text: "原来是一条实用技巧，{名字}终于把它用在了生活里。", mood: { name: "截图派上用场", emo: "inspired", pts: 1, min: 150 } },
      { text: "截图是一张优惠券，活动早就结束。{名字}看着有效期，确认自己曾经确实很有准备。", mood: { name: "过期的准备", emo: "sad", pts: 1, min: 90 } } ] },
    b: { label: "删掉，整理相册。", out: [
      { text: "相册清爽了一些，{名字}顺势又删掉了几张重复照片。", mood: { name: "相册清爽了", emo: "energized", pts: 1, min: 120 } },
      { text: "删除后突然想起用途，{名字}赶紧去最近删除里把它找了回来。", mood: { name: "赶紧捡回来", emo: "tense", pts: 1, min: 60 } } ] } },
  { n: 70, title: "存储空间不足！", when: "phone|idle",
    text: "空间快满了。占地方最多的是一个自称轻量的应用。",
    a: { label: "清理缓存。", out: [
      { text: "腾出了不少空间，手机终于不再反复提醒。", mood: { name: "空间腾出来了", emo: "happy", pts: 1, min: 120 } },
      { text: "没过多久，缓存又长了回来。{名字}感觉自己只是给软件腾出了一块活动场地。", mood: { name: "缓存又长回", emo: "angry", pts: 1, min: 120 } } ] },
    b: { label: "删除几个不用的应用。", out: [
      { text: "桌面干净了，{名字}找常用软件也更方便。", mood: { name: "桌面干净了", emo: "energized", pts: 1, min: 120 } },
      { text: "一个很久没打开的软件认真询问是否真的舍得离开。{名字}居然停顿了一下。", mood: { name: "被软件挽留", emo: "sad", pts: 1, min: 90 } } ] } },
  { n: 71, title: "比自己更了解自己", when: "phone|screen|idle|tired",
    text: "{名字}刚想着换个枕头，手机就推来了枕头广告。",
    a: { label: "检查推荐和隐私设置。", out: [
      { text: "{名字}找到了相关选项，把不需要的推荐关掉了。", mood: { name: "关掉推荐", emo: "confident", pts: 1, min: 120 } },
      { text: "设置一层套一层，{名字}看完后，对手机的信任比刚才更少了一点。", mood: { name: "对手机设防", emo: "scared", pts: 1, min: 180 } } ] },
    b: { label: "看看它到底推荐什么。", out: [
      { text: "广告里的信息确实有参考价值，{名字}对怎么选枕头更有把握了。", mood: { name: "懂了选枕头", emo: "focused", pts: 1, min: 120 } },
      { text: "此后几乎所有广告都是枕头，轮流劝{名字}睡觉。", mood: { name: "枕头劝我睡", emo: "dazed", pts: 1, min: 150 } } ] } },
  { n: 72, title: "网络延迟", when: "screen|tv|computer",
    text: "视频停在一个极其尴尬的表情上，{名字}也替主演着急。",
    a: { label: "重启路由器。", out: [
      { text: "网络恢复，画面里的人终于完成了那个表情。", mood: { name: "表情终于做完", emo: "happy", pts: 1, min: 90 }, need: { fun: 5 } },
      { text: "设备需要重新连接，{名字}却忘了密码。视频暂时连卡住的机会都没有了。", mood: { name: "忘了网络密码", emo: "angry", pts: 2, min: 150 } } ] },
    b: { label: "趁机做点别的。", out: [
      { text: "{名字}清理了一下桌面，回过神时视频也恢复了。", mood: { name: "顺手清了桌面", emo: "energized", pts: 1, min: 120 }, need: { fun: 5 } },
      { text: "视频在{名字}离开后自动播放，最关键的情节已经自己演完了。", mood: { name: "错过关键情节", emo: "sad", pts: 1, min: 150 } } ] } },
  { n: 73, title: "99%", when: "computer|screen",
    text: "进度已经到百分之九十九。最后那一点可能需要人工搬运。",
    a: { label: "耐心等待。", out: [
      { text: "好在只卡了一会，下载终于完成。", mood: { name: "下载完成", emo: "happy", pts: 1, min: 90 } },
      { text: "等了很久，页面弹出提示，要求释放更多空间。{名字}重新坐了回去。", mood: { name: "空间又不够", emo: "bored", pts: 1, min: 120 } } ] },
    b: { label: "暂停后继续。", out: [
      { text: "进度重新动起来，{名字}觉得自己的操作非常及时。", mood: { name: "操作很及时", emo: "confident", pts: 1, min: 120 } },
      { text: "下载从头开始。{名字}盯着新的百分之一，决定以后少干预一点。", mood: { name: "从头再来", emo: "angry", pts: 2, min: 150 } } ] } },
  { n: 74, title: "智能助手", when: "idle|inLiving|inBedroom",
    text: "{名字}说放点轻音乐，设备开始播放清洁教学。",
    a: { label: "重新说清楚。", out: [
      { text: "设备终于放对了内容，房间里响起轻柔的音乐。", mood: { name: "音乐终于对了", emo: "happy", pts: 1, min: 150 }, need: { fun: 8 } },
      { text: "再次识别错误后，{名字}开始用字正腔圆的播音腔发出请求。", mood: { name: "播音腔请求", emo: "playful", pts: 1, min: 90 } } ] },
    b: { label: "既然来了，就听一听。", out: [
      { text: "教程里有个方法很好用，{名字}顺便解决了一处难清理的污渍。", mood: { name: "污渍清掉了", emo: "confident", pts: 1, min: 150 }, need: { hygiene: 5 } },
      { text: "听完后，{名字}忽然觉得家里到处都需要擦一下，休息计划暂时搁置。", mood: { name: "休息被搁置", emo: "uncomfortable", pts: 1, min: 150 }, need: { energy: -8 } } ] } },
  { n: 75, title: "看完这一集就睡", when: "evening|night",
    text: "一集结束，下一集自动开始。",
    a: { label: "立刻关闭。", out: [
      { text: "及时洗漱上床养成好习惯！", mood: { name: "早早上床", emo: "confident", pts: 2, min: 240 }, need: { hygiene: 5, energy: 10 } },
      { text: "关在悬念最强的地方。躺下以后，{名字}在脑中替编剧写了三个版本的后续。", mood: { name: "脑补后续", emo: "inspired", pts: 1, min: 180 }, need: { energy: -5 } } ] },
    b: { label: "再看五分钟。", out: [
      { text: "恰好解开一个悬念，{名字}满意地关掉了视频。", mood: { name: "悬念解开了", emo: "happy", pts: 1, min: 150 }, need: { fun: 10 } },
      { text: "五分钟后出现了更大的悬念。{名字}重新看了一眼时间，暂时没有按暂停。", mood: { name: "又一个悬念", emo: "tense", pts: 1, min: 180 }, need: { fun: 8, energy: -10 } } ] } },
  { n: 76, title: "欢迎仪式", when: "computer|phone|inStudy|idle",
    text: "{名字}打开学习软件的线上课。软件先颁发了一枚成功开始学习的徽章。",
    a: { label: "趁热学完一节。", out: [
      { text: "一节课顺利完成，{名字}终于知道自己刚才在学什么了。", mood: { name: "终于学懂了", emo: "focused", pts: 2, min: 180 } },
      { text: "课程比预想难得多。{名字}看了一眼徽章觉得，它发得有些早。", mood: { name: "课程好难", emo: "tense", pts: 1, min: 120 } } ] },
    b: { label: "先研究学习计划。", out: [
      { text: "{名字}排好了适合自己的时间，准备从明天开始认真学。", mood: { name: "计划排好了", emo: "confident", pts: 1, min: 120 } },
      { text: "又收到一枚完善计划的徽章。知识还没增加，展示栏已经热闹起来。", mood: { name: "徽章又多一枚", emo: "playful", pts: 1, min: 90 } } ] } },
  { n: 77, title: "纠错冲动", when: "screen|idle",
    text: "{名字}刷到一条明显错误的生活常识。下面有很多人回复学到了。",
    a: { label: "附上来源，礼貌纠正。", out: [
      { text: "有人认真看完资料，回来向{名字}道谢。", mood: { name: "被道谢了", emo: "confident", pts: 2, min: 180 }, need: { social: 5 } },
      { text: "对方开始争论，话题越扯越远。{名字}最后关掉页面，去喝了杯水。", mood: { name: "越争越远", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "划过去。", out: [
      { text: "{名字}很快看到了别的内容，没让这件事占用自己的晚上。", mood: { name: "放过自己了", emo: "happy", pts: 1, min: 60 } },
      { text: "平台以为{名字}对此感兴趣，又推来了几条类似内容。", mood: { name: "又推来了", emo: "uncomfortable", pts: 1, min: 90 } } ] } },
  { n: 78, title: "一条意外受欢迎的动态", when: "phone|screen|idle",
    text: "{名字}随手发了一句今天不想努力，竟然收到了许多赞。",
    a: { label: "继续分享普通日常。", out: [
      { text: "朋友们也开始讲自己的小事，评论区变成了轻松的聊天角落。", mood: { name: "评论区真暖", emo: "happy", pts: 2, min: 240 }, need: { social: 10 } },
      { text: "{名字}开始反复琢磨下一条该发什么------普通日常忽然需要提前准备了。", mood: { name: "下一条发啥", emo: "tense", pts: 1, min: 120 } } ] },
    b: { label: "关掉通知。", out: [
      { text: "{名字}把手机放下，安安稳稳地做完了手头的事。", mood: { name: "安稳做完事", emo: "focused", pts: 1, min: 120 } },
      { text: "再打开时，朋友们已经在评论区聊了很久。{名字}往上翻了半天才跟上自己动态里的话题。", mood: { name: "翻半天楼", emo: "dazed", pts: 1, min: 90 }, need: { social: 5 } } ] } },
  { n: 79, title: "AI给出的完美计划", when: "morning|screen|idle",
    text: "{名字}请AI规划自己一天。它建议六点起床，并在上午完成运动、学习、整理房间以及大部分人生目标。",
    a: { label: "挑一件做得到的开始。", out: [
      { text: "一个小目标顺利完成，{名字}觉得今天已经有了不错的开头。", mood: { name: "开了好头", emo: "energized", pts: 2, min: 180 } },
      { text: "第一项就比想象中累。{名字}决定下次先完善prompt，自己的体力没有人家假设的那么充足。", mood: { name: "体力不支", emo: "uncomfortable", pts: 1, min: 120 }, need: { energy: -10 } } ] },
    b: { label: "要求它充分考虑躺着。", out: [
      { text: "新计划终于留出了休息时间，看起来可以照着做。", mood: { name: "计划能执行", emo: "happy", pts: 1, min: 120 } },
      { text: "AI郑重写下有意识地平躺十五分钟。{名字}调整好姿势开始执行。", mood: { name: "认真躺平", emo: "playful", pts: 2, min: 120 }, need: { energy: 5 } } ] } },
  { n: 80, title: "你像一把椅子", when: "screen|idle|bored",
    text: "做了个网页小测试，结果写着：稳定、可靠，常被忽略。",
    a: { label: "转发给朋友。", out: [
      { text: "大家开始分享自己离谱的测试结果，聊天很快热闹起来。", mood: { name: "测试聊嗨了", emo: "playful", pts: 2, min: 180 }, need: { social: 8, fun: 5 } },
      { text: "朋友回复挺准的。{名字}想了想，不知道对方具体认可哪一部分。", mood: { name: "挺准是哪准", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "再测一次。", out: [
      { text: "新结果是一盏台灯。{名字}觉得自己的用途正在逐渐丰富。", mood: { name: "升级成台灯", emo: "playful", pts: 1, min: 120 }, need: { fun: 3 } },
      { text: "结果依然是椅子。{名字}关掉页面并换了个坐姿。", mood: { name: "又是椅子", emo: "embarrassed", pts: 1, min: 90 } } ] } },
  { n: 81, title: "隔壁正在拼装什么", when: "",
    text: "隔墙传来几声敲击，停了一会儿，又传来一声很长的叹气。",
    a: { label: "发消息问需不需要电子版说明书。", out: [
      { text: "邻居正好找不到说明书，收到链接后连声道谢。", mood: { name: "帮到邻居了", emo: "happy", pts: 2, min: 180 }, need: { social: 5 } },
      { text: "对方说自己只是在咬一块特别硬的食物。{名字}对这顿饭肃然起敬。", mood: { name: "肃然起敬", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "戴上耳机。", out: [
      { text: "耳机挡住了大部分声音，{名字}可以继续自己的事。", mood: { name: "耳机真管用", emo: "focused", pts: 1, min: 120 } },
      { text: "------我耳机呢？！接下来是带噪音且漫长的找耳机时间。", mood: { name: "耳机去哪了", emo: "angry", pts: 2, min: 120 } } ] } },
  { n: 82, title: "楼上的滚动物", when: "",
    text: "天花板上方传来小东西滚动的声音。每次{名字}准备忘记，它就再滚一次。",
    a: { label: "发消息询问。", out: [
      { text: "原来是椅轮。邻居调整以后，声音很快停了。", mood: { name: "声音停了", emo: "happy", pts: 1, min: 120 } },
      { text: "邻居说自己也听见了，正在找来源。目前这事已经有两位调查者。", mood: { name: "联合调查中", emo: "playful", pts: 1, min: 120 }, need: { social: 3 } } ] },
    b: { label: "用背景音乐盖住。", out: [
      { text: "音乐很合适，{名字}慢慢不再留意天花板。", mood: { name: "音乐真合适", emo: "focused", pts: 1, min: 120 }, need: { fun: 5 } },
      { text: "滚动声刚好踩着节拍，{名字}听着听着，开始期待它下一次加入。", mood: { name: "等它加入", emo: "playful", pts: 1, min: 90 } } ] } },
  { n: 83, title: "失物公告", when: "phone|screen|idle|inKitchen",
    text: "邻里群里有人发了一张照片，问谁丢了一个盖子。照片里确实是个盖子，仅此而已。",
    a: { label: "检查自己家的容器。", out: [
      { text: "不是{名字}的，但检查时顺便给几个盒子配上了正确的盖。", mood: { name: "盒盖配齐了", emo: "confident", pts: 1, min: 120 } },
      { text: "{名字}找到了三个没盖子的盒子，忽然理解了这条公告的必要性。", mood: { name: "盖子都去哪", emo: "dazed", pts: 1, min: 90 } } ] },
    b: { label: "回复请问多大。", out: [
      { text: "对方补上了尺寸，失主很快出现。", mood: { name: "帮失主找到", emo: "happy", pts: 1, min: 120 } },
      { text: "对方回答，大概普通盖子那么大。{名字}暂时没有继续提问。", mood: { name: "问了个寂寞", emo: "bored", pts: 1, min: 60 } } ] } },
  { n: 84, title: "发生了什么", when: "evening|night|tv|idle",
    text: "隔壁电视机连续传来震惊的惊呼。{名字}没看节目却已经有点紧张了。",
    a: { label: "发消息问节目名字。", out: [
      { text: "对方推荐了一部有趣的作品，{名字}记进了待看列表。", mood: { name: "待看又加一部", emo: "inspired", pts: 1, min: 120 } },
      { text: "对方直接解释了为什么惊呼，连同关键剧情一起说完了。", mood: { name: "被剧透了", emo: "angry", pts: 2, min: 180 } } ] },
    b: { label: "不问，自己猜。", out: [
      { text: "{名字}编出一个越来越离谱的故事，最后把自己逗笑了。", mood: { name: "自己逗笑了", emo: "playful", pts: 2, min: 120 }, need: { fun: 5 } },
      { text: "想象得太精彩，{名字}反而担心真实节目没有这么好看。", mood: { name: "脑补太精彩", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 85, title: "邻里群里的神秘投票", when: "phone|screen|idle",
    text: "投票题目是大家觉得这样合适吗，没有解释这样是什么。",
    a: { label: "先问清楚。", out: [
      { text: "发起者发现漏发了图片，连忙补上。", mood: { name: "图补上了", emo: "happy", pts: 1, min: 60 } },
      { text: "大家发现{名字}问得很有条理，顺势请{名字}整理一下后续意见。", mood: { name: "问出了差事", emo: "confident", pts: 1, min: 120 } } ] },
    b: { label: "暂时不投。", out: [
      { text: "很快有人提出同样的问题，{名字}安静等到了说明。", mood: { name: "不急一时", emo: "confident", pts: 1, min: 60 } },
      { text: "其他人纷纷投票，{名字}看着结果怀疑是不是自己漏看了什么。", mood: { name: "漏看了啥", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 86, title: "一声来自墙后的喷嚏", when: "",
    text: "隔壁打了个喷嚏。{名字}下意识说了声保重，说完才想起隔着墙。",
    a: { label: "就这样吧。", out: [
      { text: "对面传来一句谢谢，双方又各自安静下来。", mood: { name: "隔墙道谢", emo: "happy", pts: 1, min: 120 }, need: { social: 3 } },
      { text: "没有任何回应。{名字}坐了一会儿，决定对方大概没听见。", mood: { name: "对方没听见", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "轻咳一声，掩饰刚才的话。", out: [
      { text: "这声轻咳让{名字}自在了些，事情很快过去。", mood: { name: "咳过去了", emo: "embarrassed", pts: 1, min: 60 } },
      { text: "隔壁反过来说了句你也保重。两个人隔着墙完成了一次简短的健康问候。", mood: { name: "隔墙问候", emo: "happy", pts: 2, min: 180 }, need: { social: 5 } } ] } },
  { n: 87, title: "练歌时间", when: "day|evening|idle",
    text: "同一句高音反复出现，每次都差一点。",
    a: { label: "发消息鼓励。", out: [
      { text: "邻居很感动，也意识到声音传得有点远，主动调低了音量。", mood: { name: "邻居很领情", emo: "happy", pts: 2, min: 180 }, need: { social: 5 } },
      { text: "对方觉得{名字}很懂音乐，发来完整录音，请{名字}提些专业意见。", mood: { name: "成了乐评人", emo: "tense", pts: 1, min: 120 } } ] },
    b: { label: "默默替对方使劲。", out: [
      { text: "高音终于唱上去了，{名字}忍不住跟着点了一下头。", mood: { name: "高音上去了", emo: "happy", pts: 2, min: 120 } },
      { text: "对方停止练习，{名字}却开始在脑中反复播放那一句，连缺的那一点都记得很清楚。", mood: { name: "高音洗脑", emo: "uncomfortable", pts: 1, min: 120 } } ] } },
  { n: 88, title: "手动艾特", when: "phone|evening|night|idle",
    text: "邻里群突然艾特提醒所有人。内容是：打扰一下，有人醒着吗？",
    a: { label: "\"现在醒了\"", out: [
      { text: "群里有人笑了，发消息的人赶紧道歉并说明正事。", mood: { name: "群友被逗笑", emo: "playful", pts: 2, min: 120 }, need: { social: 3 } },
      { text: "对方没听出意思，认真问{名字}是不是睡得不太好。", mood: { name: "被关心睡眠", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "静待对方说事情。", out: [
      { text: "原来只是误操作，对方很快解释清楚。" },
      { text: "对方又提醒了一次所有人，想确认刚才的消息有没有成功发出。", mood: { name: "又被艾特", emo: "bored", pts: 1, min: 60 } } ] } },
  { n: 89, title: "家里的回声", when: "idle|lonely|inLiving|inBedroom",
    text: "{名字}独自在家哼了一句，隔壁竟然接上了同一首歌的下一句。",
    a: { label: "再哼一句。", out: [
      { text: "对方又接上了，两个人隔墙唱完了一小段，各自笑了起来。", mood: { name: "隔墙合唱", emo: "happy", pts: 3, min: 240 }, need: { social: 10, fun: 10 } },
      { text: "{名字}唱错了歌词，对面突然安静。{名字}决定到此为止。", mood: { name: "唱错歌词", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "安静下来。", out: [
      { text: "对面也很快停了，房间重新恢复安静。" },
      { text: "对方又唱了一句，像是在等{名字}接力。{名字}坐在原地，感觉自己漏参加了谢幕。", mood: { name: "错过接力", emo: "sad", pts: 1, min: 120 } } ] } },
  { n: 90, title: "缺水", when: "day|evening|phone",
    text: "通知说今晚可能停水，但没有进一步解释。",
    a: { label: "准备适量用水。", out: [
      { text: "晚上确实停水了，提前准备的水刚好派上用场。", mood: { name: "有备无患", emo: "confident", pts: 2, min: 180 } },
      { text: "最后没有停水，但{名字}也因此提前完成了洗漱，不用睡前再忙。", mood: { name: "提前洗漱完", emo: "happy", pts: 1, min: 120 }, need: { hygiene: 15 } } ] },
    b: { label: "先等等后续通知。", out: [
      { text: "很快收到取消消息，{名字}照常安排自己的晚上。", mood: { name: "照常过晚上", emo: "happy", pts: 1, min: 60 } },
      { text: "洗漱到一半，水停了。{名字}看着镜子里的泡沫，决定以后认真对待可能这两个字。", mood: { name: "满脸泡沫", emo: "angry", pts: 2, min: 180 }, need: { hygiene: -10 } } ] } },
  { n: 91, title: "给家电起名字", when: "inKitchen|cooking|eating|hungry|idle",
    text: "{名字}觉得天天相处的家电至少该有个称呼。冰箱暂定叫冷静。",
    a: { label: "给所有家电都起名。", out: [
      { text: "房间忽然亲切起来，{名字}做家务时偶尔还会叫它们一声。", mood: { name: "家电变亲切", emo: "happy", pts: 2, min: 240 } },
      { text: "微波炉被命名为热情，热出来的饭却依然中间凉着。{名字}认为它还需要努力。", mood: { name: "热情还得练", emo: "playful", pts: 1, min: 90 } } ] },
    b: { label: "只给冰箱起名。", out: [
      { text: "每次打开冰箱{名字}都会想起这个名字，这其实还挺合适的。", mood: { name: "冷静挺贴切", emo: "happy", pts: 1, min: 120 } },
      { text: "{名字}对朋友打电话说冷静里还有半块蛋糕，对方沉默了一下，问冷静是谁。", mood: { name: "冷静是谁", emo: "embarrassed", pts: 1, min: 90 }, need: { social: 5 } } ] } },
  { n: 92, title: "帅气转身", when: "idle|bored|inBedroom|inBath",
    text: "{名字}觉得现在很适合练习说完一句话就转身离开的动作。",
    a: { label: "认真排练。", out: [
      { text: "练了几次，终于有了点气势。{名字}决定暂时不向任何人展示。", mood: { name: "练出气势", emo: "confident", pts: 2, min: 180 } },
      { text: "转身很成功，但转到一半忘了要往哪里走，最后又默默转了回来。", mood: { name: "转到迷路", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "改练一个自然的微笑。", out: [
      { text: "试着笑了几次，{名字}自己也跟着开心了一点。", mood: { name: "笑开心了", emo: "happy", pts: 1, min: 120 } },
      { text: "照镜子越久，越不知道嘴角应该放在哪里。{名字}决定先让脸自行运作。", mood: { name: "嘴角迷路", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 93, title: "对着物品发脾气", when: "",
    text: "一个抽屉卡住了。{名字}已经对它讲了三遍脏话。",
    a: { label: "冷静检查哪里卡住。", out: [
      { text: "找到卡住的东西，抽屉终于顺畅打开。", mood: { name: "抽屉开了", emo: "happy", pts: 1, min: 120 } },
      { text: "卡住的正是{名字}昨天硬塞进去的东西。{名字}把它拿出来，没有继续追究责任。", mood: { name: "罪魁是自己", emo: "embarrassed", pts: 1, min: 90 } } ] },
    b: { label: "先离开一会儿。", out: [
      { text: "回来后轻轻调整了一下，抽屉就开了，{名字}也不再生气。", mood: { name: "气消了", emo: "happy", pts: 1, min: 120 } },
      { text: "回来时已经忘了要拿什么，抽屉暂时不必作出让步。", mood: { name: "忘了拿啥", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 94, title: "那件丢脸的旧事", when: "evening|night|idle|tired",
    text: "多年前说错的一句话毫无预告地回到了{名字}脑中。",
    a: { label: "提醒自己别人早忘了。", out: [
      { text: "大概确实只有自己还记得，慢慢放下了这件事。", mood: { name: "放下旧事", emo: "happy", pts: 1, min: 120 } },
      { text: "为了证明自己记性很好，大脑又提供了另外两件尴尬往事。", mood: { name: "尴尬连播", emo: "embarrassed", pts: 2, min: 180 } } ] },
    b: { label: "联系当时的朋友试着自嘲。", out: [
      { text: "对方完全不记得，{名字}终于可以安心把它翻篇。", mood: { name: "终于翻篇", emo: "happy", pts: 2, min: 240 }, need: { social: 5 } },
      { text: "对方被成功唤醒了记忆，还热心补充了几个{名字}已经忘记的细节。", mood: { name: "被补充细节", emo: "embarrassed", pts: 3, min: 240 }, need: { social: 5 } } ] } },
  { n: 95, title: "和未来的自己谈判", when: "day|evening|computer|inStudy|idle",
    text: "{名字}准备把一件麻烦事留给明天。明天精神会更好，这句话听起来很熟。",
    a: { label: "现在先做十分钟。", out: [
      { text: "事情比想象中简单，十分钟还没到就完成了。", mood: { name: "十分钟搞定", emo: "energized", pts: 2, min: 180 } },
      { text: "只做完一部分，但最难开始的那一步已经过去，剩下的有了头绪。", mood: { name: "开了个头", emo: "focused", pts: 1, min: 120 } } ] },
    b: { label: "给明天的自己写清楚步骤。", out: [
      { text: "第二天照着步骤做，确实顺利了很多。", mood: { name: "步骤真好用", emo: "confident", pts: 2, min: 180 } },
      { text: "写到关键位置，{名字}留下了到时候想办法几个字。明天的自己依然需要临场发挥。", mood: { name: "到时候再说", emo: "tense", pts: 1, min: 120 } } ] } },
  { n: 96, title: "家庭颁奖典礼", when: "day|evening|goodMood|idle",
    text: "{名字}今天完成了一件平时总拖着的事。家里没有观众，但颁奖可以自己来。",
    a: { label: "发表获奖感言。", out: [
      { text: "{名字}认真感谢了自己的坚持，讲完以后，竟然觉得这件小事很值得庆祝。", mood: { name: "值得庆祝", emo: "confident", pts: 2, min: 240 } },
      { text: "感言说得越来越投入，{名字}一时忘了自己究竟完成了什么，但还是顺利感谢了所有家电。", mood: { name: "感谢家电", emo: "playful", pts: 1, min: 120 } } ] },
    b: { label: "奖励一份小零食。", out: [
      { text: "{名字}舒服地吃完零食，决定下次也给自己留一点盼头。", mood: { name: "零食奖励", emo: "happy", pts: 1, min: 120 }, need: { hunger: 8 } },
      { text: "包装打开时掉出一片碎屑，{名字}看着地板，发现下一项家务已经开始了。", mood: { name: "又要扫地", emo: "bored", pts: 1, min: 90 }, need: { hunger: 5 } } ] } },
  { n: 97, title: "一场只有自己的辩论", when: "screen|idle",
    text: "{名字}想买件东西。脑中的一方说值得，另一方说先看看余额。双方都没有离场的打算。",
    a: { label: "把理由写下来。", out: [
      { text: "写着写着，实际需求清楚了，{名字}终于做出了不再反复的决定。", mood: { name: "想清楚了", emo: "confident", pts: 2, min: 180 } },
      { text: "{名字}写出一篇论证严密的购买申请，看完以后，连自己都很难拒绝。", mood: { name: "说服了自己", emo: "playful", pts: 1, min: 120 } } ] },
    b: { label: "先等一天。", out: [
      { text: "第二天已经不太想买了，{名字}把页面关掉，没再惦记。", mood: { name: "不想买了", emo: "happy", pts: 1, min: 120 } },
      { text: "第二天更想买了，优惠却刚好结束。{名字}又开始了新一轮辩论。", mood: { name: "错过优惠", emo: "sad", pts: 2, min: 180 } } ] } },
  { n: 98, title: "独居自由", when: "eating|hungry|inKitchen|cooking|inLiving",
    text: "{名字}意识到，现在就算端着大碗、裹着毯子坐地上吃饭，也不会有人管。",
    a: { label: "执行这个自由的想法。", out: [
      { text: "饭很好吃，毯子很暖，{名字}觉得这个位置以后还可以再用。", mood: { name: "地上真香", emo: "happy", pts: 2, min: 180 }, need: { hunger: 25 } },
      { text: "坐下时很舒服，吃完以后却不太方便站起来。{名字}先把碗安置好，再重新研究自己的姿势。", mood: { name: "起不来了", emo: "uncomfortable", pts: 1, min: 90 }, need: { hunger: 25 } } ] },
    b: { label: "还是认真坐到桌前。", out: [
      { text: "桌面宽敞，碗筷顺手，{名字}安稳地吃完了一餐。", mood: { name: "安稳一餐", emo: "happy", pts: 1, min: 120 }, need: { hunger: 20 } },
      { text: "吃到一半，{名字}想起刚才的自由，默默把毯子拿来披在了肩上。", mood: { name: "披上毯子", emo: "playful", pts: 1, min: 120 }, need: { hunger: 20 } } ] } },
  { n: 99, title: "写给这间屋子的投诉", when: "",
    text: "{名字}今天被桌角、柜门和卷起的地毯接连惹恼，决定好好整顿。",
    a: { label: "列清问题，逐项处理。", out: [
      { text: "几处不方便的地方得到调整，{名字}在家走动终于顺畅了些。", mood: { name: "家里顺畅了", emo: "confident", pts: 2, min: 240 } },
      { text: "清单越写越长，{名字}看着纸，发现自己正在给自己安排接下来几天的事。", mood: { name: "清单好长", emo: "tense", pts: 1, min: 120 } } ] },
    b: { label: "写一封措辞强硬的投诉信。", out: [
      { text: "写完后舒服多了，{名字}把信放在一边，暂时原谅了家具。", mood: { name: "原谅家具", emo: "happy", pts: 1, min: 120 } },
      { text: "结尾习惯性写上请尽快整改。{名字}看着收件人一栏，决定明天再处理。", mood: { name: "投诉无门", emo: "dazed", pts: 1, min: 90 } } ] } },
  { n: 100, title: "普通的一天", when: "evening|night|tired",
    text: "今天没有大事发生。{名字}吃了饭，做了一点事，和人说了几句话，又在某个地方坐了很久。睡前，{名字}忽然想给今天起个标题。",
    a: { label: "《一切尽在掌握》", out: [
      { text: "{名字}满意地关了灯，觉得今天过得还不错。", mood: { name: "今天不错", emo: "happy", pts: 2, min: 240 } },
      { text: "刚写完，就想起一件忘记做的事。{名字}看看标题，决定先不修改，起身去补上。", mood: { name: "还有事没做", emo: "tense", pts: 1, min: 90 } } ] },
    b: { label: "《今天也算数》", out: [
      { text: "{名字}回想起今天几件很小的好事，安安稳稳地躺了下来。", mood: { name: "小事也算数", emo: "happy", pts: 2, min: 240 } },
      { text: "越想越发现今天其实做了不少。{名字}想，明天也差不多这样就行。", mood: { name: "明天照旧", emo: "confident", pts: 1, min: 180 } } ] } },
];
