#!/usr/bin/env python3
"""Extract one apartment's wall geometry from the architect's vector PDF.

The drawing separates cleanly by pen weight: the structural layer (external
walls, party walls, partitions, columns) is stroked at width 0.96, everything
else -- furniture, fittings, door swings, hatching, dimensions -- at 0.24. That
one fact is what makes an exact reconstruction possible; see _build/plans/README.

Output is metres, origin at the apartment's north-west corner, x east, y south.
"""
import json, math, os, sys
import pymupdf

PDF = os.path.join(os.path.dirname(__file__), "..", "plans", "src", "2 az 4 np.pdf")
HEAVY = 0.96

# apartment window in the PDF's display space (X = pdf y, Y = mediabox width - pdf x)
WINDOWS = {"H": (52, 412, 392, 600)}
INTERIOR_M2 = {"H": 69.9}          # from data.js, printed on the drawing


def load_paths(page):
    W = page.mediabox.width
    d = lambda x, y: (y, W - x)
    out = []
    for pa in page.get_drawings():
        if round(pa.get("width") or 0, 2) != HEAVY and pa.get("fill") != (0.0, 0.0, 0.0):
            continue
        poly = []
        for it in pa["items"]:
            if it[0] == "l":
                poly.append((d(it[1].x, it[1].y), d(it[2].x, it[2].y)))
            elif it[0] == "re":
                r = it[1]
                c = [d(r.x0, r.y0), d(r.x1, r.y0), d(r.x1, r.y1), d(r.x0, r.y1)]
                poly += [(c[i], c[(i + 1) % 4]) for i in range(4)]
            elif it[0] == "qu":
                q = it[1]
                c = [d(q.ul.x, q.ul.y), d(q.ur.x, q.ur.y), d(q.lr.x, q.lr.y), d(q.ll.x, q.ll.y)]
                poly += [(c[i], c[(i + 1) % 4]) for i in range(4)]
        if poly:
            out.append(poly)
    return out


def rings_of(path_segments, tol=0.35):
    """Rings from one PDF path, following the order the segments were drawn.

    The points already come out of the PDF in drawing order, so walking them is
    enough. An earlier version re-chained them by nearest endpoint and produced
    self-intersecting polygons that filled as bow-ties.
    """
    rings, cur = [], []
    for a, b in path_segments:
        if not cur:
            cur = [a, b]
        elif math.dist(cur[-1], a) < tol:
            cur.append(b)
        else:
            rings.append(cur); cur = [a, b]
    if cur:
        rings.append(cur)
    out = []
    for r in rings:
        if len(r) >= 3:
            if math.dist(r[0], r[-1]) < tol:
                r = r[:-1]
            out.append(r)
    return out


def dedupe(ring, tol=0.25):
    out = []
    for p in ring:
        if not out or math.dist(out[-1], p) > tol:
            out.append(p)
    return out


if __name__ == "__main__":
    letter = sys.argv[1] if len(sys.argv) > 1 else "H"
    page = pymupdf.open(PDF)[0]
    X0, Y0, X1, Y1 = WINDOWS[letter]
    # Take WHOLE paths that touch the apartment. Clipping segment-by-segment
    # breaks a path mid-run and rings_of() then splits it into 3-point shards,
    # which fill as wedges instead of walls. Party walls legitimately run past
    # the window into the neighbour, so they must be kept entire.
    rings = []
    for segs in load_paths(page):
        touches = any(X0 <= a[0] <= X1 and Y0 <= a[1] <= Y1 for s in segs for a in s)
        if not touches:
            continue
        for r in rings_of(segs):
            r = dedupe(r)
            if len(r) >= 3:
                rings.append(r)
    print(f"flat {letter}: {len(rings)} wall rings")
    json.dump({"letter": letter, "window": [X0, Y0, X1, Y1],
               "rings": [[[round(x, 3), round(y, 3)] for x, y in r] for r in rings]},
              open(os.path.join(os.path.dirname(__file__), f"walls-{letter}.json"), "w"))
