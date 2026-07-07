"use client";

import { STOPS } from "@/data/portfolio";
import { useTour } from "@/components/tour/useTour";
import { useVoyage } from "@/components/tour/useVoyage";

export default function TourControls() {
  const activeIndex = useTour((s) => s.activeIndex);
  const next = useTour((s) => s.next);
  const prev = useTour((s) => s.prev);
  const home = useTour((s) => s.home);
  const goTo = useTour((s) => s.goTo);
  const phase = useVoyage((s) => s.phase);
  const skip = useVoyage((s) => s.skip);

  const atStart = activeIndex === null || activeIndex === 0;
  const atEnd = activeIndex === STOPS.length - 1;

  // Nothing to navigate with a single stop — hide the tour bar entirely.
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
      <div className="flex items-center gap-2 rounded-full border border-white/15 bg-slate-900/70 px-3 py-2 text-white shadow-xl backdrop-blur-xl">
        <button
          onClick={prev}
          disabled={atStart}
          className="rounded-full px-3 py-1 text-sm transition enabled:hover:bg-white/10 disabled:opacity-30"
        >
          ← Prev
        </button>

        {/* Progress dots */}
        <div className="flex items-center gap-1.5 px-1">
          {STOPS.map((stop, i) => (
            <button
              key={stop.id}
              onClick={() => goTo(i)}
              aria-label={stop.label}
              title={stop.label}
              className={`h-2.5 w-2.5 rounded-full transition ${
                activeIndex === i
                  ? "scale-125 bg-amber-400"
                  : "bg-white/30 hover:bg-white/60"
              }`}
            />
          ))}
        </div>

        <button
          onClick={next}
          disabled={atEnd}
          className="rounded-full px-3 py-1 text-sm transition enabled:hover:bg-white/10 disabled:opacity-30"
        >
          Next →
        </button>

        <div className="mx-1 h-5 w-px bg-white/15" />

        <button
          onClick={home}
          className="rounded-full px-3 py-1 text-sm transition hover:bg-white/10"
          title="Return to the free-look view"
        >
          Free look
        </button>
      </div>
    </div>
  );
}
