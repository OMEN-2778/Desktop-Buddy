# 居家四季 BGM

同一主题旋律的四季居家背景音乐，全部纯代码合成（无采样素材），无缝循环。
本目录目前只存放合成脚本与说明；音频文件（MP3/WAV）需另行上传，或用脚本一键重新生成。

## 曲目

| 文件（待上传） | 时长 | 速度 | 风格 |
| --- | --- | --- | --- |
| spring-day.mp3 / spring-night.mp3 | 96 s | 80 BPM | 定稿基准版：Rhodes + 柔笛（白天）/ 抒情软钢琴（夜晚），Lo-fi 慢拍 |
| summer-day.mp3 / summer-night.mp3 | 87.3 s | 88 BPM | 钢鼓 + 马林巴、反拍和弦、四踩；夜晚改软钢琴、鼓低通、背景马林巴关闭 |
| autumn-day.mp3 / autumn-night.mp3 | 106.7 s | 72 BPM | 尼龙指弹 + 软钢琴、无刷子无沙锤；夜晚软钢琴独奏、鼓更轻 |
| winter-day.mp3 / winter-night.mp3 | 128 s | 60 BPM | 钢片琴 + 长弦乐 Pad、大混响、心跳底鼓；夜晚更薄更静、撤铃音 |

旋律数据：96 个音符，含用户在旋律编辑器中的三处改音
（第49音 D5→C5、第53音 A5→G5、第78音 A5→G5），昼夜与四季共用。

## 重新生成

依赖：Python 3、numpy、scipy、ffmpeg。

```bash
python3 make_lofi_bgm_v2_long.py   # 春（基准版）昼夜，96 秒，输出 spring-白天/夜晚.wav+mp3
python3 make_seasons_bgm.py        # 夏 / 秋 / 冬昼夜，输出 宅家四季-季节[-夜晚].wav+mp3
```

脚本会同时输出 WAV（游戏内无缝循环建议用 WAV）与 MP3（试听）。

注意：当前只是存放素材，尚未接入游戏；接入时按 季节 × 昼夜 选择对应文件即可。
