import { EvaluatePanel } from "@/components/EvaluatePanel";

export default function EvaluatePage() {
  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-zinc-800 bg-zinc-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <h1 className="text-xl font-semibold text-zinc-100">Avaliar BDD</h1>
          <p className="text-sm text-zinc-500 mt-1">
            Avalie cenários Gherkin existentes com as 4 métricas de qualidade (sem gerar novos)
          </p>
        </div>
      </div>
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <EvaluatePanel />
      </div>
    </div>
  );
}
