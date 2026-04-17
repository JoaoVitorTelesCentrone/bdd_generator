import { RunHistory } from "@/components/RunHistory";

export const metadata = { title: "BIST — Runs" };

export default function RunsPage() {
  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <h1 className="text-lg font-semibold text-bist-primary">Execuções</h1>
          <p className="text-sm text-bist-muted mt-0.5">
            Histórico de execuções de testes — geração + Playwright — status em tempo real
          </p>
        </div>
      </div>
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <RunHistory />
      </div>
    </div>
  );
}
