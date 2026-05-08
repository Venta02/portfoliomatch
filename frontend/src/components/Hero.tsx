export function Hero() {
  return (
    <section className="relative z-10 mx-auto max-w-3xl px-6 pt-12 pb-4 text-center">
      <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-zinc-400 backdrop-blur-sm fade-in-up">
        <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-400 pulse-glow" />
        AI-powered job matching for engineers
      </div>

      <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-5xl fade-in-up fade-in-up-delay-1">
        Your{" "}
        <span className="text-gradient">GitHub code</span>
        <br />
        speaks louder than your resume.
      </h1>

      <p className="mx-auto mt-5 max-w-xl text-base text-zinc-400 fade-in-up fade-in-up-delay-2">
        PortfolioMatch reads your repos, detects your real skills, and matches you to
        jobs in SEA and remote markets. With honest gap analysis included.
      </p>

      <div className="mt-8 flex items-center justify-center gap-6 text-xs text-zinc-500 fade-in-up fade-in-up-delay-3">
        <FeaturePill icon="📦" label="60+ frameworks detected" />
        <FeaturePill icon="" label="20 curated jobs" />
        <FeaturePill icon="" label="Gemini-powered" />
      </div>
    </section>
  );
}

function FeaturePill({ icon, label }: { icon: string; label: string }) {
  return (
    <div className="hidden items-center gap-1.5 sm:flex">
      <span>{icon}</span>
      <span>{label}</span>
    </div>
  );
}
