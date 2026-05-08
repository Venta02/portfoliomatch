const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RepoSummary {
  name: string;
  description: string | null;
  languages: Record<string, number>;
  frameworks: string[];
  stars: number;
  topics: string[];
  url: string;
}

export interface UserProfile {
  username: string;
  name: string | null;
  bio: string | null;
  public_repos: number;
  followers: number;
  repos: RepoSummary[];
  aggregated_skills: string[];
  skill_summary: string;
}

export interface JobPosting {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string[];
  skills_required: string[];
  experience_years: number | null;
  salary_range: string | null;
  url: string | null;
  source: string;
}

export interface MatchResult {
  job: JobPosting;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  reasoning: string | null;
}

export interface MatchResponse {
  matches: MatchResult[];
  total_jobs_evaluated: number;
}

export interface ProjectSuggestion {
  name: string;
  description: string;
  skills_addressed: string[];
  estimated_weeks: number;
  difficulty: string;
}

export interface GapAnalysisResponse {
  common_missing_skills: string[];
  skill_priority_ranking: string[];
  suggested_projects: ProjectSuggestion[];
  overall_assessment: string;
}

export interface HealthResponse {
  status: string;
  github_available: boolean;
  gemini_available: boolean;
  embedding_model: string;
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json();
}

export async function analyzeGitHub(username: string, maxRepos = 10): Promise<UserProfile> {
  return postJSON("/api/analyze", { github_username: username, max_repos: maxRepos });
}

export async function getAllJobs(): Promise<JobPosting[]> {
  return getJSON("/api/jobs");
}

export async function searchJobs(
  keywords: string[],
  location?: string,
  limit = 20
): Promise<JobPosting[]> {
  return postJSON("/api/jobs/search", { role_keywords: keywords, location, limit });
}

export async function matchJobs(
  profile: UserProfile,
  jobs: JobPosting[],
  topK = 10
): Promise<MatchResponse> {
  return postJSON("/api/match", { profile, jobs, top_k: topK });
}

export async function analyzeGap(
  profile: UserProfile,
  targetJobs: JobPosting[]
): Promise<GapAnalysisResponse> {
  return postJSON("/api/gap", { profile, target_jobs: targetJobs });
}

export async function getHealth(): Promise<HealthResponse> {
  return getJSON("/api/health");
}
