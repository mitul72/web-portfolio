"""Rock technique lab: a DESIGNED hero massif (spires + sea arch + shelf),
lofted along hand-placed spines with stepped strata, then fused, fractured and
faceted. Renders one test shot.

    blender -b --factory-startup --python blender/rocklab.py -- <out.png>
"""
import math
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Vector, noise

OUT = sys.argv[sys.argv.index("--") + 1]


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


def loft(bm, rnd, spine, radius, beds=7, sides=13, rough=0.3, squash=1.0, cap=True):
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
    prev_ref = None
    for bi in range(len(cuts) - 1):
        ph = rnd.uniform(0, 100)
        shape = []
        for k in range(sides):
            a = k / sides * math.tau
            n = noise.noise(Vector((math.cos(a) * 1.2 + ph, math.sin(a) * 1.2, ph)))
            shape.append((a, 1 + rough * n + rnd.uniform(-0.06, 0.06)))
        lip = rnd.uniform(-0.12, -0.05) if rnd.random() < 0.3 else rnd.uniform(0.02, 0.12)
        for j, s in enumerate((cuts[bi], cuts[bi + 1])):
            p, tng = at(s * total)
            ref = prev_ref or (Vector((0, 0, 1)) if abs(tng.z) < 0.9 else Vector((1, 0, 0)))
            u = tng.cross(ref).normalized()
            v = tng.cross(u).normalized()
            prev_ref = v.copy() * -1 if False else ref
            r = radius((cuts[bi] + (cuts[bi + 1] - cuts[bi]) * j))
            if j == 1:
                r *= 1 + lip  # top of the bed flares (overhang) or pinches (groove)
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


def build_massif(bm, rnd):
    # Main spire: tall, leaning slightly left, fat base.
    loft(bm, rnd, [V((0, 18, -6)), V((-2, 18, 30)), V((-7, 20, 62)), V((-13, 22, 96))],
         taper(28, 8, 0.15), beds=10, squash=0.85)
    # Second spire, leaning right.
    loft(bm, rnd, [V((34, 26, -6)), V((36, 27, 25)), V((42, 30, 58))], taper(18, 6), beds=7)
    # Back shoulder that joins them.
    loft(bm, rnd, [V((16, 40, -6)), V((16, 40, 34))], taper(26, 18), beds=5, squash=0.8)
    # Sea arch: rises from the water on the left and lands on the main spire.
    loft(bm, rnd, [V((-62, -4, -6)), V((-58, -2, 22)), V((-44, 4, 42)), V((-26, 12, 44)), V((-14, 16, 36))],
         lambda t: 9 - 2.5 * math.sin(t * math.pi), beds=9, sides=11, rough=0.25)
    # Front shelf where the outpost sits: a broad low mesa.
    loft(bm, rnd, [V((6, -16, -6)), V((6, -16, 14))], taper(40, 36), beds=3, squash=0.62, rough=0.22)
    # Side shelf toward the right spire.
    loft(bm, rnd, [V((34, 4, -6)), V((34, 4, 9))], taper(24, 21), beds=2, squash=0.7)
    # Buttresses and fallen blocks at the waterline.
    for _ in range(22):
        a = rnd.uniform(0, math.tau)
        r = rnd.uniform(32, 62)
        c = V((10 + math.cos(a) * r, 10 + math.sin(a) * r * 0.7, rnd.uniform(-4, 2)))
        s = rnd.uniform(3, 8)
        chunk(bm, rnd, c, (s * rnd.uniform(0.8, 1.4), s * rnd.uniform(0.7, 1.1), s * rnd.uniform(0.6, 1.3)))


def sea_stack(bm, rnd, base, h, r):
    lean = V((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * h * 0.08
    loft(bm, rnd, [base + V((0, 0, -6)), base + V((0, 0, h * 0.5)) + lean * 0.5, base + V((0, 0, h)) + lean],
         taper(r, r * 0.45, 0.1), beds=max(3, int(h / 7)), sides=11)


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


# --------------------------------------------------------------------------
# Materials (preview; everything here is bakeable to maps for glTF)
# --------------------------------------------------------------------------

def rock_material():
    m = bpy.data.materials.new("rock")
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    bsdf = n["Principled BSDF"]
    geo = n.new("ShaderNodeNewGeometry")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(geo.outputs["Position"], sep.inputs[0])
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.04
    l.new(geo.outputs["Position"], nz.inputs["Vector"])
    add = n.new("ShaderNodeMath")
    add.operation = "MULTIPLY_ADD"
    l.new(nz.outputs["Fac"], add.inputs[0])
    add.inputs[1].default_value = 10.0
    l.new(sep.outputs["Z"], add.inputs[2])
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.7
    l.new(add.outputs[0], mul.inputs[0])
    wave = n.new("ShaderNodeMath")
    wave.operation = "SINE"
    l.new(mul.outputs[0], wave.inputs[0])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.22, 0.13, 0.09, 1)
    ramp.color_ramp.elements[1].color = (0.5, 0.36, 0.26, 1)
    l.new(wave.outputs[0], ramp.inputs[0])
    sepn = n.new("ShaderNodeSeparateXYZ")
    l.new(geo.outputs["Normal"], sepn.inputs[0])
    moss = n.new("ShaderNodeMapRange")
    moss.inputs["From Min"].default_value = 0.7
    moss.inputs["From Max"].default_value = 0.8
    l.new(sepn.outputs["Z"], moss.inputs["Value"])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    l.new(moss.outputs[0], mix.inputs["Factor"])
    l.new(ramp.outputs[0], mix.inputs["A"])
    mix.inputs["B"].default_value = (0.17, 0.33, 0.05, 1)
    # wet dark band at the waterline
    wet = n.new("ShaderNodeMapRange")
    wet.inputs["From Min"].default_value = 3.5
    wet.inputs["From Max"].default_value = 0.5
    l.new(sep.outputs["Z"], wet.inputs["Value"])
    wmix = n.new("ShaderNodeMix")
    wmix.data_type = "RGBA"
    l.new(wet.outputs[0], wmix.inputs["Factor"])
    l.new(mix.outputs["Result"], wmix.inputs["A"])
    wmix.inputs["B"].default_value = (0.05, 0.05, 0.045, 1)
    ao = n.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 8.0
    cav = n.new("ShaderNodeMix")
    cav.data_type = "RGBA"
    cav.blend_type = "MULTIPLY"
    cav.inputs["Factor"].default_value = 1.0
    l.new(wmix.outputs["Result"], cav.inputs["A"])
    l.new(ao.outputs["AO"], cav.inputs["B"])
    l.new(cav.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Specular IOR Level"].default_value = 0.2
    return m


def sea_material():
    m = bpy.data.materials.new("sea")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.01, 0.05, 0.08, 1)
    b.inputs["Roughness"].default_value = 0.15
    return m


# --------------------------------------------------------------------------
# Scene
# --------------------------------------------------------------------------

def sun_dir(rot_deg, el_deg):
    """Direction TO the sun, matching Blender's sky model convention."""
    r, e = math.radians(rot_deg), math.radians(el_deg)
    return V((-math.sin(r) * math.cos(e), math.cos(r) * math.cos(e), math.sin(e)))


def lighting(s, rot=62, el=6):
    w = bpy.data.worlds.new("W")
    s.world = w
    w.use_nodes = True
    sky = w.node_tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_elevation = math.radians(el)
    sky.sun_rotation = math.radians(rot)
    w.node_tree.links.new(sky.outputs[0], w.node_tree.nodes["Background"].inputs[0])
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.06
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 5.5
    sun.color = (1.0, 0.62, 0.34)
    sun.angle = math.radians(1.0)
    so = bpy.data.objects.new("sun", sun)
    s.collection.objects.link(so)
    d = sun_dir(rot, el + 8)
    so.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    rnd = random.Random(11)
    bm = bmesh.new()
    build_massif(bm, rnd)
    for base, h, r in [(V((-95, -40, 0)), 30, 8), (V((78, -48, 0)), 22, 7), (V((-110, 30, 0)), 44, 10)]:
        sea_stack(bm, rnd, base, h, r)
    ob = mesh_object("massif", bm)
    finish(ob)
    ob.data.materials.append(rock_material())

    bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, 0))
    bpy.context.object.data.materials.append(sea_material())
    lighting(s)

    cam = bpy.data.cameras.new("cam")
    cam.lens = 35
    co = bpy.data.objects.new("cam", cam)
    s.collection.objects.link(co)
    co.location = (40, -230, 16)
    co.rotation_euler = (V((0, 0, 38)) - co.location).to_track_quat("-Z", "Y").to_euler()
    s.camera = co
    s.render.engine = "BLENDER_EEVEE"
    s.render.resolution_x, s.render.resolution_y = 1280, 720
    s.view_settings.view_transform = "AgX"
    s.view_settings.look = "AgX - Medium High Contrast"
    s.render.filepath = OUT
    bpy.ops.render.render(write_still=True)


main()
