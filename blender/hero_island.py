"""The hero island ("Home"): a sea arch and two strata spires over a grassy
shelf and a beach, ringed by sea stacks. Builds, saves, and renders.

    blender -b --factory-startup --python blender/hero_island.py -- <renders-dir> [shot ...]

World frame (Blender, Z up): island centred at the origin, as the home island
is in the app; the camera side (the dock) is -Y.
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import build, flora, materials, stage  # noqa: E402
from lib.rocks import chunk, finish, loft, mesh_object, taper  # noqa: E402
from lib.terrain import Footprint, heightfield  # noqa: E402

V = Vector
ROOT = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDERS = Path(args[0]) if args else ROOT / "renders"
SHOTS = args[1:] or ["home"]


def massif(rnd):
    bm = bmesh.new()
    # Main spire: tall, leaning slightly left, fat base.
    loft(bm, rnd, [V((0, 18, -6)), V((-2, 18, 30)), V((-7, 20, 62)), V((-13, 22, 96))],
         taper(28, 8, 0.15), beds=10, squash=0.85)
    # Second spire, leaning right.
    loft(bm, rnd, [V((34, 26, -6)), V((36, 27, 25)), V((42, 30, 58))], taper(18, 6), beds=7)
    # Back shoulder that joins them.
    loft(bm, rnd, [V((16, 40, -6)), V((16, 40, 34))], taper(26, 18), beds=5, squash=0.8)
    # Sea arch: rises from the water on the left and lands on the main spire.
    loft(bm, rnd, [V((-62, -4, -6)), V((-58, -2, 22)), V((-44, 4, 42)), V((-26, 12, 44)), V((-14, 16, 36))],
         lambda t: 9 - 2.5 * __import__("math").sin(t * 3.14159), beds=9, sides=11, rough=0.25)
    # Front shelf where the outpost sits: a broad low mesa.
    loft(bm, rnd, [V((6, -12, -6)), V((6, -12, 13))], taper(36, 33), beds=3, squash=0.6, rough=0.22)
    # Side shelf toward the right spire.
    loft(bm, rnd, [V((36, 4, -6)), V((36, 4, 9))], taper(22, 20), beds=2, squash=0.7)
    # Fallen blocks around the base.
    import math
    for _ in range(18):
        a = rnd.uniform(0, math.tau)
        r = rnd.uniform(34, 60)
        c = V((10 + math.cos(a) * r, 14 + math.sin(a) * r * 0.75, rnd.uniform(-3, 2)))
        if c.y < -30:  # keep the beach in front clear
            continue
        s = rnd.uniform(3, 7)
        chunk(bm, rnd, c, (s * rnd.uniform(0.8, 1.4), s * rnd.uniform(0.7, 1.1), s * rnd.uniform(0.6, 1.3)))
    ob = mesh_object("ISL_home_rock", bm)
    finish(ob)
    return ob


def sea_stacks(rnd):
    bm = bmesh.new()
    for base, h, r in [(V((-118, -52, 0)), 30, 8), (V((96, -64, 0)), 22, 7), (V((-138, 34, 0)), 46, 10),
                       (V((122, 40, 0)), 34, 9), (V((-84, -96, 0)), 12, 5)]:
        lean = V((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * h * 0.08
        loft(bm, rnd, [base + V((0, 0, -6)), base + V((0, 0, h * 0.5)) + lean * 0.5, base + V((0, 0, h)) + lean],
             taper(r, r * 0.45, 0.1), beds=max(3, int(h / 7)), sides=11)
        for _ in range(3):
            o = V((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)).normalized() * r * rnd.uniform(1.1, 1.8)
            s = r * rnd.uniform(0.25, 0.45)
            chunk(bm, rnd, base + o + V((0, 0, -0.5)), (s, s * 0.8, s * 0.7))
    ob = mesh_object("ISL_home_stacks", bm)
    finish(ob, voxel=0.6)
    return ob


def ground():
    fp = Footprint([(8, -8, 96, 66), (-52, 8, 40, 40), (54, 26, 44, 40)], seed=4.2)
    return heightfield("ISL_home_ground", fp, ((-170, -110), (170, 130)), bank_h=2.4, top=4.5)


# Footprints kept clear of vegetation: (x, y, radius).
CLEAR = []


def clear_of_buildings(loc):
    return all((V((loc.x, loc.y, 0)) - V((x, y, 0))).length > r for x, y, r in CLEAR)


def ground_z(scene, x, y, spread=0.0):
    """Lowest ground height over a footprint (centre + 4 corners)."""
    zs = []
    for dx, dy in ((0, 0), (spread, spread), (-spread, spread), (spread, -spread), (-spread, -spread)):
        hit = flora.ground_hit(scene, x + dx, y + dy)
        if hit:
            zs.append(hit[0].z)
    return min(zs) if zs else 0.0


def place_house(scene, rnd, name, x, y, yaw, **kw):
    w, d = kw.get("w", 6.0), kw.get("d", 5.0)
    ob = build.house(name, rnd, **kw)
    z = ground_z(scene, x, y, max(w, d) * 0.5)
    ob.location = (x, y, z - 0.05)
    ob.rotation_euler.z = yaw
    if kw.get("stilts", 0) <= 0:
        # stone plinth down into the slope so no house floats on a hillside
        pb = build.Builder(rnd)
        pb.box((0, 0, -0.8), (w + 0.5, d + 0.5, 1.9), build.STONE)
        p = pb.object(f"{name}_plinth", bevel=0.05)
        p.location = ob.location
        p.rotation_euler.z = yaw
    CLEAR.append((x, y, max(w, d) * 0.75 + 1.5))
    return ob


def outpost(scene, rnd):
    """The home outpost: a tavern up on the rock shelf, reached by a timber
    stair; houses around the lawn; stilt shacks at the sand; the pier."""
    face_sea = 0.0  # +Y front of a house model; rotate so it faces -Y (the sea)
    towards = lambda x, y: __import__("math").atan2(-(0 - x), (-70 - y)) + 3.14159  # noqa: E731
    shelf_z = ground_z(scene, 4, -20)
    tav = build.house("BLD_tavern", rnd, w=9.5, d=7.0, h=3.2, floors=2, pitch=40, paint=0.8)
    tav.location = (4, -20, shelf_z - 0.05)
    tav.rotation_euler.z = 3.14159
    CLEAR.append((4, -20, 9))
    lawn_z = ground_z(scene, 4, -40)
    build.stairs("BLD_tavern_stair", rnd, (4, -41, lawn_z), (4, -29, shelf_z))
    CLEAR.append((4, -35, 3))
    houses = [
        (-28, -46, dict(w=6.0, d=5.0, floors=1, paint=0.3)),
        (-44, -30, dict(w=5.0, d=4.5, floors=2, paint=0.55)),
        (-14, -56, dict(w=4.5, d=4.0, floors=1, paint=0.05)),
        (27, -50, dict(w=6.5, d=5.0, floors=2, paint=0.3)),
        (44, -34, dict(w=5.0, d=4.5, floors=1, paint=0.95)),
    ]
    for i, (x, y, kw) in enumerate(houses):
        place_house(scene, rnd, f"BLD_house_{i}", x, y, towards(x, y) + rnd.uniform(-0.25, 0.25), **kw)
    # stilt shacks on the sand
    for i, (x, y) in enumerate(((56, -58), (-54, -58))):
        place_house(scene, rnd, f"BLD_shack_{i}", x, y, towards(x, y) + rnd.uniform(-0.2, 0.2),
                    w=4.5, d=4.0, stilts=1.8, floors=1)
    build.pier("BLD_pier", rnd, (8, -66), (8, -106), deck_z=2.2)
    CLEAR.append((8, -64, 5))
    # keep the sightline from the sea to the tavern open
    CLEAR.extend([(4, -38, 9), (6, -52, 8)])


def lantern_lights(scene):
    """A small warm point light in every lantern glass."""
    import bmesh as _bm
    for ob in [o for o in scene.objects if o.name.startswith("BLD_")]:
        if bpy.data.objects.get(f"LGT_{ob.name}_0"):
            continue  # already lit (called again after more islands were built)
        me = ob.data
        idx = [i for i, m in enumerate(me.materials) if m and m.name == "lantern_glow"]
        if not idx:
            continue
        mw = ob.matrix_world
        centres = []
        for p in me.polygons:
            if p.material_index == idx[0]:
                c = mw @ p.center
                if all((c - q).length > 0.6 for q in centres):
                    centres.append(c)
        for i, c in enumerate(centres):
            L = bpy.data.lights.new(f"LGT_{ob.name}_{i}", "POINT")
            L.energy = 60
            L.color = (1.0, 0.6, 0.28)
            L.shadow_soft_size = 0.2
            lo = bpy.data.objects.new(L.name, L)
            scene.collection.objects.link(lo)
            lo.location = c


def vegetation(scene, rnd, land, rock):
    """Palms fringe the beach and lean out to sea; bushes hug the rock base
    and the grassy bank; a few palms on the rock ledges."""
    palms, bushes = flora.sources(scene, rnd)
    centre = V((8, 6, 0))

    def seaward(loc):
        d = loc - centre
        return math.atan2(d.y, d.x) + rnd.uniform(-0.5, 0.5)

    # Palms grow in groves with open lawn between them, not an even grid.
    groves = [V((-78, -30, 0)), V((-40, -52, 0)), V((62, -44, 0)), V((96, -6, 0)), V((-96, 18, 0)), V((20, -58, 0))]

    def in_grove(loc, r=20.0):
        return any((V((loc.x, loc.y, 0)) - g).length < r for g in groves)

    taken = []
    flora.scatter(scene, lambda i, loc: flora.linked_copy(rnd.choice(palms), f"FLR_palm_{len(taken)}"), 24,
                  ((-150, -100), (150, 110)),
                  lambda loc, n, ob: ob == land and 1.9 < loc.z < 7.5 and n.z > 0.85 and in_grove(loc) and clear_of_buildings(loc), rnd,
                  min_gap=6.5, taken=taken, yaw=seaward, scale=(0.7, 1.3))
    flora.scatter(scene, lambda i, loc: flora.linked_copy(rnd.choice(palms), f"FLR_palm_hi_{i}"), 5,
                  ((-60, -40), (60, 60)),
                  lambda loc, n, ob: ob == rock and loc.z > 12 and n.z > 0.9 and clear_of_buildings(loc), rnd,
                  min_gap=9.0, taken=taken, scale=(0.6, 0.85))
    # Bushes cluster under the palms and along the rock foot.
    def bushy(loc, n, ob):
        if not clear_of_buildings(loc):
            return False
        if ob == rock:
            return n.z > 0.85 and loc.z > 3
        near_rock = ground_dist_to(rock, loc) < 6
        return ob == land and loc.z > 2.3 and n.z > 0.7 and (in_grove(loc, 26) or near_rock)

    flora.scatter(scene, lambda i, loc: flora.linked_copy(rnd.choice(bushes), f"FLR_bush_{i}"), 150,
                  ((-150, -100), (150, 110)), bushy, rnd, min_gap=2.6, taken=taken, scale=(0.7, 1.6))


def ground_dist_to(ob, loc):
    ok, co, _, _ = ob.closest_point_on_mesh(ob.matrix_world.inverted() @ loc)
    return (ob.matrix_world @ co - loc).length if ok else 1e9


def build_home(scene):
    """Build the home island into `scene`; returns its land meshes (for the
    shore field). Deterministic: the approved island comes out identical."""
    rnd = random.Random(11)
    rock = massif(rnd)
    stacks = sea_stacks(rnd)
    land = ground()
    rock_mat = materials.rock()
    rock.data.materials.append(rock_mat)
    stacks.data.materials.append(rock_mat)
    land.data.materials.append(materials.terrain())

    outpost(scene, rnd)
    vegetation(scene, rnd, land, rock)
    lantern_lights(scene)
    return [rock, stacks, land]


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    land = build_home(scene)
    stage.sky_and_sun(scene)
    stage.water(scene, land)
    stage.render_settings(scene)

    cams = {
        "home": stage.camera(scene, "CAM_home", (70, -250, 16), (0, 0, 34), lens=32),
        "close": stage.camera(scene, "CAM_close", (30, -118, 8), (-4, -10, 18), lens=28),
        "hero": stage.camera(scene, "CAM_hero", (52, -172, 7), (-2, -10, 30), lens=30),
        "dock": stage.camera(scene, "CAM_dock", (22, -112, 6.5), (-2, -30, 9), lens=30),
    }
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "hero-island.blend"))
    RENDERS.mkdir(parents=True, exist_ok=True)
    for shot in SHOTS:
        stage.render(scene, cams[shot], RENDERS / f"hero_{shot}.png")


if __name__ == "__main__":
    main()
