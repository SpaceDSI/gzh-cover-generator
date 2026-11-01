#!/usr/bin/env python3
"""Semantic, composable right-side artwork for 2.35:1 WeChat covers.

Why this exists
---------------
The right ~20% of the canvas is deliberate negative space (the headline block
stops at 78–80% of the width). A single fixed glyph there reads as repetition:
whichever article you publish, the right side looks the same. This module turns
that area into a **small generated composition**:

    semantic extraction -> primary icon + secondary icon + accent layer
                       -> one of four layout archetypes
                       -> deterministic variation by content

So two different articles get visibly different artwork (different icon pair,
layout, accent set, size mix, palette weight), while **the same article always
reproduces the same cover** — the composition seed is derived from the copy
itself, not from the clock.

Design constraints (hard)
-------------------------
1. **No layout change.** The headline grid (left margin, right limit, spacing,
   font scale) is untouched — artwork only ever draws inside the reserved right
   zone, and the drawn layer is clipped to that zone as a final guarantee.
2. **No new dependency and no image asset.** Pillow primitives only (lines /
   arcs / rounded rects / polygons / dots), so it scales to any export size and
   adds zero bytes of artwork to the skill.
3. **Never competes with the type.** Low alpha, palette taken from the style's
   own accent / ink / ink_soft, drawn *below* the text layer, and **no text at
   all** inside the artwork (cards are skeletons), so it can never be misread as
   part of the headline.
4. **Responsive by construction.** On a narrow / short canvas the zone collapses
   and the artwork is silently skipped (the equivalent of "hide on small
   screens"), so no layout ever overflows or scrolls.

Usage: driven from ``render_wechat_cover.py`` via ``draw_composition()``;
inspect standalone with ``--list`` / ``--plan "标题"`` / ``--variants`` / ``--zone``.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
import zlib
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    from PIL import Image, ImageDraw
except ImportError:  # 延迟到真正绘制时才报错：保证 --help/无子命令探测退出码为 0
    Image = ImageDraw = None

RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
Box = Tuple[int, int, int, int]

MOTIF_IDS: Tuple[str, ...] = (
    "agent",      # 智能体 / 工作流编排
    "data",       # 数据 / 增长图表
    "knowledge",  # 知识图谱 / 笔记网络
    "checklist",  # 清单 / 步骤卡片
    "growth",     # 变现 / 阶梯增长
    "pulse",      # 效率 / 速度雷达
    "gear",       # 工具 / 搭建模块
    "quote",      # 观点 / 编辑随笔
    "life",       # 生活 / 美食日常
    "finance",    # 投资 / 理财资产
    "waves",      # 抽象波纹（兜底）
)

MOTIF_NAMES: Dict[str, str] = {
    "agent": "智能体·工作流编排",
    "data": "数据·增长图表",
    "knowledge": "知识·图谱网络",
    "checklist": "清单·步骤卡片",
    "growth": "变现·阶梯增长",
    "pulse": "效率·速度雷达",
    "gear": "工具·模块搭建",
    "quote": "观点·编辑随笔",
    "life": "生活·日常杯盏",
    "finance": "投资·资产叠币",
    "waves": "抽象波纹（兜底）",
}

# Topic keywords -> motif. Matched against eyebrow / hero lines / subtitle /
# tags / topic summary / original title, weighted by keyword length and position.
KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "agent": ("智能体", "agent", "自动化", "工作流", "流程", "编排", "机器人", "bot", "workflow", "流水线", "多智能体",
              "提示词", "prompt", "大模型", "llm", "ai", "copilot", "助手", "对话", "rag", "应用"),
    "data": ("数据", "增长", "指标", "图表", "复盘", "分析", "报表", "看板", "data", "chart", "统计", "趋势",
             "转化", "留存", "日活", "涨粉", "阅读量", "曝光", "漏斗", "同比", "环比", "指标拆解", "kpi"),
    "knowledge": ("知识", "笔记", "双链", "资料", "学习", "阅读", "卡片", "knowledge", "obsidian", "记忆", "库",
                  "读书", "课程", "科普", "认知", "思维模型", "学科", "理论", "概念", "教程入门", "理解"),
    "checklist": ("清单", "步骤", "教程", "指南", "操作", "配置", "上手", "checklist", "实操", "做法", "流程清单",
                  "模板", "sop", "避坑", "新手", "入门", "手把手", "自查", "检查", "要点", "方法论"),
    "growth": ("变现", "副业", "收入", "赚钱", "商业", "生意", "营收", "成本", "利润", "增长曲线", "单价",
               "引流", "获客", "客户", "定价", "报价", "开单", "产品", "卖点", "转化率", "客单价", "复购"),
    "pulse": ("效率", "提速", "速度", "时间", "并发", "性能", "响应", "省时", "加速", "吞吐",
              "延迟", "快捷", "即时", "省力", "降本", "倍速", "压缩", "异步", "并行", "自动化省时"),
    "gear": ("工具", "插件", "搭建", "开发", "代码", "部署", "脚本", "工程", "api", "sdk", "skill", "接口",
             "配置", "环境", "服务器", "云", "自建", "开源", "框架", "终端", "命令行", "pipeline", "架构"),
    "quote": ("观点", "随笔", "思考", "判断", "为什么", "真相", "代价", "反思", "心得", "认知",
              "本质", "底层", "心法", "思维", "取舍", "选择", "价值观", "深度", "锐评", "洞察"),
    "life": ("咖啡", "美食", "生活", "日常", "习惯", "早餐", "做饭", "茶", "奶茶", "饮品", "餐", "食谱",
             "睡眠", "运动", "健身", "居家", "收纳", "旅行", "通勤", "周末", "好物", "生活方式"),
    "finance": ("投资", "理财", "股票", "基金", "资产", "存钱", "复利", "财务", "钱", "收益", "回报",
                "仓位", "估值", "市盈率", "分红", "指数", "定投", "风险", "配置", "财富", "账本"),
}

# Semantically adjacent partner for each primary, so the two icons in one
# composition read as one idea instead of two unrelated stickers.
COMPLEMENTS: Dict[str, str] = {
    "agent": "data",
    "data": "growth",
    "growth": "data",
    "knowledge": "quote",
    "checklist": "gear",
    "gear": "checklist",
    "pulse": "waves",
    "quote": "knowledge",
    "life": "quote",
    "finance": "growth",
    "waves": "pulse",
}

ARCHETYPES: Tuple[str, ...] = ("stack", "stagger", "centerpiece", "ladder")
ARCHETYPE_NAMES: Dict[str, str] = {
    "stack": "上下分层",
    "stagger": "错位对角",
    "centerpiece": "大图居中",
    "ladder": "阶梯三段",
}
ACCENTS: Tuple[str, ...] = ("dots", "ticks", "brackets", "spark", "arcs")

# Minimum canvas size / zone size for the artwork to appear (responsive guard).
MIN_CANVAS_W = 1400
MIN_CANVAS_H = 380
MIN_ZONE_W = 150
MIN_ZONE_H = 180
MIN_SECONDARY_H = 96      # below this the secondary icon would turn to mush


# ----------------------------------------------------------------- semantics
def is_disabled(value: Any) -> bool:
    return str(value or "").strip().lower() in ("off", "none", "false", "0", "关", "关闭", "无")


def score_semantics(parts: Sequence[Tuple[str, float]]) -> Dict[str, float]:
    """Score every motif family from ``(text, weight)`` pairs.

    A hit scores ``len(keyword) * 2`` plus a small bonus when it appears early
    in the string (headline-first reading order). Longer keywords win ties.
    """
    scores = {mid: 0.0 for mid in MOTIF_IDS}
    for text, mult in parts:
        hay = str(text or "").lower()
        if not hay.strip():
            continue
        for mid in MOTIF_IDS:
            for kw in KEYWORDS.get(mid, ()):
                k = kw.lower()
                pos = hay.find(k)
                if pos < 0:
                    continue
                scores[mid] += (len(k) * 2.0 + (0.6 if pos < 8 else 0.0)) * max(0.1, mult)
    return scores


def motif_for_text(text: str) -> Optional[str]:
    """Pick the strongest single motif id for free-form text (back-compat helper)."""
    if not (text or "").strip():
        return None
    scores = score_semantics([(text, 1.0)])
    best = max(scores, key=lambda m: (scores[m], -MOTIF_IDS.index(m)))
    return best if scores[best] > 0 else None


def _brief_parts(brief: Dict[str, Any]) -> List[Tuple[str, float]]:
    """Weighted copy fragments: the hero line carries the topic, tags only hint."""
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


def content_seed(brief: Dict[str, Any], base_seed: int = 0) -> int:
    """Stable seed derived from the copy (+ the brief's own seed).

    Same article -> same artwork on every run; different article -> different
    artwork. Passing a different ``seed`` in the brief is the intentional way to
    ask for an alternate take on the same article.
    """
    text = "|".join(t for t, _ in _brief_parts(brief)).lower()
    return (zlib.crc32(text.encode("utf-8")) ^ (int(base_seed or 0) * 2654435761)) & 0x7FFFFFFF


def plan_composition(brief: Dict[str, Any], preset: Dict[str, Any], base_seed: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Plan the right-side composition for a cover brief.

    Returns ``None`` when disabled (``right_motif: off``). Otherwise a dict with
    primary/secondary icons, layout archetype, accent set and the seed used.
    """
    # 2026-10-25: vector motif deprecated in favor of the ImageGen theme scene.
    # Default is now OFF so the vector layer never draws unless explicitly enabled.
    requested = str(brief.get("right_motif", "off") or "off").strip().lower()
    if is_disabled(requested):
        return None

    if base_seed is None:
        base_seed = int(brief.get("seed", 0) or 0)
    seed = content_seed(brief, base_seed)
    rnd = random.Random(seed)

    scores = score_semantics(_brief_parts(brief))
    ranked = sorted(MOTIF_IDS, key=lambda m: (-scores[m], MOTIF_IDS.index(m)))
    matched = [m for m in ranked if scores[m] > 0]

    if requested and requested not in ("auto", "默认") and requested in MOTIF_IDS:
        primary = requested                      # explicit override, still composed
    elif matched:
        primary = matched[0]
    else:
        # No keyword hit: vary by content seed so different unmatched articles
        # still get different artwork (never a single fixed fallback motif).
        primary = MOTIF_IDS[rnd.randrange(len(MOTIF_IDS))]

    secondary = next((m for m in matched if m != primary), None)
    if secondary is None:
        secondary = COMPLEMENTS.get(primary, "waves")
    if secondary == primary:
        secondary = "waves" if primary != "waves" else "pulse"

    archetype = ARCHETYPES[rnd.randrange(len(ARCHETYPES))]
    accents = rnd.sample(list(ACCENTS), 2)
    # Size rhythm: primary always dominant, secondary proportionally smaller.
    primary_share = round(rnd.uniform(0.50, 0.60), 2)
    secondary_share = round(rnd.uniform(0.26, 0.36), 2)

    return {
        "primary": primary,
        "secondary": secondary,
        "archetype": archetype,
        "accents": accents,
        "primary_share": primary_share,
        "secondary_share": secondary_share,
        "seed": seed,
        "scores": {k: round(v, 1) for k, v in scores.items() if v > 0},
        "signature": f"{primary}+{secondary}/{archetype}",
    }


def resolve_motif(brief: Dict[str, Any], preset: Dict[str, Any]) -> Optional[str]:
    """Back-compat: the primary motif id (or None when disabled)."""
    plan = plan_composition(brief, preset)
    return plan["primary"] if plan else None


# ---------------------------------------------------------------------- layout
def motif_zone(size: Tuple[int, int], preset: Dict[str, Any]) -> Optional[Box]:
    """Return the drawable right zone ``(x0, y0, x1, y1)``, or ``None`` to skip.

    The zone starts *after* the headline's right limit (80% of the width, 78%
    for vertical-bar styles) and stops before the right safe margin / deco
    frame, so it can never overlap the type. On a narrow or short canvas it
    collapses and everything is skipped.
    """
    w, h = size
    if w < MIN_CANVAS_W or h < MIN_CANVAS_H:
        return None
    decor = preset.get("decor", {}) or {}
    limit_ratio = 0.78 if decor.get("vertical_bar") else 0.80
    x0 = int(w * limit_ratio) + int(w * 0.014)
    x1 = int(w * 0.955)          # stay inside the deco frame / right safe margin
    y0 = int(h * 0.135)          # below the masthead band and the deco frame top
    y1 = int(h * 0.790)          # above the bottom tag row
    if x1 - x0 < MIN_ZONE_W or y1 - y0 < MIN_ZONE_H:
        return None
    return (x0, y0, x1, y1)


def zone_for(size: Tuple[int, int], preset: Dict[str, Any]) -> Optional[Box]:
    """Public helper (tests / debugging): the zone that would be used."""
    return motif_zone(size, preset)


def _layout(plan: Dict[str, Any], zone: Box) -> Tuple[Box, Optional[Box], List[Box]]:
    """Split the zone into primary / secondary / accent boxes for the archetype."""
    x0, y0, x1, y1 = zone
    W, H = x1 - x0, y1 - y0
    a = plan["archetype"]
    p_share, s_share = plan["primary_share"], plan["secondary_share"]

    if a == "stack":
        ph = int(H * p_share)
        sh = int(H * s_share)
        primary = (x0, y0, x1, y0 + ph)
        secondary = (x0, y1 - sh, x1, y1)
        accents = [
            (x0, y0 + ph + int(H * 0.02), x1, y1 - sh - int(H * 0.02)),   # middle gap
            (x1 - int(W * 0.22), y0 + int(H * 0.03), x1, y0 + int(H * 0.11)),
        ]
    elif a == "stagger":
        ph = int(H * p_share * 0.92)
        sh = int(H * s_share)
        primary = (x0, y0, x1, y0 + ph)
        sx = x0 + int(W * 0.18)
        secondary = (sx, y1 - sh, x1, y1)
        accents = [
            (x0, y0 + ph + int(H * 0.03), sx - int(W * 0.04), y1 - int(H * 0.05)),
            (sx, y1 - sh - int(H * 0.10), x1, y1 - sh - int(H * 0.02)),
        ]
    elif a == "centerpiece":
        primary = (x0 + int(W * 0.04), y0 + int(H * 0.10), x1 - int(W * 0.04), y0 + int(H * p_share * 1.05))
        secondary = (x1 - int(W * 0.40), y0, x1, y0 + int(H * 0.13))
        accents = [
            (x0, y0 + int(H * p_share * 1.10), x1, y1),                   # below the hero icon
            (x0, y0 + int(H * 0.02), x0 + int(W * 0.30), y0 + int(H * 0.10)),
        ]
    else:  # ladder
        ph = int(H * p_share * 0.88)
        sh = int(H * s_share * 0.92)
        primary = (x0, y0, x1, y0 + ph)
        secondary = (x0, y0 + ph + int(H * 0.06), x1, y0 + ph + int(H * 0.06) + sh)
        accents = [
            (x0, y1 - int(H * 0.14), x1, y1),
            (x1 - int(W * 0.20), y0 + ph + int(H * 0.01), x1, y0 + ph + int(H * 0.05)),
        ]

    if secondary[3] - secondary[1] < MIN_SECONDARY_H:
        secondary = None
    return primary, secondary, accents


# ----------------------------------------------------------------- primitives
def _elbow(d, p0, p1, color: RGBA, width: int = 3) -> None:
    mx = (p0[0] + p1[0]) // 2
    d.line((p0[0], p0[1], mx, p0[1]), fill=color, width=width)
    d.line((mx, p0[1], mx, p1[1]), fill=color, width=width)
    d.line((mx, p1[1], p1[0], p1[1]), fill=color, width=width)
    head = max(6, width * 3)
    d.line((p1[0] - head, p1[1] - head, p1[0], p1[1]), fill=color, width=width)
    d.line((p1[0] - head, p1[1] + head, p1[0], p1[1]), fill=color, width=width)


def _tick(d, x: int, y: int, s: int, color: RGBA, width: int = 3) -> None:
    d.line((x, y, x + s * 0.4, y + s * 0.45), fill=color, width=width)
    d.line((x + s * 0.4, y + s * 0.45, x + s, y - s * 0.35), fill=color, width=width)


def _hexagon(d, cx: int, cy: int, r: int, fill: RGBA, outline: RGBA, width: int = 2) -> None:
    pts = []
    for i in range(6):
        ang = math.radians(60 * i - 30)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=outline)
    if width:
        d.line(pts + [pts[0]], fill=outline, width=width)


# ------------------------------------------------------------- icon drawers
def _agent(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    cw, ch = int(w * 0.66), max(34, int(h * 0.19))
    nodes = [
        (x0, y0),
        (x1 - cw, y0 + int(h * 0.30)),
        (x0, y0 + int(h * 0.60)),
        (x1 - cw, y1 - ch),
    ]
    for nx, ny in nodes:
        d.rounded_rectangle((nx, ny, nx + cw, ny + ch), radius=14, fill=T, outline=A, width=2)
        for k in range(2):
            ly = ny + int(ch * (0.38 + k * 0.26))
            d.line((nx + 18, ly, nx + cw - int(cw * (0.22 + 0.34 * k)), ly), fill=S, width=4)
        cx, cy = nx + 11, ny + int(ch * 0.30)
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=A)
    for a, b in zip(nodes, nodes[1:]):
        _elbow(d, (a[0] + cw, a[1] + ch // 2), (b[0], b[1] + ch // 2), A, 3)


def _data(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    base = y1 - int(h * 0.05)
    n = 5
    bw = max(10, int(w / (n * 2.0)))
    gap = max(6, (w - n * bw) // (n - 1))
    hmax = int(h * 0.52)
    heights = (0.42, 0.70, 0.56, 1.0, 0.84)
    tops = []
    for i, hv in enumerate(heights):
        bx = x0 + i * (bw + gap)
        bh = max(8, int(hmax * hv))
        d.rounded_rectangle((bx, base - bh, bx + bw, base), radius=6,
                            fill=(*A[:3], int(A[3] * 0.55)) if i % 2 else T)
        tops.append((bx + bw // 2, base - bh))
    d.line((x0 - 8, base, x1, base), fill=S, width=3)
    d.line(tops, fill=S, width=4, joint="curve")
    for px, py in tops:
        d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=A, outline=S, width=2)


def _knowledge(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    pts = [
        (x0 + int(w * rnd.uniform(0.05, 0.35)), y0 + int(h * rnd.uniform(0.05, 0.35))),
        (x1 - int(w * rnd.uniform(0.10, 0.30)), y0 + int(h * rnd.uniform(0.05, 0.30))),
        (x0 + int(w * rnd.uniform(0.30, 0.60)), y0 + int(h * rnd.uniform(0.40, 0.60))),
        (x1 - int(w * rnd.uniform(0.30, 0.55)), y0 + int(h * rnd.uniform(0.45, 0.65))),
        (x0 + int(w * rnd.uniform(0.05, 0.30)), y1 - int(h * rnd.uniform(0.05, 0.25))),
        (x1 - int(w * rnd.uniform(0.05, 0.25)), y1 - int(h * rnd.uniform(0.05, 0.20))),
    ]
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            if math.hypot(a[0] - b[0], a[1] - b[1]) < max(w, h) * 0.62:
                d.line((a[0], a[1], b[0], b[1]), fill=S, width=2)
    for i, (px, py) in enumerate(pts):
        r = 13 if i % 3 == 0 else 8
        d.ellipse((px - r, py - r, px + r, py + r), fill=A if i % 3 == 0 else T, outline=S, width=2)


def _checklist(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    ch = int((h - int(h * 0.10)) / 3)
    for i in range(3):
        ny = y0 + i * (ch + int(h * 0.05))
        d.rounded_rectangle((x0, ny, x1, ny + ch), radius=14, fill=T, outline=A, width=2)
        _tick(d, x0 + 18, ny + int(ch * 0.46), 18, A, 3)
        for k in range(2):
            ly = ny + int(ch * (0.36 + k * 0.30))
            d.line((x0 + 52, ly, x1 - int(w * (0.18 + 0.26 * k)), ly), fill=S, width=4)


def _growth(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    base = y1 - int(h * 0.06)
    steps = 4
    sw = max(16, int(w / (steps * 1.6)))
    gap = max(6, (w - steps * sw) // max(1, steps - 1))
    sh = int(h * 0.18)
    for i in range(steps):
        bx = x0 + i * (sw + gap)
        top = base - sh * (i + 1)
        d.rounded_rectangle((bx, top, bx + sw, base), radius=8,
                            fill=(*A[:3], int(A[3] * 0.5 + i * 18)), outline=A, width=2)
    ax, ay = x1 - int(w * 0.08), y0 + int(h * 0.10)
    d.line((ax, base - sh * steps - int(h * 0.10), ax, ay), fill=S, width=4)
    d.polygon([(ax - 12, ay + 16), (ax + 12, ay + 16), (ax, ay - 6)], fill=A)


def _pulse(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    cx, cy = x0 + w // 2, y0 + h // 2
    rmax = int(min(w, h) * 0.46)
    for i, rf in enumerate((1.0, 0.72, 0.44, 0.2)):
        r = int(rmax * rf)
        d.arc((cx - r, cy - r, cx + r, cy + r), 200, 340, fill=A if i % 2 == 0 else S, width=3)
    for k in range(9):
        ang = math.radians(200 + (140 * k / 8))
        r0, r1 = int(rmax * 1.02), int(rmax * 1.16)
        d.line((cx + r0 * math.cos(ang), cy + r0 * math.sin(ang),
                cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)), fill=T, width=2)
    d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=A, outline=S, width=2)
    d.arc((cx - rmax, cy - rmax, cx + rmax, cy + rmax), 20, 90, fill=S, width=4)


def _gear(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    r = int(min(w, h) * 0.26)
    spots = [(x0 + r + 6, y0 + r), (x1 - r - 6, y0 + r + int(h * 0.18)), (x0 + r + int(w * 0.12), y1 - r - 4)]
    for i, (cx, cy) in enumerate(spots):
        _hexagon(d, cx, cy, int(r * (1.0 - 0.22 * i)), T if i % 2 else (*A[:3], int(A[3] * 0.6)), A, 2)
    for a, b in zip(spots, spots[1:]):
        d.line((a[0], a[1], b[0], b[1]), fill=S, width=3)
    cx, cy = spots[0]
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=A)


def _quote(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    d.rectangle((x0, y0, x0 + int(w * 0.16), y0 + int(w * 0.16)), fill=A)
    for i in range(4):
        ly = y0 + int(h * (0.30 + i * 0.14))
        d.line((x0, ly, x1 - int(w * (0.05 + 0.22 * (i % 3))), ly), fill=S, width=4)
    for i in range(3):
        px = x1 - int(w * (0.14 + 0.14 * i))
        d.ellipse((px - 6, y1 - int(h * 0.10) - 6, px + 6, y1 - int(h * 0.10) + 6), fill=T)


def _waves(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    for li in range(4):
        amp = int(h * 0.045)
        base_y = y0 + int(h * (0.16 + li * 0.20))
        pts = []
        for i in range(25):
            t = i / 24
            pts.append((x0 + int(w * t), base_y + int(amp * math.sin(t * math.pi * 2 + li * 0.8))))
        d.line(pts, fill=A if li % 2 == 0 else S, width=3 if li % 2 == 0 else 2)


# ------------------------------------------------------------ accent layers
def _acc_dots(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    cols = max(2, min(7, w // 26))
    rows = max(1, min(3, h // 26))
    for r in range(rows):
        for c in range(cols):
            px = x0 + int(w * (c + 0.5) / cols)
            py = y0 + int(h * (r + 0.5) / rows)
            rad = 2 + (c + r) % 3
            d.ellipse((px - rad, py - rad, px + rad, py + rad),
                      fill=A if (c + r) % 3 == 0 else S)


def _acc_ticks(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    y = y0 + h // 2
    d.line((x0, y, x1, y), fill=S, width=2)
    n = max(3, min(9, w // 32))
    for i in range(n):
        px = x0 + int(w * (i + 0.5) / n)
        ln = int(h * (0.42 if i % 3 == 0 else 0.24))
        d.line((px, y - ln, px, y + ln), fill=A if i % 3 == 0 else S, width=2)


def _acc_brackets(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    arm = max(10, min(x1 - x0, y1 - y0) // 4)
    for cx, cy, dx, dy in ((x0, y0, 1, 1), (x1, y1, -1, -1)):
        d.line((cx, cy, cx + dx * arm, cy), fill=A, width=3)
        d.line((cx, cy, cx, cy + dy * arm), fill=A, width=3)


def _acc_spark(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    for i in range(3):
        cx = x0 + int(w * (0.2 + 0.3 * i))
        cy = y0 + int(h * (0.3 + 0.25 * (i % 2)))
        r = rnd.randint(6, 11)
        d.line((cx - r, cy, cx + r, cy), fill=A, width=2)
        d.line((cx, cy - r, cx, cy + r), fill=A, width=2)
        d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=S)


def _acc_arcs(d, z, A, S, T, rnd):
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    r = min(w, h)
    for i, f in enumerate((1.0, 0.66, 0.34)):
        rr = int(r * f)
        d.arc((x1 - rr, y1 - rr, x1 + rr, y1 + rr), 180, 270, fill=A if i == 0 else S, width=2)


def _life(d, z, A, S, T, rnd):
    """生活 / 美食日常：杯盏 + 热气 + 一枚小叶，暖而轻。"""
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    # cup body
    cw, ch = int(w * 0.52), int(h * 0.52)
    cx0 = x0 + int(w * 0.16)
    cy0 = y0 + int(h * 0.34)
    d.rounded_rectangle((cx0, cy0, cx0 + cw, cy0 + ch), radius=16, fill=T, outline=A, width=3)
    # saucer
    d.line((cx0 - 12, cy0 + ch + 10, cx0 + cw + 12, cy0 + ch + 10), fill=S, width=4)
    # handle
    d.arc((cx0 + cw - 6, cy0 + int(ch * 0.18), cx0 + cw + int(cw * 0.34), cy0 + int(ch * 0.72)),
          280, 80, fill=A, width=4)
    # steam
    for i in range(3):
        sx = cx0 + int(cw * (0.28 + i * 0.22))
        pts = []
        for k in range(8):
            t = k / 7
            pts.append((sx + int(6 * math.sin(t * math.pi * 2 + i)),
                        cy0 - int(h * 0.06) - int(h * 0.22 * t)))
        d.line(pts, fill=S if i % 2 else A, width=3)
    # small leaf top-right
    lx, ly = x1 - int(w * 0.16), y0 + int(h * 0.14)
    d.ellipse((lx - 18, ly - 11, lx + 18, ly + 11), fill=(*A[:3], int(A[3] * 0.7)), outline=A, width=2)
    d.line((lx - 16, ly + 8, lx + 16, ly - 8), fill=S, width=2)


def _finance(d, z, A, S, T, rnd):
    """投资 / 理财：叠币 + 上扬箭头 + 小圆点账本感。"""
    x0, y0, x1, y1 = z
    w, h = x1 - x0, y1 - y0
    base = y1 - int(h * 0.08)
    stacks = [(0.22, 3), (0.52, 5), (0.82, 4)]
    for fx, n in stacks:
        cwid = int(w * 0.18)
        cx = x0 + int(w * fx) - cwid // 2
        for i in range(n):
            ty = base - int(h * 0.09) * (i + 1)
            d.rounded_rectangle((cx, ty, cx + cwid, ty + int(h * 0.085)), radius=8,
                                fill=T if i % 2 else (*A[:3], int(A[3] * 0.55)), outline=A, width=2)
            d.line((cx + 8, ty + int(h * 0.042), cx + cwid - 8, ty + int(h * 0.042)), fill=S, width=2)
    # arrow up
    ax = x0 + int(w * 0.62)
    d.line((x0 + int(w * 0.12), base - int(h * 0.18), ax, y0 + int(h * 0.16)), fill=S, width=4)
    d.polygon([(ax - 12, y0 + int(h * 0.22)), (ax + 12, y0 + int(h * 0.22)), (ax, y0 + int(h * 0.10))], fill=A)
    # coin mark
    cx2, cy2 = x1 - int(w * 0.12), y0 + int(h * 0.12)
    d.ellipse((cx2 - 14, cy2 - 14, cx2 + 14, cy2 + 14), fill=T, outline=A, width=3)
    d.line((cx2 - 6, cy2, cx2 + 6, cy2), fill=S, width=3)


_ICONS = {
    "agent": _agent,
    "data": _data,
    "knowledge": _knowledge,
    "checklist": _checklist,
    "growth": _growth,
    "pulse": _pulse,
    "gear": _gear,
    "quote": _quote,
    "life": _life,
    "finance": _finance,
    "waves": _waves,
}

_ACCENTS = {
    "dots": _acc_dots,
    "ticks": _acc_ticks,
    "brackets": _acc_brackets,
    "spark": _acc_spark,
    "arcs": _acc_arcs,
}


# ---------------------------------------------------------------------- render
def _palette(preset: Dict[str, Any]) -> Tuple[RGBA, RGBA, RGBA]:
    """(outline/accent, ink/line, translucent fill) tuned per tone."""
    accent = tuple(preset.get("accent", (160, 80, 255)))
    ink = tuple(preset.get("ink", (255, 255, 255)))
    if preset.get("tone", "dark") == "dark":
        return (*accent, 170), (*ink, 120), (*accent, 95)
    return (*accent, 150), (*ink, 95), (*accent, 85)


def draw_composition(canvas, preset: Dict[str, Any], brief: Dict[str, Any],
                     seed: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Draw the planned composition. Returns the plan (or None when skipped)."""
    if Image is None:
        return None
    plan = plan_composition(brief, preset, base_seed=seed)
    if plan is None:
        return None
    zone = motif_zone(canvas.size, preset)
    if not zone:
        return None

    A, S, T = _palette(preset)
    primary, secondary, accents = _layout(plan, zone)

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(plan["seed"])

    # Accent layer goes first (behind the icons) and is small by design.
    for i, abox in enumerate(accents):
        if abox[2] - abox[0] < 24 or abox[3] - abox[1] < 16:
            continue
        _ACCENTS[plan["accents"][i % len(plan["accents"])]](d, abox, A, S, T, rnd)

    _ICONS[plan["primary"]](d, primary, A, S, T, rnd)
    if secondary:
        _ICONS[plan["secondary"]](d, secondary, A, S, T, rnd)

    # Hard clip to the reserved zone: a primitive can never leak into the
    # headline block, even if a drawer overshoots its box. The rectangle stops
    # one pixel short on the right/bottom edges so the *boundary* columns stay
    # untouched too.
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).rectangle((zone[0], zone[1], zone[2] - 1, zone[3] - 1), fill=255)
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", canvas.size, 0), mask))
    canvas.alpha_composite(layer)
    return plan


def draw_motif(canvas, preset: Dict[str, Any], motif: Optional[str], seed: int = 0) -> bool:
    """Legacy single-icon entry point (kept for scripts/tests that use it)."""
    if Image is None or not motif or motif not in _ICONS:
        return False
    zone = motif_zone(canvas.size, preset)
    if not zone:
        return False
    A, S, T = _palette(preset)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    _ICONS[motif](ImageDraw.Draw(layer), zone, A, S, T, random.Random(int(seed)))
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).rectangle((zone[0], zone[1], zone[2] - 1, zone[3] - 1), fill=255)
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", canvas.size, 0), mask))
    canvas.alpha_composite(layer)
    return True


def describe_plan(plan: Optional[Dict[str, Any]]) -> str:
    if not plan:
        return "off（右侧留空）"
    sec = MOTIF_NAMES.get(plan["secondary"], plan["secondary"])
    return (f"{plan['primary']}+{plan['secondary']} / {ARCHETYPE_NAMES[plan['archetype']]}"
            f" / 点缀 {'+'.join(plan['accents'])}（{MOTIF_NAMES[plan['primary']]} × {sec}）")


def describe(motif: Optional[str]) -> str:
    if not motif:
        return "off（右侧留空）"
    return f"{motif}（{MOTIF_NAMES.get(motif, motif)}）"


def _main() -> None:
    parser = argparse.ArgumentParser(description="Right-side artwork: list / plan / variants / zone probe.")
    parser.add_argument("--list", action="store_true", help="列出全部图标族与关键词")
    parser.add_argument("--resolve", metavar="TEXT", help="按一段文案推断主图标")
    parser.add_argument("--plan", metavar="TEXT", help="按文案输出完整构图方案（主+次+版式+点缀）")
    parser.add_argument("--variants", type=int, metavar="N", default=0,
                        help="示例：给出 N 篇不同文案的构图，检查变化度")
    parser.add_argument("--zone", metavar="WxH", help="探测画布尺寸下的右侧绘制区（如 2350x1000）")
    parser.add_argument("--motif", default="auto", help="auto / off / 指定主图标 id")
    if len(sys.argv) == 1:  # 无子命令：打印用法并 exit 0（沙箱探测要求）
        parser.print_help()
        print(f"\n可用图标: {', '.join(MOTIF_IDS)}；off/none 关闭。", file=sys.stderr)
        sys.exit(0)
    args = parser.parse_args()
    preset = {"tone": "light", "accent": (200, 16, 46), "ink": (20, 20, 22), "decor": {}}

    if args.list:
        for mid in MOTIF_IDS:
            print(f"{mid:<10} {MOTIF_NAMES[mid]:<16} 关键词: {', '.join(KEYWORDS.get(mid, ())[:8])}")
        print(f"版式: {', '.join(f'{a}({ARCHETYPE_NAMES[a]})' for a in ARCHETYPES)}")
        print(f"点缀: {', '.join(ACCENTS)}")
    if args.resolve:
        print(f"{args.resolve} -> {describe(motif_for_text(args.resolve))}")
    if args.plan:
        brief = {"hero_lines": [args.plan], "right_motif": args.motif}
        print(f"{args.plan}\n  -> {describe_plan(plan_composition(brief, preset))}")
    if args.variants:
        samples = [
            "我把周报交给了 Agent", "季度数据复盘：三个指标全线上扬", "Obsidian 双链笔记怎么搭",
            "照着这份清单配置你的工作流", "副业变现的三种收入结构", "把重复劳动提速 10 倍",
            "一套能跑起来的内容流水线", "为什么我不再追热点", "年度复盘：从 0 到 1 的一年",
        ]
        for i in range(min(args.variants, len(samples))):
            brief = {"hero_lines": [samples[i]], "right_motif": args.motif}
            p = plan_composition(brief, preset)
            print(f"  {samples[i]:<26} -> {describe_plan(p)}")
    if args.zone:
        try:
            w, h = (int(x) for x in str(args.zone).lower().split("x"))
        except ValueError:
            print("尺寸格式应为 WxH，如 2350x1000", file=sys.stderr)
            sys.exit(2)
        zone = motif_zone((w, h), {"decor": {}})
        print(f"{w}x{h} -> {'跳过（画布过窄/空间不足，等效窄屏隐藏）' if zone is None else zone}")


if __name__ == "__main__":
    _main()
