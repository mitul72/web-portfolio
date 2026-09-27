import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import type { WebGLRenderer } from "three";
import type { GLTFLoader, KTX2Loader as StdlibKTX2Loader } from "three-stdlib";

/**
 * Where the GLB decoders are served from. drei's default is Google's CDN,
 * which puts a third-party DNS + TLS handshake in front of the first model;
 * these are copies of three's own builds in /public (refreshed by
 * `npm run assets`, so they stay in step with the installed three).
 */
export const DRACO_PATH = "/draco/";
const BASIS_PATH = "/basis/";

let ktx2: KTX2Loader | null = null;

/**
 * GLTFLoader extension for a model with KTX2 (Basis Universal) textures: the
 * world's island albedos. They stay block-compressed on the GPU (about 6x
 * less texture memory than WebP decoded to RGBA) and transcode in a worker
 * instead of decoding on the main thread. Picking the GPU format needs the
 * renderer, so a model that uses this can't be `useGLTF.preload`ed at module
 * level; load it inside the Canvas.
 */
export function ktx2Textures(gl: WebGLRenderer) {
  return (loader: GLTFLoader) => {
    if (!ktx2) ktx2 = new KTX2Loader().setTranscoderPath(BASIS_PATH).detectSupport(gl);
    // three's loader, matched to the transcoder we ship, behind three-stdlib's type.
    loader.setKTX2Loader(ktx2 as unknown as StdlibKTX2Loader);
  };
}
