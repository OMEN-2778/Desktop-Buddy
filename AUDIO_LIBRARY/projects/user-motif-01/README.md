# 用户动机无主题BGM 01

核心动机来自用户钢琴卷帘截图：G A C G G A C G A C。按16格对应一小节暂定，落点为0/2/4/7/9/10/11/12/13/14格，每格四分之一拍；112BPM，G4/A4/C5。截图没有足够信息确定实际八度、速度与时间轴缩放，此版本可依用户试听修正。

## 重建
使用 docs/music-tools/sources.json 固定版本的 Spectro Maestro 与独立venv：
```sh
MPLCONFIGDIR=/tmp/music-mpl SPECTRO_MAESTRO_CACHE_DIR=/tmp/music-cache /workspace/extra-skills/music-venv/bin/python /workspace/extra-skills/spectro-maestro/scripts/studio.py lint AUDIO_LIBRARY/projects/user-motif-01/song.yaml
MPLCONFIGDIR=/tmp/music-mpl SPECTRO_MAESTRO_CACHE_DIR=/tmp/music-cache /workspace/extra-skills/music-venv/bin/python /workspace/extra-skills/spectro-maestro/scripts/studio.py render AUDIO_LIBRARY/projects/user-motif-01/song.yaml --formats wav,mp3,mid -o /tmp/user-motif-render
```
内部title使用英文，因为工具的MIDI导出默认latin-1；试听页使用中文标题。

music-compose用于保留源动机、动机发展、和声与分段决策；music-evaluate记录检查证据与边界。Spectro Maestro负责实际合成/混音/导出，非仅音色更名。工程不复用技能starter旋律。纯器乐BGM、约95秒；合成拨弦主奏、电钢琴、模拟贝斯、轻鼓组与温暖音垫。用户动机和延展段来源在song.yaml和source-motif.json记录。听感仍需用户确认。
