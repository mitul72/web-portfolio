// -----------------------------------------------------------------------------
// PORTFOLIO CONTENT
// -----------------------------------------------------------------------------
// Single source of truth for everything shown in the 3D scene.
//
// HONEST STATE OF THE WORLD (read this before editing):
//   The scene currently contains ONE island, a captain character, and a ship.
//   There is NO treasure chest and NO second/third island yet — those assets
//   don't exist. So only the `STOPS` below are rendered. Everything that needs
//   a model we don't have lives in `PLANNED_STOPS`, which is intentionally NOT
//   rendered. When you source a GLB for one of them, follow README.md, place it
//   with the dev coordinate logger, and move its entry from PLANNED_STOPS into
//   STOPS.
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

export interface ExperienceContent {
  kind: "experience";
  role: string;
  company: string;
  period: string;
  bullets: string[];
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

/** Prop type used for a sub-POI marker on an island. */
export type PoiProp = "bottle" | "gem" | "scroll" | "flag";

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
export const HOME_CAMERA: CameraFraming = {
  position: [23.08, 30.52, 150.63],
  lookAt: [21.7, 12, 105],
};

// -----------------------------------------------------------------------------
// ISLAND LANDMASS PLACEMENTS  ← EDIT THESE to move an island.
// -----------------------------------------------------------------------------
// Single source of truth for each landmass. The 3D model AND its floating tour
// marker both derive from these, so an island and its tag move together.
// (X = left/right, Y = height, Z = forward/back.) Source GLBs are authored
// huge, so they're scaled way down. Tune with SHOW_DEV_COORDS in page.tsx.
// -----------------------------------------------------------------------------

// Volcano island (the "project-1" stop). Far out + shrunk so it reads as a
// distinct island a real sail away.
export const VOLCANO_TRANSFORM = {
  position: [-320, 4, -140] as Vec3,
  scale: 0.009,
  rotation: [0, 0.6, 0] as Vec3,
};

// Treasure island (the "resume" stop). Authored huge with a deep-negative Y
// center, so scaled down + lifted to sit on the water. Opposite the volcano.
export const TREASURE_TRANSFORM = {
  position: [280, -2, 160] as Vec3,
  scale: 0.65,
  rotation: [0, -0.8, 0] as Vec3,
};

/** A marker position floating `height` units above an island's center. */
function markerAbove(t: { position: Vec3 }, height: number): Vec3 {
  return [t.position[0], t.position[1] + height, t.position[2]];
}

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
    // Floats above the hut/tavern (building cluster center ~[-6, -9], roof
    // ~Y45) so it anchors to the island landmark, not empty deck space.
    // Fine-tune with SHOW_DEV_COORDS if the roof peak differs.
    position: [-6, 52, -9],
    camera: {
      position: [40, 45, 60],
      lookAt: [-6, 30, -9],
    },
    content: {
      kind: "intro",
      name: "Mitul Dhawan", // TODO: confirm
      tagline: "Software Engineer",
      blurb:
        "Ahoy! Welcome to my portfolio. It's still being built — a treasure " +
        "chest for my resume and islands for my projects and experience are " +
        "on the way. For now, drag to look around the island and ship.",
    },
  },
  {
    id: "project-1",
    label: "Project Island",
    navLabel: "Projects",
    kind: "project",
    // Derived from VOLCANO_TRANSFORM so the tag follows the island when moved.
    position: markerAbove(VOLCANO_TRANSFORM, 51),
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
      title: "Project Island",
      description:
        "Wash ashore and explore — each glowing gem holds one of my projects. " +
        "Click a gem to read its story.",
      tech: [],
      links: [],
    },
    // Two example project gems on the volcano island (center ~[-320,?,-140]).
    // Place precisely with SHOW_DEV_COORDS — click the terrain to get coords.
    subPois: [
      {
        id: "fast-telemetry",
        label: "fast-telemetry",
        position: [-300, 30, -120],
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
        position: [-340, 30, -155],
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
        position: [-320, 30, -100],
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
        position: [-345, 30, -125],
        prop: "gem",
        content: {
          kind: "project",
          title: "Stack.CLI",
          description:
            "A command-line tool (\"Stacksly\") to search StackOverflow straight " +
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
    // Derived from TREASURE_TRANSFORM so the tag follows the island when moved.
    position: markerAbove(TREASURE_TRANSFORM, 35),
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
})[] = [
  {
    id: "experience-1",
    label: "The Docks (Experience)",
    kind: "experience",
    needsAsset:
      "A dock/harbor landmark, or reuse the ship as the experience stop.",
    content: {
      kind: "experience",
      role: "Software Engineer", // TODO
      company: "Company Name", // TODO
      period: "2023 — Present", // TODO
      bullets: ["Built / shipped X, resulting in Y."], // TODO
    },
  },
  {
    id: "contact",
    label: "Contact",
    kind: "contact",
    needsAsset: "None strictly — can go live as a floating marker any time.",
    content: {
      kind: "contact",
      title: "Send a Message in a Bottle",
      blurb: "Want to work together or just say hi?",
      links: [
        { label: "Email", url: "mailto:mituldhawan154@gmail.com" },
        { label: "GitHub", url: "https://github.com/mitul72" },
        { label: "LinkedIn", url: "https://linkedin.com/in/" }, // TODO
      ],
    },
  },
];

// -----------------------------------------------------------------------------
// CONTENT SELECTORS — used by BOTH the 3D scene and the 2D `/lite` page, so the
// two views never drift out of sync. All read from the data above.
// -----------------------------------------------------------------------------

const ALL_STOPS = [...STOPS, ...PLANNED_STOPS];

function contentOfKind<K extends StopContent["kind"]>(
  kind: K
): Extract<StopContent, { kind: K }> | undefined {
  for (const s of ALL_STOPS) {
    if (s.content.kind === kind) return s.content as Extract<StopContent, { kind: K }>;
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

/** Every experience entry. */
export const EXPERIENCES: ExperienceContent[] = ALL_STOPS.map(
  (s) => s.content
).filter((c): c is ExperienceContent => c.kind === "experience");
