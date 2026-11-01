#!/usr/bin/env python3
"""Render a stable 2.35:1 WeChat cover with exact Chinese typography.

Input:  cover_brief.json
Output: PNG, default 2350x1000.

The renderer is driven entirely by ``scripts/style_presets.py`` so all 14
weekly styles (two per weekday: ECONOMIST/HELVETIC, MONOCLE/AEGEAN,
NEW YORKER/BROADSHEET, WIRED/DECO, KINFOLK/CLEAN, HARVARD/AGENT,
TECH/CODEX) share one code path. It supports both dark-tone styles (light text,
gradient headline, dark background) and light-tone magazine styles (dark ink,
paper background, serif or sans headline, letter-spacing).

A preset may opt into a font family via ``"font": "source-han-sans"``; those
styles render every cover glyph in Source Han Sans Bold (思源黑体 Bold).

Covers are **typographic only — no portrait / avatar is composited**. The title
block stays in the LEFT ~29% of the canvas; the CENTER square (x ~675-1675 on a
2350px canvas) is reserved for the theme scene that WeChat keeps when sharing to
朋友圈, and the right wing stays open as negative space.

Final Chinese text is always drawn with Pillow, never by an image model. An
imagegen output may be supplied as an optional background layer.

Set ``"style": "auto"`` in the brief to rotate the style by today's weekday.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import random
import sys
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
except ImportError:  # 延迟到真正渲染时才报错：保证 --help/无子命令探测退出码为 0
    Image = ImageDraw = ImageEnhance = ImageFilter = ImageFont = ImageOps = None

Color = Tuple[int, int, int, int]
RGB = Tuple[int, int, int]

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import style_presets as sp  # noqa: E402
import cover_motifs as cm  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[1]
BRAND_MARK = sp.BRAND_MARK

# Headline metrics are brand constants, deliberately NOT style variables:
# every style must render the hero block at the same glyph scale so the weekly
# rotation reads as one consistent publication. Only the decor-driven start `y`
# is allowed to shrink the available height.
HEADLINE_CEILING = 206
HERO_STROKE_W = 10
# 主标题整体缩放：<1 让左侧大标题更小（配合「文字区收窄到 50%」的字号再减）。
HERO_SCALE = 0.85


# --------------------------------------------------------------------------- fonts
FONT_SANS_BOLD = [
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:/Windows/Fonts/NotoSansSC-VF.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

FONT_SANS_REGULAR = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:/Windows/Fonts/NotoSansSC-VF.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

# CJK serif (宋体/明朝体) candidates — used by ECONOMIST / NEW YORKER / KINFOLK / HARVARD.
FONT_SERIF_BOLD = [
    "C:/Windows/Fonts/STZHONGS.TTF",     # 华文中宋
    "C:/Windows/Fonts/NotoSerifSC-VF.ttf",
    "C:/Windows/Fonts/STSONG.TTF",       # 华文宋体
    "C:/Windows/Fonts/simsun.ttc",       # 宋体
    "/System/Library/Fonts/Songti.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Bold.ttc",
    "C:/Windows/Fonts/simfang.ttf",
]

FONT_SERIF_REGULAR = [
    "C:/Windows/Fonts/NotoSerifSC-VF.ttf",
    "C:/Windows/Fonts/STSONG.TTF",
    "C:/Windows/Fonts/simsun.ttc",
    "/System/Library/Fonts/Songti.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
    "C:/Windows/Fonts/simfang.ttf",
]

# 思源黑体（Source Han Sans / Noto Sans SC）——2026-10 新增 4 套风格指定的封面字体。
# Windows 自带 `NotoSansSC-VF.ttf` 即思源黑体可变字体，`font()` 会自动挑 Bold 实例；
# 找不到思源系列时按 find_font 的通用回退链降级（微软雅黑 / Noto CJK），不会崩。
FONT_SOURCE_HAN_BOLD = [
    "C:/Windows/Fonts/NotoSansSC-VF.ttf",
    "C:/Windows/Fonts/SourceHanSansSC-Bold.otf",
    str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts/SourceHanSansSC-Bold.otf"),
    str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts/NotoSansSC-VF.ttf"),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf",
]

FONT_SOURCE_HAN_REGULAR = [
    "C:/Windows/Fonts/NotoSansSC-VF.ttf",
    "C:/Windows/Fonts/SourceHanSansSC-Regular.otf",
    str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts/SourceHanSansSC-Regular.otf"),
    str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts/NotoSansSC-VF.ttf"),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]

# Per-style font families. A preset opts in with `"font": "<family>"`; anything
# else falls through to the historic serif/sans behaviour.
FONT_FAMILIES = {
    "source-han-sans": {"bold": FONT_SOURCE_HAN_BOLD, "regular": FONT_SOURCE_HAN_REGULAR},
}


def _font_candidates(bold: bool, serif: bool, family: Optional[str] = None) -> Sequence[str]:
    if family:
        fam = FONT_FAMILIES.get(str(family).strip().lower())
        if fam:
            return fam["bold"] if bold else fam["regular"]
    if serif:
        return FONT_SERIF_BOLD if bold else FONT_SERIF_REGULAR
    return FONT_SANS_BOLD if bold else FONT_SANS_REGULAR


def find_font(bold: bool = True, serif: bool = False, family: Optional[str] = None) -> str:
    for p in list(_font_candidates(bold, serif, family)) + list(FONT_SANS_BOLD) + list(FONT_SERIF_REGULAR):
        if Path(p).exists():
            return p
    raise FileNotFoundError("No usable CJK font found. Install Noto Sans/Serif CJK or a Windows CJK font.")


def font(size: int, bold: bool = True, serif: bool = False, family: Optional[str] = None) -> ImageFont.FreeTypeFont:
    path = find_font(bold, serif, family)
    f = ImageFont.truetype(path, size=size)
    # Try to pick a heavy/regular instance on variable fonts; harmless if unsupported.
    if "VF" in Path(path).name.upper():
        for name in (("Bold", "SemiBold", "Black") if bold else ("Regular", "Light")):
            try:
                f.set_variation_by_name(name)
                break
            except Exception:
                continue
    return f


# ----------------------------------------------------------------------- geometry
def resolve_asset_path(path_value: Optional[str], brief_path: Optional[Path] = None) -> Optional[Path]:
    if not path_value:
        return None
    raw = str(path_value).strip()
    if not raw:
        return None
    p = Path(raw).expanduser()
    candidates = []
    if p.is_absolute():
        candidates.append(p)
    else:
        candidates.append(Path.cwd() / p)
        if brief_path is not None:
            candidates.append(brief_path.parent / p)
        candidates.append(SKILL_ROOT / p)
    for cand in candidates:
        if cand.exists():
            return cand
    return candidates[0] if candidates else None


def text_bbox(draw: ImageDraw.ImageDraw, xy: Tuple[int, int], text: str, fnt: ImageFont.FreeTypeFont, stroke_width: int = 0):
    return draw.textbbox(xy, text, font=fnt, stroke_width=stroke_width)


def spacing_px(fnt: ImageFont.FreeTypeFont, ratio: float) -> int:
    return int(round(fnt.size * float(ratio))) if ratio else 0


def _is_wide(ch: str) -> bool:
    """True for CJK / full-width characters (letter-spacing applies only to these)."""
    o = ord(ch)
    return 0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFFEF


def spaced_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, gap: int) -> int:
    if gap <= 0:
        b = draw.textbbox((0, 0), text, font=fnt)
        return b[2] - b[0]
    total = 0
    for i, ch in enumerate(text):
        b = draw.textbbox((0, 0), ch, font=fnt)
        total += b[2] - b[0]
        # Only widen after CJK characters, so Latin words stay intact.
        if i != len(text) - 1 and _is_wide(ch):
            total += gap
    return total


def fit_font_size(text: str, max_width: int, max_height: int, start: int, minimum: int,
                  bold: bool = True, serif: bool = False, stroke_width: int = 0, gap_ratio: float = 0.0,
                  family: Optional[str] = None) -> ImageFont.FreeTypeFont:
    dummy = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)
    step = max(2, start // 40)
    for size in range(start, minimum - 1, -step):
        f = font(size, bold=bold, serif=serif, family=family)
        gap = spacing_px(f, gap_ratio)
        # Width: letter-spacing (when the style tracks CJK) plus the outward
        # stroke, so the outline never overflows the wrap box.
        if gap > 0:
            w = spaced_width(d, text, f, gap) + 2 * stroke_width
        else:
            bb = text_bbox(d, (0, 0), text, f, stroke_width=stroke_width)
            w = bb[2] - bb[0]
        # Height: ALWAYS the plain full-string glyph box. Two reasons — the stroke
        # bleeds outward and must not shrink the type, and both spacing paths must
        # agree on one metric (measuring a lone CJK glyph instead ran ~5% taller
        # and silently shrank every tracked style by a step).
        plain = text_bbox(d, (0, 0), text, f, stroke_width=0)
        h = plain[3] - plain[1]
        if w <= max_width and h <= max_height:
            return f
    return font(minimum, bold=bold, serif=serif, family=family)


# ------------------------------------------------------------------ image helpers
def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _sample_stops(colors: Sequence[RGB], t: float) -> RGB:
    stops = len(colors) - 1
    if stops <= 0:
        return tuple(colors[0])
    t = max(0.0, min(1.0, t))
    seg = min(stops - 1, int(t * stops))
    local = (t * stops) - seg
    c0, c1 = colors[seg], colors[min(seg + 1, len(colors) - 1)]
    return tuple(int(round(_lerp(c0[k], c1[k], local))) for k in range(3))


def gradient_image(size: Tuple[int, int], colors: Sequence[RGB], axis: str = "v") -> Image.Image:
    """Fast smooth gradient built from a small strip resized to full size."""
    w, h = size
    n = 360
    if axis == "v":
        small = Image.new("RGB", (1, n))
        px = small.load()
        for i in range(n):
            px[0, i] = _sample_stops(colors, i / (n - 1))
        small = small.resize((w, h), Image.BILINEAR)
    elif axis == "h":
        small = Image.new("RGB", (n, 1))
        px = small.load()
        for i in range(n):
            px[i, 0] = _sample_stops(colors, i / (n - 1))
        small = small.resize((w, h), Image.BILINEAR)
    else:  # diagonal
        small = Image.new("RGB", (n, n))
        px = small.load()
        for y in range(n):
            for x in range(n):
                px[x, y] = _sample_stops(colors, (x / (n - 1) * 0.55) + (y / (n - 1) * 0.45))
        small = small.resize((w, h), Image.BILINEAR)
    return small.convert("RGBA")


def vignette_layer(size: Tuple[int, int], strength: float, center: Tuple[float, float] = (0.55, 0.5)) -> Image.Image:
    w, h = size
    mw, mh = 180, 90
    m = Image.new("L", (mw, mh), 0)
    px = m.load()
    maxd = math.hypot(max(center[0], 1 - center[0]) * 1.15, max(center[1], 1 - center[1]) * 1.35) or 1.0
    for y in range(mh):
        for x in range(mw):
            dx = (x / (mw - 1) - center[0]) * 1.15
            dy = (y / (mh - 1) - center[1]) * 1.35
            d = min(1.0, (math.hypot(dx, dy) / maxd))
            px[x, y] = int((d ** 1.6) * 255 * max(0.0, min(1.0, strength)))
    m = m.resize((w, h), Image.BILINEAR)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.putalpha(m)
    return layer


def grain_layer(size: Tuple[int, int], amount: int = 12) -> Image.Image:
    w, h = size
    noise = Image.effect_noise((235, 100), 26).convert("L")
    noise = noise.resize((w, h), Image.NEAREST)
    alpha = noise.point(lambda v: int(abs(v - 128) / 128 * amount))
    layer = Image.new("RGBA", (w, h), (128, 128, 128, 0))
    layer.putalpha(alpha)
    return layer


def grid_layer(size: Tuple[int, int], color: RGB, step: int = 132, alpha: int = 54, width: int = 2) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, w, step):
        d.line((x, 0, x, h), fill=(*color, alpha), width=width)
    for y in range(0, h, step):
        d.line((0, y, w, y), fill=(*color, alpha), width=width)
    return layer


def scanline_layer(size: Tuple[int, int], alpha: int = 22, step: int = 4) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, h, step):
        d.line((0, y, w, y), fill=(0, 0, 0, alpha), width=1)
    return layer


def tech_motif(size: Tuple[int, int], preset: dict, seed: int) -> Image.Image:
    """Neon streaks, UI panels, and (for purple) a knowledge graph. Dark styles only."""
    w, h = size
    rnd = random.Random(seed)
    bg = preset.get("bg", {})
    neon = tuple(bg.get("neon", preset.get("accent", (28, 157, 255))))
    secondary = tuple(preset.get("accent", (255, 190, 50)))
    gold = (255, 196, 55)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    for _ in range(30):
        y = rnd.randint(int(h * 0.05), int(h * 0.95))
        x0 = rnd.randint(-200, int(w * 0.55))
        x1 = rnd.randint(int(w * 0.58), w + 300)
        width = rnd.choice([2, 3, 4, 6])
        color = neon if rnd.random() > 0.3 else gold
        d.line((x0, y, x1, int(y + rnd.uniform(-140, 140))), fill=(*color, rnd.randint(40, 120)), width=width)

    for _ in range(7):
        px = rnd.randint(int(w * 0.50), int(w * 0.90))
        py = rnd.randint(int(h * 0.08), int(h * 0.74))
        pw = rnd.randint(180, 360)
        ph = rnd.randint(80, 180)
        d.rounded_rectangle((px, py, px + pw, py + ph), radius=18, outline=(*neon, 120), fill=(0, 18, 42, 55), width=2)
        for i in range(3):
            yy = py + 26 + i * 25
            d.line((px + 22, yy, px + rnd.randint(90, pw - 20), yy), fill=(*neon, 85), width=2)

    if bg.get("nodes"):
        pts = [(rnd.randint(int(w * 0.28), int(w * 0.86)), rnd.randint(40, h - 90)) for _ in range(34)]
        for a, b in zip(pts, pts[1:]):
            if rnd.random() > 0.35:
                d.line((a[0], a[1], b[0], b[1]), fill=(*neon, 70), width=2)
        for p in pts:
            r = rnd.randint(4, 8)
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=(*neon, 150))
        cx, cy = int(w * 0.09), int(h * 0.30)
        prism = [(cx, cy - 120), (cx + 95, cy - 30), (cx + 60, cy + 130), (cx - 80, cy + 100), (cx - 105, cy - 25)]
        d.polygon(prism, fill=(112, 51, 200, 170), outline=(224, 188, 255, 210))
        d.line((cx, cy - 120, cx - 20, cy + 110), fill=(240, 220, 255, 150), width=3)
        d.line((cx + 95, cy - 30, cx - 80, cy + 100), fill=(240, 220, 255, 90), width=2)
    else:
        cx, cy = int(w * 0.72), int(h * 0.38)
        for r, a in [(170, 30), (115, 50), (72, 85)]:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*neon, a), width=5)
        d.rounded_rectangle((cx - 90, cy - 90, cx + 90, cy + 90), radius=22, outline=(*neon, 170), fill=(0, 18, 50, 90), width=4)

    return layer.filter(ImageFilter.GaussianBlur(radius=1.1))


def column_rules_layer(size: Tuple[int, int], color: RGB, alpha: int = 26, cols: int = 4) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(1, cols):
        x = int(w * 0.06 + (w * 0.52) * i / cols)
        d.line((x, int(h * 0.30), x, int(h * 0.72)), fill=(*color, alpha), width=1)
    return layer


def make_fallback_background(w: int, h: int, preset: dict, seed: int) -> Image.Image:
    tone = preset.get("tone", "dark")
    bg = preset.get("bg", {})
    colors = list(bg.get("colors", [(0, 0, 0)]))
    kind = bg.get("kind", "gradient")

    if kind == "solid" and len(colors) >= 2:
        canvas = gradient_image((w, h), colors, axis="v")
    else:
        canvas = gradient_image((w, h), colors if len(colors) > 1 else [colors[0], colors[0]], axis="v")

    # Style-specific texture / motif.
    if bg.get("grain"):
        canvas.alpha_composite(grain_layer((w, h), amount=14 if tone == "light" else 18))
    if bg.get("grid"):
        canvas.alpha_composite(
            grid_layer(
                (w, h),
                tuple(bg.get("grid_color", (30, 30, 34))),
                step=int(bg.get("grid_step", 132)),
                alpha=int(bg.get("grid_alpha", 54)),
                width=int(bg.get("grid_width", 2)),
            )
        )
    if tone == "dark" and (bg.get("nodes") or bg.get("neon")):
        canvas.alpha_composite(tech_motif((w, h), preset, seed))
    if preset["id"] == "wired-black":
        canvas.alpha_composite(scanline_layer((w, h)))
    if preset["id"] == "economist-crimson":
        canvas.alpha_composite(column_rules_layer((w, h), (255, 255, 255), alpha=22))

    # Vignette.
    strength = float(bg.get("vignette", 0.0) or 0.0)
    if strength > 0:
        center = (0.5, 0.5) if tone == "light" else (0.58, 0.48)
        canvas.alpha_composite(vignette_layer((w, h), strength, center=center))

    # Left readability overlay for dark styles only.
    overlay_alpha = int(preset.get("overlay_alpha", 0) or 0)
    if overlay_alpha > 0:
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle((0, 0, int(w * 0.64), h), fill=(0, 0, 0, overlay_alpha))
        canvas.alpha_composite(overlay)
    return canvas


def load_background(path: Optional[str | Path], w: int, h: int, preset: dict, seed: int,
                    brief_path: Optional[Path] = None, share_side: str = "right",
                    auto_center: bool = True) -> Image.Image:
    resolved = resolve_asset_path(str(path) if path else None, brief_path)
    if resolved and resolved.exists():
        img = Image.open(resolved).convert("RGB")
        # Strip the ImageGen corner watermark ("AI生成 / WORKBUDD") BEFORE any
        # recentring/cropping — the mark lives at the raw background's corner, so
        # it must be detected and repainted at its natural position. Bake it into
        # the default pipeline so every cover ships watermark-free.
        try:
            import remove_watermark as rwm
            img = rwm.remove_watermark(img)
        except Exception:  # never let watermark removal break a render
            pass
        img = img.convert("RGBA")
        # Auto-centre the hero scene inside the share zone (default: the right
        # 42.6% slice). This makes ImageGen's often-centred composition land
        # exactly where the 1:1 crop keeps it — baked into the skill default.
        if auto_center:
            try:
                import position_scene as ps
                img = ps.center_scene(img.convert("RGB"), share_side).convert("RGBA")
            except Exception:  # never let scene-positioning break a render
                pass
        img = ImageOps.fit(img, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        overlay_alpha = int(preset.get("overlay_alpha", 0) or 0)
        if overlay_alpha > 0:
            dim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            dd = ImageDraw.Draw(dim)
            dd.rectangle((0, 0, int(w * 0.65), h), fill=(0, 0, 0, min(160, overlay_alpha + 20)))
            img.alpha_composite(dim)
        return img
    return make_fallback_background(w, h, preset, seed)


# ------------------------------------------------------------------- decorations
def draw_masthead(canvas: Image.Image, preset: dict, text: str) -> None:
    decor = preset["decor"].get("masthead")
    if not decor:
        return
    w, h = canvas.size
    tone = preset.get("tone", "dark")
    f = font(42, bold=not decor.get("italic"), serif=True if decor.get("italic") else preset.get("serif", False),
             family=preset.get("font"))
    d = ImageDraw.Draw(canvas)
    x = int(w * 0.055)
    bar_h = int(h * 0.088)
    label = (text or decor.get("default_text") or BRAND_MARK).strip()

    if decor.get("bg"):
        # Solid masthead band across the top (ECONOMIST).
        bar = Image.new("RGBA", (w, bar_h), (*tuple(decor["bg"]), 255))
        canvas.alpha_composite(bar, (0, 0))
        d = ImageDraw.Draw(canvas)
        # red accent square before the kicker
        sq = int(bar_h * 0.46)
        sy = (bar_h - sq) // 2
        d.rectangle((x, sy, x + sq, sy + sq), fill=(*tuple(decor.get("accent", (200, 40, 40))), 255))
        tx = x + sq + 26
        b = text_bbox(d, (0, 0), label, f)
        d.text((tx, (bar_h - (b[3] - b[1])) // 2 - b[1] + 2), label, font=f, fill=(*tuple(decor["fg"]), 250))
        d.line((0, bar_h, w, bar_h), fill=(*tuple(decor.get("accent", (200, 40, 40))), 220), width=3)
        return

    # Italic / rule-only masthead (NEW YORKER).
    color = tuple(decor.get("fg", preset.get("ink", (28, 26, 24))))
    y = int(h * 0.062)
    d.text((x, y), label, font=f, fill=(*color, 235))
    b = text_bbox(d, (0, 0), label, f)
    accent = tuple(decor.get("accent", preset.get("accent", (170, 56, 44))))
    d.line((x, y + (b[3] - b[1]) + 16, x + (b[2] - b[0]) + 20, y + (b[3] - b[1]) + 16), fill=(*accent, 230), width=3)


def draw_side_band(canvas: Image.Image, preset: dict) -> None:
    band = preset["decor"].get("side_band")
    if not band:
        return
    w, h = canvas.size
    bw = int(band.get("width_px", 16))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle((0, 0, bw, h), fill=(*tuple(band["color"]), 235))
    canvas.alpha_composite(layer)


def draw_vertical_bar(canvas: Image.Image, preset: dict, text: str) -> None:
    bar = preset["decor"].get("vertical_bar")
    if not bar:
        return
    w, h = canvas.size
    bw = int(bar.get("width_px", 30))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle((0, 0, bw, h), fill=(*tuple(bar["color"]), 235))
    canvas.alpha_composite(layer)

    if bar.get("label"):
        label = (text or BRAND_MARK).strip()[:6]
        f = font(34, bold=False, serif=preset.get("serif", False), family=preset.get("font"))
        d = ImageDraw.Draw(canvas)
        x = bw + 22
        y = int(h * 0.135)
        lh = int(f.size * 1.28)
        for ch in label:
            b = text_bbox(d, (0, 0), ch, f)
            d.text((x - b[0], y), ch, font=f, fill=(*tuple(preset.get("ink_soft", (86, 84, 82))), 235))
            y += lh


def draw_top_rule(canvas: Image.Image, preset: dict) -> None:
    rule = preset["decor"].get("top_rule")
    if not rule:
        return
    w, h = canvas.size
    d = ImageDraw.Draw(canvas)
    ht = int(rule.get("width_px", 8))
    d.rectangle((0, 0, w, ht), fill=(*tuple(rule["color"]), 255))


def draw_seal(canvas: Image.Image, preset: dict, text: str) -> None:
    seal = preset["decor"].get("seal")
    if not seal:
        return
    w, h = canvas.size
    r = 68
    cx, cy = 128, 128
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*tuple(seal["ring"]), 240), width=5, fill=(*tuple(seal["fill"]), 205))
    d.ellipse((cx - r + 11, cy - r + 11, cx + r - 11, cy + r - 11), outline=(*tuple(seal["ring"]), 170), width=2)
    ch = (text or BRAND_MARK).strip()[:1] or "智"
    f = font(int(r * 0.92), bold=True, serif=True)
    b = text_bbox(d, (0, 0), ch, f)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], cy - (b[3] - b[1]) / 2 - b[1]), ch, font=f, fill=(*tuple(seal.get("fg", (232, 206, 128))), 245))
    canvas.alpha_composite(layer)


def draw_short_rule(canvas: Image.Image, preset: dict, y: int) -> None:
    rule = preset["decor"].get("short_rule")
    if not rule:
        return
    w, h = canvas.size
    d = ImageDraw.Draw(canvas)
    x = int(w * 0.055)
    ht = int(rule.get("width_px", 4))
    d.rectangle((x, y, x + 210, y + ht), fill=(*tuple(rule["color"]), 235))


def draw_bottom_band(canvas: Image.Image, preset: dict) -> None:
    """Full-width colour band hugging the bottom edge (AEGEAN postcard).

    It is drawn as a decoration, i.e. before the title and the bottom tag row,
    so the tags land on top of the band — which is why this style sets a light
    ``tags.fg``.
    """
    band = preset["decor"].get("bottom_band")
    if not band:
        return
    w, h = canvas.size
    d = ImageDraw.Draw(canvas)
    top = int(h * float(band.get("top_ratio", 0.855)))
    d.rectangle((0, top, w, h), fill=(*tuple(band["color"]), 255))
    if band.get("edge"):
        d.line((0, top + 1, w, top + 1), fill=(*tuple(band["edge"]), 220), width=3)


def draw_deco_frame(canvas: Image.Image, preset: dict) -> None:
    """Art Deco double-line frame with sunburst corner fans (DECO).

    ``inset_top`` is normally pushed below the masthead band so the two never
    collide; the frame is drawn before the title so type always stays on top.
    """
    frame = preset["decor"].get("deco_frame")
    if not frame:
        return
    w, h = canvas.size
    d = ImageDraw.Draw(canvas)
    color = tuple(frame.get("color", preset.get("accent", (201, 162, 39))))
    lw = int(frame.get("width", 3))
    ix = int(w * float(frame.get("inset_x", 0.03)))
    top = int(h * float(frame.get("inset_top", 0.12)))
    bottom = int(h * float(frame.get("inset_bottom", 0.96)))
    box = (ix, top, w - ix, bottom)
    d.rectangle(box, outline=(*color, 230), width=lw)
    if frame.get("double", True):
        pad = 11
        d.rectangle((box[0] + pad, box[1] + pad, box[2] - pad, box[3] - pad),
                    outline=(*color, 120), width=2)
    if frame.get("fan", True):
        r = int(frame.get("fan_r", 44))
        corners = (
            (box[0], box[1], 0, 90),
            (box[2], box[1], 90, 180),
            (box[2], box[3], 180, 270),
            (box[0], box[3], 270, 360),
        )
        for cx, cy, a0, a1 in corners:
            for k in range(6):
                ang = math.radians(a0 + (a1 - a0) * k / 5.0)
                d.line((cx, cy, cx + r * math.cos(ang), cy + r * math.sin(ang)),
                       fill=(*color, 195), width=3)
            rr = r * 0.62
            d.arc((cx - rr, cy - rr, cx + rr, cy + rr), a0, a1, fill=(*color, 210), width=3)


def draw_column_rules(canvas: Image.Image, preset: dict) -> None:
    """Vertical newspaper column rules (BROADSHEET 号外).

    Drawn before the headline so the type sits on top of the rules — exactly
    how a real broadsheet extra looks.
    """
    rules = preset["decor"].get("column_rules")
    if not rules:
        return
    w, h = canvas.size
    d = ImageDraw.Draw(canvas)
    color = tuple(rules.get("color", preset.get("ink", (10, 10, 10))))
    alpha = int(rules.get("alpha", 55))
    cols = int(rules.get("cols", 3))
    lw = int(rules.get("width_px", 2))
    top = int(h * float(rules.get("top_ratio", 0.40)))
    bottom = int(h * float(rules.get("bottom_ratio", 0.87)))
    for i in range(1, cols + 1):
        x = int(w * (0.055 + 0.72 * i / (cols + 1)))
        d.line((x, top, x, bottom), fill=(*color, alpha), width=lw)


# ----------------------------------------------------------------------- text
def draw_gradient_text(canvas, xy, text, fnt, fill_colors, stroke_fill=(0, 0, 0), stroke_width=8,
                       shadow=True, glow_color=None) -> None:
    x, y = xy
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if shadow:
        d.text((x + stroke_width * 2, y + stroke_width * 2), text, font=fnt, fill=(0, 0, 0, 180),
               stroke_width=stroke_width + 2, stroke_fill=(0, 0, 0, 160))
    if glow_color:
        mask_glow = Image.new("L", canvas.size, 0)
        gd = ImageDraw.Draw(mask_glow)
        gd.text((x, y), text, font=fnt, fill=255, stroke_width=stroke_width + 3, stroke_fill=255)
        glow = Image.new("RGBA", canvas.size, (*glow_color, 95))
        blur = mask_glow.filter(ImageFilter.GaussianBlur(radius=12))
        canvas.alpha_composite(Image.composite(glow, Image.new("RGBA", canvas.size, (0, 0, 0, 0)), blur))
    d.text((x, y), text, font=fnt, fill=(*stroke_fill, 255), stroke_width=stroke_width, stroke_fill=(*stroke_fill, 255))
    canvas.alpha_composite(layer)
    mask = Image.new("L", canvas.size, 0)
    md = ImageDraw.Draw(mask)
    md.text((x, y), text, font=fnt, fill=255)
    grad = gradient_image(canvas.size, fill_colors, axis="v")
    canvas.alpha_composite(Image.composite(grad, Image.new("RGBA", canvas.size, (0, 0, 0, 0)), mask))
    highlight_mask = Image.new("L", canvas.size, 0)
    hd = ImageDraw.Draw(highlight_mask)
    hd.text((x, y - 2), text, font=fnt, fill=90)
    white = Image.new("RGBA", canvas.size, (255, 255, 255, 45))
    canvas.alpha_composite(Image.composite(white, Image.new("RGBA", canvas.size, (0, 0, 0, 0)), highlight_mask))


def draw_solid_spaced_text(canvas, xy, text, fnt, fill, gap=0, shadow_color=None) -> None:
    x, y = xy
    d = ImageDraw.Draw(canvas)
    if shadow_color:
        d.text((x + 3, y + 3), text, font=fnt, fill=(*shadow_color, 90))
    if gap <= 0:
        d.text((x, y), text, font=fnt, fill=(*fill, 255))
        return
    for i, ch in enumerate(text):
        b = text_bbox(d, (0, 0), ch, fnt)
        d.text((x - b[0], y), ch, font=fnt, fill=(*fill, 255))
        x += (b[2] - b[0])
        if i != len(text) - 1 and _is_wide(ch):
            x += gap


def rounded_rect_gradient(im, box, colors, radius=28, outline=None) -> None:
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return
    grad = gradient_image((w, h), colors, axis="h")
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    im.alpha_composite(Image.composite(grad, Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask), (x0, y0))
    if outline:
        d = ImageDraw.Draw(im)
        d.rounded_rectangle(box, radius=radius, outline=outline, width=3)


def draw_badge(canvas: Image.Image, text: str, preset: dict, y: int,
               right_limit: int | None = None) -> None:
    if not text:
        return
    d = ImageDraw.Draw(canvas)
    w, h = canvas.size
    tone = preset.get("tone", "dark")
    badge = preset["badge"]
    serif = preset.get("serif", False)
    # Keep the badge inside the LEFT column. ``right_limit`` is the layout band
    # passed from render(): ~0.28*w for the center-scene layout (must not cross
    # the center square x675 that WeChat keeps) or ~0.52*w for the right-scene
    # layout (title spans left ~52%, scene on the right, right crop for share).
    left_x = int(w * 0.055)
    if right_limit is None:
        right_limit = int(w * 0.275)
    max_text_w = right_limit - left_x - 170
    f = fit_font_size(text, max_text_w, 105, 96, 24, bold=True, serif=serif, family=preset.get("font"))
    bbox = text_bbox(d, (0, 0), text, f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = left_x
    box = (x, y, min(x + tw + 160, right_limit), y + th + 62)

    colors = [tuple(c) for c in badge["colors"]]
    outline = tuple(badge.get("outline", colors[-1]))
    rounded_rect_gradient(canvas, box, colors, radius=34, outline=(*outline, 225))

    text_x = x + 80
    text_y = y + 26
    txt = tuple(badge.get("text", (20, 10, 20)))
    bar = tuple(badge.get("bar", preset.get("accent", (160, 80, 255))))
    d.text((text_x + 4, text_y + 4), text, font=f, fill=(0, 0, 0, 120), stroke_width=2, stroke_fill=(0, 0, 0, 120))
    d.text((text_x, text_y), text, font=f, fill=(*txt, 255), stroke_width=1,
           stroke_fill=(255, 255, 255, 70) if tone == "dark" else (0, 0, 0, 40))
    d.text((x - 72, text_y), "»", font=f, fill=(*bar, 235))
    d.text((min(box[2] + 24, right_limit - 10), text_y), "«", font=f, fill=(*bar, 235))


def draw_bottom_tags(canvas: Image.Image, tags: Sequence[str], preset: dict,
                     max_end: int | None = None) -> None:
    if not tags:
        return
    w, h = canvas.size
    d = ImageDraw.Draw(canvas)
    tone = preset.get("tone", "dark")
    tags = list(tags[:4])
    accent = tuple(preset.get("tags", {}).get("accent", preset.get("accent", (28, 157, 255))))
    fg = tuple(preset.get("tags", {}).get("fg", (245, 245, 255)))
    start_x = int(w * 0.065)
    # ``max_end`` is the layout band from render(): the tags must end before it.
    # center layout ~0.282*w (before the center square x675) or right layout
    # ~0.52*w (title spans left ~52%). Shrink until they fit — never overflow.
    if max_end is None:
        max_end = int(w * 0.282)
    y = int(h * 0.875)

    def layout_width(fnt: ImageFont.FreeTypeFont) -> int:
        x = start_x
        for i, tag in enumerate(tags):
            bbox = text_bbox(d, (x + 30, y), tag, fnt)
            x = bbox[2] + 32
            if i != len(tags) - 1:
                x += 32
        return x - start_x

    fam = preset.get("font")
    # Try largest size that fits; if even the smallest doesn't, fall back to a
    # tiny floor (10px) rather than the initial 40px, so the row never crosses 675.
    chosen = None
    for size in range(58, 9, -2):
        f_try = font(size, bold=True, serif=preset.get("serif", False), family=fam)
        if start_x + layout_width(f_try) <= max_end:
            chosen = f_try
            break
    if chosen is None:
        chosen = font(10, bold=True, serif=preset.get("serif", False), family=fam)
    f = chosen
    x = start_x
    for i, tag in enumerate(tags):
        cx, cy = x + 12, y + 30
        d.polygon([(cx, cy - 13), (cx + 13, cy), (cx, cy + 13), (cx - 13, cy)], fill=(*accent, 210))
        d.text((x + 30, y), tag, font=f, fill=(*fg, 240))
        bbox = text_bbox(d, (x + 30, y), tag, f)
        x = bbox[2] + 32
        if i != len(tags) - 1:
            d.line((x, y + 8, x, y + 58), fill=(*accent, 190 if tone == "dark" else 150), width=3)
            x += 32


def draw_title(canvas: Image.Image, brief: dict, preset: dict,
               band: int | None = None) -> None:
    w, h = canvas.size
    tone = preset.get("tone", "dark")
    serif = preset.get("serif", False)
    fam = preset.get("font")
    gap_ratio = float(preset.get("letter_spacing", 0.0) or 0.0)
    decor = preset["decor"]

    eyebrow = str(brief.get("eyebrow", "")).strip()
    hero_lines = [str(x).strip() for x in brief.get("hero_lines", []) if str(x).strip()]
    subtitle = str(brief.get("subtitle", "")).strip()

    left_x = int(w * 0.055)
    if decor.get("vertical_bar"):
        left_x = int(w * 0.085)
    # ``band`` is the title column's right edge, set by render() from the brief's
    # share_side: ~0.28*w for center-scene (keeps the center square x675 clear)
    # or ~0.52*w for right-scene (title spans left ~52%, scene on the right; the
    # right 42.6% slice is then the official share preview and acceptance crop).
    right_limit = band if band is not None else int(w * 0.28)
    max_title_w = right_limit - left_x

    # Title vertical start depends on top decorations.
    if decor.get("masthead"):
        y = int(h * 0.215)
    elif decor.get("seal"):
        y = int(h * 0.235)
    else:
        y = int(h * 0.105)

    d = ImageDraw.Draw(canvas)

    if decor.get("short_rule") and not decor.get("masthead"):
        draw_short_rule(canvas, preset, max(int(h * 0.09), y - int(h * 0.055)))

    # Eyebrow.
    if eyebrow:
        if tone == "dark":
            # 2026-10-27 center-crop: eyebrow must stay left of the center square
            # (x 675). Lower the floor so a long eyebrow still shrinks to fit, and
            # cap the panel's right edge at the center boundary (0.282*w ≈ 663).
            f_eye = fit_font_size(eyebrow, max_title_w, 105, 106, 30, bold=True, serif=serif, family=fam)
            bbox = text_bbox(d, (0, 0), eyebrow, f_eye, stroke_width=4)
            panel = (left_x - 22, y - 16, min(left_x + (bbox[2] - bbox[0]) + 46, right_limit),
                     y + (bbox[3] - bbox[1]) + 34)
            accent = tuple(preset.get("accent", (28, 157, 255)))
            d.rounded_rectangle(panel, radius=18, fill=(0, 0, 0, 120), outline=(*accent, 180), width=2)
            draw_gradient_text(canvas, (left_x, y), eyebrow, f_eye,
                               fill_colors=[(255, 255, 255), (205, 225, 255), (255, 255, 255)],
                               stroke_fill=tuple(preset.get("stroke", (3, 8, 20))), stroke_width=5, shadow=True,
                               glow_color=accent)
            y += int((bbox[3] - bbox[1]) + h * 0.06)
        else:
            # 2026-10-27 center-crop: long eyebrow must shrink to fit left of the
            # center square (x 675); lower the floor and cap the rule at 0.282*w.
            f_eye = fit_font_size(eyebrow, max_title_w, 96, 96, 30, bold=True, serif=serif, family=fam)
            accent = tuple(preset.get("accent", (17, 17, 19)))
            bbox = text_bbox(d, (0, 0), eyebrow, f_eye)
            # accent square + uppercase-ish kicker, no heavy panel on paper
            sq = int(f_eye.size * 0.5)
            d.rectangle((left_x, y + 8, left_x + sq, y + 8 + sq), fill=(*accent, 240))
            tx = left_x + sq + 22
            d.text((tx, y), eyebrow, font=f_eye, fill=(*tuple(preset.get("ink_soft", (86, 84, 82))), 245))
            # 2026-10-27: keep clearance below Latin descenders (p/g/y) so the
            # rule reads as an underline, not a strikethrough.
            rule_y = y + (bbox[3] - bbox[1]) + 30
            d.line((left_x, rule_y, min(left_x + (bbox[2] - bbox[0]) + sq + 22, right_limit), rule_y),
                   fill=(*accent, 105), width=2)
            y += int((bbox[3] - bbox[1]) + h * 0.07)

    # Hero lines.
    # Vertical budget: eyebrow + hero block + subtitle badge must all fit above
    # the bottom tag row, otherwise the badge collides with the last hero line.
    n_lines = max(1, len(hero_lines))
    line_gap = int(h * 0.030)
    badge_h = int(h * 0.168)
    bottom_limit = int(h * 0.845)
    hero_area = max(int(h * 0.20), bottom_limit - badge_h - y)
    # One uniform ceiling for every style AND both tones: the headline scale is a
    # brand constant. Only the decor-driven start `y` may legitimately shrink the
    # budget (a masthead band or a top-left seal eats vertical room).
    max_h = int(max(84, min(HEADLINE_CEILING, hero_area / n_lines - line_gap)))

    for idx, line in enumerate(hero_lines[:3]):
        start_size = 224 if idx == 0 else 194
        stroke_w = HERO_STROKE_W if tone == "dark" else 0
        f_hero = fit_font_size(line, max_title_w, max_h, start_size, 78, bold=True, serif=serif,
                               stroke_width=stroke_w, gap_ratio=gap_ratio, family=fam)
        f_hero = f_hero.font_variant(size=int(round(f_hero.size * HERO_SCALE)))
        bbox = text_bbox(d, (0, 0), line, f_hero, stroke_width=stroke_w)
        line_h = bbox[3] - bbox[1]
        gap = spacing_px(f_hero, gap_ratio)

        if tone == "dark":
            colors = [tuple(c) for c in preset.get("title_gradient", [(255, 255, 255)])]
            draw_gradient_text(canvas, (left_x, y), line, f_hero, fill_colors=colors,
                               stroke_fill=tuple(preset.get("stroke", (0, 0, 0))),
                               stroke_width=max(8, f_hero.size // 16), shadow=True,
                               glow_color=tuple(preset.get("glow", (255, 180, 35))))
        else:
            ink = tuple(preset.get("ink", (24, 24, 27)))
            draw_solid_spaced_text(canvas, (left_x, y), line, f_hero, ink, gap=gap)
        y += line_h + line_gap

    # Subtitle badge, always placed below the hero block and never overlapping it.
    # Nudge it a touch lower (2026-10-27 user request: "副标题偏下一点点"), while
    # clamping so its bottom never reaches the bottom tag band.
    badge_y = min(max(bottom_limit - badge_h, y), y + int(h * 0.032))
    badge_y = min(badge_y + int(h * 0.022), bottom_limit - badge_h)
    draw_badge(canvas, subtitle, preset, badge_y, right_limit)


# ------------------------------------------------------------------------ render
def render(brief_path: Path, style_override: Optional[str] = None, when: Optional[_dt.date] = None) -> Path:
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    canvas_cfg = brief.get("canvas", {})
    w = int(canvas_cfg.get("width", 2350))
    h = int(canvas_cfg.get("height", 1000))

    # share_side drives the layout + share crop. DEFAULT (and delivery standard)
    # is "right": the title spans the left ~52%, the hero scene is auto-centred
    # inside the RIGHT 42.6% square (x 1350-2350), and that 1:1 slice is the
    # acceptance preview. "center" (title left ~28%, scene inside x 675-1675)
    # matches WeChat's real centre crop; "left" is the mirror option.
    share_side = str(brief.get("share_side", "right")).lower()
    band = int(w * (0.52 if share_side == "right" else 0.28))

    requested = style_override or brief.get("style", "auto")
    if when is None and brief.get("date"):
        try:
            when = _dt.date.fromisoformat(str(brief["date"]))
        except ValueError:
            when = None
    sid = sp.resolve_style(requested, when)
    preset = sp.STYLE_PRESETS[sid]

    seed = int(brief.get("seed", 202601))
    bg_path = brief.get("background_path")
    out_path_raw = Path(brief.get("output_path", "wechat_cover.png")).expanduser()
    out_path = out_path_raw if out_path_raw.is_absolute() else brief_path.parent / out_path_raw

    canvas = load_background(bg_path, w, h, preset, seed, brief_path=brief_path,
                             share_side=share_side,
                             auto_center=bool(brief.get("auto_center_scene", True)))

    masthead_text = str(brief.get("masthead_text", "") or "").strip()

    # Center artwork: a semantic composition (primary icon + secondary icon
    # + accent layer, one of several layout archetypes) planned from the cover
    # copy, colored from the style palette, and hard-clipped to the reserved
    # center zone so it can never touch the headline block. Silently skipped on
    # narrow canvases.
    motif_plan = cm.draw_composition(canvas, preset, brief, seed=seed)

    # Decorations (top band / rules / bands / vertical bar) — no portrait layer.
    draw_top_rule(canvas, preset)
    draw_side_band(canvas, preset)
    draw_vertical_bar(canvas, preset, masthead_text)
    draw_masthead(canvas, preset, masthead_text)
    # Texture / framing decorations that must sit UNDER the type.
    draw_column_rules(canvas, preset)
    draw_deco_frame(canvas, preset)
    # Bottom colour band: under the type, over the background (tags land on it).
    draw_bottom_band(canvas, preset)

    draw_seal(canvas, preset, masthead_text)
    draw_title(canvas, brief, preset, band)
    draw_bottom_tags(canvas, brief.get("bottom_tags", []), preset, band)

    rgb = canvas.convert("RGB")
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.05)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(out_path, quality=96)
    print(f"Rendered {out_path}  [style={sid} / {preset['name_en']} {preset['name_zh']}]"
          f"  [motif={motif_plan['signature'] if motif_plan else 'off'}]")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render 2.35:1 WeChat cover from cover_brief.json")
    parser.add_argument("brief", help="Path to cover_brief.json")
    parser.add_argument("--style", default=None, help="Override style id/alias, or 'auto' to rotate by weekday")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD used when style is auto")
    if len(sys.argv) == 1:  # 无子命令：打印用法并 exit 0（沙箱探测要求）
        parser.print_help()
        print("\n提示：需要 cover_brief.json 路径参数，如 "
              "python scripts/render_wechat_cover.py cover_brief.json。", file=sys.stderr)
        sys.exit(0)
    args = parser.parse_args()
    if Image is None:
        print("❌ 缺 Pillow —— 封面渲染的硬依赖。\n   修复：pip install Pillow", file=sys.stderr)
        sys.exit(2)
    when = _dt.date.fromisoformat(args.date) if args.date else None
    render(Path(args.brief), style_override=args.style, when=when)


if __name__ == "__main__":
    main()
