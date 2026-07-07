import type { Metadata } from "next";
import Link from "next/link";
import { INTRO, RESUME, CONTACT, PROJECTS, JOBS } from "@/data/portfolio";

export const metadata: Metadata = {
  title: "Mitul Dhawan · Portfolio",
  description:
    "Software engineer — projects, experience, and resume. A fast, simple view of my portfolio.",
};

/** Only show projects that actually have detail (skip hub overview stubs). */
const projects = PROJECTS.filter(
  (p) => p.tech.length > 0 || p.links.length > 0
);

const name = INTRO?.name ?? "Mitul Dhawan";
const tagline = INTRO?.tagline ?? "Software Engineer";

function LinkPill({
  label,
  url,
  accent = "border-white/20 hover:bg-white/10",
}: {
  label: string;
  url: string;
  accent?: string;
}) {
  return (
    <a
      href={url}
      target={url.startsWith("http") ? "_blank" : undefined}
      rel="noopener noreferrer"
      className={`inline-flex items-center rounded-full border px-4 py-1.5 text-sm transition ${accent}`}
    >
      {label} ↗
    </a>
  );
}

/**
 * Static 2D fallback portfolio — no WebGL, instant load, fully responsive.
 * Reads the SAME data as the 3D scene (src/data/portfolio.ts) so the two views
 * stay in sync. Reachable at /lite; the 3D page links here and vice versa.
 */
export default function LitePortfolio() {
  return (
    <main className="min-h-[100dvh] bg-slate-950 text-white">
      <div className="mx-auto max-w-3xl px-5 py-14 sm:px-8 sm:py-20">
        {/* Header */}
        <header className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-amber-300">
              {tagline}
            </p>
            <h1 className="mt-2 text-4xl font-black tracking-tight sm:text-5xl">
              {name}
            </h1>
          </div>
          <Link
            href="/"
            className="shrink-0 rounded-full border border-white/20 px-3 py-1.5 text-xs text-white/70 transition hover:bg-white/10 hover:text-white sm:text-sm"
          >
            ⚓ 3D experience
          </Link>
        </header>

        {/* Intro / bio */}
        {INTRO && (
          <p className="mt-6 max-w-2xl leading-relaxed text-white/70">
            {INTRO.blurb}
          </p>
        )}

        {/* Quick actions */}
        <div className="mt-6 flex flex-wrap gap-3">
          {RESUME && (
            <a
              href={RESUME.pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-full bg-amber-400 px-5 py-2 text-sm font-semibold text-black transition hover:bg-amber-300"
            >
              Download Resume ↗
            </a>
          )}
          {CONTACT?.links.map((l) => (
            <LinkPill key={l.url} label={l.label} url={l.url} />
          ))}
        </div>

        {/* Projects */}
        {projects.length > 0 && (
          <section className="mt-14">
            <h2 className="text-sm font-semibold uppercase tracking-[0.25em] text-white/40">
              Projects
            </h2>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {projects.map((p) => (
                <article
                  key={p.title}
                  className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-white/20"
                >
                  <h3 className="text-lg font-bold">{p.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-white/70">
                    {p.description}
                  </p>
                  {p.tech.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {p.tech.map((t) => (
                        <span
                          key={t}
                          className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-2.5 py-0.5 text-xs text-cyan-200"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                  {p.links.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {p.links.map((l) => (
                        <LinkPill key={l.url} label={l.label} url={l.url} />
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </div>
          </section>
        )}

        {/* Experience */}
        {JOBS.length > 0 && (
          <section className="mt-14">
            <h2 className="text-sm font-semibold uppercase tracking-[0.25em] text-white/40">
              Experience
            </h2>
            <div className="mt-5 space-y-6">
              {JOBS.map((job, i) => (
                <div key={i}>
                  <h3 className="text-lg font-bold">{job.role}</h3>
                  <p className="text-sm text-emerald-300">
                    {job.company} ·{" "}
                    <span className="text-white/50">{job.period}</span>
                  </p>
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-white/70">
                    {job.bullets.map((b, j) => (
                      <li key={j}>{b}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Footer / contact */}
        {CONTACT && (
          <footer className="mt-16 border-t border-white/10 pt-8">
            <p className="text-white/60">{CONTACT.blurb}</p>
            <div className="mt-4 flex flex-wrap gap-3">
              {CONTACT.links.map((l) => (
                <LinkPill key={l.url} label={l.label} url={l.url} />
              ))}
            </div>
          </footer>
        )}
      </div>
    </main>
  );
}
