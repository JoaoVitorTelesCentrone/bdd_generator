"use client";

import { useEffect, useState } from "react";
import { RefreshCw, BarChart2 } from "lucide-react";
import { bistGetStats } from "@/lib/api";
import { FlakyChart } from "@/components/FlakyChart";
import type { BistStats } from "@/types";

export default function StatsPage() {
  const [stats, setStats]   = useState<BistStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setStats(await bistGetStats());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="border-b border-[#a3fb73]/10 bg-[#243d2c]/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <div className="flex items-baseline gap-3">
            <span className="text-[#5a7a65] font-mono text-sm select-none">$</span>
            <h1 className="text-lg font-mono font-semibold text-[#a3fb73] tracking-tight">
              bist stats
              <span className="text-[#5a7a65] font-normal"> --flaky --trend --days 30</span>
            </h1>
          </div>
          <p className="text-sm text-[#5a7a65] font-mono mt-1.5 ml-5">
            taxa de aprovação · cenários instáveis · tendência diária de execuções
          </p>
        </div>
      </div>

      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        {loading && (
          <div className="flex items-center justify-center py-20 gap-2">
            <RefreshCw className="w-4 h-4 text-[#5a7a65] animate-spin" />
            <span className="text-sm font-mono text-[#5a7a65]">carregando estatísticas...</span>
          </div>
        )}

        {error && (
          <div className="card p-6 text-center space-y-3">
            <p className="text-sm font-mono text-red-400">{error}</p>
            <button onClick={load} className="btn-ghost text-xs">tentar novamente</button>
          </div>
        )}

        {!loading && !error && stats && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button onClick={load} className="btn-ghost text-xs gap-1.5">
                <RefreshCw className="w-3 h-3" /> atualizar
              </button>
            </div>
            <FlakyChart stats={stats} />
          </div>
        )}

        {!loading && !error && stats && stats.total_runs === 0 && (
          <div className="card p-12 flex flex-col items-center text-center gap-4
                          border-dashed border-[#a3fb73]/12">
            <BarChart2 className="w-8 h-8 text-[#3d5a44]" />
            <div>
              <p className="text-sm font-mono text-[#7a9b87]">sem dados ainda</p>
              <p className="text-xs font-mono text-[#3d5a44] mt-1">
                execute <a href="/runs" className="text-[#a3fb73] hover:underline">bist runs</a> para ver estatísticas
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
