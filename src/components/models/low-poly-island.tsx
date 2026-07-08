import React, { useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import { SkeletonUtils } from "three-stdlib";
import { Group } from "three";
import IslandGLB from "@/assets/low-poly-island-transformed.glb";
import { Vec3 } from "@/data/portfolio";

/**
 * The low-poly FLOATING island (the "contact"/socials stop). The source model
 * is a classic floating-island silhouette — terrain on top, a rock spike
 * hanging below — so rather than sinking it like the landmasses, it hovers
 * above the water with a slow magical bob.
 *
 * Source bbox ±583 XZ, Y −920…+851; at scale 0.08 the footprint radius is ~47
 * and the spike bottom is ~73 below the model origin, so `position[1]` must be
 * high enough to keep the tip clear of the waves.
 */
export default function LowPolyIsland({
  position,
  scale = 0.08,
  rotation = [0, 0, 0],
}: {
  position: Vec3;
  scale?: number;
  rotation?: Vec3;
}) {
  const group = useRef<Group>(null);
  const { scene } = useGLTF(IslandGLB);
  const clone = React.useMemo(() => SkeletonUtils.clone(scene), [scene]);

  useEffect(() => {
    // receiveShadow only: outside the shadow camera's ±120 box (Lighting.tsx),
    // casting would never show — skips the shadow depth pass for this island.
    clone.traverse((o: any) => {
      if (o.isMesh) o.receiveShadow = true;
    });
  }, [clone]);

  // Slow levitation bob — sells "floating" without moving its marker/dock.
  useFrame((state) => {
    if (group.current)
      group.current.position.y =
        position[1] + Math.sin(state.clock.elapsedTime * 0.5) * 1.5;
  });

  return (
    <group ref={group} position={position}>
      <primitive object={clone} scale={scale} rotation={rotation} />
    </group>
  );
}

useGLTF.preload(IslandGLB);
