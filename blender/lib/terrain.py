"""Island ground: a faceted heightfield (beach -> grassy bank -> slopes) that
wraps the base of the rock massif."""
import math

import bmesh
import bpy
from mathutils import Vector, noise

V = Vector


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


class Footprint:
    """Union of noise-warped ellipses. inside(x, y) > 0 on land, 0 at the
    shoreline, and grows toward the interior (roughly 0..1)."""

    def __init__(self, blobs, warp=0.18, seed=0.0, holes=()):
        self.blobs = blobs  # [(cx, cy, rx, ry)]
        self.holes = holes  # [(cx, cy, rx, ry)] carved back out (lagoons, coves)
        self.warp = warp
        self.seed = seed

    def inside(self, x, y):
        best = -9.0
        for cx, cy, rx, ry in self.blobs:
            dx, dy = (x - cx) / rx, (y - cy) / ry
            a = math.atan2(dy, dx)
            wob = 1 + self.warp * noise.noise(V((math.cos(a) * 1.7 + self.seed, math.sin(a) * 1.7, cx * 0.01 + self.seed)))
            wob += 0.06 * noise.noise(V((x * 0.05, y * 0.05, self.seed)))
            best = max(best, 1 - math.hypot(dx, dy) / wob)
        for cx, cy, rx, ry in self.holes:
            dx, dy = (x - cx) / rx, (y - cy) / ry
            wob = 1 + 0.1 * noise.noise(V((x * 0.04, y * 0.04, self.seed + 9)))
            best = min(best, math.hypot(dx, dy) / wob - 1)
        return best


def heightfield(name, fp, bounds, step=1.6, beach=0.1, bank=0.035, bank_h=3.2, top=11.0, seed=3.0, base=0.0,
                floating=False):
    """Beach from the waterline up to `beach`, a short steep grassy bank, then
    rolling slopes rising toward the interior."""
    (x0, y0), (x1, y1) = bounds
    nx, ny = int((x1 - x0) / step), int((y1 - y0) / step)
    bm = bmesh.new()
    verts = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x, y = x0 + i * step, y0 + j * step
            s = fp.inside(x, y)
            if s < 0:
                h = -5.0 * min(1.0, -s * 6) + 0.4
            elif s < beach:
                h = 0.4 + 1.2 * (s / beach)
            elif s < beach + bank:
                h = 1.6 + bank_h * smooth(beach, beach + bank, s)
            else:
                t = smooth(beach + bank, 0.7, s)
                roll = noise.noise(V((x * 0.03, y * 0.03, seed))) * 2.0 + noise.noise(V((x * 0.1, y * 0.1, seed + 5))) * 0.6
                h = 1.6 + bank_h + top * t + roll * min(1.0, (s - beach - bank) * 8)
            row.append(bm.verts.new((x, y, h + base)))
        verts.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
    # Drop cells that are entirely deep underwater: nobody sees them. A
    # floating cap keeps only what's on top of its rock.
    floor = base - 3.5
    dead = [f for f in bm.faces if all(v.co.z < floor for v in f.verts)]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    dec = ob.modifiers.new("facet", "DECIMATE")
    dec.ratio = 0.3
    return ob
