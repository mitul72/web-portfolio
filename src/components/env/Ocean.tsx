import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Color, Mesh, ShaderMaterial } from "three";
import { SUN_DIRECTION, SUN_COLOR, FOG_COLOR, FOG_DENSITY } from "./sky";

/**
 * Stylized "Sea of Thieves"-flavored ocean: a large plane driven by a custom
 * shader. Gerstner-ish rolling waves in the vertex stage, a depth color
 * gradient + animated foam crests + sun glitter in the fragment stage, and a
 * manual FogExp2 fade (custom ShaderMaterials ignore scene.fog — without this
 * the water stays saturated to the horizon and ends in a hard seam against
 * the sky, which reads as "weird ocean").
 *
 * No textures, no reflections — deliberately cartoon and cheap, so it stays
 * fast and matches the low-poly island.
 */
export default function Ocean({
  sunDirection = SUN_DIRECTION,
}: {
  sunDirection?: [number, number, number];
}) {
  const mat = useRef<ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uShallow: { value: new Color("#3fb8bf") }, // near-shore teal, warmed slightly toward the sun
      uDeep: { value: new Color("#134f7e") }, // deep blue, a touch warmer/darker for dusk
      uFoam: { value: new Color("#fff0dc") }, // foam picks up warm sunset light
      uSun: { value: new Color(SUN_COLOR) }, // glitter matches the golden sun
      uSunDir: { value: sunDirection },
      // Mirror of the scene fog (see sky.ts) — keep in sync.
      uFogColor: { value: new Color(FOG_COLOR) },
      uFogDensity: { value: FOG_DENSITY },
    }),
    [sunDirection]
  );

  useFrame((_, delta) => {
    if (mat.current) mat.current.uniforms.uTime.value += delta;
  });

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.2, 0]}>
      {/* Big subdivided plane for the swell. 160² is enough: the two smallest
          chop waves are carried by the ANALYTIC normals + fragment ripples,
          not by geometry, so coarser tessellation doesn't lose shading detail
          (~51k tris vs ~97k at 220²). */}
      <planeGeometry args={[4000, 4000, 160, 160]} />
      <shaderMaterial
        ref={mat}
        uniforms={uniforms}
        vertexShader={vertex}
        fragmentShader={fragment}
      />
    </mesh>
  );
}

const vertex = /* glsl */ `
  uniform float uTime;
  varying float vElevation;
  varying vec2 vUv;
  varying vec3 vWorldPos;
  varying vec3 vNormalW;

  // Sum of directional sine waves — MIRRORED in env/waves.ts so the ship and
  // wake ride this exact surface. Add/change a wave in BOTH places.
  // Also accumulates the analytic gradient for a true surface normal.
  float wave(vec2 p, vec2 dir, float freq, float speed, float amp, inout vec2 grad) {
    vec2 d = normalize(dir);
    float arg = dot(p, d) * freq + uTime * speed;
    grad += cos(arg) * amp * freq * d;
    return sin(arg) * amp;
  }

  void main() {
    vUv = uv;
    vec3 pos = position;

    float e = 0.0;
    vec2 g = vec2(0.0);
    e += wave(pos.xy, vec2(1.0, 0.3), 0.012, 0.9, 3.2, g);
    e += wave(pos.xy, vec2(-0.4, 1.0), 0.021, 1.1, 1.9, g);
    e += wave(pos.xy, vec2(0.7, -0.6), 0.045, 1.6, 0.8, g);
    e += wave(pos.xy, vec2(0.2, 0.9), 0.09, 2.2, 0.35, g);
    e += wave(pos.xy, vec2(-0.85, 0.4), 0.15, 3.1, 0.18, g);
    e += wave(pos.xy, vec2(0.55, 0.75), 0.22, 3.8, 0.10, g);

    pos.z += e;
    vElevation = e;
    // Macro swell normal (world-ish space; plane local xy spans the sea).
    vNormalW = normalize(vec3(-g.x, 1.0, -g.y));

    vec4 world = modelMatrix * vec4(pos, 1.0);
    vWorldPos = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

const fragment = /* glsl */ `
  uniform vec3 uShallow;
  uniform vec3 uDeep;
  uniform vec3 uFoam;
  uniform vec3 uSun;
  uniform vec3 uSunDir;
  uniform vec3 uFogColor;
  uniform float uFogDensity;
  uniform float uTime;
  varying float vElevation;
  varying vec2 vUv;
  varying vec3 vWorldPos;
  varying vec3 vNormalW;

  // Smooth value noise (no grid-aligned blockiness).
  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }
  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }

  void main() {
    // Depth color: teal near the island, deep blue far out.
    float distToCenter = length(vWorldPos.xz);
    float depth = smoothstep(0.0, 320.0, distToCenter);
    vec3 col = mix(uShallow, uDeep, depth);

    // Large-scale tonal variation: slow drifting "current" patches so the
    // shallows aren't one flat cyan field (the #1 "toy water" tell). Strongest
    // near shore where the flat teal dominates, fades out over deep water.
    float patchN = noise(vWorldPos.xz * 0.004 + uTime * 0.01);
    col = mix(col, uDeep, (1.0 - depth) * patchN * 0.22);

    // --- Surface normal: macro swell (analytic, from the vertex waves) plus
    // fragment-only micro-ripples. The ripples never touch the height field,
    // so the ship/wake sync with waves.ts is untouched.
    vec2 rp = vWorldPos.xz * 0.14 + vec2(uTime * 0.35, -uTime * 0.22);
    float r1 = noise(rp);
    float r2 = noise(rp + vec2(37.2, 17.9) - uTime * 0.13);
    vec3 n = normalize(vNormalW + vec3(r1 - 0.5, 0.0, r2 - 0.5) * 0.35);

    // Soft sun shading over the swell (wrap lighting keeps troughs readable).
    vec3 L = normalize(uSunDir);
    float ndl = clamp(dot(n, L) * 0.5 + 0.5, 0.0, 1.0);
    col *= mix(0.8, 1.12, ndl);

    // Fresnel: grazing angles pick up the sky — the biggest "reads as real
    // water" cue. Sky tint = fog color, so the horizon stays coherent.
    vec3 V = normalize(cameraPosition - vWorldPos);
    float fres = pow(1.0 - max(dot(n, V), 0.0), 3.0);
    col = mix(col, uFogColor, fres * 0.55);

    // Soft foam: only the very highest crests, broken by flowing noise, and
    // never fully white — big bright blobs read as "clouds on water".
    float flow = noise(vWorldPos.xz * 0.03 + uTime * 0.05);
    float crestMask = smoothstep(2.8, 4.0, vElevation);
    col = mix(col, uFoam, crestMask * smoothstep(0.5, 0.85, flow) * 0.7);

    // Sun glitter: true reflection alignment off the rippled normal — a
    // moving sparkle path toward the sun instead of broad sheen.
    float spec = pow(max(dot(reflect(-L, n), V), 0.0), 140.0);
    col += uSun * spec * 0.8;

    // Manual FogExp2, matching scene.fog (custom shaders don't get it free).
    // This is what melts the water into the sky instead of a hard horizon.
    float fogDist = distance(vWorldPos, cameraPosition);
    float fogFactor = 1.0 - exp(-uFogDensity * uFogDensity * fogDist * fogDist);
    col = mix(col, uFogColor, fogFactor);

    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
  }
`;
