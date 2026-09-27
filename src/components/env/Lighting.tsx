import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import { DirectionalLight, FogExp2, Object3D, Vector3 } from "three";
import { FOG_COLOR, FOG_DENSITY, KEY_LIGHT_COLOR, KEY_LIGHT_INTENSITY, SUN_DIRECTION } from "./sky";

/** Half-width of the shadow volume (m): covers an island and its moored ship. */
const SHADOW_HALF = 180;
/** How far ahead of the camera the shadow volume is centred. */
const SHADOW_AHEAD = 140;
/** Snap the volume to this grid so shadow edges don't crawl as the camera drifts. */
const SNAP = 8;

const fwd = new Vector3();

/**
 * Golden-hour key + distance haze. There is deliberately no ambient or
 * hemisphere fill: the sky panorama (Atmosphere) is the fill, exactly as the
 * Blender world was in the approved renders, so the warm-lit / cool-shadow
 * split comes out the same.
 *
 * The islands are ~350 m apart, too far for one crisp shadow map, so the
 * shadow volume follows what the camera is looking at: whichever island
 * you've sailed to gets full-resolution shadows.
 */
export default function Lighting({ shadows = true }: { shadows?: boolean }) {
  const scene = useThree((s) => s.scene);
  const camera = useThree((s) => s.camera);
  const light = useRef<DirectionalLight>(null);
  const target = useMemo(() => new Object3D(), []);

  useEffect(() => {
    const fog = new FogExp2(0x000000, FOG_DENSITY);
    fog.color.copy(FOG_COLOR); // linear, like the Blender value
    scene.fog = fog;
    return () => {
      scene.fog = null;
    };
  }, [scene]);

  useEffect(() => {
    if (light.current) light.current.target = target;
  }, [target]);

  useFrame(() => {
    const l = light.current;
    if (!l) return;
    camera.getWorldDirection(fwd);
    fwd.y = 0;
    fwd.normalize();
    const x = Math.round((camera.position.x + fwd.x * SHADOW_AHEAD) / SNAP) * SNAP;
    const z = Math.round((camera.position.z + fwd.z * SHADOW_AHEAD) / SNAP) * SNAP;
    if (target.position.x === x && target.position.z === z) return;
    target.position.set(x, 0, z);
    target.updateMatrixWorld();
    l.position.set(x, 0, z).addScaledVector(SUN_DIRECTION, 400);
  });

  return (
    <>
      <primitive object={target} />
      <directionalLight
        ref={light}
        color={KEY_LIGHT_COLOR}
        intensity={KEY_LIGHT_INTENSITY}
        castShadow={shadows}
        // 2048 over a 360 m volume is ~18 cm per texel, plenty at this art
        // style; 4096 was 4x the depth fill for every frame, and the map is
        // redrawn every frame because the sea and the ship never stop moving.
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-SHADOW_HALF}
        shadow-camera-right={SHADOW_HALF}
        shadow-camera-top={SHADOW_HALF}
        shadow-camera-bottom={-SHADOW_HALF}
        shadow-camera-near={50}
        shadow-camera-far={900}
        shadow-bias={-0.0004}
        shadow-normalBias={0.04}
      />
    </>
  );
}
