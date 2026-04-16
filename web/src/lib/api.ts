import type { GenerateRequest, GenerateResult, EvaluateRequest, ScoreResult, Model } from "@/types";

/**
 * Em dev: chama o backend diretamente (CORS configurado no FastAPI).
 * Em produção: usa NEXT_PUBLIC_API_URL se definido.
 *
 * Evita o proxy do Next.js (rewrites) porque ele tem timeout curto e
 * derruba conexões em chamadas longas de LLM (socket hang up / ECONNRESET).
 */
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new Error(
      "Não foi possível conectar ao backend. Verifique se ele está rodando:\n\n" +
      "  python -m uvicorn backend.main:app --reload --port 8000\n\n" +
      "(execute na raiz do projeto, não dentro de /web)"
    );
  }

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

export async function checkHealth(): Promise<boolean> {
  try {
    await fetch("/health");
    return true;
  } catch {
    return false;
  }
}
