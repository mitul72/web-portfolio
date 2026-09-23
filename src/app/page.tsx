"use client";

import { Canvas } from "@react-three/fiber";
import { PerformanceMonitor } from "@react-three/drei";
import { Suspense, useState } from "react";
import { AgXToneMapping, NoToneMapping } from "three";
import World from "@/components/models/world";
import Ship from "@/components/models/ship";
import Npcs from "@/components/models/npcs";
import TreasureChest from "@/components/models/treasure-chest";
import NpcDialogue from "@/components/ui/NpcDialogue";
import CameraRig from "@/components/tour/CameraRig";
import DevCoords from "@/components/tour/DevCoords";
import Ocean from "@/components/env/Ocean";
import Atmosphere from "@/components/env/Atmosphere";
import Lighting from "@/components/env/Lighting";
import Seagulls from "@/components/env/Seagulls";
import Wake from "@/components/env/Wake";
import SailingSfx from "@/components/env/SailingSfx";
import Effects from "@/components/env/Effects";
import BackgroundMusic from "@/components/music";
import Navbar from "@/components/shared/navbar";
import ContentPanel from "@/components/ui/ContentPanel";
import TourControls from "@/components/ui/TourControls";
import { useIsMobile } from "@/components/env/useIsMobile";
import LoadingScreen from "@/components/ui/LoadingScreen";
import IntroTitle from "@/components/ui/IntroTitle";
import { HOME_CAMERA } from "@/data/portfolio";

// Flip to true while placing new assets/markers — logs world coords to the
// console when you click the scene (press "c" for camera). Turn off to ship.
const SHOW_DEV_COORDS = false;

export default function Home() {
  const isMobile = useIsMobile();
  // Desktop dpr adapts to measured fps (PerformanceMonitor below): full crisp
  // when the GPU keeps up, stepped down when it can't — integrated GPUs get a
  // smooth scene instead of a slideshow, fast machines keep the full look.
  const [dprMax, setDprMax] = useState(2);

  return (
    <main className="relative h-[100dvh] w-full overflow-hidden bg-slate-950">
      <Canvas
        className="h-[100dvh] w-full"
        // Mobile: no shadows, cap pixel ratio — big battery/FPS wins.
        shadows={!isMobile}
        dpr={isMobile ? [1, 1.5] : [1, dprMax]}
        // Canvas MSAA is OFF: on desktop the EffectComposer already renders
        // into its own multisampled buffer (double AA = pure waste), and
        // mobile never had it. powerPreference "default" on mobile is kinder
        // to battery/thermals.
        gl={{
          antialias: false,
          powerPreference: isMobile ? "default" : "high-performance",
          // Desktop: the composer's AgX pass owns the HDR -> display curve
          // (after fog and bloom, as Blender does), so the renderer must not
          // tone map as well. Mobile has no composer and uses the renderer's.
          toneMapping: isMobile ? AgXToneMapping : NoToneMapping,
          toneMappingExposure: 1,
        }}
        camera={{
          position: HOME_CAMERA.position,
          // ~ the approved renders' 30 mm lens; the old 75 deg default
          // flattened everything.
          fov: 48,
          near: 0.5,
          far: 4000,
        }}
      >
        {/* Gentle steps: 1.5 is the "still crisp" floor (same as the mobile
            cap); 1.25 only as the last-resort fallback. Dropping to 1 read as
            visible blur whenever the monitor flipped down. */}
        <PerformanceMonitor
          flipflops={3}
          onDecline={() => setDprMax(1.5)}
          onIncline={() => setDprMax(2)}
          onFallback={() => setDprMax(1.25)}
        />
        <Suspense fallback={null}>
          {/* Environment */}
          <Atmosphere />
          <Lighting shadows={!isMobile} />
          <Ocean />
          <Seagulls />
          <Wake />

          {/* Content */}
          <World />
          <Ship />
          <Npcs />
          <TreasureChest />


          {/* Camera + post */}
          <CameraRig />
          {/* Postprocessing (bloom + AgX grade) is desktop-only for perf. */}
          {!isMobile && <Effects />}
          {SHOW_DEV_COORDS && <DevCoords />}
        </Suspense>
      </Canvas>

      {/* DOM overlays (outside the Canvas). */}
      <Navbar />
      <LoadingScreen />
      <IntroTitle />
      <TourControls />
      <ContentPanel />
      <NpcDialogue />
      <BackgroundMusic />
      <SailingSfx />
    </main>
  );
}
