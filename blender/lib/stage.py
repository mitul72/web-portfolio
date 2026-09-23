"""Sky, sun, haze, water and cameras shared by every world render."""
import math

import bmesh
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

from . import materials

V = Vector

# The one time of day for the whole world: late golden hour, sun low in the
# west-south-west, warm key against a deepening blue sky.
SUN_ROT = 100.0  # sun azimuth (deg); direction = (-sin r, cos r): low from the west, a touch south
SUN_EL = 5.0  # visible disc elevation (deg)
KEY_EL = 12.0  # the key light sits higher than the disc so faces aren't all shadow
SUN_COLOR = (1.0, 0.64, 0.36)
CLOUD_GAIN = 6.0


def sun_dir(rot_deg=SUN_ROT, el_deg=SUN_EL):
    """Direction TO the sun. NOTE Blender's sky texture puts its sun at
    (+sin r, cos r), so the sky node gets `sun_rotation = -SUN_ROT` to land its
    disc on this same direction (verified by rendering a direction-coded
    panorama)."""
    r, e = math.radians(rot_deg), math.radians(el_deg)
    return V((-math.sin(r) * math.cos(e), math.cos(r) * math.cos(e), math.sin(e)))


def clouds(nt, sky_col, out, strength):
    """Painterly cumulus bands low on the horizon: warm-lit on the sun side,
    lavender in shadow, thinning toward the zenith."""
    from .nodes import Graph
    g = Graph(nt)
    tc = g.node("ShaderNodeTexCoord")
    d = tc.outputs["Generated"]  # world direction
    dz = g.xyz(d)["Z"]
    # Flatten the dome so clouds stretch horizontally like a real cloud deck.
    flat = g.combine(g.math("DIVIDE", g.xyz(d)["X"], g.math("ADD", dz, 0.12)),
                     g.math("DIVIDE", g.xyz(d)["Y"], g.math("ADD", dz, 0.12)), 0.0)
    big = g.noise(flat, 0.55, detail=5, rough=0.55, dist=0.3).outputs["Fac"]
    cover = g.maprange(big, 0.44, 0.6, smooth=True)
    band = g.math("MULTIPLY", g.maprange(dz, 0.0, 0.03, smooth=True), g.maprange(dz, 0.6, 0.18, smooth=True))
    a = g.math("MULTIPLY", cover, band)
    # sun-side lighting of the clouds
    sd = sun_dir()
    sdot = g.node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    g.link(d, sdot.inputs[0])
    sdot.inputs[1].default_value = (sd.x, sd.y, sd.z)
    lit = g.maprange(sdot.outputs["Value"], -0.3, 0.9, smooth=True)
    col = g.ramp(lit, [(0.0, (0.35, 0.32, 0.45)), (0.55, (0.85, 0.62, 0.5)), (1.0, (1.4, 0.9, 0.55))])
    # self-shadowed bellies: darker where cover is dense
    col = g.mix(g.maprange(big, 0.6, 0.8, 0.0, 0.35), col, (0.22, 0.2, 0.3))
    # The physical sky's raw radiance is several times brighter than 0..1
    # colours (the Background strength scales both afterwards), so lift the
    # clouds into the same range.
    col = g.mix(1.0, col, (CLOUD_GAIN,) * 3, "MULTIPLY")
    sky = g.mix(a, sky_col, col)
    # Below the horizon the sky model shows dark "ground". The sea never
    # reaches the true horizon, so that band would show as a dark line past
    # the sea's edge; fill it with the fog colour (pre-divided by the
    # Background strength), which is what the distant sea fades into anyway.
    from .materials import FOG_COLOR
    below = g.maprange(dz, 0.004, -0.004, smooth=True)
    g.link(g.mix(below, sky, tuple(c / strength for c in FOG_COLOR)), out)


def sky_and_sun(scene, sky_strength=0.1, sun_energy=6.5, haze=0.0):
    w = bpy.data.worlds.new("World")
    scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_elevation = math.radians(SUN_EL)
    sky.sun_rotation = math.radians(-SUN_ROT)
    sky.sun_size = math.radians(1.2)
    nt.nodes["Background"].inputs[1].default_value = sky_strength
    clouds(nt, sky.outputs[0], nt.nodes["Background"].inputs[0], sky_strength)
    if haze > 0:
        # Atmospheric perspective: distant planes fade and cool into the sky.
        vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Density"].default_value = haze
        vol.inputs["Color"].default_value = (0.62, 0.72, 0.9, 1)
        vol.inputs["Anisotropy"].default_value = 0.6
        nt.links.new(vol.outputs[0], nt.nodes["World Output"].inputs["Volume"])

    sun = bpy.data.lights.new("KEY_sun", "SUN")
    sun.energy = sun_energy
    sun.color = SUN_COLOR
    sun.angle = math.radians(1.5)
    ob = bpy.data.objects.new("KEY_sun", sun)
    scene.collection.objects.link(ob)
    ob.rotation_euler = (-sun_dir(SUN_ROT, KEY_EL)).to_track_quat("-Z", "Y").to_euler()
    return ob


def water(scene, shore_sources, size=1400.0, near=420.0, step=2.0, extra=()):
    """A sea plane: finely gridded near the islands (so the shore field is
    smooth), plus a big ring beyond. Each vertex gets `shore` = metres to the
    nearest point where land meets z=0."""
    # Shoreline samples from the evaluated land meshes.
    dg = bpy.context.evaluated_depsgraph_get()
    kd_pts = []
    for ob in shore_sources:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ob.matrix_world
        for e in me.edges:
            a = mw @ me.vertices[e.vertices[0]].co
            b = mw @ me.vertices[e.vertices[1]].co
            if (a.z > 0) != (b.z > 0):
                t = a.z / (a.z - b.z)
                p = a.lerp(b, t)
                kd_pts.append((p.x, p.y, 0.0))
        ev.to_mesh_clear()
    # Extra foam sources on open water (a waterfall's impact, chains).
    for x, y in extra:
        for k in range(12):
            a = k / 12 * math.tau
            kd_pts.append((x + math.cos(a) * 2.5, y + math.sin(a) * 2.5, 0.0))
    kd = KDTree(max(len(kd_pts), 1))
    for i, p in enumerate(kd_pts):
        kd.insert(p, i)
    kd.balance()

    bm = bmesh.new()
    n = int(near / step)
    bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=near / 2)
    me = bpy.data.meshes.new("ENV_sea")
    bm.to_mesh(me)
    bm.free()
    attr = me.attributes.new("shore", "FLOAT", "POINT")
    for v in me.vertices:
        _, _, dist = kd.find((v.co.x, v.co.y, 0.0)) if kd_pts else (None, None, 999.0)
        attr.data[v.index].value = dist
    sea_ob = bpy.data.objects.new("ENV_sea", me)
    scene.collection.objects.link(sea_ob)
    mat = materials.sea()
    me.materials.append(mat)

    # Far ring: a big plane with the hole cut out, shore = far.
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size * 4)
    far = bpy.data.meshes.new("ENV_sea_far")
    bm.to_mesh(far)
    bm.free()
    far_ob = bpy.data.objects.new("ENV_sea_far", far)
    far_ob.location.z = -0.02
    scene.collection.objects.link(far_ob)
    fa = far.attributes.new("shore", "FLOAT", "POINT")
    for d in fa.data:
        d.value = 999.0
    far.materials.append(mat)
    return sea_ob


def camera(scene, name, pos, look, lens=35.0):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.clip_start, cam.clip_end = 0.5, 6000
    ob = bpy.data.objects.new(name, cam)
    scene.collection.objects.link(ob)
    ob.location = V(pos)
    ob.rotation_euler = (V(look) - V(pos)).to_track_quat("-Z", "Y").to_euler()
    return ob


def render_settings(scene, w=1600, h=900):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    ee = scene.eevee
    ee.use_shadows = True
    ee.taa_render_samples = 64
    for attr, val in (("use_raytracing", True), ("volumetric_end", 3000.0), ("volumetric_tile_size", "4")):
        if hasattr(ee, attr):
            setattr(ee, attr, val)


def render(scene, cam, path):
    scene.camera = cam
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
