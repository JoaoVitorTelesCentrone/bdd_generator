"use client";

import { Download, TrendingUp } from "lucide-react";
import type { ResearchConfig } from "@/types";

interface Props {
  config: ResearchConfig;
  baselineScore?: number | null;
  bestScore?: number | null;
  nAccepted?: number | null;
  nExperiments?: number | null;
  totalTokens?: number | null;
  durationSeconds?: number | null;
  runId: number;
}

function WeightBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-bist-muted">{label}</span>
        <span className="font-code font-semibold text-bist-primary tabular-nums">{pct}%</span>
      </div>
      <div className="h-1.5 bg-bist-border rounded-full overflow-hidden">
        <div
          className="h-full bg-[#a3fb73] rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function BestConfigCard({
  config,
  baselineScore,
  bestScore,
  nAccepted,
  nExperiments,
  totalTokens,
  durationSeconds,
  runId,
}: Props) {
  const improvement =
    bestScore != null && baselineScore != null
      ? bestScore - baselineScore
      : null;

  function handleDownload() {
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: "application/json" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `best_config_run${runId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="card p-5 space-y-5 border-[#a3fb73]/30 bg-[#a3fb73]/3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-[#2D6A3F]" />
          <p className="text-sm font-semibold text-bist-primary">Melhor configuração encontrada</p>
        </div>
        <button
          onClick={handleDownload}
          className="btn-ghost text-xs gap-1.5"
          title="Baixar best_config.json"
        >
          <Download className="w-3.5 h-3.5" />
          best_config.json
        </button>
      </div>

      {improvement != null && (
        <div className="flex items-center gap-4 p-3 rounded-lg bg-bist-surface2 border border-bist-border">
          <div className="text-center">
            <p className="text-[10px] font-code text-bist-dim uppercase tracking-widest">Baseline</p>
            <p className="text-lg font-bold text-bist-muted tabular-nums">
              {baselineScore?.toFixed(3)}
            </p>
          </div>
          <div className="flex-1 text-center">
            <p className={`text-2xl font-bold tabular-nums ${improvement >= 0 ? "text-[#2D6A3F]" : "text-red-500"}`}>
              {improvement >= 0 ? "+" : ""}{improvement.toFixed(3)}
            </p>
            <p className="text-[10px] font-code text-bist-dim">variação</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] font-code text-bist-dim uppercase tracking-widest">Melhor</p>
            <p className="text-lg font-bold text-bist-primary tabular-nums">
              {bestScore?.toFixed(3)}
            </p>
          </div>
        </div>
      )}

      <div className="space-y-3">
        <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Pesos otimizados</p>
        <WeightBar label="Cobertura"       value={config.cobertura} />
        <WeightBar label="Clareza"         value={config.clareza} />
        <WeightBar label="Estrutura GWT"   value={config.estrutura} />
        <WeightBar label="Executabilidade" value={config.executabilidade} />
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="card-subtle p-3 rounded-lg">
          <p className="font-code text-bist-dim uppercase tracking-widest text-[10px] mb-1">Threshold</p>
          <p className="font-bold text-bist-primary tabular-nums">{config.threshold.toFixed(1)}</p>
        </div>
        <div className="card-subtle p-3 rounded-lg">
          <p className="font-code text-bist-dim uppercase tracking-widest text-[10px] mb-1">Max tentativas</p>
          <p className="font-bold text-bist-primary tabular-nums">{config.max_attempts}</p>
        </div>
      </div>

      {(nAccepted != null || totalTokens != null || durationSeconds != null) && (
        <div className="flex flex-wrap gap-4 text-xs text-bist-muted border-t border-bist-border pt-3">
          {nAccepted != null && nExperiments != null && (
            <span>Aceitos: <span className="font-semibold text-bist-primary">{nAccepted}/{nExperiments}</span></span>
          )}
          {totalTokens != null && (
            <span>Tokens: <span className="font-semibold text-bist-primary">{totalTokens.toLocaleString("pt-BR")}</span></span>
          )}
          {durationSeconds != null && (
            <span>Tempo: <span className="font-semibold text-bist-primary">{Math.round(durationSeconds)}s</span></span>
          )}
        </div>
      )}

    </div>
  );
}
