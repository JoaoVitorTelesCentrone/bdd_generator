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
  if (s === "passed")  return <CheckCircle2 className="w-4 h-4 text-[#a3fb73] shrink-0" />;
  if (s === "failed" || s === "error") return <XCircle className="w-4 h-4 text-red-400 shrink-0" />;
  return <Loader2 className="w-4 h-4 text-[#f59e0b] animate-spin shrink-0" />;
}

function statusBadge(s: string) {
  const cls =
    s === "passed"  ? "text-[#a3fb73] bg-[#a3fb73]/10 border-[#a3fb73]/20" :
    s === "running" ? "text-[#f59e0b] bg-[#f59e0b]/10 border-[#f59e0b]/20" :
                     "text-red-400 bg-red-400/10 border-red-400/20";
  return (
    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${cls}`}>{s}</span>
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
  const [runs, setRuns]     = useState<BistRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setRuns(await bistListRuns(limit));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [limit]);

  if (loading) return (
    <div className="flex items-center justify-center py-16 gap-2">
      <RefreshCw className="w-4 h-4 text-[#5a7a65] animate-spin" />
      <span className="text-sm font-mono text-[#5a7a65]">carregando runs...</span>
    </div>
  );

  if (error) return (
    <div className="card p-6 text-center space-y-3">
      <p className="text-sm font-mono text-red-400">{error}</p>
      <button onClick={load} className="btn-ghost text-xs">tentar novamente</button>
    </div>
  );

  if (runs.length === 0) return (
    <div className="card p-12 flex flex-col items-center text-center gap-4
                    border-dashed border-[#a3fb73]/12 min-h-[240px]">
      <Play className="w-8 h-8 text-[#3d5a44]" />
      <div>
        <p className="text-sm font-mono text-[#7a9b87]">nenhum run encontrado</p>
        <p className="text-xs font-mono text-[#3d5a44] mt-1">
          use <code className="text-[#a3fb73]">bist full</code> para iniciar um run
        </p>
      </div>
    </div>
  );

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs font-mono text-[#5a7a65]">{runs.length} runs</p>
        <button onClick={load} className="btn-ghost text-xs gap-1.5">
          <RefreshCw className="w-3 h-3" /> atualizar
        </button>
      </div>

      {runs.map(run => (
        <Link key={run.id} href={`/runs/${run.id}`}>
          <div className="card p-4 hover:border-[#a3fb73]/30 transition-colors duration-150 cursor-pointer group">
            <div className="flex items-center gap-3">
              {statusIcon(run.status)}

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-mono font-semibold text-[#eef9e8]">
                    Run #{run.id}
                  </span>
                  {statusBadge(run.status)}
                </div>
                <div className="flex items-center flex-wrap gap-x-3 gap-y-0.5 mt-0.5
                                text-[10px] font-mono text-[#5a7a65]">
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
                <span className="text-[10px] font-mono text-[#3d5a44] hidden sm:block max-w-[140px] truncate">
                  {run.feature_path.split(/[/\\]/).pop() || "—"}
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-[#3d5a44] group-hover:text-[#a3fb73]
                                        transition-colors" />
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
