export interface Model {
  id: string;
  name: string;
  provider: "gemini" | "claude";
  default?: boolean;
}

export interface ScoreResult {
  cobertura: number;
  clareza: number;
  estrutura: number;
  executabilidade: number;
  score_final: number;
  aprovado: boolean;
  threshold: number;
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

// ── Story Creator ─────────────────────────────────────────────────────────────

export interface StoryCreateRequest {
  idea: string;
  model: string;
}

export interface StoryCreateResult {
  user_story: string;
  acceptance_criteria: string[];
}
