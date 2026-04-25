import { GeneratePanel } from "@/components/GeneratePanel";

export default function GeneratePage() {
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
        <GeneratePanel />
      </div>
    </div>
  );
}
