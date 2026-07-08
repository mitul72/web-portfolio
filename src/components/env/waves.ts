// Shared wave field so the <Ocean /> shader and anything floating on it (the
// ship) agree on where the surface is at a given point/time. The GLSL vertex
// shader in Ocean.tsx mirrors these exact wave terms.

type Dir = [number, number];

const WAVES: { dir: Dir; freq: number; speed: number; amp: number }[] = [
  { dir: [1.0, 0.3], freq: 0.012, speed: 0.9, amp: 3.2 },
  { dir: [-0.4, 1.0], freq: 0.021, speed: 1.1, amp: 1.9 },
  { dir: [0.7, -0.6], freq: 0.045, speed: 1.6, amp: 0.8 },
  { dir: [0.2, 0.9], freq: 0.09, speed: 2.2, amp: 0.35 },
  { dir: [-0.85, 0.4], freq: 0.15, speed: 3.1, amp: 0.18 },
  { dir: [0.55, 0.75], freq: 0.22, speed: 3.8, amp: 0.1 },
];

function norm([x, y]: Dir): Dir {
  const l = Math.hypot(x, y) || 1;
  return [x / l, y / l];
}

/**
 * Surface elevation at ocean-plane coords (px, pz) and time t. Note the ocean
 * plane is rotated -PI/2 on X, so its local (x, y) map to world (x, z).
 */
export function waveHeight(px: number, pz: number, t: number): number {
  let e = 0;
  for (const w of WAVES) {
    const [dx, dy] = norm(w.dir);
    e += Math.sin((px * dx + pz * dy) * w.freq + t * w.speed) * w.amp;
  }
  return e;
}

/**
 * Approximate surface tilt (slope) at a point, for pitch/roll. Central
 * difference of the height field along world X and Z.
 */
export function waveSlope(px: number, pz: number, t: number, eps = 6) {
  const hL = waveHeight(px - eps, pz, t);
  const hR = waveHeight(px + eps, pz, t);
  const hD = waveHeight(px, pz - eps, t);
  const hU = waveHeight(px, pz + eps, t);
  return {
    slopeX: (hR - hL) / (2 * eps), // gradient along X
    slopeZ: (hU - hD) / (2 * eps), // gradient along Z
  };
}
