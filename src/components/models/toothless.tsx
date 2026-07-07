import React, { useEffect, useRef } from "react";
import { useGLTF } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { SkeletonUtils } from "three-stdlib";
import { Group } from "three";
import ToothlessGLB from "@/assets/toothless-transformed.glb";
import { Vec3 } from "@/data/portfolio";

/**
 * Toothless the dragon — ambient scenery perched near an island. Static model,
 * so it just breathes with a gentle bob for a touch of life. Not interactive.
 * Placed via TOOTHLESS_TRANSFORM; tune with SHOW_DEV_COORDS.
 */
export default function Toothless({
  position,
  scale = 1,
  rotation = [0, 0, 0],
}: {
  position: Vec3;
  scale?: number;
  rotation?: Vec3;
}) {
  const group = useRef<Group>(null);
  const { scene } = useGLTF(ToothlessGLB);
  const clone = React.useMemo(() => SkeletonUtils.clone(scene), [scene]);
  const baseY = position[1];

  useEffect(() => {
    clone.traverse((o: any) => {
      if (o.isMesh) {
        o.castShadow = true;
        o.receiveShadow = true;
      }
    });
  }, [clone]);

  // Gentle idle bob so it feels alive.
  useFrame((state) => {
    if (!group.current) return;
    group.current.position.y = baseY + Math.sin(state.clock.elapsedTime * 0.8) * 0.4;
  });

  return (
    <group ref={group} position={position} rotation={rotation} scale={scale}>
      <primitive object={clone} />
    </group>
  );
}

useGLTF.preload(ToothlessGLB);
