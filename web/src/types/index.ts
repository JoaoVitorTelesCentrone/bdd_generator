export interface Model {
  id: string;
  name: string;
  provider: "groq" | "gemini" | "claude";
  default?: boolean;
  free?: boolean;
}

export interface ScoreResult {
  cobertura: float;
  clareza: float;
  estrutura: float;
  executabilidade: float;
  score_final: float;
  aprovado: boolean;
  threshold: float;
}

export interface GenerateResult {
  bdd_text: string;
  score: ScoreResult;
  attempts: number;
  total_tokens: number;
  research_tokens: number;
  converged: boolean;
  duration_seconds: number;
}

export interface GenerateRequest {
  story: string;
  model: string;
  threshold: number;
  max_attempts: number;
  research: boolean;
  until_converged: boolean;
}

export interface EvaluateRequest {
  story: string;
  bdd_text: string;
  threshold: number;
}

// Fix: TypeScript doesn't have a "float" type — use number
type float = number;

// ── BIST run types ────────────────────────────────────────────────────────────

export interface BistRunSummary {
  id: number;
  started_at: number;
  finished_at?: number | null;
  env_url: string;
  status: "running" | "passed" | "failed" | "error";
  duration_ms: number;
  feature_path: string;
}

export interface BistExecuteRequest {
  feature_path: string;
  env_url: string;
}

export interface BistStep {
  id: number;
  scenario_id: number;
  step_text: string;
  status: "passed" | "failed" | "skipped";
  duration_ms: number;
  screenshot_path: string;
}

export interface BistScenario {
  id: number;
  run_id: number;
  name: string;
  status: "passed" | "failed" | "skipped";
  duration_ms: number;
  error: string;
  video_path: string;
  steps: BistStep[];
}

export interface BistRunDetail extends BistRunSummary {
  scenarios: BistScenario[];
}

export interface BistFlakyScenario {
  name: string;
  total_runs: number;
  failures: number;
  failure_rate: number;
}

export interface BistStats {
  total_runs: number;
  passed_runs: number;
  failed_runs: number;
  pass_rate: number;
  avg_duration_ms: number;
  flaky_scenarios: BistFlakyScenario[];
  runs_over_time: Array<{ date: string; passed: number; failed: number }>;
}

export interface BistRunRequest {
  user_story: string;
  env_url: string;
  model?: string;
  threshold?: number;
  max_attempts?: number;
}

// ── Story Creator ─────────────────────────────────────────────────────────────

export interface StoryCreateRequest {
  idea: string;
  model: string;
}

export interface StoryCreateResult {
  user_story: string;
  acceptance_criteria: string[];
}

// ── Unit Tests ────────────────────────────────────────────────────────────────

export interface UnitTestRequest {
  bdd_text: string;
  language: string;
  framework: string;
  model?: string;
}

export interface UnitTestResult {
  code: string;
  language: string;
  framework: string;
  file_extension: string;
  num_tests: number;
  total_tokens: number;
  duration_seconds: number;
}

export interface UnitTestFramework {
  id: string;
  label: string;
  file_extension: string;
  hint: string;
}

export interface UnitTestLanguage {
  id: string;
  label: string;
  default_framework: string;
  frameworks: UnitTestFramework[];
}

export type UnitTestLanguageCatalog = Record<string, UnitTestLanguage>;

// ── Autoresearch ──────────────────────────────────────────────────────────────

export interface ResearchConfig {
  cobertura: number;
  clareza: number;
  estrutura: number;
  executabilidade: number;
  threshold: number;
  max_attempts: number;
}

export interface ExperimentRow {
  experiment: number;
  mutation: string;
  cobertura: number;
  clareza: number;
  estrutura: number;
  executabilidade: number;
  threshold: number;
  max_attempts: number;
  avg_score: number;
  n_approved: number;
  total_tokens: number;
  accepted: boolean;
  is_best: boolean;
}

export interface AutoresearchRunRequest {
  stories: string[];
  model: string;
  n_experiments: number;
  sample_size: number;
  seed?: number | null;
  resume_config?: ResearchConfig | null;
}

export interface AutoresearchRunSummary {
  id: number;
  started_at: number;
  finished_at?: number | null;
  status: "running" | "done" | "error";
  model: string;
  n_experiments: number;
  sample_size: number;
  seed?: number | null;
  baseline_score?: number | null;
  best_score?: number | null;
  improvement?: number | null;
  n_accepted?: number | null;
  total_tokens?: number | null;
  duration_seconds?: number | null;
  error?: string | null;
}

export interface AutoresearchRunDetail extends AutoresearchRunSummary {
  best_config?: ResearchConfig | null;
  experiments: ExperimentRow[];
}
