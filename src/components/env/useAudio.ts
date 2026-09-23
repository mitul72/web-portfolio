import { create } from "zustand";

/** Shared audio state so SFX and the ambient loop honor one mute toggle. */
interface AudioState {
  muted: boolean;
  setMuted: (m: boolean) => void;
  toggle: () => void;
}

export const useAudio = create<AudioState>((set, get) => ({
  // On by default. Browsers block sound until the visitor interacts, so
  // BackgroundMusic retries on their first click, tap or key.
  muted: false,
  setMuted: (m) => set({ muted: m }),
  toggle: () => set({ muted: !get().muted }),
}));
