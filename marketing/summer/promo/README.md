# 草帽湾宣传视频（1920×1080，47.5 秒，80 年代电视广告风）

主人 2026-11-06 要的：热烈、回弹、不规则构图、弹出贴纸、展示新内容/风景/玩法/UI，一分钟以内。

1. `cap.js`：在季节测试页（`desktop/dist/map-test/index.html`）里录 草帽湾 各个场景，写 `marks.json`。
2. 用 ffmpeg 按 marks 把每段裁成 30fps 的 jpg 序列到 `clips/<名字>/`（游戏画面左右各裁 60px 去掉箭头），`clips/info.json` 记尺寸帧数。
3. `promo.html`：时间轴（每个元素都由 t 算出位置，逐帧确定）；把 `__INFO__` 换成 info.json 存成 `p.html`。
4. `render.js`：逐帧截图到 `frames/`，导出音效时间点 `snd.json`。
5. `audio.py`：《向着海风出发》（BGM/seasons/summer-day.mp3）+ 季节 UI 音效 → `mix.wav`；
   `ffmpeg -framerate 30 -i frames/%05d.jpg -i mix.wav -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac out.mp4`。
贴纸图（hat、coconut、角色立绘等 16px 小图）来自海报那次导出的游戏图。成片不进仓库（约 40 MB）。
