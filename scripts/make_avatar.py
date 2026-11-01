#!/usr/bin/env python3
"""Generate the gzh-cover-generator skill avatar (assets/avatar.png).

Deterministic typography over a flat vector composition — the same philosophy
as the cover renderer: no AI-generated text, no portrait.

Design: an app-icon squircle in the ECONOMIST 财经权威 crimson gradient
(the skill's signature Monday style), carrying a miniature 2.35:1 ivory cover
card with a black masthead strip, a Song-style serif "封面" headline, a thin
crimson rule and a "2.35:1" pill. Below the card, seven dots encode the
weekday rotation (Mon–Sat ivory, Sunday purple for the dark-tech sub-rotation).

Usage:
    python scripts/make_avatar.py --out assets/avatar.png      # 生成技能头像(512)
    python scripts/make_avatar.py --size 256 --out icon.png    # 其他尺寸/路径
    python scripts/make_avatar.py                              # 无参数: 打印用法并退出(0)

依赖: numpy + Pillow(仅真正生成时需要; --help/无参数探测不加载)。
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:  # 延迟到真正生成时才报错：保证 --help/无子命令探测退出码为 0
    np = None
    Image = ImageDraw = ImageFilter = ImageFont = None

SKILL_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = SKILL_ROOT / "assets" / "avatar.png"

# ------------------------------------------------------------------ palette
# ECONOMIST 财经权威 (economist-crimson) — the skill's signature look.
BG_GRADIENT = [(126, 20, 20), (96, 12, 14), (62, 7, 9)]
BG_VIGNETTE = 0.55
GOLD = (201, 162, 39)            # HARVARD 学术克制 seal gold
IVORY_CARD = (246, 241, 230)     # cover paper
INK = (20, 20, 22)               # cover ink
MASTHEAD_BG = (12, 12, 14)       # ECONOMIST masthead band
RULE_RED = (166, 40, 40)
DOT_IVORY = (240, 233, 218)
DOT_SUNDAY = (160, 80, 255)      # tech-purple-gold accent

# ------------------------------------------------------------------- fonts
FONT_SERIF = "C:/Windows/Fonts/STZHONGS.TTF"   # 华文中宋
FONT_SANS_BOLD = "C:/Windows/Fonts/msyhbd.ttc"


def _gradient_bg(size: int, seed: int) -> Image.Image:
    """Vertical 3-stop crimson gradient + vignette + fine grain, as RGB."""
    h = w = size
    ys = np.linspace(0.0, 1.0, h)[:, None]
    stops = np.array(BG_GRADIENT, dtype=np.float64)
    # piecewise-linear interpolation over the 3 stops
    pos = np.array([0.0, 0.55, 1.0])
    img = np.zeros((h, w, 3), dtype=np.float64)
    for c in range(3):
        img[:, :, c] = np.interp(ys, pos, stops[:, c])
    # radial vignette (darken toward the edges)
    yy, xx = np.mgrid[0:h, 0:w]
    dx = (xx - w / 2) / (w / 2)
    dy = (yy - h / 2) / (h / 2)
    t = np.clip(np.sqrt(dx * dx + dy * dy) / np.sqrt(2), 0, 1) ** 1.6
    img *= (1.0 - BG_VIGNETTE * t)[:, :, None]
    # deterministic fine grain
    rng = np.random.default_rng(seed)
    grain = rng.normal(0.0, 5.0, size=(h, w, 1))
    img = np.clip(img + grain, 0, 255)
    return Image.fromarray(img.astype(np.uint8), "RGB")


def _squircle_mask(size: int, radius: int) -> Image.Image:
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def _draw_tracked(draw: ImageDraw.ImageDraw, cx: float, cy: float, text: str,
                  font: ImageFont.FreeTypeFont, fill, tracking: float) -> None:
    """Center `text` at (cx, cy) with manual letter-spacing."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, cy), ch, font=font, fill=fill, anchor="lm")
        x += w + tracking


def build_avatar(out_size: int = 512, seed: int = 20260101) -> Image.Image:
    S = out_size * 4  # supersample factor 4 -> crisp downscale
    img = _gradient_bg(S, seed)

    # ---- squircle clip -------------------------------------------------
    radius = int(S * 0.225)
    mask = _squircle_mask(S, radius)
    img.putalpha(mask)

    # ---- gold hairline frame -------------------------------------------
    inset = int(S * 0.046)
    frame = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([inset, inset, S - 1 - inset, S - 1 - inset],
                         radius=radius - inset, outline=GOLD + (216,),
                         width=max(2, S // 290))
    img = Image.alpha_composite(img.convert("RGBA"), frame)

    # ---- geometry -------------------------------------------------------
    card_w = int(S * 0.76)
    card_h = int(round(card_w / 2.35))
    card_r = int(S * 0.012)
    dots_h = int(S * 0.0176)
    gap = int(S * 0.029)
    group_h = card_h + gap + dots_h
    top = (S - group_h) // 2
    card_x0 = (S - card_w) // 2
    card_y0 = top
    card_x1 = card_x0 + card_w
    card_y1 = card_y0 + card_h

    # ---- card shadow ----------------------------------------------------
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([card_x0, card_y0 + int(S * 0.009), card_x1,
                          card_y1 + int(S * 0.009)], radius=card_r,
                         fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(S * 0.02))
    img = Image.alpha_composite(img, shadow)

    # ---- the 2.35:1 cover card ------------------------------------------
    card = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=card_r,
                         fill=IVORY_CARD + (255,))
    img = Image.alpha_composite(img, card)
    d = ImageDraw.Draw(img)

    # masthead band (top corners keep the card radius)
    strip_h = int(card_h * 0.115)
    d.rounded_rectangle([card_x0, card_y0, card_x1, card_y0 + strip_h + card_r],
                        radius=card_r, fill=MASTHEAD_BG + (255,))
    d.rectangle([card_x0, card_y0 + strip_h, card_x1, card_y0 + strip_h + card_r],
                fill=MASTHEAD_BG + (255,))

    f_mast = ImageFont.truetype(FONT_SANS_BOLD, int(S * 0.0165))
    _draw_tracked(d, S / 2, card_y0 + strip_h / 2, "GZH COVER WEEKLY",
                  f_mast, (255, 255, 255), tracking=S * 0.006)

    # serif headline
    f_head = ImageFont.truetype(FONT_SERIF, int(card_h * 0.575))
    d.text((S / 2, card_y0 + strip_h + (card_h - strip_h) * 0.46), "封面",
           font=f_head, fill=INK, anchor="mm")

    # crimson rule
    rule_w = int(card_w * 0.24)
    rule_h = max(3, int(S * 0.0049))
    rule_y = card_y0 + strip_h + (card_h - strip_h) * 0.755
    d.rounded_rectangle([S / 2 - rule_w / 2, rule_y, S / 2 + rule_w / 2,
                         rule_y + rule_h], radius=rule_h // 2, fill=RULE_RED)

    # "2.35:1" pill
    f_pill = ImageFont.truetype(FONT_SANS_BOLD, int(S * 0.019))
    tb = d.textbbox((0, 0), "2.35:1", font=f_pill)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    pad_x, pad_y = int(S * 0.016), int(S * 0.0075)
    pw, ph = tw + 2 * pad_x, th + 2 * pad_y
    pill_cy = card_y1 - int(card_h * 0.072)
    d.rounded_rectangle([S / 2 - pw / 2, pill_cy - ph / 2, S / 2 + pw / 2,
                         pill_cy + ph / 2], radius=ph // 2, fill=RULE_RED)
    d.text((S / 2, pill_cy), "2.35:1", font=f_pill, fill=(255, 255, 255),
           anchor="mm")

    # ---- weekday rotation dots ------------------------------------------
    n = 7
    cy = card_y1 + gap + dots_h / 2
    step = dots_h + int(S * 0.015)
    total = step * (n - 1) + dots_h
    x = S / 2 - total / 2 + dots_h / 2
    for i in range(n):
        r = dots_h / 2
        if i == 6:  # Sunday: the 4-style tech sub-rotation
            r = dots_h * 0.62
            color = DOT_SUNDAY
        else:
            color = DOT_IVORY
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=color)
        x += step

    # ---- downscale ------------------------------------------------------
    out = img.convert("RGBA").resize((out_size, out_size), Image.LANCZOS)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--size", type=int, default=512)
    ap.add_argument("--out", default=str(OUT_PATH))
    if len(sys.argv) == 1:  # 无子命令：只打印用法并 exit 0（不写包内文件，沙箱探测无副作用）
        ap.print_help()
        print("\n提示：本脚本生成技能头像（开发用），需显式传参执行，如 --out assets/avatar.png。",
              file=sys.stderr)
        sys.exit(0)
    args = ap.parse_args()
    if np is None or Image is None:
        print("❌ 缺依赖 —— make_avatar.py 需要 numpy + Pillow。\n   修复：pip install numpy Pillow",
              file=sys.stderr)
        sys.exit(2)
    av = build_avatar(args.size)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    av.save(args.out, "PNG")
    print(f"saved: {args.out} ({args.size}x{args.size})")


if __name__ == "__main__":
    main()
