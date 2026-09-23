// Shared wave field, so the <Ocean /> shader and anything floating on it (the
// ship, the wake) agree on where the surface is at a given point and time.
// The Ocean's GLSL is GENERATED from this table (see `wavesGlsl`), so the two
// can't drift apart.

type Dir = [number, number];

export const WAVES: { dir: Dir; freq: number; speed: number; amp: number }[] = [
  { dir: [1.0, 0.3], freq: 0.012, speed: 0.9, amp: 3.2 },
  { dir: [-0.4, 1.0], freq: 0.021, speed: 1.1, amp: 1.9 },
  { dir: [0.7, -0.6], freq: 0.045, speed: 1.6, amp: 0.8 },
  { dir: [0.2, 0.9], freq: 0.09, speed: 2.2, amp: 0.35 },
  { dir: [-0.85, 0.4], freq: 0.15, speed: 3.1, amp: 0.18 },
  { dir: [0.55, 0.75], freq: 0.22, speed: 3.8, amp: 0.1 },
];

/**
 * Global swell height. The golden-hour sea in the approved renders is calm; at
 * full height the swell would roll straight over the home island's beach
 * (0.4-1.6 m above the waterline).
 */
export const WAVE_SCALE = 0.3;

function norm([x, y]: Dir): Dir {
  const l = Math.hypot(x, y) || 1;
  return [x / l, y / l];
}

/** Surface elevation at world (x, z) and time t. */
export function waveHeight(px: number, pz: number, t: number): number {
  let e = 0;
  for (const w of WAVES) {
    const [dx, dy] = norm(w.dir);
    e += Math.sin((px * dx + pz * dy) * w.freq + t * w.speed) * w.amp;
  }
  return e * WAVE_SCALE;
}

/** Surface slope at a point, for pitch/roll (central difference). */
export function waveSlope(px: number, pz: number, t: number, eps = 6) {
  const hL = waveHeight(px - eps, pz, t);
  const hR = waveHeight(px + eps, pz, t);
  const hD = waveHeight(px, pz - eps, t);
  const hU = waveHeight(px, pz + eps, t);
  return {
    slopeX: (hR - hL) / (2 * eps),
    slopeZ: (hU - hD) / (2 * eps),
  };
}

/**
 * GLSL for the same field: `float waves(vec2 p, out vec2 grad)` returns the
 * UNSCALED elevation at world xz `p` (multiply by WAVE_SCALE yourself) and its
 * analytic gradient. Needs `uniform float uTime`.
 */
export function wavesGlsl(): string {
  const f = (n: number) => n.toFixed(5);
  const terms = WAVES.map((w) => {
    const [dx, dy] = norm(w.dir);
    return `  a = dot(p, vec2(${f(dx)}, ${f(dy)})) * ${f(w.freq)} + uTime * ${f(w.speed)};
  e += sin(a) * ${f(w.amp)};
  grad += cos(a) * ${f(w.amp * w.freq)} * vec2(${f(dx)}, ${f(dy)});`;
  }).join("\n");
  return `float waves(vec2 p, out vec2 grad) {
  float e = 0.0;
  float a;
  grad = vec2(0.0);
${terms}
  return e;
}`;
}
