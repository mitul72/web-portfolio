"use client";

import { Canvas } from "@react-three/fiber";
import { Suspense } from "react";
import PirateIsland from "@/components/models/pirate-island";
import VolcanoIsland from "@/components/models/volcano-island";
import TreasureIsland from "@/components/models/treasure-island";
import FantasyIsland from "@/components/models/fantasy-island";
import LowPolyIsland from "@/components/models/low-poly-island";
import Toothless from "@/components/models/toothless";
import CameraRig from "@/components/tour/CameraRig";
import DevCoords from "@/components/tour/DevCoords";
import SubPois from "@/components/tour/SubPois";
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
import SubNav from "@/components/ui/SubNav";
import { useIsMobile } from "@/components/env/useIsMobile";
import LoadingScreen from "@/components/ui/LoadingScreen";
import IntroTitle from "@/components/ui/IntroTitle";
import {
  HOME_CAMERA,
  VOLCANO_TRANSFORM,
  TREASURE_TRANSFORM,
  FANTASY_TRANSFORM,
  SOCIALS_TRANSFORM,
  TOOTHLESS_TRANSFORM,
} from "@/data/portfolio";

// Flip to true while placing new assets/markers — logs world coords to the
// console when you click the scene (press "c" for camera). Turn off to ship.
const SHOW_DEV_COORDS = true;

export default function Home() {
  const isMobile = useIsMobile();

  return (
    <main className="relative h-[100dvh] w-full overflow-hidden bg-slate-950">
      <Canvas
        className="h-[100dvh] w-full"
        // Mobile: no shadows, cap pixel ratio, skip MSAA — big battery/FPS wins.
        shadows={!isMobile}
        dpr={isMobile ? [1, 1.5] : [1, 2]}
        gl={{ antialias: !isMobile, powerPreference: "high-performance" }}
        camera={{
          position: HOME_CAMERA.position,
          near: 0.1,
          far: 4000,
        }}
      >
        <Suspense fallback={null}>
          {/* Environment */}
          <Atmosphere />
          <Lighting />
          <Ocean />
          <Seagulls />
          <Wake />

          {/* Content */}
          <PirateIsland />
          <VolcanoIsland
            position={VOLCANO_TRANSFORM.position}
            scale={VOLCANO_TRANSFORM.scale}
            rotation={VOLCANO_TRANSFORM.rotation}
          />
          <TreasureIsland
            position={TREASURE_TRANSFORM.position}
            scale={TREASURE_TRANSFORM.scale}
            rotation={TREASURE_TRANSFORM.rotation}
          />
          <FantasyIsland
            position={FANTASY_TRANSFORM.position}
            scale={FANTASY_TRANSFORM.scale}
            rotation={FANTASY_TRANSFORM.rotation}
          />
          <LowPolyIsland
            position={SOCIALS_TRANSFORM.position}
            scale={SOCIALS_TRANSFORM.scale}
            rotation={SOCIALS_TRANSFORM.rotation}
          />
          <Toothless
            position={TOOTHLESS_TRANSFORM.position}
            scale={TOOTHLESS_TRANSFORM.scale}
            rotation={TOOTHLESS_TRANSFORM.rotation}
          />

          {/* Per-island sub-POIs (project bottles), shown on arrival. */}
          <SubPois />

          {/* Camera + post */}
          <CameraRig />
          {/* Postprocessing (bloom/vignette) is skipped on mobile for perf. */}
          {!isMobile && <Effects />}
          {SHOW_DEV_COORDS && <DevCoords />}
        </Suspense>
      </Canvas>

      {/* DOM overlays (outside the Canvas). */}
      <Navbar />
      <LoadingScreen />
      <IntroTitle />
      <TourControls />
      <SubNav />
      <ContentPanel />
      <BackgroundMusic />
      <SailingSfx />
    </main>
  );
}
