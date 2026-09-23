"""Outpost architecture, modeled board by board: timber-framed plank houses
with shingle roofs, lit windows and shutters, a pier on posts with hanging
lanterns, barrels and crates. Everything is slightly crooked on purpose; dead
straight lines are what make built things look like CAD, not like a place.

Material slots (shared across all buildings):
  0 wall planks  1 dark timber  2 roof shingles  3 stone  4 window glow
  5 iron  6 lantern glow  7 whitewashed plaster  8 gold  9 sail canvas
  10 black cloth (flags)  11 ship livery (deep lacquered paint)
Face attributes: `tint` (per board variation), `paint` (per building colour).
"""
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

from . import materials as M
from .nodes import material

V = Vector
WALL, TIMBER, ROOF, STONE, GLOW, IRON, LAMP, PLASTER, GOLD, CANVAS, CLOTH, LIVERY = range(12)


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------

def _wood(g, tint, base_ramp, grain_scale=(0.6, 0.6, 9.0)):
    geo = g.node("ShaderNodeNewGeometry")
    p = g.xyz(geo.outputs["Position"])
    # Grain: noise stretched along world Z works for boards in any direction
    # well enough at this scale; per-board tint does the heavy lifting.
    grain = g.noise(g.combine(g.math("MULTIPLY", p["X"], grain_scale[0]), g.math("MULTIPLY", p["Y"], grain_scale[1]),
                              g.math("MULTIPLY", p["Z"], grain_scale[2])), 1.0, detail=3).outputs["Fac"]
    col = g.ramp(g.math("ADD", g.math("MULTIPLY", tint, 0.7), g.math("MULTIPLY", grain, 0.3)), base_ramp)
    return col


def _finish(m, g, bsdf, col, rough=0.8, ao_dist=1.2, ao_k=0.6):
    ao = g.node("ShaderNodeAmbientOcclusion", in_Distance=ao_dist)
    col = g.mix(1.0, col, g.maprange(ao.outputs["AO"], 0, 1, 1 - ao_k, 1), "MULTIPLY")
    g.link(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    return M.fogged(m, g)


def wall_material():
    m, g, bsdf = material("wall_planks")
    tint = g.node("ShaderNodeAttribute", attribute_name="tint").outputs["Fac"]
    paint = g.node("ShaderNodeAttribute", attribute_name="paint").outputs["Fac"]
    wood = _wood(g, tint, [(0.0, (0.2, 0.12, 0.07)), (0.5, (0.36, 0.24, 0.14)), (1.0, (0.52, 0.38, 0.24))])
    # Some buildings have faded paint over the boards; paint wears off by board.
    painted = g.ramp(paint, [(0.0, (0.36, 0.24, 0.14)), (0.3, (0.16, 0.3, 0.36)), (0.55, (0.55, 0.47, 0.33)),
                             (0.8, (0.42, 0.14, 0.09)), (1.0, (0.36, 0.24, 0.14))])
    wear = g.maprange(tint, 0.2, 0.8, 0.75, 0.2)
    col = g.mix(wear, wood, painted)
    return _finish(m, g, bsdf, col, 0.85)


def timber_material():
    m, g, bsdf = material("timber")
    tint = g.node("ShaderNodeAttribute", attribute_name="tint").outputs["Fac"]
    col = _wood(g, tint, [(0.0, (0.08, 0.05, 0.03)), (0.6, (0.16, 0.1, 0.06)), (1.0, (0.25, 0.17, 0.1))])
    return _finish(m, g, bsdf, col, 0.8)


def roof_material():
    m, g, bsdf = material("roof_shingles")
    tint = g.node("ShaderNodeAttribute", attribute_name="tint").outputs["Fac"]
    paint = g.node("ShaderNodeAttribute", attribute_name="paint").outputs["Fac"]
    base = g.ramp(paint, [(0.0, (0.3, 0.09, 0.06)), (0.3, (0.08, 0.2, 0.22)), (0.55, (0.24, 0.16, 0.1)),
                          (0.8, (0.34, 0.2, 0.08)), (1.0, (0.3, 0.09, 0.06))])
    col = g.mix(g.maprange(tint, 0, 1, 0.0, 0.45), base, (0.06, 0.05, 0.04))
    # Moss creeping over the shingles.
    geo = g.node("ShaderNodeNewGeometry")
    moss = g.maprange(g.noise(geo.outputs["Position"], 0.6, detail=3).outputs["Fac"], 0.55, 0.68)
    col = g.mix(g.math("MULTIPLY", moss, 0.7), col, M.GRASS_DEEP)
    return _finish(m, g, bsdf, col, 0.75, 0.8, 0.7)


def stone_material():
    m, g, bsdf = material("stone")
    tint = g.node("ShaderNodeAttribute", attribute_name="tint").outputs["Fac"]
    col = g.ramp(tint, [(0.0, (0.16, 0.15, 0.14)), (0.5, (0.3, 0.28, 0.25)), (1.0, (0.42, 0.39, 0.34))])
    return _finish(m, g, bsdf, col, 0.9, 1.0, 0.7)


def glow_material(name, color, strength):
    m, g, bsdf = material(name)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Strength"].default_value = strength
    return m


def iron_material():
    m, g, bsdf = material("iron")
    bsdf.inputs["Base Color"].default_value = (0.05, 0.045, 0.04, 1)
    bsdf.inputs["Metallic"].default_value = 0.8
    bsdf.inputs["Roughness"].default_value = 0.55
    return M.fogged(m, g)


def plaster_material():
    """Whitewash over stone, with `paint` picking a colour band (0 white,
    1 faded red), weathered and grimy toward the base."""
    m, g, bsdf = material("plaster")
    tint = g.node("ShaderNodeAttribute", attribute_name="tint").outputs["Fac"]
    paint = g.node("ShaderNodeAttribute", attribute_name="paint").outputs["Fac"]
    base = g.mix(g.maprange(paint, 0.4, 0.6), (0.78, 0.75, 0.68), (0.42, 0.07, 0.05))
    col = g.mix(g.maprange(tint, 0.0, 1.0, 0.0, 0.3), base, (0.3, 0.28, 0.25))
    return _finish(m, g, bsdf, col, 0.85)


def gold_material():
    m, g, bsdf = material("gold")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.7, 0.25, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.3
    return M.fogged(m, g)


def canvas_material():
    """Weathered sailcloth: panels (per-face `tint`) a shade apart, grimier
    toward the foot, a little translucent so backlit sails glow."""
    m, g, bsdf = material("canvas")
    tint = g.node("ShaderNodeAttribute", attribute_name="tint").outputs["Fac"]
    col = g.ramp(tint, [(0.0, (0.62, 0.55, 0.42)), (0.5, (0.76, 0.7, 0.56)), (1.0, (0.84, 0.79, 0.66))])
    geo = g.node("ShaderNodeNewGeometry")
    stain = g.maprange(g.noise(geo.outputs["Position"], 0.35, detail=3).outputs["Fac"], 0.5, 0.7, 0.0, 0.35)
    col = g.mix(stain, col, (0.4, 0.34, 0.26))
    g.link(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Subsurface Weight"].default_value = 0.1
    m.use_backface_culling = False
    return _finish(m, g, bsdf, col, 0.92, 1.5, 0.35)


def cloth_material():
    m, g, bsdf = material("cloth_black")
    bsdf.inputs["Base Color"].default_value = (0.02, 0.018, 0.018, 1)
    bsdf.inputs["Roughness"].default_value = 0.95
    m.use_backface_culling = False
    return M.fogged(m, g)


def livery_material():
    """A ship's lacquered paint: deeper and more saturated than the weathered
    house paint, `paint` 0 deep teal .. 1 oxblood, worn per board by `tint`."""
    m, g, bsdf = material("livery")
    tint = g.node("ShaderNodeAttribute", attribute_name="tint").outputs["Fac"]
    paint = g.node("ShaderNodeAttribute", attribute_name="paint").outputs["Fac"]
    base = g.mix(g.maprange(paint, 0.4, 0.6), (0.025, 0.085, 0.1), (0.2, 0.025, 0.018))
    col = g.mix(g.maprange(tint, 0.0, 1.0, 0.0, 0.5), base, (0.12, 0.07, 0.04))
    bsdf.inputs["Specular IOR Level"].default_value = 0.45
    return _finish(m, g, bsdf, col, 0.55)


def all_materials():
    get = bpy.data.materials.get
    return [
        get("wall_planks") or wall_material(),
        get("timber") or timber_material(),
        get("roof_shingles") or roof_material(),
        get("stone") or stone_material(),
        get("window_glow") or glow_material("window_glow", (1.0, 0.55, 0.2), 6.0),
        get("iron") or iron_material(),
        get("lantern_glow") or glow_material("lantern_glow", (1.0, 0.62, 0.28), 14.0),
        get("plaster") or plaster_material(),
        get("gold") or gold_material(),
        get("canvas") or canvas_material(),
        get("cloth_black") or cloth_material(),
        get("livery") or livery_material(),
    ]


# --------------------------------------------------------------------------
# Mesh builder
# --------------------------------------------------------------------------

class Builder:
    """Accumulates boxes/prisms into one bmesh with material + attributes."""

    def __init__(self, rnd, paint=0.0):
        self.rnd = rnd
        self.bm = bmesh.new()
        self.tint = self.bm.faces.layers.float.new("tint")
        self.paint_l = self.bm.faces.layers.float.new("paint")
        self.paint = paint
        self.xf = Matrix.Identity(4)

    def _tag(self, faces, mat, tint=None, paint=None):
        t = self.rnd.random() if tint is None else tint
        for f in faces:
            f.material_index = mat
            f[self.tint] = t
            f[self.paint_l] = self.paint if paint is None else paint

    def box(self, center, size, mat, rot=(0, 0, 0), tint=None, paint=None):
        res = bmesh.ops.create_cube(self.bm, size=1.0)
        vs = res["verts"]
        m = self.xf @ Matrix.Translation(V(center)) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*size, 1))
        bmesh.ops.transform(self.bm, matrix=m, verts=vs)
        self._tag({f for v in vs for f in v.link_faces}, mat, tint, paint)
        return vs

    def cyl(self, a, b, r, mat, sides=8, r2=None, tint=None, paint=None):
        """Cylinder from a to b (world, pre-xf)."""
        a, b = V(a), V(b)
        d = b - a
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=sides,
                                    radius1=r, radius2=r if r2 is None else r2, depth=d.length)
        rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        m = self.xf @ Matrix.Translation((a + b) / 2) @ rot
        bmesh.ops.transform(self.bm, matrix=m, verts=res["verts"])
        self._tag({f for v in res["verts"] for f in v.link_faces}, mat, tint, paint)
        return res["verts"]

    def object(self, name, bevel=0.025):
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        for mat in all_materials():
            me.materials.append(mat)
        if bevel:
            bv = ob.modifiers.new("edges", "BEVEL")
            bv.width = bevel
            bv.segments = 1
            bv.limit_method = "ANGLE"
            bv.harden_normals = False
        for p in me.polygons:
            p.use_smooth = False
        return ob


# --------------------------------------------------------------------------
# House
# --------------------------------------------------------------------------

def house(name, rnd, w=6.0, d=5.0, h=3.2, pitch=38, stilts=0.0, paint=None, floors=1, chimney=True, lean=0.03):
    """A timber-framed plank house, origin at the centre of its footprint on
    the ground. +Y is the front (door side)."""
    b = Builder(rnd, paint if paint is not None else rnd.random())
    # Slight crookedness: shear the whole thing a little.
    b.xf = Matrix(((1, 0, rnd.uniform(-lean, lean), 0), (0, 1, rnd.uniform(-lean, lean), 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    z0 = 0.0
    if stilts > 0:
        for sx in (-1, 0, 1):
            for sy in (-1, 1):
                b.cyl((sx * (w / 2 - 0.2), sy * (d / 2 - 0.2), -1.0), (sx * (w / 2 - 0.2), sy * (d / 2 - 0.2), stilts), 0.16, TIMBER, 6)
        # cross braces
        for sy in (-1, 1):
            b.box((0, sy * (d / 2 - 0.2), stilts * 0.5), (w * 1.05, 0.1, 0.14), TIMBER, rot=(0, math.atan2(stilts, w) * 0.9, 0))
        z0 = stilts
        # deck platform
        for i in range(int((d + 2.2) / 0.32)):
            y = -d / 2 - 0.4 + i * 0.32
            b.box((rnd.uniform(-0.05, 0.05), y, z0 + 0.05), (w + 0.8, 0.29, 0.08), WALL, rot=(0, 0, rnd.uniform(-0.01, 0.01)))
    else:
        # stone footing
        for side in range(4):
            L = w if side % 2 == 0 else d
            n = max(2, int(L / 0.7))
            for i in range(n):
                t = (i + 0.5) / n - 0.5
                if side % 2 == 0:
                    c = (t * w, (d / 2) * (1 if side == 0 else -1), 0.15)
                else:
                    c = ((w / 2) * (1 if side == 1 else -1), t * d, 0.15)
                b.box(c, (0.72 * rnd.uniform(0.8, 1.1), 0.5, 0.55 * rnd.uniform(0.8, 1.2)), STONE,
                      rot=(0, 0, rnd.uniform(-0.1, 0.1)))
        z0 = 0.35

    # Each floor is its own frame; upper floors jut out over the one below
    # (a jettied storey), which gives the silhouette a stepped profile.
    dims = [(w + 0.7 * fl, d + 0.5 * fl) for fl in range(floors)]
    board = 0.3

    def window(cx, cy, cz, facing, ww=0.9, wh=1.1):
        ox = (math.cos(facing), math.sin(facing))  # along the wall
        nrm = V((-ox[1], ox[0], 0))  # outward
        c = V((cx, cy, cz)) + nrm * 0.1
        b.box(c, (ww, 0.05, wh), GLOW, rot=(0, 0, facing))
        b.box(c + nrm * 0.03, (0.07, 0.07, wh), TIMBER, rot=(0, 0, facing))
        b.box(c + nrm * 0.03, (ww, 0.07, 0.07), TIMBER, rot=(0, 0, facing))
        for dz in (-wh / 2, wh / 2):
            b.box(c + nrm * 0.04 + V((0, 0, dz)), (ww + 0.3, 0.12, 0.12), TIMBER, rot=(0, 0, facing))
        for s in (-1, 1):
            b.box(c + nrm * 0.04 + V((ox[0], ox[1], 0)) * s * ww / 2, (0.12, 0.12, wh + 0.2), TIMBER, rot=(0, 0, facing))
            sh = c + nrm * 0.25 + V((ox[0], ox[1], 0)) * s * (ww / 2 + 0.3)
            b.box(sh, (0.5, 0.06, wh), WALL, rot=(rnd.uniform(-0.05, 0.05), 0, facing + s * rnd.uniform(1.1, 1.4)))

    for fl, (fw, fd) in enumerate(dims):
        fz0 = z0 + h * fl
        fz1 = fz0 + h
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.box((sx * fw / 2, sy * fd / 2, (fz0 + fz1) / 2), (0.26, 0.26, h + 0.1), TIMBER)
        for zz in (fz0 + 0.1, fz1):
            b.box((0, fd / 2, zz), (fw + 0.2, 0.24, 0.22), TIMBER)
            b.box((0, -fd / 2, zz), (fw + 0.2, 0.24, 0.22), TIMBER)
            b.box((fw / 2, 0, zz), (0.24, fd + 0.2, 0.22), TIMBER)
            b.box((-fw / 2, 0, zz), (0.24, fd + 0.2, 0.22), TIMBER)
        if fl > 0:
            # joist ends poking out under the jetty
            for i in range(int(fw / 0.8)):
                x = -fw / 2 + 0.4 + i * 0.8
                b.box((x, fd / 2 - 0.2, fz0 - 0.1), (0.16, 0.7, 0.18), TIMBER)
        rows = int(h / board)
        for L, pos, rot in ((fw, lambda t: (t, fd / 2 - 0.02), 0), (fw, lambda t: (t, -fd / 2 + 0.02), 0),
                            (fd, lambda t: (fw / 2 - 0.02, t), math.pi / 2), (fd, lambda t: (-fw / 2 + 0.02, t), math.pi / 2)):
            for r in range(rows):
                x, y = pos(rnd.uniform(-0.04, 0.04))
                b.box((x, y, fz0 + 0.2 + r * board), (L - 0.1, 0.07, board + 0.05), WALL,
                      rot=(rnd.uniform(-0.12, -0.06), rnd.uniform(-0.012, 0.012), rot))
        zc = fz0 + h * 0.55
        nwin = max(1, int(fw / 2.6))
        for i in range(nwin):
            t = (i + 0.5) / nwin - 0.5
            if fl == 0 and abs(t * fw) < 1.0 and nwin > 1:
                continue
            window(t * fw * 0.8, fd / 2, zc, 0.0)
        window(fw / 2, rnd.uniform(-0.2, 0.2) * fd, zc, math.pi / 2)
        window(-fw / 2, rnd.uniform(-0.2, 0.2) * fd, zc, -math.pi / 2)
        if rnd.random() < 0.6:
            window(0, -fd / 2, zc, math.pi)

    wall_top = z0 + h * floors
    w, d = dims[-1]
    fw0, fd0 = dims[0]
    # door, porch awning on brackets, lantern, hanging sign
    dx = 0.0 if int(fw0 / 2.6) % 2 == 0 else fw0 * 0.25
    b.box((dx, fd0 / 2 + 0.06, z0 + 1.0), (1.0, 0.08, 2.0), TIMBER)
    for s in (-1, 1):
        b.box((dx + s * 0.58, fd0 / 2 + 0.1, z0 + 1.05), (0.14, 0.14, 2.2), TIMBER)
    b.box((dx, fd0 / 2 + 0.1, z0 + 2.15), (1.35, 0.16, 0.16), TIMBER)
    if floors == 1 or rnd.random() < 0.5:
        aw = 2.2
        for s in (-1, 1):
            b.box((dx + s * aw / 2, fd0 / 2 + 0.5, z0 + 2.45), (0.12, 1.0, 0.12), TIMBER, rot=(0.6, 0, 0))
        for i in range(4):
            b.box((dx, fd0 / 2 + 0.35 + i * 0.3, z0 + 2.75 - i * 0.12), (aw + 0.4, 0.34, 0.05), ROOF, rot=(0.38, rnd.uniform(-0.03, 0.03), 0))
    lantern(b, V((dx + 0.95, fd0 / 2 + 0.45, z0 + 2.3)), 0.28)
    if rnd.random() < 0.7:
        sx = -fw0 / 2 + 0.2
        b.box((sx - 0.5, fd0 / 2 + 0.2, z0 + 2.9), (1.2, 0.1, 0.1), IRON)
        b.box((sx - 0.8, fd0 / 2 + 0.2, z0 + 2.35), (0.8, 0.06, 0.6), WALL, rot=(0, rnd.uniform(-0.08, 0.08), 0))

    # Roof: gable along X, shingle rows with ragged lower edges, overhang.
    ov = 0.55
    half = d / 2 + ov
    rise = math.tan(math.radians(pitch)) * (d / 2)
    slope_len = math.hypot(half, rise * half / (d / 2))
    ang = math.atan2(rise, d / 2)
    sag = rnd.uniform(0.05, 0.18)
    rows = int(slope_len / 0.42) + 1
    for s in (-1, 1):
        for r in range(rows):
            u = (r + 0.5) / rows  # 0 at ridge .. 1 at eave
            y = s * u * half
            z = wall_top + rise * (1 - u * half / (d / 2)) + 0.12
            ncols = int((w + 2 * ov) / 0.55)
            for c in range(ncols):
                t = (c + 0.5) / ncols - 0.5
                x = t * (w + 2 * ov)
                zz = z - sag * (1 - (2 * t) ** 2)  # sagging ridge line
                b.box((x, y, zz), (0.56, 0.5, 0.06), ROOF,
                      rot=(-s * ang + rnd.uniform(-0.05, 0.05), rnd.uniform(-0.04, 0.04), rnd.uniform(-0.04, 0.04)),
                      tint=rnd.random())
    # ridge beam + gable boards
    b.box((0, 0, wall_top + rise + 0.2 - sag * 0.5), (w + 2 * ov + 0.2, 0.3, 0.3), TIMBER)
    for sx in (-1, 1):
        # gable triangle: boards stepping up
        n = int(rise / 0.3)
        for i in range(n):
            z = wall_top + 0.15 + i * 0.3
            span = d * (1 - (i + 0.5) / n)
            b.box((sx * (w / 2 - 0.02), 0, z), (0.07, span, 0.34), WALL, rot=(0, rnd.uniform(0.06, 0.12) * sx, 0))
        # barge boards
        for sy in (-1, 1):
            mid = V((sx * (w / 2 + ov), sy * half / 2, wall_top + rise / 2 + 0.1))
            b.box(mid, (0.12, slope_len + 0.2, 0.26), TIMBER, rot=(sy * -ang, 0, 0))
    if chimney:
        cx = w * 0.3 * rnd.choice((-1, 1))
        for i in range(int((rise + 1.6) / 0.35)):
            z = wall_top + i * 0.35
            b.box((cx, -d * 0.15, z), (0.9 * rnd.uniform(0.92, 1.05), 0.9 * rnd.uniform(0.92, 1.05), 0.36), STONE,
                  rot=(0, 0, rnd.uniform(-0.08, 0.08)))
    return b.object(name)


# --------------------------------------------------------------------------
# Props
# --------------------------------------------------------------------------

def lantern(b, at, size=0.3):
    """Hanging lantern: iron cage + glowing glass, on a bracket."""
    at = V(at)
    b.box(at + V((0, 0, size * 0.9)), (size * 0.9, size * 0.9, size * 0.15), IRON)
    b.box(at, (size * 0.6, size * 0.6, size * 1.1), LAMP)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box(at + V((sx, sy, 0)) * size * 0.32, (0.04, 0.04, size * 1.2), IRON)
    b.box(at + V((0, 0, -size * 0.6)), (size * 0.8, size * 0.8, size * 0.12), IRON)
    b.box(at + V((0, 0, size * 1.2)), (0.04, 0.04, size * 0.5), IRON)


def barrel(b, at, rnd, h=1.1, r=0.42, lying=False):
    """Staved barrel with bulge and iron hoops."""
    at = V(at)
    staves = 12
    rot_axis = Matrix.Rotation(math.pi / 2, 4, "X") if lying else Matrix.Identity(4)
    yaw = Matrix.Rotation(rnd.uniform(0, math.tau), 4, "Z")
    base_xf = b.xf
    b.xf = base_xf @ Matrix.Translation(at) @ yaw @ rot_axis
    for i in range(staves):
        a = i / staves * math.tau
        for seg, (z0, z1, k) in enumerate(((0, h / 3, 0.9), (h / 3, 2 * h / 3, 1.0), (2 * h / 3, h, 0.9))):
            rr = r * k
            c = V((math.cos(a) * rr, math.sin(a) * rr, (z0 + z1) / 2 - (h / 2 if lying else 0)))
            b.box(c, (0.08, r * 2 * math.pi / staves * 1.02, (z1 - z0) + 0.02), WALL, rot=(0, 0, a), tint=(i * 0.37) % 1)
    for zz in (0.1, h * 0.3, h * 0.7, h - 0.1):
        z = zz - (h / 2 if lying else 0)
        k = 0.95 if zz in (0.1, h - 0.1) else 1.02
        b.cyl((0, 0, z - 0.03), (0, 0, z + 0.03), r * k + 0.03, IRON, sides=12)
    b.cyl((0, 0, h - 0.05 - (h / 2 if lying else 0)), (0, 0, h - 0.02 - (h / 2 if lying else 0)), r * 0.88, TIMBER, sides=12)
    b.xf = base_xf


def crate(b, at, rnd, s=0.9):
    at = V(at)
    rot = (0, 0, rnd.uniform(-0.4, 0.4))
    b.box(at + V((0, 0, s / 2)), (s * 0.94, s * 0.94, s * 0.94), WALL, rot=rot)
    base_xf = b.xf
    b.xf = base_xf @ Matrix.Translation(at + V((0, 0, s / 2))) @ Euler(rot).to_matrix().to_4x4()
    for ax in range(3):
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                c = [0, 0, 0]
                size = [0.1, 0.1, 0.1]
                c[(ax + 1) % 3] = s1 * s / 2
                c[(ax + 2) % 3] = s2 * s / 2
                size[ax] = s
                b.box(c, size, TIMBER)
    b.xf = base_xf


def pier(name, rnd, start, end, width=4.0, deck_z=2.2, lamp_every=9.0):
    """Plank pier on posts from `start` to `end` (XY), with a T-head,
    rope rails, lamp posts, and cargo."""
    b = Builder(rnd, 0.0)
    start, end = V((*start, 0)), V((*end, 0))
    axis = (end - start)
    L = axis.length
    yaw = math.atan2(axis.y, axis.x)
    b.xf = Matrix.Translation(start) @ Matrix.Rotation(yaw, 4, "Z")
    # posts
    n_posts = int(L / 3.0) + 1
    for i in range(n_posts):
        x = i * L / (n_posts - 1)
        for s in (-1, 1):
            p = (x, s * (width / 2 - 0.15), 0)
            b.cyl((p[0], p[1], -3.0), (p[0] + rnd.uniform(-0.05, 0.05), p[1], deck_z + 0.2 + rnd.uniform(0, 0.25)), 0.2, TIMBER, 7)
        b.box((x, 0, deck_z - 0.25), (0.25, width + 0.2, 0.22), TIMBER)
    # deck planks across the pier
    k = 0
    x = 0.0
    while x < L:
        wdt = rnd.uniform(0.26, 0.32)
        if rnd.random() > 0.03:  # the odd missing board
            b.box((x + wdt / 2, rnd.uniform(-0.06, 0.06), deck_z + rnd.uniform(-0.02, 0.02)),
                  (wdt - 0.03, width + rnd.uniform(-0.1, 0.25), 0.1), WALL, rot=(rnd.uniform(-0.02, 0.02), 0, rnd.uniform(-0.02, 0.02)))
        x += wdt
        k += 1
    # stringers
    for s in (-1, 1):
        b.box((L / 2, s * (width / 2 - 0.3), deck_z - 0.12), (L, 0.22, 0.2), TIMBER)
    # T-head at the far end
    tx = L - 3.5
    for i in range(int(12 / 0.3)):
        y = -6 + i * 0.3
        b.box((tx + rnd.uniform(-0.05, 0.05), y, deck_z + 0.01), (7.0, 0.27, 0.1), WALL, rot=(0, 0, math.pi / 2 * 0 + rnd.uniform(-0.01, 0.01)))
    for px in (tx - 3.3, tx + 3.3):
        for py in (-5.8, -2, 2, 5.8):
            b.cyl((px, py, -3.0), (px, py, deck_z + 0.9), 0.24, TIMBER, 7)
    # rope rail posts + lamp posts
    n = int(L / lamp_every)
    for i in range(1, n + 1):
        x = i * lamp_every - 2
        s = 1 if i % 2 else -1
        base = V((x, s * (width / 2 - 0.1), deck_z))
        b.box(base + V((0, 0, 2.0)), (0.18, 0.18, 4.0), TIMBER)
        b.box(base + V((0, -s * 0.45, 3.9)), (0.12, 0.9, 0.12), TIMBER)
        lantern(b, base + V((0, -s * 0.85, 3.45)), 0.32)
    # cargo on the T-head
    for i in range(3):
        barrel(b, V((tx + rnd.uniform(-2.5, 2.5), rnd.uniform(3, 5.5), deck_z + 0.06)), rnd)
    for i in range(3):
        crate(b, V((tx + rnd.uniform(-2.5, 2.5), rnd.uniform(-5.5, -3), deck_z + 0.06)), rnd, rnd.uniform(0.8, 1.1))
    return b.object(name)


def stairs(name, rnd, bottom, top, width=1.6):
    """Wooden stair from `bottom` to `top` (3D points) with posts and rail."""
    b = Builder(rnd, 0.0)
    bottom, top = V(bottom), V(top)
    run = top - bottom
    flat = V((run.x, run.y, 0))
    yaw = math.atan2(flat.y, flat.x)
    steps = max(3, int(run.z / 0.3))
    b.xf = Matrix.Translation(bottom) @ Matrix.Rotation(yaw, 4, "Z")
    L = flat.length
    for i in range(steps):
        t = (i + 0.5) / steps
        b.box((t * L, 0, t * run.z), (L / steps + 0.08, width, 0.1), WALL, rot=(0, 0, rnd.uniform(-0.02, 0.02)))
    ang = math.atan2(run.z, L)
    for s in (-1, 1):
        b.box((L / 2, s * width / 2, run.z / 2 - 0.15), (math.hypot(L, run.z) + 0.3, 0.12, 0.35), TIMBER, rot=(0, -ang, 0))
        b.box((L / 2, s * width / 2, run.z / 2 + 1.0), (math.hypot(L, run.z), 0.08, 0.08), TIMBER, rot=(0, -ang, 0))
        for i in range(0, steps + 1, max(1, steps // 4)):
            t = i / steps
            b.box((t * L, s * width / 2, t * run.z + 0.1), (0.12, 0.12, 2.0), TIMBER)
    return b.object(name)
