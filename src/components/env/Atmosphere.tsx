import { Environment } from "@react-three/drei";
import { SKY_URL } from "@/data/world";

/**
 * The sky: the golden-hour panorama rendered from the same Blender world the
 * approved island renders used (sky model, sun disc, painted clouds), shown
 * as the background AND used as the image-based light for every material, so
 * shadowed faces pick up the sky's blue and the sea reflects its clouds.
 */
export default function Atmosphere() {
  return <Environment files={SKY_URL} background />;
}
