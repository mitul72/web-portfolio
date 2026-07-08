// -----------------------------------------------------------------------------
// Single source of truth for the sun + fog, shared by:
//  - Atmosphere (the Sky dome's visual sun)
//  - Lighting   (the shadow-casting key light + scene fog)
//  - Ocean      (sun glitter direction + the shader's own horizon fog)
// Mismatched suns/fog between these is what makes a scene feel subtly "off".
// -----------------------------------------------------------------------------

/** Where the visual sun sits in the sky (low = warm golden-hour look). */
export const SUN_POSITION: [number, number, number] = [180, 34, -260];

/** Normalized direction TO the sun — drives the ocean's specular glitter. */
export const SUN_DIRECTION: [number, number, number] = (() => {
  const [x, y, z] = SUN_POSITION;
  const l = Math.hypot(x, y, z);
  return [x / l, y / l, z / l];
})();

/**
 * The key light is art-directed HIGHER than the visual sun: lighting straight
 * from a sunset-low sun makes every shadow enormous and faces too dark. Same
 * azimuth as the sun, believable elevation.
 */
export const KEY_LIGHT_POSITION: [number, number, number] = [150, 110, -200];

/**
 * Fog tinted to the lower sky so water and islands melt into the horizon
 * instead of ending in a hard seam. NOTE: the Ocean's custom ShaderMaterial
 * ignores scene.fog, so it implements this same FogExp2 manually — always
 * change these constants, never the per-file values, to keep them in sync.
 */
export const FOG_COLOR = "#a9c2dc";
export const FOG_DENSITY = 0.0011;
