# UI 排版与动效 skills

已从 8 个上游仓库安装 20 个项目级 skill，覆盖布局、字体、层级、视觉打磨、
交互反馈、转场、动效节奏、性能与可访问性。这是本次搜索后安装的清单，
不是全网所有 skill 的穷尽目录。

实体在 `.agents/skills/`，`.claude/skills/` 通过相对软链接共用，供 Codex 和
Claude Code 发现。当前会话可以直接读取对应 `SKILL.md`；新会话的自动发现
取决于客户端支持，必要时重开会话。不需要把全部内容同时加载。

## 按任务选择

| 任务 | Skill | 来源 |
| --- | --- | --- |
| 排版、间距、层级、字体、配色、视觉审查与打磨 | `impeccable`，按需读取 `reference/layout.md`、`typeset.md`、`polish.md`、`animate.md` | [Impeccable](https://github.com/pbakaus/impeccable) |
| 本地检索字体搭配、配色、布局与交互建议 | `ui-ux-pro-max` | [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| 视觉方向与有辨识度的界面 | `frontend-design` | [Anthropic Skills](https://github.com/anthropics/skills) |
| 布局基础、现有界面整理、设计规范提取 | `baseline-ui`、`improve-ui`、`create-design-md` | [UI Skills](https://github.com/ibelick/ui-skills) |
| 键盘、焦点、可读性与辅助功能 | `fixing-accessibility` | [UI Skills](https://github.com/ibelick/ui-skills) |
| 动效掉帧、布局抖动、合成与绘制开销 | `fixing-motion-performance` | [UI Skills](https://github.com/ibelick/ui-skills) |
| 动效的情绪、节奏、缓动与编排 | `motion-design` | [LottieFiles](https://github.com/LottieFiles/motion-design-skill) |
| 创建或审查微交互，按使用频率控制动效强度 | `design-motion-principles` | [Design Motion Principles](https://github.com/kylezantos/design-motion-principles) |
| 菜单、弹窗、面板、提示、标签切换等 CSS 动效范例 | `transitions-dev` | [Transitions.dev](https://github.com/Jakubantalik/transitions.dev) |
| 统一时长、缓动、位移与缩放参数 | `transitions-polish` | [Transitions.dev](https://github.com/Jakubantalik/transitions.dev) |
| GSAP 基础、时间线、工具与性能 | `gsap-core`、`gsap-timeline`、`gsap-utils`、`gsap-performance` | [GSAP 官方 Skills](https://github.com/greensock/gsap-skills) |
| GSAP 插件、滚动、框架与 React 专项，使用相应技术时再加载 | `gsap-plugins`、`gsap-scrolltrigger`、`gsap-frameworks`、`gsap-react` | [GSAP 官方 Skills](https://github.com/greensock/gsap-skills) |

## 本游戏的使用约定

- 用户的要求和已有 `.claude/skills/pixel-art/SKILL.md` 优先，保留像素风、
  固定调色板、安静的主画面与既有交互轮廓规则。
- 通用网页建议要按游戏场景判断。不要因为 skill 示例使用 React、Tailwind、
  Motion 或 GSAP，就替换现有原生 JS、CSS、Canvas 或添加运行时依赖。
- 每次选择最相关的一个主 skill，再按问题补读参考文件；不同时套用所有规范，
  不强行把字体和动效风格混在一起。
- 高频按钮与菜单应反应及时；偶发的情绪反馈可以更有表现力。沿用减少动态设置。
- 本次只安装开发参考资料和配套工具，没有修改游戏 UI、玩法或打包 EXE。

## 工具验证与来源

本地设计检索（无需 API key）：

```bash
python3 .agents/skills/ui-ux-pro-max/scripts/search.py "spacing hierarchy" --domain ux --max-results 2
python3 .agents/skills/ui-ux-pro-max/scripts/search.py "readable typography" --domain typography --max-results 1
```

Impeccable 引擎检查：

```bash
.agents/skills/impeccable/scripts/impeccable engine-probe
```

该启动器固定引擎版本，首次运行下载并校验 SHA-256，缓存放在本项目
`scripts/.cache/`，已忽略提交；Windows 仍用上游 `.cmd` 启动器。
排版资料、动效范例和 GSAP 指南均可直接按文件读取。GSAP skill 的安装
不等于游戏已引入 GSAP 库。

上游地址、固定提交、源路径、SKILL.md 校验值和两处路径适配记录在
[ui-skills-sources.json](ui-skills-sources.json)。各目录保留上游许可证和通知；
更新时按对应来源获取，保留本地路径适配，重新检查引用与检索工具。
