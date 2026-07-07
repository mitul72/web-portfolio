import React, { useEffect, useRef } from "react";
import { useGLTF, useAnimations } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { SkeletonUtils } from "three-stdlib";
import { Group, LoopRepeat } from "three";
import TreasureGLB from "@/assets/treasure-island-transformed.glb";
import { Vec3 } from "@/data/portfolio";
import { useVoyage } from "@/components/tour/useVoyage";

// The baked "Scene" clip is ~6.67s and LOOPS: the chest opens then closes
// again. To keep it open, we play only up to the moment the chest is fully
// open (2.5s) and FREEZE there.
const CHEST_OPEN_TIME = 2.5;
// Delay (ms) after arrival before the chest starts opening.
const CHEST_OPEN_DELAY = 500;

/**
 * The optimized treasure island (the resume/treasure stop). It carries a baked
 * animation ("Scene" — the chest opening, coins/oyster stirring). We hold the
 * chest CLOSED at rest and play the animation once when the ship ARRIVES at the
 * treasure stop, so the chest opens as a reveal moment.
 *
 * Source is authored huge (bbox ~±650 units), so it's scaled way down.
 */
export default function TreasureIsland({
  position,
  scale = 0.02,
  rotation = [0, 0, 0],
}: {
  position: Vec3;
  scale?: number;
  rotation?: Vec3;
}) {
  const group = useRef<Group>(null);
  const { scene, animations } = useGLTF(TreasureGLB);
  const clone = React.useMemo(() => SkeletonUtils.clone(scene), [scene]);
  const { actions, mixer } = useAnimations(animations, group);

  // Soft shadows to match the rest of the world.
  useEffect(() => {
    clone.traverse((o: any) => {
      if (o.isMesh) {
        o.castShadow = true;
        o.receiveShadow = true;
      }
    });
  }, [clone]);

  // The chest action + whether we're currently rolling toward the open frame.
  const chestRef = useRef<import("three").AnimationAction | null>(null);
  const openingRef = useRef(false);

  // Each frame, once the chest animation reaches CHEST_OPEN_TIME, pause it there
  // so the chest stays fully open instead of continuing into its re-close.
  useFrame(() => {
    const chest = chestRef.current;
    if (chest && openingRef.current && !chest.paused) {
      if (chest.time >= CHEST_OPEN_TIME) {
        chest.time = CHEST_OPEN_TIME;
        chest.paused = true; // freeze open
        openingRef.current = false;
      }
    }
  });

  // Hold the chest closed at rest. EACH time the ship arrives at the treasure
  // stop, wait 2s then play the clip up to the OPEN frame (2.5s) and freeze
  // there. When the ship sails away, snap it closed so it re-opens next visit.
  useEffect(() => {
    const names = Object.keys(actions);
    const chest = names.length ? actions[names[0]] : null; // the "Scene" clip
    if (!chest) return;
    chestRef.current = chest;

    // Freeze on the first frame so the chest starts closed.
    chest.play();
    chest.paused = true;
    chest.time = 0;

    let delayTimer: ReturnType<typeof setTimeout> | null = null;

    let prev = useVoyage.getState();
    const unsub = useVoyage.subscribe((s) => {
      const arrivedAtTreasure =
        prev.phase === "sailing" &&
        s.phase === "docked" &&
        s.targetStopId === "resume";
      // Only "left" when we start sailing AWAY to a different target.
      const leftTreasure =
        s.phase === "sailing" &&
        prev.targetStopId === "resume" &&
        s.targetStopId !== "resume";

      if (arrivedAtTreasure) {
        // 2-second beat, then roll the clip forward until the useFrame watcher
        // freezes it at CHEST_OPEN_TIME.
        delayTimer = setTimeout(() => {
          chest.reset();
          chest.setLoop(LoopRepeat, Infinity); // free-running; we pause manually
          chest.time = 0;
          chest.paused = false;
          openingRef.current = true;
          chest.play();
        }, CHEST_OPEN_DELAY);
      } else if (leftTreasure) {
        // Sailing away — cancel any pending open and snap the chest shut so it
        // re-opens fresh next visit.
        if (delayTimer) clearTimeout(delayTimer);
        openingRef.current = false;
        chest.reset();
        chest.paused = true;
        chest.time = 0;
      }
      prev = s;
    });

    return () => {
      unsub();
      if (delayTimer) clearTimeout(delayTimer);
    };
  }, [actions, mixer]);

  return (
    <group ref={group}>
      <primitive
        object={clone}
        position={position}
        scale={scale}
        rotation={rotation}
      />
    </group>
  );
}

useGLTF.preload(TreasureGLB);
