#!/usr/bin/env python3
"""Map a cover brief's title/topic to a rich center cinematic scene.

This is the semantic engine behind the "center thematic scene" upgrade.
Instead of leaving the right 40% empty (or drawing a light vector motif), the
ImageGen background is prompted with a concrete, story-driven scene derived from
the article's headline + topic — mirroring the reference covers (portal cards,
workflow wheel, desk still-life, data stream, content gallery, ...).

Output: an English scene-prompt fragment injected into the ImageGen prompt by
``export_imagegen_prompt.py``. The fragment carries the objects + lighting +
composition; the style base prompt carries the palette/tone. Always tone-aware
(``dark`` vs ``light``) so a paper style never gets a neon scene.

Design language lives in ``references/scene-archetypes.md``.
"""

from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))


# --------------------------------------------------------------------- lexicon
# Scene-oriented keyword lexicon (scene semantics, distinct from the icon lexicon).
SCENE_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "portal-cards": (
        "消息", "转发", "聚合", "入口", "归集", "变成", "一键转", "收件", "汇总", "收集",
        "打包", "转化为", "沉淀", "导入", "合并", "inbox", "聚合", "信息流", "微信", "群",
        "工作台", "看板", "面板", "控制台", "仪表盘", "dashboard",
    ),
    "workflow-wheel": (
        "自动", "飞轮", "流程", "循环", "闭环", "流水线", "编排", "pipeline", "批量",
        "定时", "无人值守", "一键", "工作流", "自动化", "运转", "循环", "sop", "runbook",
        "交给", "委托", "决策", "授权", "把关", "分工", "协作", "提效", "ai处理",
    ),
    "desk-metaphor": (
        "教程", "系统", "整理", "收纳", "笔记", "文件", "文件夹", "归档", "指南", "步骤",
        "实操", "上手", "资料", "文档", "手册", "入门", "手把手", "模板", "分类", "清单文件",
        "备课", "教案", "教师", "课件", "讲义", "教学", "授课", "课堂", "讲课", "作业",
        "批改", "板书", "学情", "考卷", "试卷", "讲稿", "备课包",
        "班主任", "班务", "班级", "考勤", "请假", "家长", "通知", "值日", "评优", "班会",
    ),
    "data-stream": (
        "token", "数据", "亿", "模型", "生成", "海量", "参数", "大模型", "算力", "语料",
        "训练", "指标", "图表", "报表", "统计", "吞吐", "并发", "埋点", "指标拆解",
    ),
    "journey-panels": (
        "自由", "解放", "轻松", "帮我", "一键", "神仙", "告别", "不用", "秒出", "爆款",
        "灵感", "创意", "成品", "躺平", "省心", "爽", "全自动帮我", "告别加班",
    ),
    "growth-steps": (
        "变现", "副业", "收入", "赚钱", "商业", "营收", "增长", "涨粉", "获客", "定价",
        "产品", "转化率", "客单价", "复购", "利润", "成本", "卖", "开单", "盈利", "roi",
    ),
    "knowledge-graph": (
        "知识", "双链", "认知", "概念", "学习", "思维", "体系", "网络", "图谱", "连接",
        "书", "课程", "读书", "理解", "理论", "学科", "记忆", "关联", "卡片盒", "zettel",
    ),
    "checklist-cards": (
        "清单", "避坑", "模板", "sop", "检查", "自查", "要点", "坑", "注意", "规范",
        "踩坑", "雷区", "核对", "验收", "标准", "核查", "盘点",
        "模块", "功能", "工具箱", "码上办", "扫码", "一站式", "办事", "事项", "版本",
        "上线", "更新", "升级", "v1", "工作台模块",
    ),
    "reform-cut": (
        "减法", "做减法", "精简", "裁减", "裁剪", "裁员", "缩编", "缩减", "削减", "改革",
        "特权", "公务员", "大锅饭", "铁饭碗", "机构", "编制", "冗员", "精兵简政", "整顿",
        "取缔", "取消", "收紧", "降本增效", "瘦身", "合并", "重组", "降薪", "问责",
    ),
}

SCENE_IDS: Tuple[str, ...] = tuple(SCENE_KEYWORDS.keys())
DEFAULT_SCENE = "portal-cards"

SCENE_NAMES: Dict[str, str] = {
    "portal-cards": "信息传送门",
    "workflow-wheel": "自动化飞轮",
    "desk-metaphor": "桌面实物隐喻",
    "data-stream": "数据流汇聚",
    "journey-panels": "内容画廊之旅",
    "growth-steps": "阶梯增长",
    "knowledge-graph": "知识图谱",
    "checklist-cards": "清单卡片",
    "reform-cut": "改革减法",
}


# ------------------------------------------------------------- scene fragments
# Tone-specific, concrete, story-driven center scene prompts. Objects and
# lighting only — never readable text, never people.
SCENE_PROMPTS: Dict[str, Dict[str, str]] = {
    "portal-cards": {
        "dark": (
            "A cinematic hero scene in the CENTER: a glowing luminous portal ring / vortex "
            "emitting streams of floating translucent UI content cards and dashboard tiles "
            "flying forward toward the viewer; each tile is a clean glass panel with abstract "
            "placeholder text-lines only (no readable characters); soft depth-of-field, dramatic "
            "rim light and warm bloom, premium commercial 3D render."
        ),
        "light": (
            "A bright airy hero scene in the CENTER: a soft light beam / opening where floating "
            "paper sheets and clean UI cards fan outward toward the viewer; each card has abstract "
            "placeholder text-lines only (no readable characters); gentle daylight, shallow depth "
            "of field, premium product-photography feel."
        ),
    },
    "workflow-wheel": {
        "dark": (
            "A cinematic hero scene in the CENTER: a large glowing circular automation wheel / "
            "orbiting ring of connected rounded step-nodes (abstract, no readable labels) linked by "
            "flowing arrows, with floating content cards docked at each node; moody studio volumetric "
            "light, premium 3D infographic."
        ),
        "light": (
            "A clean hero scene in the CENTER: a large soft circular workflow wheel of connected "
            "rounded step-nodes (abstract, no readable labels) with gentle flow arrows, floating "
            "cards around it; bright minimal studio, premium 3D infographic."
        ),
    },
    "desk-metaphor": {
        "dark": (
            "A cinematic still-life hero scene in the CENTER: an elegant desk with a glowing open "
            "folder / organizer releasing a swirl of floating paper sheets and cards; premium moody "
            "studio lighting, tactile materials, shallow depth of field, commercial photography."
        ),
        "light": (
            "A warm realistic still-life hero scene in the CENTER: a tidy desk with an open kraft / "
            "coral folder releasing a swirl of floating paper sheets, a notebook and a small plant; "
            "soft natural daylight, tactile paper texture, premium product photography."
        ),
    },
    "data-stream": {
        "dark": (
            "A cinematic hero scene in the CENTER: a massive luminous particle data-stream of glowing "
            "tokens and pixels flowing and coalescing into floating UI dashboard cards and slide "
            "panels; dark studio with cyan / violet volumetric light, high-tech premium 3D render."
        ),
        "light": (
            "A clean hero scene in the CENTER: a flowing stream of soft glowing data particles and thin "
            "lines converging into floating clean dashboard cards; bright airy studio, premium 3D render."
        ),
    },
    "journey-panels": {
        "dark": (
            "A cinematic hero scene in the CENTER: an expansive dreamlike landscape of floating content "
            "panels / slide gallery receding into dramatic clouds and light, with a path of light leading "
            "into it; epic scale, premium cinematic 3D render."
        ),
        "light": (
            "A bright cinematic hero scene in the CENTER: an open airy gallery of floating content panels "
            "and slide sheets stretching into soft clouds and daylight; a sense of abundance and ease, "
            "premium cinematic render."
        ),
    },
    "growth-steps": {
        "dark": (
            "A cinematic hero scene in the CENTER: rising glowing 3D bar-steps and stacked coin / pillar "
            "forms with a luminous upward arrow and floating metric cards; premium fintech studio lighting, "
            "warm gold accent glow, commercial 3D render."
        ),
        "light": (
            "A clean hero scene in the CENTER: soft 3D rising bar-steps and gentle coin stacks with an "
            "upward arrow and floating metric cards; bright studio, premium business-illustration feel."
        ),
    },
    "knowledge-graph": {
        "dark": (
            "A cinematic hero scene in the CENTER: a glowing 3D knowledge graph of interconnected nodes "
            "and curved link-lines forming a constellation, with floating card fragments; moody depth, "
            "premium 3D render."
        ),
        "light": (
            "A clean hero scene in the CENTER: a soft 3D constellation of connected knowledge nodes and "
            "thin curved links with floating paper cards; bright minimal studio, premium 3D render."
        ),
    },
    "checklist-cards": {
        "dark": (
            "A cinematic hero scene in the CENTER: a neat fan of floating checklist cards and stacked tile "
            "panels with abstract check-marks and placeholder text-lines (no readable characters); glowing "
            "edges, premium studio 3D render."
        ),
        "light": (
            "A clean hero scene in the CENTER: a neat fan of floating checklist cards and stacked paper "
            "tiles with abstract check-marks and placeholder text-lines (no readable characters); bright "
            "studio, premium 3D render."
        ),
    },
    "reform-cut": {
        "dark": (
            "A cinematic conceptual hero scene in the CENTER: a large elegant pair of glowing golden scissors "
            "and a slicing blade cutting down through a tall floating stack of official document cards and "
            "paper folders, a few cards trimmed and drifting away, a faint luminous world-map / globe grid "
            "in the background suggesting a global trend; moody authoritative studio lighting, warm gold "
            "accent glow, premium editorial 3D render."
        ),
        "light": (
            "A bright editorial hero scene in the CENTER: an elegant pair of scissors trimming a neat stack "
            "of floating paper documents and cards, trimmed pieces drifting down, a soft faint globe / "
            "world-map hint behind; clean daylight studio, premium magazine 3D render."
        ),
    },
}


# ------------------------------------------------------------------ semantics
def is_disabled(value: Any) -> bool:
    return str(value or "").strip().lower() in ("off", "none", "false", "0", "关", "关闭", "无")


def _brief_parts(brief: Dict[str, Any]) -> List[Tuple[str, float]]:
    """Weighted copy fragments (headline-first reading order)."""
    parts: List[Tuple[str, float]] = []
    hero = " ".join(str(x) for x in (brief.get("hero_lines") or []))
    if hero:
        parts.append((hero, 1.8))
    for key, mult in (("eyebrow", 1.2), ("title_original", 1.0), ("topic", 1.0), ("subtitle", 0.9)):
        val = str(brief.get(key, "") or "")
        if val.strip():
            parts.append((val, mult))
    tags = brief.get("bottom_tags") or []
    if tags:
        parts.append((" ".join(str(t) for t in tags), 0.75))
    return parts


def score_scenes(parts: Sequence[Tuple[str, float]]) -> Dict[str, float]:
    """Score every scene archetype from ``(text, weight)`` pairs."""
    scores = {sid: 0.0 for sid in SCENE_IDS}
    for text, mult in parts:
        hay = str(text or "").lower()
        if not hay.strip():
            continue
        for sid in SCENE_IDS:
            for kw in SCENE_KEYWORDS.get(sid, ()):
                k = kw.lower()
                pos = hay.find(k)
                if pos < 0:
                    continue
                scores[sid] += (len(k) * 2.0 + (0.6 if pos < 8 else 0.0)) * max(0.1, mult)
    return scores


def content_seed(brief: Dict[str, Any], base_seed: int = 0) -> int:
    """Stable seed from the copy (+ brief seed) for reproducible scene choice."""
    text = "|".join(t for t, _ in _brief_parts(brief)).lower()
    return (zlib.crc32(text.encode("utf-8")) ^ (int(base_seed or 0) * 2654435761)) & 0x7FFFFFFF


def resolve_scene(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Pick the center scene archetype for a brief.

    Honors ``right_scene``: an explicit id locks it, ``off`` disables (returns
    the disabled flag). Otherwise scores the copy and returns the best match
    (ties broken by content seed for stable variety across articles).
    """
    requested = str(brief.get("right_scene", "auto") or "auto").strip().lower()
    if is_disabled(requested):
        return {"id": None, "name": "disabled", "seed": content_seed(brief, brief.get("seed", 0)), "disabled": True}

    if requested and requested != "auto" and requested in SCENE_KEYWORDS:
        sid = requested
    else:
        scores = score_scenes(_brief_parts(brief))
        best = max(scores.values())
        if best <= 0:
            sid = DEFAULT_SCENE
        else:
            # Tie-break among equal-scoring scenes with the content seed, so two
            # different articles never collapse to the same look by accident.
            seed = content_seed(brief, brief.get("seed", 0))
            contenders = [s for s in SCENE_IDS if abs(scores[s] - best) < 1e-6]
            sid = contenders[seed % len(contenders)]

    return {"id": sid, "name": SCENE_NAMES[sid], "seed": content_seed(brief, brief.get("seed", 0)), "disabled": False}


def scene_prompt(brief: Dict[str, Any], tone: str = "dark") -> str:
    """Return the English scene fragment for the brief and style tone."""
    plan = resolve_scene(brief)
    if plan.get("disabled"):
        return ""
    sid = plan["id"]
    frag = SCENE_PROMPTS[sid]["dark" if str(tone).lower() != "light" else "light"]
    return frag


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve center scene concept from a cover brief.")
    parser.add_argument("brief", help="Path to cover_brief.json")
    parser.add_argument("--tone", default="dark", choices=["dark", "light"], help="Style tone")
    parser.add_argument("--plan", action="store_true", help="Print the resolved plan JSON")
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n提示：需要 cover_brief.json 路径参数。", file=sys.stderr)
        sys.exit(0)
    args = parser.parse_args()

    brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
    plan = resolve_scene(brief)
    if args.plan:
        print(json.dumps({"plan": plan, "tone": args.tone}, ensure_ascii=False, indent=2))
        return
    if plan.get("disabled"):
        print("(scene disabled)")
        return
    print(f"[scene={plan['id']} / {plan['name']}] [seed={plan['seed']}]")
    print()
    print(scene_prompt(brief, args.tone))


if __name__ == "__main__":
    main()
