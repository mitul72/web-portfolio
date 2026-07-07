import { useThree } from "@react-three/fiber";
import { useEffect } from "react";
import { Color, FogExp2 } from "three";

/**
 * Warm "Sea of Thieves" lighting rig + horizon fog.
 *  - a warm key sun that casts soft shadows
 *  - a cool sky fill so shadows aren't muddy
 *  - exponential fog tinted to the sky so the ocean melts into the horizon
 */
export default function Lighting() {
  const { scene } = useThree();

  useEffect(() => {
    // Fog color roughly matches the lower sky; density tuned so the island is
    // crisp but the far ocean fades out — killing the hard horizon seam.
    scene.fog = new FogExp2(new Color("#9ec9e8").getHex(), 0.0011);
    return () => {
      scene.fog = null;
    };
  }, [scene]);

  return (
    <>
      {/* Warm key sun. */}
      <directionalLight
        color="#fff1cf"
        intensity={3.0}
        position={[120, 140, -120]}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-120}
        shadow-camera-right={120}
        shadow-camera-top={120}
        shadow-camera-bottom={-120}
        shadow-camera-near={1}
        shadow-camera-far={600}
        shadow-bias={-0.0004}
      />
      {/* Cool sky fill + warm bounce from the water. */}
      <hemisphereLight color="#cfe9ff" groundColor="#3f7f8f" intensity={0.7} />
      <ambientLight intensity={0.25} />
    </>
  );
}
