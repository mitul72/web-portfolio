"use client";

import { STOPS } from "@/data/portfolio";
import { useTour } from "@/components/tour/useTour";
import { useVoyage } from "@/components/tour/useVoyage";

/**
 * Bottom section navigation — a clean row of NAMED buttons (Home · Projects ·
 * Resume · …) so a recruiter can jump straight to any section. Clicking sails
 * there; the active section is highlighted. During a voyage it collapses to a
 * single "Skip" control.
 */
export default function TourControls() {
  const activeIndex = useTour((s) => s.activeIndex);
  const goTo = useTour((s) => s.goTo);
  const home = useTour((s) => s.home);
  const phase = useVoyage((s) => s.phase);
  const skip = useVoyage((s) => s.skip);

  if (STOPS.length <= 1) return null;

  // While sailing, show a single Skip control instead of the nav bar.
  if (phase === "sailing") {
    return (
      <div className="pointer-events-auto absolute bottom-4 left-1/2 z-20 -translate-x-1/2">
        <button
          onClick={skip}
          className="flex items-center gap-2 rounded-full border border-white/15 bg-slate-900/70 px-5 py-2 text-sm text-white shadow-xl backdrop-blur-xl transition hover:bg-white/10"
        >
          Skip voyage ⏭
        </button>
      </div>
    );
  }

  return (
    <div className="pointer-events-auto absolute bottom-4 left-1/2 z-20 -translate-x-1/2">
      <nav className="flex items-center gap-1 rounded-full border border-white/15 bg-slate-900/75 px-2 py-1.5 text-white shadow-xl backdrop-blur-xl">
        {/* Home / free-look reset */}
        <button
          onClick={home}
          className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${
            activeIndex === null
              ? "bg-white/15 text-white"
              : "text-white/70 hover:bg-white/10 hover:text-white"
          }`}
        >
          ⚓ Home
        </button>

        <div className="mx-0.5 h-5 w-px bg-white/15" />

        {STOPS.map((stop, i) => (
          <button
            key={stop.id}
            onClick={() => goTo(i)}
            className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${
              activeIndex === i
                ? "bg-amber-400 text-black"
                : "text-white/70 hover:bg-white/10 hover:text-white"
            }`}
          >
            {stop.navLabel ?? stop.label}
          </button>
        ))}
      </nav>
    </div>
  );
}
