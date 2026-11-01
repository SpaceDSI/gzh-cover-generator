#!/usr/bin/env python3
"""Build a structured WeChat cover brief JSON for the gzh-cover-generator skill.

The brief drives three downstream steps: imagegen background export, Pillow
rendering, and the QA check. ``--style auto`` (the default) rotates the cover
style by weekday, matching the weekday rotation defined in
``style_presets.py``.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import style_presets as sp  # noqa: E402
import cover_motifs as cm  # noqa: E402

WEEKDAY_NAMES = {
    "0": 0, "mon": 0, "monday": 0, "周一": 0, "星期一": 0,
    "1": 1, "tue": 1, "tuesday": 1, "周二": 1, "星期二": 1,
    "2": 2, "wed": 2, "wednesday": 2, "周三": 2, "星期三": 2,
    "3": 3, "thu": 3, "thursday": 3, "周四": 3, "星期四": 3,
    "4": 4, "fri": 4, "friday": 4, "周五": 4, "星期五": 4,
    "5": 5, "sat": 5, "saturday": 5, "周六": 5, "星期六": 5,
    "6": 6, "sun": 6, "sunday": 6, "周日": 6, "星期日": 6, "周天": 6, "星期天": 6,
}


def parse_weekday(value: str) -> int:
    key = str(value).strip().lower()
    if key in WEEKDAY_NAMES:
        return WEEKDAY_NAMES[key]
    raise argparse.ArgumentTypeError(f"无法识别的星期：{value}（可用 0-6 或 周一…周日）")


def count_title_chars(hero_lines) -> int:
    """Count meaningful title characters (CJK + latin letters/digits), ignoring spaces and punctuation."""
    total = 0
    for line in hero_lines:
        for ch in str(line):
            if ch.isspace():
                continue
            if ch.isalnum() or ("\u4e00" <= ch <= "\u9fff"):
                total += 1
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Create cover_brief.json for a 2.35:1 WeChat cover.")
    parser.add_argument("--style", default="auto",
                        help="Style id/alias, or 'auto' to rotate by weekday (default: auto)")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD used when style is auto (default: today)")
    parser.add_argument("--weekday", type=parse_weekday, default=None,
                        help="Force a weekday 0-6 / 周一…周日 when style is auto")
    parser.add_argument("--title", default="", help="Original article title or topic (required unless --list-styles)")
    parser.add_argument("--topic", default="", help="文章主旨/内容一句话概述，用于驱动右侧构图语义匹配")
    parser.add_argument("--eyebrow", default="", help="Small top line")
    parser.add_argument("--hero", action="append", default=[], help="Hero line; pass multiple times for multiple lines")
    parser.add_argument("--subtitle", default="", help="Subtitle / badge text")
    parser.add_argument("--tag", action="append", default=[], help="Bottom tag; pass multiple times")
    parser.add_argument("--motif", default="off",
                        help="右侧轻量图形：auto（按文案推断）/ off / " + " / ".join(cm.MOTIF_IDS))
    parser.add_argument("--masthead", default="", help="Masthead / brand mark text (defaults to the preset's own)")
    parser.add_argument("--background", default="./background.png", help="Path to generated background")
    parser.add_argument("--output-image", default="./wechat_cover.png", help="Final cover output path")
    parser.add_argument("--output", default="cover_brief.json", help="Brief JSON output path")
    parser.add_argument("--seed", type=int, default=202601, help="Deterministic fallback background seed")
    parser.add_argument("--list-styles", action="store_true", help="Print the 14-style rotation table and exit")
    if len(sys.argv) == 1:  # 无子命令：打印用法并 exit 0（沙箱探测要求）
        parser.print_help()
        print("\n提示：--title 是必需的（除非用 --list-styles 只查看轮换表）。", file=sys.stderr)
        sys.exit(0)
    args = parser.parse_args()

    if args.list_styles:
        for row in sp.rotation_table():
            print(f"{row['weekday_zh']} {row['iso_week']}  {row['name_en']:<11} {row['name_zh']:<8} "
                  f"{row['vibe']:<24} {row['char_range']}  ({row['style']})")
        return

    if not args.title:
        parser.error("--title 是必需的（除非使用 --list-styles 只查看轮换表）")

    when = _dt.date.fromisoformat(args.date) if args.date else None
    if args.weekday is not None:
        # --date 给定时仍按 ISO 周奇偶取该星期槽位的对应一套；不给日期则取基准套。
        sid = sp.style_for_weekday(args.weekday, when)
    else:
        sid = sp.resolve_style(args.style, when)
    preset = sp.STYLE_PRESETS[sid]

    hero_lines = args.hero if args.hero else [args.title[:18]]

    motif_requested = str(args.motif or "off").strip().lower()
    if motif_requested not in ("auto", "") and not cm.is_disabled(motif_requested) \
            and motif_requested not in cm.MOTIF_IDS:
        parser.error(f"无法识别的 motif：{args.motif}（可用 auto / off / {' / '.join(cm.MOTIF_IDS)}）")

    char_count = count_title_chars(hero_lines)
    char_min, char_max = preset["char_min"], preset["char_max"]

    masthead_decor = preset["decor"].get("masthead") or {}
    masthead_text = args.masthead or masthead_decor.get("default_text") or sp.BRAND_MARK

    brief = {
        "canvas": {"width": 2350, "height": 1000},
        # Default layout (5.5.1): left headline (~52% of width) + hero scene on the
        # RIGHT, auto-centred inside the right 42.6% 1:1 slice (x 1350-2350).
        # Banner look is primary. Switch to "center" for WeChat's real centre crop.
        "share_side": "right",
        "auto_center_scene": True,
        "style": sid,
        "style_requested": args.style,
        "date": (when or _dt.date.today()).isoformat() if (args.style == "auto" or args.weekday is not None) else None,
        "style_name": f"{preset['name_en']} {preset['name_zh']}",
        "char_count": char_count,
        "char_range": f"{char_min}-{char_max}",
        "title_original": args.title,
        "topic": args.topic,
        "eyebrow": args.eyebrow or "AI实战方法论",
        "hero_lines": hero_lines[:3],
        "subtitle": args.subtitle or "重度使用经验实战复盘",
        "bottom_tags": args.tag[:4],
        "masthead_text": masthead_text,
        "right_motif": motif_requested or "off",
        "background_path": args.background,
        "output_path": args.output_image,
        "seed": args.seed,
    }

    out = Path(args.output)
    out.write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")

    day_label = ""
    if args.weekday is not None:
        day_label = f"（{sp.WEEKDAY_ZH[args.weekday]}）"
    elif args.style == "auto":
        day_label = f"（{(when or _dt.date.today()).isoformat()} {sp.WEEKDAY_ZH[(when or _dt.date.today()).weekday()]}）"

    print(f"Wrote {out}")
    print(f"风格{day_label}: {sid} — {preset['name_en']} {preset['name_zh']}（{preset['vibe']}）")
    resolved = cm.plan_composition(
        {"eyebrow": args.eyebrow, "hero_lines": hero_lines, "subtitle": args.subtitle,
         "bottom_tags": args.tag[:4], "title_original": args.title, "topic": args.topic,
         "right_motif": motif_requested or "off", "seed": args.seed},
        preset,
    )
    print(f"右侧图形: {cm.describe_plan(resolved)}")
    print(f"主标题字数: {char_count}（建议 {char_min}-{char_max}）", end="")
    if char_count < char_min:
        print("  ⚠️ 偏少，封面会显空，建议补足卖点")
    elif char_count > char_max:
        print("  ⚠️ 偏多，字号会被压缩，建议精简或拆行")
    else:
        print("  ✓")


if __name__ == "__main__":
    main()
