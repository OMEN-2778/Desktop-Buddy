# 草帽湾宣传视频（1920×1080，47.5 秒，80 年代电视广告风）

主人 2026-11-06 要的：热烈、回弹、不规则构图、弹出贴纸、展示新内容/风景/玩法/UI，一分钟以内。

1. `cap.js`：在季节测试页（`desktop/dist/map-test/index.html`）里录 草帽湾 各个场景，写 `marks.json`。
2. 用 ffmpeg 按 marks 把每段裁成 30fps 的 jpg 序列到 `clips/<名字>/`（游戏画面左右各裁 60px 去掉箭头），`clips/info.json` 记尺寸帧数。
3. `promo.html`：时间轴（每个元素都由 t 算出位置，逐帧确定）；把 `__INFO__` 换成 info.json 存成 `p.html`。
4. `render.js`：逐帧截图到 `frames/`，导出音效时间点 `snd.json`。
5. `audio.py`：《向着海风出发》（BGM/seasons/summer-day.mp3）+ 季节 UI 音效 → `mix.wav`；
   `ffmpeg -framerate 30 -i frames/%05d.jpg -i mix.wav -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac out.mp4`。
贴纸图（hat、coconut、角色立绘等 16px 小图）来自海报那次导出的游戏图。成片不进仓库（约 40 MB）。

## 第二版：海岛极繁主义（主人 2026-11-06：装饰要多、海岛风、开头小人打开电视再钻进屏幕）
- `cap2.js` 录主世界客厅：晚上她下楼开电视、坐沙发（`home_tv`），结尾她看完的画面（`home_happy`），裁成 clips 同上。
- `promo2.html`：夏威夷衬衫印花背景（扶桑花、龟背竹、棕榈叶）、四角摇摆的叶子、海浪、太阳、上下滚动的字幕彩带、飘落的花瓣、
  明信片（胶带、邮票、邮戳）和拍立得、矢量贴纸（扶桑花、海星、菠萝、西瓜、椰子饮料、冲浪板、墨镜、贝壳、花环）加游戏像素贴纸；
  镜头 0–4.9 秒在客厅，4.9–6.3 秒推进电视屏幕，50.4–51.6 秒拉回，最后“好想去草帽湾！”。`render2.js` 出帧到 frames2/，
  `python3 audio.py 55.2 4.6`（音乐从开电视后开始，回到客厅时变小）。
