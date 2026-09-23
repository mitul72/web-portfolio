# Graph Report - web-portfolio-aaa  (2026-09-23)

## Corpus Check
- 52 files · ~8,057,452 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 527 nodes · 819 edges · 54 communities (25 shown, 29 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 47 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a4ba2541`
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
- [[_COMMUNITY_page.tsx|page.tsx]]
- [[_COMMUNITY_reference_scene.py|reference_scene.py]]
- [[_COMMUNITY_rules|rules]]
- [[_COMMUNITY_world.ts|world.ts]]
- [[_COMMUNITY_buildlab.py|buildlab.py]]
- [[_COMMUNITY_Art reference|Art reference]]
- [[_COMMUNITY_page.tsx|page.tsx]]
- [[_COMMUNITY_useTour|useTour]]
- [[_COMMUNITY_dock_check.py|dock_check.py]]
- [[_COMMUNITY_ContentPanel.tsx|ContentPanel.tsx]]
- [[_COMMUNITY_Marker.tsx|Marker.tsx]]

## God Nodes (most connected - your core abstractions)
1. `material()` - 20 edges
2. `Graph` - 18 edges
3. `useTour` - 17 edges
4. `compilerOptions` - 15 edges
5. `skull()` - 12 edges
6. `Pirate treasure map (parchment)` - 12 edges
7. `loft()` - 11 edges
8. `ember()` - 11 edges
9. `lighthouse_rock()` - 11 edges
10. `Mitul Dhawan` - 11 edges

## Surprising Connections (you probably didn't know these)
- `AI Dev Tools (Claude Code, Cursor, Copilot)` --semantically_similar_to--> `Next.js + React Three Fiber Stack`  [INFERRED] [semantically similar]
  public/resume.pdf → CLAUDE.md
- `Mitul Dhawan` --conceptually_related_to--> `portfolio.ts Content Model`  [INFERRED]
  public/resume.pdf → CLAUDE.md
- `CameraRig()` --calls--> `useTour`  [EXTRACTED]
  src/components/tour/CameraRig.tsx → src/components/tour/useTour.ts
- `Marker()` --calls--> `useTour`  [EXTRACTED]
  src/components/tour/Marker.tsx → src/components/tour/useTour.ts
- `ContentPanel()` --calls--> `useTour`  [EXTRACTED]
  src/components/ui/ContentPanel.tsx → src/components/tour/useTour.ts

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Zustand stores forming the state-store bridge** — claude_usetour, claude_usevoyage, claude_useaudio, claude_state_store_bridge [EXTRACTED 1.00]
- **End-to-end sailing flow steps** — claude_usetour, claude_usevoyage, claude_floatingvessel, claude_camerarig [EXTRACTED 1.00]
- **Mitul Dhawan's career timeline** — public_resume_eden, public_resume_zeroblock, public_resume_dexcelerate, public_resume_bitwyre [EXTRACTED 1.00]

## Communities (54 total, 29 thin omitted)

### Community 0 - "2D Lite Page & Island Models"
Cohesion: 0.18
Nodes (11): SHIP_TO_CREW, VESSEL, CameraRig(), VoyagePhase, VoyageState, Dock, dockForIndex(), dockForStop() (+3 more)

### Community 1 - "Scene Roots & Markers"
Cohesion: 0.08
Nodes (52): build_home(), clear_of_buildings(), ground(), ground_z(), lantern_lights(), main(), massif(), outpost() (+44 more)

### Community 3 - "Dev Dependencies & Config"
Cohesion: 0.09
Nodes (42): all_materials(), barrel(), Builder, crate(), _finish(), glow_material(), gold_material(), house() (+34 more)

### Community 4 - "Runtime Dependencies"
Cohesion: 0.05
Nodes (40): dependencies, class-variance-authority, clsx, file-loader, gsap, @gsap/react, lucide-react, next (+32 more)

### Community 5 - "Portfolio Content & Resume"
Cohesion: 0.13
Nodes (18): Next.js + React Three Fiber Stack, portfolio.ts Content Model, AI Dev Tools (Claude Code, Cursor, Copilot), Bitwyre (Software/Quant/Blockchain Developer), Canggu Layer-1 Blockchain, DexCelerate (Backend Engineer, Contract), Distributed Systems & Messaging, Eden (Senior Software Engineer) (+10 more)

### Community 6 - "TypeScript Config"
Cohesion: 0.05
Nodes (55): bark_material(), bush(), _frame(), _frond(), ground_hit(), leaf_material(), palm(), Vegetation: palms with ring-scarred curved trunks and folded, serrated fronds; l (+47 more)

### Community 7 - "shadcn/ui Config"
Cohesion: 0.14
Nodes (10): Graph, stops: [(pos, (r, g, b)), ...], clouds(), Sky, sun, haze, water and cameras shared by every world render., A sea plane: finely gridded near the islands (so the shore field is     smooth),, Direction TO the sun. NOTE Blender's sky texture puts its sun at     (+sin r, co, Painterly cumulus bands low on the horizon: warm-lit on the sun side,     lavend, sky_and_sun() (+2 more)

### Community 8 - "Pirate Treasure Map"
Cohesion: 0.22
Nodes (13): Pirate treasure map (parchment), Bear / creature marker, Compass rose (N/E/S/W), Dotted trail / route path, Lagoon with star marker, Main island landmass, Mountain ranges, Ocean waves (+5 more)

### Community 9 - "Sub-POI Props (Gem/Crate/Flag)"
Cohesion: 0.22
Nodes (3): flagPoleHeight(), SubPoiMarker(), SubPoi

### Community 10 - "Content Panel & Treasure Map View"
Cohesion: 0.20
Nodes (21): apply_modifiers(), bake_texture(), bake_vertex_colors(), cut_below(), cycles_gpu(), log(), main(), Export the approved archipelago for the web.      blender -b --factory-startup b (+13 more)

### Community 11 - "App Layout & Fonts"
Cohesion: 0.33
Nodes (4): geistMono, geistSans, metadata, viewport

### Community 12 - "ESLint Config"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 18 - "Performance audit — room for improvement"
Cohesion: 0.11
Nodes (16): Current state, Getting started, How to add a new landmark (chest / island / etc.), Optional sound effects, Pirate Portfolio 🏴‍☠️, Project structure, Resume, Sailing (cinematic auto-sail) (+8 more)

### Community 19 - "CLAUDE.md"
Cohesion: 0.12
Nodes (16): aliases, components, hooks, lib, ui, utils, rsc, $schema (+8 more)

### Community 20 - "Pirate Portfolio 🏴‍☠️"
Cohesion: 0.12
Nodes (16): A1. Device pixel ratio up to 2 on desktop, A2. Double antialiasing: canvas MSAA + composer MSAA, A3. Shadow pipeline: 2048² PCFSoft map, redrawn every frame, everything casts, A4. Ocean tessellation, A. Fill rate — the iGPU killers, B1. Treasure island ships its own ocean + a 24k-tri coin pile (`treasure-island-transformed.glb`, 2.7MB), B2. `ship_custom.glb` (941KB) is downloaded for ONE material, B3. Texture GPU memory: WebP decodes to raw RGBA (+8 more)

### Community 43 - "page.tsx"
Cohesion: 0.08
Nodes (22): metadata, projects, ALL_STOPS, CameraFraming, CONTACT, CONTACT_CONTENT, DRIFTING_ISLE, EMBER_ISLE (+14 more)

### Community 44 - "reference_scene.py"
Cohesion: 0.48
Nodes (6): add_camera(), import_glb(), main(), Rebuild the CURRENT world in Blender, at its real three.js transforms, with the, three_matrix(), three_vec()

### Community 45 - "rules"
Cohesion: 0.40
Nodes (4): extends, rules, @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars

### Community 46 - "world.ts"
Cohesion: 0.40
Nodes (4): FOG_COLOR, KEY_COLOR, KEY_DIR, SUN_DISC_DIR

### Community 49 - "page.tsx"
Cohesion: 0.18
Nodes (8): LAVA, SELF_LIT, World(), BackgroundMusic(), DevCoords(), IntroTitle(), LoadingScreen(), HOME_CAMERA

### Community 50 - "useTour"
Cohesion: 0.37
Nodes (8): Navbar(), SubPois(), TourState, useTour, useVoyage, SubNav(), TourControls(), STOPS

### Community 51 - "dock_check.py"
Cohesion: 0.29
Nodes (10): catmull(), ground_below(), hull_points(), land_objects(), main(), Check docks, routes and arrival cameras for src/data/anchors.ts against the real, Blender matrix for the ship mesh, mirroring the app's scene graph:     vessel(x,, Highest land surface under a Blender XY point (or -99). (+2 more)

### Community 52 - "ContentPanel.tsx"
Cohesion: 0.29
Nodes (5): ContentPanel(), SPOTS, TreasureMap(), ContactContent, StopContent

### Community 53 - "Marker.tsx"
Cohesion: 0.50
Nodes (3): KIND_COLOR, Marker(), TourStop

## Knowledge Gaps
- **162 isolated node(s):** `extends`, `@typescript-eslint/no-explicit-any`, `@typescript-eslint/no-unused-vars`, `$schema`, `style` (+157 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Graph` connect `shadcn/ui Config` to `Dev Dependencies & Config`, `TypeScript Config`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `material()` connect `Dev Dependencies & Config` to `TypeScript Config`, `shadcn/ui Config`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **What connects `extends`, `@typescript-eslint/no-explicit-any`, `@typescript-eslint/no-unused-vars` to the rest of the system?**
  _245 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Scene Roots & Markers` be split into smaller, more focused modules?**
  _Cohesion score 0.08065458796025717 - nodes in this community are weakly interconnected._
- **Should `Dev Dependencies & Config` be split into smaller, more focused modules?**
  _Cohesion score 0.08816326530612245 - nodes in this community are weakly interconnected._
- **Should `Runtime Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.04878048780487805 - nodes in this community are weakly interconnected._
- **Should `Portfolio Content & Resume` be split into smaller, more focused modules?**
  _Cohesion score 0.13071895424836602 - nodes in this community are weakly interconnected._