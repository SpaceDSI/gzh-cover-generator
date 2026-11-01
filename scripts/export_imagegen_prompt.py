#!/usr/bin/env python3
"""Export a stable imagegen background prompt from cover_brief.json.

The prompt is looked up from the shared weekday roster in ``style_presets.py``,
so the background always matches the resolved cover style.
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
import scene_concepts as sc  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Export imagegen background prompt from cover brief.")
    parser.add_argument("brief", help="Path to cover_brief.json")
    parser.add_argument("--style", default=None, help="Override style id/alias, or 'auto'")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD used when style is auto")
    if len(sys.argv) == 1:  # 无子命令：打印用法并 exit 0（沙箱探测要求）
        parser.print_help()
        print("\n提示：需要 cover_brief.json 路径参数，如 "
              "python scripts/export_imagegen_prompt.py cover_brief.json。", file=sys.stderr)
        sys.exit(0)
    args = parser.parse_args()

    brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
    when = _dt.date.fromisoformat(args.date) if args.date else None
    if when is None and brief.get("date"):
        try:
            when = _dt.date.fromisoformat(str(brief["date"]))
        except ValueError:
            when = None

    requested = args.style or brief.get("style", "auto")
    sid = sp.resolve_style(requested, when)
    preset = sp.STYLE_PRESETS[sid]
    base = sp.STYLE_PROMPTS.get(sid, sp.STYLE_PROMPTS[sp.DEFAULT_STYLE])

    title = brief.get("title_original", "")
    tags = ", ".join(brief.get("bottom_tags", []))
    tone = preset.get("tone", "dark")
    share_side = str(brief.get("share_side", "right")).lower()
    if share_side == "right":
        # The base style prompt is written for the center-scene layout (scene in
        # the middle, negative space on the right). For the right-scene layout the
        # clean side flips to the LEFT, so rewrite that hint.
        base = (base
                .replace("open negative space on the right", "open negative space on the left")
                .replace("empty negative space on the right", "empty negative space on the left")
                .replace("negative space on the right", "negative space on the left")
                .replace("fill the CENTER square as a visual anchor", "fill the right ~42.6% square as a visual anchor")
                .replace("in the CENTER", "on the RIGHT"))

    print(base)
    print()
    print(f"Style: {preset['name_en']} {preset['name_zh']} ({sid}) — {tone} tone")

    # Thematic scene: a concrete story-driven visual derived from the title +
    # topic (see references/scene-archetypes.md) — not abstract noise.
    # Which square it fills depends on share_side:
    #   * "right"  (DEFAULT + DELIVERY STANDARD): fills the RIGHT 42.6% slice
    #     (x 1350-2350 on a 2350px canvas) to match the default left-headline +
    #     right-hero layout. That slice is the accepted share preview, so the
    #     scene must sit fully inside it with margin — not spill past the edge.
    #   * "center": fills the CENTER square (x 675-1675) — opt-in only.
    scene_side_word = "on the RIGHT" if share_side == "right" else "in the CENTER"
    plan = sc.resolve_scene(brief)
    if plan.get("disabled"):
        print(f"Scene ({scene_side_word}): (disabled — keep the style's own background motif).")
    else:
        label = "RIGHT-SIDE SCENE" if share_side == "right" else "CENTER SCENE"
        print(f"{label} (theme-driven) [{plan['id']} / {plan['name']}] (place {scene_side_word}):")
        prompt_text = sc.scene_prompt(brief, tone)
        if share_side == "right":
            prompt_text = prompt_text.replace("in the CENTER", "on the RIGHT")
        print(prompt_text)

    print(f"Theme context (drives the scene, do NOT render as text): {title}")
    if tags:
        print(f"Concept keywords: {tags}")
    if share_side == "right":
        print("Composition: keep the LEFT ~52% clean and uncluttered for headline typography; "
              "fill the RIGHT ~42.6% region of the frame (a 1:1 square, x roughly 0.574W to W) "
              "as the visual anchor — this exact region IS the share crop and the delivery "
              "criterion, so make the hero scene occupy about 80-90% of that square's width, "
              "keep it fully inside the slice, and leave only a little margin at the far right edge.")
    else:
        print("Composition: keep the LEFT ~29% clean and uncluttered for headline typography; "
              "place the hero scene in the CENTER square (the part 朋友圈 keeps), and leave the "
              "right wing as calm negative space.")
    print("Hard rules: no readable text, no letters, no Chinese characters, no logos, "
          "no people, no face, no portrait, no watermark; abstract placeholder lines only.")
    print("Important: do not render the final title text; it will be added later with code.")


if __name__ == "__main__":
    main()
