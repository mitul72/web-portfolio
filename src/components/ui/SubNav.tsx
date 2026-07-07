"use client";

import { STOPS } from "@/data/portfolio";
import { useTour } from "@/components/tour/useTour";
import { useVoyage } from "@/components/tour/useVoyage";

/**
 * Contextual sub-navigation: a compact quick-jump list of the current island's
 * sub-POIs (e.g. project names). Appears ONLY while docked at a hub island that
 * has sub-POIs — hidden everywhere else, so it never clutters the scene.
 * Clicking a name selects that gem and opens its panel (same as clicking the
 * gem in 3D). Sits on the left, out of the way of the panel on the right.
 */
export default function SubNav() {
  const activeIndex = useTour((s) => s.activeIndex);
  const activeSubPoiId = useTour((s) => s.activeSubPoiId);
  const selectSubPoi = useTour((s) => s.selectSubPoi);
  const phase = useVoyage((s) => s.phase);

  const stop = activeIndex === null ? null : STOPS[activeIndex];
  const subPois = stop?.subPois ?? [];

  if (subPois.length === 0 || phase !== "docked") return null;

  return (
    <div className="pointer-events-auto absolute left-4 top-1/2 z-20 -translate-y-1/2">
      <div className="flex flex-col gap-1 rounded-2xl border border-white/15 bg-slate-900/75 p-2 text-white shadow-xl backdrop-blur-xl">
        <p className="px-2 pb-1 pt-1 text-[10px] font-semibold uppercase tracking-widest text-white/40">
          {stop?.navLabel ?? "Explore"}
        </p>
        {subPois.map((poi) => (
          <button
            key={poi.id}
            onClick={() => selectSubPoi(poi.id)}
            className={`rounded-lg px-3 py-1.5 text-left text-sm font-medium transition ${
              activeSubPoiId === poi.id
                ? "bg-cyan-400/90 text-black"
                : "text-white/75 hover:bg-white/10 hover:text-white"
            }`}
          >
            {poi.label}
          </button>
        ))}
      </div>
    </div>
  );
}
