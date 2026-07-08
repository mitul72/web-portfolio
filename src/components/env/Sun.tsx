import { forwardRef } from "react";
import { Mesh } from "three";
import { SUN_POSITION, SUN_COLOR } from "./sky";

/**
 * The visual golden-hour sun disc. Bright + emissive so it blooms and reads as
 * the sun on the horizon. Rendered on ALL devices (one cheap sphere); on
 * desktop the ref is also fed to the GodRays effect (Effects.tsx) to trace
 * light shafts outward from it.
 */
const Sun = forwardRef<Mesh>(function Sun(_, ref) {
  return (
    <mesh ref={ref} position={SUN_POSITION}>
      <sphereGeometry args={[26, 24, 24]} />
      <meshBasicMaterial color={SUN_COLOR} toneMapped={false} />
    </mesh>
  );
});

export default Sun;
