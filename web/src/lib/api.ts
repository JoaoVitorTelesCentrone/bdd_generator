import type {
  GenerateRequest, GenerateResult, EvaluateRequest, ScoreResult, Model,
  BistRunSummary, BistRunDetail, BistStats, BistRunRequest, BistExecuteRequest,
  StoryCreateRequest, StoryCreateResult,
  AutoresearchRunRequest, AutoresearchRunSummary, AutoresearchRunDetail,
  UnitTestRequest, UnitTestResult, UnitTestLanguageCatalog,
} from "@/types";

/**
 * Em dev: chama o backend diretamente (CORS configurado no FastAPI).
 * Em produção: usa NEXT_PUBLIC_API_URL se definido.
 *
 * Evita o proxy do Next.js (rewrites) porque ele tem timeout curto e
 * derruba conexões em chamadas longas de LLM (socket hang up / ECONNRESET).
 */
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function apiFetch<T>(path: string, init?: RequestInit, timeoutMs = 300_000): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let res: Response;
  try {
    res = await fetch(path, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      signal: controller.signal,
    });
  } catch (err) {
    clearTimeout(timer);
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error(`Timeout: a requisição demorou mais de ${Math.round(timeoutMs / 1000)}s sem resposta.`);
    }
    throw new Error(
      "Não foi possível conectar ao backend. Verifique se ele está rodando:\n\n" +
      "  python -m uvicorn backend.main:app --reload --port 8000\n\n" +
      "(execute na raiz do projeto, não dentro de /web)"
    );
  }
  clearTimeout(timer);

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `Erro ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchModels(): Promise<Model[]> {
  const data = await apiFetch<{ models: Model[] }>(`${BASE}/models`);
  return data.models;
}

export async function generateBDD(req: GenerateRequest): Promise<GenerateResult> {
  return apiFetch<GenerateResult>(`${BASE}/generate`, {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function evaluateBDD(req: EvaluateRequest): Promise<ScoreResult> {
  return apiFetch<ScoreResult>(`${BASE}/evaluate`, {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function createStory(req: StoryCreateRequest): Promise<StoryCreateResult> {
  return apiFetch<StoryCreateResult>(`${BASE}/stories/create`, {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function checkHealth(): Promise<boolean> {
  try {
    await fetch("/health");
    return true;
  } catch {
    return false;
  }
}

// ── BIST API ──────────────────────────────────────────────────────────────────

export async function bistTriggerRun(req: BistRunRequest): Promise<{ run_id: number; status: string }> {
  return apiFetch(`${BASE}/bist/run`, { method: "POST", body: JSON.stringify(req) });
}

export async function bistExecuteRun(req: BistExecuteRequest): Promise<{ run_id: number; status: string }> {
  return apiFetch(`${BASE}/bist/execute`, { method: "POST", body: JSON.stringify(req) });
}

export async function bistListRuns(limit = 20): Promise<BistRunSummary[]> {
  return apiFetch(`${BASE}/bist/runs?limit=${limit}`);
}

export async function bistGetRun(id: number): Promise<BistRunDetail> {
  return apiFetch(`${BASE}/bist/runs/${id}`);
}

export async function bistGetStats(): Promise<BistStats> {
  return apiFetch(`${BASE}/bist/stats`);
}

export function bistWsUrl(runId: number): string {
  const wsBase = BASE.replace(/^http/, "ws").replace(/\/api$/, "");
  return `${wsBase}/ws/bist/run/${runId}`;
}

// ── Unit Tests API ────────────────────────────────────────────────────────────

export async function fetchUnitTestLanguages(): Promise<UnitTestLanguageCatalog> {
  return apiFetch<UnitTestLanguageCatalog>(`${BASE}/unit-tests/languages`);
}

export async function generateUnitTests(req: UnitTestRequest): Promise<UnitTestResult> {
  return apiFetch<UnitTestResult>(
    `${BASE}/unit-tests/generate`,
    { method: "POST", body: JSON.stringify(req) },
    120_000,
  );
}

// ── Autoresearch API ──────────────────────────────────────────────────────────

export async function startAutoresearch(
  req: AutoresearchRunRequest,
): Promise<{ run_id: number; status: string }> {
  return apiFetch(`${BASE}/autoresearch/run`, {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function listAutoresearchRuns(
  limit = 20,
): Promise<AutoresearchRunSummary[]> {
  return apiFetch(`${BASE}/autoresearch/runs?limit=${limit}`);
}

export async function getAutoresearchRun(id: number): Promise<AutoresearchRunDetail> {
  return apiFetch(`${BASE}/autoresearch/runs/${id}`);
}

export function autoresearchWsUrl(runId: number): string {
  const wsBase = BASE.replace(/^http/, "ws").replace(/\/api$/, "");
  return `${wsBase}/ws/autoresearch/run/${runId}`;
}
