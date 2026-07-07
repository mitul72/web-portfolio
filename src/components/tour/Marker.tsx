import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Billboard, Html } from "@react-three/drei";
import { Group, Mesh } from "three";
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
 * A floating beacon "map pin" point of interest: a glowing teardrop with a soft
 * halo behind it and a pulsing ring below, plus a crisp fixed-size label. Click
 * (marker or label) to sail/fly to the stop and open its panel.
 */
export default function Marker({
  stop,
  index,
}: {
  stop: TourStop;
  index: number;
}) {
  const pin = useRef<Group>(null);
  const ring = useRef<Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const goTo = useTour((s) => s.goTo);
  const activeIndex = useTour((s) => s.activeIndex);
  const isActive = activeIndex === index;
  const color = KIND_COLOR[stop.kind];
  const lit = hovered || isActive;

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    // Bob the whole pin.
    if (pin.current) {
      pin.current.position.y = 2 + Math.sin(t * 1.6 + index) * 0.35;
      const s = (isActive ? 1.2 : 1) * (hovered ? 1.15 : 1);
      pin.current.scale.setScalar(s);
    }
    // Expanding/fading pulse ring on the ground.
    if (ring.current) {
      const k = (t * 0.6 + index * 0.5) % 1; // 0..1 loop
      ring.current.scale.setScalar(2 + k * 5);
      const mat = ring.current.material as any;
      mat.opacity = (1 - k) * 0.5;
    }
  });

  const activate = (e: any) => {
    e.stopPropagation?.();
    goTo(index);
  };
  const over = (e?: any) => {
    e?.stopPropagation?.();
    setHovered(true);
    document.body.style.cursor = "pointer";
  };
  const out = () => {
    setHovered(false);
    document.body.style.cursor = "auto";
  };

  return (
    <group position={stop.position}>
      {/* Pulsing ground ring (flat, expands outward). */}
      <mesh ref={ring} rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.5, 0]}>
        <ringGeometry args={[0.7, 1, 40]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.4}
          toneMapped={false}
          depthWrite={false}
        />
      </mesh>

      {/* The floating beacon pin. */}
      <group ref={pin}>
        {/* Soft glow halo behind the pin (billboarded, additive-ish). */}
        <Billboard>
          <mesh position={[0, 0, -0.2]}>
            <circleGeometry args={[2.6, 32]} />
            <meshBasicMaterial
              color={color}
              transparent
              opacity={lit ? 0.35 : 0.2}
              toneMapped={false}
              depthWrite={false}
            />
          </mesh>
        </Billboard>

        {/* Teardrop: a sphere head + a cone tip pointing down. */}
        <group
          onClick={activate}
          onPointerOver={over}
          onPointerOut={out}
        >
          <mesh position={[0, 0.55, 0]}>
            <sphereGeometry args={[1, 24, 24]} />
            <meshStandardMaterial
              color={color}
              emissive={color}
              emissiveIntensity={lit ? 2.2 : 1.3}
              toneMapped={false}
            />
          </mesh>
          <mesh position={[0, -0.75, 0]} rotation={[Math.PI, 0, 0]}>
            <coneGeometry args={[0.85, 1.6, 24]} />
            <meshStandardMaterial
              color={color}
              emissive={color}
              emissiveIntensity={lit ? 2.2 : 1.3}
              toneMapped={false}
            />
          </mesh>
          {/* Bright inner dot for a focused core. */}
          <mesh position={[0, 0.55, 0.85]}>
            <circleGeometry args={[0.32, 20]} />
            <meshBasicMaterial color="#ffffff" toneMapped={false} />
          </mesh>
        </group>
      </group>

      {/* Crisp, fixed-size label — does NOT shrink with distance. */}
      <Html
        center
        position={[0, 5.2, 0]}
        // Below the DOM overlays (panel/nav are z-20+) so labels never paint
        // over — or steal taps from — the panel and nav bars.
        zIndexRange={[10, 0]}
        style={{ pointerEvents: "auto" }}
      >
        <button
          onClick={activate}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
          className={`whitespace-nowrap select-none rounded-full border px-4 py-1.5 text-sm font-semibold text-white shadow-lg backdrop-blur transition-transform hover:scale-105 ${
            lit ? "scale-105 border-white/60" : "border-white/25"
          }`}
          style={{
            background: "rgba(10, 15, 25, 0.82)",
            boxShadow: `0 0 16px ${color}, 0 2px 8px rgba(0,0,0,0.6)`,
            textShadow: "0 1px 3px rgba(0,0,0,0.9)",
          }}
        >
          {stop.label}
        </button>
      </Html>
    </group>
  );
}
