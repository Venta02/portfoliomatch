import { GapAnalysisResponse } from "@/lib/api";

export function GapAnalysis({ gap }: { gap: GapAnalysisResponse }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-6">
      <p className="text-sm text-zinc-300">{gap.overall_assessment}</p>

      {gap.skill_priority_ranking.length > 0 && (
        <div className="mt-5">
          <div className="mb-2 text-xs uppercase text-zinc-500">Priority skills to learn</div>
          <ol className="space-y-1 text-sm">
            {gap.skill_priority_ranking.map((skill, i) => (
              <li key={skill} className="flex items-baseline gap-2">
                <span className="text-zinc-500">{i + 1}.</span>
                <span className="font-medium text-zinc-200">{skill}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {gap.suggested_projects.length > 0 && (
        <div className="mt-6">
          <div className="mb-3 text-xs uppercase text-zinc-500">Suggested projects</div>
          <div className="flex flex-col gap-3">
            {gap.suggested_projects.map((project) => (
              <div
                key={project.name}
                className="rounded-lg border border-zinc-800 bg-zinc-900 p-4"
              >
                <div className="flex items-baseline justify-between">
                  <h4 className="font-semibold text-zinc-100">{project.name}</h4>
                  <span className="text-xs text-zinc-500">
                    {project.estimated_weeks}w &middot; {project.difficulty}
                  </span>
                </div>
                <p className="mt-2 text-sm text-zinc-400">{project.description}</p>
                {project.skills_addressed.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {project.skills_addressed.map((s) => (
                      <span
                        key={s}
                        className="rounded border border-blue-800/40 bg-blue-950/30 px-2 py-0.5 text-xs text-blue-300"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
