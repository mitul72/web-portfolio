"""Interactive props: the things on the islands that ARE the navigation, as
the cabin concept had it. Every prop is its own object named POI_<stop>[_<n>]
so the app can hover-glow it, tag it, and fly the camera to it; moving parts
(the anemometer rotor, the chest lid, the signal flags) are separate objects
with their pivot at the object origin.

All builders take a base point on the ground and a yaw (the direction the
prop faces, radians about +Z, 0 = facing -Y) and return the created objects.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import build as B
from . import materials as M
from .rocks import mesh_object

V = Vector


def _xf(at, yaw):
    return Matrix.Translation(V(at)) @ Matrix.Rotation(yaw, 4, "Z")


def text_mesh(name, text, size, at, yaw, depth=0.02, align="CENTER"):
    """Real lettering: a Blender text object converted to a mesh, standing
    upright, facing -Y after `yaw`."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = text
    cu.size = size
    cu.extrude = depth
    cu.align_x = align
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (math.pi / 2, 0, yaw)
    ob.location = at
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    out = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(out)
    out.matrix_world = Matrix.Translation(V(at)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(math.pi / 2, 4, "X")
    return out


def _ink(ob):
    for m in B.all_materials():
        ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.material_index = B.CLOTH


# --------------------------------------------------------------------------
# About: a WANTED poster on a notice board at the pier head
# --------------------------------------------------------------------------

def wanted_board(rnd, at, yaw, name="MITUL DHAWAN", title="SOFTWARE ENGINEER"):
    b = B.Builder(rnd)
    b.xf = _xf(at, yaw)
    W, H = 3.6, 2.6
    for s in (-1, 1):
        b.box((s * W / 2, 0, 1.9), (0.2, 0.2, 3.8), B.TIMBER)
    for i in range(int(H / 0.3)):
        b.box((0, 0.05, 1.3 + i * 0.3), (W - 0.1, 0.1, 0.29), B.WALL, tint=rnd.random(), paint=0.0)
    b.box((0, 0.1, 1.3 + H + 0.2), (W + 0.8, 1.0, 0.1), B.ROOF, rot=(0.35, 0, 0), paint=0.3)
    B.lantern(b, V((W / 2 + 0.2, -0.5, 3.6)), 0.3)
    b.cyl((W / 2, 0, 3.8), (W / 2 + 0.25, -0.5, 3.85), 0.04, B.IRON, sides=4)
    # the poster: parchment, pinned, a little skewed
    b.box((0, -0.03, 2.55), (1.9, 0.04, 2.3), B.CANVAS, rot=(0, 0.03, 0), tint=0.8)
    # a smaller torn notice beside it
    b.box((-1.25, -0.03, 2.1), (0.7, 0.03, 0.9), B.CANVAS, rot=(0, -0.08, 0), tint=0.5)
    for x, z in ((-0.85, 3.6), (0.85, 3.6), (-0.85, 1.5), (0.85, 1.5)):
        b.box((x, -0.07, z), (0.06, 0.04, 0.06), B.IRON)
    board = b.object("POI_intro", bevel=0.02)
    # lettering (ink), slightly proud of the parchment
    front = -0.075
    wx = Matrix.Translation(V(at)) @ Matrix.Rotation(yaw, 4, "Z")
    parts = [
        ("WANTED", 0.42, 3.35),
        (name, 0.2, 1.95),
        (title, 0.12, 1.72),
        ("REWARD: A GOOD CONVERSATION", 0.085, 1.52),
    ]
    for i, (txt, size, z) in enumerate(parts):
        t = text_mesh(f"POI_intro_text_{i}", txt, size, wx @ V((0, front, z)), yaw)
        _ink(t)
        t.parent = board
        t.matrix_parent_inverse = board.matrix_world.inverted()
    # portrait: a sketched oval frame with a tricorn silhouette
    pb = B.Builder(rnd)
    pb.xf = b.xf
    c = V((0, front, 2.65))
    for k in range(16):
        a = k / 16 * math.tau
        pb.box(c + V((math.cos(a) * 0.5, 0, math.sin(a) * 0.55)), (0.12, 0.01, 0.05), B.CLOTH,
               rot=(0, -a, 0))
    pb.box(c + V((0, 0, -0.12)), (0.36, 0.01, 0.46), B.CLOTH)  # head + shoulders
    pb.box(c + V((0, 0, 0.2)), (0.62, 0.01, 0.12), B.CLOTH)  # tricorn brim
    pb.box(c + V((0, 0, 0.3)), (0.36, 0.01, 0.14), B.CLOTH)
    pb.box(c + V((0, 0, -0.42)), (0.7, 0.01, 0.2), B.CLOTH)
    portrait = pb.object("POI_intro_portrait", bevel=0)
    portrait.parent = board
    portrait.matrix_parent_inverse = board.matrix_world.inverted()
    return [board]


# --------------------------------------------------------------------------
# Projects: four props at the Ember Isle camp, one per project
# --------------------------------------------------------------------------

def telemetry_mast(rnd, at, yaw, key):
    """fast-telemetry: a weather station. Mast, instrument box with dials,
    and a cup anemometer (separate rotor, spins in the app)."""
    b = B.Builder(rnd)
    b.xf = _xf(at, yaw)
    b.cyl((0, 0, 0), (0, 0, 7.0), 0.26, B.TIMBER, sides=8, r2=0.16)
    b.box((0, 0, 0.25), (1.2, 1.2, 0.5), B.STONE)  # footing
    for a in (0, 2.1, 4.2):  # guy ropes
        b.cyl((math.cos(a) * 2.4, math.sin(a) * 2.4, 0.1), (0, 0, 5.5), 0.025, B.TIMBER, sides=4)
        b.box((math.cos(a) * 2.4, math.sin(a) * 2.4, 0.15), (0.3, 0.3, 0.3), B.STONE)
    # instrument cabinet with a little pitched roof and three brass dials
    b.box((0, -0.45, 1.6), (1.6, 0.8, 1.6), B.WALL, paint=0.3)
    b.box((0, -0.45, 2.5), (1.9, 1.1, 0.1), B.ROOF, rot=(0.25, 0, 0), paint=0.3)
    for i, (x, z) in enumerate(((-0.4, 1.95), (0.4, 1.95), (0, 1.3))):
        b.cyl((x, -0.86, z), (x, -0.9, z), 0.26, B.GOLD, sides=14)
        b.cyl((x, -0.9, z), (x, -0.91, z), 0.2, B.CANVAS, sides=14, tint=0.9)
        b.box((x + 0.06, -0.92, z + 0.04), (0.18, 0.01, 0.03), B.CLOTH, rot=(0, 0.3 + i, 0))
    B.lantern(b, V((0.95, -0.9, 2.2)), 0.25)
    # weather vane arrow
    b.box((0, 0, 6.2), (0.06, 1.6, 0.06), B.IRON)
    b.box((0, 0.8, 6.2), (0.02, 0.4, 0.3), B.IRON)
    b.box((0, -0.8, 6.2), (0.02, 0.3, 0.2), B.GOLD, rot=(0.785, 0, 0))
    body = b.object(f"POI_{key}", bevel=0.02)
    # rotor: three cups on arms, origin on the spin axis
    rb = B.Builder(rnd)
    for k in range(3):
        a = k / 3 * math.tau
        d = V((math.cos(a), math.sin(a), 0))
        rb.cyl((0, 0, 0), d * 1.3, 0.05, B.IRON, sides=4)
        c = d * 1.3 + V((-d.y, d.x, 0)) * 0.18
        rb.cyl(c - V((-d.y, d.x, 0)) * 0.18, c + V((-d.y, d.x, 0)) * 0.18, 0.32, B.GOLD, sides=12, r2=0.08)
    rb.cyl((0, 0, -0.1), (0, 0, 0.1), 0.08, B.IRON, sides=8)
    rotor = rb.object(f"POI_{key}_rotor", bevel=0)
    rotor.location = _xf(at, yaw) @ V((0, 0, 7.05))
    rotor.parent = body
    rotor.matrix_parent_inverse = body.matrix_world.inverted()
    return [body, rotor]


def calc_engine(rnd, at, yaw, key):
    """Intel 8080 emulator: a brass calculating engine in a wooden case, its
    green glass showing a little space invader in lit pixels."""
    b = B.Builder(rnd)
    b.xf = _xf(at, yaw)
    b.box((0, 0, 0.9), (2.4, 1.3, 1.8), B.WALL, paint=0.8)
    b.box((0, 0, 1.85), (2.6, 1.5, 0.12), B.TIMBER)
    for x in (-1.15, 1.15):
        b.box((x, 0, 0.9), (0.14, 1.36, 1.84), B.TIMBER)
    # gear train on the front: brass wheels of different sizes, meshing
    for (x, z, r) in ((-0.8, 0.55, 0.36), (-0.3, 0.72, 0.24), (0.1, 0.5, 0.3), (0.55, 0.62, 0.2), (0.85, 0.42, 0.16)):
        b.cyl((x, -0.66, z), (x, -0.74, z), r, B.GOLD, sides=14)
        for k in range(10):
            a = k / 10 * math.tau
            b.box((x + math.cos(a) * r, -0.7, z + math.sin(a) * r), (0.06, 0.06, 0.06), B.GOLD)
        b.cyl((x, -0.74, z), (x, -0.8, z), 0.05, B.IRON, sides=6)
    # screen with the invader
    b.box((0, -0.66, 1.35), (1.3, 0.05, 0.62), B.IRON)
    b.box((0, -0.68, 1.35), (1.14, 0.03, 0.5), B.GLOW, paint=0.0)
    invader = ["..X.....X..", "...X...X...", "..XXXXXXX..", ".XX.XXX.XX.", "XXXXXXXXXXX",
               "X.XXXXXXX.X", "X.X.....X.X", "...XX.XX..."]
    px = 0.07
    for r, row in enumerate(invader):
        for c, ch in enumerate(row):
            if ch == "X":
                b.box(((c - 5) * px, -0.71, 1.35 + (3.5 - r) * px), (px * 0.9, 0.02, px * 0.9), B.CLOTH)
    # crank handle and a punched-tape spool
    b.cyl((1.25, 0, 1.0), (1.55, 0, 1.0), 0.06, B.IRON, sides=6)
    b.box((1.55, 0, 0.8), (0.06, 0.06, 0.45), B.IRON)
    b.cyl((1.55, -0.12, 0.6), (1.55, 0.12, 0.6), 0.07, B.TIMBER, sides=6)
    b.cyl((-1.1, 0.1, 2.15), (-0.5, 0.1, 2.15), 0.22, B.CANVAS, sides=12)
    return [b.object(f"POI_{key}", bevel=0.02)]


def trade_stall(rnd, at, yaw, key):
    """ZeroBlock: a trader's stall. Striped awning, a counter with balance
    scales, stacks of gold, and an hourglass (it's about speed)."""
    b = B.Builder(rnd)
    b.xf = _xf(at, yaw)
    W, D = 3.2, 1.8
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box((sx * W / 2, sy * D / 2, 1.4), (0.14, 0.14, 2.8 + (0.5 if sy > 0 else 0)), B.TIMBER)
    # awning: alternating canvas and oxblood stripes, sloping to the front
    for i in range(8):
        x = -W / 2 - 0.2 + (i + 0.5) * (W + 0.4) / 8
        mat, paint = (B.CANVAS, 0.0) if i % 2 else (B.LIVERY, 1.0)
        b.box((x, 0, 3.05), ((W + 0.4) / 8, D + 0.8, 0.05), mat, rot=(-0.3, 0, 0), paint=paint, tint=0.1)
    for i in range(8):  # scalloped valance
        x = -W / 2 - 0.2 + (i + 0.5) * (W + 0.4) / 8
        mat, paint = (B.CANVAS, 0.0) if i % 2 else (B.LIVERY, 1.0)
        b.box((x, -D / 2 - 0.55, 2.78), ((W + 0.4) / 8, 0.03, 0.35), mat, paint=paint, tint=0.1)
    b.box((0, -0.3, 0.55), (W, 1.0, 1.1), B.WALL, paint=0.55)
    b.box((0, -0.3, 1.13), (W + 0.2, 1.2, 0.08), B.TIMBER)
    # balance scales
    b.box((-0.6, -0.4, 1.6), (0.06, 0.06, 0.9), B.GOLD)
    b.box((-0.6, -0.4, 2.02), (1.0, 0.05, 0.05), B.GOLD, rot=(0, 0.12, 0))
    for s, dz in ((-1, -0.06), (1, 0.06)):
        b.cyl((-0.6 + s * 0.48, -0.4, 1.5 + dz), (-0.6 + s * 0.48, -0.4, 1.52 + dz), 0.18, B.GOLD, sides=12)
    # coin stacks and a spilled heap
    for i in range(5):
        x = 0.2 + (i % 3) * 0.28
        h = rnd.randint(3, 9)
        for k in range(h):
            b.cyl((x, -0.5 + (i // 3) * 0.3, 1.18 + k * 0.045), (x, -0.5 + (i // 3) * 0.3, 1.21 + k * 0.045),
                  0.1, B.GOLD, sides=10)
    # hourglass
    hx = 1.2
    b.box((hx, -0.4, 1.19), (0.4, 0.4, 0.06), B.TIMBER)
    b.box((hx, -0.4, 1.81), (0.4, 0.4, 0.06), B.TIMBER)
    for sx in (-1, 1):
        b.box((hx + sx * 0.16, -0.4, 1.5), (0.04, 0.04, 0.6), B.TIMBER)
    b.cyl((hx, -0.4, 1.22), (hx, -0.4, 1.5), 0.16, B.GOLD, sides=10, r2=0.02)
    b.cyl((hx, -0.4, 1.5), (hx, -0.4, 1.78), 0.02, B.GOLD, sides=10, r2=0.16)
    # goods behind: a chest and sacks
    B.crate(b, V((-1.0, 0.5, 0)), rnd, 0.9)
    B.barrel(b, V((0.9, 0.55, 0)), rnd, h=1.0, r=0.38)
    B.lantern(b, V((W / 2 - 0.2, -D / 2 - 0.2, 2.5)), 0.25)
    return [b.object(f"POI_{key}", bevel=0.02)]


def scholar_lectern(rnd, at, yaw, key):
    """Stack.CLI: a scholar's lectern with an open book, and a teetering stack
    of books beside it, a quill in the inkwell, a candle-lantern."""
    b = B.Builder(rnd)
    b.xf = _xf(at, yaw)
    b.box((0, 0, 0.6), (0.3, 0.3, 1.2), B.TIMBER)
    b.box((0, 0, 0.05), (0.9, 0.9, 0.1), B.TIMBER)
    b.box((0, -0.05, 1.3), (1.2, 0.8, 0.08), B.WALL, rot=(0.35, 0, 0), paint=0.8)
    # open book: two page blocks and a cover
    for s in (-1, 1):
        b.box((s * 0.27, -0.08, 1.4), (0.5, 0.62, 0.07), B.CANVAS, rot=(0.35, s * -0.08, 0), tint=0.9)
    b.box((0, -0.06, 1.35), (1.1, 0.7, 0.03), B.LIVERY, rot=(0.35, 0, 0), paint=1.0)
    # the stack: 14 books, each a little off-square, covers in different colours
    z = 0.0
    for i in range(14):
        th = rnd.uniform(0.09, 0.16)
        w, d = rnd.uniform(0.55, 0.75), rnd.uniform(0.4, 0.55)
        rot = (0, 0, rnd.uniform(-0.25, 0.25))
        paint = rnd.choice((0.0, 1.0))
        b.box((1.1 + rnd.uniform(-0.05, 0.05), 0.1, z + th / 2), (w, d, th), B.LIVERY, rot=rot, paint=paint,
              tint=rnd.uniform(0, 0.6))
        b.box((1.1 + rnd.uniform(-0.04, 0.04), 0.1 - 0.02, z + th / 2), (w - 0.06, d - 0.02, th - 0.03), B.CANVAS,
              rot=rot, tint=0.8)
        z += th
    # inkwell + quill
    b.cyl((-0.45, 0.1, 1.46), (-0.45, 0.1, 1.56), 0.06, B.CLOTH, sides=8)
    b.cyl((-0.45, 0.1, 1.5), (-0.3, 0.2, 2.0), 0.02, B.CANVAS, sides=4, r2=0.06)
    B.lantern(b, V((-0.7, 0.4, 0.3)), 0.25)
    return [b.object(f"POI_{key}", bevel=0.015)]


# --------------------------------------------------------------------------
# Resume: the treasure chest, lid as its own hinged piece (modelled CLOSED)
# --------------------------------------------------------------------------

def chest(rnd, at, yaw, key, scale=1.6):
    W, D, H = 1.6 * scale, 1.0 * scale, 0.8 * scale
    b = B.Builder(rnd)
    b.xf = _xf(at, yaw)
    b.box((0, 0, H / 2), (W, D, H), B.LIVERY, paint=1.0, tint=0.3)
    for x in (-W / 2 + 0.2 * scale, 0, W / 2 - 0.2 * scale):
        b.box((x, 0, H / 2), (0.12 * scale, D + 0.06, H + 0.04), B.IRON)
    for i in range(30):  # the hoard, visible when the lid lifts
        c = V((rnd.uniform(-0.62, 0.62) * scale, rnd.uniform(-0.36, 0.36) * scale, H - 0.1 + rnd.uniform(-0.02, 0.12)))
        b.box(c, (0.22, 0.22, 0.05), B.GOLD, rot=(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, 3)))
    b.box((0, 0, H - 0.1), (W - 0.12, D - 0.12, 0.12), B.GOLD)
    b.box((0, -D / 2 - 0.04, H - 0.15 * scale), (0.22 * scale, 0.06, 0.28 * scale), B.GOLD)  # lock plate
    body = b.object(f"POI_{key}", bevel=0.02)
    # lid: origin on the hinge line (back top edge); rotate about local X
    lb = B.Builder(rnd)
    Lh = 0.4 * scale
    for k in range(6):  # a barrel-top lid from staves
        a0 = k / 6 * math.pi
        a1 = (k + 1) / 6 * math.pi
        am = (a0 + a1) / 2
        y = -D / 2 + D / 2 * (1 - math.cos(am))
        zz = Lh * math.sin(am)
        lb.box((0, y, zz), (W, D / 6 * 1.1, 0.06), B.LIVERY, rot=(-(am - math.pi / 2), 0, 0), paint=1.0, tint=0.3)
    for x in (-W / 2 + 0.2 * scale, W / 2 - 0.2 * scale):
        for k in range(6):
            am = (k + 0.5) / 6 * math.pi
            y = -D / 2 + D / 2 * (1 - math.cos(am))
            lb.box((x, y, Lh * math.sin(am) + 0.03), (0.13 * scale, D / 6 * 1.15, 0.05), B.IRON,
                   rot=(-(am - math.pi / 2), 0, 0))
    lid = lb.object(f"POI_{key}_lid", bevel=0.01)
    # mesh was built around the chest centre; shift so the origin is the hinge
    hinge = V((0, D / 2, 0))
    lid.data.transform(Matrix.Translation(-hinge))
    lid.matrix_world = _xf(at, yaw) @ Matrix.Translation(V((0, D / 2, H)))
    lid.parent = body
    lid.matrix_parent_inverse = body.matrix_world.inverted()
    return [body, lid]


# --------------------------------------------------------------------------
# Experience: a signal mast with four flags (one per job)
# --------------------------------------------------------------------------

def signal_material():
    """Signal-flag bunting: `paint` picks one of four colours."""
    m = bpy.data.materials.get("signal")
    if m:
        return m
    from .nodes import material
    m, g, bsdf = material("signal")
    paint = g.node("ShaderNodeAttribute", attribute_name="paint").outputs["Fac"]
    col = g.ramp(paint, [(0.0, (0.5, 0.04, 0.03)), (0.33, (0.85, 0.55, 0.06)), (0.66, (0.04, 0.16, 0.45)),
                         (1.0, (0.06, 0.3, 0.12))])
    ramp = col.node
    ramp.color_ramp.interpolation = "CONSTANT"
    g.link(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    m.use_backface_culling = False
    return M.fogged(m, g)


def signal_mast(rnd, at, yaw, key, n=4):
    b = B.Builder(rnd)
    b.xf = _xf(at, yaw)
    b.cyl((0, 0, 0), (0, 0, 13.0), 0.2, B.TIMBER, sides=8, r2=0.12)
    b.cyl((-4.2, 0, 11.0), (4.2, 0, 11.0), 0.1, B.TIMBER, sides=6)  # the yard
    b.box((0, 0, 13.1), (0.3, 0.3, 0.3), B.GOLD)
    for a in (0.6, 2.6, 4.6):
        b.cyl((math.cos(a) * 3.0, math.sin(a) * 3.0, 0.1), (0, 0, 10.5), 0.03, B.TIMBER, sides=4)
        b.box((math.cos(a) * 3.0, math.sin(a) * 3.0, 0.15), (0.35, 0.35, 0.3), B.STONE)
    body = b.object(f"POI_{key}", bevel=0.02)
    flags = [body]
    mat = signal_material()
    for i in range(n):
        # hoisted from the yard at evenly spaced points, hanging down, each
        # with its own colour and a simple device (bar, cross, disc, border)
        x = -3.3 + i * (6.6 / (n - 1))
        bm = bmesh.new()
        paint_l = bm.faces.layers.float.new("paint")
        fw, fh = 1.3, 1.9
        rows = []
        for j in range(9):
            row = []
            for k in range(6):
                u, v = k / 5, j / 8
                row.append(bm.verts.new((u * fw - fw / 2, 0, -v * fh)))
            rows.append(row)
        for j in range(8):
            for k in range(5):
                f = bm.faces.new((rows[j][k], rows[j][k + 1], rows[j + 1][k + 1], rows[j + 1][k]))
                f[paint_l] = i / 3
        me = bpy.data.meshes.new(f"POI_{key}_{i}")
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(mat)
        fl = bpy.data.objects.new(f"POI_{key}_{i}", me)
        bpy.context.scene.collection.objects.link(fl)
        fl.matrix_world = _xf(at, yaw) @ Matrix.Translation(V((x, 0, 10.95)))
        # device on both faces, in canvas white
        db = B.Builder(rnd)
        for s in (-1, 1):
            if i == 0:
                db.box((0, s * 0.02, -fh / 2), (fw, 0.01, 0.35), B.CANVAS, tint=1.0)
            elif i == 1:
                db.box((0, s * 0.02, -fh / 2), (0.25, 0.01, fh), B.CANVAS, tint=1.0)
                db.box((0, s * 0.02, -fh / 2), (fw, 0.01, 0.25), B.CANVAS, tint=1.0)
            elif i == 2:
                db.cyl((0, s * 0.02, -fh / 2), (0, s * 0.03, -fh / 2), 0.35, B.CANVAS, sides=16, tint=1.0)
            else:
                for dx, dz, sw, sh in ((0, -0.12, fw, 0.2), (0, -fh + 0.12, fw, 0.2), (-fw / 2 + 0.1, -fh / 2, 0.2, fh),
                                       (fw / 2 - 0.1, -fh / 2, 0.2, fh)):
                    db.box((dx, s * 0.02, dz), (sw, 0.01, sh), B.CANVAS, tint=1.0)
        dev = db.object(f"POI_{key}_{i}_device", bevel=0)
        dev.matrix_world = fl.matrix_world
        dev.parent = fl
        dev.matrix_parent_inverse = fl.matrix_world.inverted()
        fl.parent = body
        fl.matrix_parent_inverse = body.matrix_world.inverted()
        flags.append(fl)
    return flags


# --------------------------------------------------------------------------
# Contact: a message bottle on a stone pedestal
# --------------------------------------------------------------------------

def bottle_glass():
    m = bpy.data.materials.get("bottle_glass")
    if m:
        return m
    from .nodes import material
    m, g, bsdf = material("bottle_glass")
    bsdf.inputs["Base Color"].default_value = (0.12, 0.38, 0.26, 1)
    bsdf.inputs["Roughness"].default_value = 0.08
    bsdf.inputs["Alpha"].default_value = 0.55
    bsdf.inputs["Emission Color"].default_value = (0.2, 0.55, 0.38, 1)
    bsdf.inputs["Emission Strength"].default_value = 0.6
    m.surface_render_method = "BLENDED"  # alpha < 1 exports as glTF BLEND
    return m


def message_bottle(rnd, at, yaw, key):
    b = B.Builder(rnd)
    b.xf = _xf(at, yaw)
    # pedestal: stacked, weathered stone drums
    z = 0.0
    for i, (r, h) in enumerate(((0.9, 0.35), (0.7, 0.6), (0.62, 0.3), (0.8, 0.22))):
        b.cyl((0, 0, z), (0, 0, z + h), r, B.STONE, sides=9, tint=rnd.random())
        z += h
    top = z
    # rope coil and the scroll-in-bottle lying in a cradle
    for k in range(3):
        b.cyl((0.5, 0.35, top + 0.05 + k * 0.07), (0.5, 0.35, top + 0.1 + k * 0.07), 0.28 - k * 0.03, B.WALL,
              sides=12, paint=0.55)
    for s in (-1, 1):
        b.box((s * 0.35, -0.05, top + 0.12), (0.12, 0.5, 0.2), B.TIMBER)
    body = b.object(f"POI_{key}", bevel=0.02)
    # the bottle itself: lathe-turned glass, a cork, a rolled letter inside
    bm = bmesh.new()
    prof = [(0.0, 0.0), (0.3, 0.02), (0.34, 0.15), (0.34, 0.95), (0.3, 1.1), (0.14, 1.3), (0.11, 1.55),
            (0.13, 1.6), (0.0, 1.6)]
    rings = []
    for r, h in prof:
        ring = []
        for k in range(16):
            a = k / 16 * math.tau
            ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, h)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(16):
            k2 = (k + 1) % 16
            bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
    glass = mesh_object(f"POI_{key}_glass", bm)
    for p in glass.data.polygons:
        p.use_smooth = True
    glass.data.materials.append(bottle_glass())
    # lie it in the cradle, neck out to sea
    glass.matrix_world = _xf(at, yaw) @ Matrix.Translation(V((-0.8, -0.05, top + 0.55))) @ Matrix.Rotation(
        math.pi / 2, 4, "Y")
    ib = B.Builder(rnd)
    ib.cyl((0, 0, 0.2), (0, 0, 1.0), 0.16, B.CANVAS, sides=10, tint=0.9)  # the letter
    ib.cyl((0, 0, 1.52), (0, 0, 1.72), 0.12, B.WALL, sides=8, paint=0.55)  # cork
    ib.box((0, 0, 0.6), (0.34, 0.02, 0.1), B.LIVERY, paint=1.0)  # ribbon
    inner = ib.object(f"POI_{key}_letter", bevel=0)
    inner.matrix_world = glass.matrix_world
    for o in (glass, inner):
        o.parent = body
        o.matrix_parent_inverse = body.matrix_world.inverted()
    return [body, glass, inner]
