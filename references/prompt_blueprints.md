# ImageGen 背景提示词蓝图（14 套风格）

这些提示词只用于生成**背景与视觉氛围**，最终中文一律由代码绘制。**封面不含人物：提示词里必须保留 `no people, no portrait`。**

> 权威来源：`scripts/style_presets.py` 的 `STYLE_PROMPTS`。本文件是其可读副本，**以代码为准**。
> 也可用 `python scripts/export_imagegen_prompt.py cover_brief.json` 自动按 brief 里的风格导出对应提示词。

## 通用规则

- 比例固定 2.35:1（建议 1536×1024 或等价宽幅）。
- 标题块从左边界（5.5%，带竖排条的风格 8.5%）起，右边界止于画布 80%（带竖排条 78%），即**右侧至少留 20% 干净留白**；不要把主体元素压在右侧留白区里。
- 必须写：`No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark.`
- 生成后不要要求模型写中文标题。若背景里出现了人/人脸，作废重出。
- 浅色风格（MONOCLE / NEW YORKER / KINFOLK / HELVETIC / AEGEAN / BROADSHEET）必须用浅色纸感背景；深色风格（ECONOMIST / WIRED / HARVARD / DECO / TECH / CODEX / AGENT / CLEAN）必须用深色背景，否则与文字色打架。

---

## 一、`economist-crimson` · ECONOMIST 财经权威（周一·基准）

```text
Create a wide 2.35:1 WeChat article cover background in an authoritative financial weekly style. Deep crimson red field with a subtle darker vignette and light paper grain, restrained and serious. A solid black masthead band across the very top. Faint thin white column rules hinting at newspaper columns. Keep the composition text-friendly: a clean deep-red field across the left 62% for large white serif Chinese headline typography, with the right side similarly calm as open negative space. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. High contrast, premium, print-like, publish-ready.
```

## 二、`monocle-ivory` · MONOCLE 文化极简（周二·基准）

```text
Create a wide 2.35:1 WeChat article cover background in a refined cultural-magazine style. Warm ivory off-white (#F3EEE4) paper field with the faintest grain, airy and calm, editorial minimalism. A slim solid black vertical bar hugging the far left edge, and a single thin black hairline rule. Keep the composition text-friendly: clean ivory space across the canvas for large bold sans-serif Chinese headline typography, with generous open negative space on the right. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Clean, premium, print-magazine feel, publish-ready.
```

## 三、`newyorker-parchment` · NEW YORKER 编辑厚重（周三·基准）

```text
Create a wide 2.35:1 WeChat article cover background in a classic editorial magazine style. Warm parchment (#EFE6D4) paper field with visible fine grain and a gentle vignette, literary and weighty. A delicate thin horizontal rule near the top. Minimal, dignified, no busy graphics. Keep the composition text-friendly: clean parchment space across the canvas for large serif Chinese headline typography, with calm open negative space on the right. No readable text, no fake Chinese characters, no ornaments, no logos, no people, no portrait, no watermark. Refined, print-magazine, publish-ready.
```

## 四、`wired-black` · WIRED 未来张力（周四·基准）

```text
Create a wide 2.35:1 WeChat article cover background in a bold futuristic tech-magazine style. Pure near-black (#09090B) field with a very subtle technical grid and faint scanline texture, high-tension and clean. A single bright red (#FF2A2A) accent bar near the top. Sharp, graphic, high-contrast, no clutter. Keep the composition text-friendly: clean black space across the canvas for ultra-bold white Chinese headline typography, with dark open negative space on the right. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Bold, cinematic, publish-ready.
```

## 五、`kinfolk-whitespace` · KINFOLK 东方留白（周五·基准）

```text
Create a wide 2.35:1 WeChat article cover background in a serene oriental-whitespace style. Soft off-white (#FAF8F3) field, extremely minimal, generous empty space, the faintest warm paper grain, quiet and calm. Almost no decoration: at most one short thin warm-gray hairline. Zen, restrained, breathing room. Keep the composition text-friendly: clean white space across the canvas for widely letter-spaced thin serif Chinese headline typography, with generous empty negative space on the right. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Calm, premium, publish-ready.
```

## 六、`harvard-navy` · HARVARD 学术克制（周六·基准）

```text
Create a wide 2.35:1 WeChat article cover background in a restrained academic style. Deep navy blue (#122848) gradient, darker at the edges, subtle grain, scholarly and composed. A slim gold (#C9A227) vertical band along the left edge and a small plain gold circular seal motif in the upper-left. Keep the composition text-friendly: clean navy space across the canvas for large serif Chinese headline typography, with calm open negative space on the right. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Dignified, premium, publish-ready.
```

## 七、`tech-purple-gold` · 紫黑金科技风（周日·基准）

```text
Create a wide 2.35:1 WeChat article cover background, cinematic high-end Chinese tech/business thumbnail style. Dark black/navy base, electric purple and violet neon glow, deep perspective, subtle speed lines, digital UI cards, charts, automation workflow icons, knowledge graph nodes. Keep the left 62% clean and dark for large Chinese headline typography; let abstract tech graphics fill the right side as a visual anchor. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. High contrast, premium commercial poster, sharp, polished, publish-ready.
```

## 科技风候补成员（CODEX=周日·候补 / AGENT=周六·候补 / CLEAN=周五·候补）

下列 3 套科技风已并入星期轮换（不再「仅显式指定」），也可直接点名锁定。

### `codex-blue-gold` · 黑蓝金科技风（周日·候补）

```text
Create a wide 2.35:1 WeChat article cover background, premium Chinese tech/business thumbnail style. Dark black and navy cyber studio, electric blue light trails, golden sparks, code panels, automation workflow nodes, growth dashboards, glowing AI server core on the right-middle. Keep the left 62% clean and dark for large Chinese headline typography; let abstract tech graphics fill the right side as a visual anchor. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. High contrast, cinematic, sharp, polished, publish-ready.
```

### `agent-cyber` · 智能体蓝青风（周六·候补）

```text
Create a wide 2.35:1 WeChat article cover background, high-end AI business automation style. Dark navy operations room, glowing agent network, business dashboards, automated workflow pipeline, data cards, arrows, growth charts, blue/cyan neon, subtle gold accents. Leave the left 64% clean and dark for bold Chinese headline typography; let abstract tech graphics fill the right side as a visual anchor. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Sharp, commercial, cinematic, publish-ready.
```

### `clean-business-tech` · 极简商务科技风（周五·候补）

```text
Create a wide 2.35:1 clean premium technology banner background. Dark gradient, subtle blue/purple glow, minimalist UI panels, knowledge graph lines, elegant depth, few decorative elements, strong negative space on the left for headline, calm open right side. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. High-end consulting brand style.
```

---

## 2026-10 新增 4 套（封面文字统一思源黑体 Bold）

### `swiss-grid` · HELVETIC 瑞士网格（周一·候补）

```text
Create a wide 2.35:1 WeChat article cover background in an International Typographic Style (Swiss design) mood. Warm-neutral paper white (#F5F3EE) field with an extremely faint light-gray modular grid of thin hairlines and the subtlest paper grain, crisp and rational. A single signal-red (#E32219) hairline rule near the top edge and one short black hairline; nothing else, maximal discipline. Keep the composition text-friendly: clean paper-white space across the canvas for large bold sans-serif Chinese headline typography, with generous open negative space on the right. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Bauhaus-adjacent, museum-print quality, publish-ready.
```

### `aegean-postcard` · AEGEAN 爱琴海明信片（周二·候补）

```text
Create a wide 2.35:1 WeChat article cover background in a sun-bleached Aegean postcard style. Warm off-white / sun-washed cream (#FAF3E3) paper field with fine grain, Aegean blue (#1B7FA8) and terracotta (#E2725B) appearing only as very soft abstract washes or a horizon hint, holiday-bright but restrained. Keep the composition text-friendly: clean pale space across the upper and middle canvas for large bold sans-serif Chinese headline typography, and leave the lower ~15% of the frame flat and quiet so a solid terracotta band can sit there. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Editorial travel-magazine feel, premium, publish-ready.
```

### `newsprint-extra` · BROADSHEET 号外（周三·候补）

```text
Create a wide 2.35:1 WeChat article cover background in a vintage broadsheet newspaper 'extra' edition style. Newsprint off-white (#F7F5F0) paper with visible fibrous grain and a gentle vignette, strictly black ink and one vermilion red (#C8102E) accent, absolutely no other colors. Faint vertical column hairlines in light gray, an ink-heavy top area, gritty and urgent, printed-on-cheap-paper texture. Keep the composition text-friendly: clean paper space across the canvas for large bold sans-serif Chinese headline typography, with calm open negative space on the right. No readable text, no fake Chinese characters, no headlines, no logos, no people, no portrait, no watermark. Authentic print-press look, publish-ready.
```

### `deco-noir` · DECO 盖茨比之夜（周四·候补）

```text
Create a wide 2.35:1 WeChat article cover background in an Art Deco / Great Gatsby midnight-luxe style. Deep midnight peacock green (#0E3B2E) field with a darker vignette, champagne gold (#C9A227) appearing as thin symmetric deco linework, subtle sunburst rays and stepped chevron motifs near the corners, luxurious and symmetrical. Keep the composition text-friendly: a calm dark field across the canvas for large bold gold-tinted Chinese headline typography, with quiet open negative space on the right. No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. 1920s glamour, high-contrast, premium print feel, publish-ready.
```
