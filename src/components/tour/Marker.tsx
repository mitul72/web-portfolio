import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Billboard, Html } from "@react-three/drei";
import { Mesh } from "three";
import { TourStop } from "@/data/portfolio";
import { useTour } from "./useTour";

const KIND_COLOR: Record<TourStop["kind"], string> = {
  intro: "#ffd166",
  resume: "#ffb703",
  project: "#4cc9f0",
  experience: "#90be6d",
  contact: "#f72585",
};

/**
 * A floating, pulsing, clickable point of interest. Clicking (or activating the
 * label) selects the stop, which flies the camera and opens the content panel.
 */
export default function Marker({
  stop,
  index,
}: {
  stop: TourStop;
  index: number;
}) {
  const ref = useRef<Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const goTo = useTour((s) => s.goTo);
  const activeIndex = useTour((s) => s.activeIndex);
  const isActive = activeIndex === index;
  const color = KIND_COLOR[stop.kind];

  // Gentle bob + pulse so markers read as interactive.
  useFrame((state) => {
    if (!ref.current) return;
    const t = state.clock.elapsedTime;
    ref.current.position.y = Math.sin(t * 1.5 + index) * 0.4;
    const s = (isActive ? 1.25 : 1) * (hovered ? 1.2 : 1);
    ref.current.scale.setScalar(s + Math.sin(t * 3 + index) * 0.06);
  });

  return (
    <group position={stop.position}>
      <Billboard>
        <mesh
          ref={ref}
          onClick={(e) => {
            e.stopPropagation();
            goTo(index);
          }}
          onPointerOver={(e) => {
            e.stopPropagation();
            setHovered(true);
            document.body.style.cursor = "pointer";
          }}
          onPointerOut={() => {
            setHovered(false);
            document.body.style.cursor = "auto";
          }}
        >
          <sphereGeometry args={[1.1, 24, 24]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={hovered || isActive ? 1.6 : 0.9}
            toneMapped={false}
          />
        </mesh>
      </Billboard>

      <Html center distanceFactor={40} position={[0, 3, 0]}>
        <button
          onClick={(e) => {
            e.stopPropagation();
            goTo(index);
          }}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
          className="whitespace-nowrap select-none rounded-full border border-white/30 bg-black/60 px-3 py-1 text-xs font-medium text-white backdrop-blur transition-transform hover:scale-105"
          style={{ boxShadow: `0 0 12px ${color}` }}
        >
          {stop.label}
        </button>
      </Html>
    </group>
  );
}
