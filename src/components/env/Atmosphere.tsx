import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Sky, Cloud, Clouds } from "@react-three/drei";
import { Group, MeshBasicMaterial } from "three";

/**
 * Sky + drifting stylized clouds + warm sun for the "Sea of Thieves" look.
 * Fog is set on the scene in the parent (Experience) so the horizon melts into
 * the sky instead of showing a hard seam.
 */
export default function Atmosphere() {
  const clouds = useRef<Group>(null);

  // Slowly drift the whole cloud field so the sky feels alive.
  useFrame((_, delta) => {
    if (clouds.current) clouds.current.position.x += delta * 1.2;
    if (clouds.current && clouds.current.position.x > 400)
      clouds.current.position.x = -400;
  });

  return (
    <>
      <Sky
        distance={450000}
        sunPosition={[180, 34, -260]}
        turbidity={3}
        rayleigh={2.2}
        mieCoefficient={0.004}
        mieDirectionalG={0.8}
      />

      <group ref={clouds}>
        <Clouds material={MeshBasicMaterial} position={[0, 80, -160]}>
          <Cloud
            seed={1}
            segments={40}
            bounds={[220, 24, 60]}
            volume={70}
            color="#ffffff"
            opacity={0.55}
            speed={0.15}
          />
          <Cloud
            seed={7}
            segments={30}
            bounds={[180, 20, 50]}
            volume={55}
            color="#eaf4ff"
            opacity={0.4}
            position={[120, 20, -40]}
            speed={0.1}
          />
        </Clouds>
      </group>
    </>
  );
}
