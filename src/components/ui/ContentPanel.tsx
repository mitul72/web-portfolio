"use client";

import { STOPS, StopContent } from "@/data/portfolio";
import { useTour } from "@/components/tour/useTour";

/** Renders the body of the panel based on the active stop's content kind. */
function Body({ content }: { content: StopContent }) {
  switch (content.kind) {
    case "intro":
      return (
        <>
          <p className="text-sm uppercase tracking-widest text-amber-300">
            {content.tagline}
          </p>
          <h2 className="mt-1 text-3xl font-bold">{content.name}</h2>
          <p className="mt-4 leading-relaxed text-white/80">{content.blurb}</p>
        </>
      );

    case "resume":
      return (
        <>
          <h2 className="text-3xl font-bold">{content.title}</h2>
          <p className="mt-4 leading-relaxed text-white/80">{content.blurb}</p>
          <a
            href={content.pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-6 inline-block rounded-full bg-amber-400 px-6 py-2 font-semibold text-black transition hover:bg-amber-300"
          >
            Open Resume ↗
          </a>
        </>
      );

    case "project":
      return (
        <>
          <h2 className="text-3xl font-bold">{content.title}</h2>
          <p className="mt-4 leading-relaxed text-white/80">
            {content.description}
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {content.tech.map((t) => (
              <span
                key={t}
                className="rounded-full border border-cyan-400/40 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-200"
              >
                {t}
              </span>
            ))}
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            {content.links.map((l) => (
              <a
                key={l.url}
                href={l.url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-full border border-white/30 px-4 py-1.5 text-sm transition hover:bg-white/10"
              >
                {l.label} ↗
              </a>
            ))}
          </div>
        </>
      );

    case "experience":
      return (
        <>
          <h2 className="text-3xl font-bold">{content.title}</h2>
          {/* Island overview (no jobs of its own): point at the wisp trail. */}
          {content.jobs.length === 0 && (
            <p className="mt-4 leading-relaxed text-white/70">
              Follow the wisps — each light marks a chapter of my voyage,
              rising from the oldest at the shore to the newest at the summit.
              Click a light to read that expedition&apos;s log.
            </p>
          )}
          <div className="mt-5 space-y-6">
            {content.jobs.map((job, i) => (
              <div key={i}>
                <h3 className="text-lg font-bold leading-snug">{job.role}</h3>
                <p className="text-sm text-emerald-300">
                  {job.company} ·{" "}
                  <span className="text-white/50">{job.period}</span>
                </p>
                <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-white/75">
                  {job.bullets.map((b, j) => (
                    <li key={j}>{b}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </>
      );

    case "contact":
      return (
        <>
          <h2 className="text-3xl font-bold">{content.title}</h2>
          <p className="mt-4 leading-relaxed text-white/80">{content.blurb}</p>
          <div className="mt-6 flex flex-wrap gap-3">
            {content.links.map((l) => (
              <a
                key={l.url}
                href={l.url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-full border border-pink-400/40 bg-pink-400/10 px-4 py-1.5 text-sm text-pink-200 transition hover:bg-pink-400/20"
              >
                {l.label} ↗
              </a>
            ))}
          </div>
        </>
      );
  }
}

export default function ContentPanel() {
  const panelOpen = useTour((s) => s.panelOpen);
  const activeIndex = useTour((s) => s.activeIndex);
  const activeSubPoiId = useTour((s) => s.activeSubPoiId);
  const closePanel = useTour((s) => s.closePanel);

  // Derive content from raw primitives (stable STOPS references) — computing it
  // inside the zustand selector risks new-reference render loops.
  const stop = activeIndex === null ? null : STOPS[activeIndex];
  const content: StopContent | null = stop
    ? (activeSubPoiId
        ? stop.subPois?.find((p) => p.id === activeSubPoiId)?.content
        : null) ?? stop.content
    : null;

  const visible = panelOpen && activeIndex !== null && content !== null;

  return (
    <div
      className={`pointer-events-none absolute z-20 flex transition-all duration-500
        /* mobile: bottom sheet, full width */
        inset-x-0 bottom-0 justify-center p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]
        /* sm+: right-side full-height panel */
        sm:inset-y-0 sm:right-0 sm:left-auto sm:h-full sm:items-center sm:p-8 ${
          visible
            ? "translate-y-0 opacity-100 sm:translate-x-0"
            : "translate-y-8 opacity-0 sm:translate-y-0 sm:translate-x-8"
        }`}
      aria-hidden={!visible}
    >
      {content && (
        // When hidden, the sheet must NOT take pointer events — it still spans
        // the bottom of the screen (mobile) and would swallow taps meant for
        // the nav bar underneath.
        <div
          className={`${
            visible ? "pointer-events-auto" : "pointer-events-none"
          } max-h-[65vh] w-full overflow-y-auto rounded-2xl border border-white/15 bg-slate-900/85 p-5 text-white shadow-2xl backdrop-blur-xl sm:max-h-[80vh] sm:w-[min(92vw,26rem)] sm:p-8`}
        >
          <button
            onClick={closePanel}
            aria-label="Close"
            className="absolute right-3 top-3 flex h-9 w-9 items-center justify-center rounded-full border border-white/20 text-white/70 transition hover:bg-white/10 hover:text-white sm:right-4 sm:top-4 sm:h-8 sm:w-8"
          >
            ✕
          </button>
          <Body content={content} />
        </div>
      )}
    </div>
  );
}
