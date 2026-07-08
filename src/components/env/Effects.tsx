import {
  EffectComposer,
  Bloom,
  BrightnessContrast,
  HueSaturation,
  Vignette,
} from "@react-three/postprocessing";

/**
 * Cinematic post-processing. Bloom makes the sun-glitter and the emissive tour
 * markers glow; a light color grade (contrast + saturation) gives the frame a
 * filmic punch instead of flat even lighting; a soft vignette focuses the eye.
 * Kept subtle so the cartoon look stays crisp.
 */
export default function Effects() {
  // 2×MSAA: visually identical to 4× on this stylized content, half the
  // resolve cost — and the canvas's own AA is off (this buffer IS the AA).
  return (
    <EffectComposer multisampling={2}>
      <Bloom
        intensity={0.5}
        luminanceThreshold={0.85}
        luminanceSmoothing={0.2}
        mipmapBlur
      />
      {/* The grade: gentle S-curve feel. Push either past ~0.15 and it tips
          into Instagram-filter territory — resist. */}
      <BrightnessContrast contrast={0.08} />
      <HueSaturation saturation={0.12} />
      <Vignette eskil={false} offset={0.15} darkness={0.55} />
    </EffectComposer>
  );
}
