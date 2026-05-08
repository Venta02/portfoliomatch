import { MatchResult } from "@/lib/api";

export function MatchList({ matches }: { matches: MatchResult[] }) {
  if (matches.length === 0) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center text-sm text-zinc-500">
        No matches found.
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {matches.map((match, index) => (
        <MatchCard key={match.job.id} match={match} rank={index + 1} />
      ))}
    </div>
  );
}

function MatchCard({ match, rank }: { match: MatchResult; rank: number }) {
  const { job, score, matched_skills, missing_skills } = match;
  const scorePercent = Math.round(score * 100);

  const scoreColor =
    score >= 0.7 ? "emerald" : score >= 0.5 ? "amber" : "rose";

  const colorMap = {
    emerald: {
      text: "text-emerald-400",
      bg: "bg-emerald-500/10",
      ring: "ring-emerald-500/40",
      stroke: "stroke-emerald-400",
      label: "Strong match",
    },
    amber: {
      text: "text-amber-400",
      bg: "bg-amber-500/10",
      ring: "ring-amber-500/40",
      stroke: "stroke-amber-400",
      label: "Partial match",
    },
    rose: {
      text: "text-rose-400",
      bg: "bg-rose-500/10",
      ring: "ring-rose-500/40",
      stroke: "stroke-rose-400",
      label: "Weak match",
    },
  };

  const colors = colorMap[scoreColor];

  return (
    <div className="glass card-hover group relative overflow-hidden rounded-2xl border-white/10 p-5">
      {/* Rank badge in corner */}
      <div className="absolute right-4 top-4 z-10 flex items-center gap-3">
        <ScoreCircle percent={scorePercent} colorClass={colors.stroke} />
      </div>

      <div className="pr-24">
        <div className="flex items-center gap-2">
          <span className="rounded bg-white/5 px-1.5 py-0.5 font-mono text-xs text-zinc-500">
            #{rank}
          </span>
          <span
            className={`rounded-full ${colors.bg} px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${colors.text}`}
          >
            {colors.label}
          </span>
        </div>

        <h3 className="mt-2 text-lg font-semibold leading-tight">{job.title}</h3>

        <div className="mt-1 flex items-center gap-2 text-sm text-zinc-400">
          <span className="font-medium text-zinc-300">{job.company}</span>
          <span className="text-zinc-600">·</span>
          <span className="flex items-center gap-1">
            <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
              <circle cx="12" cy="9" r="2.5"/>
            </svg>
            {job.location}
          </span>
        </div>
      </div>

      <p className="mt-3 line-clamp-2 text-sm text-zinc-400">{job.description}</p>

      {/* Skills section */}
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {matched_skills.length > 0 && (
          <div>
            <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
              <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              You have ({matched_skills.length})
            </div>
            <div className="flex flex-wrap gap-1">
              {matched_skills.map((s) => (
                <span
                  key={s}
                  className="rounded border border-emerald-500/20 bg-emerald-500/10 px-1.5 py-0.5 text-[11px] text-emerald-300"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {missing_skills.length > 0 && (
          <div>
            <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-amber-400">
              <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 9v4M12 17h.01" strokeLinecap="round"/>
                <circle cx="12" cy="12" r="10"/>
              </svg>
              Missing ({missing_skills.length})
            </div>
            <div className="flex flex-wrap gap-1">
              {missing_skills.map((s) => (
                <span
                  key={s}
                  className="rounded border border-amber-500/20 bg-amber-500/10 px-1.5 py-0.5 text-[11px] text-amber-300"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer with metadata */}
      <div className="mt-4 flex items-center justify-between border-t border-white/5 pt-3 text-xs text-zinc-500">
        <div className="flex items-center gap-3">
          {job.experience_years !== null && (
            <span className="flex items-center gap-1">
              <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2"/>
                <path d="M16 2v4M8 2v4M3 10h18"/>
              </svg>
              {job.experience_years}+ years
            </span>
          )}
          {job.salary_range && (
            <span className="flex items-center gap-1">
              <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
              </svg>
              {job.salary_range}
            </span>
          )}
        </div>
        {job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 font-medium text-blue-400 transition-colors hover:text-blue-300"
          >
            View posting
            <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M7 17L17 7M17 7H7M17 7v10" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}

function ScoreCircle({
  percent,
  colorClass,
}: {
  percent: number;
  colorClass: string;
}) {
  const circumference = 2 * Math.PI * 28;
  const dashOffset = circumference - (percent / 100) * circumference;

  return (
    <div className="relative flex h-16 w-16 items-center justify-center">
      <svg className="h-16 w-16 -rotate-90" viewBox="0 0 64 64">
        {/* Background circle */}
        <circle
          cx="32"
          cy="32"
          r="28"
          fill="none"
          stroke="currentColor"
          strokeWidth="4"
          className="text-white/10"
        />
        {/* Progress circle */}
        <circle
          cx="32"
          cy="32"
          r="28"
          fill="none"
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          className={`${colorClass} transition-all duration-1000 ease-out`}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <div className={`text-base font-bold leading-none ${colorClass.replace("stroke-", "text-")}`}>
            {percent}
          </div>
          <div className="text-[8px] font-medium text-zinc-500">match</div>
        </div>
      </div>
    </div>
  );
}
