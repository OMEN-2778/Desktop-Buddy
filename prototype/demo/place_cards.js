// ================================================================ chance cards out and about
// User: 50 more for each place she can go (家门口 公园 商场 海边), same shape
// as cards_text.js; `at` = the place. They come only there, rolled hourly.
CARDS.push(
  { n: 201, title: "窗台上的保安", at: "front", when: "",
    text: "隔壁窗台上的橘猫睡得四仰八叉，肚皮正对着{名字}。",
    a: { label: "伸手摸一下肚皮。", out: [
      { text: "猫眯着眼让{名字}摸了三秒，然后翻个身继续睡，好像什么都没发生。", say: "三秒！我有三秒的面子！", mood: { name: "摸到了猫肚皮", emo: "confident", pts: 3, min: 180 } },
      { text: "猫闪电般抱住{名字}的手又咬又蹬，然后若无其事地继续睡。", say: "这是陷阱，绝对是陷阱。", mood: { name: "中了肚皮陷阱", emo: "embarrassed", pts: 2, min: 150 } } ] },
    b: { label: "在旁边陪它晒太阳。", out: [
      { text: "{名字}在台阶上躺平，和猫一起晒成了两块暖洋洋的面包。", say: "晒透了，翻个面。", mood: { name: "晒得晕乎乎", emo: "dazed", pts: 3, min: 150 }, need: { energy: 6 } },
      { text: "太阳挪走了，猫跟着太阳挪了窝，{名字}没跟上，被留在了阴影里。", say: "太阳和猫都不等我。", mood: { name: "被太阳抛下", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 202, title: "麻雀例会", at: "front", when: "",
    text: "一群麻雀落在人行道上叽叽喳喳，看起来正在开很重要的会。",
    a: { label: "撒点饼干屑当茶歇。", out: [
      { text: "麻雀们一拥而上，会议当场改成了聚餐，{名字}被默认成了赞助方。", say: "本次会议由我赞助！", mood: { name: "赞助了麻雀", emo: "playful", pts: 3, min: 180 } },
      { text: "饼干屑引来一只鸽子，鸽子吃完就走，麻雀们集体瞪着{名字}。", say: "我不是故意请鸽子的……", mood: { name: "被麻雀集体瞪", emo: "scared", pts: 2, min: 120 } } ] },
    b: { label: "蹲下来旁听。", out: [
      { text: "{名字}听了很久，基本确定议题是“那棵树到底归谁”。", say: "我投左边那只一票。", mood: { name: "旁听麻雀开会", emo: "focused", pts: 3, min: 150 } },
      { text: "麻雀们发现有人旁听，立刻宣布散会，一哄而飞。", say: "我还没发言呢！", mood: { name: "把会议搅黄了", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 203, title: "水管扫射", at: "front", when: "",
    text: "浅蓝房子的邻居在门口浇花，水管一甩一甩，正朝{名字}这边扫过来。",
    a: { label: "快速闪避。", out: [
      { text: "{名字}一个侧身躲了过去，连邻居都忍不住鼓掌。", say: "这身法，练过的。", mood: { name: "躲过水管扫射", emo: "confident", pts: 3, min: 150 } },
      { text: "躲过了第一下，没躲过回马枪，半边身子湿透了。", say: "它会拐弯！它会拐弯！", mood: { name: "被水管偷袭", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "张开手迎上去。", out: [
      { text: "凉水哗地浇下来，{名字}和邻居都笑得停不下来。", say: "好凉快！再来一下！", mood: { name: "门口打水仗", emo: "playful", pts: 4, min: 180 }, need: { fun: 10 } },
      { text: "邻居吓了一跳连声道歉，{名字}湿漉漉地站在原地，突然有点后悔。", say: "嗯……其实也没那么热。", mood: { name: "湿成落汤鸡", emo: "uncomfortable", pts: 2, min: 120 } } ] } },
  { n: 204, title: "奶奶的大花盆", at: "front", when: "",
    text: "砖房的奶奶想把一盆大花挪到门口，正对着它叹气。",
    a: { label: "撸起袖子帮忙。", out: [
      { text: "两人嘿哟嘿哟地把花盆搬到了位，奶奶硬塞给{名字}一把糖。", say: "这糖是劳动报酬！", mood: { name: "帮奶奶搬花盆", emo: "energized", pts: 3, min: 180 }, need: { social: 10 } },
      { text: "花盆纹丝不动，{名字}憋红了脸，最后奶奶自己一推就挪开了。", say: "奶奶，您深藏不露啊。", mood: { name: "力气输给奶奶", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "建议用滑板车运。", out: [
      { text: "花盆坐上滑板车稳稳到位，奶奶直夸{名字}脑子灵。", say: "工程学的胜利！", mood: { name: "想出了妙招", emo: "inspired", pts: 3, min: 180 } },
      { text: "滑板车载着花盆往坡下溜了一段，两人追了半条街。", say: "花盆，你给我站住！", mood: { name: "追了一盆花", emo: "tense", pts: 3, min: 120 }, need: { energy: -8 } } ] } },
  { n: 205, title: "跳房子挑战", at: "front", when: "",
    text: "几个小孩在人行道上用粉笔画了跳房子，问{名字}要不要来一局。",
    a: { label: "当然要来。", out: [
      { text: "{名字}单脚一路跳到终点，小孩们尖叫着承认这位选手很强。", say: "冠军在此，不服来战！", mood: { name: "跳房子赢了", emo: "playful", pts: 4, min: 180 }, need: { fun: 12 } },
      { text: "跳到第六格就站不稳了，{名字}被小孩们宣布“踩线出局”。", say: "那条线明明是歪的。", mood: { name: "跳房子出局", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "帮他们画一条更长的。", out: [
      { text: "{名字}画了一条从门口一直通到街角的超长跳房子，孩子们欢呼着跳了一下午。", say: "这条街今天归你们了。", mood: { name: "画了最长格子", emo: "inspired", pts: 4, min: 180 }, need: { social: 8 } },
      { text: "粉笔画到一半就用完了，后半截只能靠想象。", say: "后面是隐形格子，懂吧？", mood: { name: "粉笔不够用", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 206, title: "送错门的包裹", at: "front", when: "",
    text: "门口多了一个包裹，收件人写的却是隔壁砖房，送件的人早就走远了。",
    a: { label: "亲自送过去。", out: [
      { text: "邻居正等着这个包裹，激动得请{名字}吃了一块刚烤好的饼干。", say: "顺手做好事，还有饼干！", mood: { name: "送对了包裹", emo: "happy", pts: 3, min: 180 }, need: { hunger: 6 } },
      { text: "敲了半天门没人应，{名字}抱着包裹站在门口，像一座尽职的雕像。", say: "我会一直守着它的。", mood: { name: "当了包裹雕像", emo: "bored", pts: 2, min: 120 } } ] },
    b: { label: "放在两家中间的台阶上。", out: [
      { text: "邻居回家一眼就看见了，远远朝{名字}比了个大拇指。", say: "不客气，邻里互助！" },
      { text: "橘猫立刻占领了包裹，坐在上面谁也不让碰。", say: "猫说这是它的快递。", mood: { name: "包裹被猫占了", emo: "playful", pts: 3, min: 120 } } ] } },
  { n: 207, title: "落叶的邀请", at: "front", when: "autumn",
    text: "门口的树下积了一大堆落叶，蓬松得像在发出邀请。",
    a: { label: "助跑，跳进去。", out: [
      { text: "哗啦一声，{名字}陷进金黄的叶子里，满世界都是沙沙声。", say: "秋天的味道！", mood: { name: "跳进落叶堆", emo: "energized", pts: 4, min: 180 }, need: { fun: 12, hygiene: -5 } },
      { text: "叶子底下藏着一个水坑。", say: "……秋天还有别的味道。", mood: { name: "落叶下有水坑", emo: "uncomfortable", pts: 3, min: 150 }, need: { hygiene: -10 } } ] },
    b: { label: "认真扫成一堆。", out: [
      { text: "扫得整整齐齐，路过的邻居夸{名字}是这条街最勤快的人。", say: "嗯，这条街靠我了。", mood: { name: "被夸勤快", emo: "confident", pts: 3, min: 150 } },
      { text: "刚扫好，一阵风吹来，叶子又均匀地铺回了原处。", say: "风，你在跟我开玩笑吗？", mood: { name: "劳动被风推翻", emo: "angry", pts: 3, min: 120 } } ] } },
  { n: 208, title: "门口的新门卫", at: "front", when: "snow",
    text: "下了一夜雪，门口白茫茫一片，正适合堆点什么。",
    a: { label: "堆一个标准雪人。", out: [
      { text: "胡萝卜鼻子，石子眼睛，雪人端端正正地站在门口迎客。", say: "从今天起你就是门卫。", mood: { name: "堆了个雪人", emo: "inspired", pts: 3, min: 200 }, need: { fun: 8 } },
      { text: "雪人的脑袋掉了三次，最后{名字}宣布它是一个坐着的雪人。", say: "它只是比较放松。", mood: { name: "雪人站不住", emo: "dazed", pts: 2, min: 120 } } ] },
    b: { label: "堆一只雪做的橘猫。", out: [
      { text: "雪猫做得惟妙惟肖，真橘猫过来闻了闻，转身走了。", say: "它被自己帅到了吧。", mood: { name: "雪猫以假乱真", emo: "playful", pts: 3, min: 180 } },
      { text: "堆完一看，像一块面包。路过的小孩问：这是面包吗？", say: "是猫……是面包也行。", mood: { name: "雪猫像面包", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 209, title: "圆圆的水坑", at: "front", when: "rain",
    text: "雨下得刚刚好，人行道上积了一个圆圆的水坑，亮晶晶的。",
    a: { label: "一脚踩进去。", out: [
      { text: "水花溅起老高，{名字}忍不住又踩了第二下、第三下。", say: "再来一下，最后一下！", mood: { name: "踩水坑上瘾", emo: "playful", pts: 4, min: 150 }, need: { fun: 10, hygiene: -8 } },
      { text: "水坑比看起来深得多，{名字}一只脚陷到了脚踝。", say: "这是个湖吧？", mood: { name: "水坑深不见底", emo: "scared", pts: 2, min: 120 }, need: { hygiene: -10 } } ] },
    b: { label: "蹲下来看倒影。", out: [
      { text: "水坑里映着树、天空和一个歪着头的{名字}，像一幅小画。", say: "我在画里，好看吗？", mood: { name: "水坑里的风景", emo: "inspired", pts: 3, min: 180 } },
      { text: "一辆车开过，倒影连同{名字}一起被溅成了大花脸。", say: "我刚还在欣赏风景！", mood: { name: "被车溅一身", emo: "angry", pts: 3, min: 120 }, need: { hygiene: -12 } } ] } },
  { n: 210, title: "活地图", at: "front", when: "",
    text: "一位背着大包的路人停下来，问{名字}附近的车站怎么走。",
    a: { label: "详细地指路。", out: [
      { text: "{名字}比划着讲得清清楚楚，路人连声道谢，大步走远了。", say: "我简直是活地图！", mood: { name: "成功指了路", emo: "confident", pts: 3, min: 150 } },
      { text: "讲着讲着{名字}自己也不确定了，两人对着路口研究了半天。", say: "车站……刚才还在那儿的。", mood: { name: "把自己说晕了", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "干脆陪对方走一段。", out: [
      { text: "一路上聊了天气和这条街的猫，到了车站，两人像老朋友一样挥手告别。", say: "一路顺风呀！", mood: { name: "陪路人散步", emo: "energized", pts: 3, min: 150 }, need: { social: 12 } },
      { text: "走到半路发现方向反了，两个人又默默一起往回走。", say: "就当饭后散步了……", mood: { name: "带路带反了", emo: "dazed", pts: 3, min: 120 }, need: { energy: -6 } } ] } },
  { n: 211, title: "帽子出走", at: "front", when: "",
    text: "一阵风把一顶草帽吹到了{名字}脚边，街那头有人一边追一边喊。",
    a: { label: "捡起来送过去。", out: [
      { text: "帽子的主人笑起来很好看，接过帽子时还认真地道了谢。", say: "帽子……很适合你。", mood: { name: "心跳了一下", emo: "flirty", pts: 3, min: 180 } },
      { text: "刚弯腰，风又把帽子卷走了，{名字}和主人一起追了三个路口。", say: "这帽子想去旅行吧！", mood: { name: "追帽子三条街", emo: "energized", pts: 3, min: 120 }, need: { energy: -8 } } ] },
    b: { label: "先戴上试试。", out: [
      { text: "意外地很合适，主人跑到跟前都看愣了，说要不就送给你吧。", say: "那我就不客气啦！", mood: { name: "白得一顶草帽", emo: "happy", pts: 3, min: 180 } },
      { text: "主人跑到跟前，正看见{名字}戴着自己的帽子对着车窗照。", say: "我在帮你……检查帽子。", mood: { name: "被抓包试帽子", emo: "flirty", pts: 3, min: 150 } } ] } },
  { n: 212, title: "零食树", at: "front", when: "",
    text: "门口的树上咚的一声掉下一颗小果子，正好落在{名字}脚边。",
    a: { label: "抬头研究这棵树。", out: [
      { text: "{名字}发现树上结满了小果子，决定以后叫它“零食树”。", say: "原来你是零食树！", mood: { name: "发现零食树", emo: "inspired", pts: 3, min: 150 } },
      { text: "刚一抬头，第二颗果子正好砸在额头上。", say: "好的，我知道了，我走。", mood: { name: "被果子砸头", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "捡起来尝一口。", out: [
      { text: "酸酸甜甜，出乎意料地好吃。", say: "这棵树，很有前途。", mood: { name: "果子挺好吃", emo: "energized", pts: 2, min: 150 }, need: { hunger: 6 } },
      { text: "酸得{名字}整张脸皱成一团，路过的小孩笑得蹲在了地上。", say: "酸……酸到灵魂了。", mood: { name: "被酸到变形", emo: "uncomfortable", pts: 3, min: 120 } } ] } },
  { n: 213, title: "热情的小狗", at: "front", when: "",
    text: "一只小狗在牵绳那头拼命摇尾巴，看样子非常想认识{名字}。",
    a: { label: "蹲下打招呼。", out: [
      { text: "小狗扑上来舔了{名字}一脸，主人说它很少对谁这么热情。", say: "我很受欢迎的嘛！", mood: { name: "被小狗喜欢", emo: "confident", pts: 3, min: 180 }, need: { social: 8, hygiene: -5 } },
      { text: "小狗兴奋得绕着{名字}转圈，牵绳把{名字}的腿缠得结结实实。", say: "我被打包了……", mood: { name: "被狗绳缠住", emo: "dazed", pts: 3, min: 120 } } ] },
    b: { label: "礼貌地点头致意。", out: [
      { text: "主人点头回礼，小狗却一步三回头，看得{名字}有点心软。", say: "下次再玩吧，小家伙。", mood: { name: "辜负了小狗", emo: "sad", pts: 2, min: 120 } },
      { text: "窗台上的橘猫看见了狗，炸毛炸成了一个球，场面一时十分紧张。", say: "猫，冷静，冷静！", mood: { name: "猫狗大战前夕", emo: "tense", pts: 3, min: 120 } } ] } },
  { n: 214, title: "冰棍阿姨", at: "front", when: "summer",
    text: "一个推着小冰柜的阿姨沿街叫卖：冰棍，冰棍，凉快的冰棍！",
    a: { label: "买一根最普通的。", out: [
      { text: "咬一口，凉意从牙齿一路冲上脑门。", say: "啊——活过来了！", mood: { name: "吃了冰棍", emo: "energized", pts: 3, min: 150 }, need: { hunger: 5, fun: 5 } },
      { text: "吃得太慢，冰棍化了一手，还滴在了鞋上。", say: "它在跟我赛跑……", mood: { name: "冰棍化了一手", emo: "uncomfortable", pts: 2, min: 120 }, need: { hygiene: -8 } } ] },
    b: { label: "问阿姨有没有隐藏口味。", out: [
      { text: "阿姨神秘地从冰柜最底下掏出一根“老口味”，说只卖给识货的人。", say: "我就是识货的人！", mood: { name: "拿到隐藏款", emo: "playful", pts: 3, min: 180 }, need: { hunger: 5 } },
      { text: "阿姨想了半天，说：有，凉的。", say: "……是挺隐藏的。", mood: { name: "隐藏口味是凉的", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 215, title: "树上的风筝", at: "front", when: "",
    text: "浅蓝房子家的小孩把风筝挂在了门口的树上，正仰着脸，眼看就要哭出来。",
    a: { label: "爬上去够。", out: [
      { text: "{名字}三两下就够到了风筝，小孩从此把{名字}当成了超级英雄。", say: "这种小事交给我！", mood: { name: "当了一回英雄", emo: "confident", pts: 4, min: 200 } },
      { text: "爬到一半卡住了，现在换成小孩在下面给{名字}加油。", say: "我……我在观察地形。", mood: { name: "卡在了树上", emo: "scared", pts: 3, min: 120 } } ] },
    b: { label: "找根长竹竿挑。", out: [
      { text: "竹竿一挑，风筝轻飘飘地落了下来，小孩激动地抱住了{名字}的腿。", say: "好啦好啦，不哭啦。", mood: { name: "救下了风筝", emo: "happy", pts: 3, min: 180 }, need: { social: 8 } },
      { text: "风筝下来了，竹竿顶上的旧鸟窝也下来了，正好扣在{名字}头上。", say: "我现在有帽子了。", mood: { name: "鸟窝扣头上", emo: "embarrassed", pts: 3, min: 120 }, need: { hygiene: -6 } } ] } },
  { n: 216, title: "晨跑的邀请", at: "front", when: "morning",
    text: "一位晨跑的大叔第三次从门口经过，每次都朝{名字}点点头，好像在说：来呀。",
    a: { label: "跟上去跑一圈。", out: [
      { text: "一圈下来浑身冒汗，大叔临走前还和{名字}击了个掌。", say: "早晨的风是甜的！", mood: { name: "早起跑了一圈", emo: "energized", pts: 4, min: 200 }, need: { energy: -8, fun: 6 } },
      { text: "跑了不到半条街就喘不上气，{名字}扶着路灯杆目送大叔远去。", say: "你……你先走……", mood: { name: "跑不过大叔", emo: "embarrassed", pts: 2, min: 120 }, need: { energy: -10 } } ] },
    b: { label: "坐在台阶上加油助威。", out: [
      { text: "大叔每经过一次，{名字}就鼓一次掌，最后大叔跑出了今年最好的成绩。", say: "我是幕后功臣。", mood: { name: "给大叔加油", emo: "playful", pts: 3, min: 150 } },
      { text: "大叔跑完第十圈还没停，{名字}拍手拍得手都麻了。", say: "大叔到底要跑几圈……", mood: { name: "加油加到手麻", emo: "bored", pts: 2, min: 120 } } ] } },
  { n: 217, title: "圈圈", at: "front", when: "night",
    text: "门口的路灯亮了，一只大飞蛾绕着灯一圈又一圈地转。",
    a: { label: "给它起个名字。", out: [
      { text: "{名字}叫它“圈圈”，圈圈似乎很满意，绕得更起劲了。", say: "圈圈，再来一圈！", mood: { name: "给飞蛾起名", emo: "playful", pts: 3, min: 150 } },
      { text: "名字刚起好，飞蛾就一头扎进了{名字}的头发里。", say: "圈圈！快出来！", mood: { name: "飞蛾钻进头发", emo: "scared", pts: 3, min: 120 } } ] },
    b: { label: "想想它为什么这么爱灯。", out: [
      { text: "{名字}想了很久，觉得飞蛾爱灯，大概和自己爱看月亮是一个道理。", say: "我们都在追光呢。", mood: { name: "和飞蛾共鸣", emo: "inspired", pts: 3, min: 180 } },
      { text: "想着想着，{名字}也盯着灯看入了神，眼前全是绿色的光斑。", say: "我也开始转圈了……", mood: { name: "盯灯盯晕了", emo: "dazed", pts: 3, min: 120 } } ] } },
  { n: 218, title: "官方数据", at: "front", when: "night+clear",
    text: "夜里很晴，{名字}坐在门口台阶上，一抬头就是满天星星。",
    a: { label: "认真数一数。", out: [
      { text: "数到第一百二十七颗时，{名字}宣布这就是今晚的最终记录。", say: "一百二十七，官方数据。", mood: { name: "数了好多星星", emo: "focused", pts: 3, min: 180 } },
      { text: "每次快数完就有新的一颗冒出来，{名字}怀疑星星在故意捣乱。", say: "别动！我在数呢！", mood: { name: "星星不配合", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "对着星星许个愿。", out: [
      { text: "一颗流星正好划过，{名字}激动得愣在原地，愿望都忘了说。", say: "等等！我还没许完！", mood: { name: "看见了流星", emo: "inspired", pts: 4, min: 240 } },
      { text: "许完愿才发现，那颗一闪一闪的星星是一架飞机。", say: "你应该不是流星吧……", mood: { name: "许愿给了飞机", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 219, title: "蜗牛远征", at: "front", when: "rain",
    text: "雨后的台阶上，一只蜗牛正以惊人的耐心往门口爬。",
    a: { label: "给它让路。", out: [
      { text: "{名字}在旁边等了半个小时，蜗牛终于翻过了台阶，{名字}在心里给它颁了奖。", say: "恭喜你，冠军！", mood: { name: "目送蜗牛通关", emo: "focused", pts: 3, min: 150 } },
      { text: "等了半个小时，蜗牛掉头往回爬了。", say: "你到底要去哪儿啊！", mood: { name: "蜗牛改主意了", emo: "angry", pts: 3, min: 120 } } ] },
    b: { label: "帮它挪到草丛里。", out: [
      { text: "蜗牛在草丛里伸出触角晃了晃，像是在说谢谢。", say: "不客气，慢慢走。" },
      { text: "刚碰到壳，蜗牛就缩了进去，{名字}捏着它，莫名有点紧张。", say: "我不是坏人，真的。", mood: { name: "吓到了蜗牛", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 220, title: "铲雪大队", at: "front", when: "snow",
    text: "一夜大雪，门口的台阶和人行道全被盖住了，邻居们都拿着铲子出来了。",
    a: { label: "加入铲雪大队。", out: [
      { text: "大家一边铲一边聊，铲完一起站在干净的人行道上，有种打了胜仗的感觉。", say: "这条路是我们打下的！", mood: { name: "和邻居铲雪", emo: "energized", pts: 4, min: 200 }, need: { social: 12, energy: -8 } },
      { text: "{名字}铲得最卖力，铲完才发现雪全堆在了自己家门口。", say: "我把自己家埋了……", mood: { name: "雪堆在自家门口", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "偷偷堆个雪堡垒。", out: [
      { text: "堡垒刚完工，小孩们就闻讯赶来，一场雪球大战一触即发。", say: "守住堡垒！开火！", mood: { name: "雪球大战", emo: "playful", pts: 4, min: 200 }, need: { fun: 15 } },
      { text: "堡垒还没堆好，砖房的大叔走过来，默默递给{名字}一把铲子。", say: "好……好的，这就铲。", mood: { name: "被递了铲子", emo: "uncomfortable", pts: 2, min: 120 } } ] } },
  { n: 221, title: "红烧肉外交", at: "front", when: "hungry",
    text: "砖房的厨房窗户开着，一阵红烧肉的香味飘到了门口。",
    a: { label: "站在窗下深呼吸。", out: [
      { text: "邻居探出头来，笑着递出一小碗：“尝尝？”", say: "那……就尝一点点！", mood: { name: "吃到邻居的菜", emo: "happy", pts: 3, min: 180 }, need: { hunger: 15, social: 6 } },
      { text: "越闻越饿，{名字}的肚子咕噜一声，响得厨房里的人都听见了。", say: "不是我，是肚子自己。", mood: { name: "肚子出卖了我", emo: "embarrassed", pts: 3, min: 150 }, need: { hunger: -5 } } ] },
    b: { label: "赶紧回家自己做。", out: [
      { text: "凭着对香味的记忆做了一锅，虽然不太像，{名字}还是吃得很满足。", say: "我做的也不错嘛。", mood: { name: "模仿出一锅肉", emo: "confident", pts: 3, min: 150 }, need: { hunger: 12 } },
      { text: "回家一看，冰箱里只有一根葱。", say: "葱啊，你能变成肉吗？", mood: { name: "冰箱只剩根葱", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 222, title: "什么都五块", at: "front", when: "",
    text: "浅蓝房子的邻居在门口摆了个旧物摊，牌子上写着：什么都五块。",
    a: { label: "认真淘一淘。", out: [
      { text: "{名字}翻出一个缺了只耳朵的陶瓷小兔子，一眼就喜欢上了。", say: "五块，你就是我的了。", mood: { name: "一见钟情小兔", emo: "flirty", pts: 3, min: 200 } },
      { text: "翻了半天，看上的东西全是邻居不卖的“非卖品”。", say: "那为什么要摆出来……", mood: { name: "非卖品太多", emo: "bored", pts: 2, min: 120 } } ] },
    b: { label: "把自己的旧东西也拿来摆。", out: [
      { text: "{名字}的旧杯子五分钟就卖了出去，邻居直呼“销售奇才”。", say: "天生会做生意。", mood: { name: "卖掉了旧杯子", emo: "confident", pts: 3, min: 150 } },
      { text: "一下午一件没卖出去，倒是又从邻居摊上买回来三样。", say: "生意……越做越亏。", mood: { name: "越卖东西越多", emo: "dazed", pts: 3, min: 120 } } ] } },
  { n: 223, title: "柠檬水小摊", at: "front", when: "",
    text: "两个小孩在街边支起小桌卖柠檬水，喊得特别认真，可一个顾客都没有。",
    a: { label: "光顾一杯。", out: [
      { text: "柠檬水酸甜刚好，两个小孩激动得像开张了一家大公司。", say: "好喝！我是回头客！", mood: { name: "做了头一位顾客", emo: "playful", pts: 3, min: 180 }, need: { hunger: 4, social: 6 } },
      { text: "柠檬水里好像忘了放糖，可两双眼睛正期待地盯着{名字}。", say: "嗯！很……很有个性！", mood: { name: "硬喝酸柠檬水", emo: "tense", pts: 3, min: 120 } } ] },
    b: { label: "帮他们吆喝。", out: [
      { text: "{名字}一嗓子喊出去，路人陆续围了上来，柠檬水很快卖光了。", say: "招牌嗓子，名不虚传！", mood: { name: "吆喝卖光了", emo: "energized", pts: 4, min: 180 }, need: { social: 10 } },
      { text: "喊得太大声，窗台上的橘猫吓得滚了下去。", say: "对不起，猫先生！", mood: { name: "把猫喊下来了", emo: "scared", pts: 3, min: 120 } } ] } },
  { n: 224, title: "红气球", at: "front", when: "",
    text: "一只红气球慢慢从街那头飘过来，绳子在空中晃来晃去。",
    a: { label: "跳起来抓住绳子。", out: [
      { text: "抓住了！没过多久，一个小孩哭着跑来，看见气球立刻破涕为笑。", say: "物归原主，不谢！", mood: { name: "抓住了气球", emo: "confident", pts: 3, min: 180 }, need: { social: 6 } },
      { text: "差了一点点，气球擦着指尖飘过了屋顶。", say: "再见了，红气球……", mood: { name: "没抓住气球", emo: "sad", pts: 2, min: 120 } } ] },
    b: { label: "看着它飞走。", out: [
      { text: "气球越飞越高，最后变成天上的一个小红点，{名字}一直看到脖子发酸。", say: "去更远的地方吧。", mood: { name: "送别一只气球", emo: "inspired", pts: 3, min: 150 } },
      { text: "气球卡在树枝上，啪地爆了，{名字}吓得原地一跳。", say: "吓死我了！", mood: { name: "气球爆炸", emo: "scared", pts: 3, min: 120 } } ] } },
  { n: 225, title: "猫的回礼", at: "front", when: "",
    text: "橘猫从窗台上跳下来，把一个小东西放在{名字}脚边，然后端坐着等待。",
    a: { label: "郑重地收下。", out: [
      { text: "是一片完美的银杏叶，{名字}把它夹进口袋，橘猫满意地走了。", say: "谢谢，我会珍藏的。", mood: { name: "收到猫的礼物", emo: "happy", pts: 3, min: 200 } },
      { text: "是一条半死不活的蚯蚓，橘猫的眼神仿佛在说：别客气。", say: "这……太贵重了……", mood: { name: "收到一条蚯蚓", emo: "uncomfortable", pts: 3, min: 120 } } ] },
    b: { label: "回赠一点东西。", out: [
      { text: "{名字}放下一小块饼干，橘猫闻了闻，叼起来就走，交易达成。", say: "合作愉快，猫老板。", mood: { name: "和猫做了生意", emo: "playful", pts: 3, min: 150 } },
      { text: "橘猫看了看回礼，又看了看{名字}，把自己的礼物叼了回去。", say: "嫌我寒酸是吧！", mood: { name: "被猫嫌弃回礼", emo: "angry", pts: 2, min: 120 } } ] } },
  { n: 226, title: "塞满的信箱", at: "front", when: "",
    text: "门口的信箱塞得满满的，盖子都合不上了。",
    a: { label: "一张一张认真看。", out: [
      { text: "大多是广告，但最底下有一张手写明信片，是很久没联系的老朋友寄来的。", say: "原来有人还记着我。", mood: { name: "收到老朋友来信", emo: "happy", pts: 4, min: 240 }, need: { social: 8 } },
      { text: "认真看完了四十张广告，{名字}现在对附近每家装修公司都了如指掌。", say: "我可以去当顾问了。", mood: { name: "读了一堆广告", emo: "bored", pts: 3, min: 150 } } ] },
    b: { label: "全部塞进回收箱。", out: [
      { text: "信箱清爽了，{名字}有种开启新生活的感觉。", say: "断舍离，从信箱开始！", mood: { name: "清空了信箱", emo: "energized", pts: 3, min: 150 } },
      { text: "塞完才想起来，里面好像有一封要交费的通知。", say: "我……去回收箱里捞一下。", mood: { name: "扔错了信", emo: "tense", pts: 3, min: 150 } } ] } },
  { n: 227, title: "风铃作曲家", at: "front", when: "",
    text: "砖房门廊下的风铃今天特别热闹，叮叮当当响个不停。",
    a: { label: "跟着节奏哼歌。", out: [
      { text: "哼着哼着，{名字}即兴编出了一首关于风的小曲。", say: "今天的风是作曲家。", mood: { name: "和风铃合奏", emo: "inspired", pts: 4, min: 180 }, need: { fun: 6 } },
      { text: "风突然停了，{名字}的歌声孤零零地响在整条街上，路人都看了过来。", say: "呃……刚才有伴奏的。", mood: { name: "独唱被听见了", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "闭上眼听一会儿。", out: [
      { text: "风铃声一阵一阵，{名字}听着听着，心里慢慢安静了下来。", say: "好安静，好舒服。", mood: { name: "听风铃静下来", emo: "focused", pts: 3, min: 150 } },
      { text: "听得太入迷，再睁眼时天都暗了。", say: "我刚才去哪儿了？", mood: { name: "听风铃出了神", emo: "dazed", pts: 3, min: 120 } } ] } },
  { n: 228, title: "松手的时机", at: "front", when: "",
    text: "邻居家的小孩在学骑自行车，摇摇晃晃的，旁边没有大人扶。",
    a: { label: "过去扶着后座。", out: [
      { text: "{名字}扶着跑了几步，悄悄松了手，小孩自己骑出了好远。", say: "你看！你已经会了！", mood: { name: "教会小孩骑车", emo: "confident", pts: 4, min: 200 }, need: { energy: -6 } },
      { text: "小孩一紧张往左拐，{名字}一紧张往右拐，两人一起摔进了草丛。", say: "没事没事，草很软。", mood: { name: "教车惊魂", emo: "tense", pts: 3, min: 120 }, need: { hygiene: -6 } } ] },
    b: { label: "在旁边喊口诀。", out: [
      { text: "“眼睛看前面！脚别停！”小孩照着做，居然真的骑稳了。", say: "我是金牌教练！", mood: { name: "口诀起作用了", emo: "inspired", pts: 3, min: 150 } },
      { text: "口诀喊得又多又乱，小孩停下车，困惑地问：到底先做哪个？", say: "呃……先深呼吸？", mood: { name: "口诀喊乱了", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 229, title: "篱笆两边", at: "front", when: "",
    text: "浅蓝房子和砖房的邻居隔着篱笆争论：落在中间的树叶到底该谁扫？",
    a: { label: "主动当和事佬。", out: [
      { text: "{名字}提议一家扫一周，两位邻居想了想，握手言和。", say: "和平使者，就是我。", mood: { name: "调解成功", emo: "confident", pts: 3, min: 180 }, need: { social: 6 } },
      { text: "两位邻居听完建议，一致决定：那就让{名字}来扫。", say: "等一下，这不对吧？", mood: { name: "被安排扫叶子", emo: "angry", pts: 3, min: 150 } } ] },
    b: { label: "假装路过。", out: [
      { text: "{名字}贴着墙根悄悄溜了过去，谁都没注意到。", say: "我是空气，我是空气。", mood: { name: "溜过了战场", emo: "tense", pts: 2, min: 90 } },
      { text: "刚走两步，两位邻居同时转过头：“你来评评理！”", say: "我……我只是路过。", mood: { name: "被卷进争论", emo: "scared", pts: 3, min: 120 } } ] } },
  { n: 230, title: "好久不见", at: "front", when: "",
    text: "一位路人热情地冲{名字}挥手：“哎呀！好久不见！最近怎么样？”",
    a: { label: "热情回应。", out: [
      { text: "两人聊了五分钟，路人才发现认错了人，可已经聊得很开心了。", say: "那我们现在算认识了！", mood: { name: "和陌生人聊开", emo: "playful", pts: 3, min: 150 }, need: { social: 10 } },
      { text: "路人越聊越困惑，最后小心翼翼地问：你……是哪位来着？", say: "我也想问这个……", mood: { name: "尬聊五分钟", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "老实说对方认错了。", out: [
      { text: "路人哈哈大笑，说{名字}长得特别像自己的老同学，还送了{名字}一颗糖。", say: "那我就当一天老同学。" },
      { text: "路人一脸不信：“骗人，就是你！”然后挥着手走远了。", say: "我真的不是啊！", mood: { name: "被坚持认错", emo: "dazed", pts: 3, min: 120 } } ] } },
  { n: 231, title: "半首曲子", at: "front", when: "",
    text: "一位路人吹着口哨经过，曲子很好听，可只吹了一半，人就拐进了巷子。",
    a: { label: "追上去问后半段。", out: [
      { text: "路人很高兴有人欣赏，站在路边把整首曲子吹完了。", say: "原来结尾是这样的！", mood: { name: "听完了整首曲子", emo: "inspired", pts: 3, min: 180 } },
      { text: "追进巷子，人已经不见了，只剩那半首曲子在{名字}脑子里循环。", say: "后半段到底是什么！", mood: { name: "曲子卡在半截", emo: "tense", pts: 3, min: 150 } } ] },
    b: { label: "自己编后半段。", out: [
      { text: "{名字}编出来的结尾意外地好听，哼了一整天。", say: "我是不是有点才华？", mood: { name: "续写了曲子", emo: "confident", pts: 3, min: 150 } },
      { text: "编来编去，最后变成了一首完全不相干的儿歌。", say: "这……跑到哪儿去了？", mood: { name: "曲子跑偏了", emo: "playful", pts: 2, min: 120 } } ] } },
  { n: 232, title: "麻雀团伙", at: "front", when: "",
    text: "{名字}坐在台阶上吃饼干，一只麻雀大摇大摆地跳过来，盯着饼干看。",
    a: { label: "掰一小块给它。", out: [
      { text: "麻雀叼走了饼干，五分钟后带着全家回来了。", say: "你们家……挺大的。", mood: { name: "麻雀全家来了", emo: "dazed", pts: 3, min: 150 } },
      { text: "麻雀一口叼走的不是那一小块，而是{名字}手里的一大块。", say: "喂！那是我的！", mood: { name: "饼干被抢了", emo: "angry", pts: 3, min: 120 }, need: { hunger: -4 } } ] },
    b: { label: "护住饼干和它对视。", out: [
      { text: "对视了一分钟，麻雀先眨了眼，悻悻地飞走了。", say: "我赢了，饼干归我。", mood: { name: "瞪赢了麻雀", emo: "confident", pts: 3, min: 150 } },
      { text: "正对视着，另一只麻雀从背后叼走了饼干。", say: "你们是团伙作案！", mood: { name: "中了麻雀的计", emo: "embarrassed", pts: 3, min: 120 } } ] } },
  { n: 233, title: "搬运队长", at: "front", when: "",
    text: "人行道的砖缝间，一队蚂蚁正排着长队搬运一块面包屑。",
    a: { label: "趴下来认真观察。", out: [
      { text: "{名字}看了半个小时，记住了领头那只蚂蚁，决定叫它“队长”。", say: "队长，辛苦了！", mood: { name: "观察蚂蚁搬家", emo: "focused", pts: 4, min: 180 } },
      { text: "看得太入神，一只蚂蚁顺着手爬了上来，{名字}跳起来甩了半天。", say: "我不是面包屑！", mood: { name: "蚂蚁爬上了手", emo: "scared", pts: 2, min: 120 } } ] },
    b: { label: "再送它们一块大的。", out: [
      { text: "蚂蚁们围着大面包屑开了个会，最后决定分成十块慢慢搬。", say: "真会过日子。", mood: { name: "给蚂蚁加餐", emo: "playful", pts: 3, min: 150 } },
      { text: "大面包屑引来了麻雀，蚂蚁们辛苦了一下午，全白忙了。", say: "对不起，好心办坏事了。", mood: { name: "好心办了坏事", emo: "sad", pts: 3, min: 150 } } ] } },
  { n: 234, title: "滑落的被子", at: "front", when: "clear",
    text: "浅蓝房子二楼晒的被子被风吹开了一角，眼看整床就要滑下来。",
    a: { label: "冲到底下准备接。", out: [
      { text: "被子正好落在{名字}身上，又软又香，邻居连连道谢。", say: "是太阳的味道！", mood: { name: "接住了被子", emo: "confident", pts: 3, min: 150 } },
      { text: "被子没掉，晾衣夹掉了，正中{名字}的脑袋。", say: "被子没事，我有事。", mood: { name: "被晾衣夹砸中", emo: "dazed", pts: 2, min: 120 } } ] },
    b: { label: "大声喊邻居。", out: [
      { text: "邻居及时探出头，把被子拽了回去，还夸{名字}一句“真靠谱”。", say: "靠谱是我的特长！", need: { social: 5 } },
      { text: "邻居没听见，被子扑通掉进了花坛里。", say: "我喊了，真的喊了！", mood: { name: "没救下被子", emo: "tense", pts: 3, min: 120 } } ] } },
  { n: 235, title: "你是什么", at: "front", when: "",
    text: "一个小孩蹲在{名字}面前，认真地问：你是什么？",
    a: { label: "认真回答。", out: [
      { text: "{名字}讲了很久，小孩听完点点头：那你就是我的朋友。", say: "嗯，这个答案最准确。", mood: { name: "被认作朋友", emo: "inspired", pts: 3, min: 200 }, need: { social: 10 } },
      { text: "讲着讲着，{名字}自己也开始怀疑：我到底是什么？", say: "我……是什么来着？", mood: { name: "陷入哲学思考", emo: "dazed", pts: 4, min: 180 } } ] },
    b: { label: "反问对方是什么。", out: [
      { text: "小孩想了想，说自己是一只恐龙，然后吼了一声跑走了。", say: "好吓人的恐龙呀。", mood: { name: "遇见了小恐龙", emo: "playful", pts: 3, min: 150 } },
      { text: "小孩被问住了，愣了一会儿，哇地一声哭着去找大人。", say: "我不是故意的！", mood: { name: "把小孩问哭了", emo: "tense", pts: 3, min: 120 } } ] } },
  { n: 236, title: "花瓣雨", at: "front", when: "spring",
    text: "门口的树开花了，风一吹，花瓣纷纷扬扬地往下落。",
    a: { label: "张开手接花瓣。", out: [
      { text: "接住了一片完整的花瓣，{名字}觉得今天一定是好运的一天。", say: "好运，被我接住了！", mood: { name: "接住了好运", emo: "energized", pts: 3, min: 200 } },
      { text: "花瓣没接到几片，倒是吸进去一片，连打了十几个喷嚏。", say: "阿嚏！春天……阿嚏！", mood: { name: "被花瓣呛到", emo: "uncomfortable", pts: 3, min: 120 } } ] },
    b: { label: "在花瓣雨里转圈。", out: [
      { text: "{名字}转啊转，路过的人都笑着放慢了脚步。", say: "春天就该这样！", mood: { name: "春风里转圈圈", emo: "flirty", pts: 3, min: 180 }, need: { fun: 8 } },
      { text: "转得太猛，晕乎乎地坐在了地上，花瓣落了满身。", say: "世界在转……好美。", mood: { name: "转晕了", emo: "dazed", pts: 3, min: 120 } } ] } },
  { n: 237, title: "蝉的演唱会", at: "front", when: "summer+night",
    text: "夏天的晚上，门口树上的蝉叫得震天响，好像在开演唱会。",
    a: { label: "搬个小凳来听。", out: [
      { text: "听着听着，{名字}居然分出了高音部和低音部。", say: "这是个合唱团！", mood: { name: "听出蝉的和声", emo: "focused", pts: 3, min: 150 } },
      { text: "蝉越叫越响，{名字}觉得耳朵都在嗡嗡发烫。", say: "能不能……小点声？", mood: { name: "被蝉吵得头疼", emo: "uncomfortable", pts: 3, min: 120 } } ] },
    b: { label: "学蝉叫和它们对歌。", out: [
      { text: "{名字}一开口，整棵树突然安静了，好像都在认真听。", say: "它们被我镇住了。", mood: { name: "镇住了满树蝉", emo: "confident", pts: 3, min: 150 }, need: { fun: 6 } },
      { text: "邻居的窗户啪地打开了：“谁在学蝉叫！”", say: "……是蝉在学我。", mood: { name: "学蝉被抓包", emo: "scared", pts: 2, min: 120 } } ] } },
  { n: 238, title: "台阶的名字", at: "front", when: "bored",
    text: "{名字}坐在门口台阶上，实在没事干，开始认真思考台阶为什么是这个高度。",
    a: { label: "数一数经过的路人。", out: [
      { text: "一个小时经过了二十三个人，其中十一个朝{名字}笑了笑。", say: "今天的友好率很高！", mood: { name: "统计了路人", emo: "focused", pts: 3, min: 150 }, need: { social: 4 } },
      { text: "数到第七个就没人了，{名字}对着空荡荡的街等了好久。", say: "第八个，你在哪儿……", mood: { name: "等不到第八人", emo: "bored", pts: 3, min: 150 } } ] },
    b: { label: "给每级台阶起名字。", out: [
      { text: "第一级叫“出发”，第二级叫“犹豫”，第三级叫“到家了”。{名字}很满意。", say: "我是台阶命名大师。", mood: { name: "给台阶起了名", emo: "inspired", pts: 3, min: 150 } },
      { text: "起完名字以后，{名字}每次上台阶都得念一遍，越来越累。", say: "出发、犹豫……好麻烦！", mood: { name: "被规矩困住了", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 239, title: "对面的新邻居", at: "front", when: "",
    text: "街对面停了一辆搬家的车，新邻居正吭哧吭哧地往屋里搬箱子。",
    a: { label: "过去搭把手。", out: [
      { text: "搬完以后，新邻居请{名字}进屋喝了杯茶，两人一见如故。", say: "欢迎成为邻居！", mood: { name: "新邻居很投缘", emo: "flirty", pts: 3, min: 200 }, need: { social: 12 } },
      { text: "{名字}抱起一个箱子，里面传出瓷器碰撞的声音，之后每一步都走得心惊胆战。", say: "不能摔，不能摔……", mood: { name: "抱着易碎品", emo: "tense", pts: 4, min: 120 }, need: { energy: -6 } } ] },
    b: { label: "在门口挥手打招呼。", out: [
      { text: "新邻居回了一个大大的笑容，说改天送点家乡的点心过来。", say: "我等着你的点心！", mood: { name: "有点心可期待", emo: "playful", pts: 2, min: 150 } },
      { text: "新邻居抱着箱子没法挥手，只好朝{名字}拼命点头，差点把箱子点掉。", say: "别点了别点了！", mood: { name: "差点害人摔箱", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 240, title: "屋檐下", at: "front", when: "rain",
    text: "下雨了，一位路人缩在{名字}家门檐下躲雨，看起来很赶时间。",
    a: { label: "把伞借给对方。", out: [
      { text: "第二天，伞挂在了门把手上，伞柄上还系着一张写着“谢谢”的小纸条。", say: "世界上还是好人多。", mood: { name: "伞回来了", emo: "happy", pts: 3, min: 240 } },
      { text: "伞借出去了，雨却越下越大，{名字}这才想起自己也要出门。", say: "没伞的……是我了。", mood: { name: "把伞借出去了", emo: "sad", pts: 2, min: 120 } } ] },
    b: { label: "陪对方一起等雨停。", out: [
      { text: "两人站在屋檐下聊了好一会儿，雨停的时候，竟然有点舍不得。", say: "雨，下慢一点也行。", mood: { name: "屋檐下的聊天", emo: "flirty", pts: 4, min: 180 }, need: { social: 10 } },
      { text: "等了一个小时雨也没停，能聊的话题都聊完了，只剩沉默。", say: "嗯……雨真大啊。", mood: { name: "尬站了一小时", emo: "uncomfortable", pts: 3, min: 120 } } ] } },
  { n: 241, title: "彩虹快报", at: "front", when: "rain+day",
    text: "雨快停了，街对面的天上挂出了一道彩虹。",
    a: { label: "跑去叫邻居出来看。", out: [
      { text: "两边的邻居都跑了出来，大家站在门口仰着头，像在看一场免费演出。", say: "快看！快看那边！", mood: { name: "和邻居看彩虹", emo: "energized", pts: 3, min: 180 }, need: { social: 8 } },
      { text: "等大家出来时，彩虹已经淡得只剩一道影子了。", say: "刚才真的有，相信我！", mood: { name: "彩虹没等大家", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "一直盯着它直到消失。", out: [
      { text: "彩虹一点一点变淡，{名字}却把它记得清清楚楚。", say: "我把你记住了。", mood: { name: "看完一道彩虹", emo: "inspired", pts: 3, min: 200 } },
      { text: "看着看着，又下起了大雨，{名字}被淋了个正着。", say: "原来是骗我出来的！", mood: { name: "被彩虹骗出门", emo: "angry", pts: 3, min: 120 }, need: { hygiene: -6 } } ] } },
  { n: 242, title: "电钻鼓手", at: "front", when: "",
    text: "隔壁砖房在装修，电钻声一阵接一阵，吵得门口的麻雀都搬走了。",
    a: { label: "去找邻居商量。", out: [
      { text: "邻居很不好意思，答应中午停一停，还送了{名字}一副耳塞。", say: "沟通，就是力量。", mood: { name: "噪音谈判成功", emo: "confident", pts: 3, min: 150 } },
      { text: "敲了半天门，电钻声太响，根本没人听见。", say: "你们……听得见吗！", mood: { name: "敲门敲不应", emo: "angry", pts: 3, min: 120 } } ] },
    b: { label: "把电钻声当成鼓点。", out: [
      { text: "{名字}跟着电钻的节奏跳了一段舞，居然还挺带劲。", say: "动次打次，电钻次！", mood: { name: "跟着电钻跳舞", emo: "playful", pts: 4, min: 150 }, need: { fun: 8 } },
      { text: "刚跟上节奏，电钻换成了锤子，节奏全乱了。", say: "换也换得有点规律！", mood: { name: "节奏被打乱", emo: "uncomfortable", pts: 2, min: 120 } } ] } },
  { n: 243, title: "不许踩缝", at: "front", when: "",
    text: "{名字}突然想起一条规矩：走人行道的时候，绝对不能踩到砖缝。",
    a: { label: "认真执行到底。", out: [
      { text: "{名字}一路蹦蹦跳跳走到街角，一条缝都没踩到。", say: "完美通关，零失误！", mood: { name: "一条缝没踩", emo: "focused", pts: 4, min: 150 }, need: { energy: -4 } },
      { text: "迎面来了一位路人，两人在同一块砖上僵持了好久，谁也不肯踩缝。", say: "你……也在玩这个？", mood: { name: "和路人僵持", emo: "tense", pts: 3, min: 120 } } ] },
    b: { label: "偷偷踩一下试试。", out: [
      { text: "什么都没发生。{名字}松了口气，又隐隐有点失望。", say: "原来没有惩罚啊。", mood: { name: "踩缝无事发生", emo: "bored", pts: 2, min: 120 } },
      { text: "刚踩上去，窗台上的橘猫恰好发出一声长长的“喵——”。", say: "这……是警告吗？", mood: { name: "踩缝惊动了猫", emo: "scared", pts: 3, min: 150 } } ] } },
  { n: 244, title: "意外入镜", at: "front", when: "",
    text: "一位路人正在门口的树下拍照，镜头正好对着{名字}这边。",
    a: { label: "悄悄摆个姿势。", out: [
      { text: "路人翻看照片，惊喜地说：这张最好看，多亏你入镜！", say: "我天生上镜。", mood: { name: "被夸上镜", emo: "flirty", pts: 3, min: 180 } },
      { text: "路人放下相机，礼貌地问：可以让一让吗？", say: "好……我这就让。", mood: { name: "抢镜失败", emo: "uncomfortable", pts: 2, min: 120 } } ] },
    b: { label: "赶紧躲开。", out: [
      { text: "躲得太急，一头扎进了树丛，路人反倒拍下了这一幕。", say: "这张请务必删掉！", mood: { name: "躲进了树丛", emo: "embarrassed", pts: 3, min: 120 } },
      { text: "路人拍完特地跑过来道谢，说{名字}真体贴。", say: "应该的，应该的。" } ] } },
  { n: 245, title: "长长的影子", at: "front", when: "evening+clear",
    text: "傍晚的太阳斜斜地照过来，{名字}的影子被拉得老长，一直伸到了马路对面。",
    a: { label: "和影子玩一会儿。", out: [
      { text: "{名字}用手比出小狗、小鸟和兔子，影子在人行道上演了一整台戏。", say: "今晚的演出很成功！", mood: { name: "和影子演戏", emo: "playful", pts: 4, min: 150 }, need: { fun: 8 } },
      { text: "一位邻居路过，好奇地看着{名字}对着地面比划了半天。", say: "我在……排练。", mood: { name: "对着地面比划", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "去踩影子的脑袋。", out: [
      { text: "怎么也踩不到，{名字}追着影子转了好几圈，笑得停不下来。", say: "你别跑！站住！", mood: { name: "追自己的影子", emo: "energized", pts: 3, min: 150 }, need: { fun: 8 } },
      { text: "追着追着太阳落山了，影子不见了，{名字}突然有点失落。", say: "它下班了。", mood: { name: "影子下班了", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 246, title: "小伞", at: "front", when: "",
    text: "门口那盆半死不活的绿植里，一夜之间冒出了一朵小蘑菇。",
    a: { label: "精心照顾它。", out: [
      { text: "蘑菇一天比一天精神，{名字}给它起名“小伞”，每天早上都要打个招呼。", say: "小伞，早上好！", mood: { name: "养了一朵蘑菇", emo: "inspired", pts: 3, min: 180 } },
      { text: "第二天，蘑菇变成了一小滩软软的东西。", say: "小伞……你怎么了……", mood: { name: "蘑菇化掉了", emo: "sad", pts: 3, min: 150 } } ] },
    b: { label: "研究它能不能吃。", out: [
      { text: "{名字}研究了半天，最后决定：好看的东西不一定要吃掉。", say: "你就安心当风景吧。", mood: { name: "研究了蘑菇", emo: "focused", pts: 3, min: 150 } },
      { text: "砖房奶奶路过，瞥了一眼说：这个啊，吃了会看见小人跳舞。", say: "那……还是算了。", mood: { name: "差点吃怪蘑菇", emo: "scared", pts: 3, min: 150 } } ] } },
  { n: 247, title: "踢过来！", at: "front", when: "",
    text: "一只皮球骨碌碌滚到{名字}脚边，街那头几个小孩在喊：踢过来！",
    a: { label: "帅气地一脚踢回去。", out: [
      { text: "皮球划出一道漂亮的弧线，正好落在小孩们中间，大家齐声叫好。", say: "球王在此！", mood: { name: "踢出完美一球", emo: "confident", pts: 4, min: 180 } },
      { text: "一脚踢空，自己差点坐到地上，皮球纹丝不动。", say: "刚才那是……热身。", mood: { name: "一脚踢空", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "抱着球走过去。", out: [
      { text: "小孩们拉着{名字}一起踢，{名字}跑得满头大汗。", say: "再来一局！我还行！", mood: { name: "和小孩踢球", emo: "energized", pts: 4, min: 200 }, need: { fun: 12, energy: -10, social: 8 } },
      { text: "走到一半，小孩们已经换了一个新球，没人记得这一个了。", say: "那……这个归我了？", mood: { name: "被遗忘的球", emo: "bored", pts: 2, min: 120 } } ] } },
  { n: 248, title: "窗台对峙", at: "front", when: "",
    text: "橘猫趴在窗台上，尾巴一甩一甩，正死死盯着树枝上的一只麻雀。",
    a: { label: "偷偷给麻雀使眼色。", out: [
      { text: "麻雀好像真的看懂了，扑棱一下飞走了，橘猫回头狠狠瞪了{名字}一眼。", say: "我什么都没做哦。", mood: { name: "暗中救了麻雀", emo: "playful", pts: 3, min: 150 } },
      { text: "麻雀没看懂，橘猫却看懂了，从此每次见到{名字}都哼一声。", say: "猫大人，我错了！", mood: { name: "得罪了橘猫", emo: "tense", pts: 3, min: 150 } } ] },
    b: { label: "当解说员小声解说。", out: [
      { text: "“橘猫选手蓄力……麻雀选手梳毛……”{名字}越解说越入戏。", say: "今年最精彩的比赛！", mood: { name: "解说猫雀大战", emo: "focused", pts: 3, min: 150 }, need: { fun: 6 } },
      { text: "解说了半个小时，橘猫睡着了，麻雀也睡着了。", say: "比赛……暂停？", mood: { name: "比赛双方睡着", emo: "bored", pts: 3, min: 120 } } ] } },
  { n: 249, title: "缺一个对手", at: "front", when: "",
    text: "一位老爷爷在门口的树下摆好了棋盘，环顾四周，正缺一个对手。",
    a: { label: "坐下来陪他下。", out: [
      { text: "一局下完，{名字}输得心服口服，爷爷说明天还在这儿等。", say: "明天我一定赢你！", mood: { name: "约好明天下棋", emo: "energized", pts: 3, min: 240 }, need: { social: 12 } },
      { text: "{名字}一不小心赢了，爷爷不服气，拉着{名字}一直下到了天黑。", say: "爷爷，该吃晚饭了……", mood: { name: "被拉着连下十局", emo: "bored", pts: 3, min: 150 }, need: { energy: -8, social: 6 } } ] },
    b: { label: "去请一位邻居来。", out: [
      { text: "浅蓝房子的大叔被拉了过来，两人杀得难分难解，{名字}在旁边看得津津有味。", say: "这一步走得好！", mood: { name: "观战老将对决", emo: "focused", pts: 3, min: 150 } },
      { text: "两人下着下着吵了起来，都说对方悔棋，{名字}只好硬着头皮去劝。", say: "和气生财，和气生财！", mood: { name: "棋局劝架", emo: "tense", pts: 3, min: 120 } } ] } },
  { n: 250, title: "挥手实验", at: "front", when: "lonely",
    text: "{名字}有点寂寞，决定站在门口，朝每个经过的人挥手。",
    a: { label: "热情地挥。", out: [
      { text: "大部分人都笑着挥了回来，一个小孩还隔着马路喊了声“你好！”", say: "大家都好友好啊！", mood: { name: "被路人回应", emo: "happy", pts: 3, min: 180 }, need: { social: 15 } },
      { text: "前面三个人都低头看手机，谁也没看见。", say: "第四个一定看得见。", mood: { name: "挥手没人理", emo: "sad", pts: 3, min: 150 }, need: { social: -4 } } ] },
    b: { label: "只朝看起来友好的人挥。", out: [
      { text: "一位推婴儿车的路人停下来，和{名字}聊了好一会儿天气和孩子。", say: "今天聊得真开心。", mood: { name: "和路人聊了天", emo: "energized", pts: 3, min: 180 }, need: { social: 12 } },
      { text: "犹豫得太久，合适的人已经走过去了，{名字}的手还停在半空。", say: "我……在测风向。", mood: { name: "挥手慢了半拍", emo: "embarrassed", pts: 3, min: 120 } } ] } },
  { n: 251, title: "鸭子占座", at: "park", when: "",
    text: "一只鸭子从池塘里上岸，摇摇摆摆地跳上长椅，在{名字}旁边坐了下来。",
    a: { label: "跟它并排坐着。", out: [
      { text: "{名字}和鸭子一起看了很久的池塘。路过的人纷纷拍照，两个都显得很有明星气质。", say: "我们是公园双子星。", mood: { name: "和鸭子同框", emo: "flirty", pts: 3, min: 180 } },
      { text: "鸭子越坐越往{名字}这边挤，最后{名字}只剩下长椅的一个角。", say: "这椅子到底谁的？", mood: { name: "被鸭子挤走", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "礼貌地请它让一让。", out: [
      { text: "鸭子看了{名字}一眼，往旁边挪了一点。{名字}认为这是一次成功的外交。", say: "外交成功，各占一半。", mood: { name: "和鸭子谈判", emo: "confident", pts: 3, min: 150 } },
      { text: "鸭子嘎了一声，一口啄在{名字}的袖子上。{名字}立刻改口：“您坐，您坐。”", say: "您坐，您坐！", mood: { name: "被鸭子震慑", emo: "scared", pts: 2, min: 120 } } ] } },
  { n: 252, title: "鸭子房的租客", at: "park", when: "",
    text: "池塘中间的小鸭子房里，好像有什么东西在动，但一直没有出来。",
    a: { label: "耐心蹲守。", out: [
      { text: "{名字}盯了半个小时，门口终于探出一只小鸭的脑袋，又立刻缩了回去。", say: "看见了！虽然只有一秒。", mood: { name: "见到神秘租客", emo: "focused", pts: 3, min: 180 } },
      { text: "等到腿都麻了，出来的却是一只青蛙。它显然只是来串门的。", say: "你、你也不住这儿吧？", mood: { name: "等来一只青蛙", emo: "dazed", pts: 3, min: 150 } } ] },
    b: { label: "不打扰人家的隐私。", out: [
      { text: "{名字}把视线移开。可是不看鸭子房，公园里一下子就没什么好看的了。", say: "好吧……那我看看草。", mood: { name: "没东西可看", emo: "bored", pts: 2, min: 120 } },
      { text: "可越不看越好奇，{名字}开始脑补房子里有小沙发、小台灯和一台电视。", say: "它们晚上看什么节目呢？", mood: { name: "脑补鸭子家", emo: "inspired", pts: 3, min: 150 } } ] } },
  { n: 253, title: "树上的风筝", at: "park", when: "",
    text: "一个小孩的风筝挂在了长椅旁边的树上，他仰着头，眼看就要哭出来。",
    a: { label: "跳起来去够。", out: [
      { text: "{名字}跳了七八次，终于用指尖勾住了线尾。风筝回到地面，小孩欢呼着跑远了。", say: "跳高冠军就是我！", mood: { name: "救下了风筝", emo: "energized", pts: 4, min: 180 }, need: { energy: -8 } },
      { text: "风筝没够着，{名字}却把一树叶子摇了下来，落了自己满头。", say: "风筝没下来，我先绿了。", mood: { name: "顶了一头树叶", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "教他拉线的技巧。", out: [
      { text: "{名字}指挥小孩往左轻轻一扯，风筝居然自己滑了下来。小孩看{她}的眼神像在看大师。", say: "要顺着风，懂吗？", mood: { name: "被当成大师", emo: "confident", pts: 4, min: 180 }, need: { social: 8 } },
      { text: "小孩一用力，线断了。风筝从此成了那棵树的装饰，两人对着树沉默良久。", say: "它……喜欢那里吧。", mood: { name: "风筝住树上了", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 254, title: "不请自来的足球", at: "park", when: "",
    text: "一个足球骨碌碌滚到长椅底下，远处几个小孩在喊：“帮忙踢一下！”",
    a: { label: "潇洒地踢回去。", out: [
      { text: "球画出一道漂亮的弧线，正好落在小孩脚下。他们愣了一下，齐声喊“好球”。", say: "低调，低调。", mood: { name: "踢出好球", emo: "confident", pts: 4, min: 180 }, need: { fun: 8 } },
      { text: "{名字}一脚踢空，球纹丝不动，鞋子却飞了出去。", say: "那是……热身动作。", mood: { name: "鞋子飞出去了", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "抱着球走过去。", out: [
      { text: "小孩们顺便请{名字}当守门员。{她}扑了三个球，全都扑在了草地上。", say: "球门太宽了吧！", mood: { name: "当了守门员", emo: "playful", pts: 4, min: 180 }, need: { fun: 12, energy: -6 } },
      { text: "小孩接过球，一句谢谢都没说就跑了。{名字}伸着的手在空中停了好一会儿。", say: "嗯……不客气？", mood: { name: "被小孩无视", emo: "uncomfortable", pts: 2, min: 90 } } ] } },
  { n: 255, title: "油漆未干", at: "park", when: "",
    text: "{名字}坐下来以后，才看见长椅背后贴着一张纸：油漆未干。",
    a: { label: "慢慢站起来检查。", out: [
      { text: "衣服上只有几道浅浅的印子。{名字}决定把它当成一件限量款。", say: "限量款，全球就一件。", mood: { name: "穿上限量款", emo: "playful", pts: 3, min: 150 } },
      { text: "站起来的时候，长椅发出了“啵”的一声。周围几个人都转过头来看。", say: "大家……别看了。", mood: { name: "被椅子粘住", emo: "embarrassed", pts: 4, min: 150 }, need: { hygiene: -10 } } ] },
    b: { label: "反正晚了，坐着不动。", out: [
      { text: "{名字}一直坐到油漆干透。离开时，{她}觉得自己和这张长椅的关系更深了一层。", say: "我们是粘过的交情。", mood: { name: "和长椅结缘", emo: "dazed", pts: 3, min: 150 } },
      { text: "仔细一看，那张纸是上个月贴的。椅子早就干了，只是没人撕。", say: "白紧张了这么久！", mood: { name: "被旧告示吓到", emo: "tense", pts: 2, min: 90 } } ] } },
  { n: 256, title: "路灯的脾气", at: "park", when: "evening|night",
    text: "{名字}身边的路灯亮了一下，又灭了，又亮了，好像拿不定主意。",
    a: { label: "给它加油打气。", out: [
      { text: "{名字}小声说了句“你可以的”，路灯稳稳地亮了起来。{她}坚信这是自己的功劳。", say: "看吧，它就缺句鼓励。", mood: { name: "鼓励了路灯", emo: "inspired", pts: 3, min: 180 } },
      { text: "路灯听完，彻底灭了。{名字}一个人坐在黑暗里，总觉得池塘里有什么在看着自己。", say: "路、路灯你快回来……", mood: { name: "黑暗里发毛", emo: "scared", pts: 3, min: 120 } } ] },
    b: { label: "拍一拍灯柱。", out: [
      { text: "拍了两下，灯亮得特别稳，还顺便让远处那盏也亮了。", say: "修理工，就是我。", mood: { name: "修好了路灯", emo: "confident", pts: 3, min: 150 } },
      { text: "灯没反应，{名字}的手却被冰凉的灯柱冻得一激灵。", say: "嘶——好凉！", mood: { name: "手被冰到", emo: "uncomfortable", pts: 2, min: 90 } } ] } },
  { n: 257, title: "萤火虫开会", at: "park", when: "summer+night",
    text: "草坪上亮起了一片萤火虫，一闪一闪，好像在开一场很重要的会。",
    a: { label: "悄悄靠近旁听。", out: [
      { text: "一只萤火虫落在{名字}的手背上，亮了三下。{名字}觉得自己被接纳为列席代表。", say: "我会保守会议机密。", mood: { name: "列席萤火虫会", emo: "happy", pts: 4, min: 240 } },
      { text: "{名字}踩断一根树枝，“咔嚓”一声，会议立刻散了，全场灯都灭了。", say: "对不起，你们继续……", mood: { name: "搅了萤火会", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "坐在长椅上远远地看。", out: [
      { text: "看着看着，{名字}觉得那些光点像天上的星星掉下来散步。", say: "星星也会下来遛弯吧。", mood: { name: "星星在散步", emo: "inspired", pts: 4, min: 240 } },
      { text: "{名字}看得太入迷，连蚊子在自己腿上开了好几场会都没发现。", say: "怎么全身都是包！", mood: { name: "被蚊子围攻", emo: "angry", pts: 2, min: 120 } } ] } },
  { n: 258, title: "高空的银针", at: "park", when: "",
    text: "很高很高的地方，一架飞机慢慢飞过，小得像一枚银色的针。",
    a: { label: "使劲挥手。", out: [
      { text: "飞机轻轻转了个弯。{名字}确信，机长一定看见{她}了。", say: "机长也冲我挥手了！", mood: { name: "和机长打招呼", emo: "happy", pts: 3, min: 180 } },
      { text: "{名字}挥得太投入，路过的人以为在叫自己，也热情地挥了回来。", say: "啊……你好，你好。", mood: { name: "跟路人挥错手", emo: "embarrassed", pts: 2, min: 120 }, need: { social: 5 } } ] },
    b: { label: "猜它飞去哪里。", out: [
      { text: "{名字}给飞机排了一条路线：先去海边，再去下雪的地方，最后去一个面包很好吃的城市。", say: "替我多吃一个面包！", mood: { name: "心飞去远方", emo: "inspired", pts: 3, min: 180 } },
      { text: "猜着猜着，{名字}忽然很想出门旅行，可眼下只有一张长椅。", say: "长椅号，准备起飞……", mood: { name: "想去远方", emo: "sad", pts: 2, min: 150 } } ] } },
  { n: 259, title: "膝盖停机坪", at: "park", when: "",
    text: "一只蝴蝶落在了{名字}的膝盖上，翅膀慢慢开合，似乎打算久留。",
    a: { label: "一动也不动。", out: [
      { text: "{名字}屏住呼吸坚持了好几分钟，蝴蝶才满意地飞走。{她}觉得自己是一块合格的停机坪。", say: "欢迎下次再来降落。", mood: { name: "当了停机坪", emo: "focused", pts: 3, min: 180 } },
      { text: "{名字}忍了很久，最后还是打了个喷嚏。蝴蝶被吹出去老远。", say: "啊——嚏！对不起！", mood: { name: "喷走了蝴蝶", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "小声跟它聊天。", out: [
      { text: "蝴蝶听完，飞起来绕着{名字}转了一圈，才依依不舍地离开。", say: "它是不是喜欢我？", mood: { name: "被蝴蝶偏爱", emo: "flirty", pts: 3, min: 180 } },
      { text: "{名字}刚开口，蝴蝶就飞走了。看来它不喜欢闲聊。", say: "我还没说到重点呢！", mood: { name: "被蝴蝶冷落", emo: "sad", pts: 2, min: 90 } } ] } },
  { n: 260, title: "第一滴雨", at: "park", when: "rain",
    text: "雨点落了下来，长椅上出现了一个个小圆点，越来越多。",
    a: { label: "冲到大树底下躲雨。", out: [
      { text: "树下很干爽，几只鸭子也挤过来躲雨。{名字}和它们一起看雨，像一个小小的避难所。", say: "这里是鸭鸭避难所。", mood: { name: "和鸭子躲雨", emo: "playful", pts: 4, min: 180 } },
      { text: "刚跑到树下，一阵风把满树的雨水一次性倒在了{名字}头上。", say: "这比外面还湿啊！", mood: { name: "被大树淋透", emo: "angry", pts: 3, min: 150 }, need: { hygiene: -10 } } ] },
    b: { label: "坐着淋雨，假装是电影主角。", out: [
      { text: "{名字}望着池塘，雨水顺着脸往下流，感觉自己正在演一部很文艺的电影。", say: "这一幕，应该配音乐。", mood: { name: "雨中文艺片", emo: "inspired", pts: 4, min: 180 }, need: { hygiene: -8 } },
      { text: "演了五分钟，{名字}冷得直打哆嗦，打着喷嚏收工回家。", say: "这部片子……杀青了。", mood: { name: "淋雨着凉", emo: "uncomfortable", pts: 3, min: 180 }, need: { energy: -8, hygiene: -8 } } ] } },
  { n: 261, title: "雪人缺个鼻子", at: "park", when: "snow",
    text: "几个小孩在草坪上堆了一个雪人，围着它发愁：没有胡萝卜当鼻子。",
    a: { label: "贡献出自己的手套。", out: [
      { text: "手套成了雪人的鼻子，样子有点奇怪，但小孩们笑得前仰后合。", say: "很有个性的鼻子！", mood: { name: "贡献了手套", emo: "playful", pts: 4, min: 180 }, need: { social: 8 } },
      { text: "雪人有了鼻子，{名字}的手却没了手套，冻得通红。", say: "手……手没知觉了。", mood: { name: "手冻僵了", emo: "uncomfortable", pts: 3, min: 150 } } ] },
    b: { label: "建议用松果代替。", out: [
      { text: "松果鼻子大获成功，小孩们封{名字}为“雪人总设计师”。", say: "下一个作品叫雪鸭子。", mood: { name: "雪人总设计师", emo: "confident", pts: 4, min: 240 }, need: { social: 8 } },
      { text: "松果一按上去，雪人的脸就塌了。小孩们齐刷刷地看向{名字}。", say: "这、这是抽象派……", mood: { name: "雪人脸塌了", emo: "tense", pts: 3, min: 120 } } ] } },
  { n: 262, title: "金色的诱惑", at: "park", when: "autumn",
    text: "清洁工把落叶扫成了一大堆，金黄蓬松，就在长椅旁边。",
    a: { label: "跳进去。", out: [
      { text: "{名字}跳进叶子堆，沙沙声把{她}整个包住，像掉进了一个巨大的薯片袋。", say: "好脆！好香！好秋天！", mood: { name: "跳进落叶堆", emo: "energized", pts: 4, min: 180 }, need: { fun: 12 } },
      { text: "叶子飞得到处都是。清洁工远远看着，手里的扫帚握得很紧。", say: "我、我帮您扫回去！", mood: { name: "被扫帚盯上", emo: "scared", pts: 3, min: 120 }, need: { energy: -6 } } ] },
    b: { label: "挑一片最好看的叶子。", out: [
      { text: "{名字}挑出一片形状完美的红叶，夹进了口袋，准备当书签。", say: "这片是今年的冠军。", mood: { name: "找到冠军叶", emo: "focused", pts: 3, min: 180 } },
      { text: "挑了半个小时，每片都觉得差点意思，最后空着手回到了长椅。", say: "叶子太多，挑不过来。", mood: { name: "挑到没劲", emo: "bored", pts: 2, min: 120 } } ] } },
  { n: 263, title: "圆滚滚的访客", at: "park", when: "spring",
    text: "花坛开满了花，一只圆滚滚的蜜蜂嗡嗡嗡，围着{名字}的脑袋转圈。",
    a: { label: "保持冷静，假装是一朵花。", out: [
      { text: "蜜蜂在{名字}头顶停了一秒，大概觉得这朵花没什么蜜，失望地飞走了。", say: "我是一朵低糖花。", mood: { name: "假装成花", emo: "playful", pts: 3, min: 150 } },
      { text: "蜜蜂越飞越近，{名字}的“冷静”只坚持了两秒。", say: "啊啊啊别过来！", mood: { name: "被蜜蜂追", emo: "scared", pts: 3, min: 120 }, need: { energy: -6 } } ] },
    b: { label: "慢慢挪到长椅另一头。", out: [
      { text: "{名字}挪过去，蜜蜂也跟着挪过来。最后{她}放弃了，和蜜蜂共享长椅。", say: "行吧，这边归你。", mood: { name: "跟蜜蜂合租", emo: "dazed", pts: 3, min: 150 } },
      { text: "蜜蜂没跟过来，而是扎进了花坛。{名字}看着它忙碌的样子，觉得自己也该干点正事。", say: "它都这么努力……", mood: { name: "被蜜蜂激励", emo: "focused", pts: 3, min: 180 } } ] } },
  { n: 264, title: "石桌上的裁判", at: "park", when: "",
    text: "长椅旁的石桌上，两位老人在下棋，争执不下，转头问{名字}：“你说这步算不算？”",
    a: { label: "认真地判一下。", out: [
      { text: "{名字}说了一句“算”，一方拍手叫好，另一方哼了一声，又摆上了一盘。", say: "公正，是裁判的本分。", mood: { name: "当了棋局裁判", emo: "confident", pts: 3, min: 150 }, need: { social: 8 } },
      { text: "{名字}其实看不懂规则，随口一说，两位老人立刻一起教育起{她}来。", say: "我……我学到了。", mood: { name: "被老人教育", emo: "embarrassed", pts: 3, min: 150 }, need: { social: 6 } } ] },
    b: { label: "劝一句和气生财。", out: [
      { text: "两位老人愣了一下，哈哈大笑，决定这盘算和棋。", say: "和棋最圆满啦。", mood: { name: "化解了棋局", emo: "happy", pts: 3, min: 180 }, need: { social: 6 } },
      { text: "两人同时瞪了{名字}一眼，又转回去接着吵。{名字}默默挪远了一点。", say: "当我没说……", mood: { name: "被两边瞪了", emo: "uncomfortable", pts: 2, min: 90 } } ] } },
  { n: 265, title: "狗狗面试官", at: "park", when: "",
    text: "有人牵着一只狗路过，狗突然停下来，认真地闻{名字}的鞋子。",
    a: { label: "伸手让它闻闻。", out: [
      { text: "狗闻完，把脑袋搁到{名字}手上蹭了蹭。主人说：“它很少这样的。”", say: "我就知道我有狗缘。", mood: { name: "被狗选中", emo: "flirty", pts: 4, min: 240 }, need: { social: 8 } },
      { text: "狗闻完打了个响亮的喷嚏，转身就走。主人尴尬地笑了笑。", say: "我的手……有味道吗？", mood: { name: "被狗嫌弃", emo: "sad", pts: 2, min: 120 } } ] },
    b: { label: "严肃地坐好，接受检查。", out: [
      { text: "检查完毕，狗在{名字}脚边趴下了。主人只好坐下来陪着，跟{名字}聊了好一会儿。", say: "看来我通过面试了。", mood: { name: "通过狗的面试", emo: "confident", pts: 3, min: 180 }, need: { social: 10 } },
      { text: "狗闻得太认真，把{名字}的鞋带叼走了一根。主人追着狗跑出去老远。", say: "我的鞋带！它要去哪！", mood: { name: "鞋带被叼走", emo: "dazed", pts: 3, min: 150 } } ] } },
  { n: 266, title: "第三次经过", at: "park", when: "",
    text: "一个跑步的人第三次经过长椅，每次都朝{名字}点一下头。",
    a: { label: "下一圈也点头回应。", out: [
      { text: "第四圈，对方点头；第五圈，{名字}先点头。两人形成了某种默契。", say: "这就是跑友情谊吧。", mood: { name: "点头之交", emo: "flirty", pts: 3, min: 150 }, need: { social: 5 } },
      { text: "{名字}准备好了点头，可那人这一圈没再经过。{她}保持着点头的姿势等了很久。", say: "人呢？我脖子都酸了。", mood: { name: "等了个寂寞", emo: "bored", pts: 3, min: 120 } } ] },
    b: { label: "站起来陪跑一圈。", out: [
      { text: "{名字}跟着跑了一圈，对方竖起大拇指，还分了{她}一口水。", say: "跑完一圈，我是跑者了！", mood: { name: "陪跑了一圈", emo: "energized", pts: 4, min: 180 }, need: { energy: -10, fun: 8 } },
      { text: "才跑了半圈，{名字}就喘得说不出话，被对方远远甩在后面。", say: "你……先跑……别管我……", mood: { name: "跑不动了", emo: "uncomfortable", pts: 3, min: 150 }, need: { energy: -12 } } ] } },
  { n: 267, title: "长椅的另一端", at: "park", when: "",
    text: "一个陌生人在长椅另一端坐下，打开了一个三明治，香味飘了过来。",
    a: { label: "主动搭话。", out: [
      { text: "两人从三明治聊到天气，又聊到鸭子。分开的时候，{名字}觉得今天的公园特别热闹。", say: "原来陌生人也能聊这么久。", mood: { name: "和陌生人聊天", emo: "happy", pts: 3, min: 240 }, need: { social: 15 } },
      { text: "{名字}刚开口，对方摘下一只耳机：“啊？”{名字}只好说：“……今天天气不错。”", say: "其实我也没想好说啥。", mood: { name: "搭话失败", emo: "embarrassed", pts: 3, min: 120 }, need: { social: 3 } } ] },
    b: { label: "安静地分享这张长椅。", out: [
      { text: "两人谁也没说话，一起看了很久的池塘。走的时候，对方朝{名字}点了点头。", say: "这种安静，刚刚好。", need: { social: 6 } },
      { text: "三明治的香味实在太浓，{名字}的肚子很大声地叫了一下。对方笑着递过来半块。", say: "谢……谢谢，不好意思。", mood: { name: "肚子出卖了我", emo: "embarrassed", pts: 2, min: 120 }, need: { hunger: 10, social: 6 } } ] } },
  { n: 268, title: "傍晚的舞队", at: "park", when: "evening",
    text: "傍晚的空地上，一群人放着音乐跳起了舞，领舞的人朝{名字}招了招手。",
    a: { label: "加入队伍。", out: [
      { text: "{名字}跟着跳了三首，动作越来越熟练，最后站进了第二排。", say: "明天我还来！", mood: { name: "跳舞跳嗨了", emo: "energized", pts: 4, min: 240 }, need: { fun: 12, energy: -8, social: 8 } },
      { text: "{名字}总是慢半拍，别人向左{她}向右，最后撞上了领舞。", say: "我是在……即兴创作。", mood: { name: "跳舞撞了人", emo: "embarrassed", pts: 3, min: 150 }, need: { social: 4 } } ] },
    b: { label: "坐在长椅上用脚打拍子。", out: [
      { text: "{名字}的脚越打越起劲，干脆在长椅上跳起了坐姿版。旁边的小孩也跟着学。", say: "坐着跳，也算跳！", mood: { name: "坐着跳舞", emo: "playful", pts: 3, min: 180 }, need: { fun: 8 } },
      { text: "同一首歌放到第十一遍，{名字}的脚已经停了，脑子里却怎么也停不下来。", say: "这首歌出不去了……", mood: { name: "洗脑神曲", emo: "dazed", pts: 3, min: 240 } } ] } },
  { n: 269, title: "泡泡包围圈", at: "park", when: "",
    text: "一个小孩拿着泡泡机，一大串泡泡朝长椅飘过来，把{名字}团团围住。",
    a: { label: "伸手戳泡泡。", out: [
      { text: "{名字}一口气戳破了二十个，小孩在旁边认真计数，宣布{她}破了纪录。", say: "泡泡杀手，二十连胜！", mood: { name: "戳泡泡冠军", emo: "playful", pts: 4, min: 180 }, need: { fun: 10 } },
      { text: "一个泡泡在{名字}眼前破掉，肥皂水溅进了眼睛。", say: "眼睛！我的眼睛！", mood: { name: "泡泡进眼睛", emo: "angry", pts: 2, min: 90 } } ] },
    b: { label: "鼓起腮帮子，把它们吹走。", out: [
      { text: "泡泡被吹得飞上了天，越飞越高，飞过了路灯。小孩惊呼：“好厉害！”", say: "我的肺活量还可以吧？", mood: { name: "把泡泡送上天", emo: "confident", pts: 3, min: 150 } },
      { text: "{名字}吹得太用力，一阵头晕，眼前好像全都是泡泡。", say: "我也……变成泡泡了……", mood: { name: "吹到头晕", emo: "dazed", pts: 3, min: 120 } } ] } },
  { n: 270, title: "气球推销员", at: "park", when: "",
    text: "一个卖气球的人在小路上停下来，举着一大把气球问{名字}：“来一个？”",
    a: { label: "买一只鸭子形状的。", out: [
      { text: "{名字}把鸭子气球系在长椅上。池塘里的真鸭子游过来，对着它嘎嘎叫了好久。", say: "它们以为来了新邻居。", mood: { name: "鸭子气球交友", emo: "playful", pts: 4, min: 180 }, need: { fun: 10 } },
      { text: "刚付完钱，一阵风就把气球从{名字}手里抢走了。它越飞越高，像要去追飞机。", say: "它去追飞机了……", mood: { name: "气球飞走了", emo: "sad", pts: 3, min: 150 } } ] },
    b: { label: "礼貌地拒绝。", out: [
      { text: "卖气球的人点点头，又送了{名字}一只瘪掉的小气球：“这个不要钱。”", say: "免费的，也是气球。", mood: { name: "白得瘪气球", emo: "dazed", pts: 2, min: 120 } },
      { text: "卖气球的人没有放弃，在旁边整整推销了十分钟，把每只气球的身世都讲了一遍。", say: "我知道它们的身世了……", mood: { name: "被推销到困", emo: "bored", pts: 3, min: 120 } } ] } },
  { n: 271, title: "临时摄影师", at: "park", when: "",
    text: "一对游客把手机递给{名字}：“能帮我们和池塘拍张合照吗？”",
    a: { label: "认真构图，蹲下来拍。", out: [
      { text: "{名字}趴在草地上找角度，拍出来的照片里有人、有池塘，还有一只正好起飞的鸭子。", say: "这张能拿去参赛！", mood: { name: "拍出神照片", emo: "inspired", pts: 4, min: 180 }, need: { social: 6, hygiene: -5 } },
      { text: "{名字}拍了二十张，翻看时才发现每一张都有自己的手指。", say: "这叫……独家水印。", mood: { name: "手指入镜", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "随手按一下就还回去。", out: [
      { text: "对方看了一眼照片，惊喜地说：“哇，比我们自己拍的好多了！”", say: "可能我天生有手感。", mood: { name: "随手出大片", emo: "confident", pts: 3, min: 150 } },
      { text: "照片里两个人都闭着眼睛。对方很客气地说了谢谢，但没有请{她}再拍一张。", say: "要不……再来一张？", mood: { name: "拍砸了合照", emo: "uncomfortable", pts: 2, min: 120 } } ] } },
  { n: 272, title: "请勿投喂", at: "park", when: "hungry",
    text: "{名字}从包里掏出一块面包，正要撕给鸭子，却看见旁边立着一块牌子：请勿投喂。",
    a: { label: "遵守规定，自己吃掉。", out: [
      { text: "面包出乎意料地好吃。鸭子们在水里看着{名字}吃完，表情很复杂。", say: "对不起，规定就是规定。", mood: { name: "当着鸭子吃", emo: "tense", pts: 2, min: 120 }, need: { hunger: 12 } },
      { text: "{名字}刚咬一口，一只鸭子就上了岸，光明正大地从{她}手里叼走了剩下的半块。", say: "它自己拿的！不算我喂！", mood: { name: "面包被抢了", emo: "angry", pts: 3, min: 150 }, need: { hunger: 5 } } ] },
    b: { label: "掰一小块，偷偷扔一下。", out: [
      { text: "面包准确地落在鸭子嘴边。没人发现，鸭子用眼神表示，这是彼此之间的秘密。", say: "嘘，这是我们的秘密。", mood: { name: "和鸭子有秘密", emo: "flirty", pts: 4, min: 180 } },
      { text: "面包刚扔出去，路过的公园管理员咳嗽了一声。{名字}立刻低头研究自己的鞋。", say: "我……我在系鞋带。", mood: { name: "偷喂被发现", emo: "scared", pts: 3, min: 120 } } ] } },
  { n: 273, title: "积木城市", at: "park", when: "",
    text: "从长椅上望过去，远处的高楼只剩一排灰色的影子，像谁摆在天边的积木。",
    a: { label: "数一数有多少扇窗户。", out: [
      { text: "{名字}数到第三百四十二扇时，有扇窗户反了一下光，好像在跟{她}打招呼。", say: "三百四十二号，你好！", mood: { name: "数窗户入迷", emo: "focused", pts: 4, min: 180 } },
      { text: "数到一半，一片云飘过来挡住了半栋楼。{名字}只好从头再数。", say: "云彩，你是故意的吧！", mood: { name: "被云打断", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "想象住在楼顶的人。", out: [
      { text: "{名字}想象楼顶也有个人，正坐在窗边望着公园，心想那张长椅上坐着谁。", say: "也许他也在看我呢。", mood: { name: "隔空对望", emo: "flirty", pts: 3, min: 180 } },
      { text: "想着想着，{名字}开始担心楼顶的人有没有按时吃饭。", say: "楼顶的人，记得吃饭啊。", mood: { name: "操心陌生人", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 274, title: "云像什么", at: "park", when: "",
    text: "天上飘过一朵云，越看越像某样东西，可{名字}一时想不起来是什么。",
    a: { label: "一直盯着，直到想出来。", out: [
      { text: "终于想起来了：是一个刚出炉的面包！{名字}的肚子立刻表示赞同。", say: "是面包！肯定是面包！", mood: { name: "云像面包", emo: "inspired", pts: 3, min: 150 }, need: { hunger: -8 } },
      { text: "等{名字}想出来，云已经变成了另一样东西，只好从头开始想。", say: "你能不能别变了！", mood: { name: "追不上云", emo: "dazed", pts: 3, min: 150 } } ] },
    b: { label: "问问路过的小孩。", out: [
      { text: "小孩看了一眼，说是“一只在打哈欠的鸭子”。{名字}再看，竟然真的很像。", say: "孩子的眼睛真厉害。", mood: { name: "云是只鸭子", emo: "inspired", pts: 3, min: 150 }, need: { social: 5 } },
      { text: "小孩说“是我爸爸”，然后跑走了。{名字}盯着那朵云，陷入了深深的沉思。", say: "他爸爸……这么蓬松吗？", mood: { name: "云是谁爸爸", emo: "dazed", pts: 3, min: 150 } } ] } },
  { n: 275, title: "画里的长椅", at: "park", when: "",
    text: "池塘对岸有人支着画架写生。{名字}发现，画里的长椅上好像正坐着自己。",
    a: { label: "保持姿势，当个好模特。", out: [
      { text: "{名字}一动不动坐了一小时。画家走过来给{她}看：长椅上的小人画得特别可爱。", say: "画里的我好上镜！", mood: { name: "当了模特", emo: "flirty", pts: 4, min: 240 }, need: { social: 6 } },
      { text: "坐了一小时，{名字}腰酸背痛。走过去一看，画家把{她}画成了一个垃圾桶。", say: "我……这么方的吗？", mood: { name: "被画成垃圾桶", emo: "sad", pts: 2, min: 150 }, need: { energy: -6 } } ] },
    b: { label: "绕过去看看画。", out: [
      { text: "画家很高兴有人来看，还教了{名字}怎么画池塘里的倒影。", say: "原来倒影要画得抖一点。", mood: { name: "学了画倒影", emo: "inspired", pts: 4, min: 180 }, need: { social: 8, fun: 6 } },
      { text: "{名字}一走开，画家就叹了口气：“哎，模特跑了。”只好把长椅画成了空的。", say: "我能回去坐吗？", mood: { name: "模特跑了", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 276, title: "蝌蚪在哪儿", at: "park", when: "spring|summer",
    text: "一个小孩拿着小网兜趴在池塘边，问{名字}：“你知道蝌蚪在哪儿吗？”",
    a: { label: "帮他一起找。", out: [
      { text: "两人在水草边捞到了三只蝌蚪。小孩把它们放回水里，认真地说：“等你们长大。”", say: "长大了记得回来看看。", mood: { name: "捞到了蝌蚪", emo: "energized", pts: 3, min: 180 }, need: { fun: 10, social: 6 } },
      { text: "{名字}探身太远，一只脚踩进了池塘。蝌蚪没捞着，鞋里倒是多了几只。", say: "它们自己游进来的！", mood: { name: "鞋子进了水", emo: "uncomfortable", pts: 3, min: 150 }, need: { hygiene: -12 } } ] },
    b: { label: "给他讲青蛙小时候的故事。", out: [
      { text: "小孩听得眼睛发亮，放下网兜说：“那我不捞了，让它们安心长大。”", say: "这孩子比我还懂事。", mood: { name: "讲了好故事", emo: "confident", pts: 3, min: 180 }, need: { social: 6 } },
      { text: "{名字}讲到一半，发现自己也记不清蝌蚪是先长前腿还是后腿。", say: "这个……我回去查查。", mood: { name: "知识卡壳", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 277, title: "草坪上的飞盘", at: "park", when: "",
    text: "一只飞盘落在了长椅前的草坪上，旁边的牌子写着：请勿践踏草坪。",
    a: { label: "踮着脚尖进去捡。", out: [
      { text: "{名字}用芭蕾的姿势捡回飞盘，一根草也没踩倒。飞盘的主人带头鼓起了掌。", say: "这叫草上芭蕾。", mood: { name: "草上芭蕾", emo: "confident", pts: 3, min: 150 }, need: { fun: 6 } },
      { text: "踮到一半失去平衡，{名字}结结实实地趴在了草坪正中央。", say: "我……这是在保护草。", mood: { name: "趴在草坪上", emo: "embarrassed", pts: 3, min: 150 }, need: { hygiene: -8 } } ] },
    b: { label: "坐着等主人自己来。", out: [
      { text: "主人跑过来，也盯着牌子犹豫了。两人站在草坪边，认真讨论了很久该怎么办。", say: "这是个哲学问题。", mood: { name: "草坪哲学", emo: "focused", pts: 3, min: 150 }, need: { social: 6 } },
      { text: "一只鸭子从池塘上来，叼起飞盘，大摇大摆地走进了鸭子房。", say: "它们也想玩吧……", mood: { name: "鸭子劫飞盘", emo: "playful", pts: 3, min: 150 } } ] } },
  { n: 278, title: "天降果子", at: "park", when: "autumn",
    text: "“咚”的一声，一颗小果子从树上掉下来，正好落在{名字}的头顶。",
    a: { label: "抬头寻找肇事者。", out: [
      { text: "树枝间蹲着一只松鼠，怀里抱着另一颗果子，正在瞄准{名字}。", say: "你、你别过来啊！", mood: { name: "被松鼠瞄准", emo: "scared", pts: 3, min: 120 } },
      { text: "树上什么都没有，只有风。{名字}怀疑这棵树对自己有意见。", say: "我哪里得罪你了？", mood: { name: "被树针对", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "当作一个好兆头。", out: [
      { text: "{名字}把果子收进口袋，当作今天的幸运物。果然，接下来一切都很顺。", say: "今天的运气，树给的。", mood: { name: "捡到幸运果", emo: "happy", pts: 3, min: 240 } },
      { text: "{名字}刚说完好兆头，又一颗果子落下来，砸在了同一个地方。", say: "好兆头……太多了吧。", mood: { name: "被砸了两次", emo: "dazed", pts: 3, min: 120 } } ] } },
  { n: 279, title: "纸的远行", at: "park", when: "",
    text: "一阵风吹过，把{名字}放在长椅上的一张纸吹了起来，朝池塘飘去。",
    a: { label: "立刻去追。", out: [
      { text: "{名字}在池塘边一个飞扑，在纸落水前一秒抓住了它。路过的人都愣住了。", say: "这是守门员的本能！", mood: { name: "飞扑救下纸", emo: "energized", pts: 4, min: 180 }, need: { energy: -8 } },
      { text: "纸落在水面上，被一只鸭子当成船，坐着漂走了。", say: "那是我的购物清单啊……", mood: { name: "清单被征用", emo: "sad", pts: 2, min: 150 } } ] },
    b: { label: "算了，反正不重要。", out: [
      { text: "纸在空中转了几圈，又自己飘回了长椅上，好像只是出去兜了个风。", say: "欢迎回来，旅途愉快吗？", mood: { name: "纸自己回来了", emo: "playful", pts: 3, min: 150 } },
      { text: "过了一会儿，{名字}才想起来，那张纸上写着一件很重要的事。可惜已经想不起是什么了。", say: "到底写了啥来着……", mood: { name: "忘了要紧事", emo: "tense", pts: 3, min: 180 } } ] } },
  { n: 280, title: "长椅的邀请", at: "park", when: "tired",
    text: "阳光暖洋洋的，{名字}的眼皮越来越重，长椅好像在邀请{她}躺一会儿。",
    a: { label: "就眯五分钟。", out: [
      { text: "{名字}一觉醒来，精神焕发，身边多了一只同样在打盹的鸭子。", say: "我们都睡得很好。", mood: { name: "和鸭子同眠", emo: "energized", pts: 3, min: 240 }, need: { energy: 15 } },
      { text: "{名字}睡得太香，醒来时脸上多了几道长椅木条压出来的印子。", say: "我的脸变成条纹的了。", mood: { name: "脸上有条纹", emo: "embarrassed", pts: 3, min: 150 }, need: { energy: 12 } } ] },
    b: { label: "强打精神看鸭子。", out: [
      { text: "{名字}数鸭子数到第八只，脑袋一点一点的，最后靠着灯柱睡着了。", say: "第九只……呼……", need: { energy: 8 } },
      { text: "{名字}瞪大眼睛硬撑着。鸭子们好像觉得被监视了，纷纷游到池塘另一边去了。", say: "我只是想保持清醒！", mood: { name: "被误会监视", emo: "uncomfortable", pts: 2, min: 120 } } ] } },
  { n: 281, title: "鸭子过马路", at: "park", when: "",
    text: "鸭妈妈带着一串小鸭从草坪走向池塘，可前面的小路上人来人往。",
    a: { label: "站出来指挥交通。", out: [
      { text: "{名字}张开双臂拦住行人，鸭子们排着队安全通过。最后一只小鸭还回头看了{名字}一眼。", say: "交通指挥官，下班！", mood: { name: "护送了鸭子", emo: "confident", pts: 4, min: 240 }, need: { social: 6 } },
      { text: "行人都停下了，鸭子却不走了，一家子站在原地盯着{名字}张开的双臂。", say: "你们倒是走啊！", mood: { name: "指挥失灵", emo: "angry", pts: 3, min: 120 } } ] },
    b: { label: "坐着默默为它们加油。", out: [
      { text: "一个骑车的人也停了下来，和{名字}一起等鸭子过完，两人相视一笑。", say: "这就是公园的礼让。", mood: { name: "和路人默契", emo: "flirty", pts: 3, min: 180 } },
      { text: "{名字}越看越紧张，加油声越来越大，把鸭妈妈吓得加快了脚步，小鸭们一路小跑。", say: "对不起，我太激动了。", mood: { name: "把鸭子吓跑", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 282, title: "野餐布的邀请", at: "park", when: "",
    text: "草坪上有一家人在野餐。小孩跑过来问{名字}：“你要不要吃一个饭团？”",
    a: { label: "开心地接受。", out: [
      { text: "饭团里有惊喜馅料。{名字}被拉过去坐下，又吃了一个，聊了半个下午。", say: "这家人好热情啊！", mood: { name: "蹭了顿野餐", emo: "happy", pts: 3, min: 240 }, need: { hunger: 15, social: 10 } },
      { text: "{名字}一口咬下去，是芥末馅的。一家人看着{名字}的表情，努力忍住没笑出声。", say: "好……好有层次感！", mood: { name: "吃到芥末馅", emo: "uncomfortable", pts: 3, min: 120 }, need: { hunger: 8 } } ] },
    b: { label: "客气地推辞。", out: [
      { text: "小孩点点头，回去拿来一张自己画的画，说是送给{名字}的“不吃饭团奖”。", say: "这个奖我收下了。", mood: { name: "获得奇怪奖项", emo: "playful", pts: 3, min: 180 }, need: { social: 6 } },
      { text: "小孩走了，香味却留下了。{名字}的肚子开始抗议这个决定。", say: "我是不是太客气了……", mood: { name: "后悔推辞了", emo: "sad", pts: 2, min: 120 }, need: { hunger: -5 } } ] } },
  { n: 283, title: "鸭子的脚冷不冷", at: "park", when: "",
    text: "一个小孩坐到长椅上，指着池塘问：“鸭子的脚一直泡在水里，不冷吗？”",
    a: { label: "认真解释。", out: [
      { text: "{名字}讲得头头是道。小孩听完说：“那我以后也要穿鸭子袜。”", say: "鸭子袜，好主意！", mood: { name: "当了回老师", emo: "confident", pts: 3, min: 180 }, need: { social: 6 } },
      { text: "{名字}讲着讲着，自己也不确定了。小孩追问到第五个“为什么”，{名字}彻底答不上来了。", say: "这个……问鸭子吧。", mood: { name: "被问倒了", emo: "tense", pts: 3, min: 120 } } ] },
    b: { label: "反问他怎么想。", out: [
      { text: "小孩想了半天，说：“因为它们心里很暖。”{名字}觉得这个答案比书上的还好。", say: "这个答案满分。", mood: { name: "被孩子打动", emo: "inspired", pts: 4, min: 240 }, need: { social: 6 } },
      { text: "小孩说“我就是不知道才问你的”，然后用一种看穿一切的眼神看着{名字}。", say: "被、被看穿了……", mood: { name: "被小孩看穿", emo: "embarrassed", pts: 3, min: 120 } } ] } },
  { n: 284, title: "找不到妈妈", at: "park", when: "",
    text: "一个小孩站在小路中间东张西望，嘴巴扁扁的：“我找不到妈妈了。”",
    a: { label: "陪他在原地等。", out: [
      { text: "{名字}陪他数鸭子，数到第六只时，他妈妈就跑过来了。小孩临走前把一颗糖塞给了{名字}。", say: "这颗糖，是勋章。", mood: { name: "帮小孩找到家", emo: "happy", pts: 4, min: 240 }, need: { social: 8 } },
      { text: "两人等了好一会儿，{名字}比小孩还着急，在原地来回打转。最后还是小孩先看见了妈妈。", say: "还好你眼睛比我尖。", mood: { name: "比小孩还慌", emo: "tense", pts: 3, min: 150 } } ] },
    b: { label: "带他去找公园管理员。", out: [
      { text: "管理员用喇叭喊了一声，妈妈很快就出现了。小孩一边走一边回头跟{名字}挥手。", say: "再见，要牵好手哦！", mood: { name: "做了件好事", emo: "energized", pts: 3, min: 180 }, need: { social: 6 } },
      { text: "两人走到管理处才发现，小孩的妈妈一直坐在刚才那张长椅旁边的另一张长椅上。", say: "原来一直在旁边……", mood: { name: "兜了个大圈", emo: "dazed", pts: 3, min: 120 }, need: { energy: -6 } } ] } },
  { n: 285, title: "烤红薯的香味", at: "park", when: "winter",
    text: "公园门口来了一辆卖烤红薯的小推车，甜甜的香味顺着小路一直飘到了长椅这里。",
    a: { label: "去买一个最大的。", out: [
      { text: "卖红薯的人挑了一个最胖的给{名字}，还多送了一个小的。{名字}捧着它，手和心都暖了。", say: "冬天就该这么过！", mood: { name: "捧着烤红薯", emo: "happy", pts: 4, min: 240 }, need: { hunger: 15 } },
      { text: "红薯太烫，{名字}在两只手之间抛来抛去，跳了一段奇怪的舞。", say: "烫烫烫烫烫！", mood: { name: "被红薯烫手", emo: "uncomfortable", pts: 3, min: 120 }, need: { hunger: 10 } } ] },
    b: { label: "只闻闻香味。", out: [
      { text: "{名字}坐在长椅上深呼吸，觉得自己已经吃掉了半个。", say: "闻饱了，省钱了。", mood: { name: "闻香也算吃", emo: "playful", pts: 3, min: 150 } },
      { text: "越闻越饿，等{名字}终于下定决心去买时，小推车已经卖完收摊了。", say: "就差一步……", mood: { name: "红薯卖完了", emo: "sad", pts: 3, min: 150 }, need: { hunger: -8 } } ] } },
  { n: 286, title: "落单的手套", at: "park", when: "winter",
    text: "{名字}发现长椅扶手上搭着一只毛线手套，另一只不知道去哪儿了。",
    a: { label: "把它挂在显眼的树枝上。", out: [
      { text: "第二天，手套不见了，树枝上多了一张纸条：“谢谢！”", say: "它回家了，真好。", mood: { name: "手套回家了", emo: "inspired", pts: 3, min: 180 } },
      { text: "手套挂上去以后，看起来像树在跟每个路人挥手。有个小孩认真地朝它挥了回去。", say: "这棵树好有礼貌。", mood: { name: "树在挥手", emo: "playful", pts: 3, min: 150 } } ] },
    b: { label: "四处找另一只。", out: [
      { text: "{名字}在花坛边找到了另一只，把它们放在一起。一双手套终于团圆了。", say: "你们终于见面了。", mood: { name: "让手套团圆", emo: "focused", pts: 3, min: 180 } },
      { text: "找了一大圈都没找到，{名字}自己的一只手套却不知道丢在了哪里。", say: "现在我也只剩一只了。", mood: { name: "手套也丢了", emo: "sad", pts: 2, min: 150 } } ] } },
  { n: 287, title: "旁边在吵架", at: "park", when: "",
    text: "旁边的小路上，一对情侣停下来小声吵架，声音时大时小，刚好都能听见。",
    a: { label: "假装看鸭子，其实认真听。", out: [
      { text: "听到最后，两人为“鸭子到底有没有耳朵”争了起来，然后一起笑了。{名字}也偷偷笑了。", say: "这架吵得真可爱。", mood: { name: "偷听到和好", emo: "flirty", pts: 3, min: 180 } },
      { text: "两人突然同时转头看向{名字}。{名字}立刻对着池塘大声说：“今天鸭子真多啊！”", say: "今天……鸭子真多啊！", mood: { name: "偷听被发现", emo: "embarrassed", pts: 4, min: 150 } } ] },
    b: { label: "起身换一张长椅。", out: [
      { text: "新长椅视野更好，正对着鸭子房。{名字}觉得自己做了一个很成熟的决定。", say: "成熟的人就该这样。", mood: { name: "成熟的撤退", emo: "confident", pts: 2, min: 120 } },
      { text: "{名字}刚在新长椅坐稳，那对情侣也走了过来，在旁边接着吵。", say: "怎么又是你们……", mood: { name: "躲不开吵架", emo: "angry", pts: 3, min: 120 } } ] } },
  { n: 288, title: "推空气的人", at: "park", when: "morning",
    text: "早晨的草坪上，一位老人在慢慢地打拳，一招一式，像在推着空气。",
    a: { label: "在旁边跟着学。", out: [
      { text: "{名字}学了十分钟，身体越来越轻。老人收势时朝{她}点点头：“有点意思。”", say: "我好像打通了什么。", mood: { name: "晨练很通透", emo: "energized", pts: 4, min: 240 }, need: { energy: 8 } },
      { text: "老人的动作太慢了，{名字}学到单脚站立那招时，睡着了一秒，晃了一下。", say: "差点就倒了……", mood: { name: "学到犯困", emo: "bored", pts: 3, min: 120 } } ] },
    b: { label: "坐着看，当作看节目。", out: [
      { text: "看了一会儿，{名字}的呼吸也跟着慢了下来，脑子格外清楚。", say: "看着都觉得平静。", mood: { name: "跟着静下来", emo: "focused", pts: 3, min: 180 } },
      { text: "老人突然一转身，一掌推向{名字}的方向，然后若无其事地继续打拳。{名字}吓得往后一缩。", say: "那、那一掌是冲我吗？", mood: { name: "被一掌吓到", emo: "scared", pts: 3, min: 120 } } ] } },
  { n: 289, title: "雾中小岛", at: "park", when: "morning",
    text: "早晨的池塘上浮着一层薄雾，鸭子房只露出一个屋顶，像一座小小的岛。",
    a: { label: "对着雾喊一声。", out: [
      { text: "雾里传来一声“嘎”。{名字}觉得自己和雾里的某只鸭子完成了一次秘密接头。", say: "暗号对上了。", mood: { name: "雾中接头", emo: "playful", pts: 3, min: 150 } },
      { text: "{名字}刚喊出声，几个晨跑的人同时停下来看着{她}。雾没有回应，人有。", say: "早……早上好！", mood: { name: "一嗓子尴尬", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "静静地看雾散开。", out: [
      { text: "雾一点点散去，鸭子房、池塘、远处的高楼依次出现。{名字}觉得像在看世界开机。", say: "世界，开机完成。", mood: { name: "看世界开机", emo: "inspired", pts: 4, min: 240 } },
      { text: "{名字}看得太久，雾散了，衣服也被露水打湿了一层。", say: "雾走了，湿留下了。", mood: { name: "被露水打湿", emo: "uncomfortable", pts: 2, min: 120 }, need: { hygiene: -6 } } ] } },
  { n: 290, title: "数不完的星星", at: "park", when: "clear+night",
    text: "夜空很干净，远处高楼的灯一盏盏灭了，天上的星星却越来越多。",
    a: { label: "认真数星星。", out: [
      { text: "{名字}数到第一百零七颗时，一颗流星划了过去，{她}赶紧许了个愿。", say: "愿望是秘密！", mood: { name: "看到了流星", emo: "energized", pts: 4, min: 240 } },
      { text: "{名字}数着数着，把一架夜航飞机的灯也数了进去，从头来了三遍。", say: "那颗星怎么在动啊！", mood: { name: "数错了星星", emo: "dazed", pts: 3, min: 150 } } ] },
    b: { label: "躺在长椅上发呆。", out: [
      { text: "{名字}躺着躺着，觉得长椅在慢慢转，自己正坐着它在宇宙里漂。", say: "宇宙快递，长椅专线。", mood: { name: "长椅漂宇宙", emo: "dazed", pts: 3, min: 180 } },
      { text: "四周太安静了，草丛里突然窸窸窣窣一阵响。{名字}一下子坐了起来。", say: "谁、谁在那里？", mood: { name: "夜里一阵响", emo: "scared", pts: 3, min: 120 } } ] } },
  { n: 291, title: "许愿池", at: "park", when: "",
    text: "池塘边有块小牌子写着“许愿池”，水底躺着几枚亮闪闪的硬币。",
    a: { label: "扔一枚硬币许愿。", out: [
      { text: "硬币“咚”地落进水里，一只鸭子立刻潜下去看了看，浮上来时朝{名字}点了点头。", say: "鸭子说愿望受理了。", mood: { name: "愿望已受理", emo: "confident", pts: 3, min: 240 } },
      { text: "硬币在水面上打了三个水漂，最后落在了鸭子房的屋顶上。", say: "这个愿望……挂起来了？", mood: { name: "愿望上了房", emo: "dazed", pts: 3, min: 150 } } ] },
    b: { label: "愿望要靠自己。", out: [
      { text: "{名字}握紧拳头站了起来，浑身是劲，立刻想去做点什么。", say: "我自己就是许愿池！", mood: { name: "浑身是劲", emo: "energized", pts: 3, min: 180 } },
      { text: "站起来以后，{名字}一时也想不起要靠自己做什么，只好又坐了回去。", say: "先休息，再努力。", mood: { name: "雄心暂停", emo: "bored", pts: 2, min: 120 } } ] } },
  { n: 292, title: "特工，任务来了", at: "park", when: "",
    text: "一个小孩拿着玩具对讲机跑过来，压低声音说：“特工，你的任务来了。”",
    a: { label: "接下任务。", out: [
      { text: "任务是“监视那只白鸭子”。{名字}认真执行了半小时，每五分钟向对讲机汇报一次。", say: "报告，目标正在打盹。", mood: { name: "执行秘密任务", emo: "focused", pts: 4, min: 180 }, need: { fun: 12, social: 6 } },
      { text: "任务是“在长椅上一动不动坐到天黑”。小孩交代完，就被家长领回家了。", say: "那我……还要坐吗？", mood: { name: "任务没人收", emo: "bored", pts: 3, min: 180 } } ] },
    b: { label: "表示自己已经退休了。", out: [
      { text: "小孩很理解，敬了个礼，转身去招募了一只鸭子。", say: "鸭子特工，靠你了。", mood: { name: "推荐了鸭子", emo: "playful", pts: 3, min: 150 } },
      { text: "小孩不同意，说特工是不能退休的，然后给{名字}起了个新代号“退休特工”。", say: "退休特工，还挺酷。", mood: { name: "获得新代号", emo: "confident", pts: 3, min: 180 }, need: { social: 6 } } ] } },
  { n: 293, title: "纸船漂远了", at: "park", when: "",
    text: "一个小孩把纸船放进池塘，纸船顺着风漂向中间，他急得在岸边直跺脚。",
    a: { label: "捡根树枝去够。", out: [
      { text: "{名字}用树枝把纸船轻轻拨回岸边，船上居然还“载”着一片花瓣。", say: "货物完好无损！", mood: { name: "打捞了纸船", emo: "focused", pts: 3, min: 150 }, need: { social: 5 } },
      { text: "树枝一碰，纸船翻了。小孩愣了一下，{名字}也愣了一下。", say: "它……去潜水了。", mood: { name: "弄翻了纸船", emo: "tense", pts: 3, min: 150 } } ] },
    b: { label: "教他折一只新的。", out: [
      { text: "{名字}折了一只更大的，还写上了船名。两人一起看着它稳稳地开向鸭子房。", say: "目的地，鸭子房码头。", mood: { name: "折了新纸船", emo: "inspired", pts: 3, min: 180 }, need: { fun: 8, social: 6 } },
      { text: "{名字}折出来的东西更像一顶帽子。小孩接过去戴在头上，开开心心地跑了。", say: "也……也行吧。", mood: { name: "折船变帽子", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 294, title: "东门在哪儿", at: "park", when: "",
    text: "一个背着大包的人走过来问{名字}：“请问公园的东门怎么走？”",
    a: { label: "热情地指路。", out: [
      { text: "{名字}指得清清楚楚，那人连声道谢。过了一会儿，{她}远远看见那人顺利走出了东门。", say: "导航，就是我。", mood: { name: "指路成功", emo: "confident", pts: 3, min: 150 }, need: { social: 6 } },
      { text: "那人走远以后，{名字}忽然意识到，自己指的是西门。", say: "完了，我指反了……", mood: { name: "指错了方向", emo: "tense", pts: 4, min: 180 } } ] },
    b: { label: "干脆带他走过去。", out: [
      { text: "一路上，那人讲起了自己要去的远方城市。{名字}把他送到门口，挥手告别。", say: "一路顺风啊！", mood: { name: "送了一段路", emo: "inspired", pts: 3, min: 180 }, need: { social: 10, energy: -5 } },
      { text: "走着走着，两个人都迷了路，最后是那人看着手机地图把{名字}送回了长椅。", say: "到底是谁带谁啊……", mood: { name: "一起迷路了", emo: "dazed", pts: 3, min: 150 }, need: { energy: -8 } } ] } },
  { n: 295, title: "花粉来袭", at: "park", when: "spring",
    text: "风一吹，花坛里的花粉飘了过来，{名字}的鼻子开始发痒。",
    a: { label: "憋住。", out: [
      { text: "{名字}憋了足足十秒，喷嚏居然自己消失了。{她}为自己的意志力感到骄傲。", say: "我战胜了喷嚏！", mood: { name: "憋住了喷嚏", emo: "focused", pts: 3, min: 150 } },
      { text: "憋到最后，喷嚏以三倍的威力爆发，把长椅上的落叶全吹飞了。", say: "阿——嚏嚏嚏！", mood: { name: "喷嚏三连发", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "换到上风口坐。", out: [
      { text: "{名字}换了张长椅，鼻子马上就不痒了。旁边的一只鸭子倒是打了个喷嚏。", say: "鸭子也会打喷嚏？", mood: { name: "鸭子打喷嚏", emo: "playful", pts: 3, min: 150 } },
      { text: "新位置离鸭子房太近，空气里飘着一股很浓的鸭子味。", say: "这里……味道很浓郁。", mood: { name: "鸭子味浓郁", emo: "uncomfortable", pts: 3, min: 120 } } ] } },
  { n: 296, title: "扶手上的字", at: "park", when: "",
    text: "{名字}发现长椅扶手上刻着一行很小的字：“我在这里等过一个人。”",
    a: { label: "猜猜后来等到了没有。", out: [
      { text: "{名字}在那行字旁边又发现了一行更小的：“等到了。”{她}的心一下子软了。", say: "等到了，真好。", mood: { name: "刻字有结局", emo: "flirty", pts: 4, min: 240 } },
      { text: "{名字}想了很多种结局，越想越放不下，整个下午都在替那个人着急。", say: "到底等到没有嘛！", mood: { name: "替人着急", emo: "tense", pts: 3, min: 180 } } ] },
    b: { label: "坐着陪那行字待一会儿。", out: [
      { text: "{名字}也在长椅上等了一会儿，虽然没在等谁，却觉得这样的时光很好。", say: "等待也挺浪漫的。", mood: { name: "陪长椅等待", emo: "flirty", pts: 3, min: 180 } },
      { text: "坐着坐着，{名字}有点想念一些很久没联系的人。", say: "改天给老朋友打电话。", mood: { name: "想起老朋友", emo: "sad", pts: 3, min: 180 }, need: { social: -5 } } ] } },
  { n: 297, title: "雨里的彩虹", at: "park", when: "rain",
    text: "雨小了些，太阳从云缝里钻出来，远处的高楼上方挂起了一道彩虹。",
    a: { label: "赶紧叫路人一起看。", out: [
      { text: "几个路人停下来，大家一起仰着头看彩虹，谁也不认识谁，但都在笑。", say: "大家一起看才好看！", mood: { name: "一起看彩虹", emo: "energized", pts: 4, min: 180 }, need: { social: 8 } },
      { text: "{名字}回头叫人，再转回来时，彩虹已经没了。路人看看空荡荡的天，又看看{名字}。", say: "真的有！刚才真有！", mood: { name: "彩虹没等我", emo: "sad", pts: 2, min: 120 } } ] },
    b: { label: "盯着看它从哪儿开始。", out: [
      { text: "{名字}认定彩虹的一头插在鸭子房的屋顶上，决定以后叫它“彩虹房”。", say: "鸭子住上彩虹房了！", mood: { name: "发现彩虹房", emo: "playful", pts: 3, min: 180 } },
      { text: "看得太认真，{名字}一脚踩进了长椅边的水坑。", say: "彩虹没摸到，水坑先到。", mood: { name: "踩进水坑", emo: "angry", pts: 2, min: 120 }, need: { hygiene: -8 } } ] } },
  { n: 298, title: "割草机来了", at: "park", when: "",
    text: "公园管理员推着割草机过来了，嗡嗡声越来越近，空气里全是青草的味道。",
    a: { label: "大口闻草香。", out: [
      { text: "{名字}深深吸了一口，觉得整个人都绿了一点，精神好了很多。", say: "这是青草的味道！", mood: { name: "闻到青草香", emo: "energized", pts: 3, min: 180 } },
      { text: "吸得太猛，一小截草屑被吸进了鼻子。", say: "咳！草进鼻子了！", mood: { name: "鼻子进了草", emo: "uncomfortable", pts: 2, min: 90 } } ] },
    b: { label: "跟管理员聊几句。", out: [
      { text: "管理员停下机器告诉{名字}，那只白鸭子已经在公园住了好多年，是这里的老住户。", say: "原来它是元老啊！", mood: { name: "知道了鸭子史", emo: "focused", pts: 3, min: 180 }, need: { social: 8 } },
      { text: "割草机太吵，两人互相大喊了三分钟，谁也没听清对方说什么，最后笑着摆了摆手。", say: "啊？什么？好的！", mood: { name: "鸡同鸭讲", emo: "playful", pts: 3, min: 120 }, need: { social: 4 } } ] } },
  { n: 299, title: "请回信", at: "park", when: "",
    text: "一只纸飞机歪歪扭扭地飞过来，降落在{名字}脚边，机翼上写着：“请回信”。",
    a: { label: "写好回信，再扔回去。", out: [
      { text: "{名字}写了一句“你的飞机飞得很好”。不一会儿，飞机又飞了回来：“谢谢，你的字好丑。”", say: "……这孩子挺诚实。", mood: { name: "被小孩点评", emo: "angry", pts: 2, min: 120 }, need: { social: 6 } },
      { text: "飞机飞了回去，远处的树后传来小孩的欢呼声。两边就这样来回通信了一下午。", say: "这是长椅航空公司。", mood: { name: "纸飞机通信", emo: "playful", pts: 4, min: 240 }, need: { fun: 12, social: 8 } } ] },
    b: { label: "研究它的折法。", out: [
      { text: "{名字}拆开又折回去，发现了让它飞得更远的秘诀，一扔就飞过了池塘。", say: "我是纸飞机工程师！", mood: { name: "改良纸飞机", emo: "focused", pts: 4, min: 180 }, need: { fun: 8 } },
      { text: "拆开以后，{名字}怎么也折不回原样了。远处的小孩还在探头等着。", say: "它……升级成纸团了。", mood: { name: "飞机折不回", emo: "tense", pts: 3, min: 120 } } ] } },
  { n: 300, title: "鸭子们下班了", at: "park", when: "evening",
    text: "太阳沉到了远处高楼的后面，池塘被染成了橘色，鸭子们也慢慢往鸭子房里游。",
    a: { label: "跟鸭子们道晚安。", out: [
      { text: "{名字}挥手说晚安，最后进门的那只鸭子回头嘎了一声，好像在说明天见。", say: "明天见，鸭子们。", mood: { name: "鸭子说明天见", emo: "inspired", pts: 3, min: 180 } },
      { text: "鸭子们都进去了，只剩{名字}一个坐在长椅上，突然觉得有点冷清。", say: "大家都回家了啊……", mood: { name: "有点冷清", emo: "sad", pts: 3, min: 150 }, need: { social: -5 } } ] },
    b: { label: "拍一张照片留念。", out: [
      { text: "照片拍得刚刚好：橘色的池塘、黑色的楼影，还有一只回头的鸭子。", say: "今天的晚霞，收藏了。", mood: { name: "收藏了晚霞", emo: "focused", pts: 3, min: 180 } },
      { text: "{名字}调了半天角度，等终于满意时，太阳已经下去了，照片里只有一片黑。", say: "太阳下班太快了！", mood: { name: "错过了落日", emo: "angry", pts: 2, min: 120 } } ] } },
  { n: 301, title: "立牌合影", at: "mall", when: "",
    text: "电影院门口立着一个比真人还高的英雄立牌，摆着帅气的姿势。旁边没什么人。",
    a: { label: "摆同款姿势合影。", out: [
      { text: "{名字}学着立牌举起拳头，路过的小孩也跟着摆起来，三个人凑成了一张海报。", say: "今天我也是主角！", mood: { name: "和英雄同框", emo: "confident", pts: 3, min: 150 }, need: { fun: 8 } },
      { text: "姿势摆了太久，{名字}的胳膊开始发抖，立牌却依然纹丝不动。", say: "它怎么一点都不累……", mood: { name: "输给了纸板", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "悄悄问它今天累不累。", out: [
      { text: "立牌当然没回答，但{名字}觉得它的笑容松了一点点。", say: "辛苦啦，站岗的英雄。", mood: { name: "和立牌交心", emo: "playful", pts: 3, min: 150 } },
      { text: "检票员正好路过，礼貌地看了{名字}一眼，又礼貌地移开了视线。", say: "我、我在和它对台词！", mood: { name: "被检票员看见", emo: "embarrassed", pts: 3, min: 120 } } ] } },
  { n: 302, title: "隔壁的尖叫", at: "mall", when: "evening|night",
    text: "路过影厅门口时，里面传出一阵整齐的尖叫，接着是更整齐的安静。",
    a: { label: "贴着门缝听一下。", out: [
      { text: "{名字}什么也没听清，只听见自己的心跳，比电影还吓人。", say: "我的心脏先放映了。", mood: { name: "自己吓自己", emo: "scared", pts: 3, min: 150 } },
      { text: "门突然开了，一个观众捂着眼睛冲出来，两个人同时尖叫。", say: "哇啊！你也吓我一跳！", mood: { name: "门口互相惊吓", emo: "tense", pts: 3, min: 120 }, need: { fun: 5 } } ] },
    b: { label: "快步走开，假装没听见。", out: [
      { text: "{名字}走得飞快，走到超市门口才发现自己一路都踮着脚。", say: "踮脚走路比较安全。", mood: { name: "踮脚逃离影厅", emo: "dazed", pts: 2, min: 120 } },
      { text: "走远以后，{名字}开始琢磨那部电影到底演了什么，把能想到的剧情都猜了一遍。", say: "到底是什么那么吓人？", mood: { name: "推理恐怖片", emo: "focused", pts: 2, min: 150 } } ] } },
  { n: 303, title: "试吃阿姨的眼神", at: "mall", when: "hungry",
    text: "超市试吃台前，阿姨把一块香肠递给{名字}，然后静静地看着，等一个评价。",
    a: { label: "认真点评一番。", out: [
      { text: "{名字}说出了“肉香饱满，回味悠长”，阿姨很感动，又塞来两块。", say: "专业试吃员上岗了！", mood: { name: "被阿姨认可", emo: "confident", pts: 3, min: 180 }, need: { hunger: 10 } },
      { text: "{名字}说得太投入，周围排起了队，阿姨让{名字}帮忙维持秩序。", say: "请大家一人一块哦！", mood: { name: "帮试吃台干活", emo: "energized", pts: 3, min: 150 }, need: { social: 8 } } ] },
    b: { label: "吃完点点头就走。", out: [
      { text: "走出两步，阿姨在身后喊：“好吃就买一包嘛！”{名字}的背影僵了一下。", say: "下、下次一定……", mood: { name: "被阿姨喊住", emo: "uncomfortable", pts: 3, min: 120 }, need: { hunger: 5 } },
      { text: "{名字}觉得刚才那块意犹未尽，在货架间转了一圈，又不好意思回去。", say: "就差一块，就差一块。", mood: { name: "惦记那块香肠", emo: "sad", pts: 2, min: 120 }, need: { hunger: 3 } } ] } },
  { n: 304, title: "有主见的购物车", at: "mall", when: "",
    text: "{名字}推的购物车有一个轮子总想往左拐，像是有自己想去的货架。",
    a: { label: "跟着它走。", out: [
      { text: "购物车把{名字}带到了零食区，正好在搞活动。看来它很懂行。", say: "好车，有眼光！", mood: { name: "购物车带路", emo: "playful", pts: 3, min: 150 }, need: { fun: 8 } },
      { text: "购物车一路拐进了清洁用品区，停在马桶刷面前不动了。", say: "你这是什么暗示？", mood: { name: "被车暗示了", emo: "dazed", pts: 3, min: 120 } } ] },
    b: { label: "换一辆车。", out: [
      { text: "新车四个轮子都很听话，{名字}推得又快又稳，像在开赛车。", say: "这就叫专业座驾！", mood: { name: "推车如开赛车", emo: "energized", pts: 3, min: 150 } },
      { text: "第二辆车的轮子往右拐。{名字}开始怀疑这家超市的车都有自己的立场。", say: "怎么一个比一个有主见。", mood: { name: "购物车难伺候", emo: "angry", pts: 2, min: 120 } } ] } },
  { n: 305, title: "最后一包", at: "mall", when: "",
    text: "货架上只剩最后一包打折饼干，{名字}和一位阿姨同时伸出了手。",
    a: { label: "坚持一下。", out: [
      { text: "两人僵持三秒，阿姨忽然笑了：“你年轻，你拿。”{名字}捧着饼干有点感动。", say: "谢谢阿姨，我会好好吃！", mood: { name: "受宠若惊", emo: "dazed", pts: 3, min: 200 } },
      { text: "阿姨手速惊人，饼干一闪就进了她的篮子。{名字}的手还停在半空。", say: "这……这是武功吧？", mood: { name: "输给阿姨手速", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "礼貌让给阿姨。", out: [
      { text: "阿姨很高兴，从篮子里掏出一个苹果塞给{名字}。看来礼让也能换来水果。", say: "饼干换苹果，不亏！", mood: { name: "礼让换苹果", emo: "playful", pts: 3, min: 150 }, need: { hunger: 6 } },
      { text: "阿姨拿走饼干，转身对同伴说：“这孩子真懂事。”{名字}突然很想吃饼干。", say: "懂事的代价有点大。", mood: { name: "懂事但没饼干", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 306, title: "就差一点", at: "mall", when: "",
    text: "电玩城的抓娃娃机里，有只歪着头的小熊，好像一直在看{名字}。",
    a: { label: "再投一次币。", out: [
      { text: "爪子晃晃悠悠，居然勾住了小熊的标签！{名字}抱着战利品在机器前转了一圈。", say: "我就知道你在等我！", mood: { name: "抓到了小熊", emo: "happy", pts: 4, min: 240 }, need: { fun: 15 } },
      { text: "爪子把小熊抬起来，又温柔地放回原地，还顺便帮它摆正了姿势。", say: "这爪子是在哄它睡觉吗？", mood: { name: "爪子太温柔", emo: "angry", pts: 3, min: 150 }, need: { fun: -5 } } ] },
    b: { label: "研究一下别人怎么抓。", out: [
      { text: "{名字}看了半小时，总结出一套理论：时机、角度、还有运气，主要是运气。", say: "理论满分，实践再说。", mood: { name: "钻研抓娃娃", emo: "focused", pts: 3, min: 180 } },
      { text: "旁边的大叔连抓三只，顺手把一只塞给了看得出神的{名字}。", say: "大叔，您是隐世高人！", mood: { name: "天上掉下小熊", emo: "dazed", pts: 3, min: 150 }, need: { fun: 8 } } ] } },
  { n: 307, title: "跳舞机挑战书", at: "mall", when: "",
    text: "一个小学生在跳舞机上拿了满分，回头看着{名字}：“你敢来吗？”",
    a: { label: "接受挑战。", out: [
      { text: "{名字}踩得手忙脚乱，却意外拿到了一个“完美”。小学生沉默了很久。", say: "嘿嘿，大人也是会跳的！", mood: { name: "赢了小学生", emo: "confident", pts: 4, min: 180 }, need: { fun: 12, energy: -8 } },
      { text: "屏幕上不停闪着“未命中”，小学生在旁边耐心地教{名字}，像个小老师。", say: "老师，左边是哪边？", mood: { name: "被小学生教学", emo: "embarrassed", pts: 3, min: 150 }, need: { energy: -8, social: 8 } } ] },
    b: { label: "说自己今天穿错鞋了。", out: [
      { text: "小学生点点头：“理解，我爸也总这么说。”说完继续跳下一首。", say: "被看穿了，但很体面。", mood: { name: "被小孩看穿", emo: "uncomfortable", pts: 2, min: 120 } },
      { text: "{名字}站在一旁给小学生打拍子，打着打着，自己也跟着晃了起来。", say: "我只是在帮你数拍子！", mood: { name: "偷偷跟着跳", emo: "playful", pts: 3, min: 150 }, need: { fun: 8 } } ] } },
  { n: 308, title: "地上的游戏币", at: "mall", when: "",
    text: "{名字}在电玩城地板上捡到一枚游戏币，亮晶晶的，不知道是谁掉的。",
    a: { label: "拿去玩一把投篮机。", out: [
      { text: "一枚币投出了十几个好球，{名字}越投越准，几个围观的小孩开始鼓掌。", say: "今天手感是捡来的！", mood: { name: "投篮手感爆棚", emo: "energized", pts: 4, min: 180 }, need: { fun: 12 } },
      { text: "第一个球就砸到篮筐弹回来，正中{名字}的脑门。", say: "这枚币不太喜欢我。", mood: { name: "被篮球回击", emo: "dazed", pts: 3, min: 120 } } ] },
    b: { label: "交给前台。", out: [
      { text: "前台小哥郑重地收下，还给{名字}一颗糖当奖励。", say: "一枚币换一颗糖，划算。", mood: { name: "拾币不昧", emo: "confident", pts: 2, min: 150 }, need: { hunger: 3 } },
      { text: "前台小哥看了看：“这个……其实就一块钱。”然后顺手塞回给了{名字}。", say: "好吧，那我收下了。", mood: { name: "币又回来了", emo: "playful", pts: 2, min: 120 } } ] } },
  { n: 309, title: "橱窗里的小狗", at: "mall", when: "",
    text: "宠物店橱窗里，一只小柯基把鼻子贴在玻璃上，看着{名字}一动不动。",
    a: { label: "也把脸贴上去。", out: [
      { text: "隔着玻璃，一人一狗对视了很久。小柯基先打了个哈欠，{名字}也跟着打了一个。", say: "我们心意相通了。", mood: { name: "被柯基迷住", emo: "flirty", pts: 3, min: 180 } },
      { text: "店员敲敲玻璃提醒不要贴着，{名字}的脸在玻璃上留下了一个圆圆的印子。", say: "啊，我的脸印上去了。", mood: { name: "脸印在玻璃上", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "进店问问能不能摸摸它。", out: [
      { text: "店员抱出小柯基，它在{名字}怀里扭来扭去，最后舔了一下{名字}的下巴。", say: "被盖章了！", mood: { name: "被柯基舔了", emo: "happy", pts: 4, min: 240 }, need: { social: 10 } },
      { text: "店员说它刚吃饱在睡午觉。{名字}只好对着熟睡的小狗挥挥手。", say: "下次再来看你哦。", mood: { name: "没摸到小狗", emo: "sad", pts: 2, min: 150 } } ] } },
  { n: 310, title: "鹦鹉的评价", at: "mall", when: "",
    text: "宠物店门口挂着一只鹦鹉，{名字}一走近，它就大声喊：“欢迎光临！”",
    a: { label: "教它说一句新的。", out: [
      { text: "{名字}耐心教了十分钟“今天真可爱”，鹦鹉终于开口：“欢迎光临！”", say: "你这是职业习惯吧。", mood: { name: "鹦鹉不配合", emo: "bored", pts: 3, min: 120 } },
      { text: "鹦鹉学会了{名字}的笑声，之后每个路过的人都被它笑得莫名其妙。", say: "完了，我的笑声流传出去了。", mood: { name: "笑声被学走", emo: "playful", pts: 4, min: 180 }, need: { fun: 10 } } ] },
    b: { label: "回它一句“谢谢光临”。", out: [
      { text: "鹦鹉愣了一下，歪着头想了半天，最后憋出一句：“再见！”", say: "它好像被我绕晕了。", mood: { name: "把鹦鹉绕晕", emo: "confident", pts: 3, min: 150 } },
      { text: "鹦鹉开始和{名字}对喊，越喊越大声，店员不得不出来劝架。", say: "是它先开始的！", mood: { name: "和鹦鹉吵架", emo: "angry", pts: 2, min: 120 } } ] } },
  { n: 311, title: "仓鼠的通勤", at: "mall", when: "",
    text: "宠物店里的仓鼠在跑轮上拼命奔跑，好像要赶一班很重要的车。",
    a: { label: "替它加油。", out: [
      { text: "{名字}一喊，仓鼠跑得更快了，最后一个跟头飞出了轮子，又若无其事地爬回去。", say: "没关系，继续努力！", mood: { name: "给仓鼠加油", emo: "energized", pts: 3, min: 150 } },
      { text: "仓鼠停下来，看了{名字}一眼，转身钻进木屑里睡觉了。", say: "我是不是打扰它下班了？", mood: { name: "仓鼠罢工了", emo: "uncomfortable", pts: 2, min: 120 } } ] },
    b: { label: "陪它一起原地踏步。", out: [
      { text: "{名字}跟着节奏踏步，旁边的小孩也加入了，宠物店里多了一支踏步队。", say: "我们是仓鼠后援团！", mood: { name: "组建踏步队", emo: "playful", pts: 4, min: 180 }, need: { energy: -6, fun: 10 } },
      { text: "踏了五分钟，{名字}累得直喘气，仓鼠还在跑，脸不红心不跳。", say: "小小身体，大大能量……", mood: { name: "体力输给仓鼠", emo: "dazed", pts: 2, min: 120 }, need: { energy: -10 } } ] } },
  { n: 312, title: "试衣间的镜子", at: "mall", when: "",
    text: "服装店试衣间的镜子特别显瘦，{名字}在里面越照越觉得自己是模特。",
    a: { label: "穿着新衣服出去走两步。", out: [
      { text: "{名字}在店里走了一圈台步，店员带头鼓起了掌。", say: "这条过道就是我的秀场！", mood: { name: "走了一圈台步", emo: "confident", pts: 4, min: 200 }, need: { fun: 8 } },
      { text: "一出试衣间，普通镜子诚实地把{名字}照回了原样。", say: "试衣间的镜子骗了我。", mood: { name: "镜子说了实话", emo: "sad", pts: 2, min: 150 } } ] },
    b: { label: "多照一会儿再说。", out: [
      { text: "{名字}在镜子前摆了二十个姿势，门外排队的人开始轻轻敲门。", say: "马上好！最后一个姿势！", mood: { name: "被敲门催促", emo: "tense", pts: 3, min: 120 } },
      { text: "照着照着，{名字}觉得不买这件衣服也行，买一面这样的镜子更值。", say: "我要的是这面镜子。", mood: { name: "想买那面镜子", emo: "inspired", pts: 3, min: 150 } } ] } },
  { n: 313, title: "什么都好看", at: "mall", when: "",
    text: "服装店的店员对{名字}试的每一件衣服都说：“哇，这件太适合你了！”",
    a: { label: "故意试一件最怪的。", out: [
      { text: "{名字}穿上一件全是流苏的外套，店员停顿了两秒：“……很有个性！”", say: "我听出了那两秒。", mood: { name: "店员语塞了", emo: "playful", pts: 3, min: 150 } },
      { text: "那件怪衣服穿在身上，居然真的挺好看。{名字}和店员都愣住了。", say: "原来我什么都能驾驭？", mood: { name: "怪衣服也好看", emo: "flirty", pts: 3, min: 180 } } ] },
    b: { label: "相信店员，挑一件最贵的。", out: [
      { text: "{名字}看了眼价签，默默把衣服挂了回去，店员也默默点了点头。", say: "我们都懂的。", mood: { name: "看到了价签", emo: "uncomfortable", pts: 3, min: 120 } },
      { text: "店员夸得太真诚，{名字}飘飘然地走出店门，走了很远才发现什么都没买。", say: "被夸了一顿，白赚。", mood: { name: "免费被夸", emo: "flirty", pts: 3, min: 180 }, need: { social: 6 } } ] } },
  { n: 314, title: "撞衫", at: "mall", when: "",
    text: "{名字}路过服装店橱窗，发现里面的假人模特和自己穿得几乎一模一样。",
    a: { label: "站到旁边一起当模特。", out: [
      { text: "{名字}一动不动地站在橱窗外，好几个路人以为是新的展示方式，停下来拍照。", say: "嘘，我现在是模特。", mood: { name: "被当成模特", emo: "flirty", pts: 4, min: 180 } },
      { text: "站了十分钟，鼻子痒了，{名字}一个喷嚏破了功，路过的小孩吓了一跳。", say: "模特也是要打喷嚏的！", mood: { name: "模特破功了", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "仔细比较谁穿得好看。", out: [
      { text: "{名字}认定自己赢了：至少自己有头，而且会笑。", say: "赢在有表情。", mood: { name: "赢了假人", emo: "confident", pts: 3, min: 150 } },
      { text: "比来比去，{名字}发现假人穿的是这季新款，自己的是三年前的。", say: "原来我才是复古款。", mood: { name: "撞衫但过季", emo: "dazed", pts: 3, min: 150 } } ] } },
  { n: 315, title: "刚出炉", at: "mall", when: "hungry|morning",
    text: "面包店里传出刚出炉的香味，{名字}的脚自己就拐了进去。",
    a: { label: "买一个热乎的当场吃。", out: [
      { text: "面包又软又烫，{名字}一边吹一边咬，脸上沾了一圈面粉。", say: "烫，但是值得！", mood: { name: "热面包到手", emo: "happy", pts: 3, min: 200 }, need: { hunger: 15 } },
      { text: "{名字}咬得太急，烫到了舌头，后面一整天尝什么都木木的。", say: "舌头……下班了……", mood: { name: "被面包烫到", emo: "uncomfortable", pts: 3, min: 150 }, need: { hunger: 12 } } ] },
    b: { label: "只闻闻，不买。", out: [
      { text: "{名字}在门口深呼吸了好几次，觉得自己已经吃过了。", say: "精神上已经饱了。", mood: { name: "闻香就饱了", emo: "playful", pts: 2, min: 120 }, need: { hunger: -5 } },
      { text: "店员探出头：“要不要尝一小块？”{名字}的意志力当场瓦解。", say: "就……就一小块！", mood: { name: "被一小块收买", emo: "dazed", pts: 2, min: 120 }, need: { hunger: 5 } } ] } },
  { n: 316, title: "打烊前半价", at: "mall", when: "evening|night",
    text: "面包店打烊前开始半价，柜台前一下子挤满了人，店员在喊：“最后十个！”",
    a: { label: "冲进去抢。", out: [
      { text: "{名字}灵活地钻过人群，抢到了最后一个奶油面包，像拿到了冠军奖杯。", say: "冠军面包，归我了！", mood: { name: "抢到半价面包", emo: "energized", pts: 4, min: 180 }, need: { hunger: 10 } },
      { text: "{名字}挤到前面时只剩一根干巴巴的法棍，硬得能当擀面杖。", say: "这……能当武器吧。", mood: { name: "抢到硬法棍", emo: "dazed", pts: 3, min: 150 }, need: { hunger: 5 } } ] },
    b: { label: "在门口等人散了再进。", out: [
      { text: "人散以后，店员把剩下的边角料装了一袋送给{名字}：“反正也卖不掉了。”", say: "耐心果然有回报！", mood: { name: "等到免费面包", emo: "confident", pts: 3, min: 180 }, need: { hunger: 12 } },
      { text: "人散了，面包也没了。店员抱歉地开始拖地。", say: "空手而归，肚子在叫。", mood: { name: "面包卖光了", emo: "sad", pts: 3, min: 150 } } ] } },
  { n: 317, title: "贵鞋试穿", at: "mall", when: "",
    text: "球鞋店里摆着一双限量款，店员看出{名字}在偷瞄，热情地问：“要不要试试？”",
    a: { label: "试一试。", out: [
      { text: "穿上以后，{名字}觉得自己能跳上天窗，在店里轻轻蹦了两下。", say: "我感觉能飞起来！", mood: { name: "穿上了限量鞋", emo: "energized", pts: 4, min: 180 }, need: { fun: 8 } },
      { text: "店员蹲下帮{名字}系鞋带，{名字}紧张得一直说谢谢，说了十一次。", say: "谢谢，谢谢，真的谢谢……", mood: { name: "被店员伺候", emo: "tense", pts: 3, min: 120 } } ] },
    b: { label: "说只是看看。", out: [
      { text: "店员笑着说没关系，还给{名字}讲了半天这双鞋的来历，讲得比电影还精彩。", say: "原来一双鞋有这么多故事。", mood: { name: "听了鞋的故事", emo: "inspired", pts: 3, min: 150 }, need: { social: 8 } },
      { text: "{名字}走出店门又回头看了三次，那双鞋好像也在看{名字}。", say: "它在呼唤我……", mood: { name: "惦记那双鞋", emo: "flirty", pts: 3, min: 180 } } ] } },
  { n: 318, title: "鞋盒塔", at: "mall", when: "",
    text: "球鞋店门口堆着一座高高的鞋盒塔，最下面那个盒子上，正好写着{名字}的尺码。",
    a: { label: "小心地抽出来。", out: [
      { text: "{名字}屏住呼吸抽出鞋盒，塔晃了晃，稳住了。店员冲{名字}竖起大拇指。", say: "我就是叠叠乐之王。", mood: { name: "成功抽出鞋盒", emo: "focused", pts: 4, min: 180 } },
      { text: "塔晃了晃，然后从容地倒了一地。{名字}和店员一起蹲着捡了二十分钟。", say: "对不起，我来帮忙！", mood: { name: "推倒了鞋盒塔", emo: "embarrassed", pts: 4, min: 150 }, need: { social: 5 } } ] },
    b: { label: "请店员帮忙拿。", out: [
      { text: "店员从仓库里拿出一双新的。原来那座塔全是空盒子，只是装饰。", say: "原来是摆设啊！", mood: { name: "鞋盒塔是空的", emo: "dazed", pts: 2, min: 120 } },
      { text: "店员说那个尺码刚卖完，{名字}对着鞋盒塔叹了口气。", say: "空欢喜一场。", mood: { name: "尺码卖完了", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 319, title: "书店的地板", at: "mall", when: "tired|bored",
    text: "书店角落里，几个人坐在地上看书。{名字}也想坐下，但只剩书架之间一个窄窄的空位。",
    a: { label: "挤进去坐下。", out: [
      { text: "{名字}窝在空位里看完了一整本漫画，起身时腿麻得像别人的。", say: "腿……已经不是我的了。", mood: { name: "看书看到腿麻", emo: "inspired", pts: 3, min: 200 }, need: { fun: 12 } },
      { text: "刚坐下，旁边的大叔就开始打呼噜，{名字}看一页书要被打断三次。", say: "大叔，您是来睡觉的吗？", mood: { name: "旁边有人打呼", emo: "uncomfortable", pts: 3, min: 120 } } ] },
    b: { label: "站着看。", out: [
      { text: "{名字}站着翻了几页，发现站着看书也挺好，脑子转得特别快。", say: "站着看，思路更清晰！", mood: { name: "站着看书", emo: "focused", pts: 3, min: 150 } },
      { text: "站了一会儿，店员轻声提醒：“这本要拆封才能看哦。”{名字}这才发现手里的书还包着塑封。", say: "我……在看封面呢。", mood: { name: "看了半天封面", emo: "embarrassed", pts: 3, min: 120 } } ] } },
  { n: 320, title: "先看结局", at: "mall", when: "",
    text: "{名字}在书店拿起一本推理小说，手指已经悄悄翻到了最后一页。",
    a: { label: "偷看凶手是谁。", out: [
      { text: "知道凶手以后，{名字}从头开始看，觉得每条线索都在冲自己眨眼睛。", say: "我早就知道是你！", mood: { name: "掌握了真相", emo: "confident", pts: 3, min: 150 } },
      { text: "最后一页只写着“未完待续”。{名字}盯着这四个字看了很久。", say: "这比凶手还可怕。", mood: { name: "被未完待续", emo: "angry", pts: 3, min: 150 } } ] },
    b: { label: "合上书，自己推理。", out: [
      { text: "{名字}推理了一下午，坚信是管家干的。翻开结局一看，真的是管家。", say: "我果然是名侦探！", mood: { name: "推理正确", emo: "inspired", pts: 4, min: 200 }, need: { fun: 10 } },
      { text: "推理到一半，{名字}开始怀疑书店店员，因为他一直在看{名字}。", say: "店员先生，你有嫌疑。", mood: { name: "怀疑了店员", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 321, title: "甜度选择题", at: "mall", when: "",
    text: "奶茶摊的店员问：“全糖、七分、五分、三分还是无糖？”后面的人在等。",
    a: { label: "大胆选全糖。", out: [
      { text: "第一口甜得{名字}眼睛都亮了，整个下午都轻飘飘的。", say: "甜度满分，快乐满分！", mood: { name: "全糖的快乐", emo: "energized", pts: 4, min: 180 }, need: { hunger: 6, fun: 8 } },
      { text: "甜得{名字}嗓子发紧，只好又买了一瓶水来配奶茶。", say: "奶茶配白水，平衡了。", mood: { name: "甜到发齁", emo: "uncomfortable", pts: 3, min: 120 } } ] },
    b: { label: "选个折中的五分。", out: [
      { text: "不甜不淡，刚刚好，就是喝着有点没意思。{名字}一口一口喝得很平静。", say: "五分糖，五分快乐。", mood: { name: "喝得平平淡淡", emo: "bored", pts: 2, min: 150 } },
      { text: "犹豫太久，后面的人替{名字}喊了“五分”，然后{名字}发现自己其实想要七分。", say: "我的七分糖……", mood: { name: "被别人代选", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 322, title: "最后一颗珍珠", at: "mall", when: "",
    text: "奶茶喝完了，杯底还剩一颗珍珠，怎么吸都吸不上来。",
    a: { label: "调整角度继续吸。", out: [
      { text: "经过一番精密计算，珍珠终于被吸了上来，{名字}嚼得特别郑重。", say: "这颗珍珠来之不易。", mood: { name: "吸到最后珍珠", emo: "focused", pts: 3, min: 150 } },
      { text: "{名字}吸得太用力，发出了很响的声音，整条走廊的人都回头了。", say: "咳，管道疏通完毕。", mood: { name: "吸管声太响", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "放它一条生路。", out: [
      { text: "{名字}把杯子轻轻放进垃圾桶，觉得自己做了一件仁慈的事。", say: "去吧，自由的珍珠。", mood: { name: "放生了珍珠", emo: "playful", pts: 2, min: 120 } },
      { text: "走了很远，{名字}还在想那颗珍珠，觉得它可能是整杯里最好吃的一颗。", say: "它肯定是最好吃的。", mood: { name: "惦记那颗珍珠", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 323, title: "冰淇淋赛跑", at: "mall", when: "summer",
    text: "{名字}刚买的冰淇淋开始融化，奶油顺着蛋筒往下流，速度比预想中快。",
    a: { label: "绕着蛋筒快速舔一圈。", out: [
      { text: "{名字}以惊人的技术稳住了局面，一滴都没浪费。", say: "冰淇淋保卫战，胜利！", mood: { name: "保住了冰淇淋", emo: "focused", pts: 4, min: 180 }, need: { hunger: 8 } },
      { text: "舔得太急，冰淇淋球整个掉在了地上，{名字}手里只剩一个空蛋筒。", say: "只剩下……脆皮了。", mood: { name: "冰淇淋掉了", emo: "sad", pts: 3, min: 150 }, need: { hunger: 3 } } ] },
    b: { label: "找张纸巾先擦擦。", out: [
      { text: "等{名字}找到纸巾回来，冰淇淋已经化成了奶昔，只好当饮料喝。", say: "也行，现在是奶昔了。", mood: { name: "冰淇淋变奶昔", emo: "playful", pts: 3, min: 150 }, need: { hunger: 5 } },
      { text: "{名字}满手黏糊糊地四处找纸巾，冰淇淋摊的店员默默递来一整包。", say: "谢谢，您是救星。", mood: { name: "满手黏糊糊", emo: "uncomfortable", pts: 3, min: 120 }, need: { hygiene: -8 } } ] } },
  { n: 324, title: "飞上天窗的气球", at: "mall", when: "",
    text: "一个小孩的气球脱了手，慢悠悠地飘向商场的天窗。小孩看着它，嘴角开始往下撇。",
    a: { label: "跳起来去抓。", out: [
      { text: "{名字}一跳，指尖勾住了绳子！小孩破涕为笑，抱着{名字}的腿说谢谢。", say: "气球归还，任务完成！", mood: { name: "救回了气球", emo: "energized", pts: 4, min: 180 }, need: { social: 10 } },
      { text: "{名字}跳了三次，离气球越来越远。小孩看着{名字}，反而不哭了，开始笑。", say: "好吧，逗你笑也算成功。", mood: { name: "跳了个寂寞", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "带小孩去气球摊。", out: [
      { text: "气球摊老板听了经过，免费送了小孩一个新的，还送了{名字}一个。", say: "我也有气球啦！", mood: { name: "得到了气球", emo: "happy", pts: 3, min: 200 }, need: { fun: 8 } },
      { text: "小孩到了气球摊，挑了一个比原来大三倍的，家长在后面无奈地掏钱。", say: "这……算我帮倒忙吗？", mood: { name: "帮了倒忙", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 325, title: "有点蔫的花", at: "mall", when: "spring",
    text: "鲜花摊的老板要收摊了，指着一束有点蔫的雏菊说：“送你吧，回家泡水就能精神。”",
    a: { label: "收下。", out: [
      { text: "{名字}抱着花走了一路，那束雏菊好像真的慢慢抬起了头。", say: "你看，你也想去我家。", mood: { name: "救活了雏菊", emo: "inspired", pts: 3, min: 200 } },
      { text: "雏菊抱在怀里，花瓣一路掉，{名字}身后留下了一串小白点。", say: "像童话里撒面包屑。", mood: { name: "一路掉花瓣", emo: "playful", pts: 2, min: 120 } } ] },
    b: { label: "坚持要付钱。", out: [
      { text: "老板推辞不过，收了一块钱，又多塞了一枝小玫瑰。", say: "这笔买卖，我赚了。", mood: { name: "多得一枝玫瑰", emo: "flirty", pts: 3, min: 180 } },
      { text: "两个人推来推去，最后{名字}把钱放在摊上就跑，老板在后面喊：“花没拿！”", say: "啊！我的花！", mood: { name: "跑太快忘拿花", emo: "embarrassed", pts: 3, min: 120 } } ] } },
  { n: 326, title: "定制棉花糖", at: "mall", when: "",
    text: "棉花糖摊的师傅说什么形状都能做，问{名字}想要什么。",
    a: { label: "要一朵云。", out: [
      { text: "师傅转了几圈，一朵又大又松的云出现在{名字}手里，比天窗外的云还像云。", say: "我拿到一朵云啦！", mood: { name: "手里有朵云", emo: "inspired", pts: 3, min: 200 }, need: { hunger: 6 } },
      { text: "云做得太大，{名字}吃了半天还是一大朵，脸上已经粘满了糖丝。", say: "云……把我吃了。", mood: { name: "被棉花糖淹没", emo: "dazed", pts: 2, min: 120 }, need: { hygiene: -6 } } ] },
    b: { label: "要一个照着自己做的。", out: [
      { text: "师傅认真端详{名字}，做出来的东西圆滚滚的。{名字}觉得很像，又不想承认。", say: "我……有这么圆吗？", mood: { name: "被做成棉花糖", emo: "uncomfortable", pts: 2, min: 120 } },
      { text: "师傅做出一个很可爱的小人，围观的小孩都要买同款，{名字}成了今天的招牌。", say: "我成了限定款！", mood: { name: "成了招牌款", emo: "flirty", pts: 4, min: 200 }, need: { social: 8 } } ] } },
  { n: 327, title: "很配你的耳坠", at: "mall", when: "",
    text: "手作饰品地摊的老板举着一对小月亮耳坠说：“这对和你特别配。”",
    a: { label: "试戴一下。", out: [
      { text: "{名字}拿起小镜子一照，确实很配，配到老板开始拿{名字}给其他客人展示。", say: "我成了活体样品。", mood: { name: "被当成样品", emo: "flirty", pts: 3, min: 180 }, need: { social: 6 } },
      { text: "{名字}没有耳洞，只好把耳坠挂在耳朵边上，老板笑得直拍腿。", say: "我挂上去了，算吗？", mood: { name: "没有耳洞", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "问问是怎么做的。", out: [
      { text: "老板教{名字}用小钳子弯了一颗星星，虽然有点歪，但{名字}很骄傲。", say: "歪星星也是星星！", mood: { name: "学会做星星", emo: "inspired", pts: 4, min: 200 }, need: { fun: 10 } },
      { text: "老板讲了整整半小时工艺，讲到兴头上，忘了要卖东西。", say: "我好像上了一节课。", mood: { name: "听了半小时课", emo: "bored", pts: 3, min: 120 } } ] } },
  { n: 328, title: "旧书里的纸条", at: "mall", when: "",
    text: "旧书摊上，{名字}翻开一本旧诗集，一张折起来的纸条掉了出来。",
    a: { label: "打开看看。", out: [
      { text: "纸条上写着：“读到这里的人，今天会有好运。”{名字}决定相信。", say: "好运签收了！", mood: { name: "收到陌生祝福", emo: "inspired", pts: 4, min: 240 } },
      { text: "纸条上是一份购物清单：鸡蛋、葱、酱油。{名字}莫名觉得很亲切。", say: "原来前主人也爱吃炒蛋。", mood: { name: "读到购物清单", emo: "dazed", pts: 2, min: 120 } } ] },
    b: { label: "原样夹回去。", out: [
      { text: "{名字}把纸条放回原处，觉得自己守护了一个秘密。摊主冲{名字}点了点头。", say: "这是书的秘密。", mood: { name: "守护了秘密", emo: "confident", pts: 2, min: 150 } },
      { text: "回家后{名字}一直在想纸条上写了什么，后悔得在床上翻了好几个身。", say: "当时为什么不看一眼！", mood: { name: "后悔没看纸条", emo: "tense", pts: 3, min: 180 } } ] } },
  { n: 329, title: "隐藏款", at: "mall", when: "",
    text: "盲盒地摊的老板神秘地说：“这一排里，有一个是隐藏款。”",
    a: { label: "凭直觉挑一个。", out: [
      { text: "拆开一看，是闪闪发光的隐藏款！老板说他摆了一个月都没人抽到。", say: "我就是天选之人！", mood: { name: "抽到隐藏款", emo: "happy", pts: 5, min: 240 }, need: { fun: 15 } },
      { text: "拆出来的和家里已有的三个一模一样，{名字}现在有一支小队了。", say: "四胞胎，凑齐了。", mood: { name: "又抽到重复款", emo: "angry", pts: 2, min: 150 } } ] },
    b: { label: "先看看旁边的小孩怎么抽。", out: [
      { text: "小孩把每个盒子摇一摇、听一听，然后指了一个给{名字}。果然是想要的那款。", say: "小大师，请收下我的糖。", mood: { name: "小孩指点迷津", emo: "playful", pts: 3, min: 180 }, need: { social: 8 } },
      { text: "{名字}看小孩连抽五个都没中，越看越害怕，最后一个都没敢买。", say: "我还是保住钱包吧。", mood: { name: "看别人抽到怕", emo: "scared", pts: 2, min: 120 } } ] } },
  { n: 330, title: "逆行扶梯", at: "mall", when: "",
    text: "{名字}发现自己踏上的是向下的扶梯，而想去的地方在楼上。",
    a: { label: "逆着往上跑。", out: [
      { text: "{名字}跑得飞快，竟然真的上去了！到顶时气喘吁吁，觉得自己战胜了机器。", say: "我赢了扶梯！", mood: { name: "战胜了扶梯", emo: "energized", pts: 4, min: 180 }, need: { energy: -10, fun: 8 } },
      { text: "跑了半天还在原地，下楼的人从{名字}身边缓缓经过，礼貌地点了点头。", say: "我只是在锻炼……", mood: { name: "扶梯上原地跑", emo: "embarrassed", pts: 3, min: 120 }, need: { energy: -8 } } ] },
    b: { label: "顺着下去，再坐上行的。", out: [
      { text: "{名字}顺便在楼下发现了一家新开的小店，绕路绕出了惊喜。", say: "绕路也有绕路的好处。", mood: { name: "绕路发现新店", emo: "inspired", pts: 3, min: 150 } },
      { text: "下去以后，上行扶梯正在维修，{名字}只好爬楼梯。", say: "今天注定要锻炼。", mood: { name: "扶梯在维修", emo: "angry", pts: 2, min: 120 }, need: { energy: -8 } } ] } },
  { n: 331, title: "天窗上的雨", at: "mall", when: "rain",
    text: "外面下起了雨，雨点打在商场的天窗上，噼里啪啦，像有人在上面敲鼓。",
    a: { label: "站在天窗下听雨。", out: [
      { text: "{名字}仰着头听了很久，觉得这是全商场最好听的音乐。", say: "免费的演奏会。", mood: { name: "听天窗雨声", emo: "inspired", pts: 3, min: 200 } },
      { text: "{名字}听得入了神，被推购物车的人轻轻撞了一下脚后跟。", say: "哎哟，雨声太好听了嘛。", mood: { name: "被购物车撞", emo: "dazed", pts: 2, min: 120 } } ] },
    b: { label: "趁下雨多逛一会儿。", out: [
      { text: "反正出不去，{名字}把平时没进过的店都逛了一遍，收获满满。", say: "下雨天就是逛街天！", mood: { name: "雨天逛个够", emo: "energized", pts: 3, min: 180 }, need: { fun: 10, energy: -6 } },
      { text: "整个商场挤满了进来躲雨的人，{名字}被人潮推着走了一圈，又回到原地。", say: "我被人群打包了。", mood: { name: "被人潮推着走", emo: "uncomfortable", pts: 3, min: 150 }, need: { energy: -8 } } ] } },
  { n: 332, title: "天窗外的雪", at: "mall", when: "snow",
    text: "天窗上慢慢积了一层薄雪，商场里暖洋洋的，抬头却是一片白。",
    a: { label: "出去踩雪。", out: [
      { text: "{名字}在商场门口踩出一串脚印，回头一看，像一行歪歪扭扭的字。", say: "我在雪地上签名啦。", mood: { name: "在雪上签名", emo: "playful", pts: 4, min: 200 }, need: { fun: 12 } },
      { text: "一出门，风就灌进领子，{名字}打了个哆嗦，用最快速度退回了商场。", say: "外面是冰箱模式！", mood: { name: "被冷风劝退", emo: "scared", pts: 2, min: 120 } } ] },
    b: { label: "在天窗下看雪景。", out: [
      { text: "暖气、热饮、头顶的雪，{名字}觉得这是冬天最奢侈的看雪方式。", say: "又暖又能看雪，完美。", mood: { name: "暖暖地看雪", emo: "happy", pts: 3, min: 200 } },
      { text: "看了半天，雪一直在下，也没下出什么新花样。{名字}打了个哈欠。", say: "雪也该换个下法了。", mood: { name: "雪景看腻了", emo: "bored", pts: 2, min: 120 } } ] } },
  { n: 333, title: "巨型装饰树", at: "mall", when: "winter",
    text: "走廊中央立起一棵巨大的装饰树，挂满了彩球。最低的那颗彩球，离{名字}的鼻子只有一点点。",
    a: { label: "偷偷摇一摇彩球。", out: [
      { text: "彩球叮的一声，树上的灯突然全亮了，原来正好到了点灯时间。周围响起一片欢呼。", say: "是我点亮的！大概。", mood: { name: "以为点亮了树", emo: "confident", pts: 4, min: 200 } },
      { text: "彩球掉了下来，滚了好远，{名字}追着它跑过了半条走廊。", say: "等等我，小球！", mood: { name: "追了半条走廊", emo: "embarrassed", pts: 3, min: 120 }, need: { energy: -6 } } ] },
    b: { label: "数一数有多少彩球。", out: [
      { text: "{名字}数到第两百零三个，被保安叔叔问是不是在搞统计。", say: "是的，我在做调研。", mood: { name: "数彩球数入迷", emo: "focused", pts: 3, min: 150 } },
      { text: "数到一百多，{名字}忘了数到哪里，只好从头开始，这已经是第三次了。", say: "一、二、三……又来了。", mood: { name: "数到忘记了", emo: "bored", pts: 3, min: 120 } } ] } },
  { n: 334, title: "南瓜灯", at: "mall", when: "autumn",
    text: "商场在走廊里摆了一排南瓜灯，每一个都咧着嘴笑，其中一个笑得特别歪。",
    a: { label: "和歪嘴南瓜比鬼脸。", out: [
      { text: "{名字}的鬼脸太投入，路过的小孩笑得蹲在了地上。", say: "我的鬼脸赢了南瓜！", mood: { name: "鬼脸大获全胜", emo: "playful", pts: 4, min: 180 }, need: { fun: 10 } },
      { text: "{名字}做完鬼脸，一回头发现布置会场的工人正看着自己，手里还抱着南瓜。", say: "我在帮它们练表情。", mood: { name: "被工人撞见", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "帮它把嘴角扶正。", out: [
      { text: "扶正以后，南瓜看起来端庄多了，{名字}很满意自己的审美。", say: "这样才体面嘛。", mood: { name: "给南瓜整容", emo: "focused", pts: 2, min: 150 } },
      { text: "一碰，南瓜里面的灯灭了。歪嘴南瓜现在看起来很伤心。", say: "对不起，我不是故意的！", mood: { name: "弄灭了南瓜灯", emo: "scared", pts: 3, min: 120 } } ] } },
  { n: 335, title: "广播里的名字", at: "mall", when: "",
    text: "商场广播在找人，念的名字和{名字}的名字有点像，又不完全一样。",
    a: { label: "去服务台问问。", out: [
      { text: "原来是另一位客人丢了钱包。{名字}帮着在走廊里找到了失主，被谢了好几遍。", say: "原来我也能当侦探！", mood: { name: "帮人找到失主", emo: "confident", pts: 3, min: 180 }, need: { social: 10 } },
      { text: "服务台的人看了{名字}一眼：“不是你。”{名字}只好装作是来问厕所在哪的。", say: "那……厕所在哪儿？", mood: { name: "白跑一趟", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "继续逛，假装没听见。", out: [
      { text: "广播又念了一遍，这次{名字}听清楚了，确实不是自己，松了一口气。", say: "还好不是我。", mood: { name: "虚惊一场", emo: "tense", pts: 2, min: 120 } },
      { text: "{名字}一边逛一边想，如果广播真叫到自己，应该摆什么表情。", say: "我要练一个镇定的表情。", mood: { name: "练广播表情", emo: "focused", pts: 2, min: 120 } } ] } },
  { n: 336, title: "投币按摩椅", at: "mall", when: "tired",
    text: "走廊边有一排投币按摩椅，{名字}的腿已经走得发酸了。",
    a: { label: "投币坐上去。", out: [
      { text: "按摩椅揉得恰到好处，{名字}差点在走廊里睡着。", say: "这椅子懂我……", mood: { name: "被按摩椅治愈", emo: "happy", pts: 4, min: 200 }, need: { energy: 10 } },
      { text: "按摩椅力气太大，{名字}被揉得一颠一颠的，说话都带了颤音。", say: "我、我、我很好……", mood: { name: "被按摩椅暴揉", emo: "dazed", pts: 3, min: 120 }, need: { energy: 5 } } ] },
    b: { label: "旁边免费的长椅也行。", out: [
      { text: "{名字}坐在长椅上，看着按摩椅上的人一抖一抖，觉得自己做了正确的选择。", say: "省下的钱买奶茶。", mood: { name: "省钱坐长椅", emo: "confident", pts: 2, min: 120 }, need: { energy: 6 } },
      { text: "{名字}在长椅上坐着坐着，越坐越无聊，看着按摩椅发了半天呆。", say: "长椅好硬，好无聊……", mood: { name: "长椅坐到发呆", emo: "bored", pts: 2, min: 120 }, need: { energy: 8 } } ] } },
  { n: 337, title: "热情的传单", at: "mall", when: "",
    text: "走廊里，一个推销员拦住{名字}，热情地递上传单：“健身房开业，免费体验！”",
    a: { label: "接过来听他说。", out: [
      { text: "推销员越说越激动，{名字}听得热血沸腾，当场做了二十个深蹲。", say: "我感觉已经练过了！", mood: { name: "被推销员燃起", emo: "energized", pts: 4, min: 180 }, need: { energy: -8 } },
      { text: "推销员说了二十分钟，{名字}手里的传单已经被折成了一只纸鹤。", say: "这只鹤也想去健身。", mood: { name: "听推销走神", emo: "bored", pts: 3, min: 120 } } ] },
    b: { label: "礼貌地说不用了。", out: [
      { text: "推销员点点头放行，{名字}走了几步，又被下一个推销员拦住。是游泳馆。", say: "今天是体育节吗？", mood: { name: "连续被拦住", emo: "uncomfortable", pts: 3, min: 120 } },
      { text: "推销员很理解，还塞给{名字}一瓶开业送的矿泉水。", say: "没办卡，白拿一瓶水。", mood: { name: "白拿一瓶水", emo: "playful", pts: 2, min: 120 } } ] } },
  { n: 338, title: "迷路的小朋友", at: "mall", when: "",
    text: "一个小朋友站在走廊中间，左看右看，最后拉住了{名字}的衣角。",
    a: { label: "带去服务台。", out: [
      { text: "广播一响，小朋友的妈妈三十秒内就冲了过来，抱着孩子连声道谢。", say: "团圆啦，太好了！", mood: { name: "帮小孩找到家人", emo: "inspired", pts: 4, min: 240 }, need: { social: 10 } },
      { text: "去服务台的路上，小朋友指着冰淇淋摊不走了，{名字}被迫请了一个冰淇淋。", say: "这是赎金吗……", mood: { name: "被小孩敲竹杠", emo: "dazed", pts: 3, min: 150 } } ] },
    b: { label: "原地陪着等。", out: [
      { text: "{名字}陪小朋友玩起了猜拳，玩着玩着，家长找了过来，还加入了一局。", say: "最后是我赢了哦！", mood: { name: "陪小孩猜拳", emo: "playful", pts: 3, min: 180 }, need: { social: 8, fun: 6 } },
      { text: "等了半天没人来，小朋友突然说：“我爸爸在电玩城呀。”原来他根本没迷路。", say: "那你拉我衣角干嘛！", mood: { name: "小孩没迷路", emo: "angry", pts: 2, min: 120 } } ] } },
  { n: 339, title: "你在这里", at: "mall", when: "",
    text: "走廊的导航牌上写着“你在这里”，可是那个红点和{名字}的方向完全对不上。",
    a: { label: "相信导航牌。", out: [
      { text: "{名字}按图走了一圈，绕回了原地，导航牌依然坚定地说“你在这里”。", say: "你说得对，我确实在这里。", mood: { name: "被导航牌绕晕", emo: "dazed", pts: 3, min: 150 } },
      { text: "跟着导航牌，{名字}意外走进一条没去过的小走廊，里面全是地摊。", say: "迷路迷出了宝藏！", mood: { name: "迷路发现地摊", emo: "inspired", pts: 3, min: 180 }, need: { fun: 8 } } ] },
    b: { label: "问路过的清洁阿姨。", out: [
      { text: "阿姨三句话就说清楚了，还顺便推荐了哪家面包最好吃。", say: "阿姨才是真正的地图！", mood: { name: "遇到活地图", emo: "energized", pts: 2, min: 150 }, need: { social: 5 } },
      { text: "阿姨随手指了一个方向，{名字}走过去，推开门发现是员工通道，里面黑乎乎的。", say: "这……是阿姨的捷径吧。", mood: { name: "误入员工通道", emo: "scared", pts: 2, min: 120 } } ] } },
  { n: 340, title: "太干净的玻璃", at: "mall", when: "",
    text: "某家店的玻璃门擦得太干净了，{名字}差点以为那里什么也没有。",
    a: { label: "伸手先摸一摸。", out: [
      { text: "{名字}在玻璃上摸到了门把手，得意地推开，店员夸{名字}眼神好。", say: "我早就看穿了！", mood: { name: "识破玻璃门", emo: "confident", pts: 2, min: 120 } },
      { text: "{名字}摸着摸着，发现自己在玻璃上留下了一排手印，清洁阿姨正在后面看着。", say: "我……我帮您擦掉！", mood: { name: "留下一排手印", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "大步走过去。", out: [
      { text: "门是自动的，在{名字}鼻子前一厘米处唰地打开。{名字}觉得自己像个大人物。", say: "开门迎接我？客气了。", mood: { name: "自动门迎宾", emo: "flirty", pts: 3, min: 150 } },
      { text: "咚的一声。玻璃门没事，{名字}的额头起了一个小包。", say: "这门……擦得太认真了。", mood: { name: "撞上玻璃门", emo: "angry", pts: 3, min: 150 }, need: { fun: -5 } } ] } },
  { n: 341, title: "转盘抽奖", at: "mall", when: "",
    text: "走廊中央摆着一个大转盘，主持人举着话筒喊：“下一位！转到什么拿什么！”",
    a: { label: "上去转一把。", out: [
      { text: "转盘停在一等奖旁边那格：“再来一次”。第二次停在了“谢谢参与”。", say: "差一点就是一等奖！", mood: { name: "与大奖擦肩", emo: "angry", pts: 2, min: 150 } },
      { text: "{名字}转到了一只大玩偶熊，抱着它走过走廊，好多人羡慕地看过来。", say: "这只熊归我了！", mood: { name: "转到大玩偶", emo: "energized", pts: 4, min: 200 }, need: { fun: 12 } } ] },
    b: { label: "在旁边看别人转。", out: [
      { text: "主持人看{名字}站得久，把话筒递了过来，让{名字}帮忙喊“下一位”。", say: "下一位！下一位！", mood: { name: "当了临时主持", emo: "confident", pts: 3, min: 150 }, need: { social: 8 } },
      { text: "{名字}一边看一边记，总结出转盘最爱停在“谢谢参与”。", say: "数据不会骗人。", mood: { name: "研究转盘规律", emo: "focused", pts: 3, min: 150 } } ] } },
  { n: 342, title: "冷气太足", at: "mall", when: "summer",
    text: "外面热得冒烟，商场里的冷气却开得像冬天，{名字}的胳膊上起了一层鸡皮疙瘩。",
    a: { label: "去服装店买件外套。", out: [
      { text: "{名字}买了一件薄外套，店员说：“夏天来买外套的，你是今天第七个。”", say: "原来大家都冷啊。", mood: { name: "加入外套联盟", emo: "playful", pts: 3, min: 150 } },
      { text: "试了一件，好看又暖和，看了价签，{名字}又冷了。", say: "价签比冷气还凉。", mood: { name: "被价签冻住", emo: "uncomfortable", pts: 3, min: 120 } } ] },
    b: { label: "跑到门口晒一晒再回来。", out: [
      { text: "一冷一热来回跑了几趟，{名字}觉得自己像蒸了桑拿，浑身通透。", say: "冷热交替，神清气爽！", mood: { name: "冷热桑拿", emo: "energized", pts: 3, min: 150 }, need: { energy: 6 } },
      { text: "在门口站了一会儿热出一身汗，回到冷气里，{名字}连打了三个喷嚏。", say: "阿嚏！这是什么天气。", mood: { name: "冷热打喷嚏", emo: "angry", pts: 2, min: 120 }, need: { hygiene: -6 } } ] } },
  { n: 343, title: "打烊音乐", at: "mall", when: "night",
    text: "商场开始放打烊音乐，灯一盏一盏暗下来，走廊里只剩零星几个人。",
    a: { label: "慢慢走，享受空荡荡的商场。", out: [
      { text: "{名字}一个人走在空走廊里，脚步声有回音，好像整座商场只属于自己。", say: "今晚，商场是我的。", mood: { name: "独享整座商场", emo: "inspired", pts: 3, min: 200 } },
      { text: "走着走着，背后的灯一排排灭了，只剩前面还亮着，{名字}心里有点发毛。", say: "灯……是在追我吗？", mood: { name: "被熄灯追赶", emo: "scared", pts: 3, min: 150 } } ] },
    b: { label: "赶紧去出口。", out: [
      { text: "{名字}在保安叔叔锁门前一秒溜了出去，叔叔冲{名字}挥了挥手。", say: "晚安，商场！", mood: { name: "赶上了关门", emo: "energized", pts: 2, min: 120 } },
      { text: "跑到出口，门已经锁了。保安叔叔领着{名字}从侧门出去，一路都在讲他年轻时的故事。", say: "叔叔的故事好长……", mood: { name: "听保安讲故事", emo: "bored", pts: 3, min: 120 }, need: { social: 6 } } ] } },
  { n: 344, title: "开门前的口号", at: "mall", when: "morning",
    text: "商场刚开门，服装店的店员们排成一排，正在大声喊口号。",
    a: { label: "站在一旁跟着喊。", out: [
      { text: "{名字}喊得比谁都响，店长过来拍了拍{名字}的肩膀：“要不要来上班？”", say: "我只是来打气的！", mood: { name: "被店长看中", emo: "energized", pts: 4, min: 180 }, need: { social: 8 } },
      { text: "口号喊完，大家散开去忙了，只剩{名字}一个人还举着拳头。", say: "那个……我也收工了。", mood: { name: "一个人举拳头", emo: "embarrassed", pts: 3, min: 120 } } ] },
    b: { label: "安静地路过。", out: [
      { text: "{名字}被口号感染，一上午走路都踩着节拍，逛街效率特别高。", say: "一二一，一二一！", mood: { name: "被口号感染", emo: "focused", pts: 3, min: 150 } },
      { text: "{名字}路过时，店员们正好喊到“欢迎光临”，齐刷刷地朝{名字}鞠躬。", say: "啊，不、不用这么客气！", mood: { name: "被集体鞠躬", emo: "tense", pts: 3, min: 120 } } ] } },
  { n: 345, title: "挥手的人", at: "mall", when: "lonely",
    text: "走廊另一头，有个人笑着朝{名字}的方向使劲挥手。",
    a: { label: "也热情地挥手回去。", out: [
      { text: "那人走近了，原来是在跟{名字}身后的朋友打招呼。三个人尴尬地笑了笑。", say: "嗯……我挥手是在热身。", mood: { name: "挥错了手", emo: "embarrassed", pts: 4, min: 150 } },
      { text: "那人真的是在跟{名字}打招呼。上次在书店坐在旁边的人，居然还记得{名字}。", say: "被人记住，真好啊。", mood: { name: "被陌生人记住", emo: "happy", pts: 4, min: 240 }, need: { social: 15 } } ] },
    b: { label: "回头看看身后。", out: [
      { text: "身后果然有人在挥手回应。{名字}暗暗庆幸自己没有自作多情。", say: "好险，差点就挥了。", mood: { name: "躲过一次尴尬", emo: "tense", pts: 2, min: 120 } },
      { text: "身后没有人。等{名字}转回来，那人已经走了，留下{名字}一个人纳闷。", say: "那到底是在叫谁呢？", mood: { name: "错过一次招手", emo: "sad", pts: 3, min: 150 } } ] } },
  { n: 346, title: "摇摇车", at: "mall", when: "bored|goodMood",
    text: "超市门口有一辆投币摇摇车，做成小火车的样子，现在没有小孩在坐。",
    a: { label: "坐上去摇一回。", out: [
      { text: "摇摇车唱起了儿歌，{名字}跟着摇头晃脑，路过的小孩羡慕地看着。", say: "这是大人的特权！", mood: { name: "坐上了摇摇车", emo: "playful", pts: 4, min: 180 }, need: { fun: 12 } },
      { text: "{名字}坐进去才发现卡住了，摇摇车唱完一整首歌，{名字}还没出来。", say: "谁、谁来拉我一把……", mood: { name: "卡在摇摇车里", emo: "scared", pts: 3, min: 120 } } ] },
    b: { label: "让给路过的小孩。", out: [
      { text: "{名字}帮小孩投了币，小孩在车上一边摇一边冲{名字}挥手，像火车出站。", say: "一路顺风，小乘客！", mood: { name: "送小孩出站", emo: "inspired", pts: 2, min: 150 }, need: { social: 6 } },
      { text: "小孩坐上去没多久就哭着要下来，说火车太快了。家长和{名字}一起憋笑。", say: "摇摇车，速度惊人。", mood: { name: "憋笑憋到肚疼", emo: "tense", pts: 3, min: 120 } } ] } },
  { n: 347, title: "哪一队最快", at: "mall", when: "",
    text: "超市只开了三个收银台，三条队看起来一样长。{名字}得选一个。",
    a: { label: "选人最少的那队。", out: [
      { text: "{名字}这队前面的大叔掏出一整本优惠券，一张一张地核对。", say: "我选的是最慢的队。", mood: { name: "排到优惠券大叔", emo: "angry", pts: 3, min: 150 } },
      { text: "{名字}这队嗖嗖地往前走，回头看另外两队一动不动，心里偷偷得意。", say: "眼光，这就叫眼光。", mood: { name: "选对了队伍", emo: "confident", pts: 3, min: 150 } } ] },
    b: { label: "选收银员动作最快的那队。", out: [
      { text: "收银员扫码像在弹钢琴，{名字}还没反应过来就已经结完账了。", say: "这速度，看呆了。", mood: { name: "收银员神速", emo: "dazed", pts: 2, min: 120 } },
      { text: "排到一半，那个收银员换班了，新来的阿姨刚学会用机器。", say: "我们一起慢慢来吧。", mood: { name: "收银员换班", emo: "bored", pts: 3, min: 120 } } ] } },
  { n: 348, title: "夹子的咔嚓声", at: "mall", when: "",
    text: "面包店里，{名字}注意到每个拿起夹子的人，都会先咔嚓咔嚓夹两下空气。",
    a: { label: "也咔嚓两下。", out: [
      { text: "{名字}咔嚓了两下，旁边的人也咔嚓了两下，像在对暗号。", say: "咔嚓咔嚓，接头成功。", mood: { name: "面包店暗号", emo: "playful", pts: 3, min: 150 } },
      { text: "咔嚓得太开心，{名字}不小心把一个奶油面包夹扁了，只好买下来。", say: "对不起，我负责到底。", mood: { name: "夹扁了面包", emo: "embarrassed", pts: 2, min: 120 }, need: { hunger: 8 } } ] },
    b: { label: "忍住不咔嚓。", out: [
      { text: "{名字}直接夹起面包，觉得自己是全店最冷静的人。", say: "我，不随波逐流。", mood: { name: "忍住了咔嚓", emo: "focused", pts: 3, min: 150 } },
      { text: "忍了五分钟，手越来越痒，最后{名字}趁没人看的时候连咔嚓了十下。", say: "憋坏了，咔嚓咔嚓！", mood: { name: "终于咔嚓了", emo: "energized", pts: 2, min: 120 } } ] } },
  { n: 349, title: "两只手不够用", at: "mall", when: "goodMood",
    text: "{名字}今天心情不错，一口气买了好多东西，现在两只手各拎着四个袋子。",
    a: { label: "坚持全部拎着走。", out: [
      { text: "{名字}像举重选手一样稳步前进，路过的人纷纷让路。", say: "让一让，力士来了！", mood: { name: "大力士附体", emo: "focused", pts: 3, min: 150 }, need: { energy: -10 } },
      { text: "走到一半，一个袋子的提手断了，橘子滚了一走廊，好几个陌生人帮着一起捡。", say: "谢谢大家，橘子都在吗？", mood: { name: "橘子满地滚", emo: "tense", pts: 3, min: 120 }, need: { social: 6, energy: -6 } } ] },
    b: { label: "借一辆购物车推着。", out: [
      { text: "{名字}推着购物车，轻轻松松，还有余力再买一杯奶茶。", say: "轻松，还能再逛！", mood: { name: "推车好轻松", emo: "energized", pts: 3, min: 150 } },
      { text: "推到门口才发现购物车不能推出商场，{名字}只好又把袋子全拎了起来。", say: "绕了一圈又回到原点。", mood: { name: "推车出不了门", emo: "sad", pts: 2, min: 120 }, need: { energy: -6 } } ] } },
  { n: 350, title: "复读机喇叭", at: "mall", when: "",
    text: "地摊上的小喇叭一直在循环：“走过路过不要错过！”{名字}已经路过第三次了。",
    a: { label: "停下来看看。", out: [
      { text: "{名字}在一堆小东西里翻出一双印着小鸭子的袜子，老板说：“你是今天第一个停下来的。”", say: "原来喇叭等的是我。", mood: { name: "淘到小鸭袜子", emo: "flirty", pts: 3, min: 180 } },
      { text: "老板见有人停下，激动地关掉喇叭亲自吆喝，声音比喇叭还大，{名字}被震得后退了两步。", say: "老板，您比喇叭还响！", mood: { name: "被吆喝震住", emo: "scared", pts: 2, min: 120 } } ] },
    b: { label: "跟着喇叭一起念。", out: [
      { text: "{名字}跟着念了几遍，一整天脑子里都在循环：“走过路过不要错过！”", say: "停不下来了！", mood: { name: "脑子被洗脑", emo: "uncomfortable", pts: 2, min: 150 } },
      { text: "老板乐了，把喇叭递给{名字}，让{名字}录一段新的。现在整条地摊都在播{名字}的声音。", say: "我的声音成了招牌！", mood: { name: "给地摊录喇叭", emo: "flirty", pts: 4, min: 200 }, need: { social: 10, fun: 8 } } ] } },
  { n: 351, title: "海鸥的凝视", at: "beach", when: "hungry",
    text: "{名字}刚掏出一块小面包，一只海鸥就落在了三步远的栏杆上，一动不动地盯着。",
    a: { label: "背过身去快快吃完。", out: [
      { text: "{名字}三口吃完了面包。海鸥失望地扭过头，好像在记下这个名字。", say: "吃完了，你记仇也没用。", mood: { name: "护住了面包", emo: "confident", pts: 3, min: 150 }, need: { hunger: 10 } },
      { text: "{名字}刚转过身，第二只海鸥从另一边落下。前后夹击，面包少了一半。", say: "你们居然还有战术！", mood: { name: "被海鸥包抄", emo: "angry", pts: 3, min: 120 }, need: { hunger: 5 } } ] },
    b: { label: "掰一小块当过路费。", out: [
      { text: "海鸥叼走面包，在栏杆上多站了一会儿，像是在陪{名字}吃饭。", say: "好啦，我们算一起吃过饭了。", mood: { name: "和海鸥共进午餐", emo: "playful", pts: 3, min: 180 }, need: { hunger: 8, social: 5 } },
      { text: "一小块面包引来了半个码头的海鸥。{名字}被叫声团团围住，只好把整块都交了出去。", say: "我只是想交个过路费……", mood: { name: "被海鸥打劫", emo: "tense", pts: 3, min: 150 }, need: { hunger: -5 } } ] } },
  { n: 352, title: "清点货物", at: "beach", when: "",
    text: "远处那艘集装箱船慢慢挪着，船上的箱子一层一层，五颜六色。",
    a: { label: "认真数一数有多少个。", out: [
      { text: "{名字}数到两百三十七的时候，船正好开进了一团雾里。这个数字被庄严地记了下来。", say: "二百三十七，误差不大。", mood: { name: "数完了一艘船", emo: "focused", pts: 3, min: 180 } },
      { text: "数到一半，{名字}忘了自己数的是红色的还是全部，只好从头再来，然后又忘了。", say: "等等，我数到哪儿了……", mood: { name: "数箱子数晕了", emo: "dazed", pts: 3, min: 150 } } ] },
    b: { label: "猜猜箱子里装着什么。", out: [
      { text: "{名字}决定其中一个箱子里全是枕头，另一个全是橡皮鸭。这样一想，整艘船都软乎乎的。", say: "那艘船肯定很好睡。", mood: { name: "一船的橡皮鸭", emo: "inspired", pts: 3, min: 180 }, need: { fun: 8 } },
      { text: "想着想着，{名字}开始担心有个箱子里装着一只迷路的猫。担心了整整一下午。", say: "猫猫，你要是在里面就叫一声。", mood: { name: "担心箱子里有猫", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 353, title: "快艇过境", at: "beach", when: "",
    text: "一艘快艇呼啸着从码头边擦过，后面拖着一道白白的浪，正朝木板这边涌来。",
    a: { label: "站在原地迎接它。", out: [
      { text: "浪拍上码头，只打湿了{名字}的鞋尖。{名字}觉得自己刚刚和大海打了个平手。", say: "大海，这局算平局。", mood: { name: "和浪打成平手", emo: "confident", pts: 3, min: 150 } },
      { text: "浪比看上去高得多。{名字}从头到脚湿透了，还尝到了一口咸味。", say: "噗，好咸……", mood: { name: "被浪拍了一脸", emo: "embarrassed", pts: 3, min: 150 }, need: { hygiene: -10 } } ] },
    b: { label: "往后跳三步。", out: [
      { text: "{名字}轻盈地躲开了，浪只拍到了空空的木板。跳得太漂亮，自己都想鼓掌。", say: "身手还不错嘛我！", mood: { name: "完美闪避", emo: "energized", pts: 3, min: 120 }, need: { energy: -3 } },
      { text: "后退第三步时踩到一块湿木板，{名字}一屁股坐下。浪倒是没碰到{她}。", say: "躲过了浪，没躲过地板。", mood: { name: "摔了个屁股墩", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 354, title: "临时助手", at: "beach", when: "",
    text: "栏杆边钓鱼的大叔要去买瓶水，问{名字}能不能帮忙看一下鱼竿。",
    a: { label: "郑重地接过鱼竿。", out: [
      { text: "大叔刚走，浮漂就沉了下去。{名字}手忙脚乱地拉起一条小鱼，大叔回来时激动得请{她}喝了水。", say: "我、我钓到啦！", mood: { name: "替人钓到鱼", emo: "energized", pts: 4, min: 210 }, need: { social: 10, fun: 10 } },
      { text: "{名字}盯着浮漂看了二十分钟，什么都没发生。大叔回来后说，这已经是今天最好的成绩了。", say: "原来零条也算成绩。", mood: { name: "盯浮漂盯困了", emo: "bored", pts: 2, min: 120 }, need: { social: 5 } } ] },
    b: { label: "推荐大叔带着鱼竿去。", out: [
      { text: "大叔想了想，觉得有道理，扛着鱼竿去买了水。路上还碰到一个老朋友，聊了很久。", say: "看，我的建议多好。", mood: { name: "给大叔出主意", emo: "playful", pts: 2, min: 120 } },
      { text: "大叔走后，鱼竿留下的那个位置正好有鱼跳出水面。{名字}有点后悔，但也不好说什么。", say: "鱼，你早不跳晚不跳。", mood: { name: "错过一条鱼", emo: "uncomfortable", pts: 2, min: 120 } } ] } },
  { n: 355, title: "试穿救生圈", at: "beach", when: "",
    text: "栏杆上挂着一个红白相间的救生圈，大小看起来刚好能套住{名字}。",
    a: { label: "取下来套一套。", out: [
      { text: "大小正合适。{名字}套着救生圈在码头上走了一圈，感觉自己随时可以去远航。", say: "船长{名字}，准备出海！", mood: { name: "当了一回船长", emo: "playful", pts: 4, min: 180 }, need: { fun: 10 } },
      { text: "救生圈卡在了腰上，上不去也下不来。{名字}只好原地扭了五分钟，正好有人路过。", say: "我……我在做安全演练。", mood: { name: "被救生圈卡住", emo: "embarrassed", pts: 4, min: 180 } } ] },
    b: { label: "这是救命用的，不能乱动。", out: [
      { text: "{名字}伸手把救生圈挂得更正了一点，感觉自己为海上安全做出了贡献。", say: "挂正了，安心。", mood: { name: "守护了救生圈", emo: "confident", pts: 2, min: 120 } },
      { text: "{名字}一整天都在想套上去是什么感觉。这个问题比救生圈还要沉。", say: "就套一下也不行吗……", mood: { name: "没试成救生圈", emo: "bored", pts: 2, min: 120 } } ] } },
  { n: 356, title: "王座", at: "beach", when: "",
    text: "码头边有一根矮矮的铁系缆桩，顶上圆圆的，看起来很像一张为{名字}准备的椅子。",
    a: { label: "坐上去俯瞰大海。", out: [
      { text: "{名字}端坐在系缆桩上，海风吹过，几只海鸥在面前排成一排。像是在上朝。", say: "众卿平身。", mood: { name: "坐上海的王座", emo: "confident", pts: 4, min: 210 } },
      { text: "系缆桩被太阳晒得滚烫。{名字}坐下去的一瞬间就弹了起来，动作比海鸥起飞还快。", say: "烫烫烫烫！", mood: { name: "王座太烫了", emo: "uncomfortable", pts: 3, min: 120 } } ] },
    b: { label: "把它当成船来绑。", out: [
      { text: "{名字}捡了根绳子把自己的包系在桩上。包在风里轻轻晃，像一艘停好的小船。", say: "我的船靠岸啦。", mood: { name: "停好了一艘包", emo: "playful", pts: 3, min: 150 } },
      { text: "绳结打得太牢，{名字}花了半个钟头才把包解下来。海鸥全程围观。", say: "这结是谁打的！哦，是我。", mood: { name: "解不开自己的结", emo: "angry", pts: 2, min: 120 }, need: { energy: -5 } } ] } },
  { n: 357, title: "点灯人", at: "beach", when: "evening",
    text: "天快黑了，码头上的路灯从岸边开始，一盏一盏地亮过来。",
    a: { label: "跟着灯往前走。", out: [
      { text: "{名字}每走到一盏灯下，它就正好亮起来。走到尽头时，{名字}觉得这些灯都是自己点的。", say: "今天的灯，是我点的。", mood: { name: "当了一回点灯人", emo: "inspired", pts: 4, min: 240 } },
      { text: "走到最后一盏时，它闪了两下，没亮。{名字}站在黑影里，觉得被灯冷落了。", say: "唯独不给我亮吗……", mood: { name: "被路灯冷落", emo: "sad", pts: 2, min: 120 } } ] },
    b: { label: "对着亮起的灯许个愿。", out: [
      { text: "{名字}许完愿，海上正好有一艘船亮起了灯回应。这个愿望应该算是被收到了。", say: "收到了吧？收到就好。", mood: { name: "愿望被收到", emo: "happy", pts: 3, min: 210 } },
      { text: "{名字}许了太多愿，最后一个还没想好，灯已经全亮完了。", say: "等等，我还没说完呢！", mood: { name: "愿望没许完", emo: "tense", pts: 2, min: 90 } } ] } },
  { n: 358, title: "木板缝里的光", at: "beach", when: "",
    text: "码头的两块木板之间，有个东西在太阳下一闪一闪。",
    a: { label: "趴下来伸手去抠。", out: [
      { text: "抠出一枚硬币，还是很少见的那种年份。{名字}把它举起来对着太阳看了半天。", say: "大海给我发零花钱啦。", mood: { name: "码头捡到硬币", emo: "happy", pts: 3, min: 180 } },
      { text: "抠了半天，抠出来的是一个瓶盖。刚站起来，又看到另一条缝在闪。", say: "这码头在耍我吧。", mood: { name: "被瓶盖骗了", emo: "dazed", pts: 2, min: 120 } } ] },
    b: { label: "让它继续闪着吧。", out: [
      { text: "{名字}觉得码头也需要一点小装饰，就当是给木板戴了个耳环。", say: "码头今天也很好看。", mood: { name: "给码头留首饰", emo: "playful", pts: 2, min: 120 } },
      { text: "一个路过的小孩趴下来，三秒钟就抠出了硬币，冲{名字}晃了晃。", say: "……其实我也看到了。", mood: { name: "硬币被抢先了", emo: "uncomfortable", pts: 2, min: 120 } } ] } },
  { n: 359, title: "雨中码头", at: "beach", when: "rain",
    text: "雨点落在海面上，密密麻麻地起了无数个小圈。码头上已经没什么人了。",
    a: { label: "撑着伞多看一会儿。", out: [
      { text: "整片海像在轻轻地冒泡。{名字}听着雨打在伞上的声音，心里安静得出奇。", say: "海在下雨，我在听。", mood: { name: "听海上的雨", emo: "focused", pts: 4, min: 240 } },
      { text: "一阵风把伞翻成了一朵花。{名字}抓着伞柄站在雨里，和花一起湿透了。", say: "伞……开花了……", mood: { name: "伞被吹翻了", emo: "sad", pts: 3, min: 150 }, need: { hygiene: -8 } } ] },
    b: { label: "跑到路灯下躲雨。", out: [
      { text: "路灯下居然站着一只同样在躲雨的海鸥。一人一鸟谁也没说话，像两个等车的乘客。", say: "你也没带伞啊。", mood: { name: "和海鸥一起躲雨", emo: "playful", pts: 3, min: 180 } },
      { text: "路灯根本挡不住雨。{名字}站了半天才想明白这件事。", say: "灯又不是伞，我在想什么。", mood: { name: "躲雨躲了个寂寞", emo: "dazed", pts: 2, min: 120 }, need: { hygiene: -5 } } ] } },
  { n: 360, title: "雾里的汽笛", at: "beach", when: "morning",
    text: "清晨海上起了大雾，什么都看不清。雾的深处传来一声长长的汽笛。",
    a: { label: "学着汽笛叫一声。", out: [
      { text: "过了一会儿，雾里又响起一声汽笛，好像在回答。{名字}觉得自己和一艘船说上了话。", say: "早上好呀，大船！", mood: { name: "和大船对话", emo: "inspired", pts: 4, min: 240 }, need: { social: 5 } },
      { text: "{名字}叫得太用力，岸上的一位晨练阿姨被吓了一跳，回头看了{她}很久。", say: "我、我不是船……", mood: { name: "吓到晨练阿姨", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "安静地等雾散去。", out: [
      { text: "雾一点点退开，那艘船就在不远处，比想象中近得多。{名字}屏住了呼吸。", say: "哇，原来你一直在这儿。", mood: { name: "雾散见大船", emo: "dazed", pts: 3, min: 180 } },
      { text: "等了很久，雾一点也没散。{名字}站在白茫茫里，越来越觉得自己是在云上。", say: "我是不是飘起来了？", mood: { name: "站在云里", emo: "scared", pts: 2, min: 120 } } ] } },
  { n: 361, title: "海上来信", at: "beach", when: "",
    text: "一只玻璃瓶在码头边的水里一浮一沉，里面好像卷着一张纸。",
    a: { label: "趴在边上把它捞起来。", out: [
      { text: "纸上写着：“不管谁捡到，祝你今天顺利。”{名字}觉得今天确实挺顺利的。", say: "收到啦，谢谢陌生人。", mood: { name: "收到漂流瓶", emo: "happy", pts: 4, min: 240 }, need: { social: 5 } },
      { text: "{名字}捞了五次没捞着，第六次瓶子自己漂走了，好像嫌{她}太慢。", say: "喂，信还没送到呢！", mood: { name: "信被海收回了", emo: "sad", pts: 2, min: 120 } } ] },
    b: { label: "让它继续去找收信人。", out: [
      { text: "{名字}朝瓶子挥挥手，目送它漂远。说不定它要去的地方，正有人在等。", say: "一路顺风，小瓶子。", mood: { name: "送走了漂流瓶", emo: "inspired", pts: 3, min: 180 } },
      { text: "瓶子漂了一圈，又漂回{名字}脚下。它看起来非常坚持。", say: "好吧，看来就是给我的。", mood: { name: "被瓶子选中", emo: "dazed", pts: 3, min: 150 } } ] } },
  { n: 362, title: "喂鸟小队", at: "beach", when: "",
    text: "一个小孩拿着一袋面包屑跑过来，问{名字}要不要一起喂海鸥。",
    a: { label: "加入喂鸟小队。", out: [
      { text: "两人一把一把地撒，海鸥在空中接得又准又漂亮。小孩说{名字}是今天最好的队友。", say: "最好的队友，收到！", mood: { name: "当了好队友", emo: "energized", pts: 4, min: 180 }, need: { social: 10, fun: 8 } },
      { text: "{名字}撒得太近，海鸥直接从{她}手上叼。小孩笑得蹲在地上起不来。", say: "别笑了，我手还在呢！", mood: { name: "手被海鸥啄了", emo: "scared", pts: 3, min: 150 }, need: { social: 5 } } ] },
    b: { label: "在旁边当解说员。", out: [
      { text: "{名字}给每只海鸥都起了名字，解说得有声有色。小孩听得都忘了撒面包。", say: "三号选手，空中接球！", mood: { name: "海鸥比赛解说", emo: "playful", pts: 4, min: 180 }, need: { social: 8, fun: 10 } },
      { text: "{名字}解说到一半，发现所有海鸥长得一模一样，根本分不清谁是谁。", say: "呃，刚才那位是……也是它。", mood: { name: "认不清海鸥", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 363, title: "今日渔获", at: "beach", when: "",
    text: "旁边钓鱼的大叔猛地一拉竿，拉上来的是一只湿漉漉的旧靴子。",
    a: { label: "安慰大叔。", out: [
      { text: "{名字}说这一定是一只很稀有的靴子。大叔想了想，认真地把它摆在了桶旁边。", say: "这可是限量款。", mood: { name: "安慰了大叔", emo: "confident", pts: 3, min: 150 }, need: { social: 8 } },
      { text: "{名字}刚开口，大叔又拉上来另一只。两人对视了很久，谁都不知道该说什么。", say: "……凑成一双了呢。", mood: { name: "见证一双靴子", emo: "dazed", pts: 3, min: 150 } } ] },
    b: { label: "憋住别笑。", out: [
      { text: "{名字}憋得满脸通红，大叔自己先笑了出来。两个人笑得栏杆都在抖。", say: "哈哈哈，对不起！", mood: { name: "和大叔一起笑", emo: "playful", pts: 4, min: 180 }, need: { social: 10, fun: 8 } },
      { text: "{名字}没憋住，“噗”地笑出了声。大叔默默把靴子放进桶里，一下午没理{她}。", say: "大叔，我不是故意的……", mood: { name: "笑出声了", emo: "embarrassed", pts: 3, min: 150 } } ] } },
  { n: 364, title: "打水漂", at: "beach", when: "",
    text: "{名字}在码头边捡到一块扁扁的小石头，大小正好适合打水漂。",
    a: { label: "全力一掷。", out: [
      { text: "石头在水面上跳了七下！{名字}数得清清楚楚，连海鸥都停下来看了一眼。", say: "七下！你们都看到了吧！", mood: { name: "打出七个水漂", emo: "confident", pts: 4, min: 210 }, need: { fun: 10 } },
      { text: "石头一下都没跳，“咚”地直接沉了。声音很响，很诚实。", say: "……它是想去海底看看。", mood: { name: "石头直接沉了", emo: "embarrassed", pts: 2, min: 120 } } ] },
    b: { label: "先研究一下角度。", out: [
      { text: "{名字}比划了很久，算好风向和角度，扔出了一个稳稳的五连跳。科学的胜利。", say: "一切尽在计算之中。", mood: { name: "科学打水漂", emo: "focused", pts: 4, min: 180 } },
      { text: "研究得太久，太阳都偏了。{名字}最后决定把石头带回家，留着下次研究。", say: "今天先研究到这里。", mood: { name: "研究到天黑", emo: "bored", pts: 2, min: 120 } } ] } },
  { n: 365, title: "请帮我们拍张照", at: "beach", when: "evening|clear",
    text: "一对年轻人举着手机走过来，礼貌地问{名字}能不能帮他们和夕阳合个影。",
    a: { label: "接过手机认真拍。", out: [
      { text: "{名字}蹲下、侧身、找角度，拍出来的照片里，夕阳正好落在两个人中间。两人连连道谢。", say: "这张，绝对能当头像。", mood: { name: "拍出好照片", emo: "inspired", pts: 4, min: 210 }, need: { social: 10 } },
      { text: "拍完一看，每张都只拍到了两个人的下巴和一大片天空。", say: "天空……拍得很清楚。", mood: { name: "拍糊了别人", emo: "embarrassed", pts: 3, min: 150 }, need: { social: 5 } } ] },
    b: { label: "建议他们换个姿势。", out: [
      { text: "{名字}提议两人一起比个心，把夕阳框在中间。两人试了一下，害羞又开心。", say: "很好，夕阳被你们装起来了。", mood: { name: "当了摄影指导", emo: "flirty", pts: 3, min: 180 }, need: { social: 8 } },
      { text: "{名字}指导得太投入，夕阳已经沉下去了。三个人对着黑乎乎的海面沉默了片刻。", say: "呃，月亮也挺好看的。", mood: { name: "错过了夕阳", emo: "uncomfortable", pts: 3, min: 150 } } ] } },
  { n: 366, title: "瞪眼比赛", at: "beach", when: "",
    text: "一只海鸥站在路灯顶上，歪着头盯着{名字}，一眨不眨。",
    a: { label: "接受挑战，瞪回去。", out: [
      { text: "瞪到眼睛发酸的时候，海鸥先扭开了头。{名字}在码头上赢下了一场无声的比赛。", say: "赢了！海鸥也不过如此。", mood: { name: "赢了海鸥", emo: "confident", pts: 4, min: 180 } },
      { text: "海鸥连眨都没眨一下。{名字}眼泪都快瞪出来了，最后只好认输。", say: "你是不是没有眼皮啊！", mood: { name: "输给了海鸥", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "假装没看见。", out: [
      { text: "{名字}若无其事地看海，海鸥等了一会儿，觉得没意思，飞走了。", say: "不理你，你就没招了。", mood: { name: "冷处理海鸥", emo: "playful", pts: 2, min: 120 } },
      { text: "{名字}越是不看，越觉得后背发毛。一回头，海鸥已经飞到了离{她}一米的栏杆上。", say: "你什么时候过来的！", mood: { name: "被海鸥逼近", emo: "scared", pts: 3, min: 150 } } ] } },
  { n: 367, title: "海上的星星", at: "beach", when: "night",
    text: "夜里的海是黑的，远处的船灯和天上的星星连在一起，分不清哪些在天上。",
    a: { label: "认真分辨哪些是星星。", out: [
      { text: "{名字}发现有一颗“星星”在慢慢地动，原来是一艘船。分清的那一刻，海和天又分开了。", say: "抓到你了，假星星。", mood: { name: "分清了星和船", emo: "focused", pts: 3, min: 180 } },
      { text: "看着看着，{名字}开始觉得码头也在慢慢漂，自己正坐在一颗星星上。", say: "我是不是漂到天上了……", mood: { name: "分不清天和海", emo: "dazed", pts: 4, min: 210 } } ] },
    b: { label: "把它们都当成星星。", out: [
      { text: "{名字}对着一颗会动的“星星”许了个愿。它慢慢开远了，像是带着愿望出发了。", say: "星星，帮我送一下愿望。", mood: { name: "对船灯许愿", emo: "inspired", pts: 3, min: 210 } },
      { text: "一颗“星星”突然鸣了一声汽笛。{名字}吓得往后一缩。", say: "星星怎么还会叫！", mood: { name: "被星星吓到", emo: "scared", pts: 2, min: 120 } } ] } },
  { n: 368, title: "海风很有想法", at: "beach", when: "winter",
    text: "冬天的海风又冷又硬，一阵比一阵大，{名字}的帽子在头上开始摇摇晃晃。",
    a: { label: "双手按住帽子。", out: [
      { text: "{名字}牢牢按住帽子，顶着风站了好一会儿，觉得自己像一座小小的灯塔。", say: "我就是这里的灯塔。", mood: { name: "顶风站稳了", emo: "energized", pts: 3, min: 150 }, need: { energy: -5 } },
      { text: "帽子是保住了，围巾却被吹走了，挂在了一根系缆桩上。", say: "围巾，你别想不开！", mood: { name: "围巾被吹走", emo: "tense", pts: 3, min: 120 } } ] },
    b: { label: "转身背对着风。", out: [
      { text: "背过身去，风就从后面推着{名字}往岸上走。{名字}顺水推舟，回去喝了杯热的。", say: "好的风，我这就回家。", mood: { name: "被风送回家", emo: "playful", pts: 2, min: 120 }, need: { energy: 5 } },
      { text: "风从后面把帽子掀起来，正好盖住了{名字}的眼睛。{名字}原地转了三圈才找到方向。", say: "谁关的灯！", mood: { name: "帽子盖住眼睛", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 369, title: "脚丫度假", at: "beach", when: "summer",
    text: "夏天的午后，码头尽头的木板离海面不高，脚垂下去刚好能碰到水。",
    a: { label: "脱了鞋把脚放下去。", out: [
      { text: "凉凉的海水一下一下地拍着脚背。{名字}觉得自己的脚丫正在度一个很好的假。", say: "脚丫子，玩得开心哦。", mood: { name: "脚丫在度假", emo: "happy", pts: 4, min: 240 }, need: { fun: 10, energy: 5 } },
      { text: "一缕海草缠住了{名字}的脚趾，滑溜溜的。{名字}“嗖”地把腿收了回来。", say: "什么东西摸我！", mood: { name: "被海草缠脚", emo: "scared", pts: 3, min: 120 } } ] },
    b: { label: "坐着看就好。", out: [
      { text: "{名字}盘腿坐着，看阳光在海面上碎成一片一片。看得很安静，很久。", say: "今天的海，亮晶晶。", mood: { name: "看海面闪光", emo: "focused", pts: 3, min: 180 } },
      { text: "旁边一个小孩把脚放进水里，开心得大叫。{名字}看着，心里痒痒的。", say: "……要不，就放一只脚？", mood: { name: "看别人玩水", emo: "bored", pts: 2, min: 120 } } ] } },
  { n: 370, title: "横行的访客", at: "beach", when: "",
    text: "一只指甲盖大的小螃蟹爬上了码头，正举着两只钳子，横着往{名字}这边走。",
    a: { label: "蹲下来跟它打招呼。", out: [
      { text: "小螃蟹停下来，朝{名字}举了举钳子，然后横着走掉了。这应该算是回礼。", say: "你好呀，螃蟹先生。", mood: { name: "螃蟹回了礼", emo: "playful", pts: 3, min: 150 }, need: { fun: 5 } },
      { text: "{名字}凑得太近，螃蟹一钳子夹住了{她}的鞋带，死活不肯松。", say: "这是鞋带，不是面条！", mood: { name: "鞋带被夹住", emo: "tense", pts: 3, min: 120 } } ] },
    b: { label: "帮它回到海里。", out: [
      { text: "{名字}用一片叶子把螃蟹送到边上，它“扑通”一声跳回了海里，干脆利落。", say: "回家路上小心哦。", mood: { name: "送螃蟹回家", emo: "confident", pts: 3, min: 150 } },
      { text: "螃蟹不肯上叶子，绕着{名字}横着跑了好几圈，好像在跳舞。", say: "你到底想去哪儿嘛。", mood: { name: "被螃蟹绕晕", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 371, title: "热情的船长", at: "beach", when: "",
    text: "快艇慢慢开过码头，开船的人朝{名字}用力地挥手，笑得特别灿烂。",
    a: { label: "也用力挥回去。", out: [
      { text: "开船的人又按了两声喇叭回应。{名字}觉得自己今天在海上有了一个朋友。", say: "海上朋友，再见啦！", mood: { name: "交了海上朋友", emo: "flirty", pts: 3, min: 180 }, need: { social: 10 } },
      { text: "{名字}挥完才发现，人家是在跟{她}身后的钓鱼大叔打招呼。", say: "我……在赶海鸥。", mood: { name: "挥错了手", emo: "embarrassed", pts: 4, min: 180 } } ] },
    b: { label: "假装在看别处。", out: [
      { text: "快艇开走了，{名字}心里偷偷挥了一下手。没人知道，但{名字}自己知道。", say: "心里挥过了，不算失礼。" },
      { text: "开船的人以为{名字}没看见，绕回来又挥了一次，还更用力了。", say: "好好好，我看见了！", mood: { name: "被热情追着跑", emo: "uncomfortable", pts: 2, min: 120 }, need: { social: 5 } } ] } },
  { n: 372, title: "向大海喊话", at: "beach", when: "",
    text: "码头尽头一个人都没有，只有海和风。{名字}突然很想对着海喊点什么。",
    a: { label: "大声喊出来。", out: [
      { text: "{名字}喊了一声“你好——”，风把声音带得很远很远。喊完之后，整个人都轻了。", say: "大海，你听到了吧！", mood: { name: "对大海喊过了", emo: "energized", pts: 4, min: 210 }, need: { fun: 8 } },
      { text: "刚喊出口，下面停着的一条小船里坐起来一个人，迷迷糊糊地问：“谁叫我？”", say: "没、没叫你，你继续睡。", mood: { name: "喊醒了陌生人", emo: "embarrassed", pts: 4, min: 180 } } ] },
    b: { label: "小声说给海听。", out: [
      { text: "{名字}小声说了一句心里话。一个浪正好拍上来，好像在说“知道了”。", say: "嗯，就我们俩知道。", mood: { name: "跟海说了悄悄话", emo: "inspired", pts: 3, min: 210 } },
      { text: "说得太小声，连{名字}自己都没听清。只好又想了一遍刚才想说什么。", say: "刚才我说了啥来着？", mood: { name: "悄悄话太悄悄", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 373, title: "大狗的问候", at: "beach", when: "",
    text: "一个遛狗的人走上码头，那只大狗显然刚从海里游完泳，浑身湿透，正兴奋地朝{名字}奔来。",
    a: { label: "张开双手迎接。", out: [
      { text: "大狗扑进{名字}怀里，然后开始甩水。{名字}湿了一身，可大狗的笑容太真诚了。", say: "好吧，你值得一个拥抱。", mood: { name: "被大狗拥抱", emo: "happy", pts: 4, min: 210 }, need: { social: 10, hygiene: -10 } },
      { text: "大狗在最后一秒急刹车，在{名字}面前甩了个干干净净，然后转身跑开了。", say: "专门过来甩给我看的？", mood: { name: "被狗甩了一身", emo: "angry", pts: 2, min: 120 }, need: { hygiene: -10 } } ] },
    b: { label: "侧身闪到栏杆后面。", out: [
      { text: "大狗扑了个空，回头看{名字}的眼神有点委屈。主人连声道歉，还让狗跟{她}握了握爪。", say: "握手可以，甩水不行。", mood: { name: "和大狗握了手", emo: "playful", pts: 3, min: 150 }, need: { social: 8 } },
      { text: "大狗以为{名字}在玩捉迷藏，兴奋地绕着栏杆追了三圈。", say: "不是游戏！不是游戏啊！", mood: { name: "被大狗追着跑", emo: "tense", pts: 3, min: 120 }, need: { energy: -8 } } ] } },
  { n: 374, title: "毛线时间", at: "beach", when: "",
    text: "长椅上坐着一位织毛衣的奶奶，毛线团滚到了{名字}脚边。奶奶笑着招招手。",
    a: { label: "帮奶奶撑着毛线。", out: [
      { text: "{名字}两手撑着毛线，奶奶一边绕一边讲年轻时在海边的事。一个下午过得又暖又慢。", say: "奶奶，再讲一个嘛。", mood: { name: "听奶奶讲故事", emo: "focused", pts: 3, min: 240 }, need: { social: 15 } },
      { text: "{名字}撑着撑着走了神，毛线在手上缠成了一个巨大的结。奶奶看了半天，说这是新花样。", say: "奶奶，这个花样叫“迷路”。", mood: { name: "把毛线缠乱了", emo: "embarrassed", pts: 3, min: 150 }, need: { social: 10 } } ] },
    b: { label: "把毛线团捡起来还回去。", out: [
      { text: "奶奶从袋子里摸出一颗糖塞给{名字}。是那种很久没见过的老式水果糖。", say: "谢谢奶奶，好甜。", mood: { name: "奶奶给的糖", emo: "happy", pts: 3, min: 180 }, need: { hunger: 3, social: 5 } },
      { text: "{名字}一弯腰，毛线团又往前滚了一截，一直滚到码头边上才停下。", say: "毛线团，你别跑了！", mood: { name: "追毛线团", emo: "tense", pts: 2, min: 90 }, need: { energy: -5 } } ] } },
  { n: 375, title: "画中人", at: "beach", when: "",
    text: "码头上有人支着画架在画海。画家抬头看了看{名字}，问{她}能不能站在栏杆边别动。",
    a: { label: "站好，当一回模特。", out: [
      { text: "画完一看，画里的海边站着一个小小的身影，看起来很安静。画家说这是今天的点睛之笔。", say: "我在画里，好像很文艺。", mood: { name: "成了画中人", emo: "flirty", pts: 4, min: 240 }, need: { social: 8 } },
      { text: "一站就是四十分钟，{名字}腿都麻了。画家却说，还得再画一会儿海鸥。", say: "海鸥能不能快点画完……", mood: { name: "站得腿发麻", emo: "uncomfortable", pts: 3, min: 150 }, need: { energy: -10 } } ] },
    b: { label: "说自己不太会站着不动。", out: [
      { text: "画家笑着点头，转而给了{名字}一支笔，让{她}在角落里画一只海鸥。", say: "这只海鸥，是我画的。", mood: { name: "画了一只海鸥", emo: "inspired", pts: 4, min: 210 }, need: { fun: 10 } },
      { text: "画家有点失望，最后把{名字}画成了一个远远的小点。勉强还能认出来。", say: "那个点……还挺像我的。" } ] } },
  { n: 376, title: "越狱", at: "beach", when: "",
    text: "大叔的水桶里，一条鱼突然奋力一跳，“啪”地落在了木板上，正扑腾着往边上蹦。",
    a: { label: "扑过去抓住它。", out: [
      { text: "{名字}一个飞扑，双手稳稳按住了鱼。大叔竖起大拇指，说要给{她}发一枚抓鱼勋章。", say: "抓到了！请发勋章！", mood: { name: "徒手抓到鱼", emo: "energized", pts: 4, min: 180 }, need: { social: 8 } },
      { text: "鱼太滑了，{名字}抓了三次，三次都滑走。最后它自己蹦回了桶里。", say: "它好像在戏弄我。", mood: { name: "被鱼戏弄了", emo: "angry", pts: 2, min: 120 }, need: { hygiene: -5 } } ] },
    b: { label: "悄悄帮它蹦进海里。", out: [
      { text: "{名字}轻轻一推，鱼“扑通”回到了海里。大叔看见了，叹了口气，摆摆手说算了。", say: "大叔，你是个好人。", mood: { name: "放走了一条鱼", emo: "playful", pts: 3, min: 150 } },
      { text: "大叔回头正好看见，眉毛皱成了一团。{名字}只好陪他一起盯着浮漂，盯了一个钟头。", say: "我陪你再钓一条……", mood: { name: "被大叔抓包", emo: "tense", pts: 3, min: 150 }, need: { social: 5 } } ] } },
  { n: 377, title: "码头竞速", at: "beach", when: "morning",
    text: "一个晨跑的人从{名字}身边跑过，又折返回来，原地踏步着问：“一起跑一段？”",
    a: { label: "跟上去跑。", out: [
      { text: "{名字}一路跑到码头尽头，风灌满了衣服。停下来时心跳得很快，觉得自己能跑到海对面。", say: "呼……再来一圈！", mood: { name: "晨跑跑开了", emo: "energized", pts: 5, min: 240 }, need: { energy: -10, fun: 10 } },
      { text: "跑了不到五十米，{名字}就扶着栏杆喘气。晨跑的人已经跑成了一个小点。", say: "你……你先走……", mood: { name: "五十米就跑不动", emo: "embarrassed", pts: 3, min: 150 }, need: { energy: -10 } } ] },
    b: { label: "说自己在晨“走”。", out: [
      { text: "晨跑的人哈哈一笑，放慢脚步陪{名字}走了一段，还分享了一个看日出的好位置。", say: "明早我去那儿看看。", mood: { name: "得到日出秘籍", emo: "inspired", pts: 3, min: 180 }, need: { social: 10 } },
      { text: "晨跑的人跑走后，{名字}一个人慢慢走，越走越觉得自己好像输了什么。", say: "其实我也能跑的，真的。", mood: { name: "莫名觉得输了", emo: "uncomfortable", pts: 2, min: 120 } } ] } },
  { n: 378, title: "第一排脚印", at: "beach", when: "snow",
    text: "下了一夜的雪，码头的木板上铺着平平整整的一层白，一个脚印都没有。",
    a: { label: "踩出第一排脚印。", out: [
      { text: "{名字}一步一步走到尽头，回头一看，一排小小的脚印整整齐齐。整个码头好像签上了{她}的名字。", say: "这码头今天归我了。", mood: { name: "第一个踩雪", emo: "confident", pts: 4, min: 210 } },
      { text: "雪下面是结了冰的木板。{名字}第三步就滑出去好远，留下了一道长长的痕迹。", say: "这不是脚印，是滑板印。", mood: { name: "在雪上滑倒", emo: "scared", pts: 3, min: 150 } } ] },
    b: { label: "舍不得踩，站在岸边看。", out: [
      { text: "一只海鸥落在雪上，留下一串小叉叉。{名字}觉得这样也挺好，让鸟先签名。", say: "海鸥签名，也很好看。", mood: { name: "看海鸥踩雪", emo: "playful", pts: 3, min: 150 } },
      { text: "{名字}还在犹豫，一个小孩已经跑过去，在雪上打了好几个滚。", say: "……好吧，滚得也挺好。", mood: { name: "雪被抢先了", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 379, title: "看不清的告示", at: "beach", when: "",
    text: "码头入口有一块旧告示牌，字被海风吹得只剩一半：“禁止……海……”",
    a: { label: "努力推理出原文。", out: [
      { text: "{名字}对着残字研究了很久，得出结论：“禁止在海边不开心。”这个规定，{名字}决定严格遵守。", say: "收到，坚决执行！", mood: { name: "破译了告示", emo: "focused", pts: 3, min: 180 } },
      { text: "{名字}想了十种可能，越想越不确定自己现在站的地方合不合规。", say: "我站在这儿，犯法吗？", mood: { name: "怀疑自己违规", emo: "tense", pts: 2, min: 120 } } ] },
    b: { label: "问问路过的人。", out: [
      { text: "路过的爷爷说，原来写的是“禁止在海边乱丢东西”，是他年轻时看着挂上去的。还顺便讲了一段往事。", say: "原来告示也有故事。", mood: { name: "听来一段往事", emo: "inspired", pts: 3, min: 180 }, need: { social: 10 } },
      { text: "路过的人看了看，又看了看{名字}，说：“我也一直想知道。”然后两个人一起站着发呆。", say: "看来它永远是个谜了。", mood: { name: "和路人一起迷惑", emo: "dazed", pts: 3, min: 150 }, need: { social: 5 } } ] } },
  { n: 380, title: "挂在灯上的风筝", at: "beach", when: "",
    text: "一只风筝缠在了路灯顶上。下面站着一个快要哭出来的小孩。",
    a: { label: "想办法把它够下来。", out: [
      { text: "{名字}借来大叔的鱼竿，踮着脚一挑，风筝晃晃悠悠地落了下来。小孩破涕为笑。", say: "鱼竿也能钓风筝哦。", mood: { name: "钓下了风筝", emo: "confident", pts: 4, min: 210 }, need: { social: 10 } },
      { text: "{名字}跳了十几下，还是差一点。小孩看着{她}跳，反而先笑出了声。", say: "至少我把你逗笑了……", mood: { name: "够不着风筝", emo: "sad", pts: 2, min: 120 }, need: { energy: -8, social: 5 } } ] },
    b: { label: "陪小孩等风来。", out: [
      { text: "一阵大风吹来，风筝自己挣脱了，正好落进小孩怀里。两个人都觉得风是听懂了。", say: "谢谢你，风！", mood: { name: "等来了一阵风", emo: "playful", pts: 3, min: 180 }, need: { social: 8 } },
      { text: "风来了，把风筝吹得更高，挂到了更远的另一盏灯上。", say: "风……你不是来帮忙的吗？", mood: { name: "风帮了倒忙", emo: "uncomfortable", pts: 3, min: 120 }, need: { social: 5 } } ] } },
  { n: 381, title: "天边的乌云", at: "beach", when: "",
    text: "海的那一头堆起了一大片乌云，隐隐约约传来闷闷的雷声。码头上还是晴的。",
    a: { label: "再看五分钟就走。", out: [
      { text: "{名字}看着乌云在海上慢慢移动，闪电在云里一亮一亮，像一场远处的烟花。五分钟一到就准时撤离。", say: "大自然的烟花秀，看过了。", mood: { name: "看了一场闪电", emo: "inspired", pts: 4, min: 210 } },
      { text: "五分钟变成了十五分钟，雨点忽然砸了下来。{名字}一路跑回岸上，像只落汤鸡。", say: "说好的五分钟呢……", mood: { name: "被雨追着跑", emo: "tense", pts: 3, min: 150 }, need: { hygiene: -10, energy: -5 } } ] },
    b: { label: "马上收拾回家。", out: [
      { text: "刚到家，外面就下起了大雨。{名字}站在窗边，觉得自己的判断准得像天气预报。", say: "我就是人形天气预报。", mood: { name: "完美避开大雨", emo: "confident", pts: 3, min: 180 } },
      { text: "{名字}一走，乌云就散了，太阳又出来了。{名字}在路上回头看了好几次。", say: "乌云，你是在吓唬我吧！", mood: { name: "被乌云骗了", emo: "angry", pts: 2, min: 120 } } ] } },
  { n: 382, title: "海浪摇篮曲", at: "beach", when: "tired",
    text: "{名字}靠在栏杆边，海浪一下一下拍着木桩，节奏慢得让人眼皮发沉。",
    a: { label: "闭上眼睛眯一会儿。", out: [
      { text: "{名字}睡了一个短短的好觉，醒来时太阳挪了一点，海鸥还在原地。整个人都充好了电。", say: "睡饱啦，满血复活。", mood: { name: "听着海浪睡着", emo: "energized", pts: 4, min: 210 }, need: { energy: 15 } },
      { text: "{名字}睡得太香，醒来时身上落了三根海鸥毛，脸上还有木板压出来的印子。", say: "我睡觉时发生了什么？", mood: { name: "睡醒一脸木纹", emo: "dazed", pts: 3, min: 150 }, need: { energy: 10 } } ] },
    b: { label: "数海浪保持清醒。", out: [
      { text: "数到第一百个浪，{名字}忽然觉得每个浪都长得不一样。困意没了，好奇心来了。", say: "第一百零一号，你好。", mood: { name: "认识了一百个浪", emo: "focused", pts: 3, min: 180 } },
      { text: "数到第十二个浪，{名字}就靠着栏杆睡着了。后面的浪都没有被数到。", say: "十二……十三……呼……", need: { energy: 10 } } ] } },
  { n: 383, title: "退潮以后", at: "beach", when: "",
    text: "潮水退下去了，码头的木桩露出了长长一截，上面爬满了贝壳和湿漉漉的海草。",
    a: { label: "趴在边上仔细看。", out: [
      { text: "{名字}发现有个小贝壳正慢慢张开一条缝，好像在偷看{她}。两个都没说话。", say: "嘘，我不告诉别人。", mood: { name: "贝壳在偷看我", emo: "playful", pts: 3, min: 150 } },
      { text: "{名字}趴得太靠前，帽子掉了下去，挂在了一排贝壳上，够也够不着。", say: "帽子，你先在那儿住着。", mood: { name: "帽子掉下去了", emo: "sad", pts: 3, min: 150 } } ] },
    b: { label: "猜猜涨潮时它们在干嘛。", out: [
      { text: "{名字}认定涨潮时，这些贝壳会开一场盛大的派对，海草就是彩带。", say: "下次涨潮记得叫我。", mood: { name: "想象贝壳派对", emo: "inspired", pts: 3, min: 180 }, need: { fun: 5 } },
      { text: "想着想着，{名字}觉得木桩这么老，也该累了，开始替它担心起码头的未来。", say: "木桩，你还撑得住吗？", mood: { name: "担心码头木桩", emo: "tense", pts: 2, min: 120 } } ] } },
  { n: 384, title: "什么都没发生", at: "beach", when: "bored",
    text: "{名字}在码头坐了很久，海还是海，船还是那艘船，海鸥还是那几只。",
    a: { label: "等着看会发生什么。", out: [
      { text: "终于，一条鱼跳出了水面，又“扑通”落了回去。这是今天最大的新闻。", say: "头条：鱼跳了一下！", mood: { name: "等来一条鱼跳", emo: "playful", pts: 3, min: 150 }, need: { fun: 5 } },
      { text: "什么都没发生，一直到{名字}站起来走了，也还是什么都没发生。", say: "大海今天休息吧。", mood: { name: "等了个空", emo: "bored", pts: 3, min: 180 } } ] },
    b: { label: "自己找点事做。", out: [
      { text: "{名字}给码头的每根系缆桩起了名字，还给它们排了座次。最胖的那根当了老大。", say: "胖桩老大，今天辛苦了。", mood: { name: "给桩子排座次", emo: "focused", pts: 3, min: 150 }, need: { fun: 10 } },
      { text: "{名字}开始用脚尖敲木板打节拍，敲着敲着，发现旁边钓鱼的大叔一脸“鱼被你吓跑了”的表情。", say: "对、对不起，我停了。", mood: { name: "打扰了钓鱼人", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 385, title: "叮铃铃的小推车", at: "beach", when: "summer+day",
    text: "一辆卖冰棍的小推车摇着铃铛停在码头口。卖冰棍的阿姨冲{名字}喊：“最后两根啦！”",
    a: { label: "买一根。", out: [
      { text: "阿姨看{名字}可爱，把最后两根都塞给了{她}。一根自己吃，一根请了旁边的小孩。", say: "一根给你，一根给我。", mood: { name: "多得一根冰棍", emo: "happy", pts: 4, min: 210 }, need: { hunger: 8, social: 8 } },
      { text: "冰棍化得比吃得快，顺着手指一路往下流。{名字}吃完时手已经黏成了一团。", say: "冰棍在我手上跑了。", mood: { name: "手被冰棍黏住", emo: "uncomfortable", pts: 2, min: 120 }, need: { hunger: 5, hygiene: -8 } } ] },
    b: { label: "问阿姨“最后”是真的吗。", out: [
      { text: "阿姨哈哈大笑，掀开箱子，里面还有满满一箱。两个人笑成一团，{名字}最后还是买了一根。", say: "阿姨，你可太会做生意了。", mood: { name: "识破推销话术", emo: "playful", pts: 3, min: 150 }, need: { hunger: 5, social: 8 } },
      { text: "阿姨一本正经地说是真的。{名字}还在犹豫，后面的人就把两根都买走了。", say: "原来是真的最后两根……", mood: { name: "错过最后冰棍", emo: "sad", pts: 3, min: 150 } } ] } },
  { n: 386, title: "泡泡向大海", at: "beach", when: "",
    text: "一个小孩在码头上吹泡泡，风把泡泡一串一串地往海上送。小孩把泡泡棒递给了{名字}。",
    a: { label: "吹一个超大的。", out: [
      { text: "{名字}屏住气慢慢吹，吹出了一个西瓜那么大的泡泡，晃晃悠悠飘到了海上。小孩看呆了。", say: "看，它要出国了！", mood: { name: "吹出巨大泡泡", emo: "confident", pts: 4, min: 180 }, need: { fun: 10, social: 8 } },
      { text: "{名字}用力过猛，泡泡还没成形就“啪”地破在了自己脸上。", say: "呸呸，泡泡水是苦的！", mood: { name: "泡泡糊了一脸", emo: "embarrassed", pts: 2, min: 120 }, need: { social: 5 } } ] },
    b: { label: "帮小孩追泡泡。", out: [
      { text: "两个人在码头上跑来跑去，伸手戳泡泡。最后一个泡泡落在海鸥背上，才破。", say: "海鸥也被我们抓到了！", mood: { name: "追泡泡追疯了", emo: "energized", pts: 4, min: 180 }, need: { fun: 12, energy: -5 } },
      { text: "{名字}追着一个泡泡跑到栏杆边，差点探出身子去。被小孩一把拉住了衣角。", say: "好险，谢谢你……", mood: { name: "差点追进海里", emo: "scared", pts: 3, min: 150 }, need: { social: 5 } } ] } },
  { n: 387, title: "大叔的点歌台", at: "beach", when: "",
    text: "钓鱼的大叔身边放着一台小收音机，正咿咿呀呀地放着一首很老的歌。",
    a: { label: "跟着哼两句。", out: [
      { text: "{名字}一哼，大叔也跟着唱了起来。两个人一老一小，在码头上合唱了整首歌。", say: "大叔，再来一首！", mood: { name: "码头合唱团", emo: "playful", pts: 4, min: 210 }, need: { social: 12, fun: 10 } },
      { text: "{名字}哼的调子和收音机完全不一样。大叔默默把音量调大了一点。", say: "我……我这是改编版。", mood: { name: "跑调被盖过", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "问大叔这是什么歌。", out: [
      { text: "大叔说这是他年轻时追人用的歌，后来真追到了。说完眯起眼睛，笑得像个小伙子。", say: "这首歌，有点甜。", mood: { name: "听来一段情歌", emo: "flirty", pts: 3, min: 180 }, need: { social: 10 } },
      { text: "大叔想了半天，也想不起歌名，急得鱼竿都放下了。最后两个人一起哼着找答案。", say: "就差一点点，就差一点！", mood: { name: "歌名卡在嘴边", emo: "tense", pts: 3, min: 150 }, need: { social: 8 } } ] } },
  { n: 388, title: "会说话的木板", at: "beach", when: "",
    text: "{名字}走过码头时，脚下一块木板“吱呀”了一声。退回去踩，又“吱呀”一声。",
    a: { label: "试着踩出一首歌。", out: [
      { text: "前后左右踩了一阵，{名字}找出了四块会叫的木板，踩出了一段像模像样的曲子。", say: "码头钢琴，演奏完毕。", mood: { name: "踩出一首曲子", emo: "inspired", pts: 4, min: 210 }, need: { fun: 12 } },
      { text: "踩得太起劲，一块木板“咔”地翘起了一角。{名字}僵在原地，不敢再动。", say: "我、我什么都没干。", mood: { name: "踩翘了木板", emo: "scared", pts: 3, min: 150 } } ] },
    b: { label: "跟它对话。", out: [
      { text: "{名字}问：“你还好吗？”木板“吱呀”一声。{名字}认为这是“还行”的意思。", say: "还行就好，你辛苦了。", mood: { name: "和木板聊了天", emo: "playful", pts: 3, min: 150 } },
      { text: "{名字}聊得太投入，一抬头，发现一对路过的人正站着看{她}跟地板说话。", say: "……它先开口的。", mood: { name: "跟地板说话被看见", emo: "embarrassed", pts: 3, min: 150 } } ] } },
  { n: 389, title: "栏杆上的名字", at: "beach", when: "",
    text: "码头栏杆上刻着很多小小的名字和日期，有的已经被海风磨得快看不清了。",
    a: { label: "一个一个读过去。", out: [
      { text: "{名字}读到一对名字，日期是很多年前。旁边又刻着同样的两个名字，日期是去年。", say: "他们又一起回来了啊。", mood: { name: "读到了好故事", emo: "flirty", pts: 4, min: 240 } },
      { text: "{名字}读着读着，发现有个名字跟自己只差一个字，心里莫名地不平静起来。", say: "这是平行世界的我吗？", mood: { name: "撞见相似名字", emo: "dazed", pts: 3, min: 150 } } ] },
    b: { label: "用手指描一个空白处。", out: [
      { text: "{名字}没有刻字，只是用手指在空白的地方写了一遍自己的名字。风一吹，就当是留下了。", say: "我来过，风知道。", mood: { name: "用风签了名", emo: "inspired", pts: 3, min: 180 } },
      { text: "手指上扎了一根小木刺。{名字}拔了半天，觉得栏杆不太欢迎新名字。", say: "嘶……栏杆你小气。", mood: { name: "被木刺扎了", emo: "angry", pts: 2, min: 90 } } ] } },
  { n: 390, title: "一根羽毛", at: "beach", when: "",
    text: "一根又白又长的海鸥羽毛飘下来，正好落在{名字}的鞋尖上。",
    a: { label: "捡起来插在帽子上。", out: [
      { text: "插上羽毛之后，{名字}觉得自己走路都带风了，像一位刚靠岸的探险家。", say: "探险家{名字}，出发！", mood: { name: "戴上羽毛帽", emo: "confident", pts: 3, min: 180 } },
      { text: "一只海鸥在头顶盘旋了很久，好像在确认那是不是自己的羽毛。", say: "这不是你的！大概不是……", mood: { name: "被失主盯上", emo: "tense", pts: 3, min: 150 } } ] },
    b: { label: "用它当笔写点什么。", out: [
      { text: "{名字}蘸着木板上的一点水，用羽毛写了一首三行的小诗。写完水就干了，只有{名字}读过。", say: "世界上最短命的诗。", mood: { name: "写了一首小诗", emo: "inspired", pts: 4, min: 210 } },
      { text: "羽毛太软，什么也写不出来。{名字}最后用它挠了挠自己的下巴，竟然很舒服。", say: "原来羽毛是用来挠痒的。", mood: { name: "羽毛挠痒痒", emo: "playful", pts: 2, min: 120 } } ] } },
  { n: 391, title: "夜钓的灯", at: "beach", when: "night",
    text: "夜里的码头只剩一盏小提灯亮着，一个夜钓的人裹着外套，朝{名字}举了举保温杯。",
    a: { label: "走过去坐一会儿。", out: [
      { text: "夜钓的人倒了半杯热茶给{名字}。两个人不怎么说话，只是一起看着浮漂上的小灯一晃一晃。", say: "热茶配海风，刚刚好。", mood: { name: "夜里的一杯茶", emo: "focused", pts: 4, min: 240 }, need: { social: 10, energy: 5 } },
      { text: "{名字}刚坐下，黑暗里有个东西“啪”地拍了一下水。{名字}差点把茶洒了。", say: "刚才那是鱼吧？是鱼吧！", mood: { name: "夜里的水声", emo: "scared", pts: 3, min: 150 }, need: { social: 5 } } ] },
    b: { label: "点点头，不去打扰。", out: [
      { text: "{名字}在不远处看着那盏小灯，觉得夜里的海边有人在，就不那么空了。", say: "有灯有人，夜就不冷。", need: { social: 3 } },
      { text: "回家的路上，{名字}有点后悔没过去。那杯热茶的白气，一直在脑子里冒。", say: "下次一定过去喝一口。", mood: { name: "错过一杯热茶", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 392, title: "灯塔在哪儿", at: "beach", when: "",
    text: "一个背着大包的游客拿着地图走过来，问{名字}：“请问去灯塔怎么走？”这附近并没有灯塔。",
    a: { label: "老实说没有灯塔。", out: [
      { text: "游客愣了一下，翻了翻地图，发现自己拿的是另一座城市的。两个人笑了很久。", say: "地图都去旅游了。", mood: { name: "帮人找到真相", emo: "confident", pts: 3, min: 150 }, need: { social: 10 } },
      { text: "游客一脸不信，坚持说网上看到过。{名字}被问得越来越没底，最后自己也开始找灯塔。", say: "难道真有？我怎么不知道！", mood: { name: "怀疑自家码头", emo: "dazed", pts: 3, min: 150 }, need: { social: 5 } } ] },
    b: { label: "指向码头尽头那盏路灯。", out: [
      { text: "游客走到尽头，看了看路灯，又看了看海，回头朝{名字}比了个大拇指：“小是小了点，挺好。”", say: "迷你灯塔，也是灯塔。", mood: { name: "介绍了迷你灯塔", emo: "playful", pts: 3, min: 150 }, need: { social: 8 } },
      { text: "游客认真地在路灯下拍了二十张照片。{名字}良心不安，一直躲在系缆桩后面。", say: "对不起，路灯先生……", mood: { name: "良心不太安", emo: "uncomfortable", pts: 3, min: 150 } } ] } },
  { n: 393, title: "单只拖鞋", at: "beach", when: "",
    text: "一只蓝色拖鞋漂在码头边，慢悠悠地转着圈，看不到另一只在哪里。",
    a: { label: "捞起来挂在栏杆上。", out: [
      { text: "过了一会儿，一个光着一只脚的小孩一蹦一跳地跑来，看到拖鞋，高兴得原地转了一圈。", say: "拖鞋，你家主人来接你了。", mood: { name: "拖鞋找到主人", emo: "happy", pts: 3, min: 210 }, need: { social: 5 } },
      { text: "{名字}把拖鞋晾在栏杆上，一只海鸥飞来，叼起它就飞走了。", say: "海鸥，你又不穿鞋！", mood: { name: "拖鞋被叼走", emo: "angry", pts: 3, min: 150 } } ] },
    b: { label: "猜它经历了什么。", out: [
      { text: "{名字}认定这只拖鞋是离家出走去看世界的。想到这里，觉得它比自己还勇敢。", say: "祝你旅途愉快，拖鞋。", mood: { name: "敬佩一只拖鞋", emo: "inspired", pts: 3, min: 180 } },
      { text: "{名字}猜着猜着，开始担心另一只拖鞋是不是正孤零零地在某处等它。", say: "另一只……还好吗？", mood: { name: "替拖鞋难过", emo: "sad", pts: 2, min: 120 } } ] } },
  { n: 394, title: "海的另一边", at: "beach", when: "",
    text: "一个小孩扒着栏杆看了很久，突然转头问{名字}：“海的另一边是什么？”",
    a: { label: "认真地编一个答案。", out: [
      { text: "{名字}说，那边也有一个码头，也有一个小孩在问同样的问题。小孩听完，朝海用力挥了挥手。", say: "说不定那边也在挥手。", mood: { name: "给海编了故事", emo: "inspired", pts: 4, min: 240 }, need: { social: 10 } },
      { text: "{名字}编得太长，从鲸鱼讲到海盗，又讲到外星人。小孩早就跑去看海鸥了。", say: "等等，我还没讲到结局！", mood: { name: "故事没人听完", emo: "bored", pts: 2, min: 120 } } ] },
    b: { label: "说自己也想知道。", out: [
      { text: "小孩想了想，说那等长大了一起去看。说完就跟{名字}拉了个钩，很严肃。", say: "拉钩了，不许反悔。", mood: { name: "和小孩拉了钩", emo: "flirty", pts: 3, min: 210 }, need: { social: 10 } },
      { text: "小孩露出了“大人怎么也不知道”的表情，叹了口气走掉了。", say: "大人也不是什么都知道嘛。", mood: { name: "被小孩嫌弃", emo: "embarrassed", pts: 2, min: 120 } } ] } },
  { n: 395, title: "海鸥法庭", at: "beach", when: "",
    text: "两只海鸥为了一条小鱼在{名字}面前吵了起来，嘎嘎声一声比一声高。",
    a: { label: "出面调解。", out: [
      { text: "{名字}张开双手站到中间，两只海鸥都愣住了。小鱼趁乱一跳，回到了海里。", say: "本案判决：鱼无罪释放。", mood: { name: "当了一回法官", emo: "confident", pts: 4, min: 180 } },
      { text: "两只海鸥停下来，一起对着{名字}嘎嘎叫。看来它们在这件事上意见一致。", say: "怎么还一起骂我！", mood: { name: "被两只海鸥骂", emo: "angry", pts: 3, min: 150 } } ] },
    b: { label: "退后当观众。", out: [
      { text: "{名字}默默给两边记分。最后鱼被第三只海鸥叼走了，比赛以爆冷结束。", say: "比分作废，第三方获胜。", mood: { name: "看了场海鸥大战", emo: "playful", pts: 3, min: 150 }, need: { fun: 8 } },
      { text: "吵着吵着，两只海鸥扑腾着翅膀朝{名字}这边打过来了。{名字}抱着头蹲了下去。", say: "打架别带上我！", mood: { name: "卷进海鸥大战", emo: "scared", pts: 3, min: 150 } } ] } },
  { n: 396, title: "等太阳", at: "beach", when: "morning+clear",
    text: "天还是灰蓝色的，海平线那头已经透出一点点橘色。太阳就快出来了。",
    a: { label: "目不转睛地盯着。", out: [
      { text: "太阳一点点冒出来，海面一下子铺满了金色。{名字}看得忘了眨眼，心里亮堂堂的。", say: "早上好，太阳。", mood: { name: "看到了日出", emo: "inspired", pts: 5, min: 300 }, need: { energy: 5 } },
      { text: "盯了太久，{名字}眼睛一酸，眨了一下。再睁开时太阳已经整个跳了出来。", say: "就眨了一下眼啊！", mood: { name: "眨眼错过日出", emo: "angry", pts: 2, min: 120 } } ] },
    b: { label: "先去买杯热豆浆再回来。", out: [
      { text: "{名字}捧着热豆浆跑回来，太阳刚好露出一半。热气和朝霞混在一起，暖到了手心。", say: "豆浆和太阳，一起热乎。", mood: { name: "豆浆配日出", emo: "energized", pts: 4, min: 210 }, need: { hunger: 10 } },
      { text: "排队的人太多，{名字}回来时太阳已经挂得老高。豆浆倒是很好喝。", say: "太阳，明天再约。", mood: { name: "日出没赶上", emo: "bored", pts: 2, min: 120 }, need: { hunger: 10 } } ] } },
  { n: 397, title: "落叶船队", at: "beach", when: "autumn",
    text: "风把岸边的落叶吹上了码头，有几片落进水里，像小船一样漂了出去。",
    a: { label: "挑一片当自己的船。", out: [
      { text: "{名字}选中的那片叶子一路领先，漂过了第三根木桩。{名字}在码头上为它一路欢呼。", say: "冲啊，我的冠军船！", mood: { name: "落叶船夺冠", emo: "energized", pts: 4, min: 180 }, need: { fun: 10 } },
      { text: "{名字}的叶子刚下水就打了个转，被一个小浪拍沉了。别的叶子都漂得好好的。", say: "我的船……出师未捷。", mood: { name: "落叶船沉了", emo: "sad", pts: 2, min: 120 } } ] },
    b: { label: "数一数一共有几艘。", out: [
      { text: "{名字}一共数了十七艘，给它们编成了一支秋天舰队，指挥官是最红的那片。", say: "秋天舰队，全员出航！", mood: { name: "组建秋天舰队", emo: "focused", pts: 3, min: 180 } },
      { text: "风一阵接一阵，叶子越来越多。{名字}数到后面，已经分不清哪些数过了。", say: "秋天你别再发船了！", mood: { name: "叶子数不完", emo: "dazed", pts: 2, min: 120 } } ] } },
  { n: 398, title: "请让一让", at: "beach", when: "",
    text: "一个扛着长镜头的摄影师在码头上蹲了好久，终于小声对{名字}说：“能稍微往旁边让一让吗？”",
    a: { label: "立刻让开。", out: [
      { text: "{名字}让开的下一秒，一只海鸥正好掠过海面。摄影师按下快门，激动地把照片给{名字}看。", say: "这张有我一份功劳。", mood: { name: "成全了好照片", emo: "confident", pts: 3, min: 180 }, need: { social: 8 } },
      { text: "{名字}让得太急，一脚踩进了摄影师放在地上的包里。两个人都僵住了。", say: "我的脚……不是故意的。", mood: { name: "踩进别人包里", emo: "embarrassed", pts: 3, min: 150 } } ] },
    b: { label: "问能不能看看他在拍什么。", out: [
      { text: "摄影师把镜头让给{名字}看。镜头里，远处那艘大船上竟然有个人在晾衣服。", say: "原来大船上也晒被子！", mood: { name: "长镜头里的世界", emo: "focused", pts: 4, min: 210 }, need: { social: 8, fun: 8 } },
      { text: "{名字}凑过去的时候，海鸥正好飞过。摄影师看着空空的天空，叹了很长一口气。", say: "我……我这就走。", mood: { name: "害人错过镜头", emo: "uncomfortable", pts: 4, min: 150 } } ] } },
  { n: 399, title: "海不说话", at: "beach", when: "badMood",
    text: "今天有点不顺。{名字}一个人走到码头尽头，靠着栏杆，看着海一下一下地涌过来。",
    a: { label: "把烦心事扔进海里。", out: [
      { text: "{名字}在心里把烦心事团成一团，用力扔了出去。海一点都不介意，照单全收。", say: "拿去吧，大海，谢谢你。", mood: { name: "把烦恼扔进海", emo: "energized", pts: 4, min: 240 } },
      { text: "扔完之后，一个浪正好拍回来，溅了{名字}一身。好像在说：“这个我们不收。”", say: "连大海都退货吗……", mood: { name: "烦恼被退回", emo: "sad", pts: 3, min: 150 }, need: { hygiene: -5 } } ] },
    b: { label: "什么都不想，就看着。", out: [
      { text: "看了很久很久，海还是那样来来去去。{名字}的心跳慢慢跟上了浪的节奏。", say: "嗯，好一点了。", mood: { name: "跟着海呼吸", emo: "focused", pts: 4, min: 240 } },
      { text: "{名字}越看越出神，等回过神来，烦心事没想起来，倒是忘了自己为什么来这儿。", say: "我来这儿干嘛来着？" } ] } },
  { n: 400, title: "和海鸥谈心", at: "beach", when: "lonely",
    text: "码头上空荡荡的，只有一只海鸥站在不远的系缆桩上，偶尔歪头看看{名字}。",
    a: { label: "跟它聊聊天。", out: [
      { text: "{名字}说了好多话，海鸥一直没飞走，偶尔“嘎”一声。{名字}觉得这是个很好的听众。", say: "你是我今天的好朋友。", mood: { name: "有海鸥陪着", emo: "flirty", pts: 3, min: 210 }, need: { social: 10 } },
      { text: "{名字}刚说到最要紧的地方，海鸥就扑棱棱飞走了，头也不回。", say: "喂，我还没说完呢……", mood: { name: "海鸥中途离席", emo: "sad", pts: 3, min: 150 } } ] },
    b: { label: "去岸边找个人说说话。", out: [
      { text: "{名字}走到岸边，跟钓鱼的大叔聊起天气。聊着聊着，大叔说起了自己的小孙女，越说越高兴。", say: "原来大叔也想找人说话。", mood: { name: "和大叔聊开了", emo: "playful", pts: 3, min: 210 }, need: { social: 15 } },
      { text: "岸边的人都在忙自己的事。{名字}转了一圈，又回到了码头上，海鸥还在。", say: "还是你在等我呀。", mood: { name: "转了一圈回来", emo: "bored", pts: 3, min: 150 }, need: { social: 3 } } ] } },
);
