# Graph Report - web-portfolio  (2026-09-09)

## Corpus Check
- 38 files · ~20,801 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 293 nodes · 372 edges · 43 communities (16 shown, 27 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6258ee25`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_2D Lite Page & Island Models|2D Lite Page & Island Models]]
- [[_COMMUNITY_Scene Roots & Markers|Scene Roots & Markers]]
- [[_COMMUNITY_Architecture Concepts|Architecture Concepts]]
- [[_COMMUNITY_Dev Dependencies & Config|Dev Dependencies & Config]]
- [[_COMMUNITY_Runtime Dependencies|Runtime Dependencies]]
- [[_COMMUNITY_Portfolio Content & Resume|Portfolio Content & Resume]]
- [[_COMMUNITY_TypeScript Config|TypeScript Config]]
- [[_COMMUNITY_shadcnui Config|shadcn/ui Config]]
- [[_COMMUNITY_Pirate Treasure Map|Pirate Treasure Map]]
- [[_COMMUNITY_Sub-POI Props (GemCrateFlag)|Sub-POI Props (Gem/Crate/Flag)]]
- [[_COMMUNITY_Content Panel & Treasure Map View|Content Panel & Treasure Map View]]
- [[_COMMUNITY_App Layout & Fonts|App Layout & Fonts]]
- [[_COMMUNITY_ESLint Config|ESLint Config]]
- [[_COMMUNITY_Next.js Webpack Config|Next.js Webpack Config]]
- [[_COMMUNITY_PostCSS Config|PostCSS Config]]
- [[_COMMUNITY_Sound Toggle Icons|Sound Toggle Icons]]
- [[_COMMUNITY_Tailwind Config|Tailwind Config]]
- [[_COMMUNITY_Performance audit — room for improvement|Performance audit — room for improvement]]
- [[_COMMUNITY_CLAUDE|CLAUDE.md]]
- [[_COMMUNITY_Pirate Portfolio 🏴‍☠️|Pirate Portfolio 🏴‍☠️]]
- [[_COMMUNITY_Asset Optimization Pipeline (gltf-transform)|Asset Optimization Pipeline (gltf-transform)]]
- [[_COMMUNITY_CameraRig|CameraRig]]
- [[_COMMUNITY_DevCoords|DevCoords]]
- [[_COMMUNITY_FloatingVessel|FloatingVessel]]
- [[_COMMUNITY_Ocean Shader|Ocean Shader]]
- [[_COMMUNITY_Sailing Flow|Sailing Flow]]
- [[_COMMUNITY_sky.ts SunFog Source|sky.ts Sun/Fog Source]]
- [[_COMMUNITY_State-Store Bridge|State-Store Bridge]]
- [[_COMMUNITY_Tour Stops (STOPS  PLANNED_STOPS)|Tour Stops (STOPS / PLANNED_STOPS)]]
- [[_COMMUNITY_useAudio Store|useAudio Store]]
- [[_COMMUNITY_useTour Store|useTour Store]]
- [[_COMMUNITY_useVoyage Store|useVoyage Store]]
- [[_COMMUNITY_waves.ts Wave Sampling|waves.ts Wave Sampling]]
- [[_COMMUNITY_Zustand State Management|Zustand State Management]]
- [[_COMMUNITY_Allocation-Free useFrame Convention|Allocation-Free useFrame Convention]]
- [[_COMMUNITY_iGPU Fill-Rate Bottleneck|iGPU Fill-Rate Bottleneck]]
- [[_COMMUNITY_KTX2BasisU Texture Compression|KTX2/BasisU Texture Compression]]
- [[_COMMUNITY_Quality Tier Strategy (E1)|Quality Tier Strategy (E1)]]
- [[_COMMUNITY_Shadow Pipeline Optimization|Shadow Pipeline Optimization]]
- [[_COMMUNITY_gltfjsx Compression Pipeline|gltfjsx Compression Pipeline]]
- [[_COMMUNITY_Landmark Generic GLB Loader|Landmark Generic GLB Loader]]
- [[_COMMUNITY_Resume Tour Stop|Resume Tour Stop]]

## God Nodes (most connected - your core abstractions)
1. `useTour` - 17 edges
2. `compilerOptions` - 15 edges
3. `Pirate treasure map (parchment)` - 12 edges
4. `useVoyage` - 11 edges
5. `Mitul Dhawan` - 11 edges
6. `STOPS` - 9 edges
7. `Vec3` - 8 edges
8. `Performance audit — room for improvement` - 7 edges
9. `Pirate Portfolio 🏴‍☠️` - 7 edges
10. `tailwind` - 6 edges

## Surprising Connections (you probably didn't know these)
- `AI Dev Tools (Claude Code, Cursor, Copilot)` --semantically_similar_to--> `Next.js + React Three Fiber Stack`  [INFERRED] [semantically similar]
  public/resume.pdf → CLAUDE.md
- `Mitul Dhawan` --conceptually_related_to--> `portfolio.ts Content Model`  [INFERRED]
  public/resume.pdf → CLAUDE.md
- `ContentPanel()` --calls--> `useTour`  [EXTRACTED]
  src/components/ui/ContentPanel.tsx → src/components/tour/useTour.ts
- `CameraRig()` --calls--> `useTour`  [EXTRACTED]
  src/components/tour/CameraRig.tsx → src/components/tour/useTour.ts
- `Marker()` --calls--> `useTour`  [EXTRACTED]
  src/components/tour/Marker.tsx → src/components/tour/useTour.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Zustand stores forming the state-store bridge** — claude_usetour, claude_usevoyage, claude_useaudio, claude_state_store_bridge [EXTRACTED 1.00]
- **End-to-end sailing flow steps** — claude_usetour, claude_usevoyage, claude_floatingvessel, claude_camerarig [EXTRACTED 1.00]
- **Mitul Dhawan's career timeline** — public_resume_eden, public_resume_zeroblock, public_resume_dexcelerate, public_resume_bitwyre [EXTRACTED 1.00]

## Communities (43 total, 27 thin omitted)

### Community 0 - "2D Lite Page & Island Models"
Cohesion: 0.08
Nodes (23): metadata, projects, ContentPanel(), SPOTS, TreasureMap(), ALL_STOPS, CameraFraming, CONTACT (+15 more)

### Community 1 - "Scene Roots & Markers"
Cohesion: 0.14
Nodes (14): Navbar(), KIND_COLOR, Marker(), flagPoleHeight(), SubPoiMarker(), SubPois(), TourState, useTour (+6 more)

### Community 3 - "Dev Dependencies & Config"
Cohesion: 0.10
Nodes (20): devDependencies, eslint, eslint-config-next, @gltf-transform/cli, postcss, tailwindcss, @types/node, @types/react (+12 more)

### Community 4 - "Runtime Dependencies"
Cohesion: 0.10
Nodes (20): dependencies, class-variance-authority, clsx, file-loader, gsap, @gsap/react, lucide-react, next (+12 more)

### Community 5 - "Portfolio Content & Resume"
Cohesion: 0.13
Nodes (18): Next.js + React Three Fiber Stack, portfolio.ts Content Model, AI Dev Tools (Claude Code, Cursor, Copilot), Bitwyre (Software/Quant/Blockchain Developer), Canggu Layer-1 Blockchain, DexCelerate (Backend Engineer, Contract), Distributed Systems & Messaging, Eden (Senior Software Engineer) (+10 more)

### Community 6 - "TypeScript Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 7 - "shadcn/ui Config"
Cohesion: 0.12
Nodes (16): aliases, components, hooks, lib, ui, utils, rsc, $schema (+8 more)

### Community 8 - "Pirate Treasure Map"
Cohesion: 0.22
Nodes (13): Pirate treasure map (parchment), Bear / creature marker, Compass rose (N/E/S/W), Dotted trail / route path, Lagoon with star marker, Main island landmass, Mountain ranges, Ocean waves (+5 more)

### Community 9 - "Sub-POI Props (Gem/Crate/Flag)"
Cohesion: 0.11
Nodes (15): FantasyIsland(), LowPolyIsland(), TreasureIsland(), VolcanoIsland(), BackgroundMusic(), CameraRig(), DevCoords(), IntroTitle() (+7 more)

### Community 10 - "Content Panel & Treasure Map View"
Cohesion: 0.16
Nodes (10): SHIP_TO_CREW, VESSEL, VoyagePhase, VoyageState, Dock, dockForIndex(), dockForStop(), DOCKS (+2 more)

### Community 11 - "App Layout & Fonts"
Cohesion: 0.33
Nodes (4): geistMono, geistSans, metadata, viewport

### Community 12 - "ESLint Config"
Cohesion: 0.40
Nodes (4): extends, rules, @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars

### Community 18 - "Performance audit — room for improvement"
Cohesion: 0.12
Nodes (16): A1. Device pixel ratio up to 2 on desktop, A2. Double antialiasing: canvas MSAA + composer MSAA, A3. Shadow pipeline: 2048² PCFSoft map, redrawn every frame, everything casts, A4. Ocean tessellation, A. Fill rate — the iGPU killers, B1. Treasure island ships its own ocean + a 24k-tri coin pile (`treasure-island-transformed.glb`, 2.7MB), B2. `ship_custom.glb` (941KB) is downloaded for ONE material, B3. Texture GPU memory: WebP decodes to raw RGBA (+8 more)

### Community 19 - "CLAUDE.md"
Cohesion: 0.15
Nodes (11): Adding a 3D asset, Architecture, Commands, Conventions, Data / content (edit these to change the portfolio), graphify, Key components & gotchas, Rendering layers (`src/app/page.tsx`) (+3 more)

### Community 20 - "Pirate Portfolio 🏴‍☠️"
Cohesion: 0.22
Nodes (8): Current state (be honest with yourself), Getting started, How to add a new landmark (chest / island / etc.), Optional sound effects, Pirate Portfolio 🏴‍☠️, Project structure, Resume, Sailing (cinematic auto-sail)

## Knowledge Gaps
- **155 isolated node(s):** `extends`, `@typescript-eslint/no-explicit-any`, `@typescript-eslint/no-unused-vars`, `$schema`, `style` (+150 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dependencies` connect `Runtime Dependencies` to `Dev Dependencies & Config`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `useTour` connect `Scene Roots & Markers` to `2D Lite Page & Island Models`, `Sub-POI Props (Gem/Crate/Flag)`, `Content Panel & Treasure Map View`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **What connects `extends`, `@typescript-eslint/no-explicit-any`, `@typescript-eslint/no-unused-vars` to the rest of the system?**
  _164 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `2D Lite Page & Island Models` be split into smaller, more focused modules?**
  _Cohesion score 0.08064516129032258 - nodes in this community are weakly interconnected._
- **Should `Scene Roots & Markers` be split into smaller, more focused modules?**
  _Cohesion score 0.1396011396011396 - nodes in this community are weakly interconnected._
- **Should `Dev Dependencies & Config` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `Runtime Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._