"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FlaskConical, Plus, Loader2, ArrowRight, Clock } from "lucide-react";
import { listAutoresearchRuns } from "@/lib/api";
import type { AutoresearchRunSummary } from "@/types";

function statusBadge(s: string) {
  const cls =
    s === "done"    ? "text-[#2D6A3F] bg-[#a3fb73]/15 border-[#a3fb73]/30" :
    s === "running" ? "text-amber-700 bg-amber-50 border-amber-200" :
                      "text-red-600 bg-red-50 border-red-200";
  return (
    <span className={`text-xs font-code px-2 py-0.5 rounded-full border font-medium ${cls}`}>
      {s}
    </span>
  );
}

function fmtDate(ts: number) {
  return new Date(ts * 1000).toLocaleString("pt-BR", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

function RunCard({ run }: { run: AutoresearchRunSummary }) {
  const improvement = run.improvement;
  const impColor =
    improvement == null ? "text-bist-dim" :
    improvement > 0     ? "text-[#2D6A3F]" :
    improvement < 0     ? "text-red-500"   : "text-bist-dim";

  return (
    <Link
      href={`/autoresearch/${run.id}`}
      className="card p-4 flex items-center gap-4 hover:border-bist-muted transition-colors group"
    >
      <div className="w-9 h-9 rounded-lg bg-bist-surface2 border border-bist-border flex items-center justify-center shrink-0">
        <FlaskConical className="w-4 h-4 text-bist-muted group-hover:text-[#2D6A3F] transition-colors" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="text-sm font-semibold text-bist-primary">Run #{run.id}</span>
          {statusBadge(run.status)}
        </div>
        <p className="text-xs text-bist-muted truncate">
          <span className="font-code">{run.model}</span>
          {" · "}{run.n_experiments} experimentos · sample {run.sample_size}
          {run.seed != null && ` · seed ${run.seed}`}
        </p>
      </div>

      <div className="text-right shrink-0 space-y-0.5">
        {run.best_score != null && (
          <p className="text-sm font-semibold text-bist-primary tabular-nums">
            {run.best_score.toFixed(3)}
          </p>
        )}
        {improvement != null && (
          <p className={`text-xs font-code tabular-nums ${impColor}`}>
            {improvement >= 0 ? "+" : ""}{improvement.toFixed(3)}
          </p>
        )}
      </div>

      <div className="text-right shrink-0 hidden sm:block">
        <p className="text-xs text-bist-dim flex items-center gap-1 justify-end">
          <Clock className="w-3 h-3" />
          {fmtDate(run.started_at)}
        </p>
        {run.duration_seconds != null && (
          <p className="text-[10px] font-code text-bist-dim mt-0.5">
            {Math.round(run.duration_seconds)}s
          </p>
        )}
      </div>

      <ArrowRight className="w-4 h-4 text-bist-dim group-hover:text-bist-primary transition-colors shrink-0" />
    </Link>
  );
}

export default function AutoresearchPage() {
  const [runs, setRuns]       = useState<AutoresearchRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");

  useEffect(() => {
    listAutoresearchRuns()
      .then(setRuns)
      .catch(e => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 flex flex-col">
      <div className="border-b border-bist-border bg-bist-surface">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-5 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-bist-primary flex items-center gap-2">
              <FlaskConical className="w-4 h-4 text-bist-muted" />
              Autoresearch Lab
            </h1>
            <p className="text-sm text-bist-muted mt-0.5">
              Otimização autônoma de pesos e parâmetros do scorer via hill-climbing
            </p>
          </div>
          <Link href="/autoresearch/new" className="btn-primary text-sm gap-2">
            <Plus className="w-4 h-4" /> Novo run
          </Link>
        </div>
      </div>

      <div className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-6 space-y-4">

        {loading && (
          <div className="flex items-center gap-2 text-sm text-bist-muted py-10 justify-center">
            <Loader2 className="w-4 h-4 animate-spin" /> Carregando runs...
          </div>
        )}

        {error && (
          <div className="card p-4 border-red-200 bg-red-50 text-sm text-red-600">{error}</div>
        )}

        {!loading && !error && runs.length === 0 && (
          <div className="card p-12 text-center space-y-5 border-dashed">
            <div className="w-12 h-12 rounded-xl bg-bist-surface2 border border-bist-border flex items-center justify-center mx-auto">
              <FlaskConical className="w-5 h-5 text-bist-muted" />
            </div>
            <div>
              <p className="text-sm font-medium text-bist-primary">Nenhum run ainda</p>
              <p className="text-xs text-bist-dim mt-1 max-w-xs mx-auto leading-relaxed">
                O autoresearch descobre automaticamente a melhor configuração de pesos para o seu dataset.
              </p>
            </div>
            <Link href="/autoresearch/new" className="btn-primary text-sm inline-flex items-center gap-2">
              <Plus className="w-4 h-4" /> Iniciar primeiro run
            </Link>
          </div>
        )}

        {runs.map(run => <RunCard key={run.id} run={run} />)}

      </div>
    </div>
  );
}
