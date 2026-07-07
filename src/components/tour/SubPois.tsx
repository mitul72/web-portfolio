import { STOPS } from "@/data/portfolio";
import { useTour } from "./useTour";
import { useVoyage } from "./useVoyage";
import SubPoiMarker from "./SubPoiMarker";

/**
 * Renders the sub-POIs (message bottles) for whichever island is currently
 * active — but only once the ship has DOCKED there, so props appear as you
 * arrive rather than popping in mid-voyage. Hidden entirely at other stops.
 *
 * NOTE: select raw primitives (activeIndex/phase) — NOT a derived array — or a
 * new [] reference each render causes an infinite update loop.
 */
export default function SubPois() {
  const activeIndex = useTour((s) => s.activeIndex);
  const phase = useVoyage((s) => s.phase);

  const subPois =
    activeIndex === null ? [] : STOPS[activeIndex].subPois ?? [];

  if (subPois.length === 0 || phase !== "docked") return null;

  return (
    <>
      {subPois.map((poi) => (
        <SubPoiMarker key={poi.id} poi={poi} />
      ))}
    </>
  );
}
