type Stage = "idle" | "analyzing" | "matching" | "gap" | "done" | "error";

const STAGES = [
  { key: "analyzing", label: "Analyze repositories", description: "Reading dependency files" },
  { key: "matching", label: "Match against jobs", description: "Computing semantic similarity" },
  { key: "gap", label: "Generate gap analysis", description: "AI-powered recommendations" },
] as const;

export function LoadingState({ stage }: { stage: Stage }) {
  return (
    <div className="glass-strong fade-in-up rounded-2xl border-white/10 p-6">
      <div className="space-y-4">
        {STAGES.map((s, idx) => {
          const currentIdx = STAGES.findIndex((x) => x.key === stage);
          const stageIdx = idx;
          const status: "pending" | "active" | "done" =
            stageIdx < currentIdx ? "done" : stageIdx === currentIdx ? "active" : "pending";

          return <StageRow key={s.key} stage={s} status={status} />;
        })}
      </div>
    </div>
  );
}

function StageRow({
  stage,
  status,
}: {
  stage: { label: string; description: string };
  status: "pending" | "active" | "done";
}) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex-shrink-0">
        {status === "done" && (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/20 ring-1 ring-emerald-500/40">
            <svg className="h-4 w-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
              <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        )}
        {status === "active" && (
          <div className="relative flex h-8 w-8 items-center justify-center">
            <div className="absolute inset-0 rounded-full bg-blue-500/20" />
            <svg className="h-5 w-5 animate-spin text-blue-400" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.3"/>
              <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>
            </svg>
          </div>
        )}
        {status === "pending" && (
          <div className="flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/5">
            <div className="h-2 w-2 rounded-full bg-zinc-600" />
          </div>
        )}
      </div>

      <div className="flex-1">
        <div
          className={`text-sm font-medium ${
            status === "active" ? "text-foreground" : status === "done" ? "text-emerald-300" : "text-zinc-500"
          }`}
        >
          {stage.label}
        </div>
        <div className="text-xs text-zinc-500">{stage.description}</div>
      </div>

      {status === "active" && (
        <div className="hidden text-xs text-zinc-400 sm:block">In progress...</div>
      )}
      {status === "done" && (
        <div className="hidden text-xs text-emerald-400 sm:block">Done</div>
      )}
    </div>
  );
}
