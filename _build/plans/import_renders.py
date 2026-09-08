#!/usr/bin/env python3
"""Import the architect's rendered plans into assets/plans/ as WebP.

Source (client hand-off, not in the repo):
    P6 Floor Plans/1np.png              full 1.NP plan
    P6 Floor Plans/2-5np.png            full 2.-5.NP plan (all four are identical)
    P6 Floor Plans/2-5np/<L>.png        per-apartment, floors 2-5
    P6 Floor Plans/2-5np/1np/<L>.png    per-apartment, floor 1

Two quirks of the hand-off worth knowing:
  * apartment A differs by floor, so it ships as A1 / A2-4 / A5;
    B-I are identical across floors 2-5 and ship once.
  * 1.NP has no apartment I - that corner is the entrance lobby.

Every render is trimmed to its content, flattened onto the page white the
renders already sit on, and written as WebP. Run it again to re-import.
"""
import os, sys
from PIL import Image

SRC = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1
                         else "~/Downloads/P6 Floor Plans")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "plans")
PAGE = (247, 244, 239)          # --paper, so the trim seam never shows

# The two full-floor plans are the reference frame for the clickable overlay in
# "Poloha v dome", so they get a FIXED crop instead of an auto-trim: the polygon
# coordinates in assets/js/floorplan.js are expressed in this cropped space and
# would silently drift if the trim ever landed a pixel differently.
FLOOR_CROP = {
    "1np.png":   (16, 245, 1428, 828),
    "2-5np.png": (30, 262, 1424, 872),
}

JOBS = [
    ("1np.png",           "floor-1np.webp",  2000, 88),
    ("2-5np.png",         "floor-25np.webp", 2000, 88),
    ("2-5np/1np/A1.png",  "flat-1np-A.webp", 1500, 86),
    ("2-5np/A2-4.png",    "flat-24np-A.webp",1500, 86),
    ("2-5np/A5.png",      "flat-5np-A.webp", 1500, 86),
] + [(f"2-5np/1np/{L}.png", f"flat-1np-{L}.webp", 1500, 86) for L in "BCDEFGH"] \
  + [(f"2-5np/{L}.png",     f"flat-25np-{L}.webp",1500, 86) for L in "BCDEFGHI"]

def trim(im, tol=248):
    """Drop the white margin the renders carry, keeping a small even border."""
    g = im.convert("L").point(lambda v: 0 if v < tol else 255)
    bb = g.getbbox() if g.getextrema() == (0, 255) else None
    if not bb:
        return im
    # getbbox() finds non-zero pixels, i.e. the white; invert to find the ink
    from PIL import ImageOps, ImageChops
    bb = ImageChops.invert(g).getbbox()
    if not bb:
        return im
    pad = max(6, int(0.012 * max(im.width, im.height)))
    return im.crop((max(0, bb[0]-pad), max(0, bb[1]-pad),
                    min(im.width, bb[2]+pad), min(im.height, bb[3]+pad)))

os.makedirs(OUT, exist_ok=True)
total = 0
for src, dst, wide, q in JOBS:
    p = os.path.join(SRC, src)
    if not os.path.exists(p):
        print(f"  MISSING  {src}"); continue
    im = Image.open(p)
    bg = Image.new("RGB", im.size, PAGE)
    bg.paste(im, (0, 0), im if im.mode in ("RGBA", "LA") else None)
    im = bg.crop(FLOOR_CROP[src]) if src in FLOOR_CROP else trim(bg)
    if im.width > wide:
        im = im.resize((wide, round(im.height * wide / im.width)), Image.LANCZOS)
    out = os.path.join(OUT, dst)
    im.save(out, "WEBP", quality=q, method=6)
    kb = os.path.getsize(out) / 1024
    total += kb
    print(f"  {dst:20} {im.width}x{im.height}  {kb:6.0f} KB")
print(f"  {'':20} {'':11}  {total:6.0f} KB total")
