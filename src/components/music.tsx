import React, { useEffect, useRef, useState } from "react";
import OceanWaves from "../assets/audio/ocean-waves-compressed.mp3";
import soundOn from "../assets/images/soundon.png";
import soundOff from "../assets/images/soundoff.png";
import Image from "next/image";

export default function BackgroundMusic() {
  const [isPlaying, setIsPlaying] = useState(false); // Track the play state
  const [isClient, setIsClient] = useState(false); // Track if running in the client
  const sound = useRef<HTMLAudioElement | null>(null); // Reference for the sound

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
      if (isPlaying) {
        sound.current.play();
      } else {
        sound.current.pause();
      }
    }
  }, [isPlaying, isClient]);

  return (
    <div className="absolute bottom-2 left-2">
      <Image
        src={isPlaying ? soundOn : soundOff}
        width={50}
        height={50}
        alt="sound"
        priority
        onClick={() => {
          setIsPlaying(!isPlaying);
        }}
        className="cursor-pointer object-contain"
      />
    </div>
  );
}
