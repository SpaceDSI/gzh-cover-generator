#!/usr/bin/env python3
"""Attach a rendered cover to an existing WeChat draft, with the RIGHT 1:1 crop.

This is the "push" step that has burned us repeatedly: uploading the cover as
``thumb_media_id`` is only half the job. The 1:1 image WeChat shows in a share
card / forwarded message is chosen by ``pic_crop_1_1`` on that same cover
material — omit it and WeChat silently falls back to the CENTRE of the cover,
slicing a left-headline + right-hero design in half.

What it does
------------
1. Reads the cover, derives the crop coordinates via ``share_crop``.
2. Downscales to a 900px-wide thumb and steps JPEG quality down until it is
   under WeChat's 64KB limit for ``type=thumb``.
3. ``material/add_material?type=thumb`` -> new ``thumb_media_id``.
4. ``draft/get`` -> keep title/author/digest/content/... untouched -> swap in
   the new thumb + crop -> ``draft/update``.
5. Reads the draft back and verifies the thumb actually switched.

Usage
-----
    python scripts/push_cover.py --media-id <draft_media_id> --cover wechat_cover.png
    python scripts/push_cover.py --media-id ... --cover ... --side center
    python scripts/push_cover.py --media-id ... --crop-only          # keep the thumb
    python scripts/push_cover.py --media-id ... --cover ... --dry-run

Credentials: env ``WECHAT_APP_ID`` / ``WECHAT_APP_SECRET`` (same as the rest of
the WeChat pipeline).

Known limit: a draft in a scheduled-publish state rejects every edit with
``53407``. Cancel the schedule in the 公众号后台 first, then re-run.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import share_crop  # noqa: E402

API = "https://api.weixin.qq.com/cgi-bin"
THUMB_MAX_BYTES = 62 * 1024   # WeChat's hard limit is 64KB; keep a safety margin
KEEP_FIELDS = (
    "title", "author", "digest", "content", "content_source_url",
    "need_open_comment", "only_fans_can_comment",
)


def _get_token() -> str:
    app = os.environ.get("WECHAT_APP_ID")
    sec = os.environ.get("WECHAT_APP_SECRET")
    if not app or not sec:
        sys.exit("缺少环境变量 WECHAT_APP_ID / WECHAT_APP_SECRET")
    url = f"{API}/token?grant_type=client_credential&appid={app}&secret={sec}"
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "access_token" not in data:
        sys.exit(f"取 access_token 失败: {data}")
    return data["access_token"]


def _post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def _post_file(url: str, path: Path) -> dict:
    boundary = "----wb" + uuid.uuid4().hex
    buf = b""
    buf += f"--{boundary}\r\n".encode()
    buf += f'Content-Disposition: form-data; name="media"; filename="{path.name}"\r\n'.encode()
    buf += b"Content-Type: image/jpeg\r\n\r\n"
    buf += path.read_bytes() + b"\r\n"
    buf += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        url, data=buf, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def make_thumb(cover: Path, out: Path, width: int = 900) -> Path:
    """900-wide JPEG squeezed under WeChat's 64KB thumb limit."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("需要 Pillow：pip install pillow")
    with Image.open(cover) as im:
        im = im.convert("RGB")
        h = max(1, round(im.height * width / im.width))
        im = im.resize((width, h), Image.LANCZOS)
    for q in (88, 84, 80, 76, 72, 68, 64, 60, 55):
        im.save(out, quality=q, optimize=True)
        if out.stat().st_size < THUMB_MAX_BYTES:
            return out
    sys.exit(f"缩略图压不进 64KB（当前 {out.stat().st_size // 1024}KB），请改用更简单的封面")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Push a cover onto an existing WeChat draft and set the 1:1 "
                    "share crop (pic_crop_1_1) so the share card shows the RIGHT slice."
    )
    ap.add_argument("--media-id", required=True, help="Target draft media_id")
    ap.add_argument("--cover", help="Cover PNG/JPG (required unless --crop-only)")
    ap.add_argument("--side", choices=["right", "center", "left"], default="right",
                    help="Which 1:1 square the share card should show (default right)")
    ap.add_argument("--crop-only", action="store_true",
                    help="Only update pic_crop_1_1 / pic_crop_235_1, keep the current thumb")
    ap.add_argument("--index", type=int, default=0, help="Article index inside the draft (default 0)")
    ap.add_argument("--thumb-out", default="thumb.jpg", help="Where to write the 900px thumb")
    ap.add_argument("--dry-run", action="store_true", help="Print the plan, call nothing")
    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(0)
    args = ap.parse_args()

    if not args.crop_only and not args.cover:
        sys.exit("需要 --cover（或加 --crop-only 只改裁剪）")
    cover = Path(args.cover) if args.cover else None
    if cover and not cover.exists():
        sys.exit(f"找不到封面: {cover}")

    # Crop coordinates come from the COVER's real pixel size; the thumb keeps the
    # same aspect ratio, so the normalised values are identical either way.
    if cover:
        from PIL import Image
        with Image.open(cover) as im:
            w, h = im.size
    else:
        w = h = None

    if w:
        crops = share_crop.crop_string(w, h, args.side)
    else:
        crops = {"pic_crop_1_1": "0.574468_0_1_1", "pic_crop_235_1": "0_0_1_1"}
        print("[warn] --crop-only 且无 --cover：按 2350x1000 的默认坐标处理")

    print(f"draft     : {args.media_id}  (index {args.index})")
    print(f"side      : {args.side}")
    print(f"pic_crop_1_1   = {crops['pic_crop_1_1']}")
    print(f"pic_crop_235_1 = {crops['pic_crop_235_1']}")

    thumb = None
    if cover:
        thumb = make_thumb(cover, Path(args.thumb_out))
        print(f"thumb     : {thumb}  ({thumb.stat().st_size // 1024}KB, 900px wide)")

    if args.dry_run:
        print("\n[dry-run] 未调用任何接口。")
        return

    token = _get_token()
    draft = _post_json(f"{API}/draft/get?access_token={token}", {"media_id": args.media_id})
    if draft.get("errcode"):
        sys.exit(f"draft/get 失败: {draft}")
    items = draft["news_item"]
    if args.index >= len(items):
        sys.exit(f"index {args.index} 越界（该草稿共 {len(items)} 篇）")
    cur = items[args.index]
    print(f"title     : {cur['title']}")
    print(f"thumb old : {cur.get('thumb_media_id')}")

    art = {k: cur[k] for k in KEEP_FIELDS if k in cur}
    art.update(pic_crop_1_1=crops["pic_crop_1_1"], pic_crop_235_1=crops["pic_crop_235_1"])

    if thumb is not None:
        up = _post_file(f"{API}/material/add_material?access_token={token}&type=thumb", thumb)
        if up.get("errcode"):
            sys.exit(f"上传缩略图失败: {up}")
        art["thumb_media_id"] = up["media_id"]
        print(f"thumb new : {up['media_id']}")
    else:
        art["thumb_media_id"] = cur["thumb_media_id"]

    upd = _post_json(
        f"{API}/draft/update?access_token={token}",
        {"media_id": args.media_id, "index": args.index, "articles": art},
    )
    if upd.get("errcode"):
        hint = ""
        if upd.get("errcode") == 53407:
            hint = "\n  → 该草稿在定时发布中：先在公众号后台取消定时发布，再重跑本脚本。"
        sys.exit(f"draft/update 被拒: {upd}{hint}")
    print(f"draft/update: {upd}")

    back = _post_json(
        f"{API}/draft/get?access_token={token}", {"media_id": args.media_id}
    )["news_item"][args.index]
    ok_thumb = back.get("thumb_media_id") == art["thumb_media_id"]
    ok_body = len(back.get("content", "")) == len(cur.get("content", ""))
    print(f"verify    : thumb={'OK' if ok_thumb else 'MISMATCH'}  "
          f"body={'OK' if ok_body else 'CHANGED'}({len(back.get('content', ''))} chars)")
    print("注意      : draft/get 不回显 pic_crop_*，裁剪是否生效请在后台「封面设置」"
          "看 1:1 预览，或发表后看分享卡片。")
    if not (ok_thumb and ok_body):
        sys.exit(1)


if __name__ == "__main__":
    main()
