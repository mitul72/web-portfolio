import { useRef, ReactNode } from "react";
import { useFrame } from "@react-three/fiber";
import { Group, Vector3 } from "three";
import { waveHeight, waveSlope } from "./waves";
import { useVoyage } from "@/components/tour/useVoyage";

/**
 * The ship + its crew. Two motions compose here:
 *
 *  1. SAILING — reads the voyage store and samples its route curve as
 *     `progress` goes 0→1 (arc-length parameterized → uniform speed), turning
 *     the hull to face its travel direction. No physics.
 *  2. BOBBING — on top of the sail position, it heaves/pitches/rolls with the
 *     wave field so it always looks like it's floating, moving or docked.
 *
 * The vessel publishes its live XZ + heading back to the store each frame so
 * the camera can chase it.
 *
 * `baseY` is the resting height; children keep their own local offsets so the
 * deck/crew ride together.
 */
export default function FloatingVessel({
  baseY,
  intensity = 1,
  children,
}: {
  baseY: number;
  intensity?: number;
  children: ReactNode;
}) {
  const ref = useRef<Group>(null);
  // Smoothed heading so the ship turns gracefully instead of snapping.
  const heading = useRef(0);
  // Scratch vectors for curve sampling (no per-frame allocation).
  const point = useRef(new Vector3());
  const tangent = useRef(new Vector3());

  useFrame((state, delta) => {
    if (!ref.current) return;
    const t = state.clock.elapsedTime;
    const v = useVoyage.getState();

    // --- 1. Sail position along the voyage's route curve ---
    // getPointAt is arc-length parameterized, so equal progress steps cover
    // equal water — the speed profile is exactly the gsap ease, nothing else.
    let x: number, z: number;
    if (v.curve) {
      const pos = v.curve.getPointAt(v.progress, point.current);
      x = pos.x;
      z = pos.z;
    } else {
      [x, z] = v.to.position;
    }

    let targetHeading: number;
    if (v.phase === "sailing" && v.curve) {
      // Face along the route. (atan2(x, z) matches the model's +Z-forward.)
      const dir = v.curve.getTangentAt(v.progress, tangent.current);
      targetHeading = Math.atan2(dir.x, dir.z);
    } else {
      // Docked: settle to the dock's authored heading.
      targetHeading = v.to.heading;
    }
    heading.current = dampAngle(heading.current, targetHeading, 6, delta);

    ref.current.position.x = x;
    ref.current.position.z = z;

    // Publish live pose for the camera chase-cam.
    v.setShip(x, z, heading.current);

    // --- 2. Wave bob on top ---
    const h = waveHeight(x, z, t) * 0.35 * intensity;
    ref.current.position.y = baseY + h;

    const { slopeX, slopeZ } = waveSlope(x, z, t);
    ref.current.rotation.x = slopeZ * 0.9 * intensity;
    ref.current.rotation.z = -slopeX * 0.9 * intensity;

    // Heading (yaw) from travel + a tiny idle sway when docked. The ship
    // model's bow is 90° off its local +Z, so offset the yaw a quarter turn
    // so the hull points along the travel direction (not sideways).
    const idleSway = v.phase === "sailing" ? 0 : Math.sin(t * 0.3) * 0.02;
    ref.current.rotation.y = heading.current + Math.PI / 2 + idleSway;
  });

  return <group ref={ref}>{children}</group>;
}

/** Frame-rate-independent angular damping that wraps correctly around ±π. */
function dampAngle(current: number, target: number, lambda: number, dt: number) {
  let diff = target - current;
  while (diff > Math.PI) diff -= Math.PI * 2;
  while (diff < -Math.PI) diff += Math.PI * 2;
  return current + diff * (1 - Math.exp(-lambda * dt));
}
