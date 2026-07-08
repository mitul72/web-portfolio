import React, { useEffect } from "react";
import { useGLTF } from "@react-three/drei";
import { SkeletonUtils } from "three-stdlib";
import FantasyGLB from "@/assets/fantasy-island-transformed.glb";
import { Vec3 } from "@/data/portfolio";

/**
 * The fantasy island (the "experience" stop) — a lush treed isle whose slopes
 * carry the career expedition-flag trail (see the stop's subPois). Static
 * model; renders its scene graph and enables soft shadows to match the world.
 *
 * Source bbox is ±239 XZ, Y −39…+87 (a rock skirt hangs below the waterline),
 * so it's scaled down and sits slightly high to hide the skirt underwater.
 */
export default function FantasyIsland({
  position,
  scale = 0.25,
  rotation = [0, 0, 0],
}: {
  position: Vec3;
  scale?: number;
  rotation?: Vec3;
}) {
  const { scene } = useGLTF(FantasyGLB);
  const clone = React.useMemo(() => SkeletonUtils.clone(scene), [scene]);

  useEffect(() => {
    // receiveShadow only: outside the shadow camera's ±120 box (Lighting.tsx),
    // casting would never show — and this is the heaviest island (~50k tris),
    // so keeping it out of the per-frame shadow pass matters most here.
    clone.traverse((o: any) => {
      if (o.isMesh) o.receiveShadow = true;
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

useGLTF.preload(FantasyGLB);
