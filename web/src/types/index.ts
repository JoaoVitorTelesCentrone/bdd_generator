export interface Model {
  id: string;
  name: string;
  provider: "gemini" | "claude";
  default?: boolean;
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
