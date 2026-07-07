import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { InstancedMesh, Object3D, Color } from "three";
import { useVoyage } from "@/components/tour/useVoyage";
import { waveHeight } from "./waves";

const TRAIL = 40; // number of foam puffs in the wake ribbon

/**
 * Foam wake behind the moving ship. A ring buffer of instanced quads is dropped
 * at the ship's recent positions and fades/expands over its lifetime, so a
 * churned-water trail streams out while sailing and dissolves when docked.
 */
export default function Wake() {
  const mesh = useRef<InstancedMesh>(null);
  const dummy = useMemo(() => new Object3D(), []);
  // Per-instance age (seconds); >life = dead/hidden.
  const ages = useMemo(() => new Float32Array(TRAIL).fill(999), []);
  const positions = useMemo(
    () => Array.from({ length: TRAIL }, () => ({ x: 0, z: 0 })),
    []
  );
  const head = useRef(0);
  const dropTimer = useRef(0);

  const life = 1.6;

  useFrame((state, delta) => {
    if (!mesh.current) return;
    const v = useVoyage.getState();
    const t = state.clock.elapsedTime;

    // Drop a new foam puff at the ship's stern while sailing.
    if (v.phase === "sailing") {
      dropTimer.current -= delta;
      if (dropTimer.current <= 0) {
        dropTimer.current = 0.05;
        const { x, y: z } = v.shipPos;
        // Offset slightly behind the ship (opposite heading).
        const sx = x - Math.sin(v.shipHeading) * 6;
        const sz = z - Math.cos(v.shipHeading) * 6;
        positions[head.current] = { x: sx, z: sz };
        ages[head.current] = 0;
        head.current = (head.current + 1) % TRAIL;
      }
    }

    for (let i = 0; i < TRAIL; i++) {
      ages[i] += delta;
      const a = ages[i];
      if (a >= life) {
        // Hide dead puffs by scaling to zero.
        dummy.position.set(0, -9999, 0);
        dummy.scale.setScalar(0);
      } else {
        const k = a / life; // 0..1
        const p = positions[i];
        const y = waveHeight(p.x, p.z, t) * 0.35 + 2.6;
        dummy.position.set(p.x, y, p.z);
        dummy.rotation.x = -Math.PI / 2;
        const scale = 4 + k * 10; // expand as it fades
        dummy.scale.setScalar(scale);
      }
      dummy.updateMatrix();
      mesh.current.setMatrixAt(i, dummy.matrix);
    }
    mesh.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={mesh} args={[undefined, undefined, TRAIL]} frustumCulled={false}>
      <circleGeometry args={[1, 12]} />
      <meshBasicMaterial
        color={new Color("#eafcff")}
        transparent
        opacity={0.35}
        depthWrite={false}
      />
    </instancedMesh>
  );
}
