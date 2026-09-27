"use client";

import { useEffect, useRef } from "react";
import { useVoyage } from "@/components/tour/useVoyage";
import { useAudio } from "./useAudio";

/**
 * Voyage sound cues, layered over the ambient ocean loop:
 *   - a looping water-rush that fades in while sailing, out when docked
 *   - a one-shot splash/bell on arrival
 *
 * Files are OPTIONAL: drop them in /public/audio/ and they'll play; if absent
 * (404) the calls fail silently, so nothing breaks. Honors the global mute.
 *
 *   public/audio/sailing-loop.mp3   (looping water rush)
 *   public/audio/arrive.mp3         (one-shot splash / bell)
 */
export default function SailingSfx() {
  const sailingLoop = useRef<HTMLAudioElement | null>(null);
  const arrive = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    sailingLoop.current = new Audio("/audio/sailing-loop.mp3");
    sailingLoop.current.loop = true;
    sailingLoop.current.volume = 0;
    arrive.current = new Audio("/audio/arrive.mp3");
    arrive.current.volume = 0.6;

    const safePlay = (a: HTMLAudioElement | null) => a?.play().catch(() => {});
    // One fade at a time per element: a new fade (e.g. setting sail again
    // while the arrival fade-out is running) cancels the old one.
    const fading = new Map<HTMLAudioElement, number>();
    const fade = (a: HTMLAudioElement | null, to: number, ms = 500) => {
      if (!a) return;
      const pending = fading.get(a);
      if (pending !== undefined) cancelAnimationFrame(pending);
      const from = a.volume;
      const start = performance.now();
      const step = (now: number) => {
        // rAF's timestamp is the frame's start, which can be a hair before
        // `start`: clamp, or the first step asks for a volume below 0.
        const k = Math.min(1, Math.max(0, (now - start) / ms));
        a.volume = Math.min(1, Math.max(0, from + (to - from) * k));
        if (k < 1) fading.set(a, requestAnimationFrame(step));
        else {
          fading.delete(a);
          if (to === 0) a.pause();
        }
      };
      fading.set(a, requestAnimationFrame(step));
    };

    let prevPhase = useVoyage.getState().phase;
    const unsub = useVoyage.subscribe((s) => {
      if (s.phase === prevPhase) return;
      const muted = useAudio.getState().muted;

      if (s.phase === "sailing" && !muted) {
        safePlay(sailingLoop.current);
        fade(sailingLoop.current, 0.5);
      } else if (s.phase === "docked") {
        fade(sailingLoop.current, 0);
        if (prevPhase === "sailing" && !muted) {
          if (arrive.current) arrive.current.currentTime = 0;
          safePlay(arrive.current);
        }
      }
      prevPhase = s.phase;
    });

    // React to mute changes mid-voyage.
    const unsubMute = useAudio.subscribe((s) => {
      if (s.muted) fade(sailingLoop.current, 0);
      else if (useVoyage.getState().phase === "sailing") {
        safePlay(sailingLoop.current);
        fade(sailingLoop.current, 0.5);
      }
    });

    return () => {
      unsub();
      unsubMute();
      sailingLoop.current?.pause();
    };
  }, []);

  return null;
}
