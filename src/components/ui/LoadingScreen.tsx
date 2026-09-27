"use client";

import { useProgress } from "@react-three/drei";
import { useEffect, useState } from "react";
import LoadingShell from "./LoadingShell";

/**
 * Full-screen loader shown while the heavy GLB assets stream in. Fades out
 * (and unmounts) once loading completes so it never blocks interaction.
 * The markup lives in LoadingShell so page.tsx can paint it before this
 * bundle has even arrived.
 */
export default function LoadingScreen() {
  const { progress, active } = useProgress();
  const [hidden, setHidden] = useState(false);
  const done = !active && progress >= 100;

  useEffect(() => {
    if (done) {
      const t = setTimeout(() => setHidden(true), 600);
      return () => clearTimeout(t);
    }
  }, [done]);

  if (hidden) return null;
  return <LoadingShell progress={progress} fading={done} />;
}
