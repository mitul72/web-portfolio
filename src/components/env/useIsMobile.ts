import { useEffect, useState } from "react";

/**
 * True on small / touch screens. Used to scale back GPU-heavy rendering
 * (device pixel ratio, shadows, postprocessing) and to switch overlays to
 * mobile layouts. SSR-safe: starts false, resolves on mount.
 */
export function useIsMobile(breakpoint = 640) {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${breakpoint}px)`);
    const update = () => setIsMobile(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, [breakpoint]);

  return isMobile;
}
