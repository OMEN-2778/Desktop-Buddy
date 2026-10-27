# Desktop Buddy 音频资产库

这是游戏的统一音频目录，已收录 **20 首游戏 BGM、34 个 CC0 原始音效、54 个原创游戏音效（含 17 段情绪短旋律），以及全部可编辑合成源码**。

> **入库状态（2026-10-25）**：16 首 BGM 已按原源码重建，7 个 CC0 音效均已下载入库，并生成适合游戏播放的短循环/拟音副本。声音已经接入游戏：设置里的“背景音乐”和“音效”分别开关，默认均关闭，保存到设置及存档。家门口与朋友家沿用居家曲目。
>
> 播放规则、代码入口、扩展方法与验证见 [游戏声音说明](../docs/AUDIO.md)。

## 目录

- `BGM/home/`：居家四季昼夜 8 首；同时供家门口复用。
- `BGM/park/`：公园四季 4 首。
- `BGM/mall/`：商场主曲《人潮高光》。
- `BGM/bar/`：酒吧《琥珀低音》《杯中日光》。
- `BGM/harbor/`：海边码头《雾港归帆》。
- `SFX/`：7 个 CC0 原始录音。
- `SFX/processed/`：7 个游戏播放副本，保持原件不变，裁剪/音量/接缝参数见 `docs/PLAYBACK_SAMPLES.json`。
- `SFX/game/`：54 个原创界面、电话、动作与自然环境音，见 `docs/GAME_SFX.json` 与 `docs/EMOTION_CUES.json`。
- `SOURCE/`：纯代码合成工程与旋律数据，供人类或其他 AI 修改。
- `docs/AI_EDITING_GUIDE.md`：修改顺序、音符格式、再生成方法。
- `docs/LICENSES.md`：第三方音效来源、作者、用途与 CC0 授权记录。
- `docs/TRACKS.json`：机器可读曲目目录。
- `tools/build_audio.py`：重建全部 BGM、下载音效并生成校验清单。
- `checksums.sha256`：音频完整性校验。

## BGM 用途

| 场景 | 文件 | 用途与听感 |
|---|---|---|
| 居家／家门口 | `home/spring-*.mp3` | 春季昼夜；白天 Rhodes 与柔笛，夜晚抒情钢琴 |
| 居家／家门口 | `home/summer-*.mp3` | 夏季昼夜；钢鼓与马林巴，夜晚更轻、更收敛 |
| 居家／家门口 | `home/autumn-*.mp3` | 秋季昼夜；尼龙指弹与软钢琴，无沙锤 |
| 居家／家门口 | `home/winter-*.mp3` | 冬季昼夜；钢片琴、长弦乐与安静空间 |
| 公园 | `park/park-spring.mp3` | 春日定稿；延伸和声、暖电钢琴、丰厚低频 |
| 公园 | `park/park-summer.mp3` | 同主题巴萨诺瓦编曲 |
| 公园 | `park/park-autumn.mp3` | 同主题室内民谣编曲 |
| 公园 | `park/park-winter.mp3` | 同主题极简氛围编曲 |
| 商场 | `mall/mall-neon-escalator.mp3` | 霓虹扶梯 · 连贯编配版（试听页选定） |
| 迪厅 | `disco/disco-glitter.mp3` | 镜球亮起来，122 BPM 流行迪斯科（`tools/compose_disco_glitter.py`，FluidR3 GM 音色，MIT） |
| 酒吧 | `bar/bar-amber-bass.mp3` | 72 BPM 低频爵士；upright bass、暖电钢琴、轻刷鼓 |
| 酒吧 | `bar/bar-daylight-cup.mp3` | 《日光中庭》主题的 Swing 酒吧改编 |
| 海边码头 | `harbor/harbor-mist-return.mp3` | 68 BPM 海洋叙事；大提琴、尼龙吉他、潮声与远处浮标钟 |

## 环境音效用途

| 文件 | 建议用途 |
|---|---|
| `cat-meow-cc0.mp3` | 家门口橘猫、窗台猫偶遇；短促触发，不宜高频循环 |
| `cat-purr-meow-cc0.mp3` | 抚摸猫、猫回应互动；一次性触发 |
| `rain-soft-loop-cc0.mp3` | 细雨环境底层，可低音量循环 |
| `rain-heavy-window-cc0.mp3` | 暴雨、窗边雨势；与远雷分层使用 |
| `thunder-heavy-no-rain-cc0.mp3` | 强雷、近雷事件；随机间隔触发，避免连续轰鸣 |
| `crowd-indoor-walla-cc0.mp3` | 商场或酒吧人群底层；原录音含德语人群交谈，应低音量使用 |
| `crowd-small-laugh-cc0.mp3` | 酒吧或聚会短笑声；偶发，不作为持续循环 |

所有音效均为 Freesound 官方 HQ 预览编码，便于游戏使用与直接试听；原始无损文件需登录 Freesound 下载。每个资产的原始页面和许可证据见 `docs/LICENSES.md`。

## 一键重建

依赖：Python 3、numpy、scipy、FFmpeg、curl。

```bash
python3 -m pip install numpy scipy
python3 AUDIO_LIBRARY/tools/build_audio.py
```

脚本会在临时目录内修正原始开发环境的绝对输出路径，不影响仓库中的源代码。重建只更新定稿音频，不接入游戏，也不改动游戏文本或逻辑。

最新更新：设置已改为两条独立的 0–100% 音量滑条；新增 3 份公园和 8 份生活实录，取代对应合成音。脚步声移除。来源见 `docs/REAL_FOLEY_SOURCES.json` 和 `docs/LICENSES.md`。

环境细节扩展：音效层现有 34 个 CC0 原始录音（含 24 个生活拟音来源），播放副本支持距离、声像、隔墙和窗户过滤。来电使用轻铃声并降低背景层；界面音量滑条与数值底框已统一圆角。

节日场景音乐：端午码头白天使用原创《海风拐了个弯》，夜晚使用《末班船以后》；节日公园白天使用《街角灯亮了》。三首录音的来源和 GeneralUser GS 授权记录见 `prototype/music-preview/CREDITS.md`。
