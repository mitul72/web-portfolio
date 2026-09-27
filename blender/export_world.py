"""Export the approved archipelago for the web.

    blender -b --factory-startup blender/world.blend --python blender/export_world.py -- <repo-root>

Writes:
  src/assets/world.glb           raw GLB (compress with gltf-transform, see below)
  public/world/sky.hdr           the world sky (clouds, sun disc) as an HDR panorama
  public/world/shore.png         top-down metres-to-shore field for the ocean shader
  src/data/world.ts              sun / fog / shore-map constants shared with the app

After compressing the GLB (CLAUDE.md, "Adding a 3D asset"), run `npm run assets`:
it converts the albedos to KTX2 and the shore map to a single channel.

How the approved look survives glTF:
  - Rock + ground: procedural materials (strata, moss, wet band, cavity AO)
    baked to base-colour textures. Faceted geometry needs no normal map.
  - Buildings + flora: every board / leaf already has its own colour, so the
    material is baked per face corner into vertex colours (COLOR_0) instead of
    a texture. Window + lantern glass keep emissive materials.
  - Palms + bushes: linked duplicates exported with EXT_mesh_gpu_instancing.
  - Distance fog is stripped before baking; the app applies the same FogExp2.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import materials as M  # noqa: E402
from lib import stage  # noqa: E402

REPO = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
TMP = REPO / "blender" / "bake"
TMP.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene

# Texture budget per baked object (base colour only). Big cliffs get more.
TEX = {
    "ISL_home_rock": 4096, "ISL_home_stacks": 2048, "ISL_home_ground": 2048,
    "ISL_ember_rock": 4096, "ISL_ember_ground": 2048,
    "ISL_skull_rock": 2048, "ISL_skull_rock_teeth": 1024, "ISL_skull_rocks": 1024, "ISL_skull_ground": 2048,
    "ISL_light_rock": 2048, "ISL_light_cap": 1024,
    "ISL_drift_rock": 2048, "ISL_drift_cap": 1024,
}
SHORE_EXTENT = 512.0  # the shore map covers [-E, E] metres in X and Z
SHORE_N = 1024  # 1 m per texel (plenty for 2-9 m foam bands; `npm run assets` keeps it at this)
SHORE_MAX = 96.0  # metres encoded as 1.0
# Materials exported as they are (self-lit or flat black), never baked.
KEEP = ("window_glow", "lantern_glow", "lava_hot", "lava_cool", "void", "bottle_glass")


def log(*a):
    print("[export]", *a, flush=True)


# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------

def cycles_gpu():
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "HIP"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type == "HIP"
        scene.cycles.device = "GPU"
    except Exception as e:  # noqa: BLE001
        log("GPU unavailable, baking on CPU:", e)
        scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = False


def unfog(mat):
    """Undo materials.fogged(): reconnect the BSDF straight to the output."""
    if not mat or not mat.use_nodes:
        return
    nt = mat.node_tree
    out = nt.nodes.get("Material Output")
    if not out or not out.inputs["Surface"].links:
        return
    mix = out.inputs["Surface"].links[0].from_node
    if mix.type != "MIX_SHADER" or not mix.inputs[1].links:
        return
    nt.links.new(mix.inputs[1].links[0].from_socket, out.inputs["Surface"])


def apply_modifiers(ob, keep_bevel=False):
    """Bake the modifier stack into the mesh (so what we bake is what ships)."""
    if not keep_bevel:
        for m in list(ob.modifiers):
            if m.type == "BEVEL":
                ob.modifiers.remove(m)
    if not ob.modifiers:
        return
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)


def cut_below(ob, z):
    """Drop geometry below the waterline; nobody sees it and it wastes texels."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    mw = ob.matrix_world
    dead = [f for f in bm.faces if all((mw @ v.co).z < z for v in f.verts)]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    bm.to_mesh(ob.data)
    bm.free()


def select_only(obs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]


# --------------------------------------------------------------------------
# Texture bake: rock + ground
# --------------------------------------------------------------------------

def bake_texture(ob, size):
    apply_modifiers(ob)
    cut_below(ob, -1.5)
    # own material copy so the bake target image is per object
    src = ob.data.materials[0]
    mat = src.copy()
    mat.name = f"{ob.name}_bake"
    ob.data.materials[0] = mat
    unfog(mat)

    select_only([ob])
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.002, area_weight=0.0)
    bpy.ops.object.mode_set(mode="OBJECT")

    img = bpy.data.images.new(f"{ob.name}_albedo", size, size, alpha=False)
    nt = mat.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.nodes.active = tex
    scene.render.bake.margin = 6
    scene.render.bake.use_pass_direct = False
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_pass_color = True
    log("baking", ob.name, size)
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, use_clear=True)
    path = TMP / f"{ob.name}_albedo.png"
    img.filepath_raw = str(path)
    img.file_format = "PNG"
    img.save()

    # Export material: the baked texture, nothing procedural.
    out_mat = bpy.data.materials.new(f"{ob.name.replace('ISL_', '')}")
    out_mat.use_nodes = True
    bsdf = out_mat.node_tree.nodes["Principled BSDF"]
    t = out_mat.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = img
    out_mat.node_tree.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Specular IOR Level"].default_value = 0.25
    ob.data.materials[0] = out_mat


# --------------------------------------------------------------------------
# Vertex-colour bake: buildings + flora
# --------------------------------------------------------------------------

def vc_material(name, rough=0.8, double=False):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    ca = nt.nodes.new("ShaderNodeVertexColor")
    ca.layer_name = "Col"
    nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = 0.3
    m.use_backface_culling = not double
    return m


def water_material():
    """Baked streaks as vertex colour, plus a faint self-glow so falling water
    stays bright at dusk (glTF emissive can't be per-vertex, so it's flat)."""
    m = bpy.data.materials.get("vc_water")
    if m:
        return m
    m = vc_material("vc_water", 0.25, double=True)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Color"].default_value = (0.5, 0.72, 0.78, 1)
    bsdf.inputs["Emission Strength"].default_value = 0.3
    return m


def metal_vc():
    m = bpy.data.materials.get("vc_iron")
    if m:
        return m
    m = vc_material("vc_iron", 0.45)
    m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.7
    return m


def gold_vc():
    m = bpy.data.materials.get("vc_gold")
    if m:
        return m
    m = vc_material("vc_gold", 0.3)
    m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
    return m


def bake_vertex_colors(obs):
    for ob in obs:
        apply_modifiers(ob)
        for m in ob.data.materials:
            unfog(m)
        me = ob.data
        if "Col" not in me.color_attributes:
            me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
        me.color_attributes.active_color = me.color_attributes["Col"]
        me.attributes.default_color_name = "Col"
    select_only(obs)
    scene.render.bake.target = "VERTEX_COLORS"
    log("baking vertex colours for", len(obs), "objects")
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, use_clear=True)
    scene.render.bake.target = "IMAGE_TEXTURES"

    # Collapse to export slots: matte vertex colour, leaves, and the glows.
    for ob in obs:
        me = ob.data
        names = [m.name if m else "" for m in me.materials]
        remap = {}
        new = []

        def slot(mat):
            if mat.name not in [m.name for m in new]:
                new.append(mat)
            return [m.name for m in new].index(mat.name)

        for i, n in enumerate(names):
            if n in KEEP:
                g = bpy.data.materials[n]
                unfog(g)
                remap[i] = slot(g)
            elif n == "waterfall":
                remap[i] = slot(water_material())
            elif n == "leaf":
                remap[i] = slot(vc_material("vc_leaf", 0.6, double=True))
            elif n == "iron":
                remap[i] = slot(metal_vc())
            elif n in ("canvas", "cloth_black", "signal"):
                remap[i] = slot(vc_material("vc_cloth", 0.9, double=True))  # sails, flags, parchment
            elif n == "livery":
                remap[i] = slot(vc_material("vc_gloss", 0.5))  # lacquered paint
            elif n == "gold":
                remap[i] = slot(gold_vc())
            else:
                remap[i] = slot(vc_material("vc_matte", 0.85))
        idx = [p.material_index for p in me.polygons]
        me.materials.clear()
        for m in new:
            me.materials.append(m)
        for p, i in zip(me.polygons, idx):
            p.material_index = remap.get(i, 0)


# --------------------------------------------------------------------------
# Sky panorama + shore map + constants
# --------------------------------------------------------------------------

def render_sky():
    """World only, equirectangular, centre of the image = three.js +X, which
    is what three's equirect mapping expects."""
    for ob in scene.objects:
        ob.hide_render = True
    cam_data = bpy.data.cameras.new("CAM_sky")
    cam_data.type = "PANO"
    cam_data.panorama_type = "EQUIRECTANGULAR"
    cam = bpy.data.objects.new("CAM_sky", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0, 0, 2)
    cam.rotation_euler = Vector((1, 0, 0)).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = 2048, 1024
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 32
    scene.render.image_settings.file_format = "HDR"
    out = REPO / "public" / "world" / "sky.hdr"
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    log("sky ->", out)


def shore_map(land):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in land:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ob.matrix_world
        for e in me.edges:
            a = mw @ me.vertices[e.vertices[0]].co
            b = mw @ me.vertices[e.vertices[1]].co
            if (a.z > 0) != (b.z > 0):
                p = a.lerp(b, a.z / (a.z - b.z))
                pts.append((p.x, p.y, 0.0))
        ev.to_mesh_clear()
    extra = list(scene.get("extra_foam", []))
    for x, y in zip(extra[0::2], extra[1::2]):
        for k in range(12):
            a = k / 12 * math.tau
            pts.append((x + math.cos(a) * 2.5, y + math.sin(a) * 2.5, 0.0))
    kd = KDTree(len(pts))
    for i, p in enumerate(pts):
        kd.insert(p, i)
    kd.balance()
    N = SHORE_N
    px = np.zeros((N, N, 4), dtype=np.float32)
    for j in range(N):
        # image row j (bottom-up in Blender) -> three z; three z = -blender y
        # Row 0 of the saved PNG is the TOP row; Blender pixel rows go bottom
        # up, so row j here maps to v = j/N measured from the bottom.
        tz = -SHORE_EXTENT + (j + 0.5) / N * 2 * SHORE_EXTENT  # three z at v
        by = -tz
        for i in range(N):
            tx = -SHORE_EXTENT + (i + 0.5) / N * 2 * SHORE_EXTENT
            _, _, d = kd.find((tx, by, 0.0))
            v = min(1.0, d / SHORE_MAX)
            px[j, i] = (v, v, v, 1.0)
    img = bpy.data.images.new("shore", N, N, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(px.ravel())
    out = REPO / "public" / "world" / "shore.png"
    img.filepath_raw = str(out)
    img.file_format = "PNG"
    img.save()
    log("shore ->", out, len(pts), "shoreline samples")


def three_dir(v):
    return (round(v.x, 5), round(v.z, 5), round(-v.y, 5))


def write_interactables():
    """Close-up shots for every prop and NPC, and where each NPC stands, in
    three.js coordinates, for src/data/interactables.ts."""
    import json

    def t3(p):
        return [round(p[0], 3), round(p[2], 3), round(-p[1], 3)]

    shots = {}
    for k, (pos, look) in json.loads(scene["poi_shots"]).items():
        shots[f"poi:{k}"] = {"position": t3(pos), "target": t3(look)}
    for k, (pos, look) in json.loads(scene["npc_shots"]).items():
        shots[f"npc:{k}"] = {"position": t3(pos), "target": t3(look)}
    c = json.loads(scene["chest_placement"])["resume"]
    chest = {"position": t3(c["position"]), "yaw": round(c["yaw"], 4)}
    npcs = {}
    for k, v in json.loads(scene["npc_placements"]).items():
        npcs[k] = {"file": v["file"], "position": t3(v["position"]), "yaw": round(v["yaw"], 4),
                   "scale": round(v["scale"], 4)}
    ts = f"""// GENERATED by blender/export_world.py from blender/world.py. Do not edit:
// move a prop or an NPC in Blender and re-export.

export interface Shot {{
  position: [number, number, number];
  target: [number, number, number];
}}

/**
 * The camera's close-up for each clickable thing: "poi:<key>" for a prop
 * (framed from its real bounds), "npc:<key>" for a character (3/4, eye level).
 */
export const SHOTS: Record<string, Shot> = {json.dumps(shots, indent=2)};

/** Where each NPC stands. `yaw` is rotation.y; `scale` makes them 1.8 m tall. */
export const NPC_PLACEMENTS: Record<string, {{ file: string; position: [number, number, number]; yaw: number; scale: number }}> = {json.dumps(npcs, indent=2)};

/** Where the original animated treasure chest stands (Skull Cove). */
export const CHEST_PLACEMENT = {json.dumps(chest, indent=2)};
"""
    out = REPO / "src" / "data" / "interactables.ts"
    out.write_text(ts)
    log("interactables ->", out)


def write_constants():
    sun = stage.sun_dir(stage.SUN_ROT, stage.KEY_EL)
    disc = stage.sun_dir(stage.SUN_ROT, stage.SUN_EL)
    world = scene.world
    sun_ob = bpy.data.objects["KEY_sun"]
    ts = f"""// GENERATED by blender/export_world.py from blender/lib/stage.py and
// blender/lib/materials.py. Do not edit by hand: change the Blender side and
// re-export, so the app and the approved renders keep the same light.

/** Direction TO the key light (three.js world space, normalised). */
export const KEY_DIR: [number, number, number] = {list(three_dir(sun))};
/** Direction TO the visible sun disc in the sky panorama. */
export const SUN_DISC_DIR: [number, number, number] = {list(three_dir(disc))};
/** Key light colour (linear) and intensity (same units as Blender's sun strength). */
export const KEY_COLOR: [number, number, number] = {[round(c, 4) for c in stage.SUN_COLOR]};
export const KEY_INTENSITY = {sun_ob.data.energy};

/** Distance haze, FogExp2 curve, colour in linear working space. */
export const FOG_COLOR: [number, number, number] = {[round(c, 4) for c in M.FOG_COLOR]};
export const FOG_DENSITY = {M.FOG_DENSITY};

/** Sky panorama (HDR, already at the approved strength) and shore field. */
export const SKY_URL = "/world/sky.hdr";
export const SHORE_URL = "/world/shore.png";
/** The shore map spans [-EXTENT, EXTENT] metres on world X and Z. */
export const SHORE_EXTENT = {SHORE_EXTENT};
/** A texel value of 1.0 means this many metres (or more) from any shoreline. */
export const SHORE_MAX = {SHORE_MAX};
"""
    out = REPO / "src" / "data" / "world.ts"
    out.write_text(ts)
    log("constants ->", out)


# --------------------------------------------------------------------------

def main():
    cycles_gpu()
    land = [bpy.data.objects[n] for n in scene["land"]]
    shore_map(land)  # before cutting: the shoreline comes from the full meshes

    for name, size in TEX.items():
        bake_texture(bpy.data.objects[name], size)

    # Flora sources: lift into clear air so their AO is self-occlusion only.
    src = [o for o in bpy.data.collections["SRC_flora"].objects]
    bpy.data.collections["SRC_flora"].hide_render = False
    for i, o in enumerate(src):
        o.location = (i * 40.0, 0, 1500.0)
    baked = [o for o in scene.objects if o.name.startswith(("BLD_", "CHN_", "H2O_", "POI_")) and o.type == "MESH"]
    bake_vertex_colors(baked + src)
    for ob in scene.objects:  # anything left (lava, voids): strip the fog mix
        if ob.type == "MESH":
            for m in ob.data.materials:
                unfog(m)
    bpy.data.collections["SRC_flora"].hide_render = True

    # Group instances under empties (the exporter's GPU-instancing requirement).
    for kind in ("palm", "bush"):
        holder = bpy.data.objects.new(f"FLR_{kind}s", None)
        scene.collection.objects.link(holder)
        for o in [o for o in scene.objects if o.name.startswith(f"FLR_{kind}_")]:
            mw = o.matrix_world.copy()
            o.parent = holder
            o.matrix_world = mw

    # (hide_render excludes the skull's boolean cutters, which share the prefix)
    export = [o for o in scene.objects if o.name.startswith(("ISL_", "BLD_", "FLR_", "LAV_", "H2O_", "CHN_", "POI_"))
              and not o.hide_render]
    select_only(export)
    out = REPO / "src" / "assets" / "world.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(out),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_gpu_instances=True,
        export_lights=False,
        export_cameras=False,
        export_animations=False,
        export_extras=False,
        export_yup=True,
        export_image_format="WEBP",
    )
    log("glb ->", out)

    write_constants()
    write_interactables()
    render_sky()


if __name__ == "__main__":
    main()
