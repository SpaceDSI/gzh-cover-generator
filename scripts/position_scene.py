#!/usr/bin/env python3
"""Center the hero scene inside the share zone (default: the RIGHT 42.6%).

Why this exists
---------------
ImageGen reliably draws a nice still-life but tends to centre it, not land it in
the exact 1:1 slice WeChat shares. This module measures the subject's horizontal
span by *local gradient energy* (texture/edges — independent of the background
colour, so it works on beige, dark, navy, paper, etc.) and shifts the artwork
horizontally so the span's centre lands on the target zone's centre, filling the
vacated strip seamlessly from the opposite edge column.

Zone centres (fraction of width, for a 2.35:1 canvas):
  * right  -> 0.787  (centre of the right 42.6% slice, x 1350-2350)
  * center -> 0.500
  * left   -> 0.213

Usage (standalone):
    python scripts/position_scene.py background.png --share-side right --out background_centred.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

# Fraction of the frame width that each share zone is centred on.
TARGET_CENTER = {"right": 0.787, "center": 0.500, "left": 0.213}
# Where to look for the subject (skip left decorations + the extreme right edge
# where vignette / edge-shadow can masquerade as content).
SEARCH_WINDOW = {"right": (0.35, 0.95), "center": (0.28, 0.95), "left": (0.05, 0.65)}
# Vertical band to sample: skip the top margin and the bottom (table front edge /
# "AI生成" watermark) so only the real subject contributes edge energy.
BAND = (0.10, 0.80)
ENERGY_FRACTION = 0.25      # a column is "subject" above 25% of the peak edge energy
DETECT_WIDTH = 700          # downscale width for detection (speed)

# Scale-to-fill guard (5.7.3): if the detected subject is clearly narrower than
# the share zone, scale the whole image up about the subject centre so the scene
# occupies ~FILL_RATIO of the zone width. This keeps the right 42.6% delivery
# slice well filled even when ImageGen under-draws the hero (only triggers when
# the scene is smaller than MIN_FILL * zone, and is capped at MAX_UPSCALE to
# avoid heavy resampling blur). The headline lives on the opposite ~52% which is
# meant to stay clean, so scaling never pushes content into the type area.
FILL_RATIO = 0.85
MIN_FILL = 0.72
MAX_UPSCALE = 1.5


def detect_span(img: "Image.Image", share_side: str = "right"):
    """Return (x0, x1) subject span in full-res pixels, or None if not found."""
    W, H = img.size
    sw = DETECT_WIDTH
    sh = max(1, int(H * sw / W))
    small = img.convert("L").resize((sw, sh), Image.BILINEAR)
    px = small.load()
    win = SEARCH_WINDOW.get(share_side, SEARCH_WINDOW["right"])
    x_lo, x_hi = int(win[0] * sw), min(int(win[1] * sw), sw - 1)
    y0, y1 = int(BAND[0] * sh), min(int(BAND[1] * sh), sh - 1)

    col_e = {}
    for x in range(x_lo, x_hi):
        e = 0
        for y in range(y0, y1):
            a = px[x, y]
            e += abs(px[x + 1, y] - a) + abs(px[x, y + 1] - a)
        col_e[x] = e
    if not col_e:
        return None
    mx = max(col_e.values()) or 1
    active = [x for x, e in col_e.items() if e > ENERGY_FRACTION * mx]
    if not active:
        return None

    gap = max(3, sw // 40)
    runs = []
    s = p = active[0]
    for x in active[1:]:
        if x - p <= gap:
            p = x
        else:
            runs.append((s, p))
            s = p = x
    runs.append((s, p))
    sx0, sx1 = max(runs, key=lambda r: (r[1] - r[0]))
    scale = W / sw
    return int(round(sx0 * scale)), int(round(sx1 * scale))


def shift_h(img: "Image.Image", dx: int) -> "Image.Image":
    """Shift horizontally by dx, filling the vacated strip from the opposite edge column."""
    if dx == 0:
        return img
    W, H = img.size
    out = img.copy()
    if dx > 0:
        strip = img.crop((0, 0, 1, H)).resize((dx, H), Image.LANCZOS)
        out.paste(strip, (0, 0))
        out.paste(img.crop((0, 0, W - dx, H)), (dx, 0))
    else:
        dx = -dx
        strip = img.crop((W - 1, 0, W, H)).resize((dx, H), Image.LANCZOS)
        out.paste(strip, (W - dx, 0))
        out.paste(img.crop((dx, 0, W, H)), (0, 0))
    return out


def center_scene(img: "Image.Image", share_side: str = "right", min_shift_ratio: float = 0.012):
    """Return img shifted (and, if needed, scaled) so its subject fills+centres the share zone.

    Two steps:
      1. Scale-to-fill guard (5.7.3): when the subject is clearly narrower than the
         share zone, scale the whole image up about the subject centre so the scene
         occupies ~FILL_RATIO of the zone width (capped at MAX_UPSCALE). This fixes
         the "right-scene became smaller" regression where ImageGen drew the hero in
         only the right third instead of the full right ~42.6% square.
      2. Horizontal translation so the (scaled) subject centre lands on the zone
         centre, with the vacated strip filled seamlessly from the edge column.
    Returns the image unchanged if no subject is detected or it is already close.
    """
    W, H = img.size
    span = detect_span(img, share_side)
    if not span:
        return img
    x0, x1 = span
    subject_center = (x0 + x1) / 2

    # --- scale-to-fill guard ---
    zone_w = min(H, int(W * 0.426))
    span_w = x1 - x0
    if span_w > 0 and span_w < MIN_FILL * zone_w:
        desired = FILL_RATIO * zone_w
        scale = min(max(desired / span_w, 1.0), MAX_UPSCALE)
        if scale > 1.02:
            nW = int(round(W * scale))
            nH = int(round(H * scale))
            img = img.resize((nW, nH), Image.LANCZOS)
            x0 = int(round(x0 * scale))
            x1 = int(round(x1 * scale))
            subject_center = (x0 + x1) / 2
            W, H = nW, nH

    target = TARGET_CENTER.get(share_side, 0.787) * W
    dx = int(round(target - subject_center))
    # keep the subject fully inside the frame after shifting
    dx = max(dx, -(x0 - 2))
    dx = min(dx, (W - 2) - x1)
    if abs(dx) < W * min_shift_ratio:
        return img
    return shift_h(img, dx)


def _main() -> None:
    ap = argparse.ArgumentParser(description="Center the hero scene inside the share zone.")
    ap.add_argument("image")
    ap.add_argument("--share-side", choices=["center", "right", "left"], default="right")
    ap.add_argument("--out", default=None)
    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(0)
    args = ap.parse_args()
    if Image is None:
        print("❌ 缺 Pillow：pip install Pillow", file=sys.stderr)
        sys.exit(2)
    img = Image.open(args.image).convert("RGB")
    W = img.size[0]
    span = detect_span(img, args.share_side)
    print(f"subject span: {span}  (target centre x≈{TARGET_CENTER.get(args.share_side,0.787)*W:.0f})")
    out = center_scene(img, args.share_side)
    dst = Path(args.out) if args.out else Path(args.image).with_name(
        Path(args.image).stem + "_centred.png")
    out.save(dst)
    print(f"saved {dst}")


if __name__ == "__main__":
    _main()
