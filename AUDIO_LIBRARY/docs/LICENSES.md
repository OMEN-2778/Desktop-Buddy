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
