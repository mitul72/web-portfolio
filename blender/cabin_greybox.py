"""
Captain's cabin GREYBOX (phase 1 of docs/cabin-concept.md).

Layout + camera framing only: primitives at true metre scale, flat role colours.
Z up, metres. Room origin = floor centre. +Y = aft (stern windows), -Y = fore
(door). -X = port, +X = starboard.

Run:  blender -b --python cabin_greybox.py -- <out_dir>
"""
import bpy, bmesh, math, os, sys, json
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/tmp/cabin"
os.makedirs(os.path.join(OUT, "renders"), exist_ok=True)

# ----------------------------------------------------------------- reset
bpy.ops.wm.read_factory_settings(use_empty=True)
SCN = bpy.context.scene
SCN.unit_settings.system = "METRIC"

COLL = {}
def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name)
        SCN.collection.children.link(c)
        COLL[name] = c
    return COLL[name]

# ----------------------------------------------------------------- materials
# Flat role colours. diffuse_color drives Workbench; Base Color drives EEVEE.
PALETTE = {
    "wood_dark":  (0.10, 0.055, 0.03),
    "wood_mid":   (0.26, 0.15, 0.08),
    "wood_light": (0.42, 0.28, 0.16),
    "parchment":  (0.80, 0.70, 0.50),
    "brass":      (0.72, 0.52, 0.18),
    "iron":       (0.08, 0.08, 0.09),
    "leather":    (0.30, 0.08, 0.06),
    "fabric_red": (0.40, 0.07, 0.06),
    "linen":      (0.75, 0.72, 0.64),
    "glass_bottle": (0.10, 0.35, 0.20),
    "silk_ribbon":  (0.55, 0.08, 0.10),
    "sea":          (0.02, 0.05, 0.10),
}
EMISSIVE = {
    "window_dusk": ((0.20, 0.28, 0.55), 1.5),
    "lantern":     ((1.00, 0.62, 0.25), 6.0),
    "sky_dusk":    ((0.16, 0.20, 0.42), 1.0),
}
MATS = {}
def mat(name):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    if name in EMISSIVE:
        c, s = EMISSIVE[name]
        b.inputs["Base Color"].default_value = (*c, 1)
        b.inputs["Emission Color"].default_value = (*c, 1)
        b.inputs["Emission Strength"].default_value = s
        m.diffuse_color = (*c, 1)
    else:
        c = PALETTE[name]
        b.inputs["Base Color"].default_value = (*c, 1)
        b.inputs["Roughness"].default_value = 0.35 if name == "brass" else 0.7
        b.inputs["Metallic"].default_value = 1.0 if name in ("brass", "iron") else 0.0
        # Workbench-only display colour, lifted so the greybox reads as light
        # clay. The EEVEE Base Color above keeps the true dark wood tones.
        m.diffuse_color = (*(v ** 0.5 for v in c), 1)
    MATS[name] = m
    return m

# ----------------------------------------------------------------- builders
def _obj(name, bm, material, collection, parent=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat(material))
    coll(collection).objects.link(ob)
    if parent: ob.parent = parent
    return ob

def box(name, size, loc, material, collection, rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    M = (Matrix.Translation(Vector(loc))
         @ Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y")
         @ Matrix.Rotation(rot[0], 4, "X")
         @ Matrix.Diagonal(Vector((*size, 1))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    return _obj(name, bm, material, collection, parent)

def cyl(name, r, h, loc, material, collection, rot=(0, 0, 0), segs=16, r2=None, parent=None):
    bm = bmesh.new()
    M = (Matrix.Translation(Vector(loc))
         @ Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y")
         @ Matrix.Rotation(rot[0], 4, "X"))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r,
                          radius2=r if r2 is None else r2, depth=h, matrix=M)
    return _obj(name, bm, material, collection, parent)

def sphere(name, r, loc, material, collection, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=r,
                              matrix=Matrix.Translation(Vector(loc)))
    return _obj(name, bm, material, collection, parent)

# ================================================================= ROOM SHELL
W, D, H = 6.4, 5.2, 2.3          # width (X), depth (Y), ceiling height
HX, HY = W / 2, D / 2
S = "ENV_shell"

box("ENV_floor",   (W, D, 0.10), (0, 0, -0.05), "wood_mid",  S)
box("ENV_ceiling", (W, D, 0.10), (0, 0, H + 0.05), "wood_dark", S)
box("ENV_wall_port",      (0.15, D, H), (-HX - 0.075, 0, H / 2), "wood_dark", S)
box("ENV_wall_starboard", (0.15, D, H), ( HX + 0.075, 0, H / 2), "wood_dark", S)

# Deck beams overhead (athwartships) — the strongest "inside a ship" cue.
for i, y in enumerate((-2.0, -1.0, 0.0, 1.0, 2.0)):
    box(f"ENV_beam_{i}", (W, 0.20, 0.22), (0, y, H - 0.11), "wood_mid", S)
# Hull frames (ribs) down the side walls.
for i, y in enumerate((-2.2, -1.4, -0.6, 0.2, 1.0, 1.8)):
    for side, x in (("p", -HX + 0.06), ("s", HX - 0.06)):
        box(f"ENV_rib_{side}{i}", (0.12, 0.16, H), (x, y, H / 2), "wood_mid", S)

# Fore wall with a door opening (x -0.5..0.5, z 0..2.0).
box("ENV_wall_fore_l", (HX - 0.5, 0.15, H), (-(HX + 0.5) / 2, -HY - 0.075, H / 2), "wood_dark", S)
box("ENV_wall_fore_r", (HX - 0.5, 0.15, H), ( (HX + 0.5) / 2, -HY - 0.075, H / 2), "wood_dark", S)
box("ENV_wall_fore_header", (1.0, 0.15, H - 2.0), (0, -HY - 0.075, 2.0 + (H - 2.0) / 2), "wood_dark", S)

# Stern gallery: 5 windows, 0.8 wide, sill 0.9, head 2.0, 0.2 mullions.
SILL, HEAD, WIN, MUL = 0.9, 2.0, 0.8, 0.2
span = 5 * WIN + 4 * MUL                                  # 4.8
box("ENV_stern_lower", (W, 0.15, SILL), (0, HY + 0.075, SILL / 2), "wood_dark", S)
box("ENV_stern_upper", (W, 0.15, H - HEAD), (0, HY + 0.075, HEAD + (H - HEAD) / 2), "wood_dark", S)
end_w = (W - span) / 2
for side, x in (("p", -HX + end_w / 2), ("s", HX - end_w / 2)):
    box(f"ENV_stern_end_{side}", (end_w, 0.15, HEAD - SILL), (x, HY + 0.075, (SILL + HEAD) / 2), "wood_dark", S)
x0 = -span / 2
for i in range(5):
    cx = x0 + WIN / 2 + i * (WIN + MUL)
    box(f"ENV_window_{i}", (WIN, 0.02, HEAD - SILL), (cx, HY + 0.12, (SILL + HEAD) / 2), "window_dusk", S)
    # glazing bars: one horizontal, one vertical per window
    box(f"ENV_glazing_h{i}", (WIN, 0.04, 0.03), (cx, HY + 0.10, (SILL + HEAD) / 2), "wood_mid", S)
    box(f"ENV_glazing_v{i}", (0.03, 0.04, HEAD - SILL), (cx, HY + 0.10, (SILL + HEAD) / 2), "wood_mid", S)
    if i < 4:
        box(f"ENV_mullion_{i}", (MUL, 0.15, HEAD - SILL), (cx + WIN / 2 + MUL / 2, HY + 0.075, (SILL + HEAD) / 2), "wood_dark", S)
box("ENV_window_seat", (3.5, 0.45, 0.08), (-0.25, HY - 0.22, 0.46), "wood_light", S)

# Outside: dusk sky backdrop + sea, so the windows read as open water.
box("ENV_sky_backdrop", (400, 1, 200), (0, 120, 20), "sky_dusk", "ENV_outside")
box("ENV_sea", (400, 240, 0.1), (0, 122, -3.0), "sea", "ENV_outside")

# ================================================================= PROPS
P = "PRP"

# --- Desk (projects) — centre aft, captain's back to the windows.
DESK_Y, DESK_TOP = 1.25, 0.76
box("PRP_desk_top", (1.7, 0.9, 0.06), (0, DESK_Y, DESK_TOP - 0.03), "wood_mid", P)
for side, x in (("l", -0.58), ("r", 0.58)):
    box(f"PRP_desk_pedestal_{side}", (0.48, 0.80, DESK_TOP - 0.06), (x, DESK_Y, (DESK_TOP - 0.06) / 2), "wood_dark", P)
box("PRP_chair_seat", (0.52, 0.50, 0.06), (0, 1.88, 0.46), "leather", P)
box("PRP_chair_back", (0.52, 0.08, 0.62), (0, 2.10, 0.80), "wood_dark", P)
for i, (x, y) in enumerate(((-0.22, 1.68), (0.22, 1.68), (-0.22, 2.08), (0.22, 2.08))):
    box(f"PRP_chair_leg_{i}", (0.05, 0.05, 0.43), (x, y, 0.215), "wood_dark", P)

chart = box("PRP_sea_chart", (1.05, 0.72, 0.004), (0, DESK_Y - 0.04, DESK_TOP + 0.002), "parchment", P, rot=(0, 0, 0.04))
PIN_XY = [(-0.32, -0.18), (0.05, 0.16), (0.30, -0.08), (-0.10, -0.02)]
for i, (px, py) in enumerate(PIN_XY):
    cyl(f"PRP_chart_pin_{i}", 0.006, 0.05, (px, DESK_Y - 0.04 + py, DESK_TOP + 0.03), "brass", P)
    sphere(f"PRP_chart_pin_head_{i}", 0.018, (px, DESK_Y - 0.04 + py, DESK_TOP + 0.058), "brass", P)
# desk dressing
cyl("PRP_candle_holder", 0.05, 0.02, (0.62, DESK_Y + 0.25, DESK_TOP + 0.01), "brass", P)
cyl("PRP_candle", 0.018, 0.14, (0.62, DESK_Y + 0.25, DESK_TOP + 0.09), "linen", P)
sphere("PRP_candle_flame", 0.012, (0.62, DESK_Y + 0.25, DESK_TOP + 0.175), "lantern", P)
cyl("PRP_inkwell", 0.03, 0.05, (-0.62, DESK_Y + 0.25, DESK_TOP + 0.025), "iron", P)
cyl("PRP_spyglass", 0.025, 0.45, (-0.55, DESK_Y - 0.33, DESK_TOP + 0.025), "brass", P, rot=(0, math.pi / 2, 0.3))
cyl("PRP_compass", 0.07, 0.03, (0.60, DESK_Y - 0.30, DESK_TOP + 0.015), "brass", P)
box("PRP_rug", (2.8, 2.0, 0.012), (0, 0.75, 0.006), "fabric_red", P)

# --- Name plaque above the stern windows (intro).
box("PRP_name_plaque", (0.70, 0.02, 0.12), (0, DESK_Y - 0.45 - 0.012, 0.58), "brass", P)

# --- Box bed, port side aft.
BED_X = -HX + 0.55
box("PRP_bed_base", (1.0, 2.0, 0.40), (BED_X, 1.25, 0.20), "wood_dark", P)
box("PRP_bed_mattress", (0.92, 1.92, 0.16), (BED_X, 1.25, 0.48), "linen", P)
box("PRP_bed_side_board", (0.06, 2.0, 0.35), (BED_X + 0.50, 1.25, 0.58), "wood_mid", P)
box("PRP_bed_canopy", (1.0, 2.0, 0.06), (BED_X, 1.25, 1.95), "wood_mid", P)
for i, y in enumerate((0.27, 2.23)):
    box(f"PRP_bed_post_{i}", (0.08, 0.08, 1.95), (BED_X + 0.46, y, 0.975), "wood_mid", P)

# --- Sea chest at the foot of the bed (resume). Lid is its own node.
CHEST = Vector((BED_X, -0.12, 0))
chest = box("PRP_chest_body", (0.95, 0.52, 0.42), (CHEST.x, CHEST.y, 0.21), "wood_light", P)
lid = box("PRP_chest_lid", (0.97, 0.54, 0.12), (CHEST.x, CHEST.y, 0.48), "wood_light", P)
for i, x in enumerate((-0.32, 0.32)):
    box(f"PRP_chest_band_{i}", (0.05, 0.55, 0.56), (CHEST.x + x, CHEST.y, 0.28), "iron", P)
box("PRP_chest_lock", (0.10, 0.03, 0.12), (CHEST.x + 0.47 * 0 , CHEST.y - 0.275, 0.40), "brass", P)

# --- Lectern + logbook, starboard midships (experience).
LEC = Vector((HX - 0.75, 0.05, 0))
box("PRP_lectern_base", (0.45, 0.45, 0.06), (LEC.x, LEC.y, 0.03), "wood_dark", P)
box("PRP_lectern_post", (0.12, 0.12, 0.98), (LEC.x, LEC.y, 0.52), "wood_dark", P)
TILT = math.radians(22)
box("PRP_lectern_top", (0.42, 0.58, 0.04), (LEC.x, LEC.y, 1.03), "wood_dark", P, rot=(0, -TILT, 0))
box("PRP_logbook", (0.36, 0.50, 0.05), (LEC.x - 0.01, LEC.y, 1.075), "leather", P, rot=(0, -TILT, 0))
box("PRP_logbook_pages", (0.33, 0.47, 0.012), (LEC.x - 0.02, LEC.y, 1.105), "parchment", P, rot=(0, -TILT, 0))
for i, dy in enumerate((-0.16, -0.05, 0.06, 0.17)):
    box(f"PRP_logbook_ribbon_{i}", (0.012, 0.022, 0.20), (LEC.x - 0.19, LEC.y + dy, 0.96), "silk_ribbon", P)

# --- Bottle rack under the starboard stern window (contact).
RACK = Vector((span / 2 - WIN / 2, HY - 0.25, 0))
box("PRP_rack_frame", (0.80, 0.34, 0.84), (RACK.x, RACK.y, 0.42), "wood_mid", P)
for row in range(2):
    for col in range(3):
        cyl(f"PRP_rack_bottle_{row}{col}", 0.045, 0.30,
            (RACK.x - 0.24 + col * 0.24, RACK.y + 0.02, 0.22 + row * 0.38),
            "glass_bottle", P, rot=(math.pi / 2, 0, 0))
cyl("PRP_message_bottle", 0.05, 0.34, (RACK.x, RACK.y - 0.02, 0.90), "glass_bottle", P, rot=(0, math.pi / 2, 0.25))
box("PRP_message_scroll", (0.20, 0.03, 0.03), (RACK.x, RACK.y - 0.02, 0.90), "parchment", P, rot=(0, 0, 0.25))

# --- Cannon, starboard fore, run out toward a closed gunport.
CAN = Vector((HX - 0.55, -1.65, 0))
box("PRP_cannon_carriage", (0.70, 0.55, 0.32), (CAN.x, CAN.y, 0.22), "wood_mid", P)
for i, (dx, dy) in enumerate(((-0.25, -0.24), (0.25, -0.24), (-0.25, 0.24), (0.25, 0.24))):
    cyl(f"PRP_cannon_wheel_{i}", 0.11, 0.06, (CAN.x + dx, CAN.y + dy, 0.11), "wood_dark", P, rot=(math.pi / 2, 0, 0))
cyl("PRP_cannon_barrel", 0.11, 1.3, (CAN.x - 0.30, CAN.y, 0.46), "iron", P, rot=(0, math.pi / 2, 0), r2=0.08)
box("PRP_gunport_lid", (0.02, 0.55, 0.50), (HX - 0.005, CAN.y, 0.55), "wood_light", P)
cyl("PRP_rope_coil", 0.22, 0.10, (CAN.x - 0.55, CAN.y + 0.55, 0.05), "linen", P)

# --- Bookshelf, port fore; map-tube barrel starboard of the door.
box("PRP_bookshelf", (1.3, 0.36, 1.9), (-HX + 0.9, -HY + 0.25, 0.95), "wood_dark", P)
for s_i, z in enumerate((0.45, 0.95, 1.45)):
    for b in range(7):
        box(f"PRP_book_{s_i}{b}", (0.07, 0.24, 0.28 - (b % 3) * 0.03),
            (-HX + 0.42 + b * 0.14, -HY + 0.26, z + 0.14 - (b % 3) * 0.015),
            ("leather", "fabric_red", "wood_light")[b % 3], P)
cyl("PRP_map_barrel", 0.24, 0.70, (0.95, -HY + 0.35, 0.35), "wood_mid", P)
for i, (dx, dy) in enumerate(((-0.08, 0.02), (0.06, -0.05), (0.02, 0.08))):
    cyl(f"PRP_map_tube_{i}", 0.04, 0.60, (0.95 + dx, -HY + 0.35 + dy, 0.85), "parchment", P, rot=(0.12 * (i - 1), 0.1, 0))

# --- Lanterns: one hanging over the desk, one by the bed, one by the lectern.
LANTERNS = {
    "desk":    Vector((0.0, 1.0, 1.72)),
    "bed":     Vector((-HX + 0.15, -0.55, 1.55)),
    "lectern": Vector((HX - 0.15, 0.75, 1.55)),
}
for n, p in LANTERNS.items():
    box(f"PRP_lantern_{n}", (0.18, 0.18, 0.26), p, "lantern", P)
    box(f"PRP_lantern_{n}_cap", (0.22, 0.22, 0.04), p + Vector((0, 0, 0.15)), "iron", P)
box("PRP_lantern_desk_chain", (0.015, 0.015, H - 0.22 - 1.87), (0, 1.0, (1.87 + H - 0.22) / 2), "iron", P)

# ================================================================= LIGHTS
L = "LGT"
def point(name, loc, watts, colour, radius=0.08):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = watts; ld.color = colour; ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld); ob.location = loc
    coll(L).objects.link(ob)
    return ob
for n, p in LANTERNS.items():
    point(f"LGT_lantern_{n}", p, 60 if n == "desk" else 35, (1.0, 0.62, 0.30))
point("LGT_candle", (0.62, DESK_Y + 0.25, DESK_TOP + 0.2), 6, (1.0, 0.6, 0.28), 0.02)
# Cool dusk light coming in through the stern windows.
ad = bpy.data.lights.new("LGT_window_dusk", "AREA")
ad.shape = "RECTANGLE"; ad.size = span; ad.size_y = HEAD - SILL
ad.energy = 220; ad.color = (0.45, 0.55, 1.0)
win = bpy.data.objects.new("LGT_window_dusk", ad)
win.location = (0, HY + 0.4, (SILL + HEAD) / 2)
win.rotation_euler = (math.radians(-90), 0, 0)   # face -Y, into the room
coll(L).objects.link(win)

world = bpy.data.worlds.new("World"); SCN.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.025, 0.05, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0

# ================================================================= CAMERAS
# One authored shot per stop (docs/cabin-concept.md). Vertical FOV per shot.
SHOTS = {
    "CAM_intro":      ((0.35, -2.35, 1.60), (0.0, 1.35, 1.05), 48, ["PRP_desk_top", "PRP_name_plaque", "ENV_window_2"]),
    "CAM_projects":   ((0.0, 0.30, 1.50),   (0.0, 1.22, 0.76), 38, ["PRP_sea_chart"]),
    "CAM_experience": ((1.25, -0.35, 1.55), (HX - 0.78, 0.05, 1.05), 36, ["PRP_logbook"]),
    "CAM_resume":     ((-1.35, -1.35, 1.35), (BED_X, -0.12, 0.30), 38, ["PRP_chest_body", "PRP_chest_lid"]),
    "CAM_contact":    ((1.05, 0.85, 1.30),  (RACK.x, RACK.y, 0.85), 44, ["PRP_rack_frame", "PRP_message_bottle"]),
}
CAMS = {}
for name, (loc, target, fov, _) in SHOTS.items():
    cd = bpy.data.cameras.new(name)
    cd.sensor_fit = "VERTICAL"; cd.lens_unit = "FOV"; cd.angle_y = math.radians(fov)
    cd.clip_start = 0.05; cd.clip_end = 500
    cam = bpy.data.objects.new(name, cd)
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    coll("CAM").objects.link(cam)
    CAMS[name] = cam

SCN.render.resolution_x, SCN.render.resolution_y = 1600, 900
bpy.context.view_layer.update()

def fits(cam, subjects, margin):
    for s in subjects:
        ob = bpy.data.objects[s]
        for c in ob.bound_box:
            p = world_to_camera_view(SCN, cam, ob.matrix_world @ Vector(c))
            if not (margin <= p.x <= 1 - margin and margin <= p.y <= 1 - margin and p.z > 0):
                return False
    return True

FIT = {}
for name, (loc, target, fov, subjects) in SHOTS.items():
    cam = CAMS[name]
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
    moved = 0.0
    while not fits(cam, subjects, 0.06) and moved < 3.0:
        cam.location -= fwd * 0.05; moved += 0.05
        bpy.context.view_layer.update()
    FIT[name] = {"pulled_back_m": round(moved, 2), "final_loc": [round(v, 2) for v in cam.location]}

# ================================================================= CHECKS
# Structural gate: every prop inside the room, and each shot's subject both
# inside the frame and not hidden behind other geometry.
dg = bpy.context.evaluated_depsgraph_get()
report = {"props_outside_room": [], "shots": {}, "camera_fit": FIT}
report["cameras_outside_room"] = [n for n, c in CAMS.items()
    if not (-HX < c.location.x < HX and -HY < c.location.y < HY and 0 < c.location.z < H)]

GROUPS = [("desk", ("PRP_desk",)), ("chair", ("PRP_chair",)), ("bed", ("PRP_bed",)),
          ("chest", ("PRP_chest",)), ("lectern", ("PRP_lectern", "PRP_logbook")),
          ("rack", ("PRP_rack", "PRP_message")), ("cannon", ("PRP_cannon", "PRP_rope", "PRP_gunport")),
          ("shelf", ("PRP_bookshelf", "PRP_book_")), ("maps", ("PRP_map",)),
          ("seat", ("ENV_window_seat",)), ("lanterns", ("PRP_lantern",))]
def aabb(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))
members = {g: [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(pfx)]
           for g, pfx in GROUPS}
overlaps = []
gl = list(members)
for i in range(len(gl)):
    for j in range(i + 1, len(gl)):
        for a in members[gl[i]]:
            A0, A1 = aabb(a)
            for b in members[gl[j]]:
                B0, B1 = aabb(b)
                depth = min(min(A1[k], B1[k]) - max(A0[k], B0[k]) for k in range(3))
                if depth > 0.02:
                    overlaps.append(f"{a.name} x {b.name} ({depth:.2f}m)")
report["furniture_overlaps"] = overlaps
for ob in bpy.data.objects:
    if ob.type != "MESH" or not ob.name.startswith("PRP_"): continue
    for c in ob.bound_box:
        w = ob.matrix_world @ Vector(c)
        if not (-HX - 0.01 <= w.x <= HX + 0.01 and -HY - 0.01 <= w.y <= HY + 0.01 and -0.01 <= w.z <= H + 0.01):
            report["props_outside_room"].append(ob.name); break

for name, (loc, target, fov, subjects) in SHOTS.items():
    cam = CAMS[name]; SCN.camera = cam
    res = {}
    for sname in subjects:
        ob = bpy.data.objects[sname]
        pts = [world_to_camera_view(SCN, cam, ob.matrix_world @ Vector(c)) for c in ob.bound_box]
        xs = [p.x for p in pts]; ys = [p.y for p in pts]
        in_frame = all(0 <= p.x <= 1 and 0 <= p.y <= 1 and p.z > 0 for p in pts)
        cov = max(0, min(1, max(xs)) - max(0, min(xs))) * max(0, min(1, max(ys)) - max(0, min(ys)))
        centre = ob.matrix_world @ (sum((Vector(c) for c in ob.bound_box), Vector()) / 8)
        d = centre - cam.location
        hit, hloc, _, _, hob, _ = SCN.ray_cast(dg, cam.location, d.normalized(), distance=d.length + 0.05)
        res[sname] = {"fully_in_frame": in_frame, "frame_coverage": round(cov, 3),
                      "first_hit": hob.name if hit else None}
    report["shots"][name] = res

# ================================================================= RENDER
SCN.render.engine = "BLENDER_WORKBENCH"
sh = SCN.display.shading
sh.light = "STUDIO"; sh.color_type = "MATERIAL"
sh.show_shadows = True; sh.show_cavity = True; sh.cavity_type = "BOTH"
SCN.display.render_aa = "8"
SCN.view_settings.view_transform = "Standard"
SCN.view_settings.exposure = 1.2   # greybox readability only
renders = []
for name in SHOTS:
    SCN.camera = CAMS[name]
    SCN.render.filepath = os.path.join(OUT, "renders", f"greybox_{name[4:]}.png")
    bpy.ops.render.render(write_still=True)
    renders.append(SCN.render.filepath)

# Mood preview of the intro shot in EEVEE: lantern warmth against dusk windows.
SCN.render.engine = "BLENDER_EEVEE"
SCN.eevee.taa_render_samples = 64
if hasattr(SCN.eevee, "use_raytracing"): SCN.eevee.use_raytracing = True
SCN.view_settings.view_transform = "AgX"
SCN.view_settings.exposure = 0.0
SCN.camera = CAMS["CAM_intro"]
SCN.render.filepath = os.path.join(OUT, "renders", "mood_intro.png")
try:
    bpy.ops.render.render(write_still=True); renders.append(SCN.render.filepath)
    report["mood_render"] = "ok"
except Exception as e:
    report["mood_render"] = f"failed: {e}"

SCN.camera = CAMS["CAM_intro"]
SCN.render.engine = "BLENDER_WORKBENCH"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cabin-greybox.blend"))
report["renders"] = renders
report["objects"] = len(bpy.data.objects)
print("REPORT " + json.dumps(report))
