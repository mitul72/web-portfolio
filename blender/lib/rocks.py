"""Rock building blocks: lofted strata along spines, faceted chunks, and the
fuse/fracture/facet finishing stack."""
import math

import bmesh
import bpy
from mathutils import Euler, Vector, noise

V = Vector


# --------------------------------------------------------------------------
# Lofting
# --------------------------------------------------------------------------

def catmull(points, samples):
    """Sample a Catmull-Rom spline through `points` (open, clamped ends)."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    segs = len(points) - 1
    for i in range(samples):
        u = i / (samples - 1) * segs
        k = min(int(u), segs - 1)
        t = u - k
        p0, p1, p2, p3 = pts[k], pts[k + 1], pts[k + 2], pts[k + 3]
        t2, t3 = t * t, t * t * t
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return out


def loft(bm, rnd, spine, radius, beds=7, sides=13, rough=0.3, squash=1.0, cap=True, lip=None):
    """Sweep irregular cross-sections along `spine` (list of Vector).

    `radius(t)` gives the radius at 0..1 along the spine. The spine is cut into
    `beds`; within a bed the section keeps its outline, and at every bed
    boundary two rings share a position with DIFFERENT radii, which makes a
    crisp ledge (wider below) or an overhang (wider above). That stepped
    profile is what reads as sedimentary strata."""
    path = catmull(spine, 64)
    # cumulative length for bed placement
    L = [0.0]
    for a, b in zip(path, path[1:]):
        L.append(L[-1] + (b - a).length)
    total = L[-1]

    def at(s):
        for i in range(1, len(L)):
            if L[i] >= s:
                f = (s - L[i - 1]) / max(L[i] - L[i - 1], 1e-6)
                p = path[i - 1].lerp(path[i], f)
                tng = (path[i] - path[i - 1]).normalized()
                return p, tng
        return path[-1], (path[-1] - path[-2]).normalized()

    # bed boundaries: uneven thicknesses
    cuts = sorted(rnd.uniform(0.04, 0.96) for _ in range(beds - 1))
    cuts = [0.0] + cuts + [1.0]
    rings = []
    for bi in range(len(cuts) - 1):
        ph = rnd.uniform(0, 100)
        shape = []
        for k in range(sides):
            a = k / sides * math.tau
            n = noise.noise(Vector((math.cos(a) * 1.2 + ph, math.sin(a) * 1.2, ph)))
            shape.append((a, 1 + rough * n + rnd.uniform(-0.06, 0.06)))
        if lip is None:
            bed_lip = rnd.uniform(-0.12, -0.05) if rnd.random() < 0.3 else rnd.uniform(0.02, 0.12)
        else:
            bed_lip = rnd.uniform(*lip)
        for j, s in enumerate((cuts[bi], cuts[bi + 1])):
            p, tng = at(s * total)
            ref = Vector((0, 0, 1)) if abs(tng.z) < 0.9 else Vector((1, 0, 0))
            u = tng.cross(ref).normalized()
            v = tng.cross(u).normalized()
            r = radius((cuts[bi] + (cuts[bi + 1] - cuts[bi]) * j))
            if j == 1:
                r *= 1 + bed_lip  # top of the bed flares (overhang) or pinches (groove)
            ring = []
            for a, m in shape:
                off = (u * math.cos(a) + v * math.sin(a) * squash) * r * m
                ring.append(bm.verts.new(p + off))
            rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            k2 = (k + 1) % sides
            bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
    if cap:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])


def chunk(bm, rnd, center, size, tilt=0.25):
    """A faceted convex block (fallen rock, buttress, sea boulder)."""
    rot = Euler((rnd.uniform(-tilt, tilt), rnd.uniform(-tilt, tilt), rnd.uniform(0, math.tau))).to_matrix()
    pts = []
    for _ in range(16):
        v = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized() * rnd.uniform(0.8, 1.0)
        pts.append(bm.verts.new(center + rot @ Vector((v.x * size[0], v.y * size[1], v.z * size[2]))))
    bmesh.ops.convex_hull(bm, input=pts)


def taper(r0, r1, bulge=0.0):
    return lambda t: (r0 + (r1 - r0) * t) * (1 + bulge * math.sin(t * math.pi))


V = Vector


def finish(ob, voxel=0.8, facet=0.04):
    """Fuse, fracture, lump, facet."""
    name = ob.name
    rm = ob.modifiers.new("fuse", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = voxel
    tex = bpy.data.textures.new(f"{name}_flute", "VORONOI")
    tex.noise_scale = 7.0
    space = bpy.data.objects.new(f"{name}_flute_space", None)
    bpy.context.scene.collection.objects.link(space)
    space.scale = (1.0, 1.0, 4.0)
    d = ob.modifiers.new("flute", "DISPLACE")
    d.texture, d.texture_coords, d.texture_coords_object = tex, "OBJECT", space
    d.strength, d.mid_level = 2.2, 0.5
    tex3 = bpy.data.textures.new(f"{name}_crack", "VORONOI")
    tex3.weight_1, tex3.weight_2 = -1.0, 1.0
    tex3.noise_scale = 10.0
    d = ob.modifiers.new("crack", "DISPLACE")
    d.texture, d.texture_coords = tex3, "GLOBAL"
    d.strength, d.mid_level = 2.4, 0.0
    tex2 = bpy.data.textures.new(f"{name}_lump", "CLOUDS")
    tex2.noise_scale = 14.0
    d = ob.modifiers.new("lump", "DISPLACE")
    d.texture, d.texture_coords = tex2, "GLOBAL"
    d.strength = 2.5
    dec = ob.modifiers.new("facet", "DECIMATE")
    dec.ratio = facet


def mesh_object(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob
