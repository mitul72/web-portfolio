"use client";

import Image from "next/image";
import soundOn from "@/assets/images/soundon.png";
import soundOff from "@/assets/images/soundoff.png";
import { useTour } from "@/components/tour/useTour";
import { useAudio } from "@/components/env/useAudio";

/**
 * Lightweight top overlay: the name/brand doubles as a "return home" button,
 * with the sound toggle on the right (the bottom corners are owned by the nav
 * bar / panel on mobile). Section navigation lives in the bottom TourControls
 * bar, so the header stays minimal — important on small screens.
 */
export default function Navbar() {
  const home = useTour((s) => s.home);
  const muted = useAudio((s) => s.muted);
  const toggle = useAudio((s) => s.toggle);

  return (
    <header className="pointer-events-none absolute inset-x-0 top-0 z-30 flex items-center justify-between px-4 pt-[max(1rem,env(safe-area-inset-top))] sm:px-6">
      <button
        onClick={home}
        className="pointer-events-auto text-base font-bold tracking-tight text-white drop-shadow sm:text-lg"
      >
        ⚓ Mitul Dhawan
      </button>
      {/* Mobile-only: on sm+ the toggle sits bottom-left (BackgroundMusic). */}
      <button
        onClick={toggle}
        aria-label={muted ? "Unmute sound" : "Mute sound"}
        className="pointer-events-auto flex h-10 w-10 items-center justify-center rounded-full border border-white/15 bg-slate-900/50 shadow backdrop-blur transition hover:bg-white/10 sm:hidden"
      >
        <Image
          src={muted ? soundOff : soundOn}
          width={22}
          height={22}
          alt=""
          priority
          className="object-contain"
        />
      </button>
    </header>
  );
}
