# 桌面 UI 排版约定

验收档位是 25%、50%、75%、100%。`setScale()` 调整场景像素；文字不能随场景
不断缩小，也不能因浏览器窗口宽度改变而换另一套规则。暂不做手机适配。

## 单一入口

- `prototype/demo/ui_layout.js`：实际游戏宽度 → 字号、间距、组件密度。所有字号
  在 `sizeGameUi()` 中一次赋值，不在子组件里再乘缩放系数。
- `prototype/demo/ui.css`：页面、常驻栏、设置、日记、菜单、教程和机会卡。
- `prototype/demo/social_hud.css`：需求、人脉、来电、社交弹窗、性格编辑。
- `prototype/demo/peer_dialogue.css`：对方说话的动画与外观，文本测量共用 `fitText()`。
- `prototype/shared/studio.css`：更衣室和独立造型室；统一选项网格与像素小圆角。

同一组件的基础选择器只保留一处定义；修改原规则，不在文件尾不断叠加补丁。
打开、选中、紧凑布局和减少动态模式使用明确的状态选择器。
`hidden` 属性的不可见状态优先于布局规则，紧凑布局不能让隐藏弹窗重新显示。

## 文字、对齐和边界

常用 CSS 变量：`--ui-font-caption`、`--ui-font-label`、`--ui-font-body`、
`--ui-font-control`、`--ui-font-heading`、`--ui-font-card-title`、
`--ui-font-card-body`、`--ui-font-name`、`--ui-font-pill`、`--ui-font-speech`。

- 游戏内可见文字最低 12px，主要正文最低 13px，机会卡标题最低 20px。
- 普通中文长标题/条目允许换行，不用缩字或省略号来隐藏菜单条目。
- 对话/日记按正常字号测量高度，向上展开，不挤压场景或时间条；完整文字保持可读。
- 机会卡、结果、饮食/电影/书籍等菜单和社交弹窗必须卡住房屋尺寸。
  固定标题，正文在内部滚动；社交弹窗用 `socialContent()` 分离内容和操作区。
- 人脉固定父母在前，四字姓名完整显示；小组件改排列方式，不能把字挤没。
- 需求面板在四档都保持六根一排。特别窄的显示缩放下，面板整体向上浮出以保留文字空间，不越过右边时间条。需求、物品、造型网格按列对齐；选中加粗不能改变行高或列宽。
- 六类造型选项和页签共用 `--st-option-clip` 与 `--st-option-in`，4px 阶梯小圆角、
  2px 框线。禁止平滑大圆角/胶囊。人物与像素预览坚持整数缩放。
- 动画只操作透明度和变换；不要用动画改字号、布局宽高或存档状态。

## 验收

先在隔离的验证目录构建，源仓库不提交生成的 `prototype/demo/index.html`，
避免触发 Windows EXE 工作流。

```sh
PYTHONPATH=tools python3 tools/make_creator.py
PYTHONPATH=tools python3 tools/make_demo.py
node desktop/scripts/copy-web.mjs
```

`node tools/check_ui_layout.js <预览地址>` 按四档实际打开各面板，检查字号、
文字横向溢出、可滚动内容区高度及房屋边界，保存 `report.json`、截图和
`review.html`。`UI_DPR=1.25` 可复查 Windows 显示缩放；`UI_DESKTOP_SHELL=1`
复查桌面窗口的 CSS 布局，`UI_THEME=dark` 复查深色主题。自动检查后仍须查看实图。

`check_card_typography.js` 遍历整副牌；`check_card_result.js` 验证结果和气泡；
`check_studio_layout.js` 验证六页签；`check_contact_fit.js` 验证姓名、显示缩放和
滚动；社交、电话、存档、暂停及来访仍由原有集成检查验证。
