"use client";

import type { BistStats } from "@/types";

// ── Trend bar chart ────────────────────────────────────────────────────────────

function TrendChart({ data }: { data: BistStats["runs_over_time"] }) {
  if (!data.length) return (
    <p className="text-xs font-mono text-[#5a7a65] py-4 text-center">sem dados de tendência</p>
  );

  const max = Math.max(...data.map(d => d.passed + d.failed), 1);

  return (
    <div className="space-y-2">
      <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest mb-3">
        // runs por dia — últimos 30 dias
      </p>
      <div className="flex items-end gap-1 h-24">
        {data.map((d, i) => {
          const total    = d.passed + d.failed;
          const totalPct = (total / max) * 100;
          const passPct  = total ? (d.passed / total) * 100 : 0;

          return (
            <div key={i} className="flex-1 flex flex-col justify-end group relative" title={
              `${d.date}\n${d.passed} passed · ${d.failed} failed`
            }>
              <div className="relative overflow-hidden rounded-t" style={{ height: `${totalPct}%`, minHeight: total ? "4px" : 0 }}>
                {/* Pass portion */}
                <div
                  className="absolute bottom-0 w-full bg-[#a3fb73]/70 transition-colors group-hover:bg-[#a3fb73]"
                  style={{ height: `${passPct}%` }}
                />
                {/* Fail portion */}
                {d.failed > 0 && (
                  <div
                    className="absolute top-0 w-full bg-red-400/60 transition-colors group-hover:bg-red-400"
                    style={{ height: `${100 - passPct}%` }}
                  />
                )}
              </div>
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1
                              hidden group-hover:block z-10 pointer-events-none">
                <div className="bg-[#1a2c21] border border-[#a3fb73]/20 rounded px-2 py-1
                                text-[9px] font-mono text-[#7a9b87] whitespace-nowrap shadow-lg">
                  {d.date}<br />
                  <span className="text-[#a3fb73]">{d.passed}✓</span>
                  {d.failed > 0 && <span className="text-red-400 ml-1">{d.failed}✗</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="flex justify-between text-[9px] font-mono text-[#3d5a44]">
        <span>{data[0]?.date ?? ""}</span>
        <span>{data[data.length - 1]?.date ?? ""}</span>
      </div>
    </div>
  );
}

// ── Flaky scenario list ────────────────────────────────────────────────────────

function FlakyList({ scenarios }: { scenarios: BistStats["flaky_scenarios"] }) {
  if (!scenarios.length) return (
    <div className="text-center py-6">
      <p className="text-sm font-mono text-[#a3fb73]">nenhum cenário flaky</p>
      <p className="text-xs font-mono text-[#3d5a44] mt-1">todos os cenários são estáveis</p>
    </div>
  );

  return (
    <div className="space-y-2">
      {scenarios.map((s, i) => {
        const failColor = s.failure_rate >= 50 ? "#ef4444" : s.failure_rate >= 25 ? "#f59e0b" : "#a3fb73";
        return (
          <div key={i} className="card p-3 space-y-1.5">
            <div className="flex items-start justify-between gap-2">
              <p className="text-xs font-mono text-[#c8e8c8] leading-snug flex-1 min-w-0 truncate">
                {s.name}
              </p>
              <span
                className="text-xs font-mono font-bold tabular-nums shrink-0"
                style={{ color: failColor }}
              >
                {s.failure_rate.toFixed(0)}%
              </span>
            </div>
            <div className="flex items-center gap-3 text-[10px] font-mono text-[#5a7a65]">
              <span>{s.total_runs} runs</span>
              <span className="text-red-400">{s.failures} falhas</span>
            </div>
            {/* Failure rate bar */}
            <div className="h-1 bg-[#243d2c] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${Math.min(100, s.failure_rate)}%`,
                  backgroundColor: failColor,
                  opacity: 0.7,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Stats overview ─────────────────────────────────────────────────────────────

function StatsOverview({ stats }: { stats: BistStats }) {
  const metrics = [
    { label: "total runs",   value: stats.total_runs.toString() },
    { label: "aprovados",    value: stats.passed_runs.toString() },
    { label: "reprovados",   value: stats.failed_runs.toString() },
    { label: "pass rate",    value: `${stats.pass_rate.toFixed(1)}%` },
    { label: "duração média",value: `${(stats.avg_duration_ms / 1000).toFixed(1)}s` },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
      {metrics.map(({ label, value }) => (
        <div key={label} className="card p-3 text-center">
          <p className="text-xl font-mono font-bold text-[#a3fb73] tabular-nums">{value}</p>
          <p className="text-[9px] font-mono text-[#5a7a65] uppercase tracking-widest mt-0.5">{label}</p>
        </div>
      ))}
    </div>
  );
}

// ── Main export ───────────────────────────────────────────────────────────────

export function FlakyChart({ stats }: { stats: BistStats }) {
  return (
    <div className="space-y-8">
      <StatsOverview stats={stats} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend chart */}
        <div className="card p-5">
          <TrendChart data={stats.runs_over_time} />
        </div>

        {/* Flaky list */}
        <div className="card p-5 space-y-4">
          <p className="text-xs font-mono text-[#5a7a65] uppercase tracking-widest">
            // cenários instáveis (flaky)
          </p>
          <FlakyList scenarios={stats.flaky_scenarios} />
        </div>
      </div>
    </div>
  );
}
