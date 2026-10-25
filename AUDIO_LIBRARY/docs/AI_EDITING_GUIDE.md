# 给其他 AI 的音频修改指南

本目录的目标是让后续 AI 能在不猜测文件含义的情况下修改音频。先读 `AUDIO_LIBRARY/README.md` 与 `docs/TRACKS.json`，再改源代码。

## 基本原则

1. 只修改用户指定的曲目；不要顺手重写其他场景。
2. MP3 是交付结果，不是首选编辑对象。优先修改 `SOURCE/*.py` 中的 MIDI 音高、节奏、BPM、配器或混响参数，再重新生成。
3. 保留随机种子，便于复现；若更改噪声或配器后结果不同，先检查是否改变了随机数调用顺序。
4. 不要删除依赖脚本。公园最终版使用一条继承链，酒吧改编会读取日光中庭的主题数据。
5. 未经用户明确要求，不自动把音频接入游戏，不修改游戏对话与机会卡。

## 常用音符格式

### 居家

`SOURCE/make_lofi_bgm_v2_long.py` 与 `SOURCE/make_seasons_bgm.py` 使用：

```text
(小节, 十六分音符位置, MIDI音高, 持续单位)
```

居家定稿包含用户三处改音：第 49 音 D5→C5、第 53 音 A5→G5、第 78 音 A5→G5。`melody_notes.json` 是旋律编辑数据。

### 公园

`make_park_spring_pop_v4.py` 中的 `MELODY` 是最终 129 音主题，格式为：

```text
(1起始小节, 十六分音符位置, MIDI音高, 持续单位)
```

依赖关系：

```text
make_park_seasons_bgm.py
  └─ make_park_spring_pop_v3.py
       └─ make_park_spring_pop_v4.py
            └─ make_park_remaining_seasons_final.py
```

修改春天定稿时主要改 v4；夏秋冬完整复用 v4 的 `MELODY` 与 `HARMONY`，但编曲函数各自独立。

### 商场

`SOURCE/make_mall_crowd_rush.py` 的 `HOOK` 为 23 音、四小节主题：

```text
(四小节内的十六分音符绝对位置0–63, MIDI音高, 拍数)
```

当前定稿第 3 音为 D5（MIDI 74），第 6 音为 F4（MIDI 65）。改音后应同步修改网页播放器中的 `MALL_HOOK`（若播放器也在维护范围内）。

### 酒吧

`SOURCE/make_bar_low_jazz.py` 同时生成两首：

- 《杯中日光》：从 `make_mall_daylight_atrium.py` 读取 `CH`、`ROOT`、`A`、`B`、`C`，因此必须保留该文件。
- 《琥珀低音》：直接编辑 `MELODY`，格式为 `(小节索引, 十六分位置, MIDI音高, 拍数)`。

### 码头

`SOURCE/make_harbor_return.py` 的 `THEME` 使用：

```text
(八小节内的小节索引, 十六分位置, MIDI音高, 拍数)
```

全曲分三次陈述：离岸、远眺、归帆。修改主题时注意三个段落会共同变化。

## MIDI 速查

A4=69，A♯4/B♭4=70，B4=71，C5=72，C♯5=73，D5=74，E5=76，F4=65，F5=77，G5=79，A5=81。升降一个半音即 MIDI ±1；升降一个八度即 ±12。

## 重新生成

在仓库根目录运行：

```bash
python3 AUDIO_LIBRARY/tools/build_audio.py
```

只修改某一首时，也可在临时工作目录运行对应脚本；注意补齐同目录依赖，并把 `/mnt/agents/output/` 改为可写输出目录。构建脚本已经自动完成这项路径替换。

完成后：

1. 用 FFprobe 检查时长、采样率与声道。
2. 检查首尾循环接缝和峰值。
3. 更新 `docs/TRACKS.json` 中变化的 BPM、时长或描述。
4. 更新 `checksums.sha256`；完整构建会自动更新。
5. 对照用户指定曲目检查 diff，避免混入其他音频变化。
