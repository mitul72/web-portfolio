import { useThree } from "@react-three/fiber";
import { useEffect } from "react";
import { Raycaster, Vector2 } from "three";

/**
 * DEV-ONLY helper for placing assets/markers without guessing coordinates.
 *
 * Enable it by setting SHOW_DEV_COORDS = true in page.tsx. Then:
 *   - Click anywhere on the scene → logs the exact world (x, y, z) you hit.
 *   - Press "c" → logs the current camera position + where it's looking.
 * Copy those numbers straight into portfolio.ts. Turn it off before shipping.
 */
export default function DevCoords() {
  const { camera, scene, gl } = useThree();

  useEffect(() => {
    const raycaster = new Raycaster();
    const pointer = new Vector2();
    const el = gl.domElement;

    const onClick = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObjects(scene.children, true);
      if (hits.length) {
        const p = hits[0].point;
        // eslint-disable-next-line no-console
        console.log(
          `[world hit] position: [${p.x.toFixed(2)}, ${p.y.toFixed(
            2
          )}, ${p.z.toFixed(2)}]  (mesh: ${hits[0].object.name || "unnamed"})`
        );
      }
    };

    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "c") return;
      const p = camera.position;
      // eslint-disable-next-line no-console
      console.log(
        `[camera] position: [${p.x.toFixed(2)}, ${p.y.toFixed(2)}, ${p.z.toFixed(
          2
        )}]  rotation: [${camera.rotation.x.toFixed(
          3
        )}, ${camera.rotation.y.toFixed(3)}, ${camera.rotation.z.toFixed(3)}]`
      );
    };

    el.addEventListener("click", onClick);
    window.addEventListener("keydown", onKey);
    // eslint-disable-next-line no-console
    console.log(
      "%c[DevCoords] ON — click scene to log world coords, press 'c' for camera",
      "color:#ffb703"
    );
    return () => {
      el.removeEventListener("click", onClick);
      window.removeEventListener("keydown", onKey);
    };
  }, [camera, scene, gl]);

  return null;
}
