"use client";

import { ContactContent } from "@/data/portfolio";

/**
 * The contact "panel": a near-fullscreen unfurled pirate map (parchment texture
 * extracted from pirate_map.glb → /pirate-map.webp). The social links are
 * X-marked destinations ON the map, joined by a dashed ink route. Opened by
 * arriving at the socials island or clicking its message-in-a-bottle.
 */

/** Where each link's ✕ sits on the parchment, in % of the map's size. */
const SPOTS = [
  { x: 24, y: 46 },
  { x: 50, y: 66 },
  { x: 74, y: 38 },
  { x: 62, y: 22 }, // spare, in case a 4th link is added
];

export default function TreasureMap({
  content,
  open,
  onClose,
}: {
  content: ContactContent;
  open: boolean;
  onClose: () => void;
}) {
  const spots = content.links.map((l, i) => ({
    ...l,
    ...SPOTS[i % SPOTS.length],
  }));

  return (
    <div
      className={`absolute inset-0 z-30 flex items-center justify-center p-3 transition-all duration-500 sm:p-10 ${
        open ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
      }`}
      aria-hidden={!open}
    >
      {/* Dimmed sea behind the map; click to close. */}
      <div className="absolute inset-0 bg-slate-950/60" onClick={onClose} />

      {/* The parchment. */}
      <div
        className={`relative aspect-[4/3] max-h-full w-full max-w-4xl transition-transform duration-500 ${
          open ? "scale-100 rotate-0" : "scale-90 -rotate-2"
        }`}
        style={{
          backgroundImage: "url(/pirate-map.webp)",
          backgroundSize: "100% 100%",
          filter: "drop-shadow(0 16px 48px rgba(0,0,0,0.55))",
        }}
      >
        {/* Dashed ink route joining the marks. */}
        <svg
          className="pointer-events-none absolute inset-0 h-full w-full"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
        >
          <polyline
            points={spots.map((s) => `${s.x},${s.y}`).join(" ")}
            fill="none"
            stroke="#7a2e1d"
            strokeWidth="0.6"
            strokeDasharray="2 2"
            opacity="0.75"
          />
        </svg>

        {/* Title cartouche. */}
        <div className="absolute inset-x-0 top-[7%] text-center">
          <h2 className="text-xl font-black tracking-wide text-[#3b2a15] sm:text-3xl">
            {content.title}
          </h2>
          <p className="mx-auto mt-1 max-w-md px-8 text-xs italic text-[#5c4326] sm:text-sm">
            {content.blurb}
          </p>
        </div>

        {/* X marks the socials. */}
        {spots.map((s) => (
          <a
            key={s.url}
            href={s.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group absolute -translate-x-1/2 -translate-y-1/2 text-center"
            style={{ left: `${s.x}%`, top: `${s.y}%` }}
          >
            <span className="block text-3xl font-black leading-none text-[#8c2a18] transition-transform duration-200 group-hover:scale-125 sm:text-4xl">
              ✕
            </span>
            <span className="mt-0.5 block text-sm font-bold text-[#3b2a15] underline decoration-dashed decoration-[#8c2a18]/60 underline-offset-4 transition group-hover:text-[#8c2a18] sm:text-base">
              {s.label}
            </span>
          </a>
        ))}

        {/* Compass rose flourish. */}
        <div className="absolute bottom-[8%] right-[7%] select-none text-2xl text-[#5c4326]/80 sm:text-4xl">
          🧭
        </div>

        {/* Close — a wax-seal button on the map's corner. */}
        <button
          onClick={onClose}
          aria-label="Close map"
          className="absolute right-[4%] top-[6%] flex h-10 w-10 items-center justify-center rounded-full bg-[#8c2a18] text-lg font-bold text-amber-100 shadow-lg transition hover:scale-110"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
