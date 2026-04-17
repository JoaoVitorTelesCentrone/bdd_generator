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
  const stroke = 6;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(1, value / 10);
  const dash = pct * circ;

  const color =
    value >= 8 ? "#a3fb73" :
    value >= 7 ? "#7dd151" :
    value >= 5 ? "#f59e0b" :
    "#ef4444";

  return (
    <svg width={size} height={size} className="-rotate-90">
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#DEE8E0" strokeWidth={stroke} />
      <circle
        cx={size/2} cy={size/2} r={r}
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
  score, attempts, totalTokens, researchTokens, durationSeconds, converged,
}: Props) {
  const { score_final, aprovado } = score;

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex items-center gap-4">
        <div className="relative flex-shrink-0">
          <ScoreRing value={score_final} />
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-xl font-code font-bold text-bist-primary leading-none">
              {score_final.toFixed(1)}
            </span>
            <span className="text-[10px] font-code text-bist-dim leading-none mt-0.5">/10</span>
          </div>
        </div>
        <div className="space-y-1.5">
          {aprovado ? (
            <div className="badge-approved">
              <CheckCircle2 className="w-3 h-3" /> APROVADO
            </div>
          ) : (
            <div className="badge-rejected">
              <XCircle className="w-3 h-3" /> REPROVADO
            </div>
          )}
          <p className="text-xs text-bist-dim font-code">threshold: {score.threshold.toFixed(1)}</p>
          {converged !== undefined && (
            <p className={`text-xs font-code ${converged ? "text-[#2D6A3F]" : "text-amber-600"}`}>
              {converged ? "✓ convergiu" : "~ não convergiu"}
            </p>
          )}
        </div>
      </div>

      <div className="space-y-3">
        <MetricBar label="Cobertura"       value={score.cobertura}       weight="30%" delay={0}   />
        <MetricBar label="Estrutura GWT"   value={score.estrutura}       weight="30%" delay={100} />
        <MetricBar label="Clareza"         value={score.clareza}         weight="20%" delay={200} />
        <MetricBar label="Executabilidade" value={score.executabilidade} weight="20%" delay={300} />
      </div>

      {(attempts !== undefined || totalTokens !== undefined || durationSeconds !== undefined) && (
        <div className="flex flex-wrap gap-3 pt-3 border-t border-bist-border">
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
    <span className="flex items-center gap-1.5 text-xs font-code text-bist-muted bg-bist-surface2 border border-bist-border2 rounded-md px-2.5 py-1">
      {icon} {label}
    </span>
  );
}
