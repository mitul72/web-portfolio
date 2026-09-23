"""Hero landmarks for the destination islands: a skull rock with carved eye
sockets and a sea-cave mouth, lava channels that follow the volcano's real
surface, a stone lighthouse, a broken shipwreck, anchor chains, a waterfall,
a treasure chest, a beached rowboat."""
import math

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

from . import build as B
from . import materials as M
from .rocks import chunk, finish, loft, mesh_object, taper

V = Vector


# --------------------------------------------------------------------------
# Rock finishing with carved cavities
# --------------------------------------------------------------------------

def carve_and_finish(ob, cutters, voxel=0.7, flute=1.2, crack=1.4, lump=1.4, facet=0.05):
    """Like rocks.finish(), but boolean-subtracts `cutters` after fusing and
    BEFORE the fracture displacement, so carved openings get the same broken
    edges as the rest of the rock. Displacement is gentler by default so
    features (eye sockets, a mouth) survive."""
    rm = ob.modifiers.new("fuse", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = voxel
    if cutters:
        coll = bpy.data.collections.new(f"{ob.name}_cutters")
        bpy.context.scene.collection.children.link(coll)
        for c in cutters:
            for uc in list(c.users_collection):
                uc.objects.unlink(c)
            coll.objects.link(c)
            c.hide_render = True
            c.display_type = "WIRE"
        bo = ob.modifiers.new("carve", "BOOLEAN")
        bo.operation = "DIFFERENCE"
        bo.operand_type = "COLLECTION"
        bo.collection = coll
        bo.solver = "EXACT"
    name = ob.name
    tex = bpy.data.textures.new(f"{name}_flute", "VORONOI")
    tex.noise_scale = 6.0
    space = bpy.data.objects.new(f"{name}_flute_space", None)
    bpy.context.scene.collection.objects.link(space)
    space.scale = (1.0, 1.0, 4.0)
    d = ob.modifiers.new("flute", "DISPLACE")
    d.texture, d.texture_coords, d.texture_coords_object = tex, "OBJECT", space
    d.strength, d.mid_level = flute, 0.5
    t3 = bpy.data.textures.new(f"{name}_crack", "VORONOI")
    t3.weight_1, t3.weight_2 = -1.0, 1.0
    t3.noise_scale = 8.0
    d = ob.modifiers.new("crack", "DISPLACE")
    d.texture, d.texture_coords = t3, "GLOBAL"
    d.strength, d.mid_level = crack, 0.0
    t2 = bpy.data.textures.new(f"{name}_lump", "CLOUDS")
    t2.noise_scale = 12.0
    d = ob.modifiers.new("lump", "DISPLACE")
    d.texture, d.texture_coords = t2, "GLOBAL"
    d.strength = lump
    dec = ob.modifiers.new("facet", "DECIMATE")
    dec.ratio = facet


def ellipsoid(name, center, radii, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    m = Matrix.Translation(center) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*radii, 1))
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return mesh_object(name, bm)


def prism_cutter(name, pts2d, depth, xf):
    """Extruded polygon (in local XZ, extruded along local Y) placed by xf."""
    bm = bmesh.new()
    front = [bm.verts.new((x, -depth / 2, z)) for x, z in pts2d]
    back = [bm.verts.new((x, depth / 2, z)) for x, z in pts2d]
    n = len(pts2d)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], front[j], back[j], back[i]))
    bm.faces.new(list(reversed(front)))
    bm.faces.new(back)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.transform(bm, matrix=xf, verts=bm.verts)
    return mesh_object(name, bm)


# --------------------------------------------------------------------------
# Skull rock
# --------------------------------------------------------------------------

def skull_rock(name, rnd, xf):
    """A cliff shaped like a skull, face toward local -Y, ~44 m tall. The
    mouth is a sea cave between hanging upper teeth and half-drowned lower
    ones. `xf` places it in the world."""
    bm = bmesh.new()
    # Cranium: a fat dome, widest a third of the way up.
    loft(bm, rnd, [V((0, 6, -6)), V((0, 5, 12)), V((0, 5, 28)), V((0, 8, 40))],
         lambda t: 16 + 13 * math.sin(math.pi * min(1.0, t * 0.95)) ** 0.8 - 7 * t ** 4, beds=5, sides=20,
         rough=0.08, squash=0.9, lip=(-0.03, 0.03))
    # Dome cap.
    chunk(bm, rnd, V((0, 8, 40)), (17, 16, 8), tilt=0.05)
    # Brow ridge over the sockets.
    chunk(bm, rnd, V((0, -18, 29)), (21, 6, 4.5), tilt=0.04)
    # Cheekbones and the upper jaw (maxilla) the teeth hang from.
    for sx in (-1, 1):
        chunk(bm, rnd, V((sx * 15, -17, 15)), (8, 7, 7), tilt=0.1)
    chunk(bm, rnd, V((0, -18, 10.5)), (15, 8, 3.5), tilt=0.03)
    bmesh.ops.transform(bm, matrix=xf, verts=bm.verts)
    ob = mesh_object(name, bm)

    rot = xf.to_euler()  # cutters turn with the skull
    cutters = [ellipsoid(f"{name}_eye_{i}", xf @ V((sx * 9.5, -22, 21.5)), (7.0, 12, 7.6), rot=rot)
               for i, sx in enumerate((-1, 1))]
    # Nose: an inverted triangle, carved deep.
    cutters.append(prism_cutter(f"{name}_nose", [(-3.2, 16.5), (3.2, 16.5), (0, 10.5)], 16,
                                xf @ Matrix.Translation((0, -24, 0))))
    # The mouth cave behind the teeth.
    cutters.append(ellipsoid(f"{name}_mouth", xf @ V((0, -16, 6)), (13, 11, 5.5), rot=rot))
    # Gentle fracturing so the face survives; finer facets than a cliff.
    carve_and_finish(ob, cutters, flute=0.6, crack=0.8, lump=0.6, facet=0.1)
    # Dark voids at the back of the sockets, nose and mouth: they read as
    # black at any distance, which is what makes a skull a skull.
    bm = bmesh.new()
    for c, r in ((V((-9.5, -11, 21.5)), (5.5, 2.5, 6)), (V((9.5, -11, 21.5)), (5.5, 2.5, 6)),
                 (V((0, -12, 13.5)), (2.2, 2, 2.6)), (V((0, -6, 6)), (11, 2.5, 4.5))):
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        bmesh.ops.transform(bm, matrix=xf @ Matrix.Translation(c) @ Matrix.Diagonal((*r, 1)), verts=res["verts"])
    void = mesh_object(f"{name}_void", bm)
    void.data.materials.append(M.emissive("void", (0.0, 0.0, 0.0), 0.0))
    vm = void.data.materials[0].node_tree.nodes["Principled BSDF"]
    vm.inputs["Roughness"].default_value = 1.0
    vm.inputs["Specular IOR Level"].default_value = 0.0
    if "fog" not in void.data.materials[0]:  # haze it like everything else
        from .nodes import Graph
        M.fogged(void.data.materials[0], Graph(void.data.materials[0].node_tree))
        void.data.materials[0]["fog"] = True

    # Teeth are their own piece, so the mouth carve can't eat them.
    bm = bmesh.new()
    # Upper teeth: chunky tapered blocks hanging down to just above the water.
    for i in range(6):
        x = -12.5 + i * 5.0
        y = -23.0 + 0.02 * x * x
        loft(bm, rnd, [V((x, y, 12)), V((x, y - 0.4, 2.4))], lambda t: 2.4 - 1.2 * t, beds=1, sides=8, rough=0.08,
             lip=(0, 0))
    # Lower jaw, drowned: only the lower teeth break the surface.
    chunk(bm, rnd, V((0, -14, -5)), (18, 10, 4), tilt=0.03)
    for i in range(5):
        x = -10 + i * 5.0
        y = -21.0 + 0.02 * x * x
        loft(bm, rnd, [V((x, y, -3)), V((x, y + 0.2, 1.4))], lambda t: 2.0 - 1.0 * t, beds=1, sides=8, rough=0.08,
             lip=(0, 0))
    bmesh.ops.transform(bm, matrix=xf, verts=bm.verts)
    teeth = mesh_object(f"{name}_teeth", bm)
    carve_and_finish(teeth, [], voxel=0.35, flute=0.25, crack=0.3, lump=0.2, facet=0.3)
    return ob, teeth


# --------------------------------------------------------------------------
# Volcano parts
# --------------------------------------------------------------------------

def crater_rim(bm, rnd, top, radius, notch_dir, height=4.0, thick=5.5):
    """A ring of rock around the crater, low where `notch_dir` points, so the
    lava can spill out that side."""
    pts = []
    n = 14
    nd = V((notch_dir.x, notch_dir.y, 0)).normalized()
    for i in range(n + 1):
        a = i / n * math.tau
        d = V((math.cos(a), math.sin(a), 0))
        low = max(0.0, d.dot(nd)) ** 4  # 1 at the notch
        r = radius * (1 + 0.12 * math.sin(a * 3 + 1.3))
        pts.append(top + d * r + V((0, 0, height * (1 - 0.9 * low) + rnd.uniform(-0.8, 0.8))))
    loft(bm, rnd, pts, lambda t: thick * (0.8 + 0.3 * math.sin(t * math.pi * 5)), beds=8, sides=9, rough=0.2,
         lip=(-0.05, 0.02))


def lava_channel(name, scene, start, direction, surface, width=3.2, step=2.0, max_len=160):
    """A glowing lava ribbon that follows the evaluated surface of `surface`
    downhill from `start` along `direction`, meandering, until it reaches the
    beach. Hot near the source (material 0), cooling toward the end (1)."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = surface.evaluated_get(dg)
    inv = surface.matrix_world.inverted()
    d = V((direction.x, direction.y, 0)).normalized()
    side = V((-d.y, d.x, 0))
    pts = []
    p = V((start.x, start.y, 0))
    s = 0.0
    while s < max_len:
        wig = side * (math.sin(s * 0.06) * 4.0 + math.sin(s * 0.17 + 1.3) * 1.5)
        q = p + wig
        o = inv @ V((q.x, q.y, 400))
        ok, loc, nrm, _ = ev.ray_cast(o, V((0, 0, -1)))
        if not ok:
            break
        w = surface.matrix_world @ loc
        if w.z < 1.2:
            break
        pts.append(w)
        p += d * step
        s += step
    bm = bmesh.new()
    rows = []
    for i, c in enumerate(pts):
        t = i / max(1, len(pts) - 1)
        wdt = width * (0.6 + 1.2 * t * t)  # widens as it slows
        row = []
        for k in (-1.0, -0.4, 0.0, 0.4, 1.0):
            v = c + side * k * wdt + V((0, 0, 0.35 - 0.3 * abs(k)))
            row.append(bm.verts.new(v))
        rows.append((row, t))
    for (r0, t0), (r1, _) in zip(rows, rows[1:]):
        for k in range(4):
            f = bm.faces.new((r0[k], r0[k + 1], r1[k + 1], r1[k]))
            f.material_index = 0 if t0 < 0.55 else 1
    ob = mesh_object(name, bm)
    ob.data.materials.append(M.emissive("lava_hot", (1.0, 0.2, 0.02), 2.4))
    ob.data.materials.append(M.emissive("lava_cool", (0.7, 0.07, 0.01), 1.1))
    return ob


# --------------------------------------------------------------------------
# Lighthouse
# --------------------------------------------------------------------------

def lighthouse(name, rnd, height=22.0, r0=3.4, r1=2.4, bands=True, lamp=True):
    """Whitewashed stone tower in courses (a faded red band twice), gallery
    with railing, glazed lamp room, red cone roof. Base at the origin."""
    b = B.Builder(rnd, 0.0)
    course = 0.9
    n = int(height / course)
    sides = 10
    for i in range(n):
        t = i / n
        r = r0 + (r1 - r0) * t
        z = i * course
        red = bands and (0.38 < t < 0.5 or 0.74 < t < 0.86)
        off = 0.5 if i % 2 else 0.0
        for k in range(sides):
            a = (k + off) / sides * math.tau
            L = 2 * r * math.sin(math.pi / sides) + 0.08
            b.box((math.cos(a) * r, math.sin(a) * r, z + course / 2), (0.55, L, course * 0.98), B.PLASTER,
                  rot=(0, 0, a), paint=1.0 if red else 0.0)
        # core so there are no gaps between blocks
        b.cyl((0, 0, z), (0, 0, z + course), r - 0.2, B.STONE, sides=sides)
    top = n * course
    # small windows spiralling up (lit)
    for i, z in enumerate((3.0, 7.5, 12.0, 16.5)):
        if z > top - 2:
            break
        a = i * 2.2 + 0.4
        t = z / top
        r = r0 + (r1 - r0) * t + 0.3
        b.box((math.cos(a) * r, math.sin(a) * r, z), (0.2, 0.6, 1.0), B.GLOW, rot=(0, 0, a))
    # door
    b.box((0, -r0 - 0.25, 1.2), (1.1, 0.25, 2.3), B.TIMBER)
    # gallery deck + railing
    b.cyl((0, 0, top), (0, 0, top + 0.35), r1 + 1.3, B.STONE, sides=16)
    for k in range(16):
        a = k / 16 * math.tau
        p = V((math.cos(a), math.sin(a), 0)) * (r1 + 1.15)
        b.box((p.x, p.y, top + 0.95), (0.08, 0.08, 1.2), B.IRON)
    b.cyl((0, 0, top + 1.5), (0, 0, top + 1.6), r1 + 1.2, B.IRON, sides=16, r2=r1 + 1.2)
    # lamp room: glass drum with iron mullions
    lr = r1 * 0.72
    b.cyl((0, 0, top + 0.35), (0, 0, top + 0.9), lr, B.STONE, sides=12)
    b.cyl((0, 0, top + 0.9), (0, 0, top + 3.3), lr - 0.1, B.LAMP if lamp else B.GLOW, sides=12)
    for k in range(8):
        a = k / 8 * math.tau
        b.box((math.cos(a) * lr, math.sin(a) * lr, top + 2.1), (0.12, 0.12, 2.5), B.IRON, rot=(0, 0, a))
    b.cyl((0, 0, top + 3.3), (0, 0, top + 3.55), lr + 0.2, B.IRON, sides=12)
    # red cone roof + finial
    b.cyl((0, 0, top + 3.55), (0, 0, top + 5.6), lr + 0.55, B.ROOF, sides=12, r2=0.15, paint=0.0)
    b.cyl((0, 0, top + 5.6), (0, 0, top + 6.3), 0.08, B.IRON, sides=6)
    b.box((0, 0, top + 6.4), (0.35, 0.35, 0.35), B.GOLD)
    return b.object(name, bevel=0.03), top + 2.1


# --------------------------------------------------------------------------
# Shipwreck
# --------------------------------------------------------------------------

def shipwreck(name, rnd, length=26.0, beam=8.0, depth=5.0):
    """A broken hull on its side: keel, curved ribs (some snapped), a patch of
    planking still on, a split mast. Local +X is the bow."""
    b = B.Builder(rnd, 0.0)
    b.box((0, 0, 0), (length, 0.5, 0.6), B.TIMBER)  # keel
    nrib = 11
    for i in range(nrib):
        t = i / (nrib - 1)
        x = -length / 2 + t * length
        w = beam / 2 * math.sin(math.pi * (0.12 + 0.76 * t)) ** 0.6
        broken = rnd.random() < 0.35
        for s in (-1, 1):
            segs = 7 if not (broken and s == 1) else rnd.randint(2, 4)
            prev = V((x, 0, 0))
            for k in range(1, segs + 1):
                u = k / 7
                a = u * math.pi / 2
                p = V((x, s * w * math.sin(a), depth * (1 - math.cos(a)) * 0.9 + u * 0.8))
                mid = (prev + p) / 2
                d = p - prev
                rot = d.to_track_quat("X", "Z").to_euler()
                b.box(mid, (d.length + 0.1, 0.32, 0.4), B.TIMBER, rot=rot)
                prev = p
    # surviving planking on the port side, low down
    for r in range(4):
        u = (r + 1) / 7
        a = u * math.pi / 2
        for i in range(3):
            x0 = -length * 0.35 + i * length * 0.22 + rnd.uniform(-1, 1)
            w = beam / 2 * 0.95
            y = -w * math.sin(a)
            z = depth * (1 - math.cos(a)) * 0.9 + u * 0.8
            b.box((x0, y - 0.1, z), (length * 0.2, 0.12, 0.6), B.WALL, rot=(-a * 0.9, rnd.uniform(-0.05, 0.05), 0))
    # stern post + snapped mast
    b.box((-length / 2 - 0.6, 0, depth * 0.6), (0.6, 0.5, depth * 1.4), B.TIMBER, rot=(0, 0.2, 0))
    b.cyl((1.5, 0, 0.5), (8.0, 1.5, 12.0), 0.35, B.TIMBER, sides=8)
    b.box((6.0, 1.1, 9.0), (0.25, 5.5, 0.3), B.TIMBER, rot=(0.3, 0, 0.4))
    return b.object(name, bevel=0.03)


# --------------------------------------------------------------------------
# Chain, waterfall, chest, rowboat
# --------------------------------------------------------------------------

def _torus(bm, center, axis_u, axis_v, R=0.5, r=0.13, seg=10, rings=5):
    n = axis_u.cross(axis_v).normalized()
    verts = []
    for i in range(seg):
        a = i / seg * math.tau
        c = center + (axis_u * math.cos(a) * 1.4 + axis_v * math.sin(a)) * R
        radial = (axis_u * math.cos(a) * 1.4 + axis_v * math.sin(a)).normalized()
        row = []
        for j in range(rings):
            b = j / rings * math.tau
            row.append(bm.verts.new(c + (radial * math.cos(b) + n * math.sin(b)) * r))
        verts.append(row)
    for i in range(seg):
        for j in range(rings):
            i2, j2 = (i + 1) % seg, (j + 1) % rings
            bm.faces.new((verts[i][j], verts[i2][j], verts[i2][j2], verts[i][j2]))


def chain(name, a, b, sag=6.0, link=1.1):
    """Iron chain hanging from a to b, links alternating 90 degrees."""
    a, b = V(a), V(b)
    L = (b - a).length
    n = max(4, int(L / link))
    bm = bmesh.new()
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(a.lerp(b, t) - V((0, 0, sag * 4 * t * (1 - t))))
    for i in range(n):
        p, q = pts[i], pts[i + 1]
        d = (q - p).normalized()
        side = d.cross(V((0, 0, 1)))
        side = side.normalized() if side.length > 1e-3 else V((1, 0, 0))
        up = side.cross(d).normalized()
        other = side if i % 2 else up
        _torus(bm, (p + q) / 2, d, other, R=link * 0.36, r=link * 0.1)
    ob = mesh_object(name, bm)
    for mat in B.all_materials():
        ob.data.materials.append(mat)
    for poly in ob.data.polygons:
        poly.material_index = B.IRON
    return ob


def waterfall(name, top, out_dir, drop, width=5.0, reach=10.0):
    """A ribbon of falling water from `top`, arcing out along `out_dir` and
    down `drop` metres, cupped across its width."""
    d = V((out_dir.x, out_dir.y, 0)).normalized()
    side = V((-d.y, d.x, 0))
    bm = bmesh.new()
    rows = []
    N, W = 40, 8
    for i in range(N + 1):
        t = i / N
        wob = side * math.sin(t * 9.0) * 0.5 * t
        c = top + d * reach * math.sqrt(t) + V((0, 0, -drop * t ** 1.6)) + wob
        wdt = width * (1.0 - 0.35 * t + 0.9 * max(0.0, t - 0.85) / 0.15)  # thins, then fans at the splash
        row = []
        for k in range(W + 1):
            u = k / W * 2 - 1
            row.append(bm.verts.new(c + side * u * wdt / 2 + d * (0.6 * (1 - u * u))))
        rows.append(row)
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(W):
            bm.faces.new((r0[k], r0[k + 1], r1[k + 1], r1[k]))
    ob = mesh_object(name, bm)
    mat = bpy.data.materials.get("waterfall") or M.waterfall()
    mat.use_backface_culling = False
    ob.data.materials.append(mat)
    return ob


def treasure_chest(b, at, rnd, yaw=0.0, open_=0.9):
    """Iron-banded chest, lid thrown back, heaped with gold."""
    base = b.xf
    b.xf = base @ Matrix.Translation(V(at)) @ Matrix.Rotation(yaw, 4, "Z")
    W, D, H = 1.6, 1.0, 0.8
    b.box((0, 0, H / 2), (W, D, H), B.WALL, paint=0.8)
    for x in (-W / 2 + 0.2, 0, W / 2 - 0.2):
        b.box((x, 0, H / 2), (0.12, D + 0.06, H + 0.04), B.IRON)
    # gold heap
    for i in range(22):
        c = V((rnd.uniform(-0.62, 0.62), rnd.uniform(-0.36, 0.36), H + rnd.uniform(-0.02, 0.22)))
        b.box(c, (0.22, 0.22, 0.05), B.GOLD, rot=(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0, 3)))
    b.box((0, 0, H + 0.08), (W - 0.1, D - 0.1, 0.15), B.GOLD)
    # lid hinged at the back, thrown open
    hinge = V((0, D / 2, H))
    lid_xf = Matrix.Translation(hinge) @ Matrix.Rotation(-open_ * 1.9, 4, "X") @ Matrix.Translation(-hinge)
    saved = b.xf
    b.xf = saved @ lid_xf
    b.box((0, 0, H + 0.2), (W, D, 0.35), B.WALL, paint=0.8)
    for x in (-W / 2 + 0.2, W / 2 - 0.2):
        b.box((x, 0, H + 0.2), (0.12, D + 0.06, 0.4), B.IRON)
    b.xf = saved
    b.box((0, -D / 2 - 0.04, H - 0.15), (0.2, 0.06, 0.26), B.GOLD)  # lock plate
    b.xf = base


def rowboat(b, at, rnd, yaw=0.0, length=5.0):
    """Small clinker-built rowboat pulled up on the sand, tilted."""
    base = b.xf
    b.xf = base @ Matrix.Translation(V(at)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(0.18, 4, "X")
    b.box((0, 0, 0.1), (length, 0.25, 0.2), B.TIMBER)
    for r in range(4):
        z = 0.15 + r * 0.22
        for s in (-1, 1):
            for i in range(8):
                t = (i + 0.5) / 8 - 0.5
                w = 0.75 * (1 - (2 * t) ** 2) ** 0.5 * (0.6 + 0.4 * r / 3) + 0.05
                x = t * length * (0.92 + 0.05 * r)
                b.box((x, s * w, z), (length / 8 + 0.05, 0.08, 0.24), B.WALL,
                      rot=(s * (0.35 + 0.1 * r), 0, s * -2 * t * 0.5), paint=0.3)
    for x in (-0.8, 0.8):
        b.box((x, 0, 0.62), (0.3, 1.5, 0.08), B.WALL, paint=0.3)  # thwarts
    b.box((0.4, 1.1, 0.55), (3.2, 0.1, 0.06), B.TIMBER, rot=(0, 0.1, 0.25))  # oar
    b.xf = base


def torch_post(b, at, h=2.6):
    at = V(at)
    b.box(at + V((0, 0, h / 2)), (0.16, 0.16, h), B.TIMBER)
    B.lantern(b, at + V((0, 0, h + 0.25)), 0.3)
