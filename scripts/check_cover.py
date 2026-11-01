#!/usr/bin/env python3
"""Delivery gate for a finished WeChat cover: geometry + Moments share safe zone.

Checks the canvas ratio (2.35:1 ± 0.01) and export size, then — with
``--safe-zone`` — computes and prints the 1:1 square that survives when the
cover is shared to 朋友圈/聊天, and exports two preview images:

* ``<prefix>-safezone.png``   original with the cropped wings darkened and the
                              kept square marked by a red frame
* ``<prefix>-share-1x1.png``  the 1:1 crop exactly as exported

**The skill's delivery standard is the RIGHT 42.6% slice** (x 1350-2350 on a
2350px canvas): that 1:1 crop is the official share preview and the acceptance
criterion for the default "left headline + right hero" layout. ``--share-side``
therefore defaults to ``right``. ``center`` (the middle ~42.6%, x 675-1675) and
``left`` remain available as alternative crops on request. The banner's overall
look and the exported 1:1 slice are checked **together** — a scene that is
cropped, clipped or covered inside the slice fails the gate, regardless of how
good the full banner looks.

The printed range and the ``--export-share`` crop use the same bounds, so they
never disagree by a single pixel.

Usage (the pre-delivery gate documented in SKILL.md Step 4/5):

    python scripts/check_cover.py wechat_cover.png --safe-zone \
      --export-safe wechat_cover-preview --export-share wechat_cover-preview

Exit code: 0 = all hard checks pass, 1 = a hard check failed, 2 = I/O error.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # 延迟到真正校验时才报错：保证 --help/无子命令探测退出码为 0
    Image = ImageDraw = ImageFont = None

TARGET_RATIO = 2.35
RATIO_TOL = 0.01
PREFERRED_SIZE = (2350, 1000)          # preferred export, per SKILL.md
SAFE_ZONE_FRACTION = 0.426             # central square kept on 朋友圈 share
WING_DARKEN_ALPHA = 140                # 0-255, how hard the cropped wings are dimmed
FRAME_RED = (206, 32, 32)

# Optional label font (purely cosmetic; skipped when unavailable).
_FONT_CANDIDATES = (
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/NotoSansSC-VF.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)


def _label_font(px: int) -> ImageFont.FreeTypeFont | None:
    for p in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, px)
        except (OSError, IOError):
            continue
    return None


def safe_zone_bounds(w: int, h: int, share_side: str = "center") -> tuple[int, int, int, int]:
    """1:1 share square as (x0, y0, x1, y1) for the requested side.

    ``share_side``:
      * ``center`` — the middle 42.6%: x 675-1675 on a 2350x1000 canvas.
      * ``right``  — the right 42.6%: x 1350-2350 (skill default AND the
        official delivery/acceptance crop for the right-scene layout).
      * ``left``   — the left 42.6%: x 0-1000.

    The square's side is the smaller of the canvas height and 42.6% of its
    width; on a true 2.35:1 canvas that equals the full height (1000px on
    2350x1000). The same bounds drive the printed range and the --export-share
    crop so they never disagree.
    """
    s = str(share_side).lower()
    side = min(h, int(w * SAFE_ZONE_FRACTION))
    if s == "right":
        x0 = w - side
    elif s == "left":
        x0 = 0
    else:  # center
        x0 = (w - side) // 2
    return x0, 0, x0 + side, side


def check_geometry(path: Path, target_ratio: float, tolerance: float,
                   min_w: int, min_h: int) -> tuple[bool, list[str], Image.Image]:
    """Open the image and run the hard geometry checks. Returns (ok, lines, img)."""
    lines: list[str] = []
    img = Image.open(path)
    img.load()
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    w, h = img.size
    ok = True

    lines.append(f"文件: {path}")
    lines.append(f"尺寸: {w}x{h}")

    if w == 0 or h == 0:
        lines.append("[FAIL] 图片尺寸非法")
        return False, lines, img

    ratio = w / h
    ratio_ok = abs(ratio - target_ratio) <= tolerance
    if not ratio_ok:
        ok = False
    tag = "PASS" if ratio_ok else "FAIL"
    lines.append(f"[{tag}] 画布比例 {ratio:.4f}（目标 {target_ratio} ± {tolerance}）")
    if not ratio_ok:
        lines.append("       → 比例超差：分享裁剪与版式假设均按 2.35:1 计算，必须返工")

    if (w, h) == PREFERRED_SIZE:
        lines.append(f"[PASS] 导出尺寸为推荐值 {w}x{h}")
    else:
        note = "（如无特殊目的建议按推荐值导出）" if ratio_ok else ""
        lines.append(
            f"[INFO] 导出尺寸非推荐值 {PREFERRED_SIZE[0]}x{PREFERRED_SIZE[1]}{note}"
        )

    if min_w > 0 or min_h > 0:
        if w >= min_w and h >= min_h:
            lines.append(f"[PASS] 尺寸达到最小门槛 {min_w}x{min_h}")
        else:
            ok = False
            lines.append(f"[FAIL] 尺寸低于最小门槛 {min_w}x{min_h}：{w}x{h}")

    return ok, lines, img


def export_safezone(img: Image.Image, prefix: Path, share_side: str = "center") -> Path:
    """Original + darkened wings + red safe-zone frame (+ small label)."""
    w, h = img.size
    x0, y0, x1, y1 = safe_zone_bounds(w, h, share_side)
    base = img.convert("RGBA")

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, 0, x0, h], fill=(0, 0, 0, WING_DARKEN_ALPHA))
    od.rectangle([x1, 0, w, h], fill=(0, 0, 0, WING_DARKEN_ALPHA))
    out = Image.alpha_composite(base, overlay)

    d = ImageDraw.Draw(out)
    fw = max(3, w // 220)
    d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=FRAME_RED, width=fw)

    font = _label_font(max(16, h // 38))
    if font is not None:
        text = f"朋友圈安全区 {SAFE_ZONE_FRACTION * 100:.1f}%  x {x0}-{x1}"
        tb = d.textbbox((0, 0), text, font=font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        pad = max(8, h // 60)
        bx0, by0 = x0 + fw + pad, fw + pad
        d.rounded_rectangle(
            [bx0, by0, bx0 + tw + 2 * pad, by0 + th + 2 * pad],
            radius=(th + 2 * pad) // 2,
            fill=(12, 12, 14, 190),
        )
        d.text((bx0 + pad, by0 + pad), text, font=font, fill=(255, 255, 255))

    out_path = prefix.parent / f"{prefix.name}-safezone.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.convert("RGB").save(out_path)
    return out_path


def export_share(img: Image.Image, prefix: Path, share_side: str = "center") -> Path:
    """The 1:1 square crop for the requested side (center = real 朋友圈 view)."""
    w, h = img.size
    x0, y0, x1, y1 = safe_zone_bounds(w, h, share_side)
    crop = img.convert("RGB").crop((x0, y0, x1, y1))
    out_path = prefix.parent / f"{prefix.name}-share-1x1.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    crop.save(out_path)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check a finished WeChat cover: ratio/size + 朋友圈 share safe zone"
    )
    parser.add_argument("image", help="Cover PNG/JPG to check")
    parser.add_argument(
        "--safe-zone",
        action="store_true",
        help="Print the central share-safe range and enable zone exports",
    )
    parser.add_argument(
        "--export-safe",
        metavar="PREFIX",
        help="Export <PREFIX>-safezone.png (wings darkened + red frame)",
    )
    parser.add_argument(
        "--export-share",
        metavar="PREFIX",
        help="Export <PREFIX>-share-1x1.png (1:1 分享切片，默认右 42.6%% ＝ 验收用的分享预览)",
    )
    parser.add_argument(
        "--share-side",
        choices=["center", "right", "left"],
        default="right",
        help="Which 1:1 crop to preview. right=skill default AND delivery "
             "standard (right 42.6 percent slice x 1350-2350, matches the "
             "right-scene layout); center=the middle 42.6 percent (x 675-1675); "
             "left=mirror. The banner and the exported slice are checked together.",
    )
    parser.add_argument("--target-ratio", type=float, default=TARGET_RATIO)
    parser.add_argument("--tolerance", type=float, default=RATIO_TOL)
    parser.add_argument(
        "--min-width",
        type=int,
        default=0,
        help="Hard minimum width; 0 = no check (default)",
    )
    parser.add_argument(
        "--min-height",
        type=int,
        default=0,
        help="Hard minimum height; 0 = no check (default)",
    )
    if len(sys.argv) == 1:  # 无子命令：打印用法并 exit 0（沙箱探测要求）
        parser.print_help()
        print("\n提示：需要待检查的封面文件路径，如 "
              "python scripts/check_cover.py wechat_cover.png --safe-zone。", file=sys.stderr)
        sys.exit(0)
    args = parser.parse_args()

    if Image is None:
        print("❌ 缺 Pillow —— 封面校验的硬依赖。\n   修复：pip install Pillow", file=sys.stderr)
        sys.exit(2)

    if args.tolerance < 0:
        print("FAIL: --tolerance 不能为负", file=sys.stderr)
        sys.exit(2)
    if args.min_width < 0 or args.min_height < 0:
        print("FAIL: --min-width/--min-height 不能为负", file=sys.stderr)
        sys.exit(2)

    path = Path(args.image)
    if not path.is_file():
        print(f"错误: 文件不存在 {path}", file=sys.stderr)
        sys.exit(2)

    print("check_cover.py — 封面交付前检查")
    try:
        ok, lines, img = check_geometry(
            path, args.target_ratio, args.tolerance, args.min_width, args.min_height
        )
    except Exception as exc:  # noqa: BLE001 - surface any decode error cleanly
        print(f"错误: 无法读取图片 {path}: {exc}", file=sys.stderr)
        sys.exit(2)
    for ln in lines:
        print(" ", ln)

    w, h = img.size
    side = args.share_side
    x0, y0, x1, y1 = safe_zone_bounds(w, h, side)
    if args.safe_zone or args.export_safe or args.export_share:
        pct = (x1 - x0) / w * 100
        side_zh = {"center": "正中央", "right": "右侧", "left": "左侧"}.get(side, side)
        if side == "center":
            wing_note = "中央 42.6% 方形（x 675-1675，按需导出，非默认交付）"
        elif side == "right":
            wing_note = "技能默认且为正式交付版式（右 42.6% 切片，配右侧场景版式），此图即验收用的分享预览"
        else:
            wing_note = "左侧镜像切片（按需导出，非默认交付）"
        print(
            f"[INFO] 1:1 裁剪区（{side_zh}）x {x0}-{x1}"
            f"（{x1 - x0}x{y1 - y0}px，占画布宽度 {pct:.1f}%；{wing_note}）"
        )
        print("       打印范围与 --export-share 裁剪逐像素一致")
        # The 1:1 share card in WeChat is NOT "auto-centred" — it is the window
        # given by pic_crop_1_1 on the cover material. Omit it and WeChat falls
        # back to the centre of the cover, which slices a right-hero headline in
        # half. Print the matching values so they can be pasted into draft/add /
        # draft/update without hand-computing.
        try:
            import share_crop as _sc
            crops = _sc.crop_string(w, h, side)
            print(f"       → 建/改草稿必须带：pic_crop_1_1 = {crops['pic_crop_1_1']}"
                  f"（pic_crop_235_1 = {crops['pic_crop_235_1']}）")
            print("         详情: python scripts/share_crop.py --image <封面> "
                  f"--side {side}")
        except Exception:  # share_crop missing / older env — never block the gate
            pass

    exported: list[str] = []
    if args.export_safe:
        p = export_safezone(img, Path(args.export_safe), side)
        exported.append(f"{p}（裁切区外压暗 + 红框，检查构图）")
    if args.export_share:
        p = export_share(img, Path(args.export_share), side)
        exported.append(f"{p}（1:1 {side} 裁剪预览）")
    for e in exported:
        print(f"  已导出: {e}")

    if args.export_share:
        if side == "right":
            print("  人工确认(验收项): 打开 -share-1x1.png，确认右侧主题场景完整落在切片内、"
                  "未被右缘裁切、未被标题/装饰压住，且独立成图观感 OK；不过即返工。")
        else:
            print(f"  人工确认: 当前为「{side}」切片，请确认该 1:1 裁剪作为分享图观感 OK。")

    if ok:
        print("结果: 硬性检查全部通过（安全区可读性需人工确认）")
        sys.exit(0)
    print("结果: 存在 FAIL 项，必须返工", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
