"use client";

import { useEffect, useState } from "react";
import { STOPS } from "@/data/portfolio";

/**
 * Subtle cinematic title card: name + tagline fade in over the establishing
 * shot, hold, then fade out and unmount — handing a clean scene to the user.
 */
export default function IntroTitle() {
  const [phase, setPhase] = useState<"in" | "hold" | "out" | "done">("in");

  const intro = STOPS.find((s) => s.content.kind === "intro")?.content;
  const name = intro && intro.kind === "intro" ? intro.name : "";
  const tagline = intro && intro.kind === "intro" ? intro.tagline : "";

  useEffect(() => {
    const t1 = setTimeout(() => setPhase("hold"), 1200);
    const t2 = setTimeout(() => setPhase("out"), 3600);
    const t3 = setTimeout(() => setPhase("done"), 4600);
    return () => [t1, t2, t3].forEach(clearTimeout);
  }, []);

  if (phase === "done") return null;

  const visible = phase === "in" || phase === "hold";

  return (
    <div
      className={`pointer-events-none absolute inset-0 z-40 flex flex-col items-center justify-center text-center transition-opacity duration-1000 ${
        visible ? "opacity-100" : "opacity-0"
      }`}
    >
      <h1 className="text-5xl font-black tracking-tight text-white drop-shadow-[0_2px_20px_rgba(0,0,0,0.6)] sm:text-7xl">
        {name}
      </h1>
      <p className="mt-3 text-sm uppercase tracking-[0.4em] text-amber-200 drop-shadow sm:text-base">
        {tagline}
      </p>
      <p className="mt-8 animate-pulse text-xs uppercase tracking-[0.3em] text-white/70">
        Drag to set sail ⚓
      </p>
    </div>
  );
}
