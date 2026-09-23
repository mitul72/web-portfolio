"use client";

import { useEffect, useState } from "react";
import { NPCS } from "@/data/interact";
import { useInteract } from "@/components/tour/useInteract";
import { runDialogueAction } from "@/components/tour/activate";

/**
 * An NPC's conversation: name and role, their lines typed out, and the
 * choices, which lead into the island's content (or on to another island).
 * Sits at the bottom centre, over the scene, like a game's dialogue box.
 */
export default function NpcDialogue() {
  const id = useInteract((s) => s.dialogue);
  const close = useInteract((s) => s.closeDialogue);
  const npc = id ? NPCS[id] : null;
  const text = npc ? npc.lines.join(" ") : "";
  const [shown, setShown] = useState(0);

  // Typewriter, fast enough not to be a chore; click the box to skip it.
  useEffect(() => {
    setShown(0);
    if (!text) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setShown(text.length);
      return;
    }
    const iv = window.setInterval(() => {
      setShown((n) => {
        if (n >= text.length) {
          window.clearInterval(iv);
          return n;
        }
        return n + 2;
      });
    }, 16);
    return () => window.clearInterval(iv);
  }, [text]);

  useEffect(() => {
    if (!npc) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && close();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [npc, close]);

  if (!npc) return null;
  const done = shown >= text.length;

  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-6 z-30 flex justify-center px-4">
      <div
        role="dialog"
        aria-label={`${npc.name}, ${npc.role}`}
        className="pointer-events-auto w-full max-w-xl rounded-2xl border border-amber-200/25 bg-slate-950/85 p-5 text-white shadow-2xl backdrop-blur-xl"
        onClick={() => setShown(text.length)}
      >
        <div className="flex items-baseline justify-between gap-4">
          <p>
            <span className="text-lg font-bold text-amber-200">{npc.name}</span>
            <span className="ml-2 text-xs uppercase tracking-widest text-white/50">{npc.role}</span>
          </p>
          <button
            onClick={(e) => {
              e.stopPropagation();
              close();
            }}
            aria-label="Close"
            className="rounded-full px-2 text-white/60 transition hover:bg-white/10 hover:text-white"
          >
            ✕
          </button>
        </div>
        <p className="mt-2 min-h-[3.5rem] leading-relaxed text-white/85" aria-live="polite">
          {text.slice(0, shown)}
          {!done && <span className="animate-pulse">▍</span>}
        </p>
        <div className={`mt-4 flex flex-wrap gap-2 transition-opacity ${done ? "opacity-100" : "opacity-0"}`}>
          {npc.options.map((o) => (
            <button
              key={o.label}
              disabled={!done}
              onClick={(e) => {
                e.stopPropagation();
                runDialogueAction(o.action);
              }}
              className="rounded-full border border-amber-300/40 bg-amber-300/10 px-4 py-1.5 text-sm font-medium text-amber-100 transition hover:bg-amber-300/25"
            >
              {o.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
