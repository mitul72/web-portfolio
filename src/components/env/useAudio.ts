import { create } from "zustand";

/** Shared audio state so SFX and the ambient loop honor one mute toggle. */
interface AudioState {
  muted: boolean;
  setMuted: (m: boolean) => void;
  toggle: () => void;
}

export const useAudio = create<AudioState>((set, get) => ({
  muted: true, // start muted until the user opts in (autoplay policy)
  setMuted: (m) => set({ muted: m }),
  toggle: () => set({ muted: !get().muted }),
}));
