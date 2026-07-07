import { useEffect, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import gsap from "gsap";
import { Vector3 } from "three";
import { HOME_CAMERA } from "@/data/portfolio";
import { dockForIndex } from "@/data/anchors";
import { useTour } from "./useTour";
import { useVoyage } from "./useVoyage";

/**
 * Owns the camera across three regimes:
 *
 *  - FREE LOOK (no active stop, docked): OrbitControls is in charge, with a
 *    slow auto-rotate drift.
 *  - SAILING: a cinematic chase-cam follows the moving ship from behind/side,
 *    swooping low over the water. Driven per-frame from the voyage store.
 *  - ARRIVED (docked at a stop): gsap eases the camera to the dock's framing to
 *    reveal the island, then hands back to OrbitControls.
 *
 * The OrbitControls-vs-gsap reconciliation (update target + call update()) is
 * preserved so user drags never snap.
 */
export default function CameraRig() {
  const controls = useRef<OrbitControlsImpl>(null);
  const { camera } = useThree();
  const activeIndex = useTour((s) => s.activeIndex);

  // Scratch vectors reused each frame (no per-frame allocation).
  const desiredPos = useRef(new Vector3());
  const desiredTarget = useRef(new Vector3());
  // All camera gsap tweens live here so a starting voyage can cancel them —
  // otherwise the establishing/reveal tween fights the chase-cam and the ship
  // appears not to move (the "first sail does nothing" bug).
  const camTween = useRef<gsap.core.Tween | gsap.core.Timeline | null>(null);
  const killCamTweens = () => {
    camTween.current?.kill();
    camTween.current = null;
  };

  // Establishing shot on first mount.
  useEffect(() => {
    const [px, py, pz] = HOME_CAMERA.position;
    camTween.current = gsap.fromTo(
      camera.position,
      { x: 0, y: 10, z: 220 },
      {
        x: px,
        y: py,
        z: pz,
        duration: 2.4,
        ease: "power2.inOut",
        onUpdate: () => controls.current?.update(),
      }
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Whenever a voyage starts sailing, cancel any camera tween so the per-frame
  // chase-cam has sole control. This is the key fix for the tween/chase fight.
  useEffect(() => {
    let prev = useVoyage.getState().phase;
    return useVoyage.subscribe((s) => {
      if (prev !== "sailing" && s.phase === "sailing") killCamTweens();
      prev = s.phase;
    });
  }, []);

  // On arrival (voyage settles), ease the camera to the dock's reveal framing.
  useEffect(() => {
    const dock = dockForIndex(activeIndex);
    const framing = activeIndex === null ? HOME_CAMERA : dock.camera;
    const [px, py, pz] = framing.position;
    const [lx, ly, lz] = framing.lookAt;

    // Wait until the ship has (roughly) arrived before flying the reveal, so
    // the chase-cam hands off smoothly.
    let tl: gsap.core.Timeline | null = null;
    const revealNow = () => {
      killCamTweens();
      tl = gsap.timeline();
      camTween.current = tl;
      tl.to(
        camera.position,
        {
          x: px,
          y: py,
          z: pz,
          duration: 1.2,
          ease: "power3.out",
          onUpdate: () => controls.current?.update(),
        },
        0
      );
      if (controls.current) {
        tl.to(
          controls.current.target,
          {
            x: lx,
            y: ly,
            z: lz,
            duration: 1.2,
            ease: "power3.out",
            onUpdate: () => controls.current?.update(),
          },
          0
        );
      }
    };

    // Reveal when the voyage settles to "docked". If we're already docked
    // (intro, or no sailing needed), reveal immediately; otherwise wait for the
    // voyage to finish so the chase-cam hands off smoothly.
    if (useVoyage.getState().phase === "docked") {
      revealNow();
    } else {
      let prevPhase = useVoyage.getState().phase;
      const unsub = useVoyage.subscribe((s) => {
        if (prevPhase !== "docked" && s.phase === "docked") {
          revealNow();
          unsub();
        }
        prevPhase = s.phase;
      });
      return () => {
        unsub();
        tl?.kill();
      };
    }

    return () => {
      tl?.kill();
    };
  }, [activeIndex, camera]);

  // Per-frame chase-cam while sailing. During sailing this is the SOLE camera
  // authority (auto-rotate is off, no reveal tween runs until docked), so
  // there's no gsap/lerp fight.
  useFrame(() => {
    const v = useVoyage.getState();
    if (v.phase !== "sailing" || !controls.current) return;

    const { x, y: z } = v.shipPos; // Vector2: (x, z)
    const heading = v.shipHeading;

    // Cinematic wide chase: sit behind the ship and pull WAY back + up so the
    // vessel reads small against the open ocean. Ease the pull-back in over the
    // first part of the voyage so it feels like the camera sweeps outward.
    const zoom = Math.min(1, v.progress / 0.35); // 0→1 over first 35% of the leg
    const back = 90 + zoom * 130; // 90 → 220 units behind
    const height = 45 + zoom * 85; // 45 → 130 units up
    // Ship model's forward axis is 90° off from the heading, so the "behind"
    // offset is rotated a quarter turn to sit at the actual stern.
    const camAngle = heading + Math.PI / 2;
    const camX = x - Math.sin(camAngle) * back;
    const camZ = z - Math.cos(camAngle) * back;

    // Aim at the ship (a touch above the deck), stern toward camera.
    desiredPos.current.set(camX, height, camZ);
    desiredTarget.current.set(x, 9, z);

    // Smooth follow (lerp) so it glides rather than snapping.
    camera.position.lerp(desiredPos.current, 0.06);
    controls.current.target.lerp(desiredTarget.current, 0.1);
    controls.current.update();
  });

  return (
    <OrbitControls
      ref={controls}
      enableZoom
      enablePan={false}
      minDistance={15}
      maxDistance={320}
      maxPolarAngle={Math.PI / 2.05}
      // Free look only: no auto-rotate while sailing or parked at a stop.
      autoRotate={activeIndex === null}
      autoRotateSpeed={0.25}
      enableDamping
      dampingFactor={0.06}
    />
  );
}
