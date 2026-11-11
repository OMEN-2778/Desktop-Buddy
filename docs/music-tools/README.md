# 音乐技能安装与交接（2026-11-11）

用户明确要求从 GitHub 下载作曲技能；最看重旋律，喜欢舞厅《镜球亮起来》，不满意近期模板化短句。需要用参考分析、动机发展和真实试听改善作曲，技术通过不代表旋律好听。

## 已安装且实测
- 项目技能 `.claude/skills/music-compose/SKILL.md`：参考分析、作曲、编配、保留已选片段；Tonal + @tonejs/midi 已安装。运行 inspect-midi 成功读取舞厅MIDI；transpose 工具兼容 Node 24 的导入已修复。
- 项目技能 `.claude/skills/music-evaluate/SKILL.md`：按作曲/编配/制作阶段评价；音频检测成功读取舞厅MP3。
- 外部 `/workspace/extra-skills/spectro-maestro/SKILL.md`：完整合成/混音/导出工具，独立 venv 为 `/workspace/extra-skills/music-venv`。纯器乐依赖检查通过，已运行 keys_piano audition，生成 WAV/图。此次为工具冒烟测试，不是交付新曲或听感通过。

## 使用
```sh
cd .claude/skills/music-compose
npm ci --cache /tmp/music-npm-cache --ignore-scripts
node --experimental-strip-types scripts/inspect-midi.ts /absolute/path/song.mid
node --experimental-strip-types scripts/transpose-midi.ts /absolute/path/in.mid /tmp/out.mid --semitones 2
```
```sh
node --experimental-strip-types .claude/skills/music-evaluate/scripts/inspect-audio.ts AUDIO_LIBRARY/BGM/disco/disco-glitter.mp3
MPLCONFIGDIR=/tmp/music-mpl SPECTRO_MAESTRO_CACHE_DIR=/tmp/music-cache /workspace/extra-skills/music-venv/bin/python /workspace/extra-skills/spectro-maestro/scripts/studio.py doctor
```

## 换环境后恢复外部工具
来源及固定 commit 见 sources.json。clone music-agent-skills 到外部目录并 checkout 该 commit，复制 `skills/spectro-maestro/en/spectro-maestro/` 到 `/workspace/extra-skills/spectro-maestro`，保留 LICENSE/第三方声明。新建独立 Python venv，pip install -r 该技能 requirements.txt，然后重新跑 doctor、audition。
Spectro Maestro 工具代码为 AGPL，保留在项目外部；其上游明确输出音频/MIDI不受该工具AGPL约束。MIT项目技能保留许可证。

## 已下载候选，未验证为可用能力
- claude-music：ACE-Step 1.5 生成音乐，需要额外模型与运行时。当前没有检测到 NVIDIA GPU；未安装其大模型或测试 CPU 推理，不能声称已经能生成模型音乐。
- orchestral-midi-skill：明确乐谱和可重复管弦渲染；源码已下载，CLI 未安装验证。
- midi-skills：音色/风格/渲染指南，已下载，未应用。
- musicxml-agent-skills：MusicXML指南候选，未初始化外部子模块或验证。

## 测试边界
MIDI元数据、音频格式、器乐合成已验证；人声/歌声模型、LMMS工程重渲染、ACE-Step推理未测。不要把元数据报告说成已完成旋律审美分析。新作优先验证动机和乐句，不以换音色或数值合格代替用户评价。
