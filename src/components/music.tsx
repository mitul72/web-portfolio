import { useEffect, useRef, useState } from "react";
import OceanWaves from "../assets/audio/ocean-waves-compressed.mp3";
import soundOn from "../assets/images/soundon.png";
import soundOff from "../assets/images/soundoff.png";
import Image from "next/image";
import { useAudio } from "./env/useAudio";

/**
 * Ambient ocean loop + the desktop mute toggle (bottom-left). On mobile the
 * toggle is hidden: the bottom corners are covered by the nav bar / panel
 * there, so the Navbar renders its own header toggle instead.
 */
export default function BackgroundMusic() {
  const [isClient, setIsClient] = useState(false); // Track if running in the client
  const sound = useRef<HTMLAudioElement | null>(null); // Reference for the sound
  // Shared mute flag so this toggle also governs the voyage SFX.
  const muted = useAudio((s) => s.muted);
  const toggle = useAudio((s) => s.toggle);
  const playing = !muted;

  useEffect(() => {
    setIsClient(true); // Set this after the component has mounted on the client side
  }, []);

  useEffect(() => {
    if (isClient && !sound.current) {
      // Only create the Audio object on the client side
      sound.current = new Audio(OceanWaves);
      sound.current.loop = true; // Enable looping
      sound.current.volume = 0.4; // Adjust volume
    }
  }, [isClient]);

  useEffect(() => {
    const audio = sound.current;
    if (!isClient || !audio) return;
    if (!playing) {
      audio.pause();
      return;
    }
    // Autoplay with sound is usually refused before the visitor interacts.
    // If so, start on their first click, tap or key instead.
    const events = ["pointerdown", "keydown", "touchstart"] as const;
    const retry = () => {
      events.forEach((e) => window.removeEventListener(e, retry));
      if (!useAudio.getState().muted) audio.play().catch(() => {});
    };
    audio.play().catch(() => {
      events.forEach((e) => window.addEventListener(e, retry, { once: true }));
    });
    return () => events.forEach((e) => window.removeEventListener(e, retry));
  }, [playing, isClient]);

  return (
    <div className="absolute bottom-2 left-2 hidden sm:block">
      <Image
        src={playing ? soundOn : soundOff}
        width={50}
        height={50}
        alt="sound"
        priority
        onClick={toggle}
        className="cursor-pointer object-contain"
      />
    </div>
  );
}
