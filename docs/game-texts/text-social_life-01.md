# prototype/demo/social_life.js · 第 1 页

[返回目录](README.md) · [查看来源](https://github.com/OMEN-2778/Desktop-Buddy/blob/aebc047de517b5a9355a7973af993136aeb1b1a1/prototype/demo/social_life.js)

### L25

```text
关闭
```

### L35

```text
`和${contactName(c)}的经历`
```

### L36

```text
性格
```

### L36

```text
了解对方 · 性格
```

### L37

```text
还不太了解：聊聊天，慢慢认识彼此。
```

### L38

```text
共同的故事还没写下。下一次认真聊天，或者一起度过一段时光，就从这里开始。
```

### L41

```text
`第 ${Math.floor(memory.t/1440)+1} 天 · ${String(Math.floor(memory.t/60)%24).padStart(2,'0')}:${String(Math.floor(memory.t)%60).padStart(2,'0')}`
```

### L54

```text
公园
```

### L54

```text
酒吧
```

### L54

```text
商场
```

### L54

```text
街边
```

### L54

```text
码头
```

### L54

```text
路上
```

### L54

```text
重新
```

### L54

```text
第一次
```

### L54

```text
`在${({park:'公园',bar:'酒吧',mall:'商场',front:'街边',beach:'码头'})[sim.place]||'路上'}和${c.name}聊了几句，${returning?'重新':'第一次'}交换了联系方式。`
```

### L54

```text
再次遇见
```

### L54

```text
第一次认识
```

### L67

```text
慢慢熟悉
```

### L67

```text
聊得来
```

### L67

```text
有人懂我
```

### L67

```text
一直在身边
```

### L74

```text
`${contactName(c)}${reason}，彼此的联系淡了一点。`
```

### L75

```text
最近总没能联系上，彼此渐渐失去了联系。
```

### L78

```text
改天再来坐坐。
```

### L79

```text
暂时走散
```

### L80

```text
`和${contactName(c)}渐渐失去了联系。`
```

### L92

```text
许多天没再说上话，这段联系慢慢淡了。
```

### L93

```text
`这些天没和${c.name}联系，从${old}慢慢变成了${contactRelation(c)}。`
```

### L93

```text
关系渐渐疏远
```

### L133

```text
招待朋友
```

### L140

```text
暂时不能邀请
```

### L140

```text
这位朋友已经不在联系人名单里了。
```

### L142

```text
先回到家里，再邀请朋友来坐坐吧。
```

### L143

```text
主角晕倒了，先长按唤醒，再邀请朋友吧。
```

### L144

```text
主角正在睡觉，醒来后再邀请朋友吧。
```

### L145

```text
另一位客人
```

### L145

```text
已经在路上了
```

### L145

```text
还没有离开
```

### L145

```text
`${other?contactName(other):'另一位客人'}${socialState.guest.phase==='scheduled'?'已经在路上了':'还没有离开'}，等这次来访结束再邀请吧。`
```

### L146

```text
现在是休息时间，请在早上 8 点到晚上 9 点之间邀请朋友。
```

### L147

```text
主角正在聊天，聊完这一次后再邀请朋友吧。
```

### L148

```text
先处理完眼前的事情，再邀请朋友吧。
```

### L149

```text
主角有点饿或累了，先吃点东西、休息好，再招待朋友吧。
```

### L150

```text
`${c.name}：我们先多聊聊天，熟悉一点再登门吧。`
```

### L151

```text
暂时不能邀请
```

### L155

```text
`${contactName(c)}答应来家里坐坐，预计 ${minutes} 分钟后到达。`
```

### L155

```text
`好呀，我大概 ${minutes} 分钟后到！`
```

### L156

```text
邀请成功 · 等待出发
```

### L156

```text
`${contactName(c)}答应来啦，预计 ${minutes} 分钟后到达。当前已暂停，恢复时间后朋友才会过来。`
```

### L156

```text
恢复时间，等朋友来
```

### L159

```text
今天聊得很开心，下次再来。
```

### L161

```text
朋友
```

### L161

```text
`和${c?contactName(c):'朋友'}约好了改天再来。`
```

### L163

```text
`一起聊起了${g.count}件小事，`
```

### L163

```text
`${contactName(c)}来家里做客，${g.count?`一起聊起了${g.count}件小事，`:''}${reason}`
```

### L163

```text
来家里做客
```

### L202

```text
改天再来。
```

### L203

```text
`${contactName(c)}到了，换好鞋走进客厅。`
```

### L203

```text
`你来啦，进来坐！`
```

### L214

```text
主角要出门，约好下次再聚。
```

### L214

```text
先好好照顾自己，我们下次再聊。
```

### L221

```text
`和${contactName(c)}在家聊起「${tk.title}」。`
```

### L221

```text
`${contactName(c)}来家里时，${tk.said.map(([,s])=>s).join(' ')}`
```

### L243

```text
稍想了一下，
```

### L243

```text
回应了
```

### L243

```text
`${automatic?'稍想了一下，':'回应了'}${contactName(c)}「${reason[0]}」的来访请求：${reason[2]}。`
```

### L245

```text
稍想了一下，礼貌婉拒了
```

### L245

```text
礼貌婉拒了
```

### L245

```text
`${automatic?'稍想了一下，礼貌婉拒了':'礼貌婉拒了'}${contactName(c)}「${reason[0]}」的来访请求：${reason[3]}。`
```

### L246

```text
没关系，我们下次再约。
```

### L248

```text
`暂时没有回应${contactName(c)}「${reason[0]}」的来访请求。`
```

### L249

```text
的来访请求一直没有得到回应
```

### L254

```text
想坐车来看看你
```

### L254

```text
这阵子能挪出半天，想坐车去看看你。你今天在家吗？
```

### L254

```text
好呀，我在家等你
```

### L254

```text
这次有点不巧，咱们另约一天
```

### L259

```text
的头像
```

### L260

```text
无视
```

### L270

```text
`${contactName(c)} · 想聊聊`
```

### L270

```text
`${contactName(c)}：好久没联系了。你是不是不想再跟我来往了？`
```

### L271

```text
认真聊聊
```

### L271

```text
好好告别
```

### L271

```text
`和${contactName(c)}通了电话，把之前没说清的事讲开，约好以后有空再联系。`
```

### L271

```text
差一点走散
```

### L271

```text
通完告别电话，两个人没有再约下次。
```

