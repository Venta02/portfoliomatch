"use client";

import { useState } from "react";
import {
  analyzeGitHub,
  getAllJobs,
  matchJobs,
  analyzeGap,
  UserProfile,
  MatchResult,
  GapAnalysisResponse,
} from "@/lib/api";
import { ProfileCard } from "@/components/ProfileCard";
import { MatchList } from "@/components/MatchList";
import { GapAnalysis } from "@/components/GapAnalysis";
import { LoadingState } from "@/components/LoadingState";
import { Hero } from "@/components/Hero";

type Stage = "idle" | "analyzing" | "matching" | "gap" | "done" | "error";

const STAGE_LABELS: Record<Stage, string> = {
  idle: "Analyze my GitHub",
  analyzing: "Reading your repositories",
  matching: "Computing job matches",
  gap: "Generating gap analysis",
  done: "Run again",
  error: "Try again",
};

const STAGE_HINTS: Record<Stage, string> = {
  idle: "",
  analyzing: "Parsing dependency files and detecting frameworks",
  matching: "Comparing your skills against job requirements with embeddings",
  gap: "Asking Gemini to identify priority skills and suggest projects",
  done: "",
  error: "",
};

export default function Home() {
  const [username, setUsername] = useState("");
  const [stage, setStage] = useState<Stage>("idle");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [gap, setGap] = useState<GapAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isProcessing = stage === "analyzing" || stage === "matching" || stage === "gap";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!username.trim() || isProcessing) return;

    setError(null);
    setProfile(null);
    setMatches([]);
    setGap(null);

    try {
      setStage("analyzing");
      const userProfile = await analyzeGitHub(username.trim());
      setProfile(userProfile);

      setStage("matching");
      const allJobs = await getAllJobs();
      const matchResponse = await matchJobs(userProfile, allJobs, 10);
      setMatches(matchResponse.matches);

      setStage("gap");
      const topJobs = matchResponse.matches.slice(0, 5).map((m) => m.job);
      if (topJobs.length > 0) {
        const gapResponse = await analyzeGap(userProfile, topJobs);
        setGap(gapResponse);
      }

      setStage("done");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      setStage("error");
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden">
      {/* Grid pattern overlay */}
      <div className="pointer-events-none fixed inset-0 bg-grid opacity-40" />

      {/* Top header bar */}
      <header className="relative z-10 border-b border-white/5 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 text-white font-bold text-sm">
              P
            </div>
            <span className="text-sm font-semibold tracking-tight">PortfolioMatch</span>
            <span className="ml-2 rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-zinc-400">
              v0.1
            </span>
          </div>
          <a
            href="https://github.com/Venta02/portfoliomatch"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-zinc-300 transition-colors hover:border-white/20 hover:bg-white/10"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="h-3.5 w-3.5">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </a>
        </div>
      </header>

      {/* Hero section (only when idle) */}
      {stage === "idle" && !profile && <Hero />}

      {/* Search section */}
      <section className="relative z-10 mx-auto max-w-3xl px-6 py-8">
        <form onSubmit={handleSubmit} className="relative">
          <div className="glass-strong relative overflow-hidden rounded-2xl border-white/10 p-2">
            <div className="flex items-center gap-2">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-zinc-800 to-zinc-900">
                <svg viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5 text-zinc-400">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter GitHub username (e.g., Venta02)"
                className="flex-1 bg-transparent px-2 py-3 text-base text-foreground placeholder-zinc-500 focus:outline-none disabled:cursor-not-allowed"
                disabled={isProcessing}
                autoFocus
              />
              <button
                type="submit"
                disabled={isProcessing || !username.trim()}
                className="btn-primary flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isProcessing ? (
                  <>
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.3"/>
                      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>
                    </svg>
                    {STAGE_LABELS[stage]}
                  </>
                ) : (
                  <>
                    {STAGE_LABELS[stage]}
                    <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>

          {STAGE_HINTS[stage] && (
            <div className="mt-3 flex items-center gap-2 px-2 text-xs text-zinc-500 fade-in-up">
              <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500"/>
              {STAGE_HINTS[stage]}
            </div>
          )}
        </form>

        {error && (
          <div className="fade-in-up mt-4 flex items-start gap-3 rounded-xl border border-rose-500/20 bg-rose-500/5 px-4 py-3 text-sm">
            <svg className="mt-0.5 h-4 w-4 flex-shrink-0 text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 8v4M12 16h.01"/>
            </svg>
            <div>
              <div className="font-medium text-rose-300">Something went wrong</div>
              <div className="mt-0.5 text-rose-400/80">{error}</div>
            </div>
          </div>
        )}
      </section>

      {/* Loading state when processing */}
      {isProcessing && !profile && (
        <section className="relative z-10 mx-auto max-w-3xl px-6 py-4">
          <LoadingState stage={stage} />
        </section>
      )}

      {/* Results */}
      <section className="relative z-10 mx-auto max-w-6xl px-6 pb-20">
        {profile && (
          <div className="fade-in-up mt-6">
            <ProfileCard profile={profile} />
          </div>
        )}

        {matches.length > 0 && (
          <div className="fade-in-up fade-in-up-delay-1 mt-12">
            <SectionHeader
              eyebrow="Step 02"
              title="Top job matches"
              description={`${matches.length} jobs ranked by skill match and semantic similarity`}
            />
            <div className="mt-6">
              <MatchList matches={matches} />
            </div>
          </div>
        )}

        {gap && (
          <div className="fade-in-up fade-in-up-delay-2 mt-12">
            <SectionHeader
              eyebrow="Step 03"
              title="Skill gap analysis"
              description="Honest assessment of what is missing and how to close the gaps"
            />
            <div className="mt-6">
              <GapAnalysis gap={gap} />
            </div>
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-4 px-6 py-6 sm:flex-row sm:items-center">
          <div className="text-xs text-zinc-500">
            Built by{" "}
            <a
              href="https://github.com/Venta02"
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-zinc-300 transition-colors hover:text-blue-400"
            >
              Embun Ventani
            </a>
            {" · "}
            <span>Open source under MIT license</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-zinc-500">
            <span>Powered by Gemini · sentence-transformers</span>
          </div>
        </div>
      </footer>
    </main>
  );
}

function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wider text-blue-400">
        {eyebrow}
      </div>
      <h2 className="mt-1 text-2xl font-bold tracking-tight">{title}</h2>
      <p className="mt-1 text-sm text-zinc-400">{description}</p>
    </div>
  );
}
