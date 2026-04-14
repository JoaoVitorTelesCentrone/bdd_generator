import type { GenerateRequest, GenerateResult, EvaluateRequest, ScoreResult, Model } from "@/types";

// Chama o FastAPI diretamente — evita timeout do proxy do Next.js em chamadas longas de LLM
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchModels(): Promise<Model[]> {
  const data = await apiFetch<{ models: Model[] }>(`${BASE}/api/models`);
  return data.models;
}

export async function generateBDD(req: GenerateRequest): Promise<GenerateResult> {
  return apiFetch<GenerateResult>(`${BASE}/api/generate`, {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function evaluateBDD(req: EvaluateRequest): Promise<ScoreResult> {
  return apiFetch<ScoreResult>(`${BASE}/api/evaluate`, {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function checkHealth(): Promise<boolean> {
  try {
    await apiFetch<{ status: string }>(`${BASE}/health`);
    return true;
  } catch {
    return false;
  }
}
