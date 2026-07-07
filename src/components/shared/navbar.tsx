"use client";

import { useTour } from "@/components/tour/useTour";

/**
 * Lightweight top overlay: the name/brand doubles as a "return home" button.
 * Section navigation (incl. Resume) lives in the bottom TourControls bar, so
 * the header stays minimal — important on small screens.
 */
export default function Navbar() {
  const home = useTour((s) => s.home);

  return (
    <header className="pointer-events-none absolute inset-x-0 top-0 z-30 flex items-center justify-between px-4 pt-[max(1rem,env(safe-area-inset-top))] sm:px-6">
      <button
        onClick={home}
        className="pointer-events-auto text-base font-bold tracking-tight text-white drop-shadow sm:text-lg"
      >
        ⚓ Mitul Dhawan
      </button>
    </header>
  );
}
