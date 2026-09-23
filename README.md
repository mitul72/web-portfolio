# Pirate Portfolio 🏴‍☠️

An interactive 3D pirate-themed portfolio (Next.js + React Three Fiber). Sail an
island; visit points of interest (the "tour") to see projects, experience, and a
resume in a treasure chest.

## Getting started

```bash
npm install
npm run dev   # http://localhost:3000
```

## Current state

All five tour stops are **live and rendering**: intro (pirate island), projects
(volcano island), resume (treasure island, with an animated chest that opens on
arrival), experience (fantasy island), and contact (floating socials island).
Plus the ship, the captain, and Toothless as ambient scenery.

- ✅ Working: all five islands + ship + crew, the sailing voyage system,
  guided-tour + free-look camera, sub-POIs per island, content panels, the 2D
  `/lite` fallback, loading screen, background sound.
- ⏳ **The gap is quality, not coverage.** Every asset is placeholder-grade, and
  the lighting/composition need work. See [`TODO.md`](TODO.md) for the full gap
  analysis and the quality bar any new asset has to clear.

`PLANNED_STOPS` in [`src/data/portfolio.ts`](src/data/portfolio.ts) is currently
empty — it exists for stops whose 3D asset doesn't exist yet, so they can be
designed without faking markers over empty water.

## How to add a new landmark (chest / island / etc.)

1. **Get a `.glb` model** (Sketchfab, Poly Pizza, Kenney, Quaternius…). Prefer
   low-poly and CC0/permissive licenses.
2. **Compress it** with the same pipeline as the existing island:
   ```bash
   npx gltfjsx@6 your-model.glb --transform
   ```
   This emits `your-model-transformed.glb` (much smaller) + a typed React
   component. Aim for **under ~1.5 MB** per asset. Put the `.glb` in
   `src/assets/`.
3. **Render it.** For a simple static prop, use the generic loader:
   ```tsx
   import Chest from "@/assets/treasure-chest-transformed.glb";
   import Landmark from "@/components/tour/Landmark";
   // inside the scene:
   <Landmark url={Chest} position={[x, y, z]} scale={2} />
   ```
   For fine mesh/material control, use the gltfjsx-generated component instead.
4. **Place it precisely.** Set `SHOW_DEV_COORDS = true` in
   [`src/app/page.tsx`](src/app/page.tsx), run the app, click the scene to log
   world `(x, y, z)` to the console, press `c` to log the camera. Copy those
   numbers in. Turn the flag back off before shipping.
5. **Make it a tour stop.** Move the matching entry from `PLANNED_STOPS` into
   `STOPS` in `portfolio.ts`, filling in real `position` + `camera` values.

## Sailing (cinematic auto-sail)

Visiting a tour stop makes the **ship actually sail there** (hub-and-spoke from
the main island), with a chase-cam, wake trail, captain animation, and an
arrival reveal — then the content panel opens. A "Skip voyage" button appears
while sailing.

- Docks/paths per stop live in [`src/data/anchors.ts`](src/data/anchors.ts).
- Voyage state is [`src/components/tour/useVoyage.ts`](src/components/tour/useVoyage.ts).
- Tune voyage length via `VOYAGE_DURATION` there.

### Optional sound effects

Drop these in `public/audio/` and they'll play (absent = silently skipped):

- `sailing-loop.mp3` — looping water rush while sailing
- `arrive.mp3` — one-shot splash/bell on arrival

The existing sound toggle (bottom-left) mutes/unmutes everything.

## Resume

Drop your PDF at **`public/resume.pdf`**. The resume stop links to `/resume.pdf`.

## Project structure

```
src/
  app/page.tsx                 Scene + overlays wiring; dev-coords flag
  data/portfolio.ts            ALL content: live STOPS + PLANNED_STOPS
  components/
    models/pirate-island.tsx   The island GLB (gltfjsx output) + markers
    tour/
      CameraRig.tsx            Owns the camera (OrbitControls + gsap, reconciled)
      Landmark.tsx             Generic GLB loader — drop-in point for new assets
      Marker.tsx               Clickable floating point-of-interest
      DevCoords.tsx            Dev-only coordinate logger
      useTour.ts               Tour state (zustand)
    ui/                        ContentPanel, TourControls, LoadingScreen
    shared/navbar.tsx          Top overlay (brand + resume deep-link)
    music.tsx                  Background ocean sound toggle
  assets/                      GLBs + audio + images
```
