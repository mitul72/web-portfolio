"use client";

import { Canvas } from "@react-three/fiber";
import { Suspense } from "react";
import PirateIsland from "@/components/models/pirate-island";
import VolcanoIsland from "@/components/models/volcano-island";
import TreasureIsland from "@/components/models/treasure-island";
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
import LoadingScreen from "@/components/ui/LoadingScreen";
import IntroTitle from "@/components/ui/IntroTitle";
import {
  HOME_CAMERA,
  VOLCANO_TRANSFORM,
  TREASURE_TRANSFORM,
} from "@/data/portfolio";

// Flip to true while placing new assets/markers — logs world coords to the
// console when you click the scene (press "c" for camera). Turn off to ship.
const SHOW_DEV_COORDS = false;

export default function Home() {
  return (
    <main className="relative h-screen w-full overflow-hidden bg-slate-950">
      <Canvas
        className="h-screen w-full"
        shadows
        dpr={[1, 2]}
        gl={{ antialias: true }}
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

          {/* Per-island sub-POIs (project bottles), shown on arrival. */}
          <SubPois />

          {/* Camera + post */}
          <CameraRig />
          <Effects />
          {SHOW_DEV_COORDS && <DevCoords />}
        </Suspense>
      </Canvas>

      {/* DOM overlays (outside the Canvas). */}
      <Navbar />
      <LoadingScreen />
      <IntroTitle />
      <TourControls />
      <ContentPanel />
      <BackgroundMusic />
      <SailingSfx />
    </main>
  );
}
