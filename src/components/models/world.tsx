import { useEffect, useMemo } from "react";
import { ThreeEvent, useFrame, useThree } from "@react-three/fiber";
import { Html, useGLTF } from "@react-three/drei";
import {
  Box3,
  BoxGeometry,
  Color,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  Object3D,
  Quaternion,
  Vector3,
} from "three";
import WorldGLB from "@/assets/world-transformed.glb";
import { Interactable, propFor } from "@/data/interact";
import { useInteract } from "@/components/tour/useInteract";
import { activate } from "@/components/tour/activate";
import { DRACO_PATH, ktx2Textures } from "./loaders";

/** Materials that light themselves: they neither cast nor receive shadows. */
const SELF_LIT = new Set(["window_glow", "lantern_glow", "lava_hot", "lava_cool", "void", "bottle_glass"]);
const LAVA = new Set(["lava_hot", "lava_cool"]);
const HOVER = new Color("#ffb45a");

interface Prop {
  it: Interactable;
  meshes: Mesh[];
  /** Top-centre of the prop, where its tag floats. */
  tagAt: Vector3;
}

/**
 * glTF node names of an object and its ancestors, nearest first.
 *
 * Uses the ORIGINAL node name GLTFLoader keeps in userData.name, never
 * `.name`: a multi-material node is split into one mesh per material, and
 * those parts get auto-names with a counter ("POI_experience" -> parts
 * "POI_experience_1", "_2", ...) that collide with real nodes (the flags
 * "POI_experience_1"...). Looking parts up by `.name` animated a piece of the
 * signal mast as a flag, swinging it about the world origin.
 */
function lineage(o: Object3D) {
  const names: string[] = [];
  for (let p: Object3D | null = o; p; p = p.parent) {
    if (typeof p.userData.name === "string") names.push(p.userData.name);
  }
  return names;
}

/** The node with this exact glTF node name (see lineage for why not .name). */
function findNode(root: Object3D, name: string): Object3D | null {
  let found: Object3D | null = null;
  root.traverse((o) => {
    if (!found && o.userData.name === name) found = o;
  });
  return found;
}

/**
 * The archipelago: the home island and its outpost, Ember Isle (projects),
 * Skull Cove (resume), Lighthouse Rock (experience) and the Drifting Isle
 * (contact), plus the props on them that ARE the navigation (POI_* nodes).
 * Built and approved in Blender (blender/world.py), exported with
 * blender/export_world.py, authored in place at world coordinates.
 */
export default function World() {
  const gl = useThree((s) => s.gl);
  const { scene } = useGLTF(WorldGLB, DRACO_PATH, true, ktx2Textures(gl));
  const hovered = useInteract((s) => s.hovered);
  const setHovered = useInteract((s) => s.setHovered);

  const { root, lava, props, moving } = useMemo(() => {
    const r = scene.clone(true);
    r.updateMatrixWorld(true);
    const lavaMats = new Map<MeshStandardMaterial, number>();
    const props = new Map<string, Prop>();

    r.traverse((o) => {
      const m = o as Mesh;
      if (!m.isMesh) return;
      const mat = m.material as MeshStandardMaterial;
      const selfLit = SELF_LIT.has(mat.name);
      m.castShadow = !selfLit && mat.name !== "vc_water";
      m.receiveShadow = !selfLit;
      if (LAVA.has(mat.name)) lavaMats.set(mat, mat.emissiveIntensity);

      const it = propFor(lineage(m));
      if (!it) {
        // Scenery: never hit by the pointer. Keeps hover raycasts cheap in a
        // million-vertex world.
        m.raycast = () => {};
        return;
      }
      // Own material per prop mesh, so hover glow lights only this prop.
      const own = mat.clone();
      own.userData.baseEmissive = own.emissive.clone();
      own.userData.baseIntensity = own.emissiveIntensity;
      m.material = own;
      m.userData.interactKey = it.key;
      const p = props.get(it.key) ?? { it, meshes: [], tagAt: new Vector3() };
      p.meshes.push(m);
      props.set(it.key, p);
    });

    // Padded invisible hit volumes (a 1 m prop is a few pixels from the
    // dock), and the tag anchor over each prop. A prop whose padded box would
    // swallow other props (the signal mast around its four flags) gets no
    // box: the nearest hit wins, so its box would steal the flags' clicks.
    const boxes = new Map<string, Box3>();
    props.forEach((p, key) => {
      const b = new Box3();
      p.meshes.forEach((m) => b.expandByObject(m));
      boxes.set(key, b);
      p.tagAt.set((b.min.x + b.max.x) / 2, b.max.y + 0.8, (b.min.z + b.max.z) / 2);
    });
    const hitMat = new MeshBasicMaterial({ visible: false });
    const centre = new Vector3();
    boxes.forEach((b, key) => {
      const padded = b.clone().expandByScalar(0.6);
      let swallows = false;
      boxes.forEach((other, k) => {
        if (k !== key && padded.containsPoint(other.getCenter(centre))) swallows = true;
      });
      if (swallows) return;
      const size = padded.getSize(new Vector3());
      const hit = new Mesh(new BoxGeometry(size.x, size.y, size.z), hitMat);
      hit.position.copy(padded.getCenter(new Vector3()));
      hit.userData.interactKey = key;
      r.add(hit);
    });

    // Moving parts: pivot at the node origin, animated on top of their rest pose.
    const find = (n: string) => findNode(r, n);
    const rest = (o: Object3D | null) => (o ? { o, q: o.quaternion.clone() } : null);
    const moving = {
      rotor: rest(find("POI_projects_0_rotor")),
      flags: [0, 1, 2, 3].map((i) => rest(find(`POI_experience_${i}`))).filter(Boolean) as {
        o: Object3D;
        q: Quaternion;
      }[],
    };
    return { root: r, lava: lavaMats, props, moving };
  }, [scene]);

  // Hover glow + cursor.
  useEffect(() => {
    props.forEach((p, key) => {
      const on = key === hovered;
      p.meshes.forEach((m) => {
        const mat = m.material as MeshStandardMaterial;
        if (on) {
          mat.emissive.copy(HOVER);
          mat.emissiveIntensity = Math.max(0.35, mat.userData.baseIntensity);
        } else {
          mat.emissive.copy(mat.userData.baseEmissive);
          mat.emissiveIntensity = mat.userData.baseIntensity;
        }
      });
    });
  }, [hovered, props]);

  const q = useMemo(() => new Quaternion(), []);
  const axisX = useMemo(() => new Vector3(1, 0, 0), []);
  const axisY = useMemo(() => new Vector3(0, 1, 0), []);
  const axisZ = useMemo(() => new Vector3(0, 0, 1), []);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    // Molten, not neon: a slow uneven throb in the lava's glow.
    const k = 1 + Math.sin(t * 1.3) * 0.1 + Math.sin(t * 3.7 + 1.1) * 0.05;
    lava.forEach((base, mat) => {
      mat.emissiveIntensity = base * k;
    });
    // Anemometer spins; signal flags flap. (The chest is its own component.)
    if (moving.rotor) moving.rotor.o.quaternion.copy(moving.rotor.q).multiply(q.setFromAxisAngle(axisY, t * 2.4));
    moving.flags.forEach((f, i) => {
      const a = Math.sin(t * 2.1 + i * 1.3) * 0.25 + Math.sin(t * 5.3 + i) * 0.06;
      f.o.quaternion.copy(f.q).multiply(q.setFromAxisAngle(axisX, 0.18 + a * 0.6)).multiply(
        q.setFromAxisAngle(axisZ, a * 0.3)
      );
    });
  });

  const keyOf = (e: ThreeEvent<PointerEvent | MouseEvent>) =>
    (e.object.userData.interactKey as string | undefined) ?? null;

  const tag = hovered ? props.get(hovered) : undefined;

  return (
    <>
      <primitive
        object={root}
        onPointerMove={(e: ThreeEvent<PointerEvent>) => {
          const key = keyOf(e);
          if (!key) return;
          e.stopPropagation();
          if (key !== useInteract.getState().hovered) setHovered(key);
          document.body.style.cursor = "pointer";
        }}
        onPointerOut={(e: ThreeEvent<PointerEvent>) => {
          if (!keyOf(e)) return;
          setHovered(null);
          document.body.style.cursor = "auto";
        }}
        onClick={(e: ThreeEvent<MouseEvent>) => {
          const key = keyOf(e);
          const p = key ? props.get(key) : undefined;
          if (!p) return;
          e.stopPropagation();
          activate(p.it);
        }}
      />
      {tag && (
        <Html position={tag.tagAt} center zIndexRange={[10, 0]} style={{ pointerEvents: "none" }}>
          <div className="whitespace-nowrap rounded-full border border-amber-200/40 bg-slate-950/80 px-3 py-1 text-sm font-semibold text-amber-100 shadow-lg backdrop-blur">
            {tag.it.tag}
          </div>
        </Html>
      )}
    </>
  );
}

// No `useGLTF.preload` here: the KTX2 textures need the renderer (see
// loaders.ts), and World mounts with the Canvas anyway, so nothing is lost.
