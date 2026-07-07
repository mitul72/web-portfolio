import React, { useEffect, useRef, useState } from "react";
import OceanWaves from "../assets/audio/ocean-waves-compressed.mp3";
import soundOn from "../assets/images/soundon.png";
import soundOff from "../assets/images/soundoff.png";
import Image from "next/image";
import { useAudio } from "./env/useAudio";

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
    if (isClient && sound.current) {
      if (playing) {
        sound.current.play().catch(() => {});
      } else {
        sound.current.pause();
      }
    }
  }, [playing, isClient]);

  return (
    <div className="absolute bottom-2 left-2">
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
