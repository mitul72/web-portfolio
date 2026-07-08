import { useMemo, useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Billboard, Html, useGLTF } from "@react-three/drei";
import { DoubleSide, Group, Mesh, MeshBasicMaterial, Shape } from "three";
import { SkeletonUtils } from "three-stdlib";
import BottleGLB from "@/assets/bottle-with-scroll-transformed.glb";
import { SubPoi } from "@/data/portfolio";
import { waveHeight } from "@/components/env/waves";
import { useTour } from "./useTour";

const GLOW = "#7ad7f0";
const CRATE_GLOW = "#ffb765"; // warm amber for cargo crates
const FLAG_FALLBACK = "#ffd166"; // pennant/wisp color when the poi sets none
// How far a wisp floats above the landmark it marks.
const WISP_HOVER = 3;

/** Pole height (world units) for a flag with `stack` tenure steps. */
function flagPoleHeight(stack: number) {
  return 3.5 + stack * 0.9;
}

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

/** One wooden crate: a box with darker edge "frame" slats. */
function Crate({ y, jitter }: { y: number; jitter: number }) {
  return (
    <group position={[Math.cos(jitter) * 0.05, y, Math.sin(jitter) * 0.05]} rotation={[0, jitter * 0.3, 0]}>
      <mesh castShadow>
        <boxGeometry args={[0.95, 0.9, 0.95]} />
        <meshStandardMaterial color="#a9743e" roughness={0.85} />
      </mesh>
      {/* Corner/edge frame slats (slightly larger, darker wireframe-ish look). */}
      <mesh>
        <boxGeometry args={[1.0, 0.16, 1.0]} />
        <meshStandardMaterial color="#6f4a24" roughness={0.9} />
      </mesh>
      <mesh position={[0, 0.42, 0]}>
        <boxGeometry args={[1.0, 0.12, 1.0]} />
        <meshStandardMaterial color="#6f4a24" roughness={0.9} />
      </mesh>
      <mesh position={[0, -0.42, 0]}>
        <boxGeometry args={[1.0, 0.12, 1.0]} />
        <meshStandardMaterial color="#6f4a24" roughness={0.9} />
      </mesh>
    </group>
  );
}

/**
 * A stack of cargo crates (procedural, no assets). Height encodes role weight /
 * tenure. When `lit`, an amber glow disc sits behind it. The company name is
 * shown on the label above (rendered by the marker).
 */
function CrateStack({ count, lit }: { count: number; lit: boolean }) {
  // Deterministic little rotations so the stack looks hand-placed, not rigid.
  const jitters = useMemo(
    () => Array.from({ length: count }, (_, i) => Math.sin(i * 12.9898) * 6.5 % 1),
    [count]
  );
  return (
    <group>
      {jitters.map((j, i) => (
        <Crate key={i} y={i * 0.92} jitter={j} />
      ))}
      {/* Warm glow halo behind the stack when hovered/active. */}
      <Billboard position={[0, count * 0.4, -0.4]}>
        <mesh>
          <circleGeometry args={[count * 0.6 + 1, 24]} />
          <meshBasicMaterial
            color={CRATE_GLOW}
            transparent
            opacity={lit ? 0.28 : 0.12}
            toneMapped={false}
            depthWrite={false}
          />
        </mesh>
      </Billboard>
    </group>
  );
}

/**
 * A planted expedition flag — pole + fluttering triangular pennant. Career
 * milestones read as "lands charted": pole height encodes tenure (`stack`),
 * pennant color is per-company (poi.color). The pennant waves in the wind,
 * faster and brighter when hovered/active.
 */
function Flag({
  color,
  poleHeight,
  phase,
  lit,
}: {
  color: string;
  poleHeight: number;
  phase: number;
  lit: boolean;
}) {
  const pennant = useRef<Group>(null);

  // Swallowtail pennant silhouette, hinged at the pole (x=0).
  const shape = useMemo(() => {
    const s = new Shape();
    s.moveTo(0, 0);
    s.lineTo(2.1, 0.18);
    s.lineTo(1.55, 0.42); // swallowtail notch
    s.lineTo(2.1, 0.66);
    s.lineTo(0, 0.84);
    s.closePath();
    return s;
  }, []);

  useFrame((state) => {
    if (!pennant.current) return;
    const t = state.clock.elapsedTime;
    const amp = lit ? 0.38 : 0.22;
    // Flutter: swing around the pole + a small ripple twist.
    pennant.current.rotation.y = Math.sin(t * 2.3 + phase) * amp;
    pennant.current.rotation.z = Math.sin(t * 4.1 + phase * 2) * 0.06;
  });

  return (
    <group>
      {/* Pole — runs 3 units below ground so uneven terrain never shows a gap. */}
      <mesh position={[0, (poleHeight - 3) / 2, 0]} castShadow>
        <cylinderGeometry args={[0.07, 0.1, poleHeight + 3, 6]} />
        <meshStandardMaterial color="#6f4a24" roughness={0.9} />
      </mesh>
      {/* Gold finial cap. */}
      <mesh position={[0, poleHeight + 0.14, 0]}>
        <sphereGeometry args={[0.17, 10, 10]} />
        <meshStandardMaterial
          color="#ffd166"
          emissive="#ffd166"
          emissiveIntensity={lit ? 1.4 : 0.6}
          toneMapped={false}
        />
      </mesh>
      {/* Fluttering pennant, hinged just below the finial. */}
      <group ref={pennant} position={[0, poleHeight - 0.98, 0]}>
        <mesh castShadow>
          <shapeGeometry args={[shape]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={lit ? 0.7 : 0.25}
            side={DoubleSide}
            toneMapped={false}
          />
        </mesh>
      </group>
      {/* Soft glow halo behind the pennant when hovered/active. */}
      <Billboard position={[0, poleHeight * 0.8, -0.4]}>
        <mesh>
          <circleGeometry args={[2.1, 24]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={lit ? 0.28 : 0.1}
            toneMapped={false}
            depthWrite={false}
          />
        </mesh>
      </Billboard>
    </group>
  );
}

/**
 * A will-o'-wisp — a glowing orb that hovers over an EXISTING landmark (a
 * tree, a rock, the summit) and marks it as a point of interest without
 * planting new geometry into it. Pulses gently with two orbiting sparks;
 * brighter, bigger, and faster when hovered/active.
 */
function Wisp({
  color,
  phase,
  lit,
}: {
  color: string;
  phase: number;
  lit: boolean;
}) {
  const shell = useRef<Mesh>(null);
  const halo = useRef<Mesh>(null);
  const sparks = useRef<Group>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    const pulse = 1 + Math.sin(t * 2.6 + phase) * 0.12;
    if (shell.current) shell.current.scale.setScalar(pulse * (lit ? 1.3 : 1));
    if (halo.current) {
      (halo.current.material as MeshBasicMaterial).opacity =
        (lit ? 0.34 : 0.16) * (0.8 + Math.sin(t * 2.6 + phase) * 0.2);
    }
    if (sparks.current)
      sparks.current.rotation.y = t * (lit ? 2.4 : 1.2) + phase;
  });

  return (
    <group>
      {/* Bright core… */}
      <mesh>
        <sphereGeometry args={[0.32, 16, 16]} />
        <meshBasicMaterial color="#ffffff" toneMapped={false} />
      </mesh>
      {/* …inside a translucent colored shell that breathes. */}
      <mesh ref={shell}>
        <sphereGeometry args={[0.75, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.45}
          toneMapped={false}
          depthWrite={false}
        />
      </mesh>
      {/* Two little sparks circling the orb. */}
      <group ref={sparks}>
        <mesh position={[1.3, 0.2, 0]}>
          <octahedronGeometry args={[0.14, 0]} />
          <meshBasicMaterial color={color} toneMapped={false} />
        </mesh>
        <mesh position={[-1.15, -0.25, 0.4]}>
          <octahedronGeometry args={[0.11, 0]} />
          <meshBasicMaterial color={color} toneMapped={false} />
        </mesh>
      </group>
      {/* Soft halo. */}
      <Billboard>
        <mesh ref={halo} position={[0, 0, -0.3]}>
          <circleGeometry args={[2.2, 24]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.16}
            toneMapped={false}
            depthWrite={false}
          />
        </mesh>
      </Billboard>
      {/* Generous invisible hit target so the small orb is easy to click/tap. */}
      <mesh>
        <sphereGeometry args={[2.4, 8, 8]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
    </group>
  );
}

/**
 * A message-in-a-bottle (real GLB) — the socials/contact prop. The model is
 * ~3.1 units tall with its origin at the middle, so it's lifted by half its
 * height to stand on the terrain. No halo — a glow disc reads as fog behind a
 * realistic glass model; the hover scale-up + label are the affordance.
 */
function Bottle() {
  const { scene } = useGLTF(BottleGLB);
  const clone = useMemo(() => SkeletonUtils.clone(scene), [scene]);

  return (
    <group>
      {/* Stand on the ground: origin is mid-bottle (bbox Y −1.5…1.63). */}
      <primitive object={clone} position={[0, 1.5, 0]} />
      {/* Generous invisible hit target. */}
      <mesh position={[0, 1.6, 0]}>
        <sphereGeometry args={[2.2, 8, 8]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
    </group>
  );
}

useGLTF.preload(BottleGLB);

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
  const isCrate = poi.prop === "crate";
  const isFlag = poi.prop === "flag";
  const isWisp = poi.prop === "wisp";
  const isBottle = poi.prop === "bottle";
  // Deterministic per-poi animation phase so flags/wisps don't move in lockstep.
  const windPhase = useMemo(
    () => (poi.position[0] * 7.13 + poi.position[2] * 3.71) % (Math.PI * 2),
    [poi.position]
  );

  useFrame((state) => {
    if (!grp.current) return;
    const t = state.clock.elapsedTime;
    const [px, , pz] = poi.position;

    if (isWisp) {
      // Hover above the landmark it marks, drifting gently.
      grp.current.position.y =
        poi.position[1] + WISP_HOVER + Math.sin(t * 1.1 + windPhase) * 0.5;
      grp.current.rotation.y = 0;
      const s = 1 + (poi.stack ?? 2) * 0.12; // tenure → slightly bigger orb
      grp.current.scale.setScalar(s * (lit ? 1.15 : 1));
    } else if (isBottle) {
      // Rides the waves if bob is set; otherwise grounded where placed.
      const base = poi.bob
        ? waveHeight(px, pz, t) * 0.35 + poi.position[1]
        : poi.position[1];
      grp.current.position.y = base;
      grp.current.rotation.y = 0;
      // Resting lean + a slow tipsy sway, like it lodged on the rocks.
      grp.current.rotation.z = 0.12 + Math.sin(t * 0.8 + windPhase) * 0.04;
      grp.current.scale.setScalar((lit ? 1.1 : 1) * 1.8);
    } else if (isFlag) {
      // Planted in the ground: no bob/spin. A whisper of hover feedback.
      grp.current.position.y = poi.position[1];
      grp.current.rotation.y = 0;
      grp.current.scale.setScalar(lit ? 1.05 : 1);
    } else if (isCrate) {
      // Cargo crates sit still; bob on the water only if flagged. The active
      // stack lifts slightly, like it's being craned up to inspect.
      const base = poi.bob ? waveHeight(px, pz, t) * 0.35 + poi.position[1] : poi.position[1];
      grp.current.position.y = base + (active ? 1.2 : 0) + (hovered ? 0.4 : 0);
      grp.current.rotation.y = 0;
      grp.current.scale.setScalar(1);
    } else {
      // Gems: float, spin, and scale up.
      grp.current.position.y = poi.position[1] + Math.sin(t * 1.4) * 0.3;
      grp.current.rotation.y = t * 0.4;
      const s = (active ? 1.25 : 1) * (hovered ? 1.15 : 1);
      grp.current.scale.setScalar(s * 2);
    }
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
        {isBottle ? (
          <Bottle />
        ) : isWisp ? (
          <Wisp color={poi.color ?? FLAG_FALLBACK} phase={windPhase} lit={lit} />
        ) : isFlag ? (
          <Flag
            color={poi.color ?? FLAG_FALLBACK}
            poleHeight={flagPoleHeight(poi.stack ?? 2)}
            phase={windPhase}
            lit={lit}
          />
        ) : isCrate ? (
          <CrateStack count={poi.stack ?? 2} lit={lit} />
        ) : (
          <>
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
          </>
        )}
      </group>

      {/* Fixed-size label above the prop (clears tall poles/stacks). An empty
          label means "no pill" — the prop itself is the invitation. */}
      {poi.label && (
      <Html
        center
        position={[
          poi.position[0],
          poi.position[1] +
            (isWisp
              ? WISP_HOVER + 3
              : isBottle
                ? 7 // clears the ~5.6-unit bottle at its 1.8 scale
                : isFlag
                  ? flagPoleHeight(poi.stack ?? 2) + 1.4
                  : isCrate
                    ? (poi.stack ?? 2) * 0.95 + 1.2
                    : 3),
          poi.position[2],
        ]}
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
            boxShadow: `0 0 12px ${
              poi.color ?? (isCrate ? CRATE_GLOW : GLOW)
            }, 0 2px 8px rgba(0,0,0,0.6)`,
            textShadow: "0 1px 3px rgba(0,0,0,0.9)",
          }}
        >
          {poi.label}
        </button>
      </Html>
      )}
    </group>
  );
}
