# TODO

Running list of planned work on the portfolio.

## Asset overhaul (planned)

> ### ⛔ WORKFLOW GATE — do not skip
>
> **Build the assets in Blender first. Do NOT modify the codebase until I have
> looked at them and approved the quality.**
>
> The order is: generate/model in Blender → show me renders → wait for my
> explicit approval → only then export, compress, and wire anything into the
> app. No edits to `src/`, no new files in `src/assets/`, no data changes until
> that approval lands. If the assets are rejected, nothing in the repo needs
> unwinding.

**Every 3D asset in this scene is placeholder-grade and will be replaced.**
Nothing currently in `src/assets/` should be treated as final, or used as a
quality reference to match. A full art pass is planned — sooner or later all of
it gets redone.

Known asset gaps:

- [ ] Sub-POI markers on Project Island are four identical cyan gems, so the
      marker says nothing about which project it belongs to. Each project should
      get its own distinct landmark.
- [ ] Island props are sourced/free models at mixed quality and mixed styles.
- [ ] Ship and captain are placeholders.

See **"Where the scene stands today"** below for the full gap analysis against
the reference bar — including the lighting and composition problems, which are
the biggest wins and are *not* asset work.

### Quality bar for new assets — READ THIS BEFORE GENERATING ANYTHING

This applies to **AI agents asked to create or generate assets** as much as to
me. The bar is **production-grade**, not "reads okay from far away".

**Do not hand-assemble primitives.** Stacking cones, cylinders, and spheres into
a "windmill" or a "skull" does not meet the bar. That approach has a hard
ceiling that no amount of lighting, scaling, or clever placement gets past. It
has already been tried in this repo and rejected.

What production-grade means here:

- **Silhouette is the test.** The shape must be recognizable and characterful as
  a solid black shape at thumbnail size. If it needs its label to be
  identifiable, it failed.
- **Real modeling.** Lofted cross-sections, detail cut into the surface,
  deliberate bevels and edge treatment. Detail hierarchy with restraint —
  primary masses, medium features, fine detail — and clean areas left alone,
  because detail only registers against something undetailed.
- **Stylistically consistent** with the faceted, saturated, hand-painted
  low-poly pirate world. A photoreal asset dropped into this scene reads worse
  than a well-made stylized one.
- **Judged in context, never in isolation.** Import the destination island, place
  the asset on it at true scale, and look through the actual arrival camera from
  `src/data/anchors.ts`. Props that look fine on their own are routinely the
  wrong size or height, or facing away, once they are on the island.

### Reference bar — Sea of Thieves / Skull and Bones

The target quality is **AAA stylized pirate game art**: Sea of Thieves outposts,
Skull and Bones islands, and the hand-painted stylized island concept art in that
family. Study those before modeling. Concretely, what makes them work:

- **Complex, irregular silhouettes.** Rock formations are stacked masses of
  distinct boulders with overhangs, arches, and cracks — never one smooth
  tapered cylinder. Cliff faces have shelves and broken edges. An outpost is a
  *cluster* of buildings at varied heights, roof angles, and rotations that reads
  as a settlement, not as one object.
- **Material depth on every surface.** Weathering, moss and lichen in the
  crevices, wet darkening near the waterline, sun-bleaching on upward faces,
  grime running downward. Nothing is a single flat tone. Wood grain, worn metal,
  stained canvas, chipped paint.
- **Warm light against cool ambient.** A huge share of the appeal in the night
  reference comes from warm window/lantern glow reading against deep blue
  moonlight. Emissive practicals (lit windows, lanterns, braziers, a lighthouse
  lamp) are doing heavy lifting — plan for them in the asset.
- **Layered depth.** Foreground, midground, background all present, with
  atmospheric haze separating the planes so the eye travels into the scene.
- **Believable construction.** Buildings have foundations, supports, railings,
  stairs, and clutter — barrels, crates, rope, hanging lanterns, laundry lines.
  The small props are what sell the scale of the big ones.

The stylized concept-art reference (chunky saturated rock, hand-painted look) is
the closest fit for this project's direction — keep that stylization, but with
the sculpted detail and material richness of the AAA shots. Stylized does **not**
mean simple.

> **Reference images:** drop the actual reference shots in `docs/reference/` and
> list them here, so this bar stays concrete instead of a description. The three
> that set the bar so far: a Sea of Thieves night outpost (warm lit windows under
> a moonlit skull-rock), a Skull and Bones daylight island (ship + layered cliff
> and arch formations), and a stylized hand-painted island concept (chunky
> saturated rock, the closest match to this project's look).

### Where the scene stands today (the gap to close)

Judged against the references above, from the live home view:

**Not all of this is an asset problem** — several of the biggest wins are
lighting and composition, and they are cheaper than remodeling anything.

- [ ] **Islands are flat green blobs.** Smooth low-poly shells with almost no
      vertical relief or silhouette interest. The references get their drama from
      stacked boulder masses, cliffs, sea arches, and real height. Ours read as
      pancakes with trees stuck on top.
- [ ] **No hero landmass and no depth layering.** Four islands of roughly equal
      size, evenly spaced along the horizon, all sitting on one plane at one
      scale. Nothing towers, nothing recedes. Needs a dominant hero island plus
      deliberate foreground/midground/background separation.
- [ ] **Lighting is washing the scene out.** Flat bright sky gradient with a
      blown-out horizon, flattening every surface. This is the single largest
      visual gap and it is NOT an asset problem. The night reference earns its
      mood almost entirely from warm practicals against deep blue ambient.
      Consider a dusk/night key with warm emissive windows and lanterns.
- [ ] **No atmospheric perspective.** Distant islands render at the same clarity
      and saturation as near ones, so the scene reads flat. Distance haze /
      desaturation would add depth for almost no cost.
- [ ] **Styles do not match each other.** The contact island is faceted low-poly,
      the projects island is denser and more detailed, and the ship is a third
      style again. They do not read as one world. Pick one style and bring
      everything to it.
- [ ] **Water is a flat blue sheet.** No foam at the shoreline, no wake detail,
      no depth-based color falloff. Shoreline foam alone would sell the islands
      as sitting *in* the water rather than on it.
- [ ] **Empty midground.** Large stretches of undifferentiated water. Sea stacks,
      rocks, wrecks, or buoys would give the eye something to travel across.

Rough order of impact per unit of effort: **lighting/atmosphere first**, then
island silhouettes, then shoreline/water, then individual props.

### Importing for reference vs. reusing

**Importing existing assets into Blender for reference is allowed and
encouraged.** Pull in the destination island, the ship, or any existing prop to
check scale, style, palette, and silhouette against what you are making. Seeing
the new asset beside the world it has to live in is the whole point.

**Reuse is also allowed** — a well-made sourced model (Sketchfab, Poly Pizza,
Quaternius; CC0 or permissive) is a legitimate route when it genuinely fits.

**But the default is to GENERATE something new, not to re-dress what is already
there.** Reference the existing assets to match the world; do not simply
duplicate, rescale, or recolor them and call it a new prop.

Use **top-notch materials.** Flat untextured color is what makes these read as
toys. Give surfaces real material character — proper roughness variation, wear
where wear belongs, weathering that follows exposure, subtle per-part tonal
variation. Wood should look like wood, metal like metal, bone like bone.

**The target is impressive, not cute.** These should look like crafted game art
someone would stop and look at — not like toys, not like programmer placeholders.
Aim high. If a choice is between safe-and-plain and ambitious-and-striking, take
the ambitious one.

### Technical constraints for any new GLB

- Author roughly 1 unit tall with the **base at the origin**, so it plants on
  terrain without a Y fudge and scales predictably.
- **Keep animation out of the GLB.** Motion lives in React `useFrame` so it can
  react to hover state. Export independently-moving parts as separately named
  child nodes and look them up by name.
- Procedural node materials **do not survive glTF export**. This is NOT a licence
  to ship flat untextured color — flat color is exactly what makes an asset read
  as a toy. Build the rich material in Blender, then **bake it down to texture
  maps** (base color / roughness / normal / AO) and export those. Baked maps are
  how a production-grade look survives the trip to the browser.
- Emissive does survive directly, via `KHR_materials_emissive_strength`.
- Keep texture sizes sane for the web (512-1024 is usually plenty at the size
  these render), and compress before committing using the pipeline in
  `CLAUDE.md` — textures, not geometry, are usually the cost.

### Coordinate note (Blender ↔ three.js)

If placing assets in Blender against an imported island:

- `blender (x, y, z)` maps to `three (x, -z, y)`
- A three.js `rotation.y` is a Blender rotation about `+Z`, but the handedness
  flips: `three_yaw = -blender_yaw`. Verify by transforming the prop's facing
  vector into three space and checking it points at the dock camera.
