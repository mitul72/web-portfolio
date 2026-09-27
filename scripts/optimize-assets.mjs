#!/usr/bin/env node
/**
 * Post-processes the committed 3D assets in place. Idempotent: run it after a
 * Blender export (blender/export_world.py, export_ship.py, extract_chest.py)
 * or after upgrading three, then commit what changed.
 *
 *   npm run assets              # every step
 *   npm run assets -- npcs      # one or more steps by name
 *
 * Steps
 *   decoders  copy three's Draco decoder + Basis transcoder into public/, so
 *             they're served first-party and match the installed three
 *   world     island albedo textures -> ETC1S KTX2 (block-compressed on the
 *             GPU, ~6x less texture memory than WebP decoded to RGBA). Needs
 *             KTX-Software's `ktx` on PATH (github.com/KhronosGroup/KTX-Software
 *             releases); skipped with a warning when it isn't installed.
 *   npcs      drop the pirate-kit clips the app never plays (each file shipped
 *             14; it plays Idle, Wave and Yes), resample the rest, shrink the
 *             captain's flat-colour atlas to the 32x32 the other NPCs use
 *             (nearest: one exact source pixel per cell)
 *   chest     strip KHR_materials_transmission (one transmissive material
 *             makes three render the whole opaque scene twice per frame), cap
 *             the coin pile and chest body at a triangle budget (once: a mesh
 *             is marked in its extras so re-runs never decimate it again)
 *   shore     public/world/shore.png -> 1024x1024 single channel (1 m/texel;
 *             the shader reads one channel, and 2048 RGB was 16.8 MB on the GPU)
 */
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, renameSync, statSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Logger, NodeIO } from "@gltf-transform/core";
import { ALL_EXTENSIONS, KHRMaterialsTransmission } from "@gltf-transform/extensions";
import { dedup, draco, prune, resample, simplifyPrimitive, textureCompress, weld } from "@gltf-transform/functions";
import { ETC1S_DEFAULTS, Mode, toktx } from "@gltf-transform/cli";
import draco3d from "draco3dgltf";
import { MeshoptSimplifier } from "meshoptimizer";
import sharp from "sharp";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const rel = (p) => path.relative(ROOT, p);
const abs = (p) => path.join(ROOT, p);
const kb = (p) => `${(statSync(p).size / 1024).toFixed(0)} KB`;

const WORLD = abs("src/assets/world-transformed.glb");
const NPC_DIR = abs("src/assets/npcs");
const CHEST = abs("src/assets/treasure-chest.glb");
const SHORE = abs("public/world/shore.png");

/** Clips the app plays (models/npcs.tsx, models/ship.tsx). */
const KEEP_CLIPS = new Set(["Idle", "Wave", "Yes"]);
/**
 * Chest meshes by glTF name -> triangle budget and the error bound (a fraction
 * of the mesh radius, ~1 m here) that may stop short of it. The coins are a
 * pile of ~3 cm discs seen from a few metres, so they get a looser bound.
 */
const CHEST_BUDGET = {
  "treasure chest_individual coins_0": { budget: 8500, error: 0.006 },
  "treasure chest_cheast_0": { budget: 10500, error: 0.002 },
};
/**
 * ETC1S settings for the world albedos. Measured on the home rock (2048^2,
 * 264 KB as WebP): q128 477 KB / 37.2 dB, q160 534 KB / 37.9 dB, q255 601 KB /
 * 38.6 dB against the WebP. The curve is flat above 160, so that is the pick.
 */
const ETC1S = { quality: 160, compression: 2 };

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  "draco3d.decoder": await draco3d.createDecoderModule(),
  "draco3d.encoder": await draco3d.createEncoderModule(),
});
const logger = new Logger(Logger.Verbosity.WARN);

const triangles = (doc) =>
  doc
    .getRoot()
    .listMeshes()
    .flatMap((m) => m.listPrimitives())
    .reduce((n, p) => n + (p.getIndices() ? p.getIndices().getCount() : p.getAttribute("POSITION").getCount()) / 3, 0);

async function read(file) {
  const doc = await io.read(file);
  doc.setLogger(logger);
  return doc;
}

async function write(file, doc, before) {
  await io.write(file, doc);
  console.log(`  ${rel(file)}: ${before} -> ${kb(file)}`);
}

// ---------------------------------------------------------------------------
async function decoders() {
  const pairs = [
    ["node_modules/three/examples/jsm/libs/draco/gltf/draco_decoder.js", "public/draco/draco_decoder.js"],
    ["node_modules/three/examples/jsm/libs/draco/gltf/draco_decoder.wasm", "public/draco/draco_decoder.wasm"],
    ["node_modules/three/examples/jsm/libs/draco/gltf/draco_wasm_wrapper.js", "public/draco/draco_wasm_wrapper.js"],
    ["node_modules/three/examples/jsm/libs/basis/basis_transcoder.js", "public/basis/basis_transcoder.js"],
    ["node_modules/three/examples/jsm/libs/basis/basis_transcoder.wasm", "public/basis/basis_transcoder.wasm"],
  ];
  for (const [from, to] of pairs) {
    const same = existsSync(abs(to)) && readFileSync(abs(from)).equals(readFileSync(abs(to)));
    if (same) continue;
    mkdirSync(path.dirname(abs(to)), { recursive: true });
    copyFileSync(abs(from), abs(to));
    console.log(`  ${to}: updated from three`);
  }
}

// ---------------------------------------------------------------------------
function hasKtx() {
  try {
    execFileSync("ktx", ["--version"], { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

async function world() {
  const doc = await read(WORLD);
  const pending = doc.getRoot().listTextures().filter((t) => t.getMimeType() !== "image/ktx2");
  if (pending.length === 0) {
    console.log("  world: textures already KTX2");
    return;
  }
  if (!hasKtx()) {
    console.warn("  world: SKIPPED. `ktx` (KTX-Software 4.3+) is not on PATH, so the albedos stay WebP.");
    return;
  }
  const before = kb(WORLD);
  await doc.transform(
    // ktx only reads PNG/JPEG, so decode the WebP losslessly first.
    textureCompress({ encoder: sharp, targetFormat: "png", formats: /webp/ }),
    toktx({ ...ETC1S_DEFAULTS, mode: Mode.ETC1S, encoder: sharp, jobs: os.cpus().length, ...ETC1S }),
    draco()
  );
  await write(WORLD, doc, before);
}

// ---------------------------------------------------------------------------
async function npcs() {
  for (const name of readdirSync(NPC_DIR).filter((f) => f.endsWith(".glb")).sort()) {
    const file = path.join(NPC_DIR, name);
    const before = kb(file);
    const doc = await read(file);
    const bigAtlas = doc.getRoot().listTextures().some((t) => (t.getSize() ?? [0])[0] > 32);
    if (!bigAtlas && doc.getRoot().listAnimations().every((a) => KEEP_CLIPS.has(a.getName()))) {
      console.log(`  ${rel(file)}: already done`);
      continue;
    }
    // The kit's 1024^2 atlas is a 32x32 grid of flat colour cells, so one texel
    // per cell is lossless if each texel is one source pixel (nearest). A filter
    // kernel that spans neighbouring cells bleeds their colours in (measured up
    // to 51/255 with lanczos).
    for (const t of doc.getRoot().listTextures()) {
      if (!/atlas/i.test(t.getName()) || (t.getSize() ?? [0])[0] <= 32) continue;
      const png = await sharp(Buffer.from(t.getImage())).resize(32, 32, { kernel: "nearest" }).png().toBuffer();
      t.setImage(new Uint8Array(png)).setMimeType("image/png");
    }
    let dropped = 0;
    for (const anim of doc.getRoot().listAnimations()) {
      if (KEEP_CLIPS.has(anim.getName())) continue;
      anim.listChannels().forEach((c) => c.dispose());
      anim.listSamplers().forEach((s) => s.dispose());
      anim.dispose();
      dropped++;
    }
    await doc.transform(resample(), prune(), dedup(), draco());
    const clips = doc.getRoot().listAnimations().map((a) => a.getName()).join(", ");
    await write(file, doc, before);
    console.log(`    dropped ${dropped} clips; kept ${clips}`);
  }
}

// ---------------------------------------------------------------------------
async function chest() {
  const before = kb(CHEST);
  const doc = await read(CHEST);
  const root = doc.getRoot();
  const trisBefore = triangles(doc);
  const transmissive = root.listExtensionsUsed().some((e) => e.extensionName === KHRMaterialsTransmission.EXTENSION_NAME);
  const unsimplified = root.listMeshes().some((m) => CHEST_BUDGET[m.getName()] && !m.getExtras().simplified);
  if (!transmissive && !unsimplified) {
    console.log("  chest: already done");
    return;
  }

  for (const m of root.listMaterials()) m.setExtension(KHRMaterialsTransmission.EXTENSION_NAME, null);
  root
    .listExtensionsUsed()
    .filter((e) => e.extensionName === KHRMaterialsTransmission.EXTENSION_NAME)
    .forEach((e) => e.dispose());

  await doc.transform(weld());
  await MeshoptSimplifier.ready;
  for (const mesh of root.listMeshes()) {
    const target = CHEST_BUDGET[mesh.getName()];
    if (!target || mesh.getExtras().simplified) continue;
    for (const prim of mesh.listPrimitives()) {
      const tris = prim.getIndices().getCount() / 3;
      if (tris <= target.budget) continue;
      simplifyPrimitive(prim, { simplifier: MeshoptSimplifier, ratio: target.budget / tris, error: target.error });
      console.log(`    ${mesh.getName()}: ${tris} -> ${prim.getIndices().getCount() / 3} triangles`);
    }
    mesh.setExtras({ ...mesh.getExtras(), simplified: true });
  }
  // prune() would also fold a single-colour texture into a factor; the chest's
  // small ones turned out not to be flat, so today it only drops orphans.
  await doc.transform(prune(), dedup(), resample(), draco());
  const textures = root.listTextures().length;
  await write(CHEST, doc, before);
  console.log(`    ${trisBefore} -> ${triangles(doc)} triangles, ${textures} textures, transmission removed`);
}

// ---------------------------------------------------------------------------
async function shore() {
  const meta = await sharp(SHORE).metadata();
  if (meta.width <= 1024 && meta.channels === 1) {
    console.log("  shore: already 1024x1024 single channel");
    return;
  }
  const before = kb(SHORE);
  const tmp = SHORE + ".tmp.png";
  // Resize the field itself (no gamma: it's distances), then keep one channel.
  await sharp(SHORE).resize(1024, 1024, { kernel: "lanczos3" }).extractChannel(0).png({ compressionLevel: 9 }).toFile(tmp);
  renameSync(tmp, SHORE);
  console.log(`  ${rel(SHORE)}: ${meta.width}x${meta.height}x${meta.channels} ${before} -> 1024x1024x1 ${kb(SHORE)}`);
}

// ---------------------------------------------------------------------------
const STEPS = { decoders, world, npcs, chest, shore };
const wanted = process.argv.slice(2);
for (const name of wanted.length ? wanted : Object.keys(STEPS)) {
  if (!STEPS[name]) {
    console.error(`unknown step "${name}"; steps: ${Object.keys(STEPS).join(", ")}`);
    process.exit(1);
  }
  console.log(`[${name}]`);
  await STEPS[name]();
}
