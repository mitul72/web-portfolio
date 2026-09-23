"""The player's ship: a three-masted pirate galleon, ~34 m on deck, built from
real hull sections and board by board, in the same kit as the islands.

Frame: bow toward +Y, waterline at z = 0, centred on the mainmast. Returns
separate objects so the app can animate them:
  SHP_hull   hull, decks, masts, yards, rigging, fittings (one mesh)
  SHP_sail_* each sail (billows in the wind in the app)
  SHP_flag   the black flag at the main truck (waves)
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import build as B

V = Vector

Y_STERN, Y_BOW = -15.0, 17.0
BEAM = 5.4  # max half-beam


# --------------------------------------------------------------------------
# Hull form
# --------------------------------------------------------------------------

def t_of(y):
    return (y - Y_STERN) / (Y_BOW - Y_STERN)


def y_of(t):
    return Y_STERN + t * (Y_BOW - Y_STERN)


def half_beam(t):
    if t < 0.45:
        return BEAM * (0.72 + 0.28 * math.sin(t / 0.45 * math.pi / 2))
    u = min(1.0, (t - 0.45) / 0.55)
    return BEAM * max(0.0, math.cos(u * math.pi / 2)) ** 0.72


def keel_z(t):
    return -2.6 + 1.6 * max(0.0, (t - 0.8) / 0.2) ** 1.5 + 0.5 * max(0.0, (0.1 - t) / 0.1)


def sheer_z(t):
    return 3.9 + 2.6 * max(0.0, (0.3 - t) / 0.3) ** 0.8 + 1.4 * max(0.0, (t - 0.78) / 0.22) ** 1.4


def section(t, v):
    """Half-width and height of the hull surface at length t, girth v (0 keel,
    1 sheer): round bilge, a little tumblehome up top."""
    z = keel_z(t) + (sheer_z(t) - keel_z(t)) * v
    s = math.sin(min(1.0, v * 1.12) * math.pi / 2) ** 0.55
    tumble = 1 - 0.1 * max(0.0, (v - 0.7) / 0.3) ** 2
    return half_beam(t) * s * tumble, z


def v_at_z(t, z):
    k, s = keel_z(t), sheer_z(t)
    return max(0.0, min(1.0, (z - k) / (s - k)))


def width_at(t, z):
    return section(t, v_at_z(t, z))[0]


# Strakes: (v0, v1, material, paint, stand-out). Paint indexes the wall ramp:
# LIVERY paint: 0 deep teal, 1 oxblood.
STRAKES = [(0.0, 0.42, B.TIMBER, 0.0, 0.0)]
v = 0.42
while v < 0.58:
    STRAKES.append((v, v + 0.04, B.TIMBER, 0.0, 0.0))  # dark oiled planking
    v += 0.04
STRAKES += [
    (0.58, 0.62, B.TIMBER, 0.0, 0.12),  # lower wale
    (0.62, 0.66, B.LIVERY, 1.0, 0.0),
    (0.66, 0.70, B.LIVERY, 1.0, 0.0),
    (0.70, 0.74, B.LIVERY, 1.0, 0.0),
    (0.74, 0.77, B.GOLD, 0.0, 0.03),  # gilt moulding
    (0.77, 0.81, B.TIMBER, 0.0, 0.1),  # upper wale
]
v = 0.81
while v < 0.999:
    STRAKES.append((v, min(1.0, v + 0.0475), B.LIVERY, 0.0, 0.0))  # deep teal bulwarks
    v += 0.0475


def _normal(t, v, eps=0.01):
    x0, z0 = section(t, max(0.0, v - eps))
    x1, z1 = section(t, min(1.0, v + eps))
    tx, tz = x1 - x0, z1 - z0
    n = V((tz, -tx))  # outward for the starboard (+x) side
    return n.normalized() if n.length > 1e-6 else V((1, 0))


def hull(b, rnd, nt=56):
    ts = [i / nt for i in range(nt + 1)]
    for v0, v1, mat, paint, out in STRAKES:
        # low tint = little wear, so painted strakes keep their colour
        tint = rnd.uniform(0.0, 0.3) if mat == B.LIVERY else rnd.random()
        for side in (1, -1):
            rows = []
            for t in ts:
                row = []
                for vv, lap in ((v0, 0.045), (v1, 0.0)):
                    x, z = section(t, vv)
                    n = _normal(t, vv)
                    off = lap + out
                    row.append(b.bm.verts.new((side * (x + n.x * off), y_of(t), z + n.y * off)))
                rows.append(row)
            faces = []
            for r0, r1 in zip(rows, rows[1:]):
                q = (r0[0], r1[0], r1[1], r0[1])
                faces.append(b.bm.faces.new(q if side == 1 else tuple(reversed(q))))
            b._tag(faces, mat, tint=tint + rnd.uniform(-0.1, 0.1), paint=paint)
    # Transom: close the stern with a painted panel.
    pts = []
    for i in range(24 + 1):
        vv = i / 24
        x, z = section(0.0, vv)
        pts.append(V((x, Y_STERN - 0.02, z)))
    ring = pts + [V((-p.x, p.y, p.z)) for p in reversed(pts)]
    verts = [b.bm.verts.new(p) for p in ring]
    f = b.bm.faces.new(verts)
    b._tag([f], B.LIVERY, tint=0.2, paint=1.0)
    # Stem post and keel.
    for i in range(12):
        t0, t1 = 0.78 + i * 0.02, 0.78 + (i + 1) * 0.02
        z0, z1 = keel_z(t0), keel_z(t1)
        a, c = V((0, y_of(t0), z0)), V((0, y_of(t1), z1))
        b.cyl(a, c, 0.22, B.TIMBER, sides=6)
    b.cyl((0, y_of(1.0), keel_z(1.0)), (0, y_of(1.0) + 0.6, sheer_z(1.0) + 0.6), 0.25, B.TIMBER, sides=6)


# --------------------------------------------------------------------------
# Decks, bulkheads, rails
# --------------------------------------------------------------------------

MAIN_Z, QD_Z, FC_Z = 3.0, 5.4, 4.6
QD_T, FC_T = 0.3, 0.78


def deck(b, rnd, z, t0, t1, plank=0.32):
    half = max(width_at(t, z) for t in [t0 + (t1 - t0) * i / 40 for i in range(41)])
    x = -half
    while x < half:
        inside = [t for t in [t0 + (t1 - t0) * i / 120 for i in range(121)] if width_at(t, z) - 0.25 > abs(x) + plank / 2]
        if inside:
            ya, yb = y_of(min(inside)), y_of(max(inside))
            b.box((x + plank / 2, (ya + yb) / 2, z), (plank - 0.025, yb - ya, 0.12), B.WALL,
                  tint=rnd.random(), paint=0.0)
        x += plank


def bulkhead(b, rnd, t, z0, z1, facing, door=True, windows=2):
    """Planked wall across the ship at length t, from z0 to z1, facing
    +1 (forward) or -1 (aft), with a door, windows and lanterns."""
    y = y_of(t)
    w = width_at(t, z0) - 0.2
    for i in range(int((z1 - z0) / 0.3)):
        z = z0 + 0.15 + i * 0.3
        b.box((0, y, z), (2 * w, 0.1, 0.32), B.WALL, rot=(rnd.uniform(-0.06, -0.02) * facing, 0, 0),
              tint=rnd.random(), paint=0.3)
    b.box((0, y + facing * 0.05, z1), (2 * w + 0.2, 0.3, 0.25), B.TIMBER)
    if door:
        b.box((0, y + facing * 0.08, z0 + 1.0), (1.0, 0.1, 2.0), B.TIMBER)
        B.lantern(b, V((1.1, y + facing * 0.4, z0 + 2.0)), 0.25)
        B.lantern(b, V((-1.1, y + facing * 0.4, z0 + 2.0)), 0.25)
    for k in range(windows):
        x = (k - (windows - 1) / 2) * (w * 1.1)
        if abs(x) < 1.4:
            x = math.copysign(2.2, x or 1)
        b.box((x, y + facing * 0.08, z0 + 1.4), (0.9, 0.08, 0.8), B.GLOW)
        b.box((x, y + facing * 0.12, z0 + 1.4), (1.1, 0.06, 0.12), B.TIMBER)
        b.box((x, y + facing * 0.12, z0 + 1.4), (0.08, 0.06, 1.0), B.TIMBER)


def balustrade(b, rnd, t, z, facing):
    """Turned-baluster railing along a raised deck's edge."""
    y = y_of(t) + facing * 0.1
    w = width_at(t, z) - 0.3
    b.box((0, y, z + 1.0), (2 * w, 0.14, 0.12), B.TIMBER)
    b.box((0, y, z + 0.08), (2 * w, 0.14, 0.12), B.TIMBER)
    x = -w
    while x <= w:
        b.cyl((x, y, z + 0.1), (x, y, z + 1.0), 0.05, B.TIMBER, sides=6, r2=0.035)
        x += 0.28


def cap_rail(b):
    ts = [i / 60 for i in range(61)]
    for side in (1, -1):
        for t0, t1 in zip(ts, ts[1:]):
            x0, z0 = section(t0, 1.0)
            x1, z1 = section(t1, 1.0)
            a, c = V((side * x0, y_of(t0), z0 + 0.08)), V((side * x1, y_of(t1), z1 + 0.08))
            d = c - a
            b.box((a + c) / 2, (0.28, d.length + 0.05, 0.16), B.TIMBER, rot=(math.atan2(d.z, d.y), 0, 0))


def stairs(b, x, t, z0, z1, facing):
    """Short ladder-stair up to a raised deck (facing +1 climbs aft->fwd)."""
    y1 = y_of(t)
    n = int((z1 - z0) / 0.3)
    for i in range(n):
        u = (i + 0.5) / n
        b.box((x, y1 + facing * (1.0 - u) * 2.2, z0 + u * (z1 - z0)), (1.2, 0.3, 0.08), B.WALL, paint=0.0)
    for s in (-1, 1):
        a = V((x + s * 0.6, y1 + facing * 2.2, z0))
        c = V((x + s * 0.6, y1, z1 + 0.9))
        b.cyl(a, c, 0.05, B.TIMBER, sides=6)


# --------------------------------------------------------------------------
# Masts, yards, sails, rigging
# --------------------------------------------------------------------------

BRACE = math.radians(22)  # yards braced round to starboard

MASTS = {
    # name: (t, base z, height, [yard (frac of height, length)])
    "fore": (0.74, MAIN_Z, 22.0, [(0.36, 12.5), (0.68, 9.5), (0.9, 6.0)]),
    "main": (0.47, MAIN_Z, 27.0, [(0.34, 15.0), (0.66, 11.0), (0.89, 7.0)]),
    "mizzen": (0.17, QD_Z, 17.0, []),
}


def sail_mesh(name, corners, rnd, billow, u_seg=12, v_seg=10, bulge_dir=V((0, 1, 0)), panels=8):
    """A cloth quad (tl, tr, br, bl) billowed along bulge_dir."""
    tl, tr, br, bl = (V(c) for c in corners)
    bm = bmesh.new()
    tint = bm.faces.layers.float.new("tint")
    paint = bm.faces.layers.float.new("paint")
    grid = []
    for j in range(v_seg + 1):
        v = j / v_seg
        row = []
        for i in range(u_seg + 1):
            u = i / u_seg
            top = tl.lerp(tr, u)
            bot = bl.lerp(br, u)
            p = top.lerp(bot, v)
            depth = billow * math.sin(math.pi * u) * (0.25 + 0.75 * math.sin(math.pi * min(1.0, v * 0.95)))
            row.append(bm.verts.new(p + bulge_dir * depth))
        grid.append(row)
    ptints = [0.35 + 0.3 * rnd.random() for _ in range(panels)]
    for j in range(v_seg):
        for i in range(u_seg):
            f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            f.material_index = B.CANVAS
            f[tint] = ptints[min(panels - 1, int(i / u_seg * panels))]
            f[paint] = 0.0
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True  # cloth is soft; facets are for rock
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for m in B.all_materials():
        me.materials.append(m)
    return ob


def rope(b, a, c, r=0.045):
    b.cyl(a, c, r, B.TIMBER, sides=4)


def masts_and_rigging(b, rnd, sails):
    tops = {}
    for name, (t, z0, h, yards) in MASTS.items():
        y = y_of(t)
        lower = h * 0.62
        b.cyl((0, y, z0 - 1.0), (0, y, z0 + lower), 0.42, B.TIMBER, sides=10, r2=0.32)
        b.box((0, y, z0 + lower), (2.6, 2.2, 0.22), B.WALL, paint=0.0)  # the top
        for s in (-1, 1):
            b.box((s * 1.25, y, z0 + lower + 0.5), (0.1, 2.2, 0.9), B.TIMBER)  # top rail
        b.cyl((0, y, z0 + lower - 1.5), (0, y, z0 + h), 0.27, B.TIMBER, sides=8, r2=0.14)
        tops[name] = (y, z0 + lower, z0 + h)
        # yards + square sails between them
        # Yards braced round (as on a real ship on a reach), so the square
        # sails show their faces instead of edges from most angles.
        brace = Matrix.Rotation(BRACE, 3, "Z")

        def at(x, dy, z, _y=y):
            p = brace @ V((x, dy, 0))
            return V((p.x, _y + p.y, z))

        levels = [(z0 + f * h, L) for f, L in yards]
        for k, (z, L) in enumerate(levels):
            b.cyl(at(-L / 2, 0, z), at(L / 2, 0, z), 0.2, B.TIMBER, sides=6)
            b.cyl(at(-L / 2, 0, z), at(-L / 2 - 0.4, 0, z), 0.12, B.TIMBER, sides=6)
            b.cyl(at(L / 2, 0, z), at(L / 2 + 0.4, 0, z), 0.12, B.TIMBER, sides=6)
            foot_z = levels[k - 1][0] + 0.5 if k > 0 else z0 + 3.2
            foot_w = (levels[k - 1][1] if k > 0 else L * 1.05) * 0.96
            head_w = L * 0.94
            sails.append(sail_mesh(f"SHP_sail_{name}_{k}",
                                   [at(-head_w / 2, 0.25, z - 0.2), at(head_w / 2, 0.25, z - 0.2),
                                    at(foot_w / 2, 0.25, foot_z), at(-foot_w / 2, 0.25, foot_z)],
                                   rnd, billow=0.14 * head_w * (0.85 if k else 1.0),
                                   bulge_dir=brace @ V((0, 1, 0))))
    # Mizzen: gaff + boom with a fore-and-aft sail, bellied to starboard.
    y, zt, zh = tops["mizzen"]
    gaff_a, gaff_b = V((0, y - 0.3, zt + 1.8)), V((0, y - 7.5, zt + 4.8))
    boom_a, boom_b = V((0, y - 0.3, QD_Z + 2.4)), V((0, y - 9.0, QD_Z + 2.0))
    rope(b, gaff_a, gaff_b, 0.14)
    rope(b, boom_a, boom_b, 0.16)
    sails.append(sail_mesh("SHP_sail_mizzen", [gaff_a, gaff_b, boom_b, boom_a], rnd, billow=1.1,
                           bulge_dir=V((1, 0, 0))))
    # Bowsprit + jibs.
    bs_a, bs_b = V((0, Y_BOW - 0.5, sheer_z(1.0) - 0.4)), V((0, Y_BOW + 11.0, sheer_z(1.0) + 3.6))
    b.cyl(bs_a, bs_b, 0.32, B.TIMBER, sides=8, r2=0.16)
    fy, fz_top, fz_h = tops["fore"]
    for k, (frac_bs, frac_mast) in enumerate(((0.95, 0.78), (0.62, 0.58))):
        tip = bs_a.lerp(bs_b, frac_bs)
        head = V((0, fy + 0.4, MAIN_Z + 22.0 * frac_mast))
        foot = V((0, fy + 1.5, MAIN_Z + 2.4 + k * 1.2))
        rope(b, head, tip)
        sails.append(sail_mesh(f"SHP_sail_jib_{k}", [head, tip, tip + (foot - tip) * 0.02, foot], rnd,
                               billow=0.9, u_seg=10, v_seg=8, bulge_dir=V((1, 0, 0)), panels=5))
    # Stays between the mastheads.
    my = tops["main"]
    rope(b, V((0, my[0], my[1])), V((0, fy, MAIN_Z + 3.0)), 0.07)
    rope(b, V((0, fy, fz_top)), bs_a.lerp(bs_b, 0.45), 0.07)
    rope(b, V((0, tops["mizzen"][0], tops["mizzen"][1])), V((0, my[0], MAIN_Z + 9.0)), 0.06)
    # Shrouds with ratlines, both sides of every mast.
    for name, (y, ztop, _) in tops.items():
        t = t_of(y)
        z_deck = MASTS[name][1]
        wx = width_at(t, z_deck + 1.0) + 0.35
        lines = []
        for s in (-1, 1):
            side = []
            for k in range(4):
                oy = (k - 1.5) * 0.9
                a = V((s * wx, y + oy - 0.6, z_deck + 1.0))
                c = V((s * 1.2, y + oy * 0.35, ztop))
                rope(b, a, c, 0.04)
                side.append((a, c))
            lines.append(side)
        for side in lines:
            n = int((ztop - z_deck - 1.0) / 0.7)
            for i in range(1, n):
                u = i / n
                for (a0, c0), (a1, c1) in zip(side, side[1:]):
                    p, q = a0.lerp(c0, u), a1.lerp(c1, u)
                    rope(b, p, q, 0.025)
    return tops


def flag(name, at, rnd, w=2.6, h=1.7):
    """Black flag with a white skull and crossed bones, rippled."""
    bm = bmesh.new()
    rows = []
    nu, nv = 12, 6
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            u, v = i / nu, j / nv
            ripple = math.sin(u * 7.0) * 0.18 * u
            row.append(bm.verts.new(at + V((ripple, -u * w, -v * h))))
        rows.append(row)
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
            f.material_index = B.CLOTH
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for m in B.all_materials():
        me.materials.append(m)
    # skull and bones, both faces
    b = B.Builder(rnd)
    c = at + V((0, -w * 0.45, -h * 0.45))
    for s in (1, -1):
        off = V((s * 0.04, 0, 0))
        b.box(c + off + V((0, 0, 0.12)), (0.02, 0.5, 0.42), B.PLASTER, paint=0.0)
        b.box(c + off + V((0, 0, -0.15)), (0.02, 0.3, 0.16), B.PLASTER, paint=0.0)
        for a in (0.7, -0.7):
            b.box(c + off + V((0, 0, -0.35)), (0.02, 1.0, 0.09), B.PLASTER, rot=(a, 0, 0), paint=0.0)
        for ex in (-0.1, 0.1):
            b.box(c + off * 1.4 + V((0, ex, 0.14)), (0.02, 0.1, 0.1), B.CLOTH)
    emblem = b.object(f"{name}_emblem", bevel=0)
    emblem.parent = ob
    return ob


# --------------------------------------------------------------------------
# Fittings
# --------------------------------------------------------------------------

def fittings(b, rnd):
    # Gunports + cannon muzzles, 5 a side on the red band.
    for s in (1, -1):
        for i in range(5):
            t = 0.36 + i * 0.085
            v = 0.68
            x, z = section(t, v)
            y = y_of(t)
            b.box((s * (x + 0.06), y, z), (0.1, 0.85, 0.75), B.CLOTH)
            b.box((s * (x + 0.1), y, z + 0.5), (0.12, 0.95, 0.12), B.TIMBER)
            b.cyl((s * (x - 0.2), y, z), (s * (x + 0.9), y, z + 0.05), 0.2, B.IRON, sides=8, r2=0.17)
    # Stern gallery windows + three big stern lanterns.
    zg = MAIN_Z + 1.6
    w0 = half_beam(0.0) * 0.7
    for k in range(5):
        x = -w0 + k * (2 * w0 / 4)
        b.box((x, Y_STERN - 0.1, zg), (1.0, 0.1, 1.1), B.GLOW)
        b.box((x, Y_STERN - 0.16, zg), (1.2, 0.08, 0.12), B.TIMBER)
        b.box((x, Y_STERN - 0.16, zg), (0.08, 0.08, 1.3), B.TIMBER)
    b.box((0, Y_STERN - 0.2, zg + 0.8), (2 * w0 + 1.4, 0.2, 0.18), B.GOLD)
    b.box((0, Y_STERN - 0.2, zg - 0.8), (2 * w0 + 1.4, 0.3, 0.3), B.TIMBER)
    # carved pilasters between the lights, a gilt cornice and a stern walk rail
    for k in range(6):
        x = -w0 - w0 / 4 + k * (2 * w0 / 4)
        b.box((x, Y_STERN - 0.18, zg), (0.22, 0.2, 1.7), B.TIMBER)
        b.box((x, Y_STERN - 0.24, zg + 0.9), (0.34, 0.14, 0.2), B.GOLD)
    b.box((0, Y_STERN - 0.25, zg + 1.25), (2 * w0 + 1.8, 0.35, 0.22), B.GOLD)
    b.box((0, Y_STERN - 0.9, zg - 0.95), (2 * w0 + 1.2, 1.4, 0.12), B.WALL, paint=0.0)
    b.box((0, Y_STERN - 1.55, zg - 0.4), (2 * w0 + 1.2, 0.1, 0.1), B.TIMBER)
    for k in range(13):
        x = -w0 - 0.5 + k * ((2 * w0 + 1.0) / 12)
        b.cyl((x, Y_STERN - 1.55, zg - 0.9), (x, Y_STERN - 1.55, zg - 0.4), 0.04, B.TIMBER, sides=5)
    top = sheer_z(0.0)
    for x in (-2.4, 0.0, 2.4):
        b.cyl((x, Y_STERN + 0.2, top), (x, Y_STERN - 0.9, top + 0.6), 0.07, B.IRON, sides=5)
        B.lantern(b, V((x, Y_STERN - 1.0, top + (1.2 if x == 0 else 0.8))), 0.55 if x == 0 else 0.45)
    # Wheel on the quarterdeck, capstan, hatches, barrels, bell.
    wy = y_of(QD_T) - 2.0
    b.box((0, wy, QD_Z + 0.6), (0.3, 0.3, 1.2), B.TIMBER)
    for k in range(8):
        a = k / 8 * math.tau
        p = V((0, wy + 0.25, QD_Z + 1.35))
        d = V((math.cos(a), 0, math.sin(a)))
        b.cyl(p, p + d * 0.75, 0.035, B.TIMBER, sides=4)
        b.box(p + d * 0.62, (0.06, 0.06, 0.06), B.TIMBER)
    b.cyl((0, wy + 0.2, QD_Z + 1.35), (0, wy + 0.3, QD_Z + 1.35), 0.62, B.TIMBER, sides=16, r2=0.62)
    b.cyl((0, y_of(0.38), MAIN_Z), (0, y_of(0.38), MAIN_Z + 1.0), 0.45, B.TIMBER, sides=10, r2=0.38)
    for k in range(6):
        a = k / 6 * math.tau
        b.cyl((0, y_of(0.38), MAIN_Z + 0.85), (math.cos(a) * 1.3, y_of(0.38) + math.sin(a) * 1.3, MAIN_Z + 0.85),
              0.04, B.TIMBER, sides=4)
    for yy in (y_of(0.56), y_of(0.64)):
        b.box((0, yy, MAIN_Z + 0.12), (2.0, 1.6, 0.18), B.TIMBER)
        for k in range(6):
            b.box((-0.85 + k * 0.34, yy, MAIN_Z + 0.22), (0.06, 1.5, 0.05), B.CLOTH)
    for k in range(4):
        B.barrel(b, V((rnd.uniform(1.2, 2.4) * (1 if k % 2 else -1), y_of(0.52) + rnd.uniform(-1, 1), MAIN_Z + 0.06)),
                 rnd, h=0.9, r=0.34)
    B.crate(b, V((2.0, y_of(0.6), MAIN_Z + 0.06)), rnd, 0.8)
    B.crate(b, V((-2.1, y_of(0.66), MAIN_Z + 0.06)), rnd, 0.7)
    by = y_of(0.84)
    b.box((0, by, FC_Z + 1.2), (0.12, 0.12, 2.4), B.TIMBER)
    b.box((0, by, FC_Z + 2.3), (1.2, 0.14, 0.14), B.TIMBER)
    b.cyl((0, by, FC_Z + 2.2), (0, by, FC_Z + 1.7), 0.12, B.GOLD, sides=8, r2=0.26)
    # Lanterns at the quarterdeck corners.
    for s in (1, -1):
        p = V((s * (width_at(QD_T, QD_Z) - 0.4), y_of(QD_T) - 0.2, QD_Z))
        b.box(p + V((0, 0, 0.9)), (0.12, 0.12, 1.8), B.TIMBER)
        B.lantern(b, p + V((0, 0, 2.0)), 0.3)


# --------------------------------------------------------------------------

def galleon(rnd):
    """Build the ship at the origin; returns (hull, sails, flag)."""
    b = B.Builder(rnd, 0.0)
    hull(b, rnd)
    deck(b, rnd, MAIN_Z, QD_T - 0.02, FC_T + 0.02)
    deck(b, rnd, QD_Z, 0.0, QD_T)
    deck(b, rnd, FC_Z, FC_T, 0.97)
    bulkhead(b, rnd, QD_T, MAIN_Z, QD_Z, +1)
    bulkhead(b, rnd, FC_T, MAIN_Z, FC_Z, -1, door=True, windows=0)
    balustrade(b, rnd, QD_T, QD_Z, +1)
    balustrade(b, rnd, FC_T, FC_Z, -1)
    cap_rail(b)
    for s in (1, -1):
        stairs(b, s * 3.0, QD_T, MAIN_Z, QD_Z, +1)
    sails = []
    tops = masts_and_rigging(b, rnd, sails)
    fittings(b, rnd)
    hull_ob = b.object("SHP_hull", bevel=0.02)
    my, _, mh = tops["main"]
    fl = flag("SHP_flag", V((0, my - 0.25, mh + 0.2)), rnd)
    return hull_ob, sails, fl
