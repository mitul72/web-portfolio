"""Close-up test of the outpost kit.
    blender -b --factory-startup --python blender/buildlab.py -- <out.png>"""
import random, sys
from pathlib import Path
import bpy
from mathutils import Vector as V
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import build, stage, materials  # noqa
OUT = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
rnd = random.Random(5)
h1 = build.house("h1", rnd, w=7, d=5.5, h=3.0, floors=2, paint=0.3)
h2 = build.house("h2", rnd, w=5, d=4.5, h=3.0, stilts=2.0, paint=0.8)
h2.location = (9, 3, 0)
h2.rotation_euler.z = -0.4
p = build.pier("p", rnd, (-4, 8), (-4, 30), deck_z=1.0)
bpy.ops.mesh.primitive_plane_add(size=200)
g = bpy.context.object
g.data.materials.append(materials.terrain())
g.location.z = 0.0
stage.sky_and_sun(s)
stage.render_settings(s, 1280, 720)
cam = stage.camera(s, "c", (14, 22, 5), (0, 2, 3), lens=28)
stage.render(s, cam, OUT)
