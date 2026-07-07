import { create } from "zustand";
import { STOPS } from "@/data/portfolio";
import { useVoyage } from "./useVoyage";

interface TourState {
  /** Index of the current stop, or null when at the free-look home view. */
  activeIndex: number | null;
  /** Whether the content panel for the active stop is open. */
  panelOpen: boolean;
  /** id of the selected sub-POI on the active island (null = island overview). */
  activeSubPoiId: string | null;
  goTo: (index: number) => void;
  next: () => void;
  prev: () => void;
  /** Return to the home view and close any panel (free look). */
  home: () => void;
  closePanel: () => void;
  /** Select a sub-POI (bottle/gem) on the current island, opening its panel. */
  selectSubPoi: (id: string) => void;
}

// NOTE: derived data (active stop, its sub-POIs, the panel's content) is
// computed in the COMPONENTS from `activeIndex`/`activeSubPoiId` + the static
// STOPS array — never via a store selector that builds a new object/array each
// call, which triggers infinite re-render loops in zustand.

/**
 * Central tour state. Navigation sets the active stop and starts the ship on a
 * voyage to that stop's dock; the content panel opens only when the ship
 * ARRIVES (via the voyage's onArrive callback). Kept in a tiny store so both
 * the R3F canvas children and the DOM overlay can read/drive it.
 */
export const useTour = create<TourState>((set, get) => {
  /** Sail to a stop (or home) and open its panel on arrival. */
  const navigate = (index: number | null) => {
    // Close any open panel + clear sub-POI selection; re-opens on arrival.
    set({ activeIndex: index, panelOpen: false, activeSubPoiId: null });
    const stopId = index === null ? null : STOPS[index].id;

    // The treasure/resume stop plays a short chest-opening beat on arrival, so
    // its download-resume popup waits for the chest to start opening (kept in
    // sync with CHEST_OPEN_DELAY in treasure-island.tsx). Other stops open
    // their panel immediately on arrival.
    const panelDelay = stopId === "resume" ? 800 : 0;

    useVoyage.getState().sailTo(stopId, () => {
      // Only open the panel for real stops (not the home view).
      if (get().activeIndex === null) return;
      if (panelDelay === 0) set({ panelOpen: true });
      else
        setTimeout(() => {
          // Guard: only open if we're still at this stop when the timer fires.
          if (get().activeIndex === index) set({ panelOpen: true });
        }, panelDelay);
    });
  };

  return {
    activeIndex: null,
    panelOpen: false,
    activeSubPoiId: null,

    goTo: (index) => {
      const clamped = Math.max(0, Math.min(STOPS.length - 1, index));
      navigate(clamped);
    },

    next: () => {
      const { activeIndex } = get();
      const nextIndex = activeIndex === null ? 0 : activeIndex + 1;
      if (nextIndex > STOPS.length - 1) return;
      navigate(nextIndex);
    },

    prev: () => {
      const { activeIndex } = get();
      const prevIndex = activeIndex === null ? 0 : activeIndex - 1;
      if (prevIndex < 0) return;
      navigate(prevIndex);
    },

    home: () => navigate(null),

    closePanel: () => set({ panelOpen: false, activeSubPoiId: null }),

    selectSubPoi: (id) => set({ activeSubPoiId: id, panelOpen: true }),
  };
});
