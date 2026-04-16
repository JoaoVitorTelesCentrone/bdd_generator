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
    // Server-side: chama o backend diretamente (sem passar pelo proxy cliente)
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
      <div className="border-b border-[#a3fb73]/10 bg-[#243d2c]/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <div className="flex items-baseline gap-3">
            <span className="text-[#5a7a65] font-mono text-sm select-none">$</span>
            <h1 className="text-lg font-mono font-semibold text-[#a3fb73] tracking-tight">
              bist generate
              <span className="text-[#5a7a65] font-normal"> --bdd --auto-refine</span>
            </h1>
          </div>
          <p className="text-sm text-[#5a7a65] font-mono mt-1.5 ml-5">
            insira uma user story → obtenha cenários Gherkin avaliados por 4 métricas de qualidade
          </p>
        </div>
      </div>
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <GeneratePanel initialModels={models} />
      </div>
    </div>
  );
}
