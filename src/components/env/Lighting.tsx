import { useThree } from "@react-three/fiber";
import { useEffect } from "react";
import { Color, FogExp2 } from "three";
import { KEY_LIGHT_POSITION, FOG_COLOR, FOG_DENSITY } from "./sky";

/**
 * Warm "Sea of Thieves" lighting rig + horizon fog.
 *  - a warm key sun that casts soft shadows (aligned with the sky's sun via
 *    sky.ts, elevated so shadows stay believable)
 *  - a cool sky fill so shadows aren't muddy
 *  - exponential fog tinted to the sky so the ocean melts into the horizon
 */
export default function Lighting() {
  const { scene } = useThree();

  useEffect(() => {
    // Fog constants live in sky.ts — the Ocean shader mirrors them manually.
    scene.fog = new FogExp2(new Color(FOG_COLOR).getHex(), FOG_DENSITY);
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
        position={KEY_LIGHT_POSITION}
        castShadow
        // 1024 is plenty at this art style — the map is redrawn every frame
        // (animated scene), so halving its resolution is a per-frame win.
        shadow-mapSize={[1024, 1024]}
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
