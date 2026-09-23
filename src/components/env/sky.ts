// -----------------------------------------------------------------------------
// Single source of truth for the time of day in the app. Everything here is
// derived from src/data/world.ts, which Blender GENERATES alongside the sky
// panorama (blender/export_world.py), so the key light, the sky's sun disc and
// the fog are the same ones the approved renders were lit with.
// -----------------------------------------------------------------------------

import { Color, Vector3 } from "three";
import { FOG_COLOR as FOG_RGB, FOG_DENSITY as FOG_K, KEY_COLOR, KEY_DIR, KEY_INTENSITY } from "@/data/world";

/** Unit vector TO the key light. */
export const SUN_DIRECTION = new Vector3(...KEY_DIR).normalize();

/** Linear colour + intensity (same units as Blender's sun strength). */
export const KEY_LIGHT_COLOR = new Color().setRGB(...KEY_COLOR);
export const KEY_LIGHT_INTENSITY = KEY_INTENSITY;

/**
 * FogExp2 matching the Blender renders (materials.fogged uses the same curve).
 * The colour is linear; everything is tone mapped after fog, as in Blender.
 */
export const FOG_COLOR = new Color().setRGB(...FOG_RGB);
export const FOG_DENSITY = FOG_K;
