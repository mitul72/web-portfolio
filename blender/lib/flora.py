"""Vegetation: palms with ring-scarred curved trunks and folded, serrated
fronds; leafy bushes built from leaf cards; placement by raycasting."""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

from .nodes import material
from .rocks import catmull, loft
from . import materials as M

V = Vector

LEAF_DARK = (0.05, 0.16, 0.03)
LEAF = (0.14, 0.36, 0.05)
LEAF_TIP = (0.42, 0.52, 0.1)
BARK = (0.24, 0.16, 0.1)
BARK_LIGHT = (0.45, 0.34, 0.23)


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------

def leaf_material(name="leaf"):
    """Base-to-tip gradient from the `tip` attribute, per-plant hue shift from
    `hue`, and a little translucency so backlit fronds glow."""
    m, g, bsdf = material(name)
    tip = g.node("ShaderNodeAttribute", attribute_name="tip").outputs["Fac"]
    hue = g.node("ShaderNodeAttribute", attribute_name="hue").outputs["Fac"]
    col = g.ramp(tip, [(0.0, LEAF_DARK), (0.55, LEAF), (1.0, LEAF_TIP)])
    col = g.mix(g.math("MULTIPLY", hue, 0.35), col, (0.3, 0.42, 0.06))
    ao = g.node("ShaderNodeAmbientOcclusion", in_Distance=2.5)
    col = g.mix(1.0, col, g.maprange(ao.outputs["AO"], 0, 1, 0.35, 1.0), "MULTIPLY")
    g.link(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    bsdf.inputs["Specular IOR Level"].default_value = 0.35
    bsdf.inputs["Subsurface Weight"].default_value = 0.15
    m.use_backface_culling = False
    return M.fogged(m, g)


def bark_material(name="bark"):
    """Ring scars from the `ring` attribute (0..1 within each trunk segment)."""
    m, g, bsdf = material(name)
    ring = g.node("ShaderNodeAttribute", attribute_name="ring").outputs["Fac"]
    col = g.ramp(ring, [(0.0, BARK), (0.7, BARK_LIGHT), (1.0, (0.18, 0.11, 0.07))])
    geo = g.node("ShaderNodeNewGeometry")
    n = g.noise(geo.outputs["Position"], 3.0, detail=2).outputs["Fac"]
    col = g.mix(g.maprange(n, 0.3, 0.7, 0, 0.3), col, BARK)
    g.link(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    return M.fogged(m, g)


# --------------------------------------------------------------------------
# Palm
# --------------------------------------------------------------------------

def _frame(t):
    ref = V((0, 0, 1)) if abs(t.z) < 0.95 else V((1, 0, 0))
    u = t.cross(ref).normalized()
    return u, t.cross(u).normalized()


def _trunk(bm, rnd, spine, r0, r1, seg_len=0.55, sides=7):
    """Stacked flared segments along the spine: the ring-scarred palm trunk."""
    path = catmull(spine, 48)
    L = [0.0]
    for a, b in zip(path, path[1:]):
        L.append(L[-1] + (b - a).length)
    total = L[-1]

    def at(s):
        for i in range(1, len(L)):
            if L[i] >= s:
                f = (s - L[i - 1]) / max(L[i] - L[i - 1], 1e-6)
                return path[i - 1].lerp(path[i], f), (path[i] - path[i - 1]).normalized()
        return path[-1], (path[-1] - path[-2]).normalized()

    ring_layer = bm.verts.layers.float.get("ring") or bm.verts.layers.float.new("ring")
    rings = []
    s = 0.0
    while s < total:
        e = min(total, s + seg_len * rnd.uniform(0.85, 1.15))
        for k, (pos_s, flare, rv) in enumerate(((s, 0.92, 0.0), (e, 1.12, 1.0))):
            p, t = at(pos_s)
            u, v = _frame(t)
            r = (r0 + (r1 - r0) * pos_s / total) * flare
            ring = []
            for j in range(sides):
                a = j / sides * math.tau + (0.3 if len(rings) % 4 >= 2 else 0)
                vert = bm.verts.new(p + (u * math.cos(a) + v * math.sin(a)) * r)
                vert[ring_layer] = rv
                ring.append(vert)
            rings.append(ring)
        s = e
    for a, b in zip(rings, rings[1:]):
        for j in range(sides):
            j2 = (j + 1) % sides
            bm.faces.new((a[j], a[j2], b[j2], b[j]))
    bm.faces.new(rings[-1])
    return at(total)


def _frond(bm, rnd, base, direction, length, width, droop, tip_layer, hue_layer, hue):
    """One frond: an arching midrib with a V-folded blade whose edges step in
    and out, which reads as leaflets from any distance."""
    d = V((direction.x, direction.y, 0)).normalized()
    rise = direction.z
    pts = []
    n = 22
    for i in range(n + 1):
        t = i / n
        # arch up then droop hard toward the tip
        h = rise * length * 0.5 * math.sin(t * math.pi * 0.6) - droop * length * t * t
        pts.append(base + d * length * t + V((0, 0, h)))
    side = d.cross(V((0, 0, 1))).normalized()
    mid, left, right = [], [], []
    for i, p in enumerate(pts):
        t = i / n
        w = width * math.sin(min(1.0, t * 1.15) * math.pi) ** 0.7
        w *= 1.0 if i % 2 == 0 else 0.5  # leaflet serration
        fold = V((0, 0, w * 0.35))  # V-fold: edges sit above the midrib
        for lst, sgn in ((left, 1), (right, -1)):
            vert = bm.verts.new(p + side * w * sgn + fold)
            vert[tip_layer] = t
            vert[hue_layer] = hue
            lst.append(vert)
        vm = bm.verts.new(p)
        vm[tip_layer] = t
        vm[hue_layer] = hue
        mid.append(vm)
    for i in range(n):
        bm.faces.new((mid[i], mid[i + 1], left[i + 1], left[i]))
        bm.faces.new((mid[i], right[i], right[i + 1], mid[i + 1]))


def palm(name, rnd, height=12.0, lean=V((1, 0, 0)), lean_amt=0.25):
    """A palm with its base at the origin."""
    bm = bmesh.new()
    lean = V((lean.x, lean.y, 0)).normalized()
    spine = [V((0, 0, -0.5)), lean * height * lean_amt * 0.35 + V((0, 0, height * 0.35)),
             lean * height * lean_amt * 0.85 + V((0, 0, height * 0.72)), lean * height * lean_amt + V((0, 0, height))]
    top, tng = _trunk(bm, rnd, spine, 0.5 * max(height, 9) / 12, 0.32 * max(height, 9) / 12)
    trunk_faces = len(bm.faces)

    tip_layer = bm.verts.layers.float.new("tip")
    hue_layer = bm.verts.layers.float.new("hue")
    hue = rnd.random()
    # Two tiers: an upper crown arching up and out, a lower skirt drooping.
    for tier, count, up_rng, droop_rng, len_k in ((0, rnd.randint(7, 9), (0.8, 1.5), (0.5, 0.8), 0.5),
                                                  (1, rnd.randint(7, 9), (0.1, 0.5), (0.8, 1.2), 0.46)):
        off = rnd.uniform(0, math.tau)
        for i in range(count):
            a = off + (i + 0.5 * tier) / count * math.tau + rnd.uniform(-0.15, 0.15)
            dirv = V((math.cos(a), math.sin(a), rnd.uniform(*up_rng)))
            _frond(bm, rnd, top + V((0, 0, 0.15 - 0.2 * tier)), dirv, height * len_k * rnd.uniform(0.85, 1.1),
                   height * 0.085, rnd.uniform(*droop_rng), tip_layer, hue_layer, hue)
    # coconuts
    for _ in range(rnd.randint(2, 4)):
        c = top + V((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), -0.45))
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.28 * height / 12)
        for v in res["verts"]:
            v.co += c

    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(bpy.data.materials.get("bark") or bark_material())
    me.materials.append(bpy.data.materials.get("leaf") or leaf_material())
    for p in me.polygons:
        p.material_index = 0 if p.index < trunk_faces else 1
    return ob


# --------------------------------------------------------------------------
# Bush: leaf cards on a lumpy dome
# --------------------------------------------------------------------------

def bush(name, rnd, radius=2.0, leaves=150):
    bm = bmesh.new()
    tip_layer = bm.verts.layers.float.new("tip")
    hue_layer = bm.verts.layers.float.new("hue")
    hue = rnd.random()
    lumps = [V((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(0.3, 0.7))) * radius for _ in range(3)]
    for _ in range(leaves):
        c = rnd.choice(lumps)
        n = V((rnd.gauss(0, 1), rnd.gauss(0, 1), abs(rnd.gauss(0, 1)) + 0.3)).normalized()
        p = c + n * radius * rnd.uniform(0.45, 0.75)
        if p.z < 0.05:
            continue
        L = radius * rnd.uniform(0.4, 0.6)
        W = L * 0.5
        # leaf plane: points outward along n, tilted a bit downward at the tip
        fwd = (n + V((0, 0, -0.35))).normalized()
        side = fwd.cross(V((0, 0, 1)))
        side = side.normalized() if side.length > 1e-3 else V((1, 0, 0))
        up = side.cross(fwd).normalized()
        base = p - fwd * L * 0.3
        # rounded leaf: 6-point oval, cupped
        quad = [base, base + fwd * L * 0.3 + side * W * 0.9, base + fwd * L * 0.7 + side * W * 0.7,
                base + fwd * L, base + fwd * L * 0.7 - side * W * 0.7, base + fwd * L * 0.3 - side * W * 0.9]
        for k in (1, 2, 4, 5):
            quad[k] += up * W * 0.35
        vs = []
        for k, q in enumerate(quad):
            v = bm.verts.new(q)
            v[tip_layer] = 0.2 + 0.8 * (p.z / (radius * 1.3)) * (1.0 if k == 3 else 0.75)
            v[hue_layer] = hue
            vs.append(v)
        bm.faces.new(vs)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(bpy.data.materials.get("leaf") or leaf_material())
    return ob


# --------------------------------------------------------------------------
# Placement
# --------------------------------------------------------------------------

def ground_hit(scene, x, y, ignore=()):
    """Raycast straight down; returns (location, normal, object) or None."""
    dg = bpy.context.evaluated_depsgraph_get()
    origin = V((x, y, 300))
    hit, loc, nrm, _, ob, _ = scene.ray_cast(dg, origin, V((0, 0, -1)))
    if not hit or ob in ignore:
        return None
    return loc, nrm, ob


def sources(scene, rnd):
    """The shared palm and bush meshes every island instances (created once,
    kept in a hidden collection)."""
    hidden = bpy.data.collections.get("SRC_flora")
    if hidden:
        objs = list(hidden.objects)
        return ([o for o in objs if o.name.startswith("SRC_palm_")],
                [o for o in objs if o.name.startswith("SRC_bush_")])
    hidden = bpy.data.collections.new("SRC_flora")
    scene.collection.children.link(hidden)
    hidden.hide_render = True

    def keep(ob):
        scene.collection.objects.unlink(ob)
        hidden.objects.link(ob)
        return ob

    palms = [keep(palm(f"SRC_palm_{i}", rnd, height=rnd.uniform(7, 11), lean_amt=rnd.uniform(0.25, 0.55)))
             for i in range(6)]
    bushes = [keep(bush(f"SRC_bush_{i}", rnd, radius=rnd.uniform(1.6, 2.6))) for i in range(4)]
    return palms, bushes


def linked_copy(src, name):
    ob = bpy.data.objects.new(name, src.data)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def scatter(scene, make, count, region, accept, rnd, min_gap=4.0, taken=None, max_tries=4000, yaw=None, scale=(1.0, 1.0)):
    """Place up to `count` copies from `make(i, loc)` inside `region`
    ((x0,y0),(x1,y1)) where `accept(loc, normal, ob)` is True, keeping
    `min_gap` apart. `yaw(loc)` orients each copy (random if None)."""
    taken = taken if taken is not None else []
    placed = []
    tries = 0
    (x0, y0), (x1, y1) = region
    while len(placed) < count and tries < max_tries:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        hit = ground_hit(scene, x, y)
        if not hit or not accept(*hit):
            continue
        loc = hit[0]
        if any((loc - t).length < min_gap for t in taken):
            continue
        ob = make(len(placed), loc)
        if ob is None:
            continue
        ob.location = loc - V((0, 0, 0.15))
        ob.rotation_euler.z = yaw(loc) if yaw else rnd.uniform(0, math.tau)
        ob.scale = (rnd.uniform(*scale),) * 3
        taken.append(loc)
        placed.append(ob)
    return placed
