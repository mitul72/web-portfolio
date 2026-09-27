/**
 * The loading screen's look, with nothing from three.js in it. page.tsx shows
 * it while the 3D bundle itself is still downloading; once that bundle runs,
 * LoadingScreen renders the same markup with the real asset progress, so the
 * hand-off is invisible.
 */
export default function LoadingShell({ progress, fading = false }: { progress: number; fading?: boolean }) {
  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-950 text-white transition-opacity duration-500 ${
        fading ? "opacity-0" : "opacity-100"
      }`}
    >
      <div className="text-4xl">⚓</div>
      <p className="mt-4 text-sm uppercase tracking-[0.3em] text-white/60">
        Charting the waters
      </p>
      <div className="mt-6 h-1.5 w-56 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-amber-400 transition-[width] duration-300"
          style={{ width: `${Math.min(100, progress)}%` }}
        />
      </div>
      <p className="mt-2 text-xs text-white/40">{Math.round(progress)}%</p>
    </div>
  );
}
