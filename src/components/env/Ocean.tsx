import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Color, Mesh, ShaderMaterial } from "three";

/**
 * Stylized "Sea of Thieves"-flavored ocean: a large plane driven by a custom
 * shader. Gerstner-ish rolling waves in the vertex stage, a depth color
 * gradient + animated foam crests + sun glitter in the fragment stage.
 *
 * No textures, no reflections — deliberately cartoon and cheap, so it stays
 * fast and matches the low-poly island.
 */
export default function Ocean({
  sunDirection = [0.4, 0.35, -1] as [number, number, number],
}) {
  const mat = useRef<ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uShallow: { value: new Color("#3fd0d6") }, // vibrant near-shore teal
      uDeep: { value: new Color("#0a4f86") }, // rich deep blue
      uFoam: { value: new Color("#eafcff") },
      uSun: { value: new Color("#fff4d6") },
      uSunDir: { value: sunDirection },
    }),
    [sunDirection]
  );

  useFrame((_, delta) => {
    if (mat.current) mat.current.uniforms.uTime.value += delta;
  });

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.2, 0]}>
      {/* Big, well-subdivided plane so waves have vertices to move. */}
      <planeGeometry args={[4000, 4000, 220, 220]} />
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

  // Sum of a few directional sine waves for a rolling swell.
  float wave(vec2 p, vec2 dir, float freq, float speed, float amp) {
    return sin(dot(p, normalize(dir)) * freq + uTime * speed) * amp;
  }

  void main() {
    vUv = uv;
    vec3 pos = position;

    float e = 0.0;
    e += wave(pos.xy, vec2(1.0, 0.3), 0.012, 0.9, 3.2);
    e += wave(pos.xy, vec2(-0.4, 1.0), 0.021, 1.1, 1.9);
    e += wave(pos.xy, vec2(0.7, -0.6), 0.045, 1.6, 0.8);
    e += wave(pos.xy, vec2(0.2, 0.9), 0.09, 2.2, 0.35);

    pos.z += e;
    vElevation = e;

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
  uniform float uTime;
  varying float vElevation;
  varying vec2 vUv;
  varying vec3 vWorldPos;

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
    float depth = smoothstep(0.0, 340.0, distToCenter);
    vec3 col = mix(uShallow, uDeep, depth);

    // Give troughs/crests contrast so the swell reads as 3D.
    float shade = clamp(vElevation * 0.06 + 0.5, 0.35, 1.0);
    col *= mix(0.82, 1.12, shade);

    // Soft foam: only on the highest crests, broken up by flowing noise.
    float flow = noise(vWorldPos.xz * 0.03 + uTime * 0.05);
    float crestMask = smoothstep(2.4, 3.6, vElevation);
    float foam = crestMask * smoothstep(0.45, 0.8, flow);
    col = mix(col, uFoam, foam);

    // Sun glitter from the wave normal (soft, not sparkly-blocky).
    vec3 nrm = normalize(vec3(-dFdx(vElevation), 1.0, -dFdy(vElevation)));
    float spec = pow(max(dot(nrm, normalize(uSunDir)), 0.0), 60.0);
    col += uSun * spec * 0.5;

    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
  }
`;
