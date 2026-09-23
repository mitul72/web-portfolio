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
  // Alongside the east face of the pier's T-head (the pier runs out from the
  // beach to z~106, its T-head spans x 2..14), bow in toward the island, so
  // the ship arrives bow-first and leaves by sailing straight out to sea.
  position: [21.5, 106],
  heading: Math.PI,
  via: [21.5, 150], // straight out past the stern before turning for a leg
  camera: {
    position: [62, 14, 148],
    lookAt: [8, 16, 40],
  },
};

// Per-stop docks, keyed by stop id. Stops without a dock (e.g. the intro) use
// HOME_DOCK — the ship just stays home.
// Every dock, route and camera below was checked in Blender against the real
// terrain with a stand-in of the ship placed exactly as the app places it
// (blender/dock_check.py): no hull over land, no route leg over land, and each
// camera frames its island's landmark with the moored ship in view.
export const DOCKS: Record<string, Dock> = {
  intro: HOME_DOCK,

  "project-1": {
    // Moored off the end of Ember Isle's jetty, bow in toward the camp.
    position: [-181.2, -109.9],
    heading: -1.844,
    via: [-190, 110], // round the home island's west end, clear of its stacks
    camera: {
      // Volcano, lava flow, camp and ship in one frame.
      position: [-150, 16, 0],
      lookAt: [-270, 26, -120],
    },
  },

  resume: {
    // Anchored just outside Skull Cove's lagoon, broadside to the beach.
    position: [252.4, 241.6],
    heading: 0.864,
    via: [88, 117],
    camera: {
      // Low, square on to the skull's face; the ship on the right third.
      position: [182.5, 9, 274],
      lookAt: [280, 16, 160],
    },
  },

  experience: {
    // Alongside Lighthouse Rock's jetty, bow short of the rock shelf.
    position: [166, -222],
    heading: Math.PI,
    via: [175, 40], // round the home island's east end
    camera: {
      // From the south-east: lighthouse, cliffs, stacks and the wreck.
      position: [237, 14, -120],
      lookAt: [180, 24, -300],
    },
  },

  contact: {
    // Anchored below the Drifting Isle, well clear of its chains and the
    // waterfall's plunge pool.
    position: [-190, 290],
    heading: Math.PI / 2,
    via: [-90, 160], // south of the home island, over open water
    camera: {
      // From the south-south-east, so the low western sun side-lights the
      // floating island instead of silhouetting it.
      position: [-170, 24, 370],
      lookAt: [-240, 28, 220],
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
