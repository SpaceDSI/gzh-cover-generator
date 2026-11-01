---
name: gzh-cover-generator
version: 5.7.5
display_name: 公众号文章封面图
display_name_en: gzh-cover-generator
icon: assets/avatar.png
author: 青灯墨染
category: design-media
description: Create high-impact Chinese WeChat/公众号 cover images at 2.35:1 using deterministic typography over an imagegen background. Ships 14 cover styles that all participate in an automatic weekday rotation — each weekday owns 2 looks (base + alternate) alternating by ISO week parity (周一 ECONOMIST↔HELVETIC / 周二 MONOCLE↔AEGEAN / 周三 NEW YORKER↔BROADSHEET / 周四 WIRED↔DECO / 周五 KINFOLK↔CLEAN / 周六 HARVARD↔AGENT / 周日 TECH↔CODEX). Covers are typographic — no portrait or avatar. Trigger for 公众号封面、公众号头图、微信封面、爆款封面、封面风格轮换、2.35:1 cover.
description_zh: 生成高质感的微信公众号文章封面图（2.35:1）：内置 14 套杂志级风格，每个星期 2 套按 ISO 周奇偶自动交替（相邻两周同一天不重样）；采用 imagegen 生成背景 + 代码精确渲染中文标题的流程，新增 4 套风格封面文字统一思源黑体 Bold，纯文字排版、不含任何人物头像；默认「左标题 + 右主视觉」版式：主题场景生成在右侧并自动居中于右 42.6% 1:1 分享区（x 1350–2350），分享预览即这块主体；并自动去除 ImageGen 烙在角落的「AI生成/WORKBUDD」角标水印，默认无水印交付。触发词：公众号封面、公众号头图、微信封面、爆款封面、封面风格轮换、2.35:1 封面。
description_en: "Generate high-impact WeChat official account article covers at 2.35:1, with 14 built-in magazine-grade styles that rotate automatically by weekday — two looks per weekday alternating by ISO week parity. Uses an imagegen-generated background with code-rendered exact Chinese typography (the 4 newest styles set in Source Han Sans Bold) — purely typographic, no portrait or avatar. Default layout is left-headline + right hero: the theme scene is generated on the RIGHT and auto-centred inside the right 42.6% 1:1 share slice (x 1350–2350), so the share preview is that scene. Trigger for WeChat article covers, official account banners, viral covers, cover style rotation, and 2.35:1 covers."
agent_created: true
---

# WeChat Cover ImageGen Skill / 公众号文章封面图

## 介绍 / Overview

输入文章标题和一句话主题，直接产出可发布的公众号封面（2.35:1）：AI 生成主题场景背景，代码精确渲染中文标题（默认「左标题 + 右主视觉」：文字居左约 52%，主题场景生成在右侧、并自动居中到右 42.6% 分享方形 x 1350–2350，该 1:1 切片即本技能的正式分享预览与交付标准）；内置 14 套杂志级风格，每个星期 2 套按 ISO 周奇偶自动交替，相邻两周同一天不重样。

Supply an article title and a one-line topic to get a publish-ready 2.35:1 WeChat cover: an AI-generated theme-scene background with code-rendered exact Chinese typography. Default layout is left-headline + right hero (text on the left ~52%, the theme scene generated on the RIGHT and auto-centred inside the right 42.6% 1:1 share slice, x 1350–2350). 14 magazine-grade styles rotate automatically by weekday (two looks per weekday, alternating by ISO week parity). Typographic only — no portrait, no avatar.

**能力 / What it does**

- **14 套杂志级风格全轮换**：每个星期槽位固定配对 2 套——基准套（ISO 偶数周）+ 候补套（ISO 奇数周）：周一 ECONOMIST↔HELVETIC 瑞士网格 / 周二 MONOCLE↔AEGEAN 爱琴海明信片 / 周三 NEW YORKER↔BROADSHEET 号外 / 周四 WIRED↔DECO 盖茨比之夜 / 周五 KINFOLK↔CLEAN / 周六 HARVARD↔AGENT / 周日 TECH↔CODEX。2026-10 新增的 4 套封面文字统一**思源黑体 Bold**；用户不点名风格时一律走星期轮换，不按文章主题替他挑风格。
- **文字精准不错字**：背景由 ImageGen 生成，中文标题、刊头、副标、底部标签全部由代码渲染，可精修、可复现。
- **右侧主题场景（主视觉，默认版式）**：标题块占左侧约 **52%**，右侧（**右 42.6% 区，x 1350–2350**）留给 **ImageGen 主题场景**，渲染时由 `scripts/position_scene.py` **自动把主体居中**到该 1:1 方形（按局部梯度能量测主体跨度，再水平平移、留白无缝延展）。场景按**文章标题与主旨**自动生成 9 种电影级场景（信息传送门 / 自动化飞轮 / 桌面实物 / 数据流 / 内容画廊 / 阶梯增长 / 知识图谱 / 清单卡片 / 改革减法），语义同频、绝不侵入标题排版（见 `references/scene-archetypes.md`）。轻量矢量点缀层（`right_motif`）**已默认关闭**（2026-10-25 起弃用，改由场景承载主视觉）。
- **分享区版式（`share_side`，默认 `right`）**：2.35:1 封面分享时微信会裁 1:1 方形。默认「左标题 + 右主视觉」：
  - `right`（**默认，也是本技能的正式交付版式**）：标题占左约 52%，主题场景在右侧并自动居中到**右 42.6% 1:1 方形（x 1350–2350）**；`check_cover` 默认按右侧导出 `-share-1x1.png`，**这块 1:1 切片就是交付验收的分享预览**。
  - `center`（可选）：标题占左约 28%、场景居中于中央方形（x 675–1675），预览走中央裁剪；仅当用户明确要求「分享图里也要显示场景居中」时才切换。
  - 交付口径：**以 `-share-1x1.png`（右 42.6% 切片）为准**。横幅整体观感与右切片观感都要过检，不存在「横幅优先、切片可以牺牲」的豁免——若右切片里场景被裁、被压或残缺，即判不合格，须重排或重出背景。
  交付前用 `check_cover.py [--share-side {right|center}]` 导出对应裁剪图核对（默认 right）。
- **无水印交付（默认，5.7.4）**：`scripts/remove_watermark.py` 自动检测并抹除 ImageGen 烙在角落的「AI生成 / WORKBUDD」淡角标——用极贴角窄带 + 局部对比度 + 大窗口平坦度 + 文字形状（≥2 笔画、无单一巨块主导）四判据联合定位，再以「框外环带均值色 + 匹配颗粒」整块填平，不伤主视觉；已接入 `render_wechat_cover.py::load_background`，每次渲染自动在 `center_scene` 之前生效，**此后所有封面默认无水印**。
- **分享缩略图裁剪坐标（5.7.5）**：微信分享卡片/转发里的 1:1 缩略图**不是自动居中裁的**，而是由封面素材上的 `pic_crop_1_1` 裁剪窗口决定；不传就回退到封面正中央（右主视觉版式的标题会被切半）。`scripts/share_crop.py` 按 `share_side` 算出 `pic_crop_1_1` / `pic_crop_235_1`（2350×1000 右切片 → `0.574468_0_1_1`），坐标与 `check_cover` 导出的 `-share-1x1.png` **逐像素等价**；`check_cover --safe-zone` 也会直接把该传的值打出来。**建/改草稿时必须带上，否则分享图必然错位**——默认走 `scripts/push_cover.py`（压缩略图 → 传素材 → 换 thumb → 写裁剪坐标 → 回读核验，一条命令完成），不要手写请求体。
- **交付前质检闭环**：比例 2.35:1±0.01、25% 缩略图可读、无人物、文字不压装饰，逐项过检才交付。
- **5.5.3 渲染溢出修正（2026-10-27）**：实测上版仍偶有左栏文字越界中央方形（眉标 fit 下限过大、副标徽章尾标「«」右溢、底部标签 fallback 用 40px 溢出）。本版把眉标/副标 fit 下限降到 30/24、徽章尾标夹在 `right_limit-10`、底部标签改为「找得到最大的能塞进 x675 前的大小、否则降到 10px」绝不溢出，并夹住眉标面板/分隔线右沿，确保左栏所有文字严格止于中央方形左缘（x 675）以内。
- **5.6.0 `share_side` 双版式（2026-10-27）**：新增 brief 字段 `share_side`。`center`（默认）=标题左约 29%/场景居中/导出中央裁剪；`right`=标题左约 52%/场景居右（对标「左标题+右剪刀剪纸」参考版式）/`check_cover --share-side right` 导出右 42.6% 对照预览。`render_wechat_cover.py` 的标题/副标/标签宽度由 `share_side` 驱动（0.28w / 0.52w），`check_cover.py` 新增 `--share-side {center,right,left}`。（5.7.2 起 `right` 已升为正式交付版式，不再只是对照预览。）
- **5.6.1（2026-10-27）**：① 副标下移——`draw_title` 里 badge_y 加 `int(h*0.022)` 并夹在 `bottom_limit-badge_h` 内（用户反馈"副标题偏下一点点"）。② 右裁剪保场景技巧：ImageGen 常把主体画在中间，若要求"右 42.6% 预览只剩主体"，可在 `render` 前用 PIL 将背景整体右移（左侧米色接缝处用最左列边缘延展填平），使主体落入右 42.6%；更好的做法是让 ImageGen 直接出 2.33:1（如 1792x768）避免 fit 裁切切掉主体顶部。
- **5.7.0 右主视觉成为默认并自动居中（2026-10-27）**：把上一轮验证通过的样式固化为技能默认。① `render_wechat_cover.py` 的 `share_side` 默认改为 `right`（标题左约 52%、场景居右）；② 新增 `scripts/position_scene.py`，按**局部梯度能量**测主体水平跨度（不受背景色影响，避开左侧装饰/右缘暗角/底部水印），再把主体**自动居中到目标分享方形**（右 42.6%）并用边缘列无缝补空；`load_background` 默认调用它（brief 里 `auto_center_scene: false` 可关）；③ `check_cover.py` 的 `--share-side` 默认改为 `right`；④ 副标沿用 5.6.1 的下移。仍保留 `center` 版式以匹配微信真实居中裁剪。
- **5.7.1 规格真正生效 + 平台事实修正（2026-10-27）**：① 修默认版式不生效的 bug——`export_imagegen_prompt.py` 的 `share_side` 默认仍是 `center`，与 `render_wechat_cover.py` 的 `right` 打架，导致 AI 背景把场景画在正中央、排版却按「左标题+右主视觉」排；已把提示词脚本默认改 `right`，并让 `build_cover_brief.py` 在 brief 里显式写入 `share_side: "right"` / `auto_center_scene: true`（原来 brief 不带这两个字段，两脚本各自 fallback）。至此默认版式真正跑通：**AI 生成主题场景背景 + 代码精确渲染中文标题**，文字居左约 52%，主题场景生成在右侧并**自动沿右 42.6% 分享方形**居中（x 1350–2350，由 `position_scene.py` 按梯度能量测出主体跨度后平移、边缘列补空），当时附带的「**banner 观感优先**」要求（完整横幅好看即合格）**已在 5.7.2 取消**；② 修正分享裁剪说法冲突：统一为「微信真实裁剪 = 画面**正中央** 42.6%（x 675–1675）」，右 42.6% 切片是本技能默认版式的**对照预览**，不再误写成平台事实（原 Step 5 提示与 `check_cover.py`、版式章节互相打架）；③ 修 frontmatter YAML 语法错误——`description_en` 含 ASCII `: `（"right hero: the"）导致整个 frontmatter 解析失败，已加双引号包裹。
- **5.7.2 右 42.6% 切片升为正式交付版式，取消 banner 优先（2026-10-27）**：① 口径变更——`share_side: right`（左标题 + 右主视觉，场景自动居中于右 42.6% 方形 x 1350–2350）不再只是「对照预览」，而是本技能**默认且正式的交付/验收版式**，`check_cover` 导出的 `-share-1x1.png` 即验收用的分享预览；② **取消「banner 观感优先」这一要求**——删除「完整横幅好看即合格、share-1x1 无标题文字属预期」的豁免条款，横幅观感与右切片观感**并列过检**，右切片里场景被裁/被压/残缺一律判不合格，须重排或重出背景；③ `center` 降级为可选项，仅在用户明确要求场景居中于中央方形时使用；④ 同步清理 `check_cover.py` / `export_imagegen_prompt.py` / `render_wechat_cover.py` 里「对照预览 / banner look is primary」一类与新口径冲突的提示与注释。
- **5.7.4 自动去除 ImageGen 角标水印，固化为默认流程（2026-10-28）**：① 新增 `scripts/remove_watermark.py`——ImageGen 常在背景**角落**烙一行极淡的「AI生成 / WORKBUDD」角标（值约 200，不是纯白，普通「近白」阈值抓不到），本模块自动检测并**整块重绘抹掉**，且完全不伤主视觉。检测用四道判据联合：**极贴角落窄带**（`CORNER_BAND=0.12`，只取同时贴近某角两条边 12% 内的像素，飞轮主体永不进候选）＋**局部对比度**（比高斯模糊局部底色亮 `>16`，专抓淡字）＋**大窗口平坦度**（46px 窗口 std `<38`，水印压在平坦深底、实体亮块压在带光影的场景上，据此区分）＋**文字形状**（邻近聚类后要求 ≥2 个笔画组件、无单一巨块主导 `>0.6`、覆盖率 `<0.55`、块尺寸文字级）。命中后用「框外环带均值色 + 匹配颗粒」**整块填平**（一次覆盖全部文字像素，避免逐像素遮罩漏掉亮边），天然无缝、可复现（按坐标定种）。② 已接入 `render_wechat_cover.py::load_background`：**在 `center_scene` 平移之前、原始背景上**自动调用（水印在原始生成图角落，平移后位置会变），异常则跳过、绝不中断渲染——**此后所有封面默认无水印**。③ 单独清理某张背景：`python scripts/remove_watermark.py background.png --out background.clean.png`。
- **5.7.3 修复右侧主视觉偏小回归（2026-10-28）**：① 根因——`export_imagegen_prompt.py` 右版式构图指令写的是「place the hero scene in the RIGHT **third** of the frame」（右 33% 宽），小于实际的右 42.6% 交付方形（x 1350–2350，1:1＝画布全高）；而 `position_scene.py` 只平移不缩放，导致 AI 按「右三分之一」出图后，右切片里场景偏小、四周留白偏多（之前 center 版式写「fill the CENTER square」≈42.6%，场景能填满切片，即用户记忆里「正常」的观感）。已把指令改为「fill the RIGHT ~42.6% region（1:1 方形）as the visual anchor，场景占该方形宽约 80–90%」，让 AI 直接按交付切片大小出图；② 同时给 `center_scene` 加「缩放补满」保护：当检测到主体宽度 < 分享区宽 72% 时，把整图以主体中心为锚点放大到占区宽约 85%（上限 1.5×，避免重采样糊化），再平移居中，使场景稳定填满右切片、不再随 AI 发挥忽大忽小。
- **5.7.5 分享缩略图改由 `pic_crop_1_1` 控制，右切片真正生效（2026-10-29）**：① 定位真正的根因——**「分享缩略图居中」不是渲染 bug，也不是微信的自动居中裁剪，而是草稿没带裁剪坐标**。微信分享卡片 / 转发 / 历史消息里的 1:1 缩略图，取的是封面素材上的一个裁剪窗口，由 `pic_crop_1_1`（原图左上 0,0 – 右下 1,1 归一化，格式 `X1_Y1_X2_Y2`，≤6 位小数）指定；不传就回退封面正中央，右主视觉版式的标题必被切半。② 新增 `scripts/share_crop.py`：按 `share_side` 算出 `pic_crop_1_1` / `pic_crop_235_1`，并可 `--export` 导出对应 1:1 切片。2350×1000 右切片 → `0.574468_0_1_1`（`pic_crop_235_1` 用 `0_0_1_1`）；与 `check_cover.safe_zone_bounds` 同一套 `share_slice_box`，实测导出图与 `-share-1x1.png` **逐像素相同**。③ `check_cover.py` 在 `--safe-zone` 输出里多打一行「建/改草稿必须带：pic_crop_1_1 = …」，省掉人工换算。④ SKILL.md 新增「🔴 分享缩略图取哪一块，由 pic_crop_1_1 决定」小节 + 草稿推送第 5 条铁律 + Step5 验收项；已知限制：**定时发布中的草稿改不了（53407）**，须先在后台取消定时发布。⑤ 实测：该草稿带 `pic_crop_1_1=0.574468_0_1_1` 重推后 errcode 0，thumb 已切换到右版式封面，用户确认分享卡片显示右切片。⑥ 新增 `scripts/push_cover.py`：把推送闭环封装成一条命令（900px 缩略图自动压到 62KB 内 → `material/add_material?type=thumb` → `draft/get` 取原文保留全部字段 → `draft/update` 写入新 thumb + 裁剪坐标 → 回读核验 thumb 与正文字符数），支持 `--crop-only`（只修裁剪不动图）、`--dry-run`、`--side`；遇到 53407 直接给出「先取消定时发布」的中文提示。

**典型场景 / Typical use**：日常文章出封面（默认按发布日星期自动选风格）；点名某套风格覆盖轮换；长标题压缩成封面文案再出图；交付前检查朋友圈分享效果并导出安全区预览。

**环境 / Requirements**：内置 ImageGen（生成无文字背景）+ Python 3 + Pillow（标题渲染、星期轮换解析、质检与分享预览导出）。

## 试着这样问 / Try asking

- 「给这篇 AI 工具测评文章做一张公众号封面，标题是《Obsidian彻底封神：为什么我说印象笔记会被淘汰》，按今天星期自动选风格」
- 「用财经权威风给我的商业分析文章做张 2.35:1 封面，主标题『先算清这件事真正的代价』」
- 「做一张周三风格的封面，文章是深度人物特稿，标题《那个拒绝千万融资的年轻人》」
- 「帮我做公众号封面并检查朋友圈分享效果，标题《实测下来只有这一条路》，要确保分享缩略图里的字读得通」
- 「周日发一篇 AI 智能体文章，按周轮替选科技风，标题《我把周报交给了 Agent》」
- 「这个标题太长了，帮我压缩成封面文案再出图：《2026 年中小企业数字化转型完全指南：从工具选型到组织落地》」

---

Use this skill to create a Chinese WeChat official account cover or wide 2.35:1 banner: a magazine-grade, headline-led cover that can be published directly.

The production goal is not “a pretty AI picture.” The goal is a repeatable commercial cover: exact 2.35:1 ratio, a readable headline, strong contrast, and no random or misspelled text.

Two things define this skill:

1. **Fourteen styles all participate in the automatic weekday rotation** — each weekday owns two looks (base + alternate) that alternate by the parity of the ISO week number, so the same weekday never repeats the same cover in consecutive weeks. `"style": "auto"` follows the rotation; an explicit style id/alias overrides it. **When the user does NOT name a specific look, the style MUST stay `auto` — do not pick a style from the article topic. Weekday rotation is the default behavior, not an opt-in.**
2. **Covers are typographic — no portrait, no avatar, no face.** The headline block owns the canvas; the right side stays open as negative space (or is filled by the style's own background motif). Never composite a person into a cover.

## 14 套风格 · 按星期自动轮换（每星期 2 套，ISO 周奇偶交替）

| 星期 | 槽位 | style id | 风格 | 气质 | 推荐字数 |
| -- | ---- | -------- | ---- | ---- | ---- |
| 一 | 基准 | `economist-crimson`   | ECONOMIST 财经权威  | 深红 + 白衬线 + 黑色刊头条  | 10–20 |
| 一 | 候补 | `swiss-grid`          | HELVETIC 瑞士网格   | 纸白 + 淡灰网格 + 信号红规线 | 10–20 |
| 二 | 基准 | `monocle-ivory`       | MONOCLE 文化极简    | 米白 + 左侧竖排 + 大字无衬线 | 10–20 |
| 二 | 候补 | `aegean-postcard`     | AEGEAN 爱琴海明信片  | 晒白纸 + 爱琴海蓝 + 陶土色带 | 10–20 |
| 三 | 基准 | `newyorker-parchment` | NEW YORKER 编辑厚重 | 羊皮纸 + 斜体刊头 + 宋体大字 | 12–20 |
| 三 | 候补 | `newsprint-extra`     | BROADSHEET 号外     | 新闻纸白 + 墨黑 + 朱红刊头  | 8–20  |
| 四 | 基准 | `wired-black`         | WIRED 未来张力      | 纯黑 + 超粗白字 + 亮红强调  | 8–20  |
| 四 | 候补 | `deco-noir`           | DECO 盖茨比之夜     | 午夜孔雀绿 + 香槟金 + 金线框 | 10–20 |
| 五 | 基准 | `kinfolk-whitespace`  | KINFOLK 东方留白    | 素白 + 细衬线 + 极大字距   | 10–20 |
| 五 | 候补 | `clean-business-tech` | CLEAN 极简商务科技   | 暗色渐变 + 极简 UI       | 6–20  |
| 六 | 基准 | `harvard-navy`        | HARVARD 学术克制    | 深蓝 + 金色印章 + 侧带    | 10–20 |
| 六 | 候补 | `agent-cyber`         | AGENT 蓝青科技      | 黑底 + 蓝青 + 金色点缀     | 6–20  |
| 日 | 基准 | `tech-purple-gold`    | TECH 紫黑金科技风    | 深空紫黑 + 流光金字 + 霓虹节点 | 6–20 |
| 日 | 候补 | `codex-blue-gold`     | CODEX 蓝金科技      | 黑底 + 电光蓝 + 金色大字   | 6–20  |

- 轮换由 `scripts/style_presets.py` 单一事实来源定义；`style: auto` 即按发布当天星期 + ISO 周奇偶取风格。
- **默认即轮换**：用户没点名风格时，brief 的 `style` 一律写 `auto`（或构建时不带 `--style`，脚本默认就是 `auto`）。绝不要用「这篇文章是讲 AI 的」之类理由替用户挑一个具体风格 id——那是覆盖轮换，违反默认规则。只有在用户显式要求某种气质（"用财经风/极简风/科技风"、"走周三那套"）才设具体 id。
- 风格分 **深色色调**（ECONOMIST / WIRED / HARVARD / DECO / TECH / CODEX / AGENT / CLEAN：亮色字 + 描边 + 发光）与 **浅色色调**（MONOCLE / NEW YORKER / KINFOLK / HELVETIC / AEGEAN / BROADSHEET：纸面背景 + 深色实心字、无描边）；渲染器自动切换字体、字色、描边。**切勿让浅底配白字或深底配黑字。**
- **轮换规则（ISO 周奇偶）**：偶数周整套出基准套、奇数周整套出候补套（`style_for_weekday()` 按 `isocalendar()[1] % 2` 取）。同一自然周内 7 天各自恒定，下一周整体切换——**相邻两周同一星期绝不重样，全部 14 套风格都参与轮换**。
- **思源黑体 Bold**：2026-10 新增 4 套（`swiss-grid` / `aegean-postcard` / `newsprint-extra` / `deco-noir`）的封面文字（标题/刊头/徽章/标签）统一用思源黑体 Bold 渲染（preset 的 `font: source-han-sans`，字体缺失时自动回退微软雅黑，不会崩）。
- 显式覆盖：写风格 id 或别名（如 `wired`、`财经权威`、`学术克制`、`kinfolk`、`swiss`、`号外`、`deco`、`盖茨比`、`codex`、`agent-cyber`）即可跳过轮换，直接锁定该套。
- 每套风格完整规格（配色、版式、装饰、字体）见 `references/style_system.md`。

## Non-negotiable output standard

1. Canvas ratio: 2.35:1. Preferred export: `2350x1000` PNG. Accept only if width / height is within `2.35 ± 0.01`.
2. Layout is **headline-led and typographic**. Default layout: the headline block starts at the left margin (5.5% of width; 8.5% for styles with a left vertical bar) and its right edge stops at ~52% of the width; the theme scene lives on the RIGHT and is auto-centred inside the right 42.6% 1:1 slice (x 1350–2350 on a 2350px canvas), which is the share preview. (A `center` layout — headline ~28%, scene centred in x 675–1675 — remains available and matches WeChat's real centre crop.) Do **not** fill the scene area with a portrait, avatar, or stock person. The headline type scale is a **brand constant, not a style variable** (`HEADLINE_CEILING = 206` in `render_wechat_cover.py`): style differences come from decoration, palette and typeface, never from glyph size. A smaller headline is only legitimate when that style's own decor eats vertical room (masthead / seal) or its letter-spacing eats width (MONOCLE / KINFOLK).
3. Main title must be legible at mobile thumbnail size. Use 2–4 text blocks maximum.
4. Do not rely on image generation to render final Chinese copy. Generate the background with no text, then render exact Chinese text with code.
5. Tone consistency is per-style: dark-tone styles use a dark background with bright stroked/glowing typography; light-tone styles use a paper background with solid dark ink and no stroke. Never mix them. Serif styles must use a CJK serif face; sans styles must use a CJK sans face.
6. Keep the main title inside the style's recommended character range (see the rotation table). The renderer shrinks the font to fit and warns when the count is out of range.
7. No portrait / avatar / face anywhere in the cover — not generated, not composited, not as a watermark.
8. Every final file must pass the QA checklist in `references/qa_checklist.md` before delivery.

## 分享安全区与交付标准（硬约束）

2.35:1 封面**不止被裁一次**。在订阅号消息列表里是完整横幅，分享出去时只保留一个 1:1 方形（占画布宽度约 42.6%），左右两翼被切掉：

| 场景 | 显示 |
|---|---|
| 订阅号消息列表 / 文章顶部 | 完整 2.35:1 |
| **分享出去** | **只保留一个 1:1 方形，左右两翼被切掉** |

方形边长 = 画布宽度的 **~42.6%**（2350×1000 → 1000px 见方）。中央方形是 x 675–1675；本技能默认版式取的是**右 42.6% 方形 x 1350–2350**（见下）。

> **本技能的交付/验收标准＝右 42.6% 方形（x 1350–2350）。** 默认版式把主题场景生成在右侧并自动居中到这块方形，`check_cover` 导出的 `-share-1x1.png` 就是它。设计与验收一律以这块 1:1 切片为准：场景必须完整落在其中、不被右缘裁切、不被标题或装饰压住。**不做「横幅优先、切片可以让路」的取舍。**

✅ **默认版式：左标题 + 右主视觉**——标题压在左约 52%，主题场景生成在右侧并自动居中到**右 42.6% 方形**，`check_cover` 默认按右侧导出分享预览（`share_side: right`），**这块切片就是验收标准**。左右两翼放核心内容会在分享时被切掉，**横版「左右分栏」直觉在公众号封面上正是陷阱**（详见 `references/wechat-platform-limits.md`）。

**安全区策略**：
- **D 左标题 + 右主视觉（默认且为正式交付版式，`share_side: right`，2026-10-27 起；5.7.2 取消 banner 优先）**——标题占左约 52%、主题场景生成在右侧并自动居中到右 42.6% 方形；`check_cover` 默认导出右 42.6% 作分享预览。**分享观感全看这块主体**，所以场景须能独立成图（本技能的 ImageGen 主题场景天然满足）。横幅与右切片**并列过检**：右切片内场景必须完整不被裁切、不被标题/装饰压住；标题可读性对完整横幅负责。
- **C 场景居中（`share_side: center`，可选）**——标题占左约 28%、场景居中于中央方形（x 675–1675）、预览走中央裁剪；仅当用户明确要求场景居中时才用。
- **B 核心词居中**（仅当需要分享图里也带文字时才用）——把标题核心压进中央方形（x 675–1675），让分享也能读到字。较少用。

> `check_cover.py --safe-zone` 打印所选侧的安全区范围（与 `--export-share` 裁剪逐像素一致），并导出 `-safezone.png`（裁切区外压暗 + 红框，检查构图）与 `-share-1x1.png`（**默认右 42.6% 方形**＝正式分享预览）。`--share-side center` 可按需导中央裁剪。默认右主视觉版式下 **`-share-1x1.png` 里右侧主体完整、好看、不被裁才算合格**；横幅与切片并列过检，任一项不过即重做。

### 🔴 分享缩略图取哪一块，由 `pic_crop_1_1` 决定（5.7.5，必读）

这是最容易反复翻车的一点。封面图只是**原图**，微信在分享卡片 / 转发 / 历史消息里显示的 1:1 缩略图，取的是**封面素材上的一个裁剪窗口**，由建/改草稿时的 `pic_crop_1_1` 指定：

| 你传了什么 | 分享缩略图显示 |
|---|---|
| 不传 `pic_crop_1_1` | 封面**正中央** 1:1（右版式 → 标题被切掉左半，只剩残句） |
| `pic_crop_1_1: "0.574468_0_1_1"` | 封面**右 42.6%** 1:1（＝`-share-1x1.png`，本技能的交付标准） |

坐标以原图左上 `(0,0)`、右下 `(1,1)` 为坐标系，格式 `X1_Y1_X2_Y2`（≤6 位小数）。2350×1000 画布：右侧方形 x 1350–2350 → `0.574468_0_1_1`；`pic_crop_235_1` 用 `0_0_1_1`（整图即 2.35:1）。

```bash
python scripts/share_crop.py --image wechat_cover.png          # 打印该传的值
python scripts/share_crop.py --image wechat_cover.png --side center   # 换版式时重算
```

**所以「分享图居中」不是渲染 bug，是草稿没带 `pic_crop_1_1`。** 渲染完成后一定要把值带进草稿（见文末「推送给草稿箱」第 5 条）。

> 完整平台硬约束（三件套字数、菜单结构、手机屏阈值、合规红线）见 [references/wechat-platform-limits.md](references/wechat-platform-limits.md)。

## Recommended workflow

### Step 1 — Parse the cover brief

Extract or infer:

- Article topic and user intent.
- **文章主旨 `topic`**：用一句话概括文章讲什么（内容概述），写入 brief 的 `topic` 字段，与标题一起驱动右侧构图语义匹配。
- Exact title or headline.
- 1 short kicker/eyebrow line.
- 1 dominant hero word or phrase.
- 1 subtitle / value promise.
- Optional bottom tags, no more than 4.
- **Style — 默认 `auto`（按星期轮换），这是硬规则，不是建议。** 用户**没有**明确点名某套风格时，`style` 一律保持 `auto`，让封面按发布当天星期自动取风格。不要把文章主题 / 内容类型拿来替用户选风格（下方「内容类型→风格」映射只是**用户显式要某种气质时才参考的提示**，绝不能作为默认选择规则）。只有在用户明确点名某套风格（"用财经风 / 极简风 / 科技风"、"周三那套 NEW YORKER"、"走深色"等）时，才把 `style` 设为对应 id / 别名，跳过轮换。
- Optional masthead/brand mark text (used by the masthead band, vertical label, and seal). Defaults to the style's own running head or the brand mark.

If the user gives a long article title, compress it into cover copy instead of placing the entire title verbatim. Keep the article's core claim, and keep the total hero character count inside the style's recommended range.

### Step 2 — Build a structured brief

Create `cover_brief.json` in the working directory. Use `assets/cover_brief.example.json` as the schema. The values below are the same canonical example, kept in sync with that file:

```json
{
  "canvas": {"width": 2350, "height": 1000},
  "style": "auto",
  "style_requested": "auto",
  "date": "2026-09-29",
  "style_name": "MONOCLE 文化极简",
  "char_count": 20,
  "char_range": "10-20",
  "title_original": "AI时代最好的知识管理工具：Obsidian为什么会淘汰印象笔记",
  "topic": "知识管理工具对比与长期使用心得",
  "eyebrow": "AI时代最好的知识管理工具",
  "hero_lines": ["Obsidian彻底封神", "印象笔记会被淘汰"],
  "subtitle": "重度使用经验实战复盘",
  "bottom_tags": ["双链笔记", "AI工作流", "知识库", "长期主义"],
  "masthead_text": "智驭视界",
  "right_motif": "auto",
  "right_scene": "auto",
  "background_path": "./background.png",
  "output_path": "./wechat_cover.png",
  "seed": 202601
}
```

`right_scene` 控制中央**主题场景**（ImageGen 背景的中央主视觉，见 `references/scene-archetypes.md`）：`auto`（默认，按标题+主旨自动选 9 种场景原型）/ `off`（关闭场景化，回风格默认背景）/ 直接写场景 id（`portal-cards` / `workflow-wheel` / `desk-metaphor` / `data-stream` / `journey-panels` / `growth-steps` / `knowledge-graph` / `checklist-cards` / `reform-cut`）。**中央主视觉由 ImageGen 场景承载**，语义由「标题 + 主旨」共同驱动，产出与文章同频的电影级场景（传送门/飞轮/桌面/数据流/画廊/阶梯/图谱/清单/改革减法）。

`right_motif` 控制右侧留白区的轻量矢量图形（可选点缀层）：`auto`（默认）/ `off`（留空，追求标杆同款纯场景时设 off）/ 直接写 motif id（`agent` / `data` / `knowledge` / `checklist` / `growth` / `pulse` / `gear` / `quote` / `life` / `finance` / `waves`）。它只画在标题右边界之外的保留区，低透明度、不改任何标题排版——**场景是主视觉，矢量图只是可选点缀**。`topic` 字段写入文章主旨，与标题一起参与场景/图形的语义匹配。

`char_count` counts CJK glyphs plus Latin letters/digits in `hero_lines`, ignoring spaces and punctuation (20 above = 12 + 8). `build_cover_brief.py` computes it for you; this field is informational.

`style: "auto"` resolves to the weekday rotation. **Always build the brief with `scripts/build_cover_brief.py`** (it fills the style, `style_name`, `char_count` and warns when the title is out of range). If you ever hand-write the JSON, you MUST set `"style": "auto"` — never write a concrete style id unless the user overrode.

### Step 3 — Generate background with imagegen

Use the built-in image generation tool (ImageGen) to generate only the background and visual world, not the final text and not any person.

Always take the prompt from the resolved style — the background tone must match the style's text color:

```bash
python scripts/export_imagegen_prompt.py cover_brief.json > imagegen_background_prompt.txt
```

The exporter injects the **hero thematic scene** (`scripts/scene_concepts.py`) chosen from the title + topic — a concrete, story-driven visual (portal cards / workflow wheel / desk still-life / data stream / content gallery / growth steps / knowledge graph / checklist cards / reform-cut). With `share_side: right` (default) it is placed on the RIGHT and the LEFT ~52% stays clean for the headline; with `share_side: center` it fills the centre and the LEFT ~28% stays clean. See `references/scene-archetypes.md` for the 9 archetypes and composition rules. Preview just the scene choice with:

```bash
python scripts/scene_concepts.py cover_brief.json --tone dark   # or --plan
```

When generating, send the exporter's full output as the ImageGen prompt. Keep every hard rule it prints: **no readable text / letters / Chinese, no people / face / portrait / logos / watermark** (abstract placeholder lines on cards are fine). This deliberately diverges from reference covers that bake Chinese labels into the scene — those labels risk AI-garbled characters, so exact copy always stays in the code-rendered type layer.

This prints the correct prompt for the style stored in the brief (auto-resolved), plus the tone (`light` / `dark`) reminder. All prompts are also listed in `references/prompt_blueprints.md`.

Key rules:

- **Light-tone styles must get a light/paper background prompt; dark-tone styles must get a dark background prompt.** A mismatched background makes the text unreadable, because the renderer picks text color from the style, not from the image.
- **Every prompt already forbids people and portraits.** Keep `no people, no portrait` in the prompt. If a generated background happens to contain a person or face, discard it and regenerate.

Save imagegen prompts or generation notes in `generation_notes.md` for repeatability.

> 🧽 **角标水印（默认自动处理，5.7.4）**：ImageGen 常在背景角落烙一行极淡的「AI生成 / WORKBUDD」角标，prompt 里写 `no watermark` 也拦不住。本技能**无需你手动处理**——`render_wechat_cover.py` 在加载背景时会先调用 `remove_watermark.py` 自动抹掉它再排版。若想单独清理并核对某张背景：
> ```bash
> python scripts/remove_watermark.py background.png --out background.clean.png
> ```
> 它只抹角落的淡字、不碰主视觉场景；对已干净的图再跑也不会改动（幂等）。

### Step 4 — Compose exact typography

Use `scripts/render_wechat_cover.py`:

```bash
python scripts/render_wechat_cover.py cover_brief.json            # style from the brief
python scripts/render_wechat_cover.py cover_brief.json --style auto --date 2026-09-29   # force rotation for a date

# 交付前必跑：比例 + 尺寸 + 朋友圈分享安全区
python scripts/check_cover.py wechat_cover.png --safe-zone \
  --export-safe wechat_cover-preview --export-share wechat_cover-preview
```

> ⚠️ **`--safe-zone` 不可省**：本技能**默认版式**为「左标题 + 右主视觉」——标题占左约 52%，主题场景在右侧并**自动居中到右 42.6% 1:1 切片**（2350×1000 → x 1350–2350），脚本默认导出这块 `-share-1x1.png` 作为**正式分享预览与验收依据**，并打印安全区像素范围、导出 `-safezone.png`（左侧压暗 + 红框）。
>
> **右 42.6% 切片即交付标准（5.7.2 起）**：默认版式下，验收看的就是这块 1:1 切片——右侧主题场景必须**完整落在 x 1350–2350 内、不被画布右缘裁切、不被标题或装饰压住**，且能独立成图。切片里场景是干净完整的主体画面即合格。
>
> **不再有「banner 优先」豁免**：横幅整体观感与 `-share-1x1.png` 切片观感**并列过检**，不允许用「横幅好看」为切片里场景残缺开脱。若切片内主体被裁或被压，须调整背景几何（`position_scene.py` 或手工重排）或重出背景，而不是直接交付。仅在走 B 核心词居中策略时才额外要求切片里标题核心词可读。参见上方「分享区版式（`share_side`）」一节与 `references/qa_checklist.md`。

The script draws exact text, the style's typography (serif/sans, light/dark, letter-spacing, per-style font family), decorations (masthead band, vertical bar + vertical label, italic masthead, gold seal, side band, top rule, short rule, bottom colour band, Art Deco frame, newspaper column rules), and the bottom badges/tags — all from the resolved style preset. It composites **no portrait**. If a generated background is not ready, it creates a deterministic fallback background in the correct tone for that style, so light styles stay light and dark styles stay dark. It prints the resolved style so you can state which of the 14 was used.

Note: the lightweight vector motif layer (`scripts/cover_motifs.py`) is **deprecated and OFF by default** (2026-10-25) — the right side is now carried by the ImageGen theme scene. It still exists as an optional low-alpha accent; it draws only if a brief explicitly sets `right_motif` to a motif id or `auto`, never shifts the headline grid, and is skipped on narrow canvases. Leave `right_motif` unset / `"off"` for the clean scene-only look.

Do not “fill” the right side with an avatar or a person — the motif is vector-only and text-free. If the cover still feels empty, the fix is longer/stronger headline copy, a larger headline, a style whose background motif carries more texture, or an explicit motif id that matches the article.

### Step 5 — Quality gate before delivery

Run `scripts/check_cover.py <png> --safe-zone --export-safe <prefix> --export-share <prefix>`. Then inspect visually and verify:

- Exact 2.35:1 ratio.
- **分享安全区（验收主项）：打开 `-share-1x1.png`，确认右侧主题场景完整落在 42.6% 右切片（x 1350–2350）内、未被右缘裁切、未被标题/装饰压住，且独立成图观感 OK**。`--safe-zone` 打印的边界与实际裁剪范围一致；此项不过即判不合格，需重排或重出背景。
- **草稿已带 `pic_crop_1_1`（5.7.5）：确认草稿是带 `pic_crop_1_1="0.574468_0_1_1"` 建的/改的**——不带的话，微信分享卡片会退回居中裁剪，`-share-1x1.png` 再好看也没意义。
- No misspelled Chinese text.
- No fake UI text that looks like broken Chinese.
- Title is readable after viewing at 25% size.
- **No person, face, or avatar anywhere in the image.**
- Text does not collide with decorations; the badge does not cover the last hero line.
- Main hook is clear and honest in one glance.
- Final output is PNG or high-quality JPG.

If any item fails, fix it before delivering. Do not ask the user to accept a low-quality draft.

## Cover copy rules

Cover copy follows 智驭视界's voice: **有判断、说人话、给具体的价值**. Keep it short and strong, but do not manufacture urgency or fear.

Good patterns:

- `先把结论说清楚`
- `我自己的完整做法`
- `实测下来只有这一条路`
- `这件事真正的代价`
- `为什么我说这条路走不通`
- `一套能跑起来的流程`
- `踩过的坑和修正后的做法`

Hierarchy for a long headline:

1. Eyebrow: context, 8–14 Chinese characters.
2. Hero: biggest claim or judgment, 6–14 Chinese characters per line.
3. Subtitle badge: concrete proof/promise, 10–18 Chinese characters.
4. Bottom tags: 3–4 keywords.

Rules:

- Prefer a **specific claim or a concrete number** over a vague adjective.
- One idea per cover. If you need two claims, split the hero into two lines and make the second line the consequence.
- Never put more than 38 Chinese characters in the main title area unless the user explicitly demands it.
- **Avoid these — they are off-voice:**
  - 恐吓 / 唱衰人群：`会被时代抛弃`、`再不学就完了`、`你已经被淘汰`
  - 无法核实的绝对化承诺：`0成本`、`100%自动赚钱`、`保证涨粉`、`稳赚`
  - 硬蹭权威 / 虚构背书：`官方推荐`、`XX认证`、`全网第一`
  - 空洞口号、没有信息量：`颠覆认知`、`炸裂`、`太震撼了`
- Cover copy may be sharper than the article title, but it must not promise anything the article does not deliver.

## 右侧视觉（right_scene 主视觉 + right_motif 点缀）

右侧分两层，**场景是主视觉，矢量图只是可选点缀**：

1. **主题场景（主视觉）**——`right_scene` / `scripts/scene_concepts.py` / `references/scene-archetypes.md`：由 ImageGen 背景承载，按标题+主旨自动生成 9 种电影级场景（信息传送门 / 自动化飞轮 / 桌面实物 / 数据流 / 内容画廊 / 阶梯增长 / 知识图谱 / 清单卡片 / 改革减法）。这是右侧 42.6% 方形（默认版式）的主要画面，由 `position_scene.py` 自动居中，自带叙事与质感，与文章语义同频。
2. **矢量点缀（可选）**——`right_motif` / `scripts/cover_motifs.py`：低透明度的轻量矢量图元叠加在场景之上，提供品牌稳定层。追求标杆同款「纯场景」时设 `"right_motif": "off"` 关掉即可。

下面的 right_motif 引擎描述的是**第 2 层**（点缀层）的语义组合逻辑。

右翼是刻意留白，但纯留白会让封面左重右轻，而固定画同一个小图标又会让每篇封面右半边长得一样。`scripts/cover_motifs.py` 因此做成一个**语义驱动的组合构图引擎**：

**① 语义提取**：对「主标题（权重 1.8）→ 眉题 1.2 → 原标题 1.0 → 文章主旨 topic 1.0 → 副标 0.9 → 标签 0.75」分层打分（关键词越长、出现越靠前，分越高），得到主 Graph 族与次 Graph 族。**标题与主旨共同驱动**，主旨字段 `topic` 让「文章讲什么」直接参与构图决策。

**② 组合而非单图**：每次至少组合「主图标 + 次图标 + 2 组点缀」，共 11 族图标 × 5 类点缀 × 4 种版式：

| 元素 | 可选值 |
| -- | -- |
| 图标族（主/次） | `agent` 智能体编排 / `data` 数据图表 / `knowledge` 知识图谱 / `checklist` 清单卡片 / `growth` 阶梯增长 / `pulse` 速度雷达 / `gear` 模块搭建 / `quote` 编辑随笔 / `life` 生活杯盏 / `finance` 投资叠币 / `waves` 抽象波纹 |
| 版式 | `stack` 上下分层 / `stagger` 错位对角 / `centerpiece` 大图居中 / `ladder` 阶梯三段 |
| 点缀 | `dots` 点阵 / `ticks` 刻度 / `brackets` 角括 / `spark` 星芒 / `arcs` 同心弧 |

次图标优先取第二高分的语义族；只有一个族命中时用**语义相邻表**补位（如 `growth`→`data`、`knowledge`→`quote`、`checklist`→`gear`），保证两个图形读起来是同一个想法而不是两张贴纸。

**③ 稳定但不呆板**：构图种子由**文案内容的 CRC32**（含 brief 的 `seed`）推导，同一篇文章重复生成得到**完全一致**的封面；不同文章自然得到不同组合（实测 8 篇不同文案 → 8 种不同组合：主次图标、版式、点缀、主/次尺寸占比均不同）。想给同一篇换一种构图，改 brief 里的 `seed` 即可（实测 4 个 seed → 4 种构图）。

**④ 版式协调与硬约束**：

- 只画在标题右边界之外的保留区（80%，竖排条风格 78%，右止 95.5%，y 13.5%–79%），**最后一层按矩形硬裁剪**，任何图元越界都会被切掉——标题区像素零改动（已用空白画布逐像素验证）。
- 主图标占区高 50–60%、次图标 26–36%，尺寸天然有主次；配色全部取该风格自身的 accent / ink，深色风格线更亮、浅色风格线更沉，密度低、透明度低。
- **窄画布自动隐藏**：宽度 < 1400 或高度 < 380（或保留区 < 150×180）时整组跳过，不溢出、不需要横向滚动。
- `right_motif` 可写 `off` / `none` 关闭；写具体图标 id 则锁定主图标（次图标与版式仍按内容组合）。
- 调试：`python scripts/cover_motifs.py --list / --plan "标题" / --variants 9 / --zone 2350x1000`；渲染日志会打印实际构图签名，如 `[motif=agent+data/stack]`。

## Style families

Fourteen styles rotate by weekday — two looks per weekday (base + alternate, ISO week parity). Full specs (palette, tone, font, layout, decorations, prompt) live in `references/style_system.md`; the canonical definition is `scripts/style_presets.py`.


> ⚠️ **本表只在用户显式点名气质时参考，不要用作默认选择。** 用户未指定风格时，封面必须走 `auto` 星期轮换，不要按内容主题自动挑风格。

Quick mapping of content type to style（仅当用户说「用某类风格」时参考）：

- 行业判断 / 趋势解读 / 数据复盘 / 商业分析：`economist-crimson`（周一基准）
- 方法论 / 清单体干货 / 工具测评 / 理性分析：`swiss-grid`（周一候补）
- 文化观察 / 生活方式 / 审美方法论：`monocle-ivory`（周二基准）
- 旅行 / 轻松经验分享 / 效率工具 / 生活向：`aegean-postcard`（周二候补）
- 深度长文 / 人物特稿 / 叙事：`newyorker-parchment`（周三基准）
- 突发热点跟进 / 重要发布 / 数据速报：`newsprint-extra`（周三候补）
- 前沿科技 / AI 新物种 / 未来趋势：`wired-black`（周四基准）
- 年度总结 / 重磅复盘 / 高端活动 / 品牌向：`deco-noir`（周四候补）
- 日常随笔 / 心得 / 慢思考：`kinfolk-whitespace`（周五基准）
- 咨询 / 商业分析 / 克制高端感：`clean-business-tech`（周五候补）
- 学术方法 / 研究复盘 / 体系干货 / 课程：`harvard-navy`（周六基准）
- Agent / 工作流自动化 / 企业 AI 落地：`agent-cyber`（周六候补）
- AI 工具 / 知识管理 / 个人 IP：`tech-purple-gold`（周日基准）
- 代码 / 开发者工具 / 硬核教程：`codex-blue-gold`（周日候补）

全部 14 套均参与轮换（基准套=ISO 偶数周，候补套=ISO 奇数周）；仍可显式点名锁定其中任意一套。

## Failure modes to avoid

- Letting the model invent or misspell Chinese words.
- **Putting a person, face, or avatar into the cover** (including a “small avatar card” or a stock photo from imagegen).
- **Tone mismatch: white/light text on a light paper style, or dark text on a dark style.**
- **Reusing a dark tech background prompt for a light-tone style (or vice versa).**
- **Serif style rendered with a sans face (or the opposite) because the font fallback was not checked.**
- Background too bright behind the headline (dark styles) or too busy behind the headline (light styles).
- Decorations (masthead band, seal, vertical bar, side band) overlapping the title.
- Subtitle badge colliding with the last hero line, or the hero block pushed off-canvas.
- Too many small labels that become unreadable in a WeChat feed.
- Clickbait or fear-based copy (see the avoid list in Cover copy rules).
- Fake official product logos unless the user supplied them.
- Overcrowding with every article detail.

## Delivery format

Return the final cover file plus brief notes:

- Output file path.
- Size and ratio.
- **Which of the 14 styles was used (id + name + weekday + base/alternate slot, or "explicit override").**
- Whether the font was serif or sans (and for the 4 Source Han Sans styles, whether 思源黑体 was found or fell back).
- Any variations generated.
- Confirm: `typographic only, no portrait composited`.

## 推送给草稿箱（封面交接，关键）

生成的封面 PNG 只是个图片文件，**不会自动**成为草稿箱缩略图。如果漏掉交接步骤，草稿箱里会退化成「正文第一张插图」，一眼就能看出封面没生成。

铁律（曾踩坑，已修 gzh-draft-push/push_draft.py）：
1. **渲染输出命名**：用 `<slug>-cover.png`（如 `one-person-content-pipeline-cover.png`），明确区分正文插图。
2. **复制到推文 assets-dir**：把封面 PNG 复制到该篇文章推送用的 `--assets-dir`（即正文图所在目录），否则脚本会报「封面文件不存在」。
3. **推送显式传 `--cover`**：`python push_draft.py --html <排版.html> --assets-dir <dir> --images 01.png 02.png ... --cover "<slug>-cover.png" --title "..." --digest "..." --author "青灯墨染"`。
   - ⚠️ `--author` **必须传「青灯墨染」**（作者名），不是「智驭视界」（号名）。封面刊头 / 竖排品牌字才用号名。
   - 传了 `--cover`：封面文件会被**单独上传**为素材，其 `media_id` 用作草稿 `thumb_media_id`。
   - 省略 `--cover`：脚本会静默复用 `images[0]`（正文首图）作缩略图——这就是「封面显示成正文首图」的根因，绝不可省。
4. **推送后核验**：跑 `verify_draft.py <media_id>`，确认四项为 0（本地残留/D:/、assets/、坏 src）且 `mmbiz` 图数 = 配图数；再跑 `get_draft.py`（或核对 `thumb_media_id`）确认 `thumb_media_id == 封面 media_id`，才算封面真正挂上。
5. **必须同时传 `pic_crop_1_1`（5.7.5，分享缩略图的真正开关）**：`thumb_media_id` 只是原图，微信**分享卡片 / 转发 / 历史消息里那个 1:1 缩略图取哪一块，由 `pic_crop_1_1` 决定**。不传 → 微信从封面**正中央**裁 1:1，右主视觉版式的标题会被切掉左半（2026-10-28 实测翻车）。
   **默认走脚本，别手写请求体**——它把「压缩略图 + 传素材 + 换 thumb + 写裁剪坐标 + 回读核验」全包了：
   ```bash
   python scripts/push_cover.py --media-id <草稿 media_id> --cover wechat_cover.png
   # 只改裁剪、不动图： --crop-only ；先看计划不调用接口： --dry-run
   # 换版式： --side center
   ```
   等价的手工请求体（脚本内部就是这么发的）：
   ```json
   {"articles":[{ "title":"…", "content":"…", "thumb_media_id":"<封面素材>",
                  "pic_crop_1_1":"0.574468_0_1_1", "pic_crop_235_1":"0_0_1_1" }]}
   ```
   坐标由 `scripts/share_crop.py` 算（`--image wechat_cover.png` 直接打印），`check_cover.py --safe-zone` 也会把该传的值打出来。**坐标与 `-share-1x1.png` 逐像素等价**（同一套 `share_slice_box`）。
6. **进草稿≠群发**：草稿需用户在公众号后台手动「发表」。坏草稿可用 `draft/delete` 删掉（`{"media_id":...}`，errcode 0 即成功），重推覆盖。
7. **定时发布中的草稿改不了**：`draft/update` 会返回 `53407 定时发布中，无法删除或修改`。要改封面/裁剪，先在后台取消定时发布，再重推。
