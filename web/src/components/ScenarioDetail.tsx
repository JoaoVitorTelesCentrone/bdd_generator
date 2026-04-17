"use client";

import { useState } from "react";
import { CheckCircle2, XCircle, MinusCircle, ChevronDown, ChevronUp, Film } from "lucide-react";
import { StepTimeline } from "./StepTimeline";
import type { BistScenario } from "@/types";

function statusIcon(s: string) {
  if (s === "passed")  return <CheckCircle2 className="w-4 h-4 text-[#2D6A3F]" />;
  if (s === "failed")  return <XCircle      className="w-4 h-4 text-red-500"    />;
  return                      <MinusCircle  className="w-4 h-4 text-bist-muted" />;
}

function fmtDuration(ms: number) {
  if (!ms) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

function ScenarioCard({ scenario }: { scenario: BistScenario }) {
  const [open, setOpen]  = useState(scenario.status === "failed");
  const passedSteps      = scenario.steps.filter(s => s.status === "passed").length;
  const totalSteps       = scenario.steps.length;

  return (
    <div className={`card overflow-hidden transition-colors ${scenario.status === "failed" ? "border-red-200" : ""}`}>
      <button
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-bist-surface2 transition-colors"
        onClick={() => setOpen(o => !o)}
      >
        {statusIcon(scenario.status)}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-bist-primary truncate">{scenario.name}</p>
          <div className="flex items-center gap-3 mt-0.5 text-xs text-bist-muted font-code">
            <span>{totalSteps > 0 ? `${passedSteps}/${totalSteps} steps` : "sem steps"}</span>
            <span>{fmtDuration(scenario.duration_ms)}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {scenario.video_path && (
            <a href={scenario.video_path} target="_blank" rel="noopener noreferrer"
               onClick={e => e.stopPropagation()}
               className="text-bist-muted hover:text-bist-primary transition-colors">
              <Film className="w-3.5 h-3.5" />
            </a>
          )}
          {open ? <ChevronUp className="w-3.5 h-3.5 text-bist-muted" /> : <ChevronDown className="w-3.5 h-3.5 text-bist-muted" />}
        </div>
      </button>

      {open && (
        <div className="px-4 pb-4 border-t border-bist-border">
          {scenario.error && (
            <div className="mt-3 p-3 rounded-lg bg-red-50 border border-red-200">
              <p className="text-xs font-code text-red-600 whitespace-pre-wrap break-all">{scenario.error}</p>
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
    <p className="text-sm text-bist-muted py-4">Nenhum cenário registrado neste run.</p>
  );

  const passed  = scenarios.filter(s => s.status === "passed").length;
  const failed  = scenarios.filter(s => s.status === "failed").length;
  const skipped = scenarios.filter(s => s.status === "skipped").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 text-xs font-code">
        <span className="text-[#2D6A3F] font-medium">{passed} passou</span>
        {failed  > 0 && <span className="text-red-500 font-medium">{failed} falhou</span>}
        {skipped > 0 && <span className="text-bist-muted">{skipped} pulado</span>}
        <div className="flex-1 h-1.5 bg-bist-border rounded-full overflow-hidden">
          <div className="h-full bg-[#a3fb73] rounded-full" style={{ width: `${(passed / scenarios.length) * 100}%` }} />
        </div>
        <span className="text-bist-muted tabular-nums">{Math.round((passed / scenarios.length) * 100)}%</span>
      </div>
      <div className="space-y-2">
        {scenarios.map(s => <ScenarioCard key={s.id} scenario={s} />)}
      </div>
    </div>
  );
}
