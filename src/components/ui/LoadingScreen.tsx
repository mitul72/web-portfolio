"use client";

import { useProgress } from "@react-three/drei";
import { useEffect, useState } from "react";

/**
 * Full-screen loader shown while the heavy GLB assets stream in. Fades out
 * (and unmounts) once loading completes so it never blocks interaction.
 */
export default function LoadingScreen() {
  const { progress, active } = useProgress();
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    if (!active && progress >= 100) {
      const t = setTimeout(() => setHidden(true), 600);
      return () => clearTimeout(t);
    }
  }, [active, progress]);

  if (hidden) return null;

  return (
    <div
      className={`absolute inset-0 z-50 flex flex-col items-center justify-center bg-slate-950 text-white transition-opacity duration-500 ${
        !active && progress >= 100 ? "opacity-0" : "opacity-100"
      }`}
    >
      <div className="text-4xl">⚓</div>
      <p className="mt-4 text-sm uppercase tracking-[0.3em] text-white/60">
        Charting the waters
      </p>
      <div className="mt-6 h-1.5 w-56 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-amber-400 transition-[width] duration-300"
          style={{ width: `${Math.min(100, progress)}%` }}
        />
      </div>
      <p className="mt-2 text-xs text-white/40">{Math.round(progress)}%</p>
    </div>
  );
}
