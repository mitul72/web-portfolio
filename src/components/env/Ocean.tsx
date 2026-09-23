import { useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { useTexture } from "@react-three/drei";
import { LinearFilter, MeshStandardMaterial, NoColorSpace } from "three";
import { SHORE_EXTENT, SHORE_MAX, SHORE_URL } from "@/data/world";
import { WAVE_SCALE, wavesGlsl } from "./waves";

/**
 * The sea: a MeshStandardMaterial with the swell and the shore colouring
 * injected, so it gets the same sky reflections (scene.environment), sun,
 * shadows and fog as everything else, like the Principled sea in the approved
 * Blender renders.
 *
 *  - Vertex: the shared wave field (waves.ts), damped close to shore so the
 *    swell never floods a beach.
 *  - Fragment: turquoise over the shallows and deep blue offshore, a ragged foam
 *    line on every coast plus a fainter surf line, all driven by the
 *    metres-to-shore map Blender exports (public/world/shore.png). Rippled
 *    normals break up the reflections.
 */
export default function Ocean() {
  const shore = useTexture(SHORE_URL);

  const material = useMemo(() => {
    shore.colorSpace = NoColorSpace; // distances, not colours
    shore.minFilter = LinearFilter;
    shore.generateMipmaps = false;

    const m = new MeshStandardMaterial({ roughness: 0.1, metalness: 0 });
    const uniforms = {
      uTime: { value: 0 },
      uShore: { value: shore },
      uShoreExtent: { value: SHORE_EXTENT },
      uShoreMax: { value: SHORE_MAX },
      uWaveScale: { value: WAVE_SCALE },
    };
    m.userData.uniforms = uniforms;

    m.onBeforeCompile = (shader) => {
      Object.assign(shader.uniforms, uniforms);

      shader.vertexShader = shader.vertexShader
        .replace("#include <common>", `#include <common>\n${COMMON}\n${wavesGlsl()}\nvarying vec3 vWPos;`)
        .replace(
          "#include <beginnormal_vertex>",
          /* glsl */ `
          // The plane is rotated -90deg about X: local (x, y) -> world (x, -y).
          vec2 wp = vec2(position.x, -position.y);
          // Swell fades out over the last ~25 m to shore.
          float damp = mix(0.12, 1.0, smoothstep(0.0, 25.0 / uShoreMax, shoreField(wp)));
          vec2 wg;
          float we = waves(wp, wg);
          float wamp = uWaveScale * damp;
          vec3 objectNormal = normalize(vec3(-wg.x * wamp, wg.y * wamp, 1.0));`,
        )
        .replace(
          "#include <begin_vertex>",
          /* glsl */ `
          vec3 transformed = vec3(position);
          transformed.z += we * wamp;`,
        )
        .replace(
          "#include <project_vertex>",
          `#include <project_vertex>\nvWPos = (modelMatrix * vec4(transformed, 1.0)).xyz;`,
        );

      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", `#include <common>\n${COMMON}\n${NOISE}\nvarying vec3 vWPos;`)
        .replace(
          "#include <color_fragment>",
          /* glsl */ `
          #include <color_fragment>
          vec2 sp = vWPos.xz;
          float sd = shoreField(sp) * uShoreMax; // metres to the nearest shore

          // Depth colour, the same ramp as blender/lib/materials.py sea().
          float depth = smoothstep(0.0, 70.0, sd);
          vec3 seaCol = depth < 0.25
            ? mix(vec3(0.05, 0.42, 0.38), vec3(0.02, 0.2, 0.26), depth / 0.25)
            : mix(vec3(0.02, 0.2, 0.26), vec3(0.004, 0.035, 0.07), (depth - 0.25) / 0.75);

          // Foam: ragged shoreline band + a fainter, laced surf line that
          // breathes in and out.
          float n1 = vnoise(sp * 0.25 + vec2(uTime * 0.05, -uTime * 0.03));
          float edge = sd + n1 * 4.0 + sin(uTime * 0.7 + sp.x * 0.05) * 0.6;
          float foam = 1.0 - smoothstep(2.2, 4.5, edge);
          float surf = (1.0 - smoothstep(7.5, 9.0, edge)) * smoothstep(6.0, 7.5, edge);
          float lace = smoothstep(0.45, 0.6, vnoise(sp * 1.2 + uTime * 0.1));
          foam = clamp(max(foam, surf * lace), 0.0, 1.0);

          diffuseColor.rgb = mix(seaCol, vec3(0.85, 0.88, 0.85), foam * 0.85);`,
        )
        .replace(
          "#include <roughnessmap_fragment>",
          `#include <roughnessmap_fragment>\nroughnessFactor = mix(0.1, 0.7, foam);`,
        )
        .replace(
          "#include <normal_fragment_maps>",
          /* glsl */ `
          #include <normal_fragment_maps>
          // Ripples: a long stretched swell pattern plus fine chop, as
          // finite-difference gradients of drifting noise.
          vec2 rp = vec2(sp.x * 0.5, sp.y) * 0.12 + vec2(uTime * 0.04, uTime * 0.02);
          vec2 fp = sp * 0.7 + vec2(-uTime * 0.25, uTime * 0.18);
          float e1 = 0.05;
          vec2 g1 = vec2(vnoise(rp + vec2(e1, 0.0)) - vnoise(rp - vec2(e1, 0.0)),
                         vnoise(rp + vec2(0.0, e1)) - vnoise(rp - vec2(0.0, e1))) / (2.0 * e1);
          vec2 g2 = vec2(vnoise(fp + vec2(e1, 0.0)) - vnoise(fp - vec2(e1, 0.0)),
                         vnoise(fp + vec2(0.0, e1)) - vnoise(fp - vec2(0.0, e1))) / (2.0 * e1);
          vec2 slope = g1 * 0.06 + g2 * 0.035;
          normal = normalize(normal + (viewMatrix * vec4(-slope.x, 0.0, -slope.y, 0.0)).xyz);`,
        );
    };
    m.customProgramCacheKey = () => "ocean-v2";
    return m;
  }, [shore]);

  useFrame((_, delta) => {
    material.userData.uniforms.uTime.value += delta;
  });

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow material={material}>
      {/* 20 m quads: the swell is long; shore detail lives in the fragment. */}
      <planeGeometry args={[4000, 4000, 200, 200]} />
    </mesh>
  );
}

// Shared by both stages: the metres-to-shore field (0..1 of uShoreMax; 1.0
// outside the map, i.e. open sea).
const COMMON = /* glsl */ `
uniform float uTime;
uniform sampler2D uShore;
uniform float uShoreExtent;
uniform float uShoreMax;
uniform float uWaveScale;
float shoreField(vec2 p) {
  vec2 uv = (p + uShoreExtent) / (2.0 * uShoreExtent);
  if (any(lessThan(uv, vec2(0.0))) || any(greaterThan(uv, vec2(1.0)))) return 1.0;
  return texture2D(uShore, uv).r;
}`;

const NOISE = /* glsl */ `
float hash21(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}
float vnoise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash21(i), hash21(i + vec2(1.0, 0.0)), f.x),
             mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), f.x), f.y);
}`;
