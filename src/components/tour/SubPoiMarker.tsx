import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Billboard, Html } from "@react-three/drei";
import { Group } from "three";
import { SubPoi } from "@/data/portfolio";
import { useTour } from "./useTour";

const GLOW = "#7ad7f0";

/**
 * A faceted low-poly gem (procedural, no assets): two cones joined base-to-base
 * make a diamond/octahedron-ish crystal. Emissive so it glows, flat-shaded so
 * the facets catch light. `flatShading` gives the crisp low-poly facets.
 */
function Gem({ lit }: { lit: boolean }) {
  const gem = "#43d6f0";
  const mat = (
    <meshStandardMaterial
      color={gem}
      emissive={GLOW}
      emissiveIntensity={lit ? 1.6 : 0.9}
      metalness={0.3}
      roughness={0.15}
      flatShading
      toneMapped={false}
    />
  );
  return (
    <group>
      {/* Upper crown (short, wide cone pointing up). */}
      <mesh position={[0, 0.42, 0]}>
        <coneGeometry args={[0.62, 0.55, 6]} />
        {mat}
      </mesh>
      {/* Lower pavilion (longer cone pointing down). */}
      <mesh position={[0, -0.35, 0]} rotation={[Math.PI, 0, 0]}>
        <coneGeometry args={[0.62, 0.95, 6]} />
        {mat}
      </mesh>
      {/* Bright inner core for extra sparkle. */}
      <mesh>
        <octahedronGeometry args={[0.28, 0]} />
        <meshBasicMaterial color="#eafcff" toneMapped={false} />
      </mesh>
    </group>
  );
}

/**
 * A clickable sub-POI on an island — renders a glowing faceted gem. Bobs,
 * spins, and glows; clicking opens its project panel. Rendered only while its
 * island is the active stop (the parent controls that).
 */
export default function SubPoiMarker({ poi }: { poi: SubPoi }) {
  const grp = useRef<Group>(null);
  const [hovered, setHovered] = useState(false);
  const selectSubPoi = useTour((s) => s.selectSubPoi);
  const activeSubPoiId = useTour((s) => s.activeSubPoiId);
  const active = activeSubPoiId === poi.id;
  const lit = hovered || active;

  useFrame((state) => {
    if (!grp.current) return;
    const t = state.clock.elapsedTime;
    grp.current.position.y = poi.position[1] + Math.sin(t * 1.4) * 0.3;
    grp.current.rotation.y = t * 0.4; // slow spin
    const s = (active ? 1.25 : 1) * (hovered ? 1.15 : 1);
    grp.current.scale.setScalar(s * 2);
  });

  const activate = (e: any) => {
    e.stopPropagation?.();
    selectSubPoi(poi.id);
  };

  return (
    <group>
      <group
        ref={grp}
        position={poi.position}
        onClick={activate}
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
        <Gem lit={lit} />
        {/* Soft glow halo */}
        <Billboard>
          <mesh position={[0, 0.3, -0.3]}>
            <circleGeometry args={[1.6, 24]} />
            <meshBasicMaterial
              color={GLOW}
              transparent
              opacity={lit ? 0.3 : 0.16}
              toneMapped={false}
              depthWrite={false}
            />
          </mesh>
        </Billboard>
      </group>

      {/* Fixed-size label above the bottle. */}
      <Html
        center
        position={[poi.position[0], poi.position[1] + 3, poi.position[2]]}
        // Keep labels UNDER the DOM overlays (panel/nav are z-20+); drei's
        // default zIndexRange is ~16M, which paints over the content panel.
        zIndexRange={[10, 0]}
      >
        <button
          onClick={activate}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
          className={`whitespace-nowrap select-none rounded-full border px-3 py-1 text-xs font-semibold text-white shadow-lg backdrop-blur transition-transform hover:scale-105 ${
            lit ? "scale-105 border-white/60" : "border-white/25"
          }`}
          style={{
            background: "rgba(10, 15, 25, 0.82)",
            boxShadow: `0 0 12px ${GLOW}, 0 2px 8px rgba(0,0,0,0.6)`,
            textShadow: "0 1px 3px rgba(0,0,0,0.9)",
          }}
        >
          {poi.label}
        </button>
      </Html>
    </group>
  );
}
