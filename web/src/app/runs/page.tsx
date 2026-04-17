import { RunHistory } from "@/components/RunHistory";

export const metadata = { title: "BIST — Runs" };

export default function RunsPage() {
  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-[#a3fb73]/10 bg-[#243d2c]/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <div className="flex items-baseline gap-3">
            <span className="text-[#5a7a65] font-mono text-sm select-none">$</span>
            <h1 className="text-lg font-mono font-semibold text-[#a3fb73] tracking-tight">
              bist runs
              <span className="text-[#5a7a65] font-normal"> --list --limit 20</span>
            </h1>
          </div>
          <p className="text-sm text-[#5a7a65] font-mono mt-1.5 ml-5">
            histórico de execuções de testes · geração + playwright · status em tempo real
          </p>
        </div>
      </div>
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <RunHistory />
      </div>
    </div>
  );
}
