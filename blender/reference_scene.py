"""Rebuild the CURRENT world in Blender, at its real three.js transforms, with
the real home + dock cameras. This is the reference the rewrite is judged
against, and the layout new islands are built into.

    blender -b --factory-startup --python blender/reference_scene.py -- <out.blend>

Coordinates: three (x, y, z) == blender (x, -z, y). A three.js transform T is
applied in Blender as C @ T @ C^-1, with C the three->blender basis change.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "src" / "assets"
OUT = Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else ROOT / "blender" / "reference.blend"

# three -> blender basis change
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def three_vec(v):
    x, y, z = v
    return Vector((x, -z, y))


def three_matrix(pos=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    t = Matrix.Translation(Vector(pos))
    r = Euler(rot, "XYZ").to_matrix().to_4x4()  # three default order is XYZ
    s = Matrix.Diagonal((scale, scale, scale, 1))
    return C @ (t @ r @ s) @ C.inverted()


# (glb, three position, three rotation, scale), from src/data/portfolio.ts and
# the model components.
WORLD = [
    ("captain_ship_island-transformed.glb", (0, 0, 0), (0, 0, 0), 1.0),
    ("volcano-island-transformed.glb", (-320, 4, -140), (0, 0.6, 0), 0.009),
    ("treasure-island-transformed.glb", (280, -2, 160), (0, -0.8, 0), 0.65),
    ("fantasy-island-transformed.glb", (180, -7, -300), (0, 2.4, 0), 1.0),
    ("low-poly-island-transformed.glb", (-240, -10, 220), (0, 0.4, 0), 0.08),
]

# name -> (three position, three lookAt, vertical fov)
CAMERAS = {
    "home": ((23.08, 30.52, 150.63), (21.7, 12, 105), 75),
    "projects": ((-210, 55, -30), (-320, 25, -140), 75),
    "resume": ((207.5, 81.54, 243.09), (285.3, 20.9, 153.8), 75),
    "experience": ((195.63, 72.58, -183.81), (182, 35, -286), 75),
    "contact": ((-136.71, 65.57, 244.57), (-240, 40, 220), 75),
}


def import_glb(name, pos, rot, scale):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ASSETS / name))
    new = [o for o in bpy.data.objects if o not in before]
    holder = bpy.data.objects.new(f"REF_{Path(name).stem}", None)
    bpy.context.scene.collection.objects.link(holder)
    holder.matrix_world = three_matrix(pos, rot, scale)
    for o in new:
        if o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = holder
            o.matrix_world = holder.matrix_world @ mw
    return holder, new


def add_camera(name, pos, look, fov):
    cam = bpy.data.cameras.new(f"CAM_{name}")
    cam.sensor_fit = "VERTICAL"
    cam.angle_y = math.radians(fov)
    cam.clip_start, cam.clip_end = 0.1, 4000
    ob = bpy.data.objects.new(f"CAM_{name}", cam)
    bpy.context.scene.collection.objects.link(ob)
    p, l = three_vec(pos), three_vec(look)
    ob.location = p
    ob.rotation_euler = (l - p).to_track_quat("-Z", "Y").to_euler()
    return ob


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    for glb in WORLD:
        import_glb(*glb)
    for name, (pos, look, fov) in CAMERAS.items():
        add_camera(name, pos, look, fov)
    scene.camera = bpy.data.objects["CAM_home"]
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
    print("saved", OUT)


main()
