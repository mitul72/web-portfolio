"use client";

import { STOPS } from "@/data/portfolio";
import { useTour } from "@/components/tour/useTour";

/**
 * Lightweight top overlay: name/brand on the left, quick actions on the right.
 * Deep-links into the tour (e.g. jump straight to the resume stop).
 */
export default function Navbar() {
  const goTo = useTour((s) => s.goTo);
  const home = useTour((s) => s.home);

  const resumeIndex = STOPS.findIndex((s) => s.kind === "resume");

  return (
    <header className="pointer-events-none absolute inset-x-0 top-0 z-30 flex items-center justify-between p-4 sm:p-6">
      <button
        onClick={home}
        className="pointer-events-auto text-lg font-bold tracking-tight text-white drop-shadow"
      >
        ⚓ Mitul Dhawan
      </button>

      {resumeIndex >= 0 && (
        <button
          onClick={() => goTo(resumeIndex)}
          className="pointer-events-auto rounded-full border border-white/30 bg-black/40 px-4 py-1.5 text-sm text-white backdrop-blur transition hover:bg-white/10"
        >
          Resume
        </button>
      )}
    </header>
  );
}
