"""Island materials. Every input is geometry or position based (no UVs), so all
of it can be baked to texture maps for glTF once the look is approved."""
import bpy

from .nodes import material

# Distance haze, the same curve as three.js FogExp2: factor = 1 - exp(-(d*k)^2).
# Mixed in at the shader output as an emission, so it behaves like the app's
# fog (which blends the final lit colour) rather than tinting the albedo.
FOG_COLOR = (0.3, 0.36, 0.48)
FOG_DENSITY = 0.0011


def fogged(m, g):
    out = g.n["Material Output"]
    surf = out.inputs["Surface"].links[0].from_socket
    cam = g.node("ShaderNodeCameraData")
    k = g.math("MULTIPLY", cam.outputs["View Distance"], FOG_DENSITY)
    f = g.math("SUBTRACT", 1.0, g.math("EXPONENT", g.math("MULTIPLY", g.math("MULTIPLY", k, k), -1.0)))
    em = g.node("ShaderNodeEmission", in_Strength=1.0)
    em.inputs["Color"].default_value = (*FOG_COLOR, 1)
    mix = g.node("ShaderNodeMixShader")
    g.link(f, mix.inputs[0])
    g.link(surf, mix.inputs[1])
    g.link(em.outputs[0], mix.inputs[2])
    g.link(mix.outputs[0], out.inputs["Surface"])
    return m

# Palette: warm sandstone rock, saturated tropical greens, pale gold sand.
ROCK_DARK = (0.16, 0.095, 0.065)
ROCK_MID = (0.36, 0.23, 0.15)
ROCK_LIGHT = (0.58, 0.43, 0.3)
ROCK_WET = (0.045, 0.04, 0.035)
GRASS_DEEP = (0.07, 0.19, 0.03)
GRASS = (0.16, 0.36, 0.05)
GRASS_SUN = (0.36, 0.5, 0.09)
SAND = (0.72, 0.56, 0.36)
SAND_WET = (0.34, 0.25, 0.16)
DIRT = (0.26, 0.16, 0.09)


def _cavity(g, color, distance=6.0, strength=1.0):
    ao = g.node("ShaderNodeAmbientOcclusion", in_Distance=distance)
    shade = g.maprange(ao.outputs["AO"], 0.0, 1.0, 1.0 - strength, 1.0)
    return g.mix(1.0, color, shade, "MULTIPLY")


def rock(name="rock", dark=None, mid=None, light=None, moss=1.0):
    """Stratified cliff rock. Palette overrides give each island its own
    stone (basalt, bone-pale limestone...) with the same construction."""
    ROCK_DARK, ROCK_MID, ROCK_LIGHT = (dark or globals()["ROCK_DARK"], mid or globals()["ROCK_MID"],
                                       light or globals()["ROCK_LIGHT"])
    m, g, bsdf = material(name)
    geo = g.node("ShaderNodeNewGeometry")
    pos = geo.outputs["Position"]
    p = g.xyz(pos)
    nrm = g.xyz(geo.outputs["Normal"])

    # Strata: bands in Z, warped so they wander, uneven in width.
    warp = g.noise(pos, 0.03, detail=1).outputs["Fac"]
    band_z = g.math("ADD", p["Z"], g.math("MULTIPLY", warp, 14.0))
    bands = g.noise(g.combine(g.math("MULTIPLY", p["X"], 0.02), 0.0, band_z), 0.09, detail=2, rough=0.5)
    band_mid = tuple((a + b) / 2 for a, b in zip(ROCK_MID, ROCK_LIGHT))
    strata = g.ramp(bands.outputs["Fac"], [(0.35, ROCK_MID), (0.55, band_mid), (0.7, ROCK_LIGHT)])

    # Per-facet tonal variation: breaks the big faces up.
    cell = g.voronoi(pos, 0.12).outputs["Distance"]
    col = g.mix(g.maprange(cell, 0.0, 1.0, 0.0, 0.35), strata, ROCK_DARK)

    # Sun-bleached tops of ledges, grime streaking down under them.
    up = g.maprange(nrm["Z"], 0.25, 0.6, smooth=True)
    col = g.mix(g.math("MULTIPLY", up, 0.45), col, ROCK_LIGHT)
    streak = g.noise(g.combine(g.math("MULTIPLY", p["X"], 0.5), g.math("MULTIPLY", p["Y"], 0.5),
                               g.math("MULTIPLY", p["Z"], 0.04)), 1.0, detail=2)
    grime = g.maprange(streak.outputs["Fac"], 0.5, 0.7, 0.0, 0.5)
    col = g.mix(grime, col, ROCK_DARK)

    # Moss/grass on up-facing ledges, patchy.
    patch = g.noise(pos, 0.15, detail=3).outputs["Fac"]
    moss_up = g.maprange(nrm["Z"], 0.68, 0.8, smooth=True)
    moss = g.math("MULTIPLY", g.math("MULTIPLY", moss_up, g.maprange(patch, 0.35, 0.5), clamp=True), moss)
    grass_col = g.mix(patch, GRASS_DEEP, GRASS)
    col = g.mix(moss, col, grass_col)

    # Wet, dark band at the waterline, ragged top edge.
    wet_top = g.math("ADD", p["Z"], g.math("MULTIPLY", patch, -2.0))
    wet = g.maprange(wet_top, 1.0, -0.6, smooth=True)
    col = g.mix(wet, col, ROCK_WET)

    col = _cavity(g, col, 8.0, 0.85)
    g.link(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.88
    g.link(g.maprange(wet, 0, 1, 0.88, 0.25), bsdf.inputs["Roughness"])
    bsdf.inputs["Specular IOR Level"].default_value = 0.25
    return fogged(m, g)


def terrain(name="terrain", sand=None, sand_alt=None, sand_wet=None, grass_line=1.1):
    """Sand -> grass by height, dirt/rock on steep slopes. `grass_line` is the
    height (m) where beach turns to grass."""
    SAND, SAND_WET = sand or globals()["SAND"], sand_wet or globals()["SAND_WET"]
    alt = sand_alt or (0.62, 0.46, 0.28)
    m, g, bsdf = material(name)
    geo = g.node("ShaderNodeNewGeometry")
    pos = geo.outputs["Position"]
    p = g.xyz(pos)
    nrm = g.xyz(geo.outputs["Normal"])

    big = g.noise(pos, 0.02, detail=3).outputs["Fac"]
    small = g.noise(pos, 0.3, detail=2).outputs["Fac"]
    grass = g.ramp(g.math("ADD", g.math("MULTIPLY", big, 0.7), g.math("MULTIPLY", small, 0.3)),
                   [(0.35, GRASS_DEEP), (0.52, GRASS), (0.68, GRASS_SUN)])
    sand = g.mix(g.maprange(small, 0.3, 0.7, 0.0, 0.25), SAND, alt)
    sand = g.mix(g.maprange(p["Z"], 0.9, 0.2, smooth=True), sand, SAND_WET)

    # Grass line wanders with noise.
    line = g.math("ADD", p["Z"], g.math("MULTIPLY", big, -2.5))
    to_grass = g.maprange(line, grass_line, grass_line + 0.5, smooth=True)
    col = g.mix(to_grass, sand, grass)

    steep = g.maprange(nrm["Z"], 0.8, 0.65, smooth=True)
    col = g.mix(g.math("MULTIPLY", steep, to_grass), col, DIRT)

    col = _cavity(g, col, 5.0, 0.7)
    g.link(col, bsdf.inputs["Base Color"])
    wet = g.maprange(p["Z"], 0.8, 0.1, smooth=True)
    g.link(g.maprange(wet, 0, 1, 0.92, 0.3), bsdf.inputs["Roughness"])
    bsdf.inputs["Specular IOR Level"].default_value = 0.2
    return fogged(m, g)


def sea(name="sea"):
    """Deep blue far out, turquoise over the shallows, foam hugging the shore.
    Driven by the `shore` attribute (metres to the nearest shoreline) that the
    stage writes onto the water mesh; three.js gets the same field as a
    texture."""
    m, g, bsdf = material(name)
    attr = g.node("ShaderNodeAttribute", attribute_name="shore")
    d = attr.outputs["Fac"]
    geo = g.node("ShaderNodeNewGeometry")
    pos = geo.outputs["Position"]

    depth = g.maprange(d, 0.0, 70.0, smooth=True)
    col = g.ramp(depth, [(0.0, (0.05, 0.42, 0.38)), (0.25, (0.02, 0.2, 0.26)), (1.0, (0.004, 0.035, 0.07))])

    # Foam: a ragged line at the shore plus a second, fainter surf line.
    n1 = g.noise(pos, 0.25, detail=3).outputs["Fac"]
    edge = g.math("ADD", d, g.math("MULTIPLY", n1, 4.0))
    foam = g.maprange(edge, 4.5, 2.2, smooth=True)
    surf = g.math("MULTIPLY", g.maprange(edge, 9.0, 7.5, smooth=True), g.maprange(edge, 6.0, 7.5, smooth=True))
    lace = g.maprange(g.noise(pos, 1.2, detail=2).outputs["Fac"], 0.45, 0.6)
    foam = g.math("MAXIMUM", foam, g.math("MULTIPLY", surf, lace))
    foam = g.math("MINIMUM", foam, 1.0)
    col = g.mix(g.math("MULTIPLY", foam, 0.85), col, (0.85, 0.88, 0.85))
    g.link(col, bsdf.inputs["Base Color"])
    g.link(g.maprange(foam, 0, 1, 0.1, 0.7), bsdf.inputs["Roughness"])

    # Ripples: two noise bump layers.
    b1 = g.node("ShaderNodeBump", in_Strength=0.6, in_Distance=1.0)
    swell = g.noise(g.combine(g.math("MULTIPLY", g.xyz(pos)["X"], 0.5), g.xyz(pos)["Y"], 0.0), 0.12, detail=4, rough=0.55)
    g.link(swell.outputs["Fac"], b1.inputs["Height"])
    b2 = g.node("ShaderNodeBump", in_Strength=0.35, in_Distance=0.2)
    g.link(g.noise(pos, 0.7, detail=3).outputs["Fac"], b2.inputs["Height"])
    g.link(b1.outputs["Normal"], b2.inputs["Normal"])
    g.link(b2.outputs["Normal"], bsdf.inputs["Normal"])
    return fogged(m, g)


def emissive(name, color, strength):
    """Self-lit surfaces (lava, lamp glass). Survives glTF as-is."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat, g, bsdf = material(name)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def waterfall(name="waterfall"):
    """Falling water: streaks stretched along the fall, a little self-lit so
    it reads as bright water at dusk rather than grey plastic."""
    mat, g, bsdf = material(name)
    geo = g.node("ShaderNodeNewGeometry")
    p = g.xyz(geo.outputs["Position"])
    streak = g.noise(g.combine(g.math("MULTIPLY", p["X"], 1.4), g.math("MULTIPLY", p["Y"], 1.4),
                               g.math("MULTIPLY", p["Z"], 0.08)), 1.0, detail=3).outputs["Fac"]
    col = g.ramp(streak, [(0.3, (0.18, 0.42, 0.5)), (0.55, (0.55, 0.78, 0.82)), (0.75, (0.92, 0.96, 0.95))])
    g.link(col, bsdf.inputs["Base Color"])
    g.link(col, bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.35
    bsdf.inputs["Roughness"].default_value = 0.25
    return fogged(mat, g)
