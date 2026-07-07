import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";

/**
 * Cinematic post-processing. Bloom makes the sun-glitter and the emissive tour
 * markers glow; a soft vignette focuses the eye on the island. Kept subtle so
 * the cartoon look stays crisp.
 */
export default function Effects() {
  return (
    <EffectComposer multisampling={4}>
      <Bloom
        intensity={0.5}
        luminanceThreshold={0.85}
        luminanceSmoothing={0.2}
        mipmapBlur
      />
      <Vignette eskil={false} offset={0.15} darkness={0.55} />
    </EffectComposer>
  );
}
