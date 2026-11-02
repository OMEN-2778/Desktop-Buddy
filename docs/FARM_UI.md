# 农庄 / 丢丢币 UI（可进游戏的版本）

2026-11-02：用户不接受 Codex 的生成式概念图（`design/spring-ui-board.png`，只作方向参考），
要求画能直接进游戏的 UI。本版全部用游戏现有组件 + pixelkit 像素图标实现。
**状态：审图中，未接入正式游戏**（make_demo.py / 发布流程都不包含）。

审图总览：[design/farm-ui-board.png](design/farm-ui-board.png)（50% 档实拍）。

## 组件对应
| # | 界面 | 用的现有组件 |
|---|---|---|
| 1 | 机场航班 | 环形菜单（一圈气泡）：春季农庄 · 免费，三个 ？ 灰掉 |
| 2 | 剧情对话 | `story_bubbles.js` 说话人头顶气泡，任务对白白→浅蓝 |
| 3 | 妈妈来信 | 写信日信件（日记里「信件 · 展开」），票已由父母买好 |
| 4/7 | 菜地 / 果树操作 | 环形菜单 + 图标；不能做的项灰掉并写原因 |
| 5/9 | 种子铺 / 牲畜铺 | 物品面板（`#picker`），标题栏丢丢币余额，钱不够写「还差 x 币」 |
| 6 | 作物详情 | 房屋大小的 social-sheet：四个生长阶段（菜地原图）、浇水、预计收入、进度条 |
| 8 | 牧场 | social-sheet：鸡/羊/牛分页、饮水/饲料像素图标格、添水/喂草/收取 |
| 10–12 | 丢丢电脑 | social-sheet：左栏 农庄/丢丢币/每日操盘/礼物与藏品；走势图在房屋像素格上阶梯绘制 |

## 文件
- `art/src/concept/farm_icons.py` → `art/out/concept/farm_icon_*.png`（25 个 16×16，1×/2× 整数显示）。
  作物阶段、果树、动物直接用 `spring_fields` / `_farmstead` 原图，不重画。
- `prototype/demo/farm_ui.js` + `farm_ui.css`：`FarmUI.ring / shop / plant / ranch / computer`，只负责画，
  数据由调用方传入；规则以 `DIDI_CURRENCY.md` 为准。
- 审图：`PYTHONPATH=tools python3 tools/make_farm_ui_preview.py`（先 make_demo + npm ci）→
  `desktop/dist/farm-ui/`；`prototype/farm-ui/preview.js` 的 `farmPreview.show(1..12)`；
  `node tools/check_farm_ui.js <输出目录> 100,50,25` 截图并检查页面报错。

## 接入时要做（用户通过后）
- make_demo.py 打包图标与模块；`ringPick` / `command` 接上真正的种田、经营动作；电脑环形菜单加「丢丢电脑」。
- 试玩版关闭；四档 UI 检查（check_ui_layout.js）补上这些面板。25% 档弹窗内部滚动。
- 还缺的美术：三季农庄、田块状态（荒地/空地/湿土/缺水）、Buddy 农活动作、小牛小鸡。
