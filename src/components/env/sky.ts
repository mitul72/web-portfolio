// -----------------------------------------------------------------------------
// Single source of truth for the sun + fog, shared by:
//  - Atmosphere (the Sky dome's visual sun)
//  - Lighting   (the shadow-casting key light + scene fog)
//  - Ocean      (sun glitter direction + the shader's own horizon fog)
// Mismatched suns/fog between these is what makes a scene feel subtly "off".
// -----------------------------------------------------------------------------

/**
 * Where the visual sun sits in the sky. Kept LOW for a golden-hour rake — long
 * light across the water, big warm horizon glow, and the god-ray shafts
 * (Effects.tsx) anchor to this on-screen sun. Placed to the FAR LEFT and deep
 * on the horizon so the sun disc clears the Isle of Voyages (FANTASY_TRANSFORM
 * at X≈180, summit ~y76) — the two used to overlap on the same bearing.
 */
export const SUN_POSITION: [number, number, number] = [-160, 26, -340];

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
export const KEY_LIGHT_POSITION: [number, number, number] = [-130, 95, -260];

// -----------------------------------------------------------------------------
// GOLDEN-HOUR PALETTE — warm key, warm sun tint, warm fog. Read by Lighting,
// Ocean, and Atmosphere so the whole frame agrees on the time of day.
// -----------------------------------------------------------------------------

/** Warm sun tint (key light + ocean glitter + god-ray color). */
export const SUN_COLOR = "#ffd9a0";
/** Warm key-light color (a touch less saturated than the sun disc). */
export const KEY_LIGHT_COLOR = "#ffe4c0";
/** Warm sky fill from above; ground bounce from the lit water. */
export const SKY_FILL_COLOR = "#bcd6ff";
export const WATER_BOUNCE_COLOR = "#6a5a3e";

/**
 * Fog tinted PEACH toward the sun so water and islands melt into a warm hazy
 * horizon instead of a cool grey seam. NOTE: the Ocean's custom ShaderMaterial
 * ignores scene.fog, so it implements this same FogExp2 manually — always
 * change these constants, never the per-file values, to keep them in sync.
 */
export const FOG_COLOR = "#f0c9a0";
export const FOG_DENSITY = 0.0013;
