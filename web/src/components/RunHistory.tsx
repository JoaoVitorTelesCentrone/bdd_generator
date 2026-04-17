"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  CheckCircle2, XCircle, Clock, Globe,
  RefreshCw, Play, ChevronRight, Loader2,
} from "lucide-react";
import { bistListRuns } from "@/lib/api";
import type { BistRunSummary } from "@/types";

function statusIcon(s: string) {
  if (s === "passed")  return <CheckCircle2 className="w-4 h-4 text-[#2D6A3F] shrink-0" />;
  if (s === "failed" || s === "error") return <XCircle className="w-4 h-4 text-red-500 shrink-0" />;
  return <Loader2 className="w-4 h-4 text-amber-500 animate-spin shrink-0" />;
}

function statusBadge(s: string) {
  const cls =
    s === "passed"  ? "text-[#2D6A3F] bg-[#a3fb73]/15 border-[#a3fb73]/30" :
    s === "running" ? "text-amber-700 bg-amber-50 border-amber-200" :
                     "text-red-600 bg-red-50 border-red-200";
  return (
    <span className={`text-[10px] font-code px-2 py-0.5 rounded-full border font-medium ${cls}`}>{s}</span>
  );
}

function fmtDate(ts: number) {
  return new Date(ts * 1000).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function fmtDuration(ms: number) {
  if (!ms) return "—";
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
}

export function RunHistory({ limit = 20 }: { limit?: number }) {
  const [runs, setRuns]       = useState<BistRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");

  async function load() {
    setLoading(true); setError("");
    try { setRuns(await bistListRuns(limit)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, [limit]);

  if (loading) return (
    <div className="flex items-center justify-center py-16 gap-2">
      <Loader2 className="w-4 h-4 text-bist-muted animate-spin" />
      <span className="text-sm text-bist-muted">Carregando execuções...</span>
    </div>
  );

  if (error) return (
    <div className="card p-6 text-center space-y-3 border-red-200 bg-red-50">
      <p className="text-sm text-red-600">{error}</p>
      <button onClick={load} className="btn-secondary text-xs">Tentar novamente</button>
    </div>
  );

  if (runs.length === 0) return (
    <div className="card p-12 flex flex-col items-center text-center gap-4 border-dashed min-h-[240px]">
      <div className="w-12 h-12 rounded-xl bg-bist-surface2 border border-bist-border flex items-center justify-center">
        <Play className="w-5 h-5 text-bist-muted" />
      </div>
      <div>
        <p className="text-sm font-medium text-bist-primary">Nenhuma execução encontrada</p>
        <p className="text-xs text-bist-muted mt-1">Use o comando <code className="font-code">bist full</code> para iniciar um run</p>
      </div>
    </div>
  );

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs text-bist-dim font-code">{runs.length} execuções</p>
        <button onClick={load} className="btn-ghost text-xs gap-1.5">
          <RefreshCw className="w-3 h-3" /> Atualizar
        </button>
      </div>

      {runs.map(run => (
        <Link key={run.id} href={`/runs/${run.id}`}>
          <div className="card p-4 hover:border-bist-muted transition-colors cursor-pointer group">
            <div className="flex items-center gap-3">
              {statusIcon(run.status)}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-bist-primary">Run #{run.id}</span>
                  {statusBadge(run.status)}
                </div>
                <div className="flex items-center flex-wrap gap-x-3 gap-y-0.5 mt-0.5 text-xs text-bist-muted">
                  <span className="flex items-center gap-1">
                    <Globe className="w-3 h-3" />
                    <span className="max-w-[200px] truncate">{run.env_url}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {fmtDuration(run.duration_ms)}
                  </span>
                  <span>{fmtDate(run.started_at)}</span>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-xs text-bist-dim hidden sm:block max-w-[140px] truncate font-code">
                  {run.feature_path.split(/[/\\]/).pop() || "—"}
                </span>
                <ChevronRight className="w-4 h-4 text-bist-dim group-hover:text-bist-primary transition-colors" />
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
