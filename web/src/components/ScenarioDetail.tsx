"use client";

import { useState } from "react";
import { CheckCircle2, XCircle, MinusCircle, ChevronDown, ChevronUp, Film } from "lucide-react";
import { StepTimeline } from "./StepTimeline";
import type { BistScenario } from "@/types";

function statusIcon(s: string) {
  if (s === "passed")  return <CheckCircle2 className="w-4 h-4 text-[#a3fb73]" />;
  if (s === "failed")  return <XCircle      className="w-4 h-4 text-red-400"   />;
  return                      <MinusCircle  className="w-4 h-4 text-[#5a7a65]" />;
}

function fmtDuration(ms: number) {
  if (!ms) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

function ScenarioCard({ scenario }: { scenario: BistScenario }) {
  const [open, setOpen] = useState(scenario.status === "failed");

  const passedSteps = scenario.steps.filter(s => s.status === "passed").length;
  const totalSteps  = scenario.steps.length;

  return (
    <div className={`card overflow-hidden transition-colors duration-150 ${
      scenario.status === "failed" ? "border-red-400/20" : ""
    }`}>
      {/* Header */}
      <button
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-[#a3fb73]/3 transition-colors"
        onClick={() => setOpen(o => !o)}
      >
        {statusIcon(scenario.status)}

        <div className="flex-1 min-w-0">
          <p className="text-sm font-mono font-semibold text-[#eef9e8] truncate">
            {scenario.name}
          </p>
          <div className="flex items-center gap-3 mt-0.5 text-[10px] font-mono text-[#5a7a65]">
            <span>{totalSteps > 0 ? `${passedSteps}/${totalSteps} steps` : "sem steps"}</span>
            <span>{fmtDuration(scenario.duration_ms)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {scenario.video_path && (
            <a
              href={scenario.video_path}
              target="_blank"
              rel="noopener noreferrer"
              onClick={e => e.stopPropagation()}
              className="text-[#5a7a65] hover:text-[#a3fb73] transition-colors"
              title="ver vídeo"
            >
              <Film className="w-3.5 h-3.5" />
            </a>
          )}
          {open
            ? <ChevronUp   className="w-3.5 h-3.5 text-[#5a7a65]" />
            : <ChevronDown className="w-3.5 h-3.5 text-[#5a7a65]" />
          }
        </div>
      </button>

      {/* Expanded content */}
      {open && (
        <div className="px-4 pb-4 border-t border-[#a3fb73]/8">
          {scenario.error && (
            <div className="mt-3 p-3 rounded bg-red-500/8 border border-red-400/20">
              <p className="text-xs font-mono text-red-300 whitespace-pre-wrap break-all">
                {scenario.error}
              </p>
            </div>
          )}
          <div className="mt-3">
            <StepTimeline steps={scenario.steps} />
          </div>
        </div>
      )}
    </div>
  );
}

export function ScenarioDetail({ scenarios }: { scenarios: BistScenario[] }) {
  if (!scenarios.length) return (
    <p className="text-sm font-mono text-[#5a7a65] py-4">nenhum cenário registrado neste run.</p>
  );

  const passed  = scenarios.filter(s => s.status === "passed").length;
  const failed  = scenarios.filter(s => s.status === "failed").length;
  const skipped = scenarios.filter(s => s.status === "skipped").length;

  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <div className="flex items-center gap-4 text-xs font-mono">
        <span className="text-[#a3fb73]">{passed} passou</span>
        {failed > 0  && <span className="text-red-400">{failed} falhou</span>}
        {skipped > 0 && <span className="text-[#5a7a65]">{skipped} pulado</span>}
        <div className="flex-1 h-1.5 bg-[#243d2c] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#a3fb73] rounded-full transition-all"
            style={{ width: `${(passed / scenarios.length) * 100}%` }}
          />
        </div>
        <span className="text-[#5a7a65] tabular-nums">
          {Math.round((passed / scenarios.length) * 100)}%
        </span>
      </div>

      {/* Scenario cards */}
      <div className="space-y-2">
        {scenarios.map(s => <ScenarioCard key={s.id} scenario={s} />)}
      </div>
    </div>
  );
}
