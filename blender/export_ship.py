"""Export the approved galleon for the web (it moves, so it's its own GLB).

    blender -b --factory-startup blender/ship.blend --python blender/export_ship.py -- <repo-root>

Writes src/assets/ship.glb (compress with gltf-transform like the world).
Frame: bow toward three -Z, waterline at y = 0, origin on the mainmast.
Parts: SHP_hull, SHP_sail_* (billow), SHP_flag (+ SHP_flag_emblem) (waves).
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_world as X  # noqa: E402  (same bake + material mapping as the world)

scene = bpy.context.scene
X.cycles_gpu()
parts = [o for o in scene.objects if o.name.startswith("SHP_") and o.type == "MESH"]
X.bake_vertex_colors(parts)
X.select_only(parts)
out = X.REPO / "src" / "assets" / "ship.glb"
bpy.ops.export_scene.gltf(filepath=str(out), export_format="GLB", use_selection=True, export_apply=True,
                          export_lights=False, export_cameras=False, export_animations=False, export_yup=True)
X.log("ship ->", out, [o.name for o in parts])
