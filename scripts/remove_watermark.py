#!/usr/bin/env python3
"""Remove the ImageGen corner watermark ("AI生成 / WORKBUDD" style) from a cover background.

ImageGen sometimes bakes a faint semi-transparent caption into a corner of the
generated background. It must be gone before delivery (the QA checklist rejects
watermarks), but redrawing the corner by hand every time is wasteful.

This module detects the mark automatically and repaints ONLY the mark's compact
block, so the hero scene — which can also have bright objects near a corner — is
protected.

What the mark looks like (empirically)
-------------------------------------
The caption is *faint* light text (often only ~200 on the 0-255 scale, so a
fixed "near-white" threshold misses it) sitting flush in a CORNER, hugging BOTH
edges of that corner, on a *flat, textureless* dark patch — NOT on the detailed
hero scene. The hero scene itself often has bright objects (panels, spheres,
highlights) near a corner too, so we must tell the caption from those.

Discriminators that work together:
  1. CORNER BAND: only pixels within a small fraction (CORNER_BAND) of BOTH
     edges that meet at a corner are considered. The caption is always jammed
     into the extreme corner; this already excludes most of the scene.
  2. CANDIDATE: brighter than a heavy-Gaussian local background (low threshold,
     so the faint caption is caught).
  3. FLATNESS (large window): keep only components whose *surroundings* are flat
     (low std over a fixed ~46px window). The caption rests on a smooth dark
     patch; a solid scene object sits on textured surroundings and is rejected.
  4. TEXT SHAPE: after grouping surviving components by proximity, require the
     group to be made of SEVERAL small strokes (>= MIN_COMPONENTS) and NOT
     dominated by one big blob (largest component <= MAX_DOMINANT of the total).
     Text = many similar small glyphs; a solid object = one dominant blob.
     Plus a low bounding-box coverage (strokes on dark) and a text-sized block.

Repainting
----------
Because the caption sits on a flat patch, we simply repaint its entire padded
bounding box with the mean tone sampled from a ring just OUTSIDE the box, plus
grain matched to that ring's standard deviation. This erases every caption pixel
in one shot (no reliance on per-pixel masks that can leave bright edges), and the
flat tone + grain blends seamlessly into the surrounding dark patch.

CLI
---
    python scripts/remove_watermark.py background.png [--out cleaned.png] [--dry-run]

Importable
----------
    from remove_watermark import remove_watermark
    cleaned = remove_watermark(img)   # img: PIL.Image -> new PIL.Image
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:  # pragma: no cover
    Image = ImageFilter = None


# The watermark always lands flush in a CORNER, hugging BOTH edges of that
# corner (empirically it sits within a few percent of the right/bottom edges).
# We restrict detection to a band this fraction of the canvas in from BOTH edges
# of each corner. 12% reaches the truly extreme corner (where the mark is
# pinned) while excluding scene elements inset ~8% from the edge.
CORNER_BAND = 0.12
# Local-background estimate: a heavy Gaussian blur so thin caption strokes
# average away and the result is "scene without the text".
BLUR_RADIUS = 15
# A pixel is candidate-caption if it is brighter than the local background by
# more than this. Deliberately LOW so the *faint* watermark (often only ~200,
# not near-white) is caught, while broad mid-tone scene areas are ignored.
CONTRAST_T = 16
# Flatness is measured over a fixed window of this many pixels, centred on each
# candidate component (clamped to the image). A bigger window than the
# component's own box separates caption (uniform dark neighbours) from a scene
# object (textured neighbours).
FLAT_WIN = 46
# A component is kept only if its surroundings (the FLAT_WIN window) are FLAT
# (std below this). The caption's flat dark patch is well below; scene objects
# exceed it.
FLAT_T = 38
# Components whose bboxes are within this gap (px) are merged into one caption
# block (text glyphs sit close together).
LINK = 16
# A merged block is treated as caption only if bright pixels cover at most this
# fraction of its bounding box (strokes on dark = low coverage; solid blob = high).
COVER_T = 0.55
# A caption block must be made of at least this many stroke components (text has
# many glyphs; an isolated speck / small sliver has one).
MIN_COMPONENTS = 2
# ... and no single component may dominate the block beyond this fraction of its
# total bright area (a solid scene object is one dominant blob).
MAX_DOMINANT = 0.6
# Pad added around each block when building the repaint box.
PAD = 8
# Drop connected components smaller than this (caption strokes cluster larger;
# single bright specks are ignored).
MIN_AREA = 4
# A caption block must be smaller than these fractions of the canvas (text-sized,
# not a scene-sized region) to be accepted.
MAX_BLOCK_W = 0.16
MAX_BLOCK_H = 0.14


def _in_corner(cx: float, cy: float, W: int, H: int) -> bool:
    """True only if (cx, cy) sits inside the flush-corner band of some corner:
    within CORNER_BAND of BOTH edges that meet at that corner."""
    b = CORNER_BAND
    in_left = cx < W * b
    in_right = cx > W * (1 - b)
    in_top = cy < H * b
    in_bottom = cy > H * (1 - b)
    return (in_left and in_top) or (in_right and in_top) or \
           (in_left and in_bottom) or (in_right and in_bottom)


def _local_std(gray, cx, cy, win):
    """Std-dev of grayscale inside a win x win window centred on (cx, cy)."""
    W, H = gray.size
    x0 = max(0, int(cx - win / 2)); y0 = max(0, int(cy - win / 2))
    x1 = min(W - 1, int(cx + win / 2)); y1 = min(H - 1, int(cy + win / 2))
    if x1 <= x0 or y1 <= y0:
        return 255.0
    px = gray.load()
    total = 0
    cnt = 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            total += px[x, y]
            cnt += 1
    if cnt == 0:
        return 255.0
    mean = total / cnt
    var = 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = px[x, y] - mean
            var += d * d
    return (var / cnt) ** 0.5


def _mark_clusters(fg, W, H, min_area: int):
    """Return (x0,y0,x1,y1, comp) for each connected foreground cluster >= min_area."""
    visited = [[False] * W for _ in range(H)]
    clusters = []
    for sy in range(H):
        for sx in range(W):
            if not fg[sy][sx] or visited[sy][sx]:
                continue
            stack = [(sx, sy)]
            comp = []
            visited[sy][sx] = True
            while stack:
                x, y = stack.pop()
                comp.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and not visited[ny][nx] and fg[ny][nx]:
                        visited[ny][nx] = True
                        stack.append((nx, ny))
            if len(comp) >= min_area:
                xs = [p[0] for p in comp]
                ys = [p[1] for p in comp]
                clusters.append((min(xs), min(ys), max(xs), max(ys), comp))
    return clusters


def _flat_repaint(W, H, opx, bx0, by0, bx1, by1):
    """Repaint the whole box with the mean tone of the ring just outside it,
    plus grain matched to that ring's std. Seamless on a flat patch."""
    ring = []
    R = 5
    for x in range(max(0, bx0 - R), min(W, bx1 + R)):
        for y in (by0 - 1, by0 - 2, by0 - 3, by0 - 4, by0 - 5,
                  by1, by1 + 1, by1 + 2, by1 + 3, by1 + 4):
            if 0 <= y < H:
                ring.append(opx[x, y])
    for y in range(max(0, by0 - R), min(H, by1 + R)):
        for x in (bx0 - 1, bx0 - 2, bx0 - 3, bx0 - 4, bx0 - 5,
                  bx1, bx1 + 1, bx1 + 2, bx1 + 3, bx1 + 4):
            if 0 <= x < W:
                ring.append(opx[x, y])
    if not ring:
        return
    n = len(ring)
    mean = [sum(p[i] for p in ring) / n for i in range(3)]
    lum = [sum(p) / 3.0 for p in ring]
    ml = sum(lum) / n
    std = (sum((v - ml) ** 2 for v in lum) / n) ** 0.5
    amp = min(std * 0.6, 6.0)
    # Deterministic grain so the same background always yields the same cover.
    rng = random.Random((bx0 * 73856093) ^ (by0 * 19349663) ^ (bx1 * 83492791))
    for y in range(by0, by1):
        for x in range(bx0, bx1):
            g = rng.gauss(0, amp) if amp > 0 else 0.0
            opx[x, y] = tuple(max(0, min(255, int(mean[i] + g))) for i in range(3))


def remove_watermark(img: "Image.Image") -> "Image.Image":
    """Return a copy of ``img`` with the corner watermark repainted away.

    Safe to call on any background: if no watermark is detected, the image is
    returned unchanged.
    """
    if Image is None:
        raise RuntimeError("Pillow is required: pip install Pillow")
    src = img.convert("RGB")
    W, H = src.size
    gray = src.convert("L")
    gpx = gray.load()

    # Local background estimate (heavy blur) and candidate caption mask.
    bg = gray.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    bgpx = bg.load()
    fg = [[False] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if gpx[x, y] - bgpx[x, y] > CONTRAST_T:
                fg[y][x] = True

    # Candidate caption components: in the corner band AND on a flat patch.
    cands = []  # (x0,y0,x1,y1,comp)
    for (x0, y0, x1, y1, comp) in _mark_clusters(fg, W, H, MIN_AREA):
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        if not _in_corner(cx, cy, W, H):
            continue
        if _local_std(gray, cx, cy, FLAT_WIN) > FLAT_T:
            continue
        cands.append((x0, y0, x1, y1, comp))

    if not cands:
        return src

    # Cluster candidates by proximity (glyphs of one caption sit close together).
    parent = list(range(len(cands)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            a, b = cands[i], cands[j]
            # cand tuple is (x0, y0, x1, y1, comp). The gap between two boxes is
            # the greater left-edge minus the lesser right-edge (0 if they
            # overlap) — NOT the union span.
            gap_x = max(0, max(a[0], b[0]) - min(a[2], b[2]))
            gap_y = max(0, max(a[1], b[1]) - min(a[3], b[3]))
            if gap_x <= LINK and gap_y <= LINK:
                parent[find(i)] = find(j)

    groups = {}
    for i, c in enumerate(cands):
        groups.setdefault(find(i), []).append(c)

    boxes = []
    for gi, members in groups.items():
        if len(members) < MIN_COMPONENTS:
            continue  # an isolated speck / sliver, not a caption
        bx0 = min(c[0] for c in members)
        by0 = min(c[1] for c in members)
        bx1 = max(c[2] for c in members)
        by1 = max(c[3] for c in members)
        area = sum(len(c[4]) for c in members)
        cover = area / max(1, (bx1 - bx0 + 1) * (by1 - by0 + 1))
        block_w = (bx1 - bx0) / W
        block_h = (by1 - by0) / H
        max_comp = max(len(c[4]) for c in members)
        if cover > COVER_T or block_w > MAX_BLOCK_W or block_h > MAX_BLOCK_H:
            continue  # solid scene object, not caption
        if max_comp / max(1, area) > MAX_DOMINANT:
            continue  # dominated by one big blob -> a scene object
        boxes.append((max(0, bx0 - PAD), max(0, by0 - PAD),
                      min(W, bx1 + PAD), min(H, by1 + PAD)))

    if not boxes:
        return src

    out = src.copy()
    opx = out.load()
    for (bx0, by0, bx1, by1) in boxes:
        _flat_repaint(W, H, opx, bx0, by0, bx1, by1)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Remove the ImageGen corner watermark from a cover background.")
    ap.add_argument("image", help="Background PNG/JPG to clean")
    ap.add_argument("--out", default=None, help="Output path (default: overwrite the input)")
    ap.add_argument("--dry-run", action="store_true", help="Detect and report only, do not modify")
    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(0)
    args = ap.parse_args()

    if Image is None:
        print("❌ 缺 Pillow：pip install Pillow", file=sys.stderr)
        sys.exit(2)
    img = Image.open(args.image).convert("RGB")
    cleaned = remove_watermark(img)
    dst = Path(args.out) if args.out else Path(args.image)
    if args.dry_run:
        print(f"[dry-run] would write: {dst}")
        return
    cleaned.save(dst)
    print(f"saved cleaned background -> {dst}")


if __name__ == "__main__":
    main()
