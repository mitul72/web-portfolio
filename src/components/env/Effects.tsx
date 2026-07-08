import {
  EffectComposer,
  Bloom,
  BrightnessContrast,
  HueSaturation,
  Vignette,
  GodRays,
} from "@react-three/postprocessing";
import { BlendFunction, KernelSize } from "postprocessing";
import { Mesh } from "three";

/**
 * Cinematic post-processing for the golden-hour look:
 *  - GodRays: volumetric light shafts streaming from the sun disc (the money
 *    shot). Traced from the passed-in sun mesh; skipped if none provided.
 *  - Bloom: sun glow + emissive markers.
 *  - Warm color grade (contrast + saturation) for a filmic, photographed feel.
 *  - Vignette to focus the eye.
 *
 * Desktop-only (mounted behind !isMobile in page.tsx) — the fullscreen god-ray
 * + composer passes are too costly on phones, which keep the cheaper flat look.
 */
export default function Effects({ sun }: { sun?: Mesh | null }) {
  // multisampling MUST be 0 when GodRays is present: MSAA allocates a
  // multisampled depth/stencil buffer, and GodRays' depth blit into it throws
  // "glBlitFramebuffer: Depth/stencil format combination not allowed" every
  // frame — which stalls the render loop (froze the voyage/camera → "nav
  // broken"). Bloom's mipmap blur + the god-ray blur keep edges soft enough
  // that dropping MSAA is invisible on this stylized content.
  return (
    <EffectComposer multisampling={0}>
      {/* God rays FIRST so bloom/grade apply on top of the shafts. */}
      {sun ? (
        <GodRays
          sun={sun}
          blendFunction={BlendFunction.SCREEN}
          samples={60}
          density={0.92}
          decay={0.9}
          // Softer weight/exposure + a clamp well under 1 so the shafts read as
          // gentle atmospheric haze and can't bloom bright enough to bleed over
          // foreground islands/buildings (the "sun through the tavern" look).
          weight={0.3}
          exposure={0.32}
          clampMax={0.65}
          kernelSize={KernelSize.SMALL}
          blur
        />
      ) : (
        <></>
      )}
      <Bloom
        intensity={0.55}
        luminanceThreshold={0.8}
        luminanceSmoothing={0.2}
        mipmapBlur
      />
      {/* Warm golden-hour grade: gentle contrast + saturation + a touch of
          warmth. Past ~0.15 it tips into Instagram-filter territory. */}
      <BrightnessContrast contrast={0.09} brightness={0.01} />
      <HueSaturation saturation={0.14} />
      <Vignette eskil={false} offset={0.15} darkness={0.6} />
    </EffectComposer>
  );
}
