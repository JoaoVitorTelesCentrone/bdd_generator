"use client";

import { useEffect, useState } from "react";
import { RefreshCw, BarChart2, Loader2 } from "lucide-react";
import { bistGetStats } from "@/lib/api";
import { FlakyChart } from "@/components/FlakyChart";
import type { BistStats } from "@/types";

export default function StatsPage() {
  const [stats, setStats]       = useState<BistStats | null>(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");

  async function load() {
    setLoading(true); setError("");
    try { setStats(await bistGetStats()); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-bist-primary">Estatísticas</h1>
            <p className="text-sm text-bist-muted mt-0.5">Taxa de aprovação · cenários instáveis · tendência 30 dias</p>
          </div>
          <button onClick={load} className="btn-ghost text-xs gap-1.5">
            <RefreshCw className="w-3.5 h-3.5" /> Atualizar
          </button>
        </div>
      </div>

      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        {loading && (
          <div className="flex items-center justify-center py-20 gap-2">
            <Loader2 className="w-4 h-4 text-bist-muted animate-spin" />
            <span className="text-sm text-bist-muted">Carregando estatísticas...</span>
          </div>
        )}

        {error && (
          <div className="card p-6 text-center space-y-3 border-red-200 bg-red-50">
            <p className="text-sm text-red-600">{error}</p>
            <button onClick={load} className="btn-secondary text-xs">Tentar novamente</button>
          </div>
        )}

        {!loading && !error && stats && stats.total_runs === 0 && (
          <div className="card p-12 flex flex-col items-center text-center gap-4 border-dashed">
            <div className="w-12 h-12 rounded-xl bg-bist-surface2 border border-bist-border flex items-center justify-center">
              <BarChart2 className="w-5 h-5 text-bist-muted" />
            </div>
            <div>
              <p className="text-sm font-medium text-bist-primary">Sem dados ainda</p>
              <p className="text-xs text-bist-muted mt-1">
                Execute testes em <a href="/runs" className="text-bist-primary font-medium underline">Runs</a> para ver estatísticas
              </p>
            </div>
          </div>
        )}

        {!loading && !error && stats && stats.total_runs > 0 && (
          <FlakyChart stats={stats} />
        )}
      </div>
    </div>
  );
}
