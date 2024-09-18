"use client";
// import PokeTown from "@/components/models/pokemon-town";
import { Canvas } from "@react-three/fiber";
import { Suspense, useEffect, useState } from "react";
import { OrbitControls } from "@react-three/drei";
import PirateIsland from "@/components/models/pirate-island";
// s
export default function Home() {
  const [screenScale, setScreenScale] = useState([1, 1, 1]);
  const [screenPosition, setScreenPosition] = useState([0, -6.5, -43]);
  const [rotation, setRotation] = useState([0.1, 4.7, 0]);
  // const CameraTracker = () => {
  //   const { camera } = useThree(); // Get access to the camera object

  //   useFrame(() => {
  //     const { x, y, z } = camera.position;
  //     console.log(
  //       "Camera position: ",
  //       x.toFixed(2),
  //       y.toFixed(2),
  //       z.toFixed(2)
  //     );
  //     console.log("Camera rotation: ", camera.rotation);
  //     // setCameraPosition([x.toFixed(2), y.toFixed(2), z.toFixed(2)]); // Update the camera position state
  //   });

  //   return null;
  // };

  // Run the window-related code inside useEffect to ensure it runs on the client side
  useEffect(() => {
    const adjustTownForScreen = () => {
      let screenScale;
      const screenPosition = [0, -6.5, -43];
      const rotation = [0.1, 4.7, 0];

      if (window.innerWidth < 768) {
        screenScale = [0.9, 0.9, 0.9];
      } else {
        screenScale = [1, 1, 1];
      }
      return { screenScale, screenPosition, rotation };
    };

    const { screenScale, screenPosition, rotation } = adjustTownForScreen();
    setScreenScale(screenScale);
    setScreenPosition(screenPosition);
    setRotation(rotation);

    // Optional: Add an event listener to update on window resize
    const handleResize = () => {
      const { screenScale, screenPosition, rotation } = adjustTownForScreen();
      setScreenScale(screenScale);
      setScreenPosition(screenPosition);
      setRotation(rotation);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);
  return (
    <section className="w-full h-screen relative">
      <Canvas
        className="w-full h-screen bg-transparent"
        camera={{
          position: [23.08, 30.52, 150.63], // Default camera position
          rotation: [-0.199, 0.149, 0.03],
          near: 0.1,
          far: 1000,
        }}
      >
        <Suspense fallback={null}>
          <directionalLight
            intensity={2.5}
            scale={30}
            position={[0, 240, 200]}
          />

          <hemisphereLight intensity={0.4} />
          <ambientLight intensity={0.3} />
          {/* <PokeTown
            position={screenPosition}
            scale={screenScale}
            rotation={rotation}
          /> */}
          <PirateIsland
            position={screenPosition}
            scale={screenScale}
            rotation={rotation}
          />
          {/* <CameraTracker /> */}
        </Suspense>
        <OrbitControls enableZoom={true} />
      </Canvas>
    </section>
  );
}
