# 音频授权与来源台账

核查日期：2026-10-25。

## BGM

`BGM/` 中 16 首均为本项目通过 Python 合成的原创音乐，不使用第三方录音采样。合成工程位于 `SOURCE/`。这些文件不套用第三方音效的许可证；仓库整体使用方式仍由项目所有者决定。

## 第三方音效：统一为 CC0

下列资产均在对应 Freesound 页面标记 **Creative Commons 0**。页面许可说明为：可以复制、修改、分发和表演，包括商业用途，无需向作者请求许可。为避免误用，本包没有混入 CC BY、CC BY-NC 或许可证不明的文件。

本包保存的是官方公开 **HQ MP3 预览**，不是登录后下载的原始 WAV/FLAC。预览文件仍来自对应资产页面；若需要无损制作，可到原页面登录下载。

| 本地文件 | 原始资产与作者 | Freesound ID | 原始页面 | 用途 |
|---|---|---:|---|---|
| `cat-meow-cc0.mp3` | `cat meow`，tuberatanka | 110011 | https://freesound.org/s/110011/ | 猫短叫、门前橘猫 |
| `cat-purr-meow-cc0.mp3` | `cat purring and meow`，skymary | 412016 | https://freesound.org/s/412016/ | 呼噜与回应 |
| `rain-soft-loop-cc0.mp3` | `Soft Rain Loop`，_lynks | 595717 | https://freesound.org/s/595717/ | 细雨循环 |
| `rain-heavy-window-cc0.mp3` | `1 minute of heavy rain shower`，Andron827 | 720153 | https://freesound.org/s/720153/ | 暴雨、窗边雨 |
| `thunder-heavy-no-rain-cc0.mp3` | `Heavy Thunder Strike - no Rain - QUADRO.wav`，BlueDelta | 446753 | https://freesound.org/s/446753/ | 强雷、近雷 |
| `crowd-indoor-walla-cc0.mp3` | `pre talk show crowd.mp3`，brigitte.perchiste | 529802 | https://freesound.org/s/529802/ | 室内人群底层，含德语交谈 |
| `crowd-small-laugh-cc0.mp3` | `Crowd laugh.wav`，deleted_user_2104797 | 324894 | https://freesound.org/s/324894/ | 小群人短笑声 |

CC0 法律文本：https://creativecommons.org/publicdomain/zero/1.0/

## 下载地址记录

构建脚本使用同域官方预览地址，路径格式为：

```text
https://cdn.freesound.org/previews/{ID前三位}/{ID}_{上传者数字ID}-hq.mp3
```

每个完整 URL 固定在 `tools/build_audio.py` 的 `CC0_SFX` 中，便于审计与重新下载。即使 CC0 不强制署名，本台账仍保留作者和原始链接，方便追溯。

## 使用注意

- CC0 不代表可以把第三方素材谎称为自己的原始录音；保留本台账。
- 人群录音可能包含可辨认语言，使用前应试听并控制音量。
- 强雷与笑声不适合短周期循环，应使用随机、低频率事件触发。
- 新增素材时必须逐条记录许可证，不得仅凭网站名称推断全站可商用。

## 游戏新增音效与播放副本

`SFX/game/` 的 37 个音效由 `tools/build_game_sfx.py` 确定性合成，使用正弦波、滤波噪声和包络，不引用第三方录音；沿用游戏源码授权。

`SFX/processed/` 为上文 7 个 CC0 音效的游戏播放副本（单声道、裁剪、音量平衡、短循环接缝处理），仍使用原有 CC0 授权，原录音和作者来源均保留。具体裁剪记录见 `PLAYBACK_SAMPLES.json`。

## 公园实录环境（2026-10-25）

已逐页核验以下三份录音为 CC0 1.0（https://creativecommons.org/publicdomain/zero/1.0/）。下载官方 HQ MP3，保留原件；播放副本只做裁剪、音量平衡及接缝处理，不合成自然声音。

|文件|作品及作者|原始页|
|---|---|---|
|park-wind-cc0.mp3|Wind through trees (loop)，NomadApe|https://freesound.org/people/NomadApe/sounds/444921/|
|park-birds-cc0.mp3|Park Birds [Clean].wav，Shankfosho|https://freesound.org/people/Shankfosho/sounds/688301/|
|park-leaves-cc0.mp3|large leaves rustle in the wind sound effect，Garuda1982|https://freesound.org/people/Garuda1982/sounds/575645/|

## 生活拟音实录替换

以下素材各自的 Freesound 详情页或对应搜索结果条目均明确标为 Creative Commons 0；不是仅凭搜索条件推定。下载源和逐项记录另见 `REAL_FOLEY_SOURCES.json`。原件保留，游戏使用裁剪和平衡音量后的副本。

|文件|作品／作者|来源与授权|
|---|---|---|
|real-water-running-cc0|Tap Water 1／OwlStorm|https://freesound.org/people/OwlStorm/sounds/212177/ · CC0 1.0|
|real-pour-water-cc0|R23-22-Water Poured from Bottle.wav／craigsmith|https://freesound.org/people/craigsmith/sounds/482857/ · CC0 1.0|
|real-page-turn-cc0|Book page turning.wav／eZZin|https://freesound.org/people/eZZin/sounds/641757/ · CC0 1.0|
|real-keyboard-typing-cc0|Typing on a keyboard／SamsterBirdies|https://freesound.org/people/SamsterBirdies/sounds/489424/ · CC0 1.0|
|real-cutlery-cc0|cutlery utensil spoon fork knife down plate nice detail roomy.wav／kyles|https://freesound.org/people/kyles/sounds/450783/ · CC0 1.0|
|real-drink-cc0|Coffee Sips.wav／sidequesting|https://freesound.org/people/sidequesting/sounds/530247/ · CC0 1.0|
|real-toilet-flush-cc0|Flush_toilet.wav／martingunchev|https://freesound.org/people/martingunchev/sounds/346061/ · CC0 1.0|
|real-cooking-fry-cc0|frying_pan_sizzle.WAV／beehawk5|https://freesound.org/people/beehawk5/sounds/620441/ · CC0 1.0|

## 环境层与生活细节扩展

以下新增素材已核对 Freesound 对应条目的 Creative Commons 0 标记。优先下载官方 HQ 预览，不可用时使用同一作品的官方 LQ 预览；实际下载 URL 保存在 `REAL_FOLEY_SOURCES.json`。音量、起点和循环参数记录在 `PLAYBACK_SAMPLES.json`，使用处理副本，保留原件。

|文件|作者／作品|来源|
|---|---|---|
|real-door-cc0|kyles／door wood interior solid bathroom open close.flac|https://freesound.org/people/kyles/sounds/637492/ · CC0 1.0|
|real-fabric-cc0|Sonicquinn／Fabric-Sofa-Rubbing-Movements_Mono_192000.wav|https://freesound.org/people/Sonicquinn/sounds/435830/ · CC0 1.0|
|real-chair-cc0|cupido-1／drag chair moving|https://freesound.org/people/cupido-1/sounds/616824/ · CC0 1.0|
|real-cup-cc0|danielle.k.tiflin1201／Placing Cup On Table.wav|https://freesound.org/people/danielle.k.tiflin1201/sounds/595764/ · CC0 1.0|
|real-ice-cc0|nifigasebesharik／Ice cubes in a red wine glass (mic outside the glass)|https://freesound.org/people/nifigasebesharik/sounds/784070/ · CC0 1.0|
|real-shaker-cc0|KenRT／Cocktail Shaker.wav|https://freesound.org/people/KenRT/sounds/319995/ · CC0 1.0|
|real-lake-cc0|Anya_Media／Lake waves.wav|https://freesound.org/people/Anya_Media/sounds/523392/ · CC0 1.0|
|real-boat-cc0|Walter_Odington／ship_creak.mp3|https://freesound.org/people/Walter_Odington/sounds/31574/ · CC0 1.0|
|real-horn-cc0|Danjocross／Long Distant Foghorn.aiff|https://freesound.org/people/Danjocross/sounds/507471/ · CC0 1.0|
|real-night-cc0|Defelozedd94／Crickets At Night - Raw sound|https://freesound.org/people/Defelozedd94/sounds/522299/ · CC0 1.0|
|real-fridge-cc0|babuhr／Fridge door1.wav|https://freesound.org/people/babuhr/sounds/513340/ · CC0 1.0|
|real-auto-door-cc0|Kyodon／automatic door.wav|https://freesound.org/people/Kyodon/sounds/153423/ · CC0 1.0|
|real-sea-cc0|kkenny101／Gentle Ocean Waves Loop|https://freesound.org/people/kkenny101/sounds/852826/ · CC0 1.0|
|real-gulls-cc0|steaq／Seagull single call|https://freesound.org/people/steaq/sounds/263786/ · CC0 1.0|
|real-boil-cc0|kyles／water boiling in pot hollow1.flac|https://freesound.org/people/kyles/sounds/637935/ · CC0 1.0|
|real-checkout-cc0|videofueralle／cash register beep sound.wav|https://freesound.org/people/videofueralle/sounds/455397/ · CC0 1.0|

## 原创情绪短旋律

`SFX/game/emotion-*.mp3` 共 17 段，由 `tools/build_emotion_cues.py` 独立编写 MIDI 音列、节奏、音色和鼓点后合成，未使用其他游戏录音或旋律。素材使用游戏源码相同授权；设计与音列见 `docs/EMOTION_CUES.json`。
