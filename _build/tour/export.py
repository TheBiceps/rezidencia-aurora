#!/usr/bin/env python3
"""Export flat 3.H as .blend and .glb, in metres, ready to hand to anyone.

    blender --background --python _build/tour/export.py

Geometry only, no lighting or camera: the point is that whoever dresses this
starts from the architect's real walls instead of measuring off a picture.
"""
import os, sys

ROOT = "/Users/filipvolarik/Documents/Claude Code/rezidencia/_build/tour"
sys.argv = ["blender", "--"]
src = open(os.path.join(ROOT, "blender_scene.py")).read()
src = src.replace('ROOT = os.path.dirname(os.path.abspath(__file__))', f'ROOT = {ROOT!r}')
src = src.replace("\nmain()\n", "\n")
exec(compile(src, "blender_scene.py", "exec"))

wipe()
mats = build_shell()
furnish(mats)
out = os.path.join(ROOT, "export")
os.makedirs(out, exist_ok=True)
blend = os.path.join(out, "flat-3H.blend")
glb = os.path.join(out, "flat-3H.glb")
bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_apply=True)
n = len(bpy.context.collection.objects)
print(f"EXPORTED {n} objects")
print("  ", blend, f"{os.path.getsize(blend)/1024:.0f} KB")
print("  ", glb, f"{os.path.getsize(glb)/1024:.0f} KB")
