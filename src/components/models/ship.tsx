import { useEffect, useMemo, useRef } from "react";
import { ThreeEvent, useFrame } from "@react-three/fiber";
import { Html, useAnimations, useGLTF } from "@react-three/drei";
import { SkeletonUtils } from "three-stdlib";
import { Group, LoopRepeat, Mesh, MeshStandardMaterial } from "three";
import ShipGLB from "@/assets/ship-transformed.glb";
import CaptainGLB from "@/assets/npcs/Captain_Barbarossa.glb";
import { STOPS } from "@/data/portfolio";
import { NPCS } from "@/data/interact";
import FloatingVessel from "@/components/env/FloatingVessel";
import Marker from "@/components/tour/Marker";
import { useInteract } from "@/components/tour/useInteract";
import { activate } from "@/components/tour/activate";

// The galleon's own frame (blender/lib/ship.py, exported by export_ship.py):
// bow toward -Z, waterline at y = 0, origin on the mainmast. FloatingVessel
// yaws by heading + pi/2, so a further quarter turn points the bow along the
// travel direction.
const BOW_FIX = Math.PI / 2;
/** Where the helmsman stands: behind the wheel on the quarterdeck. */
const HELM: [number, number, number] = [0, 5.46, 8.5];
const CREW_SCALE = 1.2; // the kit characters at 1.8 m, like the NPCs

/** Flag hoist in the ship frame: the flag flies aft from here along +Z. */
const FLAG_HOIST_Z = 0.21;

/** Wave a flag in the vertex shader: more the further from the hoist. */
function waveFlag(mat: MeshStandardMaterial, uTime: { value: number }) {
  mat.onBeforeCompile = (shader) => {
    shader.uniforms.uTime = uTime;
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", "#include <common>\nuniform float uTime;")
      .replace(
        "#include <begin_vertex>",
        `#include <begin_vertex>
        float fly = max(position.z - ${FLAG_HOIST_Z.toFixed(2)}, 0.0);
        transformed.x += sin(uTime * 5.0 - position.z * 2.2 + position.y) * 0.13 * fly;
        transformed.y += sin(uTime * 3.1 - position.z * 1.7) * 0.04 * fly;`
      );
  };
  mat.customProgramCacheKey = () => "ship-flag";
}

function Captain() {
  const { scene, animations } = useGLTF(CaptainGLB);
  const clone = useMemo(() => SkeletonUtils.clone(scene), [scene]);
  const group = useRef<Group>(null);
  const { actions } = useAnimations(animations, group);
  const npc = NPCS.captain;
  const hovered = useInteract((s) => s.hovered === npc.key);

  useEffect(() => {
    clone.traverse((o) => {
      const m = o as Mesh;
      if (m.isMesh) {
        m.castShadow = true;
        m.frustumCulled = false; // skinned: rest-pose bounds don't follow the animation
        m.userData.interactKey = npc.key;
      }
    });
    const idle = actions.Idle;
    idle?.reset().setLoop(LoopRepeat, Infinity).play();
  }, [clone, actions, npc.key]);

  return (
    <group
      ref={group}
      position={HELM}
      rotation={[0, Math.PI, 0]}
      scale={CREW_SCALE}
      onPointerMove={(e: ThreeEvent<PointerEvent>) => {
        e.stopPropagation();
        if (useInteract.getState().hovered !== npc.key) useInteract.getState().setHovered(npc.key);
        document.body.style.cursor = "pointer";
      }}
      onPointerOut={() => {
        useInteract.getState().setHovered(null);
        document.body.style.cursor = "auto";
      }}
      onClick={(e: ThreeEvent<MouseEvent>) => {
        e.stopPropagation();
        activate(npc);
      }}
    >
      <primitive object={clone} />
      <mesh position={[0, 0.9, 0]}>
        <boxGeometry args={[1.6, 2.2, 1.6]} />
        <meshBasicMaterial visible={false} />
      </mesh>
      {hovered && (
        <Html position={[0, 2.2, 0]} center zIndexRange={[10, 0]} style={{ pointerEvents: "none" }}>
          <div className="whitespace-nowrap rounded-full border border-amber-200/40 bg-slate-950/80 px-3 py-1 text-sm font-semibold text-amber-100 shadow-lg backdrop-blur">
            {npc.tag}
          </div>
        </Html>
      )}
    </group>
  );
}

/**
 * The player's galleon (built and approved in Blender, blender/lib/ship.py)
 * with the captain at the helm, sailing between the islands on the voyage
 * route; plus each stop's floating tag.
 */
export default function Ship() {
  const { scene } = useGLTF(ShipGLB);
  const uTime = useMemo(() => ({ value: 0 }), []);

  const model = useMemo(() => {
    const r = scene.clone(true);
    r.traverse((o) => {
      const m = o as Mesh;
      if (!m.isMesh) return;
      const mat = m.material as MeshStandardMaterial;
      const glows = mat.name === "window_glow" || mat.name === "lantern_glow";
      m.castShadow = !glows;
      m.receiveShadow = !glows;
      m.raycast = () => {}; // only the captain is clickable aboard
      if (m.name.startsWith("SHP_flag")) {
        const own = mat.clone();
        waveFlag(own, uTime);
        m.material = own;
      }
    });
    return r;
  }, [scene, uTime]);

  useFrame((_, delta) => {
    uTime.value += delta;
  });

  return (
    <>
      <FloatingVessel baseY={0} intensity={0.8}>
        <group rotation={[0, BOW_FIX, 0]}>
          <primitive object={model} />
          <Captain />
        </group>
      </FloatingVessel>
      {STOPS.map((stop, i) => (
        <Marker key={stop.id} stop={stop} index={i} />
      ))}
    </>
  );
}

useGLTF.preload(ShipGLB);
useGLTF.preload(CaptainGLB);
