# Desktop Buddy 音频资产库

这是游戏的统一音频目录，目标内容为 **16 首定稿 BGM、7 个 CC0 环境音效，以及全部可编辑合成源代码**。

> **入库状态（2026-10-25）**：文档、11 份源文件和重建脚本已入库并校验；音频二进制尚未入库。16 首 BGM 已在本地成功重建，7 个音效中仅猫叫已成功下载，其余 6 个官方 CDN 下载返回 403。未完成前不应把下列目标目录理解为已存在的音频文件。
>
> 当前仅作为素材库保存，不代表已经接入游戏逻辑。家门口沿用 `BGM/home/` 中对应季节与昼夜的曲目。

## 目录

- `BGM/home/`：居家四季昼夜 8 首；同时供家门口复用。
- `BGM/park/`：公园四季 4 首。
- `BGM/mall/`：商场主曲《人潮高光》。
- `BGM/bar/`：酒吧《琥珀低音》《杯中日光》。
- `BGM/harbor/`：海边码头《雾港归帆》。
- `SFX/`：计划收录的 7 个 CC0 音效，文件名为英文，用途见下表；实际入库情况见上方状态说明。
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
| 商场 | `mall/mall-crowd-rush.mp3` | 122 BPM 热闹舞曲流行；含用户确认的第 3、6 音改音 |
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
