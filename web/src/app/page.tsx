import { GeneratePanel } from "@/components/GeneratePanel";
import type { Model } from "@/types";

async function getModels(): Promise<Model[]> {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/models", { cache: "no-store" });
    if (!res.ok) throw new Error();
    const data = await res.json();
    return data.models;
  } catch {
    // Fallback: return default models when backend is not running
    return [
      { id: "flash",      name: "Gemini 2.5 Flash",     provider: "gemini", default: true },
      { id: "pro",        name: "Gemini 2.5 Pro",        provider: "gemini" },
      { id: "flash-lite", name: "Gemini 2.0 Flash Lite", provider: "gemini" },
      { id: "sonnet",     name: "Claude Sonnet 4.6",     provider: "claude" },
      { id: "opus",       name: "Claude Opus 4.6",       provider: "claude" },
      { id: "haiku",      name: "Claude Haiku 4.5",      provider: "claude" },
    ];
  }
}

export default async function GeneratePage() {
  const models = await getModels();

  return (
    <div className="flex-1 flex flex-col">
      {/* Page header */}
      <div className="border-b border-zinc-800 bg-zinc-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <h1 className="text-xl font-semibold text-zinc-100">
            Gerar Cenários BDD
          </h1>
          <p className="text-sm text-zinc-500 mt-1">
            Insira uma user story e obtenha cenários Gherkin avaliados por 4 métricas de qualidade com auto-refinamento
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <GeneratePanel initialModels={models} />
      </div>
    </div>
  );
}
