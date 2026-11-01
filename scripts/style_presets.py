#!/usr/bin/env python3
"""Weekday-rotating style presets for the WeChat cover generator.

This module is the single source of truth for cover styles. It defines 14
styles that all participate in the automatic weekday rotation: every weekday
carries two looks — a base style and an alternate — and the pair alternates by
the parity of the ISO week number, so each weekday shows two distinct covers
across consecutive weeks (14 styles, none left out of the rotation).

Rotation (weekday(), 0 = Monday)
--------------------------------
    0  一  economist-crimson     ECONOMIST    财经权威      深红+白衬线+黑色刊头条      ISO 偶数周
           swiss-grid            HELVETIC     瑞士网格      纸白+淡灰网格+信号红规线    ISO 奇数周
    1  二  monocle-ivory         MONOCLE      文化极简      米白+左侧竖排+大字无衬线    ISO 偶数周
           aegean-postcard       AEGEAN       爱琴海明信片  晒白+爱琴海蓝+陶土色带      ISO 奇数周
    2  三  newyorker-parchment   NEW YORKER   编辑厚重      羊皮纸+斜体刊头+宋体大字    ISO 偶数周
           newsprint-extra       BROADSHEET   号外          新闻纸白+墨黑+朱红刊头      ISO 奇数周
    3  四  wired-black           WIRED        未来张力      纯黑+超粗白字+亮红强调      ISO 偶数周
           deco-noir             DECO         盖茨比之夜    午夜孔雀绿+香槟金+金线框    ISO 奇数周
    4  五  kinfolk-whitespace    KINFOLK      东方留白      素白+细衬线+极大字距        ISO 偶数周
           clean-business-tech   CLEAN        极简商务科技  暗色渐变+极简 UI           ISO 奇数周
    5  六  harvard-navy          HARVARD      学术克制      深蓝+金色印章+侧带          ISO 偶数周
           agent-cyber           AGENT        智能体蓝青风  黑底+蓝青+金色点缀          ISO 奇数周
    6  日  tech-purple-gold      TECH         紫黑金科技风  深空紫黑+流光金字+霓虹节点  ISO 偶数周
           codex-blue-gold       CODEX        黑蓝金科技风  黑底+电光蓝+金色大字        ISO 奇数周

Every preset participates in the rotation. `style_for_weekday()` resolves the
concrete id for any date (ISO week parity picks base vs alternate); when no
date is given the base style of that weekday is returned.

The four styles added in the 2026-10 expansion (swiss-grid / aegean-postcard /
deco-noir / newsprint-extra) set ``font: "source-han-sans"`` so their cover
text renders in Source Han Sans Bold (思源黑体 Bold); every other key keeps
the historic serif/sans behaviour.

Every generator script (render / brief / prompt export) reads from here so the
palette, tone, typography, decoration and prompt stay in sync.
"""

from __future__ import annotations

import argparse
import datetime as _dt
from typing import Any, Dict, List, Optional, Sequence, Tuple

RGB = Tuple[int, int, int]

# Brand mark used by masthead / vertical / seal decorations when the brief does
# not provide its own `masthead_text`.
BRAND_MARK = "智驭视界"

# Weekday -> base style id (index == date.weekday(), 0 = Monday).
# Used when the ISO week number is EVEN (and when no date is supplied).
WEEKDAY_ORDER: List[str] = [
    "economist-crimson",     # 一
    "monocle-ivory",         # 二
    "newyorker-parchment",   # 三
    "wired-black",           # 四
    "kinfolk-whitespace",    # 五
    "harvard-navy",          # 六
    "tech-purple-gold",      # 日
]

# Weekday -> alternate style id. Used when the ISO week number is ODD, so every
# weekday owns two distinct looks and all 14 presets stay in the rotation.
WEEKDAY_ALTERNATE: Dict[int, str] = {
    0: "swiss-grid",          # 一
    1: "aegean-postcard",     # 二
    2: "newsprint-extra",     # 三
    3: "deco-noir",           # 四
    4: "clean-business-tech", # 五
    5: "agent-cyber",         # 六
    6: "codex-blue-gold",     # 日
}

# Back-compat alias: the Sunday pair now follows the same ISO-week parity rule
# as every other weekday, so the Sunday cycle is simply [base, alternate].
SUNDAY_TECH_CYCLE: List[str] = [
    "tech-purple-gold",
    "codex-blue-gold",
]

WEEKDAY_ZH = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

DEFAULT_STYLE = "tech-purple-gold"


def _decor(
    *,
    masthead: Optional[dict] = None,
    vertical_bar: Optional[dict] = None,
    side_band: Optional[dict] = None,
    seal: Optional[dict] = None,
    top_rule: Optional[dict] = None,
    short_rule: Optional[dict] = None,
    bottom_band: Optional[dict] = None,
    deco_frame: Optional[dict] = None,
    column_rules: Optional[dict] = None,
) -> dict:
    return {
        "masthead": masthead,
        "vertical_bar": vertical_bar,
        "side_band": side_band,
        "seal": seal,
        "top_rule": top_rule,
        "short_rule": short_rule,
        "bottom_band": bottom_band,
        "deco_frame": deco_frame,
        "column_rules": column_rules,
    }


STYLE_PRESETS: Dict[str, Dict[str, Any]] = {
    # ------------------------------------------------------------------ 周一
    "economist-crimson": {
        "id": "economist-crimson",
        "name_en": "ECONOMIST",
        "name_zh": "财经权威",
        "weekday": 0,
        "weekday_zh": "周一",
        "vibe": "深红+白衬线+黑色刊头条",
        "char_min": 10,
        "char_max": 20,
        "tone": "dark",
        "serif": True,
        "letter_spacing": 0.0,
        "bg": {
            "kind": "gradient",
            "colors": [(126, 20, 20), (96, 12, 14), (62, 7, 9)],
            "vignette": 0.55,
            "grain": True,
        },
        "ink": (255, 255, 255),
        "ink_soft": (243, 226, 226),
        "accent": (14, 14, 16),
        "title_gradient": [(255, 255, 255), (255, 244, 244), (250, 236, 236)],
        "stroke": (58, 4, 6),
        "glow": (150, 26, 26),
        "overlay_alpha": 0,
        "tags": {"fg": (255, 255, 255), "accent": (255, 255, 255), "dim": (255, 255, 255, 60)},
        "badge": {"colors": [(255, 255, 255), (236, 232, 232), (214, 208, 208)], "outline": (255, 255, 255), "text": (120, 16, 18), "bar": (14, 14, 16)},
        "decor": _decor(
            masthead={
                "bg": (12, 12, 14),
                "fg": (255, 255, 255),
                "accent": (196, 40, 40),
                "default_text": "智驭视界 · AI 实战周刊",
                "italic": False,
            },
        ),
    },
    # ------------------------------------------------------------------ 周二
    "monocle-ivory": {
        "id": "monocle-ivory",
        "name_en": "MONOCLE",
        "name_zh": "文化极简",
        "weekday": 1,
        "weekday_zh": "周二",
        "vibe": "米白+左侧竖排+大字无衬线",
        "char_min": 10,
        "char_max": 20,
        "tone": "light",
        "serif": False,
        "letter_spacing": 0.02,
        "bg": {
            "kind": "solid",
            "colors": [(243, 238, 228), (236, 230, 218)],
            "vignette": 0.10,
            "grain": True,
        },
        "ink": (24, 24, 27),
        "ink_soft": (86, 84, 82),
        "accent": (17, 17, 19),
        "title_gradient": None,
        "stroke": None,
        "glow": (206, 198, 182),
        "overlay_alpha": 0,
        "tags": {"fg": (34, 34, 38), "accent": (17, 17, 19), "dim": (150, 144, 134, 90)},
        "badge": {"colors": [(24, 24, 27), (24, 24, 27), (24, 24, 27)], "outline": (24, 24, 27), "text": (243, 238, 228), "bar": (17, 17, 19)},
        "decor": _decor(
            vertical_bar={"color": (18, 18, 20), "width_px": 30, "label": True},
            top_rule={"color": (18, 18, 20), "width_px": 3},
        ),
    },
    # ------------------------------------------------------------------ 周三
    "newyorker-parchment": {
        "id": "newyorker-parchment",
        "name_en": "NEW YORKER",
        "name_zh": "编辑厚重",
        "weekday": 2,
        "weekday_zh": "周三",
        "vibe": "羊皮纸+斜体刊头+宋体大字",
        "char_min": 12,
        "char_max": 20,
        "tone": "light",
        "serif": True,
        "letter_spacing": 0.0,
        "bg": {
            "kind": "solid",
            "colors": [(239, 230, 212), (231, 220, 200)],
            "vignette": 0.16,
            "grain": True,
        },
        "ink": (28, 26, 24),
        "ink_soft": (92, 84, 74),
        "accent": (170, 56, 44),
        "title_gradient": None,
        "stroke": None,
        "glow": (206, 190, 160),
        "overlay_alpha": 0,
        "tags": {"fg": (38, 34, 30), "accent": (170, 56, 44), "dim": (168, 156, 138, 95)},
        "badge": {"colors": [(170, 56, 44), (150, 46, 36), (126, 36, 28)], "outline": (170, 56, 44), "text": (247, 240, 226), "bar": (28, 26, 24)},
        "decor": _decor(
            masthead={
                "bg": None,
                "fg": (28, 26, 24),
                "accent": (170, 56, 44),
                "default_text": "智驭视界 · 深度手记",
                "italic": True,
            },
        ),
    },
    # ------------------------------------------------------------------ 周四
    "wired-black": {
        "id": "wired-black",
        "name_en": "WIRED",
        "name_zh": "未来张力",
        "weekday": 3,
        "weekday_zh": "周四",
        "vibe": "纯黑+超粗白字+亮红强调",
        "char_min": 8,
        "char_max": 20,
        "tone": "dark",
        "serif": False,
        "letter_spacing": -0.01,
        "bg": {
            "kind": "solid",
            "colors": [(9, 9, 11), (4, 4, 6)],
            "vignette": 0.30,
            "grain": False,
            "grid": True,
            "grid_color": (30, 30, 34),
        },
        "ink": (255, 255, 255),
        "ink_soft": (206, 206, 210),
        "accent": (255, 42, 42),
        "title_gradient": [(255, 255, 255), (255, 255, 255), (232, 232, 236)],
        "stroke": (0, 0, 0),
        "glow": (255, 42, 42),
        "overlay_alpha": 0,
        "tags": {"fg": (255, 255, 255), "accent": (255, 42, 42), "dim": (255, 255, 255, 60)},
        "badge": {"colors": [(255, 42, 42), (222, 26, 30), (176, 16, 20)], "outline": (255, 42, 42), "text": (255, 255, 255), "bar": (9, 9, 11)},
        "decor": _decor(
            top_rule={"color": (255, 42, 42), "width_px": 10},
        ),
    },
    # ------------------------------------------------------------------ 周五
    "kinfolk-whitespace": {
        "id": "kinfolk-whitespace",
        "name_en": "KINFOLK",
        "name_zh": "东方留白",
        "weekday": 4,
        "weekday_zh": "周五",
        "vibe": "素白+细衬线+极大字距",
        "char_min": 10,
        "char_max": 20,
        "tone": "light",
        "serif": True,
        "letter_spacing": 0.20,
        "bg": {
            "kind": "solid",
            "colors": [(250, 249, 245), (244, 242, 236)],
            "vignette": 0.06,
            "grain": True,
        },
        "ink": (48, 47, 44),
        "ink_soft": (130, 126, 118),
        "accent": (150, 144, 132),
        "title_gradient": None,
        "stroke": None,
        "glow": (224, 220, 210),
        "overlay_alpha": 0,
        "tags": {"fg": (74, 72, 66), "accent": (150, 144, 132), "dim": (186, 182, 172, 95)},
        "badge": {"colors": [(250, 249, 245), (240, 238, 232), (232, 229, 222)], "outline": (150, 144, 132), "text": (58, 56, 52), "bar": (150, 144, 132)},
        "decor": _decor(
            short_rule={"color": (150, 144, 132), "width_px": 4},
        ),
    },
    # ------------------------------------------------------------------ 周六
    "harvard-navy": {
        "id": "harvard-navy",
        "name_en": "HARVARD",
        "name_zh": "学术克制",
        "weekday": 5,
        "weekday_zh": "周六",
        "vibe": "深蓝+金色印章+侧带",
        "char_min": 10,
        "char_max": 20,
        "tone": "dark",
        "serif": True,
        "letter_spacing": 0.0,
        "bg": {
            "kind": "gradient",
            "colors": [(18, 40, 72), (12, 28, 54), (7, 16, 32)],
            "vignette": 0.55,
            "grain": True,
        },
        "ink": (255, 255, 255),
        "ink_soft": (206, 220, 240),
        "accent": (201, 162, 39),
        "title_gradient": [(255, 255, 255), (250, 244, 226), (232, 214, 168)],
        "stroke": (8, 16, 32),
        "glow": (201, 162, 39),
        "overlay_alpha": 0,
        "tags": {"fg": (255, 255, 255), "accent": (201, 162, 39), "dim": (255, 255, 255, 60)},
        "badge": {"colors": [(214, 178, 62), (201, 162, 39), (150, 116, 20)], "outline": (232, 206, 128), "text": (16, 28, 50), "bar": (201, 162, 39)},
        "decor": _decor(
            side_band={"color": (201, 162, 39), "width_px": 16},
            seal={"ring": (201, 162, 39), "fill": (10, 22, 42), "fg": (232, 206, 128)},
        ),
    },
    # ------------------------------------------------------------------ 周日
    "tech-purple-gold": {
        "id": "tech-purple-gold",
        "name_en": "TECH",
        "name_zh": "紫黑金科技风",
        "weekday": 6,
        "weekday_zh": "周日",
        "vibe": "深空紫黑+流光金字+霓虹节点",
        "char_min": 6,
        "char_max": 20,
        "tone": "dark",
        "serif": False,
        "letter_spacing": 0.0,
        "bg": {
            "kind": "gradient",
            "colors": [(10, 4, 20), (24, 8, 46), (8, 2, 16)],
            "vignette": 0.6,
            "grain": False,
            "nodes": True,
            "neon": (160, 80, 255),
        },
        "ink": (255, 255, 255),
        "ink_soft": (214, 196, 240),
        "accent": (160, 80, 255),
        "title_gradient": [(255, 247, 224), (234, 196, 116), (148, 104, 196)],
        "stroke": (6, 1, 16),
        "glow": (214, 172, 96),
        "overlay_alpha": 90,
        "tags": {"fg": (245, 245, 255), "accent": (160, 80, 255), "dim": (255, 255, 255, 60)},
        "badge": {"colors": [(71, 34, 100), (204, 153, 255), (60, 30, 80)], "outline": (236, 196, 255), "text": (20, 10, 20), "bar": (160, 80, 255)},
        "decor": _decor(),
        "legacy": False,
    },
    # -------------------------------------------------- 周日科技风轮替成员（与 tech-purple-gold 一同在周日按 ISO 周轮替，全部参与轮换）
    "codex-blue-gold": {
        "id": "codex-blue-gold",
        "name_en": "CODEX",
        "name_zh": "黑蓝金科技风",
        "weekday": 6,
        "weekday_zh": "周日",
        "vibe": "黑底+电光蓝+金色大字",
        "char_min": 6,
        "char_max": 20,
        "tone": "dark",
        "serif": False,
        "letter_spacing": 0.0,
        "bg": {
            "kind": "gradient",
            "colors": [(2, 8, 20), (4, 22, 48), (1, 6, 16)],
            "vignette": 0.6,
            "grain": False,
            "neon": (28, 157, 255),
        },
        "ink": (255, 255, 255),
        "ink_soft": (206, 226, 250),
        "accent": (28, 157, 255),
        "title_gradient": [(255, 248, 190), (255, 202, 45), (177, 97, 0)],
        "stroke": (12, 8, 0),
        "glow": (255, 180, 35),
        "overlay_alpha": 90,
        "tags": {"fg": (245, 245, 255), "accent": (28, 157, 255), "dim": (255, 255, 255, 60)},
        "badge": {"colors": [(255, 232, 148), (255, 193, 36), (147, 91, 0)], "outline": (255, 240, 170), "text": (18, 18, 18), "bar": (28, 157, 255)},
        "decor": _decor(),
        "legacy": False,
    },
    # -------------------------------------------- 周六·候补（ISO 奇数周）
    "agent-cyber": {
        "id": "agent-cyber",
        "name_en": "AGENT",
        "name_zh": "智能体蓝青风",
        "weekday": 5,
        "weekday_zh": "周六",
        "vibe": "黑底+蓝青+金色点缀",
        "char_min": 6,
        "char_max": 20,
        "tone": "dark",
        "serif": False,
        "letter_spacing": 0.0,
        "bg": {
            "kind": "gradient",
            "colors": [(2, 10, 22), (4, 28, 52), (1, 8, 18)],
            "vignette": 0.6,
            "grain": False,
            "neon": (0, 200, 255),
        },
        "ink": (255, 255, 255),
        "ink_soft": (200, 236, 250),
        "accent": (0, 200, 255),
        "title_gradient": [(255, 255, 255), (188, 240, 255), (0, 150, 220)],
        "stroke": (2, 10, 20),
        "glow": (0, 200, 255),
        "overlay_alpha": 90,
        "tags": {"fg": (245, 255, 255), "accent": (0, 200, 255), "dim": (255, 255, 255, 60)},
        "badge": {"colors": [(255, 232, 148), (255, 193, 36), (147, 91, 0)], "outline": (255, 240, 170), "text": (18, 18, 18), "bar": (0, 200, 255)},
        "decor": _decor(),
        "legacy": False,
    },
    # -------------------------------------------- 周五·候补（ISO 奇数周）
    "clean-business-tech": {
        "id": "clean-business-tech",
        "name_en": "CLEAN",
        "name_zh": "极简商务科技风",
        "weekday": 4,
        "weekday_zh": "周五",
        "vibe": "暗色渐变+极简 UI",
        "char_min": 6,
        "char_max": 20,
        "tone": "dark",
        "serif": False,
        "letter_spacing": 0.0,
        "bg": {
            "kind": "gradient",
            "colors": [(6, 12, 26), (14, 26, 50), (4, 10, 22)],
            "vignette": 0.45,
            "grain": False,
            "neon": (120, 150, 255),
        },
        "ink": (255, 255, 255),
        "ink_soft": (210, 220, 240),
        "accent": (120, 150, 255),
        "title_gradient": [(255, 255, 255), (228, 234, 255), (180, 196, 255)],
        "stroke": (8, 14, 28),
        "glow": (120, 150, 255),
        "overlay_alpha": 80,
        "tags": {"fg": (245, 247, 255), "accent": (120, 150, 255), "dim": (255, 255, 255, 60)},
        "badge": {"colors": [(226, 232, 255), (180, 196, 255), (120, 140, 200)], "outline": (226, 232, 255), "text": (18, 22, 38), "bar": (120, 150, 255)},
        "decor": _decor(),
        "legacy": False,
    },
    # ==================================================================
    # 2026-10 扩充的 4 套杂志级风格（每个星期槽位的第二套，ISO 奇数周登场）
    # 共同点：封面文字统一走「思源黑体 Bold」（font: source-han-sans）。
    # ==================================================================
    # --------------------------------------------------- 周一·候补 瑞士网格
    "swiss-grid": {
        "id": "swiss-grid",
        "name_en": "HELVETIC",
        "name_zh": "瑞士网格",
        "weekday": 0,
        "weekday_zh": "周一",
        "vibe": "纸白+淡灰网格+信号红规线",
        "char_min": 10,
        "char_max": 20,
        "tone": "light",
        "serif": False,
        "font": "source-han-sans",
        "letter_spacing": 0.0,
        "bg": {
            "kind": "solid",
            "colors": [(245, 243, 238), (233, 230, 222)],
            "vignette": 0.08,
            "grain": True,
            "grid": True,
            "grid_color": (124, 122, 116),
            "grid_alpha": 30,
            "grid_step": 118,
            "grid_width": 1,
        },
        "ink": (16, 16, 18),
        "ink_soft": (96, 95, 92),
        "accent": (227, 34, 25),
        "title_gradient": None,
        "stroke": None,
        "glow": (198, 196, 188),
        "overlay_alpha": 0,
        "tags": {"fg": (24, 24, 27), "accent": (227, 34, 25), "dim": (140, 138, 132, 95)},
        "badge": {"colors": [(16, 16, 18), (16, 16, 18), (16, 16, 18)], "outline": (16, 16, 18), "text": (245, 243, 238), "bar": (227, 34, 25)},
        "decor": _decor(
            top_rule={"color": (227, 34, 25), "width_px": 12},
            short_rule={"color": (16, 16, 18), "width_px": 6},
        ),
    },
    # ----------------------------------------------- 周二·候补 爱琴海明信片
    "aegean-postcard": {
        "id": "aegean-postcard",
        "name_en": "AEGEAN",
        "name_zh": "爱琴海明信片",
        "weekday": 1,
        "weekday_zh": "周二",
        "vibe": "晒白纸+爱琴海蓝+陶土色带",
        "char_min": 10,
        "char_max": 20,
        "tone": "light",
        "serif": False,
        "font": "source-han-sans",
        "letter_spacing": 0.02,
        "bg": {
            "kind": "solid",
            "colors": [(250, 243, 227), (240, 230, 206)],
            "vignette": 0.10,
            "grain": True,
        },
        "ink": (14, 74, 100),
        "ink_soft": (86, 116, 132),
        "accent": (226, 114, 91),
        "title_gradient": None,
        "stroke": None,
        "glow": (212, 198, 168),
        "overlay_alpha": 0,
        "tags": {"fg": (255, 253, 248), "accent": (255, 240, 230), "dim": (255, 255, 255, 95)},
        "badge": {"colors": [(226, 114, 91), (204, 90, 68), (166, 66, 48)], "outline": (244, 196, 180), "text": (255, 250, 240), "bar": (14, 74, 100)},
        "decor": _decor(
            bottom_band={"color": (226, 114, 91), "top_ratio": 0.855, "edge": (250, 243, 227)},
        ),
    },
    # ------------------------------------------------- 周三·候补 号外
    "newsprint-extra": {
        "id": "newsprint-extra",
        "name_en": "BROADSHEET",
        "name_zh": "号外",
        "weekday": 2,
        "weekday_zh": "周三",
        "vibe": "新闻纸白+墨黑+朱红刊头",
        "char_min": 8,
        "char_max": 20,
        "tone": "light",
        "serif": False,
        "font": "source-han-sans",
        "letter_spacing": -0.01,
        "bg": {
            "kind": "solid",
            "colors": [(247, 245, 240), (237, 234, 227)],
            "vignette": 0.12,
            "grain": True,
        },
        "ink": (10, 10, 10),
        "ink_soft": (74, 74, 76),
        "accent": (200, 16, 46),
        "title_gradient": None,
        "stroke": None,
        "glow": (204, 200, 192),
        "overlay_alpha": 0,
        "tags": {"fg": (26, 26, 28), "accent": (200, 16, 46), "dim": (150, 148, 144, 95)},
        "badge": {"colors": [(200, 16, 46), (172, 12, 38), (132, 8, 28)], "outline": (200, 16, 46), "text": (255, 252, 246), "bar": (10, 10, 10)},
        "decor": _decor(
            top_rule={"color": (10, 10, 10), "width_px": 12},
            masthead={
                "bg": None,
                "fg": (10, 10, 10),
                "accent": (200, 16, 46),
                "default_text": "智驭视界 · 号外",
                "italic": False,
            },
            column_rules={
                "color": (10, 10, 10),
                "alpha": 52,
                "cols": 3,
                "top_ratio": 0.40,
                "bottom_ratio": 0.87,
                "width_px": 2,
            },
        ),
    },
    # --------------------------------------------- 周四·候补 盖茨比之夜
    "deco-noir": {
        "id": "deco-noir",
        "name_en": "DECO",
        "name_zh": "盖茨比之夜",
        "weekday": 3,
        "weekday_zh": "周四",
        "vibe": "午夜孔雀绿+香槟金+金线装饰框",
        "char_min": 10,
        "char_max": 20,
        "tone": "dark",
        "serif": False,
        "font": "source-han-sans",
        "letter_spacing": 0.10,
        "bg": {
            "kind": "gradient",
            "colors": [(16, 62, 48), (10, 42, 33), (5, 26, 20)],
            "vignette": 0.55,
            "grain": True,
        },
        "ink": (245, 239, 224),
        "ink_soft": (206, 196, 170),
        "accent": (201, 162, 39),
        "title_gradient": [(250, 245, 230), (214, 180, 92), (150, 112, 22)],
        "stroke": (6, 26, 20),
        "glow": (201, 162, 39),
        "overlay_alpha": 0,
        "tags": {"fg": (245, 239, 224), "accent": (201, 162, 39), "dim": (245, 239, 224, 70)},
        "badge": {"colors": [(226, 196, 108), (201, 162, 39), (148, 114, 20)], "outline": (238, 214, 150), "text": (10, 34, 26), "bar": (201, 162, 39)},
        "decor": _decor(
            masthead={
                "bg": (201, 162, 39),
                "fg": (10, 34, 26),
                "accent": (10, 34, 26),
                "default_text": "智驭视界 · 午夜特刊",
                "italic": False,
            },
            deco_frame={
                "color": (201, 162, 39),
                "width": 3,
                "inset_x": 0.028,
                "inset_top": 0.125,
                "inset_bottom": 0.955,
                "fan": True,
                "fan_r": 44,
            },
        ),
    },
}

# Accepted aliases -> canonical preset id.
ALIASES: Dict[str, str] = {
    "auto": "auto",
    "weekly": "auto",
    "rotate": "auto",
    "轮换": "auto",
    "economist": "economist-crimson",
    "财经权威": "economist-crimson",
    "monocle": "monocle-ivory",
    "文化极简": "monocle-ivory",
    "new-yorker": "newyorker-parchment",
    "newyorker": "newyorker-parchment",
    "编辑厚重": "newyorker-parchment",
    "wired": "wired-black",
    "未来张力": "wired-black",
    "kinfolk": "kinfolk-whitespace",
    "东方留白": "kinfolk-whitespace",
    "harvard": "harvard-navy",
    "学术克制": "harvard-navy",
    # 2026-10 扩充的 4 套（思源黑体 Bold 封面文字）
    "swiss": "swiss-grid",
    "helvetic": "swiss-grid",
    "瑞士网格": "swiss-grid",
    "瑞士风": "swiss-grid",
    "aegean": "aegean-postcard",
    "爱琴海": "aegean-postcard",
    "明信片": "aegean-postcard",
    "爱琴海明信片": "aegean-postcard",
    "deco": "deco-noir",
    "盖茨比": "deco-noir",
    "盖茨比之夜": "deco-noir",
    "装饰艺术": "deco-noir",
    "extra": "newsprint-extra",
    "broadsheet": "newsprint-extra",
    "号外": "newsprint-extra",
    "新闻纸": "newsprint-extra",
    # legacy purple/gold names map onto the existing tech style
    "紫黑金科技风": "tech-purple-gold",
    "obsidian-purple-gold": "tech-purple-gold",
    "purple-gold": "tech-purple-gold",
    # 其余三套科技风（现已分别成为周日 / 周六 / 周五的候补）
    "codex": "codex-blue-gold",
    "黑蓝金科技风": "codex-blue-gold",
    "agent": "agent-cyber",
    "智能体蓝青风": "agent-cyber",
    "clean": "clean-business-tech",
    "极简商务科技风": "clean-business-tech",
}

# ImageGen background prompts per style (background only, no final text).
STYLE_PROMPTS: Dict[str, str] = {
    "economist-crimson": (
        "Create a wide 2.35:1 WeChat article cover background in an authoritative financial weekly style. "
        "Deep crimson red field with a subtle darker vignette and light paper grain, restrained and serious. "
        "A solid black masthead band across the very top. Faint thin white column rules hinting at newspaper columns. "
        "Keep the composition text-friendly: a clean deep-red field across the left 62% for large white serif Chinese headline typography, with the right side similarly calm as open negative space. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. High contrast, premium, print-like, publish-ready."
    ),
    "monocle-ivory": (
        "Create a wide 2.35:1 WeChat article cover background in a refined cultural-magazine style. "
        "Warm ivory off-white (#F3EEE4) paper field with the faintest grain, airy and calm, editorial minimalism. "
        "A slim solid black vertical bar hugging the far left edge, and a single thin black hairline rule. "
        "Keep the composition text-friendly: clean ivory space across the canvas for large bold sans-serif Chinese headline typography, with generous open negative space on the right. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Clean, premium, print-magazine feel, publish-ready."
    ),
    "newyorker-parchment": (
        "Create a wide 2.35:1 WeChat article cover background in a classic editorial magazine style. "
        "Warm parchment (#EFE6D4) paper field with visible fine grain and a gentle vignette, literary and weighty. "
        "A delicate thin horizontal rule near the top. Minimal, dignified, no busy graphics. "
        "Keep the composition text-friendly: clean parchment space across the canvas for large serif Chinese headline typography, with calm open negative space on the right. "
        "No readable text, no fake Chinese characters, no ornaments, no logos, no people, no portrait, no watermark. Refined, print-magazine, publish-ready."
    ),
    "wired-black": (
        "Create a wide 2.35:1 WeChat article cover background in a bold futuristic tech-magazine style. "
        "Pure near-black (#09090B) field with a very subtle technical grid and faint scanline texture, high-tension and clean. "
        "A single bright red (#FF2A2A) accent bar near the top. Sharp, graphic, high-contrast, no clutter. "
        "Keep the composition text-friendly: clean black space across the canvas for ultra-bold white Chinese headline typography, with dark open negative space on the right. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Bold, cinematic, publish-ready."
    ),
    "kinfolk-whitespace": (
        "Create a wide 2.35:1 WeChat article cover background in a serene oriental-whitespace style. "
        "Soft off-white (#FAF8F3) field, extremely minimal, generous empty space, the faintest warm paper grain, quiet and calm. "
        "Almost no decoration: at most one short thin warm-gray hairline. Zen, restrained, breathing room. "
        "Keep the composition text-friendly: clean white space across the canvas for widely letter-spaced thin serif Chinese headline typography, with generous empty negative space on the right. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Calm, premium, publish-ready."
    ),
    "harvard-navy": (
        "Create a wide 2.35:1 WeChat article cover background in a restrained academic style. "
        "Deep navy blue (#122848) gradient, darker at the edges, subtle grain, scholarly and composed. "
        "A slim gold (#C9A227) vertical band along the left edge and a small plain gold circular seal motif in the upper-left. "
        "Keep the composition text-friendly: clean navy space across the canvas for large serif Chinese headline typography, with calm open negative space on the right. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Dignified, premium, publish-ready."
    ),
    "tech-purple-gold": (
        "Create a wide 2.35:1 WeChat article cover background, cinematic high-end Chinese tech/business thumbnail style. "
        "Dark black/navy base, electric purple and violet neon glow, deep perspective, subtle speed lines, digital UI cards, charts, automation workflow icons, knowledge graph nodes. "
        "Keep the left 62% clean and dark for large Chinese headline typography; let abstract tech graphics fill the CENTER square as a visual anchor. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. High contrast, premium commercial poster, sharp, polished, publish-ready."
    ),
    "codex-blue-gold": (
        "Create a wide 2.35:1 WeChat article cover background, premium Chinese tech/business thumbnail style. "
        "Dark black and navy cyber studio, electric blue light trails, golden sparks, code panels, automation workflow nodes, growth dashboards, glowing AI server core in the CENTER. "
        "Keep the left 62% clean and dark for large Chinese headline typography; let abstract tech graphics fill the CENTER square as a visual anchor. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. High contrast, cinematic, sharp, polished, publish-ready."
    ),
    "agent-cyber": (
        "Create a wide 2.35:1 WeChat article cover background, high-end AI business automation style. "
        "Dark navy operations room, glowing agent network, business dashboards, automated workflow pipeline, data cards, arrows, growth charts, blue/cyan neon, subtle gold accents. "
        "Leave the left 64% clean and dark for bold Chinese headline typography; let abstract tech graphics fill the CENTER square as a visual anchor. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Sharp, commercial, cinematic, publish-ready."
    ),
    "clean-business-tech": (
        "Create a wide 2.35:1 clean premium technology banner background. "
        "Dark gradient, subtle blue/purple glow, minimalist UI panels, knowledge graph lines, elegant depth, few decorative elements, the LEFT ~29% kept clean for headline typography, with the hero scene centered and the right wing calm. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. High-end consulting brand style."
    ),
    # -------------------------------------------- 2026-10 扩充 4 套的背景提示词
    "swiss-grid": (
        "Create a wide 2.35:1 WeChat article cover background in an International Typographic Style (Swiss design) mood. "
        "Warm-neutral paper white (#F5F3EE) field with an extremely faint light-gray modular grid of thin hairlines and the subtlest paper grain, crisp and rational. "
        "A single signal-red (#E32219) hairline rule near the top edge and one short black hairline; nothing else, maximal discipline. "
        "Keep the composition text-friendly: clean paper-white space across the canvas for large bold sans-serif Chinese headline typography, with generous open negative space on the right. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Bauhaus-adjacent, museum-print quality, publish-ready."
    ),
    "aegean-postcard": (
        "Create a wide 2.35:1 WeChat article cover background in a sun-bleached Aegean postcard style. "
        "Warm off-white / sun-washed cream (#FAF3E3) paper field with fine grain, Aegean blue (#1B7FA8) and terracotta (#E2725B) appearing only as very soft abstract washes or a horizon hint, holiday-bright but restrained. "
        "Keep the composition text-friendly: clean pale space across the upper and middle canvas for large bold sans-serif Chinese headline typography, and leave the lower ~15% of the frame flat and quiet so a solid terracotta band can sit there. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. Editorial travel-magazine feel, premium, publish-ready."
    ),
    "newsprint-extra": (
        "Create a wide 2.35:1 WeChat article cover background in a vintage broadsheet newspaper 'extra' edition style. "
        "Newsprint off-white (#F7F5F0) paper with visible fibrous grain and a gentle vignette, strictly black ink and one vermilion red (#C8102E) accent, absolutely no other colors. "
        "Faint vertical column hairlines in light gray, an ink-heavy top area, gritty and urgent, printed-on-cheap-paper texture. "
        "Keep the composition text-friendly: clean paper space across the canvas for large bold sans-serif Chinese headline typography, with calm open negative space on the right. "
        "No readable text, no fake Chinese characters, no headlines, no logos, no people, no portrait, no watermark. Authentic print-press look, publish-ready."
    ),
    "deco-noir": (
        "Create a wide 2.35:1 WeChat article cover background in an Art Deco / Great Gatsby midnight-luxe style. "
        "Deep midnight peacock green (#0E3B2E) field with a darker vignette, champagne gold (#C9A227) appearing as thin symmetric deco linework, subtle sunburst rays and stepped chevron motifs near the corners, luxurious and symmetrical. "
        "Keep the composition text-friendly: a calm dark field across the canvas for large bold gold-tinted Chinese headline typography, with quiet open negative space on the right. "
        "No readable text, no fake Chinese characters, no logos, no people, no portrait, no watermark. 1920s glamour, high-contrast, premium print feel, publish-ready."
    ),
}


def normalize_style_id(style: Optional[str]) -> str:
    """Normalize an accepted style name/alias to a canonical preset id.

    Returns ``"auto"`` for auto/rotation requests and the default id when the
    input is empty or unknown.
    """
    if style is None:
        return "auto"
    key = str(style).strip()
    if not key:
        return "auto"
    if key in ALIASES:
        return ALIASES[key]
    if key in STYLE_PRESETS:
        return key
    return DEFAULT_STYLE


def style_for_weekday(weekday: int, when: Optional[_dt.date] = None) -> str:
    """Return the rotating style id for a ``date.weekday()`` value (0=Mon).

    Each weekday owns two looks. The ISO week number decides which one shows:
    even ISO weeks use ``WEEKDAY_ORDER`` (base) and odd ISO weeks use
    ``WEEKDAY_ALTERNATE``, so consecutive weeks never repeat the same cover on
    the same weekday and all 14 presets stay in the rotation. When ``when`` is
    ``None`` the base style of that weekday is returned.
    """
    idx = weekday % 7
    if when is None:
        return WEEKDAY_ORDER[idx]
    if when.isocalendar()[1] % 2 == 1:  # ISO odd week -> alternate look
        return WEEKDAY_ALTERNATE.get(idx, WEEKDAY_ORDER[idx])
    return WEEKDAY_ORDER[idx]


def resolve_style(style: Optional[str], when: Optional[_dt.date] = None) -> str:
    """Resolve a requested style to a concrete preset id.

    ``style`` may be an explicit id, an alias, or ``auto``/empty (rotate by the
    weekday of ``when`` — today by default).
    """
    normalized = normalize_style_id(style)
    if normalized == "auto":
        day = when or _dt.date.today()
        return style_for_weekday(day.weekday(), when)
    return normalized


def get_preset(style: Optional[str], when: Optional[_dt.date] = None) -> Dict[str, Any]:
    """Return the full preset dict for a requested style, resolving auto."""
    return STYLE_PRESETS[resolve_style(style, when)]


def rotation_table() -> List[Dict[str, Any]]:
    """Return the weekday rotation table as plain dicts.

    One row per (weekday, slot): 7 weekdays x 2 looks = 14 rows, i.e. every
    preset in the skill appears exactly once.
    """
    rows = []
    for idx in range(7):
        for slot, sid in (("base", WEEKDAY_ORDER[idx]), ("alt", WEEKDAY_ALTERNATE[idx])):
            p = STYLE_PRESETS[sid]
            rows.append(
                {
                    "weekday_zh": WEEKDAY_ZH[idx],
                    "weekday": idx,
                    "slot": slot,
                    "iso_week": "ISO 偶数周" if slot == "base" else "ISO 奇数周",
                    "style": sid,
                    "name_en": p["name_en"],
                    "name_zh": p["name_zh"],
                    "vibe": p["vibe"],
                    "char_range": f"{p['char_min']}-{p['char_max']}字",
                }
            )
    return rows


def describe_style(sid: str) -> str:
    p = STYLE_PRESETS[sid]
    return f"{p['name_en']} {p['name_zh']}（{p['vibe']}，建议 {p['char_min']}-{p['char_max']} 字）"


def _main() -> None:
    parser = argparse.ArgumentParser(description="Show the weekday cover-style rotation and resolve a style.")
    parser.add_argument("--style", default=None, help="Style id/alias, or 'auto' to rotate by date")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD used when style is auto (default: today)")
    parser.add_argument("--table", action="store_true", help="Print the full 14-style rotation table")
    args = parser.parse_args()

    if args.table or (not args.style and not args.date):
        print("公众号封面风格 · 14 套按星期轮换表（每个星期 2 套，按 ISO 周奇偶交替）")
        print("-" * 92)
        for row in rotation_table():
            print(
                f"{row['weekday_zh']} {row['iso_week']}  {row['style']:<22} "
                f"{row['name_en']:<10} {row['name_zh']:<8} "
                f"{row['vibe']:<24} {row['char_range']}"
            )
        print("-" * 92)

    when = None
    if args.date:
        when = _dt.date.fromisoformat(args.date)
    if args.style is not None or args.date:
        sid = resolve_style(args.style, when)
        day = when or _dt.date.today()
        print(f"\n{day.isoformat()}（{WEEKDAY_ZH[day.weekday()]}）→ {sid}")
        print(describe_style(sid))


if __name__ == "__main__":
    _main()
