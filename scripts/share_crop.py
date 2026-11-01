#!/usr/bin/env python3
"""Compute the WeChat cover crop coordinates (and export the 1:1 share slice).

Why this exists
---------------
A WeChat article carries ONE cover image (``thumb_media_id``) plus two crop
windows chosen by the platform: the 2.35:1 feed crop and the 1:1 crop used for
**share cards / forwarded messages / the account's history list**.

If you never send a crop window, WeChat falls back to the **centre** of the
cover. On a "left headline + right hero" cover that slices the headline in half
— the classic "分享缩略图里标题只剩半截" bug.

The two API fields are normalised coordinates over the ORIGINAL cover image,
(0,0) top-left to (1,1) bottom-right, joined as ``X1_Y1_X2_Y2`` with up to 6
decimals:

* ``pic_crop_235_1`` — the 2.35:1 feed crop  → ``0_0_1_1`` (whole image)
* ``pic_crop_1_1``   — the 1:1 share crop    → e.g. ``0.574468_0_1_1`` (right)

Send them on ``draft/add`` or ``draft/update`` (``articles[0]``); there is no
separate "set share image" call.

Usage
-----
    python scripts/share_crop.py --image wechat_cover.png
    python scripts/share_crop.py --image wechat_cover.png --side center --json
    python scripts/share_crop.py --image wechat_cover.png --export share-1x1.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Width share of the 1:1 square on a 2.35:1 canvas: 1000/2350 = 0.4255.
# Kept in sync with check_cover.SAFE_ZONE_FRACTION (asserted in the smoke test).
SAFE_ZONE_FRACTION = 0.426


def share_slice_box(w: int, h: int, side: str = "right") -> tuple[int, int, int, int]:
    """1:1 share square as pixel (x0, y0, x1, y1) for the requested side."""
    s = str(side).lower()
    edge = min(h, int(w * SAFE_ZONE_FRACTION))
    if s == "right":
        x0 = w - edge
    elif s == "left":
        x0 = 0
    else:  # center
        x0 = (w - edge) // 2
    return x0, 0, x0 + edge, edge


def _num(v: float) -> str:
    """Format with 6 decimals, then trim trailing zeros (WeChat accepts both)."""
    return f"{v:.6f}".rstrip("0").rstrip(".") or "0"


def crop_string(w: int, h: int, side: str = "right") -> dict[str, str]:
    """Return the two crop strings WeChat expects for this cover size/side."""
    x0, y0, x1, y1 = share_slice_box(w, h, side)
    return {
        "pic_crop_1_1": "_".join(_num(v) for v in (x0 / w, y0 / h, x1 / w, y1 / h)),
        "pic_crop_235_1": "0_0_1_1",
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Compute WeChat pic_crop_1_1 / pic_crop_235_1 for a cover, "
                    "optionally exporting the 1:1 share slice."
    )
    ap.add_argument("--image", help="Cover image (PNG/JPG) — reads its real size")
    ap.add_argument("--width", type=int, default=2350, help="Canvas width if no --image (default 2350)")
    ap.add_argument("--height", type=int, default=1000, help="Canvas height if no --image (default 1000)")
    ap.add_argument("--side", choices=["right", "center", "left"], default="right",
                    help="Where the 1:1 square sits. right = the skill's delivery standard "
                         "for the left-headline + right-hero layout (default).")
    ap.add_argument("--export", metavar="PATH", help="Also write the 1:1 slice to PATH")
    ap.add_argument("--json", action="store_true", help="Emit JSON only (for scripting)")
    if len(sys.argv) == 1:
        ap.print_help()
        print("\n提示：需要封面路径或宽高，如 "
              "python scripts/share_crop.py --image wechat_cover.png。", file=sys.stderr)
        sys.exit(0)
    args = ap.parse_args()

    w, h = args.width, args.height
    src = None
    if args.image:
        try:
            from PIL import Image
        except ImportError:
            sys.exit("需要 Pillow：pip install pillow")
        p = Path(args.image)
        if not p.exists():
            sys.exit(f"找不到图片: {p}")
        with Image.open(p) as im:
            w, h = im.size
            src = im.convert("RGB").copy()

    x0, y0, x1, y1 = share_slice_box(w, h, args.side)
    crops = crop_string(w, h, args.side)
    pct = (x1 - x0) / w * 100

    if args.export:
        if src is None:
            sys.exit("--export 需要同时给 --image")
        out = Path(args.export)
        src.crop((x0, y0, x1, y1)).save(out)
        if not args.json:
            print(f"已导出 1:1 切片: {out}  ({(x1 - x0)}x{(y1 - y0)}px)")

    if args.json:
        print(json.dumps({"size": [w, h], "side": args.side,
                          "box": [x0, y0, x1, y1], **crops}, ensure_ascii=False, indent=2))
        return

    side_zh = {"right": "右侧", "center": "正中央", "left": "左侧"}.get(args.side, args.side)
    print(f"封面尺寸 {w}x{h}｜1:1 方形取{side_zh} x {x0}-{x1}（{x1 - x0}px，占宽 {pct:.1f}%）")
    print(f"pic_crop_1_1   = {crops['pic_crop_1_1']}")
    print(f"pic_crop_235_1 = {crops['pic_crop_235_1']}")
    print()
    print("用法：建草稿 / 改草稿时把这两个值放进 articles[0]——")
    print("  draft/add 或 draft/update 的 body：")
    print(f'  {{"articles":[{{ ..., "thumb_media_id":"<封面素材>", '
          f'"pic_crop_1_1":"{crops["pic_crop_1_1"]}", "pic_crop_235_1":"0_0_1_1" }}]}}')
    print("不传 pic_crop_1_1 时微信会从封面正中央裁 1:1 → 分享卡片会把标题切半。")


if __name__ == "__main__":
    main()
