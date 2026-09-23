"""The whole archipelago: the approved home island plus the four destination
islands, each built around a landmark for its tour stop.

    blender -b --factory-startup --python blender/world.py -- <renders-dir> [shot ...]

Shots: world, ember, skull, lighthouse, drifting (default: all). Saves
blender/world.blend for export.

Island centres are the old islands' positions (portfolio.ts transforms,
converted: blender (x, y) = three (x, -z)). Each island is composed toward its
arrival camera, which uses the app's lens (48 deg vertical).
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hero_island as H  # noqa: E402
from lib import build, flora, landmarks as LM, materials, npc, poi, ship, stage  # noqa: E402
from lib.rocks import chunk, finish, loft, mesh_object, taper  # noqa: E402
from lib.terrain import Footprint, heightfield  # noqa: E402

V = Vector
ROOT = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDERS = Path(args[0]) if args else ROOT / "renders"
SHOTS = args[1:] or ["world", "ember", "skull", "lighthouse", "drifting"]

EMBER = V((-320, 140, 0))  # Projects
SKULL = V((280, -160, 0))  # Resume
LIGHT = V((180, 300, 0))  # Experience
DRIFT = V((-240, -220, 0))  # Contact

# Where the extra foam goes on open water (waterfall impact, chains).
EXTRA_FOAM = []


def rot_z(deg):
    return Matrix.Rotation(math.radians(deg), 4, "Z")


def island_flora(scene, rnd, key, centre, radius, land_objs, n_palms, n_bushes, groves, zmin=1.9, zmax=60.0,
                 palm_scale=(0.75, 1.2)):
    palms, bushes = flora.sources(scene, rnd)

    def in_grove(loc, r=16.0):
        return any((V((loc.x, loc.y, 0)) - g).length < r for g in groves)

    def seaward(loc):
        d = loc - centre
        return math.atan2(d.y, d.x) + rnd.uniform(-0.5, 0.5)

    region = ((centre.x - radius, centre.y - radius), (centre.x + radius, centre.y + radius))
    taken = []
    flora.scatter(scene, lambda i, loc: flora.linked_copy(rnd.choice(palms), f"FLR_palm_{key}_{i}"), n_palms, region,
                  lambda loc, n, ob: ob in land_objs and zmin < loc.z < zmax and n.z > 0.85 and in_grove(loc)
                  and H.clear_of_buildings(loc), rnd, min_gap=6.0, taken=taken, yaw=seaward, scale=palm_scale)
    flora.scatter(scene, lambda i, loc: flora.linked_copy(rnd.choice(bushes), f"FLR_bush_{key}_{i}"), n_bushes,
                  region, lambda loc, n, ob: ob in land_objs and loc.z > zmin + 0.3 and n.z > 0.72
                  and in_grove(loc, 24) and H.clear_of_buildings(loc), rnd, min_gap=2.6, taken=taken,
                  scale=(0.7, 1.5))


# key -> (camera position, look-at target), Blender coords; the close-up the
# app flies to when the prop is clicked. Written out by export_world.py.
POI_SHOTS = {}
FOV_Y = math.radians(48)


def _bounds(objs):
    pts = [o.matrix_world @ V(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    lo = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def plant(scene, builder, x, y, face_to, key, clear=4.0, frame=1.0, pitch=12.0, focus_parts=False, **kw):
    """Place an interactive prop on the ground at (x, y), its front turned to
    `face_to` (the arrival camera), keep plants off it, and compute its
    close-up: a camera in front, a little above, far enough back that the
    prop's bounding sphere fills the frame (`frame` < 1 frames tighter)."""
    rnd = random.Random(sum(map(ord, key)))
    z = H.ground_z(scene, x, y, 0.8)
    d = V((face_to[0] - x, face_to[1] - y, 0)).normalized()
    yaw = math.atan2(d.x, -d.y)  # rotates the prop's -Y front onto d
    objs = builder(rnd, V((x, y, z - 0.05)), yaw, key, **kw)
    bpy.context.view_layer.update()  # refresh matrix_world of freshly placed parts
    kids = [c for o in objs for c in o.children_recursive]
    # focus_parts: frame the moving parts (e.g. the flags), not the whole rig
    lo, hi = _bounds(objs[1:] + kids if focus_parts else objs + kids)
    centre = (lo + hi) / 2
    radius = (hi - lo).length / 2
    dist = max(4.0, radius / math.tan(FOV_Y / 2) * 1.1 * frame)
    p = math.radians(pitch)
    cam = centre + d * dist * math.cos(p) + V((0, 0, dist * math.sin(p)))
    POI_SHOTS[key] = (tuple(cam), tuple(centre))
    # keep plants off the prop and off the camera's sightline
    H.CLEAR.append((x, y, max(clear, radius + 1.5)))
    for k in (0.3, 0.6, 0.9):
        q = centre + d * dist * k
        H.CLEAR.append((q.x, q.y, 3.0 + radius * 0.4))
    return objs


NPC_SHOTS = {}


def person(scene, key, file, x, y, face_to, pose="Idle", frame=12):
    """Stand an NPC on the ground at (x, y) facing `face_to`; keep plants off
    them; compute a talking close-up (3/4 view, eye level, ~4.5 m out)."""
    z = H.ground_z(scene, x, y, 0.4)
    at = V((x, y, z - 0.02))
    npc.place(scene, key, file, at, face_to, pose=pose, frame=frame)
    H.CLEAR.append((x, y, 2.5))
    d = V((face_to[0] - x, face_to[1] - y, 0)).normalized()
    side = V((-d.y, d.x, 0))
    cam = at + d * 4.2 + side * 1.6 + V((0, 0, 1.75))
    NPC_SHOTS[key] = (tuple(cam), tuple(at + V((0, 0, 1.15))))
    for k in (0.4, 0.8):
        q = at + (cam - at) * k
        H.CLEAR.append((q.x, q.y, 1.8))


def point_light(name, at, energy, color, radius=0.5):
    L = bpy.data.lights.new(name, "POINT")
    L.energy = energy
    L.color = color
    L.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, L)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = at
    return ob


# --------------------------------------------------------------------------
# Ember Isle: a volcano with a glowing caldera and a lava channel (Projects)
# --------------------------------------------------------------------------

def ember(scene):
    rnd = random.Random(21)
    C = EMBER
    toward = V((0.707, -0.707, 0))  # the arrival camera and the home island
    basalt = materials.rock("rock_basalt", dark=(0.035, 0.03, 0.03), mid=(0.1, 0.085, 0.075),
                            light=(0.22, 0.18, 0.15), moss=0.8)
    bm = bmesh.new()
    top = C + V((4, 3, 64))
    # Classic stratovolcano profile: broad flanks, steep summit cone; beds
    # recede rather than overhang, so it doesn't turn into a mushroom.
    loft(bm, rnd, [C + V((0, 0, -6)), C + V((2, 1, 30)), top],
         lambda t: 12 + 73 * (1 - t) ** 1.5, beds=12, sides=18, rough=0.18, lip=(-0.07, 0.02))
    LM.crater_rim(bm, rnd, top + V((0, 0, 0.5)), 11.5, toward, height=4.0, thick=3.8)
    # Craggy spurs and a parasitic cone on the flanks break the cone's symmetry.
    loft(bm, rnd, [C + V((-38, 22, -6)), C + V((-40, 24, 22))], taper(16, 6), beds=5, rough=0.3)
    loft(bm, rnd, [C + V((30, 40, -6)), C + V((33, 42, 16))], taper(14, 5), beds=4, rough=0.3)
    for _ in range(14):
        a = rnd.uniform(0, math.tau)
        r = rnd.uniform(62, 82)
        c = C + V((math.cos(a) * r, math.sin(a) * r, rnd.uniform(-3, 1)))
        if (c - C).normalized().dot(toward) > 0.7:
            continue  # keep the lava's beach clear
        s = rnd.uniform(3, 7)
        chunk(bm, rnd, c, (s * 1.2, s, s * 0.8))
    rock = mesh_object("ISL_ember_rock", bm)
    finish(rock, voxel=0.8)
    rock.data.materials.append(basalt)

    fp = Footprint([(C.x, C.y, 92, 86), (C.x - 40, C.y + 20, 40, 40), (C.x + 40, C.y - 44, 44, 34)], seed=7.7)
    ground = heightfield("ISL_ember_ground", fp, ((C.x - 140, C.y - 140), (C.x + 140, C.y + 140)), bank_h=2.0,
                         top=5.0, seed=8.0)
    ground.data.materials.append(materials.terrain("terrain_black_sand", sand=(0.07, 0.065, 0.06),
                                                   sand_alt=(0.12, 0.1, 0.09), sand_wet=(0.03, 0.028, 0.026)))

    # Lava: a pool in the caldera and a channel spilling through the notch.
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=24, radius=10)
    bmesh.ops.translate(bm, vec=top + V((0, 0, 1.6)), verts=bm.verts)
    pool = mesh_object("LAV_ember_pool", bm)
    pool.data.materials.append(materials.emissive("lava_hot", (1.0, 0.2, 0.02), 2.4))
    # The flow runs diagonally across the camera-facing flank, so its
    # meander reads instead of pointing straight at the viewer.
    flow = V((0.97, -0.25, 0)).normalized()
    start = top + toward * 10
    LM.lava_channel("LAV_ember_channel", scene, start, flow, rock)
    point_light("LGT_ember_crater", top + V((0, 0, 6)), 60000, (1.0, 0.4, 0.12), radius=6)
    point_light("LGT_ember_flow", C + flow * 45 + V((0, 0, 28)), 15000, (1.0, 0.3, 0.08), radius=4)

    # A small survey camp on the beach, with its own jetty.
    # (east of where the lava reaches the sea)
    camp = C + V((80, -12, 0))
    H.place_house(scene, rnd, "BLD_ember_hut", camp.x - 6, camp.y + 4, math.radians(-100),
                  w=4.5, d=4.0, stilts=1.6, floors=1, paint=0.55)
    build.pier("BLD_ember_pier", rnd, (camp.x + 2, camp.y - 2), (camp.x + 30, camp.y - 10), deck_z=2.2, lamp_every=8)

    # The four project props, south of the lava, facing the arrival camera
    # (three (-150, 16, 0) = blender (-150, 0)).
    cam = (-150, 0)
    plant(scene, poi.telemetry_mast, -282, 100, cam, "projects_0", clear=5)
    plant(scene, poi.calc_engine, -270, 94, cam, "projects_1")
    plant(scene, poi.trade_stall, -257, 92, cam, "projects_2", clear=5)
    plant(scene, poi.scholar_lectern, -245, 99, cam, "projects_3")
    person(scene, "henry", "Characters_Henry.gltf", -264, 88, cam, pose="Yes")

    island_flora(scene, rnd, "ember", C, 130, [ground, rock], 16, 70,
                 [C + V((-60, -40, 0)), C + V((-70, 30, 0)), C + V((10, 80, 0)), C + V((55, -60, 0))], zmax=18)
    return [rock, ground]


# --------------------------------------------------------------------------
# Skull Cove: the skull rock over a lagoon, treasure on the beach (Resume)
# --------------------------------------------------------------------------

def skull(scene):
    rnd = random.Random(33)
    C = SKULL
    yaw = -40.5  # the skull's face looks at its arrival camera
    R = rot_z(yaw)

    def w(x, y, z=0.0):
        return C + (R @ V((x, y, z)))

    bone = materials.rock("rock_bone", dark=(0.2, 0.17, 0.13), mid=(0.46, 0.4, 0.31), light=(0.7, 0.64, 0.52),
                          moss=0.6)
    xf = Matrix.Translation(w(0, 8)) @ R
    sk, teeth = LM.skull_rock("ISL_skull_rock", rnd, xf)
    sk.data.materials.append(bone)
    teeth.data.materials.append(bone)

    # Arms of the cove + boulders.
    bm = bmesh.new()
    for sx in (-1, 1):
        loft(bm, rnd, [w(sx * 30, 14, -6), w(sx * 32, 12, 12)], taper(14, 9), beds=3, rough=0.3)
        for _ in range(5):
            c = w(sx * rnd.uniform(36, 52), rnd.uniform(-60, -10), rnd.uniform(-2, 0.5))
            s = rnd.uniform(2, 5)
            chunk(bm, rnd, c, (s * 1.3, s, s * 0.8))
    rocks = mesh_object("ISL_skull_rocks", bm)
    finish(rocks, voxel=0.6)
    rocks.data.materials.append(bone)

    blobs = [(0, 24, 62, 30), (-40, -22, 18, 36), (40, -22, 18, 36), (-22, 6, 26, 22), (22, 6, 26, 22)]
    holes = [(0, -34, 23, 30)]
    world_blobs = [(*w(x, y).xy, rx, ry) for x, y, rx, ry in blobs]
    world_holes = [(*w(x, y).xy, rx, ry) for x, y, rx, ry in holes]
    fp = Footprint(world_blobs, seed=3.3, holes=world_holes)
    ground = heightfield("ISL_skull_ground", fp, ((C.x - 120, C.y - 120), (C.x + 120, C.y + 120)), beach=0.22,
                         bank_h=1.6, top=4.0, seed=5.0)
    ground.data.materials.append(materials.terrain("terrain_white_sand", sand=(0.82, 0.72, 0.52),
                                                   sand_alt=(0.74, 0.62, 0.42), grass_line=1.4))

    # Beach set dressing: the chest under the X, torches, a rowboat, barrels.
    b = build.Builder(rnd, 0.0)
    def gz(x, y):
        p = w(x, y)
        hit = flora.ground_hit(scene, p.x, p.y)
        return V((p.x, p.y, hit[0].z if hit else 1.0))
    chest_at = gz(-24, -40)
    plant(scene, poi.chest, chest_at.x, chest_at.y, (182.5, -274), "resume")
    sk_at = w(-27.5, -37)  # dry sand beside the chest
    person(scene, "skeleton", "Characters_Skeleton.gltf", sk_at.x, sk_at.y, (182.5, -274), pose="Idle")
    for dx, dy in ((-2.5, 2.0), (2.6, 1.6)):
        LM.torch_post(b, gz(-24 + dx, -40 + dy))
    # X marks the spot: two crossed planks in the sand beside the dig.
    xc = gz(-20, -44)
    for a in (0.785, -0.785):
        b.box(xc + V((0, 0, 0.05)), (3.0, 0.35, 0.08), build.WALL, rot=(0, 0, a + math.radians(yaw)), paint=0.8)
    LM.rowboat(b, gz(26, -46), rnd, yaw=math.radians(yaw) - 1.2)
    for i in range(3):
        build.barrel(b, gz(-30 + i * 1.3, -35 + (i % 2)), rnd)
    props = b.object("BLD_skull_props")
    H.CLEAR.extend([(chest_at.x, chest_at.y, 6), (*w(26, -46).xy, 5)])
    point_light("LGT_skull_chest", chest_at + V((0, 0, 2.5)), 600, (1.0, 0.7, 0.35), radius=0.5)

    island_flora(scene, rnd, "skull", C, 110, [ground], 18, 80,
                 [w(-42, -30), w(42, -30), w(-30, 22), w(30, 22), w(0, 36)], zmax=12)
    return [sk, teeth, rocks, ground]


# --------------------------------------------------------------------------
# Lighthouse Rock: a cliff mesa, a working lighthouse, a wreck (Experience)
# --------------------------------------------------------------------------

def lighthouse_rock(scene):
    rnd = random.Random(44)
    C = LIGHT
    grey = materials.rock("rock_grey", dark=(0.1, 0.1, 0.1), mid=(0.28, 0.27, 0.25), light=(0.48, 0.46, 0.42))
    bm = bmesh.new()
    loft(bm, rnd, [C + V((0, 0, -6)), C + V((0, 4, 34))], taper(46, 38, 0.05), beds=6, sides=18, squash=0.75,
         rough=0.25)
    loft(bm, rnd, [C + V((-26, -30, -6)), C + V((-26, -30, 7))], taper(18, 16), beds=2, squash=0.7, rough=0.2)
    for base, h, r in [(C + V((58, -30, 0)), 26, 7), (C + V((-62, 10, 0)), 18, 6), (C + V((40, 52, 0)), 30, 8)]:
        loft(bm, rnd, [base + V((0, 0, -6)), base + V((1, 1, h))], taper(r, r * 0.45, 0.1), beds=4, sides=11)
    for _ in range(16):
        a = rnd.uniform(0, math.tau)
        r = rnd.uniform(44, 60)
        c = C + V((math.cos(a) * r, math.sin(a) * r * 0.85, rnd.uniform(-3, 1)))
        s = rnd.uniform(3, 7)
        chunk(bm, rnd, c, (s * 1.3, s, s * 0.9))
    rock = mesh_object("ISL_light_rock", bm)
    finish(rock, voxel=0.8)
    rock.data.materials.append(grey)

    # Grassy cap on the plateau, kept inside the cliff edge.
    # (the loft squashes the mesa in X: ~28 m by ~38 m at the top)
    fp = Footprint([(C.x, C.y + 4, 22, 30), (C.x - 6, C.y - 4, 18, 22)], seed=2.2)
    cap = heightfield("ISL_light_cap", fp, ((C.x - 50, C.y - 50), (C.x + 50, C.y + 50)), step=1.4, beach=0.001,
                      bank=0.03, bank_h=0.6, top=2.5, seed=4.0, base=34.0)
    cap.data.materials.append(materials.terrain())

    lx, ly = C.x + 4, C.y - 22  # near the seaward cliff edge
    top_z = H.ground_z(scene, lx, ly)
    lh, lamp_z = LM.lighthouse("BLD_lighthouse", rnd)
    lh.location = (lx, ly, top_z - 0.3)
    H.CLEAR.append((lx, ly, 7))
    point_light("LGT_lighthouse", (lx, ly, top_z + lamp_z), 3000, (1.0, 0.85, 0.55), radius=1.0)
    H.place_house(scene, rnd, "BLD_keeper", C.x - 12, C.y - 4, math.radians(170), w=6.0, d=4.5, floors=1,
                  paint=0.3)
    # one flag per job, oldest on the left as seen from the arrival camera
    plant(scene, poi.signal_mast, lx + 12, ly + 6, (237, 120), "experience", clear=6, focus_parts=True, frame=1.2)
    person(scene, "mako", "Characters_Mako.gltf", lx + 8, ly + 1, (237, 120), pose="Wave", frame=18)

    # Landing: a jetty off the lower shelf, with a stair up from it.
    shelf = C + V((-26, -30, 0))
    shelf_z = H.ground_z(scene, shelf.x, shelf.y)
    build.pier("BLD_light_pier", rnd, (shelf.x - 2, shelf.y - 10), (shelf.x - 2, shelf.y - 38), deck_z=2.2,
               lamp_every=9)
    build.stairs("BLD_light_stair", rnd, (shelf.x - 2, shelf.y - 12, 2.2), (shelf.x - 2, shelf.y - 4, shelf_z))

    wreck = LM.shipwreck("BLD_wreck", rnd, length=34, beam=11, depth=7)
    wreck.location = C + V((56, -44, -2.5))
    wreck.rotation_euler = (math.radians(-38), math.radians(10), math.radians(20))

    island_flora(scene, rnd, "light", C, 60, [cap], 7, 40, [C + V((-14, 8, 0)), C + V((14, 12, 0))],
                 zmin=33, zmax=60, palm_scale=(0.6, 0.9))
    return [rock]


# --------------------------------------------------------------------------
# Drifting Isle: floating rock, waterfall, moored by chains (Contact)
# --------------------------------------------------------------------------

def drifting(scene):
    rnd = random.Random(55)
    C = DRIFT
    toward = V((0.97, -0.24, 0))
    mossy = materials.rock("rock_moss", dark=(0.12, 0.1, 0.09), mid=(0.3, 0.24, 0.19), light=(0.46, 0.38, 0.3),
                           moss=1.6)
    bm = bmesh.new()
    loft(bm, rnd, [C + V((0, 0, 47)), C + V((1, 0, 32)), C + V((3, -1, 18)), C + V((4, -2, 8))],
         lambda t: 2 + 34 * (1 - t) ** 1.25, beds=9, sides=16, rough=0.28)
    sats = []
    for i in range(7):
        a = i / 7 * math.tau + rnd.uniform(-0.3, 0.3)
        r = rnd.uniform(44, 60)
        c = C + V((math.cos(a) * r, math.sin(a) * r, rnd.uniform(26, 52)))
        s = rnd.uniform(2.5, 6.5)
        # a flat-topped chunk with a jagged hanging root, not a cone
        chunk(bm, rnd, c, (s * 1.3, s * 1.1, s * 0.55), tilt=0.12)
        loft(bm, rnd, [c + V((0, 0, -s * 0.2)), c + V((rnd.uniform(-1, 1), rnd.uniform(-1, 1), -s * 1.9))],
             lambda t, s=s: s * (0.9 - 0.75 * t), beds=3, sides=9, rough=0.35)
        sats.append((c, s))
    rock = mesh_object("ISL_drift_rock", bm)
    finish(rock, voxel=0.7)
    rock.data.materials.append(mossy)

    fp = Footprint([(C.x, C.y, 30, 28), (C.x + 10, C.y + 6, 20, 18)], seed=6.6)
    cap = heightfield("ISL_drift_cap", fp, ((C.x - 45, C.y - 45), (C.x + 45, C.y + 45)), step=1.3, beach=0.001,
                      bank=0.03, bank_h=0.8, top=3.5, seed=9.0, base=46.5)
    cap.data.materials.append(materials.terrain())

    # Watch tower with a lamp (whitewashed, no bands), lanterns along a path.
    tz = H.ground_z(scene, C.x - 8, C.y + 6)
    tw, lamp_z = LM.lighthouse("BLD_drift_tower", rnd, height=9.0, r0=2.3, r1=1.9, bands=False)
    tw.location = (C.x - 8, C.y + 6, tz - 0.3)
    H.CLEAR.append((C.x - 8, C.y + 6, 5))
    point_light("LGT_drift_tower", (C.x - 8, C.y + 6, tz + lamp_z), 1500, (1.0, 0.8, 0.5))
    b = build.Builder(rnd, 0.0)
    for i in range(4):
        p = C + V((-2 + i * 6.5, -3 - i * 2, 0))
        hit = flora.ground_hit(scene, p.x, p.y)
        if hit:
            LM.torch_post(b, hit[0], h=2.2)
    b.object("BLD_drift_lamps")

    plant(scene, poi.message_bottle, C.x + 12, C.y - 16, (-170, -370), "contact", clear=3)
    person(scene, "sharky", "Characters_Sharky.gltf", C.x + 8, C.y - 19, (-170, -370), pose="Idle")

    # Spring -> waterfall off the edge toward the camera side.
    fall_dir = V((0.8, -0.6, 0)).normalized()
    edge = C + fall_dir * 28
    hit = flora.ground_hit(scene, edge.x, edge.y)
    top = V((edge.x, edge.y, (hit[0].z if hit else 46.5) + 0.3))
    LM.waterfall("H2O_drift_fall", top, fall_dir, drop=top.z - 0.2, width=4.5, reach=12)
    impact = top + fall_dir * 12
    EXTRA_FOAM.append((impact.x, impact.y))

    # Moored: three chains down into the sea.
    for i, a in enumerate((0.5, 2.6, 4.4)):
        d = V((math.cos(a), math.sin(a), 0))
        hang = C + d * 11 + V((0, 0, 24))
        sea = C + d * 44 + V((0, 0, -2))
        LM.chain(f"CHN_drift_{i}", hang, sea, sag=7.0)
        EXTRA_FOAM.append((C.x + d.x * 42, C.y + d.y * 42))

    island_flora(scene, rnd, "drift", C, 45, [cap], 6, 34, [C + V((6, -4, 0)), C + V((-10, -8, 0))],
                 zmin=45, zmax=80, palm_scale=(0.6, 0.9))
    # a bush on top of the bigger satellite rocks
    palms, bushes = flora.sources(scene, rnd)
    for i, (c, s) in enumerate(sats):
        if s < 4:
            continue
        hit = flora.ground_hit(scene, c.x, c.y)
        if hit and hit[2] == rock:
            ob = flora.linked_copy(rnd.choice(bushes), f"FLR_bush_drift_sat_{i}")
            ob.location = hit[0] - V((0, 0, 0.1))
            ob.scale = (0.6,) * 3
    return [rock]  # floating: only the chains and waterfall meet the sea


# --------------------------------------------------------------------------

def cameras(scene):
    def cam(name, pos, look):
        ob = stage.camera(scene, name, pos, look)
        ob.data.sensor_fit = "VERTICAL"
        ob.data.angle_y = math.radians(48)
        return ob

    return {
        "world": cam("CAM_world", (60, -700, 260), (0, 40, 0)),
        "ember": cam("CAM_ember", EMBER + V((150, -150, 14)), EMBER + V((0, 0, 30))),
        "skull": cam("CAM_skull", SKULL + V((-0.65, -0.76, 0)) * 150 + V((0, 0, 9)), SKULL + V((0, 0, 16))),
        "lighthouse": cam("CAM_lighthouse", LIGHT + V((57, -180, 14)), LIGHT + V((0, 0, 24))),
        # From the south-south-east so the low western sun side-lights it
        # instead of backlighting it into a silhouette.
        "drifting": cam("CAM_drifting", DRIFT + V((70, -150, 24)), DRIFT + V((0, 0, 28))),
        "ship_home": cam("CAM_ship_home", (70, -150, 10), (18, -100, 12)),
    }


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    land = H.build_home(scene)
    plant(scene, poi.wanted_board, 15, -67, (62, -148), "intro")
    person(scene, "anne", "Characters_Anne.gltf", 10.5, -69.5, (62, -148), pose="Wave", frame=18)
    # The ship, moored at the home dock, for review renders only (its own
    # export; the world export skips SHP_*). Bow +Y = three -Z, heading pi.
    hull_ob, sails, fl = ship.galleon(random.Random(7))
    for o in [hull_ob, fl] + sails:
        o.location = (21.5, -106, 0)
    land += ember(scene)
    land += skull(scene)
    land += lighthouse_rock(scene)
    land += drifting(scene)
    H.lantern_lights(scene)
    stage.sky_and_sun(scene)
    stage.water(scene, land, size=2200.0, near=1100.0, step=2.5, extra=EXTRA_FOAM)
    # for export_world.py's shore map
    scene["extra_foam"] = [c for p in EXTRA_FOAM for c in p]
    scene["land"] = [o.name for o in land]
    stage.render_settings(scene)
    cams = cameras(scene)
    import json
    scene["poi_shots"] = json.dumps(POI_SHOTS)
    scene["npc_shots"] = json.dumps(NPC_SHOTS)
    scene["npc_placements"] = json.dumps(npc.NPC_PLACEMENTS)
    for key, (pos, look) in NPC_SHOTS.items():
        ob = stage.camera(scene, f"CAM_npc_{key}", pos, look)
        ob.data.sensor_fit = "VERTICAL"
        ob.data.angle_y = FOV_Y
        cams[f"npc_{key}"] = ob
    for key, (pos, look) in POI_SHOTS.items():
        ob = stage.camera(scene, f"CAM_poi_{key}", pos, look)
        ob.data.sensor_fit = "VERTICAL"
        ob.data.angle_y = FOV_Y
        cams[f"poi_{key}"] = ob
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "world.blend"))
    RENDERS.mkdir(parents=True, exist_ok=True)
    for shot in SHOTS:
        if shot in cams:  # pass "none" to just build + save
            stage.render(scene, cams[shot], RENDERS / f"world_{shot}.png")


main()
