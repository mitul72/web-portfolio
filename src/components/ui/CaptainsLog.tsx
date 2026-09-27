"use client";

import { useEffect, useRef, useState } from "react";
import { STOPS } from "@/data/portfolio";
import { useTour } from "@/components/tour/useTour";
import { useVoyage } from "@/components/tour/useVoyage";

/** Each stop's island, as the log names it. */
const ISLAND: Record<string, string> = {
  intro: "Home Port",
  "project-1": "Ember Isle",
  resume: "Skull Cove",
  experience: "Lighthouse Rock",
  contact: "Drifting Isle",
};

/**
 * The captain's log: how many islands you've moored at this visit ("2/5"),
 * under the name in the top-left. Opens into the list of islands, ticked off
 * as you go; an unvisited one is a click away. Each new island briefly shows
 * in the chip as it's charted, nudging you on to the rest.
 */
export default function CaptainsLog() {
  const visited = useTour((s) => s.visited);
  const activeIndex = useTour((s) => s.activeIndex);
  const goTo = useTour((s) => s.goTo);
  const sailing = useVoyage((s) => s.phase === "sailing");
  const [open, setOpen] = useState(false);
  const [charted, setCharted] = useState<string | null>(null);
  const root = useRef<HTMLDivElement>(null);
  const total = STOPS.length;
  const done = visited.length === total;

  // Flash the newest island in the chip for a moment.
  const seen = useRef(visited.length);
  useEffect(() => {
    if (visited.length <= seen.current) return;
    seen.current = visited.length;
    const id = visited[visited.length - 1];
    setCharted(ISLAND[id] ?? id);
    const t = window.setTimeout(() => setCharted(null), 2600);
    return () => window.clearTimeout(t);
  }, [visited]);

  // Close on Escape or a click anywhere else.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    const onDown = (e: PointerEvent) => {
      if (!root.current?.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("pointerdown", onDown);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("pointerdown", onDown);
    };
  }, [open]);

  return (
    <div
      ref={root}
      className="pointer-events-auto absolute left-4 top-[calc(max(1rem,env(safe-area-inset-top))_+_2.25rem)] z-30 sm:left-6 sm:top-[calc(max(1rem,env(safe-area-inset-top))_+_2.5rem)]"
    >
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label={`Captain's log: ${visited.length} of ${total} islands visited`}
        className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs text-amber-100 shadow backdrop-blur transition hover:bg-white/10 sm:text-sm ${
          charted ? "border-amber-300/70 bg-amber-400/20" : "border-amber-200/25 bg-slate-950/60"
        }`}
      >
        <span aria-hidden>📜</span>
        {charted ? (
          <span className="font-semibold">{charted} charted</span>
        ) : (
          <span>Captain&apos;s Log</span>
        )}
        <span className="font-semibold tabular-nums text-amber-300">
          {visited.length}/{total}
        </span>
      </button>

      {open && (
        <div className="mt-2 w-64 rounded-2xl border border-amber-200/25 bg-slate-950/85 p-3 text-white shadow-2xl backdrop-blur-xl">
          <div className="mb-2 h-1.5 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-amber-400 transition-all duration-500"
              style={{ width: `${(visited.length / total) * 100}%` }}
            />
          </div>
          <ol className="space-y-0.5">
            {STOPS.map((stop, i) => {
              const been = visited.includes(stop.id);
              const here = activeIndex === i;
              return (
                <li key={stop.id}>
                  <button
                    disabled={sailing || here}
                    onClick={() => {
                      setOpen(false);
                      goTo(i);
                    }}
                    className="flex w-full items-center gap-2.5 rounded-lg px-2 py-1.5 text-left transition enabled:hover:bg-white/10 disabled:cursor-default"
                  >
                    <span
                      aria-hidden
                      className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[11px] ${
                        been ? "border-amber-400 bg-amber-400 text-slate-950" : "border-white/30 text-transparent"
                      }`}
                    >
                      ✓
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className={`block text-sm ${been ? "text-white" : "text-white/70"}`}>
                        {ISLAND[stop.id] ?? stop.label}
                      </span>
                      <span className="block text-xs text-white/45">{stop.navLabel ?? stop.label}</span>
                    </span>
                    {here && <span className="text-[10px] uppercase tracking-widest text-amber-300">Here</span>}
                    <span className="sr-only">{been ? "visited" : "not visited yet"}</span>
                  </button>
                </li>
              );
            })}
          </ol>
          <p className="mt-2 border-t border-white/10 px-2 pt-2 text-xs text-white/55">
            {done
              ? "Every island charted. Fair winds, and thanks for sailing by!"
              : `${total - visited.length} ${total - visited.length === 1 ? "island" : "islands"} left to chart.`}
          </p>
        </div>
      )}
    </div>
  );
}
