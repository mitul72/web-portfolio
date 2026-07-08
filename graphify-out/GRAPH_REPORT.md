# Graph Report - .  (2026-07-08)

## Corpus Check
- Corpus is ~20,430 words - fits in a single context window. You may not need a graph.

## Summary
- 254 nodes · 369 edges · 18 communities (14 shown, 4 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.8)
- Token cost: 0 input · 66,898 output

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

## God Nodes (most connected - your core abstractions)
1. `useTour` - 17 edges
2. `compilerOptions` - 15 edges
3. `Mitul Dhawan` - 12 edges
4. `Pirate treasure map (parchment)` - 12 edges
5. `useVoyage` - 11 edges
6. `STOPS` - 9 edges
7. `Vec3` - 8 edges
8. `tailwind` - 6 edges
9. `aliases` - 6 edges
10. `useVoyage Store` - 6 edges

## Surprising Connections (you probably didn't know these)
- `AI Dev Tools (Claude Code, Cursor, Copilot)` --semantically_similar_to--> `Next.js + React Three Fiber Stack`  [INFERRED] [semantically similar]
  public/resume.pdf → CLAUDE.md
- `Mitul Dhawan` --conceptually_related_to--> `portfolio.ts Content Model`  [INFERRED]
  public/resume.pdf → CLAUDE.md
- `Resume Tour Stop` --references--> `Mitul Dhawan`  [INFERRED]
  README.md → public/resume.pdf
- `gltfjsx Compression Pipeline` --semantically_similar_to--> `Asset Optimization Pipeline (gltf-transform)`  [INFERRED] [semantically similar]
  README.md → CLAUDE.md
- `Landmark Generic GLB Loader` --conceptually_related_to--> `Tour Stops (STOPS / PLANNED_STOPS)`  [INFERRED]
  README.md → CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Zustand stores forming the state-store bridge** — claude_usetour, claude_usevoyage, claude_useaudio, claude_state_store_bridge [EXTRACTED 1.00]
- **End-to-end sailing flow steps** — claude_usetour, claude_usevoyage, claude_floatingvessel, claude_camerarig [EXTRACTED 1.00]
- **Mitul Dhawan's career timeline** — public_resume_eden, public_resume_zeroblock, public_resume_dexcelerate, public_resume_bitwyre [EXTRACTED 1.00]

## Communities (18 total, 4 thin omitted)

### Community 0 - "2D Lite Page & Island Models"
Cohesion: 0.06
Nodes (33): metadata, projects, FantasyIsland(), LowPolyIsland(), TreasureIsland(), VolcanoIsland(), BackgroundMusic(), DevCoords() (+25 more)

### Community 1 - "Scene Roots & Markers"
Cohesion: 0.13
Nodes (21): SHIP_TO_CREW, VESSEL, Navbar(), CameraRig(), KIND_COLOR, Marker(), SubPois(), TourState (+13 more)

### Community 2 - "Architecture Concepts"
Cohesion: 0.13
Nodes (22): anchors.ts Docks, Asset Optimization Pipeline (gltf-transform), CameraRig, DevCoords, FloatingVessel, Next.js + React Three Fiber Stack, Ocean Shader, Sailing Flow (+14 more)

### Community 3 - "Dev Dependencies & Config"
Cohesion: 0.10
Nodes (20): devDependencies, eslint, eslint-config-next, @gltf-transform/cli, postcss, tailwindcss, @types/node, @types/react (+12 more)

### Community 4 - "Runtime Dependencies"
Cohesion: 0.10
Nodes (20): dependencies, class-variance-authority, clsx, file-loader, gsap, @gsap/react, lucide-react, next (+12 more)

### Community 5 - "Portfolio Content & Resume"
Cohesion: 0.13
Nodes (19): portfolio.ts Content Model, Tour Stops (STOPS / PLANNED_STOPS), Bitwyre (Software/Quant/Blockchain Developer), Canggu Layer-1 Blockchain, DexCelerate (Backend Engineer, Contract), Distributed Systems & Messaging, Eden (Senior Software Engineer), FastTelemetry (+11 more)

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
Cohesion: 0.22
Nodes (3): flagPoleHeight(), SubPoiMarker(), SubPoi

### Community 10 - "Content Panel & Treasure Map View"
Cohesion: 0.29
Nodes (5): ContentPanel(), SPOTS, TreasureMap(), ContactContent, StopContent

### Community 11 - "App Layout & Fonts"
Cohesion: 0.33
Nodes (4): geistMono, geistSans, metadata, viewport

### Community 12 - "ESLint Config"
Cohesion: 0.40
Nodes (4): extends, rules, @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars

## Knowledge Gaps
- **115 isolated node(s):** `extends`, `@typescript-eslint/no-explicit-any`, `@typescript-eslint/no-unused-vars`, `$schema`, `style` (+110 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dependencies` connect `Runtime Dependencies` to `Dev Dependencies & Config`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `Mitul Dhawan` connect `Portfolio Content & Resume` to `Architecture Concepts`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Mitul Dhawan` (e.g. with `portfolio.ts Content Model` and `Resume Tour Stop`) actually correct?**
  _`Mitul Dhawan` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `extends`, `@typescript-eslint/no-explicit-any`, `@typescript-eslint/no-unused-vars` to the rest of the system?**
  _117 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `2D Lite Page & Island Models` be split into smaller, more focused modules?**
  _Cohesion score 0.05877551020408163 - nodes in this community are weakly interconnected._
- **Should `Scene Roots & Markers` be split into smaller, more focused modules?**
  _Cohesion score 0.12941176470588237 - nodes in this community are weakly interconnected._
- **Should `Architecture Concepts` be split into smaller, more focused modules?**
  _Cohesion score 0.12554112554112554 - nodes in this community are weakly interconnected._