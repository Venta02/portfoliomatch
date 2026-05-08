import { UserProfile } from "@/lib/api";

export function ProfileCard({ profile }: { profile: UserProfile }) {
  const initials = (profile.name || profile.username)
    .split(/\s+/)
    .slice(0, 2)
    .map((s) => s[0])
    .join("")
    .toUpperCase();

  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wider text-blue-400">
        Step 01
      </div>
      <h2 className="mt-1 text-2xl font-bold tracking-tight">Profile detected</h2>
      <p className="mt-1 text-sm text-zinc-400">
        Skills extracted from {profile.repos.length} repositories
      </p>

      <div className="glass-strong card-hover mt-6 overflow-hidden rounded-2xl border-white/10">
        {/* Top section with avatar and identity */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-violet-500/10" />
          <div className="relative flex flex-col gap-4 p-6 sm:flex-row sm:items-start">
            <div className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-violet-600 text-xl font-bold text-white shadow-lg glow-blue">
              {initials}
            </div>

            <div className="flex-1">
              <div className="flex items-baseline gap-2">
                <h3 className="text-xl font-bold">{profile.name || profile.username}</h3>
                <a
                  href={`https://github.com/${profile.username}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-zinc-500 transition-colors hover:text-blue-400"
                >
                  @{profile.username}
                </a>
              </div>
              {profile.bio && (
                <p className="mt-1 text-sm text-zinc-400">{profile.bio}</p>
              )}
            </div>

            <div className="flex gap-2">
              <a
                href={`https://github.com/${profile.username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-zinc-300 transition-colors hover:border-white/20 hover:bg-white/10"
              >
                View GitHub →
              </a>
            </div>
          </div>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-px border-t border-white/5 bg-white/5 sm:grid-cols-4">
          <Stat label="Public repos" value={profile.public_repos} accent="blue" />
          <Stat label="Followers" value={profile.followers} accent="violet" />
          <Stat label="Analyzed" value={profile.repos.length} accent="emerald" />
          <Stat label="Skills" value={profile.aggregated_skills.length} accent="amber" />
        </div>

        {/* Skill summary */}
        {profile.skill_summary && (
          <div className="border-t border-white/5 p-6">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
              AI summary
            </div>
            <p className="text-sm leading-relaxed text-zinc-300">{profile.skill_summary}</p>
          </div>
        )}

        {/* Detected skills */}
        {profile.aggregated_skills.length > 0 && (
          <div className="border-t border-white/5 p-6">
            <div className="mb-3 flex items-center justify-between">
              <div className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Detected skills
              </div>
              <div className="text-xs text-zinc-500">
                {profile.aggregated_skills.length} total
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {profile.aggregated_skills.map((skill) => (
                <SkillTag key={skill} skill={skill} />
              ))}
            </div>
          </div>
        )}

        {/* Top repos */}
        {profile.repos.length > 0 && (
          <div className="border-t border-white/5 p-6">
            <div className="mb-3 flex items-center justify-between">
              <div className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Top repositories
              </div>
              <div className="text-xs text-zinc-500">
                Showing {Math.min(profile.repos.length, 4)}
              </div>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {profile.repos.slice(0, 4).map((repo) => (
                <RepoCard
                  key={repo.name}
                  name={repo.name}
                  description={repo.description}
                  stars={repo.stars}
                  url={repo.url}
                  frameworks={repo.frameworks}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent: "blue" | "violet" | "emerald" | "amber";
}) {
  const accentColors = {
    blue: "text-blue-400",
    violet: "text-violet-400",
    emerald: "text-emerald-400",
    amber: "text-amber-400",
  };

  return (
    <div className="bg-background-secondary p-4 text-center">
      <div className={`text-2xl font-bold ${accentColors[accent]}`}>{value}</div>
      <div className="mt-1 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
        {label}
      </div>
    </div>
  );
}

function SkillTag({ skill }: { skill: string }) {
  // Categorize skill for color
  const isLanguage = ["Python", "TypeScript", "JavaScript", "Rust", "Go", "Java", "C++", "Ruby"].includes(skill);
  const isML = ["PyTorch", "TensorFlow", "Keras", "scikit-learn", "Hugging Face Transformers"].some(s => skill.includes(s.split(" ")[0]));
  const isLLM = skill.includes("Gemini") || skill.includes("OpenAI") || skill.includes("Anthropic") || skill.includes("LangChain") || skill.includes("LangGraph");
  const isCV = ["OpenCV", "PaddleOCR", "YOLOv8", "YOLOv5", "MediaPipe", "EasyOCR"].includes(skill);

  let className = "border-white/10 bg-white/5 text-zinc-300";
  if (isLanguage) className = "border-blue-500/20 bg-blue-500/10 text-blue-300";
  else if (isML) className = "border-violet-500/20 bg-violet-500/10 text-violet-300";
  else if (isLLM) className = "border-emerald-500/20 bg-emerald-500/10 text-emerald-300";
  else if (isCV) className = "border-amber-500/20 bg-amber-500/10 text-amber-300";

  return (
    <span
      className={`skill-tag rounded-md border px-2 py-1 text-xs font-medium ${className}`}
    >
      {skill}
    </span>
  );
}

function RepoCard({
  name,
  description,
  stars,
  url,
  frameworks,
}: {
  name: string;
  description: string | null;
  stars: number;
  url: string;
  frameworks: string[];
}) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="group rounded-lg border border-white/5 bg-white/5 p-3 transition-all hover:border-white/15 hover:bg-white/10"
    >
      <div className="flex items-start justify-between">
        <div className="font-mono text-sm font-medium text-zinc-200 group-hover:text-blue-300">
          {name}
        </div>
        {stars > 0 && (
          <div className="flex items-center gap-0.5 text-xs text-zinc-500">
            <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            {stars}
          </div>
        )}
      </div>
      {description && (
        <p className="mt-1 line-clamp-2 text-xs text-zinc-400">{description}</p>
      )}
      {frameworks.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {frameworks.slice(0, 3).map((fw) => (
            <span
              key={fw}
              className="rounded border border-white/10 bg-white/5 px-1.5 py-0.5 text-[10px] text-zinc-400"
            >
              {fw}
            </span>
          ))}
          {frameworks.length > 3 && (
            <span className="text-[10px] text-zinc-500">+{frameworks.length - 3}</span>
          )}
        </div>
      )}
    </a>
  );
}
