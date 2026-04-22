"use client";

import type { ExperimentRow } from "@/types";

interface Props {
  experiments: ExperimentRow[];
  baselineScore?: number | null;
}

export function ExperimentsTable({ experiments, baselineScore }: Props) {
  if (experiments.length === 0) return null;

  return (
    <div className="card overflow-hidden">
      <div className="px-4 py-3 border-b border-bist-border bg-bist-surface2">
        <p className="text-xs font-code text-bist-dim uppercase tracking-widest">
          Experimentos — {experiments.length} rodadas
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-bist-border bg-bist-surface2">
              <th className="text-left px-3 py-2 font-code text-bist-dim w-10">#</th>
              <th className="text-left px-3 py-2 font-code text-bist-dim">Mutação</th>
              <th className="text-right px-3 py-2 font-code text-bist-dim w-20">Score</th>
              <th className="text-right px-3 py-2 font-code text-bist-dim w-20">Δ</th>
              <th className="text-right px-3 py-2 font-code text-bist-dim w-20">Aprovados</th>
              <th className="text-right px-3 py-2 font-code text-bist-dim w-20">Tokens</th>
              <th className="text-center px-3 py-2 font-code text-bist-dim w-24">Status</th>
            </tr>
          </thead>
          <tbody>
            {experiments.map((row) => {
              const delta = baselineScore != null ? row.avg_score - baselineScore : null;
              const deltaColor =
                delta == null ? "text-bist-dim" :
                delta > 0     ? "text-[#2D6A3F]" :
                delta < 0     ? "text-red-500"   : "text-bist-dim";

              return (
                <tr
                  key={row.experiment}
                  className={[
                    "border-b border-bist-border2 transition-colors",
                    row.is_best
                      ? "bg-[#a3fb73]/5"
                      : "hover:bg-bist-surface2",
                  ].join(" ")}
                >
                  <td className="px-3 py-2 font-code text-bist-dim">
                    {row.experiment === 0 ? (
                      <span className="text-[10px] text-bist-dim">base</span>
                    ) : (
                      row.experiment
                    )}
                  </td>

                  <td className="px-3 py-2 text-bist-muted max-w-[260px] truncate">
                    {row.experiment === 0 ? (
                      <span className="text-bist-dim italic">configuração inicial</span>
                    ) : (
                      row.mutation
                    )}
                  </td>

                  <td className="px-3 py-2 text-right font-code font-semibold text-bist-primary tabular-nums">
                    {row.avg_score.toFixed(3)}
                  </td>

                  <td className={`px-3 py-2 text-right font-code tabular-nums ${deltaColor}`}>
                    {delta == null ? "—" : `${delta >= 0 ? "+" : ""}${delta.toFixed(3)}`}
                  </td>

                  <td className="px-3 py-2 text-right font-code text-bist-muted tabular-nums">
                    {row.n_approved}
                  </td>

                  <td className="px-3 py-2 text-right font-code text-bist-dim tabular-nums">
                    {row.total_tokens.toLocaleString("pt-BR")}
                  </td>

                  <td className="px-3 py-2 text-center">
                    {row.is_best ? (
                      <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-[#2D6A3F] bg-[#a3fb73]/15 border border-[#a3fb73]/30 px-2 py-0.5 rounded-full">
                        melhor
                      </span>
                    ) : row.accepted ? (
                      <span className="text-[10px] font-code text-[#2D6A3F]">aceito</span>
                    ) : row.experiment === 0 ? (
                      <span className="text-[10px] font-code text-bist-dim">baseline</span>
                    ) : (
                      <span className="text-[10px] font-code text-bist-dim">rejeitado</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
