import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Group, CatmullRomCurve3, Vector3 } from "three";

/**
 * A small flock of low-poly seagulls flying looping paths above the island.
 * Each gull is a simple V of two triangles whose "wings" flap. Cheap, but adds
 * a lot of life to an otherwise static sky.
 */
function Gull({ offset, radius, height, speed }: {
  offset: number;
  radius: number;
  height: number;
  speed: number;
}) {
  const group = useRef<Group>(null);
  const left = useRef<Group>(null);
  const right = useRef<Group>(null);
  // Scratch vectors reused each frame (getPointAt allocates otherwise).
  const pos = useRef(new Vector3());
  const ahead = useRef(new Vector3());

  const path = useMemo(
    () =>
      new CatmullRomCurve3(
        [
          new Vector3(radius, height, 0),
          new Vector3(0, height + 8, radius),
          new Vector3(-radius, height, 0),
          new Vector3(0, height - 6, -radius),
        ],
        true,
        "catmullrom",
        0.5
      ),
    [radius, height]
  );

  useFrame((state) => {
    const t = ((state.clock.elapsedTime * speed + offset) % 1 + 1) % 1;
    path.getPointAt(t, pos.current);
    path.getPointAt((t + 0.01) % 1, ahead.current);
    if (group.current) {
      group.current.position.copy(pos.current);
      group.current.lookAt(ahead.current);
    }
    // Flap.
    const flap = Math.sin(state.clock.elapsedTime * 10 + offset * 20) * 0.6;
    if (left.current) left.current.rotation.z = flap;
    if (right.current) right.current.rotation.z = -flap;
  });

  return (
    <group ref={group}>
      <group ref={left}>
        <mesh position={[-0.6, 0, 0]}>
          <planeGeometry args={[1.2, 0.35]} />
          <meshStandardMaterial color="#f4f4f4" side={2} />
        </mesh>
      </group>
      <group ref={right}>
        <mesh position={[0.6, 0, 0]}>
          <planeGeometry args={[1.2, 0.35]} />
          <meshStandardMaterial color="#e8e8e8" side={2} />
        </mesh>
      </group>
    </group>
  );
}

export default function Seagulls() {
  const gulls = useMemo(
    () => [
      { offset: 0.0, radius: 90, height: 70, speed: 0.03 },
      { offset: 0.3, radius: 110, height: 82, speed: 0.025 },
      { offset: 0.6, radius: 75, height: 64, speed: 0.035 },
      { offset: 0.85, radius: 130, height: 90, speed: 0.02 },
    ],
    []
  );
  return (
    <>
      {gulls.map((g, i) => (
        <Gull key={i} {...g} />
      ))}
    </>
  );
}
