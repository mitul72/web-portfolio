import { STOPS, Vec3 } from "./portfolio";

// -----------------------------------------------------------------------------
// SHIP DOCKS (hub-and-spoke sailing)
// -----------------------------------------------------------------------------
// Where the ship parks for each stop, and the camera "arrival" framing once it
// gets there. The main island is HOME — the ship always sails out from home to
// a stop's dock and back (hub-and-spoke), so we only author one path per stop.
//
// A dock is on the WATER near the stop's island, not on the marker itself.
// Tune positions with the dev coordinate logger (SHOW_DEV_COORDS in page.tsx).
// -----------------------------------------------------------------------------

export interface Dock {
  /** Where the ship sits (XZ on the ocean plane). */
  position: [number, number];
  /** Heading (radians) the ship faces while docked. */
  heading: number;
  /**
   * The open-water corridor waypoint for this dock: the route curves through
   * it both when arriving here AND when departing (so island→island legs sail
   * back out the way they came in, around terrain). XZ on the ocean plane.
   */
  via: [number, number];
  /** Camera framing when the ship arrives at this dock. */
  camera: { position: Vec3; lookAt: Vec3 };
}

// HOME: the ship's resting spot beside the main pirate island.
export const HOME_DOCK: Dock = {
  position: [2.278, 98.04],
  heading: -0.395, // matches the ship's authored rotation.y
  via: [2.278, 98.04],
  camera: {
    position: [23.08, 30.52, 150.63],
    lookAt: [21.7, 12, 105],
  },
};

// Per-stop docks, keyed by stop id. Stops without a dock (e.g. the intro) use
// HOME_DOCK — the ship just stays home.
export const DOCKS: Record<string, Dock> = {
  intro: HOME_DOCK,

  "project-1": {
    // Open water ~45 units short of the volcano's near shore (island footprint
    // is X[-412..-229], Z[-210..-45]). The ship parks here facing the island.
    position: [-210, -59],
    heading: -2.207, // faces from the dock toward the island center
    via: [-90, -10], // bow the sailing arc out through open water
    camera: {
      // On arrival, FOCUS on the volcano island itself (center ~[-320,-140]) so
      // it fills the frame and is easy to look around — the ship is incidental.
      position: [-210, 55, -30],
      lookAt: [-320, 25, -140],
    },
  },

  resume: {
    // Open water ~45 units short of the treasure island's shore (center
    // ~[280,160], radius ~64 at current scale). Ship parks facing the island.
    position: [174, 136],
    heading: 1.351,
    via: [88, 117],
    camera: {
      // Framing captured via SHOW_DEV_COORDS (press "c"): a high 3/4 view that
      // frames the treasure island + chest. lookAt derived from that camera's
      // forward ray, landing on the island center.
      position: [207.5, 81.54, 243.09],
      lookAt: [285.3, 20.9, 153.8],
    },
  },

  experience: {
    // Open water ~45 short of the fantasy isle's shore (center [180,-300],
    // footprint radius ~135 at scale 1). Approach from the home/NW side; tune
    // against the real shoreline via SHOW_DEV_COORDS.
    position: [106, -136],
    heading: 2.72, // faces from the dock toward the island center
    via: [68, -49],
    camera: {
      // Captured live with SHOW_DEV_COORDS ("c"): high on the NE approach,
      // looking down the flag-trail slope. lookAt derived from the captured
      // rotation's forward ray, landing on the island slope.
      position: [195.63, 72.58, -183.81],
      lookAt: [182, 35, -286],
    },
  },
};

/** Resolve the dock for a stop id, falling back to HOME. */
export function dockForStop(stopId: string | null): Dock {
  if (!stopId) return HOME_DOCK;
  return DOCKS[stopId] ?? HOME_DOCK;
}

/** Convenience: the dock for a stop index into STOPS. */
export function dockForIndex(index: number | null): Dock {
  if (index === null || index < 0 || index >= STOPS.length) return HOME_DOCK;
  return dockForStop(STOPS[index].id);
}
