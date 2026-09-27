import { useEffect, useMemo, useRef } from "react";
import { ThreeEvent } from "@react-three/fiber";
import { Html, useAnimations, useGLTF } from "@react-three/drei";
import { SkeletonUtils } from "three-stdlib";
import { AnimationAction, Group, LoopOnce, LoopRepeat, Mesh } from "three";
import Anne from "@/assets/npcs/Anne.glb";
import Henry from "@/assets/npcs/Henry.glb";
import Skeleton from "@/assets/npcs/Skeleton.glb";
import Mako from "@/assets/npcs/Mako.glb";
import Sharky from "@/assets/npcs/Sharky.glb";
import { NPC_PLACEMENTS } from "@/data/interactables";
import { NPCS } from "@/data/interact";
import { useInteract } from "@/components/tour/useInteract";
import { activate } from "@/components/tour/activate";
import { DRACO_PATH } from "./loaders";

/** Quaternius "Pirate Kit" characters (CC0), by source file name. */
const FILES: Record<string, string> = {
  "Characters_Anne.gltf": Anne,
  "Characters_Henry.gltf": Henry,
  "Characters_Skeleton.gltf": Skeleton,
  "Characters_Mako.gltf": Mako,
  "Characters_Sharky.gltf": Sharky,
};

function Npc({ id }: { id: string }) {
  const place = NPC_PLACEMENTS[id];
  const npc = NPCS[id];
  const { scene, animations } = useGLTF(FILES[place.file], DRACO_PATH);
  const clone = useMemo(() => SkeletonUtils.clone(scene), [scene]);
  const group = useRef<Group>(null);
  const { actions, mixer } = useAnimations(animations, group);
  const hovered = useInteract((s) => s.hovered === npc.key);
  const talking = useInteract((s) => s.dialogue === id);
  const met = useInteract((s) => s.met.includes(id));

  useEffect(() => {
    clone.traverse((o) => {
      const m = o as Mesh;
      if (m.isMesh) {
        m.castShadow = true;
        m.receiveShadow = true;
        // skinned: the rest-pose bounds don't follow the animation
        m.frustumCulled = false;
        m.userData.interactKey = npc.key;
      }
    });
  }, [clone, npc.key]);

  // Idle by default; a wave when you hover them; a nod ("Yes") when you
  // start talking; back to idle after each one-shot.
  const play = useRef<(name: string, once?: boolean) => void>(() => {});
  useEffect(() => {
    let current: AnimationAction | null = null;
    play.current = (name, once = false) => {
      const next = actions[name];
      if (!next || next === current) return;
      next.reset();
      next.setLoop(once ? LoopOnce : LoopRepeat, Infinity);
      next.clampWhenFinished = once;
      if (current) next.crossFadeFrom(current, 0.3, false);
      next.play();
      current = next;
    };
    // stagger the idles so the islands don't breathe in unison
    play.current("Idle");
    if (actions.Idle) actions.Idle.time = Math.random() * actions.Idle.getClip().duration;
    const done = () => play.current("Idle");
    mixer.addEventListener("finished", done);
    return () => mixer.removeEventListener("finished", done);
  }, [actions, mixer]);
  useEffect(() => {
    if (hovered && !talking) play.current("Wave", true);
  }, [hovered, talking]);
  useEffect(() => {
    if (talking) play.current("Yes", true);
  }, [talking]);

  return (
    <group
      ref={group}
      position={place.position}
      rotation={[0, place.yaw, 0]}
      scale={place.scale}
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
      {/* a generous invisible hit area: a 1.8 m person is small from the dock */}
      <mesh position={[0, 1.0 / place.scale, 0]} userData={{ interactKey: npc.key }}>
        <boxGeometry args={[1.6 / place.scale, 2.4 / place.scale, 1.6 / place.scale]} />
        <meshBasicMaterial visible={false} />
      </mesh>
      {hovered && !talking && (
        <Html position={[0, 2.5 / place.scale, 0]} center zIndexRange={[10, 0]} style={{ pointerEvents: "none" }}>
          <div className="whitespace-nowrap rounded-full border border-amber-200/40 bg-slate-950/80 px-3 py-1 text-sm font-semibold text-amber-100 shadow-lg backdrop-blur">
            {npc.tag}
          </div>
        </Html>
      )}
      {/* Quest marker: a "!" over every host you haven't talked to yet, a
          fixed size on screen so it reads from across the sea. Click it to
          sail over and talk. Gone for good once you've met them. */}
      {!met && !hovered && !talking && (
        <Html position={[0, 2.9 / place.scale, 0]} center zIndexRange={[10, 0]}>
          <button
            onClick={() => activate(npc)}
            aria-label={`Talk to ${npc.name}, ${npc.role}`}
            title={`${npc.name} · ${npc.role}`}
            className="quest-bob flex h-7 w-7 items-center justify-center rounded-full border-2 border-amber-100/80 bg-amber-400 text-base font-black text-slate-950 shadow-[0_0_14px_rgba(251,191,36,0.75)] transition hover:scale-110"
          >
            !
          </button>
        </Html>
      )}
    </group>
  );
}

/** Everyone on the islands. The captain rides the ship (models/ship.tsx). */
export default function Npcs() {
  return (
    <>
      {Object.keys(NPC_PLACEMENTS).map((id) => (
        <Npc key={id} id={id} />
      ))}
    </>
  );
}

Object.values(FILES).forEach((f) => useGLTF.preload(f, DRACO_PATH));
