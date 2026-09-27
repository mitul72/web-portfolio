"use client";

import dynamic from "next/dynamic";
import LoadingShell from "@/components/ui/LoadingShell";

// The 3D world (three.js, drei, postprocessing, gsap: a third of a megabyte
// of JS) is its own chunk, so the loading screen paints from the small page
// bundle instead of waiting for all of that. No SSR: the scene is WebGL-only
// and its overlays read client-side stores.
const Experience = dynamic(() => import("@/components/Experience"), {
  ssr: false,
  loading: () => <LoadingShell progress={0} />,
});

export default function Home() {
  return <Experience />;
}
