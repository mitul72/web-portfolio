import { useEffect, useMemo, useRef } from "react";
import { ThreeEvent, useFrame } from "@react-three/fiber";
import { Html, useAnimations, useGLTF } from "@react-three/drei";
import { SkeletonUtils } from "three-stdlib";
import { AnimationAction, Color, Group, LoopRepeat, Mesh, MeshPhysicalMaterial, MeshStandardMaterial } from "three";
import ChestGLB from "@/assets/treasure-chest.glb";
import { CHEST_PLACEMENT } from "@/data/interactables";
import { PROPS } from "@/data/interact";
import { STOPS } from "@/data/portfolio";
import { useTour } from "@/components/tour/useTour";
import { useVoyage } from "@/components/tour/useVoyage";
import { useInteract } from "@/components/tour/useInteract";
import { activate } from "@/components/tour/activate";
import { DRACO_PATH } from "./loaders";

// The original portfolio's chest, lifted out of its island by
// blender/extract_chest.py. Its one clip ("Scene", ~6.67 s) opens the lid,
// stirs the coins, then closes again. Fully open at OPEN_AT.
const OPEN_AT = 2.5;
const HOVER = new Color("#ffb45a");

type Phase = "closed" | "opening" | "open" | "closing";

/**
 * The resume stop's treasure chest on Skull Cove. Held shut at rest; opens
 * when the ship moors at Skull Cove (and holds open), plays its own closing
 * half when you sail away. Hover glows it, click opens the resume.
 */
export default function TreasureChest() {
  const { scene, animations } = useGLTF(ChestGLB, DRACO_PATH);
  const clone = useMemo(() => SkeletonUtils.clone(scene), [scene]);
  const group = useRef<Group>(null);
  const { actions } = useAnimations(animations, group);
  const prop = PROPS.POI_resume;
  const hovered = useInteract((s) => s.hovered === prop.key);
  const activeIndex = useTour((s) => s.activeIndex);
  const docked = useVoyage((s) => s.phase === "docked");
  const here = activeIndex !== null && STOPS[activeIndex]?.id === "resume" && docked;

  const meshes = useMemo(() => {
    const out: Mesh[] = [];
    clone.traverse((o) => {
      const m = o as Mesh;
      if (!m.isMesh) return;
      m.castShadow = true;
      m.receiveShadow = true;
      m.frustumCulled = false; // skinned: the lid leaves its rest bounds
      m.userData.interactKey = prop.key;
      const own = (m.material as MeshStandardMaterial).clone();
      // Never transmissive: one transmissive material makes three render the
      // whole opaque scene a second time every frame (full-res, 4x MSAA) as
      // the refraction source. `npm run assets` strips it from the GLB; this
      // guards a fresh extract from Blender.
      if ((own as MeshPhysicalMaterial).isMeshPhysicalMaterial) (own as MeshPhysicalMaterial).transmission = 0;
      own.userData.baseEmissive = own.emissive.clone();
      own.userData.baseIntensity = own.emissiveIntensity;
      m.material = own;
      out.push(m);
    });
    return out;
  }, [clone, prop.key]);

  useEffect(() => {
    meshes.forEach((m) => {
      const mat = m.material as MeshStandardMaterial;
      mat.emissive.copy(hovered ? HOVER : mat.userData.baseEmissive);
      mat.emissiveIntensity = hovered ? 0.35 : mat.userData.baseIntensity;
    });
  }, [hovered, meshes]);

  // Drive the clip by hand: closed = frame 0, open = OPEN_AT.
  const clip = useRef<AnimationAction | null>(null);
  const phase = useRef<Phase>("closed");
  useEffect(() => {
    const a = Object.values(actions)[0] ?? null;
    if (!a) return;
    clip.current = a;
    a.reset().setLoop(LoopRepeat, Infinity).play();
    a.time = 0;
    a.paused = true;
  }, [actions]);

  useEffect(() => {
    const a = clip.current;
    if (!a) return;
    if (here && phase.current !== "open" && phase.current !== "opening") {
      // Reopen from wherever the lid is: if it's partway through closing,
      // jump to the point in the opening half with the lid at the same angle.
      if (a.time > OPEN_AT) {
        const closedFraction = (a.time - OPEN_AT) / (a.getClip().duration - OPEN_AT);
        a.time = OPEN_AT * (1 - closedFraction);
      }
      a.paused = false;
      phase.current = "opening";
    } else if (!here && (phase.current === "open" || phase.current === "opening")) {
      // play the clip's own closing half
      if (a.time < OPEN_AT) a.time = OPEN_AT;
      a.paused = false;
      phase.current = "closing";
    }
  }, [here]);

  useFrame(() => {
    const a = clip.current;
    if (!a) return;
    if (phase.current === "opening" && a.time >= OPEN_AT) {
      a.time = OPEN_AT;
      a.paused = true;
      phase.current = "open";
    } else if (phase.current === "closing" && a.time >= a.getClip().duration - 0.05) {
      a.time = 0;
      a.paused = true;
      phase.current = "closed";
    }
  });

  return (
    <group
      ref={group}
      position={CHEST_PLACEMENT.position as [number, number, number]}
      rotation={[0, CHEST_PLACEMENT.yaw, 0]}
      onPointerMove={(e: ThreeEvent<PointerEvent>) => {
        e.stopPropagation();
        if (useInteract.getState().hovered !== prop.key) useInteract.getState().setHovered(prop.key);
        document.body.style.cursor = "pointer";
      }}
      onPointerOut={() => {
        useInteract.getState().setHovered(null);
        document.body.style.cursor = "auto";
      }}
      onClick={(e: ThreeEvent<MouseEvent>) => {
        e.stopPropagation();
        activate(prop);
      }}
    >
      <primitive object={clone} />
      {/* padded hit area: the chest is small from the dock */}
      <mesh position={[0, 1.0, 0]}>
        <boxGeometry args={[3.6, 2.4, 3.0]} />
        <meshBasicMaterial visible={false} />
      </mesh>
      {hovered && (
        <Html position={[0, 3.0, 0]} center zIndexRange={[10, 0]} style={{ pointerEvents: "none" }}>
          <div className="whitespace-nowrap rounded-full border border-amber-200/40 bg-slate-950/80 px-3 py-1 text-sm font-semibold text-amber-100 shadow-lg backdrop-blur">
            {prop.tag}
          </div>
        </Html>
      )}
    </group>
  );
}

useGLTF.preload(ChestGLB, DRACO_PATH);
