import { create } from "zustand";
import { hostOf } from "@/data/interact";

interface InteractState {
  /** Key of the prop or NPC under the pointer ("poi:..." / "npc:..."). */
  hovered: string | null;
  /** Close-up the camera is on (a key of SHOTS), or null for the dock view. */
  focus: string | null;
  /** NPC whose dialogue is open (key of NPCS), or null. */
  dialogue: string | null;
  /** True when the open dialogue is with someone you've already talked to. */
  returning: boolean;
  /** NPCs talked to this visit. */
  met: string[];
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
  returning: false,
  met: [],
  setHovered: (hovered) => set({ hovered }),
  focusShot: (focus) => set({ focus }),
  clearFocus: () => set({ focus: null }),
  openDialogue: (dialogue) =>
    set((s) => ({
      dialogue,
      returning: s.met.includes(dialogue),
      met: s.met.includes(dialogue) ? s.met : [...s.met, dialogue],
    })),
  closeDialogue: () => set({ dialogue: null }),
}));

/**
 * The island's host greets you: the camera lands on them and their dialogue
 * opens. Returns false if the stop has no host (the caller then falls back to
 * opening the stop's panel).
 */
export function greet(stopId: string): boolean {
  const id = hostOf(stopId);
  if (!id) return false;
  const ui = useInteract.getState();
  ui.focusShot(`npc:${id}`);
  ui.openDialogue(id);
  return true;
}
