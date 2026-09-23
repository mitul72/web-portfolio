import { create } from "zustand";

interface InteractState {
  /** Key of the prop or NPC under the pointer ("poi:..." / "npc:..."). */
  hovered: string | null;
  /** Close-up the camera is on (a key of SHOTS), or null for the dock view. */
  focus: string | null;
  /** NPC whose dialogue is open (key of NPCS), or null. */
  dialogue: string | null;
  setHovered: (key: string | null) => void;
  focusShot: (shot: string) => void;
  clearFocus: () => void;
  openDialogue: (npc: string) => void;
  closeDialogue: () => void;
}

/**
 * The cabin-style interaction layer, shared by the scene (hover glow, camera
 * close-ups) and the DOM (tags, NPC dialogue). Navigation (useTour) clears it
 * whenever the ship sets sail.
 */
export const useInteract = create<InteractState>((set) => ({
  hovered: null,
  focus: null,
  dialogue: null,
  setHovered: (hovered) => set({ hovered }),
  focusShot: (focus) => set({ focus }),
  clearFocus: () => set({ focus: null }),
  openDialogue: (dialogue) => set({ dialogue }),
  closeDialogue: () => set({ dialogue: null }),
}));
