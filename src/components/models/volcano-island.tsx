import React, { useEffect } from "react";
import { useGLTF } from "@react-three/drei";
import { SkeletonUtils } from "three-stdlib";
import VolcanoGLB from "@/assets/volcano-island-transformed.glb";
import { Vec3 } from "@/data/portfolio";

/**
 * The optimized volcano island (a second landmass = a project island).
 *
 * The source model is authored at a huge scale (bbox ~±10000 units), so it's
 * scaled way down to sit alongside the main island (~±50 units). Renders the
 * whole scene graph and enables soft shadows to match the rest of the world.
 */
export default function VolcanoIsland({
  position,
  scale = 0.01,
  rotation = [0, 0, 0],
}: {
  position: Vec3;
  scale?: number;
  rotation?: Vec3;
}) {
  const { scene } = useGLTF(VolcanoGLB);
  const clone = React.useMemo(() => SkeletonUtils.clone(scene), [scene]);

  useEffect(() => {
    clone.traverse((o: any) => {
      if (o.isMesh) {
        o.castShadow = true;
        o.receiveShadow = true;
      }
    });
  }, [clone]);

  return (
    <primitive
      object={clone}
      position={position}
      scale={scale}
      rotation={rotation}
    />
  );
}

useGLTF.preload(VolcanoGLB);
