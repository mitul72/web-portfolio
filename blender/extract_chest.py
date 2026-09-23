"""Lift the original portfolio's animated treasure chest out of its island.

    blender -b --factory-startup --python blender/extract_chest.py -- <treasure-island.glb> <out.glb> <preview.png>

The chest (body, coin heap, loose coins, gems, a staff) is skinned to one
422-bone armature shared with the island's palms, crab, oyster and seaweed,
all driven by a single "Scene" clip (0-160 @ 24 fps: the lid opens, the
coins stir, then it closes again). This keeps only the chest meshes and the
bones that deform them (plus their ancestors), drops every other bone's
animation, rescales it from the old ~3x world to a 2.6 m chest, and puts the
base of the chest at the origin.
"""
import math
import sys

import bpy
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT, PREVIEW = args[0], args[1], args[2] if len(args) > 2 else None
CHEST = {"Object_44", "Object_45", "Object_46", "Object_47", "Object_48", "Object_49"}
WIDTH = 2.6  # metres, lid to lid

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
scene = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
keep = [bpy.data.objects[n] for n in CHEST]

# Bones that actually deform the chest, plus their ancestors.
used = set()
for m in keep:
    names = {g.index: g.name for g in m.vertex_groups}
    for v in m.data.vertices:
        for g in v.groups:
            if g.weight > 1e-4 and g.group in names:
                used.add(names[g.group])
bones = arm.data.bones
needed = set()
for n in used:
    b = bones.get(n)
    while b:
        needed.add(b.name)
        b = b.parent
print("[chest] deforming bones:", len(used), "kept incl. ancestors:", len(needed), "of", len(bones))

# Drop every other object (keep the armature and the chest meshes).
for o in list(bpy.data.objects):
    if o is not arm and o not in keep:
        bpy.data.objects.remove(o, do_unlink=True)

# Delete unneeded bones.
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
for eb in list(arm.data.edit_bones):
    if eb.name not in needed:
        arm.data.edit_bones.remove(eb)
bpy.ops.object.mode_set(mode="OBJECT")

# Drop animation curves for bones that no longer exist.
def fcurves(action):
    if hasattr(action, "fcurves") and len(action.fcurves):
        return action.fcurves
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out

for act in bpy.data.actions:
    for fc in list(fcurves(act)):
        path = fc.data_path
        if path.startswith('pose.bones["'):
            name = path.split('"')[1]
            if name not in needed:
                try:
                    act.fcurves.remove(fc)
                except Exception:  # noqa: BLE001  (layered actions)
                    for layer in act.layers:
                        for strip in layer.strips:
                            for bag in strip.channelbags:
                                if fc in list(bag.fcurves):
                                    bag.fcurves.remove(fc)

# Scale + recentre: base-centre of the chest (at rest, frame 0) to the origin.
scene.frame_set(0)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for m in keep:
    ev = m.evaluated_get(dg)
    pts += [m.matrix_world @ Vector(c) for c in ev.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
size = hi - lo
s = WIDTH / max(size.x, size.y)
base = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
holder = bpy.data.objects.new("ChestRoot", None)
scene.collection.objects.link(holder)
for o in [arm] + [m for m in keep if m.parent is None]:
    o.parent = holder
holder.matrix_world = Matrix.Diagonal((s, s, s, 1)) @ Matrix.Translation(-base)
print("[chest] native size", tuple(round(x, 2) for x in size), "scale", round(s, 4))

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_animations=True,
                          export_apply=False, export_yup=True)
print("[chest] ->", OUT)

if PREVIEW:
    # front/back check: render from -Y and +Y at frame 0 (closed) and 60 (open)
    w = bpy.data.worlds.new("W")
    scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.65, 0.7, 1)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    scene.collection.objects.link(sun)
    sun.rotation_euler = (0.8, 0.2, 0.5)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 640, 480
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    import os
    stem, ext = os.path.splitext(PREVIEW)
    for label, pos, frame in (("minusY_closed", (0, -6, 2.5), 0), ("minusY_open", (0, -6, 2.5), 60),
                              ("plusY_open", (0, 6, 2.5), 60)):
        scene.frame_set(frame)
        cam.location = pos
        cam.rotation_euler = (Vector((0, 0, 0.9)) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = f"{stem}_{label}{ext}"
        bpy.ops.render.render(write_still=True)
