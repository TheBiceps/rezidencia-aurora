#!/usr/bin/env python3
"""Build flat 3.H in Blender from the reconstructed model and render a walkthrough.

Run headless:
    blender --background --python _build/tour/blender_scene.py -- --still
    blender --background --python _build/tour/blender_scene.py -- --frames 336

The architecture is NOT modelled by hand and NOT generated. Walls, their
thicknesses, and the door openings all come from assets/tour/flat-H.json, which
_build/tour/build_model.py reconstructs from the architect's vector PDF. The
only invented things in here are finishes, light and furniture massing; the
geometry you can walk into is the architect's.

Model space is the plan: x east, y south, metres. Blender is z-up, so plan y
maps to -y and heights go up z.
"""
import json, math, os, sys

import bpy, bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(ROOT, "..", "..", "assets", "tour", "flat-H.json")
OUT = os.path.join(ROOT, "render")

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
STILL = "--still" in argv
OVERVIEW = "--overview" in argv
FRAMES = 336
if "--frames" in argv:
    FRAMES = int(argv[argv.index("--frames") + 1])
RES = (1920, 1080)
SAMPLES = 96

M = json.load(open(MODEL))
CH = M["ceiling"]
PLAN_W, PLAN_D = M["size"]


# --------------------------------------------------------------------------- #
# scene helpers
# --------------------------------------------------------------------------- #

def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, base, rough=0.6, metal=0.0, spec=0.5, alpha=1.0, transmission=0.0,
        emit=None, emit_strength=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    def put(key, val):
        if key in b.inputs:
            b.inputs[key].default_value = val
    put("Base Color", (*base, 1.0))
    put("Roughness", rough)
    put("Metallic", metal)
    put("IOR Level", spec)
    put("Specular IOR Level", spec)
    put("Transmission Weight", transmission)
    if emit:
        put("Emission Color", (*emit, 1.0))
        put("Emission Strength", emit_strength)
    if alpha < 1.0:
        put("Alpha", alpha)
        m.blend_method = "BLEND" if hasattr(m, "blend_method") else m.blend_method
    return m


def solid(name, ring, z0, z1, material):
    """Extrude a plan ring between two heights into a closed solid."""
    pts = [Vector((x, -y, 0.0)) for x, y in ring]
    if len(pts) < 3:
        return None
    tris = tessellate_polygon([pts])
    n = len(pts)
    verts = [(p.x, p.y, z0) for p in pts] + [(p.x, p.y, z1) for p in pts]
    faces = []
    for a, b, c in tris:
        faces.append([a, b, c])                       # floor cap
        faces.append([c + n, b + n, a + n])           # ceiling cap
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, j + n, i + n])            # side
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(material)
    bpy.context.collection.objects.link(ob)

    # outward normals, and a shallow bevel so edges catch light like real ones
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    return ob


def box(name, cx, cy, w, d, z0, z1, material, rot=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, -cy, (z0 + z1) / 2))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (w, d, z1 - z0)
    ob.rotation_euler[2] = rot
    ob.data.materials.append(material)
    return ob


# --------------------------------------------------------------------------- #
# the apartment
# --------------------------------------------------------------------------- #

def wood_floor():
    """Oak boards: a stretched noise drives both colour and roughness."""
    m = bpy.data.materials.new("oak")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 9.0
    tex.inputs["Detail"].default_value = 6.0
    map_ = nt.nodes.new("ShaderNodeMapping")
    map_.inputs["Scale"].default_value = (1.0, 26.0, 1.0)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.26, 0.145, 0.062, 1)
    ramp.color_ramp.elements[1].color = (0.44, 0.28, 0.145, 1)
    nt.links.new(coord.outputs["Object"], map_.inputs["Vector"])
    nt.links.new(map_.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.34
    return m


def build_shell():
    oak = wood_floor()
    wall = mat("wall", (0.80, 0.77, 0.72), rough=0.9)
    ceil = mat("ceiling", (0.86, 0.85, 0.83), rough=0.95)
    glass = mat("glass", (0.92, 0.95, 0.96), rough=0.04, transmission=0.0, alpha=0.10)
    frame = mat("frame", (0.11, 0.11, 0.10), rough=0.45, metal=0.6)

    for i, ring in enumerate(M["floor"]):
        solid(f"floor{i}", ring, -0.05, 0.0, oak)
        solid(f"ceil{i}", ring, CH, CH + 0.12, ceil)
    for i, ring in enumerate(M["walls"]):
        solid(f"wall{i}", ring, 0.0, CH, wall)

    # headers over the door openings: the plan gives the hole, not the lintel
    for i, o in enumerate(M["openings"]):
        if o["kind"] != "door":
            continue
        solid(f"lintel{i}", o["ring"], o["head"], CH, wall)

    # The terrace facade sits exactly on the model's south edge, so it is not in
    # the reconstructed window. The columns along it are, though -- glaze the
    # bays between them, full height, which is how the building is drawn.
    cols = []
    for ring in M["walls"]:
        ys = [p[1] for p in ring]; xs = [p[0] for p in ring]
        if max(ys) > PLAN_D - 0.45 and (max(xs) - min(xs)) < 2.2:
            cols.append((min(xs), max(xs)))
    cols.sort()
    edges = [0.0] + [v for c in cols for v in c] + [PLAN_W]
    y = PLAN_D - 0.10
    for k in range(0, len(edges) - 1, 2):
        x0, x1 = edges[k], edges[k + 1]
        if x1 - x0 < 0.5:
            continue
        box(f"glaz{k}", (x0 + x1) / 2, y, x1 - x0, 0.06, 0.02, CH - 0.02, glass)
        box(f"gsill{k}", (x0 + x1) / 2, y, x1 - x0, 0.10, 0.0, 0.02, frame)
        box(f"ghead{k}", (x0 + x1) / 2, y, x1 - x0, 0.10, CH - 0.02, CH, frame)

    return dict(oak=oak, wall=wall, glass=glass, frame=frame)


def furnish(mats):
    """Indicative massing, placed on the architect's own layout.

    Deliberately simple: the point of the render is the apartment, and invented
    furniture that looks photographic would quietly imply a fit-out that is not
    part of the sale.
    """
    linen = mat("linen", (0.80, 0.78, 0.73), rough=0.9)
    wood = mat("wood", (0.48, 0.33, 0.19), rough=0.5)
    dark = mat("darkwood", (0.24, 0.17, 0.11), rough=0.55)
    sage = mat("sage", (0.55, 0.60, 0.52), rough=0.9)
    stone = mat("stone", (0.72, 0.70, 0.67), rough=0.35)

    # --- living / kitchen, the open west half -----------------------------
    box("kitchen_run", 2.6, 0.45, 4.6, 0.65, 0.0, 0.90, stone)
    box("kitchen_upper", 2.6, 0.30, 3.6, 0.35, 1.45, 2.10, mats["wall"])
    box("sofa_base", 2.4, 3.30, 2.30, 0.95, 0.0, 0.42, linen)
    box("sofa_back", 2.4, 3.72, 2.30, 0.22, 0.42, 0.78, linen)
    box("sofa_armL", 1.30, 3.30, 0.22, 0.95, 0.42, 0.62, linen)
    box("sofa_armR", 3.50, 3.30, 0.22, 0.95, 0.42, 0.62, linen)
    box("rug", 2.6, 2.60, 3.20, 2.20, -0.005, 0.012, sage)
    box("coffee", 2.6, 2.35, 1.10, 0.55, 0.30, 0.38, wood)
    box("dining_top", 1.70, 5.00, 1.40, 0.90, 0.72, 0.78, wood)
    for dx, dy in ((-0.55, -0.55), (0.55, -0.55), (-0.55, 0.55), (0.55, 0.55)):
        box(f"chair{dx}{dy}", 1.70 + dx, 5.00 + dy, 0.42, 0.42, 0.0, 0.45, dark)

    # --- bedroom 1 (x 6.7..9.2) --------------------------------------------
    box("bed1", 7.95, 4.10, 1.60, 2.00, 0.10, 0.55, linen)
    box("bed1_head", 7.95, 3.02, 1.70, 0.14, 0.10, 0.95, dark)
    box("wardrobe1", 6.95, 5.40, 0.60, 1.10, 0.0, 2.20, mats["wall"])

    # --- bedroom 2 (x 9.5..12.8) -------------------------------------------
    box("bed2", 11.20, 4.30, 1.60, 2.00, 0.10, 0.55, linen)
    box("bed2_head", 11.20, 3.22, 1.70, 0.14, 0.10, 0.95, dark)
    box("wardrobe2", 12.40, 4.60, 0.60, 1.60, 0.0, 2.20, mats["wall"])

    # --- entrance hall ------------------------------------------------------
    box("console", 11.90, 0.60, 1.00, 0.35, 0.0, 0.80, wood)


def light():
    """Daylight, not lamps. The flat is glazed along its whole south side, so a
    sky plus a low sun through that wall is what actually lights it."""
    world = bpy.data.worlds.new("sky")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    # Blender 5 renamed the Nishita model; take whichever multi-scattering
    # variant this build offers rather than pinning a name that moves.
    kinds = [e.identifier for e in sky.bl_rna.properties["sky_type"].enum_items]
    for want in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
        if want in kinds:
            sky.sky_type = want
            break
    for attr, val in (("sun_elevation", math.radians(26)),
                      ("sun_rotation", math.radians(196)),   # low, south-west
                      ("altitude", 15.0),
                      ("air_density", 1.1),
                      ("dust_density", 1.6)):
        if hasattr(sky, attr):
            setattr(sky, attr, val)
    nt.links.new(sky.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = 1.0

    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 6.0
    sun.angle = math.radians(1.6)
    sun.color = (1.0, 0.93, 0.82)
    ob = bpy.data.objects.new("sun", sun)
    bpy.context.collection.objects.link(ob)
    ob.location = (PLAN_W * 0.75, -PLAN_D - 12.0, 8.0)
    d = Vector((PLAN_W * 0.30, -PLAN_D * 0.45, 0.9)) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def context():
    """Terrace and ground, so the glazing looks out at something."""
    paving = mat("paving", (0.55, 0.53, 0.50), rough=0.75)
    grass = mat("ground", (0.30, 0.33, 0.26), rough=0.95)
    box("terrace", PLAN_W / 2, PLAN_D + 1.6, PLAN_W + 1.0, 3.4, -0.06, 0.0, paving)
    box("ground", PLAN_W / 2, PLAN_D + 40, 260, 80, -0.30, -0.24, grass)
    # a parapet, so the terrace reads as a terrace and not a cliff
    box("parapet", PLAN_W / 2, PLAN_D + 3.2, PLAN_W + 1.0, 0.12, 0.0, 1.05, paving)


# --------------------------------------------------------------------------- #
# camera: a walk from the front door through every room to the terrace
# --------------------------------------------------------------------------- #

WAY = json.load(open(os.path.join(ROOT, "path-H.json")))   # solved by path.py
EYE = 1.58


def resample(pts, n):
    """Constant-speed samples along the polyline, eased at both ends."""
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg)
    acc, out = [0.0], 0.0
    for d in seg:
        acc.append(acc[-1] + d)
    res = []
    for k in range(n):
        t = k / max(n - 1, 1)
        te = t * t * (3 - 2 * t)                    # ease in and out
        want = te * total
        i = 0
        while i < len(seg) and acc[i + 1] < want:
            i += 1
        i = min(i, len(seg) - 1)
        f = (want - acc[i]) / (seg[i] or 1)
        res.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f,
                    pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f))
    return res


def smooth_headings(pos, look=9, win=13):
    """Heading from a look-ahead, then low-passed.

    Taking the raw tangent makes the camera snap through 180 degrees where the
    route doubles back out of a bedroom; averaging as a unit vector turns that
    into a normal turn of the head.
    """
    n = len(pos)
    raw = []
    for i in range(n):
        j = min(i + look, n - 1)
        dx, dy = pos[j][0] - pos[i][0], pos[j][1] - pos[i][1]
        if dx == dy == 0:
            dx, dy = raw[-1] if raw else (1.0, 0.0)
        raw.append((dx, dy))
    out = []
    for i in range(n):
        sx = sy = 0.0
        for k in range(max(0, i - win), min(n, i + win + 1)):
            L = math.hypot(*raw[k]) or 1
            sx += raw[k][0] / L
            sy += raw[k][1] / L
        L = math.hypot(sx, sy) or 1
        out.append((sx / L, sy / L))
    return out


def look_at(cam, eye, target):
    cam.location = eye
    d = Vector(target) - Vector(eye)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(frames, overview=False):
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 24.0                 # wide, the way interiors are shot
    cam_data.sensor_width = 36.0
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    if overview:
        cam_data.lens = 28.0
        look_at(cam, (PLAN_W * 0.5, -PLAN_D * 0.5 - 9.0, 11.0),
                     (PLAN_W * 0.5, -PLAN_D * 0.55, 0.6))
        bpy.context.scene.frame_start = bpy.context.scene.frame_end = 1
        return cam

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = frames
    pos = resample(WAY, frames)
    head = smooth_headings(pos)
    for f in range(1, frames + 1):
        (x, y), (hx, hy) = pos[f - 1], head[f - 1]
        look_at(cam, (x, -y, EYE), (x + hx * 3.0, -(y + hy * 3.0), EYE - 0.14))
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    return cam


def render(still):
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = (d.type == "METAL")
        s.cycles.device = "GPU"
    except Exception as e:                       # CPU still works, just slower
        print("GPU unavailable, falling back to CPU:", e)
        s.cycles.device = "CPU"
    s.cycles.samples = SAMPLES
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 5
    s.cycles.diffuse_bounces = 4
    s.cycles.glossy_bounces = 4
    s.cycles.transmission_bounces = 2
    s.cycles.use_fast_gi = True
    s.render.resolution_x, s.render.resolution_y = RES
    s.render.resolution_percentage = 100
    s.render.film_transparent = False
    s.view_settings.view_transform = "AgX"
    s.view_settings.look = "AgX - Base Contrast"
    s.render.image_settings.file_format = "PNG"
    os.makedirs(OUT, exist_ok=True)
    if still:
        s.frame_set(1)
        s.render.filepath = os.path.join(OUT, "overview.png" if OVERVIEW else "still.png")
        bpy.ops.render.render(write_still=True)
    else:
        s.render.filepath = os.path.join(OUT, "frame_")
        bpy.ops.render.render(animation=True)


def main():
    wipe()
    mats = build_shell()
    furnish(mats)
    light()
    context()
    n = len(bpy.context.collection.objects)
    glaz = sum(1 for o in bpy.context.collection.objects if o.name.startswith("glaz"))
    print(f"built: {n} objects, {glaz} glazed bays")
    camera(1 if (STILL or OVERVIEW) else FRAMES, overview=OVERVIEW)
    render(STILL or OVERVIEW)
    print("done")


main()
