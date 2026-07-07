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
    <div className="pointer-events-auto absolute bottom-0 left-1/2 z-20 flex max-w-[100vw] -translate-x-1/2 justify-center px-2 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
      <nav className="flex max-w-full items-center gap-1 overflow-x-auto rounded-full border border-white/15 bg-slate-900/75 px-2 py-1.5 text-white shadow-xl backdrop-blur-xl [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {/* Home / free-look reset */}
        <button
          onClick={home}
          className={`shrink-0 rounded-full px-3 py-1.5 text-sm font-medium transition ${
            activeIndex === null
              ? "bg-white/15 text-white"
              : "text-white/70 hover:bg-white/10 hover:text-white"
          }`}
        >
          ⚓<span className="ml-1 hidden sm:inline">Home</span>
        </button>

        <div className="mx-0.5 h-5 w-px shrink-0 bg-white/15" />

        {STOPS.map((stop, i) => (
          <button
            key={stop.id}
            onClick={() => goTo(i)}
            className={`shrink-0 rounded-full px-3 py-1.5 text-sm font-medium transition ${
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
