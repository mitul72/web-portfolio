import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Sky, Cloud, Clouds } from "@react-three/drei";
import { Group, MeshBasicMaterial } from "three";
import { SUN_POSITION } from "./sky";

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
      {/* Richer gradient: more rayleigh deepens the blue overhead, a bit more
          turbidity + mie warms the horizon glow around the sun — less washed
          out without changing the golden-hour mood. */}
      {/* Golden hour: higher turbidity + mie for a rich warm haze and a strong
          glow around the low sun; rayleigh keeps the upper sky blue so it's
          sunset, not smog. */}
      <Sky
        distance={450000}
        sunPosition={SUN_POSITION}
        turbidity={8}
        rayleigh={2.4}
        mieCoefficient={0.008}
        mieDirectionalG={0.86}
      />

      <group ref={clouds}>
        {/* Cloud deck height must clear the TALLEST island (fantasy isle
            summit ≈ 80 world units) — the field drifts across the whole scene
            on X, so anything lower shrouds summits as it passes. */}
        <Clouds material={MeshBasicMaterial} position={[0, 150, -160]}>
          {/* Warm-tinted clouds catch the low golden sun (peachy underside),
              not pure white — sells the sunset. */}
          <Cloud
            seed={1}
            segments={40}
            bounds={[220, 24, 60]}
            volume={70}
            color="#ffe6c4"
            opacity={0.55}
            speed={0.15}
          />
          <Cloud
            seed={7}
            segments={30}
            bounds={[180, 20, 50]}
            volume={55}
            color="#ffd7b0"
            opacity={0.4}
            position={[120, 20, -40]}
            speed={0.1}
          />
        </Clouds>
      </group>
    </>
  );
}
