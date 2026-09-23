"""NPCs: Quaternius "Pirate Kit" characters (CC0, rigged, 14 shared
animations), imported from blender/sources/pirate_kit and placed on the
islands, posed from a real animation frame for review renders.

The app loads each character's glTF itself (skinned + animated), so these are
placements only: position, facing, and scale, recorded in NPC_PLACEMENTS and
written out by export_world.py.
"""
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

V = Vector
SOURCES = Path(__file__).resolve().parent.parent / "sources" / "pirate_kit"
HEIGHT = 1.8  # metres, a person

# key -> dict(file, position (blender), yaw (rad about +Z, 0 = facing -Y), scale)
NPC_PLACEMENTS = {}


def place(scene, key, file, at, face_to, pose="Idle", frame=12):
    before_obs = set(bpy.data.objects)
    before_actions = set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(SOURCES / file))
    new = [o for o in bpy.data.objects if o not in before_obs]
    # Each kit character carries a helper "Icosphere" bigger than the body;
    # it isn't part of the character (the app hides it too).
    for o in [o for o in new if o.type == "MESH" and o.name.startswith("Icosphere")]:
        new.remove(o)
        bpy.data.objects.remove(o, do_unlink=True)
    actions = [a for a in bpy.data.actions if a not in before_actions]
    roots = [o for o in new if o.parent is None]
    holder = bpy.data.objects.new(f"NPC_{key}", None)
    scene.collection.objects.link(holder)
    for r in roots:
        r.parent = holder

    # pose: the chosen animation, one frame in
    arm = next((o for o in new if o.type == "ARMATURE"), None)
    act = next((a for a in actions if a.name.split(".")[0].endswith(pose) or a.name.startswith(pose)), None)
    if arm and act:
        arm.animation_data_create()
        if arm.animation_data.nla_tracks:
            for t in list(arm.animation_data.nla_tracks):
                arm.animation_data.nla_tracks.remove(t)
        arm.animation_data.action = act
        if hasattr(arm.animation_data, "action_slot") and getattr(act, "slots", None):
            arm.animation_data.action_slot = act.slots[0]
    scene.frame_set(frame)

    # native size -> a 1.8 m person, feet on the ground, facing the camera
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == "MESH"]
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for m in meshes:
        ev = m.evaluated_get(dg)
        pts += [m.matrix_world @ V(c) for c in ev.bound_box]
    h = max(p.z for p in pts) - min(p.z for p in pts)
    s = HEIGHT / h if h > 0 else 1.0
    d = V((face_to[0] - at.x, face_to[1] - at.y, 0)).normalized()
    # The kit characters face -Y after import (verified by render); turn
    # that onto d, the same convention as the props.
    yaw = math.atan2(d.x, -d.y)
    holder.matrix_world = Matrix.Translation(at) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Diagonal((s, s, s, 1))
    NPC_PLACEMENTS[key] = {"file": file, "position": tuple(at), "yaw": yaw, "scale": s}
    return holder
