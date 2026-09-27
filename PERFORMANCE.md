# Performance audit — room for improvement

> **Status (2026-09-26):** re-audited after the AAA rewrite (PR #1), which had
> quietly undone most of the 2026-07-08 fixes listed below. Now in place; the
> asset side is reproducible with `npm run assets` (`scripts/optimize-assets.mjs`).
>
> | | before | after |
> |---|---|---|
> | Hidden second scene render: the chest's gems had `KHR_materials_transmission` 0.1, so three redrew every opaque object each frame as the refraction source (full-res, 4x MSAA, never culled) | every frame | stripped from the GLB; guarded in `treasure-chest.tsx` |
> | Shadow map (`Lighting.tsx`, `Experience.tsx`) | 4096² PCFSoft | 2048² PCF |
> | Composer MSAA (`Effects.tsx`) | 4x | 2x |
> | Ocean (`Ocean.tsx`): grid / ripple gradients | 200² (80k tris) / 8 noise taps per pixel | 160² (51k) / 2 analytic |
> | World albedos, 13 maps (`world-transformed.glb`) | WebP: ~224 MB GPU, decoded on the main thread | ETC1S KTX2 q160: ~28 MB GPU, transcoded in a worker; GLB 3.1 -> 5.6 MB (ETC1S is ~1 bpp, lossy WebP ~0.5) |
> | Shore field (`public/world/shore.png`) | 2048² RGB, 871 KB, 16.8 MB GPU | 1024² single channel, 209 KB, 4.2 MB GPU |
> | NPC GLBs (6) | 2.2 MB, 14 clips each, captain atlas 1024² | 0.84 MB, Idle/Wave/Yes only, atlas 32² (exact per-cell colours) |
> | Chest | 44.6k tris, 472 KB | 22.2k tris, 385 KB |
> | Draco / Basis decoders | Google CDN (drei default) | `public/draco`, `public/basis` (`models/loaders.ts`) |
> | "/" first-load JS | 422 kB, loader waits for three.js | 89 kB shell; the 3D chunk loads behind `LoadingShell` |
> | Fonts | 2 x WOFF, 130 KB | WOFF2, 110 KB |
> | Dead weight | 4 unreferenced GLBs (8.7 MB in git), 7 unused npm deps | removed |
> | `Wake.tsx` | rebuilt 40 instance matrices every frame | skips frames with nothing alive |
>
> Still open: full quality tiers (E1 beyond the adaptive dpr), the chest's 16
> small textures (not flat, so nothing folded; KTX2 would need the loader
> extension on the chest too), sky.hdr resolution. Original audit follows.

Goal: smooth (55–60fps) on **integrated GPUs** (Intel Iris Xe / AMD Vega iGPU
class), not just discrete cards. Findings ordered by expected impact. iGPUs are
almost always **fill-rate bound** (pixels × shader cost), so the top section is
where the frames are.

Current per-frame GPU work at a glance: a 2048² shadow map re-rendered every
frame + the main pass at up to `dpr 2` + a 4×MSAA postprocessing chain +
~97k-triangle animated ocean + ~69k-triangle fully-skinned treasure island.

---

## A. Fill rate — the iGPU killers

### A1. Device pixel ratio up to 2 on desktop
`page.tsx` — `dpr={isMobile ? [1, 1.5] : [1, 2]}`.
On a 1440p/4K laptop screen an iGPU renders 4× the pixels of dpr 1, then the
bloom chain resamples them again. This is the single biggest lever.
- Cap desktop dpr at ~1.5, **or** better: make it adaptive (see E1).

### A2. Double antialiasing: canvas MSAA + composer MSAA
`page.tsx` sets `gl={{ antialias: !isMobile }}` **and** `Effects.tsx` sets
`<EffectComposer multisampling={4}>`. When the composer is mounted it renders
into its own MSAA framebuffer — the canvas's own AA buffer is dead weight that
still costs memory/bandwidth.
- When `Effects` is on: `antialias: false` on the canvas.
- Drop `multisampling` to 2 (or 0 on weak GPUs — bloom's mipmap blur already
  softens edges; the art style is forgiving).

### A3. Shadow pipeline: 2048² PCFSoft map, redrawn every frame, everything casts
`Lighting.tsx` (2048² map) + every island's `traverse` marks **all** meshes
`castShadow + receiveShadow` (pirate-island.tsx, volcano-island.tsx,
treasure-island.tsx). Because the scene animates, three.js re-renders the whole
shadow depth pass each frame.
- The shadow camera only covers ±120 around the origin — the volcano (x≈-300)
  and treasure island are *outside it* and can never show their shadows. Their
  meshes still get shadow-pass work. Stop marking landmass meshes `castShadow`;
  let them only `receiveShadow` (hero meshes — ship, crew, props — keep
  casting).
- 1024² is plenty at this art style; make map size part of the quality tier
  (E1).
- If a stop's framing ever leaves the ±120 box, shadows pop off anyway — so
  nothing is lost by keeping the box tight and the caster list short.

### A4. Ocean tessellation
`Ocean.tsx` — `planeGeometry args={[4000, 4000, 220, 220]}` = **96,800
triangles** re-transformed every frame for a plane that is mostly fog-faded
horizon. The swell detail lives in the first ~500 units around the islands.
- 128×128 (~32k tris) is visually indistinguishable at this wave scale; 96×96
  for the low tier. (Optional finer move: two rings — a dense small plane near
  the islands, a coarse skirt to the horizon.)
- The fragment shader is cheap (good) — keep it; the vertex count is the cost.

---

## B. Geometry & assets doing invisible work

### B1. Treasure island ships its own ocean + a 24k-tri coin pile (`treasure-island-transformed.glb`, 2.7MB)
`gltf-transform inspect` findings:
- **`ocean_ocean_0` — 7,040 triangles of baked water** rendered *under* the
  custom `<Ocean/>` shader. Pure waste (draw + shadow pass + skinning: it even
  carries JOINTS/WEIGHTS). Remove the mesh from the GLB
  (`gltf-transform prune` after deleting the node, or re-export).
- **`treasure chest_individual coins_0` — 23,876 tris**, and the chest is
  17,514 — together over half the island's ~69k tris, all **skinned** (GPU
  skinning per frame even while the animation is paused). `gltf-transform
  simplify` the coins/chest to ~25–35% — at portfolio camera distance it's
  invisible.
- Every mesh carries `TANGENT:f32` (4 floats/vertex) — only needed for normal
  maps; strip with `gltf-transform prune --keep-attributes` tuning or
  `--simplify` pipeline. Fat vertices = upload time + memory bandwidth.

### B2. `ship_custom.glb` (941KB) is downloaded for ONE material
`pirate-island.tsx` loads the whole second GLB but uses only
`shipMaterials["Atlas.003"]` — the ship *geometry* comes from the island GLB.
Extract that material's texture into the island GLB (or a tiny standalone
`.glb` with just the material) and delete the rest: **~900KB off the critical
loading path** plus its GPU textures.

### B3. Texture GPU memory: WebP decodes to raw RGBA
Each 512² texture = **1.4MB GPU** (the inspect's `gpuSize`), and the treasure
island alone has ~9 of them; WebP/PNG must also be decoded + uploaded on the
main thread at load. Converting to **KTX2/BasisU** (`gltf-transform etc1s`)
keeps textures compressed *on the GPU* (~6–8× less memory, faster uploads,
fewer upload jank spikes on iGPUs that share system RAM).

---

## C. Per-frame JS (minor, but free wins)

- **`Seagulls.tsx`** — `path.getPointAt(t)` and `getPointAt(t + 0.01)` allocate
  **2 new `Vector3` per gull per frame** (8/frame, ~480/s → GC churn). Pass
  scratch vectors: `path.getPointAt(t, scratch)` (FloatingVessel already does
  this).
- **`useVoyage.sailTo`** — the gsap `onUpdate` calls `set({ progress })` 60×/s
  while sailing; every store subscriber (SailingSfx, CameraRig, pirate-island,
  treasure-island phase-watchers) runs its callback each tick just to compare
  `phase`. Harmless at this scale — but if subscribers grow, publish `progress`
  the same way as `shipPos` (mutate, don't `set`).
- **`Wake.tsx` / `CameraRig.tsx` / `FloatingVessel.tsx`** — already allocation
  -free in `useFrame`. Keep it that way (it's the codebase convention).

---

## D. Load path

- Total GLB payload ≈ **5.2MB**: treasure 2.7MB (B1), captain_ship_island
  1.0MB, ship_custom 0.94MB (B2), volcano 0.36MB, fantasy 0.2MB. B1+B2 alone
  roughly halve it.
- All GLBs are `useGLTF.preload`ed eagerly — right call for a single-page
  experience; just make the payloads small.
- `Atmosphere.tsx` clouds (`segments={40}` + `{30}`) build 70 volumetric
  sprites at mount — fine, but halve segments in the low tier.

---

## E. Strategy: measure capability, don't sniff screen width

### E1. The core gap: `useIsMobile` gates quality by *viewport width*
A weak iGPU laptop gets **max settings** (dpr 2, shadows, 4×MSAA bloom) because
its window is wide; an iPhone 15 Pro gets minimum. Replace the boolean with a
small **quality tier** (`high | medium | low`) in a store, defaulted by width
but *corrected at runtime* by measured fps:

- drei's **`<PerformanceMonitor>`** (wraps the scene, `onDecline` → drop tier,
  `onIncline` → raise) — a few lines, exactly this use case.
- Optionally add drei's **`<AdaptiveDpr pixelated />`** for automatic dpr
  scaling during regressions.

One tier flag then drives everything already conditional today, plus the new
knobs: dpr ceiling (A1), composer on/off + multisampling (A2), shadow map size
/ shadows off (A3), ocean segments (A4), cloud segments (D).

### E2. How to verify (before/after)
- `r3f-perf` (dev-only `<Perf/>`) for draw calls, tris, fps, GPU ms.
- Chrome DevTools → Rendering → Frame Rendering Stats; run with
  `chrome://flags` forcing ANGLE on the iGPU, or on battery (many laptops pin
  to iGPU on battery — that IS the target user).
- Sanity targets after the fixes: **< 150k tris total, < 60 draw calls, dpr
  ≤ 1.5, one 1024² shadow map, composer ≤ 2×MSAA.**

---

## Suggested order of attack

1. E1 quality tiers + A1 dpr cap (biggest win, unlocks everything else)
2. A2 kill double-AA, A3 shadow diet (config-only, ~1 hour)
3. A4 ocean segments (one number)
4. B1 re-process treasure GLB, B2 drop ship_custom (asset work, halves payload)
5. C seagull scratch vectors (5 min)
6. B3 KTX2 textures (nice-to-have, do last)
