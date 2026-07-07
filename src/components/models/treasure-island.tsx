import React, { useEffect, useRef } from "react";
import { useGLTF, useAnimations } from "@react-three/drei";
import { SkeletonUtils } from "three-stdlib";
import { Group, LoopOnce } from "three";
import TreasureGLB from "@/assets/treasure-island-transformed.glb";
import { Vec3 } from "@/data/portfolio";
import { useVoyage } from "@/components/tour/useVoyage";

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

  // Hold the chest closed at rest. The FIRST time the ship arrives at the
  // treasure stop, wait 2s, then play the opening animation exactly once (ever)
  // and clamp it open. It never resets or replays afterward.
  useEffect(() => {
    const names = Object.keys(actions);
    const chest = names.length ? actions[names[0]] : null; // the "Scene" clip
    if (!chest) return;

    // Freeze on the first frame so the chest starts closed.
    chest.play();
    chest.paused = true;
    chest.time = 0;

    let hasPlayed = false;
    let delayTimer: ReturnType<typeof setTimeout> | null = null;

    let prev = useVoyage.getState();
    const unsub = useVoyage.subscribe((s) => {
      const arrivedAtTreasure =
        prev.phase === "sailing" &&
        s.phase === "docked" &&
        s.targetStopId === "resume";

      if (arrivedAtTreasure && !hasPlayed) {
        hasPlayed = true;
        // 2-second beat before the chest springs open.
        delayTimer = setTimeout(() => {
          chest.reset();
          chest.setLoop(LoopOnce, 1);
          chest.clampWhenFinished = true;
          chest.paused = false;
          chest.play();
        }, 2000);
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
