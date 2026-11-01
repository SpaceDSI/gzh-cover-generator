# WeChat Cover ImageGen Skill — 安装与使用

这是一个给 Agent 使用的 Skill，用于稳定生成公众号封面：2.35:1、标题主导、杂志级排版、可发布级质感。

两大特点：

1. **内置 14 套风格，每个星期 2 套按 ISO 周奇偶自动交替**，相邻两周同一天不重样。
2. **封面是纯文字主导，不含头像、不含人物、不合成真人照片。**

风格定义集中在 `scripts/style_presets.py`。

## 14 套风格 · 按星期自动轮换（每星期 2 套，基准 ↔ 候补）

| 星期 | 槽位 | style id | 风格 | 气质 | 推荐字数 |
|------|------|----------|------|------|---------|
| 一 | 基准 | `economist-crimson` | ECONOMIST 财经权威 | 深红 + 白衬线 + 黑色刊头条 | 10–20 |
| 一 | 候补 | `swiss-grid` | HELVETIC 瑞士网格 | 纸白 + 淡灰网格 + 信号红规线 | 10–20 |
| 二 | 基准 | `monocle-ivory` | MONOCLE 文化极简 | 米白 + 左侧竖排 + 大字无衬线 | 10–20 |
| 二 | 候补 | `aegean-postcard` | AEGEAN 爱琴海明信片 | 晒白纸 + 爱琴海蓝 + 陶土色带 | 10–20 |
| 三 | 基准 | `newyorker-parchment` | NEW YORKER 编辑厚重 | 羊皮纸 + 斜体刊头 + 宋体大字 | 12–20 |
| 三 | 候补 | `newsprint-extra` | BROADSHEET 号外 | 新闻纸白 + 墨黑 + 朱红刊头 | 8–20 |
| 四 | 基准 | `wired-black` | WIRED 未来张力 | 纯黑 + 超粗白字 + 亮红强调 | 8–20 |
| 四 | 候补 | `deco-noir` | DECO 盖茨比之夜 | 午夜孔雀绿 + 香槟金 + 金线框 | 10–20 |
| 五 | 基准 | `kinfolk-whitespace` | KINFOLK 东方留白 | 素白 + 细衬线 + 极大字距 | 10–20 |
| 五 | 候补 | `clean-business-tech` | CLEAN 极简商务科技 | 暗色渐变 + 极简 UI | 6–20 |
| 六 | 基准 | `harvard-navy` | HARVARD 学术克制 | 深蓝 + 金色印章 + 侧带 | 10–20 |
| 六 | 候补 | `agent-cyber` | AGENT 智能体蓝青风 | 黑底 + 蓝青 + 金色点缀 | 6–20 |
| 日 | 基准 | `tech-purple-gold` | TECH 紫黑金科技风 | 深空紫黑 + 流光金字 + 霓虹节点 | 6–20 |
| 日 | 候补 | `codex-blue-gold` | CODEX 黑蓝金科技风 | 黑底 + 电光蓝 + 金色大字 | 6–20 |

- 默认 `--style auto`：按当天星期 + ISO 周奇偶自动选风格——**偶数周出基准套、奇数周出候补套**（`style_for_weekday()`），相邻两周同一星期绝不重样。
- 想看轮换表：`python scripts/build_cover_brief.py --list-styles`。
- 想固定/覆盖：直接传 id 或别名，如 `--style wired`、`--style 财经权威`、`--style kinfolk`、`--style swiss`（瑞士网格）、`--style 号外`、`--style deco`（盖茨比之夜）。
- **全部 14 套均参与轮换**，无「非轮换」遗留风格；用户显式点名可跳过轮换锁定。
- 2026-10 新增 4 套（`swiss-grid` / `aegean-postcard` / `newsprint-extra` / `deco-noir`）的封面文字统一**思源黑体 Bold**（`NotoSansSC-VF.ttf` 自动挑 Bold 实例，缺失时回退微软雅黑）。

## 安装

解压后会得到 `gzh-cover-generator/` 文件夹，把它复制到以下任一位置：

### 个人全局使用

```bash
mkdir -p ~/.agents/skills
cp -R gzh-cover-generator ~/.agents/skills/
```

### 某个项目内使用

```bash
mkdir -p .agents/skills
cp -R gzh-cover-generator .agents/skills/
```

如果没被识别到，重启客户端。

## 推荐调用方式

```text
使用 gzh-cover-generator 给这篇文章做公众号封面：
标题：AI时代最好的知识管理工具：Obsidian为什么会淘汰印象笔记和飞书
要求：2.35:1，按今天星期自动选风格，纯文字排版、不要任何人物头像，突出 Obsidian、双链、AI工作流。
```

不写风格时默认走星期轮换；要指定风格就加一句「用财经风 / 极简风 / 科技风」。

## 质量稳定策略

这个 Skill 采用“背景生成 + 代码排版”的流程，不做任何人物合成：

1. `scripts/style_presets.py` 定义 14 套风格的配色、色调、字体、版式装饰、推荐字数与背景提示词（单一事实来源）。
2. imagegen 只负责背景、氛围、纹理与抽象 UI 元素，提示词强制 `no people, no portrait`。
3. Python 脚本负责精确中文标题、比例、排版，以及风格化装饰（刊头条 / 竖条 / 印章 / 侧带 / 顶部红条 / 底部色带 / 装饰艺术金框 / 报纸栏线）+ 右侧组合构图（`cover_motifs.py`：按文案语义组合「主图标 + 次图标 + 点缀」、4 种版式、内容确定性种子、窄画布自动隐藏）。
4. `scripts/check_cover.py --safe-zone` 做尺寸比例 + 朋友圈分享安全区校验。

## 示例命令

`--style auto` 会按星期自动选风格：

```bash
# 1) 生成 brief（auto 按当天星期；也可加 --date/--weekday 指定）
python scripts/build_cover_brief.py \
  --style auto \
  --title "AI时代最好的知识管理工具：Obsidian为什么会淘汰印象笔记和飞书" \
  --eyebrow "AI时代最好的知识管理工具" \
  --hero "Obsidian彻底封神" \
  --hero "印象笔记和飞书都会被淘汰" \
  --subtitle "重度使用经验实战复盘" \
  --tag "双链笔记" --tag "AI工作流" --tag "知识库" --tag "长期主义" \
  --output cover_brief.json

# 2) 导出该风格的 imagegen 背景提示词
python scripts/export_imagegen_prompt.py cover_brief.json > imagegen_background_prompt.txt
#    用 imagegen 生成 background.png 后（背景里不应出现人物）：

# 3) 合成封面并校验
python scripts/render_wechat_cover.py cover_brief.json
python scripts/check_cover.py wechat_cover.png --safe-zone \
  --export-safe wechat_cover-preview --export-share wechat_cover-preview
```

指定风格 / 指定日期 / 查看轮换表：

```bash
python scripts/build_cover_brief.py --list-styles
python scripts/build_cover_brief.py --style wired --title "..." --hero "..." --output cover_brief.json
python scripts/build_cover_brief.py --style auto --date 2026-09-29 --title "..." --output cover_brief.json
python scripts/render_wechat_cover.py cover_brief.json --style auto --date 2026-09-29

# 右侧组合构图：查看图标族 / 预览某篇的构图 / 检查变化度 / 探测绘制区
python scripts/cover_motifs.py --list
python scripts/cover_motifs.py --plan "我把周报交给了 Agent"
python scripts/cover_motifs.py --variants 9
python scripts/cover_motifs.py --zone 2350x1000
# 构建时锁定主图标或关闭：--motif growth / --motif off
```

## 文件结构

```text
gzh-cover-generator/
├── SKILL.md                      # 技能主文档（14 套风格轮换 + 工作流 + 文案规则）
├── README_INSTALL.md             # 本文件
├── scripts/
│   ├── style_presets.py          # ★ 14 套风格 + 星期轮换的单一事实来源
│   ├── cover_motifs.py           # 右侧轻量主题图形（矢量、主题匹配、窄画布隐藏）
│   ├── build_cover_brief.py      # 生成 cover_brief.json（支持 --style auto / --date / --weekday）
│   ├── export_imagegen_prompt.py # 按风格导出背景提示词
│   ├── render_wechat_cover.py    # 渲染 2.35:1 封面（浅底/深底、衬线/无衬线、装饰、无人物）
│   ├── check_cover.py            # 尺寸比例 + 分享安全区校验
│   └── make_avatar.py            # 生成技能头像 assets/avatar.png（512×512，确定性排版）
├── references/
│   ├── style_system.md           # 14 套风格详规
│   ├── prompt_blueprints.md      # 14 套风格背景提示词
│   ├── wechat-platform-limits.md # 微信平台硬约束（三件套字数/封面安全区/菜单/合规）
│   └── qa_checklist.md           # 发布前检查表（含无人物硬性检查）
└── assets/
    ├── brand_profile.example.json # 品牌调性示例
    ├── cover_brief.example.json   # brief 示例
    └── avatar.png                 # 技能头像（ECONOMIST 深红 + 2.35:1 小封面卡 + 星期轮换圆点）
```
