"""Check docks, routes and arrival cameras for src/data/anchors.ts against the
real terrain, with a stand-in of the real ship placed exactly as the app
places it (FloatingVessel + pirate-island.tsx transforms).

    blender -b --factory-startup blender/world.blend --python blender/dock_check.py -- <renders-dir>

All positions here are THREE.JS coordinates, like anchors.ts; the script
converts. Prints hull clearance and route collisions, renders dock_<id>.png.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

V = Vector
ROOT = Path(__file__).resolve().parent
OUT = Path(sys.argv[sys.argv.index("--") + 1])
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))  # three -> blender

# id: (dock xz, heading, via xz, camera pos, camera lookAt) -- three.js coords
DOCKS = {
    "intro": ((21.5, 106), math.pi, (21.5, 150), (62, 14, 148), (8, 16, 40)),
    "project-1": ((-181.2, -109.9), -1.844, (-190, 110), (-150, 16, 0), (-270, 26, -120)),
    "resume": ((252.4, 241.6), 0.864, (88, 117), (182.5, 9, 274), (280, 16, 160)),
    "experience": ((166, -222), math.pi, (175, 40), (237, 14, -120), (180, 24, -300)),
    "contact": ((-190, 290), math.pi / 2, (-90, 160), (-170, 24, 370), (-240, 28, 220)),
}
# The rebuilt galleon (blender/lib/ship.py): bow at +17 m, stern walk at
# -16.6 m from the mainmast origin, 5.6 m half-beam at the waterline.
BEAM_HALF, LENGTH_FWD, LENGTH_AFT = 5.8, 17.5, 16.8


def three_to_blender(v):
    x, y, z = v
    return V((x, -z, y))


def ship_matrix(x, z, heading):
    """Blender matrix for the ship, mirroring the app's scene graph: the
    vessel yaws heading + pi/2 and the ship model inside it another pi/2 (its
    bow is three -Z), so the bow points along the travel direction."""
    t = Matrix.Translation((x, 0, z)) @ Matrix.Rotation(heading + math.pi, 4, "Y")
    return C @ t @ C.inverted()


def land_objects():
    return [bpy.data.objects[n] for n in bpy.context.scene["land"]]


def ground_below(x_b, y_b, land):
    """Highest land surface under a Blender XY point (or -99)."""
    best = -99.0
    for ob in land:
        ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        inv = ob.matrix_world.inverted()
        ok, loc, _, _ = ev.ray_cast(inv @ V((x_b, y_b, 300)), V((0, 0, -1)))
        if ok:
            best = max(best, (ob.matrix_world @ loc).z)
    return best


def hull_points(x, z, heading):
    fwd = V((math.sin(heading), math.cos(heading)))  # travel direction in three xz
    side = V((fwd.y, -fwd.x))
    pts = []
    for a in (-LENGTH_AFT, 0, LENGTH_FWD):
        for s in (-BEAM_HALF, 0, BEAM_HALF):
            p = V((x, z)) + fwd * a + side * s
            pts.append(p)
    return pts


def catmull(points, n=200):
    pts = [points[0]] + points + [points[-1]]
    out = []
    segs = len(points) - 1
    for i in range(n + 1):
        u = i / n * segs
        k = min(int(u), segs - 1)
        t = u - k
        p0, p1, p2, p3 = (V(p) for p in pts[k:k + 4])
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return out


def main():
    scene = bpy.context.scene
    land = land_objects()
    # the new ship is already in world.blend (moored at home for reviews);
    # gather its parts under one empty and move that around
    ship = bpy.data.objects.new("CHK_ship", None)
    scene.collection.objects.link(ship)
    for o in [o for o in scene.objects if o.name.startswith("SHP_") and o.parent is None]:
        o.location = (0, 0, 0)
        o.parent = ship

    home = DOCKS["intro"]
    for sid, (dock, heading, via, cpos, clook) in DOCKS.items():
        # hull clearance: land height under 9 points of the hull footprint
        worst = max(ground_below(p.x, -p.y, land) for p in hull_points(dock[0], dock[1], heading))
        print(f"[dock] {sid:11s} highest ground under hull: {worst:6.1f} m {'OK' if worst < -1.0 else 'AGROUND'}")
        # route out from home and back: home dock -> home via -> via -> dock
        if sid != "intro":
            route = catmull([home[0], home[2], via, dock])
            hits = []
            for p in route:
                for off in (-BEAM_HALF, 0, BEAM_HALF):
                    g = ground_below(p[0] + off, -p[1], land)
                    if g > -1.0:
                        hits.append((round(p[0]), round(p[1]), round(g, 1)))
                        break
            print(f"[route] home -> {sid}: {'clear' if not hits else f'{len(hits)} samples over land, e.g. {hits[:3]}'}")

        ship.matrix_world = ship_matrix(dock[0], dock[1], heading)
        cd = bpy.data.cameras.new(f"CHK_{sid}")
        cd.sensor_fit = "VERTICAL"
        cd.angle_y = math.radians(48)
        cd.clip_start, cd.clip_end = 0.5, 6000
        cam = bpy.data.objects.new(f"CHK_{sid}", cd)
        scene.collection.objects.link(cam)
        p, l = three_to_blender(cpos), three_to_blender(clook)
        cam.location = p
        cam.rotation_euler = (l - p).to_track_quat("-Z", "Y").to_euler()
        scene.camera = cam
        scene.render.resolution_percentage = 50
        scene.render.filepath = str(OUT / f"dock_{sid}.png")
        bpy.ops.render.render(write_still=True)


main()
