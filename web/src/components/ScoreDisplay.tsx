import { CheckCircle2, XCircle, Zap, Clock, Hash, FlaskConical } from "lucide-react";
import { MetricBar } from "./MetricBar";
import type { ScoreResult } from "@/types";

interface Props {
  score: ScoreResult;
  attempts?: number;
  totalTokens?: number;
  researchTokens?: number;
  durationSeconds?: number;
  converged?: boolean;
}

function ScoreRing({ value }: { value: number }) {
  const size = 80;
  const stroke = 7;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(1, value / 10);
  const dash = pct * circ;

  const color =
    value >= 8 ? "#10b981" :   // emerald-500
    value >= 7 ? "#22c55e" :   // green-500
    value >= 5 ? "#f59e0b" :   // amber-500
    "#ef4444";                  // red-500

  return (
    <svg width={size} height={size} className="-rotate-90">
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none" stroke="#27272a" strokeWidth={stroke}
      />
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none" stroke={color} strokeWidth={stroke}
        strokeDasharray={circ}
        strokeDashoffset={circ - dash}
        strokeLinecap="round"
        className="transition-all duration-700 ease-out"
      />
    </svg>
  );
}

export function ScoreDisplay({
  score,
  attempts,
  totalTokens,
  researchTokens,
  durationSeconds,
  converged,
}: Props) {
  const { score_final, aprovado } = score;

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="relative flex-shrink-0">
          <ScoreRing value={score_final} />
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-xl font-bold text-zinc-100 leading-none">
              {score_final.toFixed(1)}
            </span>
            <span className="text-[10px] text-zinc-500 leading-none mt-0.5">/10</span>
          </div>
        </div>
        <div className="space-y-1.5">
          {aprovado ? (
            <div className="badge-approved">
              <CheckCircle2 className="w-3 h-3" />
              APROVADO
            </div>
          ) : (
            <div className="badge-rejected">
              <XCircle className="w-3 h-3" />
              REPROVADO
            </div>
          )}
          <p className="text-xs text-zinc-500">
            Threshold: {score.threshold.toFixed(1)}
          </p>
          {converged !== undefined && (
            <p className={`text-xs ${converged ? "text-emerald-500" : "text-amber-500"}`}>
              {converged ? "Convergiu" : "Não convergiu"}
            </p>
          )}
        </div>
      </div>

      {/* Metrics */}
      <div className="space-y-3">
        <MetricBar label="Cobertura"       value={score.cobertura}       weight="30%" delay={0}   />
        <MetricBar label="Estrutura GWT"   value={score.estrutura}       weight="30%" delay={100} />
        <MetricBar label="Clareza"         value={score.clareza}         weight="20%" delay={200} />
        <MetricBar label="Executabilidade" value={score.executabilidade} weight="20%" delay={300} />
      </div>

      {/* Stats row */}
      {(attempts || totalTokens || durationSeconds) && (
        <div className="flex flex-wrap gap-3 pt-2 border-t border-zinc-800">
          {attempts !== undefined && (
            <StatChip icon={<Zap className="w-3 h-3" />} label={`${attempts} tentativa${attempts !== 1 ? "s" : ""}`} />
          )}
          {totalTokens !== undefined && (
            <StatChip icon={<Hash className="w-3 h-3" />} label={`${totalTokens.toLocaleString()} tokens`} />
          )}
          {researchTokens !== undefined && researchTokens > 0 && (
            <StatChip icon={<FlaskConical className="w-3 h-3" />} label={`${researchTokens.toLocaleString()} research`} />
          )}
          {durationSeconds !== undefined && (
            <StatChip icon={<Clock className="w-3 h-3" />} label={`${durationSeconds.toFixed(1)}s`} />
          )}
        </div>
      )}
    </div>
  );
}

function StatChip({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <span className="flex items-center gap-1 text-xs text-zinc-500">
      {icon}
      {label}
    </span>
  );
}
