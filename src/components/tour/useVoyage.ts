import { create } from "zustand";
import gsap from "gsap";
import { CatmullRomCurve3, Vector2, Vector3 } from "three";
import { Dock, HOME_DOCK, dockForStop } from "@/data/anchors";

// Legs take time proportional to their length (clamped), so short hops don't
// look slow-motion and long hauls don't teleport. A skip jumps progress to 1.
const CRUISE_SPEED = 110; // world units / second
const MIN_DURATION = 1.2;
const MAX_DURATION = 5;
// Waypoints closer than this collapse into one (e.g. HOME's via sits on HOME).
const WAYPOINT_EPSILON = 2;

export type VoyagePhase = "docked" | "sailing" | "arriving";

interface VoyageState {
  phase: VoyagePhase;
  /** Dock the ship is sailing TO (or resting at). */
  to: Dock;
  /**
   * The current leg's route, arc-length parameterized: sample with
   * `getPointAt(progress)` for uniform speed. Runs from the ship's departure
   * spot out through the departure dock's `via` corridor, then in through the
   * destination's — so island→island legs stay on authored water even though
   * only the home↔stop arcs were hand-placed. Null until the first voyage.
   */
  curve: CatmullRomCurve3 | null;
  /** 0..1 progress along the current leg (drives ship + camera). */
  progress: number;
  /** id of the stop we're sailing to (null = home). */
  targetStopId: string | null;
  /** Fired once when a voyage completes — used to open the content panel. */
  onArrive: (() => void) | null;

  /** Live ship XZ + heading, updated by the vessel each frame (for the camera). */
  shipPos: Vector2;
  shipHeading: number;
  setShip: (x: number, z: number, heading: number) => void;

  /** Begin a voyage to a stop's dock (or home). */
  sailTo: (stopId: string | null, onArrive?: () => void) => void;
  /** Skip the rest of the current voyage (jump to arrival). */
  skip: () => void;

  _tween: gsap.core.Tween | null;
}

export const useVoyage = create<VoyageState>((set, get) => ({
  phase: "docked",
  to: HOME_DOCK,
  curve: null,
  progress: 1,
  targetStopId: null,
  onArrive: null,

  shipPos: new Vector2(HOME_DOCK.position[0], HOME_DOCK.position[1]),
  shipHeading: HOME_DOCK.heading,
  setShip: (x, z, heading) => {
    // Mutated in place (read by the camera in useFrame); no re-render needed.
    const s = get();
    s.shipPos.set(x, z);
    s.shipHeading = heading;
  },

  sailTo: (stopId, onArrive) => {
    const state = get();

    // Already docked there (or en route): don't restart the voyage.
    if (stopId === state.targetStopId) {
      if (state.phase === "docked") onArrive?.();
      else set({ onArrive: onArrive ?? null });
      return;
    }

    state._tween?.kill();

    const to = dockForStop(stopId);
    const start: [number, number] = [state.shipPos.x, state.shipPos.y];
    const end = to.position;

    // Route out through the corridor we came in by (the dock we're leaving),
    // then in through the destination's. Vias that sit on an endpoint (HOME)
    // or on each other collapse away.
    const points: [number, number][] = [start];
    for (const via of [state.to.via, to.via]) {
      const prev = points[points.length - 1];
      if (dist(via, prev) > WAYPOINT_EPSILON && dist(via, end) > WAYPOINT_EPSILON)
        points.push(via);
    }
    points.push(end);

    // Same dock (e.g. two stops sharing HOME): settle instantly, no fake sail.
    if (points.length === 2 && dist(start, end) <= WAYPOINT_EPSILON) {
      set({
        to,
        curve: null,
        targetStopId: stopId,
        phase: "docked",
        progress: 1,
        onArrive: null,
        _tween: null,
      });
      onArrive?.();
      return;
    }

    const curve = new CatmullRomCurve3(
      points.map(([x, z]) => new Vector3(x, 0, z)),
      false,
      "catmullrom",
      0.5
    );
    const duration = clamp(
      curve.getLength() / CRUISE_SPEED,
      MIN_DURATION,
      MAX_DURATION
    );

    set({
      to,
      curve,
      targetStopId: stopId,
      phase: "sailing",
      progress: 0,
      onArrive: onArrive ?? null,
    });

    const proxy = { p: 0 };
    const tween = gsap.to(proxy, {
      p: 1,
      duration,
      ease: "power2.inOut",
      onUpdate: () => set({ progress: proxy.p }),
      onComplete: () => {
        set({ phase: "docked", progress: 1, _tween: null });
        get().onArrive?.();
      },
    });
    set({ _tween: tween });
  },

  skip: () => {
    const { _tween } = get();
    if (_tween) _tween.progress(1);
  },

  _tween: null,
}));

function dist(a: [number, number], b: [number, number]) {
  return Math.hypot(a[0] - b[0], a[1] - b[1]);
}

function clamp(v: number, min: number, max: number) {
  return Math.min(max, Math.max(min, v));
}
