#!/usr/bin/env python3
"""Build a 3D model of one apartment from the architect's vector PDF.

WHY THIS EXISTS
Generative video cannot be faithful to a floor plan -- it synthesises pixels and
has no model of the building, so it invents rooms, windows and doors. The only
way to show *this* apartment is to reconstruct it and move a camera through it.

HOW IT WORKS
The drawing separates by pen weight: the structural layer (external walls, party
walls, partitions, columns) is stroked at 0.96, everything else -- furniture,
fittings, door swings, hatching -- at 0.24. Stroking only the structural layer
and flood-filling from outside recovers the wall *bodies*: the thin enclosed
slivers between each pair of wall faces, with correct thickness and with door
reveals already cut out.

SCALE
The PDF carries no dimensions or scale bar, only room codes and areas. The scale
is therefore solved from the printed areas: the enclosed interior of flat H is
69,9 m2 by the drawing, which fixes 24,7 PDF units per metre. Cross-check at
that scale, after separating rooms: living+kitchen+hall 43,1 m2 (printed 43,0),
bedrooms 11,2 and 10,6 (printed 10,7 and 10,0), store 2,3 (printed 2,2).

CEILING HEIGHT IS THE ONE ASSUMPTION. A plan cannot carry it and the architect's
notes do not state it; 2,65 m clear is the normal Slovak residential figure.
Everything else in this file is measured.
"""
import json, os
import numpy as np, cv2, pymupdf

HERE = os.path.dirname(__file__)
PDF = os.path.join(HERE, "..", "plans", "src", "2 az 4 np.pdf")
OUT = os.path.join(HERE, "..", "..", "assets", "tour")

HEAVY = 0.96
UNITS_PER_M = 24.71          # solved from the printed interior areas
CEILING_M = 2.65             # assumed - see module docstring
S = 8                        # raster px per PDF unit

FLATS = {
    # letter: (interior window in PDF display space, terrace band, interior m2)
    "H": dict(win=(55, 443, 381, 592), terrace=(60, 592, 376, 616), m2=69.9),
}


def structural_segments(page):
    W = page.mediabox.width
    d = lambda x, y: (y, W - x)
    segs = []
    for pa in page.get_drawings():
        if round(pa.get("width") or 0, 2) != HEAVY and pa.get("fill") != (0.0, 0.0, 0.0):
            continue
        for it in pa["items"]:
            if it[0] == "l":
                segs.append((d(it[1].x, it[1].y), d(it[2].x, it[2].y)))
            elif it[0] == "re":
                r = it[1]
                c = [d(r.x0, r.y0), d(r.x1, r.y0), d(r.x1, r.y1), d(r.x0, r.y1)]
                segs += [(c[i], c[(i + 1) % 4]) for i in range(4)]
            elif it[0] == "qu":
                q = it[1]
                c = [d(q.ul.x, q.ul.y), d(q.ur.x, q.ur.y), d(q.lr.x, q.lr.y), d(q.ll.x, q.ll.y)]
                segs += [(c[i], c[(i + 1) % 4]) for i in range(4)]
    return segs


def rasterise(segs, win, pad=6):
    X0, Y0, X1, Y1 = win
    w, h = int((X1 - X0) * S) + 2 * pad, int((Y1 - Y0) * S) + 2 * pad
    tx = lambda P: (int(round((P[0] - X0) * S)) + pad, int(round((P[1] - Y0) * S)) + pad)
    img = np.zeros((h, w), np.uint8)
    for a, b in segs:
        cv2.line(img, tx(a), tx(b), 255, 2)
    return img, pad


def wall_bodies(outline, pad):
    """Enclosed slivers between paired wall faces = the walls themselves."""
    ff = outline.copy()
    m = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, m, (0, 0), 128)
    body = ((ff == 0) | (outline > 0)).astype(np.uint8) * 255
    return cv2.morphologyEx(body, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))


def contours_to_m(mask, win, pad, min_px=400, eps_px=2.5):
    X0, Y0, _, _ = win
    cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < min_px:
            continue
        c = cv2.approxPolyDP(c, eps_px, True)
        ring = [[round((float(x) - pad) / S / UNITS_PER_M, 4),
                 round((float(y) - pad) / S / UNITS_PER_M, 4)] for [[x, y]] in c]
        if len(ring) >= 3:
            out.append(ring)
    return out


def build(letter):
    page = pymupdf.open(PDF)[0]
    segs = structural_segments(page)
    cfg = FLATS[letter]
    win = cfg["win"]

    outline, pad = rasterise(segs, win)
    body = wall_bodies(outline, pad)

    # interior = everything the walls enclose, once the cut envelope is sealed
    sealed = body.copy()
    cv2.rectangle(sealed, (0, 0), (sealed.shape[1] - 1, sealed.shape[0] - 1), 255, pad * 2)
    n, lab, st, _ = cv2.connectedComponentsWithStats((sealed == 0).astype(np.uint8), 4)
    k = max(range(1, n), key=lambda i: st[i, cv2.CC_STAT_AREA])
    interior = (lab == k).astype(np.uint8) * 255
    area_m2 = st[k, cv2.CC_STAT_AREA] / (S * UNITS_PER_M) ** 2

    walls = contours_to_m(body, win, pad)
    floor = contours_to_m(interior, win, pad, min_px=2000, eps_px=2.0)

    X0, Y0, X1, Y1 = win
    model = {
        "flat": letter,
        "source": "architect PDF '2 az 4 np.pdf', structural layer (pen 0.96)",
        "unitsPerMetre": UNITS_PER_M,
        "ceiling": CEILING_M,
        "ceilingIsAssumed": True,
        "interiorM2": round(area_m2, 1),
        "interiorM2Printed": cfg["m2"],
        "size": [round((X1 - X0) / UNITS_PER_M, 3), round((Y1 - Y0) / UNITS_PER_M, 3)],
        "walls": walls,
        "floor": floor,
    }
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"flat-{letter}.json")
    json.dump(model, open(path, "w"), separators=(",", ":"))
    print(f"flat {letter}: {len(walls)} wall shapes, {len(floor)} floor ring(s)")
    print(f"  interior {area_m2:.1f} m2 (drawing says {cfg['m2']}) "
          f"-- {abs(area_m2 - cfg['m2']) / cfg['m2'] * 100:.1f}% off")
    print(f"  envelope {model['size'][0]:.2f} x {model['size'][1]:.2f} m")
    print(f"  -> {path}  ({os.path.getsize(path) / 1024:.0f} KB)")


if __name__ == "__main__":
    build("H")
