#!/usr/bin/env python3
"""Route the walkthrough camera through flat H.

Hand-picked waypoints kept landing the camera inside a partition or facing a
blank return, so the path is solved instead: rasterise the space a body can
actually stand in (floor polygon minus walls, minus a clearance radius), then
A* between the room centres. Whatever comes out is guaranteed walkable.
"""
import heapq, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "..", "..", "assets", "tour", "flat-H.json")
CLEAR = 0.26          # metres of shoulder room; the narrowest door is 0,78 m
RES = 0.06            # grid pitch

M = json.load(open(MODEL))
FLOOR, WALLS = M["floor"][0], M["walls"]
W, D = M["size"]


def inside(ring, x, y):
    h = False
    n = len(ring)
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[i - 1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            h = not h
    return h


def solid(x, y):
    if not inside(FLOOR, x, y):
        return True
    return any(inside(w, x, y) for w in WALLS)


NX, NY = int(W / RES), int(D / RES)
raw = [[solid(i * RES, j * RES) for i in range(NX)] for j in range(NY)]

# erode by the clearance radius so the camera keeps its shoulders off the walls
R = int(round(CLEAR / RES))
free = [[False] * NX for _ in range(NY)]
for j in range(NY):
    for i in range(NX):
        if raw[j][i]:
            continue
        ok = True
        for dj in range(-R, R + 1):
            for di in range(-R, R + 1):
                if di * di + dj * dj > R * R:
                    continue
                jj, ii = j + dj, i + di
                if not (0 <= jj < NY and 0 <= ii < NX) or raw[jj][ii]:
                    ok = False
                    break
            if not ok:
                break
        free[j][i] = ok


def nearest_free(x, y):
    i0, j0 = int(x / RES), int(y / RES)
    best, bd = None, 1e9
    for j in range(NY):
        for i in range(NX):
            if not free[j][i]:
                continue
            d = (i - i0) ** 2 + (j - j0) ** 2
            if d < bd:
                bd, best = d, (i, j)
    return best


# Distance to the nearest obstacle, so the route can prefer the middle of a
# room. A plain shortest path hugs every corner, which on camera means a wall
# filling half the frame for most of the walk.
CLEARANCE = [[0.0] * NX for _ in range(NY)]
for j in range(NY):
    for i in range(NX):
        if not free[j][i]:
            continue
        r = 1
        while r < 40:
            hit = False
            for dj in range(-r, r + 1):
                for di in (-r, r):
                    jj, ii = j + dj, i + di
                    if not (0 <= jj < NY and 0 <= ii < NX) or raw[jj][ii]:
                        hit = True; break
                if hit: break
            if not hit:
                for di in range(-r, r + 1):
                    for dj in (-r, r):
                        jj, ii = j + dj, i + di
                        if not (0 <= jj < NY and 0 <= ii < NX) or raw[jj][ii]:
                            hit = True; break
                    if hit: break
            if hit:
                break
            r += 1
        CLEARANCE[j][i] = r * RES
MAXC = max(max(r) for r in CLEARANCE) or 1.0


def openness_cost(i, j):
    """Cheap in the open, dear against a wall."""
    return 1.0 + 2.6 * (1.0 - min(CLEARANCE[j][i], 1.5) / 1.5)


def astar(a, b):
    sx, sy = a
    gx, gy = b
    h = lambda i, j: math.hypot(i - gx, j - gy)
    openq = [(h(sx, sy), 0.0, (sx, sy))]
    came, gsc = {}, {(sx, sy): 0.0}
    while openq:
        _, g, cur = heapq.heappop(openq)
        if cur == (gx, gy):
            out = [cur]
            while out[-1] in came:
                out.append(came[out[-1]])
            return out[::-1]
        ci, cj = cur
        for di, dj in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            ni, nj = ci + di, cj + dj
            if not (0 <= ni < NX and 0 <= nj < NY) or not free[nj][ni]:
                continue
            ng = g + math.hypot(di, dj) * openness_cost(ni, nj)
            if ng < gsc.get((ni, nj), 1e18):
                gsc[(ni, nj)] = ng
                came[(ni, nj)] = cur
                heapq.heappush(openq, (ng + h(ni, nj), ng, (ni, nj)))
    return []


def simplify(pix, tol=0.16):
    """Drop points that sit close to the straight line between their neighbours."""
    pts = [(i * RES, j * RES) for i, j in pix]
    out = [pts[0]]
    for p in pts[1:-1]:
        a, b = out[-1], pts[-1]
        num = abs((b[0]-a[0])*(a[1]-p[1]) - (a[0]-p[0])*(b[1]-a[1]))
        den = math.hypot(b[0]-a[0], b[1]-a[1]) or 1
        if num / den > tol or math.dist(out[-1], p) > 1.4:
            out.append(p)
    out.append(pts[-1])
    return out


# the tour: in the front door, both bedrooms, then the length of the living room
STOPS = [(10.15, 1.05), (11.15, 4.30), (10.15, 1.60),
         (7.95, 4.40), (6.10, 1.35), (3.20, 3.00), (1.50, 4.55)]

path = []
for a, b in zip(STOPS, STOPS[1:]):
    seg = astar(nearest_free(*a), nearest_free(*b))
    if not seg:
        raise SystemExit(f"no route {a} -> {b}")
    path += seg if not path else seg[1:]

pts = simplify(path)
print(f"free cells {sum(sum(r) for r in free)} of {NX*NY}")
print(f"route {len(path)} cells -> {len(pts)} waypoints")
print("WAY = [" + ", ".join(f"({x:.2f}, {y:.2f})" for x, y in pts) + "]")
json.dump([[round(x, 3), round(y, 3)] for x, y in pts],
          open(os.path.join(HERE, "path-H.json"), "w"))
