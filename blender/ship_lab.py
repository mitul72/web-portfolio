"""Build the galleon alone and render it on the sea for review.

    blender -b --factory-startup --python blender/ship_lab.py -- <renders-dir> [shot ...]
Shots: three_q (3/4 from the bow), side, deck, stern.
"""
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ship, stage  # noqa: E402

V = Vector
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(args[0]) if args else Path(__file__).resolve().parent / "renders"
SHOTS = args[1:] or ["three_q", "side", "deck", "stern"]

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
ship.galleon(random.Random(7))
stage.sky_and_sun(scene)
stage.water(scene, [], near=200, step=4)
stage.render_settings(scene, 1600, 900)
cams = {
    "three_q": stage.camera(scene, "c1", (38, 52, 9), (0, 2, 9), lens=32),
    "side": stage.camera(scene, "c2", (-62, 4, 7), (0, 3, 11), lens=35),
    "deck": stage.camera(scene, "c3", (9, -22, 13), (0, 6, 5), lens=24),
    "stern": stage.camera(scene, "c4", (-18, -42, 7), (0, -12, 6), lens=35),
}
for s in SHOTS:
    if s in cams:  # pass "none" to just build + save
        stage.render(scene, cams[s], OUT / f"ship_{s}.png")
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).resolve().parent / "ship.blend"))
