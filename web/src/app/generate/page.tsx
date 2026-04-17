import { GeneratePanel } from "@/components/GeneratePanel";
import type { Model } from "@/types";

const FALLBACK_MODELS: Model[] = [
  { id: "flash",      name: "Gemini 2.5 Flash",     provider: "gemini", default: true },
  { id: "pro",        name: "Gemini 2.5 Pro",        provider: "gemini" },
  { id: "flash-lite", name: "Gemini 2.0 Flash Lite", provider: "gemini" },
  { id: "sonnet",     name: "Claude Sonnet 4.6",     provider: "claude" },
  { id: "opus",       name: "Claude Opus 4.6",       provider: "claude" },
  { id: "haiku",      name: "Claude Haiku 4.5",      provider: "claude" },
];

async function getModels(): Promise<Model[]> {
  try {
    const url = process.env.BACKEND_URL
      ? `${process.env.BACKEND_URL}/api/models`
      : "http://127.0.0.1:8000/api/models";
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error();
    const data = await res.json();
    return data.models ?? FALLBACK_MODELS;
  } catch {
    return FALLBACK_MODELS;
  }
}

export default async function GeneratePage() {
  const models = await getModels();

  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <h1 className="text-lg font-semibold text-bist-primary">Gerar BDD</h1>
          <p className="text-sm text-bist-muted mt-0.5">
            Insira uma user story e obtenha cenários Gherkin avaliados por 4 métricas de qualidade
          </p>
        </div>
      </div>
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <GeneratePanel initialModels={models} />
      </div>
    </div>
  );
}
