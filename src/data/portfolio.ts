// -----------------------------------------------------------------------------
// PORTFOLIO CONTENT
// -----------------------------------------------------------------------------
// Single source of truth for everything shown in the 3D scene.
//
// STATE OF THE WORLD (read this before editing):
//   All five stops below are LIVE, on the rebuilt archipelago (one GLB built
//   in Blender by blender/world.py, exported by blender/export_world.py):
//   intro (home island + outpost), projects (Ember Isle, the volcano), resume
//   (Skull Cove), experience (Lighthouse Rock) and contact (the Drifting Isle).
//   `PLANNED_STOPS` is currently EMPTY; it exists for stops whose 3D asset
//   doesn't exist yet, so they can be designed without faking markers over
//   empty water.
//
//   Sub-POI positions sit on the real terrain: re-raycast them in Blender if an
//   island is rebuilt. The ship and crew are still placeholder-grade (TODO.md).
// -----------------------------------------------------------------------------

export type Vec3 = [number, number, number];

export interface CameraFraming {
  /** Where the camera moves to. */
  position: Vec3;
  /** The point in space the camera looks at. */
  lookAt: Vec3;
}

export type StopKind =
  | "intro"
  | "resume"
  | "project"
  | "experience"
  | "contact";

export interface ProjectContent {
  kind: "project";
  title: string;
  description: string;
  tech: string[];
  links: { label: string; url: string }[];
}

export interface Job {
  role: string;
  company: string;
  period: string;
  bullets: string[];
}

export interface ExperienceContent {
  kind: "experience";
  title: string;
  /** Career timeline — newest first. Rendered as a list in one panel. */
  jobs: Job[];
}

export interface ResumeContent {
  kind: "resume";
  title: string;
  blurb: string;
  /** Put your PDF at /public/resume.pdf (create the public/ folder). */
  pdfUrl: string;
}

export interface IntroContent {
  kind: "intro";
  name: string;
  tagline: string;
  blurb: string;
}

export interface ContactContent {
  kind: "contact";
  title: string;
  blurb: string;
  links: { label: string; url: string }[];
}

export type StopContent =
  | IntroContent
  | ResumeContent
  | ProjectContent
  | ExperienceContent
  | ContactContent;

// TODO(assets): all sub-POI props are placeholder-grade and planned for a full
// art overhaul. The gems below are deliberately generic — four projects all
// share one silhouette, so the marker tells you nothing about which project it
// is. Replacing them needs PRODUCTION-GRADE models, not primitives glued
// together (that was tried and rejected). Read TODO.md before generating
// any asset.

/** Prop type used for a sub-POI marker on an island. */
export type PoiProp = "bottle" | "gem" | "scroll" | "flag" | "crate" | "wisp";

/**
 * A small point of interest placed ON an island (a "hub"). It only appears
 * while its parent stop is active; clicking it opens its own content panel.
 * This is how one island can surface several projects.
 */
export interface SubPoi {
  id: string;
  label: string;
  /** WORLD position of the prop (use SHOW_DEV_COORDS to place it on terrain). */
  position: Vec3;
  prop: PoiProp;
  content: StopContent;
  /** Crates: count. Flags: pole height. Wisps: orb size. Encodes tenure/weight. */
  stack?: number;
  /** If true, the prop bobs on the water surface. */
  bob?: boolean;
  /** Accent color for the prop (e.g. a flag's pennant). Falls back per-prop. */
  color?: string;
}

export interface TourStop {
  id: string;
  /** Label shown on the 3D marker. */
  label: string;
  /** Short label for the section nav bar (falls back to `label`). */
  navLabel?: string;
  kind: StopKind;
  /** World position of the floating marker. */
  position: Vec3;
  /** Camera framing when this stop is visited. */
  camera: CameraFraming;
  content: StopContent;
  /**
   * Optional sub-POIs placed on this island (hub). When present, arriving here
   * reveals these clickable props; each opens its own panel.
   */
  subPois?: SubPoi[];
  /**
   * Optional: path to a GLB landmark this stop points at (chest, island, etc.).
   * Live STOPS don't need one — they point at geometry already in the scene.
   */
  asset?: {
    /** Import the GLB and pass the resolved URL here. */
    url: string;
    position: Vec3;
    scale?: number;
    rotation?: Vec3;
  };
}

// -----------------------------------------------------------------------------
// Default "home" view — the establishing shot.
// -----------------------------------------------------------------------------
// Low over the water, looking up at the arch and spires, the docked ship on
// the right third: the approved "hero" render's framing (CAM_hero in
// blender/hero_island.py). The orbit target sits low so the rig can keep it.
export const HOME_CAMERA: CameraFraming = {
  position: [-10, 12, 188],
  lookAt: [0, 22, 10],
};

// -----------------------------------------------------------------------------
// ISLAND CENTRES. The whole archipelago is one GLB authored in place
// (blender/world.py), so these no longer move anything: they anchor each
// stop's floating tag. Blender (x, y) = three (x, -z).
// -----------------------------------------------------------------------------

/** Ember Isle, the volcano (projects). Summit crater ~70 m. */
export const EMBER_ISLE = { position: [-320, 0, -140] as Vec3 };
/** Skull Cove (resume). Skull crown ~50 m. */
export const SKULL_COVE = { position: [280, 0, 160] as Vec3 };
/** Lighthouse Rock (experience). Lamp room ~60 m. */
export const LIGHTHOUSE_ROCK = { position: [180, 0, -300] as Vec3 };
/** Drifting Isle, the floating island (contact). Palm tops ~62 m. */
export const DRIFTING_ISLE = { position: [-240, 0, 220] as Vec3 };

/** A marker position floating `height` units above an island's center. */
function markerAbove(t: { position: Vec3 }, height: number): Vec3 {
  return [t.position[0], t.position[1] + height, t.position[2]];
}

// Shared by the contact stop AND its bottle sub-POI (both open the same map).
const CONTACT_CONTENT: ContactContent = {
  kind: "contact",
  title: "Send a Message in a Bottle",
  blurb: "Want to work together or just say hi?",
  links: [
    { label: "Email", url: "mailto:mituldhawan154@gmail.com" },
    { label: "GitHub", url: "https://github.com/mitul72" },
    {
      label: "LinkedIn",
      url: "https://www.linkedin.com/in/mitul-dhawan-b9615b266/",
    },
  ],
};

// -----------------------------------------------------------------------------
// LIVE STOPS — only things that map to geometry that actually exists today.
// Right now: just the intro at the captain. Add more as assets arrive.
// -----------------------------------------------------------------------------
export const STOPS: TourStop[] = [
  {
    id: "intro",
    label: "Welcome Aboard",
    navLabel: "About",
    kind: "intro",
    // Floats above the tavern on the rock shelf (roof ridge ~y 24).
    position: [4, 32, 20],
    camera: {
      position: [40, 30, 80],
      lookAt: [4, 18, 20],
    },
    content: {
      kind: "intro",
      name: "Mitul Dhawan", // TODO: confirm
      tagline: "Software Engineer",
      blurb:
        "Ahoy! Welcome to my portfolio. Set sail to explore: my projects on " +
        "Ember Isle, my résumé buried at Skull Cove, my voyages kept at " +
        "Lighthouse Rock, and a message bottle waiting at the Drifting Isle.",
    },
  },
  {
    id: "project-1",
    label: "Ember Isle",
    navLabel: "Projects",
    kind: "project",
    position: markerAbove(EMBER_ISLE, 88),
    camera: {
      // Unused for arrival (the dock camera in anchors.ts drives that), but
      // kept sensible for any direct camera use.
      position: [-180, 60, -30],
      lookAt: [-320, 30, -140],
    },
    // Island-level content: an overview. The individual projects are the
    // sub-POI gems scattered on the island below.
    content: {
      kind: "project",
      title: "Ember Isle",
      description:
        "Built in the shadow of the volcano: each glowing gem holds one of my " +
        "projects. " +
        "Click a gem to read its story.",
      tech: [],
      links: [],
    },
    // Project gems on Ember Isle's south-east slope, facing the arrival camera and
    // clear of the lava flow. Heights raycast on the real terrain in Blender.
    subPois: [
      {
        id: "fast-telemetry",
        label: "fast-telemetry",
        position: [-292, 11.3, -88],
        prop: "gem",
        content: {
          kind: "project",
          title: "fast-telemetry",
          description:
            "A crate I co-authored at eden.dev that makes OpenTelemetry faster. " +
            "Instead of locking or atomics on the hot path, it uses simple " +
            "thread-local counters — cutting contention and overhead in " +
            "high-throughput telemetry.",
          tech: ["Rust", "OpenTelemetry", "Observability"],
          links: [
            {
              label: "GitHub",
              url: "https://github.com/mitul72/fast-telemetry",
            },
          ],
        },
      },
      {
        id: "intel-8080-emulator",
        label: "8080 Emulator",
        position: [-280, 10.7, -96],
        prop: "gem",
        content: {
          kind: "project",
          title: "Intel 8080 Emulator",
          description:
            "A cycle-accurate Intel 8080 CPU emulator written from scratch in " +
            "Rust — complete enough to boot and play the original Space " +
            "Invaders, compiled to WebAssembly so you can play it in the " +
            "browser. Built solo in a few weeks: full instruction set, " +
            "interrupts, and machine I/O.",
          tech: ["Rust", "WebAssembly", "Emulation"],
          links: [
            {
              label: "Play it ↗",
              url: "https://8080-emulator-rust.vercel.app/",
            },
            {
              label: "GitHub",
              url: "https://github.com/mitul72/8080-emulator-rust",
            },
          ],
        },
      },
      {
        id: "zeroblock",
        label: "ZeroBlock",
        // TODO: place with SHOW_DEV_COORDS — rough third spot for now.
        position: [-268, 8.2, -90],
        prop: "gem",
        content: {
          kind: "project",
          title: "ZeroBlock",
          description:
            "An ultra-fast trading extension for Axiom.trade, co-founded with " +
            "four friends. I architected and built the entire backend from " +
            "scratch in Rust + Actix Web, with a distributed data layer " +
            "(ScyllaDB for persistence, Valkey/Redis for real-time caching). " +
            "Optimized the critical buy path from 500ms to 7ms — a 98.6% " +
            "improvement — handling thousands of concurrent requests for " +
            "high-frequency trading.",
          tech: ["Rust", "Actix Web", "ScyllaDB", "Valkey/Redis"],
          links: [{ label: "Resume ↗", url: "/resume.pdf" }],
        },
      },
      {
        id: "stack-cli",
        label: "Stack.CLI",
        // TODO: place with SHOW_DEV_COORDS — rough fourth spot for now.
        position: [-300, 24.4, -100],
        prop: "gem",
        content: {
          kind: "project",
          title: "Stack.CLI",
          description:
            'A command-line tool ("Stacksly") to search StackOverflow straight ' +
            "from your terminal — no browser needed. Returns relevant answers " +
            "inline with syntax-highlighted code snippets for a smoother dev " +
            "flow.",
          tech: ["Python", "BeautifulSoup", "Rich", "CLI"],
          links: [
            { label: "GitHub", url: "https://github.com/mitul72/Stack.cli" },
          ],
        },
      },
    ],
  },
  {
    id: "resume",
    label: "Treasure Chest (Resume)",
    navLabel: "Resume",
    kind: "resume",
    position: markerAbove(SKULL_COVE, 62),
    camera: {
      position: [180, 45, 250],
      lookAt: [280, 20, 160],
    },
    content: {
      kind: "resume",
      title: "The Treasure Chest",
      blurb:
        "X marks the spot. Here's the full record of my journey — download " +
        "my resume for the complete story.",
      pdfUrl: "/resume.pdf", // TODO: drop your PDF at public/resume.pdf
    },
  },
  {
    id: "experience",
    label: "Lighthouse Rock",
    navLabel: "Experience",
    kind: "experience",
    position: markerAbove(LIGHTHOUSE_ROCK, 76),
    camera: {
      // Matches the arrival framing in anchors.ts (captured via DevCoords).
      position: [195.63, 72.58, -183.81],
      lookAt: [182, 35, -286],
    },
    // Island overview. The individual roles are will-o'-wisp sub-POIs below —
    // glowing lights hovering over existing landmarks (a tree, a rock, the
    // summit), climbing the island chronologically: a career ascent.
    content: {
      kind: "experience",
      title: "Lighthouse Rock",
      jobs: [], // roles live in subPois; this overview panel just intros them
    },
    // The wisp trail, oldest lowest → newest highest (a career ascent). All
    // four positions are DevCoords-captured hits on existing landmarks (trees,
    // a rock, the summit); the wisp hovers a few units above each.
    subPois: [
      {
        id: "exp-bitwyre",
        label: "Bitwyre",
        position: [170, 38.4, -306],
        prop: "wisp",
        color: "#f4a261", // amber
        stack: 4, // 18 months, 3 promotions → the tallest pole
        content: {
          kind: "experience",
          title: "Bitwyre",
          jobs: [
            {
              role: "Software → Quantitative → Blockchain Developer",
              company: "Bitwyre",
              period: "Dec 2023 — May 2025",
              bullets: [
                "Promoted twice in 18 months across three engineering teams.",
                "Designed and led Canggu, a layer-1 blockchain reaching 50,000+ TPS — a dual-paradigm Rust + CUDA VM, DAG-based mempool, Leader-Verified Tower BFT with Proof of History, and ZK-SNARKs for private transactions.",
                "Built high-frequency trading and market-making systems (Binance) in C++/Python with KDB+ time-series data and LibTorch predictive models.",
              ],
            },
          ],
        },
      },
      {
        id: "exp-dexcelerate",
        label: "DexCelerate",
        position: [188, 38.2, -310],
        prop: "wisp",
        color: "#e76f51", // coral
        stack: 2, // short contract
        content: {
          kind: "experience",
          title: "DexCelerate",
          jobs: [
            {
              role: "Backend Engineer (Contract)",
              company: "DexCelerate",
              period: "May 2025 — Jul 2025",
              bullets: [
                "Improved backend performance and features of a decentralized exchange platform.",
                "Optimized the scanner ~150% faster and refactored Redis key structures for higher cache hit rates and lower latency.",
              ],
            },
          ],
        },
      },
      {
        id: "exp-zeroblock",
        label: "ZeroBlock",
        position: [176, 38.0, -290],
        prop: "wisp",
        color: "#4cc9f0", // cyan
        stack: 3,
        content: {
          kind: "experience",
          title: "ZeroBlock",
          jobs: [
            {
              role: "Co-Founder & Backend Developer",
              company: "ZeroBlock",
              period: "Apr 2025 — Present",
              bullets: [
                "Co-founded and architected ZeroBlock, an ultra-fast trading extension for Axiom.trade for professional traders.",
                "Built the entire backend from scratch in Rust + Actix Web with a distributed data layer — ScyllaDB for persistence, Valkey/Redis for real-time caching.",
                "Optimized the critical buy path from 500ms to 7ms (98.6%), handling thousands of concurrent requests.",
              ],
            },
          ],
        },
      },
      {
        id: "exp-eden",
        label: "Eden",
        position: [194, 36.7, -296], // by the lighthouse: newest chapter
        prop: "wisp",
        color: "#90be6d", // green (matches the experience kind color)
        stack: 3, // most recent — planted at the summit
        content: {
          kind: "experience",
          title: "Eden",
          jobs: [
            {
              role: "Senior Software Engineer",
              company: "Eden",
              period: "Sept 2025 — May 2026",
              bullets: [
                "Co-authored FastTelemetry (open source), a high-performance Rust metrics library that replaced OpenTelemetry on Eden's proxy — thread-local increments in ~2 ns vs ~40–400 ns for contended atomics on 16 cores.",
                "Architected the platform's OpenTelemetry rollout (94+ metrics) with a suite of Datadog dashboards and alerts powering production monitoring and on-call.",
                "Built a custom Rust logging framework 3× faster than env_logger, and a Criterion-benchmarked metrics batching system to minimize observability overhead on hot paths.",
              ],
            },
          ],
        },
      },
    ],
  },
  {
    id: "contact",
    label: "Drifting Isle",
    navLabel: "Contact",
    kind: "contact",
    // Floats above the socials island (its summit is ~80 world units high).
    position: markerAbove(DRIFTING_ISLE, 74),
    camera: {
      // Matches the arrival framing in anchors.ts (captured via DevCoords).
      position: [-136.71, 65.57, 244.57],
      lookAt: [-240, 40, 220],
    },
    content: CONTACT_CONTENT,
    // The washed-ashore bottle, lodged on a rock (DevCoords hit on
    // Rock_Rock_1001_0) — clicking it (or arriving) unfurls the pirate-map
    // overlay with the social links X-marked on it. Label left empty on
    // purpose: no pill, the bottle speaks for itself.
    subPois: [
      {
        id: "socials-bottle",
        label: "bottled message",
        position: [-204, 0, 250],
        prop: "bottle",
        content: CONTACT_CONTENT,
      },
    ],
  },
];

// -----------------------------------------------------------------------------
// PLANNED STOPS — NOT rendered. Each needs a 3D asset that doesn't exist yet.
// This is a design doc, not fake content. When you have the model:
//   1. Add & compress it per README.md, import it in the scene.
//   2. Fill in real content + real `position`/`camera` (use the dev logger).
//   3. Move the entry into STOPS above.
// -----------------------------------------------------------------------------
export const PLANNED_STOPS: (Omit<TourStop, "position" | "camera"> & {
  needsAsset: string;
})[] = [];

// -----------------------------------------------------------------------------
// CONTENT SELECTORS — used by BOTH the 3D scene and the 2D `/lite` page, so the
// two views never drift out of sync. All read from the data above.
// -----------------------------------------------------------------------------

const ALL_STOPS = [...STOPS, ...PLANNED_STOPS];

function contentOfKind<K extends StopContent["kind"]>(
  kind: K,
): Extract<StopContent, { kind: K }> | undefined {
  for (const s of ALL_STOPS) {
    if (s.content.kind === kind)
      return s.content as Extract<StopContent, { kind: K }>;
    for (const p of s.subPois ?? []) {
      if (p.content.kind === kind)
        return p.content as Extract<StopContent, { kind: K }>;
    }
  }
  return undefined;
}

/** The intro/bio block. */
export const INTRO = contentOfKind("intro");

/** The resume block (title, blurb, pdfUrl). */
export const RESUME = contentOfKind("resume");

/** The contact block (title, blurb, links). */
export const CONTACT = contentOfKind("contact");

/** Every project, flattened from island content + sub-POIs. */
export const PROJECTS: ProjectContent[] = ALL_STOPS.flatMap((s) => {
  const own = s.content.kind === "project" ? [s.content] : [];
  const subs = (s.subPois ?? [])
    .map((p) => p.content)
    .filter((c): c is ProjectContent => c.kind === "project");
  return [...own, ...subs];
  // Note: a hub island's own "overview" project (empty tech/links) is skipped
  // by the lite page via the hasDetail() check there.
});

/** Every job across all experience stops, flattened (newest first). */
export const JOBS: Job[] = ALL_STOPS.flatMap((s) => {
  const own = s.content.kind === "experience" ? s.content.jobs : [];
  const subs = (s.subPois ?? []).flatMap((p) =>
    p.content.kind === "experience" ? p.content.jobs : [],
  );
  return [...own, ...subs];
});
