import { create } from "zustand";
import { STOPS } from "@/data/portfolio";
import { useVoyage } from "./useVoyage";
import { greet, useInteract } from "./useInteract";
import { hostOf } from "@/data/interact";

/**
 * On arrival the island is shown first (the dock reveal, ~1.2 s), held for a
 * beat, THEN the camera moves on to the host. Long enough to take the island
 * in, short enough that nobody wonders what to do next.
 */
const HOST_DELAY_MS = 3000;
/** Bumps on every navigation, so a pending greeting from an earlier trip never fires. */
let arrivalToken = 0;

interface TourState {
  /** Index of the current stop, or null when at the free-look home view. */
  activeIndex: number | null;
  /** Whether the content panel for the active stop is open. */
  panelOpen: boolean;
  /** id of the selected sub-POI on the active island (null = island overview). */
  activeSubPoiId: string | null;
  /** Sail to a stop. `then` replaces the default "open the panel on arrival". */
  goTo: (index: number, then?: () => void) => void;
  next: () => void;
  prev: () => void;
  /** Return to the home view and close any panel (free look). */
  home: () => void;
  closePanel: () => void;
  /** Open the active stop's own panel (e.g. its prop was clicked). */
  openPanel: () => void;
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
  /** Sail to a stop (or home); on arrival run `then`, else the host greets you. */
  const navigate = (index: number | null, then?: () => void) => {
    // Close any open panel + clear sub-POI selection; re-opens on arrival.
    set({ activeIndex: index, panelOpen: false, activeSubPoiId: null });
    const token = ++arrivalToken;
    // Setting sail drops any close-up or conversation.
    const ui = useInteract.getState();
    ui.clearFocus();
    ui.closeDialogue();
    const stopId = index === null ? null : STOPS[index].id;

    // The resume stop's chest lid swings open on arrival (models/world.tsx),
    // so its panel waits for the lid to start lifting. Other stops open their
    // panel immediately on arrival.
    const panelDelay = stopId === "resume" ? 800 : 0;

    useVoyage.getState().sailTo(stopId, () => {
      // Only open the panel for real stops (not the home view).
      if (get().activeIndex === null) return;
      if (then) {
        // A prop or an NPC asked for this trip: it opens its own content.
        if (get().activeIndex === index) then();
        return;
      }
      // Otherwise: show the island, then its host greets you (NPC close-up
      // + dialogue); their choices lead to the content. If you've already
      // clicked something in the meantime, the host doesn't interrupt. Only a
      // stop without a host opens its panel directly.
      if (stopId && hostOf(stopId)) {
        setTimeout(() => {
          const ui = useInteract.getState();
          const stillHere =
            token === arrivalToken &&
            get().activeIndex === index &&
            useVoyage.getState().phase === "docked";
          if (!stillHere || ui.focus || ui.dialogue || get().panelOpen) return;
          greet(stopId);
        }, HOST_DELAY_MS);
        return;
      }
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

    goTo: (index, then) => {
      const clamped = Math.max(0, Math.min(STOPS.length - 1, index));
      navigate(clamped, then);
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

    openPanel: () => set({ panelOpen: true, activeSubPoiId: null }),

    selectSubPoi: (id) => set({ activeSubPoiId: id, panelOpen: true }),
  };
});
