"use client";

import type { BistStats } from "@/types";

function TrendChart({ data }: { data: BistStats["runs_over_time"] }) {
  if (!data.length) return (
    <p className="text-xs text-bist-muted py-4 text-center">Sem dados de tendência</p>
  );

  const max = Math.max(...data.map(d => d.passed + d.failed), 1);

  return (
    <div className="space-y-2">
      <p className="text-xs font-code text-bist-dim uppercase tracking-widest mb-3">Runs por dia — últimos 30 dias</p>
      <div className="flex items-end gap-1 h-24">
        {data.map((d, i) => {
          const total    = d.passed + d.failed;
          const totalPct = (total / max) * 100;
          const passPct  = total ? (d.passed / total) * 100 : 0;

          return (
            <div key={i} className="flex-1 flex flex-col justify-end group relative" title={`${d.date}\n${d.passed} passed · ${d.failed} failed`}>
              <div className="relative overflow-hidden rounded-sm" style={{ height: `${totalPct}%`, minHeight: total ? "4px" : 0 }}>
                <div className="absolute bottom-0 w-full bg-[#a3fb73]/60 transition-colors group-hover:bg-[#a3fb73]" style={{ height: `${passPct}%` }} />
                {d.failed > 0 && (
                  <div className="absolute top-0 w-full bg-red-300 transition-colors group-hover:bg-red-400" style={{ height: `${100 - passPct}%` }} />
                )}
              </div>
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block z-10 pointer-events-none">
                <div className="bg-bist-primary text-white rounded-lg px-2 py-1 text-[9px] font-code whitespace-nowrap shadow-lg">
                  {d.date}<br />
                  <span className="text-[#a3fb73]">{d.passed}✓</span>
                  {d.failed > 0 && <span className="text-red-300 ml-1">{d.failed}✗</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="flex justify-between text-[9px] font-code text-bist-dim">
        <span>{data[0]?.date ?? ""}</span>
        <span>{data[data.length - 1]?.date ?? ""}</span>
      </div>
    </div>
  );
}

function FlakyList({ scenarios }: { scenarios: BistStats["flaky_scenarios"] }) {
  if (!scenarios.length) return (
    <div className="text-center py-6">
      <p className="text-sm font-medium text-[#2D6A3F]">Nenhum cenário flaky</p>
      <p className="text-xs text-bist-muted mt-1">Todos os cenários são estáveis</p>
    </div>
  );

  return (
    <div className="space-y-2">
      {scenarios.map((s, i) => {
        const failColor = s.failure_rate >= 50 ? "#DC2626" : s.failure_rate >= 25 ? "#D97706" : "#2D6A3F";
        const barColor  = s.failure_rate >= 50 ? "bg-red-400" : s.failure_rate >= 25 ? "bg-amber-400" : "bg-[#a3fb73]";
        return (
          <div key={i} className="card-subtle p-3 space-y-1.5">
            <div className="flex items-start justify-between gap-2">
              <p className="text-xs text-bist-mid leading-snug flex-1 min-w-0 truncate">{s.name}</p>
              <span className="text-xs font-code font-bold tabular-nums shrink-0" style={{ color: failColor }}>
                {s.failure_rate.toFixed(0)}%
              </span>
            </div>
            <div className="flex items-center gap-3 text-[10px] font-code text-bist-dim">
              <span>{s.total_runs} runs</span>
              <span className="text-red-500">{s.failures} falhas</span>
            </div>
            <div className="h-1 bg-bist-border rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all ${barColor}`} style={{ width: `${Math.min(100, s.failure_rate)}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function StatsOverview({ stats }: { stats: BistStats }) {
  const metrics = [
    { label: "Total runs",     value: stats.total_runs.toString() },
    { label: "Aprovados",      value: stats.passed_runs.toString(), accent: true },
    { label: "Reprovados",     value: stats.failed_runs.toString(), danger: true },
    { label: "Pass rate",      value: `${stats.pass_rate.toFixed(1)}%`, accent: true },
    { label: "Duração média",  value: `${(stats.avg_duration_ms / 1000).toFixed(1)}s` },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
      {metrics.map(({ label, value, accent, danger }) => (
        <div key={label} className="card p-4 text-center">
          <p className={`text-2xl font-code font-bold tabular-nums ${accent ? "text-[#2D6A3F]" : danger ? "text-red-500" : "text-bist-primary"}`}>
            {value}
          </p>
          <p className="text-[10px] font-code text-bist-dim uppercase tracking-widest mt-1">{label}</p>
        </div>
      ))}
    </div>
  );
}

export function FlakyChart({ stats }: { stats: BistStats }) {
  return (
    <div className="space-y-6">
      <StatsOverview stats={stats} />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="card p-5">
          <TrendChart data={stats.runs_over_time} />
        </div>
        <div className="card p-5 space-y-4">
          <p className="text-xs font-code text-bist-dim uppercase tracking-widest">Cenários instáveis (flaky)</p>
          <FlakyList scenarios={stats.flaky_scenarios} />
        </div>
      </div>
    </div>
  );
}
