import {
  EffectComposer,
  Bloom,
  BrightnessContrast,
  ToneMapping,
  Vignette,
} from "@react-three/postprocessing";
import { ToneMappingMode } from "postprocessing";

/**
 * Desktop post chain, matching the Blender look:
 *  - Bloom on the HDR frame, so only genuinely bright things glow: lit
 *    windows, lanterns, the sun's glint on the water.
 *  - AgX tone mapping LAST in HDR (the renderer itself does NOT tone map on
 *    desktop, see page.tsx), then a touch of contrast, which is what Blender's
 *    "AgX - Medium High Contrast" look adds on top of base AgX.
 *  - A soft vignette.
 * Mobile skips the composer and uses the renderer's own AgX.
 */
export default function Effects() {
  return (
    <EffectComposer multisampling={4}>
      <Bloom intensity={0.6} luminanceThreshold={1.2} luminanceSmoothing={0.3} mipmapBlur />
      <ToneMapping mode={ToneMappingMode.AGX} />
      <BrightnessContrast contrast={0.1} />
      <Vignette eskil={false} offset={0.2} darkness={0.55} />
    </EffectComposer>
  );
}
